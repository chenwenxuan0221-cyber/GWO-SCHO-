# H3d — SCHO scalability core diagnostic and freeze

## 1. Freeze conclusion

H3c completed all **780/780** formal source-faithful SCHO runs.

H3d freezes the result as:

> **SCHO Section 3.1.4 scalability core — COMPLETE AS A SOURCE-FAITHFUL REPRODUCTION ATTEMPT; STRONG MEAN-LEVEL AGREEMENT WITH SOME BEST/STD DISTRIBUTION DIFFERENCES.**

This is the SCHO-only core of Tables 9 and 10. It is **not yet** the complete
nine-algorithm Tables 9–12 reproduction.

No parameter tuning is justified or performed.

---

## 2. Evidence basis

Formal project protocol:

- F1–F13
- D = 100 and D = 500
- N = 30
- MaxIter = 500
- 30 runs/function/dimension
- seeds 1000–1029 as a project reproducibility convention
- frozen source-faithful `algorithms/scho.py`
- H3b dimension adapter
- F7 stochastic objective retained with a separate objective RNG stream

The uploaded H3c terminal log contains all 780 completed run scores and ends
with `H3c RESULT: PASS`.

This H3d diagnostic reconstructs Best / Mean / sample STD directly from those
780 logged final scores. The user-side H3c runner has also already generated:

- `results/raw/scho_scalability_h3c_runs.csv`
- `results/processed/scho_scalability_h3c_summary.csv`
- `report/scho_scalability_h3c_tables9_10_comparison.md`

---

## 3. Mean-level agreement summary

A scale-aware rule is used.

For values where both the reproduced and paper means have magnitude <= 1e-12,
the result is classified as `NEAR_ZERO_AGREEMENT`; ratios of quantities such as
1e-249 are not treated as scientifically meaningful.

### D = 100

- near-zero agreement: 7/13
- within ±25%: 4/13
- within factor 2 but outside ±25%: 2/13
- outside factor 2: 0/13

Thus all 13 functions are either in the same near-zero regime or within a
factor of two at the mean level.

### D = 500

- near-zero agreement: 7/13
- within ±25%: 5/13
- within factor 2 but outside ±25%: 1/13
- outside factor 2: 0/13

Again, all 13 functions are either in the same near-zero regime or within a
factor of two at the mean level.

---

## 4. D = 100 detailed comparison

| F | Repro Best | Repro Mean | Repro STD | Paper Best | Paper Mean | Paper STD | Mean class |
|---|---:|---:|---:|---:|---:|---:|---|
| F1 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F2 | 0 | 4.27115e-262 | 0 | 0 | 7.576e-263 | 0 | NEAR_ZERO_AGREEMENT |
| F3 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F4 | 0 | 6.35646e-251 | 0 | 0 | 4.243e-249 | 0 | NEAR_ZERO_AGREEMENT |
| F5 | 98.7709 | 98.8922 | 0.0943624 | 98.75 | 98.87 | 0.1004 | WITHIN_25_PERCENT |
| F6 | 0.236477 | 12.6674 | 8.08345 | 0.0001466 | 8.562 | 8.137 | WITHIN_FACTOR_2 |
| F7 | 1.81152e-06 | 7.19389e-05 | 7.18356e-05 | 5.429e-07 | 7.285e-05 | 5.388e-05 | WITHIN_25_PERCENT |
| F8 | -32054.1 | -14398.2 | 6645.04 | -39260 | -18560 | 9867 | WITHIN_25_PERCENT |
| F9 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F10 | 4.44089e-16 | 4.44089e-16 | 2.00587e-31 | 4.441e-16 | 4.441e-16 | 0 | NEAR_ZERO_AGREEMENT |
| F11 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F12 | 1.81792e-08 | 0.917176 | 0.504895 | 9.093e-10 | 0.6876 | 0.6422 | WITHIN_FACTOR_2 |
| F13 | 9.79381 | 9.88047 | 0.0312111 | 1.024 | 9.58 | 1.616 | WITHIN_25_PERCENT |

### D = 100 diagnostic notes

- F1, F2, F3, F4, F9, F10 and F11 reproduce the paper's effective-zero regime.
  F2/F4 have tiny nonzero values at approximately underflow-scale, so ratio
  comparisons are intentionally not used.
- F5 is extremely close at the mean level:
  reproduced `98.8922` vs paper
  `98.87`.
- F6 shows a real seed/distribution difference:
  reproduced mean `12.6674` vs paper
  `8.562`, while sample STD
  `8.08345` is close to the paper's
  `8.137`. The reproduced best
  `0.236477` does not reproduce the paper's rare very small
  best `0.0001466`.
- F7 mean agreement is very close despite its stochastic objective:
  `7.19389e-05` vs
  `7.285e-05`.
- F8 is in the same broad performance scale:
  mean `-14398.2` vs paper `-18560`.
  The reproduced sample is less negative on average, indicating fewer/deeper
  Schwefel basin hits under this seed convention.
- F12 is somewhat worse on the mean
  (`0.917176` vs `0.6876`) but remains
  within factor two.
