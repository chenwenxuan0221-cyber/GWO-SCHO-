# H3c install

Copy into the project root, preserving paths:

- `experiments/benchmark_scho_scalability_h3c.py`
- `report/notes/H3c_scho_scalability_protocol.md`

Do not modify:
- `algorithms/scho.py`
- `benchmarks/classic_23.py`
- `benchmarks/scho_scalability_h3.py`

The formal run command will be:

```powershell
python -m experiments.benchmark_scho_scalability_h3c
```

This is a large 780-run experiment. It checkpoints every completed run and can
resume from the same command after interruption.

Expected ending after all runs:

```text
H3c RESULT: PASS
Formal runs complete: 780/780
```
