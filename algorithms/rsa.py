"""Source-structured Python translation of Reptile Search Algorithm (RSA).

Primary source
--------------
Laith Abualigah's author MATLAB `RSA.m` from the public author repository /
MATLAB Central submission 101385.

Critical source facts preserved
-------------------------------
- t starts at 1 and runs through T;
- Alpha=0.1 and Beta=0.005 in the author MATLAB source;
- ES = 2*randi([-1,1])*(1-t/T);
- update loops start from MATLAB i=2, so the first solution is NEVER updated;
- Xnew is initialized as zeros and only rows 2..N are written/evaluated;
- R uses the source operator precedence exactly:
      Best_j - X[random,j] / (Best_j + eps)
  NOT `(Best_j - X[random,j])/(Best_j+eps)`;
- P uses the current accepted X(i,:) mean;
- four quarter-phase rules use the source's strict boundary tests;
- candidate rows are clipped, evaluated, and greedily accepted immediately;
- the historical best is updated after greedy acceptance;
- one convergence value is recorded for every t=1..T.

Vector-bound compatibility
--------------------------
The published `RSA.m` expression for P uses scalar `(UB-LB)` and is not
well-defined for a vector interval in MATLAB. H5 needs F17, whose bounds differ
by coordinate. For vector bounds only, this port uses the explicit project
adapter:
    (UB_j - LB_j)
inside P.

This adapter is separately diagnosed and is NOT claimed to be author-source
exact for F17. Scalar-bound classical functions preserve the source formula.

RNG exactness
-------------
NumPy's Generator is used; MATLAB bitwise/RNG-stream equivalence is not
claimed.
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
    """Mirror the author's initialization.m call structure."""
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


