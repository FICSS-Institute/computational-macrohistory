# CMH-Koopman-Western-Europe

Replication materials for working paper **WP-2026-006**: "Koopman–CMH: A Formal Treatment of Spectral Structure Persistence in Historical Dynamics"

Author: Galen Fontaise
Institution: Fontaise Institute of Computational Social Science (FICSS), Lugano
Paper DOI: `10.5281/zenodo.<TBD>` (Zenodo, canonical)
License: MIT (see repository root)

---

## What this paper does

The paper proves the conditional theorem at the core of Conjecture 1 of WP-2026-005 — the Koopman–A2 Correspondence, which connects ergodic-class membership to shared leading Koopman spectrum — and conducts the first empirical test of its substantive antecedent.

A multi-task Hankel-DMD estimator operates on a five-dimensional state vector spanning the demographic, economic, political, and social dimensions of the CMH framework, applied to a panel of eight Western European polities (BEL, DEU, ESP, FRA, GBR, ITA, NLD, SWE) across two structurally stationary sub-windows: 1820–1913 (pre-war) and 1945–2020 (post-war).

Three pre-registered falsification questions are tested. Question 1 — existence of persistent Koopman modes with decay times exceeding three times the longest period resolvable from the sub-window — is rejected in both sub-windows. Questions 2 and 3 are conditional on Q1 admitting and are therefore not evaluated.

The rejection bears primarily on the *detectability* of persistent modes given the present panel's effective sample size and noise structure. Two post-hoc analyses (surrogate test and power calculation) document that the test had effectively zero power against finite-modulus alternatives at the available effective sample size, so the verdict does not license a corresponding claim about the *existence* of such modes in macrohistorical dynamics. The paper records this as the first instance in the CMH programme of an Axiom A8 falsifiability obligation being discharged on a substantive empirical test.

---

## Repository structure

```
CMH-Koopman-Western-Europe/
├── README.md                                  This file
├── data/
│   ├── WP-2026-006_WesternEurope_Panel_v0-1.csv   Harmonised panel, long format
│   └── codebook.md                            Variable definitions, sources, unavailability flags
├── scripts/
│   ├── build_panel.py                         Constructs the CSV from V-Dem, Maddison, COW
│   ├── sanity_check.py                        Validation diagnostics on the produced CSV
│   ├── harmonisation_log.txt                  Per-cell source attribution log
│   ├── WP-2026-006_estimator_v3.py            Production multi-task Hankel-DMD estimator
│   ├── WP-2026-006_robustness.py              Robustness diagnostics (§6.4 of the paper)
│   ├── WP-2026-006_run_v3.log                 Verbatim output of the production run
│   └── WP-2026-006_run_robustness.log         Verbatim output of the robustness run
└── posthoc/
    ├── surrogate_test.py                      Surrogate null test for the §6.3 Juglar-band match
    ├── surrogate_test_results.log             Output of the surrogate test
    ├── power_analysis.py                      Post-hoc power calculation for Question 1
    └── power_analysis_results.log             Output of the power calculation
```

---

## How to reproduce the empirical results

The pipeline requires Python 3.12, NumPy 1.26, SciPy 1.13, and pandas 2.2. No additional dependencies are required beyond the standard scientific Python stack. The pipeline runs on a contemporary laptop in approximately one minute total without GPU or specialised hardware.

### Step 1 — Verify the CSV (optional)

```bash
cd scripts
python sanity_check.py
```

This runs validation diagnostics on `data/WP-2026-006_WesternEurope_Panel_v0-1.csv` and confirms the per-country listwise-complete counts, the sub-window assignments, and the systematic-unavailability flags documented in the codebook.

### Step 2 — Run the production estimator

```bash
cd scripts
python WP-2026-006_estimator_v3.py
```

This produces the multi-task Hankel-DMD spectrum reported in §6.1 and §6.2 of the paper: effective rank $r = 16$ pre-war and $r = 15$ post-war, persistence-threshold verdicts, and the leading mode periods that appear in Tables 3 and 4. The full output is preserved in `WP-2026-006_run_v3.log` for direct comparison.

### Step 3 — Run the robustness diagnostics

```bash
cd scripts
python WP-2026-006_robustness.py
```

This produces the diagnostics of §6.4: condition numbers $\kappa_W$, per-mode misalignment statistics for the local-normality hypothesis (v) of Theorem 1, cross-country residual correlations $\overline{\rho}$ for the conditional-independence hypothesis of Proposition 4.1, and the effective-sample-size diagnostic of Proposition 4.4. The full output is preserved in `WP-2026-006_run_robustness.log`.

### Step 4 — Run the post-hoc analyses

```bash
cd posthoc
python surrogate_test.py
python power_analysis.py
```

The surrogate test computes the null distribution of cross-window matches in the 5-to-9 year band under an AR(1)-plus-common-shock null calibrated to the literature-based persistence parameters of the five variables. The power analysis computes the precision floor on $|\hat\lambda|$ implied by the observed attenuation of the invariant-measure mode, and from it the effective sample size that would be required for the Q1 test to have meaningful power against finite-modulus alternatives.

