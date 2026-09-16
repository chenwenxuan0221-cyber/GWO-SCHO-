# F0 — Engineering Design Problems Protocol Audit

## 1. Goal

Freeze the engineering-design problem definitions before running GWO or SCHO.

Primary source: Bai et al., *A Sinh Cosh optimizer*, Section 3.3 and Tables 16–21.

Secondary cross-check: Mirjalili et al., *Grey Wolf Optimizer*, Section 5 and Tables 9–11, only for the three overlapping classical engineering problems.

No optimizer is run in F0.

---

## 2. Constraint handling stated by the SCHO paper

The SCHO paper uses a **simple death penalty** for the six constrained engineering problems. If a search agent violates any constraint, its fitness is assigned a large/significant value so that it is discarded in a later selection/update step.

Important limitation: the paper does **not** state the exact numerical penalty constant.

Therefore F0 freezes only the rule:

- feasible candidate -> evaluate the physical objective;
- infeasible candidate -> death-penalty fitness;

but the exact finite penalty value is **not source-specified** and must be documented as an implementation choice in F1.

---

## 3. Problem inventory

| ID | Problem | Dim | Constraints | Paper bounds | SCHO reported design | SCHO reported objective |
|---|---|---:|---:|---|---|---:|
| P1 | Tension/compression spring | 3 | 4 | x1:[0.05,2], x2:[0.25,1.3], x3:[2,15] | (0.0517422, 0.3579972, 11.2146238) | 0.0126656 |
| P2 | Pressure vessel | 4 | 4 | x1:[0,99], x2:[0,99], x3:[10,200], x4:[10,200] | (0.7796836, 0.3854124, 40.39092, 199.0132) | 5889.0061 |
| P3 | Welded beam | 4 | 7 | x1:[0.1,2], x2:[0.1,10], x3:[0.1,10], x4:[0.1,2] | (0.20565, 3.47312, 9.03685, 0.20573) | 1.72516 |
| P4 | Speed reducer | 7 | 11 | [2.6,3.6], [0.7,0.8], [17,28], [7.3,8.3], [7.3,8.3], [2.9,3.9], [5,5.5] | (3.50008, 0.7, 17, 7.3, 7.72871, 3.35023, 5.28736) | 2995.2477 |
| P5 | Cantilever beam | 5 | 1 | each xi:[0.01,100] | (5.9763, 4.8878, 4.4573, 3.4732, 2.1447) | 1.3033 |
| P6 | Three-bar truss | 2 | 3 | x1,x2:[0,1] | (0.78866420, 0.40827926) | 263.8958476 |

---

## 4. Paper equations

### P1 — Tension/compression spring

Variables:

- x1 = wire diameter d
- x2 = mean coil diameter D
- x3 = number of active coils P

Objective:

f(x) = (x3 + 2) x2 x1^2

Constraints as printed:

g1(x) = 1 - x2^3 x3 / (71785 x1^4) <= 0

g2(x) = (4 x2^2 - x1 x2) / [12566 (x2 x1^3 - x1^4)]
        + 1 / (5108 x1^2) <= 0

g3(x) = 1 - 140.54 x1 / (x2^2 x3) <= 0

g4(x) = (x1 + x2)/1.5 - 1 <= 0

Bounds intended by the paper:

0.05 <= x1 <= 2  
0.25 <= x2 <= 1.3  
2 <= x3 <= 15

#### F0 anomaly

The printed variable-range line writes `2 <= x1 <= 15`, but x3 is the third design variable and the intended range is clearly x3:[2,15].

More importantly, the printed g2 is internally inconsistent with the reported SCHO solution. At the reported design, the printed g2 is approximately +0.9999994 and would violate g2<=0. The familiar feasibility-compatible form requires a terminal `-1`:

g2_corrected(x) =
(4 x2^2 - x1 x2) / [12566 (x2 x1^3 - x1^4)]
+ 1/(5108 x1^2) - 1 <= 0

With this terminal `-1`, the reported SCHO point is approximately active/feasible.

**F1 should implement the corrected g2, but the correction must be documented rather than silently applied.**

---

### P2 — Pressure vessel

Variables:

x1 = Ts, x2 = Th, x3 = R, x4 = L

Objective:

f(x) =
0.6224 x1 x3 x4
+ 1.7781 x2 x3^2
+ 3.1661 x1^2 x4
+ 19.84 x1^2 x3

Constraints:

g1 = -x1 + 0.0193 x3 <= 0

g2 = -x2 + 0.00954 x3 <= 0

g3 = -pi x3^2 x4 - (4/3) pi x3^3 + 1,296,000 <= 0

g4 = x4 - 240 <= 0

Bounds:

0 <= x1 <= 99  
0 <= x2 <= 99  
10 <= x3 <= 200  
10 <= x4 <= 200

