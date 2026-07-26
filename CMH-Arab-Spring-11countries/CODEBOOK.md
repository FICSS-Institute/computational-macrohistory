# Codebook — `panel_11countries_2000-2012.csv`

Replication panel for **WP-2026-004** (v2.3), Foundations Institute of Computational Social Science.
Author: Stefano Angeli. Compiled January to February 2026; provenance documented July 2026.

143 rows: 11 countries × 13 years (2000–2012), no missing values.

---

## 1. Columns

| Column | Type | Definition |
|---|---|---|
| `Year` | integer | Calendar year, 2000 to 2012 |
| `Country` | string | Country name, English short form |
| `D2_YouthBulge_pct` | float, 2 dp | Youth bulge: population aged 15–24 as a percentage of total population |
| `E2_Gini` | float, 2 dp | Gini coefficient × 100 |
| `E4_YouthUnemp_pct` | float, 2 dp | Youth unemployment rate, ages 15–24, percentage of the labour force in that band |
| `P1_Polity` | integer | Polity5 `polity2` score, −10 to +10 |
| `S3_InternetPentr_pct` | float, 2 dp | Individuals using the internet, percentage of population |
| `A_AnocracyStress` | float | Derived: `1 − |P1_Polity| / 10`. Ranges 0 (full democracy or full autocracy) to 1 (pure anocracy) |
| `SSI` | float, 6 dp | Derived: the Systemic Stress Index. See §4 |
| `Outcome` | string | Most severe political outcome observed 2011–2012 |
| `Outcome_Binary` | integer | 1 = severe instability (revolution or civil war); 0 = all other outcomes |

`A_AnocracyStress` and `SSI` are derived columns, retained for convenience. Both are fully determined by the five raw columns and the parameters of §4, and `scripts/reproduce_results.py` verifies that all 143 `SSI` values reproduce exactly.

The `SSI` column is stored at six decimal places. Earlier releases of this file stored it at two, which contradicted the three-decimal panel printed in Appendix A of the paper and made the threshold argument of Section 5 unverifiable from the CSV. That is corrected here.

---

## 2. Countries and outcomes

| Country | Outcome 2011–2012 | Binary |
|---|---|---|
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

The binary coding separates severe instability, meaning revolution or civil war, from everything else. Protest that was contained, suppressed, or defused by concession counts as 0. Section 3.1 of the paper discusses the coding and its consequences; the treatment of Morocco and Jordan as non-events is the choice most open to challenge.

---

## 3. Sources

All five source exports are in `data/source_files/` exactly as downloaded.

### D₂ — Youth bulge

**File:** `D2_YouthBulge_data_for_calculation.xlsx`
**Source:** World Bank, World Development Indicators (DataBank), underlying UN World Population Prospects estimates
**Series:** `SP.POP.1519.FE.5Y`, `SP.POP.2024.FE.5Y`, `SP.POP.1519.MA.5Y`, `SP.POP.2024.MA.5Y` (band shares by sex), with `SP.POP.0014.FE.IN`, `SP.POP.1564.FE.IN`, `SP.POP.65UP.FE.IN` and the male equivalents (absolute counts by sex)
**Database last updated:** 28 January 2026
**Query:** https://databank.worldbank.org/source/world-development-indicators
**Aggregation:** required; see §5. The WDI does not publish the 15–24 share of total population directly.

### E₂ — Gini coefficient

