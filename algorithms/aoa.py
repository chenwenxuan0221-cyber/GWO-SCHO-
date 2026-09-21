"""Source-structured Python translation of Arithmetic Optimization Algorithm (AOA).

Primary source
--------------
Laith Abualigah's author MATLAB AOA implementation (File Exchange 84742,
version 1.0.0, AOA.m).

H5 protocol override
--------------------
The author source uses Mu=0.499. The SCHO paper Table 6 explicitly uses
u/mu=0.5 for its comparison experiment. H5 therefore preserves the author
algorithm/control-flow structure while setting Mu=0.5.

Frozen interpretation:
    SOURCE-STRUCTURED AOA + SCHO_TABLE6_PARAMETER_OVERRIDE(mu=0.5)

Preserved source mechanics
--------------------------
- initialization before the main loop;
- initial objective evaluation of all solutions;
- C_Iter starts at 1 and runs through MaxIter;
- MOP = 1 - C_Iter^(1/Alpha) / MaxIter^(1/Alpha);
- MOA = 0.2 + C_Iter*((1-0.2)/MaxIter);
- one unconditional r1 draw per coordinate;
- IMPORTANT vector-bound quirk: for vector bounds the source draws r1 once
  unconditionally, then draws a second r1 inside the vector-bound branch;
  the first is unused;
- branch-local r2 or r3 draw;
- candidate Xnew is boundary-clipped after all coordinates of a candidate;
- candidate replaces current solution only on strict improvement;
- Best_P/Best_FF update after greedy acceptance;
- convergence curve records all iterations 1..MaxIter.

NumPy RNG is used; no MATLAB RNG-stream or bitwise equivalence is claimed.
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


def aoa(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
    return_diagnostics: bool = False,
    mu: float = 0.5,
):
    """Run AOA under the SCHO Table-6 protocol.

    Parameters
    ----------
    mu
        Defaults to 0.5 for H5 because Bai et al. Table 6 uses u=0.5.
        Passing another value is allowed only for explicit diagnostics.
    """
    if N < 1:
        raise ValueError("N must be >= 1.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 1:
        raise ValueError("MaxIter must be >= 1.")
    if not np.isfinite(mu):
        raise ValueError("mu must be finite.")

    rng = np.random.default_rng(seed)
    lo, hi, scalar_bounds = _normalize_bounds(lb, ub, dim)

    best_pos = np.zeros(dim, dtype=float)
    best_score = np.inf
    curve = np.zeros(MaxIter, dtype=float)

    X = _matlab_style_initialization(N, dim, lb, ub, rng)
    Xnew = X.copy()

    fit = np.zeros(N, dtype=float)
    fit_new = np.zeros(N, dtype=float)

    mop_max = 1.0
    mop_min = 0.2
    alpha = 5.0
    matlab_eps = np.finfo(float).eps

    objective_evaluations = 0

    for i in range(N):
        fit[i] = float(obj_func(X[i]))
        objective_evaluations += 1
        if fit[i] < best_score:
            best_score = fit[i]
            best_pos = X[i].copy()

    unconditional_r1_draws = 0
    vector_extra_r1_draws = 0
    branch_random_draws = 0

    division_updates = 0
    multiplication_updates = 0
    subtraction_updates = 0
    addition_updates = 0

    greedy_accepts = 0
    greedy_rejects = 0
    best_updates_after_initial = 0

    first_mop = first_moa = None
    last_mop = last_moa = None

    c_iter = 1
    while c_iter < MaxIter + 1:
        mop = 1.0 - (
            (c_iter ** (1.0 / alpha))
            / (MaxIter ** (1.0 / alpha))
        )
        moa = mop_min + c_iter * (
            (mop_max - mop_min) / MaxIter
        )

        if first_mop is None:
            first_mop = float(mop)
            first_moa = float(moa)
        last_mop = float(mop)
        last_moa = float(moa)

        for i in range(N):
            for j in range(dim):
                # Exact source call structure: this draw occurs for every
                # coordinate, even though vector bounds redraw r1 below.
                r1 = rng.random()
                unconditional_r1_draws += 1

                if scalar_bounds:
                    scale = (
                        (hi[0] - lo[0]) * mu + lo[0]
                    )

                    if r1 < moa:
                        r2 = rng.random()
                        branch_random_draws += 1

                        if r2 > 0.5:
                            Xnew[i, j] = (
                                best_pos[j]
                                / (mop + matlab_eps)
                                * scale
                            )
                            division_updates += 1
                        else:
                            Xnew[i, j] = (
                                best_pos[j] * mop * scale
                            )
                            multiplication_updates += 1
                    else:
                        r3 = rng.random()
                        branch_random_draws += 1

                        if r3 > 0.5:
                            Xnew[i, j] = (
                                best_pos[j] - mop * scale
                            )
                            subtraction_updates += 1
                        else:
                            Xnew[i, j] = (
                                best_pos[j] + mop * scale
                            )
                            addition_updates += 1

                else:
                    # Exact AOA.m quirk: r1 is drawn AGAIN for vector bounds.
                    r1 = rng.random()
                    vector_extra_r1_draws += 1

                    scale = (
                        (hi[j] - lo[j]) * mu + lo[j]
                    )

                    if r1 < moa:
                        r2 = rng.random()
                        branch_random_draws += 1

                        if r2 > 0.5:
                            Xnew[i, j] = (
                                best_pos[j]
                                / (mop + matlab_eps)
                                * scale
                            )
                            division_updates += 1
                        else:
                            Xnew[i, j] = (
                                best_pos[j] * mop * scale
                            )
                            multiplication_updates += 1
                    else:
                        r3 = rng.random()
                        branch_random_draws += 1

                        if r3 > 0.5:
                            Xnew[i, j] = (
                                best_pos[j] - mop * scale
                            )
                            subtraction_updates += 1
                        else:
                            Xnew[i, j] = (
                                best_pos[j] + mop * scale
                            )
                            addition_updates += 1

            Xnew[i] = _clip_source_style(
                Xnew[i], lo, hi
            )

            fit_new[i] = float(obj_func(Xnew[i]))
            objective_evaluations += 1

            # Source uses strict greedy acceptance.
            if fit_new[i] < fit[i]:
                X[i] = Xnew[i].copy()
                fit[i] = fit_new[i]
                greedy_accepts += 1
            else:
                greedy_rejects += 1

            if fit[i] < best_score:
                best_score = fit[i]
                best_pos = X[i].copy()
                best_updates_after_initial += 1

        curve[c_iter - 1] = best_score
        c_iter += 1

    result = (
        float(best_score),
        best_pos.copy(),
        curve.copy(),
    )

    if not return_diagnostics:
        return result

    total_coordinate_updates = N * dim * MaxIter
    diagnostics = {
        "mu": float(mu),
        "alpha": float(alpha),
        "mop_min": float(mop_min),
        "mop_max": float(mop_max),
        "scalar_bounds": bool(scalar_bounds),
        "objective_evaluations": int(objective_evaluations),
        "expected_objective_evaluations": int(
            N * (MaxIter + 1)
        ),
        "coordinate_updates": int(total_coordinate_updates),
        "unconditional_r1_draws": int(unconditional_r1_draws),
        "expected_unconditional_r1_draws": int(
            total_coordinate_updates
        ),
        "vector_extra_r1_draws": int(vector_extra_r1_draws),
        "expected_vector_extra_r1_draws": int(
            0 if scalar_bounds else total_coordinate_updates
        ),
        "branch_random_draws": int(branch_random_draws),
        "expected_branch_random_draws": int(
            total_coordinate_updates
        ),
        "division_updates": int(division_updates),
        "multiplication_updates": int(multiplication_updates),
        "subtraction_updates": int(subtraction_updates),
        "addition_updates": int(addition_updates),
        "greedy_accepts": int(greedy_accepts),
        "greedy_rejects": int(greedy_rejects),
        "best_updates_after_initial": int(
            best_updates_after_initial
        ),
        "first_mop": float(first_mop),
        "last_mop": float(last_mop),
        "first_moa": float(first_moa),
        "last_moa": float(last_moa),
    }

    return (*result, diagnostics)
