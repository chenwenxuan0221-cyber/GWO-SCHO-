"""H5c1 - structural/source audit for the Sine Cosine Algorithm port."""

from __future__ import annotations

import numpy as np

from algorithms.sca import (
    _matlab_style_initialization,
    sca,
)
from benchmarks.classic_23 import get_benchmark


ANCHORS = ("F2", "F7", "F15", "F21")
N = 6
MAX_ITER = 40
OPTIMIZER_SEED = 1000
OBJECTIVE_SEED_BASE = 5_031_000


def _objective_seed(name: str) -> int:
    return OBJECTIVE_SEED_BASE + int(name[1:])


def _make(name: str):
    b = get_benchmark(name)
    return b, b.make_objective(seed=_objective_seed(name))


def _validate(name, b, score, pos, curve, diag):
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    assert np.isfinite(score), f"{name}: score NaN/Inf"
    assert pos.shape == (b.dim,), f"{name}: wrong best-position shape"
    assert np.all(np.isfinite(pos)), f"{name}: best position NaN/Inf"
    assert curve.shape == (MAX_ITER,), f"{name}: wrong curve shape"
    assert np.all(np.isfinite(curve)), f"{name}: curve NaN/Inf"

    # Author-source quirk: first curve element is never assigned.
    assert curve[0] == 0.0, f"{name}: source curve[0] quirk lost"

    # From t=2 onward the stored curve is the historical best.
    assert np.all(np.diff(curve[1:]) <= 0.0), (
        f"{name}: historical-best tail increased"
    )
    assert score == float(curve[-1]), f"{name}: score != curve[-1]"

    assert diag["objective_evaluations"] == N * MAX_ITER
    assert diag["objective_evaluations"] == diag["expected_objective_evaluations"]
    assert diag["coordinate_updates"] == (MAX_ITER - 1) * N * b.dim
    assert diag["random_draws_update"] == 3 * (MAX_ITER - 1) * N * b.dim
    assert diag["random_draws_update"] == diag["expected_random_draws_update"]
    assert diag["sine_updates"] + diag["cosine_updates"] == diag["coordinate_updates"]

    expected_first_r1 = 2.0 - 2.0 * (2.0 / MAX_ITER)
    assert diag["first_r1"] == expected_first_r1
    assert diag["last_r1"] == 0.0


def _initialization_call_shape_audit():
    rng1 = np.random.default_rng(1234)
    got_scalar = _matlab_style_initialization(
        4, 3, -2.0, 5.0, rng1
    )

    rng2 = np.random.default_rng(1234)
    expected_scalar = rng2.random((4, 3)) * 7.0 - 2.0
    assert np.array_equal(got_scalar, expected_scalar)

    lb = np.array([-2.0, -1.0, 0.0])
    ub = np.array([2.0, 3.0, 5.0])

    rng3 = np.random.default_rng(4321)
    got_vector = _matlab_style_initialization(
        4, 3, lb, ub, rng3
    )

    rng4 = np.random.default_rng(4321)
    expected_vector = np.empty((4, 3))
    for j in range(3):
        expected_vector[:, j] = (
            rng4.random(4) * (ub[j] - lb[j]) + lb[j]
        )

    assert np.array_equal(got_vector, expected_vector)


def main():
    print("=" * 124)
    print("H5c1 - SCA source-structured Python translation audit")
    print("=" * 124)
    print(
        f"Anchors: {','.join(ANCHORS)} | N={N} | "
        f"MaxIter={MAX_ITER} | optimizer seed={OPTIMIZER_SEED}"
    )
    print("No formal 30-run comparison will be executed.")
    print("algorithms/gwo.py and algorithms/scho.py will NOT be modified.")
    print("=" * 124)

    print("\n1) Initialization call-shape audit")
    _initialization_call_shape_audit()
    print("Scalar/vector initialization structure PASS")

    print("\n2) Determinism + source-structure audit")
    for name in ANCHORS:
        b, obj1 = _make(name)
        run1 = sca(
            obj_func=obj1,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=OPTIMIZER_SEED,
            return_diagnostics=True,
        )

        _, obj2 = _make(name)
        run2 = sca(
            obj_func=obj2,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=OPTIMIZER_SEED,
            return_diagnostics=True,
        )

        score1, pos1, curve1, diag1 = run1
        score2, pos2, curve2, diag2 = run2

        _validate(name, b, score1, pos1, curve1, diag1)

        assert score1 == score2, f"{name}: score not deterministic"
        assert np.array_equal(pos1, pos2), f"{name}: position not deterministic"
        assert np.array_equal(curve1, curve2), f"{name}: curve not deterministic"
        assert diag1 == diag2, f"{name}: diagnostics not deterministic"

        print(
            f"{name:<4} D={b.dim:<2} best={score1:>14.8g} "
            f"evals={diag1['objective_evaluations']:<4} "
            f"updates={diag1['coordinate_updates']:<5} "
            f"sin/cos={diag1['sine_updates']}/{diag1['cosine_updates']} PASS"
        )

    print("\n3) Guard audit")
    b, obj = _make("F2")
    try:
        sca(
            obj_func=obj,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=1,
            seed=OPTIMIZER_SEED,
        )
    except ValueError:
        print("MaxIter<2 rejected PASS")
    else:
        raise AssertionError("MaxIter<2 was not rejected")

    print("-" * 124)
    print("H5c1 RESULT: PASS")
    print("SCA source structure is preserved in the Python port.")
    print("Source quirk preserved: convergence_curve[0] remains zero.")
    print("NumPy RNG is used; no MATLAB bitwise/random-stream equivalence is claimed.")
    print("Next: H5c2 implement/test SSA only.")
    print("=" * 124)


if __name__ == "__main__":
    main()
