# GWO 与 SCHO 元启发式算法复现项目总报告 v2
## Full-Paper Extension Closeout Report

## 摘要

本项目围绕 Grey Wolf Optimizer（GWO）与 Sinh Cosh Optimizer（SCHO）开展了分阶段、可审计的论文复现实验。项目目标不是追求 MATLAB 与 Python/NumPy 的逐随机数位级一致，也不是通过事后调参强行贴近论文结果，而是尽可能恢复论文与作者源码中的算法行为、benchmark 定义、实验规模和统计结构，并在无法恢复原始细节时明确使用 `controlled-equivalent`、`controlled-interpretation` 或 `project-controlled` 协议。

在 Stage A-G 核心复现基础上，H0-H6 进一步完成了 GWO Section 4 的 composite benchmark 与行为图扩展、SCHO 消融与定性分析、SCHO Section 3.1.3 的 9 算法 classical comparison，以及 SCHO Section 3.1.4 的 9 算法 D=100 / D=500 scalability comparison。项目最终形成了多层 exactness boundary：有些部分达到 source-faithful，有些达到 paper-structure 或 controlled-equivalent；若干数值对照只达到 partial numerical agreement，并完整保留这些差异。

本项目不应被描述为“两个论文所有实验均 100% 精确复现”。更准确的结论是：

> **本项目完成了既定 H0-H6 扩展范围内的大规模可审计复现，并对无法完全恢复的历史实验细节、未重跑的外部比较算法、数值不一致和主动排除的光学应用进行了显式标注。**

---

# 1. 项目目标与复现原则

项目遵循以下冻结原则：

- 不为逼近论文数值而修改已经冻结的核心算法。
- 不声称 MATLAB RNG 与 NumPy RNG bitwise 等价。
- 保留论文/源码中的 quirks，不静默“修正”成理想化版本。
- 区分：
  - `source-faithful`
  - `source-structured`
  - `paper-equation-faithful`
  - `paper-structure`
  - `controlled-equivalent`
  - `controlled-interpretation`
  - `project-controlled adapter`
- 无法恢复的随机种子、shift vector、history semantics 等，必须明确标注为 project convention。
- 结果与论文不一致时，保留不一致，不进行针对性调参。

冻结核心算法：

```text
algorithms/gwo.py
algorithms/scho.py
```

---

# 2. Git 与冻结状态

核心历史阶段：

```text
stage-g-final-report-v1
full-paper-extension-h0-h5-v1
h6-scho-scalability-full-comparison-v1
```

H6 最终提交：

```text
c735f57  Freeze H6e Section 3.1.4 final comparison
```

H6 annotated tag：

```text
h6-scho-scalability-full-comparison-v1
```

该 tag 已推送到远端。

---

# 3. 经典 F1-F23 核心复现

GWO 与 SCHO 在 classical F1-F23 上均完成了 30-run 级别复现。

Stage D 的 project-controlled practical mean comparison：

```text
GWO lower mean : 8
SCHO lower mean: 12
Tie            : 3
```

按函数族：

| Family | GWO lower mean | SCHO lower mean | Tie |
|---|---:|---:|---:|
| F1-F7 | 1 | 4 | 2 |
| F8-F13 | 2 | 3 | 1 |
| F14-F23 | 5 | 5 | 0 |

这一结果只说明不同 benchmark 家族上的相对表现差异，不能解释为某算法在所有问题上普遍优于另一算法。

---

# 4. GWO Section 4 扩展复现

## 4.1 最终覆盖状态

GWO Section 4 最终冻结为：

```text
GWO_SECTION4_PAPER_STRUCTURE_COVERAGE_COMPLETE
```

Exactness boundary：

| Artifact | Final tier |
|---|---|
| Fig.7 | `COMPLETE_PAPER_STYLE` |
| Fig.8 | `COMPLETE_PAPER_STYLE` |
| Fig.9 | `COMPLETE_PAPER_STYLE` |
| Fig.10 | `COMPLETE_CONTROLLED_EQUIVALENT` |
| F24-F29 / Table 8 experiment | `COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT` |
| Fig.11 | `COMPLETE_CONTROLLED_EQUIVALENT` |

这里的“complete”指 paper-structure coverage，而不是 pixel-exact 或所有数值精确一致。

## 4.2 SIS2005 composite F24-F29

H1 正式协议：

