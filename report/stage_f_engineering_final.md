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
