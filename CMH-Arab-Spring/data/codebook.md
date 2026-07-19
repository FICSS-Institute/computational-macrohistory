---
related:
  - "[[WP-2026-003_Arab-Spring-3nations_v2_0]]"
  - "[[SSI_Operational]]"
---

# Codebook — CMH Arab Spring Dataset

**Dataset**: `arab_spring_data.csv`  
**Coverage**: Tunisia, Egypt, Saudi Arabia | 2000–2012  
**Observations**: 195 (3 countries × 5 variables × 13 years)  
**Last updated**: July 2026 (aligned with paper v3.1: D₂ stated definition corrected to 15–24 after source verification; no data values changed)

---

## Dataset Structure

Each row in `arab_spring_data.csv` represents one country-year observation.

| Column | Type | Description |
|--------|------|-------------|
| `country` | string | Country name (Tunisia / Egypt / Saudi Arabia) |
| `iso3` | string | ISO 3166-1 alpha-3 code (TUN / EGY / SAU) |
| `year` | integer | Calendar year (2000–2012) |
| `d2_youth_bulge` | float | Youth Bulge (D₂) |
| `e2_gini` | float | Gini Coefficient (E₂) |
| `e4_youth_unemployment` | float | Youth Unemployment Rate (E₄) |
| `p1_polity` | integer | Polity Score (P₁) |
| `s3_internet` | float | Internet Penetration (S₃) |
| `data_quality` | string | Data quality flag (see below) |

---

## Variable Definitions

### D₂ — Youth Bulge

- **Definition**: Percentage of total population aged 15–24 years
- **Unit**: Percentage (%)
- **Range**: 0–100
- **Source**: World Bank Open Data — Population estimates (UN)
  - Age bands: `SP.POP.1519.MA.5Y` / `SP.POP.1519.FE.5Y` (15–19) and `SP.POP.2024.MA.5Y` / `SP.POP.2024.FE.5Y` (20–24), each as % of the respective sex population, summed and population-weighted
  - URL: https://data.worldbank.org
- **Operationalization**: (Population aged 15–24) / (Total population) × 100
- **CMH rationale**: Proxy for demographic pressure and potential for collective mobilization (Goldstone 1991; Turchin 2016)
- **Missing values**: None for this dataset (UN estimates available for all years)
- **Definition history**: versions 1.0–3.0 of WP-2026-003 described the band as 15–29; v3.1 (July 2026) corrected the description after verification of the deposited series against the source age bands confirmed the values are computed over ages 15–24 (canonical CMH definition). No data values changed.

---

### E₂ — Gini Coefficient

- **Definition**: Gini index of income inequality among individuals or households
- **Unit**: Index on the 0–100 scale (0 = perfect equality, 100 = maximum inequality)
  - Note: some sources express the Gini as 0–1; values in this dataset and in the paper are on the 0–100 scale (e.g. Tunisia 2010 = 42.95)
- **Source (primary)**: Standardized World Income Inequality Database (SWIID v9.0), supplemented by World Bank WDI where SWIID data unavailable (paper §4.5.3)
- **Source (secondary)**: World Bank Poverty and Inequality Platform; UNU-WIDER World Income Inequality Database (WIID), used for cross-checks
  - URL: https://www.wider.unu.edu/database/world-income-inequality-database-wiid
- **Operationalization**: Direct use of reported Gini index; when multiple surveys available for same year, consumption-based estimate preferred over income-based
- **Missing values**: Gini data are sparse (survey-based, not annual). Gaps filled by:
  1. Linear interpolation between available survey years (flagged as `interpolated`)
  2. For Saudi Arabia 2008–2010: insufficient data — see `data_quality` flag
- **Known issues**: Saudi Arabia Gini data availability limited; treat Saudi E₂ estimates with caution

---

### E₄ — Youth Unemployment Rate

- **Definition**: Percentage of the labor force aged 15–24 that is unemployed
- **Unit**: Percentage (%)
- **Range**: 0–100
- **Source**: International Labour Organization (ILO) ILOSTAT
  - Indicator: `UNE_2EAP_SEX_AGE_RT_A` (Unemployment rate by sex and age)
  - URL: https://ilostat.ilo.org
