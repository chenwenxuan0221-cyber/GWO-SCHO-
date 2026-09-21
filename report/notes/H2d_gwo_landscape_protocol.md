# H2d patch v2 — GWO Fig.7–Fig.10 benchmark landscape protocol

## Why this patch exists

The first H2d skeleton treated `get_benchmark()` as if it returned a dictionary:

`benchmark["obj_func"]`

The current project actually returns a `Benchmark` dataclass, with attributes:

- `benchmark.func`
- `benchmark.make_objective(...)`
- `benchmark.dim`
- `benchmark.lb`
- `benchmark.ub`
- `benchmark.optimum`

Therefore the first skeleton fails with:

`TypeError: 'Benchmark' object is not subscriptable`

This patch replaces that skeleton completely.

## Classic Fig.7–Fig.9 protocol

For F1–F14 and F16–F18, the plotting script uses the current project's
`Benchmark` dataclass API and evaluates the paper-style **2-D versions** of the
dimension-generic benchmark formulas.

F7 remains stochastic. Its plotting objective receives a fixed RNG seed so the
surface is reproducible. This seed is a project visualization convention; the
paper does not report a plot seed.

The plotting ranges follow the GWO `func_plot.m` visualization convention.
These plotting ranges are not always identical to the optimization search
bounds and must not be reused as benchmark optimization bounds.

## Fig.10 protocol

The recovered original SIS2005 `func_plot.m` calls `SIS_novel_func([x,y], ...)`
for a true D=2 display. In that source, CF2–CF6 generate new orthogonal matrices
when D != 10. The recovered package does not provide the exact historical
D=2 matrix realization / RNG state used for the published Fig.10.

Therefore H2d does **not** invent those matrices.

Instead Fig.10 is explicitly labeled as a controlled-equivalent visualization:

- keep the H1 frozen, source-faithful D=10 SIS2005 functions;
- vary x1 and x2 over [-5,5];
- fix x3..x10 at the first component optimum;
- thus the slice contains the known global optimum;
- F26 continues to use the H1 source-faithful Rastrigin definition.

This is:
`SOURCE-FAITHFUL D10 2D SLICE / CONTROLLED-EQUIVALENT`

It is not claimed to be a pixel-exact reconstruction of the unpublished D=2
rotation realization used for the paper figure.

## Expected outputs

- `report/figures/gwo_fig7_unimodal_landscapes.png`
- `report/figures/gwo_fig8_multimodal_landscapes.png`
- `report/figures/gwo_fig9_fixed_multimodal_landscapes.png`
- `report/figures/gwo_fig10_composite_landscapes.png`
- `results/processed/gwo_h2d_landscape_manifest.csv`

Expected terminal end:

`H2d RESULT: PASS`

The script does not execute or modify GWO.
