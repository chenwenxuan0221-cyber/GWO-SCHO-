# H4i — SCHO Fig.7 controlled 7590-run experiment

## Exactness tier

`CONTROLLED-INTERPRETATION`

The 11 Fig.7 variants use the explicit H4h project-frozen equations.
They are not claimed to be unrecovered author implementations.

## Formal protocol

- Variants: V1–V11
- Functions: F1–F23
- N = 30
- MaxIter = 500
- 30 runs/variant/function
- optimizer seeds = 1000–1029
- objective seeds intentionally identical to H4e
- formal variant runs = 7590
- SCHO baseline reused from H4e = 690 already-completed aligned runs

## Fig.7 counting convention

The paper describes the bars as the number of average optimal solutions
but does not provide a machine-readable counting rule. H4i freezes the
following controlled interpretation:

For each SCHO-vs-variant pair and each function, compare the 30-run
mean final fitness under minimization. The lower mean receives one
credit. If the means are numerically tied under
`np.isclose(rtol=1e-09, atol=1e-12)`, both receive one credit.

This interpretation explains why the two bar counts for one comparison
may sum to more than 23: tied functions are credited to both.

The tie rule is frozen before seeing H4i results and must not be tuned
to reproduce the printed paper counts.

## Pairwise counts

| Variant | Repro SCHO | Repro Variant | Ties | Paper SCHO | Paper Variant |
|---|---:|---:|---:|---:|---:|
| V1 | 14 | 17 | 8 | 18 | 15 |
| V2 | 20 | 14 | 11 | 20 | 13 |
| V3 | 17 | 17 | 11 | 17 | 15 |
| V4 | 14 | 16 | 7 | 17 | 14 |
| V5 | 19 | 16 | 12 | 17 | 16 |
| V6 | 15 | 15 | 7 | 18 | 14 |
| V7 | 17 | 15 | 9 | 20 | 13 |
| V8 | 16 | 17 | 10 | 20 | 11 |
| V9 | 16 | 14 | 7 | 18 | 9 |
| V10 | 18 | 17 | 12 | 20 | 13 |
| V11 | 19 | 20 | 16 | 18 | 15 |

## Paper anchors

- Fig.7(a): V1 = 18/15, V2 = 20/13
- Fig.7(b): V3 = 17/15, V4 = 17/14, V5 = 17/16, V6 = 18/14
- Fig.7(c): V7 = 20/13, V8 = 20/11, V9 = 18/9
- Fig.7(d): V10 = 20/13, V11 = 18/15

## Interpretation boundary

Agreement or disagreement with the paper bars cannot validate or
invalidate the unrecovered author equations, because H4h explicitly
uses controlled substitute formulas for unresolved variants.

No formula or parameter may be adjusted after H4i merely to improve
bar-count agreement.

## Outputs

- `results\raw\scho_fig7_h4i_variant_runs.csv`
- `results\processed\scho_fig7_h4i_variant_summary.csv`
- `results\processed\scho_fig7_h4i_pairwise_by_function.csv`
- `results\processed\scho_fig7_h4i_pairwise_counts.csv`
- `report\figures\scho_fig7a_h4i_controlled.png`
- `report\figures\scho_fig7b_h4i_controlled.png`
- `report\figures\scho_fig7c_h4i_controlled.png`
- `report\figures\scho_fig7d_h4i_controlled.png`

## Next

H4j should audit paper-agreement patterns and freeze Fig.7 as a
controlled interpretation, without tuning.