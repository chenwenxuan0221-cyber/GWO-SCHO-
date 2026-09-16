"""E4 - Full 30-run CEC 2014 benchmark for frozen GWO and SCHO.

Protocol (paper-oriented reproduction):
    Functions : CEC2014 F1-F30
    Dimension : D=10
    Population: N=30
    MaxIter   : 500
    Runs      : 30 per function per algorithm
    Seeds     : 1000..1029

Total optimizer runs:
    30 functions x 2 algorithms x 30 runs = 1800

Outputs
-------
results/raw/cec2014_e4_runs.csv
results/processed/cec2014_e4_summary.csv

Notes
-----
- Raw fitness is saved because Bai et al. Table 14 reports raw fitness.
- Error = BestScore - known CEC optimum is also saved for diagnostic use.
- Both sample STD (ddof=1) and population STD (ddof=0) are saved.
- Sample STD is the primary paper-comparison STD because MATLAB std()
  uses N-1 normalization by default.
- The script checkpoints after EVERY completed run and safely resumes.
- algorithms/gwo.py and algorithms/scho.py are not modified.

Place at:
    experiments/benchmark_cec2014_e4.py

Run from project root:
    python -m experiments.benchmark_cec2014_e4
"""

from __future__ import annotations

import csv
from pathlib import Path
import time

import numpy as np

from algorithms.gwo import gwo
from algorithms.scho import scho
from benchmarks.cec2014 import get_benchmark


FUNCTIONS = [f"F{i}" for i in range(1, 31)]
ALGORITHMS = [
    ("GWO", gwo),
    ("SCHO", scho),
]

N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_SEED = 1000

RAW_PATH = Path("results/raw/cec2014_e4_runs.csv")
SUMMARY_PATH = Path("results/processed/cec2014_e4_summary.csv")

RAW_FIELDS = [
    "Function",
    "Family",
    "Algorithm",
    "Run",
    "Seed",
    "Population",
    "MaxIter",
    "Dimension",
    "Optimum",
    "BestScore",
    "Error",
    "Curve0",
    "CurveLast",
    "Status",
]

SUMMARY_FIELDS = [
    "Function",
    "Family",
    "Algorithm",
    "Runs",
    "Population",
    "MaxIter",
    "Dimension",
    "Optimum",
    "Best",
    "Mean",
    "Std_sample_ddof1",
    "Std_population_ddof0",
    "Worst",
    "BestError",
    "MeanError",
    "WorstError",
]


def validate_run(
    *,
    algorithm_name: str,
    benchmark,
    best_score,
    best_pos,
    curve,
):
    best_score = float(best_score)
    best_pos = np.asarray(best_pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    if not np.isfinite(best_score):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: best_score is NaN/Inf"
        )

    if best_pos.shape != (benchmark.dim,):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            f"best_pos shape {best_pos.shape} != {(benchmark.dim,)}"
        )

    if not np.all(np.isfinite(best_pos)):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: best_pos contains NaN/Inf"
        )

    if curve.shape != (MAX_ITER,):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            f"curve shape {curve.shape} != {(MAX_ITER,)}"
        )

    if not np.all(np.isfinite(curve)):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: curve contains NaN/Inf"
        )

    # Both frozen implementations return historical-best curves.
    if np.any(np.diff(curve) > 0.0):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            "historical-best curve is not non-increasing"
        )

    if best_score != float(curve[-1]):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            "best_score != curve[-1]"
        )

    tol = 1e-12
    if np.any(best_pos < benchmark.lb - tol) or np.any(best_pos > benchmark.ub + tol):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            "best_pos is outside [-100, 100]^10"
        )

    # Known optimum guard. Tiny numerical undershoot is tolerated.
    optimum_tol = 1e-6
    if best_score < benchmark.optimum - optimum_tol:
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            f"best_score={best_score} is below known optimum "
            f"{benchmark.optimum} by more than {optimum_tol}"
        )


def load_existing_rows():
    if not RAW_PATH.exists():
        return []

    rows = []
    with RAW_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    return rows


