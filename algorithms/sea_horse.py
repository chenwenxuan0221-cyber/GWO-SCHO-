"""Sea-Horse Optimizer (SHO) — paper-equation-faithful H5 comparator.

IMPORTANT NAME
--------------
SHO here means Sea-Horse Optimizer (Zhao et al., 2022), NOT Spotted Hyena
Optimizer.

Evidence boundary
-----------------
The author MATLAB Central package (File Exchange 115945) and its SHO.m file
are publicly identifiable, but this project did not recover the full historical
v1.0.0 MATLAB body for line-by-line verification at H5c7.

Therefore this implementation is intentionally labelled:
    PAPER_EQUATION_FAITHFUL__AUTHOR_PACKAGE_IDENTIFIED__CODE_LEVEL_NOT_VERIFIED

It follows the original SHO paper equations/pseudocode for movement,
predation, breeding and survivor selection. It does NOT claim code-level
source fidelity or MATLAB RNG equivalence.

Main equations used
-------------------
Movement:
- r1 ~ N(0,1)
- r1 > 0: spiral + Levy flight
- r1 <= 0: Brownian-motion equation from the paper

Predation:
- success threshold r2 > 0.1
- alpha = (1 - t/T) ** (2*t/T)

Breeding:
- sort parents by fitness
- best half = fathers, worse half = mothers
- one offspring per father/mother pair
- offspring = r3*father + (1-r3)*mother

Selection:
- pool predation population + offspring
- retain best N

Paper constants:
u = v = l = 0.05
Levy s = 0.01
Levy lambda = 1.5
"""

from __future__ import annotations

from math import gamma, sin, pi
from typing import Callable
import numpy as np

ArrayLike = float | int | np.ndarray | list[float] | tuple[float, ...]


def _normalize_bounds(lb: ArrayLike, ub: ArrayLike, dim: int):
    lo_raw = np.asarray(lb, dtype=float)
    hi_raw = np.asarray(ub, dtype=float)

    if lo_raw.ndim == 0 and hi_raw.ndim == 0:
        lo = float(lo_raw)
        hi = float(hi_raw)
        if not lo < hi:
            raise ValueError("lb must be strictly smaller than ub.")
        return np.full(dim, lo), np.full(dim, hi), True

    lo = np.broadcast_to(lo_raw, (dim,)).astype(float, copy=True)
    hi = np.broadcast_to(hi_raw, (dim,)).astype(float, copy=True)

    if np.any(lo >= hi):
        raise ValueError("Every lower bound must be smaller than its upper bound.")

    return lo, hi, False


def _initialize(N, dim, lb, ub, rng):
    lo, hi, scalar = _normalize_bounds(lb, ub, dim)
    if scalar:
        return rng.random((N, dim)) * (hi[0] - lo[0]) + lo[0]

    X = np.empty((N, dim), dtype=float)
    for j in range(dim):
        X[:, j] = rng.random(N) * (hi[j] - lo[j]) + lo[j]
    return X


def _clip(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)


def _levy_paper(dim: int, rng: np.random.Generator, lam: float = 1.5):
    """Paper-form Levy coefficient, evaluated elementwise.

    Levy = s * omega * sigma / |k|^(1/lambda)
    with s=0.01 and omega,k uniform in [0,1].
    """
    s = 0.01
    sigma = (
        gamma(1.0 + lam) * sin(pi * lam / 2.0)
        / (
            gamma((1.0 + lam) / 2.0)
            * lam
            * 2.0 ** ((lam - 1.0) / 2.0)
        )
    )
    omega = rng.random(dim)
    k = rng.random(dim)

    # Zero has probability zero for the continuous generator; tiny is only a
    # numerical guard against an accidental exact zero.
    tiny = np.finfo(float).tiny
    return s * omega * sigma / np.maximum(np.abs(k), tiny) ** (1.0 / lam)


