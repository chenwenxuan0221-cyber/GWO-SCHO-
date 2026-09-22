"""H6d - SCHO Tables 11/12 Wilcoxon rank-sum reproduction.

Reads
-----
results/raw/scho_scalability_h6b_runs.csv

Writes
------
report/tables/H6_table11_D100_wilcoxon.csv
report/tables/H6_table12_D500_wilcoxon.csv
report/tables/H6_tables11_12_wlt_summary.csv
report/H6_tables11_12_comparison.md

Protocol
--------
H6_SCALABILITY_V1
- 9 algorithms
- F1-F13
- D = 100, 500
- 30 independent runs
- N = 30
- MaxIter = 500

Statistical test
----------------
SCHO vs each comparator independently on each function:
- two-sided Wilcoxon rank-sum / Mann-Whitney U
- alpha = 0.05
- scipy.stats.mannwhitneyu(..., method="asymptotic",
  use_continuity=True)

This is a project-controlled statistical implementation and is not claimed
to be bitwise-equivalent to MATLAB ranksum.

Symbol convention
-----------------
"+" : SCHO significantly better (lower pooled mean rank; minimization)
"-" : SCHO significantly worse
"~" : no significant difference

Paper W|L|T anchors are transcribed from Tables 11 and 12 of:
J. Bai et al., "A Sinh Cosh optimizer", Knowledge-Based Systems 282 (2023)
111081.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu, rankdata


PROTOCOL_ID = "H6_SCALABILITY_V1"
ALPHA = 0.05

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
COMPARATORS = tuple(a for a in ALGORITHM_ORDER if a != "SCHO")
FUNCTIONS = tuple(f"F{i}" for i in range(1, 14))
DIMS = (100, 500)
N_RUNS = 30
POPULATION = 30
MAX_ITER = 500

EXPECTED_ROWS = (
    len(ALGORITHM_ORDER) * len(FUNCTIONS) * len(DIMS) * N_RUNS
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "scho_scalability_h6b_runs.csv"
)
TABLE11_PATH = (
    PROJECT_ROOT
    / "report"
    / "tables"
    / "H6_table11_D100_wilcoxon.csv"
)
TABLE12_PATH = (
    PROJECT_ROOT
    / "report"
    / "tables"
    / "H6_table12_D500_wilcoxon.csv"
)
WLT_PATH = (
    PROJECT_ROOT
    / "report"
    / "tables"
    / "H6_tables11_12_wlt_summary.csv"
)
COMPARISON_PATH = (
    PROJECT_ROOT
    / "report"
    / "H6_tables11_12_comparison.md"
)

# Paper aggregate W|L|T anchors.
PAPER_WLT = {
    100: {
        "GWO": (10, 3, 0),
        "ALO": (13, 0, 0),
        "SCA": (13, 0, 0),
        "SSA": (12, 1, 0),
        "AOA": (9, 1, 3),
        "RSA": (5, 2, 6),
        "SHO": (10, 1, 2),
        "GJO": (9, 3, 1),
    },
    500: {
        "GWO": (10, 3, 0),
        "ALO": (12, 1, 0),
        "SCA": (13, 0, 0),
        "SSA": (13, 0, 0),
        "AOA": (11, 1, 1),
        "RSA": (5, 2, 6),
        "SHO": (9, 2, 2),
        "GJO": (9, 4, 0),
    },
}


def function_number(name: str) -> int:
    return int(name[1:])


def expected_optimizer_seed(run: int) -> int:
    return 999 + run


def expected_objective_seed(dim: int, function_name: str, run: int) -> int:
    return 7_000_000 + dim * 10_000 + function_number(function_name) * 100 + run


def load_raw() -> list[dict[str, str]]:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw H6 dataset not found: {RAW_PATH}")

    with RAW_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise RuntimeError("Raw H6 dataset is empty.")

    if len(rows) != EXPECTED_ROWS:
        raise RuntimeError(
            f"Raw row count={len(rows)}; expected {EXPECTED_ROWS}"
        )

    required = {
        "ProtocolID",
        "Algorithm",
        "Function",
        "Dim",
        "Run",
        "OptimizerSeed",
        "ObjectiveSeed",
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
            raise RuntimeError(
                f"Protocol mismatch: {row['ProtocolID']!r}"
            )

        algorithm = row["Algorithm"]
        function_name = row["Function"]
        dim = int(row["Dim"])
        run = int(row["Run"])

        if algorithm not in ALGORITHM_ORDER:
            raise RuntimeError(f"Unexpected algorithm: {algorithm}")
        if function_name not in FUNCTIONS:
            raise RuntimeError(f"Unexpected function: {function_name}")
        if dim not in DIMS:
            raise RuntimeError(f"Unexpected dimension: {dim}")
        if not 1 <= run <= N_RUNS:
            raise RuntimeError(
                f"Invalid run: {algorithm}/{function_name}/D={dim}/run={run}"
            )

        key = (algorithm, function_name, dim, run)
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
        if int(row["OptimizerSeed"]) != expected_optimizer_seed(run):
            raise RuntimeError(f"Optimizer seed mismatch at {key}")

        formal_objective_seed = expected_objective_seed(
            dim, function_name, run
        )
        if int(row["ObjectiveSeed"]) != formal_objective_seed:
            raise RuntimeError(f"Objective seed mismatch at {key}")

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


def group_scores(
    rows: list[dict[str, str]],
) -> dict[tuple[int, str, str], np.ndarray]:
    grouped: dict[tuple[int, str, str], list[float]] = {}

    for row in rows:
        key = (
            int(row["Dim"]),
            row["Algorithm"],
            row["Function"],
        )
        grouped.setdefault(key, []).append(float(row["BestScore"]))

    out: dict[tuple[int, str, str], np.ndarray] = {}

    for dim in DIMS:
        for algorithm in ALGORITHM_ORDER:
            for function_name in FUNCTIONS:
                key = (dim, algorithm, function_name)
                vals = grouped.get(key, [])
                arr = np.asarray(vals, dtype=float)

                if arr.size != N_RUNS:
                    raise RuntimeError(
                        f"{key} has {arr.size} runs; expected {N_RUNS}"
                    )

                if not np.all(np.isfinite(arr)):
                    raise RuntimeError(f"Non-finite grouped scores at {key}")

                out[key] = arr

    return out


def compare_one(
    scho_scores: np.ndarray,
    other_scores: np.ndarray,
) -> tuple[float, float, float, str]:
    result = mannwhitneyu(
        scho_scores,
        other_scores,
        alternative="two-sided",
        method="asymptotic",
        use_continuity=True,
    )

    u_stat = float(result.statistic)
    p_value = float(result.pvalue)

    pooled = np.concatenate([scho_scores, other_scores])
    ranks = rankdata(pooled, method="average")

    n_scho = len(scho_scores)
    scho_mean_rank = float(np.mean(ranks[:n_scho]))
    other_mean_rank = float(np.mean(ranks[n_scho:]))
    mean_rank_delta = scho_mean_rank - other_mean_rank

    if p_value >= ALPHA:
        symbol = "~"
    elif scho_mean_rank < other_mean_rank:
        symbol = "+"
    elif scho_mean_rank > other_mean_rank:
        symbol = "-"
    else:
        symbol = "~"

    return u_stat, p_value, mean_rank_delta, symbol


def build_results(
    grouped: dict[tuple[int, str, str], np.ndarray],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for dim in DIMS:
        for comparator in COMPARATORS:
            for function_name in FUNCTIONS:
                scho_scores = grouped[(dim, "SCHO", function_name)]
                other_scores = grouped[(dim, comparator, function_name)]

                u_stat, p_value, mean_rank_delta, symbol = compare_one(
                    scho_scores,
                    other_scores,
                )

                rows.append(
                    {
                        "Dimension": dim,
                        "Comparator": comparator,
                        "Function": function_name,
                        "U": u_stat,
                        "PValue": p_value,
                        "SCHO_Mean": float(np.mean(scho_scores)),
                        "Comparator_Mean": float(np.mean(other_scores)),
                        "SCHO_Median": float(np.median(scho_scores)),
                        "Comparator_Median": float(np.median(other_scores)),
                        "MeanRankDelta_SCHO_minus_Comparator": mean_rank_delta,
                        "Symbol": symbol,
                    }
                )

    expected = len(DIMS) * len(COMPARATORS) * len(FUNCTIONS)
    if len(rows) != expected:
        raise RuntimeError(
            f"Wilcoxon result rows={len(rows)}; expected {expected}"
        )

    return rows


def summarize_wlt(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    summary: list[dict[str, object]] = []

    for dim in DIMS:
        for comparator in COMPARATORS:
            sub = [
                r
                for r in rows
                if int(r["Dimension"]) == dim
                and r["Comparator"] == comparator
            ]

            if len(sub) != len(FUNCTIONS):
                raise RuntimeError(
                    f"D={dim}/{comparator}: "
                    f"rows={len(sub)}, expected {len(FUNCTIONS)}"
                )

            wins = sum(r["Symbol"] == "+" for r in sub)
            losses = sum(r["Symbol"] == "-" for r in sub)
            ties = sum(r["Symbol"] == "~" for r in sub)

            if wins + losses + ties != len(FUNCTIONS):
                raise RuntimeError(
                    f"D={dim}/{comparator}: invalid W/L/T total"
                )

            paper_w, paper_l, paper_t = PAPER_WLT[dim][comparator]

            summary.append(
                {
                    "Dimension": dim,
                    "Comparator": comparator,
                    "Wins": wins,
                    "Losses": losses,
                    "Ties": ties,
                    "PaperWins": paper_w,
                    "PaperLosses": paper_l,
                    "PaperTies": paper_t,
                    "DeltaWins": wins - paper_w,
                    "DeltaLosses": losses - paper_l,
                    "DeltaTies": ties - paper_t,
                    "ExactWLTMatch": (
                        wins == paper_w
                        and losses == paper_l
                        and ties == paper_t
                    ),
                }
            )

    return summary


def write_result_table(
    path: Path,
    rows: list[dict[str, object]],
    dim: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "Dimension",
        "Comparator",
        "Function",
        "U",
        "PValue",
        "SCHO_Mean",
        "Comparator_Mean",
        "SCHO_Median",
        "Comparator_Median",
        "MeanRankDelta_SCHO_minus_Comparator",
        "Symbol",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for row in rows:
            if int(row["Dimension"]) != dim:
                continue

            writer.writerow(
                {
                    "Dimension": dim,
                    "Comparator": row["Comparator"],
                    "Function": row["Function"],
                    "U": repr(float(row["U"])),
                    "PValue": repr(float(row["PValue"])),
                    "SCHO_Mean": repr(float(row["SCHO_Mean"])),
                    "Comparator_Mean": repr(
                        float(row["Comparator_Mean"])
                    ),
                    "SCHO_Median": repr(float(row["SCHO_Median"])),
                    "Comparator_Median": repr(
                        float(row["Comparator_Median"])
                    ),
                    "MeanRankDelta_SCHO_minus_Comparator": repr(
                        float(
                            row[
                                "MeanRankDelta_SCHO_minus_Comparator"
                            ]
                        )
                    ),
                    "Symbol": row["Symbol"],
                }
            )


def write_wlt_summary(
    summary: list[dict[str, object]],
) -> None:
    WLT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "Dimension",
        "Comparator",
        "Wins",
        "Losses",
        "Ties",
        "PaperWins",
        "PaperLosses",
        "PaperTies",
        "DeltaWins",
        "DeltaLosses",
        "DeltaTies",
        "ExactWLTMatch",
    ]

    with WLT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)


def write_comparison_report(
    summary: list[dict[str, object]],
) -> None:
    COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# H6d — SCHO Tables 11/12 Wilcoxon rank-sum reproduction",
        "",
        f"Protocol: `{PROTOCOL_ID}`",
        "",
        "Test: two-sided Mann–Whitney U / Wilcoxon rank-sum via "
        "SciPy `mannwhitneyu`, asymptotic method, continuity correction, "
        f"alpha={ALPHA}.",
        "",
        "This is a project-controlled statistical implementation and is "
        "not claimed to reproduce MATLAB `ranksum` bitwise.",
        "",
        "Symbol convention: `+` SCHO significantly better, `-` SCHO "
        "significantly worse, `~` no significant difference.",
        "",
        "Paper comparison below uses the aggregate W|L|T rows printed in "
        "Tables 11 and 12.",
    ]

    for dim in DIMS:
        lines.extend(
            [
                "",
                f"## D = {dim}",
                "",
                "| Comparator | Reproduced W|L|T | Paper W|L|T | "
                "Delta W|L|T | Exact match |",
                "|---|---:|---:|---:|:---:|",
            ]
        )

        sub = [
            r for r in summary if int(r["Dimension"]) == dim
        ]

        for row in sub:
            repro = (
                f"{row['Wins']}|{row['Losses']}|{row['Ties']}"
            )
            paper = (
                f"{row['PaperWins']}|"
                f"{row['PaperLosses']}|"
                f"{row['PaperTies']}"
            )
            delta = (
                f"{int(row['DeltaWins']):+d}|"
                f"{int(row['DeltaLosses']):+d}|"
                f"{int(row['DeltaTies']):+d}"
            )
            exact = "YES" if bool(row["ExactWLTMatch"]) else "NO"

            lines.append(
                f"| {row['Comparator']} | {repro} | {paper} | "
                f"{delta} | {exact} |"
            )

        exact_count = sum(bool(r["ExactWLTMatch"]) for r in sub)
        lines.extend(
            [
                "",
                f"Exact aggregate W|L|T matches: **{exact_count}/8**.",
            ]
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- The paper does not publish its random seeds; H6 uses the "
            "project reproducibility convention.",
            "- NumPy RNG streams are not MATLAB RNG streams.",
            "- Several comparator implementations are source-structured "
            "rather than MATLAB-bitwise reconstructions.",
            "- Therefore aggregate agreement/disagreement is interpreted "
            "as reproduction evidence, not as a tuning target.",
            "- No optimizer is modified or rerun by this analysis.",
            "",
        ]
    )

    COMPARISON_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def print_summary(
    summary: list[dict[str, object]],
) -> None:
    print("=" * 112)
    print("H6d - SCHO Tables 11/12 Wilcoxon rank-sum reproduction")
    print("=" * 112)
    print(f"Raw dataset : {RAW_PATH}")
    print(f"Protocol    : {PROTOCOL_ID}")
    print(f"Alpha       : {ALPHA}")
    print("No optimizer run is executed.")

    for dim in DIMS:
        print("-" * 112)
        print(f"D = {dim}")
        print(
            f"{'Comparator':<12} "
            f"{'Repro W|L|T':>14} "
            f"{'Paper W|L|T':>14} "
            f"{'Exact':>8}"
        )
        print("-" * 54)

        sub = [
            r for r in summary if int(r["Dimension"]) == dim
        ]

        for row in sub:
            repro = (
                f"{row['Wins']}|{row['Losses']}|{row['Ties']}"
            )
            paper = (
                f"{row['PaperWins']}|"
                f"{row['PaperLosses']}|"
                f"{row['PaperTies']}"
            )
            exact = "YES" if bool(row["ExactWLTMatch"]) else "NO"

            print(
                f"{str(row['Comparator']):<12} "
                f"{repro:>14} "
                f"{paper:>14} "
                f"{exact:>8}"
            )

        exact_count = sum(bool(r["ExactWLTMatch"]) for r in sub)
        print(f"Exact W|L|T matches: {exact_count}/8")

    print("-" * 112)
    print(f"Table 11 CSV : {TABLE11_PATH}")
    print(f"Table 12 CSV : {TABLE12_PATH}")
    print(f"W/L/T summary: {WLT_PATH}")
    print(f"Comparison   : {COMPARISON_PATH}")
    print("=" * 112)
    print("H6d RESULT: COMPLETE")
    print("Next: H6e Section 3.1.4 final comparison/freeze.")


def main() -> None:
    rows = load_raw()
    grouped = group_scores(rows)
    results = build_results(grouped)
    summary = summarize_wlt(results)

    write_result_table(TABLE11_PATH, results, 100)
    write_result_table(TABLE12_PATH, results, 500)
    write_wlt_summary(summary)
    write_comparison_report(summary)
    print_summary(summary)


if __name__ == "__main__":
    main()
