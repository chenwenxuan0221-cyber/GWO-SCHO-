# SCHO 3.3 官方 MATLAB 源码逐行审计

审计对象：用户上传的官方 SCHO 3.3 MATLAB 包  
主文件：`SCHO.m`  
辅助文件：`initialization.m`, `main.m`

## 标记
- ✅ 论文与源码一致
- ⚠️ 论文未明确，但源码给出具体实现
- ❌ 源码与论文描述/变量语义存在明显不一致或疑似缺陷
- ?  仅静态阅读不足，需运行实验验证

---

## C8-1 初始化、第一次适应度、迭代计数

### SCHO.m 14–20
```matlab
function [Destination_fitness,Destination_position,Convergence_curve]=SCHO(N,Max_iteration,lb,ub,dim,fobj)

Destination_position=zeros(1,dim);
Destination_fitness=inf;
Destination_position_second=zeros(1,dim);
Convergence_curve=zeros(1,Max_iteration);
Position_sort = zeros(N,dim);
```

审计：
- `Destination_position`：历史最优位置，初始全 0。
- `Destination_fitness`：历史最优适应度，初始 `Inf`。
- `Destination_position_second`：名义上的次优位置，初始全 0。
- `Position_sort`：名义上用于排序位置，但只初始化为全 0；后续未发现 `Position_sort = X` 或其它将候选位置写入它的语句。❌
- `Convergence_curve`：长度等于 `Max_iteration`。

### SCHO.m 22–35
```matlab
u=0.388;
m=0.45;
n=0.5;
p=10;
q=9;
Alpha=4.6;
Beta=1.55;
BS=floor(Max_iteration/Beta);
ct=3.6;
T=floor(Max_iteration/ct);
BSi=0;
BSi_temp=0;
ub_2=ub;
lb_2=lb;
```

审计：
- 参数与论文一致：`u=0.388, m=0.45, n=0.5, p=10, q=9, Alpha=4.6, Beta=1.55, ct=3.6`。✅
- `epsilon=0.003` 没有作为变量初始化，而是在第二阶段探索公式中硬编码。⚠️
- 当 `Max_iteration=500`：
  - `T = floor(500/3.6) = 138`
  - `BS = floor(500/1.55) = 322`

### initialization.m 15–31
```matlab
if Boundary_no==1
    X=rand(SearchAgents_no,dim).*(ub-lb)+lb;
end

if Boundary_no>1
    for i=1:dim
        ub_i=ub(i);
        lb_i=lb(i);
        X(:,i)=rand(SearchAgents_no,1).*(ub_i-lb_i)+lb_i;
    end
end
```

审计：
- 标量上下界：一次 `rand(N,dim)`。✅
- 不同维度不同上下界：按维度逐列初始化。✅
- 与论文 Eq. (2) 一致。✅

### SCHO.m 37–48
```matlab
X=initialization(N,dim,ub,lb);
Objective_values = zeros(1,size(X,1));

for i=1:size(X,1)
    Objective_values(1,i)=fobj(X(i,:));
    if Objective_values(1,i)<Destination_fitness
        Destination_position=X(i,:);
        Destination_fitness=Objective_values(1,i);
    end
end
Convergence_curve(1)=Destination_fitness;
t=2;
```

审计：
- 先评估初始种群的全部 N 个候选解。
- `Destination_fitness/position` 是历史最优，而非“每代重置”的当前代最优。✅
- 初始种群评估结果记为 `Convergence_curve(1)`。
- 主循环从 `t=2` 开始。⚠️
- 因而 Eq. (17) 不会在 `t=0` 计算，避免 `sinh(0)=0` 问题。
- 总评估批次：初始 1 批 + t=2..500 共 499 批 = 500 批。
- N=30 时总函数评价次数 = 500×30 = 15000，与论文实验协议一致。✅

---

## C8-2 主循环、A 与四种搜索模式

### SCHO.m 50–57
```matlab
while t<=Max_iteration
    for i=1:size(X,1)
        for j=1:size(X,2)
            cosh2=(exp(t/Max_iteration)+exp(-t/Max_iteration))/2;
            sinh2=(exp(t/Max_iteration)-exp(-t/Max_iteration))/2;
            r1=rand();
            A=(p-q*(t/Max_iteration)^(cosh2/(sinh2)))*r1;
```

审计：
- `t=2,...,Max_iteration`。
- `A` 在 **每个 candidate、每个 dimension** 内重新计算。✅
- Eq. (17) 的真实源码形式是“幂指数”：
  `z^(cosh(z)/sinh(z))`，不是乘法。✅
