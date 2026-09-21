"""GWO-paper composite functions F24-F29 (SIS 2005 CF1-CF6).

Primary implementation follows the uploaded original MATLAB package
``SIS_novel_func.m`` and its D=10 MAT data files.

Important source discrepancy
----------------------------
GWO paper Table 4 prints F26/CF3 as ten Griewank components. The original
SIS2005 MATLAB source ``com_func3`` actually uses ten Rastrigin components.
The default here is therefore ``variant='source_faithful'``. A separate
``variant='paper_table4'`` diagnostic is exposed for F26 only; it must not be
silently substituted for the source-faithful benchmark.

The GWO paper aliases are F24..F29. Canonical names are CF1..CF6.
All six problems are D=10, bounds [-5, 5], and have global minimum 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.io import loadmat


DATA_DIR = Path(__file__).resolve().parent / "data" / "sis2005"
DIM = 10
LB = -5.0
UB = 5.0


PAPER_TABLE8 = {
    "F24": {"mean": 43.83544, "std": 69.86146},
    "F25": {"mean": 91.80086, "std": 95.5518},
    "F26": {"mean": 61.43776, "std": 68.68816},
    "F27": {"mean": 123.1235, "std": 163.9937},
    "F28": {"mean": 102.1429, "std": 81.25536},
    "F29": {"mean": 43.14261, "std": 84.48573},
}

_ALIAS_TO_NUM = {
    "F24": 1, "CF1": 1,
    "F25": 2, "CF2": 2,
    "F26": 3, "CF3": 3,
    "F27": 4, "CF4": 4,
    "F28": 5, "CF5": 5,
    "F29": 6, "CF6": 6,
}

_NUM_TO_PAPER = {i: f"F{23+i}" for i in range(1, 7)}
_NUM_TO_CF = {i: f"CF{i}" for i in range(1, 7)}


def _sphere(x: np.ndarray) -> np.ndarray:
    return np.sum(x * x, axis=1)


def _griewank(x: np.ndarray) -> np.ndarray:
    idx = np.sqrt(np.arange(1, x.shape[1] + 1, dtype=float))
    return np.sum(x * x, axis=1) / 4000.0 - np.prod(np.cos(x / idx), axis=1) + 1.0


def _rastrigin(x: np.ndarray) -> np.ndarray:
    return np.sum(x * x - 10.0 * np.cos(2.0 * np.pi * x) + 10.0, axis=1)


def _ackley(x: np.ndarray) -> np.ndarray:
    d = x.shape[1]
    return (
        20.0
        - 20.0 * np.exp(-0.2 * np.sqrt(np.sum(x * x, axis=1) / d))
        - np.exp(np.sum(np.cos(2.0 * np.pi * x), axis=1) / d)
        + np.e
    )


def _weierstrass(x: np.ndarray) -> np.ndarray:
    # Literal translation of SIS_novel_func.m:
    # x <- x + 0.5, a=0.5, b=3, kmax=20,
    # then subtract D*w(0.5).
    z = x + 0.5
    k = np.arange(21, dtype=float)
    a = 0.5 ** k
    omega = 2.0 * np.pi * (3.0 ** k)
    values = np.sum(
        a[None, None, :] * np.cos(z[:, :, None] * omega[None, None, :]),
        axis=2,
    )
    w_half = np.sum(a * np.cos(0.5 * omega))
    return np.sum(values, axis=1) - x.shape[1] * w_half


_BASIC = {
    "sphere": _sphere,
    "griewank": _griewank,
    "rastrigin": _rastrigin,
    "ackley": _ackley,
    "weierstrass": _weierstrass,
}


@dataclass(frozen=True)
class SIS2005Benchmark:
    paper_name: str
    canonical_name: str
    func_num: int
    dim: int
    lb: float
    ub: float
    optimum: float
    paper_mean: float
    paper_std: float
    variant: str
    objective: Callable[[np.ndarray], float]
    optima: np.ndarray


@dataclass(frozen=True)
class _CompositionSpec:
    func_num: int
    optima: np.ndarray
    sigma: np.ndarray
    lamda: np.ndarray
    bias: np.ndarray
    matrices: tuple[np.ndarray, ...]
    functions: tuple[Callable[[np.ndarray], np.ndarray], ...]


def _load_optima(filename: str) -> np.ndarray:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing SIS2005 source asset: {path}. "
            "Place the original MAT files under benchmarks/data/sis2005/."
        )
    raw = np.asarray(loadmat(path)["o"], dtype=float)
    if raw.shape[0] != 10 or raw.shape[1] < DIM:
        raise ValueError(f"Unexpected optima shape in {filename}: {raw.shape}")
    o = raw[:, :DIM].copy()
    # The original MATLAB source overwrites the tenth optimum with zero.
    o[9, :] = 0.0
    return o


def _load_matrices(filename: str) -> tuple[np.ndarray, ...]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing SIS2005 source asset: {path}. "
            "Place the original MAT files under benchmarks/data/sis2005/."
        )
    mat = loadmat(path, squeeze_me=True, struct_as_record=False)["M"]
    matrices = []
    for i in range(1, 11):
        arr = np.asarray(getattr(mat, f"M{i}"), dtype=float)
        if arr.shape != (DIM, DIM):
            raise ValueError(f"Unexpected M{i} shape in {filename}: {arr.shape}")
        matrices.append(arr)
    return tuple(matrices)


def _identity_matrices() -> tuple[np.ndarray, ...]:
    return tuple(np.eye(DIM, dtype=float) for _ in range(10))


def _repeat_function(name: str) -> tuple[Callable[[np.ndarray], np.ndarray], ...]:
    return tuple(_BASIC[name] for _ in range(10))


@lru_cache(maxsize=None)
def _build_spec(func_num: int, variant: str) -> _CompositionSpec:
    if variant not in {"source_faithful", "paper_table4"}:
        raise ValueError("variant must be 'source_faithful' or 'paper_table4'")
    if variant == "paper_table4" and func_num != 3:
        raise ValueError("The paper_table4 diagnostic is defined only for F26/CF3.")

    bias = np.arange(10, dtype=float) * 100.0

    if func_num == 1:
        optima = _load_optima("com_func1_data.mat")
        sigma = np.ones(10)
        lamda = np.full(10, 5.0 / 100.0)
        matrices = _identity_matrices()  # source code does not load com_func1_M_D10.mat
        functions = _repeat_function("sphere")

    elif func_num == 2:
        optima = _load_optima("com_func2_data.mat")
        sigma = np.ones(10)
        lamda = np.full(10, 5.0 / 100.0)
        matrices = _load_matrices("com_func2_M_D10.mat")
        functions = _repeat_function("griewank")

    elif func_num == 3:
        optima = _load_optima("com_func3_data.mat")
        sigma = np.ones(10)
        lamda = np.ones(10)
        matrices = _load_matrices("com_func3_M_D10.mat")
        # Uploaded original source: com_func3 uses frastrigin.
        # GWO paper Table 4 prints Griewank. Keep the discrepancy explicit.
        functions = _repeat_function(
            "rastrigin" if variant == "source_faithful" else "griewank"
        )

    elif func_num == 4:
        optima = _load_optima("hybrid_func1_data.mat")
        sigma = np.ones(10)
        lamda = np.array([
            5.0 / 32.0, 5.0 / 32.0,
            1.0, 1.0,
            10.0, 10.0,
            5.0 / 100.0, 5.0 / 100.0,
            5.0 / 100.0, 5.0 / 100.0,
        ])
        matrices = _load_matrices("hybrid_func1_M_D10.mat")
        functions = tuple(_BASIC[n] for n in [
            "ackley", "ackley",
            "rastrigin", "rastrigin",
            "weierstrass", "weierstrass",
            "griewank", "griewank",
            "sphere", "sphere",
        ])

    elif func_num in {5, 6}:
        # The original source intentionally reuses hybrid_func2 data/matrices for CF6.
        optima = _load_optima("hybrid_func2_data.mat")
        base_lamda = np.array([
            1.0 / 5.0, 1.0 / 5.0,
            10.0, 10.0,
            5.0 / 100.0, 5.0 / 100.0,
            5.0 / 32.0, 5.0 / 32.0,
            5.0 / 100.0, 5.0 / 100.0,
        ])
        if func_num == 5:
            sigma = np.ones(10)
            lamda = base_lamda
        else:
            sigma = np.arange(1, 11, dtype=float) / 10.0
            lamda = base_lamda * sigma
        matrices = _load_matrices("hybrid_func2_M_D10.mat")
        functions = tuple(_BASIC[n] for n in [
            "rastrigin", "rastrigin",
            "weierstrass", "weierstrass",
            "griewank", "griewank",
            "ackley", "ackley",
            "sphere", "sphere",
        ])

    else:
        raise ValueError("func_num must be in 1..6")

    return _CompositionSpec(
        func_num=func_num,
        optima=optima,
        sigma=np.asarray(sigma, dtype=float),
        lamda=np.asarray(lamda, dtype=float),
        bias=bias,
        matrices=matrices,
        functions=functions,
    )


def _evaluate_batch(x: np.ndarray, spec: _CompositionSpec) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.ndim != 2 or arr.shape[1] != DIM:
        raise ValueError(f"Expected shape (10,) or (n,10), got {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("SIS2005 input contains non-finite values.")

    n = arr.shape[0]
    diff = arr[:, None, :] - spec.optima[None, :, :]
    sqdist = np.sum(diff * diff, axis=2)
    weights = np.exp(
        -sqdist / (2.0 * DIM * (spec.sigma[None, :] ** 2))
    )

    max_w = np.max(weights, axis=1, keepdims=True)
    is_max = weights == max_w
    weights = np.where(
        is_max,
        weights,
        weights * (1.0 - max_w ** 10),
    )
    weight_sum = np.sum(weights, axis=1, keepdims=True)
    if np.any(weight_sum == 0.0) or not np.all(np.isfinite(weight_sum)):
        raise FloatingPointError("SIS2005 composition weights could not be normalized.")
    weights = weights / weight_sum

    total = np.zeros(n, dtype=float)
    x_ref = np.full((1, DIM), 5.0, dtype=float)

    for i in range(10):
        z = ((arr - spec.optima[i]) / spec.lamda[i]) @ spec.matrices[i]
        z_ref = (x_ref / spec.lamda[i]) @ spec.matrices[i]
        f = spec.functions[i](z)
        f_ref = spec.functions[i](z_ref)[0]
        if not np.isfinite(f_ref) or f_ref == 0.0:
            raise FloatingPointError(f"Invalid height normalizer for component {i+1}: {f_ref}")
        scaled = 2000.0 * f / f_ref
        total += weights[:, i] * (scaled + spec.bias[i])

    return total


def get_sis2005_benchmark(name: str, variant: str = "source_faithful") -> SIS2005Benchmark:
    key = name.upper()
    if key not in _ALIAS_TO_NUM:
        raise ValueError(
            f"Unknown SIS2005 benchmark {name!r}. "
            "Use F24..F29 or CF1..CF6."
        )
    func_num = _ALIAS_TO_NUM[key]
    spec = _build_spec(func_num, variant)
    paper_name = _NUM_TO_PAPER[func_num]
    canonical_name = _NUM_TO_CF[func_num]

    def objective(x: np.ndarray) -> float:
        return float(_evaluate_batch(np.asarray(x, dtype=float), spec)[0])

    return SIS2005Benchmark(
        paper_name=paper_name,
        canonical_name=canonical_name,
        func_num=func_num,
        dim=DIM,
        lb=LB,
        ub=UB,
        optimum=0.0,
        paper_mean=PAPER_TABLE8[paper_name]["mean"],
        paper_std=PAPER_TABLE8[paper_name]["std"],
        variant=variant,
        objective=objective,
        optima=spec.optima.copy(),
    )


def evaluate_sis2005(name: str, x: np.ndarray, variant: str = "source_faithful") -> np.ndarray | float:
    key = name.upper()
    if key not in _ALIAS_TO_NUM:
        raise ValueError(f"Unknown SIS2005 benchmark {name!r}.")
    spec = _build_spec(_ALIAS_TO_NUM[key], variant)
    arr = np.asarray(x, dtype=float)
    out = _evaluate_batch(arr, spec)
    if arr.ndim == 1:
        return float(out[0])
    return out
