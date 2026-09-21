"""H5h - controlled-equivalent reproduction of SCHO Fig. 9 convergence curves.

Boundary
--------
The paper states that Fig. 9 shows convergence curves of SCHO and the eight
comparison algorithms on F1-F23, but the accessible paper text does not state
whether those curves are 30-run averages or a particular representative run.

Therefore this project freezes H5h as:

    COMPLETE_CONTROLLED_EQUIVALENT

Representative-run protocol:
    N = 30
    MaxIter = 500
    optimizer seed = 1000  (H5 formal run 1)
    objective seed = 5_024_000 + 100*function_number + 1

All nine algorithms use the same function-specific objective seed. For F7 this
controls the stochastic objective RNG; deterministic functions ignore it.

The script reruns one convergence trajectory per algorithm/function (207 runs),
checks the returned final score against H5_CLASSICAL_V1 run-1 raw results, and
stores every raw convergence curve before plotting.

It does NOT modify any optimizer and does NOT claim pixel/numeric exactness to
the paper's Fig. 9.

Outputs
-------
results/raw/h5h_fig9_curves/*.npz
results/raw/scho_h5h_fig9_curves.npz
report/figures/scho_fig9_part1_F1_F8.png
report/figures/scho_fig9_part2_F9_F16.png
report/figures/scho_fig9_part3_F17_F23.png
report/figures/scho_fig9_all23.png
report/notes/H5h_fig9_protocol.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from algorithms.gwo import gwo
from algorithms.scho import scho
from algorithms.alo import alo
from algorithms.sca import sca
from algorithms.ssa import ssa
from algorithms.aoa import aoa
from algorithms.rsa import rsa
from algorithms.sea_horse import sho
from algorithms.gjo import gjo
from benchmarks.classic_23 import get_benchmark


PROTOCOL_ID = "H5_CLASSICAL_V1"
H5H_PROTOCOL = "H5H_FIG9_CONTROLLED_EQUIVALENT_V1"

ALGORITHMS = (
    "SCHO",
    "GWO",
    "ALO",
    "SCA",
    "SSA",
    "AOA",
    "RSA",
    "SHO",
    "GJO",
)
FUNCTIONS = tuple(f"F{i}" for i in range(1, 24))

N = 30
MAX_ITER = 500
OPTIMIZER_SEED = 1000
RUN_NUMBER = 1
OBJECTIVE_SEED_BASE = 5_024_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
H5_RAW_PATH = (
    PROJECT_ROOT / "results" / "raw" / "scho_classical_h5_runs.csv"
)
CURVE_DIR = (
    PROJECT_ROOT / "results" / "raw" / "h5h_fig9_curves"
)
CONSOLIDATED_PATH = (
    PROJECT_ROOT / "results" / "raw" / "scho_h5h_fig9_curves.npz"
)
FIGURE_DIR = PROJECT_ROOT / "report" / "figures"
NOTE_PATH = PROJECT_ROOT / "report" / "notes" / "H5h_fig9_protocol.md"

ALGORITHM_FUNCS = {
    "SCHO": scho,
    "GWO": gwo,
    "ALO": alo,
    "SCA": sca,
    "SSA": ssa,
    "AOA": aoa,
    "RSA": rsa,
    "SHO": sho,
    "GJO": gjo,
}

# Classical positive-valued functions where logarithmic-looking scaling is
# useful. We use symlog rather than log so preserved source quirks such as
# curve[0] == 0 remain visible instead of being altered.
SYMLOG_FUNCTIONS = {
    "F1", "F2", "F3", "F4", "F5", "F6", "F7",
    "F9", "F10", "F11", "F12", "F13",
}


def function_number(name: str) -> int:
    return int(name[1:])


def objective_seed(name: str) -> int:
    return OBJECTIVE_SEED_BASE + 100 * function_number(name) + RUN_NUMBER


def task_path(algorithm: str, function_name: str) -> Path:
    return CURVE_DIR / f"{algorithm}_{function_name}.npz"


def load_expected_scores() -> dict[tuple[str, str], float]:
    if not H5_RAW_PATH.exists():
        raise FileNotFoundError(
            f"H5 raw dataset not found: {H5_RAW_PATH}"
        )

    with H5_RAW_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    expected: dict[tuple[str, str], float] = {}

    for row in rows:
        if row["ProtocolID"] != PROTOCOL_ID:
            raise RuntimeError(
                f"Unexpected protocol in H5 raw file: {row['ProtocolID']}"
            )
        if int(row["Run"]) != RUN_NUMBER:
            continue

        key = (row["Algorithm"], row["Function"])
        if key in expected:
            raise RuntimeError(f"Duplicate run-1 H5 raw key: {key}")

        score = float(row["BestScore"])
        if not math.isfinite(score):
            raise RuntimeError(f"Non-finite H5 score at {key}")

        expected[key] = score

    required = {
        (algorithm, function_name)
        for function_name in FUNCTIONS
        for algorithm in ALGORITHMS
    }

    if set(expected) != required:
        raise RuntimeError(
            f"H5 run-1 coverage mismatch: "
            f"missing={len(required - set(expected))}, "
            f"extra={len(set(expected) - required)}"
        )

    return expected


def run_one(task: tuple[str, str]) -> dict[str, Any]:
    algorithm, function_name = task

    b = get_benchmark(function_name)
    obj_seed = objective_seed(function_name)
    objective = b.make_objective(seed=obj_seed)
    optimizer = ALGORITHM_FUNCS[algorithm]

    started = time.perf_counter()

    if algorithm == "AOA":
        score, pos, curve = optimizer(
            objective,
            b.dim,
            b.lb,
            b.ub,
            N,
            MAX_ITER,
            seed=OPTIMIZER_SEED,
            mu=0.5,
        )
    else:
        score, pos, curve = optimizer(
            objective,
            b.dim,
            b.lb,
            b.ub,
            N,
            MAX_ITER,
            seed=OPTIMIZER_SEED,
        )

    elapsed = time.perf_counter() - started

    score = float(score)
    pos = np.asarray(pos, dtype=float)
    curve = np.asarray(curve, dtype=float)

    if not math.isfinite(score):
        raise RuntimeError(
            f"{algorithm}/{function_name}: non-finite score"
        )
    if pos.shape != (b.dim,):
        raise RuntimeError(
            f"{algorithm}/{function_name}: pos shape={pos.shape}, "
            f"expected {(b.dim,)}"
        )
    if not np.all(np.isfinite(pos)):
        raise RuntimeError(
            f"{algorithm}/{function_name}: non-finite position"
        )
    if curve.shape != (MAX_ITER,):
        raise RuntimeError(
            f"{algorithm}/{function_name}: curve shape={curve.shape}, "
            f"expected {(MAX_ITER,)}"
        )
    if not np.all(np.isfinite(curve)):
        raise RuntimeError(
            f"{algorithm}/{function_name}: non-finite curve"
        )

    return {
        "algorithm": algorithm,
        "function": function_name,
        "score": score,
        "position": pos,
        "curve": curve,
        "objective_seed": obj_seed,
        "elapsed": float(elapsed),
        "dim": int(b.dim),
    }


def save_task_result(
    result: dict[str, Any],
    expected_score: float,
) -> None:
    algorithm = str(result["algorithm"])
    function_name = str(result["function"])
    path = task_path(algorithm, function_name)

    actual = float(result["score"])

    # Same optimizer seed and the formal run-1 benchmark stream must reproduce
    # the H5 raw score exactly. Deterministic functions ignore the historical
    # SCHO objective seed difference, so exact equality remains expected.
    if actual != expected_score:
        raise RuntimeError(
            f"{algorithm}/{function_name}: rerun score mismatch. "
            f"actual={actual!r}, H5_run1={expected_score!r}"
        )

    metadata = {
        "H5hProtocol": H5H_PROTOCOL,
        "H5Protocol": PROTOCOL_ID,
        "Algorithm": algorithm,
        "Function": function_name,
        "Run": RUN_NUMBER,
        "OptimizerSeed": OPTIMIZER_SEED,
        "ObjectiveSeed": int(result["objective_seed"]),
        "Population": N,
        "MaxIter": MAX_ITER,
        "Dim": int(result["dim"]),
        "BestScore": actual,
        "H5Run1BestScore": expected_score,
        "ScoreRegressionExact": True,
        "RuntimeSeconds": float(result["elapsed"]),
    }

    path.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        path,
        curve=np.asarray(result["curve"], dtype=float),
        position=np.asarray(result["position"], dtype=float),
        metadata_json=np.asarray(
            json.dumps(metadata, ensure_ascii=False)
        ),
    )


def validate_existing_file(
    path: Path,
    algorithm: str,
    function_name: str,
    expected_score: float,
) -> None:
    with np.load(path, allow_pickle=False) as data:
        curve = np.asarray(data["curve"], dtype=float)
        position = np.asarray(data["position"], dtype=float)
        meta = json.loads(str(data["metadata_json"].item()))

    b = get_benchmark(function_name)

    if meta["H5hProtocol"] != H5H_PROTOCOL:
        raise RuntimeError(f"Protocol mismatch in {path}")
    if meta["Algorithm"] != algorithm:
        raise RuntimeError(f"Algorithm mismatch in {path}")
    if meta["Function"] != function_name:
        raise RuntimeError(f"Function mismatch in {path}")
    if int(meta["OptimizerSeed"]) != OPTIMIZER_SEED:
        raise RuntimeError(f"Optimizer seed mismatch in {path}")
    if int(meta["ObjectiveSeed"]) != objective_seed(function_name):
        raise RuntimeError(f"Objective seed mismatch in {path}")
    if int(meta["Population"]) != N:
        raise RuntimeError(f"Population mismatch in {path}")
    if int(meta["MaxIter"]) != MAX_ITER:
        raise RuntimeError(f"MaxIter mismatch in {path}")
    if float(meta["BestScore"]) != expected_score:
        raise RuntimeError(f"H5 regression mismatch in {path}")
    if curve.shape != (MAX_ITER,):
        raise RuntimeError(f"Curve shape mismatch in {path}")
    if position.shape != (b.dim,):
        raise RuntimeError(f"Position shape mismatch in {path}")
    if not np.all(np.isfinite(curve)):
        raise RuntimeError(f"Non-finite curve in {path}")
    if not np.all(np.isfinite(position)):
        raise RuntimeError(f"Non-finite position in {path}")


def build_pending(
    expected_scores: dict[tuple[str, str], float]
) -> tuple[list[tuple[str, str]], int]:
    CURVE_DIR.mkdir(parents=True, exist_ok=True)

    pending: list[tuple[str, str]] = []
    complete = 0

    # Function-major ordering makes --max-new-runs 9 a full F1 smoke.
    for function_name in FUNCTIONS:
        for algorithm in ALGORITHMS:
            path = task_path(algorithm, function_name)
            expected = expected_scores[(algorithm, function_name)]

            if path.exists():
                validate_existing_file(
                    path,
                    algorithm,
                    function_name,
                    expected,
                )
                complete += 1
            else:
                pending.append((algorithm, function_name))

    return pending, complete


def load_all_curves() -> dict[tuple[str, str], np.ndarray]:
    curves: dict[tuple[str, str], np.ndarray] = {}

    for function_name in FUNCTIONS:
        for algorithm in ALGORITHMS:
            path = task_path(algorithm, function_name)
            if not path.exists():
                raise RuntimeError(f"Missing curve file: {path}")

            with np.load(path, allow_pickle=False) as data:
                curves[(algorithm, function_name)] = np.asarray(
                    data["curve"],
                    dtype=float,
                )

    return curves


def write_consolidated(
    curves: dict[tuple[str, str], np.ndarray]
) -> None:
    arrays: dict[str, np.ndarray] = {}

    for function_name in FUNCTIONS:
        for algorithm in ALGORITHMS:
            arrays[f"{algorithm}__{function_name}"] = curves[
                (algorithm, function_name)
            ]

    metadata = {
        "H5hProtocol": H5H_PROTOCOL,
        "Algorithms": list(ALGORITHMS),
        "Functions": list(FUNCTIONS),
        "Population": N,
        "MaxIter": MAX_ITER,
        "Run": RUN_NUMBER,
        "OptimizerSeed": OPTIMIZER_SEED,
        "ObjectiveSeedRule": (
            "5024000 + 100*function_number + 1"
        ),
        "Exactness": "CONTROLLED_EQUIVALENT",
    }

    arrays["metadata_json"] = np.asarray(
        json.dumps(metadata, ensure_ascii=False)
    )

    CONSOLIDATED_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CONSOLIDATED_PATH, **arrays)


def symlog_linthresh(curves: list[np.ndarray]) -> float:
    values = np.concatenate(curves)
    nonzero = np.abs(values[np.nonzero(values)])

    if nonzero.size == 0:
        return 1e-12

    # A robust threshold keeps the near-zero region visible without
    # changing any stored convergence value.
    q = float(np.quantile(nonzero, 0.05))
    return max(q, np.finfo(float).tiny)


def plot_group(
    function_names: tuple[str, ...],
    output_path: Path,
    curves: dict[tuple[str, str], np.ndarray],
    ncols: int,
) -> None:
    n = len(function_names)
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(4.0 * ncols, 3.1 * nrows),
        squeeze=False,
    )

    x = np.arange(1, MAX_ITER + 1)

    for idx, function_name in enumerate(function_names):
        ax = axes[idx // ncols][idx % ncols]

        function_curves = []

        for algorithm in ALGORITHMS:
            y = curves[(algorithm, function_name)]
            function_curves.append(y)
            ax.plot(
                x,
                y,
                linewidth=1.1,
                label=algorithm,
            )

        if function_name in SYMLOG_FUNCTIONS:
            ax.set_yscale(
                "symlog",
                linthresh=symlog_linthresh(function_curves),
            )

        ax.set_title(function_name)
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Best score")
        ax.grid(True, alpha=0.25)

    for idx in range(n, nrows * ncols):
        axes[idx // ncols][idx % ncols].axis("off")

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=9,
        bbox_to_anchor=(0.5, 1.0),
        fontsize=8,
    )

    fig.suptitle(
        "SCHO Fig. 9 controlled-equivalent convergence curves",
        y=1.025,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_figures(
    curves: dict[tuple[str, str], np.ndarray]
) -> None:
    plot_group(
        tuple(f"F{i}" for i in range(1, 9)),
        FIGURE_DIR / "scho_fig9_part1_F1_F8.png",
        curves,
        ncols=4,
    )
    plot_group(
        tuple(f"F{i}" for i in range(9, 17)),
        FIGURE_DIR / "scho_fig9_part2_F9_F16.png",
        curves,
        ncols=4,
    )
    plot_group(
        tuple(f"F{i}" for i in range(17, 24)),
        FIGURE_DIR / "scho_fig9_part3_F17_F23.png",
        curves,
        ncols=4,
    )
    plot_group(
        FUNCTIONS,
        FIGURE_DIR / "scho_fig9_all23.png",
        curves,
        ncols=5,
    )


def write_note() -> None:
    NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)

    text = f"""# H5h — SCHO Fig. 9 protocol freeze

