"""F6 - Finalize and freeze Stage F engineering-design reproduction.

This script does NOT run GWO or SCHO.

It validates the completed F4/F5 artifacts, writes the final Stage-F report,
and creates a SHA-256 manifest for the intended Stage-F files.

Outputs
-------
report/stage_f_engineering_final.md
report/stage_f_manifest.csv

Important
---------
- No optimizer source file is modified.
- Historical experiments/engineering_gwo.py and engineering_scho.py are not
  part of this Stage-F manifest.
- Git commit/tag creation is intentionally NOT automated here. Freeze only
  after reviewing this script's output and `git status`.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Dict, List

import numpy as np


# ---------------------------------------------------------------------------
# Stage-F inputs
# ---------------------------------------------------------------------------

F4_RAW = Path("results/raw/engineering_f4_runs.csv")
F4_SUMMARY = Path("results/processed/engineering_f4_summary.csv")
F5_COMPARISON = Path("results/processed/engineering_f5_paper_comparison.csv")
F5_SEEDS = Path("results/processed/engineering_f5_seed_diagnostics.csv")
F5_REPORT = Path("report/engineering_f5_analysis.md")

FINAL_REPORT = Path("report/stage_f_engineering_final.md")
MANIFEST = Path("report/stage_f_manifest.csv")

# Files that should exist because they were directly used in F1-F5.
REQUIRED_STAGE_F_FILES = [
    Path("benchmarks/engineering_design.py"),
    Path("benchmarks/constraint_handling.py"),
    Path("experiments/test_engineering_f1.py"),
    Path("experiments/test_engineering_f2.py"),
    Path("experiments/test_engineering_f3_all6.py"),
    Path("experiments/benchmark_engineering_f4.py"),
    Path("experiments/analyze_engineering_f5.py"),
    Path("results/raw/engineering_f3_single_run.csv"),
    F4_RAW,
    F4_SUMMARY,
    F5_COMPARISON,
    F5_SEEDS,
    F5_REPORT,
]

# Useful source-audit note if the user placed it in the suggested location.
OPTIONAL_STAGE_F_FILES = [
    Path("report/notes/F0_engineering_protocol_audit.md"),
]


def require(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Required Stage-F file is missing: {path}")


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def as_float(value):
    if value is None or value == "":
        return np.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def as_int(value):
    return int(float(value))


def fmt(x, sig=10):
    x = float(x)
    if not np.isfinite(x):
        return "NaN"
    return f"{x:.{sig}g}"


def pct_from_rate(rate):
    return f"{100.0 * float(rate):.1f}%"


def pct_value(value):
    value = float(value)
    if not np.isfinite(value):
        return "N/A"
    return f"{value:+.3f}%"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_inputs():
    for path in REQUIRED_STAGE_F_FILES:
        require(path)

    raw = read_csv(F4_RAW)
    summary = read_csv(F4_SUMMARY)
    comparison = read_csv(F5_COMPARISON)
    seeds = read_csv(F5_SEEDS)

    if len(raw) != 360:
        raise ValueError(f"Expected 360 F4 raw rows, got {len(raw)}")
    if len(summary) != 12:
        raise ValueError(f"Expected 12 F4 summary rows, got {len(summary)}")
    if len(comparison) != 12:
        raise ValueError(
            f"Expected 12 F5 comparison rows, got {len(comparison)}"
        )
    if len(seeds) != 6:
        raise ValueError(f"Expected 6 F5 seed rows, got {len(seeds)}")

    structural = [
        r for r in raw
        if r["status"] in {"ERROR", "STRUCTURAL_FAIL"}
    ]
    no_feasible = [
        r for r in raw
        if r["status"] == "NO_FEASIBLE_FOUND"
    ]
    feasible = [
        r for r in raw
        if r["status"] == "PASS"
    ]

    if structural:
        raise ValueError(
            f"F4 contains {len(structural)} structural failures; "
            "Stage F should not be frozen."
        )

    return {
        "raw": raw,
        "summary": summary,
        "comparison": comparison,
        "seeds": seeds,
        "feasible_count": len(feasible),
        "no_feasible_count": len(no_feasible),
        "structural_count": len(structural),
    }


def make_lookup(rows, keys):
    return {
        tuple(row[k] for k in keys): row
        for row in rows
    }


def build_report(data):
    summary = make_lookup(
        data["summary"],
        ("problem", "algorithm"),
    )
    comparison = make_lookup(
        data["comparison"],
        ("problem", "algorithm"),
    )
    seeds = {
        row["problem"]: row
        for row in data["seeds"]
    }

    problem_order = [
        ("spring", "Tension/compression spring"),
        ("pressure_vessel", "Pressure vessel"),
        ("welded_beam", "Welded beam"),
        ("speed_reducer", "Speed reducer"),
        ("cantilever_printed", "Cantilever beam"),
        ("three_bar_truss", "Three-bar truss"),
    ]

    lines = []

    lines.append("# Stage F — Engineering Design Reproduction Final Report")
    lines.append("")
    lines.append("## 1. 目标与范围")
    lines.append("")
    lines.append(
        "Stage F 复现 SCHO 论文工程设计部分的 6 个约束优化问题，并将冻结的 "
        "GWO 与冻结的 source-faithful SCHO 接入同一套工程 benchmark。"
    )
    lines.append("")
    lines.append(
        "本阶段重点不是只比较一个最优值，而是同时检查：公式定义、约束可行性、"
        "优化器接口、独立运行的可行率、可行解目标值，以及论文公式本身存在的内部不一致。"
    )
    lines.append("")

    lines.append("## 2. Source-stated 与 project protocol 的区分")
    lines.append("")
    lines.append(
        "SCHO 工程部分明确给出 6 个工程问题，并说明使用 simple death penalty "
        "处理违反约束的候选；但工程章节没有明确重述数值 penalty 常数、seed schedule，"
        "也没有明确给出一套工程专用的 30-run 数值协议。"
    )
    lines.append("")
    lines.append(
        "因此 Stage F 使用以下 **project reproduction protocol**："
    )
    lines.append("")
    lines.append("- Population: `N = 30`")
    lines.append("- Iterations: `MaxIter = 500`")
    lines.append("- Independent runs: `30`")
    lines.append("- Seeds: `1000..1029`")
    lines.append("- Death penalty: `1e30`")
    lines.append("- Feasibility tolerance: `1e-8`")
    lines.append("")
    lines.append(
        "GWO 和 SCHO 在 F4 使用同一 death-penalty handler，这是受控/common-protocol "
        "比较；不能据此声称原始 GWO 工程实验使用了完全相同的约束处理规则。"
    )
    lines.append("")

    lines.append("## 3. F0–F3 实现与确定性验证")
    lines.append("")
    lines.append(
        "F0 对论文 Section 3.3 与 Tables 16–21 进行了逐题公式审计。"
        "F1 将 6 个问题实现为独立 benchmark，并直接代入论文报告的设计点验证 objective、"
        "各约束和 bounds。F2 验证 death-penalty wrapper 与两种冻结优化器的接口。"
        "F3 完成 6 problems × 2 algorithms 的单 seed 全覆盖。"
    )
    lines.append("")
    lines.append("关键冻结决策：")
    lines.append("")
    lines.append(
        "- Spring：论文 bounds 行中的最后一个变量按 `x3 in [2,15]` 解释；"
        "约束 `g2` 使用末尾 `-1` 的修正版，因为论文报告点在印刷版本下约为 "
        "`+0.9999994`，而修正后约为 `-6.0e-7`。"
    )
    lines.append(
        "- Pressure vessel：主复现保持连续变量，不擅自加入论文未说明的 "
        "`0.0625` 厚度离散投影。"
    )
    lines.append(
        "- Speed reducer：不擅自把 `x3` 做整数投影，因为论文没有给出对应实现规则。"
    )
    lines.append(
        "- Cantilever：保留论文印刷目标 `0.6224*sum(x)`；`0.06224` 只作为 "
        "Table-20-consistent diagnostic，绝不冒充论文已确认的正确公式。"
    )
    lines.append(
        "- Three-bar truss：box 包含 `(0,0)`，该点使应力公式奇异；F2 后将这种 "
        "non-finite constraint 正确判为 infeasible + death penalty，而不是让程序崩溃。"
    )
    lines.append("")

    lines.append("## 4. F4 30-run 实验总体结果")
    lines.append("")
    lines.append(
        f"F4 共执行 **360/360** 次优化，其中 **{data['feasible_count']}** 次返回 "
        f"feasible best design，**{data['no_feasible_count']}** 次为 "
        "`NO_FEASIBLE_FOUND`，结构性失败为 **0**。"
    )
    lines.append("")
    lines.append(
        "下表中的 objective 统计只使用 feasible runs；这样不会让 `1e30` death penalty "
        "污染普通 Mean/STD。STD 为 sample STD (`ddof=1`)，所以只有一个 feasible run 时 "
        "STD 正确显示为 `NaN`。"
    )
    lines.append("")
    lines.append(
        "| Problem | Algorithm | Feasible | Best feasible | Mean feasible | "
        "STD feasible |"
    )
    lines.append("|---|---|---:|---:|---:|---:|")

    for problem, _ in problem_order:
        for alg in ("GWO", "SCHO"):
            row = summary[(problem, alg)]
            lines.append(
                f"| {problem} | {alg} | "
                f"{row['feasible_runs']}/{row['runs']} "
                f"({pct_from_rate(row['feasible_rate'])}) | "
                f"{fmt(as_float(row['best_feasible']))} | "
                f"{fmt(as_float(row['mean_feasible']))} | "
                f"{fmt(as_float(row['std_feasible_sample']))} |"
            )

    lines.append("")

    lines.append("## 5. 与论文参考值的数值对照")
    lines.append("")
    lines.append(
        "对于 5 个内部一致的 formulation，F5 将 F4 的 `BestFeasible` 与 SCHO "
        "Tables 16–21 中报告的 objective 进行直接数值对照。Gap 为 "
        "`(BestFeasible - PaperReported) / |PaperReported|`。"
    )
    lines.append("")
    lines.append(
        "| Problem | Algorithm | Feasible | Best feasible | Paper | Gap |"
    )
    lines.append("|---|---|---:|---:|---:|---:|")

    for problem, _ in problem_order:
        if problem == "cantilever_printed":
            continue
        for alg in ("GWO", "SCHO"):
            row = comparison[(problem, alg)]
            lines.append(
                f"| {problem} | {alg} | "
                f"{row['feasible_runs']}/{row['runs']} | "
                f"{fmt(as_float(row['best_feasible']))} | "
                f"{fmt(as_float(row['paper_reported_f']))} | "
                f"{pct_value(as_float(row['best_gap_percent']))} |"
            )

    lines.append("")
    lines.append(
        "这些结果说明，在至少一次进入可行域的前提下，5 个内部一致问题的最佳可行目标值"
        "都能落在论文参考值附近。但这只是数值尺度复现，不能替代对实验协议差异和 stochastic "
        "variation 的说明。"
    )
    lines.append("")

    lines.append("## 6. Feasibility diagnostics")
    lines.append("")
    lines.append(
        "| Problem | Both feasible | GWO-only | SCHO-only | Neither |"
    )
    lines.append("|---|---:|---:|---:|---:|")

    for problem, _ in problem_order:
        row = seeds[problem]
        lines.append(
            f"| {problem} | "
            f"{row['both_feasible']} | "
            f"{row['gwo_only_feasible']} | "
            f"{row['scho_only_feasible']} | "
            f"{row['neither_feasible']} |"
        )

    lines.append("")
    lines.append(
        "Spring、pressure vessel、cantilever 和 three-bar truss 的可行性总体较稳定。"
        "Welded beam 明显更难：paired seeds 为 both=10、GWO-only=8、SCHO-only=9、"
        "neither=3。Speed reducer 是最强的 feasibility bottleneck：GWO 仅 1/30 "
        "找到可行解，SCHO 为 14/30；paired seeds 为 both=0、GWO-only=1、"
        "SCHO-only=14、neither=15。"
    )
    lines.append("")
    lines.append(
        "因此工程问题的结果必须同时报告 feasible rate 和 feasible-objective quality。"
        "单看 Best 会忽略算法是否经常根本无法进入可行域。"
    )
    lines.append("")

    lines.append("## 7. Cantilever 内部不一致")
    lines.append("")
    cg = comparison[("cantilever_printed", "GWO")]
    cs = comparison[("cantilever_printed", "SCHO")]

    lines.append(
        "论文印刷目标函数在 Table-20 报告点上约为 `13.0326`，而 Table 20 报告 "
        "`1.3033`，两者存在约 10 倍尺度差。Stage F 主实验始终保留论文印刷的 "
        "`0.6224`，所以主结果约在 13 的尺度。"
    )
    lines.append("")
    lines.append(
        "| Algorithm | Printed best | Diagnostic 0.06224 | Table 20 | "
        "Diagnostic gap |"
    )
    lines.append("|---|---:|---:|---:|---:|")
    for row in (cg, cs):
        lines.append(
            f"| {row['algorithm']} | "
            f"{fmt(as_float(row['best_feasible']))} | "
            f"{fmt(as_float(row['diagnostic_best_0p06224']))} | "
            f"{fmt(as_float(row['paper_reported_f']))} | "
            f"{pct_value(as_float(row['diagnostic_best_gap_percent']))} |"
        )
    lines.append("")
    lines.append(
        "`0.06224` 结果仅用于说明 Table 20 的数值尺度可以被约 0.1 rescaling 对齐；"
        "本报告不把它声明为论文已经证实的正确公式，也不引入另一个文献变体中的 "
        "first constraint coefficient `61`。"
    )
    lines.append("")

    lines.append("## 8. Stage F 结论")
    lines.append("")
    lines.append(
        "Stage F 已完成从 source audit、benchmark implementation、deterministic validation、"
        "optimizer integration、single-run coverage、360-run experiment 到 paper comparison "
        "的完整闭环。工程 benchmark 层和两种冻结优化器之间没有发现结构性接口问题。"
    )
    lines.append("")
    lines.append(
        "结果表明：当算法成功找到可行域时，5 个内部一致问题的最佳目标值总体能复现到论文"
        "参考尺度附近；但纯 death penalty 的可行性成功率明显依赖问题，尤其 welded beam "
        "和 speed reducer。Cantilever 则应持续作为论文内部公式/表格不一致的特殊案例报告。"
    )
    lines.append("")
    lines.append(
        "本阶段不通过调参消除 `NO_FEASIBLE_FOUND`，也不因为单个 Best 更低就给出算法"
        "普遍优劣结论。Feasible rate、feasible-only objective quality、source anomaly "
        "和 stochastic variation 被保留为彼此独立的证据。"
    )
    lines.append("")

    lines.append("## 9. Freeze scope")
    lines.append("")
    lines.append(
        "Stage F freeze 应包含本阶段新增 benchmark/constraint code、F1–F6 experiment "
        "scripts、F3/F4 raw data、F4/F5 processed data、F5/F6 reports 和 manifest。"
    )
    lines.append("")
    lines.append(
        "不应把历史遗留的 `experiments/engineering_gwo.py` 或 "
        "`experiments/engineering_scho.py` 误纳入 Stage F freeze，除非另外明确审计。"
    )
    lines.append("")
    lines.append(
        "冻结前还应确认 `algorithms/gwo.py` 与 `algorithms/scho.py` 没有被 Stage F 修改。"
    )

    return "\n".join(lines) + "\n"


def write_manifest():
    paths = list(REQUIRED_STAGE_F_FILES)

    for path in OPTIONAL_STAGE_F_FILES:
        if path.exists():
            paths.append(path)

    # F6 outputs themselves are included after the report is written.
    paths.extend([
        Path("experiments/finalize_engineering_f6.py"),
        FINAL_REPORT,
    ])

    rows = []
    for path in paths:
        if not path.exists():
            rows.append({
                "path": str(path).replace("\\", "/"),
                "exists": False,
                "size_bytes": "",
                "sha256": "",
            })
            continue

        rows.append({
            "path": str(path).replace("\\", "/"),
            "exists": True,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["path", "exists", "size_bytes", "sha256"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows


def main():
    print("=" * 120)
    print("F6 - Finalize Stage F engineering reproduction")
    print("=" * 120)
    print("No optimizer will be executed.")
    print("Validating F4/F5 outputs and intended Stage-F files...")
    print("=" * 120)

    data = audit_inputs()

    FINAL_REPORT.parent.mkdir(parents=True, exist_ok=True)
    FINAL_REPORT.write_text(
        build_report(data),
        encoding="utf-8",
    )

    manifest_rows = write_manifest()

    missing_optional = [
        str(p)
        for p in OPTIONAL_STAGE_F_FILES
        if not p.exists()
    ]

    print("\nValidation")
    print("-" * 120)
    print("F4 raw rows             : 360/360")
    print("F4 summary rows         : 12/12")
    print("F5 comparison rows      : 12/12")
    print("F5 seed-diagnostic rows : 6/6")
    print(f"Feasible F4 runs        : {data['feasible_count']}/360")
    print(f"NO_FEASIBLE_FOUND       : {data['no_feasible_count']}")
    print(f"Structural failures     : {data['structural_count']}")

    print("\nOutputs")
    print("-" * 120)
    print(f"Final report : {FINAL_REPORT}")
    print(f"Manifest     : {MANIFEST}")
    print(f"Manifest rows: {len(manifest_rows)}")

    if missing_optional:
        print("\nOptional file not found (does not fail F6):")
        for item in missing_optional:
            print(f"  - {item}")

    print("\nF6 RESULT: PASS")
    print("Stage F is ready for Git review/freeze.")
    print("No Git commit or tag was created automatically.")
    print("algorithms/gwo.py was not modified by F6.")
    print("algorithms/scho.py was not modified by F6.")


if __name__ == "__main__":
    main()
