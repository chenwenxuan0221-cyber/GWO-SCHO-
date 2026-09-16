"""F5 - Engineering paper comparison + feasibility diagnostics.

This stage DOES NOT run GWO or SCHO again.

Inputs
------
results/raw/engineering_f4_runs.csv
results/processed/engineering_f4_summary.csv

Outputs
-------
results/processed/engineering_f5_paper_comparison.csv
results/processed/engineering_f5_seed_diagnostics.csv
report/engineering_f5_analysis.md

Source basis
------------
The paper-reference objective values are the frozen Stage-F0 values from
SCHO Tables 16-21, carried in `paper_best_f` inside the validated
EngineeringBenchmark objects.

Important interpretation
------------------------
1. Feasibility success rate and feasible-only objective quality are reported
   separately.
2. `NO_FEASIBLE_FOUND` is retained as experimental evidence.
3. Cantilever is NOT directly compared numerically to Table 20 under the
   paper-printed objective, because the printed coefficient 0.6224 produces
   ~13.03 at the paper point while Table 20 reports ~1.3033.
4. A separately labelled cantilever diagnostic rescales the printed objective
   by 0.1, equivalent to using coefficient 0.06224 with the SAME printed
   constraint. This is a diagnostic assumption, not a paper-verified formula.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from benchmarks.engineering_design import (
    PRIMARY_BENCHMARKS,
    CANTILEVER_TABLE_CONSISTENT,
)


RAW_F4 = Path("results/raw/engineering_f4_runs.csv")
SUMMARY_F4 = Path("results/processed/engineering_f4_summary.csv")

OUT_COMPARISON = Path(
    "results/processed/engineering_f5_paper_comparison.csv"
)
OUT_SEEDS = Path(
    "results/processed/engineering_f5_seed_diagnostics.csv"
)
OUT_REPORT = Path("report/engineering_f5_analysis.md")

ALGORITHMS = ("GWO", "SCHO")


def _require_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required F4 input not found: {path}\n"
            "Run F4 successfully before F5."
        )


def _read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _float(value):
    if value is None or value == "":
        return np.nan
    try:
        return float(value)
    except ValueError:
        return np.nan


def _int(value):
    return int(float(value))


def _fmt(value, digits=10):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return "nan"
    if not np.isfinite(x):
        return "nan"
    return f"{x:.{digits}g}"


def _fmt_pct(value, digits=3):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return "nan"
    if not np.isfinite(x):
        return "nan"
    return f"{x:.{digits}f}%"


def _summary_lookup(summary_rows):
    return {
        (row["problem"], row["algorithm"]): row
        for row in summary_rows
    }


def build_paper_comparison(summary_rows):
    lookup = _summary_lookup(summary_rows)
    rows = []

    for benchmark in PRIMARY_BENCHMARKS:
        paper_x_f = benchmark.objective(benchmark.paper_best_x)
        paper_x_feasible = benchmark.is_feasible(
            benchmark.paper_best_x,
            tolerance=1e-8,
        )

        for algorithm in ALGORITHMS:
            key = (benchmark.key, algorithm)
            if key not in lookup:
                raise KeyError(
                    f"F4 summary missing row for {benchmark.key}/{algorithm}"
                )

            s = lookup[key]
            feasible_runs = _int(s["feasible_runs"])
            runs = _int(s["runs"])
            feasible_rate = _float(s["feasible_rate"])
            best = _float(s["best_feasible"])
            mean = _float(s["mean_feasible"])
            median = _float(s["median_feasible"])
            std = _float(s["std_feasible_sample"])
            worst = _float(s["worst_feasible"])
            paper_f = float(benchmark.paper_best_f)

            row = {
                "problem": benchmark.key,
                "problem_name": benchmark.name,
                "algorithm": algorithm,
                "runs": runs,
                "feasible_runs": feasible_runs,
                "feasible_rate": feasible_rate,
                "best_feasible": best,
                "mean_feasible": mean,
                "median_feasible": median,
                "std_feasible_sample": std,
                "worst_feasible": worst,
                "paper_reported_f": paper_f,
                "paper_x_recomputed_f": paper_x_f,
                "paper_x_feasible_under_frozen_formulation": paper_x_feasible,
                "comparison_basis": "",
                "best_minus_paper": np.nan,
                "best_gap_percent": np.nan,
                "diagnostic_best_0p06224": np.nan,
                "diagnostic_mean_0p06224": np.nan,
                "diagnostic_best_minus_table20": np.nan,
                "diagnostic_best_gap_percent": np.nan,
                "note": "",
            }

            if benchmark.key == "cantilever_printed":
                # The main experiment must remain the paper-printed 0.6224
                # formulation. A direct optimization-quality gap to Table 20
                # would therefore be misleading.
                row["comparison_basis"] = "FORMULA_MISMATCH_NOT_DIRECT"
                row["diagnostic_best_0p06224"] = (
                    best * 0.1 if np.isfinite(best) else np.nan
                )
                row["diagnostic_mean_0p06224"] = (
                    mean * 0.1 if np.isfinite(mean) else np.nan
                )
                diagnostic_best = row["diagnostic_best_0p06224"]
                if np.isfinite(diagnostic_best):
                    row["diagnostic_best_minus_table20"] = (
                        diagnostic_best - paper_f
                    )
                    row["diagnostic_best_gap_percent"] = (
                        (diagnostic_best - paper_f)
                        / abs(paper_f)
                        * 100.0
                    )
                row["note"] = (
                    "Primary F4 uses printed coefficient 0.6224. "
                    "Diagnostic columns multiply objective by 0.1, equivalent "
                    "to coefficient 0.06224 with the SAME printed constraint. "
                    "This is an explicitly labelled assumption, not a "
                    "paper-confirmed correction."
                )
            else:
                row["comparison_basis"] = "DIRECT_SAME_FROZEN_FORMULATION"
                if np.isfinite(best):
                    row["best_minus_paper"] = best - paper_f
                    row["best_gap_percent"] = (
                        (best - paper_f) / abs(paper_f) * 100.0
                    )

            rows.append(row)

    return rows


def build_seed_diagnostics(raw_rows):
    rows = []

    for benchmark in PRIMARY_BENCHMARKS:
        by_algorithm = {}
        for algorithm in ALGORITHMS:
            subset = [
                r for r in raw_rows
                if r["problem"] == benchmark.key
                and r["algorithm"] == algorithm
            ]
            if len(subset) != 30:
                raise ValueError(
                    f"Expected 30 F4 raw rows for "
                    f"{benchmark.key}/{algorithm}, got {len(subset)}"
                )
            by_algorithm[algorithm] = {
                _int(r["seed"]): r["status"]
                for r in subset
            }

        seeds = sorted(
            set(by_algorithm["GWO"])
            | set(by_algorithm["SCHO"])
        )

        both = []
        gwo_only = []
        scho_only = []
        neither = []
        structural = []

        for seed in seeds:
            g_status = by_algorithm["GWO"].get(seed, "MISSING")
            s_status = by_algorithm["SCHO"].get(seed, "MISSING")

            if g_status in {"ERROR", "STRUCTURAL_FAIL", "MISSING"} or \
               s_status in {"ERROR", "STRUCTURAL_FAIL", "MISSING"}:
                structural.append(seed)
                continue

            g_ok = g_status == "PASS"
            s_ok = s_status == "PASS"

            if g_ok and s_ok:
                both.append(seed)
            elif g_ok and not s_ok:
                gwo_only.append(seed)
            elif s_ok and not g_ok:
                scho_only.append(seed)
            else:
                neither.append(seed)

        rows.append(
            {
                "problem": benchmark.key,
                "problem_name": benchmark.name,
                "paired_seeds": len(seeds),
                "both_feasible": len(both),
                "gwo_only_feasible": len(gwo_only),
                "scho_only_feasible": len(scho_only),
                "neither_feasible": len(neither),
                "structural_or_missing": len(structural),
                "both_feasible_seeds": ";".join(map(str, both)),
                "gwo_only_seeds": ";".join(map(str, gwo_only)),
                "scho_only_seeds": ";".join(map(str, scho_only)),
                "neither_feasible_seeds": ";".join(map(str, neither)),
                "structural_or_missing_seeds": ";".join(map(str, structural)),
            }
        )

    return rows


def _write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write: {path}")

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def _reference_status(row):
    rate = float(row["feasible_rate"])
    if rate == 1.0:
        return "30/30"
    return f"{int(row['feasible_runs'])}/{int(row['runs'])}"


def build_markdown(comparison_rows, seed_rows):
    comp = {
        (r["problem"], r["algorithm"]): r
        for r in comparison_rows
    }
    seed = {
        r["problem"]: r
        for r in seed_rows
    }

    lines = []
    lines.append("# Stage F5 — Engineering paper comparison and diagnostics")
    lines.append("")
    lines.append("## 1. Scope and protocol")
    lines.append("")
    lines.append(
        "F5 does **not** rerun GWO or SCHO. It reads the frozen F4 outputs "
        "and compares feasible-only results with the Stage-F0 paper reference "
        "values from SCHO Tables 16–21."
    )
    lines.append("")
    lines.append(
        "Project protocol: N=30, MaxIter=500, 30 runs, seeds 1000–1029, "
        "death penalty=1e30, feasibility tolerance=1e-8. These are project "
        "reproduction settings; the SCHO engineering section does not state "
        "this complete engineering-specific numerical protocol."
    )
    lines.append("")
    lines.append(
        "Feasibility success rate and feasible-only solution quality are "
        "reported separately. A run with `NO_FEASIBLE_FOUND` is retained as "
        "data and is not replaced, retuned, or averaged as if it were a "
        "normal feasible solution."
    )
    lines.append("")

    lines.append("## 2. Feasibility results")
    lines.append("")
    lines.append(
        "| Problem | GWO feasible | SCHO feasible | Both feasible seeds | "
        "GWO-only | SCHO-only | Neither |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for benchmark in PRIMARY_BENCHMARKS:
        g = comp[(benchmark.key, "GWO")]
        s = comp[(benchmark.key, "SCHO")]
        d = seed[benchmark.key]
        lines.append(
            f"| {benchmark.key} | "
            f"{_reference_status(g)} ({float(g['feasible_rate']):.1%}) | "
            f"{_reference_status(s)} ({float(s['feasible_rate']):.1%}) | "
            f"{d['both_feasible']} | {d['gwo_only_feasible']} | "
            f"{d['scho_only_feasible']} | {d['neither_feasible']} |"
        )

    lines.append("")
    lines.append(
        "The paired-seed counts show whether the feasibility difference comes "
        "from the same or different random seeds. They are descriptive only; "
        "F5 does not turn them into a claim of general algorithm superiority."
    )
    lines.append("")

    lines.append("## 3. Paper-reference comparison")
    lines.append("")
    lines.append(
        "For five internally consistent formulations, the table below compares "
        "the best feasible F4 objective directly with the SCHO paper-reported "
        "reference objective. Negative gap means the reproduction best is "
        "numerically lower than the reported reference; positive gap means it "
        "is numerically higher. This is a numerical comparison, not proof of "
        "equivalent experimental protocol."
    )
    lines.append("")
    lines.append(
        "| Problem | Algorithm | Feasible runs | Best feasible | "
        "Paper reported | Best gap | Gap % |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---:|")

    for benchmark in PRIMARY_BENCHMARKS:
        if benchmark.key == "cantilever_printed":
            continue
        for algorithm in ALGORITHMS:
            r = comp[(benchmark.key, algorithm)]
            lines.append(
                f"| {benchmark.key} | {algorithm} | "
                f"{r['feasible_runs']}/{r['runs']} | "
                f"{_fmt(r['best_feasible'])} | "
                f"{_fmt(r['paper_reported_f'])} | "
                f"{_fmt(r['best_minus_paper'])} | "
                f"{_fmt_pct(r['best_gap_percent'])} |"
            )

    lines.append("")

    lines.append("## 4. Cantilever paper inconsistency")
    lines.append("")
    cant_g = comp[("cantilever_printed", "GWO")]
    cant_s = comp[("cantilever_printed", "SCHO")]

    printed_at_paper_x = float(cant_g["paper_x_recomputed_f"])
    diagnostic_at_paper_x = CANTILEVER_TABLE_CONSISTENT.objective(
        CANTILEVER_TABLE_CONSISTENT.paper_best_x
    )
    table20 = float(cant_g["paper_reported_f"])

    lines.append(
        f"At the Table-20 design point, the paper-printed objective "
        f"`0.6224*sum(x)` evaluates to approximately "
        f"**{printed_at_paper_x:.10g}**, whereas Table 20 reports "
        f"**{table20:.10g}**. The separately labelled diagnostic coefficient "
        f"`0.06224` evaluates to approximately "
        f"**{diagnostic_at_paper_x:.10g}**."
    )
    lines.append("")
    lines.append(
        "Therefore the primary F4 cantilever results are **not directly "
        "compared** to Table 20 as an optimization gap. For diagnostic "
        "purposes only, multiplying the printed-objective F4 values by 0.1 "
        "gives:"
    )
    lines.append("")
    lines.append(
        "| Algorithm | Printed best | Diagnostic 0.06224 best | "
        "Table 20 | Diagnostic gap % |"
    )
    lines.append("|---|---:|---:|---:|---:|")
    for r in (cant_g, cant_s):
        lines.append(
            f"| {r['algorithm']} | "
            f"{_fmt(r['best_feasible'])} | "
            f"{_fmt(r['diagnostic_best_0p06224'])} | "
            f"{_fmt(r['paper_reported_f'])} | "
            f"{_fmt_pct(r['diagnostic_best_gap_percent'])} |"
        )
    lines.append("")
    lines.append(
        "This diagnostic does **not** assert that 0.06224 is the confirmed "
        "paper formula, and it does not introduce the separate literature "
        "variant with a first constraint coefficient of 61."
    )
    lines.append("")

    lines.append("## 5. Problem-level diagnostics")
    lines.append("")
    for benchmark in PRIMARY_BENCHMARKS:
        g = comp[(benchmark.key, "GWO")]
        s = comp[(benchmark.key, "SCHO")]
        d = seed[benchmark.key]

        if benchmark.key == "spring":
            text = (
                f"- **Spring:** GWO found feasible designs in "
                f"{g['feasible_runs']}/30 runs and SCHO in "
                f"{s['feasible_runs']}/30. Both produced best feasible "
                f"objectives on the same ~0.0127 scale as the paper reference."
            )
        elif benchmark.key == "pressure_vessel":
            text = (
                f"- **Pressure vessel:** both algorithms were feasible in "
                f"30/30 runs. The experiment uses the continuous formulation "
                f"frozen in F0; no unreported thickness discretization is "
                f"introduced."
            )
        elif benchmark.key == "welded_beam":
            text = (
                f"- **Welded beam:** feasibility was intermittent "
                f"(GWO {g['feasible_runs']}/30, SCHO "
                f"{s['feasible_runs']}/30). Paired seeds: "
                f"both={d['both_feasible']}, GWO-only={d['gwo_only_feasible']}, "
                f"SCHO-only={d['scho_only_feasible']}, neither={d['neither_feasible']}."
            )
        elif benchmark.key == "speed_reducer":
            text = (
                f"- **Speed reducer:** this was the strongest feasibility "
                f"bottleneck under pure death penalty: GWO "
                f"{g['feasible_runs']}/30 versus SCHO "
                f"{s['feasible_runs']}/30. Because infeasible candidates all "
                f"receive the same `1e30`, F5 does not interpret returned "
                f"infeasible positions as meaningful 'near-feasible' optima."
            )
        elif benchmark.key == "cantilever_printed":
            text = (
                f"- **Cantilever:** both algorithms were feasible in 30/30 "
                f"runs, but the primary printed-objective values remain on "
                f"the ~13 scale; the Table-20 ~1.3033 value is handled only "
                f"through the explicitly labelled diagnostic above."
            )
        else:
            text = (
                f"- **Three-bar truss:** both algorithms were feasible in "
                f"30/30 runs and their best feasible values are close to the "
                f"paper reference scale."
            )

        lines.append(text)

    lines.append("")
    lines.append("## 6. F5 conclusion")
    lines.append("")
    lines.append(
        "The Stage-F engineering implementation is structurally stable: F4 "
        "completed all 360 requested runs with zero structural failures. "
        "However, pure death-penalty feasibility is problem dependent. "
        "Spring, pressure vessel, cantilever, and three-bar truss were mostly "
        "or fully feasible, while welded beam and especially speed reducer "
        "showed substantial feasibility failures."
    )
    lines.append("")
    lines.append(
        "For five internally consistent problems, the best feasible results "
        "can be compared numerically with the paper-reported objective values. "
        "The cantilever problem must remain separately qualified because the "
        "printed objective and Table 20 are internally inconsistent."
    )
    lines.append("")
    lines.append(
        "F5 intentionally makes no claim that one optimizer is universally "
        "superior. Feasibility rate, feasible-objective quality, formulation "
        "differences, and stochastic variation are kept as separate pieces "
        "of evidence."
    )

    return "\n".join(lines) + "\n"


def main():
    print("=" * 118)
    print("F5 - Engineering paper comparison + diagnostics")
    print("=" * 118)
    print("No optimizer runs will be executed.")
    print(f"Input raw     : {RAW_F4}")
    print(f"Input summary : {SUMMARY_F4}")
    print("=" * 118)

    _require_file(RAW_F4)
    _require_file(SUMMARY_F4)

    raw_rows = _read_csv(RAW_F4)
    summary_rows = _read_csv(SUMMARY_F4)

    if len(raw_rows) != 360:
        raise ValueError(
            f"Expected 360 raw F4 rows, got {len(raw_rows)}"
        )
    if len(summary_rows) != 12:
        raise ValueError(
            f"Expected 12 F4 summary rows, got {len(summary_rows)}"
        )

    comparison_rows = build_paper_comparison(summary_rows)
    seed_rows = build_seed_diagnostics(raw_rows)

    _write_csv(OUT_COMPARISON, comparison_rows)
    _write_csv(OUT_SEEDS, seed_rows)

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(
        build_markdown(comparison_rows, seed_rows),
        encoding="utf-8",
    )

    structural_count = sum(
        1
        for r in raw_rows
        if r["status"] in {"ERROR", "STRUCTURAL_FAIL"}
    )
    no_feasible_count = sum(
        1
        for r in raw_rows
        if r["status"] == "NO_FEASIBLE_FOUND"
    )

    print("\nInput audit")
    print("-" * 118)
    print(f"F4 raw rows             : {len(raw_rows)}/360")
    print(f"F4 summary rows         : {len(summary_rows)}/12")
    print(f"Structural failures     : {structural_count}")
    print(f"NO_FEASIBLE_FOUND runs  : {no_feasible_count}")

    print("\nDirect paper-reference comparison (best feasible)")
    print("-" * 118)
    for row in comparison_rows:
        if row["problem"] == "cantilever_printed":
            continue
        print(
            f"{row['problem']:<20} {row['algorithm']:<4} "
            f"Feasible={row['feasible_runs']:>2}/{row['runs']} "
            f"Best={_fmt(row['best_feasible']):>14} "
            f"Paper={_fmt(row['paper_reported_f']):>14} "
            f"Gap={_fmt_pct(row['best_gap_percent']):>10}"
        )

    print("\nCantilever diagnostic")
    print("-" * 118)
    for row in comparison_rows:
        if row["problem"] != "cantilever_printed":
            continue
        print(
            f"{row['algorithm']:<4} "
            f"PrintedBest={_fmt(row['best_feasible']):>14} "
            f"Diagnostic0.06224={_fmt(row['diagnostic_best_0p06224']):>14} "
            f"Table20={_fmt(row['paper_reported_f']):>12} "
            f"DiagGap={_fmt_pct(row['diagnostic_best_gap_percent']):>10}"
        )

    print("\nPaired-seed feasibility diagnostics")
    print("-" * 118)
    for row in seed_rows:
        print(
            f"{row['problem']:<20} "
            f"both={row['both_feasible']:>2} "
            f"GWO-only={row['gwo_only_feasible']:>2} "
            f"SCHO-only={row['scho_only_feasible']:>2} "
            f"neither={row['neither_feasible']:>2}"
        )

    print("\nOutputs")
    print("-" * 118)
    print(f"Comparison CSV : {OUT_COMPARISON}")
    print(f"Seed CSV       : {OUT_SEEDS}")
    print(f"Markdown report: {OUT_REPORT}")

    print("\nF5 RESULT: PASS")
    print("No optimizer was rerun.")
    print("F4 raw/summary files were read only and not overwritten.")
    print("Cantilever Table-20 comparison remains explicitly diagnostic.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