def sho(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    """Run the paper-equation-faithful Sea-Horse Optimizer."""
    if N < 2 or N % 2 != 0:
        raise ValueError("H5 Sea-Horse SHO requires an even N >= 2.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 1:
        raise ValueError("MaxIter must be >= 1.")

    rng = np.random.default_rng(seed)
    lo, hi, _ = _normalize_bounds(lb, ub, dim)

    X = _initialize(N, dim, lb, ub, rng)
    fit = np.array([float(obj_func(x)) for x in X], dtype=float)

    best_idx = int(np.argmin(fit))
    best_score = float(fit[best_idx])
    best_pos = X[best_idx].copy()

    curve = np.empty(MaxIter, dtype=float)

    u = 0.05
    v = 0.05
    l_const = 0.05
    levy_lambda = 1.5

    diag = {
        "initial_evaluations": N,
        "predation_evaluations": 0,
        "offspring_evaluations": 0,
        "spiral_moves": 0,
        "brownian_moves": 0,
        "predation_success_branch": 0,
        "predation_failure_branch": 0,
        "offspring_created": 0,
        "survivor_sorts": 0,
        "best_updates": 0,
        "vector_bound_compatible": True,
        "source_code_level_verified": False,
    }

    for t in range(1, MaxIter + 1):
        # ---------------- Movement behavior ----------------
        X1 = np.empty_like(X)

        for i in range(N):
            r1 = rng.normal()

            if r1 > 0.0:
                theta = 2.0 * np.pi * rng.random(dim)
                rho = u * np.exp(theta * v)
                xx = rho * np.cos(theta)
                yy = rho * np.sin(theta)
                zz = rho * theta
                levy = _levy_paper(dim, rng, levy_lambda)

                X1[i] = X[i] + levy * (
                    (best_pos - X[i]) * xx * yy * zz
                    + best_pos
                )
                diag["spiral_moves"] += 1
            else:
                # Paper Brownian equation:
                # X + rand*l*beta_t*(X - beta_t*Xelite)
                x_normal = rng.normal(size=dim)
                beta_t = (
                    1.0 / np.sqrt(2.0 * np.pi)
                ) * np.exp(-(x_normal ** 2) / 2.0)

                X1[i] = X[i] + (
                    rng.random(dim)
                    * l_const
                    * beta_t
                    * (X[i] - beta_t * best_pos)
                )
                diag["brownian_moves"] += 1

        # ---------------- Predation behavior ----------------
        alpha = (1.0 - t / MaxIter) ** (2.0 * t / MaxIter)
        X2 = np.empty_like(X)

        for i in range(N):
            r2 = rng.random()
            r = rng.random(dim)

            if r2 > 0.1:
                X2[i] = (
                    alpha * (best_pos - r * X1[i])
                    + (1.0 - alpha) * best_pos
                )
                diag["predation_success_branch"] += 1
            else:
                X2[i] = (
                    (1.0 - alpha) * (X1[i] - r * best_pos)
                    + alpha * X1[i]
                )
                diag["predation_failure_branch"] += 1

            X2[i] = _clip(X2[i], lo, hi)

        fit2 = np.array(
            [float(obj_func(x)) for x in X2],
            dtype=float,
        )
        diag["predation_evaluations"] += N

        order = np.argsort(fit2, kind="stable")
        X2_sorted = X2[order]
        fit2_sorted = fit2[order]

        # Update historical best from predation population.
        if float(fit2_sorted[0]) < best_score:
            best_score = float(fit2_sorted[0])
            best_pos = X2_sorted[0].copy()
            diag["best_updates"] += 1

        # ---------------- Breeding behavior ----------------
        half = N // 2
        fathers = X2_sorted[:half]
        mothers = X2_sorted[half:]

        offspring = np.empty((half, dim), dtype=float)
        for i in range(half):
            r3 = rng.random()
            offspring[i] = (
                r3 * fathers[i]
                + (1.0 - r3) * mothers[i]
            )
            offspring[i] = _clip(offspring[i], lo, hi)
            diag["offspring_created"] += 1

        fit_off = np.array(
            [float(obj_func(x)) for x in offspring],
            dtype=float,
        )
        diag["offspring_evaluations"] += half

        # ---------------- Survivor selection ----------------
        pool_X = np.vstack((X2_sorted, offspring))
        pool_fit = np.concatenate((fit2_sorted, fit_off))

        pool_order = np.argsort(pool_fit, kind="stable")
        X = pool_X[pool_order[:N]].copy()
        fit = pool_fit[pool_order[:N]].copy()
        diag["survivor_sorts"] += 1

        if float(fit[0]) < best_score:
            best_score = float(fit[0])
            best_pos = X[0].copy()
            diag["best_updates"] += 1

        curve[t - 1] = best_score

    result = (
        float(best_score),
        best_pos.copy(),
        curve.copy(),
    )

    if not return_diagnostics:
        return result

    diag.update(
        {
            "objective_evaluations": int(
                diag["initial_evaluations"]
                + diag["predation_evaluations"]
                + diag["offspring_evaluations"]
            ),
            "expected_objective_evaluations": int(
                N + MaxIter * (N + N // 2)
            ),
            "expected_movement_agents": int(N * MaxIter),
            "expected_predation_agents": int(N * MaxIter),
            "expected_offspring": int((N // 2) * MaxIter),
            "u": u,
            "v": v,
            "l": l_const,
            "levy_s": 0.01,
            "levy_lambda": levy_lambda,
        }
    )
    return (*result, diag)
