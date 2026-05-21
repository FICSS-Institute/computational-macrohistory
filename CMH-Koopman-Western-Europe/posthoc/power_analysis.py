"""
WP-2026-006 — Post-hoc power analysis: minimum detectable decay time.

Motivated by external reviewer comment §3.1: the pre-registered Q1 threshold
1 - 1/(3 T_max) is a choice; without a power analysis, a null Q1 may simply
indicate that the test had insufficient power to detect persistent modes
above the threshold.

Methodology:
  - From the §6.5 invariant-measure mode attenuation, infer the empirical
    estimation noise on |hat lambda|.
    For the post-war fit: |hat lambda_null| = 0.9703, true value = 1.0, so
    the observed bias is 0.0297 at N_eff = 210. This is the leading-order
    bias and serves as a proxy for the standard error.
    For the pre-war fit: |hat lambda_null| = 0.9936, bias = 0.0064 at N_eff = 467.

  - The standard error on |hat lambda_j| scales approximately as
      SE(|hat lambda_j|) ~ |lambda_j| * sigma_eps^2 * tr(...) / N_eff
    From the §6.5 measurements, calibrate the scale factor and use it to
    derive a confidence interval on |hat lambda_j| for any nominal value.

  - Minimum detectable decay time tau_min: the smallest decay time such
    that the corresponding |lambda| = exp(-1/tau) lies at least 2 SE above
    the Q1 threshold 1 - 1/(3 T_max).
    This is the decay time the test had power 80%-95% to detect under
    null vs. alternative.

  - Repeat for both sub-windows.

Outputs the minimum detectable decay times in calendar years.
"""

import numpy as np

# -----------------------------------------------------------------------------
# Inputs from §6.5
# -----------------------------------------------------------------------------

# Observed attenuation on the null mode (true value = 1.0)
lambda_obs_pre = 0.9936
lambda_obs_post = 0.9703

# Effective sample sizes (App A.5)
N_eff_pre = 467
N_eff_post = 210

# Q1 persistence thresholds (§5.5)
# T_max(pre) = 94/3 ~ 31.3 yr -> threshold = 1 - 1/(3*31.3) = 0.989
# T_max(post) = 76/3 ~ 25.3 yr -> threshold = 1 - 1/(3*25.3) = 0.987
T_max_pre = 94/3
T_max_post = 76/3
thr_pre = 1.0 - 1.0 / (3 * T_max_pre)
thr_post = 1.0 - 1.0 / (3 * T_max_post)

# Sub-window lengths
T_pre = 94
T_post = 76

# -----------------------------------------------------------------------------
# Calibration of the standard error
# -----------------------------------------------------------------------------

# The Proposition 4.2 bias formula at leading order:
#     E[|hat lambda_null|] - 1 = -(1) * sigma_eps^2 * Q / N_eff + o(1/N_eff)
# where Q = psi_null^T C_XX^{-1} phi_null is the per-mode quadratic form.
# The observed left-hand side IS the leading-order bias when noise is iid;
# it also serves as the typical SE under the heuristic approximation
#     SE(|hat lambda|) ~ |bias on a known-true mode at the same N_eff|.
# That is, the bias on the null mode at given N_eff is informative about
# the precision-floor for any mode at the same N_eff.

# Estimated bias = (sigma_eps^2 * Q) / N_eff
# Pre-war:  bias_pre = 1 - lambda_obs_pre = 0.0064
# Post-war: bias_post = 1 - lambda_obs_post = 0.0297

bias_pre = 1.0 - lambda_obs_pre
bias_post = 1.0 - lambda_obs_post

# Calibrated quantity sigma_eps^2 * Q (we cannot separate them)
sQ_pre = bias_pre * N_eff_pre   # = 0.0064 * 467 = 2.99
sQ_post = bias_post * N_eff_post  # = 0.0297 * 210 = 6.24

print("Calibration of the noise scale (sigma_eps^2 * Q):")
print(f"  Pre-war:  sigma_eps^2 * Q = {sQ_pre:.2f}")
print(f"  Post-war: sigma_eps^2 * Q = {sQ_post:.2f}")
print()

# Standard error on |hat lambda_j|:
#   SE(|hat lambda_j|) ~ |lambda_j| * sigma_eps^2 * Q / N_eff
# (For modes near the unit circle, |lambda_j| ~ 1, so this is essentially
# the same magnitude as the null-mode bias.)
# As an approximation, we use the bias itself as a proxy for the SE on
# leading-mode moduli.
SE_pre = bias_pre
SE_post = bias_post

# -----------------------------------------------------------------------------
# Minimum detectable decay time
# -----------------------------------------------------------------------------

