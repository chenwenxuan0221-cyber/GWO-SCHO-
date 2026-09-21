# H2c — Controlled-equivalent shifted Fig.-11 benchmark protocol

## Status

H2a established that the paper explicitly provides:
- Fig. 11 functions: F1, F7, F9, F10, F14, F18, F26, F29
- six search agents
- shifted benchmark functions
- search history and first-agent first-dimension trajectory
- figure-evident 100 iterations

H2b established a history adapter that preserves the frozen GWO numerical
trajectory exactly.

Because the exact Fig.-11 shift vectors, dimensions and seed are not publicly
recovered, H2 proceeds as:

`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`

This file freezes the controlled-equivalent shift and dimension conventions.

## Dimension convention

Retain the native benchmark dimensions already used by the project / paper
benchmark tables:

- F1: D=30
- F7: D=30
- F9: D=30
- F10: D=30
- F14: D=2
- F18: D=2
- F26: D=10
- F29: D=10

The 2D landscape/search-history panels later visualize only the first two
coordinates while the remaining coordinates are fixed at the shifted target
optimum.

This is a project convention, not a claim that the original Fig. 11 used these
exact dimensions.

## Shift convention

For each coordinate, move one known global optimum to the point 65% of the way
from the lower to the upper search bound:

    target = lb + 0.65 * (ub - lb)
    delta  = target - base_optimum
    shifted_f(x) = base_f(x - delta)

This has three advantages:
1. deterministic and fully documented;
2. the shifted optimum is strictly inside the original search box;
3. all eight functions use one common convention instead of hand-picked shifts.

Known base optimum locations used:

- F1, F7, F9, F10: all-zero vector
- F14: (-32, -32), the source-faithful best Foxholes grid point
- F18: (0, -1), Goldstein-Price global optimum
- F26: first source-faithful SIS2005 component optimum `o1`
- F29: first source-faithful SIS2005 component optimum `o1`

F26 and F29 continue to use the H1 source-faithful SIS2005 definitions.
The F26 paper-table/source discrepancy remains documented and is not silently
changed for H2.

## F7 stochastic handling

F7 contains its original random-noise term. A separate objective RNG seed is
used so that:
- benchmark noise is reproducible,
- the GWO RNG stream remains controlled independently,
- the history adapter does not alter GWO random-number consumption.

## H2c validation

The H2c test checks all eight functions for:
1. expected dimension;
2. target-location convention;
3. translation identity at the selected base optimum;
4. frozen GWO vs instrumented GWO exact equality for:
   - final best score,
   - best position,
   - full convergence curve;
5. finite history arrays and expected shapes.

Smoke protocol:
- N=6
- MaxIter=100
- GWO seed=1000
- deterministic per-function objective seeds

H2c does not produce the final Fig.-11-style plots.
Those are generated in H2d after this protocol passes on the user's machine.
