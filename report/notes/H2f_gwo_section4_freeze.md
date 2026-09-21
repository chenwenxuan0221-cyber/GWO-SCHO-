# H2f — GWO Section 4 figures / experiment coverage freeze

## 1. Freeze conclusion

GWO Section 4 is now covered at the project's declared reproduction tiers.

This does **not** mean every published number and pixel has been reproduced
exactly. The correct freeze statement is:

> **GWO Section 4 paper-structure coverage is complete.**
> Classic landscapes are reproduced in paper style; the recovered SIS2005
> source is used for the composite suite; F24-F29 numerical reproduction was
> completed but showed partial agreement with Table 8; Fig.10 and Fig.11 are
> explicitly controlled-equivalent where the original unpublished visualization
> instance / shift protocol could not be recovered.

Do not rewrite or tune previous raw evidence to improve agreement.

---

## 2. H2d — Fig.7–Fig.10 status

### Fig.7 — F1–F7
Status: **COMPLETE_PAPER_STYLE**

Generated:
`report/figures/gwo_fig7_unimodal_landscapes.png`

Seven functions plotted successfully.

Important display note:
F7 contains a stochastic noise term; its visualization uses a fixed RNG so the
surface is reproducible.

### Fig.8 — F8–F13
Status: **COMPLETE_PAPER_STYLE**

Generated:
`report/figures/gwo_fig8_multimodal_landscapes.png`

Six functions plotted successfully.

### Fig.9 — F14 / F16 / F17 / F18
Status: **COMPLETE_PAPER_STYLE**

Generated:
`report/figures/gwo_fig9_fixed_multimodal_landscapes.png`

Four functions plotted successfully.

### Fig.10 — F24–F29 / CF1–CF6
Status: **COMPLETE_CONTROLLED_EQUIVALENT**

Generated:
`report/figures/gwo_fig10_composite_landscapes.png`

The recovered SIS2005 source generates fresh orthogonal matrices for D != 10,
and the historical D=2 matrix realization used for the published visualization
was not recovered. The project therefore uses the H1 source-faithful D=10
instance and plots a first-two-coordinate slice through the first component
optimum.

This preserves the recovered benchmark instance rather than inventing a new
D=2 rotation and incorrectly calling it exact.

---

## 3. H1 — Section 4.3 / Table 8 status

Status:

`COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT`

Protocol:
- F24–F29 / CF1–CF6
- D=10
- N=30
- MaxIter=500
- 30 runs/function
- source-faithful SIS2005 benchmark assets
- frozen GWO
- seeds 1000–1029 as project reproducibility convention

Observed mean agreement:
- F28: within ±25% of paper
- F25: within factor 2
- F24/F26/F27/F29: outside factor 2

The mismatch is preserved as a reproduction result.

Special source discrepancy remains frozen:
- GWO Table 4 prints F26/CF3 as ten Griewank components.
- The recovered original `SIS_novel_func.m` implements ten Rastrigin components.
- Primary project definition remains source-faithful Rastrigin.
- The paper-table version remains diagnostic only.

---

## 4. H2e — Section 4.4 / Fig.11 status

Status:

`COMPLETE_CONTROLLED_EQUIVALENT`

Paper-structure elements reproduced:
- functions F1, F7, F9, F10, F14, F18, F26, F29
- 6 search agents
- 100 iterations
- shifted benchmark functions
- landscape
- search history
- parameter `a`
- first-agent first-dimension trajectory
- fitness history
- convergence curve

Generated:
- `report/figures/gwo_fig11_part1_F1_F7_F9.png`
- `report/figures/gwo_fig11_part2_F10_F14_F18_F26_F29.png`
- `report/figures/gwo_fig11_all8.png`

Raw histories:
- 8 `.npz` files under `results/raw/`

Processed:
- `results/processed/gwo_h2e_fig11_summary.csv`
- `results/processed/gwo_h2e_fig11_manifest.csv`

### Controlled-equivalent conventions

Because the public paper/source record did not recover the exact Fig.11 shift
vectors, seed or internal history-logging semantics, H2e freezes:

- shift target = 65% of each coordinate's original search interval;
- native benchmark dimensions retained;
- GWO seed = 1000;
- H2b evaluated-population history sampling;
- fitness history = mean fitness of the six evaluated agents.

These conventions are explicit and must remain labeled as project conventions.

---

## 5. H2e visual audit

The generated Fig.11-style figures are structurally readable and contain all
six required panel types for all eight functions.

Observed qualitative behavior:

- Parameter `a` decreases linearly from approximately 2 to 0 in every row.
- Search histories contain broad early exploration and later concentration,
  but the degree of convergence varies strongly by function.
- F18 converges essentially onto the controlled shifted target
  (`distance ≈ 9e-4`).
- F1, F7, F9, F10, F14, F26 and F29 do not end at the controlled shifted
  optimum under the single N=6 / 100-iteration run.
- F29 is especially far from the shifted target and remains near a high
  objective level, consistent with the difficulty already observed in H1.
- The convergence curves remain historical-best curves and are non-increasing.

These are reproduction observations, not defects to tune away.

The purpose of Section 4.4 is qualitative behavior visualization. H2e should
therefore not be converted into a parameter-tuning exercise merely because
some controlled-equivalent runs do not locate the shifted optimum.

---

## 6. Exactness boundary

| Artifact | Freeze tier |
|---|---|
| Fig.7 | COMPLETE_PAPER_STYLE |
| Fig.8 | COMPLETE_PAPER_STYLE |
| Fig.9 | COMPLETE_PAPER_STYLE |
| Fig.10 | COMPLETE_CONTROLLED_EQUIVALENT |
| F24–F29 / Table 8 run | COMPLETE_SOURCE_FAITHFUL_ATTEMPT__PARTIAL_NUMERICAL_AGREEMENT |
| Fig.11 | COMPLETE_CONTROLLED_EQUIVALENT |

Therefore do **not** describe GWO Section 4 as:

> pixel-exact / numerically exact full reproduction.

Use:

> GWO Section 4 has complete paper-structure coverage, with source-faithful
> benchmark recovery where available and explicit controlled-equivalent
> protocols where original visualization details were unavailable.

---

## 7. Files that remain frozen

Do not modify to improve agreement:
- `algorithms/gwo.py`
- `algorithms/scho.py`
- `benchmarks/gwo_sis2005.py`
- H1 SIS2005 source assets
- H1e raw 30-run results
- H2b history instrumentation protocol
- H2c shifted benchmark protocol
- H2d generated evidence
- H2e generated histories/results

Future corrections, if supported by new primary-source evidence, should be
added as new versions rather than overwriting this evidence trail.

---

## 8. Stage transition

H2 is complete after this freeze.

Recommended next full-paper stage:

**H3 — SCHO Section 3.1.4 scalability analysis (D=100 and D=500)**

Before running the large experiment, H3 should begin with a protocol/source
audit of the exact functions, dimensions, runs, N, MaxIter, statistics and
comparison scope.
