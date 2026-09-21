# H4g — SCHO Fig.7 source-resolution decision

## 1. Goal

Resolve whether the eleven additional Fig.7 variants can be reproduced as
source-faithful implementations before launching the formal 23-function,
30-run experiment.

This stage runs **no optimizer**.

## 2. Primary paper evidence

The paper describes eleven variants in Section 3.1.1:

- Variant 1: use the first exploitation-phase equation in both exploitation phases.
- Variant 2: remove the second exploitation-phase equation.
- Variants 3–4: replace selected sinh/cosh terms with sine/cosine having the
  same value range.
- Variants 5–6: replace selected sinh/cosh terms with linear functions having
  the same value range.
- Variant 7: use a sine/cosine switching mechanism.
- Variant 8: use a linear-function switching mechanism.
- Variant 9: use equal selection probability for exploration/exploitation.
- Variant 10: use sine/cosine in Eq. (17).
- Variant 11: use linear functions in Eq. (17).

The Fig.7 bar counts are evidence targets, not tuning targets.

## 3. Public source search

The official MATLAB Central File Exchange entry for **A Sinh Cosh Optimizer**
currently exposes the general SCHO submission and version history through
v3.3. The already-audited project copy of the official v3.3 implementation
contains the main SCHO implementation but no separately recovered Fig.7
variant implementations.

Targeted public-web searches were also performed for names/phrases such as:

- `SCHO_NSTF`
- `SCHO_NFF`
- `SCHO_NSF`
- SCHO `Variant 1` / `Variant 11`
- the paper title plus source-code / GitHub terms

No author-provided source for the eleven Fig.7 variants was recovered.

This is a **non-recovery statement**, not proof that no such source has ever
existed.

## 4. Exactness decision

### Variant 1 and Variant 9

The paper-level intent is relatively clear, but the author's exact variant
code and random-number consumption are not available.

Classification:

`PAPER-DESCRIBED / CONTROLLED-INTERPRETATION`

### Variant 2

The deletion is stated, but the paper does not explicitly specify what the
implementation does after the phase boundary when exploitation is selected
and the second exploitation equation is removed.

Classification:

`PAPER-DESCRIBED / CONTROLLED-INTERPRETATION`

### Variants 3–8 and 10–11

The paper does not print the exact sine/cosine or linear replacement formulae
that realize the phrase **same value range**, nor the exact alternative
switching equations.

Classification:

`FORMULA-UNRESOLVED / CONTROLLED-INTERPRETATION ONLY`

## 5. Freeze rule

Do **not** invent replacement formulae and call them source-faithful.

Do **not** tune formulae against the printed Fig.7 bar heights.

Do **not** alter frozen `algorithms/scho.py`.

If Fig.7 is continued without new primary-source code, the next stage must:

1. define every controlled replacement equation explicitly;
2. state the mathematical range-matching convention;
3. unit-test the eleven branches;
4. label the full experiment `CONTROLLED-INTERPRETATION`;
5. preserve disagreements with the paper rather than tuning them away.

## 6. Paper Fig.7 anchors

The paper visually reports the following SCHO/variant counts of average
optimal solutions:

- Fig.7(a): V1 = 18/15, V2 = 20/13
- Fig.7(b): V3 = 17/15, V4 = 17/14, V5 = 17/16, V6 = 18/14
- Fig.7(c): V7 = 20/13, V8 = 20/11, V9 = 18/9
- Fig.7(d): V10 = 20/13, V11 = 18/15

These counts are comparison anchors only.

## 7. Workload if continued

Eleven additional variants:

`11 × 23 × 30 = 7590` formal variant runs.

The SCHO comparison bars can be reused from the already completed full-SCHO
evidence only if the protocol/objective-seed convention is explicitly aligned;
otherwise SCHO must be rerun under the frozen Fig.7 protocol.

## 8. H4g decision

**SOURCE-FAITHFUL FIG.7 REPRODUCTION IS NOT CURRENTLY JUSTIFIED.**

Frozen label:

`SCHO_FIG7_SOURCE_NOT_RECOVERED__CONTROLLED_INTERPRETATION_REQUIRED`

Next stage:

**H4h — freeze explicit controlled Fig.7 equations and unit-test all eleven
variants before any 7590-run formal experiment.**
