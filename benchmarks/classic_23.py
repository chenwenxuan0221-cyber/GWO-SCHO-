from dataclasses import dataclass
from typing import Callable

import numpy as np

from benchmarks.basic_functions import (
    F1, F2, F3, F4, F5, F6, F7
)


def F8(x):
    return -np.sum(x * np.sin(np.sqrt(np.abs(x))))


def F9(x):
    return np.sum(x**2 - 10.0 * np.cos(2.0 * np.pi * x) + 10.0)


def F10(x):
    d = len(x)
    return (
        -20.0 * np.exp(-0.2 * np.sqrt(np.sum(x**2) / d))
        - np.exp(np.sum(np.cos(2.0 * np.pi * x)) / d)
        + 20.0
        + np.e
    )


def _U(x, a, k, m):
    x = np.asarray(x)
    return np.where(
        x > a,
        k * (x - a) ** m,
        np.where(x < -a, k * (-x - a) ** m, 0.0),
    )


def F11(x):
    x = np.asarray(x)
    i = np.arange(1, len(x) + 1)
    return np.sum(x**2) / 4000.0 - np.prod(np.cos(x / np.sqrt(i))) + 1.0


def F12(x):
    x = np.asarray(x)
    d = len(x)
    y = 1.0 + (x + 1.0) / 4.0

    term1 = 10.0 * np.sin(np.pi * y[0]) ** 2
    term2 = np.sum(
        (y[:-1] - 1.0) ** 2
        * (1.0 + 10.0 * np.sin(np.pi * y[1:]) ** 2)
    )
    term3 = (y[-1] - 1.0) ** 2

    return (
        (np.pi / d) * (term1 + term2 + term3)
        + np.sum(_U(x, 10.0, 100.0, 4.0))
    )


def F13(x):
    x = np.asarray(x)
    d = len(x)

    term1 = np.sin(3.0 * np.pi * x[0]) ** 2
    term2 = np.sum(
        (x[:-1] - 1.0) ** 2
        * (1.0 + np.sin(3.0 * np.pi * x[1:]) ** 2)
    )
    term3 = (x[-1] - 1.0) ** 2 * (
        1.0 + np.sin(2.0 * np.pi * x[-1]) ** 2
    )

    return (
        0.1 * (term1 + term2 + term3)
        + np.sum(_U(x, 5.0, 100.0, 4.0))
    )
def F14(x):
    a = np.array([
        [-32, -16,   0,  16,  32,
         -32, -16,   0,  16,  32,
         -32, -16,   0,  16,  32,
         -32, -16,   0,  16,  32,
         -32, -16,   0,  16,  32],

        [-32, -32, -32, -32, -32,
         -16, -16, -16, -16, -16,
           0,   0,   0,   0,   0,
          16,  16,  16,  16,  16,
          32,  32,  32,  32,  32]
    ], dtype=float)

    total = 0.0

    for j in range(25):
        total += 1.0 / (
            (j + 1)
            + (x[0] - a[0, j])**6
            + (x[1] - a[1, j])**6
        )

    return 1.0 / (1.0 / 500.0 + total)


def F15(x):
    a = np.array([
        0.1957,
        0.1947,
        0.1735,
        0.1600,
        0.0844,
        0.0627,
        0.0456,
        0.0342,
        0.0323,
        0.0235,
        0.0246
    ])

    b = np.array([
        4.0,
        2.0,
        1.0,
        0.5,
        0.25,
        1.0 / 6.0,
        0.125,
        0.1,
        1.0 / 12.0,
        1.0 / 14.0,
        0.0625
    ])

    numerator = x[0] * (b**2 + b * x[1])

    denominator = (
        b**2
        + b * x[2]
        + x[3]
    )

    return np.sum(
        (a - numerator / denominator) ** 2
    )


def F16(x):
    x1 = x[0]
    x2 = x[1]

    return (
        4.0 * x1**2
        - 2.1 * x1**4
        + (x1**6) / 3.0
        + x1 * x2
        - 4.0 * x2**2
        + 4.0 * x2**4
    )


