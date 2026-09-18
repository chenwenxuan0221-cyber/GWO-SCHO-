# GWO Stage B — F1–F23 Reproduction Summary

## 1. Experimental protocol

The Python reproduction uses 30 independent runs for each benchmark, population size N=30,
and MaxIter=500. The comparison uses the GWO mean values reported in the original paper
Tables 5–7. Because several printed Std entries in those tables are internally inconsistent,
the main reproduction judgment is based on mean value, theoretical optimum, best/worst
behavior, numerical order of magnitude, and 30-run stability.

## 2. Overall result

The classical F1–F23 benchmark reproduction is successful at the algorithm-behavior level.

- Highly consistent: F1, F2, F4, F5, F7, F10, F16, F17, F18, F19, F20, F22, F23
- Trend consistent with quantitative differences: F3, F6, F8, F11, F12, F13, F14, F21
- Notable deviations: F9, F15

Most fixed-dimension multimodal functions (especially F16–F23, except the higher run-to-run
variation visible in F21) closely reproduce the paper mean values. F5, F7, F10, F16–F20,
F22, and F23 are especially strong matches.

## 3. Functions with notable deviations

### F9

Our 30-run mean is 3.279163e+00, while the paper mean is
3.105210e-01. However, the best reproduced value is
0.000000e+00, showing that the implementation can reach the global
optimum region. The main difference is therefore run-to-run stability and the frequency of
convergence to local minima.

### F15

Our 30-run mean is 3.859944e-03, while the paper mean is
3.370000e-04. The best reproduced value is
3.088561e-04, which is close to the theoretical optimum
3.000000e-04. Several runs converge to a stable
local optimum near 2.036e-2, which inflates the 30-run mean.

## 4. Source-level verification already completed

The Python implementations of F8, F9, F12, F13, and F15 have been checked against the original
MATLAB benchmark definitions and found mathematically consistent. The GWO alpha/beta/delta
update logic, linear parameter a, and scalar r1/r2 call granularity have also been aligned with
the original MATLAB implementation.

A controlled test using MATLAB-style column-major assignment of the NumPy initialization random
stream did not improve F9 or F15; both means became worse. Therefore that modification should not
be retained in the final baseline.

## 5. Interpretation of remaining differences

The remaining discrepancies are most plausibly explained by stochastic-run differences rather
than a benchmark-function or core-GWO coding error. NumPy and MATLAB do not use the same random
number stream under the present implementation, and the original paper does not provide the
exact 30 seeds used for its reported Monte Carlo averages. Multimodal functions such as F9 and
F15 are especially sensitive to which random runs fall into local minima.

## 6. Stage-B conclusion

Freeze the original NumPy initialization baseline and treat the GWO F1–F23 implementation as the
validated baseline for the next stage. The current results are suitable for later GWO-vs-SCHO
comparison, while F9 and F15 should be explicitly discussed as stochastic-stability deviations
rather than silently tuned to match the paper.
