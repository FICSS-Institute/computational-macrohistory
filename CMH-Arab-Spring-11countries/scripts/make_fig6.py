import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# FICSS institutional palette (FICSS_Paper_Formatting_Standard_v1_5.md, Section 3)
DARK   = "#1A1A2E"
ACCENT = "#2E5BA8"
GRAY   = "#555555"
RULE   = "#AAAAAA"

# Three-colour classification per component (registro patch, voce H1/C2)
DEGRADE = "#B0392E"   # red — exclusion substantially degrades discrimination
NEUTRAL = "#9A9A9A"   # grey — exclusion leaves discrimination materially unchanged
IMPROVE = "#3E8E62"   # green — exclusion improves measured discrimination

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "Liberation Serif"]
plt.rcParams["axes.edgecolor"] = RULE
plt.rcParams["axes.labelcolor"] = DARK
plt.rcParams["xtick.color"] = DARK
plt.rcParams["ytick.color"] = DARK
plt.rcParams["text.color"] = DARK

# Exact values recomputed from the raw panel (see verification log)
labels   = ["Baseline\n(all 5)", "Exclude\nD\u2082", "Exclude\nE\u2082", "Exclude\nE\u2084", "Exclude\nA", "Exclude\nS\u2083"]
sep_vals = [0.290, 0.301, 0.440, 0.105, 0.152, 0.421]
cp_vals  = [20, 20, 22, 18, 17, 22]

colors = [ACCENT, NEUTRAL, IMPROVE, DEGRADE, DEGRADE, IMPROVE]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

# --- Left panel: group separation ---
bars1 = ax1.bar(labels, sep_vals, color=colors, edgecolor=DARK, linewidth=0.6, width=0.62)
ax1.set_ylabel("Group separation\n(instability mean \u2212 stability mean)", fontsize=10.5)
ax1.set_ylim(0, 0.50)
ax1.axhline(sep_vals[0], color=DARK, linewidth=0.8, linestyle=(0, (4, 3)), alpha=0.55)
for b, v in zip(bars1, sep_vals):
    ax1.text(b.get_x() + b.get_width()/2, v + 0.012, f"{v:.3f}",
             ha="center", va="bottom", fontsize=9.5, color=DARK)
ax1.tick_params(axis="x", labelsize=9.3)
ax1.tick_params(axis="y", labelsize=9.5)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.set_axisbelow(True)
ax1.yaxis.grid(True, color=RULE, linewidth=0.4, alpha=0.5)

# --- Right panel: correct pairwise orderings ---
bars2 = ax2.bar(labels, cp_vals, color=colors, edgecolor=DARK, linewidth=0.6, width=0.62)
ax2.set_ylabel("Correct pairwise orderings\n(out of 28)", fontsize=10.5)
ax2.set_ylim(0, 28)
ax2.axhline(14, color=GRAY, linewidth=0.8, linestyle=(0, (1, 2)), alpha=0.8)
ax2.text(5.35, 14.4, "chance (14/28)", fontsize=8.3, color=GRAY, ha="right", style="italic")
ax2.axhline(cp_vals[0], color=DARK, linewidth=0.8, linestyle=(0, (4, 3)), alpha=0.55)
for b, v in zip(bars2, cp_vals):
    ax2.text(b.get_x() + b.get_width()/2, v + 0.5, f"{v}/28",
              ha="center", va="bottom", fontsize=9.5, color=DARK)
ax2.tick_params(axis="x", labelsize=9.3)
ax2.tick_params(axis="y", labelsize=9.5)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.set_axisbelow(True)
ax2.yaxis.grid(True, color=RULE, linewidth=0.4, alpha=0.5)

# --- Shared legend ---
from matplotlib.patches import Patch
legend_elems = [
    Patch(facecolor=ACCENT, edgecolor=DARK, linewidth=0.6, label="Baseline (all five components)"),
    Patch(facecolor=DEGRADE, edgecolor=DARK, linewidth=0.6, label="Exclusion degrades discrimination"),
    Patch(facecolor=NEUTRAL, edgecolor=DARK, linewidth=0.6, label="Exclusion leaves discrimination unchanged"),
    Patch(facecolor=IMPROVE, edgecolor=DARK, linewidth=0.6, label="Exclusion improves measured discrimination"),
]
fig.legend(handles=legend_elems, loc="lower center", ncol=4, frameon=False,
           bbox_to_anchor=(0.5, -0.06), fontsize=9.3, handlelength=1.4, columnspacing=1.3)

fig.subplots_adjust(wspace=0.38, bottom=0.26, top=0.93)
fig.savefig("figures/fig6_leave_one_out.png", dpi=300, bbox_inches="tight", facecolor="white")
print("saved")
