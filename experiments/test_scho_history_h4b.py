"""H4b - Exact-equivalence audit for SCHO history instrumentation.

No formal Fig. 8 reproduction is generated here.

The test compares the instrumented implementation with frozen
`algorithms/scho.py` on all seven functions displayed in paper Fig. 8:
F2, F7, F9, F10, F11, F15, F21.

Smoke protocol:
- N = 6
- MaxIter = 40
- optimizer seed = 1000
- objective seed = 2024000 + function number

The smaller N/MaxIter is intentional: this stage validates equivalence and
history semantics only. H4c will use the paper-scale N=30 / MaxIter=500.
"""

from __future__ import annotations

import numpy as np

from algorithms.scho import scho
from benchmarks.classic_23 import get_benchmark
from experiments.scho_history_instrumented_h4 import scho_with_history


FUNCTIONS = ["F2", "F7", "F9", "F10", "F11", "F15", "F21"]
N = 6
MAX_ITER = 40
OPTIMIZER_SEED = 1000


def _objective_seed(name: str) -> int:
    return 2_024_000 + int(name[1:])


def _assert_history(name, b, curve, history):
    pos = np.asarray(history["position_history"], dtype=float)
    fit = np.asarray(history["fitness_history"], dtype=float)
    x1 = np.asarray(history["first_agent_x1"], dtype=float)
    avg = np.asarray(history["average_fitness"], dtype=float)
    best_pos_hist = np.asarray(history["best_position_history"], dtype=float)
    conv = np.asarray(history["convergence"], dtype=float)
    phase = np.asarray(history["phase_history"])
    redist = np.asarray(history["redistribution_count"])

    assert pos.shape == (MAX_ITER, N, b.dim), (
        name, "position_history", pos.shape
    )
    assert fit.shape == (MAX_ITER, N), (name, "fitness_history", fit.shape)
    assert x1.shape == (MAX_ITER,), (name, "first_agent_x1", x1.shape)
    assert avg.shape == (MAX_ITER,), (name, "average_fitness", avg.shape)
    assert best_pos_hist.shape == (MAX_ITER, b.dim), (
        name, "best_position_history", best_pos_hist.shape
    )
    assert conv.shape == (MAX_ITER,), (name, "convergence", conv.shape)
    assert phase.shape == (MAX_ITER,), (name, "phase_history", phase.shape)
    assert redist.shape == (MAX_ITER,), (
        name, "redistribution_count", redist.shape
    )

    assert np.all(np.isfinite(pos)), f"{name}: non-finite position history"
    assert np.all(np.isfinite(fit)), f"{name}: non-finite fitness history"
    assert np.all(np.isfinite(avg)), f"{name}: non-finite average fitness"
    assert np.all(np.isfinite(conv)), f"{name}: non-finite convergence"

    assert np.array_equal(x1, pos[:, 0, 0]), (
        f"{name}: first_agent_x1 does not match position history"
    )
    assert np.array_equal(avg, np.mean(fit, axis=1)), (
        f"{name}: average_fitness does not exactly match population mean"
    )
    assert np.array_equal(conv, curve), (
        f"{name}: history convergence != returned convergence"
    )
    assert not np.any(np.diff(conv) > 0.0), (
        f"{name}: historical-best curve increased"
    )

    T = int(history["T"])
    expected_phase = np.where(
        np.arange(1, MAX_ITER + 1) <= T, 1, 2
    ).astype(np.int8)
    assert np.array_equal(phase, expected_phase), (
        f"{name}: phase labels do not match T={T}"
    )

    # For this smoke protocol the literal source bounded-search block should
    # be exercised, proving history collection also spans that unusual path.
    assert np.sum(redist) > 0, (
        f"{name}: bounded-search redistribution path was not exercised"
    )


def main():
    print("=" * 118)
    print("H4b - SCHO Fig.8 history instrumentation exact-equivalence audit")
    print("=" * 118)
    print(
        f"Functions: {', '.join(FUNCTIONS)} | "
        f"N={N} | MaxIter={MAX_ITER} | optimizer seed={OPTIMIZER_SEED}"
    )
    print("Frozen algorithms/scho.py will NOT be modified.")
    print("=" * 118)

    for name in FUNCTIONS:
        b = get_benchmark(name)
        obj_seed = _objective_seed(name)

        # Reconstruct objective wrappers independently so stochastic F7 starts
        # from the same objective-RNG state in each implementation.
        ref_obj = b.make_objective(seed=obj_seed)
        hist_obj = b.make_objective(seed=obj_seed)

        ref_score, ref_pos, ref_curve = scho(
            obj_func=ref_obj,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=OPTIMIZER_SEED,
        )

        score, pos, curve, history = scho_with_history(
            obj_func=hist_obj,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=OPTIMIZER_SEED,
        )

        same_score = ref_score == score
        same_pos = np.array_equal(ref_pos, pos)
        same_curve = np.array_equal(ref_curve, curve)

        if not same_score:
            raise AssertionError(
                f"{name}: best score changed after instrumentation"
            )
        if not same_pos:
            raise AssertionError(
                f"{name}: best position changed after instrumentation"
            )
        if not same_curve:
            raise AssertionError(
                f"{name}: convergence curve changed after instrumentation"
            )

        _assert_history(name, b, curve, history)

        redist_total = int(np.sum(history["redistribution_count"]))
        print(
            f"{name:<4} D={b.dim:<2} "
            f"best={score:>14.8g} "
            f"score/pos/curve EXACT "
            f"history PASS "
            f"redistributions={redist_total}"
        )

    print("-" * 118)
    print("H4b RESULT: PASS")
    print("All 7 Fig.8 functions preserve frozen SCHO score/position/curve exactly.")
    print("History arrays are structurally valid and add no objective/RNG calls.")
    print("Next: H4c paper-scale Fig.8 qualitative reproduction (N=30, MaxIter=500).")


if __name__ == "__main__":
    main()
