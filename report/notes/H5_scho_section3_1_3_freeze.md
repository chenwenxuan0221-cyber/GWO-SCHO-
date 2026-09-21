# H5 — SCHO Section 3.1.3 Classical 9-Algorithm Comparison Freeze

## Status

`H5 COMPLETE`

Section covered:

- Table 7: 9-algorithm classical benchmark comparison
- Table 8: SCHO vs comparators Wilcoxon rank-sum comparison
- Fig. 9: 9-algorithm convergence curves on F1–F23

Algorithms:

`SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO`

Important:

`SHO = Sea-Horse Optimizer`, not Spotted Hyena Optimizer.

---

## H5 protocol

Classical benchmarks:

- F1–F13: D=30
- F14–F23: native dimensions
- Population N=30
- MaxIter=500
- 30 independent runs
- optimizer seeds = 1000..1029

Formal objective seed protocol:

\[
s_{\mathrm{obj}} = 5\,024\,000 + 100 f + run
\]

where `f` is the function number.

This objective RNG is active for stochastic F7.
For deterministic functions, the objective seed is recorded for protocol
bookkeeping but has no numerical effect.

Protocol ID:

`H5_CLASSICAL_V1`

---

## H5 comparator exactness boundaries

| Algorithm | Exactness boundary |
|---|---|
| SCHO | frozen source-faithful |
| GWO | frozen project baseline |
| SCA | source-structured + NumPy RNG |
| SSA | source-structured + NumPy RNG |
| GJO | source-structured + NumPy RNG |
| AOA | source-structured + SCHO Table 6 `mu=0.5` override |
| RSA | source-structured; F17 uses project-controlled coordinate-span adapter |
| ALO | source-structured literal reciprocal roulette |
| SHO | paper-equation faithful; historical author `SHO.m` body not line-by-line verified |

No MATLAB/NumPy bitwise RNG equivalence is claimed.

No source quirk is silently repaired.

No parameter tuning is performed to force agreement with the paper.

Frozen core files remain untouched:

- `algorithms/gwo.py`
- `algorithms/scho.py`

---

## H5c7 — Sea-Horse Optimizer

Status:

`PASS`

Structural audit covered:

- movement
- predation
- breeding
- survivor selection
- odd-N guard

Verified constants:

- `u=v=l=0.05`
- Levy `s=0.01`
- Levy `lambda=1.5`
- predation cutoff `0.1`

Freeze label:

`SHO_PAPER_EQUATION_FAITHFUL__HISTORICAL_SOURCE_NOT_LINE_BY_LINE_VERIFIED__NUMPY_RNG`

---

## H5d — Unified 9-algorithm protocol smoke

Representative functions:

- F2: scalar bounds
- F7: stochastic objective
- F17: vector bounds
- F21: negative optimum

Protocol:

- N=6
- MaxIter=40
- optimizer seed=1000

Result:

`PASS (36/36 algorithm-function smoke cases)`

Verified:

- common callable interface
- `(score, position, curve)` return structure
- finite results
- correct dimensions
- deterministic same-seed reruns
- vector-bound compatibility
- stochastic objective reproducibility
- negative-fitness compatibility

---

## H5e — Formal 9-algorithm raw dataset

Final dataset:

\[
9 \times 23 \times 30 = 6210
\]

Result:

`COMPLETE (6210/6210)`

Historical reuse:

- SCHO F1–F6 and F8–F23: 660 deterministic rows reused
- SCHO F7: rerun under H5 formal objective-seed protocol
- GWO: all 690 runs recomputed because no complete historical per-run raw dataset existed
- 7 comparators: all 4830 runs newly computed

New H5 runs:

\[
30 + 690 + 4830 = 5550
\]

Final raw dataset:

`results/raw/scho_classical_h5_runs.csv`

Checkpoint:

`results/raw/scho_classical_h5_checkpoint.jsonl`

---

## H5f — Table 7 reproduction

Statistics:

- Best = minimum
- Mean = arithmetic mean
- STD = sample standard deviation, `ddof=1`
- per-function rank = Mean ascending
- ties = average ranks
- mean rank = average rank across 23 functions

Reproduced mean rank / final rank:

| Algorithm | Reproduced | Paper |
|---|---:|---:|
| SCHO | 2.86957 / 1 | 2.48 / 1 |
| GWO | 4.08696 / 2 | 3.78 / 3 |
| GJO | 4.21739 / 3 | 3.74 / 2 |
| RSA | 4.60870 / 4 | 4.57 / 5 |
| SSA | 4.65217 / 5 | 4.83 / 6 |
| ALO | 5.47826 / 6 | 5.43 / 7 |
| AOA | 5.60870 / 7 | 5.83 / 8 |
| SHO | 6.13043 / 8 | 4.00 / 4 |
| SCA | 7.34783 / 9 | 7.39 / 9 |