- F24-F29 / CF1-CF6
- D=10
- N=30
- MaxIter=500
- 30 runs/function
- seeds = 1000..1029
- 180 total runs
- frozen GWO
- recovered SIS2005 source assets

最终状态：

```text
COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT
```

数值诊断：

- F28 最接近论文；
- F25 在 factor 2 范围内；
- F24/F26/F27/F29 明显偏离；
- F29 表现出强烈高-bias trapping。

重要 source anomaly：

- GWO Table 4 对 F26/CF3 写为 Griewank ×10；
- 恢复的 `SIS_novel_func.m` 实际为 Rastrigin ×10；
- 正式 primary 使用 source-faithful Rastrigin；
- Griewank 只保留为 diagnostic。

## 4.3 GWO convergence behavior

Fig.11 结构性要素已覆盖：

- 8 个指定函数；
- 6 search agents；
- 100 iterations；
- shifted functions；
- landscape；
- search history；
- parameter `a`；
- first-agent trajectory；
- fitness history；
- convergence curve。

由于无法恢复论文原始 shift vector、seed 与 history logging semantics，冻结为：

```text
COMPLETE_CONTROLLED_EQUIVALENT
```

---

# 5. SCHO Section 3.1.1-3.1.2：消融与定性分析

## 5.1 Table 5 ablation

最终状态：

```text
SCHO_TABLE5_ABLATION_COMPLETE__STRONG_RANK_LEVEL_AGREEMENT__ONE_TIE_DIFFERENCE
```

结果：

- final-rank matches = 5/6；
- 唯一主要差异为 SCHO_NFF 的 tie structure；
- 五个 ablation variants 属于：
  `PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION`。

这些 variants 没有恢复到作者独立源码文件，因此不能称为 source-faithful variant implementations。

## 5.2 Fig.7

最终状态：

```text
SCHO_FIG7_CONTROLLED_COMPLETE__PARTIAL_BAR_LEVEL_AGREEMENT__NO_TUNING
```

11 个 variants：

- same paper direction: 5/11
- reproduced tie: 2/11
- reversed direction: 4/11
- exact pair: 0/11

Fig.7 的结果被保留为 controlled interpretation，不进行反向调参。

## 5.3 Fig.8

最终状态：

```text
COMPLETE_CONTROLLED_EQUIVALENT
```

因此 SCHO Section 3.1.1-3.1.2 在项目声明的复现边界内已完成。

---

# 6. SCHO Section 3.1.3：9 算法 classical comparison

正式算法：

```text
SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO
```

重要：

```text
SHO = Sea-Horse Optimizer
```

正式 protocol：

```text
H5_CLASSICAL_V1
```

协议：

- F1-F13: D=30
- F14-F23: native dimensions
- N=30
- MaxIter=500
- 30 independent runs
- optimizer seeds = 1000..1029
- objective seed = `5_024_000 + 100*fnum + run`

最终 raw：

```text
results/raw/scho_classical_h5_runs.csv
6210 rows = 9 * 23 * 30
```

## 6.1 Table 7

Reproduced final rank：

| Algorithm | Reproduced rank | Paper rank |
|---|---:|---:|
| SCHO | 1 | 1 |
| GWO | 2 | 3 |
| GJO | 3 | 2 |
| RSA | 4 | 5 |
| SSA | 5 | 6 |
| ALO | 6 | 7 |
| AOA | 7 | 8 |
| SHO | 8 | 4 |
| SCA | 9 | 9 |

主要结论：

- SCHO rank 1 preserved；
- SCA rank 9 preserved；
- GWO/GJO 发生 2/3 互换；
- SHO 为最大持续 mismatch；
- overall = partial rank-level agreement；
- no tuning。

## 6.2 Table 8 Wilcoxon

使用：

- SCHO vs each comparator；
- two-sided Mann-Whitney U / Wilcoxon rank-sum；
- alpha = 0.05；
- asymptotic method；
- continuity correction；
- project-controlled statistical implementation。

关键结果：

- ALO aggregate W|L|T exact；
- GWO win count exact；
- RSA relatively close；
- SSA/AOA/SHO/GJO 有更大差异。

最终状态：

```text
H5_COMPLETE__SECTION_3_1_3_CLASSICAL_9_ALGORITHM_COMPARISON
```

## 6.3 Fig.9

Fig.9 冻结为：

```text
SCHO_FIG9_COMPLETE_CONTROLLED_EQUIVALENT
```

Representative-run protocol：

- formal run 1；
- 207 curves = 9 × 23；
- all 207 final scores regress exactly to H5 formal run-1 results。

