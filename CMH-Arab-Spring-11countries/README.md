# Arab Spring — 11-Country Analysis (WP-2026-004)

Replication materials for:

**Fontaise, G. (2026). "Structural Stress and Political Instability in the MENA Region: A Computational Macrohistory Analysis of the Arab Spring Across Eleven Countries, 2000–2012." FICSS Working Paper WP-2026-004.**

**DOI**: [10.5281/zenodo.19661257](https://doi.org/10.5281/zenodo.19661257)

## Contents

| File | Description |
|------|-------------|
| `raw_data_11countries_2000-2012.csv` | Complete dataset: raw components (D₂, E₂, E₄, P₁, S₃), computed SSI, and outcomes |
| `CODEBOOK.md` | Variable definitions, sources, and reference parameters |

## Countries

Algeria, Bahrain, Egypt, Jordan, Kuwait, Morocco, Oman, Saudi Arabia, Syria, Tunisia, Yemen

## SSI Formula

```
SSI(t) = 0.15·z(D₂) + 0.25·z(E₂) + 0.25·z(E₄) + 0.25·z(AS) + 0.10·z(S₃)
```

Where z-scores use MENA historical reference parameters (1980–2010), not sample estimates.

## Related Papers

- **WP-2026-001**: [Axiomatic Foundations](https://doi.org/10.5281/zenodo.18288165)
- **WP-2026-002**: [Operational Framework](https://doi.org/10.5281/zenodo.18646832)
- **WP-2026-003**: [3-Country Proof of Concept](https://doi.org/10.5281/zenodo.18848734)
- **WP-2026-004**: [11-Country Analysis](https://doi.org/10.5281/zenodo.19661257) ← this study

## License

MIT — see repository root.
