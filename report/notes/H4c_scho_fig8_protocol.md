# H4c — SCHO Fig.8 qualitative reproduction protocol

## Reproduction tier

`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`

The paper specifies the qualitative metrics and the displayed functions, but it
does not publish the exact Fig.8 random seed or an exact history logger.

## Paper structure reproduced

Functions:
- F2
- F7
- F9
- F10
- F11
- F15
- F21

Protocol:
- N = 30
- MaxIter = 500
- original benchmark dimensions
- project optimizer seed = 1000
- separate deterministic objective RNG for stochastic F7

Five panels per function:
1. parameter space / 2-D landscape
2. search history
3. first-agent first-dimension trajectory
4. average fitness of all search agents
5. historical-best convergence curve

## History source

H4c reuses the H4b instrumented implementation that already passed an
exact-equivalence audit against frozen `algorithms/scho.py`.

No extra optimizer RNG calls or objective evaluations are introduced by history
recording.

## Parameter-space convention

For F2/F7/F9/F10/F11:
- evaluate the formula directly in two dimensions.

For F15/F21:
- vary x1/x2 over the benchmark bounds;
- hold dimensions 3..D at the final best position of the H4c run.

Thus F15/F21 are explicitly controlled 2-D slices.

Surface plotting is performed only after optimization and uses a separate F7
surface RNG, so plotting cannot affect the optimizer trajectory.

## Paper phase switch

The frozen source uses:
- `ct = 3.6`
- `T = floor(MaxIter / ct)`

At MaxIter=500:
- `T = 138`

This is consistent with the paper's qualitative discussion of an average
fitness disturbance around iteration 140. H4c does not force or tune such a
disturbance; it records the actual controlled-equivalent trajectory.

## Expected outputs

Raw:
- `results/raw/scho_h4c_fig8_F2.npz`
- `results/raw/scho_h4c_fig8_F7.npz`
- `results/raw/scho_h4c_fig8_F9.npz`
- `results/raw/scho_h4c_fig8_F10.npz`
- `results/raw/scho_h4c_fig8_F11.npz`
- `results/raw/scho_h4c_fig8_F15.npz`
- `results/raw/scho_h4c_fig8_F21.npz`

Processed:
- `results/processed/scho_h4c_fig8_summary.csv`
- `results/processed/scho_h4c_fig8_manifest.csv`

Figures:
- `report/figures/scho_fig8_part1_F2_F7_F9.png`
- `report/figures/scho_fig8_part2_F10_F11_F15.png`
- `report/figures/scho_fig8_part3_F21.png`
- `report/figures/scho_fig8_all7.png`

Report:
- `report/notes/H4c_scho_fig8_results.md`

## PASS meaning

`H4c RESULT: PASS` means all seven paper-scale runs completed structurally,
all raw histories were saved, and all four Fig.8-style figures were generated.

It does not claim pixel-exact reconstruction of the paper trajectory.
