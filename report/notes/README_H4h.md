# H4h install

Copy into the project root, preserving paths:

- `experiments/scho_fig7_variants_h4.py`
- `experiments/test_scho_fig7_variants_h4h.py`
- `report/notes/H4h_scho_fig7_controlled_variant_protocol.md`

Do not modify:

- `algorithms/scho.py`
- `benchmarks/classic_23.py`

Then run:

```powershell
python -m experiments.test_scho_fig7_variants_h4h
```

Expected ending:

```text
H4h RESULT: PASS
Full SCHO control is exactly equal to frozen algorithms/scho.py.
All 11 controlled Fig.7 variants are deterministic and their intended branches are exercised.
```

This stage does NOT run the 7590-run formal Fig.7 experiment.
