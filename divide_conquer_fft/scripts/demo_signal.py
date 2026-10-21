"""Synthetic vibration-spectrum demonstration."""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from radix2_fft import fft


def main():
    sample_rate_hz, n = 1024, 1024
    signal = [math.sin(2*math.pi*64*i/sample_rate_hz)
              + 0.6*math.sin(2*math.pi*180*i/sample_rate_hz)
              + 0.1*math.sin(2*math.pi*230*i/sample_rate_hz) for i in range(n)]
    spectrum = fft(signal)
    bins = sorted(range(n//2 + 1), key=lambda k: abs(spectrum[k]), reverse=True)[:8]
    print(f"Sample rate: {sample_rate_hz} Hz; samples: {n}; bin spacing: {sample_rate_hz/n:.3f} Hz")
    print("Largest nonnegative-frequency bins:")
    for k in bins:
        print(f"  bin={k:4d}, frequency={k*sample_rate_hz/n:8.3f} Hz, magnitude={abs(spectrum[k]):.3f}")


if __name__ == "__main__":
    main()
