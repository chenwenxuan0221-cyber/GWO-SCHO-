"""H5c4 structural audit for AOA under the SCHO Table-6 protocol."""
from __future__ import annotations

import numpy as np

from algorithms.aoa import (
    _matlab_style_initialization,
    aoa,
)
from benchmarks.classic_23 import get_benchmark


SCALAR_ANCHORS = ("F2", "F7", "F15", "F21")
VECTOR_ANCHOR = "F17"

N = 6
MAX_ITER = 40
SEED = 1000
OBJ_BASE = 5_034_000


def make(name):
    b = get_benchmark(name)
    return b, b.make_objective(
        seed=OBJ_BASE + int(name[1:])
    )


def check_initialization():
    r1 = np.random.default_rng(1234)
    got = _matlab_style_initialization(
        4, 3, -2.0, 5.0, r1
    )

    r2 = np.random.default_rng(1234)
    exp = r2.random((4, 3)) * 7.0 - 2.0
    assert np.array_equal(got, exp)

    lo = np.array([-2.0, -1.0, 0.0])
    hi = np.array([2.0, 3.0, 5.0])

    r3 = np.random.default_rng(4321)
    got = _matlab_style_initialization(
        4, 3, lo, hi, r3
    )

    r4 = np.random.default_rng(4321)
    exp = np.empty((4, 3))
    for j in range(3):
        exp[:, j] = (
            r4.random(4)
            * (hi[j] - lo[j])
            + lo[j]
        )
    assert np.array_equal(got, exp)


def validate(name, b, run, expect_vector):
    score, pos, curve, d = run

    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    assert np.isfinite(score)
    assert pos.shape == (b.dim,)
    assert np.all(np.isfinite(pos))
    assert curve.shape == (MAX_ITER,)
    assert np.all(np.isfinite(curve))
    assert np.all(np.diff(curve) <= 0.0)
    assert score == float(curve[-1])

    coords = N * b.dim * MAX_ITER

    # Source performs initial N evaluations plus N evaluations per iteration.
    assert d["objective_evaluations"] == N * (MAX_ITER + 1)
    assert (
        d["objective_evaluations"]
        == d["expected_objective_evaluations"]
    )

    assert d["coordinate_updates"] == coords
    assert d["unconditional_r1_draws"] == coords
    assert d["branch_random_draws"] == coords

    if expect_vector:
        assert not d["scalar_bounds"]
        # Crucial AOA.m quirk.
        assert d["vector_extra_r1_draws"] == coords
    else:
        assert d["scalar_bounds"]
        assert d["vector_extra_r1_draws"] == 0

    assert (
        d["division_updates"]
        + d["multiplication_updates"]
        + d["subtraction_updates"]
        + d["addition_updates"]
        == coords
    )

    assert (
        d["greedy_accepts"]
        + d["greedy_rejects"]
        == N * MAX_ITER
    )

    # SCHO Table 6 protocol override.
    assert d["mu"] == 0.5
    assert d["alpha"] == 5.0

    expected_first_mop = 1.0 - (
        1.0 ** (1.0 / 5.0)
        / MAX_ITER ** (1.0 / 5.0)
    )
    expected_first_moa = (
        0.2 + 1.0 * (0.8 / MAX_ITER)
    )

    assert d["first_mop"] == expected_first_mop
    assert d["first_moa"] == expected_first_moa
    assert d["last_mop"] == 0.0
    assert d["last_moa"] == 1.0


def deterministic_run(name):
    b, o1 = make(name)
    a = aoa(
        o1,
        b.dim,
        b.lb,
        b.ub,
        N,
        MAX_ITER,
        seed=SEED,
        return_diagnostics=True,
    )

    _, o2 = make(name)
    c = aoa(
        o2,
        b.dim,
        b.lb,
        b.ub,
        N,
        MAX_ITER,
        seed=SEED,
        return_diagnostics=True,
    )

    assert a[0] == c[0]
    assert np.array_equal(a[1], c[1])
    assert np.array_equal(a[2], c[2])
    assert a[3] == c[3]

    return b, a


def main():
    print("=" * 128)
    print("H5c4 - AOA source-structured translation + SCHO Table-6 mu override audit")
    print("=" * 128)
    print(
        f"Scalar anchors: {','.join(SCALAR_ANCHORS)} | "
        f"vector-bound anchor: {VECTOR_ANCHOR}"
    )
    print(
        f"N={N} | MaxIter={MAX_ITER} | optimizer seed={SEED}"
    )
    print("H5 protocol: Alpha=5, Mu=0.5 (SCHO Table 6).")
    print("Author AOA.m default Mu=0.499 is NOT used in H5 formal runs.")
    print("No formal 30-run comparison will be executed.")
    print("algorithms/gwo.py and algorithms/scho.py will NOT be modified.")
    print("=" * 128)

    print("\n1) Initialization call-shape audit")
    check_initialization()
    print("Scalar/vector initialization structure PASS")

    print("\n2) Scalar-bound determinism + source-structure audit")
    for name in SCALAR_ANCHORS:
        b, run = deterministic_run(name)
        validate(name, b, run, expect_vector=False)
        d = run[3]

        print(
            f"{name:<4} D={b.dim:<2} "
            f"best={run[0]:>14.8g} "
            f"evals={d['objective_evaluations']:<4} "
            f"D/M/S/A="
            f"{d['division_updates']}/"
            f"{d['multiplication_updates']}/"
            f"{d['subtraction_updates']}/"
            f"{d['addition_updates']} "
            f"accept/reject="
            f"{d['greedy_accepts']}/"
            f"{d['greedy_rejects']} PASS"
        )

    print("\n3) Vector-bound extra-r1 source-quirk audit")
    b, run = deterministic_run(VECTOR_ANCHOR)
    validate(
        VECTOR_ANCHOR, b, run,
        expect_vector=True,
    )
    d = run[3]

    print(
        f"{VECTOR_ANCHOR:<4} D={b.dim:<2} "
        f"best={run[0]:>14.8g} "
        f"r1 base/extra="
        f"{d['unconditional_r1_draws']}/"
        f"{d['vector_extra_r1_draws']} "
        "PASS"
    )

    print("\n4) Protocol-override audit")
    b, obj = make("F2")
    *_, d = aoa(
        obj,
        b.dim,
        b.lb,
        b.ub,
        N,
        4,
        seed=SEED,
        return_diagnostics=True,
    )
    assert d["mu"] == 0.5
    print("SCHO Table-6 Mu=0.5 override PASS")

    print("-" * 128)
    print("H5c4 RESULT: PASS")
    print("AOA author source control-flow structure is preserved.")
    print("Vector-bound duplicate-r1 source quirk is preserved.")
    print("H5 parameter override is explicit: Mu=0.5 (author AOA.m default is 0.499).")
    print("NumPy RNG is used; no MATLAB bitwise/random-stream equivalence is claimed.")
    print("Next: H5c5 implement/test RSA only.")
    print("=" * 128)


if __name__ == "__main__":
    main()
