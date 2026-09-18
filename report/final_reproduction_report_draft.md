# GWO 与 SCHO 元启发式算法复现实验总报告（Draft）

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

# Stage G1 — Integrated Numerical Summary

## 1. Purpose

G1 consolidates the frozen numerical evidence from the classic benchmarks, CEC2014, and engineering-design experiments. No optimizer is rerun and no frozen conclusion is retuned.

## 2. Cross-stage overview

| Domain | Scope | Primary metric | Headline result |
|---|---|---|---|
| Classic F1-F23 | 23 functions | lower 30-run mean objective/error under Stage D rule | GWO lower mean: 8; SCHO lower mean: 12; Ties: 3 |
| CEC2014 | F1-F30, D=10 | mean error + paper-scale agreement | Reproduction lower mean: GWO 22, SCHO 8; Within ±25% of paper mean error: GWO 22/30, SCHO 14/30; Paper/reproduction pairwise flips: 9 |
| Engineering design | 6 problems × 2 algorithms × 30 runs | feasible rate + feasible-only objective quality | Feasible runs: 288/360; NO_FEASIBLE_FOUND: 72/360; Structural failures: 0 |

## 3. Classic F1-F23

Under the frozen Stage D practical mean-comparison rule, GWO had the lower mean on **8/23** functions, SCHO on **12/23**, with **3 ties**.

| Family | Functions | GWO lower mean | SCHO lower mean | Tie |
|---|---:|---:|---:|---:|
| F1-F7 | 7 | 1 | 4 | 2 |
| F8-F13 | 6 | 2 | 3 | 1 |
| F14-F23 | 10 | 5 | 5 | 0 |

These counts are descriptive results under the project reproduction protocol; stochastic/local-optimum deviations were retained rather than tuned away.

## 4. CEC2014

Stage E reproduced 30 CEC2014 functions at D=10. GWO mean errors were within ±25% of the paper values on **22/30** functions and within a factor of 2 on **30/30**. SCHO was within ±25% on **14/30** and within a factor of 2 on **26/30**.

The paper's pairwise lower-mean count was GWO 13 vs SCHO 17; the reproduction produced GWO 22 vs SCHO 8, with 9 pairwise flips.

The frozen Stage E interpretation remains: the GWO scale was broadly reproduced, while SCHO's relative advantage was not fully reproduced. The result is retained rather than corrected by tuning.

## 5. Engineering design

F4 completed all 360 requested runs: **288** returned feasible best designs, **72** were `NO_FEASIBLE_FOUND`, and there were **0 structural failures**.

| Problem | Alg. | Feasible | Rate | Best feasible | Paper | Best gap |
|---|---|---:|---:|---:|---:|---:|
| spring | GWO | 26/30 | 86.7% | 0.01269251641 | 0.0126656 | +0.213% |
| spring | SCHO | 30/30 | 100.0% | 0.01271284805 | 0.0126656 | +0.373% |
| pressure_vessel | GWO | 30/30 | 100.0% | 5898.46787 | 5889.0061 | +0.161% |
| pressure_vessel | SCHO | 30/30 | 100.0% | 6013.651107 | 5889.0061 | +2.117% |
| welded_beam | GWO | 18/30 | 60.0% | 1.727472228 | 1.72516 | +0.134% |
| welded_beam | SCHO | 19/30 | 63.3% | 1.733002838 | 1.72516 | +0.455% |
| speed_reducer | GWO | 1/30 | 3.3% | 3003.935707 | 2995.2477 | +0.290% |
| speed_reducer | SCHO | 14/30 | 46.7% | 3008.618945 | 2995.2477 | +0.446% |
| cantilever_printed | GWO | 30/30 | 100.0% | 13.01247099 | 1.3033 | N/A (formula mismatch) |
| cantilever_printed | SCHO | 30/30 | 100.0% | 13.01485319 | 1.3033 | N/A (formula mismatch) |
| three_bar_truss | GWO | 30/30 | 100.0% | 263.8977231 | 263.8958476 | +0.001% |
| three_bar_truss | SCHO | 30/30 | 100.0% | 263.89688 | 263.8958476 | +0.000% |

Welded beam and especially speed reducer show why feasible rate must be reported separately from best feasible objective. For speed reducer, GWO found a feasible design in only 1/30 runs while SCHO did so in 14/30.

Cantilever remains a special source anomaly: the primary experiment uses the paper-printed `0.6224` objective, while the `0.06224` version is retained only as a separately labelled Table-20-consistent diagnostic.

## 6. Integrated interpretation

