# H5f — SCHO Table 7 reproduction comparison

Protocol: `H5_CLASSICAL_V1`; F1–F13 D=30; F14–F23 native dimension; N=30; MaxIter=500; 30 runs/function.

Statistics: Best, arithmetic Mean, and sample STD (`ddof=1`, aligned with MATLAB `std` default). Per-function ranking uses Mean ascending with average-rank ties.

The paper values below are the Table 7 anchors frozen during the H5 audit. They are comparison anchors, not values recomputed from the paper inside this script.

| Algorithm | Reproduced mean rank | Paper mean rank | Delta | Reproduced final rank | Paper final rank |
|---|---:|---:|---:|---:|---:|
| SCHO | 2.86957 | 2.48 | +0.38957 | 1 | 1 |
| GWO | 4.08696 | 3.78 | +0.30696 | 2 | 3 |
| GJO | 4.21739 | 3.74 | +0.47739 | 3 | 2 |
| RSA | 4.60870 | 4.57 | +0.03870 | 4 | 5 |
| SSA | 4.65217 | 4.83 | -0.17783 | 5 | 6 |
| ALO | 5.47826 | 5.43 | +0.04826 | 6 | 7 |
| AOA | 5.60870 | 5.83 | -0.22130 | 7 | 8 |
| SHO | 6.13043 | 4.00 | +2.13043 | 8 | 4 |
| SCA | 7.34783 | 7.39 | -0.04217 | 9 | 9 |

## Rank-order view

- Reproduced order: `SCHO, GWO, GJO, RSA, SSA, ALO, AOA, SHO, SCA`
- Paper anchor order: `SCHO, GJO, GWO, SHO, RSA, SSA, ALO, AOA, SCA`

Interpretation must distinguish rank-level agreement from exact numerical agreement. No parameter tuning is performed to force reproduced ranks toward the paper.
