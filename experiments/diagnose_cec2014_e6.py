"""E6 - Diagnose anomalous SCHO run distributions on CEC 2014.

This stage uses the EXISTING E4 raw file only.
It does NOT rerun GWO or SCHO.

Input
-----
results/raw/cec2014_e4_runs.csv

Focus functions
---------------
F2, F7, F15, F21, F23, F27
F28 is included as a control because the paper/reproduction both show
a deterministic 3000 plateau there.

Outputs
-------
results/processed/E6_scho_anomaly_stats.csv
results/processed/E6_scho_selected_runs.csv
results/processed/E6_gwo_vs_scho_rank_sum.csv
report/figures/E6_scho_error_by_run.png
report/figures/E6_scho_error_boxplot.png
report/notes/E6_scho_anomaly_report.md

Run from project root:
    python -m experiments.diagnose_cec2014_e6
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mannwhitneyu


RAW_PATH = Path("results/raw/cec2014_e4_runs.csv")

STATS_PATH = Path("results/processed/E6_scho_anomaly_stats.csv")
SELECTED_PATH = Path("results/processed/E6_scho_selected_runs.csv")
RANKSUM_PATH = Path("results/processed/E6_gwo_vs_scho_rank_sum.csv")

FIG_RUNS_PATH = Path("report/figures/E6_scho_error_by_run.png")
FIG_BOX_PATH = Path("report/figures/E6_scho_error_boxplot.png")

REPORT_PATH = Path("report/notes/E6_scho_anomaly_report.md")

FOCUS = ["F2", "F7", "F15", "F21", "F23", "F27", "F28"]

EXPECTED_RUNS = 30
EXPECTED_ALGORITHMS = {"GWO", "SCHO"}

# Paper Table 14 values used only for diagnostic comparison.
PAPER_SCHO = {
    "F2":  {"Best": 1.4696e6, "Mean": 2.6184e8, "STD": 4.1319e8},
    "F7":  {"Best": 7.0091e2, "Mean": 7.0848e2, "STD": 1.2273e1},
    "F15": {"Best": 1.5017e3, "Mean": 1.5075e3, "STD": 1.1348e1},
    "F21": {"Best": 2.6731e3, "Mean": 1.0567e4, "STD": 6.8773e3},
    "F23": {"Best": 2.3118e3, "Mean": 2.4937e3, "STD": 3.4361e1},
    "F27": {"Best": 2.7039e3, "Mean": 2.8683e3, "STD": 7.2135e1},
    "F28": {"Best": 3.0000e3, "Mean": 3.0000e3, "STD": 0.0},
}

OPTIMUM = {f"F{i}": float(100 * i) for i in range(1, 31)}


def function_number(name: str) -> int:
    return int(name[1:])


def load_rows():
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Missing {RAW_PATH}\n"
            "E6 requires the E4 raw run file. "
            "Do not rerun E4 if that file already exists."
        )

    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    return rows


def validate_e4_raw(rows):
    if not rows:
        raise AssertionError("E4 raw file is empty.")

    required = {
        "Function", "Algorithm", "Run", "Seed",
        "Optimum", "BestScore", "Error", "Status"
    }
    missing = required - set(rows[0].keys())
    if missing:
        raise AssertionError(
            f"E4 raw file is missing columns: {sorted(missing)}"
        )

    pass_rows = [r for r in rows if r["Status"] == "PASS"]

    if len(pass_rows) != 1800:
        raise AssertionError(
            f"Expected 1800 PASS rows from E4, got {len(pass_rows)}."
        )

    for func in [f"F{i}" for i in range(1, 31)]:
        for alg in EXPECTED_ALGORITHMS:
            group = [
                r for r in pass_rows
                if r["Function"] == func and r["Algorithm"] == alg
            ]
            if len(group) != EXPECTED_RUNS:
                raise AssertionError(
                    f"{func} {alg}: expected 30 PASS rows, got {len(group)}"
                )

            runs = sorted(int(r["Run"]) for r in group)
            if runs != list(range(1, 31)):
                raise AssertionError(
                    f"{func} {alg}: run numbers are incomplete."
                )

    return pass_rows


def score_array(rows, func, alg):
    group = [
        r for r in rows
        if r["Function"] == func and r["Algorithm"] == alg
    ]
    group.sort(key=lambda r: int(r["Run"]))
    return np.asarray([float(r["BestScore"]) for r in group], dtype=float)


def error_array(rows, func, alg):
    group = [
        r for r in rows
        if r["Function"] == func and r["Algorithm"] == alg
    ]
    group.sort(key=lambda r: int(r["Run"]))
    return np.asarray([float(r["Error"]) for r in group], dtype=float)


def count_plateau(values, tolerance=1e-10):
    """Largest number of scores equal to the same value within tolerance."""
    vals = np.sort(np.asarray(values, dtype=float))
    best_count = 0
    best_value = None

    for v in vals:
        count = int(np.sum(np.isclose(vals, v, rtol=0.0, atol=tolerance)))
        if count > best_count:
            best_count = count
            best_value = float(v)

    return best_count, best_value


def safe_ratio(a, b):
    if abs(b) <= 1e-15:
        if abs(a) <= 1e-15:
            return 1.0
        return math.inf
    return a / b


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 104)
    print("E6 - SCHO anomalous-distribution diagnostic")
    print("=" * 104)
    print(f"Input : {RAW_PATH}")
    print("No optimization reruns will be performed.")
    print(f"Focus : {', '.join(FOCUS)}")
    print("=" * 104)

    raw_rows = load_rows()
    rows = validate_e4_raw(raw_rows)

    # ------------------------------------------------------------
    # 1. Selected raw runs
    # ------------------------------------------------------------
    selected = [
        r for r in rows
        if r["Function"] in FOCUS
    ]
    selected.sort(
        key=lambda r: (
            function_number(r["Function"]),
            r["Algorithm"],
            int(r["Run"]),
        )
    )
    write_csv(SELECTED_PATH, list(selected[0].keys()), selected)

    # ------------------------------------------------------------
    # 2. Detailed SCHO diagnostic statistics
    # ------------------------------------------------------------
    stat_rows = []

    print("\nSCHO diagnostics")
    print("-" * 104)

    for func in FOCUS:
        scores = score_array(rows, func, "SCHO")
        errors = error_array(rows, func, "SCHO")
        paper = PAPER_SCHO[func]
        opt = OPTIMUM[func]

        q1, med, q3 = np.percentile(scores, [25, 50, 75])
        err_q1, err_med, err_q3 = np.percentile(errors, [25, 50, 75])

        plateau_count, plateau_value = count_plateau(scores)
        unique_12 = len(np.unique(np.round(scores, 12)))

        mean_score = float(np.mean(scores))
        std_score = float(np.std(scores, ddof=1))
        mean_error = float(np.mean(errors))
        paper_mean_error = float(paper["Mean"] - opt)

        mean_error_ratio = safe_ratio(mean_error, paper_mean_error)
        std_ratio = safe_ratio(std_score, paper["STD"])

        # Robust outlier diagnostics.
        iqr = float(q3 - q1)
        upper_fence = float(q3 + 1.5 * iqr)
        lower_fence = float(q1 - 1.5 * iqr)
        outliers = int(np.sum((scores < lower_fence) | (scores > upper_fence)))

        # How much does the single worst run affect the mean?
        scores_wo_worst = np.delete(scores, int(np.argmax(scores)))
        mean_wo_worst = float(np.mean(scores_wo_worst))
        worst_mean_inflation = mean_score - mean_wo_worst

        row = {
            "Function": func,
            "Optimum": opt,
            "Min": float(np.min(scores)),
            "Q1": float(q1),
            "Median": float(med),
            "Q3": float(q3),
            "Max": float(np.max(scores)),
            "Mean": mean_score,
            "Std_sample_ddof1": std_score,
            "IQR": iqr,
            "IQR_Outlier_Count": outliers,
            "UniqueScores_rounded12": unique_12,
            "LargestPlateauCount": plateau_count,
            "LargestPlateauFraction": plateau_count / EXPECTED_RUNS,
            "LargestPlateauValue": plateau_value,
            "Error_Q1": float(err_q1),
            "Error_Median": float(err_med),
            "Error_Q3": float(err_q3),
            "Paper_Best": paper["Best"],
            "Paper_Mean": paper["Mean"],
            "Paper_STD": paper["STD"],
            "Paper_Mean_Error": paper_mean_error,
            "Repro_Mean_Error": mean_error,
            "Mean_Error_Ratio": mean_error_ratio,
            "STD_Ratio": std_ratio,
            "Mean_without_worst_run": mean_wo_worst,
            "Worst_run_mean_inflation": worst_mean_inflation,
        }
        stat_rows.append(row)

        print(
            f"{func:<4} "
            f"min={row['Min']:.8e} "
            f"median={row['Median']:.8e} "
            f"mean={row['Mean']:.8e} "
            f"max={row['Max']:.8e} "
            f"plateau={plateau_count:02d}/30 @ {plateau_value:.8e} "
            f"outliers={outliers}"
        )

    write_csv(STATS_PATH, list(stat_rows[0].keys()), stat_rows)

    # ------------------------------------------------------------
    # 3. GWO vs SCHO two-sided Wilcoxon rank-sum equivalent
    #    (Mann-Whitney U for independent samples)
    # ------------------------------------------------------------
    rank_rows = []

    for i in range(1, 31):
        func = f"F{i}"
        gwo = score_array(rows, func, "GWO")
        scho = score_array(rows, func, "SCHO")

        test = mannwhitneyu(
            scho,
            gwo,
            alternative="two-sided",
            method="auto",
        )

        scho_med = float(np.median(scho))
        gwo_med = float(np.median(gwo))

        if test.pvalue < 0.05:
            if scho_med < gwo_med:
                sig = "SCHO better"
            elif gwo_med < scho_med:
                sig = "GWO better"
            else:
                sig = "Significant, equal median"
        else:
            sig = "No significant difference"

        rank_rows.append({
            "Function": func,
            "Family": next(
                r["Family"] for r in rows
                if r["Function"] == func
            ),
            "SCHO_Median": scho_med,
            "GWO_Median": gwo_med,
            "U_statistic": float(test.statistic),
            "p_value_two_sided": float(test.pvalue),
            "alpha": 0.05,
            "Interpretation": sig,
        })

    write_csv(RANKSUM_PATH, list(rank_rows[0].keys()), rank_rows)

    # ------------------------------------------------------------
    # 4. Figure: SCHO error by run number
    # ------------------------------------------------------------
    FIG_RUNS_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    for func in FOCUS:
        errs = error_array(rows, func, "SCHO")
        runs = np.arange(1, EXPECTED_RUNS + 1)
        # log10(error) is appropriate here: selected functions all have >0 error.
        log_errs = np.log10(errs)
        ax.plot(runs, log_errs, marker="o", markersize=3, label=func)

    ax.set_title("E6: SCHO CEC2014 run-level error trajectories")
    ax.set_xlabel("Run number (seed = 999 + run)")
    ax.set_ylabel("log10(BestScore - optimum)")
    ax.grid(alpha=0.25)
    ax.legend(ncol=4)
    fig.tight_layout()
    fig.savefig(FIG_RUNS_PATH, dpi=220, bbox_inches="tight")
    plt.close(fig)

    # ------------------------------------------------------------
    # 5. Figure: SCHO error boxplot
    # ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    log_error_data = [
        np.log10(error_array(rows, func, "SCHO"))
        for func in FOCUS
    ]
    ax.boxplot(log_error_data, labels=FOCUS)
    ax.set_title("E6: SCHO run distribution on selected CEC2014 functions")
    ax.set_xlabel("Function")
    ax.set_ylabel("log10(BestScore - optimum)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_BOX_PATH, dpi=220, bbox_inches="tight")
    plt.close(fig)

    # ------------------------------------------------------------
    # 6. Auto-generated markdown report
    # ------------------------------------------------------------
    by_func = {r["Function"]: r for r in stat_rows}

    f21 = by_func["F21"]
    f23 = by_func["F23"]
    f27 = by_func["F27"]
    f28 = by_func["F28"]

    sig_counts = {}
    for label in (
        "SCHO better",
        "GWO better",
        "No significant difference",
        "Significant, equal median",
    ):
        sig_counts[label] = sum(
            r["Interpretation"] == label
            for r in rank_rows
        )

    report = f"""# E6 — CEC2014 SCHO anomalous-distribution diagnostic

