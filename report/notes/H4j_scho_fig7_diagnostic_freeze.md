# H4j — SCHO Fig.7 paper-agreement diagnostic + controlled freeze

## Freeze conclusion

**SCHO FIG.7 CONTROLLED REPRODUCTION COMPLETE; PARTIAL BAR-LEVEL AGREEMENT; NO TUNING.**

`SCHO_FIG7_CONTROLLED_COMPLETE__PARTIAL_BAR_LEVEL_AGREEMENT__NO_TUNING`

The eleven variants remain `CONTROLLED-INTERPRETATION`, not recovered author-source implementations.

## Pairwise comparison

| Variant | Repro SCHO/Variant | Paper SCHO/Variant | Delta | Direction |
|---|---:|---:|---:|---|
| V1 | 14/17 | 18/15 | -4/+2 | REVERSED |
| V2 | 20/14 | 20/13 | +0/+1 | SAME_DIRECTION |
| V3 | 17/17 | 17/15 | +0/+2 | REPRO_TIE |
| V4 | 14/16 | 17/14 | -3/+2 | REVERSED |
| V5 | 19/16 | 17/16 | +2/+0 | SAME_DIRECTION |
| V6 | 15/15 | 18/14 | -3/+1 | REPRO_TIE |
| V7 | 17/15 | 20/13 | -3/+2 | SAME_DIRECTION |
| V8 | 16/17 | 20/11 | -4/+6 | REVERSED |
| V9 | 16/14 | 18/9 | -2/+5 | SAME_DIRECTION |
| V10 | 18/17 | 20/13 | -2/+4 | SAME_DIRECTION |
| V11 | 19/20 | 18/15 | +1/+5 | REVERSED |

## Aggregate diagnostic

- Same paper direction: **5/11**
- Reproduced tie: **2/11**
- Reversed direction: **4/11**
- Exact SCHO bar: **2/11**
- Exact variant bar: **1/11**
- Exact pair: **0/11**
- Both bars within ±2: **3/11**
- Both bars within ±3: **6/11**
- Mean absolute SCHO-count difference: **2.182**
- Mean absolute variant-count difference: **2.727**
- Overall bar-count MAE: **2.455**

Same-direction cases: V2, V5, V7, V9, V10. Reproduced ties: V3, V6. Reversals: V1, V4, V8, V11.

## Tie/overlap diagnostic

H4i records **110** pairwise ties. If the paper bars are interpreted using the same dual-credit convention, their aggregate implied overlap is **98**. This is diagnostic only because the paper does not publish a machine-readable tie-counting rule.

## Interpretation and freeze rule

The disagreement is preserved. Do not change H4h equations, H4i tie tolerance, seeds, or protocol to move the bars toward the paper. A future change requires new primary-source evidence for the author variants and a new version.

With H4c (Fig.8), H4f (Table 5), and H4j (Fig.7), the planned Section 3.1.1–3.1.2 scope is complete with explicit exactness boundaries.

**H4 — COMPLETE WITH CONTROLLED-INTERPRETATION BOUNDARY FOR FIG.7.**