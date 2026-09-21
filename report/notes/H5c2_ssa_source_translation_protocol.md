# H5c2 — SSA source-structured Python translation

Primary source: Seyedali Mirjalili's author MATLAB SSA implementation,
File Exchange 63745, version 1.0.0.0.

Preserved mechanics:
- initial population evaluation;
- one initial sort to set FoodPosition/FoodFitness;
- main loop starts at l=2;
- c1 = 2*exp(-(4*l/MaxIter)^2);
- first floor(N/2) salps are leaders;
- fresh c2,c3 per leader coordinate;
- followers are updated sequentially/in-place;
- clipping/evaluation follows the full update;
- historical food update;
- curve[0] remains zero because source recording starts at l=2.

The SCHO Table 6 statement that c2,c3 are random in [0,1] is consistent
with this source structure.

NumPy default_rng is used. MATLAB bitwise/RNG-stream equivalence is not claimed.

Frozen label on PASS:
`SSA_SOURCE_STRUCTURED_PYTHON_TRANSLATION__NUMPY_RNG`
