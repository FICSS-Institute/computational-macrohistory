# CMH-Arab-Spring: Replication Materials

**Computational Macrohistory — Document III**  
*A Quantitative Analysis of the Arab Spring (2010–2012)*

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

---

## Overview

This repository contains the replication materials for **Document III** of the Computational Macrohistory (CMH) series, published by the Fontaise Institute for Computational Social Sciences (FICSS), Lugano, Switzerland.

The paper applies the CMH framework to analyze the structural preconditions of the Arab Spring (2010–2012), comparing three MENA countries — **Tunisia**, **Egypt**, and **Saudi Arabia** — across five key socio-political variables for the period 2000–2012.

**Key finding**: Regime type (Polity Score) acts as the critical discriminating variable between countries that experienced revolutionary transitions and those that maintained stability, conditional on shared demographic and economic stress indicators.

---

## Repository Structure

```
CMH-Arab-Spring/
├── README.md                        # This file
├── LICENSE                          # CC-BY 4.0
├── data/
│   ├── raw/
│   │   └── arab_spring_data.csv     # 195 data points (3 countries × 5 vars × 13 years)
│   └── codebook.md                  # Variable definitions, units, and sources
├── analysis/
│   ├── ssi_calculation.md           # Step-by-step SSI computation procedure
│   └── ssi_results.csv              # Final SSI scores by country and year
├── figures/
│   └── [fig1-6].png                 # Figures as they appear in the paper
└── paper/
    └── CMH_Document_III_v1.2.pdf    # The working paper (final version)
```

---

## Data

The dataset (`arab_spring_data.csv`) contains annual observations for three countries over 2000–2012 on five variables drawn from the CMH 25-dimensional state space:

| Variable | CMH Code | Description |
|----------|----------|-------------|
| Youth Bulge | D₂ | % population aged 15–29 |
| Gini Coefficient | E₂ | Income inequality index (0–1) |
| Youth Unemployment | E₄ | % unemployed aged 15–24 |
| Polity Score | P₁ | Democracy/autocracy index (–10 to +10) |
| Internet Penetration | S₃ | % population using internet |

**Sources**: World Bank Open Data, ILO Statistics, Polity V Project, Freedom House.  
See `data/codebook.md` for full operationalization details.

---

## Replication Instructions

No programming environment is required to inspect the data. All files are in standard formats:

- `.csv` files open in Excel, Google Sheets, LibreOffice Calc, Python (pandas), or R
- `.md` files open in any text editor or Markdown viewer
- `.pdf` opens in any PDF reader

To reproduce the SSI (Systemic Stress Index) calculations manually, follow the procedure documented in `analysis/ssi_calculation.md`.

---

## Citation

If you use these materials, please cite:

> Fontaise, T. (2025). *Computational Macrohistory — Document III: A Quantitative Analysis of the Arab Spring (2010–2012)*. FICSS Working Paper. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

BibTeX:
```bibtex
@techreport{fontaise2025cmh3,
  author    = {Fontaise, Tenofas},
  title     = {Computational Macrohistory --- Document III: A Quantitative Analysis of the Arab Spring (2010--2012)},
  year      = {2025},
  institution = {Fontaise Institute for Computational Social Sciences (FICSS)},
  type      = {Working Paper},
  doi       = {10.5281/zenodo.XXXXXXX},
  url       = {https://doi.org/10.5281/zenodo.XXXXXXX}
}
```

---

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).  
You are free to share and adapt the material for any purpose, provided appropriate credit is given.

---

## Contact

Fontaise Institute for Computational Social Sciences (FICSS)  
Lugano, Switzerland  
[FICSS Website]
