# H5c7 repair package

The previous `No module named experiments.test_sho_h5c7` error occurred
because H5c7 had not actually been supplied yet.

Copy this package into the project root, preserving paths:

- `algorithms/sea_horse.py`
- `experiments/test_sho_h5c7.py`
- `report/notes/H5c7_seahorse_exactness_boundary.md`

Then run:

```powershell
python -m experiments.test_sho_h5c7
```

Important: `SHO` here is Sea-Horse Optimizer, not Spotted Hyena Optimizer.
