# H3a — SCHO Section 3.1.4 Scalability Source / Protocol Audit

## 1. Stage goal

Freeze the exact experimental scope of SCHO Section 3.1.4 before writing or
running any high-dimensional optimizer code.

H3a runs no optimizer and modifies no frozen algorithm.

---

## 2. Paper-defined scalability experiment

Section 3.1.4 states that scalability is evaluated on **13 classical benchmark
functions** at two high-dimensional settings:

- F1–F13, D = 100
- F1–F13, D = 500

The paper states that the search-agent count, iteration count, and number of
runs are:

- search agents = 30
- iterations = 500
- runs = 30

The paper wording uses “running times” for the last quantity, but Tables 9–12
are statistical multi-run results and the experiment context is 30 independent
runs. In this project it is recorded as:

`30 independent runs`

without claiming recovery of the paper's random seeds.

---

## 3. Algorithms included in the original experiment

Tables 9 and 10 compare **nine algorithms**:

1. SCHO
2. GWO
3. ALO
4. SCA
5. SSA
6. AOA
7. RSA
8. SHO
9. GJO

Therefore a SCHO-only D=100/D=500 experiment is useful, but it is **not the
complete original Section 3.1.4 experiment**.

The full paper-level reproduction requires the 8 comparison algorithms as well.

---

## 4. Statistics reported

For every F1–F13 and every algorithm, Tables 9 and 10 report:

- Best
- Average
- STD
- Rank

They also report:

- Mean Rank
- Final Ranking

The paper uses a Friedman ranking analysis across the 13 functions.

Separate significance analysis is reported in:

- Table 11: D = 100
- Table 12: D = 500

using the **Wilcoxon rank-sum test** at:

`alpha = 0.05`

with SCHO compared against each of the other eight algorithms.

---

## 5. Paper ranking anchors

These paper values are useful later as table-level validation anchors.

### D = 100 — Table 9 mean rank

| Algorithm | Mean Rank |
|---|---:|
| SCHO | 1.85 |
| GWO | 4.15 |
| ALO | 7.69 |
| SCA | 8.69 |
| SSA | 6.54 |
| AOA | 4.77 |
| RSA | 2.85 |
| SHO | 3.31 |
| GJO | 4.00 |

Final ranking printed in the paper:

`SCHO, RSA, SHO, GJO, GWO, AOA, SSA, ALO, SCA`

### D = 500 — Table 10 mean rank

| Algorithm | Mean Rank |
|---|---:|
| SCHO | 2.00 |
| GWO | 4.62 |
| ALO | 7.54 |
| SCA | 8.23 |
| SSA | 6.69 |
| AOA | 5.31 |
| RSA | 2.54 |
| SHO | 3.38 |
| GJO | 4.00 |

Final ranking printed in the paper:

`SCHO, RSA, SHO, GJO, GWO, AOA, SSA, ALO, SCA`

These are paper-reference anchors only. They must not be used to tune algorithms.

---

## 6. Important benchmark implications

### 6.1 F1–F13 become dimension-variable

The current core project originally used the classic benchmark suite at its
base paper dimensions (primarily D=30 for F1–F13).

H3 must therefore provide a **dimension override / high-dimensional benchmark
adapter** rather than silently editing the frozen classic benchmark definitions.

Preferred architecture:

- keep `benchmarks/classic_23.py` unchanged;
- add a new H3-specific adapter/helper that constructs F1–F13 at arbitrary
  dimension D=100 or D=500;
- preserve original formulas and original variable bounds.

### 6.2 F7 remains stochastic

F7 contains a random term.

The high-dimensional runner must preserve the already-established project rule:
objective randomness must be reproducible and independent of the optimizer RNG
where the benchmark API supports this.

Do not silently turn F7 deterministic.

### 6.3 Function bounds remain function-specific

Increasing dimension changes `D`, not the underlying per-coordinate search
range.

