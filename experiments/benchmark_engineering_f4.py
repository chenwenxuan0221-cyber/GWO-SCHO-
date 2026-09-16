"""F4 - 30-run engineering experiment for all six primary problems.

Stage-F project protocol
------------------------
Problems     : 6 primary engineering problems
Algorithms   : frozen GWO + frozen source-faithful SCHO
Runs         : 30 independent runs per algorithm/problem
Seeds        : 1000..1029
Population   : N=30
Iterations   : MaxIter=500
Penalty      : 1e30 (project convention; paper gives no numeric constant)
Feasibility  : all bounds satisfied and every g_i(x) <= 1e-8

Total optimizer runs: 6 * 2 * 30 = 360.

Important interpretation
------------------------
- PASS: optimizer returned a feasible best design with consistent bookkeeping.
- NO_FEASIBLE_FOUND: run completed structurally, but best fitness stayed at
  the death penalty. This is retained as data and is NOT tuned away.
- ERROR / STRUCTURAL_FAIL: implementation/runtime problem requiring review.

Cantilever
----------
The primary six-problem experiment uses the paper-printed coefficient 0.6224.
The separate 0.06224 diagnostic variant is NOT mixed into this experiment.

Outputs
-------
results/raw/engineering_f4_runs.csv
results/processed/engineering_f4_summary.csv

The summary deliberately reports feasible-only statistics separately from
all-run penalized statistics so that infeasible runs cannot be hidden by an
ordinary mean.
"""

from __future__ import annotations

import csv
from pathlib import Path
import time

import numpy as np

from algorithms.gwo import gwo
from algorithms.scho import scho
from benchmarks.constraint_handling import (
    DEFAULT_DEATH_PENALTY,
    DEFAULT_FEASIBILITY_TOLERANCE,
    evaluate_candidate,
    make_death_penalty_objective,
)
from benchmarks.engineering_design import PRIMARY_BENCHMARKS


# ---------------------------------------------------------------------------
# Frozen F4 project protocol
# ---------------------------------------------------------------------------

N = 30
MAX_ITER = 500
SEEDS = tuple(range(1000, 1030))
PENALTY = DEFAULT_DEATH_PENALTY
FEAS_TOL = DEFAULT_FEASIBILITY_TOLERANCE

RAW_CSV = Path("results/raw/engineering_f4_runs.csv")
SUMMARY_CSV = Path("results/processed/engineering_f4_summary.csv")

ALGORITHMS = (
    ("GWO", gwo),
    ("SCHO", scho),
)


def optimizer_bounds(benchmark):
    """Use scalar bounds for equal-bound problems.

    This is mathematically equivalent to vector bounds, but preserves the
    scalar-bound branch of the frozen source-faithful SCHO implementation.
    """
    lb = np.asarray(benchmark.lb, dtype=float).reshape(-1)
    ub = np.asarray(benchmark.ub, dtype=float).reshape(-1)

    if np.all(lb == lb[0]) and np.all(ub == ub[0]):
        return float(lb[0]), float(ub[0])
    return lb, ub


def curve_audit(curve):
    arr = np.asarray(curve, dtype=float).reshape(-1)

    finite = bool(np.all(np.isfinite(arr)))
    correct_len = arr.size == MAX_ITER
    nonincreasing = bool(
        arr.size <= 1
        or np.all(
            np.diff(arr)
            <= 1e-12 * np.maximum(1.0, np.abs(arr[:-1]))
        )
    )

    return arr, finite, correct_len, nonincreasing


