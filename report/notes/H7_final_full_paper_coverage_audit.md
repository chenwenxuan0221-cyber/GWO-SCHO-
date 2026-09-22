# H7 — Final Full-Paper Coverage Audit

## 1. Purpose

This document is the final closeout audit for the GWO + SCHO reproduction project.

It supersedes the pre-extension coverage state recorded in:

- `report/notes/H0_full_paper_coverage_audit.md`
- `report/tables/H0_full_paper_coverage_matrix.csv`

It does **not** overwrite the scientific evidence from earlier stages. Instead, it
updates the coverage status after H1-H6 while preserving each stage's declared
exactness boundary.

The project must not be described as a pixel-exact, MATLAB-bitwise, or
numerically exact reproduction of every experiment in both papers.

The correct overall description is:

> **A broad source-/structure-faithful reproduction with explicit controlled
> equivalents where primary experimental details were unavailable, partial
> numerical agreement in several paper comparisons, and one intentionally
> excluded optical-engineering application.**

---

## 2. Global reproduction rules

The following rules remain frozen:

- `algorithms/gwo.py` must not be modified to improve agreement.
- `algorithms/scho.py` must not be modified to improve agreement.
- MATLAB and NumPy RNG streams are not claimed to be bitwise equivalent.
- Source quirks are preserved rather than silently repaired.
- Project-controlled adapters and protocols are explicitly labelled.
- No parameter tuning is performed merely to force paper agreement.
- Historical evidence is versioned/frozen rather than overwritten.

Important vocabulary used by this project:

- `source-faithful`
- `source-structured`
- `paper-equation-faithful`
- `paper-structure`
- `controlled-equivalent`
- `controlled-interpretation`
- `project-controlled adapter`

---

## 3. Final coverage matrix

| Paper | Section | Experiment | Final status | Final audit |
|---|---|---|---|---|
| GWO | 4 | Results and discussion / benchmark coverage | **COMPLETE_PAPER_STRUCTURE_COVERAGE** | Classic landscapes, SIS2005 composites, and Section 4 behavior figures are covered at declared paper-style/source-faithful/controlled-equivalent tiers. This is not a claim of exact reproduction of every published comparison number. |
| GWO | 4.1 | Exploitation analysis | **CORE_DONE** | GWO F1-F7 30-run statistics and paper-style landscapes are reproduced. Historical PSO/GSA/DE/FEP/CMA-ES comparison algorithms were not all independently rerun. |
| GWO | 4.2 | Exploration analysis | **CORE_DONE** | GWO F8-F23 statistics and paper-style landscapes are reproduced. Historical comparison algorithms were not all independently rerun. |
| GWO | 4.3 | Local minima avoidance / SIS2005 F24-F29 | **COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT** | All six CF1-CF6 functions were recovered/ported and run for 30 trials with frozen GWO. F28 is the strongest numerical match; F24/F26/F27/F29 remain materially different. F26 preserves the paper-table vs source-code Griewank/Rastrigin discrepancy. |
| GWO | 4.4 | Convergence behavior analysis / Fig.11 | **COMPLETE_CONTROLLED_EQUIVALENT** | Paper-structure elements were reproduced for the eight specified functions with six agents and 100 iterations. Exact original shift vectors, seed, and history-logging semantics were unavailable; project conventions are explicit. |
| GWO | 5 | Three classical engineering problems | **PARTIAL__COMMON_PROTOCOL_REPRODUCTION** | Spring, welded beam, and pressure vessel are included in the common Stage-F engineering framework, but the project death-penalty protocol is not claimed to be the original GWO Section-5 constraint protocol. |
| GWO | 6 | Optical buffer design / BSPCW | **INTENTIONALLY_OUT_OF_SCOPE** | No BSPCW/NDBP/photonic-band evaluator is implemented. This section was explicitly excluded from the project scope and is not a remaining implementation task. |
| SCHO | 3.1 | Classical benchmark program | **COMPLETE_WITH_EXACTNESS_BOUNDARIES** | F1-F23 core reproduction, ablation/qualitative work, 9-algorithm classical comparison, and full high-dimensional 9-algorithm scalability comparison are all covered across H4-H6. |
| SCHO | 3.1.1 | Ablation / subordinate-model analysis | **COMPLETE_CONTROLLED_REPRODUCTION__STRONG_RANK_LEVEL_AGREEMENT** | Table 5 structural ablation is complete. Final-rank agreement is 5/6; five variants remain paper-described controlled structural interpretations because author variant source files were not recovered. |
| SCHO | 3.1.2 | Qualitative analysis | **COMPLETE_WITH_CONTROLLED_INTERPRETATION_BOUNDARY** | Fig.8 is controlled-equivalent. Fig.7 controlled reproduction is complete with partial bar-level agreement; the eleven variants are controlled interpretations rather than recovered author-source implementations. |
| SCHO | 3.1.3 | Comparison with 8 other algorithms | **COMPLETE__PARTIAL_NUMERICAL_AGREEMENT** | Full 9-algorithm F1-F23 experiment is complete: 6210 raw rows, Table 7, Table 8, and controlled-equivalent Fig.9. SCHO final rank 1 is preserved; Table-8 W/L/T agreement is partial; no tuning. |
| SCHO | 3.1.4 | Scalability D=100 / D=500 | **COMPLETE__PARTIAL_NUMERICAL_AGREEMENT** | Full 9-algorithm experiment is complete: 7020 raw rows, Tables 9-12, Friedman, and Wilcoxon. SCHO rank 1 and RSA rank 2 are preserved at both dimensions; AOA is the dominant mismatch; no tuning. |
| SCHO | 3.2 | CEC2014 D=10 | **CORE_DONE__PARTIAL_NUMERICAL_AGREEMENT__FULL_9_ALG_COMPARISON_NOT_RERUN** | GWO + SCHO F1-F30 x30 are complete. GWO paper-scale agreement is strong; SCHO has several material mismatches. The paper's full 9-algorithm Friedman/Wilcoxon comparison was not independently rerun. |
| SCHO | 3.3 | Six engineering design problems | **CORE_DONE__PROJECT_CONTROLLED_PROTOCOL** | All six problems are implemented and validated; 360/360 Stage-F runs completed. The project uses an explicit death penalty of `1e30`, reports feasibility separately, and preserves source anomalies such as the cantilever scale inconsistency. Other published comparison algorithms were not fully rerun. |

