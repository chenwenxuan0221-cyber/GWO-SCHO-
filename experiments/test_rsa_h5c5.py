"""H5c5 structural audit for Reptile Search Algorithm (RSA)."""
from __future__ import annotations

import numpy as np

from algorithms.rsa import (
    _matlab_style_initialization,
    rsa,
)
from benchmarks.classic_23 import get_benchmark


SCALAR_ANCHORS = ("F2", "F7", "F15", "F21")
VECTOR_ANCHOR = "F17"

N = 6
MAX_ITER = 40
SEED = 1000
OBJ_BASE = 5_035_000


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


def expected_phase_iterations(T):
    counts = [0, 0, 0, 0]
    for t in range(1, T + 1):
        if t < T / 4.0:
            counts[0] += 1
        elif t < 2.0 * T / 4.0 and t >= T / 4.0:
            counts[1] += 1
        elif t < 3.0 * T / 4.0 and t >= 2.0 * T / 4.0:
            counts[2] += 1
        else:
            counts[3] += 1
    return counts


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

    active = N - 1
    coord = active * b.dim * MAX_ITER

    # Exact source quirk: first solution is initialized/evaluated but never updated.
    assert d["first_solution_update_attempts"] == 0

    assert d["objective_evaluations"] == (
        N + active * MAX_ITER
    )
    assert (
        d["objective_evaluations"]
        == d["expected_objective_evaluations"]
    )
    assert d["candidate_evaluations"] == active * MAX_ITER
    assert d["coordinate_updates"] == coord

    assert d["alpha"] == 0.1
    assert d["beta"] == 0.005

    # One ES integer draw per iteration.
    assert d["es_integer_draws"] == MAX_ITER
    assert (
        d["es_negative"]
        + d["es_zero"]
        + d["es_positive"]
        == MAX_ITER
    )

    # One R-index and one rand draw per coordinate in all phases.
    assert d["r_random_index_draws"] == coord
    assert d["uniform_update_draws"] == coord

    phase_iters = expected_phase_iterations(MAX_ITER)
    expected_phases = [
        n_iter * active * b.dim
        for n_iter in phase_iters
    ]

    assert d["phase1_updates"] == expected_phases[0]
    assert d["phase2_updates"] == expected_phases[1]
    assert d["phase3_updates"] == expected_phases[2]
    assert d["phase4_updates"] == expected_phases[3]

    # Only phase 2 draws the second random population index.
    assert (
        d["phase2_extra_index_draws"]
        == expected_phases[1]
    )

    assert (
        d["greedy_accepts"]
        + d["greedy_rejects"]
        == active * MAX_ITER
    )

    if expect_vector:
        assert not d["scalar_bounds"]
        assert d["vector_bound_adapter_uses"] == coord
    else:
        assert d["scalar_bounds"]
        assert d["vector_bound_adapter_uses"] == 0


def deterministic_run(name):
    b, o1 = make(name)
    a = rsa(
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
    c = rsa(
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
    print("H5c5 - RSA source-structured Python translation audit")
    print("=" * 132)
    print(
        f"Scalar anchors: {','.join(SCALAR_ANCHORS)} | "
        f"vector-bound adapter anchor: {VECTOR_ANCHOR}"
    )
    print(
        f"N={N} | MaxIter={MAX_ITER} | optimizer seed={SEED}"
    )
    print("Author RSA.m itself uses Alpha=0.1, Beta=0.005.")
    print("No formal 30-run comparison will be executed.")
    print("algorithms/gwo.py and algorithms/scho.py will NOT be modified.")
    print("=" * 132)

    print("\n1) Initialization + phase-boundary audit")
    check_initialization()
    phases = expected_phase_iterations(MAX_ITER)
    assert phases == [9, 10, 10, 11]
    print(
        "Initialization PASS | "
        f"T=40 source phase iterations={phases} PASS"
    )

    print("\n2) Scalar-bound determinism + source-structure audit")
    for name in SCALAR_ANCHORS:
        b, run = deterministic_run(name)
        validate(
            name, b, run,
            expect_vector=False,
        )
        d = run[3]

        print(
            f"{name:<4} D={b.dim:<2} "
            f"best={run[0]:>14.8g} "
            f"evals={d['objective_evaluations']:<4} "
            f"phase coord="
            f"{d['phase1_updates']}/"
            f"{d['phase2_updates']}/"
            f"{d['phase3_updates']}/"
            f"{d['phase4_updates']} "
            f"accept/reject="
            f"{d['greedy_accepts']}/"
            f"{d['greedy_rejects']} PASS"
        )

    print("\n3) First-solution freeze + vector-bound adapter audit")
    b, run = deterministic_run(VECTOR_ANCHOR)
    validate(
        VECTOR_ANCHOR, b, run,
        expect_vector=True,
    )
    d = run[3]

    print(
        f"{VECTOR_ANCHOR:<4} D={b.dim:<2} "
        f"best={run[0]:>14.8g} "
        f"first-solution update attempts="
        f"{d['first_solution_update_attempts']} "
        f"vector-adapter uses="
        f"{d['vector_bound_adapter_uses']} PASS"
    )

    print("\n4) Guard audit")
    b, obj = make("F2")
    try:
        rsa(
            obj,
            b.dim,
            b.lb,
            b.ub,
            1,
            MAX_ITER,
            seed=SEED,
        )
    except ValueError:
        print("N<2 rejected PASS")
    else:
        raise AssertionError("N<2 was not rejected")

    print("-" * 132)
    print("H5c5 RESULT: PASS")
    print("RSA scalar-bound author source structure is preserved.")
    print("Source quirk preserved: MATLAB solution i=1 is never updated.")
    print("Source precedence preserved for R: Best - Xrandom/(Best+eps).")
    print("Author RSA.m confirms Alpha=0.1 and Beta=0.005.")
    print("F17 uses an explicit coordinate-span vector-bound adapter; it is not claimed author-source exact.")
    print("NumPy RNG is used; no MATLAB bitwise/random-stream equivalence is claimed.")
    print("Next: H5c6 implement/test ALO only.")
    print("=" * 132)


if __name__ == "__main__":
    main()
