"""Source-structured Python translation of Mirjalili's Ant Lion Optimizer (ALO).

Primary basis
-------------
Seyedali Mirjalili's author MATLAB File Exchange submission 49920:
- ALO.m
- Random_walk_around_antlion.m
- RouletteWheelSelection.m
- initialization.m

Preserved source mechanics
--------------------------
- antlion and ant populations are initialized separately;
- only antlions are evaluated initially;
- antlion fitness is sorted to establish the initial elite;
- Current_iter starts at 2;
- each ant selects an antlion by roulette wheel using 1/fitness;
- roulette selection falls back to index 1 when no index is selected;
- for EACH ant and EACH of the two guides (selected antlion + elite), the
  helper regenerates a full MaxIter-step random walk matrix;
- the random-walk helper consumes two independent rand draws for the shifted
  lower/upper interval, then MaxIter random step draws per dimension;
- the shrinking-ratio I uses sequential threshold checks, with later checks
  overriding earlier ones (w=2..6 behavior);
- ant position is the mean of the selected-antlion and elite random walks at
  row Current_iter;
- ants are clipped/evaluated after all random-walk updates;
- old antlions and new ants are merged, sorted, and the best N retained;
- elite is updated, then forcibly restored to slot 1;
- convergence_curve[0] remains zero because recording starts at iteration 2.

Important source behavior
-------------------------
The roulette code is used literally with weights 1./fitness. Therefore zero or
negative objective values can produce Inf/negative weights and unusual/fallback
selection. H5c6 preserves this behavior instead of replacing it with a
"safer" probability transform.

RNG exactness
-------------
NumPy default_rng is used. Random-call structure is preserved, but no MATLAB
RNG-stream or bitwise equivalence is claimed.
"""

from __future__ import annotations

from typing import Callable
import numpy as np

ArrayLike = float | int | np.ndarray | list[float] | tuple[float, ...]


def _normalize_bounds(lb: ArrayLike, ub: ArrayLike, dim: int):
    lo_raw = np.asarray(lb, dtype=float)
    hi_raw = np.asarray(ub, dtype=float)

    scalar = lo_raw.ndim == 0 and hi_raw.ndim == 0

    if scalar:
        lo = float(lo_raw)
        hi = float(hi_raw)
        if not lo < hi:
            raise ValueError("lb must be strictly smaller than ub.")
        return np.full(dim, lo), np.full(dim, hi), True

    lo = np.broadcast_to(lo_raw, (dim,)).astype(float, copy=True)
    hi = np.broadcast_to(hi_raw, (dim,)).astype(float, copy=True)

    if np.any(lo >= hi):
        raise ValueError(
            "Every lower bound must be strictly smaller than its upper bound."
        )

    return lo, hi, False


def _matlab_style_initialization(
    N: int,
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    rng: np.random.Generator,
) -> np.ndarray:
    lo, hi, scalar = _normalize_bounds(lb, ub, dim)

    if scalar:
        return rng.random((N, dim)) * (hi[0] - lo[0]) + lo[0]

    X = np.empty((N, dim), dtype=float)
    for j in range(dim):
        X[:, j] = rng.random(N) * (hi[j] - lo[j]) + lo[j]
    return X


def _clip_source_style(
    x: np.ndarray,
    lo: np.ndarray,
    hi: np.ndarray,
) -> np.ndarray:
    flag_ub = x > hi
    flag_lb = x < lo
    keep = np.logical_not(flag_ub | flag_lb)
    return x * keep + hi * flag_ub + lo * flag_lb


def _shrink_ratio(current_iter: int, max_iter: int) -> tuple[float, int]:
    """Return source I and the corresponding w-stage (1 means no shrink stage)."""
    I = 1.0
    stage = 1

    if current_iter > max_iter / 10.0:
        I = 1.0 + 100.0 * (current_iter / max_iter)
        stage = 2

    if current_iter > max_iter / 2.0:
        I = 1.0 + 1000.0 * (current_iter / max_iter)
        stage = 3

    if current_iter > max_iter * (3.0 / 4.0):
        I = 1.0 + 10000.0 * (current_iter / max_iter)
        stage = 4

    if current_iter > max_iter * 0.9:
        I = 1.0 + 100000.0 * (current_iter / max_iter)
        stage = 5

    if current_iter > max_iter * 0.95:
        I = 1.0 + 1000000.0 * (current_iter / max_iter)
        stage = 6

    return I, stage


