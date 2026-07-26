#!/usr/bin/env python3
"""
reproduce_results.py — reproduce every quantitative result reported in WP-2026-004.

Reads data/panel_11countries_2000-2012.csv and recomputes, from the reference
parameters and weights of Table 2 alone, every number that appears in the paper:
the 2010 cross-section, the decade means of Table 3, group separation, pairwise
rank ordering, the six weighting schemes of Table 5, the leave-one-component-out
analysis, the single-component ordering statistics, the exact permutation
distributions of Section 5, the standardised-value ranges and correlations of
Section 6.1, and the component contributions of Figure 4.

Every printed value is checked against the value stated in the paper. The script
exits non-zero if any check fails.

Usage:  python scripts/reproduce_results.py
Requires: pandas, numpy

FICSS / Computational Macrohistory — WP-2026-004
"""

import os
import sys
import itertools
import collections
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PANEL = os.path.join(ROOT, "data", "panel_11countries_2000-2012.csv")
NULLOUT = os.path.join(ROOT, "outputs", "null_distribution_2010.csv")

# Table 2: reference parameters and weights. Component-specific reference windows:
# D2 1960-2010, E4 1990-2010, S3 2000-2010, E2 long-run estimated distribution,
# A theoretical distribution over the Polity scale. Source: Angeli (2026c), Table 5.
MU = {"D2": 22.5, "E2": 40.0, "E4": 18.0, "A": 0.5, "S3": 15.0}
SIG = {"D2": 4.5, "E2": 8.0, "E4": 8.0, "A": 0.3, "S3": 20.0}
W = {"D2": 0.15, "E2": 0.25, "E4": 0.25, "A": 0.25, "S3": 0.10}

RAW = {"D2": "D2_YouthBulge_pct", "E2": "E2_Gini", "E4": "E4_YouthUnemp_pct",
       "A": "A_AnocracyStress", "S3": "S3_InternetPentr_pct"}

INSTABILITY = ["Tunisia", "Egypt", "Yemen", "Syria"]

FAILURES = []


def check(label, got, expected, tol=5e-4):
    ok = abs(got - expected) <= tol if isinstance(expected, float) else got == expected
    print(f"  [{'OK  ' if ok else 'FAIL'}] {label:52s} {got!r:>12}  (paper: {expected!r})")
    if not ok:
        FAILURES.append(label)


def load():
    df = pd.read_csv(PANEL)
    for k, col in RAW.items():
        df["z_" + k] = (df[col] - MU[k]) / SIG[k]
    df["SSI_calc"] = sum(W[k] * df["z_" + k] for k in W)
    return df


def ssi_at(df, weights, year=2010):
    d = sum(weights[k] * df["z_" + k] for k in weights)
    x = df.assign(S=d)
    return x[x.Year == year].set_index("Country")["S"]


def separation(x, inst):
    stab = [c for c in x.index if c not in inst]
    return x[inst].mean() - x[stab].mean()


def pairs(x, inst):
    stab = [c for c in x.index if c not in inst]
    return sum(1 for a in inst for b in stab if x[a] > x[b])


def best_threshold_accuracy(x, labels):
    order = list(x.index)
    best = 0
    for tau in list(x.values) + [max(x.values) + 1]:
        best = max(best, sum(1 for c in order if (x[c] >= tau) == (c in labels)))
    return best


