"""H6c - SCHO Section 3.1.4 Tables 9/10 + Friedman ranking.

Reads:
    results/raw/scho_scalability_h6b_runs.csv

Writes:
    results/processed/scho_scalability_h6c_summary.csv
    report/tables/H6_table9_D100_reproduction.csv
    report/tables/H6_table10_D500_reproduction.csv
    report/tables/H6_friedman_ranking.csv
    report/H6_tables9_10_comparison.md

Statistics:
    Best    = minimum final best score over 30 runs
    Average = arithmetic mean over 30 runs
    STD     = sample standard deviation (ddof=1), matching MATLAB std default

Ranking:
    All F1-F13 are minimization problems.
    Per-function rank is by Average ascending.
    Exact ties receive average ranks.
    MeanRank is averaged across 13 functions.
    FinalRank is the ascending rank of MeanRank.

Friedman:
    One block per benchmark function (13 blocks).
    Treatments are the nine algorithms.
    Input value per block/treatment is the 30-run Average.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.stats import friedmanchisquare


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
FUNCTIONS = tuple(f"F{i}" for i in range(1, 14))
DIMS = (100, 500)
N_RUNS = 30
POPULATION = 30
MAX_ITER = 500
EXPECTED_ROWS = (
    len(ALGORITHM_ORDER) * len(FUNCTIONS) * len(DIMS) * N_RUNS
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "results" / "raw" / "scho_scalability_h6b_runs.csv"
SUMMARY_PATH = (
    PROJECT_ROOT / "results" / "processed" / "scho_scalability_h6c_summary.csv"
)
TABLE_PATH = {
    100: PROJECT_ROOT / "report" / "tables" / "H6_table9_D100_reproduction.csv",
    500: PROJECT_ROOT / "report" / "tables" / "H6_table10_D500_reproduction.csv",
}
FRIEDMAN_PATH = PROJECT_ROOT / "report" / "tables" / "H6_friedman_ranking.csv"
COMPARISON_PATH = PROJECT_ROOT / "report" / "H6_tables9_10_comparison.md"

PAPER_MEAN_RANK = {
    100: {
        "SCHO": 1.85,
        "GWO": 4.15,
        "ALO": 7.69,
        "SCA": 8.69,
        "SSA": 6.54,
        "AOA": 4.77,
        "RSA": 2.85,
        "SHO": 3.31,
        "GJO": 4.00,
    },
    500: {
        "SCHO": 2.00,
        "GWO": 4.62,
        "ALO": 7.54,
        "SCA": 8.23,
        "SSA": 6.69,
        "AOA": 5.31,
        "RSA": 2.54,
        "SHO": 3.38,
        "GJO": 4.00,
    },
}

PAPER_FINAL_ORDER = (
    "SCHO",
    "RSA",
    "SHO",
    "GJO",
    "GWO",
    "AOA",
    "SSA",
    "ALO",
    "SCA",
)
PAPER_FINAL_RANK = {
    algorithm: rank
    for rank, algorithm in enumerate(PAPER_FINAL_ORDER, start=1)
}


def function_number(name: str) -> int:
    return int(name[1:])


def objective_seed(dim: int, function_name: str, run: int) -> int:
    return 7_000_000 + dim * 10_000 + 100 * function_number(function_name) + run


def average_ranks(values: Iterable[float]) -> np.ndarray:
    """Ascending average ranks without requiring SciPy rankdata."""
    a = np.asarray(list(values), dtype=float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)

    i = 0
    while i < len(a):
        j = i + 1
        while j < len(a) and a[order[j]] == a[order[i]]:
            j += 1

        avg_rank = ((i + 1) + j) / 2.0
        ranks[order[i:j]] = avg_rank
        i = j

    return ranks


def load_raw() -> list[dict[str, str]]:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw H6b dataset not found: {RAW_PATH}")

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
        "Dim",
        "Run",
        "OptimizerSeed",
        "ObjectiveSeed",
        "FormalObjectiveSeed",
        "Population",
        "MaxIter",
        "BestScore",
        "Provenance",
    }
    missing = required - set(rows[0])
    if missing:
        raise RuntimeError(f"Missing raw columns: {sorted(missing)}")

    seen: set[tuple[str, str, int, int]] = set()

    for row in rows:
        if row["ProtocolID"] != PROTOCOL_ID:
            raise RuntimeError(f"Protocol mismatch: {row['ProtocolID']!r}")

        algorithm = row["Algorithm"]
        function_name = row["Function"]
        dim = int(row["Dim"])
        run = int(row["Run"])
        key = (algorithm, function_name, dim, run)

        if algorithm not in ALGORITHM_ORDER:
            raise RuntimeError(f"Unexpected algorithm: {algorithm}")
        if function_name not in FUNCTIONS:
            raise RuntimeError(f"Unexpected function: {function_name}")
        if dim not in DIMS:
            raise RuntimeError(f"Unexpected dimension: {dim}")
        if not 1 <= run <= N_RUNS:
            raise RuntimeError(f"Invalid run at {key}")
        if key in seen:
            raise RuntimeError(f"Duplicate raw key: {key}")
        seen.add(key)

        score = float(row["BestScore"])
        if not math.isfinite(score):
            raise RuntimeError(f"Non-finite BestScore at {key}")

        if int(row["Population"]) != POPULATION:
            raise RuntimeError(f"Population mismatch at {key}")
        if int(row["MaxIter"]) != MAX_ITER:
            raise RuntimeError(f"MaxIter mismatch at {key}")
        if int(row["OptimizerSeed"]) != 999 + run:
            raise RuntimeError(f"Optimizer seed mismatch at {key}")

        expected_obj_seed = objective_seed(dim, function_name, run)
        if int(row["ObjectiveSeed"]) != expected_obj_seed:
            raise RuntimeError(f"Objective seed mismatch at {key}")
        if int(row["FormalObjectiveSeed"]) != expected_obj_seed:
            raise RuntimeError(f"Formal objective seed mismatch at {key}")

        expected_provenance = (
            "REUSED_SCHO_H3C" if algorithm == "SCHO" else "H6_NEW_RUN"
        )
        if row["Provenance"] != expected_provenance:
            raise RuntimeError(
                f"Provenance mismatch at {key}: {row['Provenance']!r}"
            )

    expected_keys = {
        (algorithm, function_name, dim, run)
        for algorithm in ALGORITHM_ORDER
        for function_name in FUNCTIONS
        for dim in DIMS
        for run in range(1, N_RUNS + 1)
    }
    if seen != expected_keys:
        raise RuntimeError(
            "Raw key coverage mismatch: "
            f"missing={len(expected_keys - seen)}, "
            f"extra={len(seen - expected_keys)}"
        )

    return rows


def stable_sample_std(values: np.ndarray) -> float:
    """Sample STD (ddof=1) with scale normalization to avoid overflow."""
    a = np.asarray(values, dtype=float)
    scale = float(np.max(np.abs(a)))
    if scale == 0.0:
        return 0.0
    return float(np.std(a / scale, ddof=1) * scale)


def summarize(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[int, str, str], list[float]] = {}

    for row in rows:
        key = (
            int(row["Dim"]),
            row["Function"],
            row["Algorithm"],
        )
        grouped.setdefault(key, []).append(float(row["BestScore"]))

    summary: list[dict[str, object]] = []

    for dim in DIMS:
        for function_name in FUNCTIONS:
            per_function: list[dict[str, object]] = []

            for algorithm in ALGORITHM_ORDER:
                scores = np.asarray(
                    grouped[(dim, function_name, algorithm)],
                    dtype=float,
                )
                if scores.size != N_RUNS:
                    raise RuntimeError(
                        f"{algorithm}/{function_name}/D={dim} has "
                        f"{scores.size} runs; expected {N_RUNS}"
                    )

                per_function.append(
                    {
                        "Dimension": dim,
                        "Function": function_name,
                        "Algorithm": algorithm,
                        "Runs": int(scores.size),
                        "Best": float(np.min(scores)),
                        "Average": float(np.mean(scores)),
                        "STD": stable_sample_std(scores),
                    }
                )

            ranks = average_ranks(r["Average"] for r in per_function)
            for row, rank in zip(per_function, ranks):
                row["Rank"] = float(rank)
                summary.append(row)

    return summary


def build_rank_summary(
    summary: list[dict[str, object]],
) -> dict[int, list[dict[str, object]]]:
    result: dict[int, list[dict[str, object]]] = {}

    for dim in DIMS:
        out: list[dict[str, object]] = []
        dim_rows = [r for r in summary if int(r["Dimension"]) == dim]

        for algorithm in ALGORITHM_ORDER:
            alg_rows = [r for r in dim_rows if r["Algorithm"] == algorithm]
            if len(alg_rows) != len(FUNCTIONS):
                raise RuntimeError(
                    f"{algorithm}/D={dim}: function count={len(alg_rows)}, "
                    f"expected {len(FUNCTIONS)}"
                )

            mean_rank = float(
                np.mean([float(r["Rank"]) for r in alg_rows])
            )
            out.append(
                {
                    "Dimension": dim,
                    "Algorithm": algorithm,
                    "MeanRank": mean_rank,
                }
            )

        final_ranks = average_ranks(r["MeanRank"] for r in out)

        for row, final_rank in zip(out, final_ranks):
            algorithm = str(row["Algorithm"])
            row["FinalRank"] = float(final_rank)
            row["PaperMeanRank"] = float(PAPER_MEAN_RANK[dim][algorithm])
            row["PaperFinalRank"] = int(PAPER_FINAL_RANK[algorithm])
            row["MeanRankDelta"] = (
                float(row["MeanRank"]) - float(row["PaperMeanRank"])
            )
            row["FinalRankMatch"] = (
                float(row["FinalRank"]) == float(row["PaperFinalRank"])
            )

        result[dim] = out

    return result


def compute_friedman(
    summary: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for dim in DIMS:
        vectors: dict[str, list[float]] = {
            algorithm: [] for algorithm in ALGORITHM_ORDER
        }

        for function_name in FUNCTIONS:
            function_rows = {
                str(r["Algorithm"]): r
                for r in summary
                if int(r["Dimension"]) == dim
                and r["Function"] == function_name
            }
            if set(function_rows) != set(ALGORITHM_ORDER):
                raise RuntimeError(
                    f"Friedman coverage mismatch at D={dim}/{function_name}"
                )

            for algorithm in ALGORITHM_ORDER:
                vectors[algorithm].append(
                    float(function_rows[algorithm]["Average"])
                )

        stat, pvalue = friedmanchisquare(
            *(vectors[algorithm] for algorithm in ALGORITHM_ORDER)
        )

        rows.append(
            {
                "Dimension": dim,
                "Blocks": len(FUNCTIONS),
                "Algorithms": len(ALGORITHM_ORDER),
                "Statistic": float(stat),
                "PValue": float(pvalue),
                "Alpha": 0.05,
                "RejectH0": bool(pvalue < 0.05),
            }
        )

    return rows


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_outputs(
    summary: list[dict[str, object]],
    rank_summary: dict[int, list[dict[str, object]]],
    friedman_rows: list[dict[str, object]],
) -> None:
    write_csv(
        SUMMARY_PATH,
        [
            "Dimension",
            "Function",
            "Algorithm",
            "Runs",
            "Best",
            "Average",
            "STD_sample_ddof1",
            "Rank_by_Average",
        ],
        [
            {
                "Dimension": int(r["Dimension"]),
                "Function": str(r["Function"]),
                "Algorithm": str(r["Algorithm"]),
                "Runs": int(r["Runs"]),
                "Best": repr(float(r["Best"])),
                "Average": repr(float(r["Average"])),
                "STD_sample_ddof1": repr(float(r["STD"])),
                "Rank_by_Average": repr(float(r["Rank"])),
            }
            for r in summary
        ],
    )

    for dim in DIMS:
        table_rows: list[dict[str, object]] = []
        rank_map = {
            str(r["Algorithm"]): r
            for r in rank_summary[dim]
        }

        for r in summary:
            if int(r["Dimension"]) != dim:
                continue
            rr = rank_map[str(r["Algorithm"])]
            table_rows.append(
                {
                    "Function": str(r["Function"]),
                    "Algorithm": str(r["Algorithm"]),
                    "Runs": int(r["Runs"]),
                    "Best": repr(float(r["Best"])),
                    "Average": repr(float(r["Average"])),
                    "STD_sample_ddof1": repr(float(r["STD"])),
                    "Rank_by_Average": repr(float(r["Rank"])),
                    "MeanRank_13": repr(float(rr["MeanRank"])),
                    "FinalRank": repr(float(rr["FinalRank"])),
                    "PaperMeanRank": repr(float(rr["PaperMeanRank"])),
                    "PaperFinalRank": int(rr["PaperFinalRank"]),
                    "MeanRankDelta": repr(float(rr["MeanRankDelta"])),
                    "FinalRankMatch": bool(rr["FinalRankMatch"]),
                }
            )

        write_csv(
            TABLE_PATH[dim],
            [
                "Function",
                "Algorithm",
                "Runs",
                "Best",
                "Average",
                "STD_sample_ddof1",
                "Rank_by_Average",
                "MeanRank_13",
                "FinalRank",
                "PaperMeanRank",
                "PaperFinalRank",
                "MeanRankDelta",
                "FinalRankMatch",
            ],
            table_rows,
        )

    write_csv(
        FRIEDMAN_PATH,
        [
            "Dimension",
            "Blocks",
            "Algorithms",
            "Statistic",
            "PValue",
            "Alpha",
            "RejectH0",
        ],
        friedman_rows,
    )


def format_rank(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}"


def write_report(
    rank_summary: dict[int, list[dict[str, object]]],
    friedman_rows: list[dict[str, object]],
) -> None:
    lines: list[str] = [
        "# H6c - SCHO Tables 9/10 scalability reproduction",
        "",
        f"Protocol: `{PROTOCOL_ID}`",
        "",
        "Statistics: Best=min, Average=arithmetic mean, "
        "STD=sample standard deviation (ddof=1).",
        "",
        "Ranking: per-function rank by Average ascending; exact ties use "
        "average ranks; MeanRank is the average over F1-F13.",
        "",
        "Paper mean-rank values are validation anchors only and were not "
        "used to tune any algorithm.",
    ]

    for dim in DIMS:
        lines.extend(
            [
                "",
                f"## D = {dim}",
                "",
                "| Algorithm | Reproduced Mean Rank | Paper Mean Rank | Delta | "
                "Reproduced Final Rank | Paper Final Rank | Match |",
                "|---|---:|---:|---:|---:|---:|:---:|",
            ]
        )

        sorted_rows = sorted(
            rank_summary[dim],
            key=lambda r: float(r["MeanRank"]),
        )
        for row in sorted_rows:
            lines.append(
                f"| {row['Algorithm']} | "
                f"{float(row['MeanRank']):.5f} | "
                f"{float(row['PaperMeanRank']):.2f} | "
                f"{float(row['MeanRankDelta']):+.5f} | "
                f"{format_rank(float(row['FinalRank']))} | "
                f"{int(row['PaperFinalRank'])} | "
                f"{'YES' if bool(row['FinalRankMatch']) else 'NO'} |"
            )

        reproduced_order = ", ".join(
            str(r["Algorithm"]) for r in sorted_rows
        )
        lines.extend(
            [
                "",
                f"Reproduced order: `{reproduced_order}`",
                "",
                f"Paper order: `{', '.join(PAPER_FINAL_ORDER)}`",
            ]
        )

        fr = next(r for r in friedman_rows if int(r["Dimension"]) == dim)
        lines.extend(
            [
                "",
                "Friedman test across the 13 function-level Average values:",
                "",
                f"- statistic = `{float(fr['Statistic']):.12g}`",
                f"- p-value = `{float(fr['PValue']):.12g}`",
                f"- alpha = `{float(fr['Alpha']):.2f}`",
                f"- reject equal-performance null = "
                f"`{bool(fr['RejectH0'])}`",
            ]
        )

    lines.extend(
        [
            "",
            "## Scope",
            "",
            "H6c does not rerun any optimizer. It analyzes the frozen H6b "
            "7020-row raw dataset only.",
            "",
            "Next: H6d Tables 11/12 two-sided Wilcoxon rank-sum analysis.",
        ]
    )

    COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_console(
    rank_summary: dict[int, list[dict[str, object]]],
    friedman_rows: list[dict[str, object]],
) -> None:
    print("=" * 112)
    print("H6c - SCHO Tables 9/10 + Friedman ranking")
    print("=" * 112)
    print(f"Raw dataset : {RAW_PATH}")
    print(f"Rows        : {EXPECTED_ROWS}")
    print("No optimizer run is executed.")
    print("-" * 112)

    for dim in DIMS:
        print(f"D = {dim}")
        print(
            f"{'Alg':<5} {'MeanRank':>12} {'FinalRank':>11} "
            f"{'PaperMR':>10} {'PaperRank':>11} {'DeltaMR':>12} {'Match':>7}"
        )
        print("-" * 82)

        sorted_rows = sorted(
            rank_summary[dim],
            key=lambda r: float(r["MeanRank"]),
        )
        for row in sorted_rows:
            print(
                f"{str(row['Algorithm']):<5} "
                f"{float(row['MeanRank']):>12.5f} "
                f"{format_rank(float(row['FinalRank'])):>11} "
                f"{float(row['PaperMeanRank']):>10.2f} "
                f"{int(row['PaperFinalRank']):>11d} "
                f"{float(row['MeanRankDelta']):>+12.5f} "
                f"{('YES' if bool(row['FinalRankMatch']) else 'NO'):>7}"
            )

        fr = next(r for r in friedman_rows if int(r["Dimension"]) == dim)
        print(
            f"Friedman: statistic={float(fr['Statistic']):.8g}, "
            f"p={float(fr['PValue']):.8g}, "
            f"reject_H0={bool(fr['RejectH0'])}"
        )
        print("-" * 112)

    print(f"Processed summary : {SUMMARY_PATH}")
    print(f"Table 9 CSV       : {TABLE_PATH[100]}")
    print(f"Table 10 CSV      : {TABLE_PATH[500]}")
    print(f"Friedman CSV      : {FRIEDMAN_PATH}")
    print(f"Comparison report : {COMPARISON_PATH}")
    print("=" * 112)
    print("H6c RESULT: COMPLETE")
    print("Next: H6d Tables 11/12 Wilcoxon rank-sum reproduction.")


def main() -> None:
    rows = load_raw()
    summary = summarize(rows)
    rank_summary = build_rank_summary(summary)
    friedman_rows = compute_friedman(summary)
    write_outputs(summary, rank_summary, friedman_rows)
    write_report(rank_summary, friedman_rows)
    print_console(rank_summary, friedman_rows)


if __name__ == "__main__":
    main()
