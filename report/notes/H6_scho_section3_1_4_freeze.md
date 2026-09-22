# H6 — SCHO Section 3.1.4 Full 9-Algorithm Scalability Comparison Freeze

## Status

`H6 COMPLETE`

Section covered:

- Table 9: D=100 scalability comparison
- Table 10: D=500 scalability comparison
- Table 11: D=100 Wilcoxon rank-sum significance analysis
- Table 12: D=500 Wilcoxon rank-sum significance analysis
- Friedman ranking analysis for D=100 and D=500

Algorithms:

`SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO`

Important:

`SHO = Sea-Horse Optimizer`, not Spotted Hyena Optimizer.

---

## H6 protocol

Benchmarks:

- F1-F13
- D=100 and D=500
- Population N=30
- MaxIter=500
- 30 independent runs
- optimizer seeds = 1000..1029

Formal objective seed protocol:

\[
s_{\mathrm{obj}} = 7\,000\,000 + 10\,000D + 100f + run
\]

where `f` is the function number.

The objective RNG is active for stochastic F7.
For deterministic functions, the objective seed is recorded for protocol
bookkeeping but has no numerical effect.

Protocol ID:

`H6_SCALABILITY_V1`

Full formal matrix:

\[
9 \times 13 \times 2 \times 30 = 7020
\]

Historical reuse:

- SCHO: 780 rows reused from H3c under the same frozen scalability protocol
- all other 8 algorithms: 6240 rows newly computed

Final raw dataset:

`results/raw/scho_scalability_h6b_runs.csv`

Checkpoint:

`results/raw/scho_scalability_h6b_checkpoint.jsonl`

H6b audit:

- final rows = 7020/7020
- each algorithm = 780/780
- reused SCHO rows = 780
- new comparator rows = 6240
- F7 rows = 540/540
- audit result = PASS

---

## Comparator exactness boundaries

| Algorithm | Exactness boundary |
|---|---|
| SCHO | frozen source-faithful |
| GWO | frozen project baseline |
| SCA | source-structured + NumPy RNG |
| SSA | source-structured + NumPy RNG |
| GJO | source-structured + NumPy RNG |
| AOA | source-structured + SCHO Table 6 `mu=0.5` override |
| RSA | source-structured |
| ALO | source-structured literal reciprocal roulette |
| SHO | paper-equation faithful; historical author source not line-by-line verified |

No MATLAB/NumPy bitwise RNG equivalence is claimed.

No source quirk is silently repaired.

No parameter tuning is performed to force agreement with the paper.

Frozen core files remain untouched:

- `algorithms/gwo.py`
- `algorithms/scho.py`

---

## H6a — Full-comparison protocol and smoke validation

Frozen protocol:

`H6_SCALABILITY_V1`

Formal matrix:

- algorithms = 9
- functions = 13
- dimensions = 2
- runs = 30
- total = 7020

Historical reuse rule:

- SCHO H3c rows are reused only because the H3c seed/protocol matches H6 exactly
- SCHO is not rerun inside H6b
- comparator runs are newly executed

Smoke validation:

`PASS`

Representative same-seed reruns confirmed deterministic behavior under the
project-controlled NumPy protocol.

---

## H6b — Formal 7020-row raw dataset

Result:

`COMPLETE (7020/7020)`

Breakdown:

- SCHO reused = 780
- comparator new runs = 6240

Final audit:

`PASS`

No missing algorithm/function/dimension/run keys were detected.

All stored final `BestScore` values are finite.

A high-dimensional numerical warning was observed for ALO on F2 at D=500:
intermediate products can overflow during objective evaluation. The final stored
best scores remained finite and were preserved without tuning or clipping.

---

## H6c — Tables 9 and 10 + Friedman ranking

Statistics:

- Best = minimum over 30 runs
- Average = arithmetic mean over 30 runs
- STD = sample standard deviation, `ddof=1`
- per-function rank = Average ascending
- ties = average ranks
- MeanRank = average per-function rank across F1-F13
- FinalRank = ascending rank of MeanRank

