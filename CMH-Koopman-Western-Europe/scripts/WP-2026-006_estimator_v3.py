"""
WP-2026-006 §6 — Multi-task Hankel-DMD estimator (v3).

CANONICAL DMD pipeline per Tu et al. (2014), Algorithm 2.

This is the estimator that the §5.6 pre-registration intended by
"multi-task Hankel-DMD". The v1/v2 versions used unprojected ridge
regression in the full d-dimensional Hankel-augmented space, which is
not the canonical DMD construction. The corrected pipeline is:

  1. Build pooled X_-, X_+ from per-country Hankel matrices.
  2. SVD of X_-: X_- = U Sigma V^*.
  3. Truncate at rank r via Gavish-Donoho universal hard-threshold.
  4. Reduced propagator: A_tilde = U_r^* X_+ V_r Sigma_r^{-1}  (r x r).
  5. Spectrum of A_tilde returns the DMD eigenvalues.
  6. DMD modes: phi_j = U_r w_j  (projected modes).

Bug-fix carry-over from v2:
  - CV with out-of-sample sigma estimation; in v3 we use predictive
    RMSE per state dimension (no Gaussian log-likelihood) because the
    Hankel state-space has dimensions with near-zero residuals at
    lam = 0 that blow up Gaussian log-likelihood.

Three estimator variants (per §5.6):
  - Standard DMD-via-SVD (canonical Tu et al.)
  - TLS-DMD with SVD-projection (Hemati et al. 2017): SVD of
    [X_-; X_+] stack, project to leading r, then DMD.
  - Forward-backward DMD (Dawson et al. 2016) on projected
    representation.

K selection is the spectral gap on the r eigenvalues, NOT on 40.
"""

import numpy as np
import pandas as pd
from scipy.linalg import eig as sp_eig

# Pre-registered constants
TAU = 7
STATE_VARS = ['pop', 'gdppc', 'v2x_libdem', 'v2x_polyarchy', 'cinc']
LOGDIFF_VARS = ['pop', 'gdppc']
LEVEL_VARS = ['v2x_libdem', 'v2x_polyarchy', 'cinc']
PERSISTENCE_THR = {'1820-1913': 0.989, '1945-2020': 0.987}
GAP_FACTOR = 1.5


# ---------------------------------------------------------------------------
# Series construction (unchanged from v2)
# ---------------------------------------------------------------------------

def build_transformed_series(wide, country, sub_window):
    grp = (wide[(wide['ISO3'] == country) & (wide['sub_window'] == sub_window)]
           .sort_values('year').copy())
    mask = grp[STATE_VARS].notna().all(axis=1)
    grp = grp.loc[mask].reset_index(drop=True)
    if len(grp) < TAU + 2:
        return None, None
    series = pd.DataFrame(index=grp.index)
    for v in LOGDIFF_VARS:
        series[v + '_dlog'] = np.log(grp[v].values) - np.log(grp[v].shift(1).values)
    for v in LEVEL_VARS:
        series[v] = grp[v].values
    series['year'] = grp['year'].values
    series = series.iloc[1:].reset_index(drop=True)
    state_cols = [v + '_dlog' for v in LOGDIFF_VARS] + LEVEL_VARS
    return series[state_cols].values, series['year'].values

def hankel_augment(X, tau=TAU):
    T, n = X.shape
    if T <= tau:
        return None
    return np.vstack([X[i:T - tau + i].T for i in range(tau + 1)])

def standardise(X_list):
    pooled = np.vstack(X_list)
    mu = pooled.mean(axis=0)
    sd = pooled.std(axis=0, ddof=1)
    sd[sd == 0] = 1.0
    return [(X - mu) / sd for X in X_list], mu, sd

def _pool_xm_xp(H_list):
    Xm_list, Xp_list = [], []
    for H in H_list:
        if H is None or H.shape[1] < 2:
            continue
        Xm_list.append(H[:, :-1])
        Xp_list.append(H[:, 1:])
    if not Xm_list:
        return None, None
    return np.hstack(Xm_list), np.hstack(Xp_list)


# ---------------------------------------------------------------------------
# Gavish-Donoho threshold
# ---------------------------------------------------------------------------

def gavish_donoho_rank(sigma, m, n):
    """Universal hard-threshold for matrix rank estimation under noise."""
    if m > n:
        m, n = n, m
    beta = m / n
    omega = 0.56 * beta**3 - 0.95 * beta**2 + 1.82 * beta + 1.43
    thr = omega * np.median(sigma)
    return int(np.sum(sigma > thr)), thr


# ---------------------------------------------------------------------------
# DMD estimators (canonical Tu et al. 2014 pipeline)
# ---------------------------------------------------------------------------