Across the three benchmark families, there is no single scalar result that adequately summarizes reproduction quality. Classic functions mainly reveal stochastic optimizer behavior; CEC2014 tests whether the paper-scale performance transfers to a harder modern benchmark suite; engineering problems additionally expose feasibility-handling behavior.

The final report should therefore keep four evidence dimensions separate: (1) source-faithful implementation, (2) objective/error quality, (3) stochastic variation, and (4) feasibility success under constraints.

## 7. G1 status

**G1 RESULT: PASS**

The numerical evidence is now consolidated and ready for G2, where the integrated final report can be drafted without rerunning any optimizer.

---

## Appendix B — Stage D final report

# D3 — Stage D Final Comparison: GWO vs SCHO

## 1. 本阶段目标

基于 D2 的统一统计表制作可直接用于复现报告的比较图，并形成 Stage D 的最终结论。
本阶段不重新运行算法，也不修改 `algorithms/gwo.py` 或 `algorithms/scho.py`。

## 2. 图表

### Figure D3-1 — Practical Mean Wins by Function Family

文件：`D3_mean_wins_by_family.png`

该图使用 D2 的 practical winner（绝对差 `<= 1e-12` 记为 Tie）：

- F1–F7：SCHO 4，GWO 1，Tie 2。
- F8–F13：SCHO 3，GWO 2，Tie 1。
- F14–F23：SCHO 5，GWO 5，Tie 0。

这说明 SCHO 的整体优势主要集中在高维 unimodal / multimodal benchmark；固定维函数组中两者各有明显强项。

### Figure D3-2 — Mean Absolute Error to Theoretical Optimum

文件：`D3_mean_error_to_optimum.png`

纵轴为 `|30-run Mean - theoretical optimum|`，使用 symlog 标度以同时展示机器精度级误差和大尺度误差。

主要现象：

- SCHO 在 F3、F4、F7、F9、F11、F15 等函数上更接近全局最优。
- GWO 在 F18、F20、F21、F22、F23 上更有优势，尤其 F22–F23 的平均值明显更接近 Shekel 类函数的最优值。
- F1、F2、F10 等函数两种算法都已经接近机器精度，不宜过度解释严格胜负。

### Figure D3-3 — Population STD Comparison

文件：`D3_std_comparison.png`

纵轴是 30 次独立运行的 population STD（ddof=0），同样使用 symlog 标度。

整体 practical stability 统计：

- GWO：10 个函数更稳定；
- SCHO：10 个函数更稳定；
- Tie：3 个。

两种算法整体稳定性没有出现一边倒的差异；性能差异更依赖具体函数类型。

## 3. Stage D 最终统计

严格浮点 Mean 胜场：

- SCHO：15
- GWO：8

采用 `1e-12` practical tolerance 后：

- SCHO：12
- GWO：8
- Tie：3

因此，经典 F1–F23 上可以总结为：

> SCHO 在本次 Python 复现实验中总体胜场更多，优势主要集中在高维连续 benchmark；
> GWO 在若干固定维多峰函数上更稳健，尤其 F18、F22、F23 表现突出。

## 4. 关键函数解释

- **F7**：D1 修正随机噪声协议后，SCHO 仍明显优于 GWO，因此优势不是由未控制的 F7 RNG 造成。
- **F9**：SCHO 的 30-run Mean 为 0，而 GWO 受局部最优影响，Mean 明显更高。
- **F15**：SCHO 的平均结果更接近理论最优。
- **F18**：GWO 在 30 次运行中非常稳定；SCHO 存在少量很大的离群 run。
- **F22–F23**：GWO 更稳定地落入高质量 Shekel 盆地，SCHO 部分 run 停留在较差局部盆地。

## 5. Stage D 结论

Stage D 可以正式结束。

当前证据不支持“某一个算法在所有问题上普遍占优”。更准确的结论是：

1. SCHO 在高维经典 benchmark 上显示出更强的总体优化能力；
2. GWO 在部分固定维多峰问题上具有更好的稳定性与局部盆地选择能力；
3. 因此后续工程设计问题必须独立评估，不能仅凭 F1–F23 的总胜场提前判断工程问题中的最终赢家。

## 6. 下一阶段

建议进入 **Stage E：CEC / composite benchmark**。

如果你的最终复现目标更强调工程机械设计，也可以直接进入 **Stage F：engineering design problems**；但按我们之前的完整路线，下一步应先做 Stage E。

---

## Appendix C — Stage F final report

# Stage F — Engineering Design Reproduction Final Report

## 1. 目标与范围