## 1. Purpose

E6 uses the existing E4 raw results only. No GWO/SCHO optimization was rerun and no algorithm parameter was changed.

Focus functions: {", ".join(FOCUS)}.

F2, F7, F15 and F21 were selected because their reproduced SCHO mean excess-error fell outside the factor-2 band relative to Bai et al. Table 14. F23 and F27 were selected because the reproduced 30-run STD was exactly zero while the paper reported nonzero variation. F28 is a control case because both paper and reproduction show the 3000 plateau with STD=0.

## 2. Main run-level findings

### F21 — outlier-driven instability

Reproduced SCHO:

- Min: {f21['Min']:.8e}
- Median: {f21['Median']:.8e}
- Mean: {f21['Mean']:.8e}
- Max: {f21['Max']:.8e}
- Sample STD: {f21['Std_sample_ddof1']:.8e}
- IQR outliers: {f21['IQR_Outlier_Count']}
- Mean without the single worst run: {f21['Mean_without_worst_run']:.8e}

The large separation between median and mean, together with extreme upper-tail runs, confirms that the E5 F21 mismatch is primarily distributional rather than a uniform shift of every run.

### F23 — deterministic reproduced plateau

Largest repeated plateau: {f23['LargestPlateauCount']}/30 runs at {f23['LargestPlateauValue']:.8e}.

