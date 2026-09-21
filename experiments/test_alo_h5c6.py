"""H5c6 structural audit for Mirjalili's Ant Lion Optimizer."""
from __future__ import annotations

import numpy as np

from algorithms.alo import (
    _matlab_style_initialization,
    _roulette_wheel_selection,
    _shrink_ratio,
    alo,
)
from benchmarks.classic_23 import get_benchmark


ANCHORS = ("F2", "F7", "F15", "F21")
N = 6
MAX_ITER = 40
SEED = 1000
OBJ_BASE = 5_036_000


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


def check_shrink_schedule():
    expected_stages = {
        1: 3,
        2: 16,
        3: 10,
        4: 6,
        5: 2,
        6: 2,
    }
    counts = {k: 0 for k in range(1, 7)}
    for t in range(2, MAX_ITER + 1):
        I, stage = _shrink_ratio(t, MAX_ITER)
        assert I >= 1.0
        counts[stage] += 1
    assert counts == expected_stages

    assert _shrink_ratio(2, MAX_ITER) == (1.0, 1)
    I_last, stage_last = _shrink_ratio(
        MAX_ITER, MAX_ITER
    )
    assert I_last == 1000001.0
    assert stage_last == 6


def check_roulette_literal_behavior():
    # Positive finite weights: deterministic same seed.
    w = np.array([1.0, 2.0, 3.0])
    a = _roulette_wheel_selection(
        w, np.random.default_rng(77)
    )
    b = _roulette_wheel_selection(
        w, np.random.default_rng(77)
    )
    assert a == b
    assert a in (0, 1, 2)

    # Inf accumulation reproduces the source's "no selection" possibility,
    # which the main ALO then converts to the first antlion.
    w_inf = np.array([np.inf, 1.0])
    idx = _roulette_wheel_selection(
        w_inf, np.random.default_rng(77)
    )
    assert idx == -1


def validate(name, b, run):
    score, pos, curve, d = run
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    assert np.isfinite(score)
    assert pos.shape == (b.dim,)
    assert np.all(np.isfinite(pos))
    assert curve.shape == (MAX_ITER,)
    assert np.all(np.isfinite(curve))

    # Source curve recording starts at Current_iter=2.
    assert curve[0] == 0.0
    assert np.all(np.diff(curve[1:]) <= 0.0)
    assert score == float(curve[-1])

    assert d["objective_evaluations"] == N * MAX_ITER
    assert (
        d["objective_evaluations"]
        == d["expected_objective_evaluations"]
    )

    assert d["roulette_draws"] == N * (MAX_ITER - 1)
    assert d["roulette_draws"] == d["expected_roulette_draws"]

    assert (
        d["random_walk_calls"]
        == 2 * N * (MAX_ITER - 1)
    )
    assert (
        d["random_walk_calls"]
        == d["expected_random_walk_calls"]
    )

    assert (
        d["random_walk_boundary_draws"]
        == 4 * N * (MAX_ITER - 1)
    )
    assert (
        d["random_walk_boundary_draws"]
        == d["expected_random_walk_boundary_draws"]
    )

    exp_steps = (
        2
        * N
        * (MAX_ITER - 1)
        * b.dim
        * MAX_ITER
    )
    assert d["random_walk_step_draws"] == exp_steps
    assert (
        d["random_walk_step_draws"]
        == d["expected_random_walk_step_draws"]
    )

    assert d["merge_sorts"] == MAX_ITER - 1
    assert d["merge_sorts"] == d["expected_merge_sorts"]

    # Each iteration stage is invoked by 2*N random-walk calls.
    expected_iters = {
        1: 3,
        2: 16,
        3: 10,
        4: 6,
        5: 2,
        6: 2,
    }
    for stage, n_iter in expected_iters.items():
        assert (
            d["shrink_stage_calls"][stage]
            == n_iter * 2 * N
        )


def deterministic_run(name):
    b, o1 = make(name)
    a = alo(
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
    c = alo(
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
    print("=" * 132)
    print("H5c6 - ALO source-structured Python translation audit")
    print("=" * 132)
    print(
        f"Anchors: {','.join(ANCHORS)} | N={N} | "
        f"MaxIter={MAX_ITER} | optimizer seed={SEED}"
    )
    print("No formal 30-run comparison will be executed.")
    print("algorithms/gwo.py and algorithms/scho.py will NOT be modified.")
    print("=" * 132)

    print("\n1) Initialization + shrink schedule + roulette audit")
    check_initialization()
    check_shrink_schedule()
    check_roulette_literal_behavior()
    print(
        "Initialization PASS | I-stage counts "
        "[3,16,10,6,2,2] PASS | literal roulette PASS"
    )

    print("\n2) Determinism + source-structure audit")
    for name in ANCHORS:
        b, run = deterministic_run(name)
        validate(name, b, run)
        d = run[3]

        print(
            f"{name:<4} D={b.dim:<2} "
            f"best={run[0]:>14.8g} "
            f"evals={d['objective_evaluations']:<4} "
            f"roulette fallback="
            f"{d['roulette_fallbacks']:<3} "
            f"RW calls={d['random_walk_calls']:<4} "
            f"RW step draws="
            f"{d['random_walk_step_draws']:<8} PASS"
        )

    print("\n3) Guard audit")
    b, obj = make("F2")
    try:
        alo(
            obj,
            b.dim,
            b.lb,
            b.ub,
            N,
            1,
            seed=SEED,
        )
    except ValueError:
        print("MaxIter<2 rejected PASS")
    else:
        raise AssertionError("MaxIter<2 was not rejected")

    print("-" * 132)
    print("H5c6 RESULT: PASS")
    print("ALO source main-loop, roulette, elitism, and full random-walk regeneration are preserved.")
    print("Source behavior preserved: zero/negative fitness is not repaired before reciprocal roulette weighting.")
    print("Source quirk preserved: convergence_curve[0] remains zero.")
    print("NumPy RNG is used; no MATLAB bitwise/random-stream equivalence is claimed.")
    print("Next: H5c7 implement/test Sea-Horse Optimizer only.")
    print("=" * 132)


if __name__ == "__main__":
    main()
