"""H4h structural validation for controlled SCHO Fig.7 Variants 1-11."""

from __future__ import annotations

import numpy as np

from algorithms.scho import scho
from benchmarks.classic_23 import get_benchmark
from experiments.scho_fig7_variants_h4 import (
    FIG7_VARIANTS,
    _COSH1,
    _SINH1,
    _A_whole_linear_schedule,
    _A_whole_sincos_schedule,
    _linear_pair,
    _sincos_pair,
    scho_fig7_variant,
)


ANCHORS = ("F2", "F7", "F15", "F21")
CONTROLLED = tuple(v for v in FIG7_VARIANTS if v != "SCHO")
N = 6
MAX_ITER = 40
OPTIMIZER_SEED = 1000
OBJECTIVE_SEED_BASE = 2_024_000


def _objective_seed(name):
    return OBJECTIVE_SEED_BASE + int(name[1:])


def _new_objective(name):
    b = get_benchmark(name)
    return b, b.make_objective(seed=_objective_seed(name))


def _validate_result(name, b, score, pos, curve):
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    assert np.isfinite(score), f"{name}: non-finite score"
    assert pos.shape == (b.dim,), f"{name}: wrong position shape"
    assert curve.shape == (MAX_ITER,), f"{name}: wrong curve shape"
    assert np.all(np.isfinite(pos)), f"{name}: position NaN/Inf"
    assert np.all(np.isfinite(curve)), f"{name}: curve NaN/Inf"
    assert score == float(curve[-1]), f"{name}: score != curve[-1]"
    assert np.all(np.diff(curve) <= 0.0), f"{name}: best curve increased"


def _test_range_matching():
    for x, expected_s, expected_c in [
        (0.0, 0.0, 1.0),
        (1.0, _SINH1, _COSH1),
    ]:
        s, c = _sincos_pair(x)
        assert np.isclose(s, expected_s, rtol=0.0, atol=1e-14)
        assert np.isclose(c, expected_c, rtol=0.0, atol=1e-14)

        s, c = _linear_pair(x)
        assert np.isclose(s, expected_s, rtol=0.0, atol=1e-14)
        assert np.isclose(c, expected_c, rtol=0.0, atol=1e-14)

    grid = np.linspace(0.0, 1.0, 101)
    for fn in (_sincos_pair, _linear_pair):
        vals = np.asarray([fn(float(x)) for x in grid])
        assert np.all(vals[:, 0] >= -1e-14)
        assert np.all(vals[:, 0] <= _SINH1 + 1e-14)
        assert np.all(vals[:, 1] >= 1.0 - 1e-14)
        assert np.all(vals[:, 1] <= _COSH1 + 1e-14)
        assert np.all(np.diff(vals[:, 0]) >= -1e-14)
        assert np.all(np.diff(vals[:, 1]) >= -1e-14)

    # Whole switching substitutes keep deterministic envelope endpoints 10 -> 1.
    assert np.isclose(_A_whole_sincos_schedule(0.0, 1.0), 10.0)
    assert np.isclose(_A_whole_sincos_schedule(1.0, 1.0), 1.0)
    assert np.isclose(_A_whole_linear_schedule(0.0, 1.0), 10.0)
    assert np.isclose(_A_whole_linear_schedule(1.0, 1.0), 1.0)


