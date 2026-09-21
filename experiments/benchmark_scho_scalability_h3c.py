"""H3c - Formal SCHO scalability reproduction for Section 3.1.4.

Protocol
--------
Functions : F1-F13
Dimensions: D=100 and D=500
Population: N=30
MaxIter   : 500
Runs      : 30 / function / dimension
Seeds     : 1000..1029 (project reproducibility convention)
Total     : 780 optimizer runs

Primary optimizer
-----------------
Frozen source-faithful `algorithms/scho.py`.

Benchmark layer
---------------
`benchmarks/scho_scalability_h3.py`, validated in H3b.

Outputs
-------
results/raw/scho_scalability_h3c_runs.csv
results/processed/scho_scalability_h3c_summary.csv
report/scho_scalability_h3c_tables9_10_comparison.md

The runner checkpoints after every completed run and safely resumes.

Parallel execution
------------------
Each run has explicit optimizer and objective seeds, so independent runs can be
executed in separate processes without changing their individual deterministic
trajectories.  The parent process alone writes checkpoints.

Set environment variable H3C_WORKERS to override the default worker count.
"""

from __future__ import annotations

import csv
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from algorithms.scho import scho
from benchmarks.scho_scalability_h3 import (
    SCALABILITY_DIMS,
    SCALABILITY_FUNCTIONS,
    get_scalability_benchmark,
)


N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_SEED = 1000

RAW_PATH = Path("results/raw/scho_scalability_h3c_runs.csv")
SUMMARY_PATH = Path("results/processed/scho_scalability_h3c_summary.csv")
REPORT_PATH = Path("report/scho_scalability_h3c_tables9_10_comparison.md")

RAW_FIELDS = [
    "Function",
    "Dimension",
    "Run",
    "OptimizerSeed",
    "ObjectiveSeed",
    "Population",
    "MaxIter",
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
    "Dimension",
    "Runs",
    "Population",
    "MaxIter",
    "Best",
    "Mean",
    "Std_sample_ddof1",
    "Std_population_ddof0",
    "Median",
    "Worst",
    "Optimum",
    "PaperBest",
    "PaperMean",
    "PaperStd",
    "BestGap",
    "MeanGap",
    "StdGap",
    "MeanRatio_repro_over_paper",
    "MeanErrorFromOptimum",
    "PaperMeanErrorFromOptimum",
    "MeanErrorRatio",
]


# SCHO columns from paper Tables 9 (D=100) and 10 (D=500).
# Values are reference anchors only; they are never used to tune the algorithm.
PAPER_SCHO = {
    100: {
        "F1":  (0.000e+00, 0.000e+00, 0.000e+00),
        "F2":  (0.000e+00, 7.576e-263, 0.000e+00),
        "F3":  (0.000e+00, 0.000e+00, 0.000e+00),
        "F4":  (0.000e+00, 4.243e-249, 0.000e+00),
        "F5":  (9.875e+01, 9.887e+01, 1.004e-01),
        "F6":  (1.466e-04, 8.562e+00, 8.137e+00),
        "F7":  (5.429e-07, 7.285e-05, 5.388e-05),
        "F8":  (-3.926e+04, -1.856e+04, 9.867e+03),
        "F9":  (0.000e+00, 0.000e+00, 0.000e+00),
        "F10": (4.441e-16, 4.441e-16, 0.000e+00),
        "F11": (0.000e+00, 0.000e+00, 0.000e+00),
        "F12": (9.093e-10, 6.876e-01, 6.422e-01),
        "F13": (1.024e+00, 9.580e+00, 1.616e+00),
    },
    500: {
        "F1":  (0.000e+00, 0.000e+00, 0.000e+00),
        "F2":  (0.000e+00, 3.513e-211, 0.000e+00),
        "F3":  (0.000e+00, 0.000e+00, 0.000e+00),
        "F4":  (0.000e+00, 1.492e-204, 0.000e+00),
        "F5":  (4.988e+02, 4.990e+02, 5.200e-02),
        "F6":  (1.242e+02, 1.246e+02, 1.481e-01),
        "F7":  (4.091e-06, 8.216e-05, 6.352e-05),
        "F8":  (-1.944e+05, -6.282e+04, 5.105e+04),
        "F9":  (0.000e+00, 0.000e+00, 0.000e+00),
        "F10": (4.441e-16, 4.441e-16, 0.000e+00),
        "F11": (0.000e+00, 0.000e+00, 0.000e+00),
        "F12": (9.540e-08, 1.040e+00, 4.150e-01),
        "F13": (2.821e+01, 4.916e+01, 3.957e+00),
    },
}


