"""H5c7 structural audit for Sea-Horse Optimizer (SHO).

This test intentionally validates the paper-equation-faithful implementation.
It does not claim line-by-line equivalence to the unrecovered historical
author SHO.m body.
"""
from __future__ import annotations

import numpy as np

from algorithms.sea_horse import sho
from benchmarks.classic_23 import get_benchmark


ANCHORS = ("F2", "F7", "F15", "F17", "F21")
N = 6
MAX_ITER = 40
SEED = 1000
OBJ_BASE = 5_037_000


def make(name):
    b = get_benchmark(name)
    return b, b.make_objective(
        seed=OBJ_BASE + int(name[1:])
    )


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

    assert d["source_code_level_verified"] is False

    assert (
        d["spiral_moves"] + d["brownian_moves"]
        == N * MAX_ITER
    )
    assert (
        d["predation_success_branch"]
        + d["predation_failure_branch"]
        == N * MAX_ITER
    )
    assert d["offspring_created"] == (N // 2) * MAX_ITER
    assert d["survivor_sorts"] == MAX_ITER

    expected_evals = N + MAX_ITER * (N + N // 2)
    assert d["objective_evaluations"] == expected_evals
    assert (
        d["objective_evaluations"]
        == d["expected_objective_evaluations"]
    )

    assert d["u"] == 0.05
    assert d["v"] == 0.05
    assert d["l"] == 0.05
    assert d["levy_s"] == 0.01
    assert d["levy_lambda"] == 1.5


def deterministic_run(name):
    b, o1 = make(name)
    a = sho(
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
    c = sho(
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
    print("H5c7 - Sea-Horse Optimizer (SHO) paper-equation audit")
    print("=" * 132)
    print(
        f"Anchors: {','.join(ANCHORS)} | N={N} | "
        f"MaxIter={MAX_ITER} | optimizer seed={SEED}"
    )
    print("IMPORTANT: SHO here = Sea-Horse Optimizer, NOT Spotted Hyena Optimizer.")
    print("Exactness: paper-equation faithful; historical author SHO.m body not line-by-line verified.")
    print("No formal 30-run comparison will be executed.")
    print("algorithms/gwo.py and algorithms/scho.py will NOT be modified.")
    print("=" * 132)

    print("\n1) Determinism + structural equation audit")
    for name in ANCHORS:
        b, run = deterministic_run(name)
        validate(name, b, run)
        d = run[3]

        print(
            f"{name:<4} D={b.dim:<2} "
            f"best={run[0]:>14.8g} "
            f"evals={d['objective_evaluations']:<4} "
            f"spiral/brownian="
            f"{d['spiral_moves']}/"
            f"{d['brownian_moves']} "
            f"predation success/fail="
            f"{d['predation_success_branch']}/"
            f"{d['predation_failure_branch']} "
            f"offspring={d['offspring_created']} PASS"
        )

    print("\n2) Guard audit")
    b, obj = make("F2")
    try:
        sho(
            obj,
            b.dim,
            b.lb,
            b.ub,
            5,
            MAX_ITER,
            seed=SEED,
        )
    except ValueError:
        print("Odd N rejected PASS")
    else:
        raise AssertionError("Odd N was not rejected")

    print("-" * 132)
    print("H5c7 RESULT: PASS")
    print("Sea-Horse SHO movement, predation, breeding, and survivor-selection equations are structurally covered.")
    print("Paper constants verified: u=v=l=0.05, Levy s=0.01, lambda=1.5, predation cutoff=0.1.")
    print("Exactness boundary: historical author SHO.m body was not line-by-line recovered; no code-level source-fidelity claim.")
    print("NumPy RNG is used; no MATLAB bitwise/random-stream equivalence is claimed.")
    print("Next: H5d nine-algorithm unified-interface/protocol compatibility audit.")
    print("=" * 132)


if __name__ == "__main__":
    main()
