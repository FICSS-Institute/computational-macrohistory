# CMH-Arab-Spring: Replication Materials

**Computational Macrohistory — Document III**
*Exploratory empirical application. The Arab Spring as a preliminary test case for structural-demographic theory*

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21440130.svg)](https://doi.org/10.5281/zenodo.21440130)

---

## Overview

This repository contains the replication materials for **Document III** (WP-2026-003) of the Computational Macrohistory (CMH) series, published by the Foundations Institute of Computational Social Science (FICSS), Milano, Italy. The current version of the paper is **v3.1** (July 2026; supersedes v3.0 and all earlier versions).

The paper applies the CMH framework to the structural preconditions of the Arab Spring (2010-2012), comparing three MENA countries, **Tunisia**, **Egypt**, and **Saudi Arabia**, across five structural variables for 2000-2012.

**Key finding**: regime type, operationalised as anocracy stress, is the discriminating variable between the countries that experienced revolutionary transitions and the country that remained stable, conditional on shared demographic and economic stress indicators.

**Note on the youth bulge definition (v3.1).** Versions 1.0 to 3.0 of the paper described the youth bulge band D₂ as ages 15 to 29. Verification of the deposited series against the source age bands (World Bank Open Data, UN population estimates, July 2026) established that the values are computed over ages 15 to 24, the canonical CMH definition. Version 3.1 corrects the description; **no data values were changed**.

---

## Repository Structure

```
CMH-Arab-Spring/
├── README.md                        # This file
├── LICENSE                          # CC-BY 4.0
├── data/
│   ├── raw/
│   │   └── arab_spring_data.csv     # 195 data points (3 countries x 5 vars x 13 years)
│   └── codebook.md                  # Variable definitions, units, and sources
├── analysis/
│   ├── ssi_calculation.md           # Step-by-step SSI computation procedure
│   └── ssi_results.csv              # Final SSI scores by country and year
├── figures/
│   └── fig1, fig3-fig6 .png         # Figures 1 to 5 of the paper (see note below)
└── paper/
    └── WP_2026_003_Empirical_Application.pdf    # The working paper (v3.1)
```

Figure mapping: Figures 1 to 5 of the current paper correspond to `fig1_causal_diagram.png`, `fig3_time_series.png`, `fig4_ssi_analysis.png`, `fig5_validation.png`, and `fig6_counterfactual.png`. The files `fig2_probability_model.png` and `fig7_causal_flowchart.png` belong to earlier versions and are retained for continuity.

---

## Data

The dataset (`arab_spring_data.csv`) contains annual observations for three countries over 2000-2012 on five variables drawn from the CMH 25-dimensional state space:

| Variable | CMH Code | Description |
|---|---|---|
| Youth Bulge | D₂ | % population aged 15-24 |
| Gini Coefficient | E₂ | Income inequality index (0-100) |
| Youth Unemployment | E₄ | % unemployed aged 15-24 |
| Polity Score | P₁ | Democracy/autocracy index (-10 to +10) |
| Internet Penetration | S₃ | % population using internet |

**Sources**: UN World Population Prospects (via World Bank Open Data), SWIID v9.0 / World Bank, ILO ILOSTAT, Polity V Project, ITU / World Bank.
See `data/codebook.md` for full operationalization details.

---

## Replication Instructions

No programming environment is required to inspect the data. All files are in standard formats:

- `.csv` files open in Excel, Google Sheets, LibreOffice Calc, Python (pandas), or R
- `.md` files open in any text editor or Markdown viewer
- `.pdf` opens in any PDF reader

Replication is deterministic: the procedure documented in `analysis/ssi_calculation.md` applied to the data of `data/raw/arab_spring_data.csv` reproduces every SSI value reported in the paper to the reported two decimal places, including all robustness variants.

---

## Citation

If you use these materials, please cite:

> Angeli, S. (2026). *Computational Macrohistory: Exploratory empirical application. The Arab Spring as a preliminary test case for structural-demographic theory* (FICSS Working Paper No. WP-2026-003, v3.1). Foundations Institute of Computational Social Science. https://doi.org/10.5281/zenodo.21440130

BibTeX:

```bibtex
@techreport{angeli2026cmh3,
  author      = {Angeli, Stefano},
  title       = {Computational Macrohistory: Exploratory empirical application. The Arab Spring as a preliminary test case for structural-demographic theory},
  year        = {2026},
  institution = {Foundations Institute of Computational Social Science (FICSS)},
  type        = {Working Paper},
  number      = {WP-2026-003, v3.1},
  doi         = {10.5281/zenodo.21440130},
  url         = {https://doi.org/10.5281/zenodo.21440130}
}
```

---

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
You are free to share and adapt the material for any purpose, provided appropriate credit is given.

---

## Contact

Foundations Institute of Computational Social Science (FICSS)
Milano, Italy
stefano.angeli@ficss.institute
[https://www.ficss.institute](https://www.ficss.institute)
