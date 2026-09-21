import numpy as np


def F1(x):
    return np.sum(x ** 2)


def F2(x):
    abs_x = np.abs(x)
    return np.sum(abs_x) + np.prod(abs_x)


def F3(x):
    cumulative_sum = np.cumsum(x)
    return np.sum(cumulative_sum ** 2)


def F4(x):
    """
    F4: Maximum absolute value
    f(x) = max(|x_i|)
    """
    return np.max(np.abs(x))


def F5(x):
    """
    F5: Rosenbrock
    """
    return np.sum(
        100.0 * (x[1:] - x[:-1] ** 2) ** 2
        + (x[:-1] - 1.0) ** 2
    )


def F6(x):
    """
    F6: Shifted Sphere
    f(x) = sum((x_i + 0.5)^2)
    """
    return np.sum((x + 0.5) ** 2)


def F7(x, rng=None):
    """
    F7: Quartic function with random noise

    f(x) = sum(i * x_i^4) + random[0, 1)

    rng:
        np.random.Generator
    """
    if rng is None:
        rng = np.random.default_rng()

    i = np.arange(1, len(x) + 1)

    noise = rng.uniform(0.0, 1.0)

    return np.sum(i * x ** 4) + noise
