# H5g — SCHO Table 8 Wilcoxon rank-sum reproduction

Protocol: `H5_CLASSICAL_V1`; 30 final-best scores per algorithm/function; alpha = 0.05.

Statistical implementation: two-sided Mann–Whitney U / Wilcoxon rank-sum via SciPy `mannwhitneyu`, asymptotic method with continuity correction. This is a project-controlled statistical implementation and does not claim bitwise MATLAB `ranksum` equivalence.

Symbols: `+` = SCHO significantly better, `-` = SCHO significantly worse, `~` = no significant difference.

| Comparator | Reproduced W|L|T | Paper W|L|T | ΔW | ΔL | ΔT |
|---|---:|---:|---:|---:|---:|
| GWO | 12|5|6 | 12|8|3 | +0 | -3 | +3 |
| ALO | 14|6|3 | 14|6|3 | +0 | +0 | +0 |
| SCA | 23|0|0 | 21|2|0 | +2 | -2 | +0 |
| SSA | 13|8|2 | 18|5|0 | -5 | +3 | +2 |
| AOA | 15|0|8 | 18|2|3 | -3 | -2 | +5 |
| RSA | 13|1|9 | 11|2|10 | +2 | -1 | -1 |
| SHO | 19|0|4 | 13|3|7 | +6 | -3 | -3 |
| GJO | 17|1|5 | 14|3|6 | +3 | -2 | -1 |

No parameter tuning or post-hoc threshold adjustment is performed to force the reproduced W|L|T counts toward the paper anchors.