def F17(x):
    x1 = x[0]
    x2 = x[1]

    return (
        (x2 - (5.1 / (4.0 * np.pi**2)) * x1**2 + (5.0 / np.pi) * x1 - 6.0) ** 2
        + 10.0 * (1.0 - 1.0 / (8.0 * np.pi)) * np.cos(x1)
        + 10.0
    )


def F18(x):
    x1 = x[0]
    x2 = x[1]

    term1 = (
        1.0
        + (x1 + x2 + 1.0) ** 2
        * (
            19.0
            - 14.0 * x1
            + 3.0 * x1**2
            - 14.0 * x2
            + 6.0 * x1 * x2
            + 3.0 * x2**2
        )
    )

    term2 = (
        30.0
        + (2.0 * x1 - 3.0 * x2) ** 2
        * (
            18.0
            - 32.0 * x1
            + 12.0 * x1**2
            + 48.0 * x2
            - 36.0 * x1 * x2
            + 27.0 * x2**2
        )
    )

    return term1 * term2


def F19(x):
    alpha = np.array([1.0, 1.2, 3.0, 3.2])

    A = np.array([
        [3.0, 10.0, 30.0],
        [0.1, 10.0, 35.0],
        [3.0, 10.0, 30.0],
        [0.1, 10.0, 35.0],
    ])

    P = 1e-4 * np.array([
        [3689, 1170, 2673],
        [4699, 4387, 7470],
        [1091, 8732, 5547],
        [381, 5743, 8828],
    ])

    total = 0.0
    for i in range(4):
        inner = np.sum(A[i] * (x - P[i]) ** 2)
        total += alpha[i] * np.exp(-inner)

    return -total


def F20(x):
    alpha = np.array([1.0, 1.2, 3.0, 3.2])

    A = np.array([
        [10.0, 3.0, 17.0, 3.5, 1.7, 8.0],
        [0.05, 10.0, 17.0, 0.1, 8.0, 14.0],
        [3.0, 3.5, 1.7, 10.0, 17.0, 8.0],
        [17.0, 8.0, 0.05, 10.0, 0.1, 14.0],
    ])

    P = 1e-4 * np.array([
        [1312, 1696, 5569, 124, 8283, 5886],
        [2329, 4135, 8307, 3736, 1004, 9991],
        [2348, 1451, 3522, 2883, 3047, 6650],
        [4047, 8828, 8732, 5743, 1091, 381],
    ])

    total = 0.0
    for i in range(4):
        inner = np.sum(A[i] * (x - P[i]) ** 2)
        total += alpha[i] * np.exp(-inner)

    return -total


def _shekel(x, m):
    a = np.array([
        [4.0, 4.0, 4.0, 4.0],
        [1.0, 1.0, 1.0, 1.0],
        [8.0, 8.0, 8.0, 8.0],
        [6.0, 6.0, 6.0, 6.0],
        [3.0, 7.0, 3.0, 7.0],
        [2.0, 9.0, 2.0, 9.0],
        [5.0, 5.0, 3.0, 3.0],
        [8.0, 1.0, 8.0, 1.0],
        [6.0, 2.0, 6.0, 2.0],
        [7.0, 3.6, 7.0, 3.6],
    ])

    c = np.array([0.1, 0.2, 0.2, 0.4, 0.4, 0.6, 0.3, 0.7, 0.5, 0.5])

    total = 0.0
    for i in range(m):
        total += 1.0 / (np.sum((x - a[i]) ** 2) + c[i])

    return -total


def F21(x):
    return _shekel(x, 5)


def F22(x):
    return _shekel(x, 7)


def F23(x):
    return _shekel(x, 10)

@dataclass
class Benchmark:
    name: str
    func: Callable
    dim: int
    lb: float
    ub: float
    optimum: float
    stochastic: bool = False

    def make_objective(self, seed=None):
        """
        返回可以直接传给 GWO 的 obj_func(x)。
        """

        if not self.stochastic:
            return self.func

        rng = np.random.default_rng(seed)

        def objective(x):
            return self.func(x, rng)

        return objective


