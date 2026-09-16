# Stage E Final Report — CEC2014 Reproduction and Validation

## 1. Stage objective

Stage E reproduces the CEC2014 section of the SCHO paper under a frozen Python protocol and checks whether the frozen GWO and source-faithful SCHO implementations can reproduce the paper's reported behavior.

The purpose of Stage E is not to tune either optimizer. The goal is to separate four questions:

1. Is the CEC2014 evaluator configured correctly?
2. Can the frozen GWO and SCHO implementations run across all 30 CEC2014 functions?
3. Do the 30-run statistics reproduce the paper's Table 14 at the same scale?
4. When they do not, what kind of mismatch is present?

## 2. Frozen protocol

- Benchmark suite: CEC2014 single-objective real-parameter optimization
- Functions: F1–F30
- Dimension: D = 10
- Search range: [-100, 100]^10
- Known optimum: f_opt(F_i) = 100*i
- Population size: N = 30
- Maximum iterations: 500
- Independent runs: 30
- Seeds: 1000–1029
- Optimizers: frozen GWO and frozen source-faithful SCHO
- Paper comparison metrics: Best, Average/Mean, STD
- Primary STD for paper comparison: sample STD, ddof=1
- Auxiliary diagnostic metric: error = fitness - f_opt

Important scope note: this reproduces the paper's experiment protocol, not the original CEC2014 competition budget.

## 3. Stage-by-stage validation

### E0 — Protocol audit

Completed.

The paper-oriented CEC2014 experiment uses F1–F30 at D=10 with 30 independent runs. The reproduction uses the official family structure:

- F1–F3: unimodal
- F4–F16: simple multimodal
- F17–F22: hybrid
- F23–F30: composition

### E1 — Evaluator audit

Completed: PASS.

Backend: `minionpy==1.6.1`, using `CEC2014Functions`.

Checks passed:

- F1–F30 instantiate at D=10.
- Project bounds are [-100,100]^10.
- f_opt(F_i)=100*i.
- Probe evaluations are finite and deterministic.
- Batch and one-point backend evaluations agree.
- The project wrapper agrees with the backend.

No optimizer was run during E1.

### E2 — Representative integration

Completed: PASS.

Representative functions: F1, F8, F17, F23.

Each was run once with GWO and once with SCHO at D=10, N=30, MaxIter=500, seed=1000.

All 8 runs passed the structural checks.

### E3 — F1–F30 single-run coverage

Completed: PASS.

- 30 functions × 2 algorithms = 60 runs
- PASS: 60/60
- FAIL: 0
- Missing: 0

### E4 — Full 30-run experiment

Completed.

- 30 functions
- 2 algorithms
- 30 runs
- 1800 optimizer runs total
- PASS: 1800/1800
- Summary rows: 60/60

Primary outputs:

- `results/raw/cec2014_e4_runs.csv`
- `results/processed/cec2014_e4_summary.csv`

No algorithm code was modified.

### E5 — Comparison with paper Table 14

Completed.

Primary diagnostic:

`MeanError = Mean - f_opt`

`MeanErrorRatio = Reproduced MeanError / Paper MeanError`

This is more informative than comparing raw CEC fitness directly because every function has a different additive optimum offset.

#### GWO cross-check

- 30/30 functions are within a factor of 2 of the paper's mean excess-error.
- 22/30 are within ±25%.

This strongly supports evaluator/protocol compatibility.

#### SCHO comparison

- 14/30 functions are within ±25%.
- 26/30 functions are within a factor of 2.
- F2, F7, F15 and F21 fall outside the factor-2 band.

F21 is the largest discrepancy.

#### Relative GWO-vs-SCHO outcome

Using only GWO and SCHO Mean/Average:

- Paper: SCHO lower Mean on 17/30, GWO on 13/30.
- Reproduction: SCHO lower Mean on 8/30, GWO on 22/30.
- Nine functions flip from paper-SCHO to reproduced-GWO:
  F1, F3, F4, F10, F17, F18, F20, F21, F26.

Therefore the current experiment reproduces the CEC/GWO scale well, but does not reproduce the paper's overall SCHO-vs-GWO advantage across CEC2014.

### E6 — Run-level anomaly diagnosis

Completed.

Focus: F2, F7, F15, F21, F23, F27, with F28 as a control.

No optimization was rerun.

#### F21 — heavy-tail/outlier instability

