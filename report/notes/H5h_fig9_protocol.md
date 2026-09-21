# H5h — SCHO Fig. 9 protocol freeze

Status:

`SCHO_FIG9_COMPLETE_CONTROLLED_EQUIVALENT`

## Paper structure

Fig. 9 compares SCHO with GWO, ALO, SCA, SSA, AOA, RSA, SHO, and GJO on
F1–F23 using convergence curves.

The accessible paper text/caption does not state whether the displayed curves
are 30-run averages or a selected representative run. Therefore this project
does not claim exact run-selection or aggregation equivalence.

## Controlled-equivalent protocol

- F1–F13: D=30
- F14–F23: native dimension
- N=30
- MaxIter=500
- representative H5 run=1
- optimizer seed=1000
- objective seed=`5024000 + 100*function_number + 1`
- NumPy RNG; no MATLAB bitwise RNG equivalence
- AOA uses H5 Table 6 `mu=0.5`
- SHO means Sea-Horse Optimizer
- frozen GWO/SCHO are not modified

Every rerun final score is checked for exact equality against the corresponding
H5_CLASSICAL_V1 run-1 raw `BestScore`.

## Plotting layer

Raw optimizer curves are stored unchanged.

For functions whose scores span many orders of magnitude, the plotting layer
uses `symlog` rather than silently replacing source-preserved zeros. Functions
with naturally negative optima are shown on a linear y-axis.

This plotting choice is controlled-equivalent and is not claimed to reproduce
the paper's exact axis transform or pixel layout.
