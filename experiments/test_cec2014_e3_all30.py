"""E3 - Full CEC 2014 single-run sweep for frozen GWO and SCHO.

Purpose
-------
After E2 verified four representative CEC2014 categories, E3 checks that
both frozen optimizers can run on ALL F1-F30 at D=10 without structural
failures.

Protocol
--------
D=10
N=30
MaxIter=500
seed=1000
1 run per algorithm/function pair

Total optimizer runs: 30 functions x 2 algorithms = 60.

This is still a structural/full-coverage stage:
- NOT a 30-run statistical reproduction
- NOT a paper-performance judgement
- NO algorithm tuning

Output
------
results/raw/cec2014_e3_single_run.csv

The script checkpoints after every completed algorithm/function pair and
can resume safely if interrupted.

Place at:
    experiments/test_cec2014_e3_all30.py

Run from project root:
    python -m experiments.test_cec2014_e3_all30
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from algorithms.gwo import gwo
from algorithms.scho import scho
from benchmarks.cec2014 import get_benchmark


N = 30
MAX_ITER = 500
SEED = 1000

FUNCTIONS = [f"F{i}" for i in range(1, 31)]

OUTPUT_PATH = Path("results/raw/cec2014_e3_single_run.csv")

FIELDNAMES = [
    "Function",
    "Family",
    "Algorithm",
    "Seed",
    "Population",
    "MaxIter",
    "Optimum",
    "BestScore",
    "Error",
    "Curve0",
    "CurveLast",
    "Status",
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

    # Both frozen implementations expose historical best curves.
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

    # CEC2014 global optimum is known as 100*i. A result materially below
    # that value would indicate an evaluator/integration problem.
    optimum_tol = 1e-6
    if best_score < benchmark.optimum - optimum_tol:
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            f"best_score={best_score} is below known optimum "
            f"{benchmark.optimum} by more than {optimum_tol}"
        )


def load_existing():
    if not OUTPUT_PATH.exists():
        return [], set()

    rows = []
    completed = set()

    with OUTPUT_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if row.get("Status") == "PASS":
                completed.add((row["Function"], row["Algorithm"]))

    return rows, completed


def save_rows(rows):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def run_one(algorithm_name, optimizer, benchmark):
    objective = benchmark.make_objective(seed=SEED)

    best_score, best_pos, curve = optimizer(
        obj_func=objective,
        dim=benchmark.dim,
        lb=benchmark.lb,
        ub=benchmark.ub,
        N=N,
        MaxIter=MAX_ITER,
        seed=SEED,
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
        "Seed": SEED,
        "Population": N,
        "MaxIter": MAX_ITER,
        "Optimum": float(benchmark.optimum),
        "BestScore": best_score,
        "Error": best_score - float(benchmark.optimum),
        "Curve0": float(curve[0]),
        "CurveLast": float(curve[-1]),
        "Status": "PASS",
    }


def main():
    print("=" * 108)
    print("E3 - Full CEC 2014 single-run sweep")
    print("=" * 108)
    print(f"Functions : F1-F30")
    print(f"Algorithms: GWO, SCHO")
    print(f"D=10, N={N}, MaxIter={MAX_ITER}, seed={SEED}")
    print(f"Output    : {OUTPUT_PATH}")
    print("This is a structural/full-coverage test, not a 30-run comparison.")
    print("=" * 108)

    existing_rows, completed = load_existing()

    # Keep only rows corresponding to the current fixed E3 protocol.
    rows = []
    for row in existing_rows:
        try:
            same_protocol = (
                int(row["Seed"]) == SEED
                and int(row["Population"]) == N
                and int(row["MaxIter"]) == MAX_ITER
            )
        except Exception:
            same_protocol = False

        if same_protocol:
            rows.append(row)

    completed = {
        (row["Function"], row["Algorithm"])
        for row in rows
        if row.get("Status") == "PASS"
    }

    total = len(FUNCTIONS) * 2
    done = len(completed)

    if done:
        print(f"Resume: found {done}/{total} completed PASS runs.\n")

    for func_name in FUNCTIONS:
        benchmark = get_benchmark(func_name)

        print(
            f"\n{benchmark.name} | {benchmark.family} | "
            f"f_opt={benchmark.optimum:.1f}"
        )

        for algorithm_name, optimizer in [
            ("GWO", gwo),
            ("SCHO", scho),
        ]:
            key = (benchmark.name, algorithm_name)

            if key in completed:
                print(f"  {algorithm_name:<4} SKIP (already PASS)")
                continue

            try:
                result = run_one(
                    algorithm_name=algorithm_name,
                    optimizer=optimizer,
                    benchmark=benchmark,
                )

                # Remove an older non-PASS row for the same pair, if any.
                rows = [
                    r for r in rows
                    if (r["Function"], r["Algorithm"]) != key
                ]
                rows.append(result)
                completed.add(key)
                save_rows(rows)

                print(
                    f"  {algorithm_name:<4} "
                    f"Best={result['BestScore']:.8e}  "
                    f"Error={result['Error']:.8e}  PASS"
                )

            except Exception as exc:
                fail_row = {
                    "Function": benchmark.name,
                    "Family": benchmark.family,
                    "Algorithm": algorithm_name,
                    "Seed": SEED,
                    "Population": N,
                    "MaxIter": MAX_ITER,
                    "Optimum": float(benchmark.optimum),
                    "BestScore": "",
                    "Error": "",
                    "Curve0": "",
                    "CurveLast": "",
                    "Status": f"FAIL: {type(exc).__name__}: {exc}",
                }

                rows = [
                    r for r in rows
                    if (r["Function"], r["Algorithm"]) != key
                ]
                rows.append(fail_row)
                save_rows(rows)

                print(
                    f"  {algorithm_name:<4} "
                    f"FAIL: {type(exc).__name__}: {exc}"
                )

    # Final audit.
    pass_rows = [r for r in rows if r.get("Status") == "PASS"]
    failed_rows = [r for r in rows if r.get("Status") != "PASS"]

    expected_pairs = {
        (f"F{i}", alg)
        for i in range(1, 31)
        for alg in ("GWO", "SCHO")
    }
    pass_pairs = {
        (r["Function"], r["Algorithm"])
        for r in pass_rows
    }

    missing = sorted(expected_pairs - pass_pairs)

    print("\n" + "-" * 108)
    print("E3 final audit")
    print("-" * 108)
    print(f"PASS rows : {len(pass_rows)}/{total}")
    print(f"FAIL rows : {len(failed_rows)}")
    print(f"Missing   : {len(missing)}")

    if failed_rows:
        print("\nFailed rows:")
        for r in failed_rows:
            print(
                f"  {r['Function']} {r['Algorithm']}: "
                f"{r['Status']}"
            )

    if missing:
        print("\nMissing PASS pairs:")
        for function_name, algorithm_name in missing:
            print(f"  {function_name} {algorithm_name}")

    if failed_rows or missing:
        raise SystemExit(
            "\nE3 RESULT: FAIL\n"
            "At least one CEC2014 optimizer/function pair did not pass."
        )

    print("\nE3 RESULT: PASS")
    print("All 60 GWO/SCHO x CEC2014 F1-F30 runs passed structural checks.")
    print(f"Saved: {OUTPUT_PATH}")
    print("Optimization quality has NOT yet been judged statistically.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