def _roulette_wheel_selection(
    weights: np.ndarray,
    rng: np.random.Generator,
) -> int:
    """Literal translation of the author's RouletteWheelSelection.m.

    Returns a zero-based index, or -1 when no cumulative weight is strictly
    greater than the sampled threshold.
    """
    accumulation = np.cumsum(np.asarray(weights, dtype=float))
    with np.errstate(invalid="ignore", over="ignore"):
        p = rng.random() * accumulation[-1]

    for index in range(accumulation.size):
        if accumulation[index] > p:
            return index

    return -1


def _random_walk_around_antlion(
    dim: int,
    max_iter: int,
    lb: ArrayLike,
    ub: ArrayLike,
    antlion: np.ndarray,
    current_iter: int,
    rng: np.random.Generator,
    diagnostics: dict | None = None,
) -> np.ndarray:
    """Literal-structure port of Random_walk_around_antlion.m.

    Shape is (max_iter+1, dim), matching MATLAB's leading zero followed by a
    MaxIter-step cumulative walk.
    """
    lo, hi, _ = _normalize_bounds(lb, ub, dim)

    I, stage = _shrink_ratio(current_iter, max_iter)
    lo = lo / I
    hi = hi / I

    # Two independent source `rand` calls.
    r_lb = rng.random()
    r_ub = rng.random()

    if r_lb < 0.5:
        lo = lo + antlion
    else:
        lo = -lo + antlion

    if r_ub >= 0.5:
        hi = hi + antlion
    else:
        hi = -hi + antlion

    RWs = np.empty((max_iter + 1, dim), dtype=float)

    for j in range(dim):
        steps = 2.0 * (rng.random(max_iter) > 0.5) - 1.0
        X = np.concatenate(
            (np.array([0.0]), np.cumsum(steps))
        )

        a = float(np.min(X))
        b = float(np.max(X))
        c = lo[j]
        d = hi[j]

        # Preserve the source normalization algebra. In the practically
        # negligible all-equal walk case, MATLAB would likewise divide by 0.
        with np.errstate(divide="ignore", invalid="ignore"):
            RWs[:, j] = (
                ((X - a) * (d - c)) / (b - a) + c
            )

    if diagnostics is not None:
        diagnostics["random_walk_calls"] += 1
        diagnostics["random_walk_boundary_draws"] += 2
        diagnostics["random_walk_step_draws"] += dim * max_iter
        diagnostics["shrink_stage_calls"][stage] += 1

    return RWs