The paper reports nonzero STD and a better Best value, so the current Python source-faithful trajectory does not reproduce the paper's F23 run-to-run distribution.

### F27 — deterministic reproduced plateau

Largest repeated plateau: {f27['LargestPlateauCount']}/30 runs at {f27['LargestPlateauValue']:.8e}.

Again, this differs from the paper's nonzero variation.

### F28 — useful control

Largest repeated plateau: {f28['LargestPlateauCount']}/30 runs at {f28['LargestPlateauValue']:.8e}.

Here the zero-variance plateau is consistent with the paper, so a plateau by itself is not evidence that the CEC evaluator is broken.

## 3. Other selected functions

F2, F7 and F15 should be read as stochastic/search-trajectory mismatches: their reproduced SCHO run distributions do not match the paper's mean-error scale as closely as most other functions.

See `E6_scho_anomaly_stats.csv` for quartiles, IQR outliers, plateau counts, paper/reproduction ratios, and worst-run sensitivity.

## 4. Pairwise GWO vs SCHO rank-sum diagnostic

Using the 30 independent E4 runs for each algorithm and a two-sided Mann–Whitney U test (the standard independent-sample Wilcoxon rank-sum formulation), alpha=0.05:

- SCHO better: {sig_counts['SCHO better']} functions
- GWO better: {sig_counts['GWO better']} functions
- No significant difference: {sig_counts['No significant difference']} functions
- Significant with equal sample medians: {sig_counts['Significant, equal median']} functions

