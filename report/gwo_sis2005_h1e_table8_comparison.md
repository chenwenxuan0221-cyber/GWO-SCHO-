# H1e — GWO SIS2005 F24–F29 30-run reproduction

## Protocol

- Benchmark: source-faithful SIS2005 CF1–CF6 (`source_faithful`)
- Paper aliases: F24–F29
- Dimension: 10
- Bounds: [-5, 5]^10
- Population: 30
- MaxIter: 500
- Runs: 30 per function
- Seeds: 1000–1029 (project reproducibility convention; paper does not report seeds)
- Primary STD for paper comparison: sample STD (`ddof=1`)

## Table 8 comparison

| Function | Repro Best | Repro Mean | Repro STD | Paper Mean | Paper STD | Mean ratio | Mean agreement |
|---|---:|---:|---:|---:|---:|---:|---|
| F24 / CF1 | 0.4716025785 | 106.3177215 | 100.4223749 | 43.83544 | 69.86146 | 2.4254 | outside factor 2 |
| F25 / CF2 | 15.43258194 | 163.0810821 | 86.81494187 | 91.80086 | 95.5518 | 1.7765 | within factor 2 |
| F26 / CF3 | 113.1079031 | 221.9662581 | 108.93687 | 61.43776 | 68.68816 | 3.6129 | outside factor 2 |
| F27 / CF4 | 234.5502229 | 395.2386121 | 138.1911072 | 123.1235 | 163.9937 | 3.2101 | outside factor 2 |
| F28 / CF5 | 1.682107386 | 100.6648558 | 140.1317776 | 102.1429 | 81.25536 | 0.9855 | within ±25% |
| F29 / CF6 | 501.2529949 | 847.2115721 | 138.3928447 | 43.14261 | 84.48573 | 19.6375 | outside factor 2 |

## Mechanical summary

- Mean within ±25% of paper: 1/6
- Mean within factor 2 of paper: 2/6

These counts are descriptive diagnostics only. They are not used to tune
the optimizer or benchmark implementation.

## Source discrepancy reminder

F26/CF3 in the uploaded original `SIS_novel_func.m` uses ten Rastrigin
components, whereas GWO Table 4 prints ten Griewank components. H1e uses
the source-faithful Rastrigin definition. The paper-table definition remains
a diagnostic variant and is not silently substituted.

## Interpretation rule

H1e completion establishes the 30-run evidence set. Agreement or disagreement
with Table 8 must be interpreted afterward without parameter tuning.
