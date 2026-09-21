"""H5e formal runner for SCHO Section 3.1.3 classical 9-algorithm comparison.

This runner implements the frozen H5_CLASSICAL_V1 project-controlled protocol.

Formal scope
------------
Algorithms:
    SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO

Benchmarks:
    F1-F13 : D=30
    F14-F23: native dimensions from benchmarks.classic_23

Protocol:
    N=30
    MaxIter=500
    30 independent runs
    optimizer seeds = 1000..1029

Formal objective-seed schedule:
    objective_seed = 5_024_000 + 100 * function_number + run

The objective RNG is reconstructed separately for every algorithm/function/run.
For the stochastic F7 this is an active benchmark-noise RNG. For deterministic
functions the benchmark seed is recorded for protocol bookkeeping but has no
numerical effect.

Reuse rule
----------
Historical SCHO C12 raw rows are reused only for deterministic functions:
    F1-F6, F8-F23  -> 660 rows

Historical SCHO F7 is NOT reused because H5_CLASSICAL_V1 uses the new formal
objective-seed schedule.

No complete historical per-run GWO F1-F23 raw dataset exists, so all 690 GWO
runs are recomputed.

Expected new work:
    SCHO F7                30
    GWO F1-F23            690
    7 comparators        4830
                         ----
                         5550 new runs

Expected final dataset:
    9 * 23 * 30 = 6210 rows

Exactness boundaries
--------------------
- algorithms/gwo.py and algorithms/scho.py are frozen and are never modified.
- SHO means Sea-Horse Optimizer from algorithms.sea_horse.
- AOA uses the SCHO Table 6 override mu=0.5 explicitly.
- RSA F17 uses the already-audited project-controlled vector-bound adapter
  inside algorithms/rsa.py.
- NumPy RNG is used; no MATLAB bitwise RNG equivalence is claimed.
- Source quirks are not repaired.
- This runner stores final-run distributions for Table 7 / Table 8.
  Convergence curves for Fig.9 are intentionally left to a separate plotting
  stage so source quirks such as curve[0]=0 remain transparent.

Checkpoint design
-----------------
- Workers compute only.
- The main process alone appends JSONL checkpoint records.
- Each completed run is flushed and fsync'ed immediately.
- Resume key: (Algorithm, Function, Run).
- Existing rows are validated against protocol metadata before being accepted.
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
from benchmarks.classic_23 import get_benchmark


PROTOCOL_ID = "H5_CLASSICAL_V1"

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
FUNCTIONS = tuple(f"F{i}" for i in range(1, 24))

N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_OPTIMIZER_SEED = 1000
OBJECTIVE_SEED_BASE = 5_024_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_SCHO_RAW = PROJECT_ROOT / "results" / "raw" / "scho_classic23_runs.csv"

CHECKPOINT_PATH = (
    PROJECT_ROOT / "results" / "raw" / "scho_classical_h5_checkpoint.jsonl"
)
FINAL_RAW_PATH = (
    PROJECT_ROOT / "results" / "raw" / "scho_classical_h5_runs.csv"
)

EXPECTED_TOTAL = len(ALGORITHM_ORDER) * len(FUNCTIONS) * N_RUNS
EXPECTED_REUSED_SCHO = 22 * N_RUNS
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
    if not 1 <= n <= 23:
        raise ValueError(f"Function outside F1-F23: {name}")
    return n


def optimizer_seed(run: int) -> int:
    return BASE_OPTIMIZER_SEED + run - 1


def formal_objective_seed(function_name: str, run: int) -> int:
    return OBJECTIVE_SEED_BASE + function_number(function_name) * 100 + run


def is_stochastic(function_name: str) -> bool:
    return function_name == "F7"


def expected_dim(function_name: str) -> int:
    return int(get_benchmark(function_name).dim)


def key_of(row: dict[str, Any]) -> tuple[str, str, int]:
    return (
        str(row["Algorithm"]),
        str(row["Function"]),
        int(row["Run"]),
    )


def jsonable_float(value: Any) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise RuntimeError(f"Non-finite numeric value: {value!r}")
    return out


def validate_common_metadata(row: dict[str, Any]) -> None:
    if row.get("ProtocolID") != PROTOCOL_ID:
        raise RuntimeError(
            f"Protocol mismatch for {key_of(row)}: {row.get('ProtocolID')!r}"
        )

    algorithm = str(row["Algorithm"])
    function_name = str(row["Function"])
    run = int(row["Run"])

    if algorithm not in ALGORITHM_ORDER:
        raise RuntimeError(f"Unknown algorithm in checkpoint: {algorithm}")
    if function_name not in FUNCTIONS:
        raise RuntimeError(f"Unknown function in checkpoint: {function_name}")
    if not 1 <= run <= N_RUNS:
        raise RuntimeError(f"Invalid run number in checkpoint: {run}")

    if int(row["OptimizerSeed"]) != optimizer_seed(run):
        raise RuntimeError(f"Optimizer seed mismatch for {key_of(row)}")

    if int(row["FormalObjectiveSeed"]) != formal_objective_seed(
        function_name, run
    ):
        raise RuntimeError(f"Formal objective seed mismatch for {key_of(row)}")

    if int(row["Dim"]) != expected_dim(function_name):
        raise RuntimeError(f"Dimension mismatch for {key_of(row)}")

    if int(row["Population"]) != N:
        raise RuntimeError(f"Population mismatch for {key_of(row)}")

    if int(row["MaxIter"]) != MAX_ITER:
        raise RuntimeError(f"MaxIter mismatch for {key_of(row)}")

    score = float(row["BestScore"])
    if not math.isfinite(score):
        raise RuntimeError(f"Non-finite BestScore for {key_of(row)}")

    provenance = str(row["Provenance"])

    if provenance == "REUSED_SCHO_C12":
        if algorithm != "SCHO" or function_name == "F7":
            raise RuntimeError(
                f"Illegal historical reuse for {key_of(row)}"
            )
        # Historical C12 used the same integer seed for the optimizer RNG
        # and benchmark RNG. For deterministic functions that benchmark RNG
        # is numerically irrelevant; we retain the actually executed seed.
        if int(row["ObjectiveSeed"]) != optimizer_seed(run):
            raise RuntimeError(
                f"Historical objective seed mismatch for {key_of(row)}"
            )
        if str(row["ObjectiveSeedRole"]) != "IGNORED_DETERMINISTIC":
            raise RuntimeError(
                f"Historical seed-role mismatch for {key_of(row)}"
            )
    elif provenance == "H5_NEW_RUN":
        if int(row["ObjectiveSeed"]) != formal_objective_seed(
            function_name, run
        ):
            raise RuntimeError(
                f"Executed objective seed mismatch for {key_of(row)}"
            )
        expected_role = (
            "ACTIVE_STOCHASTIC_F7"
            if is_stochastic(function_name)
            else "IGNORED_DETERMINISTIC"
        )
        if str(row["ObjectiveSeedRole"]) != expected_role:
            raise RuntimeError(
                f"Objective-seed role mismatch for {key_of(row)}"
            )
    else:
        raise RuntimeError(
            f"Unknown provenance for {key_of(row)}: {provenance!r}"
        )


def load_checkpoint() -> tuple[dict[tuple[str, str, int], dict[str, Any]], int]:
    rows: dict[tuple[str, str, int], dict[str, Any]] = {}
    reused = 0

    if not CHECKPOINT_PATH.exists():
        return rows, reused

    with CHECKPOINT_PATH.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL at {CHECKPOINT_PATH}:{lineno}"
                ) from exc

            validate_common_metadata(row)
            key = key_of(row)

            if key in rows:
                raise RuntimeError(
                    f"Duplicate checkpoint key at line {lineno}: {key}"
                )

            rows[key] = row
            if row["Provenance"] == "REUSED_SCHO_C12":
                reused += 1

    return rows, reused


def append_checkpoint(row: dict[str, Any]) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with CHECKPOINT_PATH.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def load_historical_scho_rows() -> list[dict[str, Any]]:
    if not HISTORICAL_SCHO_RAW.exists():
        raise FileNotFoundError(
            f"Historical SCHO raw file not found: {HISTORICAL_SCHO_RAW}"
        )

    with HISTORICAL_SCHO_RAW.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected = {"Function", "Run", "Seed", "BestScore"}

        if reader.fieldnames is None or not expected.issubset(reader.fieldnames):
            raise RuntimeError(
                f"Unexpected columns in {HISTORICAL_SCHO_RAW}: "
                f"{reader.fieldnames}"
            )

        source_rows = list(reader)

    if len(source_rows) != 23 * 30:
        raise RuntimeError(
            f"Historical SCHO raw row count={len(source_rows)}; expected 690"
        )

    seen: set[tuple[str, int]] = set()
    reusable: list[dict[str, Any]] = []

    for src in source_rows:
        function_name = str(src["Function"])
        run = int(src["Run"])
        seed = int(src["Seed"])

        if function_name not in FUNCTIONS:
            raise RuntimeError(
                f"Unexpected historical function: {function_name}"
            )
        if not 1 <= run <= N_RUNS:
            raise RuntimeError(
                f"Unexpected historical run: {function_name}/{run}"
            )
        if seed != optimizer_seed(run):
            raise RuntimeError(
                f"Historical seed mismatch: {function_name}/{run}: {seed}"
            )

        pair = (function_name, run)
        if pair in seen:
            raise RuntimeError(
                f"Duplicate historical SCHO key: {pair}"
            )
        seen.add(pair)

        if function_name == "F7":
            continue

        score = jsonable_float(src["BestScore"])
        b = get_benchmark(function_name)

        row = {
            "ProtocolID": PROTOCOL_ID,
            "Algorithm": "SCHO",
            "Function": function_name,
            "Run": run,
            "OptimizerSeed": seed,
            # Keep the actually executed historical benchmark seed.
            "ObjectiveSeed": seed,
            # Also record what H5_CLASSICAL_V1 would assign. It is irrelevant
            # for these deterministic functions, but makes the equivalence
            # boundary explicit instead of pretending the run was re-executed.
            "FormalObjectiveSeed": formal_objective_seed(
                function_name, run
            ),
            "ObjectiveSeedRole": "IGNORED_DETERMINISTIC",
            "Dim": int(b.dim),
            "Population": N,
            "MaxIter": MAX_ITER,
            "BestScore": score,
            "BestPositionJSON": "",
            "PositionAvailable": False,
            "RuntimeSeconds": None,
            "Provenance": "REUSED_SCHO_C12",
            "SourcePath": str(
                HISTORICAL_SCHO_RAW.relative_to(PROJECT_ROOT)
            ).replace("\\", "/"),
        }
        validate_common_metadata(row)
        reusable.append(row)

    if len(seen) != 690:
        raise RuntimeError(
            f"Historical SCHO unique Function/Run pairs={len(seen)}; "
            "expected 690"
        )

    if len(reusable) != EXPECTED_REUSED_SCHO:
        raise RuntimeError(
            f"Reusable SCHO rows={len(reusable)}; "
            f"expected {EXPECTED_REUSED_SCHO}"
        )

    return reusable


def bootstrap_reuse(
    completed: dict[tuple[str, str, int], dict[str, Any]]
) -> int:
    historical = load_historical_scho_rows()
    added = 0

    for row in historical:
        key = key_of(row)
        if key in completed:
            existing = completed[key]
            if existing["Provenance"] != "REUSED_SCHO_C12":
                raise RuntimeError(
                    f"Reuse key already occupied by non-reuse row: {key}"
                )
            continue

        append_checkpoint(row)
        completed[key] = row
        added += 1

    return added


def all_required_keys() -> list[tuple[str, str, int]]:
    return [
        (algorithm, function_name, run)
        for algorithm in ALGORITHM_ORDER
        for function_name in FUNCTIONS
        for run in range(1, N_RUNS + 1)
    ]


def build_pending(
    completed: dict[tuple[str, str, int], dict[str, Any]]
) -> list[tuple[str, str, int]]:
    return [
        key for key in all_required_keys()
        if key not in completed
    ]


def run_one(task: tuple[str, str, int]) -> dict[str, Any]:
    algorithm, function_name, run = task

    b = get_benchmark(function_name)
    opt_seed = optimizer_seed(run)
    obj_seed = formal_objective_seed(function_name, run)

    objective = b.make_objective(seed=obj_seed)
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
    best_pos = np.asarray(best_pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    if best_pos.shape != (b.dim,):
        raise RuntimeError(
            f"{algorithm}/{function_name}/run{run}: "
            f"best_pos shape={best_pos.shape}, expected {(b.dim,)}"
        )
    if not np.all(np.isfinite(best_pos)):
        raise RuntimeError(
            f"{algorithm}/{function_name}/run{run}: non-finite best position"
        )
    if curve.shape != (MAX_ITER,):
        raise RuntimeError(
            f"{algorithm}/{function_name}/run{run}: "
            f"curve shape={curve.shape}, expected {(MAX_ITER,)}"
        )
    if not np.all(np.isfinite(curve)):
        raise RuntimeError(
            f"{algorithm}/{function_name}/run{run}: non-finite curve"
        )

    row = {
        "ProtocolID": PROTOCOL_ID,
        "Algorithm": algorithm,
        "Function": function_name,
        "Run": run,
        "OptimizerSeed": opt_seed,
        "ObjectiveSeed": obj_seed,
        "FormalObjectiveSeed": obj_seed,
        "ObjectiveSeedRole": (
            "ACTIVE_STOCHASTIC_F7"
            if is_stochastic(function_name)
            else "IGNORED_DETERMINISTIC"
        ),
        "Dim": int(b.dim),
        "Population": N,
        "MaxIter": MAX_ITER,
        "BestScore": score,
        "BestPositionJSON": json.dumps(
            best_pos.tolist(),
            separators=(",", ":"),
        ),
        "PositionAvailable": True,
        "RuntimeSeconds": float(elapsed),
        "Provenance": "H5_NEW_RUN",
        "SourcePath": "",
    }

    validate_common_metadata(row)
    return row


def count_by_algorithm(
    rows: dict[tuple[str, str, int], dict[str, Any]]
) -> dict[str, int]:
    return {
        alg: sum(
            1 for (a, _f, _r) in rows
            if a == alg
        )
        for alg in ALGORITHM_ORDER
    }


def print_audit(
    completed: dict[tuple[str, str, int], dict[str, Any]],
    pending: list[tuple[str, str, int]],
    added_reuse: int,
) -> None:
    print("=" * 120)
    print("H5e - formal classical 9-algorithm runner audit")
    print("=" * 120)
    print(f"Protocol             : {PROTOCOL_ID}")
    print(f"N / MaxIter          : {N} / {MAX_ITER}")
    print(
        f"Optimizer seeds      : {BASE_OPTIMIZER_SEED}.."
        f"{BASE_OPTIMIZER_SEED + N_RUNS - 1}"
    )
    print(
        "Objective seed rule  : "
        f"{OBJECTIVE_SEED_BASE} + 100*function_number + run"
    )
    print(f"Checkpoint           : {CHECKPOINT_PATH}")
    print(f"Final raw CSV        : {FINAL_RAW_PATH}")
    print(f"Expected final rows  : {EXPECTED_TOTAL}")
    print(f"Expected reuse rows  : {EXPECTED_REUSED_SCHO}")
    print(f"Expected new runs    : {EXPECTED_NEW}")
    print(f"Reuse rows added now : {added_reuse}")
    print(f"Completed/checkpoint : {len(completed)}")
    print(f"Pending              : {len(pending)}")
    print("-" * 120)

    counts = count_by_algorithm(completed)
    for alg in ALGORITHM_ORDER:
        print(
            f"{alg:<4}: completed={counts[alg]:>3}/690  "
            f"pending={690 - counts[alg]:>3}"
        )

    print("-" * 120)

    reuse_count = sum(
        1 for row in completed.values()
        if row["Provenance"] == "REUSED_SCHO_C12"
    )
    new_count = sum(
        1 for row in completed.values()
        if row["Provenance"] == "H5_NEW_RUN"
    )
    print(
        f"Provenance: reused_scho_c12={reuse_count}, "
        f"h5_new_run={new_count}"
    )

    f7_completed = sum(
        1 for (_a, f, _r) in completed if f == "F7"
    )
    print(f"F7 completed         : {f7_completed}/270")
    print("=" * 120)


def write_final_csv(
    completed: dict[tuple[str, str, int], dict[str, Any]]
) -> None:
    if len(completed) != EXPECTED_TOTAL:
        raise RuntimeError(
            f"Cannot write final CSV: completed={len(completed)}, "
            f"expected={EXPECTED_TOTAL}"
        )

    required = set(all_required_keys())
    actual = set(completed)

    missing = required - actual
    extra = actual - required

    if missing or extra:
        raise RuntimeError(
            f"Final key mismatch: missing={len(missing)}, extra={len(extra)}"
        )

    for row in completed.values():
        validate_common_metadata(row)

    FINAL_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "ProtocolID",
        "Algorithm",
        "Function",
        "Run",
        "OptimizerSeed",
        "ObjectiveSeed",
        "FormalObjectiveSeed",
        "ObjectiveSeedRole",
        "Dim",
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
        name: idx for idx, name in enumerate(ALGORITHM_ORDER)
    }

    rows = sorted(
        completed.values(),
        key=lambda r: (
            alg_index[str(r["Algorithm"])],
            function_number(str(r["Function"])),
            int(r["Run"]),
        ),
    )

    with FINAL_RAW_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "H5e formal SCHO classical 9-algorithm runner "
            "with checkpoint/resume."
        )
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="ProcessPoolExecutor worker count (default: 4).",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help=(
            "Validate/bootstrap historical SCHO reuse and print the "
            "planned workload without executing new optimizer runs."
        ),
    )
    parser.add_argument(
        "--max-new-runs",
        type=int,
        default=None,
        help=(
            "Optional cap on newly executed runs for controlled testing. "
            "Checkpoint/resume remains valid."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.workers < 1:
        raise ValueError("--workers must be >= 1")
    if args.max_new_runs is not None and args.max_new_runs < 1:
        raise ValueError("--max-new-runs must be >= 1")

    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)

    completed, _reused_before = load_checkpoint()
    added_reuse = bootstrap_reuse(completed)
    pending = build_pending(completed)

    print_audit(completed, pending, added_reuse)

    if args.audit_only:
        print("H5e AUDIT-ONLY RESULT: PASS")
        print("No new optimizer run was executed.")
        return

    tasks = pending
    if args.max_new_runs is not None:
        tasks = tasks[: args.max_new_runs]

    if not tasks:
        if len(completed) == EXPECTED_TOTAL:
            write_final_csv(completed)
            print("H5e RESULT: COMPLETE")
            print(f"Saved final raw dataset to: {FINAL_RAW_PATH}")
        else:
            print("No tasks selected, but the full dataset is not complete.")
        return

    print()
    print(
        f"Executing {len(tasks)} new runs with "
        f"{args.workers} worker(s)..."
    )
    print(
        "Each completed run is checkpointed immediately by the main process."
    )
    print()

    started = time.perf_counter()
    completed_this_invocation = 0

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        future_to_task = {
            executor.submit(run_one, task): task
            for task in tasks
        }

        for future in as_completed(future_to_task):
            task = future_to_task[future]

            try:
                row = future.result()
            except Exception as exc:
                raise RuntimeError(
                    f"H5e worker failed for task={task}"
                ) from exc

            key = key_of(row)

            if key in completed:
                raise RuntimeError(
                    f"Worker returned already-completed key: {key}"
                )

            append_checkpoint(row)
            completed[key] = row
            completed_this_invocation += 1

            total_done = len(completed)
            elapsed = time.perf_counter() - started

            if (
                completed_this_invocation <= 10
                or completed_this_invocation % 10 == 0
                or completed_this_invocation == len(tasks)
            ):
                print(
                    f"[{completed_this_invocation:>4}/{len(tasks)} this call] "
                    f"[{total_done:>4}/{EXPECTED_TOTAL} total] "
                    f"{row['Algorithm']}/{row['Function']}/"
                    f"run{row['Run']:02d} "
                    f"best={float(row['BestScore']):.10e} "
                    f"elapsed={elapsed:.1f}s"
                )

    print()
    remaining = build_pending(completed)

    print("-" * 120)
    print(
        f"Completed this invocation: {completed_this_invocation}"
    )
    print(f"Total completed         : {len(completed)}/{EXPECTED_TOTAL}")
    print(f"Remaining               : {len(remaining)}")

    if remaining:
        print("H5e RESULT: PARTIAL_CHECKPOINTED")
        print(
            "Re-run the same command to resume from the existing checkpoint."
        )
        return

    write_final_csv(completed)

    print("H5e RESULT: COMPLETE")
    print(f"Final rows: {len(completed)}")
    print(f"Saved final raw dataset to: {FINAL_RAW_PATH}")
    print(
        "Next: H5f Table 7 Best/Mean/sample-STD/rank reproduction."
    )
    print("=" * 120)


if __name__ == "__main__":
    main()
