"""H5g - SCHO Table 8 Wilcoxon rank-sum reproduction.

Reads
-----
results/raw/scho_classical_h5_runs.csv

Writes
------
report/tables/H5_table8_wilcoxon.csv
report/H5_table8_comparison.md

Test
----
SCHO vs each comparator independently on each F1-F23 function.

- 30 final-best scores vs 30 final-best scores
- two-sided Wilcoxon rank-sum / Mann-Whitney U test
- alpha = 0.05
- SciPy implementation:
      scipy.stats.mannwhitneyu(
          x, y,
          alternative="two-sided",
          method="asymptotic",
          use_continuity=True,
      )

Why Mann-Whitney U?
-------------------
It is the Wilcoxon rank-sum test and handles ties, which occur in these
benchmark results. This is a project-controlled statistical implementation;
it does not claim bitwise equivalence to MATLAB ranksum.

Symbol convention
-----------------
"+" : SCHO significantly better (lower mean rank; minimization)
"-" : SCHO significantly worse
"~" : no significant difference

Paper Table 8 W|L|T anchors:
    GWO 12|8|3
    ALO 14|6|3
    SCA 21|2|0
    SSA 18|5|0
    AOA 18|2|3
    RSA 11|2|10
    SHO 13|3|7
    GJO 14|3|6
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu, rankdata


PROTOCOL_ID = "H5_CLASSICAL_V1"
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
FUNCTIONS = tuple(f"F{i}" for i in range(1, 24))
N_RUNS = 30
EXPECTED_ROWS = len(ALGORITHM_ORDER) * len(FUNCTIONS) * N_RUNS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "results" / "raw" / "scho_classical_h5_runs.csv"
TABLE8_PATH = PROJECT_ROOT / "report" / "tables" / "H5_table8_wilcoxon.csv"
COMPARISON_PATH = PROJECT_ROOT / "report" / "H5_table8_comparison.md"

PAPER_WLT = {
    "GWO": (12, 8, 3),
    "ALO": (14, 6, 3),
    "SCA": (21, 2, 0),
    "SSA": (18, 5, 0),
    "AOA": (18, 2, 3),
    "RSA": (11, 2, 10),
    "SHO": (13, 3, 7),
    "GJO": (14, 3, 6),
}


def load_raw() -> list[dict[str, str]]:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw H5 dataset not found: {RAW_PATH}")

    with RAW_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != EXPECTED_ROWS:
        raise RuntimeError(
            f"Raw row count={len(rows)}; expected {EXPECTED_ROWS}"
        )

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

    return rows


def group_scores(
    rows: list[dict[str, str]],
) -> dict[tuple[str, str], np.ndarray]:
    grouped: dict[tuple[str, str], list[float]] = {}

    for row in rows:
        key = (row["Algorithm"], row["Function"])
        grouped.setdefault(key, []).append(float(row["BestScore"]))

    out: dict[tuple[str, str], np.ndarray] = {}

    for key, vals in grouped.items():
        arr = np.asarray(vals, dtype=float)
        if arr.size != N_RUNS:
            raise RuntimeError(
                f"{key} has {arr.size} runs; expected {N_RUNS}"
            )
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
    scho_mean_rank = float(np.mean(ranks[: len(scho_scores)]))
    other_mean_rank = float(np.mean(ranks[len(scho_scores) :]))

    if p_value >= ALPHA:
        symbol = "~"
    elif scho_mean_rank < other_mean_rank:
        symbol = "+"
    elif scho_mean_rank > other_mean_rank:
        symbol = "-"
    else:
        # This should be extremely rare; with equal mean ranks the
        # two-sided test should normally not be significant.
        symbol = "~"

    return u_stat, p_value, scho_mean_rank - other_mean_rank, symbol


def build_results(
    grouped: dict[tuple[str, str], np.ndarray],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for comparator in COMPARATORS:
        for function_name in FUNCTIONS:
            scho_scores = grouped[("SCHO", function_name)]
            other_scores = grouped[(comparator, function_name)]

            u_stat, p_value, mean_rank_delta, symbol = compare_one(
                scho_scores,
                other_scores,
            )

            rows.append(
                {
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

    return rows


def summarize_wlt(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    summary: list[dict[str, object]] = []

    for comparator in COMPARATORS:
        sub = [r for r in rows if r["Comparator"] == comparator]

        wins = sum(r["Symbol"] == "+" for r in sub)
        losses = sum(r["Symbol"] == "-" for r in sub)
        ties = sum(r["Symbol"] == "~" for r in sub)

        if wins + losses + ties != 23:
            raise RuntimeError(
                f"{comparator}: invalid W/L/T total"
            )

        pw, pl, pt = PAPER_WLT[comparator]

        summary.append(
            {
                "Comparator": comparator,
                "Wins": wins,
                "Losses": losses,
                "Ties": ties,
                "PaperWins": pw,
                "PaperLosses": pl,
                "PaperTies": pt,
                "DeltaWins": wins - pw,
                "DeltaLosses": losses - pl,
                "DeltaTies": ties - pt,
            }
        )

    return summary


def write_csv(rows: list[dict[str, object]]) -> None:
    TABLE8_PATH.parent.mkdir(parents=True, exist_ok=True)

    fields = [
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

    with TABLE8_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_report(summary: list[dict[str, object]]) -> None:
    COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# H5g — SCHO Table 8 Wilcoxon rank-sum reproduction",
        "",
        (
            "Protocol: `H5_CLASSICAL_V1`; 30 final-best scores per "
            "algorithm/function; alpha = 0.05."
        ),
        "",
        (
            "Statistical implementation: two-sided Mann–Whitney U / "
            "Wilcoxon rank-sum via SciPy `mannwhitneyu`, asymptotic method "
            "with continuity correction. This is a project-controlled "
            "statistical implementation and does not claim bitwise MATLAB "
            "`ranksum` equivalence."
        ),
        "",
        (
            "Symbols: `+` = SCHO significantly better, `-` = SCHO "
            "significantly worse, `~` = no significant difference."
        ),
        "",
        "| Comparator | Reproduced W|L|T | Paper W|L|T | ΔW | ΔL | ΔT |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for r in summary:
        lines.append(
            f"| {r['Comparator']} | "
            f"{r['Wins']}|{r['Losses']}|{r['Ties']} | "
            f"{r['PaperWins']}|{r['PaperLosses']}|{r['PaperTies']} | "
            f"{r['DeltaWins']:+d} | "
            f"{r['DeltaLosses']:+d} | "
            f"{r['DeltaTies']:+d} |"
        )

    lines.extend(
        [
            "",
            (
                "No parameter tuning or post-hoc threshold adjustment is "
                "performed to force the reproduced W|L|T counts toward the "
                "paper anchors."
            ),
            "",
        ]
    )

    COMPARISON_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def print_console(summary: list[dict[str, object]]) -> None:
    print("=" * 104)
    print("H5g - SCHO Table 8 Wilcoxon rank-sum reproduction")
    print("=" * 104)
    print(f"Raw dataset : {RAW_PATH}")
    print(f"Alpha       : {ALPHA}")
    print(
        "Test        : scipy.stats.mannwhitneyu, two-sided, "
        "asymptotic, continuity correction"
    )
    print("Symbols     : + SCHO better | - SCHO worse | ~ no significant difference")
    print("-" * 104)
    print(
        f"{'Comparator':<12} "
        f"{'Reproduced W|L|T':>20} "
        f"{'Paper W|L|T':>16} "
        f"{'Delta W|L|T':>18}"
    )
    print("-" * 104)

    for r in summary:
        reproduced = f"{r['Wins']}|{r['Losses']}|{r['Ties']}"
        paper = f"{r['PaperWins']}|{r['PaperLosses']}|{r['PaperTies']}"
        delta = (
            f"{r['DeltaWins']:+d}|"
            f"{r['DeltaLosses']:+d}|"
            f"{r['DeltaTies']:+d}"
        )

        print(
            f"{r['Comparator']:<12} "
            f"{reproduced:>20} "
            f"{paper:>16} "
            f"{delta:>18}"
        )

    print("-" * 104)
    print(f"Detailed CSV : {TABLE8_PATH}")
    print(f"Report       : {COMPARISON_PATH}")
    print("H5g RESULT: COMPLETE")
    print("Next: interpret Table 8 agreement, then H5h Fig.9.")
    print("=" * 104)


def main() -> None:
    raw = load_raw()
    grouped = group_scores(raw)
    rows = build_results(grouped)
    summary = summarize_wlt(rows)

    write_csv(rows)
    write_report(summary)
    print_console(summary)


if __name__ == "__main__":
    main()
