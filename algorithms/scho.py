"""Source-faithful Python reproduction of the official MATLAB SCHO 3.3 code.

Reference implementation audited from the official SCHO.m / initialization.m
package supplied by the user (MathWorks File Exchange, v3.3).

IMPORTANT
---------
This module intentionally preserves several behaviors of the official MATLAB
source even when they look unusual or differ from the paper's apparent intent:

1. The initial population is evaluated first; the main loop starts at t = 2.
2. A is recomputed for every candidate and every dimension.
3. Five scalar random numbers are consumed per coordinate in the normal
   position-update path (A random number + r2/r3/r4/r5), including random
   numbers that a selected branch may not use.
4. Boundary repair is asymmetric: upper violations go to the current interval
   midpoint; lower violations go to the current lower bound.
5. Position_sort is initialized to zeros and is never filled with X, so the
   MATLAB source's Destination_position_second remains a zero vector.
6. A bounded-search event is scheduled at t == BS but redistributed at t ==
   BS + 1 through BSi. Because the redistribution code is inside the i-loop,
   the whole population is reinitialized once for each candidate (N times).
7. In that event, the first dimension triggers the redistribution and the
   resulting scalar bounded-search interval is applied to all dimensions
   (for the scalar-bound classical functions such as F1).

The goal here is NOT to silently repair the algorithm. A later
"paper-intended" implementation can be compared against this baseline.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


ArrayLike = float | int | np.ndarray | list[float] | tuple[float, ...]


def _is_scalar_bound(x: ArrayLike) -> bool:
    """Match the MATLAB initialization branch for scalar vs per-dimension bounds."""
    return np.asarray(x).ndim == 0 or np.asarray(x).size == 1


def _matlab_initialization(
    n_agents: int,
    dim: int,
    ub: ArrayLike,
    lb: ArrayLike,
    rng: np.random.Generator,
) -> np.ndarray:
    """Translate initialization.m while preserving MATLAB column fill order.

    NumPy and MATLAB do not use the same random-number generator, so identical
    seeded trajectories across languages are not expected.  However, consuming
    the generated values in Fortran/column-major order mirrors MATLAB's
    rand(N, dim) assignment order.
    """

    ub_arr = np.asarray(ub, dtype=float)
    lb_arr = np.asarray(lb, dtype=float)

    if _is_scalar_bound(ub_arr):
        ub_s = float(ub_arr.reshape(-1)[0])
        lb_s = float(lb_arr.reshape(-1)[0])

        # MATLAB: rand(N, dim) is populated column-major.
        u = rng.random(n_agents * dim).reshape((n_agents, dim), order="F")
        return u * (ub_s - lb_s) + lb_s

    ub_vec = np.asarray(ub_arr, dtype=float).reshape(-1)
    lb_vec = np.asarray(lb_arr, dtype=float).reshape(-1)

    if ub_vec.size != dim or lb_vec.size != dim:
        raise ValueError(
            "Per-dimension bounds must have exactly `dim` elements."
        )

    # MATLAB source loops over dimensions and calls rand(N, 1) each time.
    X = np.empty((n_agents, dim), dtype=float)
    for j in range(dim):
        X[:, j] = (
            rng.random(n_agents) * (ub_vec[j] - lb_vec[j]) + lb_vec[j]
        )
    return X


def _matlab_if_all_greater(a: ArrayLike, b: ArrayLike) -> bool:
    """MATLAB-style truth test for `if a > b` when an array is produced."""
    return bool(np.all(np.asarray(a, dtype=float) > np.asarray(b, dtype=float)))


def _matlab_if_all_less(a: ArrayLike, b: ArrayLike) -> bool:
    """MATLAB-style truth test for `if a < b` when an array is produced."""
    return bool(np.all(np.asarray(a, dtype=float) < np.asarray(b, dtype=float)))


def scho(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
):
    """Sinh Cosh Optimizer (SCHO), source-faithful MATLAB 3.3 reproduction.

    Parameters
    ----------
    obj_func : callable
        Objective function. Receives shape=(dim,) and returns a scalar fitness.
    dim : int
        Problem dimension.
    lb, ub : float or array-like
        Lower and upper search-space bounds.
    N : int
        Number of candidate solutions.
    MaxIter : int
        MATLAB code's Max_iteration. The initial population evaluation is
        stored as convergence point 1, then t = 2..MaxIter is executed.
    seed : int or None
        NumPy seed for reproducible Python runs. This does not reproduce
        MATLAB's RNG stream exactly.

    Returns
    -------
    best_score : float
        Historical best fitness (Destination_fitness).
    best_pos : ndarray, shape=(dim,)
        Historical best position (Destination_position).
    convergence_curve : ndarray, shape=(MaxIter,)
        Historical best after the initial evaluation and after each MATLAB t.
    """

    if N < 2:
        raise ValueError("Source-faithful SCHO requires N >= 2.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 1:
        raise ValueError("MaxIter must be >= 1.")

    rng = np.random.default_rng(seed)

    # Keep the original bounds in their input form because the MATLAB source
    # compares bounded-search scalars against the original lb/ub variables.
    lb_original = np.asarray(lb, dtype=float)
    ub_original = np.asarray(ub, dtype=float)

    # MATLAB source variables, kept close to the original names/semantics.
    Destination_position = np.zeros(dim, dtype=float)
    Destination_fitness = np.inf
    Destination_position_second = np.zeros(dim, dtype=float)
    Convergence_curve = np.zeros(MaxIter, dtype=float)
    Position_sort = np.zeros((N, dim), dtype=float)

    # SCHO parameters from the official source.
    u = 0.388
    m = 0.45
    n = 0.5
    p = 10.0
    q = 9.0
    Alpha = 4.6
    Beta = 1.55
    BS = int(np.floor(MaxIter / Beta))
    ct = 3.6
    T = int(np.floor(MaxIter / ct))
    BSi = 0
    BSi_temp = 0

    # These are dynamic bounds in the MATLAB source.
    ub_2: ArrayLike = np.array(ub_original, copy=True)
    lb_2: ArrayLike = np.array(lb_original, copy=True)

    # ---------------------------------------------------------
    # Initial population and first fitness evaluation
    # ---------------------------------------------------------
    X = _matlab_initialization(N, dim, ub_original, lb_original, rng)
    Objective_values = np.zeros(N, dtype=float)

    for i in range(N):
        Objective_values[i] = float(obj_func(X[i]))
        if Objective_values[i] < Destination_fitness:
            Destination_position = X[i].copy()
            Destination_fitness = Objective_values[i]

    Convergence_curve[0] = Destination_fitness

    # The official MATLAB source starts its main loop at t = 2.
    t = 2

    # ---------------------------------------------------------
    # Main loop: MATLAB t = 2 ... Max_iteration
    # ---------------------------------------------------------
    while t <= MaxIter:

        # ----- Position update -----
        for i in range(N):
            for j in range(dim):

                # Eq. (17): update A.
                z = t / MaxIter
                cosh2 = (np.exp(z) + np.exp(-z)) / 2.0
                sinh2 = (np.exp(z) - np.exp(-z)) / 2.0

                # MATLAB variable r1 is the paper's switching random number.
                r1 = rng.random()
                A = (p - q * (z ** (cosh2 / sinh2))) * r1

                # ---------------------------------------------------------
                # Official bounded-search block.
                # This is intentionally inside i/j exactly as in SCHO.m.
                # ---------------------------------------------------------
                if t == BSi:
                    ub_2 = (
                        Destination_position[j]
                        + (1.0 - t / MaxIter)
                        * abs(
                            Destination_position[j]
                            - Destination_position_second[j]
                        )
                    )
                    lb_2 = (
                        Destination_position[j]
                        - (1.0 - t / MaxIter)
                        * abs(
                            Destination_position[j]
                            - Destination_position_second[j]
                        )
                    )

                    # Exact source behavior: compare with original bounds and
                    # replace by original ub/lb if the MATLAB if-condition holds.
                    if _matlab_if_all_greater(ub_2, ub_original):
                        ub_2 = np.array(ub_original, copy=True)
                    if _matlab_if_all_less(lb_2, lb_original):
                        lb_2 = np.array(lb_original, copy=True)

                    X = _matlab_initialization(N, dim, ub_2, lb_2, rng)
                    BSi_temp = BSi
                    BSi = 0

                # ---------------------------------------------------------
                # First phase: exploration / exploitation
                # ---------------------------------------------------------
                if t <= T:
                    r2 = rng.random()
                    r3 = rng.random()
                    a1 = 3.0 * (-1.3 * t / MaxIter + m)
                    r4 = rng.random()
                    r5 = rng.random()

                    sinh_r3 = (np.exp(r3) - np.exp(-r3)) / 2.0
                    cosh_r3 = (np.exp(r3) + np.exp(-r3)) / 2.0

                    if A > 1.0:
                        # Eq. (5) + Eq. (4)
                        W1 = r2 * a1 * (cosh_r3 + u * sinh_r3 - 1.0)
                        if r5 <= 0.5:
                            X[i, j] = (
                                Destination_position[j]
                                + r4 * W1 * X[i, j]
                            )
                        else:
                            X[i, j] = (
                                Destination_position[j]
                                - r4 * W1 * X[i, j]
                            )
                    else:
                        # Eq. (11) + Eq. (10)
                        W3 = r2 * a1 * (cosh_r3 + u * sinh_r3)
                        if r5 <= 0.5:
                            X[i, j] = (
                                Destination_position[j]
                                + r4 * W3 * X[i, j]
                            )
                        else:
                            X[i, j] = (
                                Destination_position[j]
                                - r4 * W3 * X[i, j]
                            )

                # ---------------------------------------------------------
                # Second phase: exploitation / exploration
                # ---------------------------------------------------------
                else:
                    r2 = rng.random()
                    r3 = rng.random()
                    a2 = 2.0 * (-t / MaxIter + n)
                    W2 = r2 * a2
                    r4 = rng.random()
                    r5 = rng.random()

                    if A < 1.0:
                        # Eq. (12): second-phase exploitation.
                        sinh_r3 = (np.exp(r3) - np.exp(-r3)) / 2.0
                        cosh_r3 = (np.exp(r3) + np.exp(-r3)) / 2.0
                        X[i, j] = X[i, j] + (
                            r5
                            * sinh_r3
                            / cosh_r3
                            * abs(W2 * Destination_position[j] - X[i, j])
                        )
                    else:
                        # Eq. (7): second-phase exploration.
                        distance = abs(
                            0.003 * W2 * Destination_position[j] - X[i, j]
                        )
                        if r4 <= 0.5:
                            X[i, j] = X[i, j] + distance
                        else:
                            X[i, j] = X[i, j] - distance

            # Exact source statement after each candidate's inner dimension loop.
            BSi = BSi_temp

        # ---------------------------------------------------------
        # Boundary repair + fitness + historical best update
        # ---------------------------------------------------------
        for i in range(N):
            ub2_arr = np.asarray(ub_2, dtype=float)
            lb2_arr = np.asarray(lb_2, dtype=float)

            Flag4ub = X[i] > ub2_arr
            Flag4lb = X[i] < lb2_arr

            # Literal translation of:
            # X(i,:)=(X(i,:).*(~(Flag4ub+Flag4lb))) ...
            #       +(ub_2+lb_2)/2.*Flag4ub + lb_2.*Flag4lb;
            keep = np.logical_not(
                Flag4ub.astype(int) + Flag4lb.astype(int)
            )
            X[i] = (
                X[i] * keep
                + (ub2_arr + lb2_arr) / 2.0 * Flag4ub
                + lb2_arr * Flag4lb
            )

            Objective_values[i] = float(obj_func(X[i]))

            if Objective_values[i] < Destination_fitness:
                Destination_position = X[i].copy()
                Destination_fitness = Objective_values[i]

        # ---------------------------------------------------------
        # Official "find second solution" block
        # ---------------------------------------------------------
        if t == BS:
            BSi = BS + 1
            BS = BS + int(np.floor((MaxIter - BS) / Alpha))

            # Position_sort intentionally remains the zero matrix, exactly as
            # in SCHO.m.  Reproduce the source's bubble-sort loop bounds.
            for i_sort in range(1, N):
                for j_sort in range(0, N - 1 - i_sort):
                    if Objective_values[j_sort] > Objective_values[j_sort + 1]:
                        temp = Objective_values[j_sort]
                        Objective_values[j_sort] = Objective_values[j_sort + 1]
                        Objective_values[j_sort + 1] = temp

                        temp_row = Position_sort[j_sort].copy()
                        Position_sort[j_sort] = Position_sort[j_sort + 1]
                        Position_sort[j_sort + 1] = temp_row

            Destination_position_second = Position_sort[1].copy()

        Convergence_curve[t - 1] = Destination_fitness
        t += 1

    return (
        float(Destination_fitness),
        Destination_position.copy(),
        Convergence_curve.copy(),
    )
