# H4a — SCHO Section 3.1.1 / 3.1.2 source and protocol audit

## 1. Goal

Freeze what the paper actually requires for:

- Section 3.1.1 — analysis of the four subordinate models;
- Section 3.1.2 — qualitative analysis of SCHO.

H4a runs no optimizer and does not modify the frozen `algorithms/scho.py`.

---

## 2. Section 3.1.1 — four subordinate models

The paper defines four subordinate models:

1. exploration;
2. exploitation;
3. bounded-search strategy;
4. switching mechanism.

The first ablation compares SCHO with five structural variants on all F1–F23.

### Five Table-5 structural variants

| Name | Paper definition | Models retained |
|---|---|---|
| SCHO | full algorithm | 1 + 2 + 3 + 4 |
| SCHO_NT | without the 3rd subordinate model | 1 + 2 + 4 |
| SCHO_NSTF | without 2nd, 3rd, 4th | 1 only: exploration |
| SCHO_NFTF | without 1st, 3rd, 4th | 2 only: exploitation |
| SCHO_NSF | without 2nd and 4th | 1 + 3 |
| SCHO_NFF | without 1st and 4th | 2 + 3 |

The prose interpretation above is directly implied by the paper's own
numbering of the four models.

### Formal Table-5 protocol

The paper states:

- functions: F1–F23;
- N = 30 search agents;
- MaxIter = 500;
- 15,000 fitness evaluations;
- F1–F13: D = 30;
- F14–F23: fixed native dimensions;
- 30 independent runs per algorithm/function.

Table 5 reports:

- Best;
- Average;
- STD;
- per-function Rank;
- Mean Rank;
- Final Ranking.

### Table-5 paper anchors

Mean Rank:

| Variant | Mean Rank |
|---|---:|
| SCHO | 1.65 |
| SCHO_NT | 2.96 |
| SCHO_NSTF | 3.35 |
| SCHO_NFTF | 4.52 |
| SCHO_NSF | 2.13 |
| SCHO_NFF | 3.35 |

Final Ranking printed by the paper:

- SCHO: 1
- SCHO_NSF: 2
- SCHO_NT: 3
- SCHO_NSTF: 4
- SCHO_NFF: 4
- SCHO_NFTF: 6

These values are paper-reference anchors only and must never be used to tune
the implementation.

---

## 3. Section 3.1.1 — Fig. 7 variants

Fig. 7 is a second, separate ablation layer. It compares SCHO against eleven
additional variants and plots the **number of average optimal solutions**.

### Fig. 7(a): second exploitation phase

- Variant 1:
  use the first-phase exploitation equation in both exploitation phases.
- Variant 2:
  remove the second-phase exploitation equation.

Paper bar-count anchors:

- SCHO vs Variant 1: 18 vs 15
- SCHO vs Variant 2: 20 vs 13

### Fig. 7(b): sinh/cosh replacements in search equations

- Variant 3:
  replace sinh/cosh by sine/cosine with the same value range in the
  second-phase exploitation equation.
- Variant 4:
  replace sinh/cosh by sine/cosine with the same value range in the
  first-phase exploration equation.
- Variant 5:
  replace sinh/cosh by linear functions with the same value range in the
  second-phase exploitation equation.
- Variant 6:
  replace sinh/cosh by linear functions with the same value range in the
  first-phase exploration equation.

Paper bar-count anchors:

- SCHO vs Variant 3: 17 vs 15
- SCHO vs Variant 4: 17 vs 14
- SCHO vs Variant 5: 17 vs 16
- SCHO vs Variant 6: 18 vs 14

### Fig. 7(c): alternative switching mechanisms

- Variant 7: switching mechanism using sine/cosine;
- Variant 8: switching mechanism using linear functions;
- Variant 9: equal selection probability for exploration and exploitation.

Paper bar-count anchors:

- SCHO vs Variant 7: 20 vs 13
- SCHO vs Variant 8: 20 vs 11
- SCHO vs Variant 9: 18 vs 9

### Fig. 7(d): replacements specifically inside Eq. (17)

- Variant 10: sine/cosine in Eq. (17);
- Variant 11: linear functions in Eq. (17).

Paper bar-count anchors:

- SCHO vs Variant 10: 20 vs 13
- SCHO vs Variant 11: 18 vs 15

---

## 4. Important exactness boundary for Fig. 7

The audited official SCHO package used to freeze `algorithms/scho.py` exposed
the main SCHO implementation, but no separate implementation of Table-5 /
Fig.-7 variants has been recovered in the current project evidence.

The paper gives clear conceptual definitions for the five Table-5 variants.

However, for several Fig.-7 variants the prose says:

