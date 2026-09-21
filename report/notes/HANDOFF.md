# HANDOFF.md
# GWO 与 SCHO 论文复现项目技术交接

项目根目录：`D:\Anaconda\envs\DL\metaheuristic-reproduction`
环境：Windows PowerShell，conda `(DL)`，Python 3.11
当前分支：`post-stage-g-h5-freeze`
当前 HEAD：以 `git rev-parse --short HEAD` 为准（本文更新于最终 extension tag 前）

## 1. 总原则
- 优先忠实于作者源码与论文结构。
- 不追求 MATLAB 与 NumPy bitwise RNG 一致。
- 不为了逼近论文数值而调参。
- 源码 quirk 不静默修复。
- 区分 `source-faithful`、`source-structured`、`paper-equation-faithful`、`paper-structure`、`controlled-equivalent`、`project-controlled adapter`。
- 已冻结核心算法不得为了后续结果再次修改。

## 2. Git 冻结链
Core reproduction：
```text
ee3db4f  Freeze Stage G final reproduction report
tag: stage-g-final-report-v1
```

Full-paper extension：
```text
82ae593  Freeze H0-H2 GWO full-paper extension
63a02f8  Freeze H3 SCHO scalability core
4e44904  Freeze H4 SCHO ablation and qualitative analyses
2955124  Freeze H5 SCHO Section 3.1.3 nine-algorithm comparison
5168402  Freeze supplemental provenance and Stage D evidence
c4f89d3  Freeze SCHO 3.3 MATLAB source audit
d98e215  Freeze Stage D corrected F7 rerun provenance
1d43a59  Freeze Stage B GWO comparison figures and data
ef1cac6  Ignore local legacy and superseded artifacts
```

## 3. 冻结核心算法
禁止为后续结果修改：
```text
algorithms/gwo.py
algorithms/scho.py
```

GWO 以冻结源码行为为准，不采用早期 README 中的自动 leader shifting 写法。

SCHO 官方 MATLAB 逐行审计见：
```text
SCHO_3_3_source_audit.md
```
必须保留 `t=2` 起始、candidate/dimension 内重新计算 A、随机数消费顺序、非对称边界行为、`Position_sort` 异常、bounded-search / redistribution 时点与循环位置等源码 quirks。

## 4. H0-H2
H0：完成全文覆盖审计。Stage G 是 strong core reproduction，不代表 100% full-paper coverage。

H1：完成 GWO F24-F29 / SIS2005。F26/CF3 存在论文 Table 4 与作者源码冲突：论文写 Griewank×10，`SIS_novel_func.m` 实际为 Rastrigin×10。正式 primary 使用 source-faithful Rastrigin，Griewank 仅作 diagnostic。结论：source-faithful reproduction attempt，partial numerical agreement。

H2：完成 GWO Section 4 figures。Fig.7-9 为 paper-style；Fig.10-11 为 controlled-equivalent。不得声称 pixel-level 或随机轨迹 exact reproduction。

## 5. H3-H4
H3：SCHO scalability core 完成，仅 SCHO、F1-F13、D=100/500、30 runs，共 780 runs。结论为 strong mean-level agreement；不是完整 9-algorithm scalability。

H4：Table 5 ablation 正式完成，strong rank-level agreement；Fig.8 为 controlled-equivalent；Fig.7 因历史生成源码不足，属于 controlled interpretation / diagnostic，partial bar-level agreement。

## 6. H5：SCHO Section 3.1.3
正式 9 算法：
```text
SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO
```
SHO = Sea-Horse Optimizer。

正式 H5 使用：
```text
algorithms/sea_horse.py
function: sho(...)
```
边界：`SHO_PAPER_EQUATION_FAITHFUL`，历史源码未逐行验证。

不要把以下旧路径与正式 H5 混用：
```text
algorithms/sea_horse_sho.py
experiments/test_sea_horse_sho_h5c7.py
report/notes/H5c7_sea_horse_sho_protocol.md
```

H5 unified smoke：36/36 PASS。

正式 protocol ID：
```text
H5_CLASSICAL_V1
```
optimizer seed：`1000 + run - 1`
objective seed：`5_024_000 + 100*fnum + run`
optimizer RNG 与 objective RNG 分离；随机 objective 仅 F7。

最终 raw：
```text
results/raw/scho_classical_h5_runs.csv
6210 rows = 9 × 23 × 30
```

历史 SCHO：
```text
results/raw/scho_classic23_runs.csv
```
deterministic 660 rows 在 H5 复用，F7 重跑 30。

Table 7 最终 rank：
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
结论：partial rank-level agreement；SCHO rank 1 preserved；SHO mismatch；no tuning。

Table 8：partial W/L/T agreement；ALO exact；GWO win count exact；SHO/SSA/AOA 有较大 mismatch；no tuning。

Fig.9：controlled-equivalent；representative run=1；207 curves；207/207 final-score regression PASS。

H5 总状态：
```text
H5_COMPLETE__SECTION_3_1_3_CLASSICAL_9_ALGORITHM_COMPARISON
```

## 7. 补充 provenance
`5168402` 冻结补充 provenance / Stage D evidence，包括旧 GWO benchmark 脚本、3 张 D3 图和 `results/raw/scho_classic23_runs.csv`。

`c4f89d3` 冻结 `SCHO_3_3_source_audit.md`。

## 8. 当前剩余未跟踪文件
明确不要直接纳入正式 freeze：
```text
README.md
algorithms/sea_horse_sho.py
experiments/test_sea_horse_sho_h5c7.py
report/notes/H5c7_sea_horse_sho_protocol.md
experiments/engineering_gwo.py
experiments/engineering_scho.py
results/raw/scho_classical_h5_checkpoint.jsonl
```

不要使用：
```text
git add .
```
清理剩余 untracked 时必须逐项判断。

## 9. 当前状态
```text
CORE_REPRODUCTION_FROZEN
FULL_PAPER_EXTENSION_H0_H5_FROZEN
```

后续重点：仓库清理、最终 extension tag，以及如有需要再新增明确未覆盖范围；不要重新调整已经冻结的实验结果。
