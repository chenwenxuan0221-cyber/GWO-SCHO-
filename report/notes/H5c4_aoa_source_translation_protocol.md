# H5c4 — AOA source structure + SCHO Table-6 parameter override

## 1. Primary source

Author source:

- Laith Abualigah
- MATLAB Central File Exchange 84742
- version 1.0.0
- `AOA.m`
- published 24 Dec 2020

The public author source sets:

- `MOP_Max = 1`
- `MOP_Min = 0.2`
- `Alpha = 5`
- `Mu = 0.499`

## 2. H5 protocol override

Bai et al. SCHO Table 6 specifies AOA:

- alpha = 5
- u/mu = 0.5

H5 reproduces Bai et al.'s comparison protocol rather than the untouched AOA
default experiment.

Therefore:

`Mu = 0.5`

is frozen for H5.

This is an explicit:

`SCHO_TABLE6_PARAMETER_OVERRIDE`

It is not silently described as the original AOA default.

## 3. Exact AOA.m control-flow details preserved

Initial population is evaluated once before the loop.

Main loop:

`C_Iter = 1 ... MaxIter`

Per iteration:

`MOP = 1 - C_Iter^(1/Alpha) / MaxIter^(1/Alpha)`

`MOA = 0.2 + C_Iter * (0.8/MaxIter)`

For each candidate coordinate:

1. draw `r1`;
2. scalar bounds:
   - directly use this `r1`;
3. vector bounds:
   - the source draws **another `r1`** inside the vector-bound branch;
   - the first `r1` is unused;
4. if `r1 < MOA`, draw `r2` and use division/multiplication;
5. otherwise draw `r3` and use subtraction/addition.

After all coordinates of candidate `i`:

- clip `Xnew(i,:)` to bounds;
- evaluate it;
- accept only if `Ffun_new(i) < Ffun(i)`;
- update global best from accepted/current `X(i,:)`.

This greedy acceptance is part of the author code and is preserved.

## 4. Important vector-bound RNG quirk

The duplicate `r1` draw for vector bounds is source behavior, not a typo
introduced by this project.

This matters for F17 because it has per-coordinate bounds.

H5c4 keeps the unused first draw so NumPy random-call structure follows the
MATLAB source structure as closely as possible.

No MATLAB RNG-stream or bitwise equivalence is claimed.

## 5. Convergence curve

Unlike SCA/SSA, AOA records every loop iteration from 1 through MaxIter.

Therefore there is no leading-zero source quirk in the AOA curve.

## 6. H5c4 validation

Smoke:

- scalar bounds: F2, F7, F15, F21
- vector bounds: F17

Settings:

- N=6
- MaxIter=40
- seed=1000

Checks:

- deterministic same-seed reruns;
- finite outputs;
- non-increasing historical-best curve;
- objective evaluations = `N*(MaxIter+1)`;
- one unconditional r1 per coordinate;
- one branch-local r2/r3 per coordinate;
- vector bounds consume an additional r1 per coordinate;
- D/M/S/A branch counts cover every coordinate update;
- greedy accept + reject = `N*MaxIter`;
- first MOP/MOA match source indexing;
- final MOP=0 and MOA=1;
- H5 mu=0.5 override is explicit.

Frozen label on PASS:

`AOA_SOURCE_STRUCTURED_PYTHON_TRANSLATION__SCHO_TABLE6_MU_0P5__NUMPY_RNG`
