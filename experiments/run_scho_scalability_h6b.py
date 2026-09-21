"""H6b formal runner for SCHO Section 3.1.4 full scalability comparison.

Protocol
--------
Protocol ID : H6_SCALABILITY_V1
Algorithms  : SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO
Functions   : F1-F13
Dimensions  : D=100, D=500
Population  : 30
MaxIter     : 500
Runs        : 30 per algorithm/function/dimension

Full dataset:
    9 * 13 * 2 * 30 = 7020 rows

Reuse:
    Existing H3c SCHO rows = 780

New work:
    8 * 13 * 2 * 30 = 6240 optimizer runs

The runner is checkpointed and resumable. Frozen optimizer implementations
are never modified.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

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

ALGORITHM_ORDER = (
    "SCHO",
    "GWO",
    "ALO",
    "SCA",
    "SSA",
    "AOA",
    "RSA",
    "SHO",
    "GJO",
)

FUNCTIONS = tuple(SCALABILITY_FUNCTIONS)
DIMS = tuple(SCALABILITY_DIMS)

N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_OPTIMIZER_SEED = 1000

PROJECT_ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_SCHO_RAW = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "scho_scalability_h3c_runs.csv"
)

CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "scho_scalability_h6b_checkpoint.jsonl"
)

FINAL_RAW_PATH = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "scho_scalability_h6b_runs.csv"
)

PER_ALGORITHM = len(FUNCTIONS) * len(DIMS) * N_RUNS
EXPECTED_TOTAL = len(ALGORITHM_ORDER) * PER_ALGORITHM
EXPECTED_REUSED_SCHO = PER_ALGORITHM
EXPECTED_NEW = EXPECTED_TOTAL - EXPECTED_REUSED_SCHO


ALGORITHM_FUNCS = {
    "SCHO": scho,
    "GWO": gwo,
    "ALO": alo,
    "SCA": sca,
    "SSA": ssa,
    "AOA": aoa,
    "RSA": rsa,
    "SHO": sho,
    "GJO": gjo,
}


def function_number(name: str) -> int:
    if not name.startswith("F"):
        raise ValueError(f"Invalid function name: {name}")

    n = int(name[1:])

    if not 1 <= n <= 13:
        raise ValueError(f"Function outside F1-F13: {name}")

    return n


def optimizer_seed(run: int) -> int:
    return BASE_OPTIMIZER_SEED + run - 1


def formal_objective_seed(
    function_name: str,
    dim: int,
    run: int,
) -> int:
    return (
        7_000_000
        + dim * 10_000
        + function_number(function_name) * 100
        + run
    )


def is_stochastic(function_name: str) -> bool:
    return function_name == "F7"


def key_of(
    row: dict[str, Any],
) -> tuple[str, str, int, int]:
    return (
        str(row["Algorithm"]),
        str(row["Function"]),
        int(row["Dim"]),
        int(row["Run"]),
    )


def jsonable_float(value: Any) -> float:
    out = float(value)

    if not math.isfinite(out):
        raise RuntimeError(
            f"Non-finite numeric value: {value!r}"
        )

    return out


def validate_common_metadata(
    row: dict[str, Any],
) -> None:
    if row.get("ProtocolID") != PROTOCOL_ID:
        raise RuntimeError(
            f"Protocol mismatch for {key_of(row)}: "
            f"{row.get('ProtocolID')!r}"
        )

    algorithm = str(row["Algorithm"])
    function_name = str(row["Function"])
    dim = int(row["Dim"])
    run = int(row["Run"])

    if algorithm not in ALGORITHM_ORDER:
        raise RuntimeError(
            f"Unknown algorithm: {algorithm}"
        )

    if function_name not in FUNCTIONS:
        raise RuntimeError(
            f"Unknown function: {function_name}"
        )

    if dim not in DIMS:
        raise RuntimeError(
            f"Unknown dimension: {dim}"
        )

    if not 1 <= run <= N_RUNS:
        raise RuntimeError(
            f"Invalid run number: {run}"
        )

    if int(row["OptimizerSeed"]) != optimizer_seed(run):
        raise RuntimeError(
            f"Optimizer seed mismatch for {key_of(row)}"
        )

    expected_obj_seed = formal_objective_seed(
        function_name,
        dim,
        run,
    )

    if int(row["FormalObjectiveSeed"]) != expected_obj_seed:
        raise RuntimeError(
            f"Formal objective seed mismatch "
            f"for {key_of(row)}"
        )

    if int(row["ObjectiveSeed"]) != expected_obj_seed:
        raise RuntimeError(
            f"Executed objective seed mismatch "
            f"for {key_of(row)}"
        )

    if int(row["Population"]) != N:
        raise RuntimeError(
            f"Population mismatch for {key_of(row)}"
        )

    if int(row["MaxIter"]) != MAX_ITER:
        raise RuntimeError(
            f"MaxIter mismatch for {key_of(row)}"
        )

    score = float(row["BestScore"])

    if not math.isfinite(score):
        raise RuntimeError(
            f"Non-finite BestScore for {key_of(row)}"
        )

    expected_role = (
        "ACTIVE_STOCHASTIC_F7"
        if is_stochastic(function_name)
        else "IGNORED_DETERMINISTIC"
    )

    if str(row["ObjectiveSeedRole"]) != expected_role:
        raise RuntimeError(
            f"Objective-seed role mismatch "
            f"for {key_of(row)}"
        )

    provenance = str(row["Provenance"])

    if provenance == "REUSED_SCHO_H3C":
        if algorithm != "SCHO":
            raise RuntimeError(
                f"Illegal H3c reuse for {key_of(row)}"
            )

    elif provenance == "H6_NEW_RUN":
        if algorithm == "SCHO":
            raise RuntimeError(
                f"Unexpected new SCHO run for {key_of(row)}"
            )

    else:
        raise RuntimeError(
            f"Unknown provenance for {key_of(row)}: "
            f"{provenance!r}"
        )


def load_checkpoint() -> dict[
    tuple[str, str, int, int],
    dict[str, Any],
]:
    rows: dict[
        tuple[str, str, int, int],
        dict[str, Any],
    ] = {}

    if not CHECKPOINT_PATH.exists():
        return rows

    with CHECKPOINT_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL at "
                    f"{CHECKPOINT_PATH}:{lineno}"
                ) from exc

            validate_common_metadata(row)
            key = key_of(row)

            if key in rows:
                raise RuntimeError(
                    f"Duplicate checkpoint key "
                    f"at line {lineno}: {key}"
                )

            rows[key] = row

    return rows


def append_checkpoint(
    row: dict[str, Any],
) -> None:
    CHECKPOINT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with CHECKPOINT_PATH.open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(
            json.dumps(
                row,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def load_historical_scho_rows() -> list[
    dict[str, Any]
]:
    if not HISTORICAL_SCHO_RAW.exists():
        raise FileNotFoundError(
            f"H3c SCHO raw file not found: "
            f"{HISTORICAL_SCHO_RAW}"
        )

    with HISTORICAL_SCHO_RAW.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        reader = csv.DictReader(f)

        required = {
            "Function",
            "Dimension",
            "Run",
            "OptimizerSeed",
            "ObjectiveSeed",
            "Population",
            "MaxIter",
            "BestScore",
            "Status",
        }

        if (
            reader.fieldnames is None
            or not required.issubset(reader.fieldnames)
        ):
            raise RuntimeError(
                f"Unexpected H3c columns: "
                f"{reader.fieldnames}"
            )

        source_rows = list(reader)

    if len(source_rows) != EXPECTED_REUSED_SCHO:
        raise RuntimeError(
            f"H3c SCHO raw row count="
            f"{len(source_rows)}; "
            f"expected {EXPECTED_REUSED_SCHO}"
        )

    seen: set[
        tuple[str, int, int]
    ] = set()

    reusable: list[
        dict[str, Any]
    ] = []

    for src in source_rows:
        function_name = str(src["Function"])
        dim = int(src["Dimension"])
        run = int(src["Run"])

        pair = (
            function_name,
            dim,
            run,
        )

        if function_name not in FUNCTIONS:
            raise RuntimeError(
                f"Unexpected H3c function: "
                f"{function_name}"
            )

        if dim not in DIMS:
            raise RuntimeError(
                f"Unexpected H3c dimension: {dim}"
            )

        if not 1 <= run <= N_RUNS:
            raise RuntimeError(
                f"Unexpected H3c run: {pair}"
            )

        if pair in seen:
            raise RuntimeError(
                f"Duplicate H3c key: {pair}"
            )

        seen.add(pair)

        opt_seed = optimizer_seed(run)
        obj_seed = formal_objective_seed(
            function_name,
            dim,
            run,
        )

        if int(src["OptimizerSeed"]) != opt_seed:
            raise RuntimeError(
                f"H3c optimizer seed mismatch: {pair}"
            )

        if int(src["ObjectiveSeed"]) != obj_seed:
            raise RuntimeError(
                f"H3c objective seed mismatch: {pair}"
            )

        if int(src["Population"]) != N:
            raise RuntimeError(
                f"H3c population mismatch: {pair}"
            )

        if int(src["MaxIter"]) != MAX_ITER:
            raise RuntimeError(
                f"H3c MaxIter mismatch: {pair}"
            )

        if str(src["Status"]) != "PASS":
            raise RuntimeError(
                f"H3c status mismatch: {pair}"
            )

        score = jsonable_float(
            src["BestScore"]
        )

        row = {
            "ProtocolID": PROTOCOL_ID,
            "Algorithm": "SCHO",
            "Function": function_name,
            "Dim": dim,
            "Run": run,
            "OptimizerSeed": opt_seed,
            "ObjectiveSeed": obj_seed,
            "FormalObjectiveSeed": obj_seed,
            "ObjectiveSeedRole": (
                "ACTIVE_STOCHASTIC_F7"
                if is_stochastic(function_name)
                else "IGNORED_DETERMINISTIC"
            ),
            "Population": N,
            "MaxIter": MAX_ITER,
            "BestScore": score,
            "BestPositionJSON": "",
            "PositionAvailable": False,
            "RuntimeSeconds": (
                float(src["ElapsedSeconds"])
                if src.get("ElapsedSeconds")
                not in (None, "")
                else None
            ),
            "Provenance": "REUSED_SCHO_H3C",
            "SourcePath": str(
                HISTORICAL_SCHO_RAW.relative_to(
                    PROJECT_ROOT
                )
            ).replace("\\", "/"),
        }

        validate_common_metadata(row)
        reusable.append(row)

    if len(seen) != EXPECTED_REUSED_SCHO:
        raise RuntimeError(
            f"H3c unique keys={len(seen)}; "
            f"expected {EXPECTED_REUSED_SCHO}"
        )

    return reusable


def bootstrap_reuse(
    completed: dict[
        tuple[str, str, int, int],
        dict[str, Any],
    ],
) -> int:
    historical = load_historical_scho_rows()
    added = 0

    for row in historical:
        key = key_of(row)

        if key in completed:
            existing = completed[key]

            if (
                existing["Provenance"]
                != "REUSED_SCHO_H3C"
            ):
                raise RuntimeError(
                    f"Reuse key occupied by "
                    f"non-reuse row: {key}"
                )

            continue

        append_checkpoint(row)
        completed[key] = row
        added += 1

    return added


def all_required_keys() -> list[
    tuple[str, str, int, int]
]:
    return [
        (
            algorithm,
            function_name,
            dim,
            run,
        )
        for algorithm in ALGORITHM_ORDER
        for dim in DIMS
        for function_name in FUNCTIONS
        for run in range(1, N_RUNS + 1)
    ]


def build_pending(
    completed: dict[
        tuple[str, str, int, int],
        dict[str, Any],
    ],
) -> list[
    tuple[str, str, int, int]
]:
    return [
        key
        for key in all_required_keys()
        if key not in completed
    ]


def run_one(
    task: tuple[str, str, int, int],
) -> dict[str, Any]:
    algorithm, function_name, dim, run = task

    if algorithm == "SCHO":
        raise RuntimeError(
            "H6b must reuse H3c SCHO rows; "
            "new SCHO execution is not allowed."
        )

    b = get_scalability_benchmark(
        function_name,
        dim,
    )

    opt_seed = optimizer_seed(run)
    obj_seed = formal_objective_seed(
        function_name,
        dim,
        run,
    )

    objective = b.make_objective(
        seed=obj_seed
    )

    optimizer = ALGORITHM_FUNCS[algorithm]

    start = time.perf_counter()

    if algorithm == "AOA":
        score, best_pos, curve = optimizer(
            objective,
            b.dim,
            b.lb,
            b.ub,
            N,
            MAX_ITER,
            seed=opt_seed,
            mu=0.5,
        )
    else:
        score, best_pos, curve = optimizer(
            objective,
            b.dim,
            b.lb,
            b.ub,
            N,
            MAX_ITER,
            seed=opt_seed,
        )

    elapsed = time.perf_counter() - start

    score = jsonable_float(score)
    best_pos = np.asarray(
        best_pos,
        dtype=float,
    )
    curve = np.asarray(
        curve,
        dtype=float,
    )

    if best_pos.shape != (b.dim,):
        raise RuntimeError(
            f"{algorithm}/{function_name}/"
            f"D={dim}/run{run}: "
            f"best_pos shape={best_pos.shape}, "
            f"expected {(b.dim,)}"
        )

    if not np.all(np.isfinite(best_pos)):
        raise RuntimeError(
            f"{algorithm}/{function_name}/"
            f"D={dim}/run{run}: "
            "non-finite best position"
        )

    if curve.shape != (MAX_ITER,):
        raise RuntimeError(
            f"{algorithm}/{function_name}/"
            f"D={dim}/run{run}: "
            f"curve shape={curve.shape}, "
            f"expected {(MAX_ITER,)}"
        )

    if not np.all(np.isfinite(curve)):
        raise RuntimeError(
            f"{algorithm}/{function_name}/"
            f"D={dim}/run{run}: "
            "non-finite curve"
        )

    row = {
        "ProtocolID": PROTOCOL_ID,
        "Algorithm": algorithm,
        "Function": function_name,
        "Dim": dim,
        "Run": run,
        "OptimizerSeed": opt_seed,
        "ObjectiveSeed": obj_seed,
        "FormalObjectiveSeed": obj_seed,
        "ObjectiveSeedRole": (
            "ACTIVE_STOCHASTIC_F7"
            if is_stochastic(function_name)
            else "IGNORED_DETERMINISTIC"
        ),
        "Population": N,
        "MaxIter": MAX_ITER,
        "BestScore": score,
        "BestPositionJSON": json.dumps(
            best_pos.tolist(),
            separators=(",", ":"),
        ),
        "PositionAvailable": True,
        "RuntimeSeconds": float(elapsed),
        "Provenance": "H6_NEW_RUN",
        "SourcePath": "",
    }

    validate_common_metadata(row)

    return row


def count_by_algorithm(
    rows: dict[
        tuple[str, str, int, int],
        dict[str, Any],
    ],
) -> dict[str, int]:
    return {
        alg: sum(
            1
            for (a, _f, _d, _r) in rows
            if a == alg
        )
        for alg in ALGORITHM_ORDER
    }


def print_audit(
    completed: dict[
        tuple[str, str, int, int],
        dict[str, Any],
    ],
    pending: list[
        tuple[str, str, int, int]
    ],
    added_reuse: int,
) -> None:
    print("=" * 120)
    print(
        "H6b - formal Section 3.1.4 "
        "nine-algorithm scalability runner audit"
    )
    print("=" * 120)

    print(
        f"Protocol             : {PROTOCOL_ID}"
    )
    print(
        f"Functions / Dims     : "
        f"F1-F13 / {DIMS}"
    )
    print(
        f"N / MaxIter          : "
        f"{N} / {MAX_ITER}"
    )
    print(
        f"Optimizer seeds      : "
        f"{BASE_OPTIMIZER_SEED}.."
        f"{BASE_OPTIMIZER_SEED + N_RUNS - 1}"
    )
    print(
        "Objective seed rule  : "
        "7_000_000 + D*10_000 + "
        "100*function_number + run"
    )
    print(
        f"Checkpoint           : "
        f"{CHECKPOINT_PATH}"
    )
    print(
        f"Final raw CSV        : "
        f"{FINAL_RAW_PATH}"
    )
    print(
        f"Expected final rows  : "
        f"{EXPECTED_TOTAL}"
    )
    print(
        f"Expected reuse rows  : "
        f"{EXPECTED_REUSED_SCHO}"
    )
    print(
        f"Expected new runs    : "
        f"{EXPECTED_NEW}"
    )
    print(
        f"Reuse rows added now : "
        f"{added_reuse}"
    )
    print(
        f"Completed/checkpoint : "
        f"{len(completed)}"
    )
    print(
        f"Pending              : "
        f"{len(pending)}"
    )

    print("-" * 120)

    counts = count_by_algorithm(completed)

    for alg in ALGORITHM_ORDER:
        print(
            f"{alg:<4}: "
            f"completed="
            f"{counts[alg]:>3}/{PER_ALGORITHM}  "
            f"pending="
            f"{PER_ALGORITHM - counts[alg]:>3}"
        )

    print("-" * 120)

    reuse_count = sum(
        1
        for row in completed.values()
        if row["Provenance"]
        == "REUSED_SCHO_H3C"
    )

    new_count = sum(
        1
        for row in completed.values()
        if row["Provenance"]
        == "H6_NEW_RUN"
    )

    print(
        f"Provenance: "
        f"reused_scho_h3c={reuse_count}, "
        f"h6_new_run={new_count}"
    )

    f7_completed = sum(
        1
        for (_a, f, _d, _r) in completed
        if f == "F7"
    )

    print(
        f"F7 completed         : "
        f"{f7_completed}/"
        f"{len(ALGORITHM_ORDER) * len(DIMS) * N_RUNS}"
    )

    print("=" * 120)


def write_final_csv(
    completed: dict[
        tuple[str, str, int, int],
        dict[str, Any],
    ],
) -> None:
    if len(completed) != EXPECTED_TOTAL:
        raise RuntimeError(
            f"Cannot write final CSV: "
            f"completed={len(completed)}, "
            f"expected={EXPECTED_TOTAL}"
        )

    required = set(all_required_keys())
    actual = set(completed)

    missing = required - actual
    extra = actual - required

    if missing or extra:
        raise RuntimeError(
            f"Final key mismatch: "
            f"missing={len(missing)}, "
            f"extra={len(extra)}"
        )

    for row in completed.values():
        validate_common_metadata(row)

    FINAL_RAW_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "ProtocolID",
        "Algorithm",
        "Function",
        "Dim",
        "Run",
        "OptimizerSeed",
        "ObjectiveSeed",
        "FormalObjectiveSeed",
        "ObjectiveSeedRole",
        "Population",
        "MaxIter",
        "BestScore",
        "BestPositionJSON",
        "PositionAvailable",
        "RuntimeSeconds",
        "Provenance",
        "SourcePath",
    ]

    alg_index = {
        name: idx
        for idx, name
        in enumerate(ALGORITHM_ORDER)
    }

    dim_index = {
        dim: idx
        for idx, dim
        in enumerate(DIMS)
    }

    rows = sorted(
        completed.values(),
        key=lambda r: (
            alg_index[str(r["Algorithm"])],
            dim_index[int(r["Dim"])],
            function_number(
                str(r["Function"])
            ),
            int(r["Run"]),
        ),
    )

    with FINAL_RAW_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fields,
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "H6b formal SCHO Section 3.1.4 "
            "nine-algorithm scalability runner "
            "with checkpoint/resume."
        )
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help=(
            "ProcessPoolExecutor worker count "
            "(default: 4)."
        ),
    )

    parser.add_argument(
        "--audit-only",
        action="store_true",
        help=(
            "Validate/bootstrap H3c SCHO reuse "
            "and print workload without executing "
            "new optimizer runs."
        ),
    )

    parser.add_argument(
        "--max-new-runs",
        type=int,
        default=None,
        help=(
            "Optional cap on new comparator runs "
            "for controlled testing. "
            "Checkpoint/resume remains valid."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.workers < 1:
        raise ValueError(
            "--workers must be >= 1"
        )

    if (
        args.max_new_runs is not None
        and args.max_new_runs < 1
    ):
        raise ValueError(
            "--max-new-runs must be >= 1"
        )

    CHECKPOINT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    completed = load_checkpoint()

    added_reuse = bootstrap_reuse(
        completed
    )

    pending = build_pending(
        completed
    )

    print_audit(
        completed,
        pending,
        added_reuse,
    )

    if args.audit_only:
        print(
            "H6b AUDIT-ONLY RESULT: PASS"
        )
        print(
            "No new comparator optimizer "
            "run was executed."
        )
        return

    tasks = pending

    if args.max_new_runs is not None:
        tasks = tasks[
            : args.max_new_runs
        ]

    if not tasks:
        if len(completed) == EXPECTED_TOTAL:
            write_final_csv(completed)

            print(
                "H6b RESULT: COMPLETE"
            )
            print(
                f"Saved final raw dataset to: "
                f"{FINAL_RAW_PATH}"
            )
        else:
            print(
                "No tasks selected, but the "
                "full dataset is incomplete."
            )

        return

    print()
    print(
        f"Executing {len(tasks)} new runs "
        f"with {args.workers} worker(s)..."
    )
    print(
        "Each completed run is checkpointed "
        "immediately by the main process."
    )
    print()

    started = time.perf_counter()
    completed_this_invocation = 0

    with ProcessPoolExecutor(
        max_workers=args.workers
    ) as executor:
        future_to_task = {
            executor.submit(
                run_one,
                task,
            ): task
            for task in tasks
        }

        for future in as_completed(
            future_to_task
        ):
            task = future_to_task[future]

            try:
                row = future.result()
            except Exception as exc:
                raise RuntimeError(
                    f"H6b worker failed "
                    f"for task={task}"
                ) from exc

            key = key_of(row)

            if key in completed:
                raise RuntimeError(
                    f"Worker returned already-"
                    f"completed key: {key}"
                )

            append_checkpoint(row)
            completed[key] = row
            completed_this_invocation += 1

            total_done = len(completed)
            elapsed = (
                time.perf_counter()
                - started
            )

            if (
                completed_this_invocation <= 10
                or completed_this_invocation % 10 == 0
                or completed_this_invocation
                == len(tasks)
            ):
                print(
                    f"[{completed_this_invocation:>4}/"
                    f"{len(tasks)} this call] "
                    f"[{total_done:>4}/"
                    f"{EXPECTED_TOTAL} total] "
                    f"{row['Algorithm']}/"
                    f"{row['Function']}/"
                    f"D={row['Dim']}/"
                    f"run{row['Run']:02d} "
                    f"best="
                    f"{float(row['BestScore']):.10e} "
                    f"elapsed={elapsed:.1f}s"
                )

    print()

    remaining = build_pending(
        completed
    )

    print("-" * 120)

    print(
        f"Completed this invocation: "
        f"{completed_this_invocation}"
    )
    print(
        f"Total completed         : "
        f"{len(completed)}/"
        f"{EXPECTED_TOTAL}"
    )
    print(
        f"Remaining               : "
        f"{len(remaining)}"
    )

    if remaining:
        print(
            "H6b RESULT: PARTIAL_CHECKPOINTED"
        )
        print(
            "Re-run the same command to resume "
            "from the existing checkpoint."
        )
        return

    write_final_csv(completed)

    print(
        "H6b RESULT: COMPLETE"
    )
    print(
        f"Final rows: {len(completed)}"
    )
    print(
        f"Saved final raw dataset to: "
        f"{FINAL_RAW_PATH}"
    )
    print(
        "Next: H6c Tables 9/10 "
        "Best/Mean/sample-STD/Friedman ranking."
    )
    print("=" * 120)


if __name__ == "__main__":
    main()