- "sine & cosine with the same value range";
- "linear functions with the same value range";
- alternative switching mechanism using those functions.

The exact replacement formulas are not printed in Section 3.1.1.

Therefore:

- do **not** silently invent a formula and call it source-exact;
- Table-5 structural variants can be implemented first and validated against
  the published Table-5 behavior;
- Fig.-7 variants that require unspecified transforms must be labeled
  `PAPER-DESCRIBED / CONTROLLED-INTERPRETATION` unless exact variant source is
  recovered later.

This distinction is essential for a defensible reproduction.

---

## 5. Workload

### Table 5

Six algorithms/variants total:

`6 × 23 × 30 = 4140 optimizer runs`

This includes the full SCHO baseline.

The existing Stage-C SCHO baseline is useful evidence, but the formal Table-5
rerun should use a common H4 seed/objective-RNG convention across all variants
so the comparison is internally controlled.

### Fig. 7

Eleven additional variants:

`11 × 23 × 30 = 7590 variant runs`

If one shared SCHO baseline is reused, the union of Table-5 and Fig.-7 models is:

`17 models × 23 × 30 = 11730 formal optimizer runs`

This is large enough that H4 must be staged and checkpointable.

---

## 6. Section 3.1.2 — Fig. 8 qualitative analysis

Visual inspection of the paper figure identifies seven displayed functions:

- F2
- F7
- F9
- F10
- F11
- F15
- F21

Fig. 8 uses five qualitative columns:

1. parameter-space / 2-D function surface;
2. search history;
3. trajectory of the first dimension of the first agent;
4. average fitness of all search agents;
5. convergence curve of the best solution.

The x-axis visible in the published histories is 0–500 iterations.

The optimization dimensions should follow the benchmark protocol:

- F2/F7/F9/F10/F11: D = 30;
- F15: fixed D = 4;
- F21: fixed D = 4.

The 2-D parameter-space panels are visual projections/surfaces and do not imply
that the optimizer itself was run at D=2 for F2/F7/F9/F10/F11.

### Paper qualitative observations to check later

The paper describes:

- larger trajectory frequency/amplitude early and much smaller movement later;
- average population fitness becoming small rapidly;
- a transient average-fitness increase around iteration ~140 for many
  functions, associated by the authors with the first/second-phase switch;
- smoother convergence on unimodal functions;
- more stepwise convergence on multimodal functions;
- later improvements on F9/F10;
- bounded-search-assisted later improvement on F21.

These are qualitative paper observations, not pass/fail numerical targets.

---

## 7. Fig. 8 exactness boundary

The paper does not state the random seed used for Fig. 8, and the exact
history-sampling implementation is not separately published.

Therefore H4 qualitative reproduction should use:

`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`

Recommended project convention:

- frozen source-faithful `algorithms/scho.py` behavior;
- N = 30;
- MaxIter = 500;
- project optimizer seed = 1000;
- a separate fixed F7 objective RNG;
- instrumentation in a new H4 module, leaving `algorithms/scho.py` unchanged;
- explicitly freeze when positions and fitness are sampled within an iteration.

Do not claim pixel-exact trajectory reproduction.

---

## 8. Recommended H4 sequence

### H4a — source/protocol audit
Current stage. No optimizer runs.

### H4b — source-faithful SCHO history instrumentation + Fig. 8 smoke validation
Goal:
- instrument the frozen SCHO logic without modifying `algorithms/scho.py`;
- verify final best/position/convergence remain exactly equal to frozen SCHO;
- validate F2/F7/F9/F10/F11/F15/F21 history shapes.

### H4c — generate Fig. 8 qualitative reproduction
- 7 functions;
- N=30;
- MaxIter=500;
- five paper-style panels per function;
- raw history evidence + manifest;
- controlled-equivalent label.

### H4d — implement and unit-test the five Table-5 structural variants
No formal 4140-run launch until one-run/seeded equivalence and branch semantics
are verified.

### H4e — Table-5 formal 4140-run ablation
- checkpoint/resume;
- Best/Average/STD;
- Friedman-style ranking;
- paper comparison.

### H4f — Fig.-7 variant source-resolution decision
Attempt to recover exact variant source/equations.
If exact source remains unavailable, freeze explicit controlled
interpretations before any 7590-run launch.

### H4g — Fig.-7 formal reproduction
Only after H4f definitions are frozen.

---

## 9. H4a acceptance decision

H4a status:

**COMPLETE**

The next safe step is:

**H4b — SCHO history instrumentation for Fig. 8**

This is deliberately chosen before the very large Table-5/Fig.-7 ablation
runs. It validates the qualitative-history layer cheaply while preserving the
frozen optimizer.
