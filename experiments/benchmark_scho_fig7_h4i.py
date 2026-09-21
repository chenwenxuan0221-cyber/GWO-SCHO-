"""H4i - Formal controlled SCHO Fig.7 Variant 1-11 experiment.

IMPORTANT
---------
This is a CONTROLLED-INTERPRETATION experiment.

The 11 variant equations are frozen by H4h. They are not claimed to be the
unrecovered author implementations.

Formal variant workload:
    11 variants * 23 functions * 30 runs = 7590 optimizer runs

The SCHO control is NOT rerun. It is reused from the completed H4e raw
evidence because H4i intentionally uses the same:
    - benchmark definitions
    - N=30
    - MaxIter=500
    - optimizer seeds 1000..1029
    - per-function/run objective-seed convention

This gives a protocol-aligned common SCHO baseline while avoiding 690
duplicate optimizer runs.
"""

from __future__ import annotations

import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from benchmarks.classic_23 import get_benchmark
from experiments.scho_fig7_variants_h4 import scho_fig7_variant


VARIANTS = tuple(f"V{i}" for i in range(1, 12))
FUNCTIONS = tuple(f"F{i}" for i in range(1, 24))

N = 30
MAX_ITER = 500
N_RUNS = 30
BASE_SEED = 1000

# Must match H4e exactly so the SCHO control is reusable.
OBJECTIVE_SEED_BASE = 4_024_000

H4E_RAW = Path("results/raw/scho_table5_h4e_runs.csv")

RAW_PATH = Path("results/raw/scho_fig7_h4i_variant_runs.csv")
SUMMARY_PATH = Path("results/processed/scho_fig7_h4i_variant_summary.csv")
PER_FUNCTION_PATH = Path(
    "results/processed/scho_fig7_h4i_pairwise_by_function.csv"
)
PAIRWISE_PATH = Path("results/processed/scho_fig7_h4i_pairwise_counts.csv")

FIG_A = Path("report/figures/scho_fig7a_h4i_controlled.png")
FIG_B = Path("report/figures/scho_fig7b_h4i_controlled.png")
FIG_C = Path("report/figures/scho_fig7c_h4i_controlled.png")
FIG_D = Path("report/figures/scho_fig7d_h4i_controlled.png")

REPORT_PATH = Path("report/scho_fig7_h4i_controlled_comparison.md")

PAPER_COUNTS = {
    "V1": (18, 15),
    "V2": (20, 13),
    "V3": (17, 15),
    "V4": (17, 14),
    "V5": (17, 16),
    "V6": (18, 14),
    "V7": (20, 13),
    "V8": (20, 11),
    "V9": (18, 9),
    "V10": (20, 13),
    "V11": (18, 15),
}

FIG_GROUPS = {
    "a": ("V1", "V2"),
    "b": ("V3", "V4", "V5", "V6"),
    "c": ("V7", "V8", "V9"),
    "d": ("V10", "V11"),
}

# Controlled interpretation of "average optimal solutions":
# For each SCHO-vs-variant pair and each function, compare 30-run mean final
# fitness under minimization. If means are numerically tied, credit both.
TIE_RTOL = 1e-9
TIE_ATOL = 1e-12

RAW_FIELDS = [
    "Variant",
    "Function",
    "Run",
    "OptimizerSeed",
    "ObjectiveSeed",
    "Population",
    "MaxIter",
    "Dimension",
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
    "Dimension",
    "Best",
    "Average",
    "STD_sample_ddof1",
    "Median",
    "Worst",
]

PER_FUNCTION_FIELDS = [
    "Variant",
    "Function",
    "SCHO_Average",
    "Variant_Average",
    "Comparison",
    "SCHO_Credit",
    "Variant_Credit",
    "AbsoluteMeanDifference",
]

PAIRWISE_FIELDS = [
    "Variant",
    "SCHO_OptimalAverageCount",
    "Variant_OptimalAverageCount",
    "Ties",
    "SCHO_StrictWins",
    "Variant_StrictWins",
    "Paper_SCHO_Count",
    "Paper_Variant_Count",
    "SCHO_Count_Delta_vs_Paper",
    "Variant_Count_Delta_vs_Paper",
    "TieRTol",
    "TieATol",
]


def _objective_seed(name: str, run: int) -> int:
    return OBJECTIVE_SEED_BASE + int(name[1:]) * 100 + run


