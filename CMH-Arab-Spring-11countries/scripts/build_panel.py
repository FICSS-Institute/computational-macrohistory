#!/usr/bin/env python3
"""
build_panel.py — reconstruct the analysis panel from the source files and compare
it with the deposited canonical panel.

This is a VERIFICATION tool, not the producer of the canonical panel. The canonical
panel is data/panel_11countries_2000-2012.csv, which is the series as used for every
value reported in WP-2026-004. Running this script re-extracts the five components
from the files in data/source_files/ and reports any cell that differs.

Nine cells are known to differ by 0.01 to 0.03 on the youth-unemployment component
(see CODEBOOK, "Known reconstruction differences"). Their effect on every reported
result is below the reported precision; the single exception is the Saudi Arabian
2010 index value, which prints as -0.094 in the canonical panel and would print as
-0.095 under re-extraction. No ranking, threshold interval or classification changes.

Usage:  python scripts/build_panel.py [--write reconstructed.csv]
Requires: pandas, openpyxl, xlrd>=2.0.1

FICSS / Computational Macrohistory — WP-2026-004
"""

import os
import sys
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "source_files")
CANON = os.path.join(ROOT, "data", "panel_11countries_2000-2012.csv")

YEARS = list(range(2000, 2013))
WB_NAME = {"Egypt, Arab Rep.": "Egypt", "Yemen, Rep.": "Yemen",
           "Syrian Arab Republic": "Syria"}


def half_up(v, places=2):
    q = Decimal(10) ** -places
    return float(Decimal(repr(float(v))).quantize(q, rounding=ROUND_HALF_UP))


def wdi_data_sheet(filename):
    """Read a World Bank DataBank 'Data' sheet: metadata columns then year columns."""
    d = pd.read_excel(os.path.join(SRC, filename), sheet_name="Data", header=None)
    years = [int(str(x)[:4]) for x in d.iloc[0, 4:].tolist() if str(x)[:4].isdigit()]
    out = {}
    for _, r in d.iloc[1:].iterrows():
        c = str(r.iloc[0]).strip()
        if c == "nan" or c.startswith("Data from") or c.startswith("Last Updated"):
            continue
        out[WB_NAME.get(c, c)] = {y: float(r.iloc[i + 4]) for i, y in enumerate(years)
                                  if pd.notna(r.iloc[i + 4])}
    return out


def load_d2():
    """Youth bulge 15-24 as a share of TOTAL population (Appendix B of the paper).

    The WDI reports the 15-19 and 20-24 bands as shares of the population of the
    SAME SEX. Each share is therefore weighted by that sex's total population,
    itself reconstructed from the three absolute age-band counts.
    """
    d = pd.read_excel(os.path.join(SRC, "D2_YouthBulge_data_for_calculation.xlsx"),
                      sheet_name="Data", header=None)
    years = [int(float(x)) for x in d.iloc[0, 2:].tolist() if pd.notna(x)]
    tab = {}
    for _, r in d.iloc[1:].iterrows():
        c, s = str(r.iloc[0]).strip(), str(r.iloc[1]).strip()
        if c == "nan" or s == "nan" or c.startswith("Data from"):
            continue
        tab[(WB_NAME.get(c, c), s)] = {y: float(r.iloc[i + 2]) for i, y in enumerate(years)
                                       if pd.notna(r.iloc[i + 2])}
    out = {}
    for c in sorted({k[0] for k in tab}):
        out[c] = {}
        for y in years:
            total = youth = 0.0
            for g in ("female", "male"):
                n = sum(tab[(c, f"Population ages {b}, {g}")][y]
                        for b in ("0-14", "15-64", "65 and above"))
                share = (tab[(c, f"Population ages 15-19, {g} (% of {g} population)")][y]
                         + tab[(c, f"Population ages 20-24, {g} (% of {g} population)")][y]) / 100.0
                total += n
                youth += share * n
            out[c][y] = 100.0 * youth / total
    return out


def load_e2():
    """Gini x 100 from the UNU-WIDER WIID Companion export (sheet 'data')."""
    d = pd.read_excel(os.path.join(SRC, "E2_GINI2000-12_wiid-data-map-chart.xlsx"),
                      sheet_name="data", header=None)
    years = [int(float(x)) for x in d.iloc[1, 2:].tolist()]
    out = {}
    for _, r in d.iloc[2:].iterrows():
        c = str(r.iloc[1]).strip()
        if c != "nan":
            out[c] = {y: float(r.iloc[i + 2]) for i, y in enumerate(years)}
    return out


def load_p1():
    """Polity5 polity2 score."""
    d = pd.read_excel(os.path.join(SRC, "P1_Polity.xls"), sheet_name="p5v2018")
    d.columns = [str(c).strip().lower() for c in d.columns]
    out = {}
    for _, r in d.iterrows():
        c = WB_NAME.get(str(r["country"]).strip(), str(r["country"]).strip())
        out.setdefault(c, {})[int(r["year"])] = int(r["polity2"])
    return out


def reconstruct():
    d2, e2, p1 = load_d2(), load_e2(), load_p1()
    e4 = wdi_data_sheet("E4_Youth_Unemployment.xlsx")
    s3 = wdi_data_sheet("S3_Internet_Use___of_population.xlsx")
    canon = pd.read_csv(CANON)
    rows = []
    for c in sorted(canon.Country.unique()):
        for y in YEARS:
            rows.append({"Year": y, "Country": c,
                         "D2_YouthBulge_pct": half_up(d2[c][y]),
                         "E2_Gini": half_up(e2[c][y]),
                         "E4_YouthUnemp_pct": half_up(e4[c][y]),
                         "P1_Polity": p1[c][y],
                         "S3_InternetPentr_pct": half_up(s3[c][y])})
    return pd.DataFrame(rows), canon


def main():
    rec, canon = reconstruct()
    m = canon.merge(rec, on=["Year", "Country"], suffixes=("_canon", "_rec"))
    cols = ["D2_YouthBulge_pct", "E2_Gini", "E4_YouthUnemp_pct",
            "P1_Polity", "S3_InternetPentr_pct"]
    diffs = []
    for col in cols:
        d = m[abs(m[col + "_canon"] - m[col + "_rec"]) > 0.005]
        for _, r in d.iterrows():
            diffs.append((r.Country, int(r.Year), col, r[col + "_canon"], r[col + "_rec"]))
    print(f"cells compared: {len(m) * len(cols)}")
    print(f"cells differing: {len(diffs)}")
    for c, y, col, a, b in sorted(diffs):
        print(f"  {c:14s} {y}  {col:22s} canonical {a:8.2f}  reconstructed {b:8.2f}")
    if not diffs:
        print("  none — reconstruction is exact")
    if "--write" in sys.argv:
        path = sys.argv[sys.argv.index("--write") + 1]
        rec.to_csv(path, index=False, lineterminator="\n")
        print(f"\nwrote reconstruction to {path}")


if __name__ == "__main__":
    main()