A numerically stable scaled implementation is used for sample STD to avoid
overflow in the variance computation when finite values are extremely large.
This changes only the numerical evaluation of the statistic, not the raw data.

### D = 100 — Table 9

| Algorithm | Reproduced MeanRank / FinalRank | Paper MeanRank / FinalRank |
|---|---:|---:|
| SCHO | 2.84615 / 1 | 1.85 / 1 |
| RSA | 3.38462 / 2 | 2.85 / 2 |
| AOA | 3.69231 / 3 | 4.77 / 6 |
| SHO | 3.92308 / 4 | 3.31 / 3 |
| GJO | 4.00000 / 5 | 4.00 / 4 |
| GWO | 4.23077 / 6 | 4.15 / 5 |
| SSA | 6.61538 / 7 | 6.54 / 7 |
| ALO | 7.61538 / 8 | 7.69 / 8 |
| SCA | 8.69231 / 9 | 8.69 / 9 |

Exact final-rank matches:

`5/9`

Preserved paper positions:

- SCHO = rank 1
- RSA = rank 2
- SSA = rank 7
- ALO = rank 8
- SCA = rank 9

Largest structural mismatch:

- AOA is reproduced substantially stronger than in the paper, moving from
  paper rank 6 to reproduced rank 3.

Friedman test:

- statistic = 62.553191
- p = 1.4673495e-10
- reject H0 at alpha=0.05

### D = 500 — Table 10

| Algorithm | Reproduced MeanRank / FinalRank | Paper MeanRank / FinalRank |
|---|---:|---:|
| SCHO | 3.00000 / 1 | 2.00 / 1 |
| RSA | 3.23077 / 2 | 2.54 / 2 |
| AOA | 3.38462 / 3 | 5.31 / 6 |
| SHO | 3.61538 / 4 | 3.38 / 3 |
| GJO | 4.30769 / 5 | 4.00 / 4 |
| GWO | 4.76923 / 6 | 4.62 / 5 |
| SSA | 6.69231 / 7 | 6.69 / 7 |
| ALO | 7.46154 / 8 | 7.54 / 8 |
| SCA | 8.53846 / 9 | 8.23 / 9 |

Exact final-rank matches:

`5/9`

Preserved paper positions:

- SCHO = rank 1
- RSA = rank 2
- SSA = rank 7
- ALO = rank 8
- SCA = rank 9

Largest structural mismatch:

- AOA is again reproduced substantially stronger than in the paper, moving
  from paper rank 6 to reproduced rank 3.

Friedman test:

- statistic = 59.674541
- p = 5.3989853e-10
- reject H0 at alpha=0.05

H6c interpretation:

- SCHO retains paper final rank 1 at both D=100 and D=500
- RSA retains paper final rank 2 at both dimensions
- the lower end of the ranking is also stable: SSA/ALO/SCA retain ranks 7/8/9
- the main rank-order disagreement is concentrated in AOA/SHO/GJO/GWO
- AOA is the dominant high-dimensional comparator mismatch
- no tuning is performed to repair the discrepancy

Freeze label:

`SCHO_TABLES9_10_COMPLETE__PARTIAL_RANK_LEVEL_AGREEMENT__SCHO_RANK1_PRESERVED_BOTH_DIMS__AOA_MAJOR_MISMATCH__FRIEDMAN_SIGNIFICANT__NO_TUNING`

Outputs:

- `results/processed/scho_scalability_h6c_summary.csv`
- `report/tables/H6_table9_D100_reproduction.csv`
- `report/tables/H6_table10_D500_reproduction.csv`
- `report/tables/H6_friedman_ranking.csv`
- `report/H6_tables9_10_comparison.md`

---

## H6d — Tables 11 and 12 Wilcoxon rank-sum reproduction

Test:

- SCHO vs each comparator
- F1-F13
- 30-run distributions
- two-sided Mann-Whitney U / Wilcoxon rank-sum
- alpha = 0.05
- SciPy asymptotic method with continuity correction

Statistical implementation boundary:

`project-controlled statistical implementation`

No bitwise MATLAB `ranksum` equivalence is claimed.

