# H1b/c — SIS2005 source assets + Python benchmark implementation

## Source package audit

The uploaded archive is the original-style `SIS2005` package for
*Novel Composition Test Functions for Numerical Global Optimization*.

It contains:
- `SIS_novel_func.m`
- five shift-data MAT files
- five D=10 matrix MAT files
- the six-function source implementation
- an attached PSO example and plotting/test scripts

The project copy used by H1 stores the required source assets under:

`benchmarks/data/sis2005/`

## Important source findings

1. All source data files contain the expected D=10 instance information.
2. The MATLAB source overwrites the 10th component optimum with the zero vector.
3. CF1 uses identity transforms in the MATLAB source, even though the source
   package also contains `com_func1_M_D10.mat`; that MAT matrix file is not
   used by `com_func1`.
4. CF2 and CF3 use their D=10 matrix files.
5. CF4 uses `hybrid_func1_*`.
6. CF5 and CF6 both use `hybrid_func2_data.mat` and
   `hybrid_func2_M_D10.mat`.
7. CF6 changes `sigma` and scales `lambda` by `sigma`.

## GWO Table-4 vs source discrepancy

GWO paper Table 4 prints F26/CF3 as ten Griewank components.

The uploaded original `SIS_novel_func.m`, however, implements `com_func3`
with ten `frastrigin` components.

H1 therefore freezes:
- primary implementation: `source_faithful` -> Rastrigin for CF3
- optional diagnostic: `paper_table4` -> Griewank for CF3 only

The diagnostic must never silently replace the primary definition.

## Deterministic validation

The generated test checks:
- SHA256 of all copied source assets
- MAT shapes and finite values
- matrix condition-number structure
- D=10, bounds [-5,5], fmin=0
- first component optimum evaluates to 0 for CF1-CF6
- x=0 evaluates to exactly 900 for CF1-CF6
- fixed x=1 regression anchors
- vectorized vs scalar evaluation
- explicit CF3 source-vs-paper diagnostic difference

No optimizer is run in H1b/c.
