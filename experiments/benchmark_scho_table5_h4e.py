"""H4e - Formal SCHO Table-5 subordinate-model ablation.

Paper section
-------------
SCHO paper Section 3.1.1 / Table 5.

Models
------
SCHO, SCHO_NT, SCHO_NSTF, SCHO_NFTF, SCHO_NSF, SCHO_NFF

Protocol
--------
Functions : F1-F23
Population: N=30
MaxIter   : 500
Runs      : 30 / model / function
Seeds     : 1000..1029 (project reproducibility convention)
Total     : 6 * 23 * 30 = 4140 optimizer runs

Important exactness boundary
----------------------------
- `SCHO` mode is exact-trajectory equivalent to frozen `algorithms/scho.py`,
  as verified in H4d.
- Five ablations are PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION
  because separate author variant source files were not recovered.
- Results must not be tuned to chase Table-5 ranks.

Outputs
-------
results/raw/scho_table5_h4e_runs.csv
results/processed/scho_table5_h4e_summary.csv
results/processed/scho_table5_h4e_ranks.csv
report/scho_table5_h4e_comparison.md

Checkpoint/resume
-----------------
The parent process appends one validated row after every completed run.
Rerunning the same command skips completed protocol-matching rows.
"""

from __future__ import annotations

import csv
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from benchmarks.classic_23 import get_benchmark
from experiments.scho_table5_variants_h4 import (
    TABLE5_VARIANTS,
    scho_table5_variant,
)


FUNCTIONS = tuple(f"F{i}" for i in range(1, 24))
N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_SEED = 1000

RAW_PATH = Path("results/raw/scho_table5_h4e_runs.csv")
SUMMARY_PATH = Path("results/processed/scho_table5_h4e_summary.csv")
RANK_PATH = Path("results/processed/scho_table5_h4e_ranks.csv")
REPORT_PATH = Path("report/scho_table5_h4e_comparison.md")

# Paper Table-5 ranking anchors. These are validation references only.
PAPER_MEAN_RANK = {
    "SCHO": 1.65,
    "SCHO_NT": 2.96,
    "SCHO_NSTF": 3.35,
    "SCHO_NFTF": 4.52,
    "SCHO_NSF": 2.13,
    "SCHO_NFF": 3.35,
}
PAPER_FINAL_RANK = {
    "SCHO": 1,
    "SCHO_NT": 3,
    "SCHO_NSTF": 4,
    "SCHO_NFTF": 6,
    "SCHO_NSF": 2,
    "SCHO_NFF": 4,
}

RAW_FIELDS = [
    "Variant",
    "Function",
    "Run",
    "OptimizerSeed",
    "ObjectiveSeed",
    "Population",
    "MaxIter",
    "Dimension",
    "LowerBound",
    "UpperBound",
    "Optimum",
    "BestScore",
    "Curve0",
    "CurveLast",
    "ElapsedSeconds",
    "Status",
]

SUMMARY_FIELDS = [
    "Variant",
    "Function",
    "Runs",
    "Population",
    "MaxIter",
    "Dimension",
    "Optimum",
    "Best",
    "Average",
    "STD_sample_ddof1",
    "STD_population_ddof0",
    "Median",
    "Worst",
]

RANK_FIELDS = [
    "Function",
    "Variant",
    "Average",
    "Rank",
]


def _objective_seed(name: str, run: int) -> int:
    """Common benchmark RNG stream across all variants for the same F/run.

    Only stochastic F7 consumes this RNG. Deterministic benchmarks ignore it.
    """
    return 4_024_000 + int(name[1:]) * 100 + run


