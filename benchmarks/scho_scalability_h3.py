"""Dimension-flexible F1-F13 adapter for SCHO Section 3.1.4 scalability.

This module leaves ``benchmarks/classic_23.py`` unchanged.  It reuses the
already-audited F1-F13 formulas and bounds while overriding only the dimension
for the paper's D=100 and D=500 scalability settings.
"""

from __future__ import annotations

from dataclasses import replace

from benchmarks.classic_23 import Benchmark, get_benchmark


SCALABILITY_FUNCTIONS = tuple(f"F{i}" for i in range(1, 14))
SCALABILITY_DIMS = (100, 500)


def get_scalability_benchmark(name: str, dim: int) -> Benchmark:
    """Return an F1-F13 benchmark at D=100 or D=500.

    Only dimension-dependent metadata are changed.  The objective callable,
    per-coordinate bounds, stochastic flag, and objective construction logic
    come directly from the frozen classic benchmark layer.
    """

    name = str(name).upper()
    if name not in SCALABILITY_FUNCTIONS:
        raise ValueError(
            f"H3 scalability supports F1-F13 only; got {name!r}."
        )
    if dim not in SCALABILITY_DIMS:
        raise ValueError(
            f"H3 scalability supports D=100 or D=500 only; got {dim}."
        )

    base = get_benchmark(name)

    # F8's known optimum scales linearly with dimension.  F1-F7/F9-F13 retain
    # optimum 0 under dimension changes in the project's benchmark definitions.
    optimum = -418.9829 * dim if name == "F8" else float(base.optimum)

    return replace(base, dim=int(dim), optimum=float(optimum))
