from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "processed" / "gwo_classic23_comparison.csv"
OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)
eps = 1e-30

df["Our_Gap"] = np.abs(df["Our_Mean"] - df["Theoretical_Optimum"])
df["Paper_Gap"] = np.abs(df["Paper_Mean"] - df["Theoretical_Optimum"])
df["Mean_Abs_Diff"] = np.abs(df["Our_Mean"] - df["Paper_Mean"])
df["Run_Spread"] = np.abs(df["Worst"] - df["Best"])

x = np.arange(len(df))

fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(x, np.log10(df["Our_Gap"] + eps), marker="o", label="Our reproduction")
ax.plot(x, np.log10(df["Paper_Gap"] + eps), marker="s", label="GWO paper")
ax.set_xticks(x)
ax.set_xticklabels(df["Function"], rotation=45)
ax.set_ylabel("log10(|Mean - theoretical optimum|)")
ax.set_xlabel("Benchmark function")
ax.set_title("GWO reproduction vs paper: mean distance to theoretical optimum")
ax.grid(True, alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "gwo_mean_gap_to_optimum.png", dpi=220, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(13, 6))
ax.bar(df["Function"], np.log10(df["Mean_Abs_Diff"] + eps))
ax.set_ylabel("log10(|Our Mean - Paper Mean|)")
ax.set_xlabel("Benchmark function")
ax.set_title("Absolute difference between reproduced and paper mean values")
ax.tick_params(axis="x", rotation=45)
ax.grid(True, axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "gwo_mean_difference_vs_paper.png", dpi=220, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(13, 6))
ax.bar(df["Function"], np.log10(df["Run_Spread"] + eps))
ax.set_ylabel("log10(|Worst - Best|)")
ax.set_xlabel("Benchmark function")
ax.set_title("GWO reproduction: spread across 30 independent runs")
ax.tick_params(axis="x", rotation=45)
ax.grid(True, axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "gwo_30run_spread.png", dpi=220, bbox_inches="tight")
plt.close(fig)

print(f"Figures saved to: {OUT}")
