# Codebook — Western European Panel, 1820–2020

**Dataset file:** `WP-2026-006_WesternEurope_Panel_v0-1.csv`
**Format:** long, one row per `(ISO3, year, sub_window, variable)` tuple
**Encoding:** UTF-8
**Total rows:** 1,360 nominal country-years × 5 variables = 6,800 observations (with missingness flagged)
**Working paper:** WP-2026-006, "Koopman–CMH: A Formal Treatment of Spectral Structure Persistence in Historical Dynamics"
**Author:** Galen Fontaise, Fontaise Institute of Computational Social Science (FICSS)

---

## Panel scope

The panel covers eight Western European polities observed annually across two structurally stationary sub-windows. The two World Wars are excluded by a strict cut, on the principle that the structural-stationarity requirement that Theorem 1 of the paper inherits from Axiom A2 of the CMH framework cannot accommodate discontinuities of the magnitude of 1914–1918 or 1939–1944.

| Property | Value |
|---|---|
| Countries | BEL, DEU, ESP, FRA, GBR, ITA, NLD, SWE |
| Sub-window 1 (pre-war) | 1820–1913, 94 years |
| Sub-window 2 (post-war) | 1945–2020, 76 years |
| Variables | pop, gdppc, v2x_libdem, v2x_polyarchy, cinc |
| Nominal coverage | 8 × 170 = 1,360 country-years |
| Listwise-complete | 1,250 (91.9%) |
| Listwise-complete pre-war | 684 / 752 (90.9%) |
| Listwise-complete post-war | 566 / 608 (93.1%) |

---

## Column schema

| Column | Type | Description |
|---|---|---|
| `ISO3` | string | ISO 3166-1 alpha-3 country code |
| `year` | integer | Calendar year, range 1820–2020 (excluding 1914–1944) |
| `sub_window` | string | Either `pre_war` (1820–1913) or `post_war` (1945–2020) |
| `variable` | string | One of `pop`, `gdppc`, `v2x_libdem`, `v2x_polyarchy`, `cinc` |
| `value` | float (nullable) | The variable's value; `NaN` indicates systematic unavailability |
| `source` | string | Primary source attribution: `Maddison`, `V-Dem`, or `COW` |
| `note` | string (nullable) | Optional flag for systematic unavailability (see below) |

---

## Variables

### `pop` — Population

- **CMH dimension:** Demographic (D)
- **Source:** Maddison Project Database 2023 release (Bolt and van Zanden 2024)
- **Unit:** Thousands of persons
- **Temporal coverage:** 1820–2020 (full), with the qualification that pre-1846 Belgian population reflects Maddison's reconstruction
- **Operationalisation:** The simplest D-dimension variable available with full panel coverage over the entire 1820–2020 window; the canonical demographic state variable in CMH treatments

### `gdppc` — GDP per capita

- **CMH dimension:** Economic (E)
- **Source:** Maddison Project Database 2023 release (Bolt and van Zanden 2024)
- **Unit:** 2011 PPP-adjusted US dollars
- **Temporal coverage:** 1820–2020 (full), with the qualification that pre-1846 Belgian GDP per capita is reconstructed rather than directly observed
- **Note on imputation:** The Maddison `i_cgdppc` (interpolation flag) variable was not preserved in the output column structure because the present release does not separate interpolated from observed values in a format the panel-building pipeline could reliably parse; the listwise-complete count includes Maddison-imputed values without explicit flagging (limitation discussed in §8.4 of the paper)

### `v2x_libdem` — Liberal Democracy Index

- **CMH dimension:** Political (P)
- **Source:** V-Dem version 16, November 2025 release
- **Unit:** Continuous index on [0, 1]
- **Temporal coverage:** 1789–present in V-Dem; the panel uses 1820 forward
- **Operationalisation:** Emphasises liberal-constitutional dimensions (rule of law, minority protections, judicial constraints on the executive)

### `v2x_polyarchy` — Electoral Democracy Index

- **CMH dimension:** Political (P)
- **Source:** V-Dem version 16, November 2025 release
- **Unit:** Continuous index on [0, 1]
- **Temporal coverage:** 1789–present in V-Dem; the panel uses 1820 forward
- **Operationalisation:** Emphasises electoral-procedural dimensions (free and fair elections, suffrage extension, freedom of association); conceptually distinct from `v2x_libdem` and tracking different time scales of regime evolution
- **Rationale for two P variables:** P is the dimension in which the Koopman framework's primary predictions of Conjecture 1 were originally formulated, and the two V-Dem indices capture institutional features that move on different time scales. Modes operating on one but not the other would be lost if only one variable were retained.

### `cinc` — Composite Index of National Capability

- **CMH dimension:** Social/structural (S)
- **Source:** Correlates of War National Material Capabilities dataset version 6.0 (Singer 1987, current release)
- **Unit:** A country's share of the global total of military, demographic, and economic capabilities; continuous on [0, 1] with all countries' values summing to 1.0 in any given year
- **Temporal coverage:** 1816–2016 for sovereign system members; **no v7.0 release at the time of writing**, so years 2017–2020 are unavailable for all panel countries
- **Operationalisation:** The canonical S variable in the international-relations literature; a composite of military expenditure, military personnel, total population, urban population, iron and steel production, and primary energy consumption

