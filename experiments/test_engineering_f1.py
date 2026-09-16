"""F1 deterministic audit for the six engineering benchmark definitions.

No GWO/SCHO optimization is executed.

Run from project root:
    python -m experiments.test_engineering_f1
"""

from __future__ import annotations

import math

import numpy as np

from benchmarks.engineering_design import (
    CANTILEVER_PRINTED,
    CANTILEVER_TABLE_CONSISTENT,
    PRIMARY_BENCHMARKS,
    SPRING,
    spring_g2_as_printed,
)


# Rounded paper designs naturally reproduce reported objectives only up to
# rounding. These per-problem tolerances are absolute objective tolerances.
OBJECTIVE_TOL = {
    "spring": 1e-7,
    "pressure_vessel": 2e-3,
    "welded_beam": 1e-4,
    "speed_reducer": 2e-3,
    "three_bar_truss": 1e-6,
}


def fmt_constraints(values):
    return "[" + ", ".join(f"{v:+.8e}" for v in values) + "]"


def main():
    print("=" * 118)
    print("F1 - Engineering benchmark deterministic audit")
    print("=" * 118)
    print("No optimizer will be run.")
    print("Feasibility convention: bounds satisfied AND every g_i(x) <= 1e-8")
    print("=" * 118)

    failures = []

    for bench in PRIMARY_BENCHMARKS:
        x = bench.paper_best_x
        f = bench.objective(x)
        g = bench.constraints(x)
        in_bounds = bench.within_bounds(x, tolerance=1e-12)
        feasible = bench.is_feasible(x, tolerance=1e-8)

        print(f"\n{bench.key}: {bench.name}")
        print(f"  paper x          = {np.array2string(x, precision=8, separator=', ')}")
        print(f"  computed f       = {f:.12g}")
        print(f"  paper reported f = {bench.paper_best_f:.12g}")
        print(f"  |difference|     = {abs(f - bench.paper_best_f):.8e}")
        print(f"  g(x)             = {fmt_constraints(g)}")
        print(f"  within bounds    = {in_bounds}")
        print(f"  feasible         = {feasible}")
        if bench.notes:
            print(f"  note             = {bench.notes}")

        if not np.all(np.isfinite(g)) or not math.isfinite(f):
            failures.append(f"{bench.key}: non-finite objective/constraint")

        if not in_bounds:
            failures.append(f"{bench.key}: paper point outside frozen bounds")

        # Cantilever printed formulation is EXPECTED to disagree with Table 20.
        if bench.key == "cantilever_printed":
            if not feasible:
                failures.append("cantilever_printed: paper point should satisfy printed constraint")
            continue

        if not feasible:
            failures.append(f"{bench.key}: reported SCHO point is not feasible")

        tol = OBJECTIVE_TOL[bench.key]
        if abs(f - bench.paper_best_f) > tol:
            failures.append(
                f"{bench.key}: objective mismatch "
                f"{abs(f-bench.paper_best_f):.3e} > {tol:.3e}"
            )

    print("\n" + "-" * 118)
    print("F1 source-anomaly checks")
    print("-" * 118)

    # 1. Spring: demonstrate why the documented terminal -1 matters.
    spring_printed_g2 = spring_g2_as_printed(SPRING.paper_best_x)
    spring_corrected_g2 = SPRING.constraints(SPRING.paper_best_x)[1]

    print(f"Spring g2 as printed in paper : {spring_printed_g2:+.12e}")
    print(f"Spring g2 with F0 correction : {spring_corrected_g2:+.12e}")

    if spring_printed_g2 <= 0.0:
        failures.append("spring anomaly check: printed g2 unexpectedly feasible")
    if spring_corrected_g2 > 1e-8:
        failures.append("spring anomaly check: corrected g2 still infeasible")

    # 2. Cantilever: demonstrate printed-vs-table inconsistency explicitly.
    x_c = CANTILEVER_PRINTED.paper_best_x
    f_printed = CANTILEVER_PRINTED.objective(x_c)
    f_table_variant = CANTILEVER_TABLE_CONSISTENT.objective(x_c)
    g_c = CANTILEVER_PRINTED.constraints(x_c)

    print()
    print(f"Cantilever Table 20 reported f       : {CANTILEVER_PRINTED.paper_best_f:.12g}")
    print(f"Cantilever printed 0.6224 objective  : {f_printed:.12g}")
    print(f"Cantilever diagnostic 0.06224 value  : {f_table_variant:.12g}")
    print(f"Cantilever printed constraint g(x)   : {g_c[0]:+.12e}")
    print(
        "Cantilever diagnostic status       : "
        "paper equation and Table 20 are internally inconsistent"
    )

    # The printed equation should differ by roughly a factor of 10.
    if abs(f_printed - CANTILEVER_PRINTED.paper_best_f) < 1.0:
        failures.append("cantilever anomaly check: expected printed mismatch not detected")

    # The diagnostic variant should match Table 20 to table rounding.
    if abs(f_table_variant - CANTILEVER_PRINTED.paper_best_f) > 1e-3:
        failures.append("cantilever diagnostic variant does not match Table 20 scale")

    if g_c[0] > 1e-8:
        failures.append("cantilever: reported point violates printed constraint")

    print("\n" + "-" * 118)
    print("F1 final audit")
    print("-" * 118)

    if failures:
        print(f"FAILURES: {len(failures)}")
        for item in failures:
            print(f"  - {item}")
        raise SystemExit(1)

    print("PASS: 6/6 primary benchmark definitions audited")
    print("PASS: 5/5 internally consistent paper reference points reproduce objective values within rounding")
    print("PASS: 6/6 paper reference points satisfy the frozen constraints/bounds")
    print("EXPECTED MISMATCH: cantilever printed objective gives ~13.03 while Table 20 reports ~1.3033")
    print("DOCUMENTED CORRECTION: spring g2 terminal -1 is required for the paper reference point")
    print()
    print("F1 RESULT: PASS")
    print("No GWO/SCHO optimization was executed.")
    print("algorithms/gwo.py was not modified.")
    print("algorithms/scho.py was not modified.")


if __name__ == "__main__":
    main()