Stage F 复现 SCHO 论文工程设计部分的 6 个约束优化问题，并将冻结的 GWO 与冻结的 source-faithful SCHO 接入同一套工程 benchmark。

本阶段重点不是只比较一个最优值，而是同时检查：公式定义、约束可行性、优化器接口、独立运行的可行率、可行解目标值，以及论文公式本身存在的内部不一致。

## 2. Source-stated 与 project protocol 的区分

SCHO 工程部分明确给出 6 个工程问题，并说明使用 simple death penalty 处理违反约束的候选；但工程章节没有明确重述数值 penalty 常数、seed schedule，也没有明确给出一套工程专用的 30-run 数值协议。

因此 Stage F 使用以下 **project reproduction protocol**：

- Population: `N = 30`
- Iterations: `MaxIter = 500`
- Independent runs: `30`
- Seeds: `1000..1029`
- Death penalty: `1e30`
- Feasibility tolerance: `1e-8`

GWO 和 SCHO 在 F4 使用同一 death-penalty handler，这是受控/common-protocol 比较；不能据此声称原始 GWO 工程实验使用了完全相同的约束处理规则。

## 3. F0–F3 实现与确定性验证

F0 对论文 Section 3.3 与 Tables 16–21 进行了逐题公式审计。F1 将 6 个问题实现为独立 benchmark，并直接代入论文报告的设计点验证 objective、各约束和 bounds。F2 验证 death-penalty wrapper 与两种冻结优化器的接口。F3 完成 6 problems × 2 algorithms 的单 seed 全覆盖。

关键冻结决策：

- Spring：论文 bounds 行中的最后一个变量按 `x3 in [2,15]` 解释；约束 `g2` 使用末尾 `-1` 的修正版，因为论文报告点在印刷版本下约为 `+0.9999994`，而修正后约为 `-6.0e-7`。
- Pressure vessel：主复现保持连续变量，不擅自加入论文未说明的 `0.0625` 厚度离散投影。
- Speed reducer：不擅自把 `x3` 做整数投影，因为论文没有给出对应实现规则。
- Cantilever：保留论文印刷目标 `0.6224*sum(x)`；`0.06224` 只作为 Table-20-consistent diagnostic，绝不冒充论文已确认的正确公式。
- Three-bar truss：box 包含 `(0,0)`，该点使应力公式奇异；F2 后将这种 non-finite constraint 正确判为 infeasible + death penalty，而不是让程序崩溃。

## 4. F4 30-run 实验总体结果

F4 共执行 **360/360** 次优化，其中 **288** 次返回 feasible best design，**72** 次为 `NO_FEASIBLE_FOUND`，结构性失败为 **0**。

下表中的 objective 统计只使用 feasible runs；这样不会让 `1e30` death penalty 污染普通 Mean/STD。STD 为 sample STD (`ddof=1`)，所以只有一个 feasible run 时 STD 正确显示为 `NaN`。

| Problem | Algorithm | Feasible | Best feasible | Mean feasible | STD feasible |
|---|---|---:|---:|---:|---:|
| spring | GWO | 26/30 (86.7%) | 0.01269251641 | 0.01297921357 | 0.0003454436934 |
| spring | SCHO | 30/30 (100.0%) | 0.01271284805 | 0.0151057376 | 0.002249286552 |
| pressure_vessel | GWO | 30/30 (100.0%) | 5898.46787 | 6231.54991 | 516.8674718 |
| pressure_vessel | SCHO | 30/30 (100.0%) | 6013.651107 | 6468.606986 | 302.0138033 |
| welded_beam | GWO | 18/30 (60.0%) | 1.727472228 | 1.927434533 | 0.5329902807 |
| welded_beam | SCHO | 19/30 (63.3%) | 1.733002838 | 2.070887787 | 0.4581170675 |
| speed_reducer | GWO | 1/30 (3.3%) | 3003.935707 | 3003.935707 | NaN |
| speed_reducer | SCHO | 14/30 (46.7%) | 3008.618945 | 3082.621073 | 245.3000668 |
| cantilever_printed | GWO | 30/30 (100.0%) | 13.01247099 | 13.01402151 | 0.0009669856813 |
| cantilever_printed | SCHO | 30/30 (100.0%) | 13.01485319 | 13.02237253 | 0.006553286021 |
| three_bar_truss | GWO | 30/30 (100.0%) | 263.8977231 | 263.9079531 | 0.01286067873 |
| three_bar_truss | SCHO | 30/30 (100.0%) | 263.89688 | 263.9167896 | 0.02645690288 |

## 5. 与论文参考值的数值对照