def run_one(algorithm_name, algorithm, benchmark, seed):
    objective = make_death_penalty_objective(
        benchmark,
        penalty=PENALTY,
        tolerance=FEAS_TOL,
    )
    lb, ub = optimizer_bounds(benchmark)

    t0 = time.perf_counter()

    try:
        best_score, best_pos, curve = algorithm(
            obj_func=objective,
            dim=benchmark.dim,
            lb=lb,
            ub=ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=seed,
        )
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        return {
            "algorithm": algorithm_name,
            "problem": benchmark.key,
            "problem_name": benchmark.name,
            "dim": benchmark.dim,
            "n_constraints": int(
                benchmark.constraints(benchmark.paper_best_x).size
            ),
            "seed": seed,
            "N": N,
            "MaxIter": MAX_ITER,
            "penalty": PENALTY,
            "feasibility_tolerance": FEAS_TOL,
            "paper_reported_f": benchmark.paper_best_f,
            "best_fitness": np.nan,
            "raw_objective": np.nan,
            "feasible": False,
            "within_bounds": False,
            "max_violation": np.nan,
            "curve_start": np.nan,
            "curve_end": np.nan,
            "curve_len": 0,
            "elapsed_seconds": elapsed,
            "status": "ERROR",
            "message": f"{type(exc).__name__}: {exc}",
            "best_x": [],
        }

    elapsed = time.perf_counter() - t0

    best_score = float(best_score)
    best_pos = np.asarray(best_pos, dtype=float).reshape(-1)
    curve, curve_finite, curve_len_ok, curve_nonincreasing = curve_audit(curve)

    audit = evaluate_candidate(
        benchmark,
        best_pos,
        penalty=PENALTY,
        tolerance=FEAS_TOL,
    )

    score_matches_curve = bool(
        curve.size > 0
        and np.isclose(
            best_score,
            curve[-1],
            rtol=1e-12,
            atol=1e-12,
        )
    )

    found_feasible = bool(best_score < PENALTY)

    if found_feasible:
        score_matches_point = bool(
            audit.feasible
            and audit.max_violation <= FEAS_TOL
            and np.isclose(
                best_score,
                audit.raw_objective,
                rtol=1e-10,
                atol=1e-10,
            )
        )
    else:
        score_matches_point = None

    structural_ok = all(
        [
            np.isfinite(best_score),
            best_pos.shape == (benchmark.dim,),
            audit.within_bounds,
            curve_finite,
            curve_len_ok,
            curve_nonincreasing,
            score_matches_curve,
        ]
    )

    if not structural_ok:
        status = "STRUCTURAL_FAIL"
        message = (
            f"curve_finite={curve_finite}; "
            f"curve_len_ok={curve_len_ok}; "
            f"curve_nonincreasing={curve_nonincreasing}; "
            f"score_matches_curve={score_matches_curve}; "
            f"within_bounds={audit.within_bounds}"
        )
    elif not found_feasible:
        status = "NO_FEASIBLE_FOUND"
        message = "Best fitness stayed at the death penalty."
    elif not score_matches_point:
        status = "STRUCTURAL_FAIL"
        message = (
            "Returned feasible-score bookkeeping does not match "
            "the returned best position."
        )
    else:
        status = "PASS"
        message = ""

    return {
        "algorithm": algorithm_name,
        "problem": benchmark.key,
        "problem_name": benchmark.name,
        "dim": benchmark.dim,
        "n_constraints": int(
            benchmark.constraints(benchmark.paper_best_x).size
        ),
        "seed": seed,
        "N": N,
        "MaxIter": MAX_ITER,
        "penalty": PENALTY,
        "feasibility_tolerance": FEAS_TOL,
        "paper_reported_f": benchmark.paper_best_f,
        "best_fitness": best_score,
        "raw_objective": audit.raw_objective,
        "feasible": audit.feasible,
        "within_bounds": audit.within_bounds,
        "max_violation": audit.max_violation,
        "curve_start": float(curve[0]) if curve.size else np.nan,
        "curve_end": float(curve[-1]) if curve.size else np.nan,
        "curve_len": int(curve.size),
        "elapsed_seconds": elapsed,
        "status": status,
        "message": message,
        "best_x": best_pos.tolist(),
    }


def raw_fieldnames():
    max_dim = max(b.dim for b in PRIMARY_BENCHMARKS)
    return [
        "algorithm",
        "problem",
        "problem_name",
        "dim",
        "n_constraints",
        "seed",
        "N",
        "MaxIter",
        "penalty",
        "feasibility_tolerance",
        "paper_reported_f",
        "best_fitness",
        "raw_objective",
        "feasible",
        "within_bounds",
        "max_violation",
        "curve_start",
        "curve_end",
        "curve_len",
        "elapsed_seconds",
        "status",
        "message",
    ] + [f"x{i}" for i in range(1, max_dim + 1)]


def csv_ready_row(row):
    fields = raw_fieldnames()
    out = {k: row[k] for k in fields if not k.startswith("x")}
    max_dim = sum(1 for k in fields if k.startswith("x"))

    for i in range(max_dim):
        out[f"x{i+1}"] = row["best_x"][i] if i < len(row["best_x"]) else ""

    return out


def write_raw_csv(rows):
    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)

    with RAW_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=raw_fieldnames())
        writer.writeheader()
        for row in rows:
            writer.writerow(csv_ready_row(row))


