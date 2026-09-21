# H4i install

Copy into the project root, preserving paths:

- `experiments/benchmark_scho_fig7_h4i.py`
- `report/notes/H4i_scho_fig7_formal_protocol.md`

Prerequisites:

- H4h PASS
- `experiments/scho_fig7_variants_h4.py` present
- H4e raw file still present:
  `results/raw/scho_table5_h4e_runs.csv`

The formal command will be:

```powershell
python -m experiments.benchmark_scho_fig7_h4i
```

This performs 7590 new controlled-variant optimizer runs.

Checkpoint/resume is enabled. If interrupted, rerun the exact same command.

Expected ending:

```text
H4i RESULT: PASS
Formal controlled variant runs complete: 7590/7590
Protocol-aligned SCHO control reused: 690/690
```