The reported SCHO point reproduces the reported objective to rounding and satisfies the printed constraints.

#### F0 anomaly / ambiguity

The paper describes the pressure-vessel problem as a mixed-integer design problem, but Section 3.3.2 does not provide a discretization/rounding rule. Its reported SCHO x1 and x2 values are continuous-valued.

Therefore the **source-faithful SCHO-paper reproduction should not invent a discrete projection rule**. A discrete-thickness variant may be studied separately, but must not be mixed with the main reproduction.

---

### P3 — Welded beam

Variables:

x1 = h, x2 = l, x3 = t, x4 = b

Objective:

f(x) =
1.10471 x1^2 x2
+ 0.04811 x3 x4 (14 + x2)

Constraints:

g1 = tau(x) - tau_max <= 0  
g2 = sigma(x) - sigma_max <= 0  
g3 = x1 - x4 <= 0  
g4 = f(x) - 5 <= 0  
g5 = 0.125 - x1 <= 0  
g6 = delta(x) - delta_max <= 0  
g7 = P - Pc(x) <= 0

Auxiliary quantities:

tau(x) = sqrt[(tau')^2 + 2 tau' tau'' x2/(2R) + (tau'')^2]

tau' = P / (sqrt(2) x1 x2)

tau'' = M R / J

M = P (L + x2/2)

R = sqrt[x2^2/4 + ((x1+x3)/2)^2]

J = 2 sqrt(2) x1 x2 [x2^2/12 + ((x1+x3)/2)^2]

sigma(x) = 6 P L / (x4 x3^2)

delta(x) = 4 P L^3 / (E x3^3 x4)

Pc(x) =
[4.013 E sqrt(x3^2 x4^6 / 36) / L^2]
[1 - x3/(2L) sqrt(E/(4G))]

Constants:

P = 6000 lb  
L = 14 in  
E = 30e6 psi  
G = 12e6 psi  
tau_max = 13600 psi  
sigma_max = 30000 psi  
delta_max = 0.25 in

Bounds:

0.1 <= x1 <= 2  
0.1 <= x2 <= 10  
0.1 <= x3 <= 10  
0.1 <= x4 <= 2

The reported SCHO point is feasible under these equations and reproduces the reported objective to rounding.

---

### P4 — Speed reducer

Variables: x1,...,x7.

Objective:

f(x) =
0.7854 x1 x2^2 (3.3333 x3^2 + 14.9334 x3 - 43.0934)
- 1.508 x1 (x6^2 + x7^2)
+ 7.4777 (x6^3 + x7^3)
+ 0.7854 (x4 x6^2 + x5 x7^2)

Constraints:

g1 = 27/(x1 x2^2 x3) - 1 <= 0

g2 = 397.5/(x1 x2^2 x3^2) - 1 <= 0

g3 = 1.93 x4^3/(x2 x3 x6^4) - 1 <= 0

g4 = 1.93 x5^3/(x2 x3 x7^4) - 1 <= 0

g5 =
sqrt[(745 x4/(x2 x3))^2 + 16.9e6] / (110 x6^3) - 1 <= 0

g6 =
sqrt[(745 x5/(x2 x3))^2 + 157.5e6] / (85 x7^3) - 1 <= 0

g7 = x2 x3/40 - 1 <= 0

g8 = 5 x2/x1 - 1 <= 0

g9 = x1/(12 x2) - 1 <= 0

g10 = (1.5 x6 + 1.9)/x4 - 1 <= 0

g11 = (1.1 x7 + 1.9)/x5 - 1 <= 0

Bounds:

2.6 <= x1 <= 3.6  
0.7 <= x2 <= 0.8  
17 <= x3 <= 28  
7.3 <= x4,x5 <= 8.3  
2.9 <= x6 <= 3.9  
5 <= x7 <= 5.5

The reported SCHO point reproduces the reported objective to rounding and satisfies the constraints.

#### F0 ambiguity

The text describes x3 as the number of teeth on the pinion, but Section 3.3.4 does not specify an integer-enforcement operator. Table 19 reports x3=17.

For the main source-faithful reproduction, F1 should not invent an integer-projection mechanism unless it is explicitly introduced as a separate variant.

---

### P5 — Cantilever beam

Variables: x1,...,x5.

Printed objective:

f_printed(x) = 0.6224 (x1+x2+x3+x4+x5)

Printed constraint:

g_printed(x) =
60/x1^3 + 27/x2^3 + 19/x3^3 + 7/x4^3 + 1/x5^3 - 1 <= 0

Bounds:

0.01 <= xi <= 100

Reported SCHO design:

(5.9763, 4.8878, 4.4573, 3.4732, 2.1447)

Reported objective:

1.3033

#### Major F0 inconsistency

At the reported SCHO design:

- sum(xi) = 20.9393
- using the **printed** coefficient 0.6224 gives f ≈ 13.0326
- the paper/table reports 1.3033

Therefore Table 20 cannot be reproduced from the printed objective equation.

The printed constraint at the reported SCHO point is feasible (left-hand sum ≈ 0.9953 before subtracting 1), so the main internal inconsistency is the objective coefficient/result relationship.

A coefficient of approximately 0.06224 would numerically reproduce the SCHO table row, but **the paper does not print 0.06224**, so F0 does not treat that value as established fact.

**Conclusion:** P5 cannot be frozen as a unique source-faithful mathematical problem from this paper alone. F1 must either:
1. preserve a `paper_printed` formulation and accept that it cannot match Table 20; or
2. add a separately labeled `table_consistent` formulation, with the coefficient explicitly marked as an implementation assumption.

Do not silently overwrite the printed equation.

---

### P6 — Three-bar truss

Variables: x1, x2.

Objective:

f(x) = (2 sqrt(2) x1 + x2) l

Constraints:

g1 =
[(sqrt(2)x1 + x2)/(sqrt(2)x1^2 + 2x1x2)] P - sigma <= 0

g2 =
[x2/(sqrt(2)x1^2 + 2x1x2)] P - sigma <= 0

g3 =
[1/(sqrt(2)x2 + x1)] P - sigma <= 0

Constants:

l = 100 cm  
P = 2 kN/cm^2  
sigma = 2 kN/cm^2

Bounds:

0 <= x1,x2 <= 1

The reported SCHO design reproduces the reported objective essentially exactly and is feasible.

#### Minor text typo

The prose says the two variables include `A1(x1)` and `A2(x1)`; the mathematical formulation clearly uses x1 and x2.

---

## 5. Cross-check with the GWO paper

The original GWO paper uses three of the same classical engineering problems:

- tension/compression spring
- welded beam
- pressure vessel

Its reported GWO values include:

- Spring: x=(0.05169, 0.356737, 11.28885), f=0.012666
- Welded beam: x=(0.205676, 3.478377, 9.03681, 0.205778), f=1.72624
- Pressure vessel: x=(0.812500, 0.434500, 42.089181, 176.758731), f=6051.5639

The SCHO paper reproduces the GWO literature values for welded beam and pressure vessel in Tables 18 and 17, respectively.

Constraint handling differs in wording:

- SCHO paper: simple death penalty for all six engineering problems.
- GWO paper: penalty functions; simple scalar penalties for most engineering problems, but a more complex penalty function for the spring problem.

Therefore a future **common-handler GWO-vs-SCHO experiment** is a controlled project comparison, not an exact reproduction of both papers' original constraint-handling implementations.

---

## 6. Engineering-specific experiment settings: what is and is not stated

The SCHO engineering section explicitly states the six problems and the death-penalty strategy, but it does **not** restate:

- population N,
- MaxIter,
- number of independent runs,
- seed policy,
- exact numerical death-penalty constant.

Elsewhere in the paper, the benchmark experiments use N=30, MaxIter=500 and 30 independent runs, but that statement is tied to the benchmark-function experiment section rather than explicitly to Section 3.3.

Therefore Stage F must distinguish:

- **source-stated engineering protocol:** problem equations, bounds, constraints, death-penalty concept;
- **project reproduction convention:** any chosen N, MaxIter, run count, seed policy and numeric penalty.

Do not claim N=30 / MaxIter=500 / 30 runs as an engineering-specific paper setting unless additional source evidence is found.

---

## 7. F0 freeze decisions

F0 freezes the following decisions for the next implementation stage:

1. Implement all six SCHO engineering problems in a dedicated benchmark module.
2. Keep all physical objectives separate from constraint handling.
3. Expose constraints individually so feasibility can be audited numerically.
4. Implement the spring bound typo as x3:[2,15].
5. Implement spring g2 with the documented terminal `-1` correction because otherwise the reported solution is not feasible.
6. Pressure vessel: use continuous variables for the main SCHO-paper reproduction; do not invent a discrete projection.
7. Speed reducer: do not invent integer rounding for x3 in the main source-faithful formulation.
8. Cantilever beam: preserve the printed formulation and explicitly support a separately labeled table-consistent diagnostic variant; do not silently rewrite the equation.
9. Three-bar truss: use the printed equations and x1/x2 variables.
10. Do not modify frozen `algorithms/gwo.py` or `algorithms/scho.py`.

---

## 8. F0 acceptance status

F0 is complete when this audit is accepted as the source-of-truth for implementing the engineering benchmark layer.

Recommended next stage:

**F1 — implement and numerically validate the six engineering benchmark definitions only.**

F1 should first evaluate the paper's reported SCHO design points and print every constraint value. No optimizer should be run until those deterministic checks pass.