---

## Systematic unavailability flags

Three categories of country-year-variable triples are systematically unavailable for historical reasons rather than from data-collection failure. These are encoded as `NaN` in the `value` column with an explanatory string in the `note` column.

### 1. Pre-1830 Belgium (all variables)

Belgium did not exist as an independent state until the 1830 secession from the United Kingdom of the Netherlands. All variables for `(ISO3='BEL', year < 1830)` are unavailable. Maddison covers Belgium pre-1830 within the territory of the United Kingdom of the Netherlands but the panel excludes these as not country-comparable.

### 2. Pre-1846 Belgian `gdppc`

Even after Belgian independence in 1830, the Maddison series for `gdppc` does not begin until 1846. For `(ISO3='BEL', year ∈ [1830, 1845], variable='gdppc')`, values are unavailable.

### 3. Pre-1862 Italian `v2x_libdem` and `v2x_polyarchy`

V-Dem codes for Italy do not exist before 1862, the first post-unification year in V-Dem's coding scheme. For `(ISO3='ITA', year < 1862, variable ∈ {'v2x_libdem', 'v2x_polyarchy'})`, values are unavailable.

### 4. German `cinc` 1945–1954

The Federal Republic of Germany was formed in 1949 but did not achieve full sovereignty in the Correlates of War system until the *Deutschlandvertrag* of 5 May 1955; consequently no CINC value is assigned to any German state for the years 1945–1954. The harmonised panel handles this by using COW code 255 (unified Germany) for 1820–1944 and 1990–2016, COW code 260 (Federal Republic) for 1955–1989, and flagging 1945–1954 as systematically unavailable. Germany contributes only 62 listwise-complete country-years to the post-war sub-window — the lowest individual-country count in the panel — and this is discussed in §6.4 of the paper as a sensitivity element.

### 5. `cinc` 2017–2020 (all countries)

The Correlates of War NMC v6.0 release terminates in 2016. No v7.0 release exists at the time of writing. For `(year > 2016, variable='cinc')`, values are unavailable for all eight panel countries.

---

## Per-country listwise-complete counts

| Country | Pre-war (max 94) | Post-war (max 76) | Total (max 170) |
|---|---|---|---|
| BEL | 68 | 76 | 144 |
| DEU | 94 | 62 | 156 |
| ESP | 94 | 76 | 170 |
| FRA | 94 | 76 | 170 |
| GBR | 94 | 76 | 170 |
| ITA | 52 | 76 | 128 |
| NLD | 94 | 76 | 170 |
| SWE | 94 | 76 | 170 |

The counts reflect the unavailability flags above plus the COW 2017–2020 gap (which reduces every country's post-war count by 4 years for `cinc`, but the listwise-complete column reports country-years where *all five* variables are non-missing, so the COW termination at 2016 propagates to a post-war ceiling of 72 for `cinc`-availability that the §5.3 paper text identifies). The values in this table follow the same listwise-completion rule as §5.3 of the paper.

---

## Sub-window assignment

The `sub_window` column is derived deterministically from `year`:

- `pre_war` if `1820 ≤ year ≤ 1913`
- `post_war` if `1945 ≤ year ≤ 2020`
- `excluded` if `1914 ≤ year ≤ 1944` (these rows are present in the long-format CSV for completeness but are flagged for exclusion in any structural analysis)

The two World Wars and the inter-war period are excluded by design under the structural-stationarity requirement.

---

## Reproduction

The CSV is regenerated deterministically from primary sources by running `scripts/build_panel.py`. The script reads:

- The V-Dem v16 country-year CSV (`v2x_libdem`, `v2x_polyarchy`)
- The Maddison Project 2023 release (`pop`, `gdppc`)
- The Correlates of War NMC v6.0 release (`cinc`)

and produces this file as output. The script's source-attribution logic, sub-window assignment, and systematic-unavailability flagging are documented in `scripts/harmonisation_log.txt`. Validation diagnostics on the produced CSV are run by `scripts/sanity_check.py`.

---

## Citation

If you use this dataset, please cite the paper:

> Fontaise, G. (2026). *Koopman–CMH: A Formal Treatment of Spectral Structure Persistence in Historical Dynamics* (Working Paper WP-2026-006). Fontaise Institute of Computational Social Science. DOI: 10.5281/zenodo.<TBD>

and the primary sources:

- Bolt, J., and J. L. van Zanden. 2024. "Maddison Project Database 2023." *Journal of Economic Surveys*.
- Coppedge, M., J. Gerring, et al. 2025. "V-Dem [Country-Year] Dataset v16." Varieties of Democracy (V-Dem) Project.
- Singer, J. D. 1987. "Reconstructing the Correlates of War Dataset on Material Capabilities of States, 1816–1985." *International Interactions* 14: 115–32.

---

*FICSS Institute · Computational Macrohistory programme · MIT License*