def main():
    print("=" * 128)
    print("H4h - SCHO Fig.7 controlled Variant 1-11 structural audit")
    print("=" * 128)
    print(
        f"Anchors: {','.join(ANCHORS)} | N={N} | MaxIter={MAX_ITER} "
        f"| optimizer seed={OPTIMIZER_SEED}"
    )
    print("No formal 7590-run Fig.7 experiment will be executed.")
    print("Frozen algorithms/scho.py will NOT be modified.")
    print("=" * 128)

    print("\n1) Controlled replacement-function endpoint/range audit")
    _test_range_matching()
    print("Range matching / switching endpoints PASS")

    print("\n2) Full SCHO exact-equivalence control")
    control_curves = {}

    for name in ANCHORS:
        b, obj_a = _new_objective(name)
        frozen = scho(
            obj_func=obj_a,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=OPTIMIZER_SEED,
        )

        _, obj_b = _new_objective(name)
        wrapped = scho_fig7_variant(
            obj_func=obj_b,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            variant="SCHO",
            seed=OPTIMIZER_SEED,
        )

        assert frozen[0] == wrapped[0], f"{name}: score mismatch"
        assert np.array_equal(frozen[1], wrapped[1]), f"{name}: pos mismatch"
        assert np.array_equal(frozen[2], wrapped[2]), f"{name}: curve mismatch"

        control_curves[name] = np.asarray(wrapped[2], dtype=float)
        print(
            f"{name:<4} D={b.dim:<2} best={wrapped[0]:>14.8g} "
            "score/pos/curve EXACT"
        )

    print("\n3) Eleven controlled variants: determinism + structure")
    signatures = {}
    total_special_hits = {}

    for variant in CONTROLLED:
        variant_signature = []
        special_hits = 0

        for name in ANCHORS:
            b, obj1 = _new_objective(name)
            run1 = scho_fig7_variant(
                obj_func=obj1,
                dim=b.dim,
                lb=b.lb,
                ub=b.ub,
                N=N,
                MaxIter=MAX_ITER,
                variant=variant,
                seed=OPTIMIZER_SEED,
                return_diagnostics=True,
            )

            _, obj2 = _new_objective(name)
            run2 = scho_fig7_variant(
                obj_func=obj2,
                dim=b.dim,
                lb=b.lb,
                ub=b.ub,
                N=N,
                MaxIter=MAX_ITER,
                variant=variant,
                seed=OPTIMIZER_SEED,
                return_diagnostics=True,
            )

            score1, pos1, curve1, diag1 = run1
            score2, pos2, curve2, diag2 = run2

            _validate_result(f"{variant}/{name}", b, score1, pos1, curve1)

            assert score1 == score2, f"{variant}/{name}: score not deterministic"
            assert np.array_equal(pos1, pos2), f"{variant}/{name}: pos not deterministic"
            assert np.array_equal(curve1, curve2), f"{variant}/{name}: curve not deterministic"
            assert diag1 == diag2, f"{variant}/{name}: diagnostics not deterministic"

            expected_updates = (MAX_ITER - 1) * N * b.dim
            assert diag1["coordinate_updates"] == expected_updates
            branch_sum = (
                diag1["first_exploration"]
                + diag1["first_exploitation"]
                + diag1["second_exploration"]
                + diag1["second_exploitation"]
            )
            assert branch_sum == expected_updates

            if variant == "V1":
                special = diag1["v1_second_exploitation_replaced"]
            elif variant == "V2":
                special = diag1["v2_second_exploitation_noop"]
            elif variant in {"V3", "V5"}:
                special = diag1["v3_v5_eq12_alt"]
            elif variant in {"V4", "V6"}:
                special = diag1["v4_v6_eq5_alt"]
            else:
                special = diag1["v7_v8_v9_v10_v11_switch_alt"]

            special_hits += special
            variant_signature.append(float(score1))

        assert special_hits > 0, f"{variant}: controlled change never exercised"
        total_special_hits[variant] = special_hits
        signatures[variant] = tuple(variant_signature)

        print(
            f"{variant:<4} PASS | special_hits={special_hits:<7} "
            f"| anchor bests={[f'{x:.5g}' for x in variant_signature]}"
        )

    # Every controlled variant must differ from full SCHO on at least one anchor.
    for variant in CONTROLLED:
        differs = False
        for name, score in zip(ANCHORS, signatures[variant]):
            b, obj = _new_objective(name)
            control = scho_fig7_variant(
                obj_func=obj,
                dim=b.dim,
                lb=b.lb,
                ub=b.ub,
                N=N,
                MaxIter=MAX_ITER,
                variant="SCHO",
                seed=OPTIMIZER_SEED,
            )
            if (
                score != control[0]
                or not np.array_equal(
                    control_curves[name],
                    np.asarray(control[2], dtype=float),
                )
            ):
                # The curve comparison above is intentionally against the
                # exact control cache. Score inequality is sufficient in most
                # cases; below we also compare controlled curve separately.
                pass

            _, objv = _new_objective(name)
            variant_run = scho_fig7_variant(
                obj_func=objv,
                dim=b.dim,
                lb=b.lb,
                ub=b.ub,
                N=N,
                MaxIter=MAX_ITER,
                variant=variant,
                seed=OPTIMIZER_SEED,
            )
            if not np.array_equal(
                np.asarray(variant_run[2], dtype=float),
                control_curves[name],
            ):
                differs = True
                break

        assert differs, f"{variant}: no trajectory difference from SCHO on anchors"

    print("\n4) Guard audit")
    b, obj = _new_objective("F2")
    try:
        scho_fig7_variant(
            obj_func=obj,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            variant="V99",
            seed=OPTIMIZER_SEED,
        )
    except ValueError:
        print("Unknown variant rejected PASS")
    else:
        raise AssertionError("Unknown variant was not rejected")

    print("-" * 128)
    print("H4h RESULT: PASS")
    print("Full SCHO control is exactly equal to frozen algorithms/scho.py.")
    print("All 11 controlled Fig.7 variants are deterministic and their intended branches are exercised.")
    print("Exactness label: CONTROLLED-INTERPRETATION, not recovered author source.")
    print("Next: H4i decide/formalize the 7590-run Fig.7 experiment.")
    print("=" * 128)


if __name__ == "__main__":
    main()
