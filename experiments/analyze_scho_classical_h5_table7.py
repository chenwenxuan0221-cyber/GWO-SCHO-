"""H5f - SCHO Table 7 reproduction from H5_CLASSICAL_V1 raw results.

Reads:
    results/raw/scho_classical_h5_runs.csv

Writes:
    results/processed/scho_classical_h5_summary.csv
    report/tables/H5_table7_reproduction.csv
    report/H5_table7_comparison.md

Statistics:
    Best = minimum final best score
    Mean = arithmetic mean
    STD  = sample standard deviation (ddof=1), matching MATLAB std default

Ranking:
    All F1-F23 are minimization problems.
    Per-function rank is by Mean ascending.
    Ties receive average ranks.
    MeanRank is averaged across 23 functions.
    FinalRank is the ascending rank of MeanRank.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable

import numpy as np


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
N_RUNS = 30
EXPECTED_ROWS = len(ALGORITHM_ORDER) * len(FUNCTIONS) * N_RUNS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "results" / "raw" / "scho_classical_h5_runs.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "processed" / "scho_classical_h5_summary.csv"
TABLE7_PATH = PROJECT_ROOT / "report" / "tables" / "H5_table7_reproduction.csv"
COMPARISON_PATH = PROJECT_ROOT / "report" / "H5_table7_comparison.md"

# Paper anchors already frozen during the H5 audit.
PAPER_MEAN_RANK = {
    "SCHO": 2.48,
    "GWO": 3.78,
    "ALO": 5.43,
    "SCA": 7.39,
    "SSA": 4.83,
    "AOA": 5.83,
    "RSA": 4.57,
    "SHO": 4.00,
    "GJO": 3.74,
}
PAPER_FINAL_RANK = {
    "SCHO": 1,
    "GWO": 3,
    "ALO": 7,
    "SCA": 9,
    "SSA": 6,
    "AOA": 8,
    "RSA": 5,
    "SHO": 4,
    "GJO": 2,
}


def function_number(name: str) -> int:
    return int(name[1:])


def average_ranks(values: Iterable[float]) -> np.ndarray:
    """Ascending average ranks without requiring SciPy."""
    a = np.asarray(list(values), dtype=float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)

    i = 0
    while i < len(a):
        j = i + 1
        while j < len(a) and a[order[j]] == a[order[i]]:
            j += 1

        # Occupied one-based ranks are i+1 ... j.
        avg_rank = ((i + 1) + j) / 2.0
        ranks[order[i:j]] = avg_rank
        i = j

    return ranks


def load_raw() -> list[dict[str, str]]:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw H5 dataset not found: {RAW_PATH}")

    with RAW_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != EXPECTED_ROWS:
        raise RuntimeError(
            f"Raw row count={len(rows)}; expected {EXPECTED_ROWS}"
        )

    if not rows:
        raise RuntimeError("Raw file is empty.")

    required = {
        "ProtocolID",
        "Algorithm",
        "Function",
        "Run",
        "OptimizerSeed",
        "Dim",
        "Population",
        "MaxIter",
        "BestScore",
        "Provenance",
    }

    missing = required - set(rows[0])
    if missing:
        raise RuntimeError(f"Missing raw columns: {sorted(missing)}")

    seen: set[tuple[str, str, int]] = set()

    for row in rows:
        if row["ProtocolID"] != PROTOCOL_ID:
            raise RuntimeError(
                f"Protocol mismatch: {row['ProtocolID']!r}"
            )

        algorithm = row["Algorithm"]
        function_name = row["Function"]
        run = int(row["Run"])

        if algorithm not in ALGORITHM_ORDER:
            raise RuntimeError(f"Unexpected algorithm: {algorithm}")
        if function_name not in FUNCTIONS:
            raise RuntimeError(f"Unexpected function: {function_name}")
        if not 1 <= run <= N_RUNS:
            raise RuntimeError(
                f"Invalid run: {algorithm}/{function_name}/{run}"
            )

        key = (algorithm, function_name, run)
        if key in seen:
            raise RuntimeError(f"Duplicate raw key: {key}")
        seen.add(key)

        score = float(row["BestScore"])
        if not math.isfinite(score):
            raise RuntimeError(f"Non-finite BestScore at {key}")

        if int(row["Population"]) != 30:
            raise RuntimeError(f"Population mismatch at {key}")
        if int(row["MaxIter"]) != 500:
            raise RuntimeError(f"MaxIter mismatch at {key}")
        if int(row["OptimizerSeed"]) != 999 + run:
            raise RuntimeError(f"Optimizer seed mismatch at {key}")

    expected_keys = {
        (algorithm, function_name, run)
        for algorithm in ALGORITHM_ORDER
        for function_name in FUNCTIONS
        for run in range(1, N_RUNS + 1)
    }

    if seen != expected_keys:
        raise RuntimeError(
            f"Raw key coverage mismatch: "
            f"missing={len(expected_keys - seen)}, "
            f"extra={len(seen - expected_keys)}"
        )

    return rows


def summarize(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[float]] = {}

    for row in rows:
        key = (row["Algorithm"], row["Function"])
        grouped.setdefault(key, []).append(float(row["BestScore"]))

    summary: list[dict[str, object]] = []

    for function_name in FUNCTIONS:
        per_function: list[dict[str, object]] = []

        for algorithm in ALGORITHM_ORDER:
            scores = np.asarray(
                grouped[(algorithm, function_name)],
                dtype=float,
            )

            if scores.size != N_RUNS:
                raise RuntimeError(
                    f"{algorithm}/{function_name} has {scores.size} runs; "
                    f"expected {N_RUNS}"
                )

            per_function.append(
                {
                    "Algorithm": algorithm,
                    "Function": function_name,
                    "Runs": int(scores.size),
                    "Best": float(np.min(scores)),
                    "Mean": float(np.mean(scores)),
                    "STD": float(np.std(scores, ddof=1)),
                    "Median": float(np.median(scores)),
                }
            )

        ranks = average_ranks(r["Mean"] for r in per_function)

        for row, rank in zip(per_function, ranks):
            row["Rank"] = float(rank)
            summary.append(row)

    return summary


def build_rank_summary(
    summary: list[dict[str, object]],
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []

    for algorithm in ALGORITHM_ORDER:
        alg_rows = [
            r for r in summary
            if r["Algorithm"] == algorithm
        ]

        if len(alg_rows) != 23:
            raise RuntimeError(
                f"{algorithm}: function count={len(alg_rows)}, expected 23"
            )

        mean_rank = float(
            np.mean([float(r["Rank"]) for r in alg_rows])
        )

        out.append(
            {
                "Algorithm": algorithm,
                "MeanRank": mean_rank,
            }
        )

    final_ranks = average_ranks(r["MeanRank"] for r in out)

    for row, final_rank in zip(out, final_ranks):
        alg = str(row["Algorithm"])
        row["FinalRank"] = float(final_rank)
        row["PaperMeanRank"] = float(PAPER_MEAN_RANK[alg])
        row["PaperFinalRank"] = int(PAPER_FINAL_RANK[alg])
        row["MeanRankDelta"] = (
            float(row["MeanRank"]) - float(PAPER_MEAN_RANK[alg])
        )

    return out


def write_summary(summary: list[dict[str, object]]) -> None:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "Algorithm",
        "Function",
        "Runs",
        "Best",
        "Mean",
        "STD",
        "Median",
        "Rank",
    ]

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)


def write_table7(
    summary: list[dict[str, object]],
    rank_summary: list[dict[str, object]],
) -> None:
    TABLE7_PATH.parent.mkdir(parents=True, exist_ok=True)

    rank_lookup = {
        str(r["Algorithm"]): r
        for r in rank_summary
    }

    fields = [
        "Function",
        "Algorithm",
        "Best",
        "Mean",
        "STD_sample_ddof1",
        "Rank_by_Mean",
        "MeanRank_23",
        "FinalRank",
    ]

    with TABLE7_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for function_name in FUNCTIONS:
            for algorithm in ALGORITHM_ORDER:
                row = next(
                    r for r in summary
                    if r["Function"] == function_name
                    and r["Algorithm"] == algorithm
                )
                rr = rank_lookup[algorithm]

                writer.writerow(
                    {
                        "Function": function_name,
                        "Algorithm": algorithm,
                        "Best": repr(float(row["Best"])),
                        "Mean": repr(float(row["Mean"])),
                        "STD_sample_ddof1": repr(float(row["STD"])),
                        "Rank_by_Mean": repr(float(row["Rank"])),
                        "MeanRank_23": repr(float(rr["MeanRank"])),
                        "FinalRank": repr(float(rr["FinalRank"])),
                    }
                )


def format_rank(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}"


def write_comparison(
    rank_summary: list[dict[str, object]],
) -> None:
    COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)

    sorted_rows = sorted(
        rank_summary,
        key=lambda r: float(r["MeanRank"]),
    )

    lines: list[str] = [
        "# H5f — SCHO Table 7 reproduction comparison",
        "",
        (
            "Protocol: `H5_CLASSICAL_V1`; F1–F13 D=30; "
            "F14–F23 native dimension; N=30; MaxIter=500; "
            "30 runs/function."
        ),
        "",
        (
            "Statistics: Best, arithmetic Mean, and sample STD "
            "(`ddof=1`, aligned with MATLAB `std` default). "
            "Per-function ranking uses Mean ascending with average-rank ties."
        ),
        "",
        (
            "The paper values below are the Table 7 anchors frozen during "
            "the H5 audit. They are comparison anchors, not values "
            "recomputed from the paper inside this script."
        ),
        "",
        (
            "| Algorithm | Reproduced mean rank | Paper mean rank | Delta | "
            "Reproduced final rank | Paper final rank |"
        ),
        "|---|---:|---:|---:|---:|---:|",
    ]

    for row in sorted_rows:
        lines.append(
            f"| {row['Algorithm']} | "
            f"{float(row['MeanRank']):.5f} | "
            f"{float(row['PaperMeanRank']):.2f} | "
            f"{float(row['MeanRankDelta']):+.5f} | "
            f"{format_rank(float(row['FinalRank']))} | "
            f"{int(row['PaperFinalRank'])} |"
        )

    reproduced_order = ", ".join(
        str(r["Algorithm"]) for r in sorted_rows
    )
    paper_order = ", ".join(
        sorted(ALGORITHM_ORDER, key=lambda a: PAPER_FINAL_RANK[a])
    )

    lines.extend(
        [
            "",
            "## Rank-order view",
            "",
            f"- Reproduced order: `{reproduced_order}`",
            f"- Paper anchor order: `{paper_order}`",
            "",
            (
                "Interpretation must distinguish rank-level agreement from "
                "exact numerical agreement. No parameter tuning is performed "
                "to force reproduced ranks toward the paper."
            ),
            "",
        ]
    )

    COMPARISON_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def print_console(
    rank_summary: list[dict[str, object]],
) -> None:
    sorted_rows = sorted(
        rank_summary,
        key=lambda r: float(r["MeanRank"]),
    )

    print("=" * 108)
    print("H5f - SCHO Table 7 reproduction")
    print("=" * 108)
    print(f"Raw dataset : {RAW_PATH}")
    print(f"Raw rows    : {EXPECTED_ROWS}")
    print("STD         : sample STD, ddof=1")
    print("Rank basis  : per-function Mean ascending; average ties")
    print("-" * 108)
    print(
        f"{'Alg':<5} "
        f"{'MeanRank':>12} "
        f"{'FinalRank':>11} "
        f"{'PaperMR':>10} "
        f"{'PaperRank':>11} "
        f"{'DeltaMR':>12}"
    )
    print("-" * 108)

    for row in sorted_rows:
        print(
            f"{str(row['Algorithm']):<5} "
            f"{float(row['MeanRank']):>12.5f} "
            f"{format_rank(float(row['FinalRank'])):>11} "
            f"{float(row['PaperMeanRank']):>10.2f} "
            f"{int(row['PaperFinalRank']):>11d} "
            f"{float(row['MeanRankDelta']):>+12.5f}"
        )

    print("-" * 108)
    print(f"Processed summary : {SUMMARY_PATH}")
    print(f"Table 7 CSV       : {TABLE7_PATH}")
    print(f"Comparison report : {COMPARISON_PATH}")
    print("H5f RESULT: COMPLETE")
    print("Next: H5g Table 8 Wilcoxon rank-sum reproduction.")
    print("=" * 108)


def main() -> None:
    rows = load_raw()
    summary = summarize(rows)
    rank_summary = build_rank_summary(summary)

    write_summary(summary)
    write_table7(summary, rank_summary)
    write_comparison(rank_summary)
    print_console(rank_summary)


if __name__ == "__main__":
    main()
