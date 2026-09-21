"""History-instrumented GWO for Stage H2.

This module intentionally mirrors the frozen `algorithms/gwo.py` control flow
and random-call order. It exists only to record qualitative histories required
for the GWO-paper Section 4.4 / Fig. 11 reproduction.

DO NOT replace `algorithms/gwo.py` with this file.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class GWOHistory:
    best_score: float
    best_pos: np.ndarray
    convergence_curve: np.ndarray
    position_history: np.ndarray
    fitness_history: np.ndarray
    first_agent_x1: np.ndarray
    first_agent_fitness: np.ndarray
    best_position_history: np.ndarray
    a_history: np.ndarray


def gwo_with_history(obj_func, dim, lb, ub, N, MaxIter, seed=None):
    """Run the frozen-project GWO logic while recording Fig.-11 histories."""

    # Keep this setup aligned with algorithms/gwo.py.
    lb = np.broadcast_to(np.asarray(lb, dtype=float), (dim,))
    ub = np.broadcast_to(np.asarray(ub, dtype=float), (dim,))

    rng = np.random.default_rng(seed)
    X = rng.uniform(lb, ub, size=(N, dim))

    alpha_score = np.inf
    beta_score = np.inf
    delta_score = np.inf

    alpha_pos = np.zeros(dim)
    beta_pos = np.zeros(dim)
    delta_pos = np.zeros(dim)

    convergence_curve = np.zeros(MaxIter)

    # History is sampled at the evaluated population state:
    # after boundary repair and before the position update.
    position_history = np.zeros((MaxIter, N, dim), dtype=float)
    fitness_history = np.zeros((MaxIter, N), dtype=float)
    first_agent_x1 = np.zeros(MaxIter, dtype=float)
    first_agent_fitness = np.zeros(MaxIter, dtype=float)
    best_position_history = np.zeros((MaxIter, dim), dtype=float)
    a_history = np.zeros(MaxIter, dtype=float)

    for t in range(MaxIter):
        X = np.clip(X, lb, ub)

        # Sampling here adds no RNG calls and does not alter the population.
        position_history[t] = X
        first_agent_x1[t] = X[0, 0]

        fitness = np.apply_along_axis(obj_func, 1, X)

        fitness_history[t] = fitness
        first_agent_fitness[t] = fitness[0]

        for i in range(N):
            current_score = fitness[i]

            if current_score < alpha_score:
                alpha_score = current_score
                alpha_pos = X[i].copy()

            if current_score > alpha_score and current_score < beta_score:
                beta_score = current_score
                beta_pos = X[i].copy()

            if (
                current_score > alpha_score
                and current_score > beta_score
                and current_score < delta_score
            ):
                delta_score = current_score
                delta_pos = X[i].copy()

        a = 2.0 - 2.0 * t / MaxIter
        a_history[t] = a
        best_position_history[t] = alpha_pos

        for i in range(N):
            X1 = np.zeros(dim)
            X2 = np.zeros(dim)
            X3 = np.zeros(dim)

            for j in range(dim):
                # alpha
                r1 = rng.random()
                r2 = rng.random()
                A1 = 2.0 * a * r1 - a
                C1 = 2.0 * r2
                D_alpha = abs(C1 * alpha_pos[j] - X[i, j])
                X1[j] = alpha_pos[j] - A1 * D_alpha

                # beta
                r1 = rng.random()
                r2 = rng.random()
                A2 = 2.0 * a * r1 - a
                C2 = 2.0 * r2
                D_beta = abs(C2 * beta_pos[j] - X[i, j])
                X2[j] = beta_pos[j] - A2 * D_beta

                # delta
                r1 = rng.random()
                r2 = rng.random()
                A3 = 2.0 * a * r1 - a
                C3 = 2.0 * r2
                D_delta = abs(C3 * delta_pos[j] - X[i, j])
                X3[j] = delta_pos[j] - A3 * D_delta

            new_position = (X1 + X2 + X3) / 3.0
            X[i] = np.clip(new_position, lb, ub)

        convergence_curve[t] = alpha_score

    return GWOHistory(
        best_score=float(alpha_score),
        best_pos=alpha_pos.copy(),
        convergence_curve=convergence_curve,
        position_history=position_history,
        fitness_history=fitness_history,
        first_agent_x1=first_agent_x1,
        first_agent_fitness=first_agent_fitness,
        best_position_history=best_position_history,
        a_history=a_history,
    )
