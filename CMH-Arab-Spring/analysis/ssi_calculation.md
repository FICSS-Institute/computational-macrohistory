# SSI Calculation Procedure — CMH Arab Spring (WP-2026-003)

**Applies to:** *Computational Macrohistory: Exploratory Empirical Application — The Arab Spring as a Preliminary Test Case for Structural-Demographic Theory*, v2.0 (May 2026).
**Supersedes:** the earlier version of this file, which documented an exploratory equal-weight, min-max specification that does not correspond to the published paper. The procedure below reproduces the published results exactly.

---

## Step 1 — Input variables

Five variables per country-year (see `data/codebook.md`):

| Code | Variable |
|------|----------|
| D₂ | Youth Bulge (% population aged 15–29) |
| E₂ | Gini coefficient (0–100 scale) |
| E₄ | Youth unemployment rate (% of labor force aged 15–24) |
| P₁ | Polity score (−10 to +10) |
| S₃ | Internet penetration (% of population) |

## Step 2 — Anocracy Stress transformation

The Polity score is transformed to capture the inverted-U relationship between regime type and instability risk:

```
Anocracy Stress (AS) = 1 − |P₁| / 10
```

AS = 1.0 at P₁ = 0 (pure anocracy); AS = 0.0 at P₁ = ±10 (pure democracy or pure autocracy).
Examples (2010): Tunisia P₁ = −4 → AS = 0.6; Egypt P₁ = −3 → AS = 0.7; Saudi Arabia P₁ = −10 → AS = 0.0.

## Step 3 — Z-score standardisation

Each component is standardised against MENA regional reference parameters (paper, Appendix B.2):

```
z = (X − μ) / σ
```

| Component | μ | σ | Reference population |
|-----------|------|------|----------------------|
| D₂ (%) | 22.5 | 4.5 | MENA average 1960–2010 |
| E₂ (Gini, 0–100) | 40.0 | 8.0 | MENA average (estimated) |
| E₄ (%) | 18.0 | 8.0 | MENA average 1990–2010 |
| Anocracy Stress | 0.5 | 0.3 | Theoretical distribution |
| S₃ (%) | 15.0 | 20.0 | MENA average 2000–2010 |

## Step 4 — Weighted aggregation

Weights are theory-derived (structural-demographic theory; paper §2.5.2 and §5.1.4), not estimated from data:

```
SSI = 0.15·z(D₂) + 0.25·z(E₂) + 0.25·z(E₄) + 0.25·z(AS) + 0.10·z(S₃)
```

## Worked example — Tunisia 2010

| Component | Raw value | z-score | Weight | Contribution |
|-----------|-----------|---------|--------|--------------|
| D₂ | 18.64% | −0.86 | 0.15 | −0.13 |
| E₂ | 42.95 | +0.37 | 0.25 | +0.09 |
| E₄ | 29.57% | +1.45 | 0.25 | +0.36 |
| AS (P₁ = −4) | 0.60 | +0.33 | 0.25 | +0.08 |
| S₃ | 36.8% | +1.09 | 0.10 | +0.11 |
| **SSI** | | | | **0.52** |

Benchmark values (2010): Tunisia **0.52**, Egypt **0.10**, Saudi Arabia **−0.09**. Threshold SSI > 0 separates revolutionary from stable outcomes in this sample.

## Robustness conventions (paper §6.10 and Appendix C, v2.0)

- **Weight variation (±30%):** the varied component takes w·(1±0.30); the remaining four weights are rescaled proportionally so the five weights sum to 1.0.
- **Leave-one-variable-out:** the excluded component's weight is set to zero and the remaining four weights are rescaled proportionally to sum to 1.0 (standard rescaled convention; Tables 6.10.2 and C.2 are identical under this convention in v2.0).

## Interpretive notes

1. **Weights are theory-derived, not calibrated.** With N = 3, any data-driven weighting would be meaningless. Sensitivity to the weighting scheme is reported in Appendix C.1 of the paper: equal-weight and economic-emphasis schemes break discrimination; the baseline and regime-emphasis schemes preserve it.
2. **The SSI is a static approximation** (quasi-steady state) of the CMH dynamic system; see paper §2.6.
3. **Results are exploratory.** N = 3 precludes statistical validation; see paper §8.

---

## Reference

Fontaise, G. (2026). *Computational Macrohistory: Exploratory Empirical Application — The Arab Spring as a Preliminary Test Case for Structural-Demographic Theory* (Working Paper WP-2026-003, v2.0). Fontaise Institute of Computational Social Science. DOI (v1.0): 10.5281/zenodo.18848734.
