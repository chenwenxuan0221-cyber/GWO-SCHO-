"""H3b validation of the D=100/D=500 F1-F13 scalability adapter.

No 30-run experiment is executed here.  The test checks benchmark metadata,
formula reuse, F7 reproducibility, and source-faithful SCHO integration.
"""

from __future__ import annotations

import numpy as np

from algorithms.scho import scho
from benchmarks.classic_23 import get_benchmark
from benchmarks.scho_scalability_h3 import (
    SCALABILITY_DIMS,
    SCALABILITY_FUNCTIONS,
    get_scalability_benchmark,
)


OPTIMIZER_SEED = 1000
F7_OBJECTIVE_SEED = 7000
SMOKE_N = 6
SMOKE_MAX_ITER = 20


def _same_bound(a, b) -> bool:
    return np.array_equal(np.asarray(a, dtype=float), np.asarray(b, dtype=float))


def metadata_and_formula_audit() -> None:
    print("Metadata/formula audit")
    print("-" * 118)

    for dim in SCALABILITY_DIMS:
        for name in SCALABILITY_FUNCTIONS:
            base = get_benchmark(name)
            high = get_scalability_benchmark(name, dim)

            if high.dim != dim:
                raise AssertionError(f"{name} D={dim}: dimension override failed")
            if high.func is not base.func:
                raise AssertionError(f"{name} D={dim}: formula callable changed")
            if high.stochastic != base.stochastic:
                raise AssertionError(f"{name} D={dim}: stochastic flag changed")
            if not _same_bound(high.lb, base.lb) or not _same_bound(high.ub, base.ub):
                raise AssertionError(f"{name} D={dim}: bounds changed")

            expected_opt = -418.9829 * dim if name == "F8" else base.optimum
            if high.optimum != expected_opt:
                raise AssertionError(
                    f"{name} D={dim}: optimum metadata {high.optimum} != {expected_opt}"
                )

            # For deterministic functions, compare direct evaluation on the same
            # dimension-valid vector.  This catches accidental formula wrappers.
            if not high.stochastic:
                x = np.linspace(-0.2, 0.2, dim, dtype=float)
                a = float(high.func(x))
                b = float(base.func(x))
                if a != b:
                    raise AssertionError(f"{name} D={dim}: formula evaluation changed")

        print(f"D={dim}: F1-F13 metadata/formulas PASS")


def f7_rng_audit() -> None:
    print("\nF7 objective-RNG audit")
    print("-" * 118)

    for dim in SCALABILITY_DIMS:
        b = get_scalability_benchmark("F7", dim)
        x = np.linspace(-0.1, 0.1, dim, dtype=float)

        obj1 = b.make_objective(seed=F7_OBJECTIVE_SEED + dim)
        obj2 = b.make_objective(seed=F7_OBJECTIVE_SEED + dim)
        seq1 = np.array([obj1(x) for _ in range(5)])
        seq2 = np.array([obj2(x) for _ in range(5)])

        if not np.array_equal(seq1, seq2):
            raise AssertionError(f"F7 D={dim}: same objective seed is not reproducible")
        if np.all(seq1 == seq1[0]):
            raise AssertionError(f"F7 D={dim}: stochastic noise was accidentally removed")

        print(f"F7 D={dim}: reproducible stochastic sequence PASS")


def run_scho_once(name: str, dim: int, objective_seed: int):
    b = get_scalability_benchmark(name, dim)
    obj = b.make_objective(seed=objective_seed)
    score, pos, curve = scho(
        obj_func=obj,
        dim=b.dim,
        lb=b.lb,
        ub=b.ub,
        N=SMOKE_N,
        MaxIter=SMOKE_MAX_ITER,
        seed=OPTIMIZER_SEED,
    )
    return float(score), np.asarray(pos, dtype=float), np.asarray(curve, dtype=float)


def scho_integration_audit() -> None:
    print("\nSource-faithful SCHO integration smoke test")
    print("-" * 118)
    print(
        f"Smoke only: N={SMOKE_N}, MaxIter={SMOKE_MAX_ITER}, "
        f"optimizer seed={OPTIMIZER_SEED}"
    )

    # F1: simple deterministic anchor.
    # F7: stochastic-objective anchor.
    # F13: penalized high-dimensional anchor.
    cases = ("F1", "F7", "F13")

    for dim in SCALABILITY_DIMS:
        for idx, name in enumerate(cases):
            objective_seed = F7_OBJECTIVE_SEED + dim + idx
            out1 = run_scho_once(name, dim, objective_seed)
            out2 = run_scho_once(name, dim, objective_seed)

            score1, pos1, curve1 = out1
            score2, pos2, curve2 = out2

            if not np.isfinite(score1):
                raise AssertionError(f"{name} D={dim}: non-finite best score")
            if pos1.shape != (dim,) or not np.all(np.isfinite(pos1)):
                raise AssertionError(f"{name} D={dim}: invalid best position")
            if curve1.shape != (SMOKE_MAX_ITER,) or not np.all(np.isfinite(curve1)):
                raise AssertionError(f"{name} D={dim}: invalid convergence curve")
            if np.any(np.diff(curve1) > 0):
                raise AssertionError(f"{name} D={dim}: historical best increased")
            if score1 != score2 or not np.array_equal(pos1, pos2) or not np.array_equal(curve1, curve2):
                raise AssertionError(f"{name} D={dim}: repeated seeded SCHO run changed")

            print(
                f"{name} D={dim}: final={score1:.12g} "
                f"shape={pos1.shape} reproducible PASS"
            )


def invalid_input_audit() -> None:
    print("\nInvalid-input guard audit")
    print("-" * 118)

    for name, dim in [("F14", 100), ("F1", 30), ("F23", 500)]:
        try:
            get_scalability_benchmark(name, dim)
        except ValueError:
            print(f"{name} D={dim}: rejected PASS")
        else:
            raise AssertionError(f"Invalid H3 request unexpectedly accepted: {name}, D={dim}")


def main() -> None:
    print("=" * 118)
    print("H3b - SCHO scalability F1-F13 D=100/D=500 adapter + integration audit")
    print("=" * 118)
    print("No formal 30-run scalability experiment will be executed.")
    print("Frozen algorithms/scho.py and benchmarks/classic_23.py are not modified.")
    print("=" * 118)

    metadata_and_formula_audit()
    f7_rng_audit()
    scho_integration_audit()
    invalid_input_audit()

    print("\n" + "-" * 118)
    print("H3b RESULT: PASS")
    print("F1-F13 dimension override is validated for D=100 and D=500.")
    print("Source-faithful SCHO integrates reproducibly with deterministic and stochastic anchors.")
    print("Next: H3c formal SCHO scalability run (780 optimizer runs) with checkpoint/resume.")


if __name__ == "__main__":
    main()
