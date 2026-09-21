# H2e — GWO Fig.11 qualitative convergence protocol

## Reproduction tier

`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`

The original paper confirms the qualitative structure of Fig.11 but the exact
shift vectors, random seed and internal history-logging semantics were not
recovered from public source assets. H2e therefore builds on the already frozen
H2b/H2c protocol instead of inventing an "exact" trajectory.

## Paper-structure elements reproduced

Functions:
- F1
- F7
- F9
- F10
- F14
- F18
- F26
- F29

Protocol:
- 6 search agents
- 100 iterations
- shifted benchmarks
- six panels per function:
  1. benchmark landscape
  2. search history
  3. parameter `a`
  4. trajectory of the first agent in the first dimension
  5. fitness history
  6. convergence curve

## Controlled-equivalent conventions

### Shift
Reuse H2c exactly:
- one known optimum is moved to 65% of each coordinate's [lb,ub] interval;
- native benchmark dimensions are retained;
- F26/F29 use the H1 source-faithful SIS2005 definitions.

### GWO random seed
`1000`

The paper does not report the Fig.11 seed. This is a deterministic project
convention, not a reconstruction of the original random stream.

### Objective RNG
F7 is stochastic. H2e uses a dedicated fixed objective RNG seed independent of
the GWO RNG. Surface visualization uses a separate objective instance so that
plotting cannot alter the optimizer's stochastic sequence.

### History sampling
Reuse the H2b convention:
- boundary repair
- record positions
- evaluate fitness
- record fitness
- leader update
- compute `a`
- position update
- record historical-best convergence

H2b already verified that adding this instrumentation leaves the frozen GWO
best score, best position and full convergence curve unchanged.

### Fitness history
The exact paper-internal definition of "Fitness history" was not recovered.
H2e freezes it as:

`mean fitness of the six evaluated agents at each iteration`

The full per-agent fitness matrix is still saved in each raw `.npz` file.

### Landscape/search-history projection
For high-dimensional functions:
- x1 and x2 are varied/plotted;
- all remaining dimensions are fixed at the shifted target optimum.

Search history is the projection of all six evaluated agents over all
iterations onto x1/x2.

## Expected outputs

Figures:
- `report/figures/gwo_fig11_part1_F1_F7_F9.png`
- `report/figures/gwo_fig11_part2_F10_F14_F18_F26_F29.png`
- `report/figures/gwo_fig11_all8.png`

Raw history evidence:
- `results/raw/gwo_h2e_fig11_F1.npz`
- ...
- `results/raw/gwo_h2e_fig11_F29.npz`

Processed evidence:
- `results/processed/gwo_h2e_fig11_summary.csv`
- `results/processed/gwo_h2e_fig11_manifest.csv`

Generated report:
- `report/notes/H2e_gwo_fig11_results.md`

## PASS meaning

`H2e RESULT: PASS` means:
- all 8 controlled-equivalent shifted runs completed;
- all recorded arrays have expected shapes and finite values;
- convergence curves are valid historical-best curves;
- 8 raw history files were saved;
- all 3 Fig.11-style output figures were generated.

It does not mean pixel-by-pixel equality with the paper's unrecovered original
Fig.11 trajectory.
