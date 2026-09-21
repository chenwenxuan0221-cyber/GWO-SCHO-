"""H2b regression test: history instrumentation must not change GWO results."""

from __future__ import annotations

import numpy as np

from algorithms.gwo import gwo
from benchmarks.classic_23 import F1, F9
from experiments.gwo_history_instrumented import gwo_with_history


CASES = [
    ("F1", F1, 30, -100.0, 100.0),
    ("F9", F9, 30, -5.12, 5.12),
]

N = 6
MAX_ITER = 100
SEED = 1000


def run_case(name, func, dim, lb, ub):
    base_score, base_pos, base_curve = gwo(
        func, dim, lb, ub, N, MAX_ITER, seed=SEED
    )
    hist = gwo_with_history(
        func, dim, lb, ub, N, MAX_ITER, seed=SEED
    )

    if not np.array_equal(np.asarray(base_pos), hist.best_pos):
        raise AssertionError(f"{name}: best position changed by instrumentation")

    if float(base_score) != hist.best_score:
        raise AssertionError(
            f"{name}: best score changed: {base_score} vs {hist.best_score}"
        )

    if not np.array_equal(np.asarray(base_curve), hist.convergence_curve):
        raise AssertionError(f"{name}: convergence curve changed")

    expected_shapes = {
        "position_history": (MAX_ITER, N, dim),
        "fitness_history": (MAX_ITER, N),
        "first_agent_x1": (MAX_ITER,),
        "first_agent_fitness": (MAX_ITER,),
        "best_position_history": (MAX_ITER, dim),
        "a_history": (MAX_ITER,),
    }

    for attr, expected in expected_shapes.items():
        actual = getattr(hist, attr).shape
        if actual != expected:
            raise AssertionError(f"{name}: {attr} shape {actual} != {expected}")

    if not np.all(np.isfinite(hist.position_history)):
        raise AssertionError(f"{name}: non-finite position history")
    if not np.all(np.isfinite(hist.fitness_history)):
        raise AssertionError(f"{name}: non-finite fitness history")

    expected_a = 2.0 - 2.0 * np.arange(MAX_ITER) / MAX_ITER
    if not np.array_equal(hist.a_history, expected_a):
        raise AssertionError(f"{name}: a-history mismatch")

    if np.any(np.diff(hist.convergence_curve) > 0):
        raise AssertionError(f"{name}: historical best is not non-increasing")

    # First-agent summaries must be exact views of the full histories.
    if not np.array_equal(hist.first_agent_x1, hist.position_history[:, 0, 0]):
        raise AssertionError(f"{name}: first-agent x1 history mismatch")
    if not np.array_equal(hist.first_agent_fitness, hist.fitness_history[:, 0]):
        raise AssertionError(f"{name}: first-agent fitness history mismatch")

    print(
        f"{name}: frozen/instrumented outputs identical | "
        f"final={hist.best_score:.12g} | PASS"
    )


def main():
    print("=" * 112)
    print("H2b - GWO history-instrumentation regression test")
    print("=" * 112)
    print(f"Protocol: N={N}, MaxIter={MAX_ITER}, seed={SEED}")
    print("No shifted Fig.-11 reproduction is run in this test.")
    print("=" * 112)

    for case in CASES:
        run_case(*case)

    print("-" * 112)
    print("H2b RESULT: PASS")
    print("History instrumentation preserves the frozen GWO numerical trajectory.")
    print("algorithms/gwo.py was not modified.")
    print("Next: H2c controlled-equivalent shifted benchmark protocol + Fig.-11 reproduction.")


if __name__ == "__main__":
    main()