Status:

`SCHO_FIG9_COMPLETE_CONTROLLED_EQUIVALENT`

## Paper structure

Fig. 9 compares SCHO with GWO, ALO, SCA, SSA, AOA, RSA, SHO, and GJO on
F1–F23 using convergence curves.

The accessible paper text/caption does not state whether the displayed curves
are 30-run averages or a selected representative run. Therefore this project
does not claim exact run-selection or aggregation equivalence.

## Controlled-equivalent protocol

- F1–F13: D=30
- F14–F23: native dimension
- N={N}
- MaxIter={MAX_ITER}
- representative H5 run={RUN_NUMBER}
- optimizer seed={OPTIMIZER_SEED}
- objective seed=`{OBJECTIVE_SEED_BASE} + 100*function_number + {RUN_NUMBER}`
- NumPy RNG; no MATLAB bitwise RNG equivalence
- AOA uses H5 Table 6 `mu=0.5`
- SHO means Sea-Horse Optimizer
- frozen GWO/SCHO are not modified

Every rerun final score is checked for exact equality against the corresponding
H5_CLASSICAL_V1 run-1 raw `BestScore`.

## Plotting layer

Raw optimizer curves are stored unchanged.

For functions whose scores span many orders of magnitude, the plotting layer
uses `symlog` rather than silently replacing source-preserved zeros. Functions
with naturally negative optima are shown on a linear y-axis.

