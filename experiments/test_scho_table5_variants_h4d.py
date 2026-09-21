"""H4d - Structural validation of the five paper Table-5 SCHO variants.

This is a smoke/equivalence stage only.  It does NOT run the formal
6 algorithms x 23 functions x 30 runs Table-5 experiment.
"""

from __future__ import annotations

import numpy as np

from algorithms.scho import scho
from benchmarks.classic_23 import get_benchmark
from experiments.scho_table5_variants_h4 import (
    TABLE5_VARIANTS,
    scho_table5_variant,
)


BASELINE_ANCHORS = ["F2", "F7", "F15", "F21"]
SMOKE_ANCHORS = ["F2", "F7", "F15", "F21"]

N = 6
MAX_ITER = 40
OPTIMIZER_SEED = 1000


def _objective_seed(name: str) -> int:
    return 4_024_000 + int(name[1:])


def _validate_result(name, variant, b, score, pos, curve):
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    assert np.isfinite(score), f"{variant} {name}: non-finite score"
    assert pos.shape == (b.dim,), f"{variant} {name}: position shape mismatch"
    assert np.all(np.isfinite(pos)), f"{variant} {name}: position NaN/Inf"
    assert curve.shape == (MAX_ITER,), f"{variant} {name}: curve shape mismatch"
    assert np.all(np.isfinite(curve)), f"{variant} {name}: curve NaN/Inf"
    assert score == float(curve[-1]), f"{variant} {name}: score != curve[-1]"
    assert not np.any(np.diff(curve) > 0.0), (
        f"{variant} {name}: historical best increased"
    )


def _assert_structure(variant, diagnostics):
    exp = diagnostics["exploration_updates"]
    exploit = diagnostics["exploitation_updates"]
    switch = diagnostics["switching_draws"]
    bounded = diagnostics["bounded_redistributions"]

    if variant == "SCHO":
        assert exp > 0 and exploit > 0
        assert switch > 0
        assert bounded > 0
    elif variant == "SCHO_NT":
        assert exp > 0 and exploit > 0
        assert switch > 0
        assert bounded == 0
    elif variant == "SCHO_NSTF":
        assert exp > 0 and exploit == 0
        assert switch == 0
        assert bounded == 0
    elif variant == "SCHO_NFTF":
        assert exp == 0 and exploit > 0
        assert switch == 0
        assert bounded == 0
    elif variant == "SCHO_NSF":
        assert exp > 0 and exploit == 0
        assert switch == 0
        assert bounded > 0
    elif variant == "SCHO_NFF":
        assert exp == 0 and exploit > 0
        assert switch == 0
        assert bounded > 0
    else:
        raise AssertionError(f"Unhandled variant {variant}")


def main():
    print("=" * 124)
    print("H4d - SCHO Table-5 structural variant implementation audit")
    print("=" * 124)
    print(
        f"Smoke protocol: anchors={','.join(SMOKE_ANCHORS)} | "
        f"N={N} | MaxIter={MAX_ITER} | optimizer seed={OPTIMIZER_SEED}"
    )
    print("No formal 30-run Table-5 experiment will be executed.")
    print("Frozen algorithms/scho.py will NOT be modified.")
    print("=" * 124)

    print("\n1) Full-SCHO exact-equivalence control")
    print("-" * 124)
    for name in BASELINE_ANCHORS:
        b = get_benchmark(name)
        obj_seed = _objective_seed(name)

        ref_obj = b.make_objective(seed=obj_seed)
        var_obj = b.make_objective(seed=obj_seed)

        ref_score, ref_pos, ref_curve = scho(
            obj_func=ref_obj,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=OPTIMIZER_SEED,
        )
        score, pos, curve, diag = scho_table5_variant(
            obj_func=var_obj,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            variant="SCHO",
            seed=OPTIMIZER_SEED,
            return_diagnostics=True,
        )

        assert ref_score == score, f"{name}: SCHO score is not exact"
        assert np.array_equal(ref_pos, pos), f"{name}: SCHO position is not exact"
        assert np.array_equal(ref_curve, curve), f"{name}: SCHO curve is not exact"
        _assert_structure("SCHO", diag)

        print(
            f"{name:<4} D={b.dim:<2} best={score:>14.8g} "
            "score/pos/curve EXACT"
        )

    print("\n2) Five Table-5 variants: reproducibility + structural branch audit")
    print("-" * 124)

    for variant in TABLE5_VARIANTS[1:]:
        first_diag = None
        scores = []

        for name in SMOKE_ANCHORS:
            b = get_benchmark(name)
            obj_seed = _objective_seed(name)

            obj1 = b.make_objective(seed=obj_seed)
            obj2 = b.make_objective(seed=obj_seed)

            score1, pos1, curve1, diag1 = scho_table5_variant(
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
            score2, pos2, curve2, diag2 = scho_table5_variant(
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

            _validate_result(name, variant, b, score1, pos1, curve1)
            assert score1 == score2, f"{variant} {name}: score not reproducible"
            assert np.array_equal(pos1, pos2), (
                f"{variant} {name}: position not reproducible"
            )
            assert np.array_equal(curve1, curve2), (
                f"{variant} {name}: curve not reproducible"
            )
            assert diag1 == diag2, f"{variant} {name}: diagnostics not reproducible"
            _assert_structure(variant, diag1)

            if first_diag is None:
                first_diag = diag1
            scores.append(score1)

        print(
            f"{variant:<11} PASS | "
            f"explore={first_diag['exploration_updates']:<6} "
            f"exploit={first_diag['exploitation_updates']:<6} "
            f"switch={first_diag['switching_draws']:<6} "
            f"bounded={first_diag['bounded_redistributions']:<4} | "
            f"anchor bests={[f'{x:.4g}' for x in scores]}"
        )

    print("\n3) Guard audit")
    print("-" * 124)
    b = get_benchmark("F2")
    try:
        scho_table5_variant(
            obj_func=b.make_objective(seed=1),
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            variant="NOT_A_VARIANT",
            seed=OPTIMIZER_SEED,
        )
    except ValueError:
        print("Unknown variant rejected PASS")
    else:
        raise AssertionError("Unknown variant was not rejected")

    print("-" * 124)
    print("H4d RESULT: PASS")
    print("Full SCHO control is exactly equal to frozen algorithms/scho.py.")
    print("All five paper-described structural variants are deterministic and structurally distinct.")
    print("Next: H4e formal Table-5 ablation (6 models x 23 functions x 30 runs = 4140 runs).")


if __name__ == "__main__":
    main()
