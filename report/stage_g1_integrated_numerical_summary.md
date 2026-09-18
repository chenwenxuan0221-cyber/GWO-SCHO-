# Stage G1 — Integrated Numerical Summary

## 1. Purpose

G1 consolidates the frozen numerical evidence from the classic benchmarks, CEC2014, and engineering-design experiments. No optimizer is rerun and no frozen conclusion is retuned.

## 2. Cross-stage overview

| Domain | Scope | Primary metric | Headline result |
|---|---|---|---|
| Classic F1-F23 | 23 functions | lower 30-run mean objective/error under Stage D rule | GWO lower mean: 8; SCHO lower mean: 12; Ties: 3 |
| CEC2014 | F1-F30, D=10 | mean error + paper-scale agreement | Reproduction lower mean: GWO 22, SCHO 8; Within ±25% of paper mean error: GWO 22/30, SCHO 14/30; Paper/reproduction pairwise flips: 9 |
| Engineering design | 6 problems × 2 algorithms × 30 runs | feasible rate + feasible-only objective quality | Feasible runs: 288/360; NO_FEASIBLE_FOUND: 72/360; Structural failures: 0 |

## 3. Classic F1-F23

Under the frozen Stage D practical mean-comparison rule, GWO had the lower mean on **8/23** functions, SCHO on **12/23**, with **3 ties**.

| Family | Functions | GWO lower mean | SCHO lower mean | Tie |
|---|---:|---:|---:|---:|
| F1-F7 | 7 | 1 | 4 | 2 |
| F8-F13 | 6 | 2 | 3 | 1 |
| F14-F23 | 10 | 5 | 5 | 0 |

These counts are descriptive results under the project reproduction protocol; stochastic/local-optimum deviations were retained rather than tuned away.

## 4. CEC2014

Stage E reproduced 30 CEC2014 functions at D=10. GWO mean errors were within ±25% of the paper values on **22/30** functions and within a factor of 2 on **30/30**. SCHO was within ±25% on **14/30** and within a factor of 2 on **26/30**.

The paper's pairwise lower-mean count was GWO 13 vs SCHO 17; the reproduction produced GWO 22 vs SCHO 8, with 9 pairwise flips.

The frozen Stage E interpretation remains: the GWO scale was broadly reproduced, while SCHO's relative advantage was not fully reproduced. The result is retained rather than corrected by tuning.

## 5. Engineering design

F4 completed all 360 requested runs: **288** returned feasible best designs, **72** were `NO_FEASIBLE_FOUND`, and there were **0 structural failures**.

| Problem | Alg. | Feasible | Rate | Best feasible | Paper | Best gap |
|---|---|---:|---:|---:|---:|---:|
| spring | GWO | 26/30 | 86.7% | 0.01269251641 | 0.0126656 | +0.213% |
| spring | SCHO | 30/30 | 100.0% | 0.01271284805 | 0.0126656 | +0.373% |
| pressure_vessel | GWO | 30/30 | 100.0% | 5898.46787 | 5889.0061 | +0.161% |
| pressure_vessel | SCHO | 30/30 | 100.0% | 6013.651107 | 5889.0061 | +2.117% |
| welded_beam | GWO | 18/30 | 60.0% | 1.727472228 | 1.72516 | +0.134% |
| welded_beam | SCHO | 19/30 | 63.3% | 1.733002838 | 1.72516 | +0.455% |
| speed_reducer | GWO | 1/30 | 3.3% | 3003.935707 | 2995.2477 | +0.290% |
| speed_reducer | SCHO | 14/30 | 46.7% | 3008.618945 | 2995.2477 | +0.446% |
| cantilever_printed | GWO | 30/30 | 100.0% | 13.01247099 | 1.3033 | N/A (formula mismatch) |
| cantilever_printed | SCHO | 30/30 | 100.0% | 13.01485319 | 1.3033 | N/A (formula mismatch) |
| three_bar_truss | GWO | 30/30 | 100.0% | 263.8977231 | 263.8958476 | +0.001% |
| three_bar_truss | SCHO | 30/30 | 100.0% | 263.89688 | 263.8958476 | +0.000% |

Welded beam and especially speed reducer show why feasible rate must be reported separately from best feasible objective. For speed reducer, GWO found a feasible design in only 1/30 runs while SCHO did so in 14/30.

Cantilever remains a special source anomaly: the primary experiment uses the paper-printed `0.6224` objective, while the `0.06224` version is retained only as a separately labelled Table-20-consistent diagnostic.

## 6. Integrated interpretation

Across the three benchmark families, there is no single scalar result that adequately summarizes reproduction quality. Classic functions mainly reveal stochastic optimizer behavior; CEC2014 tests whether the paper-scale performance transfers to a harder modern benchmark suite; engineering problems additionally expose feasibility-handling behavior.

The final report should therefore keep four evidence dimensions separate: (1) source-faithful implementation, (2) objective/error quality, (3) stochastic variation, and (4) feasibility success under constraints.

## 7. G1 status

**G1 RESULT: PASS**

The numerical evidence is now consolidated and ready for G2, where the integrated final report can be drafted without rerunning any optimizer.
