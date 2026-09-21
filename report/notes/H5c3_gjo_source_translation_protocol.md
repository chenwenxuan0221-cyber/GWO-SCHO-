# H5c3 — GJO source-structured Python translation

## 1. Primary basis

Author source package:

- Nitish Chopra
- MATLAB Central File Exchange 108889
- version 1.0.0
- published 27 Mar 2022
- files include `GJO.m`, `levy.m`, `initialization.m`

Original paper:

Chopra & Ansari (2022), *Golden jackal optimization: A novel
nature-inspired optimizer for engineering applications*.

The SCHO paper Table 6 uses:

- `c1 = 1.5`
- Levy `beta = 1.5`

These agree with the GJO formulation used here.

## 2. Frozen algorithm structure

H5c3 preserves:

- population initialized before the loop;
- `Male_Jackal_score = inf`;
- `Female_Jackal_score = inf`;
- loop counter `l=0`;
- bound repair and fitness evaluation before movement;
- independent sequential male/female leader tests;
- `E1 = 1.5*(1-l/MaxIter)`;
- one Levy matrix per iteration;
- `RL = 0.05 * levy(N,dim,1.5)`;
- one fresh `E0=2*rand-1` per coordinate;
- exploration when `|E| >= 1`;
- exploitation when `|E| < 1`;
- average of male- and female-guided proposals;
- curve records the historical male score at every loop.

## 3. Exploration equations

For prey coordinate `X`:

`X1 = Male - E * |Male - RL*X|`

`X2 = Female - E * |Female - RL*X|`

then:

`X_new = (X1 + X2)/2`

## 4. Exploitation equations

`X1 = Male - E * |RL*Male - X|`

`X2 = Female - E * |RL*Female - X|`

then:

`X_new = (X1 + X2)/2`

## 5. Leader-update quirk

The author-code family updates male and female using separate sequential
`if` statements.

When a new male is discovered, the previous male is not automatically shifted
into the female slot. H5c3 intentionally preserves that behavior.

## 6. Levy helper

H5c3 implements the Mantegna helper used by the author package family:

- `beta=1.5`
- Gaussian `u` with computed sigma
- Gaussian `v` with unit standard deviation
- `z = u / |v|^(1/beta)`

and the main optimizer applies the documented `0.05` multiplier.

The Python implementation uses NumPy's normal generator; MATLAB RNG-stream
equivalence is not claimed.

## 7. H5c3 test

Anchors:

- F2
- F7
- F15
- F21

Settings:

- N=6
- MaxIter=40
- seed=1000

Checks:

- initialization random-call shape;
- Levy deterministic same-seed behavior;
- exactly N*MaxIter objective evaluations;
- exactly N*D*MaxIter coordinate E0 draws;
- exactly two N*D Gaussian Levy matrices per iteration;
- exploration + exploitation counts cover all updates;
- first E1 = 1.5;
- last E1 matches l=MaxIter-1 source indexing;
- finite female leader exists;
- same-seed deterministic rerun;
- convergence curve non-increasing.

Frozen label on PASS:

`GJO_SOURCE_STRUCTURED_PYTHON_TRANSLATION__NUMPY_RNG`