- 源码中的 `r1` 实际承担论文 Eq. (17) 的 `r13` 角色。⚠️
- 随机变量名与论文编号不一致，但数学分布角色可对应。

### 第一阶段：t <= T，SCHO.m 73–97
```matlab
r2=rand();
r3=rand();
a1=3*(-1.3*t/Max_iteration+m);
r4=rand();
r5=rand();

if A>1
    sinh=(exp(r3)-exp(-r3))/2;
    cosh=(exp(r3)+exp(-r3))/2;
    W1=r2*a1*(cosh+u*sinh-1);
    if r5<=0.5
        X(i,j)=Destination_position(j)+r4*W1*X(i,j);
    else
        X(i,j)=Destination_position(j)-r4*W1*X(i,j);
    end
else
    sinh=(exp(r3)-exp(-r3))/2;
    cosh=(exp(r3)+exp(-r3))/2;
    W3=r2*a1*(cosh+u*sinh);
    if r5<=0.5
        X(i,j)=Destination_position(j)+r4*W3*X(i,j);
    else
        X(i,j)=Destination_position(j)-r4*W3*X(i,j);
    end
end
```

审计：
- 每个坐标固定消耗 `r2,r3,r4,r5` 四个随机数，无论最后走 exploration 还是 exploitation。⚠️
- `a1` 与论文 Eq. (6) 一致。✅
- `W1` 与论文 Eq. (5) 数学结构一致，但随机变量编号不同：
  - 论文 `r3`（W1 幅度） ↔ 源码 `r2`
  - 论文 `r4`（sinh/cosh 自变量） ↔ 源码 `r3`
  - 论文 Eq. (4) 步长随机数 ↔ 源码 `r4`
  - 论文 Eq. (4) 正负选择 ↔ 源码 `r5`
- 源码正负判断是 `r5<=0.5` 用加号；论文文字/公式的随机变量编号和不等号方向与源码并不逐字相同。由于随机变量为 U(0,1)，正负概率仍各约 50%，统计意义相同，但固定随机流下轨迹不同。⚠️
- `W3` 的括号没有 `-1`，与论文 Eq. (11) 一致。✅

### 第二阶段：t > T，SCHO.m 100–116
```matlab
r2=rand();
r3=rand();
a2=2*(-t/Max_iteration+n);
W2=r2*a2;
r4=rand();
r5=rand();

if A<1
    sinh=(exp(r3)-exp(-r3))/2;
    cosh=(exp(r3)+exp(-r3))/2;
    X(i,j)=X(i,j)+(r5*sinh/cosh*abs(W2*Destination_position(j)-X(i,j)));
else
    if r4<=0.5
        X(i,j)=X(i,j)+(abs(0.003*W2*Destination_position(j)-X(i,j)));
    else
        X(i,j)=X(i,j)+(-abs(0.003*W2*Destination_position(j)-X(i,j)));
    end
end
```

审计：
- `a2` 与 Eq. (9) 一致。✅
- `W2=r2*a2` 与 Eq. (8) 数学结构一致。✅
- 当 `A<1`：第二阶段 exploitation，结构与 Eq. (12) 一致。✅
  - `r3` 是 sinh/cosh 自变量。
  - `r5` 是系数随机数。
  - `r4` 已生成但本分支不使用；它仍然消耗 RNG。⚠️
- 当 `A>=1`：第二阶段 exploration，结构与 Eq. (7) 一致。✅
  - `0.003` 硬编码。
  - `r4` 决定正负。
  - `r3` 与 `r5` 已生成，但本分支不用于位置式；依旧消耗 RNG。⚠️
- `A==1` 在源码进入 exploration 分支；概率上几乎不会精确发生。⚠️

### 每坐标的 RNG 顺序（无 bounded search 时）
第一阶段：
1. `r1` → A
2. `r2`
3. `r3`
4. `r4`
5. `r5`

第二阶段：
1. `r1` → A
2. `r2`
3. `r3`
4. `r4`
5. `r5`

因此，若做“source-faithful” Python 版本，应保留“每个坐标固定 5 次标量随机调用”的结构，而不是只在需要的分支才生成随机数。⚠️

---

## C8-3 普通边界处理、fitness 与历史最优

### SCHO.m 122–134
```matlab
Flag4ub=X(i,:)>ub_2;
Flag4lb=X(i,:)<lb_2;
X(i,:)=(X(i,:).*(~(Flag4ub+Flag4lb))) ...
       +(ub_2+lb_2)/2.*Flag4ub ...
       +lb_2.*Flag4lb;

Objective_values(1,i)=fobj(X(i,:));

if Objective_values(1,i)<Destination_fitness
    Destination_position=X(i,:);
    Destination_fitness=Objective_values(1,i);
end
```