---

# 7. SCHO Section 3.1.4：9 算法 scalability comparison

正式 protocol：

```text
H6_SCALABILITY_V1
```

实验矩阵：

```text
9 algorithms × 13 functions × 2 dimensions × 30 runs = 7020
```

协议：

- F1-F13
- D=100, 500
- N=30
- MaxIter=500
- 30 runs
- optimizer seeds = 1000..1029
- objective seed =
  `7_000_000 + dim*10_000 + fnum*100 + run`
- AOA uses `mu=0.5`

组成：

- SCHO H3c reused = 780 rows
- 8 comparators newly run = 6240 rows

正式 raw：

```text
results/raw/scho_scalability_h6b_runs.csv
```

H6b audit：

- 7020/7020；
- each algorithm 780/780；
- F7 540/540；
- all stored BestScore finite；
- audit 不执行 optimizer。

---

# 8. Tables 9/10 + Friedman

## 8.1 D=100

| Algorithm | Reproduced MeanRank / FinalRank | Paper MeanRank / FinalRank |
|---|---:|---:|
| SCHO | 2.84615 / 1 | 1.85 / 1 |
| RSA | 3.38462 / 2 | 2.85 / 2 |
| AOA | 3.69231 / 3 | 4.77 / 6 |
| SHO | 3.92308 / 4 | 3.31 / 3 |
| GJO | 4.00000 / 5 | 4.00 / 4 |
| GWO | 4.23077 / 6 | 4.15 / 5 |
| SSA | 6.61538 / 7 | 6.54 / 7 |
| ALO | 7.61538 / 8 | 7.69 / 8 |
| SCA | 8.69231 / 9 | 8.69 / 9 |

Paper final-rank positions preserved：

```text
SCHO 1
RSA  2
SSA  7
ALO  8
SCA  9
```

Friedman：

```text
statistic = 62.553191
p = 1.4673495e-10
```

## 8.2 D=500

| Algorithm | Reproduced MeanRank / FinalRank | Paper MeanRank / FinalRank |
|---|---:|---:|
| SCHO | 3.00000 / 1 | 2.00 / 1 |
| RSA | 3.23077 / 2 | 2.54 / 2 |
| AOA | 3.38462 / 3 | 5.31 / 6 |
| SHO | 3.61538 / 4 | 3.38 / 3 |
| GJO | 4.30769 / 5 | 4.00 / 4 |
| GWO | 4.76923 / 6 | 4.62 / 5 |
| SSA | 6.69231 / 7 | 6.69 / 7 |
| ALO | 7.46154 / 8 | 7.54 / 8 |
| SCA | 8.53846 / 9 | 8.23 / 9 |

Friedman：

```text
statistic = 59.674541
p = 5.3989853e-10
```

两个维度均在 alpha=0.05 下 reject H0。

H6c 最大结构性 mismatch：

```text
AOA
```

AOA 在项目复现中两个维度均为 rank 3，而论文均为 rank 6。

冻结标签：

```text
SCHO_TABLES9_10_COMPLETE__PARTIAL_RANK_LEVEL_AGREEMENT__SCHO_RANK1_PRESERVED_BOTH_DIMS__AOA_MAJOR_MISMATCH__FRIEDMAN_SIGNIFICANT__NO_TUNING
```

---

# 9. Tables 11/12 Wilcoxon

使用：

- SCHO vs each comparator；
- F1-F13；
- 30-run distributions；
- two-sided Mann-Whitney U / Wilcoxon rank-sum；
- alpha=0.05；
- asymptotic + continuity correction。

符号：

- `+` = SCHO significantly better
- `-` = SCHO significantly worse
- `~` = no significant difference

## 9.1 D=100

| Comparator | Reproduced | Paper | Exact |
|---|---:|---:|:---:|
| GWO | 8|5|0 | 10|3|0 | NO |
| ALO | 12|1|0 | 13|0|0 | NO |
| SCA | 13|0|0 | 13|0|0 | YES |
| SSA | 12|1|0 | 12|1|0 | YES |
| AOA | 5|2|6 | 9|1|3 | NO |
| RSA | 4|3|6 | 5|2|6 | NO |
| SHO | 7|0|6 | 10|1|2 | NO |
| GJO | 6|3|4 | 9|3|1 | NO |

Exact aggregate W|L|T：

```text
2/8
```

## 9.2 D=500