def _default_workers() -> int:
    override = os.environ.get("H4E_WORKERS")
    if override is not None:
        try:
            value = int(override)
        except ValueError as exc:
            raise ValueError("H4E_WORKERS must be an integer >= 1") from exc
        if value < 1:
            raise ValueError("H4E_WORKERS must be >= 1")
        return value

    cpu = os.cpu_count() or 1
    return max(1, min(4, cpu // 2 if cpu >= 2 else 1))


def _scalar_bound_text(bound) -> str:
    arr = np.asarray(bound, dtype=float)
    if arr.ndim == 0 or arr.size == 1:
        return f"{float(arr.reshape(-1)[0]):.17g}"
    return ";".join(f"{x:.17g}" for x in arr.reshape(-1))


def _validate_run(variant, name, b, best_score, best_pos, curve):
    score = float(best_score)
    pos = np.asarray(best_pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    if not np.isfinite(score):
        raise AssertionError(f"{variant} {name}: non-finite best score")
    if pos.shape != (b.dim,):
        raise AssertionError(
            f"{variant} {name}: best position shape {pos.shape} != {(b.dim,)}"
        )
    if not np.all(np.isfinite(pos)):
        raise AssertionError(f"{variant} {name}: best position contains NaN/Inf")
    if curve.shape != (MAX_ITER,):
        raise AssertionError(
            f"{variant} {name}: curve shape {curve.shape} != {(MAX_ITER,)}"
        )
    if not np.all(np.isfinite(curve)):
        raise AssertionError(f"{variant} {name}: convergence has NaN/Inf")
    if np.any(np.diff(curve) > 0.0):
        idx = int(np.flatnonzero(np.diff(curve) > 0.0)[0])
        raise AssertionError(
            f"{variant} {name}: historical best increased at {idx}->{idx+1}"
        )
    if score != float(curve[-1]):
        raise AssertionError(f"{variant} {name}: score != curve[-1]")


def _run_task(task):
    variant, name, run = task
    optimizer_seed = BASE_SEED + run - 1
    objective_seed = _objective_seed(name, run)

    b = get_benchmark(name)
    objective = b.make_objective(seed=objective_seed)

    start = time.perf_counter()
    best_score, best_pos, curve = scho_table5_variant(
        obj_func=objective,
        dim=b.dim,
        lb=b.lb,
        ub=b.ub,
        N=N,
        MaxIter=MAX_ITER,
        variant=variant,
        seed=optimizer_seed,
    )
    elapsed = time.perf_counter() - start

    _validate_run(variant, name, b, best_score, best_pos, curve)

    return {
        "Variant": variant,
        "Function": name,
        "Run": run,
        "OptimizerSeed": optimizer_seed,
        "ObjectiveSeed": objective_seed,
        "Population": N,
        "MaxIter": MAX_ITER,
        "Dimension": int(b.dim),
        "LowerBound": _scalar_bound_text(b.lb),
        "UpperBound": _scalar_bound_text(b.ub),
        "Optimum": float(b.optimum),
        "BestScore": float(best_score),
        "Curve0": float(np.asarray(curve, dtype=float)[0]),
        "CurveLast": float(np.asarray(curve, dtype=float)[-1]),
        "ElapsedSeconds": float(elapsed),
        "Status": "PASS",
    }


def _normalize_raw_row(row):
    return {
        "Variant": row["Variant"],
        "Function": row["Function"],
        "Run": int(row["Run"]),
        "OptimizerSeed": int(row["OptimizerSeed"]),
        "ObjectiveSeed": int(row["ObjectiveSeed"]),
        "Population": int(row["Population"]),
        "MaxIter": int(row["MaxIter"]),
        "Dimension": int(row["Dimension"]),
        "LowerBound": row["LowerBound"],
        "UpperBound": row["UpperBound"],
        "Optimum": float(row["Optimum"]),
        "BestScore": float(row["BestScore"]),
        "Curve0": float(row["Curve0"]),
        "CurveLast": float(row["CurveLast"]),
        "ElapsedSeconds": float(row["ElapsedSeconds"]),
        "Status": row["Status"],
    }


def _row_matches_protocol(row):
    try:
        variant = row["Variant"]
        name = row["Function"]
        run = int(row["Run"])
        b = get_benchmark(name)
        return (
            variant in TABLE5_VARIANTS
            and name in FUNCTIONS
            and 1 <= run <= N_RUNS
            and int(row["OptimizerSeed"]) == BASE_SEED + run - 1
            and int(row["ObjectiveSeed"]) == _objective_seed(name, run)
            and int(row["Population"]) == N
            and int(row["MaxIter"]) == MAX_ITER
            and int(row["Dimension"]) == int(b.dim)
            and row["Status"] == "PASS"
        )
    except Exception:
        return False


def _ensure_dirs():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_existing_rows():
    if not RAW_PATH.exists():
        return [], set()

    rows = []
    completed = set()

    with RAW_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != RAW_FIELDS:
            raise RuntimeError(
                f"Unexpected columns in {RAW_PATH}.\n"
                f"Expected: {RAW_FIELDS}\n"
                f"Found   : {reader.fieldnames}"
            )

        for disk_row in reader:
            row = _normalize_raw_row(disk_row)
            if not _row_matches_protocol(row):
                raise RuntimeError(
                    "Existing H4e raw file contains a row from a different "
                    f"protocol: {row}"
                )

            key = (row["Variant"], row["Function"], row["Run"])
            if key in completed:
                raise RuntimeError(f"Duplicate H4e raw result: {key}")

            completed.add(key)
            rows.append(row)

    return rows, completed


def _append_raw(row):
    new_file = not RAW_PATH.exists()
    with RAW_PATH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def _build_summary(rows):
    summary = []

    for variant in TABLE5_VARIANTS:
        for name in FUNCTIONS:
            b = get_benchmark(name)
            group = sorted(
                [
                    row
                    for row in rows
                    if row["Variant"] == variant
                    and row["Function"] == name
                    and _row_matches_protocol(row)
                ],
                key=lambda row: row["Run"],
            )

            if len(group) != N_RUNS:
                raise RuntimeError(
                    f"{variant} {name}: expected {N_RUNS} rows, got {len(group)}"
                )

            if [row["Run"] for row in group] != list(range(1, N_RUNS + 1)):
                raise RuntimeError(
                    f"{variant} {name}: incomplete run sequence"
                )

            scores = np.asarray([row["BestScore"] for row in group], dtype=float)

            summary.append(
                {
                    "Variant": variant,
                    "Function": name,
                    "Runs": N_RUNS,
                    "Population": N,
                    "MaxIter": MAX_ITER,
                    "Dimension": int(b.dim),
                    "Optimum": float(b.optimum),
                    "Best": float(np.min(scores)),
                    "Average": float(np.mean(scores)),
                    "STD_sample_ddof1": float(np.std(scores, ddof=1)),
                    "STD_population_ddof0": float(np.std(scores, ddof=0)),
                    "Median": float(np.median(scores)),
                    "Worst": float(np.max(scores)),
                }
            )

    return summary


def _competition_ranks(values):
    """Minimization competition ranks: 1,2,2,4 ... for exact ties."""
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=int)

    rank = 1
    i = 0
    while i < len(order):
        j = i + 1
        v = values[order[i]]
        while j < len(order) and values[order[j]] == v:
            j += 1
        for k in range(i, j):
            ranks[order[k]] = rank
        rank = j + 1
        i = j

    return ranks


def _build_ranks(summary):
    by_key = {(r["Variant"], r["Function"]): r for r in summary}
    rank_rows = []

    for name in FUNCTIONS:
        averages = [by_key[(variant, name)]["Average"] for variant in TABLE5_VARIANTS]
        ranks = _competition_ranks(averages)

        for variant, avg, rank in zip(TABLE5_VARIANTS, averages, ranks):
            rank_rows.append(
                {
                    "Function": name,
                    "Variant": variant,
                    "Average": float(avg),
                    "Rank": int(rank),
                }
            )

    return rank_rows


def _mean_ranks(rank_rows):
    out = {}
    for variant in TABLE5_VARIANTS:
        vals = [
            row["Rank"]
            for row in rank_rows
            if row["Variant"] == variant
        ]
        if len(vals) != len(FUNCTIONS):
            raise RuntimeError(f"{variant}: missing rank rows")
        out[variant] = float(np.mean(np.asarray(vals, dtype=float)))
    return out


def _final_ranks_from_mean(mean_ranks):
    vals = [mean_ranks[v] for v in TABLE5_VARIANTS]
    ranks = _competition_ranks(vals)
    return {
        variant: int(rank)
        for variant, rank in zip(TABLE5_VARIANTS, ranks)
    }


def _write_summary(summary, rank_rows):
    with SUMMARY_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary)

    with RANK_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RANK_FIELDS)
        writer.writeheader()
        writer.writerows(rank_rows)


