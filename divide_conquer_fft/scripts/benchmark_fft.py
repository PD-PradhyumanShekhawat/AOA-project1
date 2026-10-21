"""Repeated runtime benchmark; writes CSV and an optional PNG plot."""
import argparse
import csv
import math
import statistics
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from radix2_fft import fft


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results")
    parser.add_argument("--min-power", type=int, default=8)
    parser.add_argument("--max-power", type=int, default=15)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=1)
    args = parser.parse_args()
    if args.min_power < 0 or args.max_power < args.min_power or args.repeats < 1 or args.warmups < 0:
        parser.error("invalid powers/repeats/warmups")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for power in range(args.min_power, args.max_power + 1):
        n = 2 ** power
        signal = [math.sin(0.013*i) + 0.25*math.cos(0.071*i) for i in range(n)]
        for _ in range(args.warmups):
            fft(signal)
        times = []
        for _ in range(args.repeats):
            start = time.perf_counter()
            fft(signal)
            times.append((time.perf_counter()-start)*1000)
        med = statistics.median(times)
        rows.append({"n": n, "n_log2_n": n*power, "repeats": args.repeats,
                     "median_ms": f"{med:.6f}", "min_ms": f"{min(times):.6f}",
                     "max_ms": f"{max(times):.6f}"})
        print(f"n={n:6d} median={med:10.4f} ms")
    csv_path = out / "fft_runtime.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {csv_path}")
    try:
        import matplotlib.pyplot as plt
        ns = [int(r["n"]) for r in rows]
        medians = [float(r["median_ms"]) for r in rows]
        theoretical = [n*math.log2(n) for n in ns]
        scale = medians[0]/theoretical[0]
        plt.figure()
        plt.plot(ns, medians, marker="o", label="Measured median")
        plt.plot(ns, [v*scale for v in theoretical], marker="x", label="Scaled n log2(n)")
        plt.xlabel("Input size n")
        plt.ylabel("Runtime (ms)")
        plt.title("Radix-2 FFT runtime")
        plt.legend()
        plt.tight_layout()
        plot_path = out / "fft_runtime_vs_nlogn.png"
        plt.savefig(plot_path, dpi=160)
        plt.close()
        print(f"Wrote {plot_path}")
    except ImportError:
        print("Matplotlib not installed; CSV was written, plot skipped.")


if __name__ == "__main__":
    main()
