"""
WP-2026-006 — Automated sanity check on the harmonised panel
=============================================================

Runs a series of logical and statistical checks on the canonical panel CSV
produced by build_panel.py. For each check, prints PASS or FAIL with
the reason.

The checks are designed to catch the kinds of errors that would silently
break §6 of the paper — wrong country mapping, wrong sign, off-by-one
years, units mismatch, columns swapped between sources.

Run from WP-2026-006_data/:
    python sanity_check.py

Author: Galen Fontaise (FICSS)
Date:   May 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
PANEL_CSV   = PROJECT_DIR / "processed" / "WP-2026-006_WesternEurope_Panel_v0-1.csv"

# =============================================================================
# Load and reshape
# =============================================================================

print(f"Loading {PANEL_CSV.name}...")
df = pd.read_csv(PANEL_CSV)
# Reshape to wide for easier checks
wide = df.pivot_table(
    index=['ISO3', 'year', 'sub_window'],
    columns='variable',
    values='value',
    aggfunc='first'
).reset_index()
print(f"Loaded: {len(df):,} long rows, {len(wide):,} country-year rows\n")

# Counters
results = []

def check(name, condition, details=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, details))
    icon = "[OK]" if condition else "[!!]"
    print(f"{icon} {name}")
    if details and not condition:
        print(f"     → {details}")
    elif details:
        print(f"     ({details})")

# =============================================================================
# CHECK 1 — Panel completeness (structural)
# =============================================================================

print("\n--- STRUCTURAL CHECKS ---")

check(
    "1.1 Total country-year rows = 1360",
    len(wide) == 1360,
    f"got {len(wide)}"
)

check(
    "1.2 All 8 countries present",
    set(wide['ISO3'].unique()) == {'FRA','GBR','DEU','ITA','ESP','NLD','SWE','BEL'},
    f"got {sorted(wide['ISO3'].unique())}"
)

check(
    "1.3 Sub-window 1 has 752 rows (8 countries × 94 years)",
    (wide['sub_window'] == '1820-1913').sum() == 752,
    f"got {(wide['sub_window'] == '1820-1913').sum()}"
)

check(
    "1.4 Sub-window 2 has 608 rows (8 countries × 76 years)",
    (wide['sub_window'] == '1945-2020').sum() == 608,
    f"got {(wide['sub_window'] == '1945-2020').sum()}"
)

check(
    "1.5 No years in 1914-1918 (WWI excluded)",
    ((wide['year'] >= 1914) & (wide['year'] <= 1918)).sum() == 0,
    "WWI years should be entirely absent"
)

check(
    "1.6 No years in 1939-1944 (WWII active conflict excluded)",
    ((wide['year'] >= 1939) & (wide['year'] <= 1944)).sum() == 0,
    "WWII active years should be entirely absent"
)

check(
    "1.7 1945 IS present (post-war transition year)",
    (wide['year'] == 1945).sum() == 8,
    f"got {(wide['year'] == 1945).sum()}"
)

check(
    "1.8 No interwar years 1919-1938",
    ((wide['year'] >= 1919) & (wide['year'] <= 1938)).sum() == 0,
    "interwar years should be entirely absent"
)

# =============================================================================
# CHECK 2 — Value ranges (catches column swaps and unit errors)
# =============================================================================

print("\n--- VALUE RANGE CHECKS ---")

# V-Dem indices: bounded [0,1]
for var in ['v2x_libdem', 'v2x_polyarchy']:
    series = wide[var].dropna()
    out_of_range = ((series < 0) | (series > 1)).sum()
    check(
        f"2.1 {var} all in [0,1]",
        out_of_range == 0,
        f"{out_of_range} values out of range; min={series.min():.4f}, max={series.max():.4f}"
    )

# CINC: bounded [0,1] (it's a global share)
cinc = wide['cinc'].dropna()
out_of_range = ((cinc < 0) | (cinc > 1)).sum()
check(
    "2.2 cinc all in [0,1]",
    out_of_range == 0,
    f"{out_of_range} out of range; min={cinc.min():.4f}, max={cinc.max():.4f}"
)

# Population: positive, in thousands; Western European countries
# range from ~3M (BEL 1820) to ~80M (DEU 2020) = 3,000 to 80,000 in Maddison
pop = wide['pop'].dropna()
check(
    "2.3 pop strictly positive",
    (pop > 0).all(),
    f"min={pop.min():.1f}"
)
check(
    "2.4 pop in plausible range [2000, 100000] thousand",
    (pop >= 2000).all() and (pop <= 100000).all(),
    f"min={pop.min():.1f}, max={pop.max():.1f}"
)

# GDP per capita: positive, in 2011 USD PPP; Western Europe
# ranges from ~1000 (1820) to ~50000 (2020)
gdppc = wide['gdppc'].dropna()
check(
    "2.5 gdppc strictly positive",
    (gdppc > 0).all(),
    f"min={gdppc.min():.1f}"
)
check(
    "2.6 gdppc in plausible range [500, 80000] (2011 USD PPP)",
    (gdppc >= 500).all() and (gdppc <= 80000).all(),
    f"min={gdppc.min():.1f}, max={gdppc.max():.1f}"
)

# =============================================================================
# CHECK 3 — Country-specific historical anchors
# =============================================================================

print("\n--- HISTORICAL ANCHOR CHECKS ---")

# France 1820: cinc ~0.123, v2x_libdem ~0.154, pop ~31250, gdppc ~1809
fra_1820 = wide[(wide['ISO3'] == 'FRA') & (wide['year'] == 1820)].iloc[0]
check(
    "3.1 FRA 1820 cinc ≈ 0.123",
    abs(fra_1820['cinc'] - 0.123) < 0.01,
    f"got {fra_1820['cinc']:.4f}"
)
check(
    "3.2 FRA 1820 v2x_libdem ≈ 0.154",
    abs(fra_1820['v2x_libdem'] - 0.154) < 0.01,
    f"got {fra_1820['v2x_libdem']:.4f}"
)
check(
    "3.3 FRA 1820 pop ≈ 31250 (thousands)",
    abs(fra_1820['pop'] - 31250) < 100,
    f"got {fra_1820['pop']:.1f}"
)
check(
    "3.4 FRA 1820 gdppc ≈ 1809 (2011 USD PPP)",
    abs(fra_1820['gdppc'] - 1809) < 20,
    f"got {fra_1820['gdppc']:.1f}"
)

# Germany sovereignty boundary: cinc should be NaN 1945-1954, present from 1955
deu_1949 = wide[(wide['ISO3'] == 'DEU') & (wide['year'] == 1949)]
check(
    "3.5 DEU 1949 cinc is NaN (FRG pre-sovereignty)",
    len(deu_1949) == 1 and pd.isna(deu_1949.iloc[0]['cinc']),
    "should be missing"
)

deu_1955 = wide[(wide['ISO3'] == 'DEU') & (wide['year'] == 1955)]
check(
    "3.6 DEU 1955 cinc is present (FRG sovereign)",
    len(deu_1955) == 1 and pd.notna(deu_1955.iloc[0]['cinc']),
    f"got cinc={deu_1955.iloc[0]['cinc']:.4f}" if len(deu_1955) == 1 else "row missing"
)

# Italy V-Dem boundary: NaN before 1862, present from 1862
ita_1850 = wide[(wide['ISO3'] == 'ITA') & (wide['year'] == 1850)]
check(
    "3.7 ITA 1850 v2x_libdem is NaN (pre-unification)",
    len(ita_1850) == 1 and pd.isna(ita_1850.iloc[0]['v2x_libdem']),
    "should be missing"
)

ita_1862 = wide[(wide['ISO3'] == 'ITA') & (wide['year'] == 1862)]
check(
    "3.8 ITA 1862 v2x_libdem is present (post-unification)",
    len(ita_1862) == 1 and pd.notna(ita_1862.iloc[0]['v2x_libdem']),
    f"got v2x_libdem={ita_1862.iloc[0]['v2x_libdem']:.4f}" if len(ita_1862) == 1 else "row missing"
)

# Belgium independence boundary
bel_1825 = wide[(wide['ISO3'] == 'BEL') & (wide['year'] == 1825)]
check(
    "3.9 BEL 1825 v2x_libdem is NaN (pre-independence)",
    len(bel_1825) == 1 and pd.isna(bel_1825.iloc[0]['v2x_libdem']),
    "should be missing"
)

bel_1830 = wide[(wide['ISO3'] == 'BEL') & (wide['year'] == 1830)]
check(
    "3.10 BEL 1830 v2x_libdem is present (independence)",
    len(bel_1830) == 1 and pd.notna(bel_1830.iloc[0]['v2x_libdem']),
    f"got v2x_libdem={bel_1830.iloc[0]['v2x_libdem']:.4f}" if len(bel_1830) == 1 else "row missing"
)

# =============================================================================
# CHECK 4 — Cross-country plausibility (sanity of relative magnitudes)
# =============================================================================

print("\n--- CROSS-COUNTRY PLAUSIBILITY CHECKS ---")

# 1900: France/Germany pop ratio ~ 0.6 to 0.7 (Germany was bigger)
fra_1900 = wide[(wide['ISO3'] == 'FRA') & (wide['year'] == 1900)].iloc[0]
deu_1900 = wide[(wide['ISO3'] == 'DEU') & (wide['year'] == 1900)].iloc[0]
ratio = fra_1900['pop'] / deu_1900['pop']
check(
    "4.1 FRA/DEU pop ratio in 1900 between 0.55 and 0.80",
    0.55 < ratio < 0.80,
    f"got ratio={ratio:.3f}"
)

# 2000: UK pop ~ 60M = 60000 thousand, with tolerance
gbr_2000 = wide[(wide['ISO3'] == 'GBR') & (wide['year'] == 2000)].iloc[0]
check(
    "4.2 GBR pop in 2000 between 55000 and 65000 thousand",
    55000 < gbr_2000['pop'] < 65000,
    f"got pop={gbr_2000['pop']:.1f}"
)

# Italy gdppc grew massively 1820 → 2000
ita_1820 = wide[(wide['ISO3'] == 'ITA') & (wide['year'] == 1820)].iloc[0]
ita_2000 = wide[(wide['ISO3'] == 'ITA') & (wide['year'] == 2000)].iloc[0]
growth = ita_2000['gdppc'] / ita_1820['gdppc']
check(
    "4.3 ITA gdppc 1820-2000 growth factor between 10 and 30",
    10 < growth < 30,
    f"got factor={growth:.2f} ({ita_1820['gdppc']:.0f} → {ita_2000['gdppc']:.0f})"
)

# v2x_libdem ranking in 2000: should be high for all (>0.7)
high_dem_2000 = []
for iso3 in ['FRA','GBR','DEU','ITA','ESP','NLD','SWE','BEL']:
    row = wide[(wide['ISO3'] == iso3) & (wide['year'] == 2000)]
    if len(row) == 1 and pd.notna(row.iloc[0]['v2x_libdem']):
        high_dem_2000.append((iso3, row.iloc[0]['v2x_libdem']))
all_high = all(v > 0.7 for _, v in high_dem_2000)
check(
    "4.4 All 8 countries v2x_libdem > 0.7 in year 2000",
    all_high,
    f"got: {high_dem_2000}"
)

# =============================================================================
# CHECK 5 — Temporal continuity (no weird gaps)
# =============================================================================

print("\n--- TEMPORAL CONTINUITY CHECKS ---")

# For FRA, GBR, ESP, NLD, SWE: no missing v2x_libdem in sub-window 1
for iso3 in ['FRA','GBR','ESP','NLD','SWE']:
    sub1 = wide[(wide['ISO3'] == iso3)
                & (wide['sub_window'] == '1820-1913')]
    missing = sub1['v2x_libdem'].isna().sum()
    check(
        f"5.1 {iso3} no missing v2x_libdem in 1820-1913",
        missing == 0,
        f"{missing} missing"
    )

# Maddison pop should be complete for all 8 countries in both sub-windows
for iso3 in ['FRA','GBR','DEU','ITA','ESP','NLD','SWE','BEL']:
    for sw in ['1820-1913', '1945-2020']:
        sub = wide[(wide['ISO3'] == iso3) & (wide['sub_window'] == sw)]
        missing = sub['pop'].isna().sum()
        if missing > 0:
            check(
                f"5.2 {iso3} {sw} pop missing",
                False,
                f"{missing} missing"
            )

# =============================================================================
# CHECK 6 — Listwise totals match expected
# =============================================================================

print("\n--- LISTWISE TOTALS ---")

VARIABLES = ['pop', 'gdppc', 'v2x_libdem', 'v2x_polyarchy', 'cinc']

sub1 = wide[wide['sub_window'] == '1820-1913']
sub2 = wide[wide['sub_window'] == '1945-2020']

listwise_sub1 = len(sub1.dropna(subset=VARIABLES))
listwise_sub2 = len(sub2.dropna(subset=VARIABLES))

check(
    "6.1 Listwise complete sub1 ≈ 684",
    abs(listwise_sub1 - 684) <= 5,
    f"got {listwise_sub1}"
)
check(
    "6.2 Listwise complete sub2 ≈ 566",
    abs(listwise_sub2 - 566) <= 5,
    f"got {listwise_sub2}"
)

total_listwise = listwise_sub1 + listwise_sub2
check(
    "6.3 Total listwise complete ≥ 1000 (well above 400 threshold)",
    total_listwise >= 1000,
    f"got {total_listwise}"
)

# =============================================================================
# Summary
# =============================================================================

print("\n" + "=" * 70)
print("SANITY CHECK SUMMARY")
print("=" * 70)

passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
print(f"Total checks: {len(results)}")
print(f"PASSED:       {passed}")
print(f"FAILED:       {failed}")

if failed > 0:
    print("\nFAILED CHECKS:")
    for name, status, details in results:
        if status == "FAIL":
            print(f"  - {name}: {details}")
else:
    print("\nAll checks passed. The panel is ready for §6 of WP-2026-006.")
