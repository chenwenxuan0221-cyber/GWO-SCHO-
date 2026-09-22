# HANDOFF.md
# GWO 与 SCHO 论文复现项目技术交接

项目根目录：

`D:\Anaconda\envs\DL\metaheuristic-reproduction`

环境：

- Windows PowerShell
- conda env: `(DL)`
- Python 3.11

当前工作分支：

`h6-scho-scalability-full-comparison`

当前已冻结 H6 HEAD：

`c735f57` — `Freeze H6e Section 3.1.4 final comparison`

H6 annotated tag：

`h6-scho-scalability-full-comparison-v1`

---

## 1. 总原则

本项目始终遵循以下规则：

- 优先忠实于作者源码、论文结构和可恢复的实验协议。
- 不追求 MATLAB 与 NumPy 的 bitwise RNG 一致。
- 不为逼近论文数值而事后调参。
- 源码 quirk 不静默修复。
- 明确区分：
  - `source-faithful`
  - `source-structured`
  - `paper-equation-faithful`
  - `paper-structure`
  - `controlled-equivalent`
  - `controlled-interpretation`
  - `project-controlled adapter`
- 已冻结的核心算法不得为了后续结果再次修改。
- 历史证据通过新版本/新阶段追加，不覆盖旧证据。

---

## 2. 冻结核心算法

禁止为了提高论文一致性修改：

```text
algorithms/gwo.py
algorithms/scho.py
```

GWO：

- 以冻结的项目基线为准。
- 不采用早期 README 中与冻结实现不一致的自动 leader-shifting 写法。

SCHO：

- 以 source-faithful MATLAB 审计结果为准。
- 必须保留源行为，包括但不限于：
  - `t=2` 起始；
  - candidate/dimension 内重新计算 A；
  - 随机数消费顺序；
  - 非对称边界行为；
  - bounded-search / redistribution 时点；
  - second-best / sorting 相关行为；
  - 源码中已记录的异常和 quirks。

---

## 3. 核心 Git 冻结链

早期核心 reproduction：

```text
ee3db4f  Freeze Stage G final reproduction report
tag: stage-g-final-report-v1
```

Full-paper extension H0-H5：

```text
82ae593  Freeze H0-H2 GWO full-paper extension
63a02f8  Freeze H3 SCHO scalability core
4e44904  Freeze H4 SCHO ablation and qualitative analyses
2955124  Freeze H5 SCHO Section 3.1.3 nine-algorithm comparison
5168402  Freeze supplemental provenance and Stage D evidence
c4f89d3  Freeze SCHO 3.3 MATLAB source audit
e57f64d  Update H0-H5 project handoff
d98e215  Freeze Stage D corrected F7 rerun provenance
1d43a59  Freeze Stage B GWO comparison figures and data
ef1cac6  Ignore local legacy and superseded artifacts
ebcdaca  Finalize H0-H5 handoff metadata
```

Annotated tag：

```text
full-paper-extension-h0-h5-v1
```

指向：

```text
ebcdacac8777959b60a1320a8c6cdd3f40252203
```

H6 full scalability extension：

```text
3af2261  Freeze H6a scalability full-comparison protocol
82a2c05  Freeze H6b scalability full-comparison runner
0569ad4  Freeze H6b formal scalability raw dataset
2f48481  Freeze H6c scalability Tables 9-10 and Friedman analysis
5002697  Freeze H6d scalability Tables 11-12 Wilcoxon analysis
c735f57  Freeze H6e Section 3.1.4 final comparison
```

Annotated tag：

```text
h6-scho-scalability-full-comparison-v1
```

远端已推送：

```text
origin/h6-scho-scalability-full-comparison
h6-scho-scalability-full-comparison-v1
```

---

## 4. H0-H2：GWO 全文扩展

### H0

完成 full-paper coverage audit。

Stage G 只能理解为 strong core reproduction，
不能解释为两个论文 100% 全覆盖。

旧 H0 文档是“扩展前基线”，H7 最终审计已生成新的覆盖状态。

### H1 — GWO SIS2005 F24-F29

完成 GWO Section 4.3 / SIS2005 CF1-CF6：

- D=10
- N=30
- MaxIter=500
- 30 runs/function
- 180 runs
- seeds 1000..1029
- frozen GWO
- recovered SIS2005 source assets

最终状态：

```text
COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT
```

关键异常：

