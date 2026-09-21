# H4f — SCHO Table-5 paper-agreement diagnostic and ablation freeze

## Freeze conclusion

> **TABLE-5 STRUCTURAL ABLATION COMPLETE AS A CONTROLLED REPRODUCTION; STRONG RANK-LEVEL AGREEMENT, WITH ONE TIE-STRUCTURE DIFFERENCE.**

The full SCHO control is source-faithful. The five ablations remain `PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION` because separate author variant source files were not recovered.

No parameter tuning is performed.

## Ranking comparison

| Variant | Repro Mean Rank | Paper Mean Rank | Delta | Repro Final Rank | Paper Final Rank | Match |
|---|---:|---:|---:|---:|---:|---|
| SCHO | 1.82609 | 1.65 | +0.17609 | 1 | 1 | MATCH |
| SCHO_NT | 3.08696 | 2.96 | +0.12696 | 3 | 3 | MATCH |
| SCHO_NSTF | 3.17391 | 3.35 | -0.17609 | 4 | 4 | MATCH |
| SCHO_NFTF | 4.56522 | 4.52 | +0.04522 | 6 | 6 | MATCH |
| SCHO_NSF | 2.26087 | 2.13 | +0.13087 | 2 | 2 | MATCH |
| SCHO_NFF | 3.56522 | 3.35 | +0.21522 | 5 | 4 | DIFF |

Final-rank matches: **5/6**.

The only final-rank mismatch is `SCHO_NFF`: reproduced rank 5 versus paper rank 4. In the paper, `SCHO_NSTF` and `SCHO_NFF` both have mean rank 3.35 and share final rank 4; the reproduced means separate them, so the controlled reproduction assigns ranks 4 and 5.

This difference is preserved and must not be tuned away.

## Freeze rule

Do not change the five structural variant definitions merely to reproduce the paper tie. Any future change requires new primary-source evidence and a new version.

## H4f status

**H4f — COMPLETE**

`SCHO_TABLE5_ABLATION_COMPLETE__STRONG_RANK_LEVEL_AGREEMENT__ONE_TIE_DIFFERENCE`

Next: Fig.7 variant source-resolution stage.