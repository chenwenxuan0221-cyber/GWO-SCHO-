# H1f — GWO SIS2005 F24–F29 post-run diagnostic

## 1. Purpose

This stage analyzes the completed H1e evidence without changing the optimizer,
benchmark implementation, seeds, or protocol.

H1e completed all 180 runs structurally, but its Table-8 numerical agreement is
mixed. H1f diagnoses the shape of that mismatch instead of tuning it away.

## 2. H1e status

Protocol:
- source-faithful SIS2005 CF1–CF6
- D=10
- bounds [-5,5]
- N=30
- MaxIter=500
- 30 runs/function
- seeds 1000–1029
- total 180 GWO runs

H1e structural status: **PASS**

Numerical status versus GWO Table 8: **PARTIAL / NOT FULLY REPRODUCED**

## 3. Distribution diagnostic

The “nearest bias” column is a descriptive bucket only. The SIS2005 composition
construction has component bias levels 0,100,...,900, so a final score near one
of these levels is consistent with convergence around a corresponding
composition component. It is **not** proof of the exact final basin.

| Function | Best | Median | Mean | Paper mean | Mean ratio | Runs <= paper mean | Nearest 100-level buckets |
|---|---:|---:|---:|---:|---:|---:|---|
| F24 | 0.471603 | 101.052971 | 106.317721 | 43.835440 | 2.4254 | 12/30 | 0:12, 100:7, 200:9, 300:2 |
| F25 | 15.432582 | 162.760379 | 163.081082 | 91.800860 | 1.7765 | 5/30 | 0:2, 100:12, 200:14, 300:1, 400:1 |
| F26 | 113.107903 | 199.103393 | 221.966258 | 61.437760 | 3.6129 | 0/30 | 100:6, 200:16, 300:6, 400:1, 700:1 |
| F27 | 234.550223 | 328.543111 | 395.238612 | 123.123500 | 3.2101 | 0/30 | 200:2, 300:15, 400:6, 500:2, 600:3, 700:2 |
| F28 | 1.682107 | 16.335792 | 100.664856 | 102.142900 | 0.9855 | 18/30 | 0:17, 100:4, 200:7, 500:2 |
| F29 | 501.252995 | 903.357027 | 847.211572 | 43.142610 | 19.6375 | 0/30 | 500:4, 800:1, 900:25 |

## 4. Key observations

### F24 / CF1

The run distribution is genuinely multi-basin:
- 12/30 results fall nearest the 0-level,
- 7/30 near 100,
- 9/30 near 200,
- 2/30 near 300.

The optimizer can reach the low-value region, but not often enough to reproduce
the paper mean. This looks different from a simple objective-function failure.

### F25 / CF2

The distribution is concentrated mainly around the 100 and 200 levels.
Only 5/30 runs are at or below the paper's reported mean.

The reproduced mean is within a factor of two of the paper, and the reproduced
STD is of similar magnitude, but the mean remains substantially higher.

### F26 / CF3

This is a special case because the benchmark definition itself has a documented
source discrepancy:
- GWO Table 4 prints ten Griewank components.
- The uploaded original `SIS_novel_func.m` uses ten Rastrigin components.

H1e intentionally used the source-faithful Rastrigin definition.

More importantly, **0/30** source-faithful runs reached the paper mean, and the
best reproduced result (113.107903) is still worse than the paper mean
(61.437760). Therefore F26 cannot be called numerically reproduced.

The source/table discrepancy is a plausible contributor, but it must not be
used to explain the other functions.

### F27 / CF4

All 30 reproduced runs are worse than the paper mean. The best reproduced value
(234.550223) is almost twice the paper mean (123.123500).

Because F27 has no F26-style Table-4/source component-family discrepancy, this
shows that the H1e disagreement is broader than the F26 typo alone.

### F28 / CF5

This is the strongest match:
- reproduced mean = 100.664856
- paper mean = 102.142900
- mean ratio = 0.9855

However, the reproduced sample STD (140.131778) is materially larger than the
paper STD (81.255360), so even F28 is not a full distribution-level match.

### F29 / CF6

This is the clearest failure mode:
- 25/30 runs finish nearest the 900-level,
- 4/30 near 500,
- 1/30 near 800,
- 0/30 at or below the paper mean.

The best reproduced result (501.252995) is more than an order of magnitude above
the paper mean (43.142610).

This is consistent with strong trapping around high-bias composition regions
under the present source-faithful benchmark + frozen GWO implementation.

## 5. What the evidence does and does not establish

The evidence establishes:
1. The H1e runner worked structurally.
2. The mismatch is systematic, not just one anomalous function.
3. F28 mean agrees closely with Table 8.
4. F26 has a genuine paper-table/source definition discrepancy.
5. F29 exhibits a very strong high-bias trapping pattern.
6. F26, F27, and F29 did not produce even one run as low as the paper mean.

The evidence does **not** establish a single root cause.

Possible unresolved sources include:
- unreleased experimental details used for Table 8,
- benchmark-instance/source-version differences,
- MATLAB-vs-NumPy random-stream effects,
- historical GWO implementation differences,
- the documented F26 Table-4/source inconsistency.

No one of these should be asserted as the cause without additional evidence.

## 6. H1 final status

Recommended freeze status:

**H1 — COMPLETE AS A SOURCE-FAITHFUL REPRODUCTION ATTEMPT; PARTIAL NUMERICAL AGREEMENT**

More explicitly:

> The original SIS2005 source assets were recovered and ported deterministically.
> The frozen GWO was then run for 30 trials on all F24–F29. The formal experiment
> completed, but only F28 reproduced the paper mean within ±25%; F25 was within
> a factor of two, while F24, F26, F27, and F29 were outside a factor of two.
> The mismatch is preserved as a reproduction result and is not tuned away.

## 7. Recommended project decision

Do not modify:
- `algorithms/gwo.py`
- the source-faithful SIS2005 benchmark
- the completed H1e raw results

Do not rerun arbitrary parameter sweeps to force agreement.

Keep `paper_table4` for F26 as a labeled diagnostic variant only.

Proceed to GWO Section 4.4 after freezing H1. A future appendix may investigate
historical benchmark/GWO versions if exact Table-8 archaeology becomes a
separate research objective.
