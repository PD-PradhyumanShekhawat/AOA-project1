
from pathlib import Path
import sys

import numpy as np
from scipy.io import loadmat

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from radix2_fft import fft

data = loadmat(PROJECT_ROOT / "105.mat")
signal = np.asarray(data["X105_DE_time"]).squeeze()

n = 4096
segment = signal[:n].astype(float)
centered = segment - np.mean(segment)

# Project implementation
actual = np.asarray(fft(centered.tolist()), dtype=complex)

# Independent reference implementation
expected = np.fft.fft(centered)

if actual.shape != expected.shape:
    raise AssertionError(
        f"Shape mismatch: {actual.shape} vs {expected.shape}"
    )

max_error = float(np.max(np.abs(actual - expected)))
passed = bool(np.allclose(actual, expected, rtol=1e-9, atol=1e-9))

print(f"Signal samples available: {signal.size}")
print(f"Samples tested: {n}")
print(f"Project FFT output length: {actual.size}")
print(f"Reference FFT output length: {expected.size}")
print(f"Maximum absolute coefficient error: {max_error:.12g}")
print(f"Independent comparison: {'PASS' if passed else 'FAIL'}")

if not passed:
    raise SystemExit(1)

