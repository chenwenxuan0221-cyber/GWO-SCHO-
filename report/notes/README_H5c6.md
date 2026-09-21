# H5c6 install

Copy into project root, preserving paths:

- `algorithms/alo.py`
- `experiments/test_alo_h5c6.py`
- `report/notes/H5c6_alo_source_translation_protocol.md`

Then run:

```powershell
python -m experiments.test_alo_h5c6
```

This is a structural smoke test only.

Important:
ALO's literal `1./fitness` roulette behavior is intentionally preserved even
for zero/negative benchmark fitness.
