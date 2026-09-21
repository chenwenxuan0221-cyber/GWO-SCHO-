# H3b — SCHO scalability adapter + smoke validation protocol

## Goal

Prepare F1–F13 for the paper's D=100 and D=500 scalability experiment without
editing the already frozen `benchmarks/classic_23.py` or `algorithms/scho.py`.

H3b is a structural validation stage only. It does not run the formal 30-run
experiment.

## Adapter rule

New module:

`benchmarks/scho_scalability_h3.py`

The adapter:
- supports F1–F13 only;
- supports D=100 and D=500 only;
- reuses the frozen classic benchmark function callables directly;
- preserves each function's original per-coordinate bounds;
- preserves each function's stochastic flag / objective factory;
- changes only dimension-dependent metadata.

For F8 only, the known optimum metadata scales with dimension:

`fmin = -418.9829 * D`

For F1–F7 and F9–F13 the project benchmark optimum remains 0.

## F7 rule

F7 keeps its stochastic random-noise term.

The adapter does not convert F7 into a deterministic benchmark.
A fixed objective seed is used in validation so repeated runs can be audited
reproducibly while keeping benchmark randomness independent of the optimizer
RNG.

## Source-faithful SCHO smoke protocol

The H3b test uses a small smoke protocol only:

- N = 6
- MaxIter = 20
- optimizer seed = 1000
- anchor functions = F1, F7, F13
- dimensions = 100 and 500

For every anchor, the test checks:
- finite best score;
- best-position shape equals D;
- finite best position;
- convergence-curve length equals 20;
- finite curve;
- historical best is non-increasing;
- repeated runs with identical optimizer/objective seeds are exactly
  reproducible.

## Metadata / formula validation

For all F1–F13 at D=100 and D=500 the test checks:
- dimension override;
- exact reuse of the frozen function callable;
- unchanged bounds;
- unchanged stochastic flag;
- dimension-correct optimum metadata;
- deterministic formula evaluation equivalence for non-stochastic functions.

The adapter also rejects:
- functions outside F1–F13;
- dimensions other than 100 or 500.

## Expected result

`H3b RESULT: PASS`

H3b PASS means the benchmark layer is ready for the formal SCHO scalability
experiment.

It does not imply agreement with paper Tables 9/10.

## Next stage

H3c:
- SCHO only
- F1–F13
- D=100 and D=500
- N=30
- MaxIter=500
- 30 runs/function/dimension
- 780 optimizer runs total
- checkpoint/resume
- raw + processed summaries
- direct comparison against the SCHO columns of Tables 9 and 10