| Comparator | Reproduced | Paper | Exact |
|---|---:|---:|:---:|
| GWO | 9|4|0 | 10|3|0 | NO |
| ALO | 12|1|0 | 12|1|0 | YES |
| SCA | 13|0|0 | 13|0|0 | YES |
| SSA | 12|1|0 | 13|0|0 | NO |
| AOA | 5|2|6 | 11|1|1 | NO |
| RSA | 4|3|6 | 5|2|6 | NO |
| SHO | 7|3|3 | 9|2|2 | NO |
| GJO | 8|4|1 | 9|4|0 | NO |

Exact aggregate W|L|T：

```text
2/8
```

SCA 在两个维度均 exact。

H6 overall：

```text
H6_COMPLETE__SECTION_3_1_4_FULL_9_ALGORITHM_SCALABILITY_COMPARISON
```

推荐解释：

```text
COMPLETE_PROTOCOL_REPRODUCTION__PARTIAL_NUMERICAL_AGREEMENT__NO_TUNING
```

---

# 10. CEC2014 / SCHO Section 3.2

Stage E 完成：

- F1-F30
- D=10
- N=30
- MaxIter=500
- 30 runs
- GWO + SCHO

Paper-scale comparison：

```text
GWO within ±25% : 22/30
GWO within factor 2: 30/30

SCHO within ±25% : 14/30
SCHO within factor 2: 26/30
```

Paper pairwise lower-mean：

```text
SCHO 17
GWO  13
```

Project reproduction：

```text
GWO  22
SCHO 8
```

pairwise flips：

```text
9
```

因此：

```text
CORE_DONE__PARTIAL_NUMERICAL_AGREEMENT__FULL_9_ALG_COMPARISON_NOT_RERUN
```

不能描述为 SCHO Section 3.2 的完整 9-algorithm Friedman/Wilcoxon 重跑。

---

# 11. Engineering Design / SCHO Section 3.3

Stage F project protocol：

- N=30
- MaxIter=500
- 30 runs
- seeds 1000..1029
- death penalty = `1e30`
- feasibility tolerance = `1e-8`

六个问题：

- spring
- pressure vessel
- welded beam
- speed reducer
- cantilever
- three-bar truss

正式运行：

```text
360/360 completed
288 feasible best designs
72 NO_FEASIBLE_FOUND
0 structural failures
```

关键解释：

- feasibility rate 必须和 feasible-only objective quality 分开；
- speed reducer 为最明显 feasibility bottleneck；
- welded beam 也较难；
- cantilever 存在论文打印公式与表格约 10× scale inconsistency。

SCHO Section 3.3 status：

```text
CORE_DONE__PROJECT_CONTROLLED_PROTOCOL
```

---

# 12. GWO Section 5 engineering boundary

Stage F 中 spring / welded beam / pressure vessel 可用于 GWO 的 controlled common-protocol engineering comparison，但不能称为原始 GWO Section-5 penalty protocol 的 exact reconstruction。

因此最终状态：

```text
PARTIAL__COMMON_PROTOCOL_REPRODUCTION
```

---

# 13. GWO Section 6 optical buffer / BSPCW

最终项目决定：

```text
INTENTIONALLY_OUT_OF_SCOPE
```

未实现：

- BSPCW evaluator
- NDBP evaluator
- photonic-band simulation
- optical-buffer optimization

这一部分是主动排除，不是未完成待办。

除非未来明确重新开启该研究方向，否则不应继续列入 roadmap。

---

# 14. 最终全文覆盖状态

最终覆盖审计文件：

```text
report/notes/H7_final_full_paper_coverage_audit.md
report/tables/H7_final_full_paper_coverage_matrix.csv
```

推荐项目级状态：

```text
GWO_SCHO_REPRODUCTION_CLOSEOUT__H0_H6_COMPLETE__DECLARED_SCOPE_BOUNDARIES_PRESERVED
```

仍然保留明确 partial / controlled boundary 的部分：

1. GWO 4.1 / 4.2  
   原历史 comparator suite 没有全部重跑。

2. GWO 5  
   common Stage-F constraint protocol 不等于原 GWO penalty protocol。

3. SCHO 3.2  
   full 9-algorithm CEC2014 comparison 未完整重跑。

4. SCHO 3.3  
   六个工程问题均完成，但论文中的外部比较算法未全部重跑。

5. GWO 6  
   intentionally out of scope。

这些边界是最终项目结论的一部分，不应被后续汇报删除。

