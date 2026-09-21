"""H1b/c deterministic audit for GWO-paper SIS2005 CF1-CF6.

No optimizer is run here.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy.io import loadmat

from benchmarks.gwo_sis2005 import DATA_DIR, evaluate_sis2005, get_sis2005_benchmark


EXPECTED_SHA256 = {
    "com_func1_M_D10.mat": "532d268d02cfbdd6bfcf27ce49df854929712571ec4162b70f6346a624edeab4",
    "com_func1_data.mat": "f75a242eb36fc3a5ca988ac0755803cdb2b8a6a6a67911a810b53c3f352d4383",
    "com_func2_M_D10.mat": "dd60d66949b5360a7405ec7cbfcc857013cea43ebe420de9cd64ece715f9b61e",
    "com_func2_data.mat": "db0c4d6a8f65698342a194101ef43816b6184d8502f18d2e80687d1fa5bb31af",
    "com_func3_M_D10.mat": "64989f88cdcd54913a91ec5e4a33ecaeaa7185a59f2092083815c56ae22aa17f",
    "com_func3_data.mat": "375c3d4a32835e6d8aefb6f9e63914805615464d623424b4e7946e9b04fbb944",
    "hybrid_func1_M_D10.mat": "dbe481056ab04a2f3428146537f7e5566355fb1c5ee39725f20a4d180384ecc2",
    "hybrid_func1_data.mat": "4a27044fb507f19ba0d5b32ba997c0950e179ba08a345cbe7c3be5113d9ee692",
    "hybrid_func2_M_D10.mat": "063706d0c1ffa66ff8b98363a759dde284ea7f89c491cf4157d1bae8d3357c13",
    "hybrid_func2_data.mat": "37f73dff680159b697af9529aae42c34bfe092f3612e03457ce4d62f3213bf8a",
    "SIS_novel_func.m": "4862560f81a857181e02e20c620797bff01845f3068b991b5075e667663e746c",
    "SOURCE_README.txt": "6839bad08ae9292db604128fe9d28461b03da3d740d1ba1710dfc122b2ac65f5",
}

EXPECTED_FIXED = {
    "F24": {"zero": 900.0, "ones": 847.3853976649203},
    "F25": {"zero": 900.0, "ones": 934.8514648058881},
    "F26": {"zero": 900.0, "ones": 1619.653851983732},
    "F27": {"zero": 900.0, "ones": 1251.530969633085},
    "F28": {"zero": 900.0, "ones": 1389.957918991629},
    "F29": {"zero": 900.0, "ones": 1164.557457236172},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_close(a, b, *, atol=1e-10, rtol=1e-12, label=""):
    if not np.isclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{label}: {a} != {b}")


def load_matrix_condition_numbers(filename: str):
    obj = loadmat(DATA_DIR / filename, squeeze_me=True, struct_as_record=False)["M"]
    out = []
    for i in range(1, 11):
        m = np.asarray(getattr(obj, f"M{i}"), dtype=float)
        if m.shape != (10, 10) or not np.all(np.isfinite(m)):
            raise AssertionError(f"{filename}: invalid M{i}")
        out.append(float(np.linalg.cond(m)))
    return np.array(out)


def main():
    print("=" * 124)
    print("H1b/c - GWO SIS2005 CF1-CF6 source assets + deterministic benchmark audit")
    print("=" * 124)
    print("No optimizer will be executed.")
    print("Primary definition: uploaded original SIS_novel_func.m + D10 MAT assets")
    print("=" * 124)

    print("\nSource asset audit")
    print("-" * 124)
    passed_assets = 0
    for filename, expected in EXPECTED_SHA256.items():
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(path)
        actual = sha256(path)
        ok = actual == expected
        print(f"{filename:<28} SHA256={'PASS' if ok else 'FAIL'}")
        if not ok:
            raise AssertionError(f"SHA256 mismatch for {filename}")
        passed_assets += 1
    print(f"Source assets: {passed_assets}/{len(EXPECTED_SHA256)} PASS")

    print("\nMAT structure audit")
    print("-" * 124)
    for filename in [
        "com_func1_data.mat", "com_func2_data.mat", "com_func3_data.mat",
        "hybrid_func1_data.mat", "hybrid_func2_data.mat",
    ]:
        o = np.asarray(loadmat(DATA_DIR / filename)["o"], dtype=float)
        ok = o.shape == (10, 100) and np.all(np.isfinite(o))
        print(f"{filename:<28} shape={str(o.shape):<10} finite={bool(np.all(np.isfinite(o)))}  {'PASS' if ok else 'FAIL'}")
        if not ok:
            raise AssertionError(filename)

    c2 = load_matrix_condition_numbers("com_func2_M_D10.mat")
    c3 = load_matrix_condition_numbers("com_func3_M_D10.mat")
    h1 = load_matrix_condition_numbers("hybrid_func1_M_D10.mat")
    h2 = load_matrix_condition_numbers("hybrid_func2_M_D10.mat")
    if not np.allclose(c2, 1.0, rtol=1e-10, atol=1e-10):
        raise AssertionError("com_func2 matrices are not orthogonal as expected")
    if not np.allclose(c3, 1.0, rtol=1e-10, atol=1e-10):
        raise AssertionError("com_func3 matrices are not orthogonal as expected")
    if not np.allclose(h1, 2.0, rtol=1e-10, atol=1e-10):
        raise AssertionError("hybrid_func1 matrix condition numbers differ from source data")
    expected_h2 = np.array([2, 3, 2, 3, 2, 3, 20, 30, 200, 300], dtype=float)
    if not np.allclose(h2, expected_h2, rtol=1e-10, atol=1e-10):
        raise AssertionError(f"hybrid_func2 condition numbers: {h2}")
    print("D10 matrices                PASS")
    print(f"  com_func2 cond(M)  ~ {np.round(c2, 6).tolist()}")
    print(f"  com_func3 cond(M)  ~ {np.round(c3, 6).tolist()}")
    print(f"  hybrid_func1 cond  ~ {np.round(h1, 6).tolist()}")
    print(f"  hybrid_func2 cond  ~ {np.round(h2, 6).tolist()}")

    print("\nDeterministic function audit")
    print("-" * 124)
    for name in ["F24", "F25", "F26", "F27", "F28", "F29"]:
        b = get_sis2005_benchmark(name)
        if b.dim != 10 or b.lb != -5.0 or b.ub != 5.0 or b.optimum != 0.0:
            raise AssertionError(f"Protocol mismatch for {name}")

        f_zero = b.objective(np.zeros(10))
        f_ones = b.objective(np.ones(10))
        f_opt = b.objective(b.optima[0])
        assert_close(f_zero, EXPECTED_FIXED[name]["zero"], label=f"{name}@0")
        assert_close(f_ones, EXPECTED_FIXED[name]["ones"], atol=1e-9, label=f"{name}@1")
        assert_close(f_opt, 0.0, atol=1e-12, rtol=0.0, label=f"{name}@o1")
        print(
            f"{name} / CF{b.func_num}: f(0)={f_zero: .12f}  "
            f"f(1)={f_ones: .12f}  f(o1)={f_opt:.3e}  PASS"
        )

    batch = np.vstack([
        np.zeros(10),
        np.ones(10),
        np.linspace(-4.5, 4.5, 10),
    ])
    vals = evaluate_sis2005("F27", batch)
    scalar = np.array([evaluate_sis2005("F27", x) for x in batch])
    if not np.allclose(vals, scalar, rtol=1e-13, atol=1e-12):
        raise AssertionError("Batch/scalar mismatch")
    print("Batch/scalar evaluation      PASS")

    print("\nSource discrepancy audit")
    print("-" * 124)
    source_val = evaluate_sis2005("F26", np.ones(10), variant="source_faithful")
    paper_val = evaluate_sis2005("F26", np.ones(10), variant="paper_table4")
    if np.isclose(source_val, paper_val, rtol=1e-8, atol=1e-8):
        raise AssertionError("F26 source/paper diagnostic unexpectedly identical")
    print("GWO Table 4 F26/CF3       : prints ten Griewank components")
    print("Uploaded SIS_novel_func.m : com_func3 uses ten Rastrigin components")
    print(f"F26 source-faithful f(1)  : {source_val:.12f}")
    print(f"F26 paper-table diagnostic: {paper_val:.12f}")
    print("Primary H1 implementation : SOURCE-FAITHFUL (Rastrigin)  PASS")

    print("\nPaper Table 8 reference")
    print("-" * 124)
    for name in ["F24", "F25", "F26", "F27", "F28", "F29"]:
        b = get_sis2005_benchmark(name)
        print(f"{name}: paper Mean={b.paper_mean:<10g} Std={b.paper_std:g}")

    print("\nH1b/c RESULT: PASS")
    print("Original source assets are frozen and the Python benchmark layer passed deterministic checks.")
    print("No GWO optimization was executed.")
    print("algorithms/gwo.py was not modified.")
    print("Next: H1d single-seed integration smoke test, then H1e 30-run Table-8 reproduction.")


if __name__ == "__main__":
    main()
