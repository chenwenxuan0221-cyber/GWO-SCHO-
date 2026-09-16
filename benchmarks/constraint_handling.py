"""Constraint-handling helpers for Stage F engineering problems.

The SCHO paper states that a simple death penalty is used for its six
engineering design problems, but it does not state the exact numerical
penalty constant.

Stage F therefore makes the numerical constant an explicit PROJECT
CONVENTION rather than presenting it as a paper-specified value.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable
import numpy as np
from benchmarks.engineering_design import EngineeringBenchmark

DEFAULT_DEATH_PENALTY = 1.0e30
DEFAULT_FEASIBILITY_TOLERANCE = 1.0e-8

@dataclass(frozen=True)
class CandidateEvaluation:
    raw_objective: float
    penalized_fitness: float
    feasible: bool
    within_bounds: bool
    max_violation: float
    constraints: np.ndarray

def make_death_penalty_objective(
    benchmark: EngineeringBenchmark,
    *,
    penalty: float = DEFAULT_DEATH_PENALTY,
    tolerance: float = DEFAULT_FEASIBILITY_TOLERANCE,
) -> Callable[[np.ndarray], float]:
    penalty = float(penalty)
    tolerance = float(tolerance)
    if not np.isfinite(penalty) or penalty <= 0.0:
        raise ValueError("penalty must be a positive finite number.")
    if tolerance < 0.0 or not np.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative.")

    def objective(x: np.ndarray) -> float:
        arr = np.asarray(x, dtype=float)
        if benchmark.is_feasible(arr, tolerance=tolerance):
            return benchmark.objective(arr)
        return penalty
    return objective

def evaluate_candidate(
    benchmark: EngineeringBenchmark,
    x: Iterable[float],
    *,
    penalty: float = DEFAULT_DEATH_PENALTY,
    tolerance: float = DEFAULT_FEASIBILITY_TOLERANCE,
) -> CandidateEvaluation:
    arr = np.asarray(x, dtype=float)
    raw = benchmark.objective(arr)
    constraints = benchmark.constraints(arr)
    in_bounds = benchmark.within_bounds(arr, tolerance=tolerance)
    feasible = benchmark.is_feasible(arr, tolerance=tolerance)
    max_violation = benchmark.max_violation(arr)
    penalized = raw if feasible else float(penalty)
    return CandidateEvaluation(
        raw_objective=float(raw),
        penalized_fitness=float(penalized),
        feasible=bool(feasible),
        within_bounds=bool(in_bounds),
        max_violation=float(max_violation),
        constraints=constraints.copy(),
    )
