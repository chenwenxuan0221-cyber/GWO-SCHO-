"""H5d unified-interface / protocol compatibility audit for SCHO Section 3.1.3.

Purpose
-------
Structural smoke test only. This script does NOT perform the formal 30-run
comparison and does NOT modify any optimizer implementation.

Algorithms
----------
SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO (Sea-Horse Optimizer), GJO

Representative functions
------------------------
F2  : scalar bounds
F7  : noisy objective / objective-RNG determinism
F17 : vector bounds
F21 : negative optimum / reciprocal-roulette stress case

Protocol
--------
N = 6
MaxIter = 40
optimizer seed = 1000

Objective RNG:
A fresh objective object is reconstructed for every optimizer run.
For this H5d structural audit we retain the H5c7-style deterministic schedule

    OBJ_BASE + function_number

with OBJ_BASE = 5_037_000.

This schedule is ONLY an H5d audit convention at this stage; it is not yet
declared to be the final H5 formal-run objective-seed schedule.

Exactness boundaries
--------------------
- algorithms/gwo.py and algorithms/scho.py are frozen and must not be edited.
- SHO means Sea-Horse Optimizer, imported from algorithms.sea_horse.
- NumPy RNG is used; no MATLAB bitwise RNG equivalence is claimed.
- Source quirks are preserved.
- Curve monotonicity is NOT imposed as a universal assertion because several
  source-structured implementations intentionally preserve curve[0] quirks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from algorithms.gwo import gwo
from algorithms.scho import scho
from algorithms.alo import alo
from algorithms.sca import sca
from algorithms.ssa import ssa
from algorithms.aoa import aoa
from algorithms.rsa import rsa
from algorithms.sea_horse import sho
from algorithms.gjo import gjo
from benchmarks.classic_23 import get_benchmark


N = 6
MAX_ITER = 40
OPTIMIZER_SEED = 1000
OBJ_BASE = 5_037_000

FUNCTIONS = ("F2", "F7", "F17", "F21")


@dataclass(frozen=True)
class AlgorithmSpec:
    name: str
    func: Callable


ALGORITHMS = (
    AlgorithmSpec("SCHO", scho),
    AlgorithmSpec("GWO", gwo),
    AlgorithmSpec("ALO", alo),
    AlgorithmSpec("SCA", sca),
    AlgorithmSpec("SSA", ssa),
    AlgorithmSpec("AOA", aoa),
    AlgorithmSpec("RSA", rsa),
    AlgorithmSpec("SHO", sho),
    AlgorithmSpec("GJO", gjo),
)


def objective_seed(function_name: str) -> int:
    return OBJ_BASE + int(function_name[1:])


def run_once(spec: AlgorithmSpec, function_name: str):
    b = get_benchmark(function_name)
    obj = b.make_objective(seed=objective_seed(function_name))

    result = spec.func(
        obj,
        b.dim,
        b.lb,
        b.ub,
        N,
        MAX_ITER,
        seed=OPTIMIZER_SEED,
    )

    assert isinstance(result, tuple), (
        f"{spec.name}/{function_name}: result is not a tuple"
    )
    assert len(result) == 3, (
        f"{spec.name}/{function_name}: expected 3 return values, got {len(result)}"
    )

    score, pos, curve = result
    score = float(score)
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    return b, score, pos, curve


def validate_structure(
    spec: AlgorithmSpec,
    function_name: str,
    b,
    score: float,
    pos: np.ndarray,
    curve: np.ndarray,
) -> None:
    assert np.isfinite(score), (
        f"{spec.name}/{function_name}: non-finite score"
    )

    assert pos.shape == (b.dim,), (
        f"{spec.name}/{function_name}: position shape {pos.shape}, "
        f"expected {(b.dim,)}"
    )
    assert np.all(np.isfinite(pos)), (
        f"{spec.name}/{function_name}: non-finite position"
    )

    assert curve.shape == (MAX_ITER,), (
        f"{spec.name}/{function_name}: curve shape {curve.shape}, "
        f"expected {(MAX_ITER,)}"
    )
    assert np.all(np.isfinite(curve)), (
        f"{spec.name}/{function_name}: non-finite curve"
    )


def validate_determinism(
    spec: AlgorithmSpec,
    function_name: str,
    first,
    second,
) -> None:
    _, score1, pos1, curve1 = first
    _, score2, pos2, curve2 = second

    assert score1 == score2, (
        f"{spec.name}/{function_name}: score is not deterministic"
    )
    assert np.array_equal(pos1, pos2), (
        f"{spec.name}/{function_name}: position is not deterministic"
    )
    assert np.array_equal(curve1, curve2), (
        f"{spec.name}/{function_name}: curve is not deterministic"
    )


def bound_kind(b) -> str:
    lb = np.asarray(b.lb)
    ub = np.asarray(b.ub)
    scalar_like = lb.ndim == 0 and ub.ndim == 0
    return "scalar" if scalar_like else "vector"


def main() -> None:
    print("=" * 132)
    print("H5d - nine-algorithm unified-interface / protocol compatibility audit")
    print("=" * 132)
    print(
        "Algorithms: SCHO,GWO,ALO,SCA,SSA,AOA,RSA,SHO,GJO | "
        f"N={N} | MaxIter={MAX_ITER} | optimizer seed={OPTIMIZER_SEED}"
    )
    print(
        f"Objective seed schedule for this structural audit: "
        f"{OBJ_BASE} + function number"
    )
    print(
        "IMPORTANT: SHO = Sea-Horse Optimizer (algorithms.sea_horse), "
        "NOT Spotted Hyena Optimizer."
    )
    print(
        "No formal 30-run comparison is executed. "
        "Frozen GWO/SCHO are not modified."
    )
    print("=" * 132)

    total = 0

    for function_name in FUNCTIONS:
        b = get_benchmark(function_name)

        print()
        print(
            f"{function_name}: D={b.dim} | bounds={bound_kind(b)} | "
            f"objective_seed={objective_seed(function_name)}"
        )

        for spec in ALGORITHMS:
            first = run_once(spec, function_name)
            second = run_once(spec, function_name)

            validate_structure(
                spec,
                function_name,
                first[0],
                first[1],
                first[2],
                first[3],
            )
            validate_determinism(spec, function_name, first, second)

            _, score, pos, curve = first

            print(
                f"  {spec.name:<4} "
                f"score={score: .10e} "
                f"pos={str(pos.shape):<7} "
                f"curve={str(curve.shape):<7} "
                f"finite=PASS deterministic=PASS"
            )
            total += 1

    print()
    print("-" * 132)
    print(f"H5d RESULT: PASS ({total}/{len(ALGORITHMS) * len(FUNCTIONS)} algorithm-function smoke cases)")
    print(
        "Unified callable/return interface, scalar bounds, vector bounds, "
        "noisy-objective reproducibility, and negative-fitness compatibility "
        "are structurally covered."
    )
    print(
        "No universal convergence-curve monotonicity assertion is imposed; "
        "source quirks such as curve[0]=0 remain untouched."
    )
    print(
        "Next after PASS: freeze the H5 formal-run objective-seed schedule, "
        "checkpoint schema, reuse rules for existing SCHO/GWO rows, and then "
        "build the formal H5 runner."
    )
    print("=" * 132)


if __name__ == "__main__":
    main()
