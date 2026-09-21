"""C12: Source-faithful SCHO on F1-F23, 30 independent runs each.

Run from project root:
    python -m experiments.benchmark_scho_c12

This script:
- does NOT modify algorithms/scho.py
- uses N=30, MaxIter=500
- uses 30 independent runs with seeds 1000..1029
- checkpoints every completed run
- resumes safely if interrupted
- saves raw and summary CSV files
"""

from __future__ import annotations

import csv
import time
from pathlib import Path

import numpy as np

from algorithms.scho import scho
from benchmarks.classic_23 import get_benchmark


FUNCTIONS = [f"F{i}" for i in range(1, 24)]

N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_SEED = 1000

RAW_PATH = Path("results/raw/scho_classic23_runs.csv")
SUMMARY_PATH = Path("results/processed/scho_classic23_summary.csv")


def validate_run(best_score, best_pos, curve, dim):
    best_pos = np.asarray(best_pos)
    curve = np.asarray(curve, dtype=float)

    if not np.isfinite(best_score):
        raise ValueError("best_score is NaN/Inf")

    if best_pos.shape != (dim,):
        raise ValueError(f"best_pos shape {best_pos.shape} != expected {(dim,)}")

    if not np.all(np.isfinite(best_pos)):
        raise ValueError("best_pos contains NaN/Inf")

    if curve.shape != (MAX_ITER,):
        raise ValueError(f"curve shape {curve.shape} != expected {(MAX_ITER,)}")

    if not np.all(np.isfinite(curve)):
        raise ValueError("curve contains NaN/Inf")

    if np.any(np.diff(curve) > 0.0):
        raise ValueError("historical-best curve increases")

    if best_score != curve[-1]:
        raise ValueError("best_score != curve[-1]")


def ensure_dirs():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_raw():
    completed = set()
    rows = []

    if not RAW_PATH.exists():
        return completed, rows

    with RAW_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        expected = {"Function", "Run", "Seed", "BestScore"}
        if reader.fieldnames is None or not expected.issubset(reader.fieldnames):
            raise RuntimeError(
                f"Unexpected columns in {RAW_PATH}: {reader.fieldnames}"
            )

        for row in reader:
            normalized = {
                "Function": row["Function"],
                "Run": int(row["Run"]),
                "Seed": int(row["Seed"]),
                "BestScore": float(row["BestScore"]),
            }

            key = (normalized["Function"], normalized["Run"])

            if key in completed:
                raise RuntimeError(f"Duplicate raw result: {key}")

            completed.add(key)
            rows.append(normalized)

    return completed, rows


def append_raw(row):
    new_file = not RAW_PATH.exists()

    with RAW_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Function", "Run", "Seed", "BestScore"],
        )
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def build_summary(raw_rows):
    summary = []

    for name in FUNCTIONS:
        rows = sorted(
            [r for r in raw_rows if r["Function"] == name],
            key=lambda r: r["Run"],
        )

        if len(rows) != N_RUNS:
            raise RuntimeError(f"{name}: {len(rows)} runs found, expected {N_RUNS}")

        expected_runs = list(range(1, N_RUNS + 1))
        actual_runs = [r["Run"] for r in rows]

        if actual_runs != expected_runs:
            raise RuntimeError(f"{name}: run numbers are incomplete: {actual_runs}")

        scores = np.asarray([r["BestScore"] for r in rows], dtype=float)
        benchmark = get_benchmark(name)

        summary.append(
            {
                "Function": name,
                "Runs": N_RUNS,
                "Best": float(np.min(scores)),
                "Mean": float(np.mean(scores)),
                "Std_sample_ddof1": float(np.std(scores, ddof=1)),
                "Std_population_ddof0": float(np.std(scores, ddof=0)),
                "Worst": float(np.max(scores)),
                "Optimum": float(benchmark.optimum),
                "MeanGap": float(np.mean(scores) - benchmark.optimum),
            }
        )

    return summary


def write_summary(summary_rows):
    fieldnames = [
        "Function",
        "Runs",
        "Best",
        "Mean",
        "Std_sample_ddof1",
        "Std_population_ddof0",
        "Worst",
        "Optimum",
        "MeanGap",
    ]

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)


