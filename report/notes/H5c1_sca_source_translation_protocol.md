# H5c1 — SCA source-structured Python translation

## Source basis

Primary source: Seyedali Mirjalili's author MATLAB implementation `SCA.m`
(File Exchange submission 54948).

The author source uses:

- initial population before the main loop;
- first population evaluated once;
- `t=2` for the main loop;
- `a=2`;
- `r1 = a - t*(a/Max_iteration)`;
- per coordinate:
  - `r2 = 2*pi*rand`
  - `r3 = 2*rand`
  - `r4 = rand`
- sine update when `r4 < 0.5`, otherwise cosine update;
- boundary clipping after all coordinates have been updated;
- objective reevaluation after clipping.

This matches the SCHO paper Table 6 anchor `a=2`.

## Important source quirk

The MATLAB source creates `Convergence_curve=zeros(1,Max_iteration)`, starts
the loop at `t=2`, and only assigns `Convergence_curve(t)`.

Therefore `Convergence_curve(1)` remains zero.

H5c1 preserves this behavior intentionally. It is not silently repaired.

For later Fig.9 plotting, this quirk must be handled transparently at the
plotting layer if a log axis is used; do not rewrite the optimizer merely to
beautify the curve.

## RNG exactness

The Python port uses `numpy.random.default_rng`.

It preserves the source random-draw *structure*:

- scalar bounds: one N×D initialization draw;
- vector bounds: one N-vector draw per dimension;
- three fresh random scalars per candidate coordinate per update.

It does not claim MATLAB RNG-stream or bitwise equivalence.

## H5c1 acceptance

Smoke anchors:

- F2
- F7
- F15
- F21

Settings:

- N=6
- MaxIter=40
- optimizer seed=1000

Checks:

- deterministic same-seed reruns;
- finite score/position/curve;
- source curve index 0 remains zero;
- historical-best curve tail is non-increasing;
- N×MaxIter objective evaluations;
- exactly 3 random update draws per coordinate;
- first r1 follows t=2 source indexing;
- final r1 is zero;
- scalar/vector initialization call structure;
- MaxIter<2 guard.

Frozen label on PASS:

`SCA_SOURCE_STRUCTURED_PYTHON_TRANSLATION__NUMPY_RNG`
