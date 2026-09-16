"""CEC 2014 benchmark adapter used by Stage E.

Backend
-------
MinionPy's CEC2014Functions wrapper is used only as the benchmark evaluator.
Its C++ implementation is directly adapted from the original CEC source.

Stage-E paper-reproduction protocol:
    dimension = 10
    bounds    = [-100, 100]^10
    f_opt(Fi) = 100 * i

This module intentionally does NOT contain GWO/SCHO logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

try:
    from minionpy.cec import CEC2014Functions
except ImportError as exc:
    raise ImportError(
        "CEC2014 backend is not installed. Run:\n"
        "    python -m pip install minionpy==1.6.1"
    ) from exc


DIM = 10
LB = -100.0
UB = 100.0


DESCRIPTIONS = {
    1: "Rotated High Conditioned Elliptic Function",
    2: "Rotated Bent Cigar Function",
    3: "Rotated Discus Function",
    4: "Shifted and Rotated Rosenbrock's Function",
    5: "Shifted and Rotated Ackley's Function",
    6: "Shifted and Rotated Weierstrass Function",
    7: "Shifted and Rotated Griewank's Function",
    8: "Shifted Rastrigin's Function",
    9: "Shifted and Rotated Rastrigin's Function",
    10: "Shifted Schwefel's Function",
    11: "Shifted and Rotated Schwefel's Function",
    12: "Shifted and Rotated Katsuura Function",
    13: "Shifted and Rotated HappyCat Function",
    14: "Shifted and Rotated HGBat Function",
    15: "Shifted and Rotated Expanded Griewank plus Rosenbrock Function",
    16: "Shifted and Rotated Expanded Scaffer's F6 Function",
    17: "Hybrid Function 1 (N=3)",
    18: "Hybrid Function 2 (N=3)",
    19: "Hybrid Function 3 (N=4)",
    20: "Hybrid Function 4 (N=4)",
    21: "Hybrid Function 5 (N=5)",
    22: "Hybrid Function 6 (N=5)",
    23: "Composition Function 1 (N=5)",
    24: "Composition Function 2 (N=3)",
    25: "Composition Function 3 (N=3)",
    26: "Composition Function 4 (N=5)",
    27: "Composition Function 5 (N=5)",
    28: "Composition Function 6 (N=5)",
    29: "Composition Function 7 (N=3)",
    30: "Composition Function 8 (N=3)",
}


def _family(func_num: int) -> str:
    if 1 <= func_num <= 3:
        return "unimodal"
    if 4 <= func_num <= 16:
        return "simple_multimodal"
    if 17 <= func_num <= 22:
        return "hybrid"
    if 23 <= func_num <= 30:
        return "composition"
    raise ValueError(f"CEC2014 function number must be 1..30, got {func_num}")


@dataclass
class CEC2014Benchmark:
    name: str
    func_num: int
    dim: int = DIM
    lb: float = LB
    ub: float = UB

    def __post_init__(self):
        if not 1 <= self.func_num <= 30:
            raise ValueError("func_num must be in 1..30")
        if self.dim != 10:
            raise ValueError(
                "Stage E paper reproduction is frozen to D=10. "
                f"Received dim={self.dim}."
            )
        self.optimum = float(100 * self.func_num)
        self.family = _family(self.func_num)
        self.description = DESCRIPTIONS[self.func_num]
        self._backend = CEC2014Functions(self.func_num, self.dim)

    def make_objective(self, seed=None) -> Callable[[np.ndarray], float]:
        """Return deterministic scalar objective; seed is accepted for API parity."""
        del seed

        backend = self._backend
        dim = self.dim

        def objective(x: np.ndarray) -> float:
            arr = np.asarray(x, dtype=float)

            if arr.shape != (dim,):
                raise ValueError(
                    f"{self.name} expects shape ({dim},), got {arr.shape}"
                )
            if not np.all(np.isfinite(arr)):
                raise ValueError(f"{self.name} received NaN/Inf")

            # MinionPy CEC evaluator accepts a batch: list[list[float]].
            value = backend([arr.tolist()])[0]
            return float(value)

        return objective

    def backend_f_opt(self) -> float:
        """Return backend metadata for the known global optimum value."""
        getter = getattr(self._backend, "get_f_opt", None)
        if getter is None:
            return self.optimum
        return float(getter())


def get_benchmark(name: str) -> CEC2014Benchmark:
    name = str(name).upper().strip()
    if not name.startswith("F"):
        raise KeyError(f"Unknown CEC2014 benchmark: {name!r}")

    try:
        func_num = int(name[1:])
    except ValueError as exc:
        raise KeyError(f"Unknown CEC2014 benchmark: {name!r}") from exc

    if not 1 <= func_num <= 30:
        raise KeyError(f"Unknown CEC2014 benchmark: {name!r}")

    return CEC2014Benchmark(name=f"F{func_num}", func_num=func_num)


def all_benchmarks():
    return [get_benchmark(f"F{i}") for i in range(1, 31)]
