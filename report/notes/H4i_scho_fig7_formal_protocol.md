# H4i — Formal controlled SCHO Fig.7 protocol

## Goal

Run the full Fig.7 experiment under the explicit H4h controlled equations.

This is **not** a source-faithful reconstruction of the unrecovered eleven
author variants.

Frozen exactness label:

`CONTROLLED-INTERPRETATION`

## Workload

Formal new runs:

`11 variants × 23 functions × 30 runs = 7590`

A separate 690-run SCHO control is not rerun. H4i reuses the completed H4e
SCHO rows because H4i intentionally adopts the same protocol:

- N=30
- MaxIter=500
- functions F1–F23
- optimizer seeds 1000–1029
- objective-seed rule:
  `4_024_000 + function_number*100 + run_number`

The runner validates all 690 SCHO rows before starting/resuming H4i.

## Fig.7 counting rule

The paper calls the bars the "number of the average optimal solutions" but
does not provide a machine-readable counting rule.

H4i freezes this controlled interpretation **before** seeing H4i results:

For each pair `(SCHO, Vn)` and each benchmark function:

1. Compute each algorithm's 30-run mean final fitness.
2. Minimization: lower mean receives one credit.
3. If the two means satisfy:
   `np.isclose(rtol=1e-9, atol=1e-12)`,
   both receive one credit.

Therefore two bars may sum to more than 23 when tied functions are credited to
both.

The tie tolerance is a project reproducibility convention and must not be
changed merely to improve agreement with Fig.7.

## Paper anchors

- V1: 18 / 15
- V2: 20 / 13
- V3: 17 / 15
- V4: 17 / 14
- V5: 17 / 16
- V6: 18 / 14
- V7: 20 / 13
- V8: 20 / 11
- V9: 18 / 9
- V10: 20 / 13
- V11: 18 / 15

Each pair is `SCHO / variant`.

These are diagnostic anchors only, never tuning targets.

## Checkpoint / resume

Every completed controlled-variant run is appended by the parent process to:

`results/raw/scho_fig7_h4i_variant_runs.csv`

Rerun the exact same command after interruption.

## Outputs

- `results/raw/scho_fig7_h4i_variant_runs.csv`
- `results/processed/scho_fig7_h4i_variant_summary.csv`
- `results/processed/scho_fig7_h4i_pairwise_by_function.csv`
- `results/processed/scho_fig7_h4i_pairwise_counts.csv`
- `report/figures/scho_fig7a_h4i_controlled.png`
- `report/figures/scho_fig7b_h4i_controlled.png`
- `report/figures/scho_fig7c_h4i_controlled.png`
- `report/figures/scho_fig7d_h4i_controlled.png`
- `report/scho_fig7_h4i_controlled_comparison.md`

## PASS meaning

`H4i RESULT: PASS` means all 7590 controlled variant runs completed and the
pairwise-average count analysis/figures were generated.

It does not mean the eleven controlled equations are author-source exact, and
it does not mean the paper bar heights were reproduced.

H4j performs the paper-agreement diagnostic and freezes all disagreements
without tuning.
