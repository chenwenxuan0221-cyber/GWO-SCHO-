# GWO + SCHO 原论文实验覆盖审计（基于当前项目 ZIP）

## 审计对象

- 当前项目：`metaheuristic-reproduction.zip`
- 静态检查：算法、benchmark、experiment scripts、raw/processed results、report、Git tags
- Python 语法检查：39 个 `.py` 文件全部通过 `py_compile`
- Git tags 已包含：
  - `scho-source-faithful-v1`
  - `stage-e-cec2014-v1`
  - `stage-f-engineering-v1`
  - `stage-g-final-report-v1`

## 重要结论

当前项目是**高质量的核心复现 v1**，但还不是两篇原论文“所有实验章节 100% 全覆盖”。

最大的遗漏是：

1. GWO 原论文 Section 4.3 的 CEC2005 composite F24-F29。
2. GWO Section 4.4 的 shifted benchmark + 6 search agents + search-history/trajectory 实验。
3. GWO Section 6 optical buffer / BSPCW 真实应用。
4. SCHO Section 3.1.1 消融实验。
5. SCHO Section 3.1.2 qualitative analysis。
6. SCHO Section 3.1.4 D=100 / D=500 scalability。
7. SCHO 3.1.3 与 3.2 的完整 9-algorithm comparison 没有全部重新运行。

## 覆盖矩阵

| Paper | Section | Experiment | Status | Audit |
|---|---|---|---|---|
| GWO | 4 | Results and discussion: 29 benchmark functions | **PARTIAL** | F1-F23 classic reproduced; six CEC2005 composite F24-F29 not implemented. |
| GWO | 4.1 | Exploitation analysis | **CORE_DONE** | GWO F1-F7 30-run statistics reproduced; full PSO/GSA/DE/FEP/CMA-ES rerun not present. |
| GWO | 4.2 | Exploration analysis | **CORE_DONE** | GWO F8-F23 statistics reproduced; full paper comparison-algorithm rerun not present. |
| GWO | 4.3 | Local minima avoidance on CEC2005 composite F24-F29 | **MISSING** | No CEC2005 benchmark module/script/results found. CEC2014 F24-F29 are a different benchmark set. |
| GWO | 4.4 | Convergence behavior analysis | **MISSING** | No exact shifted-function + 6-agent search-history/trajectory experiment found. Existing Stage-B plots are aggregate summaries. |
| GWO | 5 | Three classical engineering problems | **PARTIAL** | Spring/welded-beam/pressure-vessel definitions are present and run in Stage F, but common death penalty differs from original GWO Section-5 penalty protocol. |
| GWO | 6 | Optical buffer design (BSPCW) | **MISSING** | No BSPCW/NDBP/photonic-band evaluator or optical-engineering optimization script/result found. |
| SCHO | 3.1 | 23 classical benchmark functions | **CORE_DONE** | Source-faithful SCHO F1-F23 x30 runs and paper comparison exist. |
| SCHO | 3.1.1 | Four subordinate-model / ablation analysis | **MISSING** | No SCHO_NT/SCHO_NSTF/SCHO_NFTF/SCHO_NSF/SCHO_NFF or variants 1-11 implementation/results found. |
| SCHO | 3.1.2 | Qualitative analysis | **MISSING** | No exact 2D topology/search-history/first-agent trajectory/average-fitness experiment found; frozen SCHO currently returns best curve, not population history. |
| SCHO | 3.1.3 | Comparison with 8 other algorithms | **PARTIAL** | SCHO and GWO runs/comparison exist; ALO/SCA/SSA/AOA/RSA/SHO/GJO are not implemented/rerun, so full Friedman/Wilcoxon experiment is not reproduced. |
| SCHO | 3.1.4 | Scalability analysis D=100 and D=500 | **MISSING** | No dedicated D=100/D=500 experiment/results found; classic_23 benchmark dimensions are currently fixed to paper's base dimensions. |
| SCHO | 3.2 | CEC2014 D=10 | **CORE_DONE_PARTIAL_FULL_COMPARISON** | GWO+SCHO F1-F30 x30 and paper-scale comparison exist; full 9-algorithm Friedman/Wilcoxon comparison is not rerun. |
| SCHO | 3.3 | Six engineering design problems | **CORE_DONE** | All six problems implemented, validated, and run; project uses explicit death penalty constant 1e30 because paper does not state the numeric constant. Other published comparison algorithms are not rerun. |

