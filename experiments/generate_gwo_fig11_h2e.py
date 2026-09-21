"""Stage H2e: GWO paper Fig. 11 qualitative convergence reproduction.

Tier-B / controlled-equivalent protocol
---------------------------------------
The original paper confirms the eight Fig.-11 functions, six search agents,
shifted benchmarks, search history, first-agent first-dimension trajectory and
100-iteration figure structure, but the exact shift vectors / seed / logging
semantics were not recovered. This script therefore uses the H2c frozen
controlled-equivalent shifted benchmark protocol and the H2b regression-tested
history adapter.

Outputs
-------
- report/figures/gwo_fig11_part1_F1_F7_F9.png
- report/figures/gwo_fig11_part2_F10_F14_F18_F26_F29.png
- report/figures/gwo_fig11_all8.png
- results/raw/gwo_h2e_fig11_<F>.npz (one per function)
- results/processed/gwo_h2e_fig11_summary.csv
- results/processed/gwo_h2e_fig11_manifest.csv
- report/notes/H2e_gwo_fig11_results.md

No frozen optimizer file is modified.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from benchmarks.gwo_shifted_h2 import FIG11_FUNCTIONS, get_h2_shifted_benchmark
from experiments.gwo_history_instrumented import gwo_with_history

N = 6
MAX_ITER = 100
GWO_SEED = 1000
OBJECTIVE_SEED_BASE = 93000
SURFACE_SEED_BASE = 94000
GRID_SIZE = 72

RAW_DIR = Path("results/raw")
PROCESSED_DIR = Path("results/processed")
FIG_DIR = Path("report/figures")
REPORT_PATH = Path("report/notes/H2e_gwo_fig11_results.md")
SUMMARY_PATH = PROCESSED_DIR / "gwo_h2e_fig11_summary.csv"
MANIFEST_PATH = PROCESSED_DIR / "gwo_h2e_fig11_manifest.csv"

PART1 = ("F1", "F7", "F9")
PART2 = ("F10", "F14", "F18", "F26", "F29")


def _safe_positive(y: np.ndarray) -> np.ndarray:
    arr = np.asarray(y, dtype=float)
    finite_pos = arr[np.isfinite(arr) & (arr > 0)]
    floor = float(np.min(finite_pos)) * 1e-6 if finite_pos.size else 1e-300
    floor = max(floor, 1e-300)
    return np.where(np.isfinite(arr) & (arr > floor), arr, floor)


def _surface_slice(name: str, grid_size: int = GRID_SIZE):
    """2-D first-two-coordinate slice through the shifted target optimum."""
    b = get_h2_shifted_benchmark(name)
    x1 = np.linspace(float(b.lb[0]), float(b.ub[0]), grid_size)
    x2 = np.linspace(float(b.lb[1]), float(b.ub[1]), grid_size)
    X, Y = np.meshgrid(x1, x2)
    pts = np.tile(b.target_optimum, (X.size, 1))
    pts[:, 0] = X.ravel()
    pts[:, 1] = Y.ravel()

    # Separate objective instance so surface sampling never advances the
    # optimizer's objective RNG (relevant only to stochastic F7).
    idx = FIG11_FUNCTIONS.index(name)
    obj = b.make_objective(SURFACE_SEED_BASE + idx)
    vals = np.empty(X.size, dtype=float)
    for k, p in enumerate(pts):
        vals[k] = float(obj(p))
    Z = vals.reshape(X.shape)
    if not np.all(np.isfinite(Z)):
        raise FloatingPointError(f"{name}: non-finite surface values")
    return X, Y, Z


def _run_one(name: str):
    b = get_h2_shifted_benchmark(name)
    idx = FIG11_FUNCTIONS.index(name)
    objective_seed = OBJECTIVE_SEED_BASE + idx
    obj = b.make_objective(objective_seed)
    hist = gwo_with_history(
        obj, b.dim, b.lb, b.ub, N, MAX_ITER, seed=GWO_SEED
    )

    expected_shapes = {
        "position_history": (MAX_ITER, N, b.dim),
        "fitness_history": (MAX_ITER, N),
        "first_agent_x1": (MAX_ITER,),
        "first_agent_fitness": (MAX_ITER,),
        "best_position_history": (MAX_ITER, b.dim),
        "a_history": (MAX_ITER,),
        "convergence_curve": (MAX_ITER,),
    }
    for key, expected in expected_shapes.items():
        actual = np.asarray(getattr(hist, key)).shape
        if actual != expected:
            raise AssertionError(f"{name}: {key} shape={actual}, expected={expected}")
        if not np.all(np.isfinite(getattr(hist, key))):
            raise AssertionError(f"{name}: {key} contains NaN/Inf")

    if np.any(np.diff(hist.convergence_curve) > 1e-12):
        raise AssertionError(f"{name}: convergence curve is not non-increasing")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"gwo_h2e_fig11_{name}.npz"
    np.savez_compressed(
        raw_path,
        function=name,
        dim=b.dim,
        lb=b.lb,
        ub=b.ub,
        base_optimum=b.base_optimum,
        target_optimum=b.target_optimum,
        shift=b.shift,
        gwo_seed=GWO_SEED,
        objective_seed=objective_seed,
        N=N,
        MaxIter=MAX_ITER,
        best_score=hist.best_score,
        best_pos=hist.best_pos,
        convergence_curve=hist.convergence_curve,
        position_history=hist.position_history,
        fitness_history=hist.fitness_history,
        first_agent_x1=hist.first_agent_x1,
        first_agent_fitness=hist.first_agent_fitness,
        best_position_history=hist.best_position_history,
        a_history=hist.a_history,
    )
    return b, hist, raw_path


def _add_surface(ax, name: str, X, Y, Z):
    stride = max(1, X.shape[0] // 45)
    ax.plot_surface(X, Y, Z, rstride=stride, cstride=stride,
                    linewidth=0, antialiased=True)
    zmin = float(np.min(Z))
    zmax = float(np.max(Z))
    if zmax > zmin:
        ax.contour(X, Y, Z, zdir="z", offset=zmin, levels=7)
    ax.set_title(name, fontsize=8)
    ax.set_xlabel("x1", fontsize=7)
    ax.set_ylabel("x2", fontsize=7)
    ax.set_zlabel("f(x)", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.view_init(elev=30, azim=-45)


def _add_search_history(ax, b, hist, X, Y, Z):
    ax.contour(X, Y, Z, levels=8)
    pos = hist.position_history
    ax.scatter(pos[:, :, 0].ravel(), pos[:, :, 1].ravel(), s=5, alpha=0.45)
    ax.scatter([b.target_optimum[0]], [b.target_optimum[1]], marker="*", s=48)
    ax.set_xlim(float(b.lb[0]), float(b.ub[0]))
    ax.set_ylim(float(b.lb[1]), float(b.ub[1]))
    ax.set_title("Search history", fontsize=8)
    ax.set_xlabel("x1", fontsize=7)
    ax.set_ylabel("x2", fontsize=7)
    ax.tick_params(labelsize=6)


def _add_a(ax, hist):
    t = np.arange(MAX_ITER)
    ax.plot(t, hist.a_history, linewidth=1.0)
    ax.set_xlim(0, MAX_ITER)
    ax.set_ylim(0, 2.05)
    ax.set_title("a", fontsize=8)
    ax.set_xlabel("iteration", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.35)


def _add_trajectory(ax, hist):
    t = np.arange(MAX_ITER)
    ax.plot(t, hist.first_agent_x1, linewidth=0.9)
    ax.set_xlim(0, MAX_ITER)
    ax.set_title("Trajectory in 1st dimension", fontsize=8)
    ax.set_xlabel("iteration", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.35)


def _add_fitness(ax, hist):
    t = np.arange(MAX_ITER)
    # Exact original Fig.-11 logging semantics are unavailable. H2e freezes
    # "fitness history" as the mean fitness of the six evaluated agents.
    mean_fitness = np.mean(hist.fitness_history, axis=1)
    ax.semilogy(t, _safe_positive(mean_fitness), linewidth=0.9)
    ax.set_xlim(0, MAX_ITER)
    ax.set_title("Fitness history (population mean)", fontsize=8)
    ax.set_xlabel("iteration", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, which="both", alpha=0.35)


def _add_convergence(ax, hist):
    t = np.arange(MAX_ITER)
    ax.semilogy(t, _safe_positive(hist.convergence_curve), linewidth=0.9)
    ax.set_xlim(0, MAX_ITER)
    ax.set_title("Convergence curve", fontsize=8)
    ax.set_xlabel("iteration", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, which="both", alpha=0.35)


def _plot_rows(names, records, path: Path, title: str):
    fig = plt.figure(figsize=(21, 3.2 * len(names)))
    for row, name in enumerate(names):
        b, hist, _raw = records[name]
        X, Y, Z = _surface_slice(name)

        ax = fig.add_subplot(len(names), 6, row * 6 + 1, projection="3d")
        _add_surface(ax, name, X, Y, Z)

        ax = fig.add_subplot(len(names), 6, row * 6 + 2)
        _add_search_history(ax, b, hist, X, Y, Z)

        ax = fig.add_subplot(len(names), 6, row * 6 + 3)
        _add_a(ax, hist)

        ax = fig.add_subplot(len(names), 6, row * 6 + 4)
        _add_trajectory(ax, hist)

        ax = fig.add_subplot(len(names), 6, row * 6 + 5)
        _add_fitness(ax, hist)

        ax = fig.add_subplot(len(names), 6, row * 6 + 6)
        _add_convergence(ax, hist)

    fig.suptitle(title, fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def _write_summary(records):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "Function", "Dim", "N", "MaxIter", "GWOSeed", "ObjectiveSeed",
        "TargetX1", "TargetX2", "BestScore", "BestX1", "BestX2",
        "DistanceToTarget", "InitialBest", "FinalMeanFitness", "RawHistoryFile",
    ]
    rows = []
    for idx, name in enumerate(FIG11_FUNCTIONS):
        b, hist, raw_path = records[name]
        rows.append({
            "Function": name,
            "Dim": b.dim,
            "N": N,
            "MaxIter": MAX_ITER,
            "GWOSeed": GWO_SEED,
            "ObjectiveSeed": OBJECTIVE_SEED_BASE + idx,
            "TargetX1": float(b.target_optimum[0]),
            "TargetX2": float(b.target_optimum[1]),
            "BestScore": float(hist.best_score),
            "BestX1": float(hist.best_pos[0]),
            "BestX2": float(hist.best_pos[1]),
            "DistanceToTarget": float(np.linalg.norm(hist.best_pos - b.target_optimum)),
            "InitialBest": float(hist.convergence_curve[0]),
            "FinalMeanFitness": float(np.mean(hist.fitness_history[-1])),
            "RawHistoryFile": str(raw_path),
        })
    with SUMMARY_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return rows


def _write_manifest():
    rows = [
        {
            "Artifact": "Fig11 part 1",
            "Path": str(FIG_DIR / "gwo_fig11_part1_F1_F7_F9.png"),
            "Functions": "F1;F7;F9",
            "Protocol": "controlled-equivalent shifted; 6 agents; 100 iterations",
        },
        {
            "Artifact": "Fig11 part 2",
            "Path": str(FIG_DIR / "gwo_fig11_part2_F10_F14_F18_F26_F29.png"),
            "Functions": "F10;F14;F18;F26;F29",
            "Protocol": "controlled-equivalent shifted; 6 agents; 100 iterations",
        },
        {
            "Artifact": "Fig11 all 8",
            "Path": str(FIG_DIR / "gwo_fig11_all8.png"),
            "Functions": ";".join(FIG11_FUNCTIONS),
            "Protocol": "controlled-equivalent shifted; 6 agents; 100 iterations",
        },
    ]
    fields = ["Artifact", "Path", "Functions", "Protocol"]
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _write_report(summary_rows):
    lines = [
        "# H2e — GWO Fig.11 qualitative convergence reproduction",
        "",
        "## Reproduction tier",
        "",
        "`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`",
        "",
        "The exact original Fig.-11 shift vectors, seed and internal logging semantics",
        "were not recovered. H2e therefore uses the H2c frozen deterministic shift",
        "convention and the H2b history adapter, which was regression-tested against",
        "the frozen GWO implementation.",
        "",
        "## Protocol",
        "",
        "- Functions: F1, F7, F9, F10, F14, F18, F26, F29",
        "- Search agents: 6",
        "- Iterations: 100",
        f"- GWO seed: {GWO_SEED}",
        "- Dimensions: native benchmark dimensions frozen in H2c",
        "- Shift: target optimum at 65% from lower to upper bound in every coordinate",
        "- F26/F29: H1 source-faithful SIS2005 definitions",
        "- Fitness-history display: population mean fitness per evaluated iteration",
        "- Search history: all six evaluated agents projected onto x1/x2",
        "- Surface: x1/x2 slice through the shifted target optimum for remaining dimensions",
        "",
        "## Outputs",
        "",
        "- `report/figures/gwo_fig11_part1_F1_F7_F9.png`",
        "- `report/figures/gwo_fig11_part2_F10_F14_F18_F26_F29.png`",
        "- `report/figures/gwo_fig11_all8.png`",
        "- eight raw `.npz` history evidence files in `results/raw/`",
        "- `results/processed/gwo_h2e_fig11_summary.csv`",
        "- `results/processed/gwo_h2e_fig11_manifest.csv`",
        "",
        "## Run summary",
        "",
        "| Function | D | Best score | Target x1 | Best x1 | Distance to shifted target |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['Function']} | {row['Dim']} | {row['BestScore']:.10g} | "
            f"{row['TargetX1']:.8g} | {row['BestX1']:.8g} | "
            f"{row['DistanceToTarget']:.8g} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "These figures reproduce the paper's qualitative structure, not its unrecovered",
        "exact random trajectory. Similar qualitative exploration-to-exploitation behavior",
        "may be compared, but point-by-point agreement with the published Fig.11 is not",
        "claimed.",
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("=" * 118)
    print("H2e - GWO Fig.11 controlled-equivalent qualitative convergence reproduction")
    print("=" * 118)
    print(f"Functions: {', '.join(FIG11_FUNCTIONS)}")
    print(f"Protocol: N={N}, MaxIter={MAX_ITER}, GWO seed={GWO_SEED}")
    print("Shift protocol: H2c target at 65% of each coordinate's search interval")
    print("Fitness-history convention: population mean of six evaluated agents")
    print("=" * 118)

    records = {}
    for name in FIG11_FUNCTIONS:
        b, hist, raw_path = _run_one(name)
        records[name] = (b, hist, raw_path)
        print(
            f"{name:<4} D={b.dim:<2} final={hist.best_score:>14.7g} "
            f"target_x1={b.target_optimum[0]:>10.5g} "
            f"best_x1={hist.best_pos[0]:>10.5g} PASS"
        )

    summary = _write_summary(records)
    _write_manifest()
    _plot_rows(
        PART1, records,
        FIG_DIR / "gwo_fig11_part1_F1_F7_F9.png",
        "GWO paper Fig.11-style qualitative behavior — part 1\n"
        "H2 controlled-equivalent shifted protocol",
    )
    print("Fig.11 part 1: PASS")
    _plot_rows(
        PART2, records,
        FIG_DIR / "gwo_fig11_part2_F10_F14_F18_F26_F29.png",
        "GWO paper Fig.11-style qualitative behavior — part 2\n"
        "H2 controlled-equivalent shifted protocol",
    )
    print("Fig.11 part 2: PASS")
    _plot_rows(
        FIG11_FUNCTIONS, records,
        FIG_DIR / "gwo_fig11_all8.png",
        "GWO paper Fig.11-style qualitative behavior — all 8 functions\n"
        "H2 controlled-equivalent shifted protocol",
    )
    print("Fig.11 all-8 composite: PASS")
    _write_report(summary)

    expected_raw = [RAW_DIR / f"gwo_h2e_fig11_{name}.npz" for name in FIG11_FUNCTIONS]
    expected_fig = [
        FIG_DIR / "gwo_fig11_part1_F1_F7_F9.png",
        FIG_DIR / "gwo_fig11_part2_F10_F14_F18_F26_F29.png",
        FIG_DIR / "gwo_fig11_all8.png",
    ]
    for p in expected_raw + expected_fig + [SUMMARY_PATH, MANIFEST_PATH, REPORT_PATH]:
        if not p.exists() or p.stat().st_size == 0:
            raise AssertionError(f"Missing/empty H2e artifact: {p}")

    print("-" * 118)
    print("H2e RESULT: PASS")
    print("Functions completed: 8/8")
    print("Raw history files: 8/8")
    print("Fig.11-style figures: 3/3")
    print(f"Summary : {SUMMARY_PATH}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Report  : {REPORT_PATH}")
    print("algorithms/gwo.py was not modified.")
    print("Next: H2f visual/coverage audit and freeze of GWO Section 4 figures.")


if __name__ == "__main__":
    main()