def _objective_seed(name: str, dim: int, run: int) -> int:
    # A separate benchmark RNG stream is important for stochastic F7.
    # Deterministic functions ignore this seed in Benchmark.make_objective().
    fnum = int(name[1:])
    return 7_000_000 + dim * 10_000 + fnum * 100 + run


def _default_workers() -> int:
    override = os.environ.get("H3C_WORKERS")
    if override is not None:
        try:
            value = int(override)
        except ValueError as exc:
            raise ValueError("H3C_WORKERS must be an integer >= 1") from exc
        if value < 1:
            raise ValueError("H3C_WORKERS must be >= 1")
        return value

    cpu = os.cpu_count() or 1
    # The D=500 source-faithful Python loop is expensive. Use modest process
    # parallelism while avoiding automatic saturation of the whole machine.
    return max(1, min(4, cpu // 2 if cpu >= 2 else 1))


def _validate_run(name, dim, b, best_score, best_pos, curve):
    best_score = float(best_score)
    best_pos = np.asarray(best_pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    if not np.isfinite(best_score):
        raise AssertionError(f"{name} D={dim}: non-finite best score")
    if best_pos.shape != (dim,):
        raise AssertionError(
            f"{name} D={dim}: best_pos shape {best_pos.shape} != {(dim,)}"
        )
    if not np.all(np.isfinite(best_pos)):
        raise AssertionError(f"{name} D={dim}: best position contains NaN/Inf")
    if curve.shape != (MAX_ITER,):
        raise AssertionError(
            f"{name} D={dim}: curve shape {curve.shape} != {(MAX_ITER,)}"
        )
    if not np.all(np.isfinite(curve)):
        raise AssertionError(f"{name} D={dim}: convergence curve contains NaN/Inf")
    if np.any(np.diff(curve) > 0):
        idx = int(np.flatnonzero(np.diff(curve) > 0)[0])
        raise AssertionError(
            f"{name} D={dim}: historical best increased at {idx}->{idx+1}"
        )
    if float(curve[-1]) != best_score:
        raise AssertionError(
            f"{name} D={dim}: curve[-1]={curve[-1]} != best={best_score}"
        )

    # Returned best should lie inside original function bounds.
    lb = np.asarray(b.lb, dtype=float)
    ub = np.asarray(b.ub, dtype=float)
    if np.any(best_pos < lb - 1e-12) or np.any(best_pos > ub + 1e-12):
        raise AssertionError(f"{name} D={dim}: returned best position violates bounds")


def _run_task(task):
    name, dim, run = task
    seed = BASE_SEED + run - 1
    objective_seed = _objective_seed(name, dim, run)

    b = get_scalability_benchmark(name, dim)
    obj = b.make_objective(seed=objective_seed)

    start = time.perf_counter()
    best_score, best_pos, curve = scho(
        obj_func=obj,
        dim=b.dim,
        lb=b.lb,
        ub=b.ub,
        N=N,
        MaxIter=MAX_ITER,
        seed=seed,
    )
    elapsed = time.perf_counter() - start

    _validate_run(name, dim, b, best_score, best_pos, curve)
    curve = np.asarray(curve, dtype=float)

    return {
        "Function": name,
        "Dimension": dim,
        "Run": run,
        "OptimizerSeed": seed,
        "ObjectiveSeed": objective_seed,
        "Population": N,
        "MaxIter": MAX_ITER,
        "LowerBound": float(np.asarray(b.lb).reshape(-1)[0]),
        "UpperBound": float(np.asarray(b.ub).reshape(-1)[0]),
        "Optimum": float(b.optimum),
        "BestScore": float(best_score),
        "Curve0": float(curve[0]),
        "CurveLast": float(curve[-1]),
        "ElapsedSeconds": float(elapsed),
        "Status": "PASS",
    }


def _normalize_raw_row(row):
    return {
        "Function": row["Function"],
        "Dimension": int(row["Dimension"]),
        "Run": int(row["Run"]),
        "OptimizerSeed": int(row["OptimizerSeed"]),
        "ObjectiveSeed": int(row["ObjectiveSeed"]),
        "Population": int(row["Population"]),
        "MaxIter": int(row["MaxIter"]),
        "LowerBound": float(row["LowerBound"]),
        "UpperBound": float(row["UpperBound"]),
        "Optimum": float(row["Optimum"]),
        "BestScore": float(row["BestScore"]),
        "Curve0": float(row["Curve0"]),
        "CurveLast": float(row["CurveLast"]),
        "ElapsedSeconds": float(row["ElapsedSeconds"]),
        "Status": row["Status"],
    }


def _row_matches_protocol(row):
    try:
        name = row["Function"]
        dim = int(row["Dimension"])
        run = int(row["Run"])
        return (
            name in SCALABILITY_FUNCTIONS
            and dim in SCALABILITY_DIMS
            and 1 <= run <= N_RUNS
            and int(row["OptimizerSeed"]) == BASE_SEED + run - 1
            and int(row["ObjectiveSeed"]) == _objective_seed(name, dim, run)
            and int(row["Population"]) == N
            and int(row["MaxIter"]) == MAX_ITER
            and row["Status"] == "PASS"
        )
    except Exception:
        return False


def _ensure_dirs():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_existing_rows():
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
            if not _row_matches_protocol(row):
                raise RuntimeError(
                    "Existing H3c raw file contains a row from a different "
                    f"protocol: {row}"
                )
            key = (row["Function"], row["Dimension"], row["Run"])
            if key in completed:
                raise RuntimeError(f"Duplicate H3c raw result: {key}")
            completed.add(key)
            rows.append(row)

    return rows, completed


def _append_raw(row):
    new_file = not RAW_PATH.exists()
    with RAW_PATH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def _safe_ratio(num, den):
    if den == 0.0:
        return math.nan
    return num / den


def _build_summary(rows):
    summary = []

    for dim in SCALABILITY_DIMS:
        for name in SCALABILITY_FUNCTIONS:
            b = get_scalability_benchmark(name, dim)
            group = sorted(
                [
                    row for row in rows
                    if row["Function"] == name
                    and row["Dimension"] == dim
                    and _row_matches_protocol(row)
                ],
                key=lambda row: row["Run"],
            )

            if len(group) != N_RUNS:
                raise RuntimeError(
                    f"{name} D={dim}: expected {N_RUNS} PASS rows, got {len(group)}"
                )

            actual_runs = [row["Run"] for row in group]
            if actual_runs != list(range(1, N_RUNS + 1)):
                raise RuntimeError(
                    f"{name} D={dim}: incomplete run sequence {actual_runs}"
                )

            scores = np.asarray([row["BestScore"] for row in group], dtype=float)
            best = float(np.min(scores))
            mean = float(np.mean(scores))
            std_sample = float(np.std(scores, ddof=1))
            std_pop = float(np.std(scores, ddof=0))
            median = float(np.median(scores))
            worst = float(np.max(scores))

            paper_best, paper_mean, paper_std = PAPER_SCHO[dim][name]
            optimum = float(b.optimum)

            mean_error = abs(mean - optimum)
            paper_mean_error = abs(paper_mean - optimum)

            summary.append(
                {
                    "Function": name,
                    "Dimension": dim,
                    "Runs": N_RUNS,
                    "Population": N,
                    "MaxIter": MAX_ITER,
                    "Best": best,
                    "Mean": mean,
                    "Std_sample_ddof1": std_sample,
                    "Std_population_ddof0": std_pop,
                    "Median": median,
                    "Worst": worst,
                    "Optimum": optimum,
                    "PaperBest": paper_best,
                    "PaperMean": paper_mean,
                    "PaperStd": paper_std,
                    "BestGap": best - paper_best,
                    "MeanGap": mean - paper_mean,
                    "StdGap": std_sample - paper_std,
                    "MeanRatio_repro_over_paper": _safe_ratio(mean, paper_mean),
                    "MeanErrorFromOptimum": mean_error,
                    "PaperMeanErrorFromOptimum": paper_mean_error,
                    "MeanErrorRatio": _safe_ratio(mean_error, paper_mean_error),
                }
            )

    return summary


def _write_summary(summary):
    with SUMMARY_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary)


def _fmt(x):
    if isinstance(x, float) and math.isnan(x):
        return "NA"
    return f"{x:.6g}"


def _agreement_label(row):
    paper_mean = row["PaperMean"]
    mean = row["Mean"]

    if paper_mean == 0.0:
        if abs(mean) <= 1e-12:
            return "near paper zero"
        return "nonzero vs paper zero"

    ratio = row["MeanRatio_repro_over_paper"]
    if not math.isfinite(ratio) or ratio <= 0:
        return "sign/ratio mismatch"
    if 0.75 <= ratio <= 1.25:
        return "within ±25%"
    if 0.5 <= ratio <= 2.0:
        return "within factor 2"
    return "outside factor 2"


def _write_report(summary, workers):
    lines = [
        "# H3c — SCHO D=100 / D=500 scalability core reproduction",
        "",
        "## Protocol",
        "",
        "- Functions: F1–F13",
        "- Dimensions: 100 and 500",
        "- Search agents: 30",
        "- MaxIter: 500",
        "- Runs: 30/function/dimension",
        "- Optimizer: frozen source-faithful `algorithms/scho.py`",
        "- Seeds: 1000–1029 (project reproducibility convention)",
        "- F7 uses a separate deterministic objective RNG seed per run",
        f"- Execution workers used: {workers}",
        "- Primary paper-comparison STD: sample STD (`ddof=1`)",
        "",
        "This stage reproduces the **SCHO columns** of Tables 9 and 10.",
        "It does not yet reproduce the complete nine-algorithm Friedman / Wilcoxon",
        "comparison.",
        "",
    ]

    for dim in SCALABILITY_DIMS:
        lines += [
            f"## D = {dim}",
            "",
            "| F | Repro Best | Repro Mean | Repro STD | Paper Best | Paper Mean | Paper STD | Mean agreement |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for row in summary:
            if row["Dimension"] != dim:
                continue
            lines.append(
                f"| {row['Function']} "
                f"| {_fmt(row['Best'])} "
                f"| {_fmt(row['Mean'])} "
                f"| {_fmt(row['Std_sample_ddof1'])} "
                f"| {_fmt(row['PaperBest'])} "
                f"| {_fmt(row['PaperMean'])} "
                f"| {_fmt(row['PaperStd'])} "
                f"| {_agreement_label(row)} |"
            )
        lines.append("")

    lines += [
        "## Interpretation rule",
        "",
        "`H3c RESULT: PASS` means all 780 source-faithful SCHO runs completed",
        "structurally and the evidence files were generated.",
        "",
        "It does **not** mean the reproduced statistics must equal the paper.",
        "Any disagreement is preserved and analyzed in H3d without tuning.",
        "",
        "## Full-paper limitation after H3c",
        "",
        "Tables 9–12 also require GWO, ALO, SCA, SSA, AOA, RSA, SHO and GJO,",
        "plus Friedman ranking and Wilcoxon rank-sum tests. Those comparator",
        "experiments remain pending after this SCHO-core stage.",
        "",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _print_partial_progress(completed_count, total, row, wall_start):
    elapsed_wall = time.perf_counter() - wall_start
    done = max(completed_count, 1)
    avg_wall_per_completion = elapsed_wall / done
    remaining = total - completed_count
    rough_eta = avg_wall_per_completion * remaining
    print(
        f"[{completed_count:03d}/{total}] "
        f"{row['Function']} D={row['Dimension']} run={row['Run']:02d} "
        f"seed={row['OptimizerSeed']} best={row['BestScore']:.10g} "
        f"worker_time={row['ElapsedSeconds']:.1f}s "
        f"rough_remaining={rough_eta/3600:.1f}h"
    )


def main():
    _ensure_dirs()
    rows, completed = _load_existing_rows()

    all_tasks = [
        (name, dim, run)
        for dim in SCALABILITY_DIMS
        for name in SCALABILITY_FUNCTIONS
        for run in range(1, N_RUNS + 1)
    ]
    pending = [
        task for task in all_tasks
        if (task[0], task[1], task[2]) not in completed
    ]

    workers = _default_workers()
    total = len(all_tasks)

    print("=" * 122)
    print("H3c - Formal SCHO scalability F1-F13 at D=100 and D=500")
    print("=" * 122)
    print(f"Protocol: N={N}, MaxIter={MAX_ITER}, runs={N_RUNS}/function/dimension")
    print(f"Seeds: {BASE_SEED}..{BASE_SEED + N_RUNS - 1}")
    print(f"Total optimizer runs: {total}")
    print(f"Workers: {workers}")
    print(f"Already complete: {len(completed)}/{total}")
    print(f"Raw checkpoint : {RAW_PATH}")
    print(f"Summary output : {SUMMARY_PATH}")
    print(f"Report output  : {REPORT_PATH}")
    print("The run is resumable; rerun the same command after interruption.")
    print("=" * 122)

    if not pending:
        print("All 780 runs already exist; rebuilding summary/report only.")
    else:
        wall_start = time.perf_counter()

        if workers == 1:
            for task in pending:
                row = _run_task(task)
                _append_raw(row)
                rows.append(row)
                completed.add((row["Function"], row["Dimension"], row["Run"]))
                _print_partial_progress(len(completed), total, row, wall_start)
        else:
            # Submit in bounded batches so Ctrl+C / interruption loses at most
            # a small number of in-flight deterministic runs.
            batch_size = workers * 2
            for start_idx in range(0, len(pending), batch_size):
                batch = pending[start_idx:start_idx + batch_size]
                with ProcessPoolExecutor(max_workers=workers) as pool:
                    futures = {pool.submit(_run_task, task): task for task in batch}
                    for future in as_completed(futures):
                        row = future.result()
                        _append_raw(row)
                        rows.append(row)
                        completed.add(
                            (row["Function"], row["Dimension"], row["Run"])
                        )
                        _print_partial_progress(
                            len(completed), total, row, wall_start
                        )

    if len(completed) != total:
        raise RuntimeError(
            f"H3c incomplete: {len(completed)}/{total} runs checkpointed"
        )

    summary = _build_summary(rows)
    _write_summary(summary)
    _write_report(summary, workers)

    print("\n" + "=" * 122)
    print("H3c RESULT: PASS")
    print(f"Formal runs complete: {total}/{total}")
    print(f"Saved raw     : {RAW_PATH}")
    print(f"Saved summary : {SUMMARY_PATH}")
    print(f"Saved report  : {REPORT_PATH}")
    print("No parameter tuning was performed.")
    print("Next: H3d paper-agreement diagnostic and scalability-core freeze.")
    print("=" * 122)


if __name__ == "__main__":
    main()
