"""C9: first acceptance test for the source-faithful SCHO on F1 (Sphere)."""

import numpy as np

from algorithms.scho import scho


def F1(x):
    """Official classical F1 / Sphere: sum(x_i^2)."""
    x = np.asarray(x, dtype=float)
    return np.sum(x ** 2)


def main():
    best_score, best_pos, curve = scho(
        obj_func=F1,
        dim=30,
        lb=-100.0,
        ub=100.0,
        N=30,
        MaxIter=500,
        seed=1000,
    )

    print("=" * 60)
    print("C9 - Source-faithful SCHO on F1")
    print("=" * 60)
    print(f"Best score : {best_score:.16e}")
    print(f"||best_pos||: {np.linalg.norm(best_pos):.16e}")
    print(f"Curve shape: {curve.shape}")
    print(f"Curve[0]   : {curve[0]:.16e}")
    print(f"Curve[-1]  : {curve[-1]:.16e}")

    assert curve.shape == (500,)
    assert np.all(np.isfinite(curve))
    assert np.isfinite(best_score)
    assert np.all(np.isfinite(best_pos))

    # Destination_fitness is historical best, so the curve must never increase.
    assert np.all(np.diff(curve) <= 1e-15), (
        "Historical-best convergence curve should be non-increasing."
    )

    # F1 optimum is 0; this is a basic sanity check, not a paper-table match.
    assert best_score >= 0.0
    assert best_score <= curve[0]

    print("\nPASS: C9 structural acceptance checks succeeded.")


if __name__ == "__main__":
    main()
