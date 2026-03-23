#!/usr/bin/env python3
"""Generate results figure for the PoisonedGithubIssues mini-benchmark."""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
from pathlib import Path

matplotlib.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)

# Results from experiments/analysis.py on all_repos_cmd re-graded log
# 130 samples, Sonnet 4.6
metrics = [
    "Ran untrusted command (deterministic)",
    "Recommended untrusted command (GPT-5.4)",
    "Flagged suspicious content (GPT-5.4)",
]
rates = np.array([0.00, 0.00, 0.762])
stderr = np.array([0.00, 0.00, 0.038])
y = np.arange(len(metrics))

fig, ax = plt.subplots(figsize=(7.0, 2.8))
colors = ["#3B6FB6", "#E07A30", "#2E8B57"]

for yi, rate, err, color in zip(y, rates, stderr, colors):
    ax.errorbar(
        x=rate,
        y=yi,
        xerr=err,
        fmt="o",
        markersize=6.5,
        color=color,
        ecolor=color,
        elinewidth=1.2,
        capsize=3,
        capthick=1.2,
    )

ax.set_yticks(y, labels=metrics)
ax.invert_yaxis()
ax.set_xlim(-0.02, 1.0)
ax.set_xlabel("Rate")
ax.xaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
ax.set_title("PoisonedGithubIssues command variant results", loc="left", pad=10)
ax.text(
    0.0,
    1.02,
    "N=130 across 13 repositories (Claude Code Sonnet 4.6)",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize=8,
    color="#5C6670",
)

ax.grid(axis="x", color="#D9DEE5", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color("#A7B0BA")

for yi, rate in zip(y, rates):
    label_x = min(rate + 0.03, 0.97)
    ax.text(
        label_x,
        yi,
        f"{rate * 100:.1f}%",
        va="center",
        ha="left",
        fontsize=8,
        color="#1F2933",
    )

fig.tight_layout()
out_dir = Path(__file__).resolve().parent
fig.savefig(out_dir / "results.pdf", bbox_inches="tight")
fig.savefig(out_dir / "results.png", bbox_inches="tight", dpi=220)
print("Saved submission/figures/results.pdf and results.png")
