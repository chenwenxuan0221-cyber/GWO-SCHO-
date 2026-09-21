"""Source-structured Python translation of Golden Jackal Optimization (GJO).

Primary basis
-------------
Nitish Chopra's author MATLAB File Exchange submission 108889, together with
the original GJO equations from Chopra & Ansari (2022).

Preserved source mechanics
--------------------------
- male/female jackal scores start at +inf;
- population is initialized before the main loop;
- main loop counter starts at l=0 and runs while l < MaxIter;
- clipping/evaluation happens before every position-update phase;
- male/female leader updates use independent sequential if-statements, so a
  newly discovered male is NOT shifted into the female slot automatically;
- E1 = 1.5 * (1 - l/MaxIter);
- one Levy matrix RL = 0.05*levy(N,dim,1.5) is generated per iteration;
- one fresh E0 = 2*rand-1 is generated per coordinate;
- |E| < 1 uses the exploitation equations;
- |E| >= 1 uses the exploration equations;
- the two jackal proposals are averaged;
- the convergence curve is written after the position update, but records the
  male score from the evaluation phase that happened before that update.

RNG exactness
-------------
NumPy's Generator is used. The source random-call structure is preserved, but
MATLAB RNG-stream / bitwise equivalence is not claimed.

Levy helper
-----------
The author package includes levy.m. H5c3 follows the common Mantegna helper
used by the GJO source family:
    u ~ Normal(0, sigma_u)
    v ~ Normal(0, 1)
    z = u / |v|^(1/beta)
and GJO multiplies it by 0.05 in the main loop.

No optimizer "repairs" are introduced.
"""

from __future__ import annotations

from math import gamma, sin, pi
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
    """Mirror the initialization.m call structure used in the author package."""
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


def levy(
    n: int,
    m: int,
    beta: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Mantegna Levy helper used by the GJO source family."""
    if not (1.0 < beta < 2.0):
        raise ValueError("beta must satisfy 1 < beta < 2.")

    num = gamma(1.0 + beta) * sin(pi * beta / 2.0)
    den = (
        gamma((1.0 + beta) / 2.0)
        * beta
        * (2.0 ** ((beta - 1.0) / 2.0))
    )
    sigma_u = (num / den) ** (1.0 / beta)

    u = rng.normal(0.0, sigma_u, size=(n, m))
    v = rng.normal(0.0, 1.0, size=(n, m))

    return u / (np.abs(v) ** (1.0 / beta))


def gjo(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    """Run Golden Jackal Optimization.

    Returns
    -------
    best_score, best_position, convergence_curve
    """
    if N < 2:
        raise ValueError("GJO requires N >= 2.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 1:
        raise ValueError("MaxIter must be >= 1.")

    rng = np.random.default_rng(seed)
    lo, hi, _ = _normalize_bounds(lb, ub, dim)

    male_pos = np.zeros(dim, dtype=float)
    male_score = np.inf

    female_pos = np.zeros(dim, dtype=float)
    female_score = np.inf

    positions = _matlab_style_initialization(
        N, dim, lb, ub, rng
    )

    convergence_curve = np.zeros(MaxIter, dtype=float)

    objective_evaluations = 0
    leader_random_draws = 0
    levy_normal_draws = 0
    exploitation_updates = 0
    exploration_updates = 0

    first_e1 = None
    last_e1 = None
    female_updates = 0
    male_updates = 0

    l = 0
    while l < MaxIter:
        # Source evaluates and updates leaders before the movement phase.
        for i in range(N):
            positions[i] = _clip_source_style(
                positions[i], lo, hi
            )

            fitness = float(obj_func(positions[i]))
            objective_evaluations += 1

            # Independent sequential ifs: intentionally no "old male -> female"
            # shift when a new male is found.
            if fitness < male_score:
                male_score = fitness
                male_pos = positions[i].copy()
                male_updates += 1

            if fitness > male_score and fitness < female_score:
                female_score = fitness
                female_pos = positions[i].copy()
                female_updates += 1

        e1 = 1.5 * (1.0 - (l / MaxIter))
        if first_e1 is None:
            first_e1 = float(e1)
        last_e1 = float(e1)

        # One Levy matrix is generated per iteration.
        rl = 0.05 * levy(N, dim, 1.5, rng)
        levy_normal_draws += 2 * N * dim

        # Position update.
        for i in range(N):
            for j in range(dim):
                e0 = 2.0 * rng.random() - 1.0
                leader_random_draws += 1
                e = e1 * e0

                if abs(e) < 1.0:
                    # Exploitation: jackals encircle/pounce.
                    d_male = abs(
                        rl[i, j] * male_pos[j]
                        - positions[i, j]
                    )
                    d_female = abs(
                        rl[i, j] * female_pos[j]
                        - positions[i, j]
                    )
                    x1 = male_pos[j] - e * d_male
                    x2 = female_pos[j] - e * d_female
                    exploitation_updates += 1
                else:
                    # Exploration: jackals search/follow prey.
                    d_male = abs(
                        male_pos[j]
                        - rl[i, j] * positions[i, j]
                    )
                    d_female = abs(
                        female_pos[j]
                        - rl[i, j] * positions[i, j]
                    )
                    x1 = male_pos[j] - e * d_male
                    x2 = female_pos[j] - e * d_female
                    exploration_updates += 1

                positions[i, j] = (x1 + x2) / 2.0

        convergence_curve[l] = male_score
        l += 1

    result = (
        float(male_score),
        male_pos.copy(),
        convergence_curve.copy(),
    )

    if not return_diagnostics:
        return result

    diagnostics = {
        "objective_evaluations": int(objective_evaluations),
        "expected_objective_evaluations": int(N * MaxIter),
        "coordinate_updates": int(N * dim * MaxIter),
        "leader_random_draws": int(leader_random_draws),
        "expected_leader_random_draws": int(N * dim * MaxIter),
        "levy_normal_draws": int(levy_normal_draws),
        "expected_levy_normal_draws": int(
            2 * N * dim * MaxIter
        ),
        "exploration_updates": int(exploration_updates),
        "exploitation_updates": int(exploitation_updates),
        "male_updates": int(male_updates),
        "female_updates": int(female_updates),
        "first_e1": float(first_e1),
        "last_e1": float(last_e1),
        "female_score_finite": bool(np.isfinite(female_score)),
    }

    return (*result, diagnostics)
