"""H2c deterministic protocol/integration test for shifted Fig.-11 benchmarks."""

from __future__ import annotations
import numpy as np

from algorithms.gwo import gwo
from benchmarks.gwo_shifted_h2 import FIG11_FUNCTIONS, get_h2_shifted_benchmark
from experiments.gwo_history_instrumented import gwo_with_history

N = 6
MAX_ITER = 100
GWO_SEED = 1000
OBJECTIVE_SEED = 91000

EXPECTED_DIMS = {
    "F1": 30, "F7": 30, "F9": 30, "F10": 30,
    "F14": 2, "F18": 2, "F26": 10, "F29": 10,
}


def main():
    print("=" * 120)
    print("H2c - Controlled-equivalent shifted Fig.-11 benchmark integration test")
    print("=" * 120)
    print(f"Functions: {', '.join(FIG11_FUNCTIONS)}")
    print(f"Protocol smoke: N={N}, MaxIter={MAX_ITER}, GWO seed={GWO_SEED}")
    print("Shift target: 65% from lower to upper bound in every coordinate")
    print("Dimensions: native paper dimensions; NOT claimed as exact Fig.-11 dimensions")
    print("=" * 120)

    for idx, name in enumerate(FIG11_FUNCTIONS):
        b = get_h2_shifted_benchmark(name)
        if b.dim != EXPECTED_DIMS[name]:
            raise AssertionError(f"{name}: dim={b.dim}, expected={EXPECTED_DIMS[name]}")
        if not np.allclose(b.target_optimum, b.lb + 0.65 * (b.ub - b.lb)):
            raise AssertionError(f"{name}: target convention mismatch")

        # Translation identity at the selected known optimum. For stochastic F7,
        # separate base/shifted objectives use the same objective RNG seed.
        obj_seed = OBJECTIVE_SEED + idx
        base_obj = b.make_base_objective(obj_seed)
        shifted_obj = b.make_objective(obj_seed)
        base_val = float(base_obj(b.base_optimum.copy()))
        shifted_val = float(shifted_obj(b.target_optimum.copy()))
        if base_val != shifted_val:
            raise AssertionError(
                f"{name}: shift identity failed: {base_val} != {shifted_val}"
            )

        # Frozen vs instrumented regression on the shifted objective.
        obj_seed = OBJECTIVE_SEED + 100 + idx
        base_score, base_pos, base_curve = gwo(
            b.make_objective(obj_seed), b.dim, b.lb, b.ub,
            N, MAX_ITER, seed=GWO_SEED,
        )
        hist = gwo_with_history(
            b.make_objective(obj_seed), b.dim, b.lb, b.ub,
            N, MAX_ITER, seed=GWO_SEED,
        )

        if float(base_score) != hist.best_score:
            raise AssertionError(f"{name}: best score changed by history adapter")
        if not np.array_equal(np.asarray(base_pos), hist.best_pos):
            raise AssertionError(f"{name}: best position changed by history adapter")
        if not np.array_equal(np.asarray(base_curve), hist.convergence_curve):
            raise AssertionError(f"{name}: convergence changed by history adapter")

        if hist.position_history.shape != (MAX_ITER, N, b.dim):
            raise AssertionError(f"{name}: bad position_history shape")
        if hist.fitness_history.shape != (MAX_ITER, N):
            raise AssertionError(f"{name}: bad fitness_history shape")
        if not np.all(np.isfinite(hist.position_history)):
            raise AssertionError(f"{name}: nonfinite position history")
        if not np.all(np.isfinite(hist.fitness_history)):
            raise AssertionError(f"{name}: nonfinite fitness history")

        print(
            f"{name:<4} D={b.dim:<2} "
            f"target_x1={b.target_optimum[0]:>11.6g} "
            f"base(target-check)={base_val:>12.6g} "
            f"smoke_final={hist.best_score:>12.6g} PASS"
        )

    print("-" * 120)
    print("H2c RESULT: PASS")
    print("All eight controlled-equivalent shifted benchmarks passed translation and GWO-history integration checks.")
    print("Next: H2d generate histories and six-panel Fig.-11-style plots for all eight functions.")


if __name__ == "__main__":
    main()
