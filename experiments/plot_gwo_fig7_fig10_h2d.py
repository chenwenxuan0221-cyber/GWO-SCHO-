"""Stage H2d: reproduce GWO paper Fig. 7-Fig. 10 benchmark landscapes.

This plotting-only script does not run GWO and does not modify frozen optimizers.
Classic F1-F18 use the project's Benchmark dataclass API. Fig.10 uses the
H1 source-faithful SIS2005 D=10 backend as a controlled 2D slice through the
first component optimum because the original D=2 rotation generator/state used
by SIS2005 func_plot.m is not available in the recovered package.
"""
from __future__ import annotations

import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from benchmarks.classic_23 import get_benchmark
from benchmarks.gwo_sis2005 import get_sis2005_benchmark, evaluate_sis2005

OUT_DIR = Path("report/figures")
MANIFEST = Path("results/processed/gwo_h2d_landscape_manifest.csv")
PLOT_SEED = 27007

# Ranges from the commonly distributed GWO func_plot.m plotting helper.
# These are visualization ranges, not always the optimizer search bounds.
CLASSIC_RANGES = {
    "F1": (-100.0, 100.0, 2.0),
    "F2": (-100.0, 100.0, 2.0),
    "F3": (-100.0, 100.0, 2.0),
    "F4": (-100.0, 100.0, 2.0),
    "F5": (-200.0, 200.0, 2.0),
    "F6": (-100.0, 100.0, 2.0),
    "F7": (-1.0, 1.0, 0.03),
    "F8": (-500.0, 500.0, 10.0),
    "F9": (-5.0, 5.0, 0.1),
    "F10": (-20.0, 20.0, 0.5),
    "F11": (-500.0, 500.0, 10.0),
    "F12": (-10.0, 10.0, 0.1),
    "F13": (-5.0, 5.0, 0.08),
    "F14": (-100.0, 100.0, 2.0),
    "F16": (-1.0, 1.0, 0.01),
    "F17": (-5.0, 5.0, 0.1),
    "F18": (-5.0, 5.0, 0.06),
}

GROUPS = [
    ("Fig.7", ["F1", "F2", "F3", "F4", "F5", "F6", "F7"], 2, 4,
     "gwo_fig7_unimodal_landscapes.png"),
    ("Fig.8", ["F8", "F9", "F10", "F11", "F12", "F13"], 2, 3,
     "gwo_fig8_multimodal_landscapes.png"),
    ("Fig.9", ["F14", "F16", "F17", "F18"], 2, 2,
     "gwo_fig9_fixed_multimodal_landscapes.png"),
]


def inclusive_axis(lo: float, hi: float, step: float) -> np.ndarray:
    n = int(np.floor((hi - lo) / step + 0.5))
    x = lo + step * np.arange(n + 1, dtype=float)
    if x[-1] < hi - 1e-12:
        x = np.append(x, hi)
    return x[x <= hi + 1e-12]


def classic_grid(name: str):
    b = get_benchmark(name)
    lo, hi, step = CLASSIC_RANGES[name]
    axis = inclusive_axis(lo, hi, step)
    X, Y = np.meshgrid(axis, axis)

    # The paper labels these as 2-D versions. The benchmark formulas F1-F14,
    # F16-F18 accept a two-variable input directly. For stochastic F7, use a
    # fixed objective RNG to make the visualization reproducible.
    obj = b.make_objective(seed=PLOT_SEED + int(name[1:]))
    Z = np.empty_like(X, dtype=float)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = float(obj(np.array([X[i, j], Y[i, j]], dtype=float)))

    if not np.all(np.isfinite(Z)):
        raise FloatingPointError(f"{name}: landscape contains NaN/Inf")
    return X, Y, Z, f"2-D benchmark version; plot range [{lo:g},{hi:g}]"


def sis_grid(name: str):
    b = get_sis2005_benchmark(name, variant="source_faithful")
    axis = inclusive_axis(-5.0, 5.0, 0.1)
    X, Y = np.meshgrid(axis, axis)

    # Controlled-equivalent visualization: keep dimensions 3..10 at the
    # first component optimum, and vary dimensions 1..2. This preserves the
    # exact H1 D=10 source assets and ensures the slice contains the global
    # optimum. It is not claimed to recover the original paper's unreleased
    # D=2 random rotation state.
    pts = np.tile(np.asarray(b.optima[0], dtype=float), (X.size, 1))
    pts[:, 0] = X.ravel()
    pts[:, 1] = Y.ravel()
    vals = np.asarray(
        evaluate_sis2005(name, pts, variant="source_faithful"), dtype=float
    )
    Z = vals.reshape(X.shape)
    if not np.all(np.isfinite(Z)):
        raise FloatingPointError(f"{name}: SIS2005 slice contains NaN/Inf")
    return X, Y, Z, "H1 source-faithful D10 slice through component-1 optimum"