- **Operationalization**: ILO modeled estimates used where national survey data unavailable; both sexes combined
- **Missing values**: ILO modeled estimates available for all country-years in this dataset

---

### P₁ — Polity Score

- **Definition**: Combined Polity Score measuring the degree of democracy vs. autocracy of a political regime
- **Unit**: Integer scale, –10 (hereditary monarchy/full autocracy) to +10 (full democracy)
- **Source**: Polity V Project, Center for Systemic Peace
  - Dataset: `p5v2018.sav` / annual CSV
  - URL: https://www.systemicpeace.org/polityproject.html
  - Reference: Marshall, Gurr & Jaggers (2018). *Polity IV Project: Political Regime Characteristics and Transitions, 1800–2018*
- **Operationalization**: Direct use of `polity2` variable (preferred over raw `polity` for transitional periods)
- **Special codes**:
  - `-66`: Interruption (foreign occupation, etc.) — recoded as missing
  - `-77`: Interregnum — recoded as missing
  - `-88`: Transition — recoded as missing; linear interpolation applied if brief
- **Missing values**: None in this dataset after standard recoding

---

### S₃ — Internet Penetration

- **Definition**: Percentage of individuals using the internet
- **Unit**: Percentage (%)
- **Range**: 0–100
- **Source (primary)**: International Telecommunication Union (ITU) — ICT Statistics
  - URL: https://www.itu.int/en/ITU-D/Statistics
- **Source (secondary)**: World Bank Open Data
  - Indicator: `IT.NET.USER.ZS`
  - URL: https://data.worldbank.org
- **Operationalization**: Direct use of reported values; ITU definition: "An individual who has used the Internet (from any location) in the last 3 months"
- **Missing values**: Linear interpolation for isolated missing years

---

## Data Quality Flags

| Flag | Meaning |
|------|---------|
| `observed` | Directly reported by primary source |
| `interpolated` | Linearly interpolated between two observed values |
| `estimated` | ILO modeled estimate or secondary source estimate |
| `uncertain` | Data quality concerns (see notes); use with caution |

**Row-level assignment (v3.1):** the flag records the most severe caveat affecting the row, with E₂ interpolation taking precedence. D₂, P₁, and S₃ are observed institutional series in all rows; E₂ is SWIID model-based except where interpolated; E₄ is an ILO modeled series throughout. Every row is therefore at least `estimated`; Saudi Arabia 2008–2010, where E₂ was filled by linear interpolation, is flagged `interpolated`.

---

## Outcome Variable (not in CSV — for reference)

The outcome variable used in the paper is binary:

| Country | Outcome (2010–2012) |
|---------|---------------------|
| Tunisia | 1 (Revolutionary transition — Ben Ali removed Jan 2011) |
| Egypt | 1 (Revolutionary transition — Mubarak removed Feb 2011) |
| Saudi Arabia | 0 (Regime stability maintained) |

Source: NAVCO 2.1 (Nonviolent and Violent Campaigns and Outcomes) + qualitative coding.

---

## Known Limitations

1. **Small N**: Three countries is insufficient for formal statistical inference. Analyses in Document III are explicitly exploratory and descriptive.
2. **Gini sparsity**: Income inequality data are survey-based and not available annually for all countries. Interpolated values reduce precision.
3. **Measurement validity**: Polity V and Freedom House scores reflect coder judgments and may not capture within-year variation.
4. **Endogeneity**: Internet penetration and protest activity may be mutually causal; causal claims limited accordingly.
5. **Selection on observables**: Three countries were selected to maximize variation on outcome, not as a random sample of MENA states.

---

## References

- Goldstone, J.A. (1991). *Revolution and Rebellion in the Early Modern World*. University of California Press.
- Marshall, M.G., Gurr, T.R., & Jaggers, K. (2018). *Polity IV Project Dataset Users' Manual*. Center for Systemic Peace.
- Turchin, P. (2016). *Ages of Discord*. Beresta Books.
- UNU-WIDER (2021). World Income Inequality Database (WIID). Version 31 May 2021.
