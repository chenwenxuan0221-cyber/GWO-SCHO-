"""Controlled-equivalent shifted benchmarks for GWO paper Section 4.4 / Fig. 11.

This module does NOT claim to recover the authors' unpublished shift vectors.
It implements a deterministic, documented Tier-B protocol for the eight
functions visibly used in Fig. 11:
F1, F7, F9, F10, F14, F18, F26, F29.

Dimension convention
--------------------
Retain each benchmark's native paper dimension:
- F1/F7/F9/F10: D=30
- F14/F18: D=2
- F26/F29: D=10

Shift convention
----------------
For every coordinate, relocate one known global optimum to the point 65% of
the way from the lower to upper bound:

    target = lb + 0.65 * (ub - lb)
    delta  = target - base_optimum
    g(x)   = f(x - delta)

This keeps the shifted optimum inside the original search box and makes the
protocol deterministic. It is a controlled-equivalent convention, not the
unavailable original Fig.-11 shift.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np

from benchmarks.classic_23 import get_benchmark
from benchmarks.gwo_sis2005 import get_sis2005_benchmark


FIG11_FUNCTIONS = ("F1", "F7", "F9", "F10", "F14", "F18", "F26", "F29")
TARGET_FRACTION = 0.65


@dataclass(frozen=True)
class H2ShiftedBenchmark:
    name: str
    dim: int
    lb: np.ndarray
    ub: np.ndarray
    base_optimum: np.ndarray
    target_optimum: np.ndarray
    shift: np.ndarray
    stochastic: bool
    make_base_objective: Callable[[int | None], Callable[[np.ndarray], float]]

    def make_objective(self, seed: int | None = None):
        base_obj = self.make_base_objective(seed)
        delta = self.shift.copy()

        def objective(x):
            arr = np.asarray(x, dtype=float)
            return float(base_obj(arr - delta))

        return objective


def _as_vector(value, dim):
    return np.broadcast_to(np.asarray(value, dtype=float), (dim,)).copy()


def _classic_original_optimum(name: str) -> np.ndarray:
    b = get_benchmark(name)
    if name in {"F1", "F7", "F9", "F10"}:
        return np.zeros(b.dim, dtype=float)
    if name == "F14":
        # Shekel's Foxholes: the source-faithful best grid point is (-32,-32).
        return np.array([-32.0, -32.0], dtype=float)
    if name == "F18":
        # Goldstein-Price global optimum.
        return np.array([0.0, -1.0], dtype=float)
    raise ValueError(f"No H2 classic optimum mapping for {name}")


def get_h2_shifted_benchmark(name: str) -> H2ShiftedBenchmark:
    key = name.upper()
    if key not in FIG11_FUNCTIONS:
        raise ValueError(f"{name!r} is not one of the eight Fig.-11 functions")

    if key in {"F26", "F29"}:
        base = get_sis2005_benchmark(key, variant="source_faithful")
        dim = base.dim
        lb = _as_vector(base.lb, dim)
        ub = _as_vector(base.ub, dim)
        base_optimum = np.asarray(base.optima[0], dtype=float).copy()

        def factory(seed=None, _base=base):
            # Deterministic; seed kept for uniform API.
            return _base.objective

        stochastic = False
    else:
        base = get_benchmark(key)
        dim = base.dim
        lb = _as_vector(base.lb, dim)
        ub = _as_vector(base.ub, dim)
        base_optimum = _classic_original_optimum(key)

        def factory(seed=None, _base=base):
            return _base.make_objective(seed=seed)

        stochastic = bool(base.stochastic)

    target = lb + TARGET_FRACTION * (ub - lb)
    shift = target - base_optimum

    if np.any(target <= lb) or np.any(target >= ub):
        raise AssertionError(f"{key}: controlled target is not strictly inside bounds")

    return H2ShiftedBenchmark(
        name=key,
        dim=dim,
        lb=lb,
        ub=ub,
        base_optimum=base_optimum,
        target_optimum=target,
        shift=shift,
        stochastic=stochastic,
        make_base_objective=factory,
    )