对于 5 个内部一致的 formulation，F5 将 F4 的 `BestFeasible` 与 SCHO Tables 16–21 中报告的 objective 进行直接数值对照。Gap 为 `(BestFeasible - PaperReported) / |PaperReported|`。

| Problem | Algorithm | Feasible | Best feasible | Paper | Gap |
|---|---|---:|---:|---:|---:|
| spring | GWO | 26/30 | 0.01269251641 | 0.0126656 | +0.213% |
| spring | SCHO | 30/30 | 0.01271284805 | 0.0126656 | +0.373% |
| pressure_vessel | GWO | 30/30 | 5898.46787 | 5889.0061 | +0.161% |
| pressure_vessel | SCHO | 30/30 | 6013.651107 | 5889.0061 | +2.117% |
| welded_beam | GWO | 18/30 | 1.727472228 | 1.72516 | +0.134% |
| welded_beam | SCHO | 19/30 | 1.733002838 | 1.72516 | +0.455% |
| speed_reducer | GWO | 1/30 | 3003.935707 | 2995.2477 | +0.290% |
| speed_reducer | SCHO | 14/30 | 3008.618945 | 2995.2477 | +0.446% |
| three_bar_truss | GWO | 30/30 | 263.8977231 | 263.8958476 | +0.001% |
| three_bar_truss | SCHO | 30/30 | 263.89688 | 263.8958476 | +0.000% |

这些结果说明，在至少一次进入可行域的前提下，5 个内部一致问题的最佳可行目标值都能落在论文参考值附近。但这只是数值尺度复现，不能替代对实验协议差异和 stochastic variation 的说明。

## 6. Feasibility diagnostics

| Problem | Both feasible | GWO-only | SCHO-only | Neither |
|---|---:|---:|---:|---:|
| spring | 26 | 0 | 4 | 0 |
| pressure_vessel | 30 | 0 | 0 | 0 |
| welded_beam | 10 | 8 | 9 | 3 |
| speed_reducer | 0 | 1 | 14 | 15 |
| cantilever_printed | 30 | 0 | 0 | 0 |
| three_bar_truss | 30 | 0 | 0 | 0 |

Spring、pressure vessel、cantilever 和 three-bar truss 的可行性总体较稳定。Welded beam 明显更难：paired seeds 为 both=10、GWO-only=8、SCHO-only=9、neither=3。Speed reducer 是最强的 feasibility bottleneck：GWO 仅 1/30 找到可行解，SCHO 为 14/30；paired seeds 为 both=0、GWO-only=1、SCHO-only=14、neither=15。

因此工程问题的结果必须同时报告 feasible rate 和 feasible-objective quality。单看 Best 会忽略算法是否经常根本无法进入可行域。

## 7. Cantilever 内部不一致

论文印刷目标函数在 Table-20 报告点上约为 `13.0326`，而 Table 20 报告 `1.3033`，两者存在约 10 倍尺度差。Stage F 主实验始终保留论文印刷的 `0.6224`，所以主结果约在 13 的尺度。

| Algorithm | Printed best | Diagnostic 0.06224 | Table 20 | Diagnostic gap |
|---|---:|---:|---:|---:|
| GWO | 13.01247099 | 1.301247099 | 1.3033 | -0.158% |
| SCHO | 13.01485319 | 1.301485319 | 1.3033 | -0.139% |

`0.06224` 结果仅用于说明 Table 20 的数值尺度可以被约 0.1 rescaling 对齐；本报告不把它声明为论文已经证实的正确公式，也不引入另一个文献变体中的 first constraint coefficient `61`。

## 8. Stage F 结论

Stage F 已完成从 source audit、benchmark implementation、deterministic validation、optimizer integration、single-run coverage、360-run experiment 到 paper comparison 的完整闭环。工程 benchmark 层和两种冻结优化器之间没有发现结构性接口问题。

结果表明：当算法成功找到可行域时，5 个内部一致问题的最佳目标值总体能复现到论文参考尺度附近；但纯 death penalty 的可行性成功率明显依赖问题，尤其 welded beam 和 speed reducer。Cantilever 则应持续作为论文内部公式/表格不一致的特殊案例报告。

本阶段不通过调参消除 `NO_FEASIBLE_FOUND`，也不因为单个 Best 更低就给出算法普遍优劣结论。Feasible rate、feasible-only objective quality、source anomaly 和 stochastic variation 被保留为彼此独立的证据。

## 9. Freeze scope

Stage F freeze 应包含本阶段新增 benchmark/constraint code、F1–F6 experiment scripts、F3/F4 raw data、F4/F5 processed data、F5/F6 reports 和 manifest。

