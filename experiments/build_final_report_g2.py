"""G2 - Build integrated final reproduction-report draft.

No optimizer is rerun. Frozen Stage D/E/F/G1 conclusions are assembled into
one Markdown draft plus a claim-provenance matrix.
"""

from __future__ import annotations
import csv
from pathlib import Path

G1 = Path("report/stage_g1_integrated_numerical_summary.md")
D3 = Path("report/notes/D3_StageD_final_report.md")
F6 = Path("report/stage_f_engineering_final.md")
G0 = Path("report/stage_g0_evidence_audit.md")

OUT = Path("report/final_reproduction_report_draft.md")
CLAIMS = Path("report/tables/stage_g2_claims_matrix.csv")


def require(p: Path):
    if not p.exists():
        raise FileNotFoundError(f"Required input missing: {p}")


def text(p: Path) -> str:
    return p.read_text(encoding="utf-8").strip()


def write_claims():
    rows = [
        ["C01","Classic F1-F23","GWO lower mean 8, SCHO 12, Tie 3","Stage D / G1","frozen"],
        ["C02","CEC2014","Reproduction lower mean GWO 22, SCHO 8; 9 pairwise flips","Stage E / G1","frozen"],
        ["C03","CEC2014","Within ±25% of paper mean error: GWO 22/30, SCHO 14/30","Stage E / G1","frozen"],
        ["C04","Engineering","360/360 runs; 288 feasible; 72 NO_FEASIBLE_FOUND; 0 structural failures","Stage F / G1","frozen"],
        ["C05","Engineering","Speed reducer feasible runs: GWO 1/30, SCHO 14/30","Stage F5 / G1","frozen"],
        ["C06","Source anomaly","Cantilever 0.6224 printed objective conflicts with Table 20 scale; 0.06224 is diagnostic only","Stage F0-F6","frozen"],
        ["C07","Source anomaly","Spring g2 terminal -1 is required for paper-point feasibility","Stage F0-F1","frozen"],
        ["C08","Implementation","SCHO keeps source-faithful implementation behavior rather than an idealized rewrite","Stage C freeze","frozen"],
        ["C09","Reproducibility","NumPy RNG is not MATLAB RNG; no bitwise MATLAB claim","Project methodology","frozen"],
        ["C10","Interpretation","Stochastic deviations were retained rather than tuned away","Stages D/E/F","frozen"],
    ]
    CLAIMS.parent.mkdir(parents=True, exist_ok=True)
    with CLAIMS.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["claim_id","section","claim","evidence","status"])
        w.writerows(rows)
    return len(rows)


