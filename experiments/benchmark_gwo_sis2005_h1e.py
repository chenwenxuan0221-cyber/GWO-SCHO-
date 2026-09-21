"""H1e - Formal 30-run GWO reproduction on SIS2005 CF1-CF6 (paper F24-F29).

Primary benchmark definition
----------------------------
Source-faithful port of the uploaded original `SIS_novel_func.m` and D=10
MAT assets. In particular, F26/CF3 follows the source (10 Rastrigin
components), while the GWO paper Table 4's Griewank wording is retained only
as a separately documented diagnostic discrepancy.

Protocol
--------
Functions : F24-F29 / CF1-CF6
Dimension : D=10
Bounds    : [-5,5]^10
Population: N=30
MaxIter   : 500
Runs      : 30 per function
Seeds     : 1000..1029 (project reproducibility convention)

Outputs
-------
results/raw/gwo_sis2005_h1e_runs.csv
results/processed/gwo_sis2005_h1e_summary.csv
report/gwo_sis2005_h1e_table8_comparison.md

Notes
-----
- The GWO paper states 30 runs for each benchmark function but does not state
  the random seeds. Seeds 1000..1029 are therefore a project convention.
- Sample STD (ddof=1) is the primary paper-comparison STD; population STD is
  saved as a diagnostic.
- The script checkpoints after EVERY completed optimizer run and safely resumes.
- A numerical mismatch with the paper does NOT make the script fail. H1e PASS
  means the formal experiment completed structurally and its evidence files
  were generated.
- algorithms/gwo.py is not modified.
"""

from __future__ import annotations

import csv
from pathlib import Path
import time

import numpy as np

from algorithms.gwo import gwo
from benchmarks.gwo_sis2005 import get_sis2005_benchmark


FUNCTIONS = [f"F{i}" for i in range(24, 30)]

N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_SEED = 1000
VARIANT = "source_faithful"

RAW_PATH = Path("results/raw/gwo_sis2005_h1e_runs.csv")
SUMMARY_PATH = Path("results/processed/gwo_sis2005_h1e_summary.csv")
REPORT_PATH = Path("report/gwo_sis2005_h1e_table8_comparison.md")

RAW_FIELDS = [
    "Function",
    "Canonical",
    "Variant",
    "Run",
    "Seed",
    "Population",
    "MaxIter",
    "Dimension",
    "LowerBound",
    "UpperBound",
    "Optimum",
    "BestScore",
    "Curve0",
    "CurveLast",
    "ElapsedSeconds",
    "Status",
]

SUMMARY_FIELDS = [
    "Function",
    "Canonical",
    "Variant",
    "Runs",
    "Population",
    "MaxIter",
    "Dimension",
    "Best",
    "Mean",
    "Std_sample_ddof1",
    "Std_population_ddof0",
    "Worst",
    "PaperMean",
    "PaperStd",
    "MeanGap",
    "MeanAbsGap",
    "MeanRatio_repro_over_paper",
    "StdRatio_repro_over_paper",
]


