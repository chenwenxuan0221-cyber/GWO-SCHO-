# Stage F5 — Engineering paper comparison and diagnostics

## 1. Scope and protocol

F5 does **not** rerun GWO or SCHO. It reads the frozen F4 outputs and compares feasible-only results with the Stage-F0 paper reference values from SCHO Tables 16–21.

Project protocol: N=30, MaxIter=500, 30 runs, seeds 1000–1029, death penalty=1e30, feasibility tolerance=1e-8. These are project reproduction settings; the SCHO engineering section does not state this complete engineering-specific numerical protocol.

Feasibility success rate and feasible-only solution quality are reported separately. A run with `NO_FEASIBLE_FOUND` is retained as data and is not replaced, retuned, or averaged as if it were a normal feasible solution.

## 2. Feasibility results

| Problem | GWO feasible | SCHO feasible | Both feasible seeds | GWO-only | SCHO-only | Neither |
|---|---:|---:|---:|---:|---:|---:|
| spring | 26/30 (86.7%) | 30/30 (100.0%) | 26 | 0 | 4 | 0 |
| pressure_vessel | 30/30 (100.0%) | 30/30 (100.0%) | 30 | 0 | 0 | 0 |
| welded_beam | 18/30 (60.0%) | 19/30 (63.3%) | 10 | 8 | 9 | 3 |
| speed_reducer | 1/30 (3.3%) | 14/30 (46.7%) | 0 | 1 | 14 | 15 |
| cantilever_printed | 30/30 (100.0%) | 30/30 (100.0%) | 30 | 0 | 0 | 0 |
| three_bar_truss | 30/30 (100.0%) | 30/30 (100.0%) | 30 | 0 | 0 | 0 |

The paired-seed counts show whether the feasibility difference comes from the same or different random seeds. They are descriptive only; F5 does not turn them into a claim of general algorithm superiority.

## 3. Paper-reference comparison

For five internally consistent formulations, the table below compares the best feasible F4 objective directly with the SCHO paper-reported reference objective. Negative gap means the reproduction best is numerically lower than the reported reference; positive gap means it is numerically higher. This is a numerical comparison, not proof of equivalent experimental protocol.

| Problem | Algorithm | Feasible runs | Best feasible | Paper reported | Best gap | Gap % |
|---|---|---:|---:|---:|---:|---:|
| spring | GWO | 26/30 | 0.01269251641 | 0.0126656 | 2.691640791e-05 | 0.213% |
| spring | SCHO | 30/30 | 0.01271284805 | 0.0126656 | 4.724805251e-05 | 0.373% |
| pressure_vessel | GWO | 30/30 | 5898.46787 | 5889.0061 | 9.46177018 | 0.161% |
| pressure_vessel | SCHO | 30/30 | 6013.651107 | 5889.0061 | 124.6450066 | 2.117% |
| welded_beam | GWO | 18/30 | 1.727472228 | 1.72516 | 0.002312228401 | 0.134% |
| welded_beam | SCHO | 19/30 | 1.733002838 | 1.72516 | 0.007842837924 | 0.455% |
| speed_reducer | GWO | 1/30 | 3003.935707 | 2995.2477 | 8.688006539 | 0.290% |
| speed_reducer | SCHO | 14/30 | 3008.618945 | 2995.2477 | 13.37124482 | 0.446% |
| three_bar_truss | GWO | 30/30 | 263.8977231 | 263.8958476 | 0.001875496417 | 0.001% |
| three_bar_truss | SCHO | 30/30 | 263.89688 | 263.8958476 | 0.001032387065 | 0.000% |

## 4. Cantilever paper inconsistency

At the Table-20 design point, the paper-printed objective `0.6224*sum(x)` evaluates to approximately **13.03262032**, whereas Table 20 reports **1.3033**. The separately labelled diagnostic coefficient `0.06224` evaluates to approximately **1.303262032**.

Therefore the primary F4 cantilever results are **not directly compared** to Table 20 as an optimization gap. For diagnostic purposes only, multiplying the printed-objective F4 values by 0.1 gives:

| Algorithm | Printed best | Diagnostic 0.06224 best | Table 20 | Diagnostic gap % |
|---|---:|---:|---:|---:|
| GWO | 13.01247099 | 1.301247099 | 1.3033 | -0.158% |
| SCHO | 13.01485319 | 1.301485319 | 1.3033 | -0.139% |

This diagnostic does **not** assert that 0.06224 is the confirmed paper formula, and it does not introduce the separate literature variant with a first constraint coefficient of 61.

## 5. Problem-level diagnostics

- **Spring:** GWO found feasible designs in 26/30 runs and SCHO in 30/30. Both produced best feasible objectives on the same ~0.0127 scale as the paper reference.
- **Pressure vessel:** both algorithms were feasible in 30/30 runs. The experiment uses the continuous formulation frozen in F0; no unreported thickness discretization is introduced.
- **Welded beam:** feasibility was intermittent (GWO 18/30, SCHO 19/30). Paired seeds: both=10, GWO-only=8, SCHO-only=9, neither=3.
- **Speed reducer:** this was the strongest feasibility bottleneck under pure death penalty: GWO 1/30 versus SCHO 14/30. Because infeasible candidates all receive the same `1e30`, F5 does not interpret returned infeasible positions as meaningful 'near-feasible' optima.
- **Cantilever:** both algorithms were feasible in 30/30 runs, but the primary printed-objective values remain on the ~13 scale; the Table-20 ~1.3033 value is handled only through the explicitly labelled diagnostic above.
- **Three-bar truss:** both algorithms were feasible in 30/30 runs and their best feasible values are close to the paper reference scale.

## 6. F5 conclusion

The Stage-F engineering implementation is structurally stable: F4 completed all 360 requested runs with zero structural failures. However, pure death-penalty feasibility is problem dependent. Spring, pressure vessel, cantilever, and three-bar truss were mostly or fully feasible, while welded beam and especially speed reducer showed substantial feasibility failures.

For five internally consistent problems, the best feasible results can be compared numerically with the paper-reported objective values. The cantilever problem must remain separately qualified because the printed objective and Table 20 are internally inconsistent.

F5 intentionally makes no claim that one optimizer is universally superior. Feasibility rate, feasible-objective quality, formulation differences, and stochastic variation are kept as separate pieces of evidence.
