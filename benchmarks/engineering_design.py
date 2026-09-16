"""Engineering design benchmarks for Stage F.

Source basis
------------
Bai et al. (2023), "A Sinh Cosh optimizer", Section 3.3, Tables 16-21.

F0 policy
---------
- Physical objective functions and constraints are kept separate.
- Feasibility means: inside variable bounds AND every g_i(x) <= tolerance.
- The paper states a simple death-penalty concept but does not state the
  numerical penalty constant. Therefore the benchmark definitions do not
  hard-code a penalty.
- Known paper inconsistencies are preserved/documented explicitly rather
  than silently hidden.

Important source-audit decisions
--------------------------------
1. Spring final bound is interpreted as x3 in [2, 15], because the paper
   prints x1 by mistake.
2. Spring g2 uses the terminal "-1" needed for the paper-reported design
   to satisfy g2 <= 0. The paper print omits it.
3. Pressure-vessel x1/x2 remain continuous in the main paper-oriented
   reproduction because the paper does not give a discretization rule and
   reports continuous-valued x1/x2.
4. Speed-reducer x3 remains continuous at benchmark level; the paper calls
   it the number of teeth but gives no integer-projection mechanism.
5. Cantilever beam has two EXPLICIT variants:
   - "cantilever_printed": uses the printed coefficient 0.6224.
   - "cantilever_table_consistent": diagnostic variant using 0.06224,
     because this reproduces the scale of Table 20. This coefficient is an
     implementation assumption, NOT a value printed in the paper.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple

import numpy as np


Array = np.ndarray
Objective = Callable[[Array], float]
Constraints = Callable[[Array], Array]


@dataclass(frozen=True)
class EngineeringBenchmark:
    key: str
    name: str
    dim: int
    lb: Array
    ub: Array
    objective_fn: Objective
    constraints_fn: Constraints
    paper_best_x: Array
    paper_best_f: float
    notes: str = ""

    def _as_vector(self, x: Iterable[float]) -> Array:
        arr = np.asarray(x, dtype=float)
        if arr.shape != (self.dim,):
            raise ValueError(
                f"{self.key}: expected shape ({self.dim},), got {arr.shape}"
            )
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"{self.key}: x contains non-finite values.")
        return arr

    def objective(self, x: Iterable[float]) -> float:
        arr = self._as_vector(x)
        value = float(self.objective_fn(arr))
        if not np.isfinite(value):
            raise ValueError(f"{self.key}: objective is non-finite.")
        return value

    def constraints(self, x: Iterable[float]) -> Array:
        arr = self._as_vector(x)
        values = np.asarray(self.constraints_fn(arr), dtype=float)
        if values.ndim != 1:
            raise ValueError(f"{self.key}: constraints must return a 1-D array.")
        # A benchmark may be singular at a legal box boundary (for example
        # the three-bar truss at x=(0,0)). Non-finite constraint values mean
        # "infeasible"; they must not crash a population-based optimizer.
        return values

    def within_bounds(self, x: Iterable[float], tolerance: float = 0.0) -> bool:
        arr = self._as_vector(x)
        return bool(
            np.all(arr >= self.lb - tolerance)
            and np.all(arr <= self.ub + tolerance)
        )

    def is_feasible(self, x: Iterable[float], tolerance: float = 1e-8) -> bool:
        arr = self._as_vector(x)

        # Short-circuit before evaluating physical formulas. This avoids
        # needless singular evaluations for candidates already outside the
        # original design box.
        if not self.within_bounds(arr, tolerance=tolerance):
            return False

        g = self.constraints(arr)
        return bool(np.all(np.isfinite(g)) and np.all(g <= tolerance))

    def max_violation(self, x: Iterable[float]) -> float:
        """Maximum positive constraint/bound violation; 0 means feasible."""
        arr = self._as_vector(x)

        lower = np.maximum(self.lb - arr, 0.0)
        upper = np.maximum(arr - self.ub, 0.0)
        raw_g = self.constraints(arr)
        if not np.all(np.isfinite(raw_g)):
            return float("inf")
        g = np.maximum(raw_g, 0.0)

        pieces = [lower, upper, g]
        return float(max(float(np.max(p)) if p.size else 0.0 for p in pieces))

    def death_penalty_objective(
        self,
        x: Iterable[float],
        *,
        penalty: float,
        tolerance: float = 1e-8,
    ) -> float:
        """Explicit death penalty.

        The SCHO paper states the death-penalty concept but does NOT state
        the numerical penalty constant. Callers must therefore provide it.
        """
        if not np.isfinite(penalty):
            raise ValueError("penalty must be a finite number.")
        arr = self._as_vector(x)
        if self.is_feasible(arr, tolerance=tolerance):
            return self.objective(arr)
        return float(penalty)


# ---------------------------------------------------------------------------
# P1 - Tension/compression spring
# ---------------------------------------------------------------------------

def _spring_objective(x: Array) -> float:
    x1, x2, x3 = x
    return (x3 + 2.0) * x2 * x1**2


def _spring_constraints(x: Array) -> Array:
    x1, x2, x3 = x
    return np.array(
        [
            1.0 - (x2**3 * x3) / (71785.0 * x1**4),

            # F0 documented correction:
            # The paper print omits this terminal -1. Without it, the
            # paper-reported SCHO point violates g2 <= 0 by about +1.
            (4.0 * x2**2 - x1 * x2)
            / (12566.0 * (x2 * x1**3 - x1**4))
            + 1.0 / (5108.0 * x1**2)
            - 1.0,

            1.0 - (140.54 * x1) / (x2**2 * x3),
            (x1 + x2) / 1.5 - 1.0,
        ],
        dtype=float,
    )


# Diagnostic only: reproduce the paper-printed spring g2 with no terminal -1.
def spring_g2_as_printed(x: Iterable[float]) -> float:
    arr = np.asarray(x, dtype=float)
    if arr.shape != (3,):
        raise ValueError("spring_g2_as_printed expects 3 variables.")
    x1, x2, _ = arr
    return float(
        (4.0 * x2**2 - x1 * x2)
        / (12566.0 * (x2 * x1**3 - x1**4))
        + 1.0 / (5108.0 * x1**2)
    )


# ---------------------------------------------------------------------------
# P2 - Pressure vessel
# ---------------------------------------------------------------------------

def _pressure_vessel_objective(x: Array) -> float:
    x1, x2, x3, x4 = x
    return (
        0.6224 * x1 * x3 * x4
        + 1.7781 * x2 * x3**2
        + 3.1661 * x1**2 * x4
        + 19.84 * x1**2 * x3
    )


def _pressure_vessel_constraints(x: Array) -> Array:
    x1, x2, x3, x4 = x
    return np.array(
        [
            -x1 + 0.0193 * x3,
            -x2 + 0.00954 * x3,
            -np.pi * x3**2 * x4
            - (4.0 / 3.0) * np.pi * x3**3
            + 1_296_000.0,
            x4 - 240.0,
        ],
        dtype=float,
    )


# ---------------------------------------------------------------------------
# P3 - Welded beam
# ---------------------------------------------------------------------------

def _welded_beam_aux(x: Array) -> Dict[str, float]:
    x1, x2, x3, x4 = x

    P = 6000.0
    L = 14.0
    E = 30.0e6
    G = 12.0e6

    tau_prime = P / (np.sqrt(2.0) * x1 * x2)
    M = P * (L + x2 / 2.0)
    R = np.sqrt(x2**2 / 4.0 + ((x1 + x3) / 2.0) ** 2)
    J = (
        2.0
        * np.sqrt(2.0)
        * x1
        * x2
        * (x2**2 / 12.0 + ((x1 + x3) / 2.0) ** 2)
    )
    tau_double_prime = M * R / J

    tau = np.sqrt(
        tau_prime**2
        + 2.0 * tau_prime * tau_double_prime * x2 / (2.0 * R)
        + tau_double_prime**2
    )

    sigma = 6.0 * P * L / (x4 * x3**2)
    delta = 4.0 * P * L**3 / (E * x3**3 * x4)

    Pc = (
        4.013
        * E
        * np.sqrt(x3**2 * x4**6 / 36.0)
        / L**2
        * (1.0 - x3 / (2.0 * L) * np.sqrt(E / (4.0 * G)))
    )

    return {
        "tau": float(tau),
        "sigma": float(sigma),
        "delta": float(delta),
        "Pc": float(Pc),
    }


def _welded_beam_objective(x: Array) -> float:
    x1, x2, x3, x4 = x
    return 1.10471 * x1**2 * x2 + 0.04811 * x3 * x4 * (14.0 + x2)


def _welded_beam_constraints(x: Array) -> Array:
    x1, x2, x3, x4 = x

    tau_max = 13_600.0
    sigma_max = 30_000.0
    delta_max = 0.25
    P = 6000.0

    aux = _welded_beam_aux(x)
    f = _welded_beam_objective(x)

    return np.array(
        [
            aux["tau"] - tau_max,
            aux["sigma"] - sigma_max,
            x1 - x4,
            f - 5.0,
            0.125 - x1,
            aux["delta"] - delta_max,
            P - aux["Pc"],
        ],
        dtype=float,
    )


# ---------------------------------------------------------------------------
# P4 - Speed reducer
# ---------------------------------------------------------------------------

def _speed_reducer_objective(x: Array) -> float:
    x1, x2, x3, x4, x5, x6, x7 = x
    return (
        0.7854
        * x1
        * x2**2
        * (3.3333 * x3**2 + 14.9334 * x3 - 43.0934)
        - 1.508 * x1 * (x6**2 + x7**2)
        + 7.4777 * (x6**3 + x7**3)
        + 0.7854 * (x4 * x6**2 + x5 * x7**2)
    )


def _speed_reducer_constraints(x: Array) -> Array:
    x1, x2, x3, x4, x5, x6, x7 = x
    return np.array(
        [
            27.0 / (x1 * x2**2 * x3) - 1.0,
            397.5 / (x1 * x2**2 * x3**2) - 1.0,
            1.93 * x4**3 / (x2 * x3 * x6**4) - 1.0,
            1.93 * x5**3 / (x2 * x3 * x7**4) - 1.0,
            np.sqrt((745.0 * x4 / (x2 * x3)) ** 2 + 16.9e6)
            / (110.0 * x6**3)
            - 1.0,
            np.sqrt((745.0 * x5 / (x2 * x3)) ** 2 + 157.5e6)
            / (85.0 * x7**3)
            - 1.0,
            x2 * x3 / 40.0 - 1.0,
            5.0 * x2 / x1 - 1.0,
            x1 / (12.0 * x2) - 1.0,
            (1.5 * x6 + 1.9) / x4 - 1.0,
            (1.1 * x7 + 1.9) / x5 - 1.0,
        ],
        dtype=float,
    )


# ---------------------------------------------------------------------------
# P5 - Cantilever beam
# ---------------------------------------------------------------------------

def _cantilever_constraint(x: Array) -> Array:
    x1, x2, x3, x4, x5 = x
    return np.array(
        [
            60.0 / x1**3
            + 27.0 / x2**3
            + 19.0 / x3**3
            + 7.0 / x4**3
            + 1.0 / x5**3
            - 1.0
        ],
        dtype=float,
    )


def _cantilever_printed_objective(x: Array) -> float:
    # This is exactly the coefficient printed in the SCHO paper.
    return 0.6224 * float(np.sum(x))


def _cantilever_table_consistent_objective(x: Array) -> float:
    # Diagnostic/project assumption ONLY. The paper itself prints 0.6224.
    # This 0.06224 coefficient matches Table 20's ~1.3033 scale.
    return 0.06224 * float(np.sum(x))


# ---------------------------------------------------------------------------
# P6 - Three-bar truss
# ---------------------------------------------------------------------------

def _three_bar_truss_objective(x: Array) -> float:
    x1, x2 = x
    l = 100.0
    return (2.0 * np.sqrt(2.0) * x1 + x2) * l


def _three_bar_truss_constraints(x: Array) -> Array:
    x1, x2 = x
    P = 2.0
    sigma = 2.0

    denominator = np.sqrt(2.0) * x1**2 + 2.0 * x1 * x2
    denominator3 = np.sqrt(2.0) * x2 + x1

    # The legal box includes (0,0), where the stress formulas are singular.
    # Return non-finite constraint values there; the generic feasibility
    # check classifies them as infeasible instead of raising an exception.
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.array(
            [
                ((np.sqrt(2.0) * x1 + x2) / denominator) * P - sigma,
                (x2 / denominator) * P - sigma,
                (1.0 / denominator3) * P - sigma,
            ],
            dtype=float,
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SPRING = EngineeringBenchmark(
    key="spring",
    name="Tension/compression spring",
    dim=3,
    lb=np.array([0.05, 0.25, 2.0], dtype=float),
    ub=np.array([2.0, 1.3, 15.0], dtype=float),
    objective_fn=_spring_objective,
    constraints_fn=_spring_constraints,
    paper_best_x=np.array([0.0517422, 0.3579972, 11.2146238], dtype=float),
    paper_best_f=0.0126656,
    notes=(
        "Uses F0-documented correction: x3 upper/lower bound typo fixed and "
        "terminal -1 restored in g2."
    ),
)

PRESSURE_VESSEL = EngineeringBenchmark(
    key="pressure_vessel",
    name="Pressure vessel",
    dim=4,
    lb=np.array([0.0, 0.0, 10.0, 10.0], dtype=float),
    ub=np.array([99.0, 99.0, 200.0, 200.0], dtype=float),
    objective_fn=_pressure_vessel_objective,
    constraints_fn=_pressure_vessel_constraints,
    paper_best_x=np.array([0.7796836, 0.3854124, 40.39092, 199.0132], dtype=float),
    paper_best_f=5889.0061,
    notes=(
        "Continuous paper-oriented formulation; no unreported thickness "
        "discretization is imposed."
    ),
)

WELDED_BEAM = EngineeringBenchmark(
    key="welded_beam",
    name="Welded beam",
    dim=4,
    lb=np.array([0.1, 0.1, 0.1, 0.1], dtype=float),
    ub=np.array([2.0, 10.0, 10.0, 2.0], dtype=float),
    objective_fn=_welded_beam_objective,
    constraints_fn=_welded_beam_constraints,
    paper_best_x=np.array([0.20565, 3.47312, 9.03685, 0.20573], dtype=float),
    paper_best_f=1.72516,
)

SPEED_REDUCER = EngineeringBenchmark(
    key="speed_reducer",
    name="Speed reducer",
    dim=7,
    lb=np.array([2.6, 0.7, 17.0, 7.3, 7.3, 2.9, 5.0], dtype=float),
    ub=np.array([3.6, 0.8, 28.0, 8.3, 8.3, 3.9, 5.5], dtype=float),
    objective_fn=_speed_reducer_objective,
    constraints_fn=_speed_reducer_constraints,
    paper_best_x=np.array(
        [3.50008, 0.7, 17.0, 7.3, 7.72871, 3.35023, 5.28736],
        dtype=float,
    ),
    paper_best_f=2995.2477,
    notes=(
        "Benchmark-level x3 is continuous; no unreported integer projection "
        "is imposed."
    ),
)

CANTILEVER_PRINTED = EngineeringBenchmark(
    key="cantilever_printed",
    name="Cantilever beam (paper-printed objective)",
    dim=5,
    lb=np.full(5, 0.01, dtype=float),
    ub=np.full(5, 100.0, dtype=float),
    objective_fn=_cantilever_printed_objective,
    constraints_fn=_cantilever_constraint,
    paper_best_x=np.array([5.9763, 4.8878, 4.4573, 3.4732, 2.1447], dtype=float),
    paper_best_f=1.3033,
    notes=(
        "Paper prints coefficient 0.6224, which does NOT reproduce Table 20. "
        "This variant preserves the printed equation."
    ),
)

CANTILEVER_TABLE_CONSISTENT = EngineeringBenchmark(
    key="cantilever_table_consistent",
    name="Cantilever beam (Table-20-consistent diagnostic)",
    dim=5,
    lb=np.full(5, 0.01, dtype=float),
    ub=np.full(5, 100.0, dtype=float),
    objective_fn=_cantilever_table_consistent_objective,
    constraints_fn=_cantilever_constraint,
    paper_best_x=np.array([5.9763, 4.8878, 4.4573, 3.4732, 2.1447], dtype=float),
    paper_best_f=1.3033,
    notes=(
        "Uses 0.06224 as an explicitly labeled project diagnostic assumption. "
        "The SCHO paper does NOT print this coefficient."
    ),
)

THREE_BAR_TRUSS = EngineeringBenchmark(
    key="three_bar_truss",
    name="Three-bar truss",
    dim=2,
    lb=np.array([0.0, 0.0], dtype=float),
    ub=np.array([1.0, 1.0], dtype=float),
    objective_fn=_three_bar_truss_objective,
    constraints_fn=_three_bar_truss_constraints,
    paper_best_x=np.array([0.78866420, 0.40827926], dtype=float),
    paper_best_f=263.8958476,
)


# Six primary source-oriented problems.
# The cantilever primary entry intentionally preserves the PRINTED equation.
PRIMARY_BENCHMARKS = (
    SPRING,
    PRESSURE_VESSEL,
    WELDED_BEAM,
    SPEED_REDUCER,
    CANTILEVER_PRINTED,
    THREE_BAR_TRUSS,
)

_REGISTRY = {b.key: b for b in PRIMARY_BENCHMARKS}
_REGISTRY[CANTILEVER_TABLE_CONSISTENT.key] = CANTILEVER_TABLE_CONSISTENT


def get_engineering_benchmark(key: str) -> EngineeringBenchmark:
    try:
        return _REGISTRY[key]
    except KeyError as exc:
        valid = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown engineering benchmark {key!r}. Valid: {valid}") from exc


def all_engineering_benchmarks(*, include_diagnostic_variant: bool = False):
    if include_diagnostic_variant:
        return tuple(_REGISTRY.values())
    return PRIMARY_BENCHMARKS