def validate_run(*, benchmark, best_score, best_pos, curve):
    best_score = float(best_score)
    best_pos = np.asarray(best_pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    if not np.isfinite(best_score):
        raise AssertionError(f"{benchmark.paper_name}: best_score is NaN/Inf")

    if best_pos.shape != (benchmark.dim,):
        raise AssertionError(
            f"{benchmark.paper_name}: best_pos shape {best_pos.shape} "
            f"!= {(benchmark.dim,)}"
        )

    if not np.all(np.isfinite(best_pos)):
        raise AssertionError(f"{benchmark.paper_name}: best_pos contains NaN/Inf")

    tol = 1e-12
    if np.any(best_pos < benchmark.lb - tol) or np.any(best_pos > benchmark.ub + tol):
        raise AssertionError(f"{benchmark.paper_name}: best_pos violates bounds")

    if curve.shape != (MAX_ITER,):
        raise AssertionError(
            f"{benchmark.paper_name}: curve shape {curve.shape} != {(MAX_ITER,)}"
        )

    if not np.all(np.isfinite(curve)):
        raise AssertionError(
            f"{benchmark.paper_name}: convergence curve contains NaN/Inf"
        )

    if np.any(np.diff(curve) > tol):
        idx = int(np.flatnonzero(np.diff(curve) > tol)[0])
        raise AssertionError(
            f"{benchmark.paper_name}: historical-best curve increased "
            f"at {idx}->{idx+1}"
        )

    if not np.isclose(best_score, curve[-1], rtol=1e-12, atol=1e-12):
        raise AssertionError(
            f"{benchmark.paper_name}: best_score {best_score} != curve[-1] {curve[-1]}"
        )

    # Global minimum is 0. Tiny numerical undershoot only is tolerated.
    if best_score < benchmark.optimum - 1e-8:
        raise AssertionError(
            f"{benchmark.paper_name}: best_score={best_score} "
            f"is below known optimum={benchmark.optimum}"
        )


def ensure_dirs():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def _normalize_raw_row(row):
    return {
        "Function": row["Function"],
        "Canonical": row["Canonical"],
        "Variant": row["Variant"],
        "Run": int(row["Run"]),
        "Seed": int(row["Seed"]),
        "Population": int(row["Population"]),
        "MaxIter": int(row["MaxIter"]),
        "Dimension": int(row["Dimension"]),
        "LowerBound": float(row["LowerBound"]),
        "UpperBound": float(row["UpperBound"]),
        "Optimum": float(row["Optimum"]),
        "BestScore": float(row["BestScore"]),
        "Curve0": float(row["Curve0"]),
        "CurveLast": float(row["CurveLast"]),
        "ElapsedSeconds": float(row["ElapsedSeconds"]),
        "Status": row["Status"],
    }


def row_matches_protocol(row):
    try:
        return (
            row["Function"] in FUNCTIONS
            and row["Variant"] == VARIANT
            and int(row["Population"]) == N
            and int(row["MaxIter"]) == MAX_ITER
            and int(row["Dimension"]) == 10
            and 1 <= int(row["Run"]) <= N_RUNS
            and int(row["Seed"]) == BASE_SEED + int(row["Run"]) - 1
            and row["Status"] == "PASS"
        )
    except Exception:
        return False


def load_existing_rows():
    if not RAW_PATH.exists():
        return [], set()

    rows = []
    completed = set()

    with RAW_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames != RAW_FIELDS:
            raise RuntimeError(
                f"Unexpected columns in {RAW_PATH}.\n"
                f"Expected: {RAW_FIELDS}\n"
                f"Found   : {reader.fieldnames}"
            )

        for disk_row in reader:
            row = _normalize_raw_row(disk_row)

            if not row_matches_protocol(row):
                raise RuntimeError(
                    "Existing H1e raw file contains a row from a different protocol: "
                    f"{row}"
                )

            key = (row["Function"], row["Run"])
            if key in completed:
                raise RuntimeError(f"Duplicate H1e raw result: {key}")

            completed.add(key)
            rows.append(row)

    return rows, completed


def append_raw(row):
    new_file = not RAW_PATH.exists()
    with RAW_PATH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def build_summary(rows):
    summary = []

    for name in FUNCTIONS:
        benchmark = get_sis2005_benchmark(name, variant=VARIANT)

        group = sorted(
            [
                row for row in rows
                if (
                    row["Function"] == name
                    and row["Variant"] == VARIANT
                    and row_matches_protocol(row)
                )
            ],
            key=lambda row: row["Run"],
        )

        if len(group) != N_RUNS:
            raise RuntimeError(
                f"{name}: expected {N_RUNS} PASS rows, got {len(group)}"
            )

        expected_runs = list(range(1, N_RUNS + 1))
        actual_runs = [row["Run"] for row in group]
        if actual_runs != expected_runs:
            raise RuntimeError(
                f"{name}: run numbers are incomplete or unordered: {actual_runs}"
            )

        scores = np.asarray([row["BestScore"] for row in group], dtype=float)

        mean = float(np.mean(scores))
        std_sample = float(np.std(scores, ddof=1))
        std_pop = float(np.std(scores, ddof=0))

        paper_mean = float(benchmark.paper_mean)
        paper_std = float(benchmark.paper_std)

        summary.append(
            {
                "Function": name,
                "Canonical": benchmark.canonical_name,
                "Variant": VARIANT,
                "Runs": N_RUNS,
                "Population": N,
                "MaxIter": MAX_ITER,
                "Dimension": benchmark.dim,
                "Best": float(np.min(scores)),
                "Mean": mean,
                "Std_sample_ddof1": std_sample,
                "Std_population_ddof0": std_pop,
                "Worst": float(np.max(scores)),
                "PaperMean": paper_mean,
                "PaperStd": paper_std,
                "MeanGap": mean - paper_mean,
                "MeanAbsGap": abs(mean - paper_mean),
                "MeanRatio_repro_over_paper": mean / paper_mean,
                "StdRatio_repro_over_paper": std_sample / paper_std,
            }
        )

    return summary


def write_summary(summary):
    with SUMMARY_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary)


