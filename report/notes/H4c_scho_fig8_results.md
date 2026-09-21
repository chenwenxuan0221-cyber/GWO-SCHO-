# H4c — SCHO Fig.8 qualitative reproduction

## Freeze tier

`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`

The paper identifies five qualitative metrics but does not publish the
exact Fig.8 seed or an exact history-logging implementation. This stage
therefore reproduces the paper structure with the frozen source-faithful
SCHO and an explicitly frozen H4b history convention.

## Protocol

- Functions: F2, F7, F9, F10, F11, F15, F21
- N = 30
- MaxIter = 500
- optimizer seed = 1000 (project convention)
- separate deterministic F7 objective RNG
- no modification of `algorithms/scho.py`
- phase switch from frozen source: `T = floor(500 / 3.6) = 138`

## Five reproduced metrics

1. parameter-space / 2-D landscape
2. search history
3. first-agent first-dimension trajectory
4. average fitness of all search agents
5. historical-best convergence curve

For F2/F7/F9/F10/F11, the surface is the direct 2-D version of the
benchmark formula. For fixed-dimensional F15/F21, dimensions 3..D are
held at the final best position while x1/x2 are varied; those panels are
therefore controlled 2-D slices rather than claims of an exact published
projection.

## Run diagnostics

| F | D | Final best | Paper fmin metadata | T | Redistributions | Strict best improvements | Post-switch improvements |
|---|---:|---:|---:|---:|---:|---:|---:|
| F2 | 30 | 0 | 0 | 138 | 570 | 263 | 126 |
| F7 | 30 | 0.00018841019 | 0 | 138 | 570 | 40 | 4 |
| F9 | 30 | 0 | 0 | 138 | 570 | 63 | 7 |
| F10 | 30 | 4.4408921e-16 | 0 | 138 | 570 | 146 | 10 |
| F11 | 30 | 0 | 0 | 138 | 570 | 143 | 6 |
| F15 | 4 | 0.00031109031 | 0.0003 | 138 | 570 | 46 | 4 |
| F21 | 4 | -10.151814 | -10.1532 | 138 | 570 | 21 | 3 |

## Interpretation boundary

The paper qualitatively discusses stronger early exploration, later
exploitation, a population-average-fitness disturbance near the phase
switch, smoother unimodal convergence and more stepwise multimodal
convergence. H4c records the evidence needed to inspect those claims,
but does not force the project trajectory to exhibit every published
visual feature under the unrecovered paper seed.

No trajectory is tuned to imitate the printed figure.

## Outputs

- `report/figures/scho_fig8_part1_F2_F7_F9.png`
- `report/figures/scho_fig8_part2_F10_F11_F15.png`
- `report/figures/scho_fig8_part3_F21.png`
- `report/figures/scho_fig8_all7.png`
- seven raw `.npz` history files under `results/raw/`
- `results/processed/scho_h4c_fig8_summary.csv`
- `results/processed/scho_h4c_fig8_manifest.csv`

## PASS meaning

`H4c RESULT: PASS` means all seven paper-scale controlled-equivalent
runs completed, raw histories were saved, and all four figure files were
generated. It does not mean pixel-exact equality with the paper's Fig.8.