# H1e — Formal 30-run GWO SIS2005 protocol

## Goal

Reproduce the GWO-paper F24–F29 / SIS2005 CF1–CF6 experiment using the
source-faithful benchmark layer frozen in H1b/c.

## Frozen protocol

- Functions: F24–F29 / CF1–CF6
- Dimension: D=10
- Bounds: [-5,5]^10
- Population: N=30
- MaxIter: 500
- Runs: 30/function
- Seeds: 1000–1029
- Optimizer: frozen `algorithms/gwo.py`
- Benchmark variant: `source_faithful`

The paper states 30 runs but does not report seeds. Seeds 1000–1029 are the
project's deterministic reproduction convention, not a claim about the paper's
original random streams.

## Statistical convention

The script saves both:
- sample STD (`ddof=1`) — primary Table-8 comparison,
- population STD (`ddof=0`) — diagnostic.

No optimizer parameter is tuned to improve paper agreement.

## Checkpoint / resume

The raw CSV is written after every completed run. If interrupted, rerun the
same command; already completed protocol-matching runs are skipped.

## Output files

- `results/raw/gwo_sis2005_h1e_runs.csv`
- `results/processed/gwo_sis2005_h1e_summary.csv`
- `report/gwo_sis2005_h1e_table8_comparison.md`

## Meaning of PASS

`H1e RESULT: PASS` means:
- 180 optimizer runs completed structurally,
- all run-level validation checks passed,
- summary/report evidence was generated.

It does **not** mean the reproduced numerical means/STD must equal Table 8.
Numerical agreement is interpreted after the run and is never tuned into place.
