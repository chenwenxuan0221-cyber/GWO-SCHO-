"""D1: Re-run GWO on stochastic F7 under the corrected RNG protocol.

Purpose
-------
Stage D compares the existing GWO Stage B results with the new SCHO C12 results.
Only F7 needs to be re-run because C11.5 changed its benchmark registration to
stochastic=True, so the objective noise is now controlled by make_objective(seed).

This script:
- does NOT modify algorithms/gwo.py
- does NOT modify algorithms/scho.py
- uses N=30, MaxIter=500
- uses 30 independent runs with seeds 1000..1029
- checks F7 is registered as stochastic=True
- saves raw and summary CSV files
- reports population STD (ddof=0) to match the original GWO Stage B script

Place at:
    experiments/rerun_gwo_f7_d1.py

Run from project root:
    python -m experiments.rerun_gwo_f7_d1
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from algorithms.gwo import gwo
from benchmarks.classic_23 import get_benchmark


FUNCTION = "F7"
N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_SEED = 1000

RAW_PATH = Path("results/raw/gwo_f7_d1_runs.csv")
SUMMARY_PATH = Path("results/processed/gwo_f7_d1_summary.csv")


def validate_run(best_score, best_pos, curve, dim):
    best_pos = np.asarray(best_pos)
    curve = np.asarray(curve, dtype=float)

    if not np.isfinite(best_score):
        raise ValueError("best_score is NaN/Inf")

    if best_pos.shape != (dim,):
        raise ValueError(
            f"best_pos shape {best_pos.shape} != expected {(dim,)}"
        )

    if not np.all(np.isfinite(best_pos)):
        raise ValueError("best_pos contains NaN/Inf")

    if curve.shape != (MAX_ITER,):
        raise ValueError(
            f"curve shape {curve.shape} != expected {(MAX_ITER,)}"
        )

    if not np.all(np.isfinite(curve)):
        raise ValueError("curve contains NaN/Inf")

    # GWO stores historical alpha score, so its convergence curve should
    # be monotonically non-increasing.
    if np.any(np.diff(curve) > 0.0):
        raise ValueError("historical-best curve increases")

    if best_score != curve[-1]:
        raise ValueError("best_score != curve[-1]")


def main():
    benchmark = get_benchmark(FUNCTION)

    print("=" * 78)
    print("D1 - GWO F7 rerun under corrected stochastic benchmark protocol")
    print("=" * 78)
    print(f"benchmark.stochastic = {benchmark.stochastic}")
    print(f"N={N}, MaxIter={MAX_ITER}, runs={N_RUNS}")
    print(f"Seeds={BASE_SEED}..{BASE_SEED + N_RUNS - 1}")
    print("=" * 78)

    if not benchmark.stochastic:
        raise AssertionError(
            "F7 must be registered with stochastic=True before D1."
        )

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    scores = []

    for run in range(1, N_RUNS + 1):
        seed = BASE_SEED + run - 1

        # Corrected F7 protocol:
        # objective RNG is deterministic via make_objective(seed),
        # while GWO uses its own independent Generator with the same integer seed.
        objective = benchmark.make_objective(seed=seed)

        best_score, best_pos, curve = gwo(
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

        score = float(best_score)
        scores.append(score)
        rows.append(
            {
                "Function": FUNCTION,
                "Run": run,
                "Seed": seed,
                "BestScore": repr(score),
            }
        )

        print(
            f"Run {run:02d}/{N_RUNS}  "
            f"seed={seed}  "
            f"best={score:.8e}"
        )

    scores = np.asarray(scores, dtype=float)

    summary = {
        "Function": FUNCTION,
        "Runs": N_RUNS,
        "Population": N,
        "MaxIter": MAX_ITER,
        "Best": float(np.min(scores)),
        "Mean": float(np.mean(scores)),
        # Match original GWO Stage B script: np.std(scores) => ddof=0
        "Std_population_ddof0": float(np.std(scores, ddof=0)),
        "Std_sample_ddof1": float(np.std(scores, ddof=1)),
        "Worst": float(np.max(scores)),
        "Optimum": float(benchmark.optimum),
    }

    with RAW_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Function", "Run", "Seed", "BestScore"],
        )
        writer.writeheader()
        writer.writerows(rows)

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    print("\n" + "-" * 78)
    print("D1 summary")
    print("-" * 78)
    print(f"Best               = {summary['Best']:.8e}")
    print(f"Mean               = {summary['Mean']:.8e}")
    print(f"Std population     = {summary['Std_population_ddof0']:.8e}")
    print(f"Std sample         = {summary['Std_sample_ddof1']:.8e}")
    print(f"Worst              = {summary['Worst']:.8e}")
    print(f"Theoretical optimum= {summary['Optimum']:.8e}")

    print("\nD1 RESULT: COMPLETE")
    print(f"Saved raw results to: {RAW_PATH}")
    print(f"Saved summary to: {SUMMARY_PATH}")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