def fit_dmd_canonical(H_list, rank_override=None):
    """Standard DMD per Tu et al. (2014), Algorithm 2.

    Returns:
      A_tilde: reduced (r x r) propagator
      U_r:     left-singular basis (d x r) — DMD modes' projection basis
      r:       effective rank used
      diag:    dict of diagnostics
    """
    Xm, Xp = _pool_xm_xp(H_list)
    if Xm is None:
        return None
    d, N = Xm.shape

    # Economy SVD of X_minus
    U, S, Vt = np.linalg.svd(Xm, full_matrices=False)

    # Rank truncation: Gavish-Donoho on Xm singular values
    r_gd, thr = gavish_donoho_rank(S, d, N)
    r = r_gd if rank_override is None else rank_override
    r = max(2, min(r, len(S)))

    U_r = U[:, :r]
    S_r = S[:r]
    V_r = Vt[:r, :].T            # (N, r)

    # Reduced propagator: A_tilde = U_r^* X_+ V_r Sigma_r^{-1}
    A_tilde = U_r.T @ Xp @ V_r @ np.diag(1.0 / S_r)

    diag = {
        'singular_values': S,
        'gd_threshold': thr,
        'gd_rank': r_gd,
        'effective_rank': r,
        'd': d,
        'N': N,
    }
    return A_tilde, U_r, r, diag

def fit_dmd_tls_canonical(H_list, rank_override=None):
    """TLS-DMD with SVD projection (Hemati et al. 2017).

    Stack Z = [X_-; X_+], SVD it, truncate at GD rank,
    project (X_-, X_+) onto the leading r columns of Vz,
    then run canonical DMD on the projected pair.
    """
    Xm, Xp = _pool_xm_xp(H_list)
    if Xm is None:
        return None
    d, N = Xm.shape
    Z = np.vstack([Xm, Xp])
    Uz, Sz, Vzt = np.linalg.svd(Z, full_matrices=False)
    r_gd, thr = gavish_donoho_rank(Sz, Z.shape[0], Z.shape[1])
    r = r_gd if rank_override is None else rank_override
    r = max(2, min(r, len(Sz)))

    V_r = Vzt[:r, :].T              # (N, r)
    Xm_p = Xm @ V_r                 # (d, r)
    Xp_p = Xp @ V_r                 # (d, r)

    # Now canonical DMD on (Xm_p, Xp_p)
    U, S, Vt = np.linalg.svd(Xm_p, full_matrices=False)
    # rank for the inner SVD: cannot exceed r
    r_inner_gd, _ = gavish_donoho_rank(S, d, r)
    r_inner = max(2, min(r_inner_gd, len(S)))
    U_ri = U[:, :r_inner]
    S_ri = S[:r_inner]
    V_ri = Vt[:r_inner, :].T

    A_tilde = U_ri.T @ Xp_p @ V_ri @ np.diag(1.0 / S_ri)

    diag = {
        'singular_values_Z': Sz,
        'gd_rank_Z': r_gd,
        'singular_values_Xm_proj': S,
        'gd_rank_inner': r_inner_gd,
        'effective_rank_Z': r,
        'effective_rank_inner': r_inner,
    }
    return A_tilde, U_ri, r_inner, diag