- GWO Table 4 对 F26/CF3 写为 Griewank ×10。
- 恢复的 `SIS_novel_func.m` 实际使用 Rastrigin ×10。
- 正式 primary 使用 source-faithful Rastrigin。
- Griewank 仅保留为 diagnostic。

数值结论：

- F28 最接近论文；
- F25 在 factor 2 内；
- F24/F26/F27/F29 明显偏离；
- 不调参修复。

### H2 — GWO Section 4 figures

最终状态：

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
| F24-F29 / Table 8 run | `COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT` |
| Fig.11 | `COMPLETE_CONTROLLED_EQUIVALENT` |

Fig.11 保留的 project-controlled conventions：

- shift target = 原始坐标区间的 65%
- native benchmark dimensions
- GWO seed = 1000
- H2b evaluated-population history sampling
- fitness history = 6 个 evaluated agents 的 mean fitness

不得声明 pixel-level 或随机轨迹 exact reproduction。

---

## 5. H3-H4：SCHO scalability core / ablation / qualitative

### H3 — SCHO scalability core

已完成：

- SCHO only
- F1-F13
- D=100 / D=500
- 30 runs
- 780 runs

H3c raw：

```text
results/raw/scho_scalability_h3c_runs.csv
```

H3 最初只是 scalability core；
完整 9-algorithm scalability 后来由 H6 补齐。

### H4 — Section 3.1.1-3.1.2

Table 5 ablation：

```text
SCHO_TABLE5_ABLATION_COMPLETE__STRONG_RANK_LEVEL_AGREEMENT__ONE_TIE_DIFFERENCE
```

结果：

- final-rank matches = 5/6
- 唯一主要差异为 SCHO_NFF 的 tie structure
- 5 个消融变体仍是 `PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION`

Fig.7：

```text
SCHO_FIG7_CONTROLLED_COMPLETE__PARTIAL_BAR_LEVEL_AGREEMENT__NO_TUNING
```

- 11 个 variants 是 controlled-interpretation
- 不是 recovered author-source implementations
- partial bar-level agreement

Fig.8：

```text
COMPLETE_CONTROLLED_EQUIVALENT
```

H4 整体：

```text
COMPLETE WITH CONTROLLED-INTERPRETATION BOUNDARY FOR FIG.7
```

---

## 6. H5：SCHO Section 3.1.3 classical 9-algorithm comparison

正式 9 算法：

```text
SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO
```

重要：

```text
SHO = Sea-Horse Optimizer
```

正式 SHO 路径：

```text
algorithms/sea_horse.py
function: sho(...)
```

不要把旧路径与正式 H5 混用：

```text
algorithms/sea_horse_sho.py
experiments/test_sea_horse_sho_h5c7.py
report/notes/H5c7_sea_horse_sho_protocol.md
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
- 30 runs
- optimizer seeds = 1000..1029
- objective seed = `5_024_000 + 100*fnum + run`
- objective RNG 与 optimizer RNG 分离
- stochastic objective 仅 F7

Formal raw：

```text
results/raw/scho_classical_h5_runs.csv
6210 rows = 9 * 23 * 30
```

Table 7 reproduced final ranking：

```text
SCHO 1
GWO  2
GJO  3
RSA  4
SSA  5
ALO  6
AOA  7
SHO  8
SCA  9
```

解释：

- SCHO paper rank 1 preserved
- partial rank-level agreement
- SHO 是 H5 最大持续 mismatch
- no tuning

Table 8：

- two-sided Mann-Whitney U / Wilcoxon rank-sum
- alpha=0.05
- SciPy asymptotic method + continuity correction
- project-controlled statistical implementation
- partial W/L/T agreement
- ALO aggregate W/L/T exact
- GWO win count exact
- SHO/SSA/AOA mismatch 较大
- no MATLAB `ranksum` bitwise claim

Fig.9：

```text
SCHO_FIG9_COMPLETE_CONTROLLED_EQUIVALENT
```

- representative run = 1
- 207 curves = 9 * 23
- all 207 final scores regress exactly to H5 run-1 results

H5 总状态：

```text
H5_COMPLETE__SECTION_3_1_3_CLASSICAL_9_ALGORITHM_COMPARISON
```

---

## 7. H6：SCHO Section 3.1.4 full 9-algorithm scalability

H6 已完整完成并推送远端。

正式 protocol：

```text
H6_SCALABILITY_V1
```

协议：

- algorithms = 9
- functions = F1-F13
- dimensions = D=100, D=500
- N=30
- MaxIter=500
- 30 independent runs
- optimizer seeds = 1000..1029
- objective seed =
  `7_000_000 + dim*10_000 + fnum*100 + run`
- AOA uses `mu=0.5`

Formal matrix：

```text
9 * 13 * 2 * 30 = 7020
```

构成：

- reused SCHO H3c = 780 rows
- new 8-comparator runs = 6240 rows

Formal raw：

```text
results/raw/scho_scalability_h6b_runs.csv
```

H6b audit：

- 7020/7020
- each algorithm 780/780
- F7 540/540
- finite stored BestScore
- no optimizer executed during audit

### H6c — Tables 9/10 + Friedman

D=100 reproduced final rank：

```text
SCHO 1
RSA  2
AOA  3
SHO  4
GJO  5
GWO  6
SSA  7
ALO  8
SCA  9
```

Paper preserved positions：

- SCHO 1
- RSA 2
- SSA 7
- ALO 8
- SCA 9

Friedman：

```text
D=100:
statistic = 62.553191
p = 1.4673495e-10

