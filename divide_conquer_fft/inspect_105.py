from pathlib import Path

import numpy as np
from scipy.io import loadmat

file_path = Path("105.mat")

if not file_path.exists():
    raise FileNotFoundError(f"File not found: {file_path.resolve()}")

print(f"File: {file_path.resolve()}")
print(f"Size: {file_path.stat().st_size:,} bytes")

data = loadmat(file_path)

print("\nVariables found:")
for name, value in data.items():
    if not name.startswith("__"):
        print(f"{name}: shape={value.shape}, dtype={value.dtype}")

signal_name = "X105_DE_time"

if signal_name not in data:
    raise KeyError(f"Variable '{signal_name}' was not found.")

signal = np.asarray(data[signal_name]).squeeze()

print(f"\nSignal: {signal_name}")
print(f"Number of samples: {signal.size}")
print(f"All values finite: {bool(np.isfinite(signal).all())}")
print(f"First 10 samples: {signal[:10]}")