def fit_dmd_forward_backward(H_list, rank_override=None):
    """Forward-backward DMD on canonical-projected representation.

    Run canonical DMD forwards (X_- -> X_+) and backwards (X_+ -> X_-),
    then construct the geometric mean of the two reduced propagators.
    """
    Xm, Xp = _pool_xm_xp(H_list)
    if Xm is None:
        return None
    d, N = Xm.shape

    # Forward
    Uf, Sf, Vtf = np.linalg.svd(Xm, full_matrices=False)
    r_f_gd, _ = gavish_donoho_rank(Sf, d, N)
    r_f = r_f_gd if rank_override is None else rank_override
    r_f = max(2, min(r_f, len(Sf)))
    Ufr, Sfr, Vfr = Uf[:, :r_f], Sf[:r_f], Vtf[:r_f, :].T
    A_fwd_tilde = Ufr.T @ Xp @ Vfr @ np.diag(1.0 / Sfr)

    # Backward (swap roles)
    Ub, Sb, Vtb = np.linalg.svd(Xp, full_matrices=False)
    r_b_gd, _ = gavish_donoho_rank(Sb, d, N)
    r_b = r_b_gd if rank_override is None else rank_override
    r_b = max(2, min(r_b, len(Sb)))
    Ubr, Sbr, Vbr = Ub[:, :r_b], Sb[:r_b], Vtb[:r_b, :].T
    A_bwd_tilde = Ubr.T @ Xm @ Vbr @ np.diag(1.0 / Sbr)

    # If ranks match, can compute fb in shared basis
    if r_f != r_b:
        # use minimum; recompute on common basis = forward basis
        r_common = min(r_f, r_b)
        Ufr = Uf[:, :r_common]
        Sfr = Sf[:r_common]
        Vfr = Vtf[:r_common, :].T
        Ubr_proj_to_f = Ufr  # use forward basis for both
        A_fwd_tilde = Ufr.T @ Xp @ Vfr @ np.diag(1.0 / Sfr)
        # Backward in forward basis
        Ub_in_f = Ufr  # project Xm in same basis
        # need to recompute backward propagator with Xm projected on Ufr
        # B_tilde = Ufr^* X_- V Sigma^-1 where V, Sigma from SVD of X_+ projected on Ufr
        Xp_f = Ufr.T @ Xp        # (r_common, N)
        # SVD of Xp_f
        Ubf, Sbf, Vtbf = np.linalg.svd(Xp_f, full_matrices=False)
        r_b_eff = min(r_common, len(Sbf))
        Ubf_r = Ubf[:, :r_b_eff]
        Sbf_r = Sbf[:r_b_eff]
        Vbf_r = Vtbf[:r_b_eff, :].T
        # backward propagator in forward-projected basis
        Xm_f = Ufr.T @ Xm        # (r_common, N)
        A_bwd_tilde = Ubf_r.T @ Xm_f @ Vbf_r @ np.diag(1.0 / Sbf_r)
        r = r_b_eff
        U_r = Ufr
    else:
        r = r_f
        U_r = Ufr

    # Geometric mean: sqrt(A_fwd_tilde @ A_bwd_tilde^{-1})
    from scipy.linalg import sqrtm
    M = A_fwd_tilde @ np.linalg.pinv(A_bwd_tilde)
    A_fb_tilde = sqrtm(M)
    if np.allclose(A_fb_tilde.imag, 0, atol=1e-6):
        A_fb_tilde = A_fb_tilde.real

    diag = {'rank_fwd': r_f, 'rank_bwd': r_b, 'effective_rank': r}
    return A_fb_tilde, U_r, r, diag


def spectrum(A):
    if A is None:
        return None, None
    evals, evecs = (sp_eig(A) if not np.iscomplexobj(A)
                    else np.linalg.eig(A))
    order = np.argsort(-np.abs(evals))
    return evals[order], evecs[:, order]

def select_K_by_gap(evals, factor=GAP_FACTOR):
    mods = np.abs(evals)
    mods = mods[mods > 1e-12]
    if len(mods) < 2:
        return None, None
    log_mods = np.log(mods)
    gaps = -np.diff(log_mods)
    largest = int(np.argmax(gaps))
    if np.exp(gaps[largest]) >= factor:
        return largest + 1, float(np.exp(gaps[largest]))
    return None, float(np.exp(gaps.max()))


# ---------------------------------------------------------------------------
# CV via predictive RMSE (BUG-FIX over v2: avoid log-lik with zero residuals)
# ---------------------------------------------------------------------------

