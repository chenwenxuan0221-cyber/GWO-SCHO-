# H1d — GWO × SIS2005 single-seed integration smoke test

## Purpose

H1d is a structural integration check before the 30-run experiment.

It deliberately does **not** judge agreement with GWO Table 8.

## Protocol used

- GWO: frozen `algorithms/gwo.py`
- Benchmark: source-faithful `benchmarks/gwo_sis2005.py`
- F24–F29 / CF1–CF6
- D = 10
- bounds = [-5, 5]^10
- N = 30
- MaxIter = 500
- seed = 1000
- one run per function

The paper explicitly reports 30 independent runs for the benchmark functions.
The released GWO `main.m` uses 30 search agents and 500 iterations; H1d uses
those released-code settings as the project/source-aligned integration protocol.

## PASS criteria

For every F24–F29:

1. finite best score;
2. finite best position with shape (10,);
3. best position stays within [-5,5];
4. convergence curve length = 500;
5. all curve values finite;
6. historical-best curve is non-increasing;
7. final curve value equals returned best score.

A numerical difference from Table 8 is not a smoke-test failure.
Paper agreement is assessed only in H1e after 30 runs.