审计：
- 边界修复发生在 **整轮位置更新完成之后、fitness 计算之前**。⚠️
- 不是 `clip`：
  - 在界内 → 保持原值
  - 超过上界 → 放到 `(ub_2+lb_2)/2`（当前搜索区中点）
  - 低于下界 → 直接设为 `lb_2`
- 修复方式明显不对称。⚠️
- fitness 逐个体计算。
- best 为历史最优：只有更优才覆盖，不会每代重置。✅
- bounded search 后 `ub_2/lb_2` 会继续作为后续边界处理范围，不自动恢复原始 `ub/lb`。⚠️

---

## C8-4 Bounded Search 的真实触发机制

### 源码还会把 bounded-search 新边界限制回原始边界

在位置循环的 bounded-search 块中，源码在 Eq. (15)/(16) 计算 `ub_2/lb_2` 后立即执行：

```matlab
if ub_2>ub
    ub_2=ub;
end
if lb_2<lb
    lb_2=lb;
end
```

因此 source-faithful 版本必须保留这一层限制。对于 F1 这类标量上下界，含义非常直接：新上界不能高于原始 `ub`，新下界不能低于原始 `lb`。✅/⚠️

### “计划时刻”与“实际重分布时刻”并不相同

初始：
```matlab
BS=floor(Max_iteration/Beta);   % 322
BSi=0;
BSi_temp=0;
```

每轮 fitness 完成后：
```matlab
if t==BS
    BSi=BS+1;
    BS=BS+floor((Max_iteration-BS)/Alpha);
    ...
end
```

因此：
- `t=322`：只设置 `BSi=323`，并计算下一次 `BS=360`。
- 真正重新初始化发生在下一轮 `t=323`，因为位置循环内判断的是 `if t==BSi`。⚠️

例如 MaxIter=500 的 `BS` 序列：
`322, 360, 390, 413, 431, 446, 457, 466, 473, 478, 482, 485, 488, 490, 492, 493, 494, 495, 496`

对应实际重分布从：
`323, 361, 391, 414, ...` 开始。

### 更关键：每个 bounded-search 事件会重新初始化 N 次

位置循环：
```matlab
for i=1:N
    for j=1:dim
        ...
        if t==BSi
            ...
            X=initialization(N,dim,ub_2,lb_2);
            BSi_temp=BSi;
            BSi=0;
        end
        ...
    end
    BSi=BSi_temp;
end
```

执行逻辑：
- 对 `i=1,j=1`：`t==BSi`，重初始化整个 X，随后 `BSi=0`。
- 同一个 `i` 的 j=2...dim 不再触发。
- i=1 结束后，`BSi=BSi_temp` 恢复。
- 到 `i=2,j=1` 再次触发，又重初始化整个 X。
- 如此直到 `i=N`。

因此一次 bounded-search 事件实际调用：
`initialization(N,dim,...)` **N 次**。❌/⚠️

这也恰好解释论文复杂度中 redistribution 被写为 `O(z*N^2*D)`：一次事件 N 次重建一个 N×D 的种群。

副作用：
- 前面 i 的更新会被后续 i 的整群重初始化抹掉。
- 最后一次（i=N）重初始化后，只有第 N 个 candidate 随后真正执行四种位置公式；1...N-1 保持为最后一次重新随机生成的值。
- bounded-search 事件会额外消耗大量随机数。

### 新 bounds 实际只用 j=1 计算

因为每个 i 中第一次触发发生在 `j=1`，随后 `BSi=0`，所以：
```matlab
ub_2=Destination_position(1)+...
lb_2=Destination_position(1)-...
```

之后 `ub_2/lb_2` 成为标量，并用于 `initialization(N,dim,ub_2,lb_2)`，即 **所有维度都使用由第 1 维 best 推出的同一个区间**。❌/⚠️

这与论文 Eq. (15)–(16) 按第 j 维构造 bounds 的直观含义并不一致。

---

## C8-5 second-best / Position_sort 数据流审计

### 初始化
```matlab
Destination_position_second=zeros(1,dim);
Position_sort=zeros(N,dim);
```

### 在整个 SCHO.m 中
未发现任何：
```matlab
Position_sort = X;
```
或
```matlab
Position_sort(i,:) = X(i,:);
```

### 排序代码
```matlab
if Objective_values(1,j) > Objective_values(1,j+1)
    ...
    temp2(j,:) = Position_sort(j,:);
    Position_sort(j,:) = Position_sort(j+1,:);
    Position_sort(j+1,:) = temp2(j,:);
end
...
Destination_position_second=Position_sort(2,:);
```

