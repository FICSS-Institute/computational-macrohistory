# SSI Calculation Procedure

**Systemic Stress Index (SSI) — Computational Macrohistory, Document III**

---

## Overview

The Systemic Stress Index (SSI) is a composite index aggregating five structural variables into a single scalar measure of socio-political stress for a given country-year. It is derived from the CMH Political Stress Index (PSI) framework and operationalized here for the Arab Spring case study.

**SSI range**: 0 (no stress) to 10 (maximum stress)  
**Interpretation**: Higher SSI = greater structural conditions for political instability

---

## Step 1 — Variable Normalization

Each of the five raw variables is normalized to a [0, 1] scale using **min-max normalization** across the full dataset (all 3 countries, all 13 years):

$$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}}$$

**Direction of normalization** (higher normalized value = higher stress):

| Variable | CMH Code | Direction | Rationale |
|----------|----------|-----------|-----------|
| Youth Bulge | D₂ | Higher → Higher stress | Large youth cohort increases mobilization potential |
| Gini Coefficient | E₂ | Higher → Higher stress | Greater inequality increases grievances |
| Youth Unemployment | E₄ | Higher → Higher stress | Economic exclusion drives protest |
| Polity Score | P₁ | **Lower → Higher stress** | More autocratic = less legitimate outlet, higher instability risk |
| Internet Penetration | S₃ | Higher → Higher stress | Facilitates coordination and cascade effects |

**Note on P₁**: The Polity Score is inverted before normalization:
$$P_{1,inv} = -P_1$$
so that P₁ = –10 (full autocracy) maps to normalized value 1.0, and P₁ = +10 (full democracy) maps to 0.

---

## Step 2 — Weighted Aggregation

The SSI is computed as a weighted average of the five normalized variables, scaled to [0, 10]:

$$SSI = 10 \times \sum_{i=1}^{5} w_i \cdot x_{i,norm}$$

**Weights used in Document III** (equal weighting, exploratory baseline):

| Variable | Weight (wᵢ) |
|----------|-------------|
| D₂ (Youth Bulge) | 0.20 |
| E₂ (Gini) | 0.20 |
| E₄ (Youth Unemployment) | 0.20 |
| P₁ (Polity, inverted) | 0.20 |
| S₃ (Internet) | 0.20 |

**Rationale for equal weights**: In the absence of empirical calibration on a sufficiently large sample (N >> 30), equal weighting is the methodologically conservative choice. Differential weighting is planned for Document IV with the expanded 10–11 country dataset.

---

## Step 3 — Temporal Smoothing (Optional)

For time-series visualization, a 3-year centered moving average may be applied to reduce year-to-year noise:

$$SSI_{smooth}(t) = \frac{SSI(t-1) + SSI(t) + SSI(t+1)}{3}$$

Raw (unsmoothed) values are used for all quantitative comparisons in the paper. Smoothed values appear only in Figure 3 (time series plot).

---

## Step 4 — Computation Example

**Tunisia, 2010 (illustrative)**

| Variable | Raw value | Min | Max | Normalized | Weight | Contribution |
|----------|-----------|-----|-----|------------|--------|--------------|
| D₂ | 29.5% | 22.1 | 32.8 | 0.70 | 0.20 | 0.140 |
| E₂ | 0.407 | 0.36 | 0.48 | 0.39 | 0.20 | 0.078 |
| E₄ | 30.2% | 15.8 | 42.6 | 0.53 | 0.20 | 0.106 |
| P₁ | −7 (inv: +7) | −10 (inv) | +10 (inv) | 0.85 | 0.20 | 0.170 |
| S₃ | 34.1% | 0.4 | 60.5 | 0.56 | 0.20 | 0.112 |
| **SSI** | | | | | | **6.06** |

*Note: values above are illustrative; use actual dataset values for replication.*

---

## Limitations and Caveats

1. **Equal weights are provisional**: The weights reflect theoretical priors, not empirical calibration. Results are sensitive to weight specification (acknowledged as a limitation in Section 6.3 of the paper).
2. **Normalization is dataset-dependent**: Min-max normalization using this 3-country dataset will differ from normalization on the expanded 10–11 country dataset in Document IV. SSI values are not directly comparable across papers.
3. **No inferential statistics**: The SSI is an exploratory descriptive tool in Document III. It is not used for hypothesis testing or causal inference.
4. **Missing data propagation**: If any component variable is missing, SSI for that country-year is flagged as missing (no imputation of the composite index itself).

---

## Reference

Fontaise, T. (2025). *CMH Document III: A Quantitative Analysis of the Arab Spring (2010–2012)*. FICSS Working Paper.
