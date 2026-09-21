# H5a — SCHO Section 3.1.3 comparison-protocol audit

## 1. Scope

H5 targets SCHO paper Section 3.1.3: comparison on the 23 classical benchmark
functions.

Algorithms in the paper:

1. SCHO
2. GWO
3. ALO
4. SCA
5. SSA
6. AOA
7. RSA
8. SHO
9. GJO

The current project already has frozen SCHO and GWO optimizer implementations.
The other seven comparison algorithms require a separate source-resolution and
implementation stage before any formal nine-algorithm reproduction.

## 2. Paper protocol

The Section 3.1.3 experiment reuses the earlier classical-benchmark settings:

- F1–F13: D = 30
- F14–F23: native fixed dimensions
- population/search agents N = 30
- MaxIter = 500
- 30 independent runs per algorithm/function

Full theoretical workload:

`9 algorithms × 23 functions × 30 runs = 6210 runs`

If already-completed SCHO/GWO evidence is proven protocol-aligned and reusable,
the seven missing comparators would require:

`7 × 23 × 30 = 4830 new runs`

Reuse must be verified rather than assumed.

## 3. Table 6 parameter anchors

Paper Table 6 lists:

- SCHO:
  - ct = 3.6
  - u = 0.388
  - m = 0.45
  - epsilon = 0.003
  - n = 0.5
  - alpha = 4.6
  - beta = 1.55
  - p = 10
  - q = 9
- GWO:
  - a linearly decreases from 2 to 0
- ALO:
  - w integer in [2, 6]
- SCA:
  - a = 2
- SSA:
  - c2, c3 are random numbers in [0, 1]
- AOA:
  - alpha = 5
  - u = 0.5
- RSA:
  - alpha = 0.1
  - beta = 0.005
- SHO:
  - r1 cut-off point = 0
  - success probability r2 = 0.1
- GJO:
  - c1 = 1.5
  - beta = 1.5

These parameters are paper anchors. They do not by themselves uniquely define
all seven missing algorithms; source-code / original-paper resolution is still
required.

## 4. Table 7 outputs

For each function and algorithm, Table 7 reports:

- Best
- Average
- STD
- Rank

It then reports:

- Mean Rank
- Final Ranking

Paper mean-rank / final-rank anchors:

- SCHO: 2.48 / 1
- GWO: 3.78 / 3
- ALO: 5.43 / 7
- SCA: 7.39 / 9
- SSA: 4.83 / 6
- AOA: 5.83 / 8
- RSA: 4.57 / 5
- SHO: 4.00 / 4
- GJO: 3.74 / 2

These values are diagnostic anchors only. Do not tune implementations to match
them.

## 5. Table 8 statistical test

The paper applies the Wilcoxon rank-sum test between SCHO and each comparator:

- alpha = 0.05
- `+`: SCHO significantly better
- `-`: SCHO significantly worse
- `~`: no significant difference

The paper prints final W|L|T totals:

- GWO: 12|8|3
- ALO: 14|6|3
- SCA: 21|2|0
- SSA: 18|5|0
- AOA: 18|2|3
- RSA: 11|2|10
- SHO: 13|3|7
- GJO: 14|3|6

H5 must reproduce the statistical procedure from raw 30-run samples, not infer
it from Table 7 averages.

## 6. Figure 9

Fig. 9 contains convergence curves of all nine algorithms for all 23 classical
benchmark functions.

A full H5 reproduction therefore has two distinct deliverables:

1. statistical benchmark reproduction (Tables 7 and 8);
2. convergence-curve reproduction (Fig. 9).

Convergence histories must be defined consistently for each comparator before
formal plotting.

## 7. Current exactness boundary

Frozen source-faithful implementations already exist for:

- SCHO
- GWO

Pending:

- ALO
- SCA
- SSA
- AOA
- RSA
- SHO
- GJO

Do not implement these seven algorithms from memory or from abbreviated
secondary pseudocode and then label them source-faithful.

The next stage must resolve the most authoritative implementation source for
each comparator and record any differences between:

- original paper equations,
- official/reference code,
- SCHO paper Table 6 parameters.

## 8. Recommended H5 sequence

### H5a
Protocol audit — **this stage**.

### H5b
Source-resolution matrix for ALO/SCA/SSA/AOA/RSA/SHO/GJO.

### H5c
Implement comparators one by one with deterministic structural tests.

### H5d
Protocol-alignment audit for reuse of existing SCHO/GWO runs.

### H5e
Formal Table 7 runs and summary/ranking reproduction.

### H5f
Table 8 Wilcoxon reproduction.

### H5g
Fig. 9 convergence curves.

### H5h
Paper-agreement diagnostic and H5 freeze.

## 9. H5a status

**H5a — COMPLETE AS A PAPER-PROTOCOL AUDIT.**

Next:

**H5b — resolve authoritative sources and exact implementation conventions for
the seven missing comparison algorithms before writing optimizer code.**