- minimum ≈ 2.4872e3
- median ≈ 1.2379e4
- mean ≈ 5.7306e5
- maximum ≈ 1.6290e7
- IQR outliers: 4

The large separation between median and mean shows that a small number of very poor runs inflate the mean and STD.

#### F15 — long-tail behavior

- minimum ≈ 1.5031e3
- median ≈ 1.5051e3
- mean ≈ 1.5373e3
- maximum ≈ 1.9766e3
- IQR outliers: 6

#### F2 and F7

F2 is broadly shifted upward relative to the paper, while F7 is mostly concentrated with a poorer upper tail.

#### F23 — deterministic plateau mismatch

All 30 SCHO runs ended at exactly 2500:

- plateau count: 30/30
- STD = 0

The paper reports nonzero variation and a better Best value.

#### F27 — deterministic plateau mismatch

All 30 SCHO runs ended at exactly 2900:

- plateau count: 30/30
- STD = 0

Again, this differs from the paper's nonzero variation.

#### F28 — matching deterministic plateau

All 30 SCHO runs ended at exactly 3000:

- plateau count: 30/30
- STD = 0

This agrees with the paper and is an important control.

E6 also generated a GWO-vs-SCHO two-sided Mann–Whitney U / Wilcoxon rank-sum diagnostic table. It describes the current Python reproduction only and is not equivalent to the paper's complete Table 15.

## 4. What Stage E supports

### Supported conclusion 1 — evaluator/protocol compatibility

Evidence:

- E1 evaluator checks passed.
- E2/E3 integration passed.
- E4 completed all 1800 runs.
- GWO reproduces the paper's CEC2014 mean-error scale consistently.

### Supported conclusion 2 — SCHO is only partially reproduced on CEC2014

Most functions remain on a comparable scale to the paper, but the full stochastic behavior is not reproduced.

Mismatch modes include:

- F21: heavy-tail/outlier instability
- F15: long-tail instability
- F23/F27: deterministic plateau mismatch
- F28: deterministic plateau that agrees with the paper

### Supported conclusion 3 — do not tune the frozen implementation

The source-faithful SCHO implementation should not be changed merely to force Table 14 agreement.

Possible contributors include:

- NumPy versus MATLAB random-number trajectories
- source-level SCHO behaviors already preserved from the official implementation
- sensitivity of some CEC2014 functions to stochastic search paths

The current results do not isolate these causes uniquely.

## 5. What Stage E does NOT establish

Do not claim:

- bitwise MATLAB reproduction
- exact reproduction of every SCHO Table 14 statistic
- exact reproduction of the paper's full Friedman ranking
- exact reproduction of Table 15 against all paper algorithms
- proof that SCHO is universally better or worse than GWO
- proof that one implementation detail alone explains every mismatch

## 6. Frozen Stage E artifacts

### Benchmark / experiment code

- `benchmarks/cec2014.py`
- `experiments/test_cec2014_e1.py`
- `experiments/test_cec2014_e2.py`
- `experiments/test_cec2014_e3_all30.py`
- `experiments/benchmark_cec2014_e4.py`
- `experiments/diagnose_cec2014_e6.py`

### Raw / processed results

- `results/raw/cec2014_e3_single_run.csv`
- `results/raw/cec2014_e4_runs.csv`
- `results/processed/cec2014_e4_summary.csv`
- `results/processed/E5_CEC2014_vs_Paper_Table14.csv`
- `results/processed/E6_scho_anomaly_stats.csv`
- `results/processed/E6_scho_selected_runs.csv`
- `results/processed/E6_gwo_vs_scho_rank_sum.csv`

### Figures

- `report/figures/E6_scho_error_by_run.png`
- `report/figures/E6_scho_error_boxplot.png`

### Reports

- `report/tables/E5_CEC2014_vs_Paper_Table14.xlsx`
- `report/notes/E5_CEC2014_vs_Paper_report.md`
- `report/notes/E6_scho_anomaly_report.md`
- `report/notes/E7_StageE_final_report.md`

## 7. Final Stage E status

E0 — COMPLETE  
E1 — COMPLETE  
E2 — COMPLETE  
E3 — COMPLETE  
E4 — COMPLETE  
E5 — COMPLETE  
E6 — COMPLETE  
E7 — READY TO FREEZE

After this report is placed in the repository and Git status is checked, Stage E can be committed/tagged and the project can move to Stage F engineering design problems.
