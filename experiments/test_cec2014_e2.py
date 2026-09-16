"""E2 - GWO/SCHO compatibility smoke test on representative CEC 2014 functions.

Representative functions:
    F1  -> Unimodal
    F8  -> Simple multimodal
    F17 -> Hybrid
    F23 -> Composition

Protocol:
    D=10, N=30, MaxIter=500, seed=1000

This stage is structural only:
- no 30-run statistics
- no paper-quality judgement
- no algorithm tuning
- algorithms/gwo.py and algorithms/scho.py remain unchanged

Place at:
    experiments/test_cec2014_e2.py

Run from project root:
    python -m experiments.test_cec2014_e2
"""

from __future__ import annotations

import numpy as np

from algorithms.gwo import gwo
from algorithms.scho import scho
from benchmarks.cec2014 import get_benchmark


FUNCTIONS = ["F1", "F8", "F17", "F23"]

N = 30
MAX_ITER = 500
SEED = 1000


def validate_run(
    *,
    algorithm_name: str,
    benchmark,
    best_score,
    best_pos,
    curve,
):
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

    if best_score != curve[-1]:
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            "best_score != curve[-1]"
        )

    # The returned best position should lie in the original CEC search box.
    tol = 1e-12
    if np.any(best_pos < benchmark.lb - tol) or np.any(best_pos > benchmark.ub + tol):
        raise AssertionError(
            f"{algorithm_name} {benchmark.name}: "
            "best_pos is outside [-100, 100]^10"
        )


def run_one(algorithm_name: str, optimizer, benchmark):
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

    return {
        "algorithm": algorithm_name,
        "function": benchmark.name,
        "family": benchmark.family,
        "optimum": benchmark.optimum,
        "best_score": float(best_score),
        "error": float(best_score - benchmark.optimum),
        "curve0": float(curve[0]),
        "curve_last": float(curve[-1]),
        "status": "PASS",
    }


def main():
    print("=" * 124)
    print("E2 - GWO/SCHO compatibility smoke test on representative CEC 2014 functions")
    print(f"D=10, N={N}, MaxIter={MAX_ITER}, seed={SEED}")
    print("Functions: F1 (unimodal), F8 (simple multimodal), F17 (hybrid), F23 (composition)")
    print("=" * 124)

    results = []

    for func_name in FUNCTIONS:
        benchmark = get_benchmark(func_name)

        print(
            f"\n{benchmark.name}: "
            f"{benchmark.family}, optimum={benchmark.optimum:.1f}"
        )

        for algorithm_name, optimizer in [
            ("GWO", gwo),
            ("SCHO", scho),
        ]:
            try:
                result = run_one(
                    algorithm_name=algorithm_name,
                    optimizer=optimizer,
                    benchmark=benchmark,
                )
                results.append(result)

                print(
                    f"  {algorithm_name:<4} "
                    f"Best={result['best_score']:.8e}  "
                    f"Error={result['error']:.8e}  "
                    f"Curve[0]={result['curve0']:.8e}  "
                    f"Curve[-1]={result['curve_last']:.8e}  "
                    f"PASS"
                )

            except Exception as exc:
                results.append(
                    {
                        "algorithm": algorithm_name,
                        "function": benchmark.name,
                        "family": benchmark.family,
                        "optimum": benchmark.optimum,
                        "best_score": np.nan,
                        "error": np.nan,
                        "curve0": np.nan,
                        "curve_last": np.nan,
                        "status": f"FAIL: {type(exc).__name__}: {exc}",
                    }
                )

                print(
                    f"  {algorithm_name:<4} "
                    f"FAIL: {type(exc).__name__}: {exc}"
                )

    print("\n" + "-" * 124)
    print(
        f"{'Function':<10}"
        f"{'Family':<22}"
        f"{'Algorithm':<12}"
        f"{'Best':>18}"
        f"{'Optimum':>14}"
        f"{'Error':>18}"
        f"{'Status':>12}"
    )
    print("-" * 124)

    all_pass = True

    for row in results:
        if row["status"] != "PASS":
            all_pass = False

        best_text = (
            f"{row['best_score']:.8e}"
            if np.isfinite(row["best_score"])
            else "nan"
        )
        error_text = (
            f"{row['error']:.8e}"
            if np.isfinite(row["error"])
            else "nan"
        )

        print(
            f"{row['function']:<10}"
            f"{row['family']:<22}"
            f"{row['algorithm']:<12}"
            f"{best_text:>18}"
            f"{row['optimum']:>14.1f}"
            f"{error_text:>18}"
            f"{row['status']:>12}"
        )

    print("-" * 124)

    if not all_pass:
        raise SystemExit(
            "\nE2 RESULT: FAIL\n"
            "At least one representative CEC2014 run failed structural checks."
        )

    print("\nE2 RESULT: PASS")
    print("All 8 representative optimizer/function runs passed structural checks.")
    print("Optimization quality has NOT yet been judged statistically.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