def main():
    df = load()
    order = sorted(df.Country.unique())
    inst = INSTABILITY
    stab = [c for c in order if c not in inst]
    s = df[df.Year == 2010].set_index("Country")["SSI_calc"]

    print("\n1. Deposited SSI column reproduces from Table 2 parameters")
    d = df[abs(df.SSI - df.SSI_calc) > 1e-6]
    check("all 143 SSI values reproduce", len(d), 0)

    print("\n2. Section 4.3 / Table 3 — 2010 cross-section (3 dp)")
    expected_2010 = {"Jordan": 0.574, "Tunisia": 0.517, "Yemen": 0.324, "Morocco": 0.104,
                     "Egypt": 0.102, "Algeria": -0.034, "Saudi Arabia": -0.094,
                     "Syria": -0.192, "Oman": -0.306, "Kuwait": -0.457, "Bahrain": -0.499}
    for c, v in expected_2010.items():
        check(f"SSI 2010 {c}", round(s[c], 3), v)

    print("\n3. Section 4.2 — group means and separation")
    check("instability group mean 2010", round(s[inst].mean(), 3), 0.188)
    check("stability group mean 2010", round(s[stab].mean(), 3), -0.102)
    check("group separation", round(separation(s, inst), 3), 0.290)

    print("\n4. Section 5 — rank ordering")
    cp = pairs(s, inst)
    check("correct pairwise orderings", cp, 20)
    check("area under the curve", round(cp / 28, 3), 0.714)
    check("chance expectation", 28 // 2, 14)

    print("\n5. Section 5 — exact permutation distributions (330 assignments)")
    allc = list(itertools.combinations(order, 4))
    check("C(11,4)", len(allc), 330)
    acc_null = [best_threshold_accuracy(s, set(L)) for L in allc]
    n_opt = sum(1 for a in acc_null if a >= 8)
    check("threshold-optimised accuracy >= 8/11", n_opt, 165)
    check("  ... as a probability (the median)", round(n_opt / 330, 3), 0.500)
    n_fix = sum(1 for L in allc
                if sum(1 for c in order if (s[c] >= 0.10) == (c in set(L))) >= 8)
    check("fixed threshold 0.10, accuracy >= 8/11", n_fix, 65)
    check("  ... as a probability", round(n_fix / 330, 3), 0.197)
    n_pr = sum(1 for L in allc if pairs(s, set(L)) >= 20)
    check("correct pairs >= 20/28", n_pr, 52)
    check("  ... as a probability", round(n_pr / 330, 3), 0.158)
    check("random classifier expected accuracy", round((4 * 4 + 7 * 7) / 121, 3), 0.537)
    check("majority-class accuracy", round(7 / 11, 3), 0.636)

    os.makedirs(os.path.dirname(NULLOUT), exist_ok=True)
    rows = [{"assignment": "|".join(L),
             "best_threshold_accuracy": best_threshold_accuracy(s, set(L)),
             "accuracy_at_tau_0.10": sum(1 for c in order if (s[c] >= 0.10) == (c in set(L))),
             "correct_pairs": pairs(s, set(L))} for L in allc]
    pd.DataFrame(rows).to_csv(NULLOUT, index=False, lineterminator="\n")
    print(f"  wrote null distribution to {os.path.relpath(NULLOUT, ROOT)}")

    print("\n6. Section 5 — threshold intervals")
    check("Egypt 2010 unrounded", round(s["Egypt"], 5), 0.10219)
    check("Morocco 2010 unrounded", round(s["Morocco"], 5), 0.10390)
    check("Yemen 2010 unrounded", round(s["Yemen"], 5), 0.32371)
    check("Algeria 2010 unrounded", round(s["Algeria"], 5), -0.03429)
    for tau in (-0.033, 0.102):
        acc = sum(1 for c in order if (s[c] >= tau) == (c in inst))
        check(f"accuracy at tau={tau}", acc, 8)
    for tau in (0.105, 0.323):
        acc = sum(1 for c in order if (s[c] >= tau) == (c in inst))
        check(f"accuracy at tau={tau}", acc, 8)
    check("accuracy at tau=0.324 (excluded bound)",
          sum(1 for c in order if (s[c] >= 0.324) == (c in inst)), 7)

    print("\n7. Table 5 — alternative weighting schemes")
    schemes = {
        "Baseline":     {"D2": 0.15, "E2": 0.25, "E4": 0.25, "A": 0.25, "S3": 0.10},
        "Equal":        {"D2": 0.20, "E2": 0.20, "E4": 0.20, "A": 0.20, "S3": 0.20},
        "Economic":     {"D2": 0.08, "E2": 0.35, "E4": 0.35, "A": 0.15, "S3": 0.07},
        "Regime":       {"D2": 0.10, "E2": 0.18, "E4": 0.18, "A": 0.40, "S3": 0.14},
        "Demographic":  {"D2": 0.40, "E2": 0.15, "E4": 0.25, "A": 0.10, "S3": 0.10},
        "Coordination": {"D2": 0.10, "E2": 0.20, "E4": 0.20, "A": 0.20, "S3": 0.30},
    }
    expected = {"Baseline": (0.290, 20), "Equal": (0.142, 17), "Economic": (0.298, 20),
                "Regime": (0.301, 22), "Demographic": (0.256, 18), "Coordination": (0.031, 15)}
    for name, w in schemes.items():
        check(f"{name} weights sum to 1", round(sum(w.values()), 6), 1.0)
        x = ssi_at(df, w)
        check(f"{name} separation", round(separation(x, inst), 3), expected[name][0])
        check(f"{name} correct pairs", pairs(x, inst), expected[name][1])

    print("\n8. Section 6.2 — leave-one-component-out")
    expected_loo = {"D2": (0.301, 20), "E2": (0.440, 22), "E4": (0.105, 18),
                    "A": (0.152, 17), "S3": (0.421, 22)}
    for drop, (esep, ecp) in expected_loo.items():
        w = {k: v for k, v in W.items() if k != drop}
        tot = sum(w.values())
        w = {k: v / tot for k, v in w.items()}
        x = ssi_at(df, w)
        check(f"exclude {drop}: separation", round(separation(x, inst), 3), esep)
        check(f"exclude {drop}: correct pairs", pairs(x, inst), ecp)

    print("\n9. Section 6.2 — single-component ordering (strict wins)")
    t10 = df[df.Year == 2010].set_index("Country")
    expected_single = {"E4": 19, "A": 19, "D2": 15, "E2": 11, "S3": 5}
    for k, e in expected_single.items():
        z = t10["z_" + k]
        check(f"{k} alone", sum(1 for a in inst for b in stab if z[a] > z[b]), e)
    z_pair = 0.5 * t10["z_E4"] + 0.5 * t10["z_A"]
    check("E4 + A combined", sum(1 for a in inst for b in stab if z_pair[a] > z_pair[b]), 21)
    ties = sum(1 for a in inst for b in stab if t10["z_A"][a] == t10["z_A"][b])
    check("tied pairs on A", ties, 3)
    check("A with half credit", 19 + ties / 2, 20.5)

    print("\n10. Section 6.1 — standardised values and correlations at 2010")
    check("z(S3) minimum", round(t10["z_S3"].min(), 3), -0.132)
    check("z(S3) maximum", round(t10["z_S3"].max(), 3), 2.320)
    check("z(S3) mean", round(t10["z_S3"].mean(), 3), 0.961)
    check("z(D2) maximum", round(t10["z_D2"].max(), 3), 0.233)
    check("z(D2) mean", round(t10["z_D2"].mean(), 3), -0.623)
    for k, e in (("D2", -0.617), ("E4", -0.619), ("A", -0.603)):
        check(f"corr z(S3), z({k})", round(t10["z_S3"].corr(t10["z_" + k]), 3), e)

    print("\n11. Figure 4 — weighted component contributions at 2010")
    check("Jordan E4 contribution", round(W["E4"] * t10["z_E4"]["Jordan"], 3), 0.377)
    check("Tunisia E4 contribution", round(W["E4"] * t10["z_E4"]["Tunisia"], 3), 0.362)
    check("Egypt E4 contribution", round(W["E4"] * t10["z_E4"]["Egypt"], 3), 0.206)
    check("Egypt E2 contribution", round(W["E2"] * t10["z_E2"]["Egypt"], 3), -0.203)
    check("Yemen A contribution", round(W["A"] * t10["z_A"]["Yemen"], 3), 0.250)
    check("Algeria A contribution", round(W["A"] * t10["z_A"]["Algeria"], 3), 0.250)
    check("theoretical maximum A contribution",
          round(W["A"] * (1.0 - MU["A"]) / SIG["A"], 3), 0.417)

    print("\n12. Section 7.1 — Egyptian index series 2007 to 2010")
    eg = df[(df.Country == "Egypt") & (df.Year.between(2007, 2010))].SSI_calc.round(3).tolist()
    check("Egypt 2007 to 2010", eg, [0.158, 0.163, 0.141, 0.102])

    print("\n13. Section 8.2 — data-quality claims on the Gini component")
    g = df.pivot(index="Year", columns="Country", values="E2_Gini")
    check("Kuwait constant", len(set(g["Kuwait"])), 1)
    check("Kuwait value", round(float(g["Kuwait"].iloc[0]), 2), 40.41)
    check("Bahrain identical to Saudi Arabia",
          bool((g["Bahrain"].values == g["Saudi Arabia"].values).all()), True)
    check("Syria constant 2007 to 2012", len(set(g.loc[2007:2012, "Syria"])), 1)
    check("panel size", len(df), 143)

    print("\n" + "=" * 72)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        for f in FAILURES:
            print("  -", f)
        sys.exit(1)
    print("All checks passed. Every reported value reproduces from the deposited panel.")


if __name__ == "__main__":
    main()
