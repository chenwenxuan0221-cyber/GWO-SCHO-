"""E1 - CEC 2014 evaluator structural and numerical consistency audit.

Place at:
    experiments/test_cec2014_e1.py

Run from project root:
    python -m experiments.test_cec2014_e1

This test DOES NOT run GWO or SCHO.

Compatibility note
------------------
MinionPy 1.6.1 exposes CEC2014Functions in the Python API, but does not
expose the C++-side combined CEC20142017Functions wrapper through
minionpy.cec. Therefore this audit validates the Python CEC2014 backend
directly, including batch-vs-scalar consistency.
"""

from __future__ import annotations

import importlib.metadata

import numpy as np

from benchmarks.cec2014 import (
    DIM,
    LB,
    UB,
    all_benchmarks,
)

try:
    from minionpy.cec import CEC2014Functions
except ImportError as exc:
    raise ImportError(
        "Install the frozen E1 backend first:\n"
        "    python -m pip install minionpy==1.6.1"
    ) from exc


EXPECTED_FAMILY = {
    **{i: "unimodal" for i in range(1, 4)},
    **{i: "simple_multimodal" for i in range(4, 17)},
    **{i: "hybrid" for i in range(17, 23)},
    **{i: "composition" for i in range(23, 31)},
}


def _check_bounds_metadata(backend):
    """
    Best-effort verification of backend bounds metadata.

    MinionPy versions may expose no bounds metadata at all; the Stage-E
    adapter itself freezes the CEC2014 search range to [-100, 100]^10.
    """
    getter = getattr(backend, "get_bounds", None)
    if getter is None:
        return "not exposed"

    raw = getter()

    try:
        arr = np.asarray(raw, dtype=float)
    except Exception:
        return f"unparsed: {type(raw).__name__}"

    if arr.shape == (2,):
        assert np.allclose(arr, [LB, UB])
        return "verified"

    if arr.shape == (DIM, 2):
        assert np.allclose(arr[:, 0], LB)
        assert np.allclose(arr[:, 1], UB)
        return "verified"

    if arr.shape == (2, DIM):
        assert np.allclose(arr[0], LB)
        assert np.allclose(arr[1], UB)
        return "verified"

    return f"unrecognized shape {arr.shape}"


def main():
    try:
        version = importlib.metadata.version("minionpy")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"

    print("=" * 96)
    print("E1 - CEC 2014 evaluator audit")
    print("=" * 96)
    print(f"Backend             : minionpy {version}")
    print(f"Dimension           : {DIM}")
    print(f"Bounds              : [{LB}, {UB}]^{DIM}")
    print("Functions           : F1-F30")
    print("Expected f_opt(Fi)  : 100 * i")
    print("=" * 96)

    benchmarks = all_benchmarks()
    assert len(benchmarks) == 30

    # Fixed points used only for deterministic evaluator checks.
    x_zero = np.zeros(DIM, dtype=float)
    x_probe = np.linspace(-80.0, 80.0, DIM, dtype=float)
    x_probe_2 = np.linspace(75.0, -75.0, DIM, dtype=float)

    rows = []

    for b in benchmarks:
        i = b.func_num

        # ---- Adapter metadata checks ----
        assert b.name == f"F{i}"
        assert b.dim == DIM
        assert b.lb == LB
        assert b.ub == UB
        assert b.family == EXPECTED_FAMILY[i]
        assert b.optimum == float(100 * i)

        # ---- Backend optimum metadata check, if exposed ----
        backend_f_opt = b.backend_f_opt()
        assert backend_f_opt == b.optimum, (
            f"{b.name}: backend f_opt={backend_f_opt}, "
            f"expected={b.optimum}"
        )

        bounds_status = _check_bounds_metadata(b._backend)

        # ---- Scalar wrapper deterministic checks ----
        objective = b.make_objective()

        f_zero_1 = objective(x_zero)
        f_zero_2 = objective(x_zero.copy())
        f_probe_1 = objective(x_probe)
        f_probe_2 = objective(x_probe.copy())

        assert np.isfinite(f_zero_1)
        assert np.isfinite(f_probe_1)
        assert f_zero_1 == f_zero_2
        assert f_probe_1 == f_probe_2

        # ---- Direct backend batch check ----
        direct = CEC2014Functions(i, DIM)
        batch_points = [
            x_zero.tolist(),
            x_probe.tolist(),
            x_probe_2.tolist(),
        ]
        batch_vals = np.asarray(direct(batch_points), dtype=float)

        assert batch_vals.shape == (3,)
        assert np.all(np.isfinite(batch_vals))

        # The wrapper's scalar objective must match the direct CEC2014
        # Python backend exactly at identical points.
        assert f_zero_1 == batch_vals[0]
        assert f_probe_1 == batch_vals[1]

        # Batch evaluation and separate one-point evaluations must agree.
        separate_vals = np.asarray(
            [
                direct([x_zero.tolist()])[0],
                direct([x_probe.tolist()])[0],
                direct([x_probe_2.tolist()])[0],
            ],
            dtype=float,
        )
        assert np.array_equal(batch_vals, separate_vals), (
            f"{b.name}: batch and scalar backend evaluations disagree"
        )

        rows.append(
            (
                b.name,
                b.family,
                b.optimum,
                f_zero_1,
                f_probe_1,
                bounds_status,
            )
        )

    print(
        f"{'Func':<6}"
        f"{'Family':<20}"
        f"{'f_opt':>12}"
        f"{'f(0)':>18}"
        f"{'f(probe)':>18}"
        f"{'Bounds metadata':>20}"
    )
    print("-" * 96)

    for name, family, optimum, f0, fp, bounds_status in rows:
        print(
            f"{name:<6}"
            f"{family:<20}"
            f"{optimum:>12.1f}"
            f"{f0:>18.8e}"
            f"{fp:>18.8e}"
            f"{bounds_status:>20}"
        )

    print("-" * 96)
    print("PASS checks:")
    print("  1) F1-F30 all instantiate at D=10")
    print("  2) adapter bounds are [-100, 100]^10")
    print("  3) f_opt(Fi) = 100*i and agrees with backend metadata/fallback")
    print("  4) all probe evaluations are finite and deterministic")
    print("  5) direct CEC2014 batch and one-point evaluations agree exactly")
    print("  6) wrapper scalar objective agrees exactly with CEC2014 backend")
    print()
    print("E1 RESULT: PASS")
    print("No GWO/SCHO optimization was executed.")


if __name__ == "__main__":
    main()
