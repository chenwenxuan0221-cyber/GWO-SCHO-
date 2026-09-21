"""Source-structured Python translation of Mirjalili's Sine Cosine Algorithm (SCA).

Primary implementation basis
----------------------------
Seyedali Mirjalili, "SCA: A Sine Cosine Algorithm", author MATLAB source
(File Exchange 54948, SCA.m).

H5 protocol note
----------------
The SCHO paper Table 6 uses SCA parameter a=2, which is also the value used
by the author MATLAB source.

Exactness boundary
------------------
This module preserves the author MATLAB control/update structure, including:
- initialization before the main loop;
- main loop starts at t=2;
- r1 = 2 - t*(2/MaxIter);
- three fresh random scalars r2/r3/r4 for every candidate coordinate;
- in-place coordinate position updates;
- boundary clipping only after all position updates;
- objective evaluation after clipping;
- source convergence-curve quirk: element 1 is left at zero.

NumPy's RNG is used, so this is NOT a MATLAB bitwise/RNG-stream reproduction.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

ArrayLike = float | int | np.ndarray | list[float] | tuple[float, ...]


def _normalize_bounds(lb: ArrayLike, ub: ArrayLike, dim: int):
    lb_arr = np.asarray(lb, dtype=float)
    ub_arr = np.asarray(ub, dtype=float)

    if lb_arr.ndim == 0 and ub_arr.ndim == 0:
        if not float(lb_arr) < float(ub_arr):
            raise ValueError("lb must be strictly smaller than ub.")
        return lb_arr, ub_arr, True

    lb_vec = np.broadcast_to(lb_arr, (dim,)).astype(float, copy=True)
    ub_vec = np.broadcast_to(ub_arr, (dim,)).astype(float, copy=True)

    if np.any(lb_vec >= ub_vec):
        raise ValueError("Every lower bound must be smaller than its upper bound.")

    return lb_vec, ub_vec, False


def _matlab_style_initialization(
    N: int,
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    rng: np.random.Generator,
) -> np.ndarray:
    """Mirror the author's initialization.m call structure.

    Scalar bounds -> one N x dim random matrix draw.
    Vector bounds -> one N-vector random draw per dimension.
    """
    lb_n, ub_n, scalar = _normalize_bounds(lb, ub, dim)

    if scalar:
        return (
            rng.random((N, dim))
            * (float(ub_n) - float(lb_n))
            + float(lb_n)
        )

    X = np.empty((N, dim), dtype=float)
    for j in range(dim):
        X[:, j] = (
            rng.random(N)
            * (ub_n[j] - lb_n[j])
            + lb_n[j]
        )
    return X


def _clip_source_style(
    x: np.ndarray,
    lb: ArrayLike,
    ub: ArrayLike,
    dim: int,
) -> np.ndarray:
    lb_n, ub_n, scalar = _normalize_bounds(lb, ub, dim)

    if scalar:
        lo = float(lb_n)
        hi = float(ub_n)
        flag_ub = x > hi
        flag_lb = x < lo
        keep = np.logical_not(flag_ub | flag_lb)
        return x * keep + hi * flag_ub + lo * flag_lb

    flag_ub = x > ub_n
    flag_lb = x < lb_n
    keep = np.logical_not(flag_ub | flag_lb)
    return x * keep + ub_n * flag_ub + lb_n * flag_lb


def sca(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    """Run the source-structured Sine Cosine Algorithm.

    Returns
    -------
    best_score, best_position, convergence_curve

    Notes
    -----
    The returned convergence curve intentionally preserves the author source's
    first-element-zero behavior. For H5/Fig.9 this will be handled explicitly
    rather than silently "fixed".
    """
    if N < 1:
        raise ValueError("N must be >= 1.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 2:
        raise ValueError(
            "MaxIter must be >= 2 to preserve the author SCA main-loop/curve semantics."
        )

    rng = np.random.default_rng(seed)

    X = _matlab_style_initialization(N, dim, lb, ub, rng)

    destination_position = np.zeros(dim, dtype=float)
    destination_fitness = np.inf

    # Intentionally source-faithful: index 0 remains zero.
    convergence_curve = np.zeros(MaxIter, dtype=float)
    objective_values = np.zeros(N, dtype=float)

    objective_evaluations = 0

    # Initial evaluation.
    for i in range(N):
        objective_values[i] = float(obj_func(X[i]))
        objective_evaluations += 1

        # Source uses a first-agent special case, then '<' comparisons.
        if i == 0:
            destination_position = X[i].copy()
            destination_fitness = objective_values[i]
        elif objective_values[i] < destination_fitness:
            destination_position = X[i].copy()
            destination_fitness = objective_values[i]

    sine_updates = 0
    cosine_updates = 0
    random_draws_update = 0
    first_r1 = None
    last_r1 = None

    # Author source starts from the second iteration.
    t = 2
    while t <= MaxIter:
        a = 2.0
        r1 = a - t * (a / MaxIter)

        if first_r1 is None:
            first_r1 = float(r1)
        last_r1 = float(r1)

        # In-place coordinate updates, using the current historical destination.
        for i in range(N):
            for j in range(dim):
                r2 = (2.0 * np.pi) * rng.random()
                r3 = 2.0 * rng.random()
                r4 = rng.random()
                random_draws_update += 3

                distance = abs(
                    r3 * destination_position[j] - X[i, j]
                )

                if r4 < 0.5:
                    X[i, j] = (
                        X[i, j]
                        + r1 * np.sin(r2) * distance
                    )
                    sine_updates += 1
                else:
                    X[i, j] = (
                        X[i, j]
                        + r1 * np.cos(r2) * distance
                    )
                    cosine_updates += 1

        # Source performs boundary repair/evaluation only after all positions
        # have been updated.
        for i in range(N):
            X[i] = _clip_source_style(X[i], lb, ub, dim)

            objective_values[i] = float(obj_func(X[i]))
            objective_evaluations += 1

            if objective_values[i] < destination_fitness:
                destination_position = X[i].copy()
                destination_fitness = objective_values[i]

        convergence_curve[t - 1] = destination_fitness
        t += 1

    result = (
        float(destination_fitness),
        destination_position.copy(),
        convergence_curve.copy(),
    )

    if not return_diagnostics:
        return result

    diagnostics = {
        "objective_evaluations": int(objective_evaluations),
        "expected_objective_evaluations": int(N * MaxIter),
        "coordinate_updates": int((MaxIter - 1) * N * dim),
        "random_draws_update": int(random_draws_update),
        "expected_random_draws_update": int(
            3 * (MaxIter - 1) * N * dim
        ),
        "sine_updates": int(sine_updates),
        "cosine_updates": int(cosine_updates),
        "first_r1": float(first_r1),
        "last_r1": float(last_r1),
        "curve_index0_source_zero": bool(convergence_curve[0] == 0.0),
    }
    return (*result, diagnostics)
