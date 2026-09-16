"""F2 v2 - Engineering constraint-handler + optimizer integration smoke test.

This test is STRUCTURAL. It does not judge optimization quality statistically.

Important interpretation:
- A completed optimizer run that returns a feasible finite best design is PASS.
- A completed run whose best fitness remains the death penalty is reported as
  NO_FEASIBLE_FOUND. This is a search diagnostic, not an interface failure.
- Any crash, malformed curve, score/curve inconsistency, or invalid feasible
  score is a structural FAIL.

Protocol:
N=30, MaxIter=500, seed=1000, death penalty=1e30, tolerance=1e-8.
"""

from __future__ import annotations

import numpy as np

from algorithms.gwo import gwo
from algorithms.scho import scho
from benchmarks.constraint_handling import (
    DEFAULT_DEATH_PENALTY,
    DEFAULT_FEASIBILITY_TOLERANCE,
    evaluate_candidate,
    make_death_penalty_objective,
)
from benchmarks.engineering_design import SPRING, WELDED_BEAM, THREE_BAR_TRUSS


N = 30
MAX_ITER = 500
SEED = 1000
PENALTY = DEFAULT_DEATH_PENALTY
FEAS_TOL = DEFAULT_FEASIBILITY_TOLERANCE
REPRESENTATIVE = (SPRING, WELDED_BEAM, THREE_BAR_TRUSS)


def _optimizer_bounds(benchmark):
    """Use scalar bounds when every dimension has the same box.

    This is mathematically identical to vector bounds, but it is important for
    the frozen source-faithful SCHO implementation because its MATLAB source
    has distinct scalar-bound and vector-bound initialization branches.
    """
    lb = np.asarray(benchmark.lb, dtype=float).reshape(-1)
    ub = np.asarray(benchmark.ub, dtype=float).reshape(-1)

    if np.all(lb == lb[0]) and np.all(ub == ub[0]):
        return float(lb[0]), float(ub[0])
    return lb, ub


def _curve_checks(curve):
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


def _run_one(name, algorithm, benchmark):
    objective = make_death_penalty_objective(
        benchmark,
        penalty=PENALTY,
        tolerance=FEAS_TOL,
    )
    lb, ub = _optimizer_bounds(benchmark)

    best_score, best_pos, curve = algorithm(
        obj_func=objective,
        dim=benchmark.dim,
        lb=lb,
        ub=ub,
        N=N,
        MaxIter=MAX_ITER,
        seed=SEED,
    )

    best_score = float(best_score)
    best_pos = np.asarray(best_pos, dtype=float).reshape(-1)
    curve, curve_finite, curve_len_ok, curve_nonincreasing = _curve_checks(curve)

    audit = evaluate_candidate(
        benchmark,
        best_pos,
        penalty=PENALTY,
        tolerance=FEAS_TOL,
    )

    score_matches_curve = bool(
        curve.size > 0
        and np.isclose(best_score, curve[-1], rtol=1e-12, atol=1e-12)
    )

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

    found_feasible = best_score < PENALTY

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
        status = "PASS" if structural_ok and score_matches_point else "FAIL"
    else:
        score_matches_point = None
        # A flat death-penalty result is a meaningful diagnostic: the
        # optimizer completed, but this seed did not discover feasibility.
        status = "NO_FEASIBLE_FOUND" if structural_ok else "FAIL"

    return {
        "algorithm": name,
        "benchmark": benchmark,
        "best_score": best_score,
        "best_pos": best_pos,
        "curve": curve,
        "audit": audit,
        "found_feasible": found_feasible,
        "score_matches_point": score_matches_point,
        "structural_ok": structural_ok,
        "status": status,
    }