def sample_std(values):
    arr = np.asarray(values, dtype=float)
    if arr.size < 2:
        return np.nan
    return float(np.std(arr, ddof=1))


def summarize_group(group_rows, benchmark, algorithm_name):
    total = len(group_rows)
    pass_rows = [r for r in group_rows if r["status"] == "PASS"]
    no_feasible_rows = [
        r for r in group_rows
        if r["status"] == "NO_FEASIBLE_FOUND"
    ]
    structural_rows = [
        r for r in group_rows
        if r["status"] in {"ERROR", "STRUCTURAL_FAIL"}
    ]

    feasible_values = np.asarray(
        [r["raw_objective"] for r in pass_rows],
        dtype=float,
    )

    # Penalized-all-run stats are reported for transparency only.
    # If one or more runs did not find feasibility, the 1e30 penalty can
    # dominate these values. Use feasible-only stats for solution quality.
    valid_penalized = np.asarray(
        [
            r["best_fitness"]
            for r in group_rows
            if np.isfinite(r["best_fitness"])
        ],
        dtype=float,
    )

    if feasible_values.size:
        best_feasible = float(np.min(feasible_values))
        mean_feasible = float(np.mean(feasible_values))
        median_feasible = float(np.median(feasible_values))
        std_feasible = sample_std(feasible_values)
        worst_feasible = float(np.max(feasible_values))
    else:
        best_feasible = np.nan
        mean_feasible = np.nan
        median_feasible = np.nan
        std_feasible = np.nan
        worst_feasible = np.nan

    if valid_penalized.size:
        penalized_best = float(np.min(valid_penalized))
        penalized_mean = float(np.mean(valid_penalized))
        penalized_std = sample_std(valid_penalized)
        penalized_worst = float(np.max(valid_penalized))
    else:
        penalized_best = np.nan
        penalized_mean = np.nan
        penalized_std = np.nan
        penalized_worst = np.nan

    return {
        "algorithm": algorithm_name,
        "problem": benchmark.key,
        "problem_name": benchmark.name,
        "dim": benchmark.dim,
        "n_constraints": int(
            benchmark.constraints(benchmark.paper_best_x).size
        ),
        "runs": total,
        "feasible_runs": len(pass_rows),
        "feasible_rate": len(pass_rows) / total if total else np.nan,
        "no_feasible_runs": len(no_feasible_rows),
        "structural_failures": len(structural_rows),
        "best_feasible": best_feasible,
        "mean_feasible": mean_feasible,
        "median_feasible": median_feasible,
        "std_feasible_sample": std_feasible,
        "worst_feasible": worst_feasible,
        "penalized_best_all_runs": penalized_best,
        "penalized_mean_all_runs": penalized_mean,
        "penalized_std_all_runs_sample": penalized_std,
        "penalized_worst_all_runs": penalized_worst,
        "paper_reported_f": benchmark.paper_best_f,
        "reference_note": (
            "Paper-printed cantilever objective; Table 20 is internally "
            "inconsistent by about a factor of 10."
            if benchmark.key == "cantilever_printed"
            else ""
        ),
    }


def write_summary_csv(rows):
    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)

    summary_rows = []

    for benchmark in PRIMARY_BENCHMARKS:
        for algorithm_name, _ in ALGORITHMS:
            group_rows = [
                r for r in rows
                if r["problem"] == benchmark.key
                and r["algorithm"] == algorithm_name
            ]
            summary_rows.append(
                summarize_group(
                    group_rows,
                    benchmark,
                    algorithm_name,
                )
            )

    fieldnames = list(summary_rows[0].keys())

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    return summary_rows


def fmt_value(value):
    if value is None:
        return "nan"
    try:
        if np.isnan(value):
            return "nan"
    except TypeError:
        pass
    return f"{float(value):.10e}"


