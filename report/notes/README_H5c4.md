# H5c4 install

Copy into project root, preserving paths:

- `algorithms/aoa.py`
- `experiments/test_aoa_h5c4.py`
- `report/notes/H5c4_aoa_source_translation_protocol.md`

Then run:

```powershell
python -m experiments.test_aoa_h5c4
```

This is a structural smoke test only.

Important:
H5 uses `Mu=0.5` because the SCHO paper Table 6 specifies 0.5.
The author AOA.m default is 0.499.
