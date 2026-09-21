# H4e install

Copy into the project root, preserving paths:

- `experiments/benchmark_scho_table5_h4e.py`
- `report/notes/H4e_scho_table5_formal_protocol.md`

Prerequisite:
- H4d PASS
- `experiments/scho_table5_variants_h4.py` already present

Do not modify:
- `algorithms/scho.py`
- `benchmarks/classic_23.py`
- `experiments/scho_table5_variants_h4.py`

After placement, the formal command will be:

```powershell
python -m experiments.benchmark_scho_table5_h4e
```

This is a large 4140-run experiment.

It checkpoints after every completed run. If interrupted, rerun the exact same
command to resume.

Expected ending:

```text
H4e RESULT: PASS
Formal runs complete: 4140/4140
```
