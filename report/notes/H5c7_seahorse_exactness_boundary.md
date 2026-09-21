# H5c7 — Sea-Horse Optimizer (SHO) exactness boundary

## Identity guard

In the SCHO paper, reference [109] is:

Shijie Zhao, Tianran Zhang, Shilin Ma, Mengchen Wang,
**Sea-horse optimizer: a novel nature-inspired meta-heuristic for global
optimization problems**.

Therefore H5 `SHO` means **Sea-Horse Optimizer**, not Spotted Hyena Optimizer.

## Author package status

The official/author MATLAB Central entry is File Exchange **115945** by S. Zhao.

The File Exchange version history shows:

- v1.0.0 — 6 Aug 2022
- v2.0.0 — DOI update
- v3.0.0 — Cite update
- v4.0.0 — Cite update
- v5.0.0 — Paper statement update

The current files listing identifies:

- `BenchmarkFunctions.m`
- `main_SHO.m`
- `initialization`
- `SHO`
- `levy`

However, in H5c7 the full historical v1.0.0 `SHO.m` body was not recovered
for line-by-line code verification.

Therefore **do not freeze H5c7 as SOURCE_STRUCTURED**.

Frozen exactness label after PASS:

`SHO_SEAHORSE_PAPER_EQUATION_FAITHFUL__AUTHOR_PACKAGE_IDENTIFIED__CODE_LEVEL_NOT_VERIFIED__NUMPY_RNG`

## Equations implemented

Movement behavior:

- `r1 = randn()`
- if `r1 > 0`: spiral movement with `u=v=0.05` and Levy flight
- else: Brownian-motion equation
- Levy constants: `s=0.01`, `lambda=1.5`

Predation behavior:

- success threshold `r2 > 0.1`
- `alpha = (1 - t/T)^(2t/T)`

Breeding behavior:

- sort predation population by fitness
- best half = fathers
- worse half = mothers
- one offspring per father/mother pair
- `offspring = r3*father + (1-r3)*mother`

Selection:

- combine predation population with offspring
- retain the best N

## Paper-vs-third-party diagnostic discrepancy

A public third-party Python implementation (MEALPY OriginalSeaHO) was checked
only as a diagnostic cross-reference.

Its Brownian branch differs from the paper equation in the inner vector term.
H5c7 follows the **paper equation**, not that third-party expression.

This is why H5c7 is not labelled author-source exact.

## H5 formal protocol

Later H5 formal runs use:

- N=30
- MaxIter=500
- F1–F13: D=30
- F14–F23: native dimensions
- 30 independent runs

No tuning is performed to force Table 7 agreement.