def add_surface(ax, X, Y, Z, title: str):
    # Match the paper's surface-plus-contour intent without changing Z.
    stride = max(1, X.shape[0] // 55)
    ax.plot_surface(X, Y, Z, rstride=stride, cstride=stride,
                    linewidth=0, antialiased=True)
    zmin = float(np.nanmin(Z))
    zmax = float(np.nanmax(Z))
    if zmax > zmin:
        ax.contour(X, Y, Z, zdir="z", offset=zmin, levels=8)
    ax.set_title(title)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_zlabel("f(x)")
    ax.view_init(elev=30, azim=-45)


def plot_group(fig_label, names, nrows, ncols, filename, manifest):
    fig = plt.figure(figsize=(4.2 * ncols, 3.7 * nrows))
    for idx, name in enumerate(names, start=1):
        X, Y, Z, protocol = classic_grid(name)
        ax = fig.add_subplot(nrows, ncols, idx, projection="3d")
        add_surface(ax, X, Y, Z, name)
        manifest.append({
            "Figure": fig_label,
            "Function": name,
            "GridRows": Z.shape[0],
            "GridCols": Z.shape[1],
            "ZMin": float(np.min(Z)),
            "ZMax": float(np.max(Z)),
            "Finite": True,
            "Protocol": protocol,
        })
    fig.suptitle(f"GWO paper {fig_label}-style benchmark landscapes")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    path = OUT_DIR / filename
    fig.savefig(path, dpi=260, bbox_inches="tight")
    plt.close(fig)
    print(f"{fig_label}: saved {path} | functions={len(names)} | PASS")


def plot_fig10(manifest):
    names = ["F24", "F25", "F26", "F27", "F28", "F29"]
    fig = plt.figure(figsize=(12.6, 7.4))
    for idx, name in enumerate(names, start=1):
        X, Y, Z, protocol = sis_grid(name)
        b = get_sis2005_benchmark(name, variant="source_faithful")
        ax = fig.add_subplot(2, 3, idx, projection="3d")
        add_surface(ax, X, Y, Z, f"{name} / {b.canonical_name}")
        manifest.append({
            "Figure": "Fig.10",
            "Function": f"{name}/{b.canonical_name}",
            "GridRows": Z.shape[0],
            "GridCols": Z.shape[1],
            "ZMin": float(np.min(Z)),
            "ZMax": float(np.max(Z)),
            "Finite": True,
            "Protocol": protocol,
        })
    fig.suptitle("GWO paper Fig.10-style composite benchmark landscapes\n"
                 "H1 source-faithful D10 first-two-coordinate slices")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    path = OUT_DIR / "gwo_fig10_composite_landscapes.png"
    fig.savefig(path, dpi=260, bbox_inches="tight")
    plt.close(fig)
    print(f"Fig.10: saved {path} | functions=6 | PASS")


def write_manifest(rows):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    fields = ["Figure", "Function", "GridRows", "GridCols", "ZMin", "ZMax", "Finite", "Protocol"]
    with MANIFEST.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    print("=" * 112)
    print("H2d - GWO Fig.7-Fig.10 benchmark landscape reproduction")
    print("=" * 112)
    print("No optimizer will be executed.")
    print("Classic benchmark API: Benchmark dataclass (.func/.make_objective/.dim/.lb/.ub)")
    print("Fig.10: H1 source-faithful SIS2005 D10 controlled 2D slices")
    print("=" * 112)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for args in GROUPS:
        plot_group(*args, manifest)
    plot_fig10(manifest)
    write_manifest(manifest)

    if len(manifest) != 23:
        raise AssertionError(f"Expected 23 plotted functions, got {len(manifest)}")

    print("-" * 112)
    print("H2d RESULT: PASS")
    print("Figures generated: 4/4")
    print("Functions plotted: 23/23")
    print(f"Manifest: {MANIFEST}")
    print("algorithms/gwo.py was not used or modified.")


if __name__ == "__main__":
    main()