# A mode is "detectable" at 95% confidence if its expected |lambda|
# exceeds the threshold by at least 2 SE.
# |lambda| = exp(-1/tau_decay) for a mode with decay time tau_decay years.
# Requirement: exp(-1/tau_min) - 2*SE >= threshold
#  ==> exp(-1/tau_min) >= threshold + 2*SE
#  ==> tau_min >= -1 / log(threshold + 2*SE)
#
# But the alternative formulation uses linear approximation:
# |lambda| ~ 1 - 1/tau_decay, so the condition becomes
#   1 - 1/tau_min - 2*SE >= 1 - 1/(3*T_max)
#   ==> 1/tau_min <= 1/(3*T_max) - 2*SE
#   ==> tau_min >= 1 / (1/(3*T_max) - 2*SE)
# This requires (1/(3*T_max) - 2*SE) > 0, i.e., 2*SE < 1/(3*T_max).
# If 2*SE >= 1/(3*T_max), then even infinitely-persistent modes cannot
# be distinguished from sub-threshold modes given the available precision.

print("=" * 70)
print("MINIMUM DETECTABLE DECAY TIME (95% confidence, exact form)")
print("=" * 70)
print()

for sw_name, threshold, SE, T_window, T_max in [
    ("Pre-war 1820-1913", thr_pre, SE_pre, T_pre, T_max_pre),
    ("Post-war 1945-2020", thr_post, SE_post, T_post, T_max_post)
]:
    print(f"  {sw_name}:")
    print(f"    Q1 threshold (1 - 1/(3 T_max))   = {threshold:.4f}")
    print(f"    Estimated SE on |hat lambda|      = {SE:.4f}")
    print(f"    2 * SE                            = {2*SE:.4f}")
    print(f"    1 / (3 * T_max)                   = {1/(3*T_max):.4f}")
    # Detectability check
    margin = 1/(3*T_max) - 2*SE
    if margin > 0:
        tau_min_linear = 1.0 / margin
        # Exact form
        lambda_required = threshold + 2*SE
        if lambda_required >= 1.0:
            tau_min_exact = float('inf')
        else:
            tau_min_exact = -1.0 / np.log(lambda_required)
        print(f"    Minimum detectable decay time     = {tau_min_exact:.1f} years")
        print(f"    Window length T_window            = {T_window} years")
        print(f"    Ratio tau_min / T_window          = {tau_min_exact/T_window:.2f}")
        print(f"    Interpretation: only modes with decay time >= {tau_min_exact:.0f} yr")
        print(f"                    are detectable above Q1 threshold at 95% CI.")
    else:
        print(f"    Margin (1/(3*T_max) - 2*SE) = {margin:.4f} <= 0")
        print(f"    Interpretation: the noise floor exceeds the Q1 threshold's")
        print(f"    distance from unit modulus. Even genuinely neutral modes")
        print(f"    (|lambda| = 1) cannot be reliably distinguished from")
        print(f"    sub-threshold modes given the available precision.")
        print(f"    The Q1 test has effectively zero power on this sub-window.")
    print()

# -----------------------------------------------------------------------------
# Reverse direction: at what N_eff would the test have adequate power?
# -----------------------------------------------------------------------------

print("=" * 70)
print("WHAT N_eff WOULD BE REQUIRED FOR ADEQUATE POWER?")
print("=" * 70)
print()
print("To detect a mode with decay time tau_target, the test needs:")
print("    SE on |hat lambda| <= [1/(3 T_max) - 1/tau_target] / 2")
print()
print("Assuming sigma_eps^2 * Q (the calibrated noise scale) is constant:")
print()

# Targets
targets = [50, 75, 100, 150, 200]

for sw_name, sQ, T_max, T_window in [
    ("Pre-war 1820-1913", sQ_pre, T_max_pre, T_pre),
    ("Post-war 1945-2020", sQ_post, T_max_post, T_post)
]:
    print(f"  {sw_name} (current N_eff = "
          f"{N_eff_pre if 'Pre' in sw_name else N_eff_post}):")
    for tau_target in targets:
        if tau_target <= T_window:
            continue  # below window length is meaningless
        # Required SE
        target_margin = 1/(3*T_max) - 1/tau_target
        if target_margin <= 0:
            print(f"    tau = {tau_target}y: not detectable above threshold")
            continue
        required_SE = target_margin / 2
        # required N_eff = sQ / required_SE
        N_required = sQ / required_SE
        ratio = N_required / (N_eff_pre if 'Pre' in sw_name else N_eff_post)
        print(f"    decay tau = {tau_target}y: needs N_eff >= {N_required:.0f} "
              f"({ratio:.1f}x current)")
    print()
