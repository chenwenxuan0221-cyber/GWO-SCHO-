# Stage H1 — GWO F24–F29 Composite Functions: Source / Protocol Audit

## 1. 本阶段目标

重新审计 GWO 原论文 Section 4.3 使用的 F24–F29，并判断能否仅凭 GWO 论文安全实现。

结论：**不能仅凭 GWO 论文 Table 4 就进行 paper-instance 精确实现。**
必须取得 Liang, Suganthan & Deb (2005) 发布的 composition-function source/data
（或能够逐项验证为同一实例的等价镜像）后，再进入 benchmark implementation。

这不是算法阻塞，而是 benchmark-instance 数据阻塞。

---

## 2. GWO 原论文明确给出的协议

GWO Section 4 使用 29 个 benchmark functions：

- F1–F23：classic benchmark functions
- F24–F29：6 个 composite benchmark functions
- F24–F29 dimension：D = 10
- search range：[-5, 5]^10
- optimum value：0
- 每个 benchmark 运行 30 次
- Table 8 报告 Average 与 Std

GWO Table 8 的论文参考值：

| Function | GWO Average | GWO Std |
|---|---:|---:|
| F24 / CF1 | 43.83544 | 69.86146 |
| F25 / CF2 | 91.80086 | 95.5518 |
| F26 / CF3 | 61.43776 | 68.68816 |
| F27 / CF4 | 123.1235 | 163.9937 |
| F28 / CF5 | 102.1429 | 81.25536 |
| F29 / CF6 | 43.14261 | 84.48573 |

---

## 3. Table 4 给出的 CF1–CF6 结构

所有函数均由 n=10 个 basic functions 构成。

### CF1 / F24
- 10 × Sphere
- sigma = [1, ..., 1]
- lambda = [5/100, ..., 5/100]

### CF2 / F25
- 10 × Griewank
- sigma = [1, ..., 1]
- lambda = [5/100, ..., 5/100]

### CF3 / F26
- 10 × Griewank
- sigma = [1, ..., 1]
- lambda = [1, ..., 1]

### CF4 / F27
- f1–f2 Ackley
- f3–f4 Rastrigin
- f5–f6 Weierstrass
- f7–f8 Griewank
- f9–f10 Sphere
- sigma = [1, ..., 1]
- lambda =
  [5/32, 5/32, 1, 1, 5/0.5, 5/0.5, 5/100, 5/100, 5/100, 5/100]

### CF5 / F28
- f1–f2 Rastrigin
- f3–f4 Weierstrass
- f5–f6 Griewank
- f7–f8 Ackley
- f9–f10 Sphere
- sigma = [1, ..., 1]
- lambda =
  [1/5, 1/5, 5/0.5, 5/0.5, 5/100, 5/100, 5/32, 5/32, 5/100, 5/100]

### CF6 / F29
- same basic-function ordering as CF5
- sigma = [0.1, 0.2, ..., 1.0]
- lambda =
  [0.1*(1/5), 0.2*(1/5),
   0.3*(5/0.5), 0.4*(5/0.5),
   0.5*(5/100), 0.6*(5/100),
   0.7*(5/32), 0.8*(5/32),
   0.9*(5/100), 1.0*(5/100)]

---

## 4. Liang et al. composition framework

The construction paper / CEC technical material supplies the general composition formula.

For each component i:

1. Weight

   w_i = exp(
       - sum_k (x_k - o_ik)^2
       / (2 D sigma_i^2)
   )

2. Component transform

   fit_i = f_i( ((x - o_i) / lambda_i) M_i )

3. Height normalization

   fmax_i = f_i( (z / lambda_i) M_i ), z=[5,...,5]

   fit_i <- C * fit_i / fmax_i

4. Weight suppression

   Let MaxW=max_i(w_i).
   The maximum-weight component keeps its weight.
   Other weights are multiplied by (1 - MaxW^10).

5. Normalize weights and combine

   F(x) = sum_i w_i * (fit_i + bias_i) + f_bias

Global construction parameters:
- n = 10
- D = 10
- C = 2000
- bias = [0,100,200,...,900]
- f_bias = 0
- search range = [-5,5]^10

Basic functions:
Sphere, Rastrigin, Weierstrass (a=0.5,b=3,kmax=20),
Griewank and Ackley.

---

## 5. 为什么现在不能直接实现“论文同一实例”

关键缺失不是公式，而是 **instance data**：

- o_i：10 个 component optimum / shift vectors
- M_i：10 个 D×D orthogonal transformation matrices

Liang et al. 说明 o1–o9 在 search range 内随机生成，o10 设为零；
M_i 使用指定方法生成。

这意味着：

> 同一套 CF1–CF6 数学结构，可以产生很多不同的具体 landscape。

GWO Table 8 对应的是作者当时使用的某一套固定 o_i / M_i 数据。
若我们自己重新随机生成 o_i / M_i，虽然仍是合法的 CF1–CF6，
但已经不是论文 Table 8 的同一 benchmark instance，无法把数值差异解释为 GWO reproduction error。

因此 Stage H1 禁止：
- 自己猜 shift vectors；
- 自己生成新的随机 shift/matrix 后仍称“paper reproduction”；
- 用 CEC2014 F24–F29 替代；
- 用标准 CEC2005 competition F15–F25 直接替代；
- 仅根据函数编号把其它年份的 composition functions 当作相同问题。

---

## 6. 一个重要命名澄清

GWO 论文把这 6 个问题描述为来自 “CEC 2005 special session”，并引用：

- Liang, Suganthan & Deb (2005), *Novel composition test functions for numerical global optimization*
- CEC 2005 technical report

但 GWO Table 4 的 CF1–CF6 是上述 **novel composition-function construction**
的 6 个函数，不能仅凭 “CEC2005” 字样就映射成标准 CEC2005 competition
benchmark_func 的某六个编号。

因此本项目建议名称固定为：

`GWO-SIS2005-CF1 ... CF6`

项目内仍可提供 paper aliases：

`F24 ... F29`

这样可避免与 CEC2014 F24–F29 混淆。

---

## 7. H1 freeze decision

### 已冻结
- paper aliases: F24–F29
- canonical names: CF1–CF6
- D=10
- bounds [-5,5]^10
- fmin=0
- GWO paper Table-8 Average / Std
- composition equation / C / bias / sigma / lambda / basic-function definitions

### 尚未冻结
- exact shift vectors o_i
- exact matrices M_i
- exact released MATLAB data/code instance

### 实现门槛
在取得官方 `SIS2005-function-codes`（或经校验的镜像）之前，
**不创建声称与论文 Table 8 同实例的 benchmark backend。**

---

## 8. 下一步

H1b — Source asset acquisition + deterministic validation

需要取得原发布包中的 composition-function code/data，然后首先做确定性验证：

1. 读取 o_i / M_i
2. 检查 shape / finite / orthogonality
3. 验证 global optimum component
4. 与原 MATLAB code 对若干固定 x 做数值交叉验证
5. 通过后才运行 GWO 30-run

在 H1b 通过前不运行 GWO F24–F29 正式统计实验。
