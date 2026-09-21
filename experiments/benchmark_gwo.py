import csv
from pathlib import Path

import numpy as np

from algorithms.gwo import gwo
from benchmarks.classic_23 import get_benchmark


# GWO 原论文中 23 个经典 benchmark 的平均值（Ave）。
# 用于与本次 Python 复现实验的 Mean 做直接对比。
PAPER_GWO_MEAN = {
    "F1": 6.59e-28,
    "F2": 7.18e-17,
    "F3": 3.29e-06,
    "F4": 5.61e-07,
    "F5": 26.81258,
    "F6": 0.816579,
    "F7": 0.002213,
    "F8": -6123.1,
    "F9": 0.310521,
    "F10": 1.06e-13,
    "F11": 0.004485,
    "F12": 0.053438,
    "F13": 0.654464,
    "F14": 4.042493,
    "F15": 0.000337,
    "F16": -1.03163,
    "F17": 0.397889,
    "F18": 3.000028,
    "F19": -3.86263,
    "F20": -3.28654,
    "F21": -10.1514,
    "F22": -10.4015,
    "F23": -10.5343,
}


def run_benchmark(
    benchmark_name,
    n_runs=30,
    N=30,
    MaxIter=500,
    verbose=True,
):
    """
    对指定 benchmark 独立运行 GWO，并返回统计结果。
    """

    benchmark = get_benchmark(benchmark_name)
    scores = []

    if verbose:
        print("=" * 60)
        print(f"GWO on {benchmark.name}")
        print("=" * 60)

    for run in range(n_runs):
        seed = 1000 + run
        objective = benchmark.make_objective(seed=seed)

        best_score, best_pos, convergence_curve = gwo(
            obj_func=objective,
            dim=benchmark.dim,
            lb=benchmark.lb,
            ub=benchmark.ub,
            N=N,
            MaxIter=MaxIter,
            seed=seed,
        )

        scores.append(best_score)

        if verbose:
            print(f"Run {run + 1:02d}: {best_score:.6e}")

    scores = np.asarray(scores, dtype=float)

    mean = float(np.mean(scores))
    std = float(np.std(scores))
    best = float(np.min(scores))
    worst = float(np.max(scores))
    optimum = float(benchmark.optimum)
    paper_mean = PAPER_GWO_MEAN.get(benchmark.name, np.nan)

    result = {
        "Function": benchmark.name,
        "Runs": n_runs,
        "Population": N,
        "MaxIter": MaxIter,
        "Mean": mean,
        "Std": std,
        "Best": best,
        "Worst": worst,
        "Theoretical_Optimum": optimum,
        "Paper_Mean": paper_mean,
        "Mean_Difference": mean - paper_mean if np.isfinite(paper_mean) else np.nan,
        "Abs_Mean_Difference": abs(mean - paper_mean) if np.isfinite(paper_mean) else np.nan,
    }

    if verbose:
        print("\nStatistics")
        print("-" * 60)
        print(f"Mean  = {mean:.6e}")
        print(f"Std   = {std:.6e}")
        print(f"Best  = {best:.6e}")
        print(f"Worst = {worst:.6e}")
        print(f"Theoretical optimum = {optimum:.6e}")
        print(f"Paper GWO mean      = {paper_mean:.6e}")
        print(f"Mean difference      = {result['Mean_Difference']:.6e}")

    return result


def save_results_csv(results, output_path):
    """
    将 F1-F23 汇总结果保存为 CSV。
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Function",
        "Runs",
        "Population",
        "MaxIter",
        "Mean",
        "Std",
        "Best",
        "Worst",
        "Theoretical_Optimum",
        "Paper_Mean",
        "Mean_Difference",
        "Abs_Mean_Difference",
    ]

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def run_all_classic23(
    n_runs=30,
    N=30,
    MaxIter=500,
):
    """
    一次运行 F1-F23，汇总结果并保存到 results/processed/。
    """
    all_results = []

    for i in range(1, 24):
        func_name = f"F{i}"

        print("\n" + "=" * 70)
        print(f"Running {func_name} ({i}/23)")
        print("=" * 70)

        result = run_benchmark(
            benchmark_name=func_name,
            n_runs=n_runs,
            N=N,
            MaxIter=MaxIter,
            verbose=True,
        )

        all_results.append(result)

    project_root = Path(__file__).resolve().parents[1]
    output_path = (
        project_root
        / "results"
        / "processed"
        / "gwo_classic23_results.csv"
    )

    save_results_csv(all_results, output_path)

    print("\n" + "=" * 70)
    print("F1-F23 全部运行完成")
    print("=" * 70)
    print(f"结果已保存到: {output_path}")

    print("\nSummary")
    print("-" * 110)
    print(
        f"{'Func':<6}"
        f"{'Mean':>16}"
        f"{'Std':>16}"
        f"{'Best':>16}"
        f"{'Paper Mean':>16}"
        f"{'Difference':>18}"
    )
    print("-" * 110)

    for r in all_results:
        print(
            f"{r['Function']:<6}"
            f"{r['Mean']:>16.6e}"
            f"{r['Std']:>16.6e}"
            f"{r['Best']:>16.6e}"
            f"{r['Paper_Mean']:>16.6e}"
            f"{r['Mean_Difference']:>18.6e}"
        )

    return all_results


if __name__ == "__main__":
    run_all_classic23(
        n_runs=30,
        N=30,
        MaxIter=500,
    )