def print_summary(summary_rows):
    print("\n" + "=" * 119)
    print("C12 summary: SCHO F1-F23, 30 runs each")
    print("=" * 119)
    print(
        f"{'Func':<6}"
        f"{'Best':>17}"
        f"{'Mean':>17}"
        f"{'Std(ddof=1)':>17}"
        f"{'Worst':>17}"
        f"{'Optimum':>17}"
        f"{'MeanGap':>17}"
    )
    print("-" * 119)

    for row in summary_rows:
        print(
            f"{row['Function']:<6}"
            f"{row['Best']:>17.8e}"
            f"{row['Mean']:>17.8e}"
            f"{row['Std_sample_ddof1']:>17.8e}"
            f"{row['Worst']:>17.8e}"
            f"{row['Optimum']:>17.8e}"
            f"{row['MeanGap']:>17.8e}"
        )

    print("-" * 119)


def main():
    ensure_dirs()
    completed, raw_rows = load_raw()

    print("=" * 80)
    print("C12 - Source-faithful SCHO on F1-F23 x 30 independent runs")
    print(f"N={N}, MaxIter={MAX_ITER}, seeds={BASE_SEED}..{BASE_SEED + N_RUNS - 1}")
    print(f"Raw checkpoint : {RAW_PATH}")
    print(f"Summary output : {SUMMARY_PATH}")
    print(f"Already complete: {len(completed)}/{len(FUNCTIONS) * N_RUNS}")
    print("=" * 80)

    total_start = time.perf_counter()

    for name in FUNCTIONS:
        benchmark = get_benchmark(name)
        function_start = time.perf_counter()

        already_done = sum(
            (name, run) in completed for run in range(1, N_RUNS + 1)
        )

        print(f"\n{name}: dim={benchmark.dim}, completed={already_done}/{N_RUNS}")

        for run in range(1, N_RUNS + 1):
            key = (name, run)

            if key in completed:
                continue

            seed = BASE_SEED + run - 1

            # For F7, make_objective(seed=seed) controls the noise RNG.
            # The optimizer uses a separate Generator with the same integer seed.
            objective = benchmark.make_objective(seed=seed)

            best_score, best_pos, curve = scho(
                obj_func=objective,
                dim=benchmark.dim,
                lb=benchmark.lb,
                ub=benchmark.ub,
                N=N,
                MaxIter=MAX_ITER,
                seed=seed,
            )

            validate_run(
                best_score=best_score,
                best_pos=best_pos,
                curve=curve,
                dim=benchmark.dim,
            )

            disk_row = {
                "Function": name,
                "Run": run,
                "Seed": seed,
                "BestScore": repr(float(best_score)),
            }
            append_raw(disk_row)

            memory_row = {
                "Function": name,
                "Run": run,
                "Seed": seed,
                "BestScore": float(best_score),
            }

            raw_rows.append(memory_row)
            completed.add(key)

            print(
                f"  run {run:02d}/{N_RUNS}  "
                f"seed={seed}  "
                f"best={best_score:.8e}"
            )

        scores = np.asarray(
            [r["BestScore"] for r in raw_rows if r["Function"] == name],
            dtype=float,
        )
        elapsed = time.perf_counter() - function_start

        print(
            f"  {name} complete: "
            f"best={np.min(scores):.8e}, "
            f"mean={np.mean(scores):.8e}, "
            f"elapsed={elapsed:.1f}s"
        )

    # Reload from disk so final statistics depend on the checkpoint file.
    _, raw_rows = load_raw()

    expected_total = len(FUNCTIONS) * N_RUNS
    if len(raw_rows) != expected_total:
        raise RuntimeError(
            f"Raw file has {len(raw_rows)} rows; expected {expected_total}"
        )

    summary_rows = build_summary(raw_rows)
    write_summary(summary_rows)
    print_summary(summary_rows)

    total_elapsed = time.perf_counter() - total_start

    print("\nC12 RESULT: COMPLETE")
    print(f"Raw rows: {len(raw_rows)}")
    print(f"Elapsed this invocation: {total_elapsed:.1f}s")
    print(f"Saved raw results to: {RAW_PATH}")
    print(f"Saved summary to: {SUMMARY_PATH}")
    print("Next: compare Best / Mean / STD with the SCHO paper.")


if __name__ == "__main__":
    main()
