# H6a — H6 Scalability Full Comparison Protocol

## Scope

Protocol ID: `H6_SCALABILITY_V1`

- Algorithms: SCHO, GWO, ALO, SCA, SSA, AOA, RSA, SHO, GJO
- Functions: F1–F13
- Dimensions: 100, 500
- Population: 30
- MaxIter: 500
- Runs: 30 per function/dimension/algorithm
- Full matrix: 9 × 13 × 2 × 30 = 7020 runs

## Frozen components

- `algorithms/scho.py` and `algorithms/gwo.py` remain unchanged.
- High-dimensional benchmarks come from `benchmarks/scho_scalability_h3.py`.
- Comparators reuse the H5-implemented algorithms.
- SHO means Sea-Horse Optimizer from `algorithms/sea_horse.py`.
- AOA must be called with `mu=0.5`.
- Source quirks are preserved; no tuning is permitted.

## Seed protocol

Optimizer seed:

```text
1000 + run - 1
```

Objective seed:

```text
7_000_000 + dim * 10_000 + function_number * 100 + run
```

This inherits the frozen H3c scalability schedule.
F7 consumes the objective RNG. Deterministic functions record the seed for protocol traceability but do not numerically depend on it.

## SCHO reuse

`results/raw/scho_scalability_h3c_runs.csv` contains 780 complete SCHO rows.

These rows are reused only if they pass protocol validation for:

- Function F1–F13
- Dimension 100/500
- Run 1–30
- optimizer seed
- objective seed
- N=30
- MaxIter=500
- Status=PASS

Reused SCHO rows: 780
New comparator runs: 6240
Final dataset: 7020 rows

## Statistical outputs

- Table 9: D=100 — Best, Average, sample STD (ddof=1), per-function rank, Mean Rank, Final Ranking.
- Table 10: D=500 — same statistics.
- Table 11: D=100 — two-sided Wilcoxon rank-sum style SCHO vs each comparator, alpha=0.05.
- Table 12: D=500 — same significance analysis.

## Exactness boundaries

- NumPy RNG is used; no MATLAB bitwise RNG equivalence is claimed.
- Algorithm implementations are reused from frozen H5/core work.
i- Tables 9/10 are table-structure reproductions; numerical agreement with the paper is assessed after the runs.
- Wilcoxon statistical internals are project-controlled and not claimed to be bitwise-identical to the paper's software.