def row_matches_protocol(row):
    try:
        return (
            int(row["Population"]) == N
            and int(row["MaxIter"]) == MAX_ITER
            and int(row["Dimension"]) == 10
            and 1 <= int(row["Run"]) <= N_RUNS
            and int(row["Seed"]) == BASE_SEED + int(row["Run"]) - 1
        )
    except Exception:
        return False


def save_raw_rows(rows):
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RAW_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run_one(algorithm_name, optimizer, benchmark, run_number, seed):
    # CEC2014 evaluator is deterministic; seed is accepted for API parity.
    objective = benchmark.make_objective(seed=seed)

    best_score, best_pos, curve = optimizer(
        obj_func=objective,
        dim=benchmark.dim,
        lb=benchmark.lb,
        ub=benchmark.ub,
        N=N,
        MaxIter=MAX_ITER,
        seed=seed,
    )

    validate_run(
        algorithm_name=algorithm_name,
        benchmark=benchmark,
        best_score=best_score,
        best_pos=best_pos,
        curve=curve,
    )

    best_score = float(best_score)
    curve = np.asarray(curve, dtype=float)

    return {
        "Function": benchmark.name,
        "Family": benchmark.family,
        "Algorithm": algorithm_name,
        "Run": run_number,
        "Seed": seed,
        "Population": N,
        "MaxIter": MAX_ITER,
        "Dimension": benchmark.dim,
        "Optimum": float(benchmark.optimum),
        "BestScore": best_score,
        "Error": best_score - float(benchmark.optimum),
        "Curve0": float(curve[0]),
        "CurveLast": float(curve[-1]),
        "Status": "PASS",
    }


def build_summary(rows):
    summary_rows = []

    for func_name in FUNCTIONS:
        benchmark = get_benchmark(func_name)

        for algorithm_name, _ in ALGORITHMS:
            group = [
                r for r in rows
                if (
                    r["Function"] == func_name
                    and r["Algorithm"] == algorithm_name
                    and r.get("Status") == "PASS"
                    and row_matches_protocol(r)
                )
            ]

            if len(group) != N_RUNS:
                raise RuntimeError(
                    f"{func_name} {algorithm_name}: "
                    f"expected {N_RUNS} PASS rows, got {len(group)}"
                )

            group = sorted(group, key=lambda r: int(r["Run"]))

            scores = np.asarray(
                [float(r["BestScore"]) for r in group],
                dtype=float,
            )
            errors = scores - float(benchmark.optimum)

            summary_rows.append(
                {
                    "Function": func_name,
                    "Family": benchmark.family,
                    "Algorithm": algorithm_name,
                    "Runs": N_RUNS,
                    "Population": N,
                    "MaxIter": MAX_ITER,
                    "Dimension": benchmark.dim,
                    "Optimum": float(benchmark.optimum),
                    "Best": float(np.min(scores)),
                    "Mean": float(np.mean(scores)),
                    "Std_sample_ddof1": float(np.std(scores, ddof=1)),
                    "Std_population_ddof0": float(np.std(scores, ddof=0)),
                    "Worst": float(np.max(scores)),
                    "BestError": float(np.min(errors)),
                    "MeanError": float(np.mean(errors)),
                    "WorstError": float(np.max(errors)),
                }
            )

    return summary_rows


def save_summary(summary_rows):
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary_rows)


