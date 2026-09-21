# H5c1 install

Copy into the project root, preserving paths:

- `algorithms/sca.py`
- `experiments/test_sca_h5c1.py`
- `report/notes/H5c1_sca_source_translation_protocol.md`

Do not modify:
- `algorithms/gwo.py`
- `algorithms/scho.py`

Then run:

```powershell
python -m experiments.test_sca_h5c1
```

This is a structural smoke test only. It does not run the formal 30-run
nine-algorithm experiment.
