# H4f protocol — Table-5 agreement diagnostic and freeze

H4f runs no optimizer. It audits the completed H4e evidence (4140 raw rows, 138 summary rows, 138 rank rows), recomputes Mean Rank and Final Rank, compares them with the paper Table-5 anchors, and freezes the result.

Expected current ranking from H4e:
- SCHO: 1.82609 / rank 1
- SCHO_NT: 3.08696 / rank 3
- SCHO_NSTF: 3.17391 / rank 4
- SCHO_NFTF: 4.56522 / rank 6
- SCHO_NSF: 2.26087 / rank 2
- SCHO_NFF: 3.56522 / rank 5

Paper anchors:
- SCHO: 1.65 / rank 1
- SCHO_NT: 2.96 / rank 3
- SCHO_NSTF: 3.35 / rank 4
- SCHO_NFTF: 4.52 / rank 6
- SCHO_NSF: 2.13 / rank 2
- SCHO_NFF: 3.35 / rank 4

The only final-rank difference is the paper's SCHO_NSTF/SCHO_NFF rank-4 tie, which the controlled reproduction separates into ranks 4 and 5. Preserve this difference; do not tune it away.
