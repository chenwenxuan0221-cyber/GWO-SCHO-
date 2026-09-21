# H4h — Explicit controlled equations for SCHO Fig.7 Variants 1–11

## 1. Status

This stage implements **controlled interpretations**, not recovered author
variant source.

Frozen label:

`SCHO_FIG7_VARIANTS__CONTROLLED_INTERPRETATION_V1`

The paper describes the eleven modifications but does not publish enough
formula/code detail to reconstruct all eleven variants uniquely. In particular,
the exact meaning of “same value range” and the alternative switching
equations are not specified. Therefore H4h freezes one transparent convention
before any large experiment.

## 2. Shared rules

All variants preserve the frozen SCHO v3.3 source behavior unless the named
Fig.7 modification requires a change.

Preserved source behaviors include:

- initial population evaluated before t=2;
- per-coordinate switching draw;
- source RNG draw order where possible;
- asymmetric boundary repair;
- zero `Position_sort` second destination;
- bounded-search scheduling and repeated population reinitialization quirk;
- no parameter tuning.

## 3. Range-matching convention

For an argument `x in [0,1]`, the original hyperbolic ranges are:

- `sinh(x): [0, sinh(1)]`
- `cosh(x): [1, cosh(1)]`

### Sine/cosine controlled substitutes

Sinh-shaped replacement:

`S_sin(x) = sinh(1) * sin(x) / sin(1)`

Cosh-shaped replacement:

`C_cos(x) = 1 + (cosh(1)-1) * (1-cos(x)) / (1-cos(1))`

Thus:

- `S_sin(0)=0`, `S_sin(1)=sinh(1)`
- `C_cos(0)=1`, `C_cos(1)=cosh(1)`

The endpoints, monotone direction and value ranges match the original
hyperbolic functions.

### Linear controlled substitutes

`S_lin(x) = sinh(1) * x`

`C_lin(x) = 1 + (cosh(1)-1) * x`

Again, endpoints and ranges match.

This is an H4h project convention. It is **not** claimed to be the unrecovered
author implementation.

## 4. Variant definitions

### V1

Paper description: use the first-phase exploitation equation in both
exploitation phases.

Controlled implementation:

When `t>T` and the switching mechanism chooses exploitation, use the same
Eq.(10)+Eq.(11) structure as first-phase exploitation, evaluated with the
current late-iteration `t`.

### V2

Paper description: remove the second-phase exploitation equation.

Controlled implementation:

When `t>T` and exploitation would select Eq.(12), retain the current coordinate
unchanged for that update. The usual random draws are still consumed so this is
a structural deletion rather than an RNG-shortening optimization.

### V3

In second-phase exploitation Eq.(12), replace sinh/cosh by the range-matched
sine/cosine substitutes above.

### V4

In first-phase exploration Eq.(5), replace sinh/cosh by the range-matched
sine/cosine substitutes above.

### V5

In second-phase exploitation Eq.(12), replace sinh/cosh by the range-matched
linear substitutes above.

### V6

In first-phase exploration Eq.(5), replace sinh/cosh by the range-matched
linear substitutes above.

### V7

Paper description: switching mechanism using sine/cosine.

Because no exact alternate switch equation was recovered, H4h replaces the
**whole deterministic switching envelope** by a smooth sine/cosine schedule
with the same endpoints 10 -> 1:

`g(z) = 0.5 * [cos(pi*z/2) + 1 - sin(pi*z/2)]`

`A = [1 + 9*g(z)] * r_switch`

where `z=t/MaxIter`.

### V8

Paper description: switching mechanism using linear functions.

Controlled whole-envelope replacement:

`A = (10 - 9*z) * r_switch`

This also matches the original envelope endpoints 10 -> 1.

### V9

Paper description: same selection probability for exploration/exploitation.

Controlled implementation:

Use the source switching draw directly:

- exploration if `r_switch > 0.5`
- exploitation otherwise

Thus the two mechanisms have equal probability in both phases.

### V10

Paper description: sine/cosine in Eq.(17).

Unlike V7, this keeps the **Eq.(17) algebraic structure** and substitutes only
the hyperbolic functions inside its exponent:

`A = [p - q * z^(C_cos(z)/S_sin(z))] * r_switch`

### V11

Like V10, but with linear substitutes:

`A = [p - q * z^(C_lin(z)/S_lin(z))] * r_switch`

## 5. Why V7/V8 differ from V10/V11

The paper separately describes:

- V7/V8 as variants with a different switching mechanism;
- V10/V11 as variants using sine/cosine or linear functions **in Eq.(17)**.

Because no author formulas were recovered, H4h freezes a distinction:

- V7/V8 replace the whole deterministic switching envelope;
- V10/V11 retain Eq.(17)'s structure and replace only the function family.

This distinction is explicitly project-controlled.

## 6. H4h test protocol

Smoke anchors:

- F2
- F7
- F15
- F21

Settings:

- N=6
- MaxIter=40
- optimizer seed=1000
- separate deterministic F7 objective seed

Acceptance:

1. full `SCHO` wrapper equals frozen `algorithms/scho.py` exactly;
2. replacement functions match frozen endpoint/range conventions;
3. all 11 variants are deterministic under identical seeds;
4. all outputs are finite and best curves are non-increasing;
5. every intended modified branch is actually exercised;
6. every variant differs from full SCHO on at least one anchor trajectory.

## 7. What H4h does NOT claim

H4h does not claim:

- author-source equivalence for V1–V11;
- MATLAB bitwise equivalence;
- that the controlled formulas reproduce Fig.7 bar counts;
- that matching the bar counts would validate the formulas.

Do not tune these definitions against Fig.7.

## 8. Next stage

If H4h passes, H4i should decide whether to spend the computation on the full
controlled Fig.7 experiment:

`11 variants × 23 functions × 30 runs = 7590 variant runs`

plus an aligned SCHO control if needed.
