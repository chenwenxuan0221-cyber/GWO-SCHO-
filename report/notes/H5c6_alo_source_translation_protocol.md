# H5c6 — ALO source-structured Python translation

## Primary source

Seyedali Mirjalili's author MATLAB ALO package:

- MATLAB Central File Exchange 49920
- Version 1.0
- `ALO.m`
- `Random_walk_around_antlion.m`
- `RouletteWheelSelection.m`
- `initialization.m`

The MathWorks page identifies it as source code of Mirjalili's 2015
*The Ant Lion Optimizer* paper.

## Main-loop structure frozen

1. Initialize antlions.
2. Initialize ants separately.
3. Evaluate **antlions only**.
4. Sort antlion fitness.
5. Set elite from best antlion.
6. Start `Current_iter=2`.
7. For every ant:
   - roulette select using `1./sorted_antlion_fitness`;
   - fallback to the first antlion if selection returns -1;
   - create a complete random walk around the selected antlion;
   - create another complete random walk around the elite;
   - use the `Current_iter` row of both and average them.
8. Clip/evaluate all ants.
9. Merge old antlions and ants.
10. Sort 2N candidates and retain N.
11. Update elite.
12. Force elite back into sorted slot 1.
13. Store convergence at `Current_iter`.

Therefore:

`convergence_curve[0] == 0`

is preserved.

## Random-walk helper

The source creates, for every call and every dimension:

`X = [0 cumsum(2*(rand(Max_iter,1)>0.5)-1)']`

So each helper call consumes:

- two interval-shift `rand` draws;
- `Dim * MaxIter` random step draws.

The helper is called **twice for every ant at every iteration**.

This is intentionally expensive and is not vectorized away in a manner that
would change random-call structure.

## Shrinking schedule

Sequential source checks produce the effective stages:

- w=2 after 0.1T
- w=3 after 0.5T
- w=4 after 0.75T
- w=5 after 0.9T
- w=6 after 0.95T

For T=40 and Current_iter=2..40, stage iteration counts are:

`3 / 16 / 10 / 6 / 2 / 2`

where the first count is the pre-w=2 `I=1` stage.

## Roulette source behavior

Author function:

- cumulative sum of provided weights;
- `p = rand * accumulation(end)`;
- return first cumulative weight strictly greater than p;
- otherwise return -1.

ALO passes:

`1./sorted_antlion_fitness`

literally.

Consequences for benchmark objectives:

- zero fitness can create `Inf` weights;
- negative fitness can create negative weights;
- selection can therefore become unusual or fail;
- ALO.m falls back to antlion 1 on failure.

H5c6 **does not** replace this with absolute fitness, shifted fitness,
normalized probabilities, or rank selection.

That would be algorithm repair rather than source reproduction.

## Objective-evaluation count

- initial antlion evaluations: N
- ant evaluations for Current_iter=2..MaxIter: N*(MaxIter-1)

Total:

`N*MaxIter`

Initial ants are initialized but not initially evaluated.

## RNG exactness

NumPy default_rng is used.

The MATLAB random-call structure is preserved, but MATLAB stream/bitwise
equivalence is not claimed.

Frozen label on PASS:

`ALO_SOURCE_STRUCTURED_PYTHON_TRANSLATION__LITERAL_RECIPROCAL_ROULETTE__NUMPY_RNG`
