# CMH — Arab Spring, eleven countries (2000–2012)

Replication materials for **WP-2026-004**, *Structural stress and political instability in the MENA region: A computational macrohistory analysis of the Arab Spring across eleven countries, 2000–2012*.

**Author:** Stefano Angeli, Foundations Institute of Computational Social Science (FICSS)
**ORCID:** [0009-0007-6643-2307](https://orcid.org/0009-0007-6643-2307)
**Paper DOI:** 10.5281/zenodo.XXXXXXXX
**Paper version covered by this folder:** v2.3 (July 2026)

Earlier work in this series appeared under the anagrammatic pseudonym Galen Fontaise.

---

## What this study does

The paper constructs a five-component Systemic Stress Index (SSI) for eleven states of the Middle East and North Africa over 2000 to 2012 and asks whether the structural signals hypothesised by the Computational Macrohistory framework are detectable in the historical record at the 2010 pre-event benchmark. It is a Type B exploratory application, not a statistical validation: with eleven cases the standard apparatus of inference is unavailable, and the paper reports exact permutation probabilities in its place.

The headline results are that the index ranks the four instability cases above the seven stability cases in 20 of 28 pairs (AUC 0.714, exact one-sided permutation probability 0.158) and separates the two groups by 0.290 index units. Threshold classification assigns eight of eleven countries correctly, a figure that carries no evidential weight on its own because the threshold is selected within the sample; its own permutation null has a median of exactly eight of eleven.

---

## Folder contents

```
CMH-Arab-Spring-11countries/
├── README.md                              this file
├── CODEBOOK.md                            variable definitions, provenance, known issues
├── LICENSE                                MIT
├── data/
│   ├── panel_11countries_2000-2012.csv    canonical analysis panel (143 rows)
│   ├── source_files/                      the five source exports, as downloaded
│   └── explored_not_used/                 material examined and discarded
├── scripts/
│   ├── build_panel.py                     re-extract from source and verify
│   ├── reproduce_results.py               reproduce every number in the paper
│   └── make_fig6.py                       regenerate Figure 6
├── figures/                               figures as they appear in the paper
└── outputs/
    └── null_distribution_2010.csv         all 330 permutation assignments
```

---

## Reproducing the results

Requires Python 3.9 or later with `pandas`, `numpy`, `openpyxl`, `xlrd>=2.0.1` and, for the figure, `matplotlib`.

```bash
python scripts/reproduce_results.py
```

This recomputes every quantitative claim in the paper from `data/panel_11countries_2000-2012.csv` and the reference parameters and weights of Table 2, and checks each against the value printed in the paper. It covers the 2010 cross-section, the decade means, group separation, pairwise rank ordering, all six weighting schemes, the leave-one-component-out analysis, the single-component ordering statistics, the three exact permutation distributions, the threshold intervals, the standardised-value ranges and correlations of Section 6.1, the component contributions of Figure 4, and the data-quality claims of Section 8.2. It writes `outputs/null_distribution_2010.csv` and exits non-zero if any check fails.

Replication is deterministic. There is no estimation step, no random seed and no software-version dependence beyond floating-point arithmetic: the index is a weighted sum of standardised components with parameters fixed a priori.

To re-extract the panel from the original source exports rather than trusting the deposited CSV:

```bash
python scripts/build_panel.py
```

This reports the nine cells where a clean re-extraction differs from the deposited panel. See the CODEBOOK section "Known reconstruction differences" before interpreting the output.

---

## The index

The Polity score is transformed to anocracy stress, `A = 1 − |P₁| / 10`. Each component is standardised as `z = (X − μ) / σ` against the reference parameters below, and the standardised components are combined with theory-derived signs, all `+1` in the baseline specification:

```
SSI = 0.15·z(D₂) + 0.25·z(E₂) + 0.25·z(E₄) + 0.25·z(A) + 0.10·z(S₃)
```

| Component | Variable | μ | σ | Weight | Reference window |
|---|---|---|---|---|---|
| D₂ | Youth bulge, ages 15–24, % of population | 22.5 | 4.5 | 0.15 | 1960–2010 |
| E₂ | Gini × 100 | 40.0 | 8.0 | 0.25 | long-run estimated distribution |
| E₄ | Youth unemployment, ages 15–24, % | 18.0 | 8.0 | 0.25 | 1990–2010 |
| A | Anocracy stress, from Polity5 | 0.5 | 0.3 | 0.25 | theoretical distribution over the Polity scale |
| S₃ | Internet penetration, % of population | 15.0 | 20.0 | 0.10 | 2000–2010 |

The reference parameters are conventional values fixed before contact with the data, not moments estimated from this sample. They are taken unchanged from the three-country study that precedes this one (Angeli 2026, WP-2026-003, Table 5). Estimating them from the same sample used for assessment would introduce the circularity that Axiom A8 exists to prevent.

Positive values indicate above-average systemic stress relative to the stated reference population; negative values indicate below-average stress.

---

## Two things a user of these data should know

**The inequality component is model-imputed throughout.** E₂ comes from the UNU-WIDER WIID *Companion* dataset, which supplies complete annual country coverage by imputation, and not from the WIID proper, which reports survey observations with the gaps they leave. Every E₂ value in this panel is a model estimate. For nine of the eleven countries the 2010 value lies on a smooth interpolation between two or three anchor points. Bahrain and Saudi Arabia carry an identical imputed series in every year. Section 8.2 of the paper and the CODEBOOK document this in full; the leave-one-component-out result for E₂ should be read in that light.

**The threshold-classification accuracy is descriptive, not inferential.** Eight of eleven correct is the median of its own permutation null. The rank-ordering statistic, which does not depend on in-sample threshold selection, is the measure the paper treats as primary.

---

## Citation

Angeli, S. (2026). *Structural stress and political instability in the MENA region: A computational macrohistory analysis of the Arab Spring across eleven countries, 2000–2012* (FICSS Working Paper No. WP-2026-004, v2.3). Foundations Institute of Computational Social Science. https://doi.org/10.5281/zenodo.XXXXXXXX

## Related work in this series

- **WP-2026-001** Axiomatic foundations — [10.5281/zenodo.21178550](https://doi.org/10.5281/zenodo.21178550)
- **WP-2026-002** Operational framework — [10.5281/zenodo.18646832](https://doi.org/10.5281/zenodo.18646832)
- **WP-2026-003** Three-country empirical application — [10.5281/zenodo.21440130](https://doi.org/10.5281/zenodo.21440130) — replication materials in [`../CMH-Arab-Spring`](../CMH-Arab-Spring)

## License

MIT for code. Data are redistributed under the terms of their original providers; see the CODEBOOK for per-source licensing.
