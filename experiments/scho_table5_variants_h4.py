"""H4d - Paper-described structural SCHO variants for Table 5.

The original paper defines five structural ablations by removing one or more
of four subordinate models:

1. exploration
2. exploitation
3. bounded-search strategy
4. switching mechanism

Exact variant source code was not recovered.  This module therefore freezes a
transparent, paper-described structural interpretation while preserving the
frozen source-faithful SCHO equations and quirks for every retained model.

`variant="SCHO"` is included as an internal control and must remain exactly
trajectory-equivalent to the frozen `algorithms.scho.scho` implementation.

Variants
--------
SCHO
    exploration + exploitation + bounded search + switching
SCHO_NT
    exploration + exploitation + switching; no bounded search
SCHO_NSTF
    exploration only; no exploitation / bounded search / switching
SCHO_NFTF
    exploitation only; no exploration / bounded search / switching
SCHO_NSF
    exploration + bounded search; no exploitation / switching
SCHO_NFF
    exploitation + bounded search; no exploration / switching

When the switching model is absent, no Eq.(17) random draw is consumed.
The active search model is applied unconditionally in each phase:
- t <= T: first-phase exploration or first-phase exploitation
- t > T : second-phase exploration or second-phase exploitation

Within an active phase we retain the frozen source's branch-local random draw
pattern r2/r3/r4/r5.  This is a controlled implementation decision because the
paper does not publish the deleted-variant source code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from algorithms.scho import (
    ArrayLike,
    _matlab_if_all_greater,
    _matlab_if_all_less,
    _matlab_initialization,
)


@dataclass(frozen=True)
class VariantConfig:
    exploration: bool
    exploitation: bool
    bounded_search: bool
    switching: bool


VARIANT_CONFIGS = {
    "SCHO": VariantConfig(True, True, True, True),
    "SCHO_NT": VariantConfig(True, True, False, True),
    "SCHO_NSTF": VariantConfig(True, False, False, False),
    "SCHO_NFTF": VariantConfig(False, True, False, False),
    "SCHO_NSF": VariantConfig(True, False, True, False),
    "SCHO_NFF": VariantConfig(False, True, True, False),
}

TABLE5_VARIANTS = tuple(VARIANT_CONFIGS.keys())


def _validate_variant(variant: str) -> VariantConfig:
    try:
        cfg = VARIANT_CONFIGS[variant]
    except KeyError as exc:
        raise ValueError(
            f"Unknown H4 Table-5 variant {variant!r}. "
            f"Available: {list(VARIANT_CONFIGS)}"
        ) from exc

    if not (cfg.exploration or cfg.exploitation):
        raise AssertionError("At least one search model must remain active.")
    if cfg.switching and not (cfg.exploration and cfg.exploitation):
        raise AssertionError(
            "This H4 protocol uses switching only when both search models exist."
        )
    return cfg


def scho_table5_variant(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    *,
    variant: str,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    """Run a Table-5 structural SCHO variant.

    Returns the same three primary outputs as frozen SCHO.  When
    `return_diagnostics=True`, a fourth dictionary is returned with structural
    branch counts used only for H4d validation.
    """

    cfg = _validate_variant(variant)

    if N < 2:
        raise ValueError("H4 structural SCHO variants require N >= 2.")
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

    # Frozen source parameters.
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

    ub_2: ArrayLike = np.array(ub_original, copy=True)
    lb_2: ArrayLike = np.array(lb_original, copy=True)

    diagnostics = {
        "variant": variant,
        "exploration_updates": 0,
        "exploitation_updates": 0,
        "switching_draws": 0,
        "bounded_redistributions": 0,
        "phase1_coordinate_updates": 0,
        "phase2_coordinate_updates": 0,
        "T": int(T),
        "initial_BS": int(BS),
    }

    X = _matlab_initialization(N, dim, ub_original, lb_original, rng)
    Objective_values = np.zeros(N, dtype=float)

    for i in range(N):
        Objective_values[i] = float(obj_func(X[i]))
        if Objective_values[i] < Destination_fitness:
            Destination_position = X[i].copy()
            Destination_fitness = Objective_values[i]

    Convergence_curve[0] = Destination_fitness
    t = 2

    while t <= MaxIter:
        for i in range(N):
            for j in range(dim):
                z = t / MaxIter

                # Switching model: exact frozen Eq.(17) computation and RNG draw.
                A = None
                if cfg.switching:
                    cosh2 = (np.exp(z) + np.exp(-z)) / 2.0
                    sinh2 = (np.exp(z) - np.exp(-z)) / 2.0
                    r1 = rng.random()
                    A = (p - q * (z ** (cosh2 / sinh2))) * r1
                    diagnostics["switching_draws"] += 1

                # Bounded-search model: literal retained source block.
                if cfg.bounded_search and t == BSi:
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
                    diagnostics["bounded_redistributions"] += 1
                    BSi_temp = BSi
                    BSi = 0

                # Retain source's r2/r3/r4/r5 draw pattern in every active
                # search phase.  This is exact for full SCHO and our frozen
                # controlled interpretation for non-switching ablations.
                if t <= T:
                    diagnostics["phase1_coordinate_updates"] += 1

                    r2 = rng.random()
                    r3 = rng.random()
                    a1 = 3.0 * (-1.3 * t / MaxIter + m)
                    r4 = rng.random()
                    r5 = rng.random()

                    sinh_r3 = (np.exp(r3) - np.exp(-r3)) / 2.0
                    cosh_r3 = (np.exp(r3) + np.exp(-r3)) / 2.0

                    if cfg.exploration and cfg.exploitation:
                        do_exploration = bool(A > 1.0)
                    else:
                        do_exploration = cfg.exploration

                    if do_exploration:
                        # First-phase exploration: Eq.(5) + Eq.(4).
                        W1 = r2 * a1 * (cosh_r3 + u * sinh_r3 - 1.0)
                        if r5 <= 0.5:
                            X[i, j] = Destination_position[j] + r4 * W1 * X[i, j]
                        else:
                            X[i, j] = Destination_position[j] - r4 * W1 * X[i, j]
                        diagnostics["exploration_updates"] += 1
                    else:
                        # First-phase exploitation: Eq.(11) + Eq.(10).
                        W3 = r2 * a1 * (cosh_r3 + u * sinh_r3)
                        if r5 <= 0.5:
                            X[i, j] = Destination_position[j] + r4 * W3 * X[i, j]
                        else:
                            X[i, j] = Destination_position[j] - r4 * W3 * X[i, j]
                        diagnostics["exploitation_updates"] += 1

                else:
                    diagnostics["phase2_coordinate_updates"] += 1

                    r2 = rng.random()
                    r3 = rng.random()
                    a2 = 2.0 * (-t / MaxIter + n)
                    W2 = r2 * a2
                    r4 = rng.random()
                    r5 = rng.random()

                    if cfg.exploration and cfg.exploitation:
                        do_exploitation = bool(A < 1.0)
                    else:
                        do_exploitation = cfg.exploitation

                    if do_exploitation:
                        # Second-phase exploitation: Eq.(12).
                        sinh_r3 = (np.exp(r3) - np.exp(-r3)) / 2.0
                        cosh_r3 = (np.exp(r3) + np.exp(-r3)) / 2.0
                        X[i, j] = X[i, j] + (
                            r5
                            * sinh_r3
                            / cosh_r3
                            * abs(W2 * Destination_position[j] - X[i, j])
                        )
                        diagnostics["exploitation_updates"] += 1
                    else:
                        # Second-phase exploration: Eq.(7).
                        distance = abs(
                            0.003 * W2 * Destination_position[j] - X[i, j]
                        )
                        if r4 <= 0.5:
                            X[i, j] = X[i, j] + distance
                        else:
                            X[i, j] = X[i, j] - distance
                        diagnostics["exploration_updates"] += 1

            if cfg.bounded_search:
                BSi = BSi_temp

        # Boundary repair + fitness + historical best, exact retained source
        # behavior.  If bounded search is disabled, ub_2/lb_2 remain original.
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

        # Retain the source's second-solution / bounded-search scheduling only
        # when subordinate model 3 exists.
        if cfg.bounded_search and t == BS:
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

    outputs = (
        float(Destination_fitness),
        Destination_position.copy(),
        Convergence_curve.copy(),
    )
    if return_diagnostics:
        return (*outputs, dict(diagnostics))
    return outputs