def alo(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    """Run source-structured Ant Lion Optimizer."""
    if N < 1:
        raise ValueError("N must be >= 1.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 2:
        raise ValueError(
            "MaxIter must be >= 2 to preserve ALO loop/curve semantics."
        )

    rng = np.random.default_rng(seed)
    lo, hi, _ = _normalize_bounds(lb, ub, dim)

    # Source consumes two independent population initializations.
    antlion_position = _matlab_style_initialization(
        N, dim, lb, ub, rng
    )
    ant_position = _matlab_style_initialization(
        N, dim, lb, ub, rng
    )

    sorted_antlions = np.zeros((N, dim), dtype=float)
    elite_position = np.zeros(dim, dtype=float)
    elite_fitness = np.inf

    convergence_curve = np.zeros(MaxIter, dtype=float)
    antlions_fitness = np.zeros(N, dtype=float)
    ants_fitness = np.zeros(N, dtype=float)

    diagnostics = {
        "objective_evaluations": 0,
        "roulette_draws": 0,
        "roulette_fallbacks": 0,
        "random_walk_calls": 0,
        "random_walk_boundary_draws": 0,
        "random_walk_step_draws": 0,
        "shrink_stage_calls": {
            1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0
        },
        "elite_improvements_after_initial": 0,
        "merge_sorts": 0,
        "zero_or_negative_weight_events": 0,
        "nonfinite_weight_events": 0,
    }

    # Only antlions are evaluated initially; initial ants are not.
    for i in range(N):
        antlions_fitness[i] = float(
            obj_func(antlion_position[i])
        )
        diagnostics["objective_evaluations"] += 1

    idx = np.argsort(antlions_fitness, kind="stable")
    sorted_antlion_fitness = antlions_fitness[idx].copy()
    sorted_antlions[:] = antlion_position[idx]

    elite_position = sorted_antlions[0].copy()
    elite_fitness = float(sorted_antlion_fitness[0])

    current_iter = 2
    while current_iter < MaxIter + 1:
        # Simulate random walks for every ant.
        for i in range(N):
            with np.errstate(divide="ignore", invalid="ignore"):
                weights = 1.0 / sorted_antlion_fitness

            if np.any(sorted_antlion_fitness <= 0.0):
                diagnostics["zero_or_negative_weight_events"] += 1
            if np.any(~np.isfinite(weights)):
                diagnostics["nonfinite_weight_events"] += 1

            roulette_index = _roulette_wheel_selection(
                weights, rng
            )
            diagnostics["roulette_draws"] += 1

            if roulette_index == -1:
                # MATLAB fallback: Rolette_index=1.
                roulette_index = 0
                diagnostics["roulette_fallbacks"] += 1

            RA = _random_walk_around_antlion(
                dim,
                MaxIter,
                lb,
                ub,
                sorted_antlions[roulette_index],
                current_iter,
                rng,
                diagnostics,
            )

            RE = _random_walk_around_antlion(
                dim,
                MaxIter,
                lb,
                ub,
                elite_position,
                current_iter,
                rng,
                diagnostics,
            )

            # MATLAB Current_iter is 1-based; Python row is current_iter-1.
            ant_position[i] = (
                RA[current_iter - 1]
                + RE[current_iter - 1]
            ) / 2.0

        # Clip and evaluate ants.
        for i in range(N):
            ant_position[i] = _clip_source_style(
                ant_position[i], lo, hi
            )
            ants_fitness[i] = float(
                obj_func(ant_position[i])
            )
            diagnostics["objective_evaluations"] += 1

        # Merge retained antlions + new ants, then keep best N.
        double_population = np.vstack(
            (sorted_antlions, ant_position)
        )
        double_fitness = np.concatenate(
            (sorted_antlion_fitness, ants_fitness)
        )

        idx = np.argsort(double_fitness, kind="stable")
        double_fitness_sorted = double_fitness[idx]
        double_sorted_population = double_population[idx]

        sorted_antlion_fitness = (
            double_fitness_sorted[:N].copy()
        )
        sorted_antlions = (
            double_sorted_population[:N].copy()
        )
        diagnostics["merge_sorts"] += 1

        if sorted_antlion_fitness[0] < elite_fitness:
            elite_position = sorted_antlions[0].copy()
            elite_fitness = float(
                sorted_antlion_fitness[0]
            )
            diagnostics[
                "elite_improvements_after_initial"
            ] += 1

        # Exact elitism restoration from source.
        sorted_antlions[0] = elite_position.copy()
        sorted_antlion_fitness[0] = elite_fitness

        convergence_curve[current_iter - 1] = (
            elite_fitness
        )

        current_iter += 1

    result = (
        float(elite_fitness),
        elite_position.copy(),
        convergence_curve.copy(),
    )

    if not return_diagnostics:
        return result

    diagnostics.update(
        {
            "expected_objective_evaluations": int(
                N * MaxIter
            ),
            "expected_roulette_draws": int(
                N * (MaxIter - 1)
            ),
            "expected_random_walk_calls": int(
                2 * N * (MaxIter - 1)
            ),
            "expected_random_walk_boundary_draws": int(
                4 * N * (MaxIter - 1)
            ),
            "expected_random_walk_step_draws": int(
                2
                * N
                * (MaxIter - 1)
                * dim
                * MaxIter
            ),
            "expected_merge_sorts": int(
                MaxIter - 1
            ),
            "curve_index0_source_zero": bool(
                convergence_curve[0] == 0.0
            ),
        }
    )

    return (*result, diagnostics)
