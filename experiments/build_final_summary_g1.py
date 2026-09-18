"""G1 - Final tables + integrated numerical summary.

G1 does NOT rerun any optimizer. It consolidates frozen Stage D/E/F evidence
into compact final-report tables.

Inputs
------
results/processed/D2_GWO_vs_SCHO_classic23.csv
results/processed/cec2014_e4_summary.csv
results/raw/engineering_f4_runs.csv
results/processed/engineering_f4_summary.csv
results/processed/engineering_f5_paper_comparison.csv
results/processed/engineering_f5_seed_diagnostics.csv

Outputs
-------
report/tables/stage_g1_overview.csv
report/tables/stage_g1_classic_family_summary.csv
report/tables/stage_g1_engineering_summary.csv
report/stage_g1_integrated_numerical_summary.md

Important
---------
The classic and CEC headline counts below are the already-frozen Stage D/E
conclusions. G1 verifies that the corresponding evidence files exist, but it
does not silently reinterpret their historical schemas or recompute a new
criterion from differently named columns.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


CLASSIC_D2 = Path("results/processed/D2_GWO_vs_SCHO_classic23.csv")
CEC_E4 = Path("results/processed/cec2014_e4_summary.csv")
ENG_F4_RAW = Path("results/raw/engineering_f4_runs.csv")
ENG_F4_SUMMARY = Path("results/processed/engineering_f4_summary.csv")
ENG_F5_COMPARE = Path("results/processed/engineering_f5_paper_comparison.csv")
ENG_F5_SEEDS = Path("results/processed/engineering_f5_seed_diagnostics.csv")

OUT_OVERVIEW = Path("report/tables/stage_g1_overview.csv")
OUT_CLASSIC = Path("report/tables/stage_g1_classic_family_summary.csv")
OUT_ENGINEERING = Path("report/tables/stage_g1_engineering_summary.csv")
OUT_REPORT = Path("report/stage_g1_integrated_numerical_summary.md")


# ---------------------------------------------------------------------------
# Frozen Stage D conclusions
# ---------------------------------------------------------------------------

CLASSIC_TOTAL = 23
CLASSIC_GWO_MEAN_WINS = 8
CLASSIC_SCHO_MEAN_WINS = 12
CLASSIC_TIES = 3

CLASSIC_FAMILIES = [
    {
        "family": "F1-F7",
        "functions": 7,
        "GWO_lower_mean": 1,
        "SCHO_lower_mean": 4,
        "Tie": 2,
    },
    {
        "family": "F8-F13",
        "functions": 6,
        "GWO_lower_mean": 2,
        "SCHO_lower_mean": 3,
        "Tie": 1,
    },
    {
        "family": "F14-F23",
        "functions": 10,
        "GWO_lower_mean": 5,
        "SCHO_lower_mean": 5,
        "Tie": 0,
    },
]


# ---------------------------------------------------------------------------
# Frozen Stage E conclusions
# ---------------------------------------------------------------------------

CEC_TOTAL = 30

# Reproduction pairwise lower mean:
CEC_REPRO_GWO_LOWER = 22
CEC_REPRO_SCHO_LOWER = 8

# Paper pairwise lower mean:
CEC_PAPER_GWO_LOWER = 13
CEC_PAPER_SCHO_LOWER = 17

CEC_PAIRWISE_FLIPS = 9

# Mean-error agreement with paper:
CEC_GWO_WITHIN_25PCT = 22
CEC_GWO_WITHIN_FACTOR2 = 30
CEC_SCHO_WITHIN_25PCT = 14
CEC_SCHO_WITHIN_FACTOR2 = 26


def require(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Required evidence missing: {path}")


def read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def as_float(value):
    if value is None or value == "":
        return np.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def as_int(value):
    return int(float(value))


def fmt(x, sig=10):
    x = float(x)
    if not np.isfinite(x):
        return "NaN"
    return f"{x:.{sig}g}"


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def validate_historical_evidence():
    for p in [
        CLASSIC_D2,
        CEC_E4,
        ENG_F4_RAW,
        ENG_F4_SUMMARY,
        ENG_F5_COMPARE,
        ENG_F5_SEEDS,
    ]:
        require(p)

    classic_rows = read_csv(CLASSIC_D2)
    cec_rows = read_csv(CEC_E4)
    eng_raw = read_csv(ENG_F4_RAW)
    eng_summary = read_csv(ENG_F4_SUMMARY)
    eng_compare = read_csv(ENG_F5_COMPARE)
    eng_seeds = read_csv(ENG_F5_SEEDS)

    if len(classic_rows) != 23:
        raise ValueError(
            f"Expected 23 classic comparison rows, got {len(classic_rows)}"
        )
    if len(eng_raw) != 360:
        raise ValueError(
            f"Expected 360 engineering raw rows, got {len(eng_raw)}"
        )
    if len(eng_summary) != 12:
        raise ValueError(
            f"Expected 12 engineering summary rows, got {len(eng_summary)}"
        )
    if len(eng_compare) != 12:
        raise ValueError(
            f"Expected 12 engineering comparison rows, got {len(eng_compare)}"
        )
    if len(eng_seeds) != 6:
        raise ValueError(
            f"Expected 6 engineering seed rows, got {len(eng_seeds)}"
        )

    # CEC2014 summary can be stored in different historical layouts.
    # Require at least 30 rows, but do not silently assume a particular schema.
    if len(cec_rows) < 30:
        raise ValueError(
            f"CEC2014 summary unexpectedly short: {len(cec_rows)} rows"
        )

    structural = sum(
        r.get("status") in {"ERROR", "STRUCTURAL_FAIL"}
        for r in eng_raw
    )
    feasible = sum(r.get("status") == "PASS" for r in eng_raw)
    no_feasible = sum(
        r.get("status") == "NO_FEASIBLE_FOUND"
        for r in eng_raw
    )

    if structural != 0:
        raise ValueError(
            f"Engineering raw data contains {structural} structural failures."
        )

    return {
        "classic_rows": len(classic_rows),
        "cec_rows": len(cec_rows),
        "eng_raw_rows": len(eng_raw),
        "eng_feasible": feasible,
        "eng_no_feasible": no_feasible,
        "eng_summary": eng_summary,
        "eng_compare": eng_compare,
        "eng_seeds": eng_seeds,
    }


def build_overview(data):
    return [
        {
            "domain": "Classic F1-F23",
            "scope": "23 functions",
            "primary_metric": "lower 30-run mean objective/error under Stage D rule",
            "headline_1": f"GWO lower mean: {CLASSIC_GWO_MEAN_WINS}",
            "headline_2": f"SCHO lower mean: {CLASSIC_SCHO_MEAN_WINS}",
            "headline_3": f"Ties: {CLASSIC_TIES}",
            "status": "COMPLETE",
        },
        {
            "domain": "CEC2014",
            "scope": "F1-F30, D=10",
            "primary_metric": "mean error + paper-scale agreement",
            "headline_1": (
                f"Reproduction lower mean: GWO {CEC_REPRO_GWO_LOWER}, "
                f"SCHO {CEC_REPRO_SCHO_LOWER}"
            ),
            "headline_2": (
                f"Within ±25% of paper mean error: "
                f"GWO {CEC_GWO_WITHIN_25PCT}/30, "
                f"SCHO {CEC_SCHO_WITHIN_25PCT}/30"
            ),
            "headline_3": f"Paper/reproduction pairwise flips: {CEC_PAIRWISE_FLIPS}",
            "status": "COMPLETE",
        },
        {
            "domain": "Engineering design",
            "scope": "6 problems × 2 algorithms × 30 runs",
            "primary_metric": "feasible rate + feasible-only objective quality",
            "headline_1": f"Feasible runs: {data['eng_feasible']}/360",
            "headline_2": (
                f"NO_FEASIBLE_FOUND: {data['eng_no_feasible']}/360"
            ),
            "headline_3": "Structural failures: 0",
            "status": "COMPLETE",
        },
    ]


def build_engineering_summary(data):
    compare = {
        (r["problem"], r["algorithm"]): r
        for r in data["eng_compare"]
    }
    seeds = {
        r["problem"]: r
        for r in data["eng_seeds"]
    }

    order = [
        "spring",
        "pressure_vessel",
        "welded_beam",
        "speed_reducer",
        "cantilever_printed",
        "three_bar_truss",
    ]

    rows = []
    for problem in order:
        for alg in ("GWO", "SCHO"):
            r = compare[(problem, alg)]
            s = seeds[problem]

            if problem == "cantilever_printed":
                paper_gap = "N/A (formula mismatch)"
                paper_value = r["paper_reported_f"]
                note = (
                    "Primary result uses printed 0.6224 objective; "
                    "Table-20 comparison is diagnostic only."
                )
            else:
                paper_gap = f"{as_float(r['best_gap_percent']):+.3f}%"
                paper_value = r["paper_reported_f"]
                note = ""

            rows.append({
                "problem": problem,
                "algorithm": alg,
                "feasible_runs": r["feasible_runs"],
                "runs": r["runs"],
                "feasible_rate": f"{100*as_float(r['feasible_rate']):.1f}%",
                "best_feasible": fmt(as_float(r["best_feasible"])),
                "paper_reported_f": paper_value,
                "best_gap_vs_paper": paper_gap,
                "both_feasible_seeds": s["both_feasible"],
                "gwo_only_seeds": s["gwo_only_feasible"],
                "scho_only_seeds": s["scho_only_feasible"],
                "neither_feasible_seeds": s["neither_feasible"],
                "note": note,
            })

    return rows


def build_report(data, overview, engineering_rows):
    lines = []
    lines.append("# Stage G1 — Integrated Numerical Summary")
    lines.append("")
    lines.append("## 1. Purpose")
    lines.append("")
    lines.append(
        "G1 consolidates the frozen numerical evidence from the classic "
        "benchmarks, CEC2014, and engineering-design experiments. "
        "No optimizer is rerun and no frozen conclusion is retuned."
    )
    lines.append("")

    lines.append("## 2. Cross-stage overview")
    lines.append("")
    lines.append(
        "| Domain | Scope | Primary metric | Headline result |"
    )
    lines.append("|---|---|---|---|")
    for row in overview:
        headline = (
            f"{row['headline_1']}; {row['headline_2']}; "
            f"{row['headline_3']}"
        )
        lines.append(
            f"| {row['domain']} | {row['scope']} | "
            f"{row['primary_metric']} | {headline} |"
        )
    lines.append("")

    lines.append("## 3. Classic F1-F23")
    lines.append("")
    lines.append(
        "Under the frozen Stage D practical mean-comparison rule, "
        f"GWO had the lower mean on **{CLASSIC_GWO_MEAN_WINS}/23** functions, "
        f"SCHO on **{CLASSIC_SCHO_MEAN_WINS}/23**, with "
        f"**{CLASSIC_TIES} ties**."
    )
    lines.append("")
    lines.append("| Family | Functions | GWO lower mean | SCHO lower mean | Tie |")
    lines.append("|---|---:|---:|---:|---:|")
    for row in CLASSIC_FAMILIES:
        lines.append(
            f"| {row['family']} | {row['functions']} | "
            f"{row['GWO_lower_mean']} | {row['SCHO_lower_mean']} | "
            f"{row['Tie']} |"
        )
    lines.append("")
    lines.append(
        "These counts are descriptive results under the project reproduction "
        "protocol; stochastic/local-optimum deviations were retained rather "
        "than tuned away."
    )
    lines.append("")

    lines.append("## 4. CEC2014")
    lines.append("")
    lines.append(
        f"Stage E reproduced 30 CEC2014 functions at D=10. GWO mean errors "
        f"were within ±25% of the paper values on "
        f"**{CEC_GWO_WITHIN_25PCT}/30** functions and within a factor of 2 on "
        f"**{CEC_GWO_WITHIN_FACTOR2}/30**. SCHO was within ±25% on "
        f"**{CEC_SCHO_WITHIN_25PCT}/30** and within a factor of 2 on "
        f"**{CEC_SCHO_WITHIN_FACTOR2}/30**."
    )
    lines.append("")
    lines.append(
        f"The paper's pairwise lower-mean count was GWO "
        f"{CEC_PAPER_GWO_LOWER} vs SCHO {CEC_PAPER_SCHO_LOWER}; the "
        f"reproduction produced GWO {CEC_REPRO_GWO_LOWER} vs SCHO "
        f"{CEC_REPRO_SCHO_LOWER}, with {CEC_PAIRWISE_FLIPS} pairwise flips."
    )
    lines.append("")
    lines.append(
        "The frozen Stage E interpretation remains: the GWO scale was broadly "
        "reproduced, while SCHO's relative advantage was not fully reproduced. "
        "The result is retained rather than corrected by tuning."
    )
    lines.append("")

    lines.append("## 5. Engineering design")
    lines.append("")
    lines.append(
        f"F4 completed all 360 requested runs: **{data['eng_feasible']}** "
        f"returned feasible best designs, **{data['eng_no_feasible']}** were "
        "`NO_FEASIBLE_FOUND`, and there were **0 structural failures**."
    )
    lines.append("")
    lines.append(
        "| Problem | Alg. | Feasible | Rate | Best feasible | Paper | "
        "Best gap |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for row in engineering_rows:
        lines.append(
            f"| {row['problem']} | {row['algorithm']} | "
            f"{row['feasible_runs']}/{row['runs']} | "
            f"{row['feasible_rate']} | {row['best_feasible']} | "
            f"{row['paper_reported_f']} | {row['best_gap_vs_paper']} |"
        )
    lines.append("")
    lines.append(
        "Welded beam and especially speed reducer show why feasible rate must "
        "be reported separately from best feasible objective. For speed "
        "reducer, GWO found a feasible design in only 1/30 runs while SCHO "
        "did so in 14/30."
    )
    lines.append("")
    lines.append(
        "Cantilever remains a special source anomaly: the primary experiment "
        "uses the paper-printed `0.6224` objective, while the `0.06224` "
        "version is retained only as a separately labelled Table-20-consistent "
        "diagnostic."
    )
    lines.append("")

    lines.append("## 6. Integrated interpretation")
    lines.append("")
    lines.append(
        "Across the three benchmark families, there is no single scalar result "
        "that adequately summarizes reproduction quality. Classic functions "
        "mainly reveal stochastic optimizer behavior; CEC2014 tests whether "
        "the paper-scale performance transfers to a harder modern benchmark "
        "suite; engineering problems additionally expose feasibility-handling "
        "behavior."
    )
    lines.append("")
    lines.append(
        "The final report should therefore keep four evidence dimensions "
        "separate: (1) source-faithful implementation, (2) objective/error "
        "quality, (3) stochastic variation, and (4) feasibility success under "
        "constraints."
    )
    lines.append("")

    lines.append("## 7. G1 status")
    lines.append("")
    lines.append("**G1 RESULT: PASS**")
    lines.append("")
    lines.append(
        "The numerical evidence is now consolidated and ready for G2, where "
        "the integrated final report can be drafted without rerunning any "
        "optimizer."
    )

    return "\n".join(lines) + "\n"


def main():
    print("=" * 120)
    print("G1 - Final tables + integrated numerical summary")
    print("=" * 120)
    print("No optimizer will be executed.")
    print("=" * 120)

    data = validate_historical_evidence()

    overview = build_overview(data)
    engineering_rows = build_engineering_summary(data)

    write_csv(OUT_OVERVIEW, overview)
    write_csv(OUT_CLASSIC, CLASSIC_FAMILIES)
    write_csv(OUT_ENGINEERING, engineering_rows)

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(
        build_report(data, overview, engineering_rows),
        encoding="utf-8",
    )

    print("\nEvidence validation")
    print("-" * 120)
    print(f"Classic comparison rows : {data['classic_rows']}/23")
    print(f"CEC2014 summary rows     : {data['cec_rows']}")
    print(f"Engineering raw rows     : {data['eng_raw_rows']}/360")
    print(f"Engineering feasible     : {data['eng_feasible']}/360")
    print(f"Engineering no-feasible  : {data['eng_no_feasible']}/360")

    print("\nFrozen headline summary")
    print("-" * 120)
    print(
        f"Classic F1-F23           : "
        f"GWO {CLASSIC_GWO_MEAN_WINS}, "
        f"SCHO {CLASSIC_SCHO_MEAN_WINS}, "
        f"Tie {CLASSIC_TIES}"
    )
    print(
        f"CEC2014 reproduction     : "
        f"lower mean GWO {CEC_REPRO_GWO_LOWER}, "
        f"SCHO {CEC_REPRO_SCHO_LOWER}; "
        f"pairwise flips {CEC_PAIRWISE_FLIPS}"
    )
    print(
        f"CEC paper-scale ±25%     : "
        f"GWO {CEC_GWO_WITHIN_25PCT}/30, "
        f"SCHO {CEC_SCHO_WITHIN_25PCT}/30"
    )
    print(
        f"Engineering              : "
        f"feasible {data['eng_feasible']}/360, "
        f"NO_FEASIBLE_FOUND {data['eng_no_feasible']}"
    )

    print("\nOutputs")
    print("-" * 120)
    print(f"Overview table     : {OUT_OVERVIEW}")
    print(f"Classic family     : {OUT_CLASSIC}")
    print(f"Engineering table  : {OUT_ENGINEERING}")
    print(f"Integrated summary : {OUT_REPORT}")

    print("\nG1 RESULT: PASS")
    print("No optimizer was rerun.")
    print("Frozen Stage D/E/F conclusions were preserved.")
    print("Stage G is ready for G2 integrated final-report drafting.")


if __name__ == "__main__":
    main()
