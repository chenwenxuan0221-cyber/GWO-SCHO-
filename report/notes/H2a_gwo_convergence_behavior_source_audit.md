# Stage H2a — GWO Section 4.4 Convergence-Behavior Source/Protocol Audit

## 1. 本阶段目标

审计 GWO 原论文 Section 4.4 / Fig. 11 的真实实验结构，
在不修改冻结版 `algorithms/gwo.py` 的前提下，确定后续如何做
history instrumentation 与可视化复现。

本阶段不运行优化器。

---

## 2. 论文正文能够明确确认的内容

Section 4.4 明确说明：

- 目标：观察 GWO 的 convergence behavior；
- 展示：
  - search history；
  - 第一个 search agent 在第一维上的 trajectory；
- benchmark functions 在本节被 shifted；
- 使用 **six search agents**；
- 动画版本位于 Supplementary Materials。

正文还说明：
- 初期 position change 应出现较大的 abrupt changes；
- 后期变化逐渐减小，以强化 exploitation；
- Fig. 11 第二列是 search history；
- Fig. 11 第四列是 first agent / first dimension trajectory。

---

## 3. Fig. 11 实际选取的 8 个函数

对论文 Fig. 11 两页进行视觉核对后，函数为：

1. F1
2. F7
3. F9
4. F10
5. F14
6. F18
7. F26
8. F29

这 8 个函数跨越：

- unimodal：F1、F7
- multimodal：F9、F10
- fixed-dimensional multimodal：F14、F18
- composite：F26、F29

因此 Fig. 11 不是只对某一函数族做可视化。

---

## 4. Fig. 11 每一行的 6 个 panel

从左到右：

1. 3D function surface / 2D landscape view
2. Search history
3. `a`
4. Trajectory in 1st dimension
5. Fitness history
6. Convergence curve

其中参数 `a` 从 2 线性下降到 0。

Fig. 11 横轴清楚显示 0–100：
- `a` panel：0–100
- trajectory：0–100
- fitness history：0–100
- convergence curve：0–100

因此 **Fig. 11 图形证据强烈支持 MaxIter = 100**。

注意：论文正文没有单独用一句话写 “MaxIter=100”，
所以项目中应标记为：

`MaxIter=100 (figure-evident, not prose-explicit)`

而不是声称正文明确给出。

---

## 5. 尚未由论文充分指定的关键参数

### 5.1 Exact shift vectors

论文只说：

> benchmark functions are shifted in this section

但没有列出每个函数的 shift vector。

Fig. 11 的 first-dimension trajectories 可以帮助观察最终位置，
但不能恢复完整 shift vector，尤其对高维函数更不能。

因此不能从图中“反推一个大概 shift”再称为 exact reproduction。

### 5.2 Optimization dimension

Fig. 11 使用：
- 3D surface；
- x1/x2 search-history plane；
- first-dimension trajectory。

这证明展示是二维/前二维投影，但**不充分证明优化本身全部使用 D=2**。

原 benchmark 默认维度不同：
- F1、F7、F9、F10：论文 Tables 1–2 为 D=30；
- F14、F18：固定 D=2；
- F26、F29：Table 4 为 D=10。

原文没有在 Section 4.4 明确写出：
- 保持这些原始维度，
或
- 统一改成 D=2。

因此 dimension 必须继续标记为 unresolved。

### 5.3 Random seed / random stream

论文未提供 Fig. 11 的 seed。
即使 protocol 其它部分全部恢复，也不应预期轨迹逐点相同。

### 5.4 Exact history-sampling semantics

论文没有明确写：
- position history 是 boundary repair 前还是后；
- fitness history 是 population mean、所有 agent fitness、还是其它统计；
- initial population 是否记作 iteration 0；
- trajectory 是 update 前还是 update 后位置。

这些可能可由 supplementary source/animation 辅助恢复。

---

## 6. 官方公开 GWO code 能确认什么

当前公开的官方 GWO repository 提供：

- `GWO.m`
- `main.m`
- `Get_Functions_details.m`
- `func_plot.m`
- `initialization.m`

公开 `main.m` 是一般 benchmark demo：
- SearchAgents_no = 30
- Max_iteration = 500
- Function_name can be F1–F23

它**不是** Fig. 11 的 Section-4.4 qualitative runner。

因此不能把公开 `main.m` 的 30/500 参数直接覆盖到 Fig. 11。

冻结版项目中的 `algorithms/gwo.py` 继续保持不动。

---

## 7. 与 H1 的衔接

Fig. 11 包含：
- F26 / CF3
- F29 / CF6

因此 composite rows 应继续使用 H1 冻结的
source-faithful SIS2005 benchmark assets。

特别是 F26：
- GWO Table 4 打印 Griewank ×10；
- 上传的原 `SIS_novel_func.m` 使用 Rastrigin ×10。

H2 不应在 qualitative experiment 中偷偷切换定义。

---

## 8. H2 推荐实现架构

不要修改：

`algorithms/gwo.py`

新增独立 instrumentation 层，例如：

- `experiments/gwo_history_instrumented.py`
- `experiments/run_gwo_convergence_h2.py`
- `experiments/plot_gwo_convergence_h2.py`

instrumented implementation 的要求：

1. 和冻结 GWO 的 update/evaluation/random-call structure 对齐；
2. 只额外记录：
   - position_history
   - fitness_history
   - first-agent first-dimension trajectory
   - historical best convergence
   - a history
3. 有自动 regression test：
   同一 seed / 同一 benchmark 下，instrumented 版本的
   final score / best position / convergence curve 必须与冻结版
   `algorithms/gwo.py` 对齐。
4. history recording 不能改变 RNG 消耗顺序。

---

## 9. H2 reproduction tiers

### Tier A — Exact/source-backed

需要取得 Section 4.4 Supplementary Materials 或对应生成脚本，
从中确认：
- shift vectors；
- dimensions；
- exact history semantics；
- 其它可能的 plot protocol。

若取得，则按 source-backed protocol 实现。

### Tier B — Paper-structure reproduction

若 supplementary material 无法取得，则可以复现论文明确可观察的结构：

- 8 个相同函数；
- 6 search agents；
- 100 iterations；
- shifted benchmarks；
- 同样的 6-panel qualitative metrics；
- 透明记录 deterministic shift convention；
- 不宣称逐点重现 Fig. 11。

这应标记为：

`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`

不能标记为 exact Fig.-11 reproduction。

---

## 10. 当前 H2a 结论

已确认：

- functions = F1, F7, F9, F10, F14, F18, F26, F29
- search agents = 6
- MaxIter = 100（图形证据）
- functions are shifted
- 6-panel structure
- supplementary animations exist

仍缺：

- exact shift vectors
- exact optimization dimensions
- exact seed
- exact history sampling semantics
- supplementary generation code/data

因此：

**H2a = COMPLETE**
**H2b implementation = WAITING FOR SUPPLEMENTARY CHECK / OR CONTROLLED-EQUIVALENT DECISION**

---

## 11. 下一步

优先尝试取得论文 Supplementary Materials。

如果用户能从 DOI / ScienceDirect 的 supplementary data 下载任何：
- ZIP
- MATLAB files
- videos/animations
- additional code/data

请原样上传，不要先改名或编辑。

如果补充材料无法获得，则进入 H2b：
构建不修改 frozen GWO 的 instrumented adapter，并采用明确标注的
controlled-equivalent shift protocol。
