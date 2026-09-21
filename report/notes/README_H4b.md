# H4b install

Copy into the project root, preserving paths:

- `experiments/scho_history_instrumented_h4.py`
- `experiments/test_scho_history_h4b.py`
- `report/notes/H4b_scho_history_instrumentation_protocol.md`

Do not modify:

- `algorithms/scho.py`
- `benchmarks/classic_23.py`

After placement run:

```powershell
python -m experiments.test_scho_history_h4b
```

Expected ending:

```text
H4b RESULT: PASS
All 7 Fig.8 functions preserve frozen SCHO score/position/curve exactly.
```