不应把历史遗留的 `experiments/engineering_gwo.py` 或 `experiments/engineering_scho.py` 误纳入 Stage F freeze，除非另外明确审计。

冻结前还应确认 `algorithms/gwo.py` 与 `algorithms/scho.py` 没有被 Stage F 修改。

---

## Appendix D — G0 evidence audit

# Stage G0 — Final Report Evidence Audit

## 1. 目的

Stage G0 不重新运行任何优化器。它只检查最终报告所需的主要证据是否已经存在，并冻结 Stage G 的报告结构。

## 2. Final report structure

最终报告建议按以下顺序组织：

1. Introduction and reproduction goals
2. Algorithms: GWO and source-faithful SCHO
3. Reproduction protocol and implementation principles
4. Classic 23 benchmark reproduction
5. GWO vs SCHO comparison on classic benchmarks
6. CEC2014 reproduction
7. Engineering-design reproduction
8. Source anomalies and implementation caveats
9. Overall findings and limitations
10. Reproducibility / Git freeze information

## 3. Evidence audit

| Group | Required | File | Exists |
|---|---|---|---|
| classic_gwo | yes | `results/processed/gwo_classic23_results.csv` | yes |
| classic_gwo | yes | `results/processed/gwo_stageB_summary.csv` | yes |
| classic_gwo | yes | `report/notes/gwo_stageB_report.md` | yes |
| classic_scho | yes | `results/processed/scho_classic23_summary.csv` | yes |
| classic_scho | yes | `report/notes/C13_SCHO_vs_Paper_Table7_report.md` | yes |
| classic_comparison | yes | `results/processed/D2_GWO_vs_SCHO_classic23.csv` | yes |
| classic_comparison | yes | `report/notes/D2_GWO_vs_SCHO_report.md` | yes |
| classic_comparison | yes | `report/notes/D3_StageD_final_report.md` | yes |
| cec2014 | yes | `results/raw/cec2014_e4_runs.csv` | yes |
| cec2014 | yes | `results/processed/cec2014_e4_summary.csv` | yes |
| engineering | yes | `results/raw/engineering_f4_runs.csv` | yes |
| engineering | yes | `results/processed/engineering_f4_summary.csv` | yes |
| engineering | yes | `results/processed/engineering_f5_paper_comparison.csv` | yes |
| engineering | yes | `results/processed/engineering_f5_seed_diagnostics.csv` | yes |
| engineering | yes | `report/stage_f_engineering_final.md` | yes |
| engineering | yes | `report/stage_f_manifest.csv` | yes |
| optional | no | `report/notes/F0_engineering_protocol_audit.md` | yes |
| optional | no | `report/engineering_f5_analysis.md` | yes |
| optional | no | `report/figures/D3_mean_error_to_optimum.png` | yes |
| optional | no | `report/figures/D3_mean_wins_by_family.png` | yes |
| optional | no | `report/figures/D3_std_comparison.png` | yes |

## 4. Git freeze references

| Tag | Found | Commit | Subject |
|---|---|---|---|
| `scho-source-faithful-v1` | yes | `tag scho-sou` | Freeze SCHO source-faithful baseline v1 after C9 F1 validation |
| `stage-e-cec2014-v1` | yes | `4c6ad0998705` | Freeze Stage E CEC2014 reproduction |
| `stage-f-engineering-v1` | yes | `23eab4b30f83` | Freeze Stage F engineering reproduction |

## 5. Frozen conclusions to preserve in Stage G

- Classic 23 functions: GWO and SCHO have already been reproduced and compared under the frozen project protocol; stochastic deviations should not be tuned away.
- SCHO implementation: keep the source-faithful behavior frozen, including its unusual boundary handling, dynamic bounded initialization behavior, leader/second-best behavior, and exact equation branching documented earlier.
- CEC2014: GWO broadly reproduced the paper scale; SCHO's relative advantage was not fully reproduced under the project protocol. The result must remain reported as evidence, not corrected by retuning.
- Engineering design: feasibility rate is a primary metric in addition to feasible-only objective quality. `NO_FEASIBLE_FOUND` runs must remain visible.
- Cantilever beam: keep the paper-printed 0.6224 formulation separate from the Table-20-consistent 0.06224 diagnostic; do not silently replace one with the other.
- Spring: keep the documented x3 bound correction and terminal `-1` in g2.

## 6. G0 decision

**G0 status: PASS**

All required evidence groups are present. Stage G can proceed to G1 (final tables + integrated numerical summary) without rerunning optimizers.
