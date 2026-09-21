# H4d install

Copy into the project root, preserving paths:

- `experiments/scho_table5_variants_h4.py`
- `experiments/test_scho_table5_variants_h4d.py`
- `report/notes/H4d_scho_table5_structural_variant_protocol.md`

Do not modify:

- `algorithms/scho.py`
- `benchmarks/classic_23.py`

Then run:

```powershell
python -m experiments.test_scho_table5_variants_h4d
```

Expected ending:

```text
H4d RESULT: PASS
Full SCHO control is exactly equal to frozen algorithms/scho.py.
All five paper-described structural variants are deterministic and structurally distinct.
```
