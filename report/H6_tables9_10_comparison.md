# H6c - SCHO Tables 9/10 scalability reproduction

Protocol: `H6_SCALABILITY_V1`

Statistics: Best=min, Average=arithmetic mean, STD=sample standard deviation (ddof=1).

Ranking: per-function rank by Average ascending; exact ties use average ranks; MeanRank is the average over F1-F13.

Paper mean-rank values are validation anchors only and were not used to tune any algorithm.

## D = 100

| Algorithm | Reproduced Mean Rank | Paper Mean Rank | Delta | Reproduced Final Rank | Paper Final Rank | Match |
|---|---:|---:|---:|---:|---:|:---:|
| SCHO | 2.84615 | 1.85 | +0.99615 | 1 | 1 | YES |
| RSA | 3.38462 | 2.85 | +0.53462 | 2 | 2 | YES |
| AOA | 3.69231 | 4.77 | -1.07769 | 3 | 6 | NO |
| SHO | 3.92308 | 3.31 | +0.61308 | 4 | 3 | NO |
| GJO | 4.00000 | 4.00 | +0.00000 | 5 | 4 | NO |
| GWO | 4.23077 | 4.15 | +0.08077 | 6 | 5 | NO |
| SSA | 6.61538 | 6.54 | +0.07538 | 7 | 7 | YES |
| ALO | 7.61538 | 7.69 | -0.07462 | 8 | 8 | YES |
| SCA | 8.69231 | 8.69 | +0.00231 | 9 | 9 | YES |

Reproduced order: `SCHO, RSA, AOA, SHO, GJO, GWO, SSA, ALO, SCA`

Paper order: `SCHO, RSA, SHO, GJO, GWO, AOA, SSA, ALO, SCA`

Friedman test across the 13 function-level Average values:

- statistic = `62.5531914894`
- p-value = `1.4673494939e-10`
- alpha = `0.05`
- reject equal-performance null = `True`

## D = 500

| Algorithm | Reproduced Mean Rank | Paper Mean Rank | Delta | Reproduced Final Rank | Paper Final Rank | Match |
|---|---:|---:|---:|---:|---:|:---:|
| SCHO | 3.00000 | 2.00 | +1.00000 | 1 | 1 | YES |
| RSA | 3.23077 | 2.54 | +0.69077 | 2 | 2 | YES |
| AOA | 3.38462 | 5.31 | -1.92538 | 3 | 6 | NO |
| SHO | 3.61538 | 3.38 | +0.23538 | 4 | 3 | NO |
| GJO | 4.30769 | 4.00 | +0.30769 | 5 | 4 | NO |
| GWO | 4.76923 | 4.62 | +0.14923 | 6 | 5 | NO |
| SSA | 6.69231 | 6.69 | +0.00231 | 7 | 7 | YES |
| ALO | 7.46154 | 7.54 | -0.07846 | 8 | 8 | YES |
| SCA | 8.53846 | 8.23 | +0.30846 | 9 | 9 | YES |

Reproduced order: `SCHO, RSA, AOA, SHO, GJO, GWO, SSA, ALO, SCA`

Paper order: `SCHO, RSA, SHO, GJO, GWO, AOA, SSA, ALO, SCA`

Friedman test across the 13 function-level Average values:

- statistic = `59.6745406824`
- p-value = `5.39898528251e-10`
- alpha = `0.05`
- reject equal-performance null = `True`

## Scope

H6c does not rerun any optimizer. It analyzes the frozen H6b 7020-row raw dataset only.

Next: H6d Tables 11/12 two-sided Wilcoxon rank-sum analysis.
