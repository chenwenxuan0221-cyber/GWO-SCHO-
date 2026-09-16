# E5 — CEC2014 reproduction vs SCHO paper Table 14

## 1. Goal

Compare the completed E4 30-run GWO/SCHO results against Bai et al. Table 14 for CEC2014 (D=10), without changing either frozen optimizer.

## 2. Protocol

Reproduction: F1–F30, D=10, N=30, MaxIter=500, 30 runs, seeds 1000–1029.

Paper comparison metrics: Best, Average, STD. The reproduction's `Std_sample_ddof1` is used for STD comparison.

For the main diagnostic, use excess error:

`MeanError = Mean - f_opt`

and

`MeanErrorRatio = ReproMeanError / PaperMeanError`.

This avoids the CEC offset `f_opt = 100*i` hiding optimization differences.

Diagnostic bands are descriptive, not significance tests:
- Close: ratio 0.8–1.25
- Same order: ratio 0.5–2, excluding Close
- Notable deviation: ratio 0.1–10, excluding the closer bands
- Major deviation: outside 0.1–10

## 3. GWO consistency

GWO is the strongest cross-check of the evaluator/protocol:

- Close (±25%): 22/30
- Same order (additional): 8/30
- Within factor 2 overall: 30/30
- No GWO function has mean excess-error outside factor 2 of the paper.

This strongly supports that the CEC2014 evaluator, dimensionality, bounds, and gross experiment protocol are compatible with the paper.

## 4. SCHO consistency

SCHO:
- Close (±25%): 14/30
- Same order (additional): 12/30
- Within factor 2 overall: 26/30
- Outside factor 2: 4/30 — F2, F7, F15, F21.

The largest mismatch is F21. The reproduced SCHO mean excess-error is about 67× the paper value, with very large run-to-run dispersion.

F23 and F27 show a different type of mismatch: the reproduced SCHO runs collapse to fixed plateaus (STD=0), while the paper reports nonzero STD and substantially better Best values. F28, by contrast, matches the paper's 3000 plateau with STD=0.

## 5. Pairwise GWO-vs-SCHO consequence

Using only the two algorithms' Table-14 Average/Mean values:

- Paper: SCHO wins 17/30, GWO wins 13/30.
- Reproduction: SCHO wins 8/30, GWO wins 22/30.
- Winner flips: 9 functions — F1, F3, F4, F10, F17, F18, F20, F21, F26.

All nine flips are cases where the paper has SCHO below GWO, but the current reproduction has GWO below SCHO.

Therefore the current E4 experiment reproduces the CEC/GWO scale well, but does not reproduce the paper's relative SCHO-vs-GWO advantage across CEC2014.

## 6. Interpretation

Do not tune the frozen SCHO implementation to force Table 14 agreement.

The evidence points to:
1. evaluator/protocol compatibility being broadly sound (supported by GWO);
2. most SCHO functions remaining in the same error scale as the paper;
3. a smaller set of SCHO functions having material distributional/stochastic mismatches, especially F21 and the F23/F27 plateaus.

Possible contributors include NumPy-vs-MATLAB RNG trajectory differences and source-level SCHO behaviors already preserved in the source-faithful baseline. From summary statistics alone, these causes cannot be separated conclusively.

## 7. E5 status

E5 comparison is complete. No algorithm code was modified.

Next recommended step: E6, using the existing E4 raw run file to inspect the SCHO outliers/plateaus and, if desired, reproduce pairwise Wilcoxon tests for GWO vs SCHO only. This should be diagnostic, not tuning.
