# H2e — GWO Fig.11 qualitative convergence reproduction

## Reproduction tier

`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`

The exact original Fig.-11 shift vectors, seed and internal logging semantics
were not recovered. H2e therefore uses the H2c frozen deterministic shift
convention and the H2b history adapter, which was regression-tested against
the frozen GWO implementation.

## Protocol

- Functions: F1, F7, F9, F10, F14, F18, F26, F29
- Search agents: 6
- Iterations: 100
- GWO seed: 1000
- Dimensions: native benchmark dimensions frozen in H2c
- Shift: target optimum at 65% from lower to upper bound in every coordinate
- F26/F29: H1 source-faithful SIS2005 definitions
- Fitness-history display: population mean fitness per evaluated iteration
- Search history: all six evaluated agents projected onto x1/x2
- Surface: x1/x2 slice through the shifted target optimum for remaining dimensions

## Outputs

- `report/figures/gwo_fig11_part1_F1_F7_F9.png`
- `report/figures/gwo_fig11_part2_F10_F14_F18_F26_F29.png`
- `report/figures/gwo_fig11_all8.png`
- eight raw `.npz` history evidence files in `results/raw/`
- `results/processed/gwo_h2e_fig11_summary.csv`
- `results/processed/gwo_h2e_fig11_manifest.csv`

## Run summary

| Function | D | Best score | Target x1 | Best x1 | Distance to shifted target |
|---|---:|---:|---:|---:|---:|
| F1 | 30 | 11827.18319 | 30 | 1.6609306 | 108.75285 |
| F7 | 30 | 4.464591656 | 0.384 | 0.1116421 | 1.6062101 |
| F9 | 30 | 190.710365 | 1.536 | -0.53739173 | 8.8512852 |
| F10 | 30 | 17.17061153 | 9.6 | -0.78241532 | 43.987928 |
| F14 | 2 | 6.903335783 | 19.6608 | 35.697553 | 22.606266 |
| F18 | 2 | 3.000293848 | 0.6 | 0.59917747 | 0.00090099767 |
| F26 | 10 | 373.9582872 | 1.5 | -0.58153725 | 6.3299505 |
| F29 | 10 | 909.2546053 | 1.5 | -3.6352036 | 9.662965 |

## Interpretation boundary

These figures reproduce the paper's qualitative structure, not its unrecovered
exact random trajectory. Similar qualitative exploration-to-exploitation behavior
may be compared, but point-by-point agreement with the published Fig.11 is not
claimed.