---

# 15. 主要数值复现结论

整个项目最重要的科学观察可以归纳为：

### 15.1 Source fidelity 与 numerical agreement 是两个不同维度

一个 source-faithful 实现仍然可能因为：

- RNG；
- benchmark instance；
- 作者未公开实验细节；
- 历史 source/version 差异；

而无法精确复现论文数字。

因此“源码忠实”不等于“论文数字必然一致”。

### 15.2 经典 benchmark 上不存在一个简单的全面赢家

GWO 与 SCHO 在不同 benchmark 家族上表现不同。

因此不能把整个项目压缩成“哪个算法绝对更好”。

### 15.3 SCHO classical 9-alg comparison 保留了核心 ranking structure

H5 中：

- SCHO rank 1 preserved；
- SCA rank 9 preserved；
- 其他中间 comparator 有一定 rank drift；
- SHO mismatch 最大。

### 15.4 SCHO scalability 中核心排名结构部分保留

H6 中两个维度均：

- SCHO rank 1 preserved；
- RSA rank 2 preserved；
- SSA/ALO/SCA ranks 7/8/9 preserved；
- AOA 是最大高维 mismatch。

### 15.5 Engineering 不能只看 best objective

在约束问题中：

- feasibility rate；
- feasible-only quality；
- source anomaly；
- penalty sensitivity；

必须共同报告。

---

# 16. 复现限制

本项目存在以下明确限制：

- Python/NumPy RNG 与 MATLAB RNG 不等价；
- 部分 paper comparator source 未恢复；
- 部分原始 seed / shift / history semantics 未公开；
- SCHO variant source files 未全部恢复；
- SHO 为 paper-equation-faithful，不是历史 author-source line-by-line 验证；
- GWO optical application 未复现；
- full CEC2014 9-alg comparison 未重跑；
- engineering external comparator suites 未全部重跑。

因此本项目适合被称为：

> **可审计的结构化论文复现与实验扩展**

而不是：

> **逐位、逐图、逐数值 exact replication**

---

# 17. 最终结论

本项目已经完成声明范围内的主要科学复现工作：

- GWO classical benchmark core；
- GWO SIS2005 F24-F29；
- GWO Section 4 paper-structure figures；
- SCHO classical F1-F23；
- SCHO ablation / qualitative；
- SCHO Section 3.1.3 full 9-algorithm classical comparison；
- SCHO Section 3.1.4 full 9-algorithm D=100/D=500 scalability；
- CEC2014 GWO/SCHO core；
- 6 engineering design problems。

项目最重要的价值不只是“复现出多少相同数字”，而是建立了一条清晰、可审计、带 exactness boundary 的证据链：

- 能精确恢复的地方明确恢复；
- 只能结构等价的地方明确标注；
- 数值不一致的地方保留证据；
- 源码与论文冲突的地方不替论文“猜正确答案”；
- 未恢复/未公开的历史细节不伪装成 exact；
- 主动排除的范围明确记录。

最终建议使用以下表述作为项目 closeout：

```text
GWO_SCHO_REPRODUCTION_CLOSEOUT__H0_H6_COMPLETE__DECLARED_SCOPE_BOUNDARIES_PRESERVED
```

而不要使用：

```text
100% exact reproduction of both papers
```

---

# Appendix A — 关键正式数据集

```text
results/raw/scho_classical_h5_runs.csv
results/raw/scho_scalability_h3c_runs.csv
results/raw/scho_scalability_h6b_runs.csv
results/raw/cec2014_e4_runs.csv
results/raw/engineering_f4_runs.csv
```

---

# Appendix B — 关键正式报告

```text
report/notes/H1f_gwo_sis2005_postrun_diagnostic.md
report/notes/H2f_gwo_section4_freeze.md
report/notes/H4f_scho_table5_diagnostic.md
report/notes/H4j_scho_fig7_diagnostic_freeze.md
report/notes/H5_scho_section3_1_3_freeze.md
report/notes/H6_scho_section3_1_4_freeze.md
report/notes/H7_final_full_paper_coverage_audit.md
report/notes/HANDOFF.md
```

---

# Appendix C — 历史总报告说明

旧文件：

```text
report/final_reproduction_report.md
```

应继续作为 Stage G 核心 reproduction 的历史 frozen report 保留。

本 v2 报告：

```text
report/final_reproduction_report_v2.md
```

是 H1-H6 full-paper extension 与 H7 closeout 后的最终整合版本。
