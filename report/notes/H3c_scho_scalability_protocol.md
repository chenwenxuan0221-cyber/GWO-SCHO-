# H3c — Formal SCHO scalability core protocol

## Goal

Reproduce the SCHO columns of paper Tables 9 and 10 using the frozen,
source-faithful SCHO implementation and the H3b-validated high-dimensional
F1–F13 adapter.

## Formal protocol

- F1–F13
- D = 100 and D = 500
- N = 30
- MaxIter = 500
- 30 independent runs/function/dimension
- optimizer seeds = 1000–1029
- total optimizer runs = 780

The paper does not publish random seeds. The seed range is a project
reproducibility convention.

F7 keeps its stochastic noise term and receives a separate deterministic
objective RNG seed per run.

## Paper reference values

The runner embeds only the **SCHO columns** from:
- Table 9 (D=100)
- Table 10 (D=500)

for:
- Best
- Average
- STD

These values are comparison anchors only and are never used to tune the
optimizer.

## STD convention

The paper does not explicitly state `ddof`.

H3c saves both:
- sample STD (`ddof=1`) — primary comparison, consistent with MATLAB's default
  `std` behavior;
- population STD (`ddof=0`) — diagnostic.

## Checkpoint / resume

After every completed optimizer run, the parent process appends one validated
row to:

`results/raw/scho_scalability_h3c_runs.csv`

If the process is interrupted, run the same command again. Completed rows that
match the exact protocol are skipped.

## Parallel execution

D=500 is computationally expensive in the frozen pure-Python source-faithful
implementation.

H3c therefore uses modest process-level parallelism by default. Each run has
explicit optimizer and objective seeds, so scheduling order does not alter its
individual deterministic trajectory.

The parent process alone writes result files.

Optional environment variable:
`H3C_WORKERS`

may be used later if runtime tuning is needed. Changing worker count changes
wall-clock execution only, not the scientific protocol or run seeds.

## Outputs

- `results/raw/scho_scalability_h3c_runs.csv`
- `results/processed/scho_scalability_h3c_summary.csv`
- `report/scho_scalability_h3c_tables9_10_comparison.md`

## Meaning of PASS

`H3c RESULT: PASS` means:
- all 780 formal runs completed;
- run-level validation passed;
- raw and processed evidence was generated.

It does not mean exact numerical agreement with Tables 9/10.

H3d analyzes agreement and freezes the SCHO scalability-core result without
parameter tuning.

## Full-paper status after H3c

H3c is **SCHO scalability core**, not the full Section 3.1.4 comparison.

Still required for full Tables 9–12:
- GWO
- ALO
- SCA
- SSA
- AOA
- RSA
- SHO
- GJO
- Friedman ranking
- Wilcoxon rank-sum tests
