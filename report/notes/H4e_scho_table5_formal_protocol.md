# H4e — Formal SCHO Table-5 ablation protocol

## Goal

Run the complete Table-5-style structural ablation experiment using the H4d
frozen definitions.

## Models

- SCHO
- SCHO_NT
- SCHO_NSTF
- SCHO_NFTF
- SCHO_NSF
- SCHO_NFF

## Protocol

- F1–F23
- N = 30
- MaxIter = 500
- 30 independent runs/model/function
- optimizer seeds = 1000–1029
- common objective seed across variants for the same function/run
- total = 4140 optimizer runs

The seed range is a project reproducibility convention; the paper does not
publish its random streams.

## Exactness tiers

`SCHO`
- exact-trajectory control against frozen `algorithms/scho.py`.

Five ablations
- `PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION`.

The paper gives the deletion structure but separate author variant source was
not recovered.

## F7 rule

F7 remains stochastic.

For each F7 run:
- every variant receives an independently reconstructed objective wrapper;
- wrappers for the same run use the same objective seed.

Thus stochastic benchmark noise is controlled across variants without sharing
mutable RNG state.

## Statistics

For every model/function:
- Best
- Average
- sample STD (`ddof=1`) — primary Table-5-style STD
- population STD (`ddof=0`) — diagnostic
- Median
- Worst

Per-function rank is computed from the reproduced Average fitness under
minimization.

Tie convention:
- competition rank: `1, 2, 2, 4, ...` for exact equal averages.

Mean Rank:
- arithmetic mean of the 23 per-function ranks.

Final Rank:
- competition rank of the reproduced Mean Rank.

Paper ranking anchors:
- SCHO: mean 1.65, final 1
- SCHO_NT: mean 2.96, final 3
- SCHO_NSTF: mean 3.35, final 4
- SCHO_NFTF: mean 4.52, final 6
- SCHO_NSF: mean 2.13, final 2
- SCHO_NFF: mean 3.35, final 4

These anchors are not used to tune the implementations.

## Checkpoint/resume

After each completed run, the parent process appends one validated row to:

`results/raw/scho_table5_h4e_runs.csv`

Rerunning the same command skips exact protocol-matching rows.

Only the parent process writes output files.

## Parallel execution

Default:
- modest process parallelism, capped at 4 workers.

Optional environment variable:
- `H4E_WORKERS`

Changing worker count affects wall-clock time only, not seeds or per-run
scientific protocol.

## Outputs

- `results/raw/scho_table5_h4e_runs.csv`
- `results/processed/scho_table5_h4e_summary.csv`
- `results/processed/scho_table5_h4e_ranks.csv`
- `report/scho_table5_h4e_comparison.md`

## PASS meaning

`H4e RESULT: PASS` means:
- all 4140 runs completed;
- run-level structural validation passed;
- Table-5-style statistics and ranks were produced.

It does not imply numerical equality with the paper.

H4f performs the paper-agreement diagnostic and freezes the result without
parameter tuning.
