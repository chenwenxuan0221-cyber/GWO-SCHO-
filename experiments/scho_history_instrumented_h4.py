"""H4b - History-instrumented source-faithful SCHO.

This module mirrors the frozen `algorithms/scho.py` logic and adds read-only
history recording for SCHO paper Fig. 8.

IMPORTANT
---------
- `algorithms/scho.py` is not modified.
- No additional optimizer RNG draws are made.
- No additional objective evaluations are made.
- History is recorded only from states that the frozen algorithm already
  evaluates.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from algorithms.scho import (
    ArrayLike,
    _matlab_if_all_greater,
    _matlab_if_all_less,
    _matlab_initialization,
)


def scho_with_history(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
):
    """Run frozen-source-equivalent SCHO while recording evaluated histories.

    Returns
    -------
    best_score, best_pos, convergence_curve, history

    history keys
    ------------
    position_history : (MaxIter, N, dim)
        Evaluated population states after boundary repair.
    fitness_history : (MaxIter, N)
        Fitness values corresponding to `position_history`.
    first_agent_x1 : (MaxIter,)
        First coordinate of the first evaluated search agent.
    average_fitness : (MaxIter,)
        Mean fitness of all N evaluated agents.
    best_position_history : (MaxIter, dim)
        Historical-best position after each evaluated population.
    convergence : (MaxIter,)
        Historical-best fitness; identical to returned convergence curve.
    phase_history : (MaxIter,)
        1 for the first search phase, 2 for the second.  The initial
        evaluation is labeled phase 1 for visualization.
    redistribution_count : (MaxIter,)
        Number of full-population reinitializations triggered by the literal
        bounded-search block during that evaluation step.
    T : int
        Frozen source phase-switch index floor(MaxIter / 3.6).
    initial_BS : int
        Frozen source first bounded-search scheduling index
        floor(MaxIter / 1.55).
    """

    if N < 2:
        raise ValueError("Source-faithful SCHO requires N >= 2.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 1:
        raise ValueError("MaxIter must be >= 1.")

    rng = np.random.default_rng(seed)

    lb_original = np.asarray(lb, dtype=float)
    ub_original = np.asarray(ub, dtype=float)

    Destination_position = np.zeros(dim, dtype=float)
    Destination_fitness = np.inf
    Destination_position_second = np.zeros(dim, dtype=float)
    Convergence_curve = np.zeros(MaxIter, dtype=float)
    Position_sort = np.zeros((N, dim), dtype=float)

    # Official-source parameters.
    u = 0.388
    m = 0.45
    n = 0.5
    p = 10.0
    q = 9.0
    Alpha = 4.6
    Beta = 1.55
    BS = int(np.floor(MaxIter / Beta))
    initial_BS = BS
    ct = 3.6
    T = int(np.floor(MaxIter / ct))
    BSi = 0
    BSi_temp = 0

    ub_2: ArrayLike = np.array(ub_original, copy=True)
    lb_2: ArrayLike = np.array(lb_original, copy=True)

    # Read-only evidence arrays. Allocating/storing these consumes no RNG and
    # performs no objective evaluations.
    position_history = np.empty((MaxIter, N, dim), dtype=float)
    fitness_history = np.empty((MaxIter, N), dtype=float)
    first_agent_x1 = np.empty(MaxIter, dtype=float)
    average_fitness = np.empty(MaxIter, dtype=float)
    best_position_history = np.empty((MaxIter, dim), dtype=float)
    phase_history = np.empty(MaxIter, dtype=np.int8)
    redistribution_count = np.zeros(MaxIter, dtype=np.int64)

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

    position_history[0] = X
    fitness_history[0] = Objective_values
    first_agent_x1[0] = X[0, 0]
    average_fitness[0] = float(np.mean(Objective_values))
    best_position_history[0] = Destination_position
    phase_history[0] = 1

    t = 2

    # ---------------------------------------------------------
    # Main loop: exact frozen logic + passive history recording
    # ---------------------------------------------------------
    while t <= MaxIter:
        redistribution_this_iteration = 0

        for i in range(N):
            for j in range(dim):
                z = t / MaxIter
                cosh2 = (np.exp(z) + np.exp(-z)) / 2.0
                sinh2 = (np.exp(z) - np.exp(-z)) / 2.0

                r1 = rng.random()
                A = (p - q * (z ** (cosh2 / sinh2))) * r1

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

                    if _matlab_if_all_greater(ub_2, ub_original):
                        ub_2 = np.array(ub_original, copy=True)
                    if _matlab_if_all_less(lb_2, lb_original):
                        lb_2 = np.array(lb_original, copy=True)

                    X = _matlab_initialization(N, dim, ub_2, lb_2, rng)
                    redistribution_this_iteration += 1
                    BSi_temp = BSi
                    BSi = 0

                if t <= T:
                    r2 = rng.random()
                    r3 = rng.random()
                    a1 = 3.0 * (-1.3 * t / MaxIter + m)
                    r4 = rng.random()
                    r5 = rng.random()

                    sinh_r3 = (np.exp(r3) - np.exp(-r3)) / 2.0
                    cosh_r3 = (np.exp(r3) + np.exp(-r3)) / 2.0

                    if A > 1.0:
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
                else:
                    r2 = rng.random()
                    r3 = rng.random()
                    a2 = 2.0 * (-t / MaxIter + n)
                    W2 = r2 * a2
                    r4 = rng.random()
                    r5 = rng.random()

                    if A < 1.0:
                        sinh_r3 = (np.exp(r3) - np.exp(-r3)) / 2.0
                        cosh_r3 = (np.exp(r3) + np.exp(-r3)) / 2.0
                        X[i, j] = X[i, j] + (
                            r5
                            * sinh_r3
                            / cosh_r3
                            * abs(W2 * Destination_position[j] - X[i, j])
                        )
                    else:
                        distance = abs(
                            0.003 * W2 * Destination_position[j] - X[i, j]
                        )
                        if r4 <= 0.5:
                            X[i, j] = X[i, j] + distance
                        else:
                            X[i, j] = X[i, j] - distance

            BSi = BSi_temp

        for i in range(N):
            ub2_arr = np.asarray(ub_2, dtype=float)
            lb2_arr = np.asarray(lb_2, dtype=float)

            Flag4ub = X[i] > ub2_arr
            Flag4lb = X[i] < lb2_arr

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

        # Record the evaluated population BEFORE the source's t==BS fitness
        # sorting block. Sorting does not change the mean, but this convention
        # keeps fitness_history aligned with the row order of X.
        idx = t - 1
        position_history[idx] = X
        fitness_history[idx] = Objective_values
        first_agent_x1[idx] = X[0, 0]
        average_fitness[idx] = float(np.mean(Objective_values))
        best_position_history[idx] = Destination_position
        phase_history[idx] = 1 if t <= T else 2
        redistribution_count[idx] = redistribution_this_iteration

        if t == BS:
            BSi = BS + 1
            BS = BS + int(np.floor((MaxIter - BS) / Alpha))

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

    history = {
        "position_history": position_history.copy(),
        "fitness_history": fitness_history.copy(),
        "first_agent_x1": first_agent_x1.copy(),
        "average_fitness": average_fitness.copy(),
        "best_position_history": best_position_history.copy(),
        "convergence": Convergence_curve.copy(),
        "phase_history": phase_history.copy(),
        "redistribution_count": redistribution_count.copy(),
        "T": int(T),
        "initial_BS": int(initial_BS),
    }

    return (
        float(Destination_fitness),
        Destination_position.copy(),
        Convergence_curve.copy(),
        history,
    )
