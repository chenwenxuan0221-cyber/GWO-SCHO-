# H3c — SCHO D=100 / D=500 scalability core reproduction

## Protocol

- Functions: F1–F13
- Dimensions: 100 and 500
- Search agents: 30
- MaxIter: 500
- Runs: 30/function/dimension
- Optimizer: frozen source-faithful `algorithms/scho.py`
- Seeds: 1000–1029 (project reproducibility convention)
- F7 uses a separate deterministic objective RNG seed per run
- Execution workers used: 4
- Primary paper-comparison STD: sample STD (`ddof=1`)

This stage reproduces the **SCHO columns** of Tables 9 and 10.
It does not yet reproduce the complete nine-algorithm Friedman / Wilcoxon
comparison.

## D = 100

| F | Repro Best | Repro Mean | Repro STD | Paper Best | Paper Mean | Paper STD | Mean agreement |
|---|---:|---:|---:|---:|---:|---:|---|
| F1 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F2 | 0 | 4.27115e-262 | 0 | 0 | 7.576e-263 | 0 | outside factor 2 |
| F3 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F4 | 0 | 6.35646e-251 | 0 | 0 | 4.243e-249 | 0 | outside factor 2 |
| F5 | 98.7709 | 98.8922 | 0.0943624 | 98.75 | 98.87 | 0.1004 | within ±25% |
| F6 | 0.236477 | 12.6674 | 8.08345 | 0.0001466 | 8.562 | 8.137 | within factor 2 |
| F7 | 1.81152e-06 | 7.19389e-05 | 7.18356e-05 | 5.429e-07 | 7.285e-05 | 5.388e-05 | within ±25% |
| F8 | -32054.1 | -14398.2 | 6645.04 | -39260 | -18560 | 9867 | within ±25% |
| F9 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F10 | 4.44089e-16 | 4.44089e-16 | 0 | 4.441e-16 | 4.441e-16 | 0 | within ±25% |
| F11 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F12 | 1.81792e-08 | 0.917176 | 0.504895 | 9.093e-10 | 0.6876 | 0.6422 | within factor 2 |
| F13 | 9.79381 | 9.88047 | 0.0312111 | 1.024 | 9.58 | 1.616 | within ±25% |

## D = 500

| F | Repro Best | Repro Mean | Repro STD | Paper Best | Paper Mean | Paper STD | Mean agreement |
|---|---:|---:|---:|---:|---:|---:|---|
| F1 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F2 | 0 | 8.1149e-217 | 0 | 0 | 3.513e-211 | 0 | outside factor 2 |
| F3 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F4 | 0 | 5.47363e-207 | 0 | 0 | 1.492e-204 | 0 | outside factor 2 |
| F5 | 498.771 | 498.948 | 0.0705278 | 498.8 | 499 | 0.052 | within ±25% |
| F6 | 124.263 | 124.631 | 0.104877 | 124.2 | 124.6 | 0.1481 | within ±25% |
| F7 | 1.06078e-06 | 0.000100365 | 9.7401e-05 | 4.091e-06 | 8.216e-05 | 6.352e-05 | within ±25% |
| F8 | -209344 | -45452 | 38066.4 | -194400 | -62820 | 51050 | within factor 2 |
| F9 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F10 | 4.44089e-16 | 4.44089e-16 | 0 | 4.441e-16 | 4.441e-16 | 0 | within ±25% |
| F11 | 0 | 0 | 0 | 0 | 0 | 0 | near paper zero |
| F12 | 6.08442e-06 | 1.16099 | 0.219286 | 9.54e-08 | 1.04 | 0.415 | within ±25% |
| F13 | 49.6927 | 49.8763 | 0.0462704 | 28.21 | 49.16 | 3.957 | within ±25% |

## Interpretation rule

`H3c RESULT: PASS` means all 780 source-faithful SCHO runs completed
structurally and the evidence files were generated.

It does **not** mean the reproduced statistics must equal the paper.
Any disagreement is preserved and analyzed in H3d without tuning.

## Full-paper limitation after H3c

Tables 9–12 also require GWO, ALO, SCA, SSA, AOA, RSA, SHO and GJO,
plus Friedman ranking and Wilcoxon rank-sum tests. Those comparator
experiments remain pending after this SCHO-core stage.