def build(g1, d3, f6, g0):
    return f"""# GWO 与 SCHO 元启发式算法复现实验总报告（Draft）

## 摘要

本项目复现 Grey Wolf Optimizer（GWO）与 Sinh Cosh Optimizer（SCHO），并依次完成经典 F1–F23、CEC2014 与 6 个约束工程设计问题。复现原则不是追求与 MATLAB 逐随机数位一致，而是尽量保持论文/公开源码行为、实验尺度和 benchmark 定义，同时显式保留随机差异、约束失败与论文内部不一致。

总体上，经典函数中两种算法各有优势区间；CEC2014 中 GWO 的论文尺度整体复现较稳定，而 SCHO 在本项目协议下没有完整复现论文中的相对优势；工程问题中，最佳可行解通常接近论文参考尺度，但纯 death penalty 对 welded beam 与 speed reducer 的可行率影响明显。

## 1. 研究目标与复现原则

项目目标包括：建立与官方/公开源码一致的算法基线；复现经典函数和 CEC2014 数值尺度；验证约束工程问题；记录公式、表格、源码之间的不一致。全过程坚持“不为了贴近论文而事后调参”，并用 Git freeze 保存关键阶段。

## 2. 算法实现

### 2.1 GWO

GWO 以官方 MATLAB 源码行为为基准，保留 Alpha/Beta/Delta 更新逻辑、参数 `a` 的线性衰减和随机调用结构。Python 使用 NumPy RNG，因此不主张 MATLAB bitwise reproduction。

### 2.2 SCHO

SCHO 采用 source-faithful 原则，保留源码中的实际 phase 切换、A 参数逐坐标计算、非对称边界处理、动态 bounded 行为、历史最优和 second-best 相关实现，而不是改写成更理想化的版本。

## 3. 经典 F1–F23

冻结的 Stage D 结果为：GWO lower mean 8，SCHO 12，Tie 3。按族划分：F1–F7 为 1/4/2，F8–F13 为 2/3/1，F14–F23 为 5/5/0。由此只能说明不同函数族上的相对表现不同，不能压缩成单一全面优势结论。

## 4. CEC2014

Stage E 在 F1–F30、D=10 下完成复现。GWO 有 22/30 个函数的 mean error 落在论文值 ±25% 内，30/30 在 factor 2 内；SCHO 分别为 14/30 与 26/30。论文 pairwise lower-mean 为 SCHO 17、GWO 13，而复现得到 GWO 22、SCHO 8，共 9 个 pairwise flip。

冻结解释是：GWO 的整体尺度较好复现；SCHO 的论文相对优势未在本项目协议下完整重现。F21 呈 heavy-tail/outlier 特征，F15 为长尾，F2 更像整体上移，F23/F27 存在 deterministic plateau mismatch；不把这些差异归结为单一原因。

## 5. 工程设计

Stage F 实现 spring、pressure vessel、welded beam、speed reducer、cantilever beam、three-bar truss。项目工程协议为 `N=30`、`MaxIter=500`、30 runs、seeds 1000–1029、death penalty `1e30`、feasibility tolerance `1e-8`。这套完整数值协议属于 project reproduction convention。

360 次工程优化全部完成：288 次 feasible，72 次 `NO_FEASIBLE_FOUND`，0 structural failures。Speed reducer 中 GWO 仅 1/30 次找到可行解，SCHO 为 14/30；welded beam 中 GWO 18/30、SCHO 19/30。因此工程问题必须同时报告 feasible rate 与 feasible-only objective statistics。

## 6. Source anomalies

### 6.1 Spring

边界行的最后一个变量按上下文冻结为 `x3 in [2,15]`。论文印刷 g2 缺少末尾 `-1`；论文报告点在印刷版下约为 `+0.9999994`，修正后约为 `-6.0e-7`，与其可行性一致。

### 6.2 Cantilever

论文印刷目标为 `0.6224*sum(x)`，在 Table 20 报告点上约为 `13.0326`，而表中报告 `1.3033`。`0.06224*sum(x)` 可得到约 `1.30326`，但这只能作为 table-consistent diagnostic，不能冒充论文已经确认的正确公式。

### 6.3 离散变量

Pressure vessel 与 speed reducer 存在语义上可能离散/整数的变量，但 SCHO 工程章节没有给出投影规则，因此主复现不擅自加入离散化。

## 7. 综合讨论

三个 benchmark 家族揭示不同层面的行为：经典函数主要观察基础搜索行为与随机稳定性；CEC2014 检验复杂 landscape 上的尺度复现；工程问题进一步暴露约束可行性与 penalty strategy。最终解释因此分开保留 source fidelity、objective/error quality、stochastic variation、feasibility success 与 source anomaly。

## 8. 局限性

Python/NumPy RNG 与 MATLAB RNG 不同；部分工程协议未在论文中完整给出；source-faithful SCHO 保留了源码中的不常见行为；death penalty 对小可行域问题非常敏感。因此结果应解释为可审计的 reproduction，而不是逐位复刻。

## 9. 可复现性

关键冻结 tag 包括：

- `scho-source-faithful-v1`
- `stage-e-cec2014-v1`
- `stage-f-engineering-v1`

Stage G 只整合冻结证据，不重新运行优化器，不修改算法基线。

## 10. 结论

本项目完成了从源码审计、经典 benchmark、CEC2014 到约束工程设计的完整复现链。结果表明，元启发式复现不能只看单个最优值；必须同时考虑实现细节、随机性、benchmark 定义、约束可行性和论文自身的不一致。能够复现的结果与不能完整复现的结果都被保留下来，而不是通过调参消除差异。

---

## Appendix A — G1 frozen numerical summary

{g1}

---

## Appendix B — Stage D final report

{d3}

---

## Appendix C — Stage F final report

{f6}

---

## Appendix D — G0 evidence audit

{g0}
"""


def main():
    print("=" * 112)
    print("G2 - Integrated final report draft")
    print("=" * 112)
    print("No optimizer will be executed.")

    for p in [G1, D3, F6, G0]:
        require(p)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(text(G1), text(D3), text(F6), text(G0)), encoding="utf-8")
    n = write_claims()

    print("\nOutputs")
    print("-" * 112)
    print(f"Draft report : {OUT}")
    print(f"Claims matrix: {CLAIMS}")
    print(f"Claims       : {n}")
    print("\nG2 RESULT: PASS")
    print("No optimizer was rerun.")
    print("Frozen Stage D/E/F/G1 conclusions were preserved.")
    print("Stage G is ready for G3 consistency/formatting QA.")


if __name__ == "__main__":
    main()
