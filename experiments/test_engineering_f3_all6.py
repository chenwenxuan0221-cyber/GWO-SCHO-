"""F3 - Six engineering problems, single-run full coverage.

Purpose
-------
Run the frozen GWO and frozen source-faithful SCHO exactly once on each of
the six primary engineering problems using the Stage-F project protocol.

This is still a STRUCTURAL / COVERAGE stage, not a statistical performance
comparison.

Protocol
--------
N = 30
MaxIter = 500
seed = 1000
death penalty = 1e30
feasibility tolerance = 1e-8

Primary cantilever formulation
------------------------------
The main six-problem experiment uses `CANTILEVER_PRINTED`, i.e. the objective
coefficient 0.6224 printed in the SCHO paper. The separately labelled
table-consistent diagnostic variant is NOT mixed into the primary results.

Output
------
results/raw/engineering_f3_single_run.csv
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


N = 30
MAX_ITER = 500
SEED = 1000
PENALTY = DEFAULT_DEATH_PENALTY
FEAS_TOL = DEFAULT_FEASIBILITY_TOLERANCE

OUTPUT_CSV = Path("results/raw/engineering_f3_single_run.csv")


def optimizer_bounds(benchmark):
    """Return scalar bounds when every dimension has the same interval.

    This is mathematically equivalent to vector bounds, but preserves the
    scalar-bound branch of the frozen source-faithful SCHO implementation
    for equal-bound problems such as cantilever and three-bar truss.
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


def run_one(algorithm_name, algorithm, benchmark):
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
            seed=SEED,
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
            "seed": SEED,
            "N": N,
            "MaxIter": MAX_ITER,
            "penalty": PENALTY,
            "feasibility_tolerance": FEAS_TOL,
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

    # Audit the returned best position. This is safe even if it is infeasible:
    # singular constraints have already been made non-crashing in F2 v2.
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
            "Returned feasible-score bookkeeping does not match the returned "
            "best position."
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
        "seed": SEED,
        "N": N,
        "MaxIter": MAX_ITER,
        "penalty": PENALTY,
        "feasibility_tolerance": FEAS_TOL,
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


def write_csv(rows):
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    max_dim = max(b.dim for b in PRIMARY_BENCHMARKS)
    fieldnames = [
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

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            out = {k: row[k] for k in fieldnames if not k.startswith("x")}
            for i in range(max_dim):
                out[f"x{i+1}"] = (
                    row["best_x"][i] if i < len(row["best_x"]) else ""
                )
            writer.writerow(out)


def main():
    print("=" * 132)
    print("F3 - Six engineering problems / single-run full coverage")
    print("=" * 132)
    print(f"N={N}, MaxIter={MAX_ITER}, seed={SEED}")
    print(f"Death penalty        : {PENALTY:.1e}")
    print(f"Feasibility tolerance: {FEAS_TOL:.1e}")
    print("Algorithms           : GWO, SCHO")
    print("Primary problems     : 6")
    print("Total optimization runs: 12")
    print("Cantilever           : paper-printed 0.6224 formulation")
    print("Purpose              : full coverage, NOT statistical ranking")
    print("=" * 132)

    rows = []
    total_start = time.perf_counter()

    for problem_index, benchmark in enumerate(PRIMARY_BENCHMARKS, start=1):
        n_constraints = benchmark.constraints(benchmark.paper_best_x).size

        print(
            f"\n[{problem_index}/6] {benchmark.key}: {benchmark.name} "
            f"(dim={benchmark.dim}, constraints={n_constraints})"
        )
        print("-" * 132)

        for algorithm_name, algorithm in (("GWO", gwo), ("SCHO", scho)):
            row = run_one(
                algorithm_name,
                algorithm,
                benchmark,
            )
            rows.append(row)

            best_text = (
                f"{row['best_fitness']:.10e}"
                if np.isfinite(row["best_fitness"])
                else "nan"
            )
            violation_text = (
                f"{row['max_violation']:.3e}"
                if np.isfinite(row["max_violation"])
                else "nan"
            )

            print(
                f"  {algorithm_name:<4} "
                f"Best={best_text:<16} "
                f"Feasible={str(row['feasible']):<5} "
                f"MaxViolation={violation_text:<12} "
                f"Time={row['elapsed_seconds']:.2f}s  "
                f"{row['status']}"
            )

            if row["best_x"]:
                print(
                    "       x="
                    + np.array2string(
                        np.asarray(row["best_x"], dtype=float),
                        precision=8,
                        separator=", ",
                        suppress_small=False,
                    )
                )

            if row["message"]:
                print(f"       note={row['message']}")

    total_elapsed = time.perf_counter() - total_start

    write_csv(rows)

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

    print("\n" + "=" * 132)
    print("F3 final audit")
    print("=" * 132)
    print(f"Completed runs        : {len(rows)}/12")
    print(f"Feasible PASS runs    : {len(passes)}/12")
    print(f"No-feasible diagnostics: {len(no_feasible)}")
    print(f"Structural failures   : {len(structural_fails)}")
    print(f"Total elapsed         : {total_elapsed:.2f}s")
    print(f"Saved CSV             : {OUTPUT_CSV}")

    if no_feasible:
        print("\nNO_FEASIBLE_FOUND diagnostics:")
        for r in no_feasible:
            print(
                f"  - {r['problem']} / {r['algorithm']} / seed={r['seed']}"
            )

    if structural_fails:
        print("\nStructural failures:")
        for r in structural_fails:
            print(
                f"  - {r['problem']} / {r['algorithm']}: "
                f"{r['status']} {r['message']}"
            )
        print("\nF3 RESULT: FAIL")
        raise SystemExit(1)

    if no_feasible:
        print("\nF3 RESULT: PASS_WITH_DIAGNOSTIC")
    else:
        print("\nF3 RESULT: PASS")

    print("All six engineering problems were covered by both frozen optimizers.")
    print("NO_FEASIBLE_FOUND outcomes, if any, are retained rather than tuned away.")
    print("No statistical performance conclusion is made in F3.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