These tests describe the current Python reproduction only. They are not a reproduction of the paper's full Table 15 because the paper compares SCHO against eight other algorithms, not only GWO.

## 5. Interpretation

E6 supports three conclusions:

1. The SCHO-paper mismatch is not one single failure mode. F21 is heavy-tail/outlier-driven, whereas F23/F27 are deterministic plateau mismatches.
2. F28 shows that a deterministic plateau can also be genuinely consistent with the paper.
3. There is still no justification for tuning the frozen SCHO implementation. The correct next step is to document these differences and preserve the source-faithful implementation.

## 6. Files

- `results/processed/E6_scho_anomaly_stats.csv`
- `results/processed/E6_scho_selected_runs.csv`
- `results/processed/E6_gwo_vs_scho_rank_sum.csv`
- `report/figures/E6_scho_error_by_run.png`
- `report/figures/E6_scho_error_boxplot.png`
- `report/notes/E6_scho_anomaly_report.md`
"""

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    print("\n" + "-" * 104)
    print("E6 output")
    print("-" * 104)
    print(f"Saved: {STATS_PATH}")
    print(f"Saved: {SELECTED_PATH}")
    print(f"Saved: {RANKSUM_PATH}")
    print(f"Saved: {FIG_RUNS_PATH}")
    print(f"Saved: {FIG_BOX_PATH}")
    print(f"Saved: {REPORT_PATH}")
    print()
    print("E6 RESULT: COMPLETE")
    print("No optimizer reruns were performed.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
