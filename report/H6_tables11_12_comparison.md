# H6d — SCHO Tables 11/12 Wilcoxon rank-sum reproduction

Protocol: `H6_SCALABILITY_V1`

Test: two-sided Mann–Whitney U / Wilcoxon rank-sum via SciPy `mannwhitneyu`, asymptotic method, continuity correction, alpha=0.05.

This is a project-controlled statistical implementation and is not claimed to reproduce MATLAB `ranksum` bitwise.

Symbol convention: `+` SCHO significantly better, `-` SCHO significantly worse, `~` no significant difference.

Paper comparison below uses the aggregate W|L|T rows printed in Tables 11 and 12.

## D = 100

| Comparator | Reproduced W|L|T | Paper W|L|T | Delta W|L|T | Exact match |
|---|---:|---:|---:|:---:|
| GWO | 8|5|0 | 10|3|0 | -2|+2|+0 | NO |
| ALO | 12|1|0 | 13|0|0 | -1|+1|+0 | NO |
| SCA | 13|0|0 | 13|0|0 | +0|+0|+0 | YES |
| SSA | 12|1|0 | 12|1|0 | +0|+0|+0 | YES |
| AOA | 5|2|6 | 9|1|3 | -4|+1|+3 | NO |
| RSA | 4|3|6 | 5|2|6 | -1|+1|+0 | NO |
| SHO | 7|0|6 | 10|1|2 | -3|-1|+4 | NO |
| GJO | 6|3|4 | 9|3|1 | -3|+0|+3 | NO |

Exact aggregate W|L|T matches: **2/8**.

## D = 500

| Comparator | Reproduced W|L|T | Paper W|L|T | Delta W|L|T | Exact match |
|---|---:|---:|---:|:---:|
| GWO | 9|4|0 | 10|3|0 | -1|+1|+0 | NO |
| ALO | 12|1|0 | 12|1|0 | +0|+0|+0 | YES |
| SCA | 13|0|0 | 13|0|0 | +0|+0|+0 | YES |
| SSA | 12|1|0 | 13|0|0 | -1|+1|+0 | NO |
| AOA | 5|2|6 | 11|1|1 | -6|+1|+5 | NO |
| RSA | 4|3|6 | 5|2|6 | -1|+1|+0 | NO |
| SHO | 7|3|3 | 9|2|2 | -2|+1|+1 | NO |
| GJO | 8|4|1 | 9|4|0 | -1|+0|+1 | NO |

Exact aggregate W|L|T matches: **2/8**.

## Interpretation boundary

- The paper does not publish its random seeds; H6 uses the project reproducibility convention.
- NumPy RNG streams are not MATLAB RNG streams.
- Several comparator implementations are source-structured rather than MATLAB-bitwise reconstructions.
- Therefore aggregate agreement/disagreement is interpreted as reproduction evidence, not as a tuning target.
- No optimizer is modified or rerun by this analysis.