---

## 4. GWO final coverage interpretation

### 4.1 Section 4

H1-H2 changed the old H0 status substantially.

Section 4 is now frozen as:

`GWO_SECTION4_PAPER_STRUCTURE_COVERAGE_COMPLETE`

with the following exactness boundaries:

| Artifact | Final tier |
|---|---|
| Fig.7 | `COMPLETE_PAPER_STYLE` |
| Fig.8 | `COMPLETE_PAPER_STYLE` |
| Fig.9 | `COMPLETE_PAPER_STYLE` |
| Fig.10 | `COMPLETE_CONTROLLED_EQUIVALENT` |
| F24-F29 / Table 8 experiment | `COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT` |
| Fig.11 | `COMPLETE_CONTROLLED_EQUIVALENT` |

The project must not relabel this as pixel-exact or numerically exact.

### 4.2 SIS2005 F24-F29

H1 completed:

- D=10
- N=30
- MaxIter=500
- 30 runs/function
- 180 total GWO runs
- source-faithful recovered SIS2005 assets

Final H1 interpretation:

`COMPLETE AS A SOURCE-FAITHFUL REPRODUCTION ATTEMPT; PARTIAL NUMERICAL AGREEMENT`

The F26/CF3 discrepancy remains an explicit source anomaly:

- GWO Table 4 prints ten Griewank components.
- recovered `SIS_novel_func.m` uses ten Rastrigin components.
- project primary = source-faithful Rastrigin
- Griewank version = diagnostic only

### 4.3 Optical application

GWO Section 6 is intentionally excluded.

Final status:

`INTENTIONALLY_OUT_OF_SCOPE`

This is a deliberate project-scope decision, not an unfinished TODO.

---

## 5. SCHO final coverage interpretation

### 5.1 Section 3.1.1-3.1.2

H4 completed the planned ablation and qualitative scope.

Table 5:

`SCHO_TABLE5_ABLATION_COMPLETE__STRONG_RANK_LEVEL_AGREEMENT__ONE_TIE_DIFFERENCE`

Key result:

- final-rank matches = 5/6

Fig.7:

`SCHO_FIG7_CONTROLLED_COMPLETE__PARTIAL_BAR_LEVEL_AGREEMENT__NO_TUNING`

Fig.8:

`COMPLETE_CONTROLLED_EQUIVALENT`

The absence of author-source files for the ablation/variant implementations is
preserved as an exactness boundary.

### 5.2 Section 3.1.3 classical 9-algorithm comparison