def main():
    print("=" * 138)
    print("F4 - 30-run engineering experiment")
    print("=" * 138)
    print("Problems             : 6")
    print("Algorithms           : GWO, SCHO")
    print("Runs/problem/algorithm: 30")
    print("Seeds                : 1000..1029")
    print(f"N                    : {N}")
    print(f"MaxIter              : {MAX_ITER}")
    print(f"Death penalty        : {PENALTY:.1e}")
    print(f"Feasibility tolerance: {FEAS_TOL:.1e}")
    print("Total optimizer runs : 360")
    print("Cantilever           : paper-printed 0.6224 formulation")
    print("=" * 138)

    rows = []
    total_start = time.perf_counter()
    completed = 0
    total_expected = len(PRIMARY_BENCHMARKS) * len(ALGORITHMS) * len(SEEDS)

    for p_index, benchmark in enumerate(PRIMARY_BENCHMARKS, start=1):
        print(
            f"\n[{p_index}/6] {benchmark.key}: {benchmark.name}"
        )
        print("-" * 138)

        for algorithm_name, algorithm in ALGORITHMS:
            algorithm_rows = []

            for seed in SEEDS:
                row = run_one(
                    algorithm_name,
                    algorithm,
                    benchmark,
                    seed,
                )
                rows.append(row)
                algorithm_rows.append(row)
                completed += 1

                # Write a current snapshot after every run. If the console or
                # machine stops later, completed work remains available.
                write_raw_csv(rows)

                print(
                    f"  [{completed:03d}/{total_expected}] "
                    f"{algorithm_name:<4} seed={seed} "
                    f"status={row['status']:<18} "
                    f"best={fmt_value(row['best_fitness'])} "
                    f"time={row['elapsed_seconds']:.2f}s"
                )

            pass_count = sum(
                r["status"] == "PASS"
                for r in algorithm_rows
            )
            no_feasible_count = sum(
                r["status"] == "NO_FEASIBLE_FOUND"
                for r in algorithm_rows
            )
            failure_count = sum(
                r["status"] in {"ERROR", "STRUCTURAL_FAIL"}
                for r in algorithm_rows
            )

            feasible_values = [
                r["raw_objective"]
                for r in algorithm_rows
                if r["status"] == "PASS"
            ]

            best_text = (
                fmt_value(min(feasible_values))
                if feasible_values
                else "nan"
            )

            print(
                f"  -> {algorithm_name} summary for {benchmark.key}: "
                f"Feasible={pass_count}/30, "
                f"NoFeasible={no_feasible_count}, "
                f"StructuralFail={failure_count}, "
                f"BestFeasible={best_text}"
            )

    total_elapsed = time.perf_counter() - total_start

    # Final complete raw snapshot + processed summary.
    write_raw_csv(rows)
    summary_rows = write_summary_csv(rows)

    structural_fails = [
        r for r in rows
        if r["status"] in {"ERROR", "STRUCTURAL_FAIL"}
    ]
    no_feasible = [
        r for r in rows
        if r["status"] == "NO_FEASIBLE_FOUND"
    ]
    passes = [
        r for r in rows
        if r["status"] == "PASS"
    ]

    print("\n" + "=" * 138)
    print("F4 final audit")
    print("=" * 138)
    print(f"Completed runs          : {len(rows)}/{total_expected}")
    print(f"Feasible PASS runs      : {len(passes)}/{total_expected}")
    print(f"NO_FEASIBLE_FOUND runs  : {len(no_feasible)}")
    print(f"Structural failures     : {len(structural_fails)}")
    print(f"Elapsed                 : {total_elapsed/60.0:.2f} min")
    print(f"Raw CSV                 : {RAW_CSV}")
    print(f"Processed summary CSV   : {SUMMARY_CSV}")

    print("\nFeasibility summary")
    print("-" * 138)

    for s in summary_rows:
        print(
            f"  {s['problem']:<22} {s['algorithm']:<4} "
            f"Feasible={s['feasible_runs']:>2}/30 "
            f"Rate={s['feasible_rate']:.3f} "
            f"Best={fmt_value(s['best_feasible'])} "
            f"Mean={fmt_value(s['mean_feasible'])} "
            f"Std={fmt_value(s['std_feasible_sample'])}"
        )

    if structural_fails:
        print("\nStructural failures:")
        for r in structural_fails:
            print(
                f"  - {r['problem']} / {r['algorithm']} / "
                f"seed={r['seed']}: {r['status']} {r['message']}"
            )
        print("\nF4 RESULT: FAIL")
        raise SystemExit(1)

    if no_feasible:
        print("\nF4 RESULT: PASS_WITH_DIAGNOSTIC")
    else:
        print("\nF4 RESULT: PASS")

    print("All 360 requested optimizer runs completed.")
    print("Feasibility success rate is retained as a primary engineering metric.")
    print("Feasible-only solution statistics are kept separate from penalized all-run statistics.")
    print("No paper-performance conclusion is made by this script.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
