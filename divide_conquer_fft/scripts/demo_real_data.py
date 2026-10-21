"""Run the project's own radix-2 FFT on a CWRU MATLAB bearing recording.

Optional dependencies:
    python -m pip install scipy matplotlib

Example:
    python scripts/demo_real_data.py --file data/105.mat --sample-rate 12000 \
        --samples 4096 --out results/real_data
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from radix2_fft import fft


def choose_channel(mat, requested):
    candidates = sorted(
        key for key, value in mat.items()
        if not key.startswith("__")
        and key.lower().endswith("_de_time")
        and np.asarray(value).size > 0
    )
    if requested != "auto":
        if requested not in mat:
            raise ValueError(
                f"Channel {requested!r} not found. Available drive-end channels: {candidates}"
            )
        return requested
    if not candidates:
        candidates = sorted(
            key for key, value in mat.items()
            if not key.startswith("__")
            and ("de_time" in key.lower())
            and np.asarray(value).size > 0
        )
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError(
            "No drive-end acceleration variable found. Variables in file: "
            + ", ".join(k for k in mat if not k.startswith("__"))
        )
    raise ValueError(
        "More than one possible drive-end channel found. Choose --channel explicitly. "
        f"Candidates: {candidates}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Path to a downloaded CWRU .mat file")
    parser.add_argument("--sample-rate", required=True, type=float,
                        help="Sampling rate in Hz, verified from the selected dataset record")
    parser.add_argument("--channel", default="auto",
                        help="MATLAB variable name, or 'auto' to choose a unique *_DE_time variable")
    parser.add_argument("--samples", type=int, default=4096,
                        help="Number of initial samples to analyze; must be a power of two")
    parser.add_argument("--out", default="results/real_data", help="Output directory")
    args = parser.parse_args()

    data_path = Path(args.file)
    if not data_path.is_file():
        parser.error(f"Input file does not exist: {data_path}")
    if args.sample_rate <= 0:
        parser.error("--sample-rate must be positive")
    if args.samples < 2 or args.samples & (args.samples - 1):
        parser.error("--samples must be a power of two and at least 2")

    mat = loadmat(data_path)
    channel = choose_channel(mat, args.channel)
    signal = np.asarray(mat[channel]).squeeze()
    if signal.ndim != 1:
        raise ValueError(f"Selected channel should be 1-D after squeeze; got shape {signal.shape}")
    if signal.size < args.samples:
        raise ValueError(
            f"Channel contains only {signal.size} samples; requested {args.samples}"
        )
    segment = np.asarray(signal[:args.samples], dtype=float)
    if not np.all(np.isfinite(segment)):
        raise ValueError("Selected signal segment contains NaN or infinite values")

    # Remove the segment's mean to suppress the DC component in the plotted spectrum.
    centered = segment - float(np.mean(segment))
    spectrum = fft(centered.tolist())  # The project's own implementation, not numpy.fft.
    n = len(centered)
    freqs = np.arange(n // 2 + 1) * args.sample_rate / n
    mags = np.abs(np.asarray(spectrum[:n // 2 + 1]))
    # Single-sided amplitude spectrum; double interior positive-frequency bins.
    amplitude = mags / n
    if n > 2:
        amplitude[1:-1] *= 2
    if n == 2:
        pass

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = data_path.stem
    waveform_path = out / f"{stem}_waveform.png"
    spectrum_path = out / f"{stem}_spectrum.png"
    csv_path = out / f"{stem}_spectrum.csv"
    metadata_path = out / f"{stem}_metadata.json"

    time_s = np.arange(n) / args.sample_rate
    plt.figure(figsize=(10, 4))
    plt.plot(time_s, segment, linewidth=0.7)
    plt.xlabel("Time (s)")
    plt.ylabel("Recorded acceleration (dataset units)")
    plt.title(f"CWRU vibration segment: {stem}, channel {channel}")
    plt.tight_layout()
    plt.savefig(waveform_path, dpi=160)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.plot(freqs, amplitude, linewidth=0.8)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Single-sided amplitude (recorded units)")
    plt.title(f"FFT spectrum: {stem}, channel {channel}")
    plt.tight_layout()
    plt.savefig(spectrum_path, dpi=160)
    plt.close()

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["frequency_hz", "amplitude"])
        writer.writerows((f"{f:.8f}", f"{a:.12g}") for f, a in zip(freqs, amplitude))

    top = np.argsort(amplitude)[::-1]
    top = [int(i) for i in top if freqs[i] > 0][:10]
    metadata = {
        "dataset": "Case Western Reserve University Bearing Data Center",
        "source_url": "https://engineering.case.edu/bearingdatacenter",
        "input_file": str(data_path),
        "channel": channel,
        "sample_rate_hz": args.sample_rate,
        "samples_analyzed": n,
        "segment": "first N samples; mean removed for spectrum",
        "frequency_resolution_hz": args.sample_rate / n,
        "algorithm": "project radix-2 Cooley-Tukey FFT (src/radix2_fft.py)",
        "outputs": {
            "waveform_png": str(waveform_path),
            "spectrum_png": str(spectrum_path),
            "spectrum_csv": str(csv_path)
        },
        "largest_nonzero_frequency_bins": [
            {"frequency_hz": float(freqs[i]), "amplitude": float(amplitude[i])}
            for i in top
        ],
        "interpretation_limit": "Spectrum peaks alone do not diagnose bearing condition."
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