Final status:

`H5_COMPLETE__SECTION_3_1_3_CLASSICAL_9_ALGORITHM_COMPARISON`

Formal matrix:

`9 * 23 * 30 = 6210`

Algorithms:

`SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO`

Important:

`SHO = Sea-Horse Optimizer`

Main numerical interpretation:

- SCHO Table-7 final rank 1 preserved
- partial rank-level agreement overall
- Table-8 W/L/T agreement partial
- no tuning
- Fig.9 complete controlled-equivalent

### 5.3 Section 3.1.4 full scalability comparison

Final status:

`H6_COMPLETE__SECTION_3_1_4_FULL_9_ALGORITHM_SCALABILITY_COMPARISON`

Formal matrix:

`9 * 13 * 2 * 30 = 7020`

Protocol:

`H6_SCALABILITY_V1`

Key ranking result:

- D=100: SCHO rank 1, RSA rank 2, SSA/ALO/SCA ranks 7/8/9 preserved
- D=500: same preserved positions
- AOA is reproduced substantially stronger than in the paper

Wilcoxon aggregate agreement:

- Table 11 / D=100: exact W|L|T matches = 2/8
- Table 12 / D=500: exact W|L|T matches = 2/8
- SCA exact at both dimensions
- no tuning

Recommended interpretation:

`COMPLETE_PROTOCOL_REPRODUCTION__PARTIAL_NUMERICAL_AGREEMENT__NO_TUNING`

### 5.4 CEC2014

SCHO Section 3.2 remains a core reproduction rather than a full paper-comparison rerun.

Completed:

- F1-F30
- D=10
- N=30
- MaxIter=500
- 30 runs
- GWO + SCHO

Paper-scale evidence:

- GWO within +/-25% on 22/30 mean-error comparisons
- GWO within factor 2 on 30/30
- SCHO within +/-25% on 14/30
- SCHO within factor 2 on 26/30
- 9 paper/reproduction GWO-vs-SCHO pairwise flips

The full 9-algorithm CEC2014 comparison is not rerun.

### 5.5 Engineering design

SCHO Section 3.3 core engineering reproduction is complete under an explicit
project-controlled protocol:

- N=30
- MaxIter=500
- 30 runs
- seeds 1000..1029
- death penalty = `1e30`
- feasibility tolerance = `1e-8`

Stage F completed:

- 360/360 optimization runs
- 288 feasible best designs
- 72 `NO_FEASIBLE_FOUND`
- 0 structural failures

Feasibility rate and feasible-only objective quality must remain separate metrics.

---

## 6. What remains intentionally partial

After H6, there are no planned H-stage experiments remaining.

However, several paper sections still carry explicit partial/comparison boundaries:

1. GWO 4.1 / 4.2:
   original historical comparator algorithms were not all rerun.
2. GWO 5:
   common Stage-F constraint handling is not claimed to reproduce the original
   GWO Section-5 penalty protocol exactly.
3. SCHO 3.2:
   the full 9-algorithm CEC2014 Friedman/Wilcoxon comparison was not rerun.
4. SCHO 3.3:
   all six engineering problems are reproduced under the project protocol, but
   the paper's full external-comparator suite was not rerun.
5. GWO 6:
   intentionally out of scope.

These are not hidden gaps. They are final declared scope/exactness boundaries.

---

## 7. Final project status

Recommended project-level status:

`GWO_SCHO_REPRODUCTION_CLOSEOUT__H0_H6_COMPLETE__DECLARED_SCOPE_BOUNDARIES_PRESERVED`

Recommended reporting language:

> The project completed its planned H0-H6 extension, including source-faithful
> GWO SIS2005 composites, GWO Section-4 paper-structure figures, SCHO ablation
> and qualitative experiments, the full 9-algorithm classical comparison, and
> the full 9-algorithm D=100/D=500 scalability comparison. Several historical
> comparison suites remain only partially rerun, and the GWO optical-buffer
> application is intentionally excluded. Numerical mismatches are preserved as
> reproduction evidence rather than tuned away.

Do **not** use:

> "Both papers were reproduced 100% exactly."

Do **not** use:

> "All published experiments and comparison algorithms were rerun."

---

## 8. Closeout actions

Scientific experimentation is complete for the declared project scope.

Remaining closeout work:

- freeze this final coverage audit
- update the handoff document
- create the final v2 reproduction report
- run a repository/evidence consistency check
- create the final closeout commit/tag
