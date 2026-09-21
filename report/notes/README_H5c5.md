# H5c5 install

Copy into project root, preserving paths:

- `algorithms/rsa.py`
- `experiments/test_rsa_h5c5.py`
- `report/notes/H5c5_rsa_source_translation_protocol.md`

Then run:

```powershell
python -m experiments.test_rsa_h5c5
```

This is a structural smoke test only.

Important source facts:
- author RSA.m itself uses Alpha=0.1, Beta=0.005;
- first solution is never updated;
- F17 requires an explicitly labelled vector-bound adapter.