Examples:
- F1 uses its original bound replicated to D coordinates;
- F8 uses its original Schwefel bound replicated to D coordinates;
- F9 uses its original Rastrigin bound replicated to D coordinates;
- etc.

No common artificial bound should be introduced.

---

## 7. SCHO implementation rule

Use the already frozen source-faithful:

`algorithms/scho.py`

Do not modify it for high dimensions.

All known source-faithful quirks remain part of the reproduction, including:
- source random-call structure;
- source boundary behavior;
- source redistribution behavior;
- source sorting / second-best behavior;
- 500 evaluation-batch convention already frozen by the project.

High-dimensional reproduction must expose the behavior of the frozen
implementation rather than redesign it.

---

## 8. Random-seed rule

The paper does not publish the 30 random seeds.

For the project, the recommended convention remains:

`seeds = 1000 ... 1029`

This must be labeled:

`project reproducibility convention`

and never described as the paper's original random stream.

---

## 9. Runtime scale

### SCHO-only core scalability

13 functions × 2 dimensions × 30 runs:

`780 optimizer runs`

### SCHO + GWO project-core comparison

13 × 2 × 30 × 2:

`1560 optimizer runs`

### Full original nine-algorithm Section 3.1.4

13 × 2 × 30 × 9:

`7020 optimizer runs`

The full paper experiment also requires implementing and validating:
ALO, SCA, SSA, AOA, RSA, SHO, and GJO.

Therefore H3 should be staged rather than launching 7020 runs immediately.

---

## 10. Reproduction tiers for H3

### Tier 1 — SCHO scalability core

Required:
- F1–F13 at D=100 and D=500
- source-faithful SCHO
- N=30
- MaxIter=500
- 30 runs
- Best / Average / STD
- paper-value comparison for SCHO

This answers the narrow question:
“Does the frozen SCHO implementation reproduce the paper's high-dimensional
SCHO behavior?”

### Tier 2 — Project-core comparison

Add:
- frozen GWO under the same D=100 / D=500 protocol

This gives a controlled GWO-vs-SCHO scalability comparison.

### Tier 3 — Full paper Section 3.1.4

Add:
- ALO
- SCA
- SSA
- AOA
- RSA
- SHO
- GJO
- full Friedman ranking
- Tables 11/12 Wilcoxon significance analysis

Only Tier 3 can be called a complete rerun of the original nine-algorithm
Section 3.1.4 comparison.

---

## 11. Recommended H3 sequence

### H3a — source/protocol audit
Current stage. No optimizer runs.

### H3b — high-dimensional F1–F13 benchmark adapter + smoke validation
- D=100 / D=500
- formula/bound checks
- F7 RNG check
- source-faithful SCHO integration smoke test
- frozen files unchanged

### H3c — SCHO 780-run scalability experiment
- 13 × 2 × 30
- checkpoint/resume
- raw + summary
- paper SCHO comparison

### H3d — diagnostic / freeze of SCHO scalability core
- D100/D500 agreement analysis
- preserve deviations without tuning

### H3e — comparator expansion
Either:
- execute full 8-comparator implementation/validation here,
or
- defer it to the dedicated full-comparator stage, while keeping H3 marked
  `CORE_COMPLETE / FULL_COMPARISON_PENDING`.

Because the overall project goal is full-paper coverage, the comparator work
must eventually be completed or explicitly remain a documented limitation.

---

## 12. H3a completion decision

H3a status:

**COMPLETE**

Frozen paper protocol:

- functions: F1–F13
- dimensions: D=100 and D=500
- search agents: 30
- iterations: 500
- runs: 30
- algorithms in complete paper comparison: 9
- descriptive statistics: Best / Average / STD
- Friedman ranking
- Wilcoxon rank-sum test, alpha=0.05

Next:

**H3b — dimension-flexible F1–F13 adapter + source-faithful SCHO smoke test**

No large experiment should be launched before H3b passes.