def _fmt(x):
    return f"{float(x):.6g}"


def _write_report(summary, rank_rows, workers):
    by_key = {(r["Variant"], r["Function"]): r for r in summary}
    mean_ranks = _mean_ranks(rank_rows)
    final_ranks = _final_ranks_from_mean(mean_ranks)

    lines = [
        "# H4e — SCHO Table-5 structural ablation reproduction",
        "",
        "## Reproduction tier",
        "",
        "`SCHO: SOURCE-FAITHFUL CONTROL`",
        "",
        "`Five ablations: PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION`",
        "",
        "## Protocol",
        "",
        "- Models: SCHO, SCHO_NT, SCHO_NSTF, SCHO_NFTF, SCHO_NSF, SCHO_NFF",
        "- Functions: F1–F23",
        "- N = 30",
        "- MaxIter = 500",
        "- 30 runs/model/function",
        "- seeds = 1000–1029 (project convention)",
        "- common objective-RNG seed across variants for the same function/run",
        "- sample STD (`ddof=1`) saved as the primary Table-5 comparison STD",
        f"- execution workers used: {workers}",
        "",
        "Total formal runs: 4140.",
        "",
        "## Reproduced ranking",
        "",
        "| Variant | Repro Mean Rank | Paper Mean Rank | Repro Final Rank | Paper Final Rank |",
        "|---|---:|---:|---:|---:|",
    ]

    for variant in TABLE5_VARIANTS:
        lines.append(
            f"| {variant} | {_fmt(mean_ranks[variant])} "
            f"| {_fmt(PAPER_MEAN_RANK[variant])} "
            f"| {final_ranks[variant]} | {PAPER_FINAL_RANK[variant]} |"
        )

    lines += [
        "",
        "## Per-function Best / Average / sample STD / rank",
        "",
    ]

    for name in FUNCTIONS:
        lines += [
            f"### {name}",
            "",
            "| Variant | Best | Average | STD | Rank |",
            "|---|---:|---:|---:|---:|",
        ]
        rank_map = {
            row["Variant"]: row["Rank"]
            for row in rank_rows
            if row["Function"] == name
        }
        for variant in TABLE5_VARIANTS:
            row = by_key[(variant, name)]
            lines.append(
                f"| {variant} | {_fmt(row['Best'])} "
                f"| {_fmt(row['Average'])} "
                f"| {_fmt(row['STD_sample_ddof1'])} "
                f"| {rank_map[variant]} |"
            )
        lines.append("")

    lines += [
        "## Interpretation boundary",
        "",
        "`H4e RESULT: PASS` means all 4140 protocol runs completed and the",
        "Table-5-style statistics/ranks were produced.",
        "",
        "It does **not** mean the five controlled structural variants numerically",
        "match the unrecovered author variant implementations.",
        "",
        "H4f must compare the reproduced Table-5 statistics/ranking against the",
        "paper and freeze any disagreement without parameter tuning.",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _print_progress(completed_count, total, row, wall_start):
    elapsed_wall = time.perf_counter() - wall_start
    newly_done = max(completed_count, 1)
    avg_wall = elapsed_wall / newly_done
    remaining = max(total - completed_count, 0)
    rough_eta = avg_wall * remaining

    print(
        f"[{completed_count:04d}/{total}] "
        f"{row['Variant']:<11} {row['Function']:<3} run={row['Run']:02d} "
        f"seed={row['OptimizerSeed']} best={row['BestScore']:.10g} "
        f"worker_time={row['ElapsedSeconds']:.1f}s "
        f"rough_remaining={rough_eta/3600:.1f}h"
    )


def main():
    _ensure_dirs()
    rows, completed = _load_existing_rows()

    all_tasks = [
        (variant, name, run)
        for variant in TABLE5_VARIANTS
        for name in FUNCTIONS
        for run in range(1, N_RUNS + 1)
    ]
    pending = [
        task
        for task in all_tasks
        if (task[0], task[1], task[2]) not in completed
    ]

    workers = _default_workers()
    total = len(all_tasks)

    print("=" * 132)
    print("H4e - Formal SCHO Table-5 subordinate-model ablation")
    print("=" * 132)
    print(f"Models    : {', '.join(TABLE5_VARIANTS)}")
    print(f"Functions : F1-F23")
    print(f"Protocol  : N={N}, MaxIter={MAX_ITER}, runs={N_RUNS}/model/function")
    print(f"Seeds     : {BASE_SEED}..{BASE_SEED + N_RUNS - 1}")
    print(f"Total runs: {total}")
    print(f"Workers   : {workers}")
    print(f"Complete  : {len(completed)}/{total}")
    print(f"Checkpoint: {RAW_PATH}")
    print("The run is resumable; rerun the same command after interruption.")
    print("=" * 132)

    if pending:
        wall_start = time.perf_counter()

        if workers == 1:
            for task in pending:
                row = _run_task(task)
                _append_raw(row)
                rows.append(row)
                completed.add((row["Variant"], row["Function"], row["Run"]))
                _print_progress(len(completed), total, row, wall_start)
        else:
            # Small bounded batches reduce lost work after interruption.
            batch_size = workers * 2

            for start_idx in range(0, len(pending), batch_size):
                batch = pending[start_idx:start_idx + batch_size]

                with ProcessPoolExecutor(max_workers=workers) as pool:
                    futures = {
                        pool.submit(_run_task, task): task
                        for task in batch
                    }

                    for future in as_completed(futures):
                        row = future.result()
                        _append_raw(row)
                        rows.append(row)
                        completed.add(
                            (row["Variant"], row["Function"], row["Run"])
                        )
                        _print_progress(
                            len(completed), total, row, wall_start
                        )

    if len(completed) != total:
        raise RuntimeError(
            f"H4e incomplete: {len(completed)}/{total} rows checkpointed"
        )

    summary = _build_summary(rows)
    rank_rows = _build_ranks(summary)
    _write_summary(summary, rank_rows)
    _write_report(summary, rank_rows, workers)

    mean_ranks = _mean_ranks(rank_rows)
    final_ranks = _final_ranks_from_mean(mean_ranks)

    print("\n" + "-" * 132)
    print("Reproduced mean ranks:")
    for variant in TABLE5_VARIANTS:
        print(
            f"{variant:<11} mean_rank={mean_ranks[variant]:.6g} "
            f"final_rank={final_ranks[variant]} "
            f"| paper mean_rank={PAPER_MEAN_RANK[variant]:.6g} "
            f"paper final_rank={PAPER_FINAL_RANK[variant]}"
        )

    print("-" * 132)
    print("H4e RESULT: PASS")
    print(f"Formal runs complete: {total}/{total}")
    print(f"Saved raw    : {RAW_PATH}")
    print(f"Saved summary: {SUMMARY_PATH}")
    print(f"Saved ranks  : {RANK_PATH}")
    print(f"Saved report : {REPORT_PATH}")
    print("No parameter tuning was performed.")
    print("Next: H4f Table-5 paper-agreement diagnostic and ablation freeze.")
    print("=" * 132)


if __name__ == "__main__":
    main()
