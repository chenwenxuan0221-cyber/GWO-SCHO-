# H4b — SCHO Fig.8 history instrumentation protocol

## Goal

Instrument the frozen source-faithful SCHO implementation so that the five
qualitative metrics in paper Fig. 8 can be reproduced in H4c, without modifying
`algorithms/scho.py`.

## Paper Fig.8 functions

- F2
- F7
- F9
- F10
- F11
- F15
- F21

The paper displays five qualitative columns:
1. parameter-space / function surface;
2. search history;
3. first search agent, first dimension trajectory;
4. average fitness of all search agents;
5. convergence curve.

## History sampling convention

The exact source code does not expose a history logger, so H4b freezes a
controlled-equivalent sampling convention.

For each of the `MaxIter` convergence points, history is captured from the same
population state that the frozen optimizer actually evaluates:

1. initialize / update positions;
2. apply source-faithful boundary repair;
3. evaluate each candidate exactly once;
4. update historical best;
5. record evaluated positions and fitness;
6. continue with source bookkeeping.

At the special `t == BS` source sorting step, histories are recorded immediately
before sorting `Objective_values`, so each fitness row remains aligned with the
corresponding row of `X`. The mean fitness is unchanged by that sorting.

## What is recorded

- `position_history`: `(MaxIter, N, dim)`
- `fitness_history`: `(MaxIter, N)`
- `first_agent_x1`: `(MaxIter,)`
- `average_fitness`: `(MaxIter,)`
- `best_position_history`: `(MaxIter, dim)`
- `convergence`: `(MaxIter,)`
- `phase_history`: first/second phase label
- `redistribution_count`: literal bounded-search population reinitializations
- `T`: source phase-switch index
- `initial_BS`: first source bounded-search scheduling index

## Equivalence requirement

Instrumentation is acceptable only if, for identical optimizer/objective seeds:

- final best score is exactly equal to frozen SCHO;
- final best position is array-exact equal;
- the complete convergence curve is array-exact equal.

This is checked on all seven Fig.8 functions.

F7 receives two independently reconstructed objective wrappers with the same
objective seed so its stochastic sequence starts identically in both runs.

## H4b smoke protocol

- N = 6
- MaxIter = 40
- optimizer seed = 1000
- objective seed = `2024000 + function_number`

This is intentionally small because H4b validates semantics, not paper-scale
optimization quality. MaxIter=40 is still long enough to exercise:
- first phase;
- second phase;
- the source's bounded-search scheduling / redistribution path.

## H4c paper-scale protocol

After H4b passes, H4c will use:
- N = 30
- MaxIter = 500
- project seed = 1000
- same seven functions
- raw `.npz` history evidence
- five-column Fig.8-style rendering
- explicit `PAPER-STRUCTURE / CONTROLLED-EQUIVALENT` label.

The paper does not state the Fig.8 random seed, so pixel/trajectory equality is
not claimed.
