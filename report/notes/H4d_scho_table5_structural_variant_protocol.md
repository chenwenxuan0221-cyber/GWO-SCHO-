# H4d — SCHO Table-5 structural variant protocol

## Goal

Implement and validate the five structural ablations used in SCHO paper
Table 5, without modifying the frozen source-faithful implementation:

`algorithms/scho.py`

H4d is a structural smoke/equivalence stage only. It does not run the formal
30-run Table-5 experiment.

## Paper-defined four subordinate models

The paper defines:

1. exploration;
2. exploitation;
3. bounded-search strategy;
4. switching mechanism.

The Table-5 models are frozen as:

| Variant | Exploration | Exploitation | Bounded search | Switching |
|---|---:|---:|---:|---:|
| SCHO | yes | yes | yes | yes |
| SCHO_NT | yes | yes | no | yes |
| SCHO_NSTF | yes | no | no | no |
| SCHO_NFTF | no | yes | no | no |
| SCHO_NSF | yes | no | yes | no |
| SCHO_NFF | no | yes | yes | no |

## Exactness boundary

The original paper gives explicit structural definitions for these five
ablations, but the audited official package did not provide separate variant
source files.

Therefore:

- the full `SCHO` mode is required to reproduce frozen `algorithms/scho.py`
  exactly;
- retained equations and retained bounded-search behavior preserve the frozen
  source-faithful implementation, including its known quirks;
- deletion semantics for the five ablations are labeled
  `PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION`;
- no claim is made that the authors' unrecovered variant source consumed random
  numbers in exactly the same order.

## No-switch interpretation

When the switching mechanism is removed:

- Eq. (17) is not evaluated;
- no switching random draw is consumed;
- if exploration is retained, the first exploration equation is used for
  `t <= T` and the second exploration equation for `t > T`;
- if exploitation is retained, the first exploitation equation is used for
  `t <= T` and the second exploitation equation for `t > T`.

Within each retained phase, the frozen source's `r2/r3/r4/r5` draw pattern is
preserved.

## No-bounded-search interpretation

When subordinate model 3 is removed:

- the dynamic bounded interval remains equal to the original problem bounds;
- no population redistribution is performed;
- the source's second-solution / bounded-search scheduling block is skipped.

## H4d validation protocol

Smoke settings:

- anchors: F2, F7, F15, F21
- N = 6
- MaxIter = 40
- optimizer seed = 1000
- deterministic per-function objective seed

The anchors cover:

- 30-D deterministic benchmark;
- 30-D stochastic F7;
- 4-D fixed benchmark F15;
- 4-D fixed multimodal F21.

### Required checks

1. Full-SCHO control must have exact equality with frozen `scho()` for:
   - best score;
   - best position;
   - complete convergence curve.

2. Every structural variant must:
   - return finite outputs;
   - produce the correct shapes;
   - return a non-increasing historical-best curve;
   - be exactly reproducible for identical seeds.

3. Structural branch counters must reflect the paper-defined deletion:
   - SCHO_NT: no bounded-search redistribution;
   - SCHO_NSTF: exploration only;
   - SCHO_NFTF: exploitation only;
   - SCHO_NSF: exploration + bounded search;
   - SCHO_NFF: exploitation + bounded search.

## H4d local acceptance result

The prepared implementation was tested against the frozen project copy and
passed:

`H4d RESULT: PASS`

The full-SCHO control was exactly equal on F2, F7, F15 and F21.

All five variants were deterministic and structurally distinct.

## Next stage

H4e formal Table-5 reproduction:

- 6 models total;
- F1-F23;
- N=30;
- MaxIter=500;
- 30 independent runs/model/function;
- 4140 optimizer runs;
- checkpoint/resume;
- Best / Average / sample STD;
- rank / mean-rank comparison against paper Table 5.

Any disagreement must be preserved rather than tuned away.