**File:** `E2_GINI2000-12_wiid-data-map-chart.xlsx`
**Source:** UNU-WIDER, **World Income Inequality Database (WIID) Companion dataset** (`wiidcountry`), version 30 June 2022
**DOI:** [10.35188/UNU-WIDER/WIIDcomp-300622](https://doi.org/10.35188/UNU-WIDER/WIIDcomp-300622)
**Reproducible query:**
`https://www4.wider.unu.edu/?ind=1&type=ChoroplethSeq&year=62&iso=DZA,BHR,EGY,JOR,KWT,MAR,OMN,SAU,SYR,TUN,YEM&byCountry=false&slider=buttons`

The Companion is a distinct product from the WIID proper and this distinction matters for interpretation. The WIID reports survey observations together with the gaps they leave. The Companion supplies complete annual coverage for every country by model imputation. Every value in this column is therefore a model estimate, and the completeness of the column is a property of the source product and not of the underlying survey record. See §6.

### E₄ — Youth unemployment

**File:** `E4_Youth_Unemployment.xlsx`
**Source:** World Bank WDI, mirroring the ILO Modelled Estimates database (ILOEST)
**Series code:** `SL.UEM.1524.ZS`
**Definition (source):** share of the labour force aged 15–24 without work but available for and seeking employment
**ILOSTAT accessed:** 17 January 2026 · **WDI last updated:** 28 January 2026
**License:** CC BY-4.0

Modelled estimates, not direct survey observations. The ILO imputes where national labour-force surveys are absent or non-comparable, which is frequently the case in this region.

### P₁ — Polity score

**File:** `P1_Polity.xls`, sheet `p5v2018`
**Source:** Center for Systemic Peace, Polity5: Political Regime Characteristics and Transitions, 1800–2018
**Variable:** `polity2` (the revised, interpolated combined score, −10 to +10)
**Coverage note:** the Polity5 release ends in 2018, which fully covers the 2000–2012 window.

### S₃ — Internet penetration

**File:** `S3_Internet_Use___of_population.xlsx`
**Source:** World Bank WDI, mirroring the ITU World Telecommunication/ICT Indicators database
**Series code:** `IT.NET.USER.ZS`
**WDI last updated:** 28 January 2026

---

## 4. Index construction

Reference parameters and weights, Table 2 of the paper, taken unchanged from WP-2026-003 Table 5:

| Component | μ | σ | Weight | Reference window |
|---|---|---|---|---|
| D₂ | 22.5 | 4.5 | 0.15 | 1960–2010 |
| E₂ | 40.0 | 8.0 | 0.25 | long-run estimated distribution |
| E₄ | 18.0 | 8.0 | 0.25 | 1990–2010 |
| A | 0.5 | 0.3 | 0.25 | theoretical distribution over the Polity scale |
| S₃ | 15.0 | 20.0 | 0.10 | 2000–2010 |

The reference window differs by component for reasons of data availability. The parameters are conventional reference values fixed before contact with the data, not moments estimated from any specified country set.

Three steps:

1. `A = 1 − |P₁| / 10`
2. `z(X) = (X − μ) / σ` for each of the five components
3. `SSI = Σ sᵢ wᵢ z(Xᵢ)` with all signs `sᵢ = +1` in the baseline:

```
SSI = 0.15·z(D₂) + 0.25·z(E₂) + 0.25·z(E₄) + 0.25·z(A) + 0.10·z(S₃)
```

The signed form follows WP-2026-002 §4.7. The sign on S₃ is the one the theory leaves open; Section 6.2 of the paper reports that this sample rejects the positive assignment.

---

## 5. The D₂ aggregation

The WDI reports the 15–19 and 20–24 bands as shares of the population of the **same sex**, not of the total. The youth bulge is therefore reconstructed by weighting each sex-specific share by that sex's total population, itself rebuilt from the three absolute age-band counts:

```
        Σ_g ( p_g[15–19] + p_g[20–24] ) · N_g
D₂ = 100 · ─────────────────────────────────────
                     Σ_g N_g

where  N_g = N_g[0–14] + N_g[15–64] + N_g[65+]
       g ∈ {female, male}
       p_g expressed as a fraction
```

This procedure reproduces all 143 deposited values to within 0.015 percentage points. It is implemented in `scripts/build_panel.py`. No earlier release of this codebook stated it, and the definition alone is not sufficient to replicate the column.

---

## 6. Known data-quality issues

### 6.1 The Gini component is imputed across the panel

This is the most consequential limitation in the dataset and it is a property of the source, not of the extraction.

- For **nine of the eleven countries** the 2010 value, on which the paper's benchmark classification rests, lies on a smooth interpolation between two or three anchor points rather than at an anchor.
- **Algeria's** entire thirteen-year series is a single straight line, slope −0.363 per year.
- **Tunisia's** series is two straight segments meeting at 2006.
- **Kuwait** carries one constant value, 40.41, in all thirteen years.
- **Syria** is constant at 35.12 from 2007 to 2012.
- **Bahrain and Saudi Arabia carry identical values in every year of the panel, to six decimal places.** The imputation assigns the two states the same predicted series; neither has usable survey coverage.

A component constructed as a smooth function of two or three anchor points per country cannot, by construction, carry information about a single event year. This is the mechanism behind the leave-one-component-out result: excluding E₂ *improves* measured discrimination, from 20 to 22 correct pairs.

Sensitivity was checked directly. The Bahraini Gini would have to rise by roughly ten points to alter a single pairwise ordering and by nineteen to alter its own classification. Neither magnitude is plausible, so the reported results are robust to the defect even though the component is uninformative.

### 6.2 Known reconstruction differences

Re-extracting the panel from the source files with a consistent half-up rounding rule reproduces 706 of the 715 cells exactly. Nine cells differ, all on E₄, by 0.01 to 0.03:

| Country | Year | Deposited | Re-extracted |
|---|---|---|---|
| Egypt | 2000 | 24.99 | 25.00 |
| Egypt | 2003 | 29.43 | 29.40 |
| Egypt | 2004 | 28.37 | 28.35 |
| Egypt | 2005 | 31.24 | 31.22 |
| Saudi Arabia | 2003 | 24.46 | 24.44 |
| Saudi Arabia | 2004 | 25.09 | 25.08 |
| Saudi Arabia | 2005 | 25.81 | 25.80 |
| Saudi Arabia | 2010 | 24.76 | 24.74 |
| Tunisia | 2003 | 30.67 | 30.66 |

These are rounding-boundary artefacts of the original manual extraction and follow no single rule. Their effect on the results was measured: group separation moves from 0.289513 to 0.289602, both printing as 0.290; the correct-pairs statistic is 20 of 28 under both; no threshold interval, ranking or classification changes. The single visible consequence is that the Saudi Arabian 2010 index value prints as −0.094 in the canonical panel and would print as −0.095 under re-extraction.

The deposited panel is retained as canonical because it is the series from which every value printed in the paper was computed. `scripts/build_panel.py` exists so that a replicator can see exactly this discrepancy rather than discover it.

### 6.3 Other component limitations

**E₄** is an ILO modelled estimate, not a survey observation, in most country-years of this region.

**P₁** enters the index only through the symmetric transformation `A = 1 − |P₁|/10`, which by construction assigns identical institutional vulnerability to states equidistant from the centre of the Polity scale on opposite sides. Algeria in 2010 scores +2 and Yemen −2, and both therefore receive `A = 0.8`. Section 4.1 of the paper discusses whether that indifference is defensible; the Vreeland critique of the Polity aggregate is noted and deferred.

**S₃** is standardised against a 2000–2010 reference window that coincides with the steepest phase of internet diffusion. A terminal-year cross-section drawn from a decade of monotone growth necessarily sits in the upper tail of its own reference distribution, which is why every 2010 standardised value is high and why the component carries little discriminating variance. Section 6.1 of the paper treats this as a failure of the comparability condition of Axiom A2, internal to the reference window.

---

## 7. Material examined and not used

`data/explored_not_used/WID_Data_19022026-104718.xlsx` contains series `ghweal999j`, the **net personal wealth Gini**, from the World Inequality Database (wid.world), downloaded 19 February 2026, for Algeria, Egypt and Kuwait only. It is a wealth Gini, not an income Gini, and its values (0.74 to 0.79) are on a different scale and measure a different quantity from the `E2_Gini` column (29 to 47).

**It was not used.** None of its values appears in the panel. It is retained and segregated here so that a replicator finding it in the working folder does not mistake it for the E₂ source.

---

## 8. Licensing

Code in this folder is MIT-licensed. Data are redistributed under their original terms: World Bank WDI under CC BY-4.0; UNU-WIDER WIID Companion under the UNU-WIDER terms of use; Polity5 under the Center for Systemic Peace terms. Users redistributing these data should cite the original providers, not this repository.

---

## 9. Change log for this folder

**July 2026, aligned to paper v2.3.** Author corrected from the former pseudonym to Stefano Angeli throughout. E₂ source corrected from "UNU-WIDER WIID" to the WIID Companion dataset, with its own DOI and reproducible query. Reference window corrected from "1980–2010", which appears in no canonical source, to the component-specific windows of WP-2026-003 Table 5. Anocracy notation corrected from `AS` to `A`, matching WP-2026-002 and WP-2026-003. Panel `SSI` column moved from two to six decimal places. Added: the D₂ aggregation formula, indicator codes, dataset versions, access dates, the reproducible WIID query, the source files as downloaded, the disclosure of the Bahrain and Saudi Arabia identity and of the Companion imputation, the reconstruction-difference table, the segregated unused WID file, the reproduction and verification scripts, and the full permutation null distribution.
