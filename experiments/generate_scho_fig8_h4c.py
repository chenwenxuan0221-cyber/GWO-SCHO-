"""H4c - SCHO paper Fig.8 controlled-equivalent qualitative reproduction.

Paper structure
---------------
Displayed functions:
    F2, F7, F9, F10, F11, F15, F21

Protocol:
    N = 30
    MaxIter = 500
    optimizer seed = 1000 (project convention)
    F7 objective RNG uses a separate deterministic seed.

For each function, five paper-style panels are generated:
    1. Parameter space / 2-D landscape
    2. Search history (x1, x2 projection)
    3. Trajectory of the first dimension of the first agent
    4. Average fitness of all search agents
    5. Historical-best convergence curve

The paper does not publish the exact Fig.8 random seed or a history logger.
Therefore this stage is explicitly:
    PAPER-STRUCTURE / CONTROLLED-EQUIVALENT
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from benchmarks.classic_23 import get_benchmark
from experiments.scho_history_instrumented_h4 import scho_with_history


FUNCTIONS = ["F2", "F7", "F9", "F10", "F11", "F15", "F21"]

N = 30
MAX_ITER = 500
OPTIMIZER_SEED = 1000
OBJECTIVE_SEED_BASE = 2_024_000
SURFACE_SEED_BASE = 9_024_000
GRID_POINTS = 61

RAW_DIR = Path("results/raw")
PROCESSED_DIR = Path("results/processed")
FIG_DIR = Path("report/figures")
REPORT_PATH = Path("report/notes/H4c_scho_fig8_results.md")

SUMMARY_PATH = PROCESSED_DIR / "scho_h4c_fig8_summary.csv"
MANIFEST_PATH = PROCESSED_DIR / "scho_h4c_fig8_manifest.csv"

FIG_PART1 = FIG_DIR / "scho_fig8_part1_F2_F7_F9.png"
FIG_PART2 = FIG_DIR / "scho_fig8_part2_F10_F11_F15.png"
FIG_PART3 = FIG_DIR / "scho_fig8_part3_F21.png"
FIG_ALL7 = FIG_DIR / "scho_fig8_all7.png"


def _function_number(name: str) -> int:
    return int(name[1:])


def _objective_seed(name: str) -> int:
    return OBJECTIVE_SEED_BASE + _function_number(name)


def _surface_seed(name: str) -> int:
    return SURFACE_SEED_BASE + _function_number(name)


def _scalar_axis_bounds(bound, dim: int):
    arr = np.asarray(bound, dtype=float)
    if arr.ndim == 0 or arr.size == 1:
        value = float(arr.reshape(-1)[0])
        return np.full(dim, value, dtype=float)
    arr = arr.reshape(-1)
    if arr.size != dim:
        raise ValueError("Per-coordinate bound length does not match dimension.")
    return arr


def _surface_value(name, b, x1, x2, fixed_full, f7_rng):
    """Evaluate only the visualization surface, never the optimizer objective.

    F2/F7/F9/F10/F11:
        use the benchmark formula directly as a genuine 2-D version.

    F15/F21:
        keep dimensions 3..D fixed at the final best position from the
        qualitative run and vary x1/x2. This is a controlled 2-D slice.
    """
    if name in {"F2", "F9", "F10", "F11"}:
        return float(b.func(np.array([x1, x2], dtype=float)))

    if name == "F7":
        return float(b.func(np.array([x1, x2], dtype=float), f7_rng))

    x = np.asarray(fixed_full, dtype=float).copy()
    x[0] = x1
    x[1] = x2
    return float(b.func(x))


def _build_surface(name, b, best_pos):
    lb = _scalar_axis_bounds(b.lb, b.dim)
    ub = _scalar_axis_bounds(b.ub, b.dim)

    x = np.linspace(lb[0], ub[0], GRID_POINTS)
    y = np.linspace(lb[1], ub[1], GRID_POINTS)
    X, Y = np.meshgrid(x, y)
    Z = np.empty_like(X, dtype=float)

    f7_rng = np.random.default_rng(_surface_seed(name))

    for row in range(GRID_POINTS):
        for col in range(GRID_POINTS):
            Z[row, col] = _surface_value(
                name,
                b,
                float(X[row, col]),
                float(Y[row, col]),
                best_pos,
                f7_rng,
            )

    if not np.all(np.isfinite(Z)):
        raise AssertionError(f"{name}: non-finite parameter-space surface")

    return X, Y, Z


def _save_raw(name, b, score, best_pos, curve, history):
    path = RAW_DIR / f"scho_h4c_fig8_{name}.npz"
    np.savez_compressed(
        path,
        function=name,
        dim=int(b.dim),
        lb=np.asarray(b.lb, dtype=float),
        ub=np.asarray(b.ub, dtype=float),
        optimum=float(b.optimum),
        N=N,
        MaxIter=MAX_ITER,
        optimizer_seed=OPTIMIZER_SEED,
        objective_seed=_objective_seed(name),
        best_score=float(score),
        best_position=np.asarray(best_pos, dtype=float),
        convergence_curve=np.asarray(curve, dtype=float),
        position_history=np.asarray(history["position_history"], dtype=float),
        fitness_history=np.asarray(history["fitness_history"], dtype=float),
        first_agent_x1=np.asarray(history["first_agent_x1"], dtype=float),
        average_fitness=np.asarray(history["average_fitness"], dtype=float),
        best_position_history=np.asarray(
            history["best_position_history"], dtype=float
        ),
        phase_history=np.asarray(history["phase_history"]),
        redistribution_count=np.asarray(history["redistribution_count"]),
        T=int(history["T"]),
        initial_BS=int(history["initial_BS"]),
    )
    return path


def _validate_paper_scale_run(name, b, score, best_pos, curve, history):
    best_pos = np.asarray(best_pos, dtype=float)
    curve = np.asarray(curve, dtype=float)
    pos = np.asarray(history["position_history"], dtype=float)
    fit = np.asarray(history["fitness_history"], dtype=float)
    avg = np.asarray(history["average_fitness"], dtype=float)

    if not np.isfinite(score):
        raise AssertionError(f"{name}: non-finite best score")
    if best_pos.shape != (b.dim,):
        raise AssertionError(f"{name}: best position shape mismatch")
    if curve.shape != (MAX_ITER,):
        raise AssertionError(f"{name}: convergence shape mismatch")
    if pos.shape != (MAX_ITER, N, b.dim):
        raise AssertionError(f"{name}: position history shape mismatch")
    if fit.shape != (MAX_ITER, N):
        raise AssertionError(f"{name}: fitness history shape mismatch")
    if avg.shape != (MAX_ITER,):
        raise AssertionError(f"{name}: average-fitness shape mismatch")

    for arr_name, arr in [
        ("best_pos", best_pos),
        ("curve", curve),
        ("position_history", pos),
        ("fitness_history", fit),
        ("average_fitness", avg),
    ]:
        if not np.all(np.isfinite(arr)):
            raise AssertionError(f"{name}: {arr_name} has NaN/Inf")

    if score != float(curve[-1]):
        raise AssertionError(f"{name}: score != curve[-1]")
    if np.any(np.diff(curve) > 0.0):
        raise AssertionError(f"{name}: historical-best curve increased")
    if not np.array_equal(
        np.asarray(history["first_agent_x1"], dtype=float),
        pos[:, 0, 0],
    ):
        raise AssertionError(f"{name}: first-agent trajectory mismatch")
    if not np.array_equal(avg, np.mean(fit, axis=1)):
        raise AssertionError(f"{name}: average fitness mismatch")


def _strict_improvements(curve, start_index=1):
    curve = np.asarray(curve, dtype=float)
    return int(np.sum(curve[start_index:] < curve[start_index - 1:-1]))


def _post_switch_improvements(curve, T):
    curve = np.asarray(curve, dtype=float)
    # T is the last 1-based convergence point labeled phase 1.
    start = max(int(T), 1)
    if start >= len(curve):
        return 0
    return int(np.sum(curve[start:] < curve[start - 1:-1]))


def _switch_transient_ratio(avg, T):
    """Diagnostic only: level near switch relative to preceding local median.

    Values >1 mean the population-average objective became worse at/just after
    the switch on a positive-valued scale. For signed objectives the raw ratio
    is not robust, so return NaN if the local median is non-positive.
    """
    avg = np.asarray(avg, dtype=float)
    center = min(max(int(T), 1), len(avg) - 1)
    before = avg[max(0, center - 10):center]
    after = avg[center:min(len(avg), center + 4)]
    if before.size == 0 or after.size == 0:
        return math.nan

    base = float(np.median(before))
    peak = float(np.max(after))
    if base <= 0.0:
        return math.nan
    return peak / base


def _plot_parameter_space(ax, name, b, result):
    X, Y, Z = _build_surface(name, b, result["best_pos"])
    ax.plot_surface(X, Y, Z, rstride=2, cstride=2, linewidth=0)
    ax.contour(X, Y, Z, zdir="z", offset=float(np.nanmin(Z)), levels=10)
    ax.set_title("Parameter space", fontsize=8)
    ax.set_xlabel("$x_1$", fontsize=7)
    ax.set_ylabel("$x_2$", fontsize=7)
    ax.set_zlabel(f"{name}($x_1,x_2$)", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.view_init(elev=28, azim=-55)


def _plot_search_history(ax, name, b, result):
    pos = np.asarray(result["history"]["position_history"], dtype=float)
    flat = pos[:, :, :2].reshape(-1, 2)

    ax.scatter(flat[:, 0], flat[:, 1], s=2, alpha=0.22)
    ax.scatter(
        result["best_pos"][0],
        result["best_pos"][1],
        marker="x",
        s=28,
        linewidths=1.0,
    )

    lb = _scalar_axis_bounds(b.lb, b.dim)
    ub = _scalar_axis_bounds(b.ub, b.dim)
    ax.set_xlim(lb[0], ub[0])
    ax.set_ylim(lb[1], ub[1])
    ax.set_title("Search history", fontsize=8)
    ax.set_xlabel("$x_1$", fontsize=7)
    ax.set_ylabel("$x_2$", fontsize=7)
    ax.tick_params(labelsize=6)


def _plot_trajectory(ax, result):
    x = np.arange(1, MAX_ITER + 1)
    ax.plot(x, result["history"]["first_agent_x1"], linewidth=0.9)
    ax.set_xlim(1, MAX_ITER)
    ax.set_title("Trajectory of 1st agent", fontsize=8)
    ax.set_xlabel("Iteration", fontsize=7)
    ax.set_ylabel("$x_1$", fontsize=7)
    ax.tick_params(labelsize=6)


def _plot_average_fitness(ax, result):
    x = np.arange(1, MAX_ITER + 1)
    ax.plot(x, result["history"]["average_fitness"], linewidth=0.9)
    ax.set_xlim(1, MAX_ITER)
    ax.set_title("Average fitness of all agents", fontsize=8)
    ax.set_xlabel("Iteration", fontsize=7)
    ax.set_ylabel("Mean fitness", fontsize=7)
    ax.tick_params(labelsize=6)


def _plot_convergence(ax, result):
    x = np.arange(1, MAX_ITER + 1)
    ax.plot(x, result["curve"], linewidth=0.9)
    ax.set_xlim(1, MAX_ITER)
    ax.set_title("Convergence curve", fontsize=8)
    ax.set_xlabel("Iteration", fontsize=7)
    ax.set_ylabel("Best fitness", fontsize=7)
    ax.tick_params(labelsize=6)


def _render_group(functions, results, path, page_title):
    rows = 2 * len(functions)
    fig = plt.figure(figsize=(11.5, 3.8 * len(functions)))
    gs = fig.add_gridspec(
        rows,
        3,
        height_ratios=[1.3, 0.9] * len(functions),
        hspace=0.55,
        wspace=0.38,
    )

    for k, name in enumerate(functions):
        b = results[name]["benchmark"]
        r = results[name]

        ax1 = fig.add_subplot(gs[2 * k, 0], projection="3d")
        ax2 = fig.add_subplot(gs[2 * k, 1])
        ax3 = fig.add_subplot(gs[2 * k, 2])
        ax4 = fig.add_subplot(gs[2 * k + 1, 0])
        ax5 = fig.add_subplot(gs[2 * k + 1, 1])
        ax_blank = fig.add_subplot(gs[2 * k + 1, 2])
        ax_blank.axis("off")

        _plot_parameter_space(ax1, name, b, r)
        _plot_search_history(ax2, name, b, r)
        _plot_trajectory(ax3, r)
        _plot_average_fitness(ax4, r)
        _plot_convergence(ax5, r)

        ax1.text2D(
            -0.15,
            1.05,
            name,
            transform=ax1.transAxes,
            fontsize=9,
            fontweight="bold",
        )

    fig.suptitle(page_title, fontsize=12, y=0.995)
    fig.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(fig)


def _write_summary(rows):
    fields = [
        "Function",
        "Dimension",
        "Population",
        "MaxIter",
        "OptimizerSeed",
        "ObjectiveSeed",
        "FinalBest",
        "Optimum",
        "PhaseSwitchT",
        "InitialBS",
        "TotalRedistributions",
        "StrictBestImprovements",
        "PostSwitchBestImprovements",
        "AverageFitnessAtSwitch",
        "SwitchTransientRatioDiagnostic",
    ]

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_manifest(raw_paths):
    fields = ["ArtifactType", "FunctionOrGroup", "Path", "Status", "Notes"]
    rows = []

    for name, path in raw_paths.items():
        rows.append(
            {
                "ArtifactType": "raw_history_npz",
                "FunctionOrGroup": name,
                "Path": str(path),
                "Status": "PASS",
                "Notes": "Full evaluated-position/fitness history and convergence evidence.",
            }
        )

    for group, path in [
        ("F2_F7_F9", FIG_PART1),
        ("F10_F11_F15", FIG_PART2),
        ("F21", FIG_PART3),
        ("ALL7", FIG_ALL7),
    ]:
        rows.append(
            {
                "ArtifactType": "figure",
                "FunctionOrGroup": group,
                "Path": str(path),
                "Status": "PASS",
                "Notes": "SCHO Fig.8 paper-structure / controlled-equivalent visualization.",
            }
        )

    rows += [
        {
            "ArtifactType": "summary_csv",
            "FunctionOrGroup": "ALL7",
            "Path": str(SUMMARY_PATH),
            "Status": "PASS",
            "Notes": "Run-level qualitative diagnostics.",
        },
        {
            "ArtifactType": "manifest_csv",
            "FunctionOrGroup": "ALL7",
            "Path": str(MANIFEST_PATH),
            "Status": "PASS",
            "Notes": "H4c evidence manifest.",
        },
        {
            "ArtifactType": "report_md",
            "FunctionOrGroup": "ALL7",
            "Path": str(REPORT_PATH),
            "Status": "PASS",
            "Notes": "Protocol and observation summary.",
        },
    ]

    with MANIFEST_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_report(summary_rows):
    lines = [
        "# H4c — SCHO Fig.8 qualitative reproduction",
        "",
        "## Freeze tier",
        "",
        "`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`",
        "",
        "The paper identifies five qualitative metrics but does not publish the",
        "exact Fig.8 seed or an exact history-logging implementation. This stage",
        "therefore reproduces the paper structure with the frozen source-faithful",
        "SCHO and an explicitly frozen H4b history convention.",
        "",
        "## Protocol",
        "",
        "- Functions: F2, F7, F9, F10, F11, F15, F21",
        "- N = 30",
        "- MaxIter = 500",
        "- optimizer seed = 1000 (project convention)",
        "- separate deterministic F7 objective RNG",
        "- no modification of `algorithms/scho.py`",
        "- phase switch from frozen source: `T = floor(500 / 3.6) = 138`",
        "",
        "## Five reproduced metrics",
        "",
        "1. parameter-space / 2-D landscape",
        "2. search history",
        "3. first-agent first-dimension trajectory",
        "4. average fitness of all search agents",
        "5. historical-best convergence curve",
        "",
        "For F2/F7/F9/F10/F11, the surface is the direct 2-D version of the",
        "benchmark formula. For fixed-dimensional F15/F21, dimensions 3..D are",
        "held at the final best position while x1/x2 are varied; those panels are",
        "therefore controlled 2-D slices rather than claims of an exact published",
        "projection.",
        "",
        "## Run diagnostics",
        "",
        "| F | D | Final best | Paper fmin metadata | T | Redistributions | Strict best improvements | Post-switch improvements |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in summary_rows:
        lines.append(
            f"| {row['Function']} | {row['Dimension']} "
            f"| {row['FinalBest']:.8g} | {row['Optimum']:.8g} "
            f"| {row['PhaseSwitchT']} | {row['TotalRedistributions']} "
            f"| {row['StrictBestImprovements']} "
            f"| {row['PostSwitchBestImprovements']} |"
        )

    lines += [
        "",
        "## Interpretation boundary",
        "",
        "The paper qualitatively discusses stronger early exploration, later",
        "exploitation, a population-average-fitness disturbance near the phase",
        "switch, smoother unimodal convergence and more stepwise multimodal",
        "convergence. H4c records the evidence needed to inspect those claims,",
        "but does not force the project trajectory to exhibit every published",
        "visual feature under the unrecovered paper seed.",
        "",
        "No trajectory is tuned to imitate the printed figure.",
        "",
        "## Outputs",
        "",
        "- `report/figures/scho_fig8_part1_F2_F7_F9.png`",
        "- `report/figures/scho_fig8_part2_F10_F11_F15.png`",
        "- `report/figures/scho_fig8_part3_F21.png`",
        "- `report/figures/scho_fig8_all7.png`",
        "- seven raw `.npz` history files under `results/raw/`",
        "- `results/processed/scho_h4c_fig8_summary.csv`",
        "- `results/processed/scho_h4c_fig8_manifest.csv`",
        "",
        "## PASS meaning",
        "",
        "`H4c RESULT: PASS` means all seven paper-scale controlled-equivalent",
        "runs completed, raw histories were saved, and all four figure files were",
        "generated. It does not mean pixel-exact equality with the paper's Fig.8.",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 122)
    print("H4c - SCHO Fig.8 paper-scale controlled-equivalent qualitative reproduction")
    print("=" * 122)
    print(f"Functions: {', '.join(FUNCTIONS)}")
    print(f"Protocol : N={N}, MaxIter={MAX_ITER}, optimizer seed={OPTIMIZER_SEED}")
    print("Five metrics: parameter space | search history | first-agent x1 | average fitness | convergence")
    print("Frozen algorithms/scho.py will NOT be modified.")
    print("=" * 122)

    results = {}
    raw_paths = {}
    summary_rows = []

    for name in FUNCTIONS:
        b = get_benchmark(name)
        obj_seed = _objective_seed(name)
        objective = b.make_objective(seed=obj_seed)

        score, best_pos, curve, history = scho_with_history(
            obj_func=objective,
            dim=b.dim,
            lb=b.lb,
            ub=b.ub,
            N=N,
            MaxIter=MAX_ITER,
            seed=OPTIMIZER_SEED,
        )

        _validate_paper_scale_run(name, b, score, best_pos, curve, history)

        raw_path = _save_raw(name, b, score, best_pos, curve, history)
        raw_paths[name] = raw_path

        T = int(history["T"])
        avg = np.asarray(history["average_fitness"], dtype=float)
        row = {
            "Function": name,
            "Dimension": int(b.dim),
            "Population": N,
            "MaxIter": MAX_ITER,
            "OptimizerSeed": OPTIMIZER_SEED,
            "ObjectiveSeed": obj_seed,
            "FinalBest": float(score),
            "Optimum": float(b.optimum),
            "PhaseSwitchT": T,
            "InitialBS": int(history["initial_BS"]),
            "TotalRedistributions": int(
                np.sum(np.asarray(history["redistribution_count"]))
            ),
            "StrictBestImprovements": _strict_improvements(curve),
            "PostSwitchBestImprovements": _post_switch_improvements(curve, T),
            "AverageFitnessAtSwitch": float(avg[T - 1]),
            "SwitchTransientRatioDiagnostic": _switch_transient_ratio(avg, T),
        }
        summary_rows.append(row)

        results[name] = {
            "benchmark": b,
            "score": float(score),
            "best_pos": np.asarray(best_pos, dtype=float),
            "curve": np.asarray(curve, dtype=float),
            "history": history,
        }

        print(
            f"{name:<4} D={b.dim:<2} "
            f"final={score:>14.8g} "
            f"T={T:<3} "
            f"redistributions={row['TotalRedistributions']:<4} "
            f"post-switch improvements={row['PostSwitchBestImprovements']:<3} "
            "PASS"
        )

    _write_summary(summary_rows)

    _render_group(
        ["F2", "F7", "F9"],
        results,
        FIG_PART1,
        "SCHO paper Fig.8-style qualitative results — part 1",
    )
    print("Fig.8 part 1 (F2/F7/F9): PASS")

    _render_group(
        ["F10", "F11", "F15"],
        results,
        FIG_PART2,
        "SCHO paper Fig.8-style qualitative results — part 2",
    )
    print("Fig.8 part 2 (F10/F11/F15): PASS")

    _render_group(
        ["F21"],
        results,
        FIG_PART3,
        "SCHO paper Fig.8-style qualitative results — part 3",
    )
    print("Fig.8 part 3 (F21): PASS")

    _render_group(
        FUNCTIONS,
        results,
        FIG_ALL7,
        "SCHO paper Fig.8-style qualitative results — all 7 functions",
    )
    print("Fig.8 all-7 composite: PASS")

    _write_report(summary_rows)
    _write_manifest(raw_paths)

    expected_raw = [RAW_DIR / f"scho_h4c_fig8_{name}.npz" for name in FUNCTIONS]
    expected_figs = [FIG_PART1, FIG_PART2, FIG_PART3, FIG_ALL7]

    if not all(path.exists() and path.stat().st_size > 0 for path in expected_raw):
        raise AssertionError("One or more raw H4c history files are missing/empty")
    if not all(path.exists() and path.stat().st_size > 0 for path in expected_figs):
        raise AssertionError("One or more H4c Fig.8 images are missing/empty")
    if not SUMMARY_PATH.exists() or not MANIFEST_PATH.exists() or not REPORT_PATH.exists():
        raise AssertionError("H4c processed/report output missing")

    print("-" * 122)
    print("H4c RESULT: PASS")
    print(f"Functions completed: {len(FUNCTIONS)}/{len(FUNCTIONS)}")
    print(f"Raw history files: {len(expected_raw)}/{len(expected_raw)}")
    print(f"Fig.8-style figures: {len(expected_figs)}/{len(expected_figs)}")
    print(f"Summary : {SUMMARY_PATH}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Report  : {REPORT_PATH}")
    print("algorithms/scho.py was not modified.")
    print("Next: H4d structural Table-5 subordinate-model variants.")
    print("=" * 122)


if __name__ == "__main__":
    main()
