# H5b — Comparator source-resolution matrix

## 1. Decision

The seven missing SCHO Section 3.1.3 comparators all have identifiable
author/official MATLAB sources suitable for a source-audited Python translation:

- ALO — Ant Lion Optimizer
- SCA — Sine Cosine Algorithm
- SSA — Salp Swarm Algorithm
- AOA — Arithmetic Optimization Algorithm
- RSA — Reptile Search Algorithm
- SHO — **Sea-Horse Optimizer**
- GJO — Golden Jackal Optimization

No optimizer is implemented in H5b. This stage freezes source identity and
parameter precedence before H5c.

## 2. Critical identity finding: SHO

The SCHO paper reference [109] is:

**S. Zhao, T. Zhang, S. Ma, M. Wang — Sea-horse optimizer.**

Therefore the `SHO` comparator in the SCHO paper is **Sea-Horse Optimizer**.

It is **not** the older **Spotted Hyena Optimizer**, which is also commonly
abbreviated `SHO`.

This acronym collision must be guarded in code, filenames, reports, and tests.

Recommended project filename:

`algorithms/sea_horse_optimizer.py`

Do not name the implementation only `sho.py` unless the module docstring and
tests make the identity unambiguous.

## 3. Source hierarchy

H5 will use this precedence:

1. author-maintained / author-uploaded MATLAB source;
2. original algorithm paper for equations and intent;
3. SCHO paper Table 6 for the parameter values used in the SCHO comparison;
4. third-party implementations only as diagnostics, never as primary truth.

The goal is not to reproduce each comparator's original paper experiment.
The goal is to reproduce **Bai et al.'s SCHO comparison experiment**, so a
Table-6 parameter override is allowed when explicitly documented.

## 4. Per-algorithm freeze

### ALO — Ant Lion Optimizer

Primary source:
Seyedali Mirjalili's MATLAB Central submission for the Ant Lion Optimizer.

Status:

`AUTHOR_SOURCE_RECOVERED`

H5c should translate the author source rather than implement from abbreviated
paper pseudocode.

High-risk details to audit:

- roulette-wheel antlion selection;
- random-walk construction and normalization;
- elite/random-antlion averaging;
- boundary behavior;
- MATLAB random-number consumption/order.

SCHO Table 6 anchor:

`w ∈ {2,...,6}` according to the iteration-dependent random-walk shrinking rule.

### SCA — Sine Cosine Algorithm

Primary source:
Seyedali Mirjalili's MATLAB Central SCA source.

Status:

`AUTHOR_SOURCE_RECOVERED`

SCHO Table 6 anchor:

`a = 2`

Audit:

- exact linear schedule;
- sine/cosine branch threshold;
- independent random draws per coordinate;
- iteration indexing.

### SSA — Salp Swarm Algorithm

Primary source:
Seyedali Mirjalili's MATLAB Central SSA source.

Status:

`AUTHOR_SOURCE_RECOVERED`

SCHO Table 6 explicitly lists `c2,c3 ∈ [0,1]`; the source-defined `c1`
schedule is part of the algorithm and must be retained.

Audit:

- leader vs follower indexing;
- follower averaging order;
- boundary repair;
- evaluation/sort timing;
- c1 schedule.

### AOA — Arithmetic Optimization Algorithm

Primary source:
Laith Abualigah's MATLAB Central submission, which also points to author
GitHub code.

Status:

`AUTHOR_SOURCE_RECOVERED_WITH_PROTOCOL_OVERRIDE`

SCHO Table 6:

- `alpha = 5`
- `u / mu = 0.5`

Important discrepancy:

Many AOA implementations and papers that state they use the original/default
settings report `Mu = 0.499`, whereas the SCHO paper explicitly uses `u=0.5`.

H5 policy:

**Use the author-source algorithm structure but set `mu=0.5` for the SCHO-paper
comparison.**

This must be labelled a `SCHO_TABLE6_PARAMETER_OVERRIDE`, not silently treated
as the original AOA default.

### RSA — Reptile Search Algorithm

Primary source:
Laith Abualigah's MATLAB Central RSA submission; its page also links the author
GitHub repository.

Status:

`AUTHOR_SOURCE_RECOVERED_WITH_PARAMETER_DISCREPANCY_TO_A_PAPER_TEXT`

SCHO Table 6:

- `alpha = 0.1`
- `beta = 0.005`

Audit finding:

An accessible copy of the original RSA paper contains an experimental-setting
passage that states `beta=0.1`, while the SCHO paper uses `beta=0.005` and
`0.005` is also widely reported as the canonical implementation value.

H5 policy:

Because H5 is reproducing the **SCHO comparison**, use:

`alpha=0.1, beta=0.005`

while preserving the discrepancy in documentation. H5c must still inspect the
author MATLAB source line-by-line before freezing the Python port.

### SHO — Sea-Horse Optimizer

Primary source:
S. Zhao's MATLAB Central submission.

Status:

`AUTHOR_SOURCE_RECOVERED`

The submission has historical versions beginning with v1.0.0 on 6 Aug 2022.
Later visible release notes are citation/paper-statement updates, so H5c should
prefer the earliest recoverable algorithm source and compare later versions
before choosing a frozen source snapshot.

SCHO Table 6:

- `r1` cut-off point = 0
- success probability `r2 = 0.1`

These settings are consistent with the Sea-Horse optimizer's movement and
predation description.

Again:

**This is Sea-Horse Optimizer, not Spotted Hyena Optimizer.**

### GJO — Golden Jackal Optimization

Primary source:
Nitish Chopra's MATLAB Central submission containing:

- `GJO.m`
- `levy.m`
- `initialization.m`
- benchmark/main helpers

Status:

`AUTHOR_SOURCE_RECOVERED`

SCHO Table 6:

- `c1 = 1.5`
- Levy exponent `beta = 1.5`

Audit:

- male/female best bookkeeping;
- prey update equations;
- Levy-flight constants and random draws;
- evaluation/update timing.

## 5. Implementation exactness labels for H5c

A comparator may receive `SOURCE-FAITHFUL PYTHON TRANSLATION` only after:

1. its selected MATLAB source snapshot is archived/audited;
2. every source random draw and update order is mapped;
3. boundary behavior is mapped;
4. benchmark-independent smoke tests pass;
5. no unexplained "cleanup" or algorithm repair is introduced.

For AOA and RSA, distinguish:

- **algorithm/source structure fidelity**, and
- **SCHO Table-6 parameter protocol**.

A parameter override does not invalidate the translation, but it prevents a
claim that the run uses the comparator paper's untouched default protocol.

## 6. H5c implementation order

Recommended order, from simplest/lowest-risk to more source-sensitive:

1. SCA
2. SSA
3. GJO
4. AOA
5. RSA
6. ALO
7. Sea-Horse Optimizer

H5c should still be performed one comparator at a time with exact structural
tests before moving to the next.

## 7. H5b status

**H5b — COMPLETE AS A SOURCE-RESOLUTION AUDIT.**

Frozen source policy:

`AUTHOR_SOURCE_FIRST__SCHO_TABLE6_PARAMETER_PRECEDENCE_FOR_H5`

Next:

**H5c1 — implement and test SCA only.**
