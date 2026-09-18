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