BENCHMARKS = {

    "F1": Benchmark(
        name="F1",
        func=F1,
        dim=30,
        lb=-100,
        ub=100,
        optimum=0.0,
    ),

    "F2": Benchmark(
        name="F2",
        func=F2,
        dim=30,
        lb=-10,
        ub=10,
        optimum=0.0,
    ),

    "F3": Benchmark(
        name="F3",
        func=F3,
        dim=30,
        lb=-100,
        ub=100,
        optimum=0.0,
    ),

    "F4": Benchmark(
        name="F4",
        func=F4,
        dim=30,
        lb=-100,
        ub=100,
        optimum=0.0,
    ),

    "F5": Benchmark(
        name="F5",
        func=F5,
        dim=30,
        lb=-30,
        ub=30,
        optimum=0.0,
    ),

    "F6": Benchmark(
        name="F6",
        func=F6,
        dim=30,
        lb=-100,
        ub=100,
        optimum=0.0,
    ),

    "F7": Benchmark(
        name="F7",
        func=F7,
        dim=30,
        lb=-1.28,
        ub=1.28,
        optimum=0.0,
        stochastic=True,
    ),

    "F8": Benchmark(
        name="F8",
        func=F8,
        dim=30,
        lb=-500,
        ub=500,
        optimum=-418.9829 * 30,
    ),

    "F9": Benchmark(
        name="F9",
        func=F9,
        dim=30,
        lb=-5.12,
        ub=5.12,
        optimum=0.0,
    ),

    "F10": Benchmark(
        name="F10",
        func=F10,
        dim=30,
        lb=-32,
        ub=32,
        optimum=0.0,
    ),

    "F11": Benchmark(
        name="F11",
        func=F11,
        dim=30,
        lb=-600,
        ub=600,
        optimum=0.0,
    ),

    "F12": Benchmark(
        name="F12",
        func=F12,
        dim=30,
        lb=-50,
        ub=50,
        optimum=0.0,
    ),

    "F13": Benchmark(
        name="F13",
        func=F13,
        dim=30,
        lb=-50,
        ub=50,
        optimum=0.0,
    ),

    "F14": Benchmark(
        name="F14",
        func=F14,
        dim=2,
        lb=-65.536,
        ub=65.536,
        optimum=1.0,
    ),

    "F15": Benchmark(
        name="F15",
        func=F15,
        dim=4,
        lb=-5.0,
        ub=5.0,
        optimum=0.00030,
    ),

    "F16": Benchmark(
        name="F16",
        func=F16,
        dim=2,
        lb=-5.0,
        ub=5.0,
        optimum=-1.0316,
    ),

    "F17": Benchmark(
        name="F17",
        func=F17,
        dim=2,
        lb=np.array([-5.0, 0.0]),
        ub=np.array([10.0, 15.0]),
        optimum=0.397887,
    ),

    "F18": Benchmark(
        name="F18",
        func=F18,
        dim=2,
        lb=-2.0,
        ub=2.0,
        optimum=3.0,
    ),

    "F19": Benchmark(
        name="F19",
        func=F19,
        dim=3,
        lb=0.0,
        ub=1.0,
        optimum=-3.8628,
    ),

    "F20": Benchmark(
        name="F20",
        func=F20,
        dim=6,
        lb=0.0,
        ub=1.0,
        optimum=-3.322,
    ),

    "F21": Benchmark(
        name="F21",
        func=F21,
        dim=4,
        lb=0.0,
        ub=10.0,
        optimum=-10.1532,
    ),

    "F22": Benchmark(
        name="F22",
        func=F22,
        dim=4,
        lb=0.0,
        ub=10.0,
        optimum=-10.4028,
    ),

    "F23": Benchmark(
        name="F23",
        func=F23,
        dim=4,
        lb=0.0,
        ub=10.0,
        optimum=-10.5363,
    ),

}


def get_benchmark(name: str) -> Benchmark:

    if name not in BENCHMARKS:
        raise ValueError(
            f"Unknown benchmark: {name}. "
            f"Available: {list(BENCHMARKS.keys())}"
        )

    return BENCHMARKS[name]