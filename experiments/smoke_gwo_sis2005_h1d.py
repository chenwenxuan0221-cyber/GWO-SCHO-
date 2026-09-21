"""H1d single-seed integration smoke test for GWO on SIS2005 CF1-CF6.

This is not the formal 30-run reproduction. It checks that the frozen GWO
optimizer and the source-faithful SIS2005 benchmark layer integrate correctly
under the project/source-aligned N=30, MaxIter=500 protocol.
"""

from __future__ import annotations

import time
import numpy as np

from algorithms.gwo import gwo
from benchmarks.gwo_sis2005 import get_sis2005_benchmark


FUNCTIONS = ("F24", "F25", "F26", "F27", "F28", "F29")
N = 30
MAX_ITER = 500
SEED = 1000
TOL = 1e-12


def _assert_nonincreasing(curve: np.ndarray, name: str) -> None:
    diff = np.diff(curve)
    if np.any(diff > TOL):
        idx = int(np.flatnonzero(diff > TOL)[0])
        raise AssertionError(
            f"{name}: convergence curve increased at {idx}->{idx+1}: "
            f"{curve[idx]} -> {curve[idx+1]}"
        )


def main() -> None:
    print("=" * 118)
    print("H1d - GWO x SIS2005 CF1-CF6 single-seed integration smoke test")
    print("=" * 118)
    print(f"Protocol: N={N}, MaxIter={MAX_ITER}, seed={SEED}")
    print("Primary benchmark definition: source_faithful")
    print("This is NOT the formal 30-run Table-8 reproduction.")
    print("=" * 118)

    total_start = time.perf_counter()
    rows = []

    for name in FUNCTIONS:
        b = get_sis2005_benchmark(name, variant="source_faithful")

        start = time.perf_counter()
        best_score, best_pos, curve = gwo(
            b.objective,
            b.dim,
            b.lb,
            b.ub,
            N,
            MAX_ITER,
            seed=SEED,
        )
        elapsed = time.perf_counter() - start

        best_pos = np.asarray(best_pos, dtype=float)
        curve = np.asarray(curve, dtype=float)

        if not np.isfinite(best_score):
            raise AssertionError(f"{name}: non-finite best score")
        if best_pos.shape != (b.dim,):
            raise AssertionError(f"{name}: best_pos shape={best_pos.shape}")
        if not np.all(np.isfinite(best_pos)):
            raise AssertionError(f"{name}: best_pos contains non-finite values")
        if np.any(best_pos < b.lb - TOL) or np.any(best_pos > b.ub + TOL):
            raise AssertionError(f"{name}: best_pos violates bounds")
        if curve.shape != (MAX_ITER,):
            raise AssertionError(f"{name}: curve shape={curve.shape}")
        if not np.all(np.isfinite(curve)):
            raise AssertionError(f"{name}: convergence curve contains non-finite values")
        _assert_nonincreasing(curve, name)
        if not np.isclose(curve[-1], best_score, rtol=1e-12, atol=1e-12):
            raise AssertionError(
                f"{name}: final curve value {curve[-1]} != best score {best_score}"
            )
        if best_score > curve[0] + TOL:
            raise AssertionError(f"{name}: final best is worse than first-iteration best")

        rows.append((name, best_score, curve[0], elapsed))
        print(
            f"{name} / {b.canonical_name}: "
            f"iter1={curve[0]:.12g}  final={best_score:.12g}  "
            f"time={elapsed:.2f}s  PASS"
        )

    total_elapsed = time.perf_counter() - total_start

    print("-" * 118)
    print(f"Functions passed: {len(rows)}/{len(FUNCTIONS)}")
    print(f"Total elapsed: {total_elapsed:.2f}s")
    print("H1d RESULT: PASS")
    print("GWO and source-faithful SIS2005 benchmark layer integrate correctly.")
    print("No paper-agreement conclusion is made from this single-seed smoke test.")
    print("Next: H1e 30-run F24-F29 reproduction and Table-8 comparison.")


if __name__ == "__main__":
    main()
