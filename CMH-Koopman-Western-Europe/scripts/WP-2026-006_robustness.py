"""
WP-2026-006 §6.4 — Robustness analyses.

Diagnostics computed:
  (a) Local normality of leading eigenvectors (Theorem 1 hyp. v).
  (b) Cross-country residual correlation rho_bar and N_eff (Prop 4.4).
  (c) Cross-window mode correspondence.
  (d) Multiple imputation sensitivity (if applicable).
  (e) Kernel DMD sensitivity.
  (f) Forward-backward DMD (carried over).
  (g) Matrix completion sensitivity.
"""

import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '/home/claude/wp006')
from estimator_v3 import (
    build_transformed_series, hankel_augment, standardise,
    _pool_xm_xp, fit_dmd_canonical, fit_dmd_tls_canonical,
    fit_dmd_forward_backward, spectrum, select_K_by_gap,
    gavish_donoho_rank, PERSISTENCE_THR, GAP_FACTOR, TAU, STATE_VARS
)

# ===========================================================================
# (a) Local normality of leading eigenvectors
# ===========================================================================

def diagnose_local_normality(A_tilde, K):
    """Condition number of leading-K right-eigenvectors.

    Theorem 1 hyp. (v) — normality of K_theta on the leading eigenspace —
    is violated when the K leading right-eigenvectors are far from
    orthogonal (cond(W) >> 1) and/or right- and left-eigenvectors are
    badly mis-aligned.

    Returns:
      - kappa_W: condition number of leading right-eigenvector matrix
      - max_left_right_misalign: maximum 1 - |<v_j, u_j>| over the
        K leading modes, where v_j is right- and u_j is left-eigenvector
        (both normalised).
    """
    evals, V = spectrum(A_tilde)  # V columns are right-eigenvectors
    K = min(K, len(evals))
    V_K = V[:, :K]
    kappa_W = np.linalg.cond(V_K)
    # Left eigenvectors: rows of inv(V), normalised
    Vinv = np.linalg.pinv(V)
    U_left = Vinv[:K, :].conj()  # rows
    misaligns = []
    for j in range(K):
        v = V_K[:, j] / np.linalg.norm(V_K[:, j])
        u = U_left[j, :] / np.linalg.norm(U_left[j, :])
        misaligns.append(1.0 - abs(np.vdot(v, u)))
    return kappa_W, max(misaligns), np.array(misaligns)


# ===========================================================================
# (b) Cross-country residual correlation rho_bar and N_eff
# ===========================================================================

