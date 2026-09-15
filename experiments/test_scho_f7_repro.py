"""C11.5 - F7 RNG reproducibility audit.

Prerequisite:
    benchmarks/classic_23.py must register F7 with stochastic=True.

Run from project root:
    python -m experiments.test_scho_f7_repro
"""

from __future__ import annotations

import numpy as np

from algorithms.scho import scho
from benchmarks.classic_23 import get_benchmark


SEED = 1000
N = 30
MAX_ITER = 500


def main():
    benchmark = get_benchmark("F7")

    print("=" * 72)
    print("C11.5 - F7 RNG reproducibility audit")
    print("=" * 72)
    print(f"benchmark.stochastic = {benchmark.stochastic}")

    if not benchmark.stochastic:
        raise AssertionError(
            "F7 is still registered with stochastic=False. "
            "Set stochastic=True in benchmarks/classic_23.py."
        )

    x = np.zeros(benchmark.dim)

    # Two separately-created objective wrappers with the same seed should
    # generate the same noise sequence.
    obj_a = benchmark.make_objective(seed=SEED)
    obj_b = benchmark.make_objective(seed=SEED)

    seq_a = np.array([obj_a(x) for _ in range(3)], dtype=float)
    seq_b = np.array([obj_b(x) for _ in range(3)], dtype=float)

    print("\nF7 noise sequence A:")
    print(seq_a)
    print("F7 noise sequence B:")
    print(seq_b)

    if not np.array_equal(seq_a, seq_b):
        raise AssertionError("Same objective seed did not reproduce the same F7 noise sequence.")

    # Full SCHO run #1
    objective_1 = benchmark.make_objective(seed=SEED)
    score_1, pos_1, curve_1 = scho(
        obj_func=objective_1,
        dim=benchmark.dim,
        lb=benchmark.lb,
        ub=benchmark.ub,
        N=N,
        MaxIter=MAX_ITER,
        seed=SEED,
    )

    # Full SCHO run #2, reconstructed from scratch with exactly the same seeds.
    objective_2 = benchmark.make_objective(seed=SEED)
    score_2, pos_2, curve_2 = scho(
        obj_func=objective_2,
        dim=benchmark.dim,
        lb=benchmark.lb,
        ub=benchmark.ub,
        N=N,
        MaxIter=MAX_ITER,
        seed=SEED,
    )

    print("\nFull SCHO F7 run #1:")
    print(f"Best score = {score_1:.16e}")
    print("Full SCHO F7 run #2:")
    print(f"Best score = {score_2:.16e}")

    same_score = score_1 == score_2
    same_pos = np.array_equal(pos_1, pos_2)
    same_curve = np.array_equal(curve_1, curve_2)

    print("\nExact reproducibility checks:")
    print(f"score : {same_score}")
    print(f"pos   : {same_pos}")
    print(f"curve : {same_curve}")

    assert same_score, "F7 best scores differ under the same seeds."
    assert same_pos, "F7 best positions differ under the same seeds."
    assert same_curve, "F7 convergence curves differ under the same seeds."

    print("\nPASS: C11.5 F7 reproducibility is now deterministic.")


if __name__ == "__main__":
    main()