D=500:
statistic = 59.674541
p = 5.3989853e-10
```

两者都在 alpha=0.05 下 reject H0。

D=500 preserved positions 同样为：

- SCHO 1
- RSA 2
- SSA 7
- ALO 8
- SCA 9

主要 mismatch：

```text
AOA
```

AOA 在 project reproduction 中明显比论文更强，
两个维度均 reproduced rank 3、paper rank 6。

H6c freeze：

```text
SCHO_TABLES9_10_COMPLETE__PARTIAL_RANK_LEVEL_AGREEMENT__SCHO_RANK1_PRESERVED_BOTH_DIMS__AOA_MAJOR_MISMATCH__FRIEDMAN_SIGNIFICANT__NO_TUNING
```

### H6d — Tables 11/12 Wilcoxon

方法：

- SCHO vs each comparator
- 30-run distributions
- two-sided Mann-Whitney U / Wilcoxon rank-sum
- alpha=0.05
- asymptotic
- continuity correction
- project-controlled statistical implementation

D=100 reproduced / paper W|L|T：

```text
GWO  8|5|0   vs 10|3|0
ALO 12|1|0   vs 13|0|0
SCA 13|0|0   vs 13|0|0  EXACT
SSA 12|1|0   vs 12|1|0  EXACT
AOA  5|2|6   vs  9|1|3
RSA  4|3|6   vs  5|2|6
SHO  7|0|6   vs 10|1|2
GJO  6|3|4   vs  9|3|1
```

Exact aggregate W|L|T：

```text
2/8
```

D=500：

```text
GWO  9|4|0   vs 10|3|0
ALO 12|1|0   vs 12|1|0  EXACT
SCA 13|0|0   vs 13|0|0  EXACT
SSA 12|1|0   vs 13|0|0
AOA  5|2|6   vs 11|1|1
RSA  4|3|6   vs  5|2|6
SHO  7|3|3   vs  9|2|2
GJO  8|4|1   vs  9|4|0
```

Exact aggregate W|L|T：

```text
2/8
```

SCA 两个维度都 exact。

H6d freeze：

```text
SCHO_TABLES11_12_COMPLETE__PARTIAL_WLT_AGREEMENT__SCA_EXACT_BOTH_DIMS__AOA_MAJOR_MISMATCH__NO_TUNING
```

H6 overall：

```text
H6_COMPLETE__SECTION_3_1_4_FULL_9_ALGORITHM_SCALABILITY_COMPARISON
```

推荐解释：

```text
COMPLETE_PROTOCOL_REPRODUCTION__PARTIAL_NUMERICAL_AGREEMENT__NO_TUNING
```

---

## 8. CEC2014 / SCHO Section 3.2

Stage E 核心实验完成：

- F1-F30
- D=10
- N=30
- MaxIter=500
- 30 runs
- GWO + SCHO

GWO paper-scale consistency：

- within ±25%: 22/30
- within factor 2: 30/30

SCHO：

- within ±25%: 14/30
- within factor 2: 26/30
- material mismatches include F2/F7/F15/F21
- F23/F27 exhibit plateau-type mismatch

Paper lower-mean pairwise：

```text
SCHO 17
GWO  13
```

Project reproduction：

```text
GWO  22
SCHO 8
```

pairwise flips = 9。

最终 exactness boundary：

```text
CORE_DONE__PARTIAL_NUMERICAL_AGREEMENT__FULL_9_ALG_COMPARISON_NOT_RERUN
```

不要声明 SCHO Section 3.2 完整 9-algorithm comparison 已重跑。

---

## 9. Engineering / SCHO Section 3.3 + GWO Section 5

Stage F formal project protocol：

- N=30
- MaxIter=500
- 30 runs
- seeds 1000..1029
- death penalty = `1e30`
- feasibility tolerance = `1e-8`

Stage F：

```text
360/360 optimizer runs
288 feasible best designs
72 NO_FEASIBLE_FOUND
0 structural failures
```

六问题：

- spring
- pressure vessel
- welded beam
- speed reducer
- cantilever
- three-bar truss

SCHO Section 3.3 status：

```text
CORE_DONE__PROJECT_CONTROLLED_PROTOCOL
```

GWO Section 5 status：

```text
PARTIAL__COMMON_PROTOCOL_REPRODUCTION
```

关键边界：

- common Stage-F death penalty 不等于原 GWO Section-5 penalty protocol 的 exact reconstruction。
- 可行率必须与 feasible-only objective quality 分开报告。
- cantilever paper-printed objective 与 Table 20 存在约 10× scale inconsistency。
- `0.06224` 只保留为 Table-20-consistent diagnostic，不冒充论文已确认正确公式。

---

## 10. GWO Section 6 optical buffer / BSPCW

最终项目决定：

```text
INTENTIONALLY_OUT_OF_SCOPE
```

未实现：

- BSPCW fitness evaluator
- NDBP evaluator
- photonic-band simulation
- optical-buffer engineering optimization

这不是剩余 TODO。

除非未来明确重新打开该研究方向，否则不要在 roadmap 中再次把它列为“待完成实验”。

---

## 11. H7 final coverage closeout

H7 新生成的最终覆盖文档：

```text
report/notes/H7_final_full_paper_coverage_audit.md
report/tables/H7_final_full_paper_coverage_matrix.csv
```

这些文档用于替代 H0 的“扩展前状态”作为最终覆盖判断。

H0 文件保留为历史基线，不覆盖、不删除。

H7 最终状态原则：

- H1/H2/H4/H5/H6 已按各自 exactness boundary 完成。
- GWO 6 = intentionally out of scope。
- GWO 5、SCHO 3.2、SCHO 3.3 保留明确 partial/project-controlled 边界。
- 不得写“两个论文所有实验 100% exact reproduced”。

推荐项目级状态：

```text
GWO_SCHO_REPRODUCTION_CLOSEOUT__H0_H6_COMPLETE__DECLARED_SCOPE_BOUNDARIES_PRESERVED
```

---

## 12. 历史总报告

旧文件：

```text
report/final_reproduction_report.md
```

对应 Stage G 核心 reproduction 历史版本。

不要覆盖它。

它只整合到：

- classic F1-F23
- CEC2014
- engineering design

并不包含后来的 H1-H6 full-paper extension。

最终 closeout 应新建：

```text
report/final_reproduction_report_v2.md
```

用于整合 H1-H6 + H7 最终覆盖审计。

---

## 13. 当前本地非正式文件 / 噪声

当前工作树中存在大量与 PPT/Codex/Workbuddy 流程相关的本地文件。

不要使用：

```text
git add .
```

已知需谨慎排除的本地噪声包括：

```text
.chart-data-*/
.codex-finalizer-*/
.workbuddy/
output/
tmp/
report/assets/
storyboard_check_report.md
report/GWO_SCHO_*PPT_QA.md
report/GWO_SCHO_*图表清单.md
report/GWO_SCHO_*storyboard*.md
```

另有：

```text
experiments/generate_scho_fig9_h5h.py
```

当前本地显示 modified，但不是 H7 closeout 应直接纳入的文件。

所有 closeout commit 必须 selective `git add`。

---

## 14. 当前 closeout 进度

已经完成并推送：

```text
H0-H6 scientific reproduction stages
```

当前正在进行：

```text
H7 final coverage / handoff / report-v2 closeout
```

已创建但尚待最终 freeze 的文件：

```text
report/notes/H7_final_full_paper_coverage_audit.md
report/tables/H7_final_full_paper_coverage_matrix.csv
report/notes/HANDOFF.md
```

下一步建议：

1. 更新并保存本 HANDOFF。
2. 创建 `report/final_reproduction_report_v2.md`。
3. 运行 final repository/evidence consistency audit。
4. selective `git add` H7 正式文件。
5. final closeout commit。
6. annotated final tag。
7. push branch/tag。

不要重新运行已经冻结的优化器实验，除非有新的 primary-source evidence 或明确的新研究问题。
