"""H4h - Explicit controlled interpretations for SCHO Fig.7 Variants 1-11.

IMPORTANT EXACTNESS LABEL
-------------------------
These eleven variants are NOT claimed to reproduce unrecovered author variant
source code. They implement a frozen, explicit controlled interpretation of
the descriptions in SCHO Section 3.1.1 / Fig.7.

The full "SCHO" control delegates directly to frozen `algorithms.scho.scho`.

Do not tune these definitions against the printed Fig.7 bar heights.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from algorithms.scho import (
    _matlab_if_all_greater,
    _matlab_if_all_less,
    _matlab_initialization,
    scho as frozen_scho,
)


ArrayLike = float | int | np.ndarray | list[float] | tuple[float, ...]

FIG7_VARIANTS = (
    "SCHO",
    "V1",
    "V2",
    "V3",
    "V4",
    "V5",
    "V6",
    "V7",
    "V8",
    "V9",
    "V10",
    "V11",
)

# Fixed SCHO constants from the source-faithful implementation.
_U = 0.388
_M = 0.45
_N = 0.5
_P = 10.0
_Q = 9.0
_ALPHA = 4.6
_BETA = 1.55
_CT = 3.6

_SINH1 = float(np.sinh(1.0))
_COSH1 = float(np.cosh(1.0))
_SIN1 = float(np.sin(1.0))
_ONE_MINUS_COS1 = float(1.0 - np.cos(1.0))


def _range_matched_sine_sinh(x: float) -> float:
    """Sine-shaped substitute with sinh([0,1]) endpoint/range matching.

    h_sin(0)=sinh(0)=0
    h_sin(1)=sinh(1)

    The raw sine argument remains x in [0,1]; only amplitude is normalized.
    """
    return float(_SINH1 * np.sin(x) / _SIN1)


def _range_matched_cosine_cosh(x: float) -> float:
    """Cosine-shaped substitute with cosh([0,1]) endpoint/range matching.

    h_cos(0)=cosh(0)=1
    h_cos(1)=cosh(1)

    `1-cos(x)` is normalized so the substitute has the same endpoints,
    monotone direction, and value range as cosh(x) on [0,1].
    """
    return float(
        1.0
        + (_COSH1 - 1.0)
        * (1.0 - np.cos(x))
        / _ONE_MINUS_COS1
    )


def _range_matched_linear_sinh(x: float) -> float:
    """Linear substitute matching sinh endpoints/range on [0,1]."""
    return float(_SINH1 * x)


def _range_matched_linear_cosh(x: float) -> float:
    """Linear substitute matching cosh endpoints/range on [0,1]."""
    return float(1.0 + (_COSH1 - 1.0) * x)


def _hyperbolic_pair(x: float) -> tuple[float, float]:
    return float(np.sinh(x)), float(np.cosh(x))


def _sincos_pair(x: float) -> tuple[float, float]:
    return _range_matched_sine_sinh(x), _range_matched_cosine_cosh(x)


def _linear_pair(x: float) -> tuple[float, float]:
    return _range_matched_linear_sinh(x), _range_matched_linear_cosh(x)


def _original_A(z: float, r_switch: float) -> float:
    sinh_z = float(np.sinh(z))
    cosh_z = float(np.cosh(z))
    exponent = cosh_z / sinh_z
    return float((_P - _Q * (z ** exponent)) * r_switch)


def _A_whole_sincos_schedule(z: float, r_switch: float) -> float:
    """V7 controlled whole-switch substitute.

    Replace the *entire deterministic switching envelope* by a smooth
    sine/cosine schedule with the same endpoints as the original envelope:

        z=0 -> 10
        z=1 -> 1

    g(z)=0.5*[cos(pi*z/2) + 1 - sin(pi*z/2)]
    envelope=1+9*g(z)
    A=envelope*r_switch
    """
    g = 0.5 * (
        np.cos(np.pi * z / 2.0)
        + 1.0
        - np.sin(np.pi * z / 2.0)
    )
    return float((1.0 + 9.0 * g) * r_switch)


def _A_whole_linear_schedule(z: float, r_switch: float) -> float:
    """V8 controlled whole-switch linear envelope, 10 -> 1."""
    return float((_P - _Q * z) * r_switch)


def _A_eq17_sincos(z: float, r_switch: float) -> float:
    """V10: retain Eq.(17) structure; replace sinh/cosh inside exponent."""
    s, c = _sincos_pair(z)
    exponent = c / s
    return float((_P - _Q * (z ** exponent)) * r_switch)


def _A_eq17_linear(z: float, r_switch: float) -> float:
    """V11: retain Eq.(17) structure; replace sinh/cosh inside exponent."""
    s, c = _linear_pair(z)
    exponent = c / s
    return float((_P - _Q * (z ** exponent)) * r_switch)


def _compute_A_and_switch(
    variant: str,
    z: float,
    r_switch: float,
) -> tuple[float, bool | None]:
    """Return A and optional forced exploration decision.

    For V9, `forced_explore` is Bernoulli(0.5) using the same r_switch draw.
    Other variants return None and branch using A exactly as SCHO does.
    """
    if variant == "V7":
        return _A_whole_sincos_schedule(z, r_switch), None
    if variant == "V8":
        return _A_whole_linear_schedule(z, r_switch), None
    if variant == "V9":
        # Explicit controlled interpretation of "same selection probability":
        # use the source's switching random draw directly as a 50/50 selector.
        return float("nan"), bool(r_switch > 0.5)
    if variant == "V10":
        return _A_eq17_sincos(z, r_switch), None
    if variant == "V11":
        return _A_eq17_linear(z, r_switch), None
    return _original_A(z, r_switch), None


def _pair_for_eq12(variant: str, r: float) -> tuple[float, float]:
    if variant == "V3":
        return _sincos_pair(r)
    if variant == "V5":
        return _linear_pair(r)
    return _hyperbolic_pair(r)


def _pair_for_eq5(variant: str, r: float) -> tuple[float, float]:
    if variant == "V4":
        return _sincos_pair(r)
    if variant == "V6":
        return _linear_pair(r)
    return _hyperbolic_pair(r)


def _new_diagnostics():
    return {
        "coordinate_updates": 0,
        "first_exploration": 0,
        "first_exploitation": 0,
        "second_exploration": 0,
        "second_exploitation": 0,
        "bounded_reinitializations": 0,
        "v1_second_exploitation_replaced": 0,
        "v2_second_exploitation_noop": 0,
        "v3_v5_eq12_alt": 0,
        "v4_v6_eq5_alt": 0,
        "v7_v8_v9_v10_v11_switch_alt": 0,
    }


def scho_fig7_variant(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    variant: str,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    """Run SCHO or one frozen H4h controlled Fig.7 variant.

    Returns
    -------
    By default:
        best_score, best_pos, convergence_curve

    If `return_diagnostics=True`:
        best_score, best_pos, convergence_curve, diagnostics
    """
    variant = str(variant).upper()

    if variant not in FIG7_VARIANTS:
        raise ValueError(
            f"Unknown Fig.7 variant {variant!r}. "
            f"Available: {FIG7_VARIANTS}"
        )

    if variant == "SCHO":
        result = frozen_scho(
            obj_func=obj_func,
            dim=dim,
            lb=lb,
            ub=ub,
            N=N,
            MaxIter=MaxIter,
            seed=seed,
        )
        if return_diagnostics:
            return (*result, {"delegated_to_frozen_scho": True})
        return result

    if N < 2:
        raise ValueError("SCHO Fig.7 variants require N >= 2.")
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

    BS = int(np.floor(MaxIter / _BETA))
    T = int(np.floor(MaxIter / _CT))
    BSi = 0
    BSi_temp = 0

    ub_2: ArrayLike = np.array(ub_original, copy=True)
    lb_2: ArrayLike = np.array(lb_original, copy=True)

    X = _matlab_initialization(N, dim, ub_original, lb_original, rng)
    Objective_values = np.zeros(N, dtype=float)

    for i in range(N):
        Objective_values[i] = float(obj_func(X[i]))
        if Objective_values[i] < Destination_fitness:
            Destination_position = X[i].copy()
            Destination_fitness = Objective_values[i]

    Convergence_curve[0] = Destination_fitness
    diagnostics = _new_diagnostics()

    t = 2
    while t <= MaxIter:
        for i in range(N):
            for j in range(dim):
                diagnostics["coordinate_updates"] += 1

                z = t / MaxIter

                # One switching draw per coordinate, preserving source call count.
                r1 = rng.random()
                A, forced_explore = _compute_A_and_switch(
                    variant, z, r1
                )
                if variant in {"V7", "V8", "V9", "V10", "V11"}:
                    diagnostics[
                        "v7_v8_v9_v10_v11_switch_alt"
                    ] += 1

                # Exact source bounded-search block and quirks are retained.
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

                    X = _matlab_initialization(
                        N, dim, ub_2, lb_2, rng
                    )
                    diagnostics["bounded_reinitializations"] += 1
                    BSi_temp = BSi
                    BSi = 0

                if t <= T:
                    # Preserve the source's four post-switch draws.
                    r2 = rng.random()
                    r3 = rng.random()
                    a1 = 3.0 * (-1.3 * t / MaxIter + _M)
                    r4 = rng.random()
                    r5 = rng.random()

                    if forced_explore is None:
                        explore = bool(A > 1.0)
                    else:
                        explore = forced_explore

                    if explore:
                        diagnostics["first_exploration"] += 1

                        s3, c3 = _pair_for_eq5(variant, r3)
                        if variant in {"V4", "V6"}:
                            diagnostics["v4_v6_eq5_alt"] += 1

                        W1 = r2 * a1 * (c3 + _U * s3 - 1.0)

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
                        diagnostics["first_exploitation"] += 1

                        s3, c3 = _hyperbolic_pair(r3)
                        W3 = r2 * a1 * (c3 + _U * s3)

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
                    # Preserve source draw order/count even when a controlled
                    # deletion/replacement does not need every value.
                    r2 = rng.random()
                    r3 = rng.random()
                    a2 = 2.0 * (-t / MaxIter + _N)
                    W2 = r2 * a2
                    r4 = rng.random()
                    r5 = rng.random()

                    if forced_explore is None:
                        exploit = bool(A < 1.0)
                    else:
                        exploit = not forced_explore

                    if exploit:
                        diagnostics["second_exploitation"] += 1

                        if variant == "V1":
                            # Paper description: use the first-phase
                            # exploitation equation in both exploitation phases.
                            a1 = 3.0 * (-1.3 * t / MaxIter + _M)
                            s3, c3 = _hyperbolic_pair(r3)
                            W3 = r2 * a1 * (c3 + _U * s3)

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

                            diagnostics[
                                "v1_second_exploitation_replaced"
                            ] += 1

                        elif variant == "V2":
                            # Controlled deletion semantics:
                            # when Eq.(12) would have executed, keep X(i,j)
                            # unchanged. Random draws are still consumed.
                            diagnostics[
                                "v2_second_exploitation_noop"
                            ] += 1

                        else:
                            s3, c3 = _pair_for_eq12(variant, r3)
                            if variant in {"V3", "V5"}:
                                diagnostics["v3_v5_eq12_alt"] += 1

                            X[i, j] = X[i, j] + (
                                r5
                                * s3
                                / c3
                                * abs(
                                    W2 * Destination_position[j]
                                    - X[i, j]
                                )
                            )
                    else:
                        diagnostics["second_exploration"] += 1
                        distance = abs(
                            0.003
                            * W2
                            * Destination_position[j]
                            - X[i, j]
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

        if t == BS:
            BSi = BS + 1
            BS = BS + int(np.floor((MaxIter - BS) / _ALPHA))

            for i_sort in range(1, N):
                for j_sort in range(0, N - 1 - i_sort):
                    if (
                        Objective_values[j_sort]
                        > Objective_values[j_sort + 1]
                    ):
                        temp = Objective_values[j_sort]
                        Objective_values[j_sort] = (
                            Objective_values[j_sort + 1]
                        )
                        Objective_values[j_sort + 1] = temp

                        temp_row = Position_sort[j_sort].copy()
                        Position_sort[j_sort] = Position_sort[
                            j_sort + 1
                        ]
                        Position_sort[j_sort + 1] = temp_row

            Destination_position_second = Position_sort[1].copy()

        Convergence_curve[t - 1] = Destination_fitness
        t += 1

    result = (
        float(Destination_fitness),
        Destination_position.copy(),
        Convergence_curve.copy(),
    )
    if return_diagnostics:
        return (*result, diagnostics)
    return result