Symbol convention:

- `+` = SCHO significantly better
- `-` = SCHO significantly worse
- `~` = no significant difference

### D = 100 — Table 11 aggregate W|L|T

| Comparator | Reproduced | Paper | Exact |
|---|---:|---:|:---:|
| GWO | 8|5|0 | 10|3|0 | NO |
| ALO | 12|1|0 | 13|0|0 | NO |
| SCA | 13|0|0 | 13|0|0 | YES |
| SSA | 12|1|0 | 12|1|0 | YES |
| AOA | 5|2|6 | 9|1|3 | NO |
| RSA | 4|3|6 | 5|2|6 | NO |
| SHO | 7|0|6 | 10|1|2 | NO |
| GJO | 6|3|4 | 9|3|1 | NO |

Exact aggregate W|L|T matches:

`2/8`

### D = 500 — Table 12 aggregate W|L|T

| Comparator | Reproduced | Paper | Exact |
|---|---:|---:|:---:|
| GWO | 9|4|0 | 10|3|0 | NO |
| ALO | 12|1|0 | 12|1|0 | YES |
| SCA | 13|0|0 | 13|0|0 | YES |
| SSA | 12|1|0 | 13|0|0 | NO |
| AOA | 5|2|6 | 11|1|1 | NO |
| RSA | 4|3|6 | 5|2|6 | NO |
| SHO | 7|3|3 | 9|2|2 | NO |
| GJO | 8|4|1 | 9|4|0 | NO |

Exact aggregate W|L|T matches:

`2/8`

H6d interpretation:

- SCA is the strongest agreement: exact W|L|T at both dimensions
- SSA is exact at D=100
- ALO is exact at D=500
- AOA shows the largest persistent significance-pattern discrepancy
- RSA/SHO/GJO also show partial rather than exact agreement
- the direction of the H6d discrepancy is consistent with H6c: AOA is
  substantially stronger in the project reproduction than in the paper
- no optimizer or statistical threshold is tuned to force agreement

Freeze label:

`SCHO_TABLES11_12_COMPLETE__PARTIAL_WLT_AGREEMENT__SCA_EXACT_BOTH_DIMS__AOA_MAJOR_MISMATCH__NO_TUNING`

Outputs:

- `report/tables/H6_table11_D100_wilcoxon.csv`
- `report/tables/H6_table12_D500_wilcoxon.csv`
- `report/tables/H6_tables11_12_wlt_summary.csv`
- `report/H6_tables11_12_comparison.md`

---

## Overall H6 freeze

Final status:

`H6_COMPLETE__SECTION_3_1_4_FULL_9_ALGORITHM_SCALABILITY_COMPARISON`

Coverage:

- H6 protocol audit: complete
- formal 7020-row dataset: complete
- Tables 9/10: complete
- Friedman ranking: complete
- Tables 11/12: complete
- final paper comparison: complete

Numerical interpretation:

- SCHO retains paper final rank 1 at both D=100 and D=500
- RSA retains paper final rank 2 at both dimensions
- SSA/ALO/SCA also preserve their paper final ranks 7/8/9
- AOA is the dominant ranking/significance mismatch and is substantially
  stronger in the project reproduction
- SCA Wilcoxon W|L|T matches the paper exactly at both dimensions
- overall Section 3.1.4 agreement is partial rather than exact
- the discrepancy is preserved as reproduction evidence; no tuning is used

Recommended overall H6 interpretation:

`COMPLETE_PROTOCOL_REPRODUCTION__PARTIAL_NUMERICAL_AGREEMENT__NO_TUNING`

---

## Scope boundary after H6

The GWO optical/photonic engineering application (Section 6 optical-buffer /
BSPCW application) is intentionally out of scope for this project and is not
planned as a remaining implementation task.

After H6, the remaining work is therefore project closeout:

- update the full-paper coverage matrix
- mark SCHO Section 3.1.4 as complete
- retain the optical application as intentionally not reproduced
- run final full-project audit
- prepare final reproduction summary / handoff
- freeze the project state with final Git commit/tag