def main():
    print("=" * 124)
    print("F2 v2 - Engineering constraint-handler + optimizer integration smoke test")
    print("=" * 124)
    print(f"N={N}, MaxIter={MAX_ITER}, seed={SEED}")
    print(f"Project death penalty : {PENALTY:.1e}")
    print(f"Feasibility tolerance : {FEAS_TOL:.1e}")
    print("Problems              : spring, welded_beam, three_bar_truss")
    print("Algorithms            : GWO, SCHO")
    print("Purpose               : structural integration, NOT performance ranking")
    print("=" * 124)

    print("\nDeath-penalty wrapper audit")
    print("-" * 124)

    for benchmark in REPRESENTATIVE:
        objective = make_death_penalty_objective(
            benchmark, penalty=PENALTY, tolerance=FEAS_TOL
        )

        paper_eval = evaluate_candidate(
            benchmark,
            benchmark.paper_best_x,
            penalty=PENALTY,
            tolerance=FEAS_TOL,
        )
        if not paper_eval.feasible:
            raise AssertionError(
                f"{benchmark.key}: frozen paper point became infeasible."
            )
        if not np.isclose(
            objective(benchmark.paper_best_x),
            paper_eval.raw_objective,
            rtol=1e-12,
            atol=1e-12,
        ):
            raise AssertionError(
                f"{benchmark.key}: wrapper altered a feasible objective."
            )

        bad_x = benchmark.paper_best_x.copy()
        bad_x[0] = benchmark.lb[0] - max(1.0, abs(benchmark.lb[0]) + 1.0)

        if objective(bad_x) != PENALTY:
            raise AssertionError(
                f"{benchmark.key}: infeasible point did not receive penalty."
            )

        print(
            f"{benchmark.key:<18} "
            f"paper-point feasible=True, "
            f"infeasible-test fitness={PENALTY:.1e}  PASS"
        )

    # Explicitly verify the formerly crashing singular truss boundary.
    truss_origin = np.zeros(THREE_BAR_TRUSS.dim)
    truss_origin_fitness = make_death_penalty_objective(
        THREE_BAR_TRUSS, penalty=PENALTY, tolerance=FEAS_TOL
    )(truss_origin)
    if truss_origin_fitness != PENALTY:
        raise AssertionError("three_bar_truss: singular origin was not penalized.")
    print(
        "three_bar_truss@0  singular boundary -> "
        f"fitness={truss_origin_fitness:.1e}  PASS"
    )

    print("\nOptimizer integration")
    print("-" * 124)

    results = []
    for benchmark in REPRESENTATIVE:
        n_constraints = benchmark.constraints(benchmark.paper_best_x).size
        print(
            f"\n{benchmark.key}: {benchmark.name} "
            f"(dim={benchmark.dim}, constraints={n_constraints})"
        )

        for name, algorithm in (("GWO", gwo), ("SCHO", scho)):
            result = _run_one(name, algorithm, benchmark)
            results.append(result)

            a = result["audit"]
            c = result["curve"]

            print(
                f"  {name:<4} "
                f"Best={result['best_score']:.10e}  "
                f"Feasible={a.feasible}  "
                f"MaxViolation={a.max_violation:.3e}  "
                f"Curve[0]={c[0]:.10e}  "
                f"Curve[-1]={c[-1]:.10e}  "
                f"{result['status']}"
            )
            print(
                "       x="
                + np.array2string(
                    result["best_pos"],
                    precision=8,
                    separator=", ",
                    suppress_small=False,
                )
            )

    structural_failures = [r for r in results if r["status"] == "FAIL"]
    no_feasible = [r for r in results if r["status"] == "NO_FEASIBLE_FOUND"]
    feasible = [r for r in results if r["status"] == "PASS"]

    print("\n" + "-" * 124)
    print("F2 final audit")
    print("-" * 124)
    print(f"Wrapper audits       : 4/4 PASS")
    print(f"Structural runs      : {len(results)-len(structural_failures)}/{len(results)} PASS")
    print(f"Feasible best designs: {len(feasible)}/{len(results)}")
    print(f"No-feasible diagnostics: {len(no_feasible)}")

    if structural_failures:
        print("\nStructural failures:")
        for r in structural_failures:
            print(f"  - {r['benchmark'].key} / {r['algorithm']}")
        print("\nF2 RESULT: FAIL")
        raise SystemExit(1)

    if no_feasible:
        print("\nDiagnostic only — completed runs that did not discover feasibility:")
        for r in no_feasible:
            print(
                f"  - {r['benchmark'].key} / {r['algorithm']} "
                f"(seed={SEED}, best stayed at death penalty)"
            )

    print("\nF2 RESULT: PASS_WITH_DIAGNOSTIC" if no_feasible else "\nF2 RESULT: PASS")
    print("The wrapper and both frozen optimizers are structurally integrated.")
    print("A NO_FEASIBLE_FOUND result is carried forward to F3/F4; it is not hidden or retuned away.")
    print("Optimization quality has NOT yet been judged statistically.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
