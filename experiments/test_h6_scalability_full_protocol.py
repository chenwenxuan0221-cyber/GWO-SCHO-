"""H6a structural/protocol smoke for Section 3.1.4 full comparison."""

from __future__ import annotations

import csv
from pathlib import Path
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

from benchmarks.scho_scalability_h3 import (
    SCALABILITY_DIMS,
    SCALABILITY_FUNCTIONS,
    get_scalability_benchmark,
)

PROTOCOL_ID = "H6_SCALABILITY_V1"

FORMAL_N = 30
FORMAL_MAX_ITER = 500
FORMAL_RUNS = 30
BASE_OPTIMIZER_SEED = 1000

SMOKE_N = 6
SMOKE_MAX_ITER = 12
SMOKE_RUN = 1

PROJECT_ROOT = Path(__file__).resolve().parents[1]
H3_RAW = PROJECT_ROOT / "results" / "raw" / "scho_scalability_h3c_runs.csv"

ALGORITHMS: tuple[tuple[str, Callable], ...] = (
    ("SCHO", scho),
    ("GWO", gwo),
    ("ALO", alo),
    ("SCA", sca),
    ("SSA", ssa),
    ("AOA", aoa),
    ("RSA", rsa),
    ("SHO", sho),
    ("GJO", gjo),
)


def optimizer_seed(run: int) -> int:
    return BASE_OPTIMIZER_SEED + run - 1


def objective_seed(function_name: str, dim: int, run: int) -> int:
    fnum = int(function_name[1:])
    return 7_000_000 + dim * 10_000 + fnum * 100 + run


def validate_h3_reuse() -> None:
    with H3_RAW.open("r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    expected_keys = {
        (function_name, dim, run)
        for dim in SCALABILITY_DIMS
        for function_name in SCALABILITY_FUNCTIONS
        for run in range(1, FORMAL_RUNS + 1)
    }

    assert len(rows) == 780, f"H3 raw row count != 780: {len(rows)}"

    seen = set()

    for row in rows:
        function_name = row["Function"]
        dim = int(row["Dimension"])
        run = int(row["Run"])
        key = (function_name, dim, run)

        assert key in expected_keys, f"Unexpected H3 key: {key}"
        assert key not in seen, f"Duplicate H3 key: {key}"
        seen.add(key)

        assert int(row["OptimizerSeed"]) == optimizer_seed(run)
        assert int(row["ObjectiveSeed"]) == objective_seed(
            function_name, dim, run
        )
        assert int(row["Population"]) == FORMAL_N
        assert int(row["MaxIter"]) == FORMAL_MAX_ITER
        assert row["Status"] == "PASS"
        assert np.isfinite(float(row["BestScore"]))

    assert seen == expected_keys

    print("H3 reuse validation: PASS (780/780 rows)")


def run_once(
    algorithm_name: str,
    optimizer: Callable,
    function_name: str,
    dim: int,
):
    b = get_scalability_benchmark(function_name, dim)

    opt_seed = optimizer_seed(SMOKE_RUN)
    obj_seed = objective_seed(function_name, dim, SMOKE_RUN)
    objective = b.make_objective(seed=obj_seed)

    if algorithm_name == "AOA":
        result = optimizer(
            objective,
            b.dim,
            b.lb,
            b.ub,
            SMOKE_N,
            SMOKE_MAX_ITER,
            seed=opt_seed,
            mu=0.5,
        )
    else:
        result = optimizer(
            objective,
            b.dim,
            b.lb,
            b.ub,
            SMOKE_N,
            SMOKE_MAX_ITER,
            seed=opt_seed,
        )

    assert isinstance(result, tuple)
    assert len(result) == 3

    score, pos, curve = result

    score = float(score)
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    assert np.isfinite(score)
    assert pos.shape == (dim,)
    assert np.all(np.isfinite(pos))
    assert curve.shape == (SMOKE_MAX_ITER,)
    assert np.all(np.isfinite(curve))

    return score, pos, curve


def validate_algorithm_smoke() -> None:
    cases = (
        ("F2", 100),
        ("F7", 500),
    )

    total = 0

    for function_name, dim in cases:
        print()
        print(
            f"Case {function_name} D={dim} | "
            f"optimizer_seed={optimizer_seed(SMOKE_RUN)} | "
            f"objective_seed={objective_seed(function_name, dim, SMOKE_RUN)}"
        )

        for algorithm_name, optimizer in ALGORITHMS:
            first = run_once(
                algorithm_name,
                optimizer,
                function_name,
                dim,
            )

            second = run_once(
                algorithm_name,
                optimizer,
                function_name,
                dim,
            )

            score1, pos1, curve1 = first
            score2, pos2, curve2 = second

            assert score1 == score2
            assert np.array_equal(pos1, pos2)
            assert np.array_equal(curve1, curve2)

            total += 1

            print(
                f"  PASS {algorithm_name:4s} "
                f"score={score1:.10g}"
            )

    expected = len(cases) * len(ALGORITHMS)

    assert total == expected

    print()
    print(f"Algorithm smoke: PASS ({total}/{expected} cases)")


def main() -> None:
    print("=" * 100)
    print("H6a - full scalability comparison structural/protocol smoke")
    print(f"Protocol: {PROTOCOL_ID}")
    print("Formal matrix: 9 x 13 x 2 x 30 = 7020 rows")
    print("Reuse: SCHO H3c = 780 rows | New comparator work = 6240 runs")
    print("=" * 100)

    validate_h3_reuse()
    validate_algorithm_smoke()

    print()
    print("=" * 100)
    print("H6a RESULT: PASS")
    print("No formal comparator experiment was launched.")
    print("=" * 100)


if __name__ == "__main__":
    main()
