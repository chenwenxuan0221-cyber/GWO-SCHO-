# D2 — GWO vs SCHO 经典 F1–F23 统一对比

## 1. 本阶段目标

在统一实验协议下比较已经完成的 GWO Stage B 与 SCHO C12。两边均使用 N=30、MaxIter=500、30 次独立运行、seed 1000–1029。D1 已单独重跑 GWO F7，使随机噪声函数 F7 的 objective RNG 控制方式与 SCHO C12 一致。

## 2. 统计口径

D2 的主指标是 30 次运行的 Mean，所有函数均为最小化问题。为避免把机器精度级差异解释成有意义的胜负，正式工作簿的 Winner 标签采用绝对差 `1e-12` 作为 practical tie tolerance。稳定性使用 population STD（ddof=0），因为原 GWO Stage B 使用 `np.std(scores)`；SCHO 对应使用 C12 的 `Std_population_ddof0`。

同时保留“严格浮点比较”作为参考：不加容差时，Mean 胜场为 SCHO **15**、GWO **8**。

## 3. 总体结果（practical tolerance = 1e-12）

- Mean：SCHO **12**，GWO **8**，Tie **3**。
- 更低 population STD：SCHO **10**，GWO **10**，Tie **3**。
- Best-of-30：SCHO **14**，GWO **3**，Tie **6**。

按函数族的 Mean practical winner：

- Unimodal F1–F7：GWO 1，SCHO 4，Tie 2。
- Multimodal F8–F13：GWO 2，SCHO 3，Tie 1。
- Fixed-dim F14–F23：GWO 5，SCHO 5，Tie 0。

因此，SCHO 的优势主要集中在高维 unimodal / multimodal benchmark；固定维组则是 5:5，二者各有明显强项。

## 4. Strict Mean 胜负（不设容差）

SCHO Mean 更优：
F1, F2, F3, F4, F6, F7, F8, F9, F10, F11, F14, F15, F16, F17, F19。

GWO Mean 更优：
F5, F12, F13, F18, F20, F21, F22, F23。

其中 F1、F2、F10 属于机器精度级差异，因此 practical 统计将它们记为 Tie。

## 5. 关键现象

- **F7**：D1 后 GWO Mean = 1.95665010e-03，SCHO Mean = 9.29664383e-05。SCHO 仍明显更优，说明此前优势不是由未受控 F7 噪声造成。
- **F9**：SCHO Mean = 0；GWO Mean ≈ 3.279，SCHO 在这一多峰函数上优势明显。
- **F15**：SCHO Mean ≈ 3.27e-04，GWO ≈ 3.86e-03，SCHO 明显更接近全局最优。
- **F18**：GWO Mean ≈ 3.00002 且波动极小；SCHO Mean ≈ 7.58，受到若干大离群 run 影响。这里 GWO 明显更强。
- **F22–F23**：GWO Mean 已非常接近 Shekel 类函数的最优区域，而 SCHO 的若干 run 落在较差局部盆地，是固定维组中 GWO 的突出优势。
- **F16**：两者 Mean 只差约 1.16e-10，虽然 strict winner 是 SCHO，但实际应视为几乎无差别。

## 6. D2 结论

在这套统一 Python 复现实验中：

- 严格浮点 Mean 胜场：**SCHO 15 : GWO 8**；
- 排除 `1e-12` 以内机器精度差异后：**SCHO 12 : GWO 8 : Tie 3**。

SCHO 整体上在经典 23 函数中更占优，尤其是高维连续 benchmark；GWO 则在若干固定维多峰问题（尤其 F18、F22、F23）表现出明显优势。这个结果更支持“算法性能依赖问题类型”，而不是把 23 个函数的总胜场直接外推到后续工程设计问题。

## 7. 数据来源

- GWO：`gwo_classic23_results.csv`；F7 使用 D1 corrected rerun。
- SCHO：`scho_classic23_summary.csv`（C12）。
- D2 不修改 `algorithms/gwo.py` 或 `algorithms/scho.py`。
