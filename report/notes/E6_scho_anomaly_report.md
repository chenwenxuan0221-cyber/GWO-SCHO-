# E6 — CEC2014 SCHO anomalous-distribution diagnostic

## 1. Purpose

E6 uses the existing E4 raw results only. No GWO/SCHO optimization was rerun and no algorithm parameter was changed.

Focus functions: F2, F7, F15, F21, F23, F27, F28.

F2, F7, F15 and F21 were selected because their reproduced SCHO mean excess-error fell outside the factor-2 band relative to Bai et al. Table 14. F23 and F27 were selected because the reproduced 30-run STD was exactly zero while the paper reported nonzero variation. F28 is a control case because both paper and reproduction show the 3000 plateau with STD=0.

## 2. Main run-level findings

### F21 — outlier-driven instability

Reproduced SCHO:

- Min: 2.48716603e+03
- Median: 1.23790869e+04
- Mean: 5.73062120e+05
- Max: 1.62899268e+07
- Sample STD: 2.96901053e+06
- IQR outliers: 4
- Mean without the single worst run: 3.11012688e+04

The large separation between median and mean, together with extreme upper-tail runs, confirms that the E5 F21 mismatch is primarily distributional rather than a uniform shift of every run.

### F23 — deterministic reproduced plateau

Largest repeated plateau: 30/30 runs at 2.50000000e+03.

The paper reports nonzero STD and a better Best value, so the current Python source-faithful trajectory does not reproduce the paper's F23 run-to-run distribution.

### F27 — deterministic reproduced plateau

Largest repeated plateau: 30/30 runs at 2.90000000e+03.

Again, this differs from the paper's nonzero variation.

### F28 — useful control

Largest repeated plateau: 30/30 runs at 3.00000000e+03.

Here the zero-variance plateau is consistent with the paper, so a plateau by itself is not evidence that the CEC evaluator is broken.

## 3. Other selected functions

F2, F7 and F15 should be read as stochastic/search-trajectory mismatches: their reproduced SCHO run distributions do not match the paper's mean-error scale as closely as most other functions.

See `E6_scho_anomaly_stats.csv` for quartiles, IQR outliers, plateau counts, paper/reproduction ratios, and worst-run sensitivity.

## 4. Pairwise GWO vs SCHO rank-sum diagnostic

Using the 30 independent E4 runs for each algorithm and a two-sided Mann–Whitney U test (the standard independent-sample Wilcoxon rank-sum formulation), alpha=0.05:

- SCHO better: 5 functions
- GWO better: 18 functions
- No significant difference: 7 functions
- Significant with equal sample medians: 0 functions

These tests describe the current Python reproduction only. They are not a reproduction of the paper's full Table 15 because the paper compares SCHO against eight other algorithms, not only GWO.

## 5. Interpretation

E6 supports three conclusions:

1. The SCHO-paper mismatch is not one single failure mode. F21 is heavy-tail/outlier-driven, whereas F23/F27 are deterministic plateau mismatches.
2. F28 shows that a deterministic plateau can also be genuinely consistent with the paper.
3. There is still no justification for tuning the frozen SCHO implementation. The correct next step is to document these differences and preserve the source-faithful implementation.

## 6. Files

- `results/processed/E6_scho_anomaly_stats.csv`
- `results/processed/E6_scho_selected_runs.csv`
- `results/processed/E6_gwo_vs_scho_rank_sum.csv`
- `report/figures/E6_scho_error_by_run.png`
- `report/figures/E6_scho_error_boxplot.png`
- `report/notes/E6_scho_anomaly_report.md`