def classify_ratio(ratio):
    if 0.75 <= ratio <= 1.25:
        return "within ±25%"
    if 0.5 <= ratio <= 2.0:
        return "within factor 2"
    return "outside factor 2"


def write_report(summary):
    lines = [
        "# H1e — GWO SIS2005 F24–F29 30-run reproduction",
        "",
        "## Protocol",
        "",
        f"- Benchmark: source-faithful SIS2005 CF1–CF6 (`{VARIANT}`)",
        "- Paper aliases: F24–F29",
        "- Dimension: 10",
        "- Bounds: [-5, 5]^10",
        f"- Population: {N}",
        f"- MaxIter: {MAX_ITER}",
        f"- Runs: {N_RUNS} per function",
        f"- Seeds: {BASE_SEED}–{BASE_SEED + N_RUNS - 1} "
        "(project reproducibility convention; paper does not report seeds)",
        "- Primary STD for paper comparison: sample STD (`ddof=1`)",
        "",
        "## Table 8 comparison",
        "",
        "| Function | Repro Best | Repro Mean | Repro STD | Paper Mean | Paper STD | Mean ratio | Mean agreement |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    for row in summary:
        ratio = row["MeanRatio_repro_over_paper"]
        lines.append(
            f"| {row['Function']} / {row['Canonical']} "
            f"| {row['Best']:.10g} "
            f"| {row['Mean']:.10g} "
            f"| {row['Std_sample_ddof1']:.10g} "
            f"| {row['PaperMean']:.10g} "
            f"| {row['PaperStd']:.10g} "
            f"| {ratio:.4f} "
            f"| {classify_ratio(ratio)} |"
        )

    within_25 = sum(
        0.75 <= row["MeanRatio_repro_over_paper"] <= 1.25 for row in summary
    )
    within_2 = sum(
        0.5 <= row["MeanRatio_repro_over_paper"] <= 2.0 for row in summary
    )

    lines += [
        "",
        "## Mechanical summary",
        "",
        f"- Mean within ±25% of paper: {within_25}/6",
        f"- Mean within factor 2 of paper: {within_2}/6",
        "",
        "These counts are descriptive diagnostics only. They are not used to tune",
        "the optimizer or benchmark implementation.",
        "",
        "## Source discrepancy reminder",
        "",
        "F26/CF3 in the uploaded original `SIS_novel_func.m` uses ten Rastrigin",
        "components, whereas GWO Table 4 prints ten Griewank components. H1e uses",
        "the source-faithful Rastrigin definition. The paper-table definition remains",
        "a diagnostic variant and is not silently substituted.",
        "",
        "## Interpretation rule",
        "",
        "H1e completion establishes the 30-run evidence set. Agreement or disagreement",
        "with Table 8 must be interpreted afterward without parameter tuning.",
        "",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def print_summary(summary):
    print("\n" + "=" * 132)
    print("H1e summary - GWO SIS2005 CF1-CF6 x 30 runs")
    print("=" * 132)
    print(
        f"{'Func':<10}"
        f"{'Best':>16}"
        f"{'Mean':>16}"
        f"{'Std(n-1)':>16}"
        f"{'PaperMean':>16}"
        f"{'PaperStd':>16}"
        f"{'MeanRatio':>14}"
        f"{'Agreement':>22}"
    )
    print("-" * 132)

    for row in summary:
        ratio = row["MeanRatio_repro_over_paper"]
        print(
            f"{row['Function']+'/'+row['Canonical']:<10}"
            f"{row['Best']:>16.6f}"
            f"{row['Mean']:>16.6f}"
            f"{row['Std_sample_ddof1']:>16.6f}"
            f"{row['PaperMean']:>16.6f}"
            f"{row['PaperStd']:>16.6f}"
            f"{ratio:>14.4f}"
            f"{classify_ratio(ratio):>22}"
        )

    print("-" * 132)

    within_25 = sum(
        0.75 <= row["MeanRatio_repro_over_paper"] <= 1.25 for row in summary
    )
    within_2 = sum(
        0.5 <= row["MeanRatio_repro_over_paper"] <= 2.0 for row in summary
    )
    print(f"Mean within ±25% : {within_25}/6")
    print(f"Mean within x2   : {within_2}/6")


def main():
    ensure_dirs()
    rows, completed = load_existing_rows()

    total_runs = len(FUNCTIONS) * N_RUNS

    print("=" * 118)
    print("H1e - Formal GWO SIS2005 F24-F29 / CF1-CF6 30-run reproduction")
    print("=" * 118)
    print("Primary benchmark definition: source_faithful")
    print(f"Protocol: D=10, bounds=[-5,5], N={N}, MaxIter={MAX_ITER}")
    print(f"Runs={N_RUNS}/function, seeds={BASE_SEED}..{BASE_SEED + N_RUNS - 1}")
    print(f"Total optimizer runs={total_runs}")
    print(f"Raw checkpoint : {RAW_PATH}")
    print(f"Summary output : {SUMMARY_PATH}")
    print(f"Report output  : {REPORT_PATH}")
    print(f"Already complete: {len(completed)}/{total_runs}")
    print("=" * 118)

    all_start = time.perf_counter()

    for name in FUNCTIONS:
        benchmark = get_sis2005_benchmark(name, variant=VARIANT)
        function_start = time.perf_counter()

        already_done = sum(
            (name, run) in completed for run in range(1, N_RUNS + 1)
        )
        print(
            f"\n{name}/{benchmark.canonical_name}: "
            f"completed={already_done}/{N_RUNS}"
        )

        for run in range(1, N_RUNS + 1):
            key = (name, run)
            if key in completed:
                continue

            seed = BASE_SEED + run - 1
            run_start = time.perf_counter()

            best_score, best_pos, curve = gwo(
                obj_func=benchmark.objective,
                dim=benchmark.dim,
                lb=benchmark.lb,
                ub=benchmark.ub,
                N=N,
                MaxIter=MAX_ITER,
                seed=seed,
            )

            validate_run(
                benchmark=benchmark,
                best_score=best_score,
                best_pos=best_pos,
                curve=curve,
            )

            elapsed = time.perf_counter() - run_start
            curve = np.asarray(curve, dtype=float)

            row = {
                "Function": name,
                "Canonical": benchmark.canonical_name,
                "Variant": VARIANT,
                "Run": run,
                "Seed": seed,
                "Population": N,
                "MaxIter": MAX_ITER,
                "Dimension": benchmark.dim,
                "LowerBound": benchmark.lb,
                "UpperBound": benchmark.ub,
                "Optimum": benchmark.optimum,
                "BestScore": float(best_score),
                "Curve0": float(curve[0]),
                "CurveLast": float(curve[-1]),
                "ElapsedSeconds": elapsed,
                "Status": "PASS",
            }

            append_raw(row)
            rows.append(row)
            completed.add(key)

            total_done = len(completed)
            print(
                f"  run={run:02d} seed={seed} "
                f"best={float(best_score):.10g} "
                f"time={elapsed:.2f}s "
                f"[{total_done}/{total_runs}]"
            )

        function_elapsed = time.perf_counter() - function_start
        print(
            f"{name}/{benchmark.canonical_name} block elapsed: "
            f"{function_elapsed:.2f}s"
        )

    summary = build_summary(rows)
    write_summary(summary)
    write_report(summary)
    print_summary(summary)

    total_elapsed = time.perf_counter() - all_start

    print("\n" + "=" * 118)
    print("H1e RESULT: PASS")
    print(f"Formal runs complete: {total_runs}/{total_runs}")
    print(f"Total elapsed this invocation: {total_elapsed:.2f}s")
    print(f"Saved raw     : {RAW_PATH}")
    print(f"Saved summary : {SUMMARY_PATH}")
    print(f"Saved report  : {REPORT_PATH}")
    print("No parameter tuning was performed.")
    print("Next: inspect Table-8 agreement and decide whether targeted diagnostics are needed.")
    print("=" * 118)


if __name__ == "__main__":
    main()
