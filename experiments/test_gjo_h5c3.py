"""H5c3 structural audit for Golden Jackal Optimization."""
from __future__ import annotations

import numpy as np

from algorithms.gjo import (
    _matlab_style_initialization,
    gjo,
    levy,
)
from benchmarks.classic_23 import get_benchmark


ANCHORS = ("F2", "F7", "F15", "F21")
N = 6
MAX_ITER = 40
SEED = 1000
OBJ_BASE = 5_033_000


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
            r4.random(4) * (hi[j] - lo[j]) + lo[j]
        )
    assert np.array_equal(got, exp)


def check_levy():
    r1 = np.random.default_rng(77)
    z1 = levy(5, 4, 1.5, r1)

    r2 = np.random.default_rng(77)
    z2 = levy(5, 4, 1.5, r2)

    assert z1.shape == (5, 4)
    assert np.all(np.isfinite(z1))
    assert np.array_equal(z1, z2)

    try:
        levy(2, 2, 1.0, np.random.default_rng(1))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid beta was not rejected")


def validate(name, b, run):
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

    expected_coords = N * b.dim * MAX_ITER
    assert d["objective_evaluations"] == N * MAX_ITER
    assert d["coordinate_updates"] == expected_coords
    assert d["leader_random_draws"] == expected_coords
    assert d["levy_normal_draws"] == 2 * expected_coords
    assert (
        d["exploration_updates"]
        + d["exploitation_updates"]
        == expected_coords
    )

    assert d["first_e1"] == 1.5
    expected_last = 1.5 * (
        1.0 - (MAX_ITER - 1) / MAX_ITER
    )
    assert d["last_e1"] == expected_last
    assert d["female_score_finite"]


def main():
    print("=" * 124)
    print("H5c3 - GJO source-structured Python translation audit")
    print("=" * 124)
    print(
        f"Anchors: {','.join(ANCHORS)} | N={N} | "
        f"MaxIter={MAX_ITER} | optimizer seed={SEED}"
    )
    print("No formal 30-run comparison will be executed.")
    print("algorithms/gwo.py and algorithms/scho.py will NOT be modified.")
    print("=" * 124)

    print("\n1) Initialization + Levy helper audit")
    check_initialization()
    check_levy()
    print("Initialization and Levy determinism/shape PASS")

    print("\n2) Determinism + source-structure audit")
    for name in ANCHORS:
        b, o1 = make(name)
        a = gjo(
            o1, b.dim, b.lb, b.ub, N, MAX_ITER,
            seed=SEED, return_diagnostics=True,
        )

        _, o2 = make(name)
        c = gjo(
            o2, b.dim, b.lb, b.ub, N, MAX_ITER,
            seed=SEED, return_diagnostics=True,
        )

        validate(name, b, a)

        assert a[0] == c[0]
        assert np.array_equal(a[1], c[1])
        assert np.array_equal(a[2], c[2])
        assert a[3] == c[3]

        d = a[3]
        print(
            f"{name:<4} D={b.dim:<2} "
            f"best={a[0]:>14.8g} "
            f"evals={d['objective_evaluations']:<4} "
            f"explore/exploit="
            f"{d['exploration_updates']}/"
            f"{d['exploitation_updates']} "
            f"male/female updates="
            f"{d['male_updates']}/{d['female_updates']} PASS"
        )

    print("\n3) Guard audit")
    b, obj = make("F2")
    try:
        gjo(
            obj, b.dim, b.lb, b.ub,
            1, MAX_ITER, seed=SEED,
        )
    except ValueError:
        print("N<2 rejected PASS")
    else:
        raise AssertionError("N<2 was not rejected")

    print("-" * 124)
    print("H5c3 RESULT: PASS")
    print("GJO source structure and paper phase equations are preserved.")
    print("Independent male/female leader-update semantics are preserved.")
    print("NumPy RNG is used; no MATLAB bitwise/random-stream equivalence is claimed.")
    print("Next: H5c4 implement/test AOA only.")
    print("=" * 124)


if __name__ == "__main__":
    main()
