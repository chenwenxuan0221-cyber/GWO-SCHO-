# H3b install

Copy into the project root, preserving paths:

- `benchmarks/scho_scalability_h3.py`
- `experiments/test_scho_scalability_h3b.py`
- `report/notes/H3b_scho_scalability_adapter_protocol.md`

Do not modify:
- `algorithms/scho.py`
- `benchmarks/classic_23.py`

Then run:

```powershell
python -m experiments.test_scho_scalability_h3b
```

Expected final lines:

```text
H3b RESULT: PASS
F1-F13 dimension override is validated for D=100 and D=500.
```
