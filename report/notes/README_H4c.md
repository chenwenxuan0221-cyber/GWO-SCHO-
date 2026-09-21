# H4c install

Copy into the project root, preserving paths:

- `experiments/generate_scho_fig8_h4c.py`
- `report/notes/H4c_scho_fig8_protocol.md`

Prerequisite:
- H4b PASS and `experiments/scho_history_instrumented_h4.py` already present.

Do not modify:
- `algorithms/scho.py`
- `benchmarks/classic_23.py`

After placement run:

```powershell
python -m experiments.generate_scho_fig8_h4c
```

Expected ending:

```text
H4c RESULT: PASS
Functions completed: 7/7
Raw history files: 7/7
Fig.8-style figures: 4/4
```