These two analyses are *post-hoc* — neither was part of the §5 pre-registration — and are reported in §6.8 of the paper as such. The full outputs are preserved in `surrogate_test_results.log` and `power_analysis_results.log`.

### Step 5 — Regenerate the CSV from primary sources (optional)

To regenerate `data/WP-2026-006_WesternEurope_Panel_v0-1.csv` from scratch, place the V-Dem v16 country-year CSV, the Maddison Project 2023 release, and the Correlates of War NMC v6.0 release in the local working directory and run:

```bash
cd scripts
python build_panel.py
```

The script reads the three source CSVs, applies the harmonisation logic documented in `harmonisation_log.txt`, applies the systematic-unavailability flags listed in the codebook, and writes the panel CSV.

---

## Implementation history

The paper documents that the production estimator (v3, the canonical Tu et al. 2014 pipeline with Gavish-Donoho rank truncation) was preceded by two intermediate implementations that produced numerically incoherent spectra:

- **v1** — unprojected multi-task ridge regression in the full Hankel-augmented dimension. Produced eigenvalues with $|\lambda|$ approaching 3, in formal contradiction with the contraction property of the stochastic Koopman operator on $L^2(\mu_\theta)$.
- **v2** — bug-fixes within the unprojected framework. Retained a cross-validation criterion based on Gaussian log-likelihood that was numerically dominated by Hankel-augmented dimensions whose residual variance approached zero at $\lambda = 0$, making the criterion monotone in the regularisation parameter and uninformative for selection.

The pathological behaviour of v1 and v2 is documented in detail in §B.3.1 and §B.3.2 of the paper. The intermediate scripts are not preserved as standalone files in this repository, but their behaviour is reproducible by the targeted modifications to v3 that §B.3 specifies (omission of the SVD-projection step for v1; replacement of the predictive-RMSE cross-validation criterion with the Gaussian log-likelihood criterion for v2).

---

## Pre-registration

The pre-registration in §5 of the paper was completed before data assembly. The pre-registered test specification is unambiguous on Question 1 (existence of persistent modes), the persistence threshold ($1 - 1/(3 T_{\max})$), the Hankel delay ($\tau = 7$), the rank selection criterion (Gavish-Donoho), and the gap selection criterion (multiplicative factor 1.5 on a logarithmic scale between consecutive moduli).

Two deviations from the pre-registration are explicitly disclosed in the paper:

1. **CV criterion shift.** §5.6 specified predictive log-likelihood; the v3 production pipeline uses predictive RMSE per state dimension instead. The shift was forced by the discovery during execution that the log-likelihood criterion is numerically dominated by Hankel-augmented dimensions with near-zero residual variance at $\lambda = 0$, making the criterion monotone in $\lambda$ and uninformative. The deviation is recorded in §6.1 (pre-registration note) and §7.2 (lessons learned).

2. **Post-hoc analyses.** §6.8 reports a surrogate null test for the §6.3 cross-window match and a post-hoc power calculation for the Q1 test. Neither was pre-registered. Both were added during paper revision to address external reviewer concerns about the inferential reach of the Q1 verdict and the sub-threshold cross-window pattern. Both are flagged explicitly as post-hoc throughout §6.8 and §7.1.

The substantive content of the §6 verdicts on Questions 1–3 does not depend on the CV criterion choice because the Gavish-Donoho rank selection is the operative dimensionality control in the canonical pipeline; the post-hoc analyses qualify the inferential reach of the Q1 verdict but do not change it within its pre-registered terms.

---

## Relationship to the CMH programme

This paper is the sixth working paper in the FICSS Computational Macrohistory series:

- WP-2026-001: Axiomatic Foundations
- WP-2026-002: Operational Framework
- WP-2026-003: Arab Spring (three countries)
- WP-2026-004: Arab Spring (eleven countries)
- WP-2026-005: Beyond the Lyapunov Wall — the original statement of Conjecture 1
- **WP-2026-006: Koopman–CMH (this paper)**

WP-2026-007, currently in scoping, will address the resolvent-norm integration that produces the sharp pseudospectral projection bound (replacing the placeholder $\kappa(V)/\delta_{\mathrm{ps}}$ of Lemma 3.4 b) and the panel extension to twenty to twenty-five countries identified in §7.4. WP-2026-008, also in scoping, will undertake the controlled simulation study with noise structures calibrated to V-Dem, Maddison, and COW that several of the external reviewers identified as the next methodological step.

The umbrella programme repository is at <https://github.com/FICSS-Institute/computational-macrohistory>. The FICSS website is at <https://ficss.institute>. Project blog (long-form expositions): <https://galenfontaise.substack.com>.

---

## Contact

Questions about this replication directory, the paper, or the broader Computational Macrohistory programme:

Galen Fontaise — `galen.fontaise@ficss.institute`

---

*Released under the MIT License. All research in the CMH programme is transparent, reproducible, and explicitly acknowledges uncertainty.*