## 对当前项目文件的具体核对

### GWO

- `algorithms/gwo.py`：存在，且是我们冻结的 source-aligned GWO baseline。
- `benchmarks/classic_23.py`：只定义 F1-F23，不包含 GWO 原论文的 CEC2005 F24-F29。
- `experiments/benchmark_gwo.py` / `benchmark_gwo_with_paper_std.py`：针对经典 F1-F23。
- `experiments/plot_gwo_stageB.py`：是结果汇总图，不是论文 Section 4.4 的 search history / first-agent trajectory。
- `experiments/engineering_gwo.py`：当前是 0 字节空文件，因此不存在隐藏的原版 GWO Section-5 专用 penalty 实验。
- 项目中未发现 `BSPCW`、`NDBP`、`photonic`、`optical buffer` 的实现或结果。

### SCHO

- `algorithms/scho.py`：source-faithful baseline 已完整保留。
- `experiments/benchmark_scho_c12.py`：F1-F23 × 30 runs，属于 3.1 主数值实验核心部分。
- 未发现 `SCHO_NT`、`SCHO_NSTF`、`SCHO_NFTF`、`SCHO_NSF`、`SCHO_NFF` 或 variant 1-11 的实现。
- 未发现 D=100/D=500 scalability runner。
- 未发现用于保存 population search history / first-agent trajectory / average population fitness 的定制 instrumentation。
- CEC2014 的 GWO/SCHO 30-run、paper comparison、GWO-vs-SCHO rank-sum 已存在，但没有其它 7 个 comparison algorithms。

### Engineering

- `benchmarks/engineering_design.py` 与 `constraint_handling.py` 已覆盖 6 个 SCHO 工程题。
- Stage F 的 360-run 结果完整。
- 对 GWO 原论文 Section 5 而言，这属于**共同协议工程比较**，不是严格复现原 GWO penalty scheme。
- `engineering_gwo.py` 与 `engineering_scho.py` 两个历史文件均为空，不应作为有效实验代码。

## 一个容易混淆的重要点

项目 Stage E 的 `CEC2014 F24-F29` **不是** GWO 原论文 Section 4.3 的 `CEC2005 F24-F29`。

虽然函数编号都写作 F24-F29，但它们来自不同 benchmark suite，数学定义和实验目的不同，不能互相替代。

## Git / 项目完整性

把 ZIP 解压到 Linux 后，`git status` 显示很多 tracked files 为 modified；进一步使用 `git diff --ignore-cr-at-eol` 检查后为空，说明这些 tracked-file 变化是 **CRLF/LF 行尾差异**，不是科学内容被改动。

仍有一批历史 untracked 文件（如旧 benchmark 脚本、图、Excel、README 等）。Stage E/F/G 的冻结 commit/tag 本身仍存在。

## 报告需要修正的措辞

当前 `report/final_reproduction_report.md` 的“完整复现链”应该理解为：

> 已完成当前既定范围内，从源码审计、经典 benchmark、CEC2014 到工程设计的核心复现链。

不应再写成：

> 两篇原论文所有实验章节均已完整复现。

在完成 Stage H 之前，建议把最终报告标记为：

**Core reproduction v1 / 核心复现版本**

## 建议的新路线

### Stage H0 — Full-paper coverage freeze
冻结本审计表，明确所有遗漏，不动 Stage G v1。

### Stage H1 — GWO CEC2005 F24-F29
优先补原论文 Section 4.3。

### Stage H2 — GWO convergence behavior
实现 Section 4.4 的 shifted functions、6 agents、search history、first-agent trajectory。

### Stage H3 — SCHO scalability
补 F1-F13 的 D=100 与 D=500。

### Stage H4 — SCHO ablation + qualitative analysis
先实现 variants，再做 Fig.7 / Fig.8 类实验。

### Stage H5 — Full comparison scope decision
决定是否真的实现 ALO/SCA/SSA/AOA/RSA/SHO/GJO，或明确把 full 9-algorithm rerun 排除在复现范围外。

### Stage H6 — GWO optical buffer feasibility audit
先审计 supplementary material 和物理求解依赖；确认能否构建 BSPCW fitness evaluator，再决定是否执行真实 optical reproduction。

### Stage H7 — Final report v2
只有在 Stage H 完成后，再产生“full-paper coverage”版本，不覆盖 `stage-g-final-report-v1`。