This plotting choice is controlled-equivalent and is not claimed to reproduce
the paper's exact axis transform or pixel layout.
"""

    NOTE_PATH.write_text(text, encoding="utf-8")


def finalize() -> None:
    curves = load_all_curves()
    write_consolidated(curves)
    write_figures(curves)
    write_note()

    print("-" * 116)
    print("H5h RESULT: COMPLETE_CONTROLLED_EQUIVALENT")
    print(f"Curve files   : {CURVE_DIR}")
    print(f"Consolidated  : {CONSOLIDATED_PATH}")
    print(f"Figures       : {FIGURE_DIR}")
    print(f"Protocol note : {NOTE_PATH}")
    print(
        "All 207 final scores regress exactly to H5_CLASSICAL_V1 run-1 results."
    )
    print("=" * 116)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H5h controlled-equivalent SCHO Fig.9 convergence curves."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="ProcessPoolExecutor workers (default: 4).",
    )
    parser.add_argument(
        "--max-new-runs",
        type=int,
        default=None,
        help=(
            "Optional cap on new curve runs for smoke testing. "
            "Use 9 to execute all algorithms on F1."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.workers < 1:
        raise ValueError("--workers must be >= 1")
    if args.max_new_runs is not None and args.max_new_runs < 1:
        raise ValueError("--max-new-runs must be >= 1")

    expected_scores = load_expected_scores()
    pending, complete = build_pending(expected_scores)

    print("=" * 116)
    print("H5h - SCHO Fig. 9 controlled-equivalent convergence curves")
    print("=" * 116)
    print(
        f"Algorithms={len(ALGORITHMS)} | Functions={len(FUNCTIONS)} | "
        f"total curves={len(ALGORITHMS) * len(FUNCTIONS)}"
    )
    print(
        f"N={N} | MaxIter={MAX_ITER} | optimizer seed={OPTIMIZER_SEED} | "
        "representative formal run=1"
    )
    print(
        "Objective seed rule: "
        f"{OBJECTIVE_SEED_BASE} + 100*function_number + {RUN_NUMBER}"
    )
    print(
        "Exactness: CONTROLLED_EQUIVALENT; paper text does not expose "
        "the Fig.9 run-selection/aggregation rule."
    )
    print(f"Already complete: {complete}/207")
    print(f"Pending         : {len(pending)}/207")
    print("=" * 116)

    if not pending:
        finalize()
        return

    tasks = pending
    if args.max_new_runs is not None:
        tasks = tasks[: args.max_new_runs]

    print()
    print(
        f"Executing {len(tasks)} curve run(s) with {args.workers} worker(s)..."
    )

    started = time.perf_counter()
    completed_now = 0

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        future_to_task = {
            executor.submit(run_one, task): task
            for task in tasks
        }

        for future in as_completed(future_to_task):
            task = future_to_task[future]

            try:
                result = future.result()
            except Exception as exc:
                raise RuntimeError(
                    f"H5h worker failed for task={task}"
                ) from exc

            key = (
                str(result["algorithm"]),
                str(result["function"]),
            )
            save_task_result(
                result,
                expected_scores[key],
            )

            completed_now += 1
            elapsed = time.perf_counter() - started

            print(
                f"[{completed_now:>3}/{len(tasks)}] "
                f"{key[0]}/{key[1]} "
                f"score={float(result['score']):.10e} "
                f"regression=PASS elapsed={elapsed:.1f}s"
            )

    remaining, complete_after = build_pending(expected_scores)

    print()
    print("-" * 116)
    print(f"Completed this invocation: {completed_now}")
    print(f"Total complete           : {complete_after}/207")
    print(f"Remaining                : {len(remaining)}")

    if remaining:
        print("H5h RESULT: PARTIAL_CHECKPOINTED")
        print("Re-run the same command to resume.")
        print("=" * 116)
        return

    finalize()


if __name__ == "__main__":
    main()