def cv_select_rank(H_dict, rank_grid):
    """Leave-one-country-out CV on truncation rank r.

    For each candidate r, fit canonical DMD on training panel projected
    to rank r, then evaluate one-step-ahead prediction RMSE on the
    held-out country (transformed to the training U_r basis).
    """
    countries = list(H_dict.keys())
    results = {r: [] for r in rank_grid}
    for r in rank_grid:
        for c_out in countries:
            train_H = [H_dict[c] for c in countries if c != c_out]
            fit = fit_dmd_canonical(train_H, rank_override=r)
            if fit is None:
                continue
            A_tilde, U_r, r_eff, _ = fit
            if r_eff < r:
                # training fold couldn't support this rank — skip
                continue
            H_test = H_dict[c_out]
            if H_test is None or H_test.shape[1] < 2:
                continue
            Xm_t = H_test[:, :-1]
            Xp_t = H_test[:, 1:]
            # Project test data onto training U_r basis
            Xm_tp = U_r.T @ Xm_t              # (r, N_test)
            Xp_tp = U_r.T @ Xp_t
            # Predict
            resid = Xp_tp - A_tilde @ Xm_tp
            rmse = np.sqrt((resid ** 2).mean())
            results[r].append(rmse)
    means = {r: np.mean(v) if v else np.inf for r, v in results.items()}
    best_r = min(means, key=means.get)
    return best_r, means


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_subwindow(wide, sub_window):
    print(f'\n{"="*70}\n  Sub-window: {sub_window}\n{"="*70}')
    series_dict = {}
    for c in sorted(wide['ISO3'].unique()):
        X, _ = build_transformed_series(wide, c, sub_window)
        if X is not None:
            series_dict[c] = X
    std_list, mu, sd = standardise(list(series_dict.values()))
    H_dict = dict(zip(series_dict.keys(),
                      [hankel_augment(X) for X in std_list]))
    H_list = list(H_dict.values())
    d_aug = next(iter(H_dict.values())).shape[0]

    # Probe: full Gavish-Donoho rank on pooled X_-
    Xm_full, _ = _pool_xm_xp(H_list)
    _, S_full, _ = np.linalg.svd(Xm_full, full_matrices=False)
    r_gd_full, thr_full = gavish_donoho_rank(S_full, d_aug, Xm_full.shape[1])
    print(f'  d_aug = {d_aug}, N = {Xm_full.shape[1]}')
    print(f'  Pooled X_- singular values (top 10): '
          + ', '.join(f'{s:.2f}' for s in S_full[:10]))
    print(f'  Gavish-Donoho threshold: {thr_full:.4f}')
    print(f'  GD-implied effective rank: {r_gd_full}')

    # CV over rank
    rank_grid = list(range(2, min(d_aug, r_gd_full + 5) + 1))
    print(f'\n  CV-searching ranks in {rank_grid[0]}..{rank_grid[-1]}')
    best_r, rank_cv = cv_select_rank(H_dict, rank_grid)
    print(f'  CV-selected rank r* (one-step RMSE, LOO over countries): {best_r}')
    print(f'  CV RMSE curve (top 12 ranks shown):')
    sorted_r = sorted(rank_cv.items())
    for r, rmse in sorted_r[:12]:
        marker = '  <-- selected' if r == best_r else ''
        print(f'    r={r:>3}  RMSE = {rmse:.6f}{marker}')
    if len(sorted_r) > 12:
        print(f'    ... ({len(sorted_r)-12} more)')
        # also show best 3
        best3 = sorted(rank_cv.items(), key=lambda x: x[1])[:3]
        print(f'  Top-3 ranks by CV RMSE: ' +
              ', '.join(f'r={r} ({rm:.6f})' for r, rm in best3))

    # Use BOTH the GD rank and the CV rank if they differ — report both
    runs = []
    runs.append(('canonical DMD @ GD rank', fit_dmd_canonical(H_list, rank_override=r_gd_full)))
    if best_r != r_gd_full:
        runs.append(('canonical DMD @ CV rank', fit_dmd_canonical(H_list, rank_override=best_r)))
    runs.append(('TLS-DMD (Hemati 2017)', fit_dmd_tls_canonical(H_list)))
    runs.append(('forward-backward', fit_dmd_forward_backward(H_list, rank_override=r_gd_full)))

    thr = PERSISTENCE_THR[sub_window]
    results = {}
    for name, fit in runs:
        if fit is None:
            print(f'\n  {name}: FAILED')
            continue
        A_t, U_r, r, dgn = fit
        evals, evecs = spectrum(A_t)
        K, gap = select_K_by_gap(evals)
        n_pers = int((np.abs(evals) >= thr).sum())
        n_unit = int((np.abs(evals) > 1.001).sum())
        print(f'\n  {name}:  (r = {r})')
        print(f'    spectrum extreme: max |λ| = {np.abs(evals[0]):.4f}, '
              f'#|λ|>1 = {n_unit} of {len(evals)}')
        print(f'    persistence threshold {thr} — modes meeting it: {n_pers}')
        if K is not None:
            print(f'    K from spectral gap: {K} (gap factor = {gap:.2f})')
        else:
            print(f'    no spectral gap >= {GAP_FACTOR}; max gap factor = {gap:.2f}')
        print(f'    all |λ|: ' +
              ', '.join(f'{np.abs(e):.4f}' for e in evals))
        # oscillatory modes
        osc = [(np.abs(e), 2*np.pi/np.angle(e), e) for e in evals
               if e.imag > 1e-6 and np.angle(e) > 1e-4]
        if osc:
            print(f'    oscillatory modes (period in years, sorted by |λ|):')
            for mag, T_p, e in osc[:8]:
                print(f'      |λ|={mag:.4f}  T={T_p:7.2f}y  λ={e.real:+.4f}{e.imag:+.4f}j')
        results[name] = dict(evals=evals, evecs=evecs, A=A_t, U_r=U_r,
                             r=r, K=K, gap=gap, n_persistent=n_pers,
                             n_above_unit=n_unit)
    return results


if __name__ == '__main__':
    wide = pd.read_csv('/home/claude/panel_wide.csv')
    summary = {}
    for sw in ['1820-1913', '1945-2020']:
        summary[sw] = run_subwindow(wide, sw)
    print('\n\n' + '='*70)
    print('  HEADLINE — canonical DMD pipeline')
    print('='*70)
    for sw, res in summary.items():
        primary_key = 'canonical DMD @ GD rank'
        if primary_key in res:
            t = res[primary_key]
            K_str = str(t['K']) if t['K'] is not None else 'n/a (no gap)'
            print(f'  {sw}: max |λ| = {np.abs(t["evals"][0]):.4f}, '
                  f'persistent = {t["n_persistent"]}, K = {K_str}, '
                  f'r = {t["r"]}, gap factor = {t["gap"]:.2f}')