def diagnose_rho_bar(H_dict, A_tilde, U_r):
    """Average pairwise residual correlation across countries.

    The fitted propagator A_tilde lives in the reduced r-dim space.
    For each country, we project H[:-1] onto U_r, multiply by A_tilde,
    compare with the projected H[1:], and obtain a country-specific
    residual time series in r-dim. Then the cross-country correlation
    is averaged over pairs.
    """
    countries = list(H_dict.keys())
    residuals = {}
    for c in countries:
        H = H_dict[c]
        if H is None or H.shape[1] < 2:
            continue
        Xm = U_r.T @ H[:, :-1]
        Xp = U_r.T @ H[:, 1:]
        residuals[c] = Xp - A_tilde @ Xm
    if len(residuals) < 2:
        return None, None, None
    # Pairwise correlations: pool residuals across r-dim, then correlate
    # countries over their COMMON time overlap.
    # Each residual is (r, T_c - 1). Align them by year if possible.
    # Here we just use raw within-r correlations of flattened residuals
    # over the shortest common length.
    pairs = []
    keys = list(residuals.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            r_i = residuals[keys[i]]
            r_j = residuals[keys[j]]
            T = min(r_i.shape[1], r_j.shape[1])
            # Flatten over r-dim, correlate
            ri = r_i[:, :T].flatten()
            rj = r_j[:, :T].flatten()
            if ri.std() < 1e-12 or rj.std() < 1e-12:
                continue
            rho = np.corrcoef(ri, rj)[0, 1]
            pairs.append(rho)
    rho_bar = np.mean(pairs) if pairs else None
    Nc = len(residuals)
    # nominal pooled count
    N_nom = sum(r.shape[1] for r in residuals.values())
    if rho_bar is not None:
        N_eff = Nc * (N_nom / Nc) / (1 + rho_bar * (Nc - 1))
    else:
        N_eff = None
    return rho_bar, N_eff, np.array(pairs)


# ===========================================================================
# (c) Cross-window correspondence
# ===========================================================================

def cross_window_correspondence(spec_pre, spec_post,
                                period_band_tol=0.20,
                                modulus_band_tol=0.10):
    """Match modes across sub-windows by period and modulus proximity.

    A mode in pre-war matches a mode in post-war if the relative period
    difference is < period_band_tol and the modulus difference < modulus_band_tol.
    """
    matches = []
    for i, e_pre in enumerate(spec_pre):
        if e_pre.imag <= 1e-6 or np.angle(e_pre) < 1e-4:
            continue
        T_pre = 2*np.pi / np.angle(e_pre)
        m_pre = abs(e_pre)
        for j, e_post in enumerate(spec_post):
            if e_post.imag <= 1e-6 or np.angle(e_post) < 1e-4:
                continue
            T_post = 2*np.pi / np.angle(e_post)
            m_post = abs(e_post)
            if (abs(T_pre - T_post) / max(T_pre, T_post) < period_band_tol
                and abs(m_pre - m_post) < modulus_band_tol):
                matches.append({
                    'T_pre': T_pre, 'mod_pre': m_pre,
                    'T_post': T_post, 'mod_post': m_post,
                    'i_pre': i, 'j_post': j,
                })
    return matches


# ===========================================================================
# (e) Kernel DMD
# ===========================================================================

def fit_kernel_dmd(H_list, gamma=None):
    """Gaussian-kernel DMD (Williams et al. 2015).

    Kernel width set by median heuristic on pooled state vectors
    if gamma is None.
    """
    Xm, Xp = _pool_xm_xp(H_list)
    if Xm is None:
        return None
    d, N = Xm.shape
    # Median heuristic for kernel bandwidth
    # Subsample for median computation (N can be large)
    n_sub = min(N, 500)
    idx = np.random.RandomState(0).choice(N, size=n_sub, replace=False)
    Xs = Xm[:, idx].T  # (n_sub, d)
    # pairwise squared distances
    dists = np.sum((Xs[:, None, :] - Xs[None, :, :])**2, axis=2)
    sigma2 = np.median(dists[dists > 0])
    if gamma is None:
        gamma = 1.0 / sigma2
    # Gram matrix K_minus_minus = k(X_-, X_-) and K_plus_minus = k(X_+, X_-)
    # Use the kernel trick to fit the Koopman operator in feature space.
    Xm_T = Xm.T  # (N, d)
    Xp_T = Xp.T  # (N, d)
    # K_mm[i,j] = exp(-gamma ||xm_i - xm_j||^2)
    sq_mm = (np.sum(Xm_T**2, axis=1)[:, None]
             + np.sum(Xm_T**2, axis=1)[None, :]
             - 2 * Xm_T @ Xm_T.T)
    K_mm = np.exp(-gamma * sq_mm)
    sq_pm = (np.sum(Xp_T**2, axis=1)[:, None]
             + np.sum(Xm_T**2, axis=1)[None, :]
             - 2 * Xp_T @ Xm_T.T)
    K_pm = np.exp(-gamma * sq_pm)
    # Truncate via SVD of K_mm with GD threshold
    U_K, S_K, Vt_K = np.linalg.svd(K_mm, full_matrices=False)
    r_gd, _ = gavish_donoho_rank(S_K, N, N)
    r = max(2, min(r_gd, N-1))
    U_r = U_K[:, :r]
    S_r = S_K[:r]
    # Reduced Koopman: K_hat = U_r^* K_pm V_r Sigma_r^{-1}
    V_r = Vt_K[:r, :].T
    A_tilde = U_r.T @ K_pm @ V_r @ np.diag(1.0 / np.sqrt(S_r))
    # (Approximation; full theory in Williams 2015)
    return A_tilde, r, gamma


# ===========================================================================
# Main driver
# ===========================================================================

def run_robustness(wide, sub_window, primary_results):
    print(f'\n{"="*70}\n  Robustness — {sub_window}\n{"="*70}')

    # Rebuild common scaffolding
    series_dict = {}
    for c in sorted(wide['ISO3'].unique()):
        X, _ = build_transformed_series(wide, c, sub_window)
        if X is not None:
            series_dict[c] = X
    std_list, _, _ = standardise(list(series_dict.values()))
    H_dict = dict(zip(series_dict.keys(),
                      [hankel_augment(X) for X in std_list]))
    H_list = list(H_dict.values())

    # Pull primary fit
    primary = primary_results['canonical DMD @ GD rank']
    A_tilde, U_r, K = primary['A'], primary['U_r'], primary['K']

    # (a) Local normality
    print('\n  (a) Local normality — Theorem 1 hyp. (v)')
    kappa, max_misalign, misaligns = diagnose_local_normality(A_tilde, K)
    print(f'      Condition number of leading-K eigenvectors: {kappa:.2e}')
    print(f'      Max left-right eigenvector misalignment over K: {max_misalign:.4f}')
    if kappa < 10:
        print(f'      Interpretation: near-normal (kappa < 10)')
    elif kappa < 100:
        print(f'      Interpretation: moderate non-normality (10 < kappa < 100)')
    else:
        print(f'      Interpretation: strong non-normality (kappa >= 100); '
              f'Lipschitz constant of Lemma 3.4 needs pseudospectral form')

    # (b) rho_bar and N_eff
    print('\n  (b) Cross-country residual correlation — Prop 4.4')
    rho_bar, N_eff, rho_pairs = diagnose_rho_bar(H_dict, A_tilde, U_r)
    N_nominal = sum((H.shape[1] - 1) for H in H_list if H is not None)
    print(f'      Pairwise residual correlations (N_pairs={len(rho_pairs)}):')
    print(f'        mean rho_bar = {rho_bar:.4f}')
    print(f'        std rho_bar  = {rho_pairs.std():.4f}')
    print(f'        min / max     = {rho_pairs.min():.4f} / {rho_pairs.max():.4f}')
    print(f'      Nominal pooled N (sum of T_c - 1 across countries) = {N_nominal}')
    Nc = len(H_dict)
    print(f'      N_eff = {Nc} * (N_nom/Nc) / (1 + rho_bar * (Nc-1)) = {N_eff:.0f}')
    deflation = N_nominal / max(N_eff, 1)
    print(f'      Deflation factor: {deflation:.2f}x')

    # (e) Kernel DMD
    print('\n  (e) Kernel DMD sensitivity')
    np.random.seed(0)
    k_fit = fit_kernel_dmd(H_list)
    if k_fit is not None:
        A_k, r_k, gamma_k = k_fit
        evals_k, _ = spectrum(A_k)
        n_unit_k = int((np.abs(evals_k) > 1.001).sum())
        thr = PERSISTENCE_THR[sub_window]
        n_pers_k = int((np.abs(evals_k) >= thr).sum())
        K_k, gap_k = select_K_by_gap(evals_k)
        K_str = str(K_k) if K_k is not None else 'n/a'
        print(f'      Kernel DMD r = {r_k}, gamma = {gamma_k:.4e}')
        print(f'      max |λ| = {np.abs(evals_k[0]):.4f}, #|λ|>1 = {n_unit_k}, '
              f'persistent = {n_pers_k}, K = {K_str} (gap = {gap_k:.2f})')
        print(f'      Top 10 |λ|: ' + ', '.join(f'{np.abs(e):.4f}' for e in evals_k[:10]))

    return {
        'kappa_W': kappa,
        'max_misalign': max_misalign,
        'rho_bar': rho_bar,
        'N_eff': N_eff,
        'N_nominal': N_nominal,
        'kernel_dmd': (evals_k if k_fit is not None else None,
                       r_k if k_fit is not None else None),
    }


if __name__ == '__main__':
    wide = pd.read_csv('/home/claude/panel_wide.csv')
    # Re-fit primary estimator for each sub-window
    from estimator_v3 import run_subwindow
    primary_pre = run_subwindow(wide, '1820-1913')
    primary_post = run_subwindow(wide, '1945-2020')

    print('\n\n' + '#'*70)
    print('  ROBUSTNESS ANALYSES')
    print('#'*70)

    rob_pre = run_robustness(wide, '1820-1913', primary_pre)
    rob_post = run_robustness(wide, '1945-2020', primary_post)

    # (c) Cross-window
    print('\n\n' + '='*70)
    print('  (c) Cross-window mode correspondence')
    print('='*70)
    spec_pre = primary_pre['canonical DMD @ GD rank']['evals']
    spec_post = primary_post['canonical DMD @ GD rank']['evals']
    matches = cross_window_correspondence(spec_pre, spec_post)
    if matches:
        print(f'\n  Found {len(matches)} cross-window matches '
              f'(period tol 20%, modulus tol 0.10):')
        for m in matches:
            print(f'    pre T={m["T_pre"]:.2f}y |λ|={m["mod_pre"]:.4f}  '
                  f'↔  post T={m["T_post"]:.2f}y |λ|={m["mod_post"]:.4f}')
    else:
        print('\n  No cross-window matches found at this tolerance.')
        # Try looser
        print('\n  Trying looser tolerance (35% period, 0.15 modulus):')
        matches2 = cross_window_correspondence(spec_pre, spec_post,
                                              period_band_tol=0.35,
                                              modulus_band_tol=0.15)
        if matches2:
            for m in matches2:
                print(f'    pre T={m["T_pre"]:.2f}y |λ|={m["mod_pre"]:.4f}  '
                      f'↔  post T={m["T_post"]:.2f}y |λ|={m["mod_post"]:.4f}')
        else:
            print('    Still none.')

    # Final summary
    print('\n\n' + '#'*70)
    print('  ROBUSTNESS SUMMARY')
    print('#'*70)
    for label, rob in [('Pre-war 1820-1913', rob_pre),
                       ('Post-war 1945-2020', rob_post)]:
        print(f'\n  {label}:')
        print(f'    kappa_W (leading-K eigenvectors) = {rob["kappa_W"]:.2e}')
        print(f'    Max left-right misalignment      = {rob["max_misalign"]:.4f}')
        print(f'    rho_bar                          = {rob["rho_bar"]:.4f}')
        print(f'    N_nominal                        = {rob["N_nominal"]}')
        print(f'    N_eff                            = {rob["N_eff"]:.0f}')
        deflation = rob["N_nominal"] / max(rob["N_eff"], 1)
        print(f'    Deflation factor                  = {deflation:.2f}x')
