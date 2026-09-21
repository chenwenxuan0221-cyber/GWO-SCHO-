# H5c5 — RSA source-structured Python translation

## 1. Primary source resolution

The H5b uncertainty about RSA beta is now resolved at the **author-code level**.

Laith Abualigah's public author `RSA.m` explicitly contains:

- `Alpha=0.1`
- `Beta=0.005`

Therefore the SCHO Table 6 settings:

- alpha = 0.1
- beta = 0.005

match the accessible author implementation.

Any different beta value printed in secondary/paper prose remains a
documentation discrepancy; H5 does not override the author MATLAB code here.

## 2. Important source quirks

### The first solution is never updated

Author code:

`for i=2:size(X,1)`

Therefore:

- all N solutions are initialized and evaluated initially;
- only solutions 2..N are updated/evaluated inside every iteration;
- solution 1 remains permanently frozen at its initial location.

H5c5 preserves this exactly for all bounds.

Formal source evaluation count is therefore:

`N + (N-1)*MaxIter`

not `N*(MaxIter+1)`.

### Exact R operator precedence

Author code is equivalent to:

`R = Best_j - X[random,j] / (Best_j + eps)`

It is **not**:

`R = (Best_j - X[random,j]) / (Best_j + eps)`

H5c5 preserves the source precedence.

### ES uses a random integer, including zero

`ES = 2*randi([-1 1])*(1-t/T)`

So the integer factor is one of:

`{-1, 0, +1}`

with a fresh draw once per iteration.

## 3. Four source phases

Author conditions:

1. `t < T/4`
2. `t < 2*T/4 && t >= T/4`
3. `t < 3*T/4 && t >= 2*T/4`
4. otherwise

For T=40 this means iteration counts:

`9 / 10 / 10 / 11`

not 10/10/10/10.

### Phase 1

`Xnew = Best - Eta*Beta - R*rand`

### Phase 2

`Xnew = Best * X[random] * ES * rand`

### Phase 3

`Xnew = Best * P * rand`

### Phase 4

`Xnew = Best - Eta*eps - R*rand`

After completing candidate i:

- clip Xnew(i,:) to bounds;
- evaluate;
- strict greedy acceptance;
- update historical best.

## 4. P and vector-bound issue

Author scalar formula:

`P = Alpha + (X(i,j)-mean(X(i,:))) / (Best(j)*(UB-LB)+eps)`

For scalar UB/LB this is directly well-defined.

For a vector UB/LB, the MATLAB expression as written does not produce the
desired scalar coordinate denominator and is not directly usable for the H5
F17 rectangle.

H5 must include F17, so H5c5 freezes this explicit adapter for vector bounds:

`Best(j) * (UB(j)-LB(j)) + eps`

Only F17 uses this adapter in the classical suite.

Exactness boundary:

- scalar-bound F1–F16 except F17, and F18–F23:
  `SOURCE-STRUCTURED`
- F17 vector-bound P denominator:
  `PROJECT-CONTROLLED COORDINATE-SPAN ADAPTER`

Do not silently call F17 author-source exact.

## 5. RNG exactness

NumPy `default_rng` preserves the source random-call categories/order as closely
as practical:

- one ES integer draw per iteration;
- one population-index draw for R per updated coordinate;
- one additional population-index draw in phase 2;
- one uniform rand per coordinate update.

No MATLAB RNG-stream or bitwise equivalence is claimed.

## 6. H5c5 acceptance

Smoke:

- scalar bounds: F2, F7, F15, F21
- vector adapter: F17
- N=6
- MaxIter=40
- seed=1000

Frozen label on PASS:

`RSA_SOURCE_STRUCTURED_PYTHON_TRANSLATION__ALPHA0P1_BETA0P005__F17_VECTOR_BOUND_ADAPTER__NUMPY_RNG`
