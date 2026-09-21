"""Source-structured Python translation of Mirjalili et al.'s Salp Swarm Algorithm (SSA).

Primary basis: Seyedali Mirjalili's author MATLAB SSA implementation
(File Exchange 63745).

Preserved source structure:
- initial population evaluated first;
- initial fitness sorted once to define FoodPosition/FoodFitness;
- main loop starts at l=2;
- c1 = 2*exp(-(4*l/MaxIter)^2);
- first floor(N/2) salps are leaders;
- each leader coordinate draws fresh c2,c3;
- followers update sequentially/in-place from the already-updated previous salp;
- clipping/evaluation occur after all salps are updated;
- convergence_curve[0] remains zero, matching the source recording quirk.

NumPy RNG is used; MATLAB bitwise/RNG-stream equivalence is not claimed.
"""
from __future__ import annotations
from typing import Callable
import numpy as np

ArrayLike = float | int | np.ndarray | list[float] | tuple[float, ...]

def _normalize_bounds(lb: ArrayLike, ub: ArrayLike, dim: int):
    lo = np.asarray(lb, dtype=float)
    hi = np.asarray(ub, dtype=float)
    if lo.ndim == 0 and hi.ndim == 0:
        a, b = float(lo), float(hi)
        if not a < b:
            raise ValueError("lb must be strictly smaller than ub.")
        return np.full(dim, a), np.full(dim, b), True
    lo = np.broadcast_to(lo, (dim,)).astype(float, copy=True)
    hi = np.broadcast_to(hi, (dim,)).astype(float, copy=True)
    if np.any(lo >= hi):
        raise ValueError("Every lower bound must be smaller than its upper bound.")
    return lo, hi, False

def _matlab_style_initialization(N, dim, lb, ub, rng):
    lo, hi, scalar = _normalize_bounds(lb, ub, dim)
    if scalar:
        return rng.random((N, dim)) * (hi[0] - lo[0]) + lo[0]
    X = np.empty((N, dim), dtype=float)
    for j in range(dim):
        X[:, j] = rng.random(N) * (hi[j] - lo[j]) + lo[j]
    return X

def _clip_source_style(x, lo, hi):
    up = x > hi
    low = x < lo
    keep = np.logical_not(up | low)
    return x * keep + hi * up + lo * low

def ssa(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    if N < 2:
        raise ValueError("SSA requires N >= 2.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 2:
        raise ValueError("MaxIter must be >= 2.")

    rng = np.random.default_rng(seed)
    lo, hi, _ = _normalize_bounds(lb, ub, dim)
    X = _matlab_style_initialization(N, dim, lb, ub, rng)

    fit = np.empty(N, dtype=float)
    evals = 0
    for i in range(N):
        fit[i] = float(obj_func(X[i]))
        evals += 1

    idx = np.argsort(fit, kind="stable")
    food_pos = X[idx[0]].copy()
    food_fit = float(fit[idx[0]])

    curve = np.zeros(MaxIter, dtype=float)
    leaders = N // 2
    leader_coord_updates = follower_vector_updates = 0
    leader_random_draws = c3_lt = c3_ge = 0
    first_c1 = last_c1 = None

    l = 2
    while l <= MaxIter:
        c1 = 2.0 * np.exp(-((4.0 * l / MaxIter) ** 2))
        if first_c1 is None:
            first_c1 = float(c1)
        last_c1 = float(c1)

        for i in range(N):
            if i < leaders:
                for j in range(dim):
                    c2 = rng.random()
                    c3 = rng.random()
                    leader_random_draws += 2
                    leader_coord_updates += 1
                    base = (hi[j] - lo[j]) * c2 + lo[j]
                    if c3 < 0.5:
                        X[i, j] = food_pos[j] + c1 * base
                        c3_lt += 1
                    else:
                        X[i, j] = food_pos[j] - c1 * base
                        c3_ge += 1
            else:
                # Sequential/in-place follower update.
                X[i] = (X[i].copy() + X[i - 1].copy()) / 2.0
                follower_vector_updates += 1

        for i in range(N):
            X[i] = _clip_source_style(X[i], lo, hi)
            fit[i] = float(obj_func(X[i]))
            evals += 1
            if fit[i] < food_fit:
                food_pos = X[i].copy()
                food_fit = float(fit[i])

        curve[l - 1] = food_fit
        l += 1

    result = (float(food_fit), food_pos.copy(), curve.copy())
    if not return_diagnostics:
        return result

    diag = {
        "objective_evaluations": evals,
        "expected_objective_evaluations": N * MaxIter,
        "leader_count": leaders,
        "leader_coordinate_updates": leader_coord_updates,
        "expected_leader_coordinate_updates": (MaxIter - 1) * leaders * dim,
        "follower_vector_updates": follower_vector_updates,
        "expected_follower_vector_updates": (MaxIter - 1) * (N - leaders),
        "leader_random_draws": leader_random_draws,
        "expected_leader_random_draws": 2 * (MaxIter - 1) * leaders * dim,
        "c3_less_half": c3_lt,
        "c3_ge_half": c3_ge,
        "first_c1": float(first_c1),
        "last_c1": float(last_c1),
        "curve_index0_source_zero": bool(curve[0] == 0.0),
    }
    return (*result, diag)