def main():
    print("=" * 112)
    print("E4 - CEC 2014 F1-F30 x GWO/SCHO x 30 runs")
    print("=" * 112)
    print("Protocol:")
    print("  D=10")
    print(f"  N={N}")
    print(f"  MaxIter={MAX_ITER}")
    print(f"  Runs={N_RUNS}")
    print(f"  Seeds={BASE_SEED}..{BASE_SEED + N_RUNS - 1}")
    print(f"  Total optimizer runs={len(FUNCTIONS) * len(ALGORITHMS) * N_RUNS}")
    print(f"Raw output     : {RAW_PATH}")
    print(f"Summary output : {SUMMARY_PATH}")
    print("=" * 112)

    existing = load_existing_rows()

    # Retain only valid rows matching the frozen E4 protocol.
    rows = [
        r for r in existing
        if row_matches_protocol(r)
    ]

    completed = {
        (r["Function"], r["Algorithm"], int(r["Run"]))
        for r in rows
        if r.get("Status") == "PASS"
    }

    total_runs = len(FUNCTIONS) * len(ALGORITHMS) * N_RUNS

    if completed:
        print(f"Resume: {len(completed)}/{total_runs} PASS runs already completed.\n")

    global_start = time.time()

    for func_index, func_name in enumerate(FUNCTIONS, start=1):
        benchmark = get_benchmark(func_name)

        print(
            f"\n[{func_index:02d}/30] {func_name} | "
            f"{benchmark.family} | f_opt={benchmark.optimum:.1f}"
        )

        for algorithm_name, optimizer in ALGORITHMS:
            print(f"  {algorithm_name}")

            for run_number in range(1, N_RUNS + 1):
                key = (func_name, algorithm_name, run_number)
                seed = BASE_SEED + run_number - 1

                if key in completed:
                    print(
                        f"    Run {run_number:02d}/{N_RUNS} "
                        f"seed={seed} SKIP"
                    )
                    continue

                run_start = time.time()

                try:
                    result = run_one(
                        algorithm_name=algorithm_name,
                        optimizer=optimizer,
                        benchmark=benchmark,
                        run_number=run_number,
                        seed=seed,
                    )

                    # Replace any stale row for the same run.
                    rows = [
                        r for r in rows
                        if not (
                            r["Function"] == func_name
                            and r["Algorithm"] == algorithm_name
                            and int(r["Run"]) == run_number
                        )
                    ]
                    rows.append(result)
                    completed.add(key)

                    # Checkpoint after EVERY successful run.
                    save_raw_rows(rows)

                    elapsed = time.time() - run_start
                    print(
                        f"    Run {run_number:02d}/{N_RUNS} "
                        f"seed={seed} "
                        f"best={result['BestScore']:.8e} "
                        f"error={result['Error']:.8e} "
                        f"({elapsed:.1f}s)"
                    )

                except Exception as exc:
                    fail_row = {
                        "Function": func_name,
                        "Family": benchmark.family,
                        "Algorithm": algorithm_name,
                        "Run": run_number,
                        "Seed": seed,
                        "Population": N,
                        "MaxIter": MAX_ITER,
                        "Dimension": benchmark.dim,
                        "Optimum": float(benchmark.optimum),
                        "BestScore": "",
                        "Error": "",
                        "Curve0": "",
                        "CurveLast": "",
                        "Status": f"FAIL: {type(exc).__name__}: {exc}",
                    }

                    rows = [
                        r for r in rows
                        if not (
                            r["Function"] == func_name
                            and r["Algorithm"] == algorithm_name
                            and int(r["Run"]) == run_number
                        )
                    ]
                    rows.append(fail_row)
                    save_raw_rows(rows)

                    raise RuntimeError(
                        f"E4 stopped at {func_name} {algorithm_name} "
                        f"run={run_number}, seed={seed}"
                    ) from exc

    # Final completeness audit.
    expected = {
        (f"F{i}", alg, run)
        for i in range(1, 31)
        for alg, _ in ALGORITHMS
        for run in range(1, N_RUNS + 1)
    }
    pass_pairs = {
        (r["Function"], r["Algorithm"], int(r["Run"]))
        for r in rows
        if r.get("Status") == "PASS" and row_matches_protocol(r)
    }

    missing = sorted(expected - pass_pairs)

    if missing:
        raise RuntimeError(
            f"E4 incomplete: {len(missing)} runs missing PASS status."
        )

    summary_rows = build_summary(rows)
    save_summary(summary_rows)

    elapsed_total = time.time() - global_start

    print("\n" + "-" * 112)
    print("E4 final audit")
    print("-" * 112)
    print(f"PASS runs     : {len(pass_pairs)}/{total_runs}")
    print(f"Summary rows  : {len(summary_rows)}/60")
    print(f"Elapsed this invocation: {elapsed_total / 60.0:.1f} min")
    print(f"Saved raw     : {RAW_PATH}")
    print(f"Saved summary : {SUMMARY_PATH}")
    print()
    print("E4 RESULT: COMPLETE")
    print("All CEC2014 F1-F30 x GWO/SCHO x 30-run experiments are complete.")
    print("Paper Table 14 comparison has NOT yet been performed.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