Interpretation:

- SCHO final rank 1 preserved
- SCA final rank 9 preserved
- GWO/GJO swap positions 2/3
- RSA/SSA/ALO/AOA differ mildly
- SHO is the dominant mismatch

Freeze label:

`SCHO_TABLE7_COMPLETE__PARTIAL_RANK_LEVEL_AGREEMENT__SCHO_FINAL_RANK1_PRESERVED__SHO_MAJOR_MISMATCH__NO_TUNING`

Outputs:

- `results/processed/scho_classical_h5_summary.csv`
- `report/tables/H5_table7_reproduction.csv`
- `report/H5_table7_comparison.md`

---

## H5g — Table 8 Wilcoxon rank-sum reproduction

Test:

- SCHO vs each comparator
- 23 functions
- 30-run distributions
- two-sided Mann–Whitney U / Wilcoxon rank-sum
- alpha = 0.05
- SciPy asymptotic method with continuity correction

Statistical implementation boundary:

`project-controlled statistical implementation`

No bitwise MATLAB `ranksum` equivalence is claimed.

Reproduced W|L|T vs paper:

| Comparator | Reproduced | Paper |
|---|---:|---:|
| GWO | 12|5|6 | 12|8|3 |
| ALO | 14|6|3 | 14|6|3 |
| SCA | 23|0|0 | 21|2|0 |
| SSA | 13|8|2 | 18|5|0 |
| AOA | 15|0|8 | 18|2|3 |
| RSA | 13|1|9 | 11|2|10 |
| SHO | 19|0|4 | 13|3|7 |
| GJO | 17|1|5 | 14|3|6 |

Interpretation:

- ALO W|L|T exactly reproduced
- GWO win count exactly reproduced
- RSA remains relatively close
- SSA/AOA/SHO/GJO show larger differences
- SHO mismatch is consistent with Table 7 SHO behavior

Freeze label:

`SCHO_TABLE8_COMPLETE__PARTIAL_WLT_AGREEMENT__ALO_EXACT__GWO_WIN_COUNT_EXACT__SHO_SSA_AOA_MAJOR_MISMATCH__NO_TUNING`

Outputs:

- `report/tables/H5_table8_wilcoxon.csv`
- `report/H5_table8_comparison.md`

---

## H5h — Fig. 9 convergence curves

The accessible paper text states that Fig. 9 shows convergence curves for all
9 algorithms on F1–F23, but does not expose whether the displayed curves are
30-run averages or a particular representative run.

Therefore H5h is frozen as:

`SCHO_FIG9_COMPLETE_CONTROLLED_EQUIVALENT`

Representative-run protocol:

- H5 formal run 1
- N=30
- MaxIter=500
- optimizer seed=1000
- objective seed = `5_024_000 + 100*f + 1`

Total convergence runs:

\[
9 \times 23 = 207
\]

Result:

`COMPLETE_CONTROLLED_EQUIVALENT`

Regression guard:

`All 207 final scores regress exactly to H5_CLASSICAL_V1 run-1 results.`

This verifies that convergence instrumentation did not alter optimizer behavior.

Raw curves:

- `results/raw/h5h_fig9_curves/`
- `results/raw/scho_h5h_fig9_curves.npz`

Figures:

- `report/figures/scho_fig9_part1_F1_F8.png`
- `report/figures/scho_fig9_part2_F9_F16.png`
- `report/figures/scho_fig9_part3_F17_F23.png`
- `report/figures/scho_fig9_all23.png`

Protocol note:

- `report/notes/H5h_fig9_protocol.md`

Plotting boundary:

- raw optimizer curves are stored unchanged
- preserved source quirks such as `curve[0]=0` are not repaired
- plotting may use `symlog` for wide dynamic ranges
- no pixel/numeric exactness to the paper is claimed

---

## Overall H5 freeze

Final status:

`H5_COMPLETE__SECTION_3_1_3_CLASSICAL_9_ALGORITHM_COMPARISON`

Coverage:

- comparator source/equation resolution: complete
- comparator structural audits: complete
- unified protocol audit: complete
- formal 6210-row dataset: complete
- Table 7: complete
- Table 8: complete
- Fig. 9: complete controlled-equivalent

Numerical interpretation:

- SCHO retains paper final rank 1 in Table 7
- several comparator rank relationships are close
- Table 8 contains one exact W|L|T match (ALO) and partial agreement elsewhere
- SHO is the largest persistent discrepancy across both Table 7 and Table 8
- no tuning is performed to repair the discrepancy

Most important unresolved full-paper item after H5:

- H3 full 9-algorithm scalability comparison remains incomplete
  (`9 * 13 * 2 * 30 = 7020` total runs; only SCHO-only 780 runs were previously completed)

