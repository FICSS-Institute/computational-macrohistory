# Codebook: SSI_11countries_2000-2012.csv

## Dataset Description

Complete dataset for the eleven-country Arab Spring analysis.
Computed as part of WP-2026-004 (Fontaise 2026).

**File**: `raw_data_11countries_2000-2012.csv`
**DOI**: https://doi.org/10.5281/zenodo.19661257

## Variables

| Variable | Type | Description |
|----------|------|-------------|
| Year | Integer | Calendar year (2000–2012) |
| Country | String | Country name (11 MENA countries, English) |
| D2_YouthBulge_pct | Float | Youth bulge: population aged 15–24 as % of total |
| E2_Gini | Float | Gini coefficient × 100 |
| E4_YouthUnemp_pct | Float | Youth unemployment rate (ages 15–24, %) |
| P1_Polity | Integer | Polity V score (−10 to +10) |
| S3_InternetPentr_pct | Float | Internet penetration (% of population) |
| SSI | Float | Computed Systemic Stress Index |
| Outcome | String | Most severe political outcome observed 2011–2012 |
| Outcome_Binary | Integer | 1 = severe instability (revolution or civil war); 0 = otherwise |

## SSI Formula

```
SSI(t) = 0.15·z(D₂) + 0.25·z(E₂) + 0.25·z(E₄) + 0.25·z(AS) + 0.10·z(S₃)
```

Where:
- z(X) = (X − μ) / σ using MENA historical reference parameters (1980–2010)
- D₂ = Youth Bulge (population aged 15–24 as % of total population)
- E₂ = Gini coefficient × 100
- E₄ = Youth unemployment rate (ages 15–24, %)
- AS = Anocracy Stress = 1 − |P₁|/10 (P₁ = Polity V score)
- S₃ = Internet penetration (% of population)

## Reference Parameters

| Component | μ (MENA mean) | σ (MENA SD) | Weight |
|-----------|---------------|-------------|--------|
| D₂ | 22.5 | 4.5 | 0.15 |
| E₂ | 40.0 | 8.0 | 0.25 |
| E₄ | 18.0 | 8.0 | 0.25 |
| AS | 0.5 | 0.3 | 0.25 |
| S₃ | 15.0 | 20.0 | 0.10 |

## Countries and Outcomes

| Country | Outcome | Binary |
|---------|---------|--------|
| Algeria | Protest contained | 0 |
| Bahrain | Protest suppressed | 0 |
| Egypt | Revolution | 1 |
| Jordan | Reform avoided | 0 |
| Kuwait | Stable | 0 |
| Morocco | Reform avoided | 0 |
| Oman | Protest contained | 0 |
| Saudi Arabia | Stable | 0 |
| Syria | Civil war | 1 |
| Tunisia | Revolution | 1 |
| Yemen | Civil war | 1 |

## Data Sources

- D₂: World Bank World Development Indicators
- E₂: UNU-WIDER World Income Inequality Database (WIID)
- E₄: World Bank WDI / ILO modelled estimates
- P₁: Polity V Dataset (Center for Systemic Peace)
- S₃: World Bank WDI

## Notes

- Kuwait E₂ is a constant academic estimate (40.41) for all years — no annual official data available.
- Syria E₂ is partially interpolated from sparse survey data.
- SSI values rounded to 2 decimal places.
- Pre-event analysis window: 2000–2010. Post-event years (2011–2012) included for completeness.

## Citation

Fontaise, G. (2026). Structural Stress and Political Instability in the MENA Region:
A Computational Macrohistory Analysis of the Arab Spring. FICSS Working Paper
WP-2026-004. https://doi.org/10.5281/zenodo.19661257