def _default_workers() -> int:
    override = os.environ.get("H4I_WORKERS")
    if override is not None:
        value = int(override)
        if value < 1:
            raise ValueError("H4I_WORKERS must be >= 1")
        return value

    cpu = os.cpu_count() or 1
    return max(1, min(4, cpu // 2 if cpu >= 2 else 1))


def _ensure_dirs():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIG_A.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def _validate_result(variant, name, b, score, pos, curve):
    score = float(score)
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    if not np.isfinite(score):
        raise AssertionError(f"{variant}/{name}: non-finite score")
    if pos.shape != (b.dim,):
        raise AssertionError(f"{variant}/{name}: wrong best-position shape")
    if curve.shape != (MAX_ITER,):
        raise AssertionError(f"{variant}/{name}: wrong convergence shape")
    if not np.all(np.isfinite(pos)):
        raise AssertionError(f"{variant}/{name}: position NaN/Inf")
    if not np.all(np.isfinite(curve)):
        raise AssertionError(f"{variant}/{name}: curve NaN/Inf")
    if score != float(curve[-1]):
        raise AssertionError(f"{variant}/{name}: score != curve[-1]")
    if np.any(np.diff(curve) > 0.0):
        raise AssertionError(f"{variant}/{name}: best curve increased")


def _run_task(task):
    variant, name, run = task
    optimizer_seed = BASE_SEED + run - 1
    objective_seed = _objective_seed(name, run)

    b = get_benchmark(name)
    objective = b.make_objective(seed=objective_seed)

    start = time.perf_counter()
    score, pos, curve = scho_fig7_variant(
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

    _validate_result(variant, name, b, score, pos, curve)

    return {
        "Variant": variant,
        "Function": name,
        "Run": run,
        "OptimizerSeed": optimizer_seed,
        "ObjectiveSeed": objective_seed,
        "Population": N,
        "MaxIter": MAX_ITER,
        "Dimension": int(b.dim),
        "BestScore": float(score),
        "Curve0": float(curve[0]),
        "CurveLast": float(curve[-1]),
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
            variant in VARIANTS
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


def _load_checkpoint():
    if not RAW_PATH.exists():
        return [], set()

    rows = []
    complete = set()

    with RAW_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != RAW_FIELDS:
            raise RuntimeError(
                f"Unexpected H4i checkpoint columns.\n"
                f"Expected: {RAW_FIELDS}\nFound: {reader.fieldnames}"
            )

        for disk_row in reader:
            row = _normalize_raw_row(disk_row)
            if not _row_matches_protocol(row):
                raise RuntimeError(
                    "Existing H4i checkpoint contains a row from a "
                    f"different protocol: {row}"
                )

            key = (row["Variant"], row["Function"], row["Run"])
            if key in complete:
                raise RuntimeError(f"Duplicate checkpoint row: {key}")

            complete.add(key)
            rows.append(row)

    return rows, complete


def _append_checkpoint(row):
    new_file = not RAW_PATH.exists()
    with RAW_PATH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def _load_h4e_scho_control():
    if not H4E_RAW.exists():
        raise FileNotFoundError(
            f"Missing protocol-aligned SCHO control: {H4E_RAW}\n"
            "H4e must remain in the project before H4i."
        )

    rows = []
    seen = set()

    with H4E_RAW.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        required = {
            "Variant",
            "Function",
            "Run",
            "OptimizerSeed",
            "ObjectiveSeed",
            "Population",
            "MaxIter",
            "Dimension",
            "BestScore",
            "Status",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise RuntimeError("H4e raw file does not contain expected columns")

        for row in reader:
            if row["Variant"] != "SCHO":
                continue

            name = row["Function"]
            run = int(row["Run"])

            if name not in FUNCTIONS or not (1 <= run <= N_RUNS):
                continue

            b = get_benchmark(name)
            if int(row["OptimizerSeed"]) != BASE_SEED + run - 1:
                raise RuntimeError(f"H4e SCHO optimizer seed mismatch: {name}/{run}")
            if int(row["ObjectiveSeed"]) != _objective_seed(name, run):
                raise RuntimeError(f"H4e SCHO objective seed mismatch: {name}/{run}")
            if int(row["Population"]) != N:
                raise RuntimeError(f"H4e SCHO population mismatch: {name}/{run}")
            if int(row["MaxIter"]) != MAX_ITER:
                raise RuntimeError(f"H4e SCHO MaxIter mismatch: {name}/{run}")
            if int(row["Dimension"]) != int(b.dim):
                raise RuntimeError(f"H4e SCHO dimension mismatch: {name}/{run}")
            if row["Status"] != "PASS":
                raise RuntimeError(f"H4e SCHO non-PASS row: {name}/{run}")

            key = (name, run)
            if key in seen:
                raise RuntimeError(f"Duplicate H4e SCHO row: {key}")
            seen.add(key)

            rows.append(
                {
                    "Function": name,
                    "Run": run,
                    "BestScore": float(row["BestScore"]),
                }
            )

    expected = {
        (name, run)
        for name in FUNCTIONS
        for run in range(1, N_RUNS + 1)
    }
    if seen != expected:
        raise RuntimeError(
            f"H4e SCHO control incomplete: {len(seen)}/{len(expected)} rows"
        )

    return rows


def _build_summary(rows):
    out = []

    for variant in VARIANTS:
        for name in FUNCTIONS:
            b = get_benchmark(name)
            group = sorted(
                [
                    row for row in rows
                    if row["Variant"] == variant
                    and row["Function"] == name
                ],
                key=lambda row: row["Run"],
            )

            if len(group) != N_RUNS:
                raise RuntimeError(
                    f"{variant}/{name}: expected {N_RUNS}, got {len(group)}"
                )

            scores = np.asarray(
                [row["BestScore"] for row in group],
                dtype=float,
            )

            out.append(
                {
                    "Variant": variant,
                    "Function": name,
                    "Runs": N_RUNS,
                    "Dimension": int(b.dim),
                    "Best": float(np.min(scores)),
                    "Average": float(np.mean(scores)),
                    "STD_sample_ddof1": float(np.std(scores, ddof=1)),
                    "Median": float(np.median(scores)),
                    "Worst": float(np.max(scores)),
                }
            )

    return out


def _scho_means(h4e_rows):
    out = {}
    for name in FUNCTIONS:
        scores = np.asarray(
            [
                row["BestScore"]
                for row in h4e_rows
                if row["Function"] == name
            ],
            dtype=float,
        )
        if scores.size != N_RUNS:
            raise RuntimeError(f"SCHO/{name}: expected {N_RUNS} scores")
        out[name] = float(np.mean(scores))
    return out


def _pairwise(summary, h4e_rows):
    variant_means = {
        (row["Variant"], row["Function"]): float(row["Average"])
        for row in summary
    }
    scho = _scho_means(h4e_rows)

    per_function = []
    counts = []

    for variant in VARIANTS:
        scho_credit = 0
        variant_credit = 0
        ties = 0
        scho_strict = 0
        variant_strict = 0

        for name in FUNCTIONS:
            a = scho[name]
            b = variant_means[(variant, name)]

            tied = bool(np.isclose(a, b, rtol=TIE_RTOL, atol=TIE_ATOL))

            if tied:
                comp = "TIE"
                sc = 1
                vc = 1
                ties += 1
            elif a < b:
                comp = "SCHO"
                sc = 1
                vc = 0
                scho_strict += 1
            else:
                comp = variant
                sc = 0
                vc = 1
                variant_strict += 1

            scho_credit += sc
            variant_credit += vc

            per_function.append(
                {
                    "Variant": variant,
                    "Function": name,
                    "SCHO_Average": a,
                    "Variant_Average": b,
                    "Comparison": comp,
                    "SCHO_Credit": sc,
                    "Variant_Credit": vc,
                    "AbsoluteMeanDifference": abs(a - b),
                }
            )

        paper_s, paper_v = PAPER_COUNTS[variant]
        counts.append(
            {
                "Variant": variant,
                "SCHO_OptimalAverageCount": scho_credit,
                "Variant_OptimalAverageCount": variant_credit,
                "Ties": ties,
                "SCHO_StrictWins": scho_strict,
                "Variant_StrictWins": variant_strict,
                "Paper_SCHO_Count": paper_s,
                "Paper_Variant_Count": paper_v,
                "SCHO_Count_Delta_vs_Paper": scho_credit - paper_s,
                "Variant_Count_Delta_vs_Paper": variant_credit - paper_v,
                "TieRTol": TIE_RTOL,
                "TieATol": TIE_ATOL,
            }
        )

    return per_function, counts


def _write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _plot_group(letter, variants, pairwise_rows, path):
    import matplotlib.pyplot as plt

    by_variant = {row["Variant"]: row for row in pairwise_rows}

    labels = []
    values = []
    for variant in variants:
        row = by_variant[variant]
        labels.extend([f"SCHO/{variant}", variant])
        values.extend(
            [
                int(row["SCHO_OptimalAverageCount"]),
                int(row["Variant_OptimalAverageCount"]),
            ]
        )

    x = np.arange(len(values))
    fig, ax = plt.subplots(figsize=(max(6.5, len(values) * 1.15), 4.2))
    bars = ax.bar(x, values)
    ax.set_ylim(0, 23)
    ax.set_ylabel("Number of pairwise-optimal average results")
    ax.set_title(
        f"SCHO Fig.7({letter}) controlled reproduction "
        "(H4h controlled variants)"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            value + 0.25,
            str(value),
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(fig)


def _write_report(summary, pairwise_rows):
    lines = [
        "# H4i — SCHO Fig.7 controlled 7590-run experiment",
        "",
        "## Exactness tier",
        "",
        "`CONTROLLED-INTERPRETATION`",
        "",
        "The 11 Fig.7 variants use the explicit H4h project-frozen equations.",
        "They are not claimed to be unrecovered author implementations.",
        "",
        "## Formal protocol",
        "",
        "- Variants: V1–V11",
        "- Functions: F1–F23",
        "- N = 30",
        "- MaxIter = 500",
        "- 30 runs/variant/function",
        "- optimizer seeds = 1000–1029",
        "- objective seeds intentionally identical to H4e",
        "- formal variant runs = 7590",
        "- SCHO baseline reused from H4e = 690 already-completed aligned runs",
        "",
        "## Fig.7 counting convention",
        "",
        "The paper describes the bars as the number of average optimal solutions",
        "but does not provide a machine-readable counting rule. H4i freezes the",
        "following controlled interpretation:",
        "",
        "For each SCHO-vs-variant pair and each function, compare the 30-run",
        "mean final fitness under minimization. The lower mean receives one",
        "credit. If the means are numerically tied under",
        f"`np.isclose(rtol={TIE_RTOL}, atol={TIE_ATOL})`, both receive one credit.",
        "",
        "This interpretation explains why the two bar counts for one comparison",
        "may sum to more than 23: tied functions are credited to both.",
        "",
        "The tie rule is frozen before seeing H4i results and must not be tuned",
        "to reproduce the printed paper counts.",
        "",
        "## Pairwise counts",
        "",
        "| Variant | Repro SCHO | Repro Variant | Ties | Paper SCHO | Paper Variant |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for row in pairwise_rows:
        lines.append(
            f"| {row['Variant']} "
            f"| {row['SCHO_OptimalAverageCount']} "
            f"| {row['Variant_OptimalAverageCount']} "
            f"| {row['Ties']} "
            f"| {row['Paper_SCHO_Count']} "
            f"| {row['Paper_Variant_Count']} |"
        )

    lines += [
        "",
        "## Paper anchors",
        "",
        "- Fig.7(a): V1 = 18/15, V2 = 20/13",
        "- Fig.7(b): V3 = 17/15, V4 = 17/14, V5 = 17/16, V6 = 18/14",
        "- Fig.7(c): V7 = 20/13, V8 = 20/11, V9 = 18/9",
        "- Fig.7(d): V10 = 20/13, V11 = 18/15",
        "",
        "## Interpretation boundary",
        "",
        "Agreement or disagreement with the paper bars cannot validate or",
        "invalidate the unrecovered author equations, because H4h explicitly",
        "uses controlled substitute formulas for unresolved variants.",
        "",
        "No formula or parameter may be adjusted after H4i merely to improve",
        "bar-count agreement.",
        "",
        "## Outputs",
        "",
        f"- `{RAW_PATH}`",
        f"- `{SUMMARY_PATH}`",
        f"- `{PER_FUNCTION_PATH}`",
        f"- `{PAIRWISE_PATH}`",
        f"- `{FIG_A}`",
        f"- `{FIG_B}`",
        f"- `{FIG_C}`",
        f"- `{FIG_D}`",
        "",
        "## Next",
        "",
        "H4j should audit paper-agreement patterns and freeze Fig.7 as a",
        "controlled interpretation, without tuning.",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _progress(done, total, row, wall_start, initial_complete):
    elapsed = time.perf_counter() - wall_start
    new_done = max(done - initial_complete, 1)
    avg_wall = elapsed / new_done
    remain = max(total - done, 0)
    rough = avg_wall * remain

    print(
        f"[{done:04d}/{total}] "
        f"{row['Variant']:<3} {row['Function']:<3} "
        f"run={row['Run']:02d} seed={row['OptimizerSeed']} "
        f"best={row['BestScore']:.10g} "
        f"worker_time={row['ElapsedSeconds']:.1f}s "
        f"rough_remaining={rough/3600:.1f}h"
    )


def main():
    _ensure_dirs()

    h4e_scho = _load_h4e_scho_control()
    print("Protocol-aligned H4e SCHO control: PASS (690/690 rows)")

    rows, complete = _load_checkpoint()

    all_tasks = [
        (variant, name, run)
        for variant in VARIANTS
        for name in FUNCTIONS
        for run in range(1, N_RUNS + 1)
    ]
    pending = [
        task for task in all_tasks
        if (task[0], task[1], task[2]) not in complete
    ]

    total = len(all_tasks)
    workers = _default_workers()
    initial_complete = len(complete)

    print("=" * 132)
    print("H4i - Formal controlled SCHO Fig.7 Variant 1-11 experiment")
    print("=" * 132)
    print("Exactness : CONTROLLED-INTERPRETATION")
    print(f"Variants  : V1-V11")
    print(f"Functions : F1-F23")
    print(f"Protocol  : N={N}, MaxIter={MAX_ITER}, runs={N_RUNS}/variant/function")
    print(f"Seeds     : {BASE_SEED}..{BASE_SEED + N_RUNS - 1}")
    print(f"Variant runs: {total}")
    print("SCHO control: reused from protocol-aligned H4e (690 completed runs)")
    print(f"Workers   : {workers}")
    print(f"Complete  : {len(complete)}/{total}")
    print(f"Checkpoint: {RAW_PATH}")
    print("Rerun the same command after interruption to resume.")
    print("=" * 132)

    if pending:
        wall_start = time.perf_counter()

        if workers == 1:
            for task in pending:
                row = _run_task(task)
                _append_checkpoint(row)
                rows.append(row)
                complete.add((row["Variant"], row["Function"], row["Run"]))
                _progress(
                    len(complete), total, row, wall_start, initial_complete
                )
        else:
            batch_size = workers * 2

            for start in range(0, len(pending), batch_size):
                batch = pending[start:start + batch_size]

                with ProcessPoolExecutor(max_workers=workers) as pool:
                    futures = {
                        pool.submit(_run_task, task): task
                        for task in batch
                    }

                    for future in as_completed(futures):
                        row = future.result()
                        _append_checkpoint(row)
                        rows.append(row)
                        complete.add(
                            (row["Variant"], row["Function"], row["Run"])
                        )
                        _progress(
                            len(complete),
                            total,
                            row,
                            wall_start,
                            initial_complete,
                        )

    if len(complete) != total:
        raise RuntimeError(
            f"H4i incomplete: {len(complete)}/{total} variant runs"
        )

    summary = _build_summary(rows)
    per_function, pairwise = _pairwise(summary, h4e_scho)

    _write_csv(SUMMARY_PATH, SUMMARY_FIELDS, summary)
    _write_csv(PER_FUNCTION_PATH, PER_FUNCTION_FIELDS, per_function)
    _write_csv(PAIRWISE_PATH, PAIRWISE_FIELDS, pairwise)

    _plot_group("a", FIG_GROUPS["a"], pairwise, FIG_A)
    _plot_group("b", FIG_GROUPS["b"], pairwise, FIG_B)
    _plot_group("c", FIG_GROUPS["c"], pairwise, FIG_C)
    _plot_group("d", FIG_GROUPS["d"], pairwise, FIG_D)

    _write_report(summary, pairwise)

    print("\n" + "-" * 132)
    print("Controlled Fig.7 pairwise counts:")
    for row in pairwise:
        print(
            f"{row['Variant']:<3} "
            f"repro SCHO/variant="
            f"{row['SCHO_OptimalAverageCount']:>2}/"
            f"{row['Variant_OptimalAverageCount']:<2} "
            f"ties={row['Ties']:<2} | "
            f"paper="
            f"{row['Paper_SCHO_Count']:>2}/"
            f"{row['Paper_Variant_Count']:<2}"
        )

    print("-" * 132)
    print("H4i RESULT: PASS")
    print(f"Formal controlled variant runs complete: {total}/{total}")
    print("Protocol-aligned SCHO control reused: 690/690")
    print(f"Saved raw      : {RAW_PATH}")
    print(f"Saved summary  : {SUMMARY_PATH}")
    print(f"Saved pairwise : {PAIRWISE_PATH}")
    print(f"Saved report   : {REPORT_PATH}")
    print("Fig.7 figures  : 4/4")
    print("No parameter/formula tuning was performed.")
    print("Next: H4j Fig.7 paper-agreement diagnostic + controlled freeze.")
    print("=" * 132)


if __name__ == "__main__":
    main()
