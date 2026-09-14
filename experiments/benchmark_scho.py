"""C10 smoke test: source-faithful SCHO on F1-F7, one run each.

This script intentionally does NOT modify algorithms/scho.py.
It only connects the frozen SCHO baseline to benchmarks.classic_23.

Place this file at:
    experiments/benchmark_scho.py

Run from the project root:
    python -m experiments.benchmark_scho
"""

from __future__ import annotations

import numpy as np

from algorithms.scho import scho
from benchmarks.classic_23 import get_benchmark


FUNCTIONS = [f"F{i}" for i in range(1, 8)]
N = 30
MAX_ITER = 500
SEED = 1000


def _check_run(best_score, best_pos, curve, dim, max_iter):
    """Return (passed, reasons) for structural smoke-test checks."""
    reasons = []

    if not np.isfinite(best_score):
        reasons.append("best_score is NaN/Inf")

    if np.asarray(best_pos).shape != (dim,):
        reasons.append(
            f"best_pos shape is {np.asarray(best_pos).shape}, expected {(dim,)}"
        )

    if not np.all(np.isfinite(best_pos)):
        reasons.append("best_pos contains NaN/Inf")

    curve = np.asarray(curve, dtype=float)

    if curve.shape != (max_iter,):
        reasons.append(
            f"curve shape is {curve.shape}, expected {(max_iter,)}"
        )

    if not np.all(np.isfinite(curve)):
        reasons.append("curve contains NaN/Inf")

    # Source-faithful SCHO stores the historical best, so the curve
    # must never increase.
    if curve.size > 1 and np.any(np.diff(curve) > 0.0):
        reasons.append("historical-best curve increases")

    if curve.size > 0 and best_score != curve[-1]:
        reasons.append("best_score != curve[-1]")

    return len(reasons) == 0, reasons


def run_one(name: str, seed: int = SEED):
    benchmark = get_benchmark(name)
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

    passed, reasons = _check_run(
        best_score=best_score,
        best_pos=best_pos,
        curve=curve,
        dim=benchmark.dim,
        max_iter=MAX_ITER,
    )

    return {
        "Function": name,
        "Best": float(best_score),
        "Optimum": float(benchmark.optimum),
        "Gap": float(best_score - benchmark.optimum),
        "Curve0": float(curve[0]),
        "CurveEnd": float(curve[-1]),
        "Status": "PASS" if passed else "FAIL",
        "Reasons": reasons,
    }


def main():
    print("=" * 104)
    print("C10 - Source-faithful SCHO smoke test on F1-F7 (1 run each)")
    print(f"N={N}, MaxIter={MAX_ITER}, seed={SEED}")
    print("=" * 104)
    print(
        f"{'Function':<8}"
        f"{'Best':>17}"
        f"{'Optimum':>15}"
        f"{'Gap':>17}"
        f"{'Curve[0]':>17}"
        f"{'Curve[-1]':>17}"
        f"{'Status':>10}"
    )
    print("-" * 104)

    results = []

    for name in FUNCTIONS:
        try:
            result = run_one(name)
        except Exception as exc:
            result = {
                "Function": name,
                "Best": np.nan,
                "Optimum": np.nan,
                "Gap": np.nan,
                "Curve0": np.nan,
                "CurveEnd": np.nan,
                "Status": "ERROR",
                "Reasons": [f"{type(exc).__name__}: {exc}"],
            }

        results.append(result)

        print(
            f"{result['Function']:<8}"
            f"{result['Best']:>17.8e}"
            f"{result['Optimum']:>15.6e}"
            f"{result['Gap']:>17.8e}"
            f"{result['Curve0']:>17.8e}"
            f"{result['CurveEnd']:>17.8e}"
            f"{result['Status']:>10}"
        )

        if result["Reasons"]:
            for reason in result["Reasons"]:
                print(f"         -> {reason}")

    failures = [r for r in results if r["Status"] != "PASS"]

    if failures:
        print("\nC10 RESULT: FAIL")
        print("At least one function failed the structural smoke test.")
        raise SystemExit(1)

    print("\nC10 RESULT: PASS")
    print("F1-F7 all completed one source-faithful SCHO run successfully.")
    print("No structural problem was detected; algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