def rsa(
    obj_func: Callable[[np.ndarray], float],
    dim: int,
    lb: ArrayLike,
    ub: ArrayLike,
    N: int,
    MaxIter: int,
    seed: int | None = None,
    return_diagnostics: bool = False,
):
    """Run source-structured RSA under the SCHO Table-6 protocol."""
    if N < 2:
        raise ValueError("RSA requires N >= 2.")
    if dim < 1:
        raise ValueError("dim must be >= 1.")
    if MaxIter < 1:
        raise ValueError("MaxIter must be >= 1.")

    rng = np.random.default_rng(seed)
    lo, hi, scalar_bounds = _normalize_bounds(lb, ub, dim)

    best_pos = np.zeros(dim, dtype=float)
    best_score = np.inf

    X = _matlab_style_initialization(
        N, dim, lb, ub, rng
    )

    # Exact source structure: starts as zeros, not a copy of X.
    Xnew = np.zeros((N, dim), dtype=float)

    curve = np.zeros(MaxIter, dtype=float)

    alpha = 0.1
    beta = 0.005
    matlab_eps = np.finfo(float).eps

    fit = np.zeros(N, dtype=float)
    fit_new = np.zeros(N, dtype=float)

    objective_evaluations = 0

    # Initial evaluation of all N solutions.
    for i in range(N):
        fit[i] = float(obj_func(X[i]))
        objective_evaluations += 1

        if fit[i] < best_score:
            best_score = fit[i]
            best_pos = X[i].copy()

    # Diagnostics.
    es_integer_draws = 0
    es_negative = 0
    es_zero = 0
    es_positive = 0

    r_random_index_draws = 0
    phase2_extra_index_draws = 0
    uniform_update_draws = 0

    phase1_updates = 0
    phase2_updates = 0
    phase3_updates = 0
    phase4_updates = 0

    candidate_evaluations = 0
    greedy_accepts = 0
    greedy_rejects = 0
    best_updates_after_initial = 0

    first_solution_update_attempts = 0
    vector_bound_adapter_uses = 0

    t = 1
    while t < MaxIter + 1:
        # MATLAB randi([-1 1]) -> one discrete draw from {-1,0,1}.
        es_int = int(rng.integers(-1, 2))
        es_integer_draws += 1

        if es_int < 0:
            es_negative += 1
        elif es_int == 0:
            es_zero += 1
        else:
            es_positive += 1

        ES = 2.0 * es_int * (1.0 - (t / MaxIter))

        # Exact source quirk: MATLAB `for i=2:size(X,1)`.
        # Python zero-based rows 1..N-1; row 0 is never updated.
        for i in range(1, N):
            row_mean = float(np.mean(X[i]))

            for j in range(dim):
                # R index draw occurs in every phase before the branch.
                ridx = int(rng.integers(0, N))
                r_random_index_draws += 1

                # Exact source precedence:
                # Best - X[ridx,j] / (Best + eps)
                R = (
                    best_pos[j]
                    - X[ridx, j]
                    / (best_pos[j] + matlab_eps)
                )

                if scalar_bounds:
                    span = hi[0] - lo[0]
                else:
                    # H5 F17 adapter; author scalar formula is not
                    # MATLAB-compatible with vector UB-LB here.
                    span = hi[j] - lo[j]
                    vector_bound_adapter_uses += 1

                P = (
                    alpha
                    + (X[i, j] - row_mean)
                    / (
                        best_pos[j] * span
                        + matlab_eps
                    )
                )
                eta = best_pos[j] * P

                if t < MaxIter / 4.0:
                    Xnew[i, j] = (
                        best_pos[j]
                        - eta * beta
                        - R * rng.random()
                    )
                    uniform_update_draws += 1
                    phase1_updates += 1

                elif (
                    t < 2.0 * MaxIter / 4.0
                    and t >= MaxIter / 4.0
                ):
                    ridx2 = int(rng.integers(0, N))
                    phase2_extra_index_draws += 1

                    Xnew[i, j] = (
                        best_pos[j]
                        * X[ridx2, j]
                        * ES
                        * rng.random()
                    )
                    uniform_update_draws += 1
                    phase2_updates += 1

                elif (
                    t < 3.0 * MaxIter / 4.0
                    and t >= 2.0 * MaxIter / 4.0
                ):
                    Xnew[i, j] = (
                        best_pos[j] * P * rng.random()
                    )
                    uniform_update_draws += 1
                    phase3_updates += 1

                else:
                    Xnew[i, j] = (
                        best_pos[j]
                        - eta * matlab_eps
                        - R * rng.random()
                    )
                    uniform_update_draws += 1
                    phase4_updates += 1

            Xnew[i] = _clip_source_style(
                Xnew[i], lo, hi
            )

            fit_new[i] = float(obj_func(Xnew[i]))
            candidate_evaluations += 1
            objective_evaluations += 1

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

        curve[t - 1] = best_score
        t += 1

    result = (
        float(best_score),
        best_pos.copy(),
        curve.copy(),
    )

    if not return_diagnostics:
        return result

    coordinate_updates = (
        (N - 1) * dim * MaxIter
    )

    diagnostics = {
        "alpha": float(alpha),
        "beta": float(beta),
        "scalar_bounds": bool(scalar_bounds),
        "objective_evaluations": int(objective_evaluations),
        "expected_objective_evaluations": int(
            N + (N - 1) * MaxIter
        ),
        "candidate_evaluations": int(
            candidate_evaluations
        ),
        "expected_candidate_evaluations": int(
            (N - 1) * MaxIter
        ),
        "coordinate_updates": int(coordinate_updates),
        "first_solution_update_attempts": int(
            first_solution_update_attempts
        ),
        "es_integer_draws": int(es_integer_draws),
        "es_negative": int(es_negative),
        "es_zero": int(es_zero),
        "es_positive": int(es_positive),
        "r_random_index_draws": int(
            r_random_index_draws
        ),
        "phase2_extra_index_draws": int(
            phase2_extra_index_draws
        ),
        "uniform_update_draws": int(
            uniform_update_draws
        ),
        "phase1_updates": int(phase1_updates),
        "phase2_updates": int(phase2_updates),
        "phase3_updates": int(phase3_updates),
        "phase4_updates": int(phase4_updates),
        "greedy_accepts": int(greedy_accepts),
        "greedy_rejects": int(greedy_rejects),
        "best_updates_after_initial": int(
            best_updates_after_initial
        ),
        "vector_bound_adapter_uses": int(
            vector_bound_adapter_uses
        ),
    }

    return (*result, diagnostics)