- F13 is the clearest **best/STD distribution mismatch** despite close mean:
  reproduced mean `9.88047` vs paper
  `9.58`, but reproduced best
  `9.79381` vs paper `1.024` and
  reproduced STD `0.0312111` vs paper
  `1.616`. The paper statistics imply at least one much
  lower outlier that is absent from the project's 1000–1029 seed set.

---

## 5. D = 500 detailed comparison

| F | Repro Best | Repro Mean | Repro STD | Paper Best | Paper Mean | Paper STD | Mean class |
|---|---:|---:|---:|---:|---:|---:|---|
| F1 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F2 | 0 | 8.1149e-217 | 0 | 0 | 3.513e-211 | 0 | NEAR_ZERO_AGREEMENT |
| F3 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F4 | 0 | 5.47363e-207 | 0 | 0 | 1.492e-204 | 0 | NEAR_ZERO_AGREEMENT |
| F5 | 498.771 | 498.948 | 0.0705278 | 498.8 | 499 | 0.052 | WITHIN_25_PERCENT |
| F6 | 124.263 | 124.631 | 0.104877 | 124.2 | 124.6 | 0.1481 | WITHIN_25_PERCENT |
| F7 | 1.06078e-06 | 0.000100365 | 9.7401e-05 | 4.091e-06 | 8.216e-05 | 6.352e-05 | WITHIN_25_PERCENT |
| F8 | -209344 | -45452 | 38066.4 | -194400 | -62820 | 51050 | WITHIN_FACTOR_2 |
| F9 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F10 | 4.44089e-16 | 4.44089e-16 | 2.00587e-31 | 4.441e-16 | 4.441e-16 | 0 | NEAR_ZERO_AGREEMENT |
| F11 | 0 | 0 | 0 | 0 | 0 | 0 | NEAR_ZERO_AGREEMENT |
| F12 | 6.08442e-06 | 1.16099 | 0.219286 | 9.54e-08 | 1.04 | 0.415 | WITHIN_25_PERCENT |
| F13 | 49.6927 | 49.8763 | 0.0462704 | 28.21 | 49.16 | 3.957 | WITHIN_25_PERCENT |

### D = 500 diagnostic notes

- F1, F2, F3, F4, F9, F10 and F11 again reproduce the paper's effective-zero
  regime.
- F5 is extremely close at the mean level.
- F6 is especially strong numerically:
  mean `124.631` vs paper `124.6`,
  with comparable spread.
- F7 remains close at the mean level despite benchmark stochasticity:
  `0.000100365` vs
  `8.216e-05`.
- F8 has a distinctive multi-basin distribution. The reproduced best
  `-209344` is actually more negative than the paper best
  `-194400` and is close to the benchmark optimum metadata
  `-209491`, but the reproduced mean
  `-45452` is less negative than the paper mean
  `-62820`. This means a few runs reached a very deep basin
  while many did not; it is not evidence that the overall mean reproduction is
  better.
- F12 mean is close:
  `1.16099` vs `1.04`.
- F13 again has a strong best/STD mismatch with a close mean:
  reproduced mean `49.8763` vs paper
  `49.16`, but best
  `49.6927` vs `28.21` and STD
  `0.0462704` vs `3.957`.
  This mirrors the D=100 observation and is consistent with a seed-dependent
  rare-outlier difference rather than a broad mean-level failure.

---

## 6. What H3c/H3d do and do not establish

### Established

- the frozen source-faithful SCHO implementation scales structurally to D=100
  and D=500;
- all 780 formal runs completed successfully;
- many functions reproduce the paper very closely;
- across both dimensions, all 26 function/dimension mean results are either in
  the same near-zero regime or within a factor of two of the paper SCHO mean;
- no mismatch was tuned away.

### Not yet established

The paper's full Section 3.1.4 comparison also includes:

- GWO
- ALO
- SCA
- SSA
- AOA
- RSA
- SHO
- GJO
- Friedman mean/final rankings
- Wilcoxon Tables 11 and 12

Therefore do **not** call H3c/H3d a full reproduction of Tables 9–12.

Use:

> **SCHO scalability core reproduced with strong mean-level agreement; full
> nine-algorithm comparison remains pending.**

---

## 7. Freeze rule

Do not modify:
- `algorithms/scho.py`
- `benchmarks/classic_23.py`
- `benchmarks/scho_scalability_h3.py`
- H3c raw results
- H3c summary
- H3c comparison report

Do not rerun different seeds merely to chase the paper's F6/F13 best values.

Any later comparator implementation must be added as a new stage and must use
the same common F1–F13 / D100-D500 experiment protocol.

---

## 8. H3d status

**H3d — COMPLETE**

Frozen label:

`SCHO_SCALABILITY_CORE_COMPLETE__STRONG_MEAN_LEVEL_AGREEMENT`

Next recommended stage:

**H4 — SCHO Section 3.1.1 subordinate-model ablation + Section 3.1.2 qualitative analysis**

The eight missing comparison algorithms remain a separate full-comparison
obligation and must be returned to before the project is called full-paper
complete.