由于 `Position_sort` 从头到尾为全零矩阵，只是在零行之间交换，所以：
```matlab
Destination_position_second
```
在源码字面执行下始终为全零向量。❌

因此 bounded search 实际使用：
```text
second-best = 0-vector
```
而不是当前真正的第二优候选解。

这会把 Eq. (15)/(16) 实际变成（触发时 j=1）：
```text
radius = (1 - t/MaxIter) * abs(best[1] - 0)
```

### 排序循环还有一个 off-by-one 特征
```matlab
for i=1:(N-1)
    for j=1:(N-1-i)
```
当 i=1 时 j 只到 N-2，没有比较第 N-1 与第 N 个元素，因此第 N 个 fitness 从未参与邻接交换。⚠️

但由于 `Position_sort` 本身是零矩阵，这个排序缺陷不会改变“second-best 始终为 0”的核心结论。

### 另外
排序直接原地修改 `Objective_values` 的顺序，但下一轮 fitness 评估会重新覆盖全部 N 个值；历史最优已在排序前更新，因此该排序对 best 不产生直接影响。⚠️

---

## C8-6 main.m 实验协议

```matlab
maxFunc = 23;
SearchAgents_no = 30;
Max_iteration= 500;
runs = 30;
```

每个 F1–F23：
```matlab
for run=1:runs
    [Best_score,Best_pos,cg_curve]=SCHO(...);
    Best_score_T(run) = Best_score;
end

Best_score_Best = min(Best_score_T);
Best_Score_Mean = mean(Best_score_T);
Best_Score_std = std(Best_score_T);
```

审计：
- 23 个经典函数。
- N=30。
- MaxIter=500。
- 每函数独立运行 30 次。
- 输出 Best / Mean / Std。
- 与论文实验协议一致。✅
- `main.m` 没有设置固定 RNG seed，所以论文/官方代码的 30 次结果默认依赖当时 MATLAB 的随机状态。⚠️

---

# 最终 Source-Faithful 实现规则

若目标是“忠实复现官方 SCHO 3.3 MATLAB 代码实际行为”，Python 应遵循：

1. 初始化 N×dim 种群。
2. 先评估初始种群并建立历史 best。
3. `curve[0] = best`。
4. 主迭代对应 MATLAB `t=2..MaxIter`。
5. 每个 i,j 先标量生成一次随机数用于 A。
6. Eq. (17) 使用真正的幂指数形式。
7. 每个坐标再固定生成 4 个随机数，即使其中有些在当前分支不使用。
8. `t<=T`：第一阶段；否则第二阶段。
9. 第一阶段 A>1 exploration，否则 exploitation。
10. 第二阶段 A<1 exploitation，否则 exploration。
11. 一轮所有位置更新完成后才做边界修复。
12. 上越界 → 当前范围中点；下越界 → 当前下界。
13. best 是历史 best。
14. `Position_sort` 源码行为保持全零，因此 source-faithful second-best 为零向量。
15. `t==BS` 时只“计划”下一轮 bounded event；实际重分布在 `t=BS+1`。
16. bounded event 中，每个 i 在 j=1 时都重初始化整个种群一次，共 N 次。
17. bounded bounds 由 best 的第 1 维与 0 构造为标量，再应用到所有维度。
18. bounded 后的新 `ub_2/lb_2` 持续用于后续边界修复。
19. convergence curve 在每轮 fitness 更新后记录历史 best。
20. 30×500 时总函数评价 15000 次/单次 run。

---

# 审计结论

官方 SCHO 3.3 源码与论文在核心数学模型（T、a1、a2、W1、W2、W3、A、四种位置更新）上总体一致，但实现层面存在若干非常重要的特殊行为：

1. `t` 从 2 开始，而非 0/1。
2. 随机变量编号和论文不同，并且会生成一些当前分支未使用的随机数。
3. 边界恢复不是 clip，而是“上越界→中点，下越界→下界”。
4. bounded search 实际延后 1 个 iteration 执行。
5. bounded event 每次把整个种群重新初始化 N 次。
6. bounded bounds 实际只使用第 1 维构造，并作为标量作用于所有维度。
7. `Position_sort` 从未装入 X，因此 `Destination_position_second` 按源码字面行为始终为零向量。
8. bubble sort 还有一个 off-by-one 特征。

其中第 5–7 点足以显著影响优化结果，因此后续 Python 复现不应“悄悄修正”。建议同时保留：
- `source-faithful`：严格模拟官方 3.3 源码；
- `paper-intended`：按论文真正的 second-best、逐维 bounded bounds、每次 bounded event 只重新分布一次。

先用 `source-faithful` 对齐论文表格；如偏差明显，再用 `paper-intended` 做对照实验并在报告中解释源码异常。
