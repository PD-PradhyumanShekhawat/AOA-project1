#!/usr/bin/env python3
"""Reproducible runtime benchmark for greedy interval scheduling."""
import argparse
import csv
import random
import statistics
import sys
import time
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from greedy_satnet import greedy_schedule
except ImportError as exc:
    raise SystemExit(
        "Could not import greedy_satnet.py from greedy_dsn/src/."
    ) from exc


def make_intervals(n, seed):
    """Generate reproducible positive-duration synthetic intervals."""
    rng = random.Random(seed)
    intervals = []
    for i in range(n):
        start = rng.randint(0, max(100, n * 10))
        duration = rng.randint(1, 100)
        intervals.append({
            "week_key": "SYNTHETIC",
            "track_id": str(i),
            "activity_start_epoch": str(start),
            "activity_end_epoch": str(start + duration),
        })
    return intervals


def median_runtime_ms(intervals, repeats):
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = greedy_schedule(intervals)
        elapsed = time.perf_counter() - t0
        samples.append(elapsed * 1000.0)
        assert len(result) <= len(intervals)
    return statistics.median(samples), min(samples), max(samples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sizes",
        default="100,250,500,1000,2000,4000,8000",
        help="Comma-separated input sizes",
    )
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--seed", type=int, default=5405)
    parser.add_argument("--out", default=str(PROJECT_ROOT / "results" / "runtime"))
    args = parser.parse_args()

    sizes = [int(x.strip()) for x in args.sizes.split(",") if x.strip()]
    if not sizes or any(n < 1 for n in sizes):
        parser.error("--sizes must contain positive integers")
    if args.repeats < 3:
        parser.error("--repeats must be at least 3")

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    results = []

    print("GREEDY INTERVAL-SCHEDULING RUNTIME BENCHMARK")
    print("Timer covers greedy_schedule() only; input generation is excluded.")
    print(f"Seed: {args.seed}; repeats per size: {args.repeats}")
    print("n, median_ms, min_ms, max_ms, n_log2_n")

    for n in sizes:
        intervals = make_intervals(n, args.seed + n)
        median_ms, min_ms, max_ms = median_runtime_ms(intervals, args.repeats)
        row = {
            "n": n,
            "median_ms": f"{median_ms:.6f}",
            "min_ms": f"{min_ms:.6f}",
            "max_ms": f"{max_ms:.6f}",
            "n_log2_n": f"{n * math.log2(n):.6f}",
            "seed_used": args.seed + n,
            "repeats": args.repeats,
        }
        results.append(row)
        print(
            f"{n}, {row['median_ms']}, {row['min_ms']}, "
            f"{row['max_ms']}, {row['n_log2_n']}"
        )

    csv_path = outdir / "runtime_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; CSV saved, but graphs were not created.")
        print("Install with: python3 -m pip install matplotlib")
        print("CSV:", csv_path.resolve())
        return

    ns = [int(r["n"]) for r in results]
    medians = [float(r["median_ms"]) for r in results]
    nlogn = [float(r["n_log2_n"]) for r in results]

    fig, ax = plt.subplots()
    ax.plot(ns, medians, marker="o")
    ax.set_xlabel("Number of candidate intervals (n)")
    ax.set_ylabel("Median runtime (milliseconds)")
    ax.set_title("Greedy DSN Scheduler: Observed Runtime")
    ax.grid(True)
    fig.tight_layout()
    runtime_plot = outdir / "runtime_median.png"
    fig.savefig(runtime_plot, dpi=160)
    plt.close(fig)

    scale = medians[0] / nlogn[0] if nlogn[0] else 1.0
    reference = [value * scale for value in nlogn]

    fig, ax = plt.subplots()
    ax.plot(ns, medians, marker="o", label="Observed median runtime")
    ax.plot(ns, reference, marker="s", label="Scaled n log2(n) reference")
    ax.set_xlabel("Number of candidate intervals (n)")
    ax.set_ylabel("Runtime / scaled reference (milliseconds)")
    ax.set_title("Observed Runtime vs. O(n log n) Growth Reference")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    comparison_plot = outdir / "runtime_vs_nlogn.png"
    fig.savefig(comparison_plot, dpi=160)
    plt.close(fig)


    # Log-log plot to examine runtime growth across input sizes.
    fig, ax = plt.subplots()
    ax.plot(ns, medians, marker="o", label="Observed median runtime")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of candidate intervals (n, log scale)")
    ax.set_ylabel("Median runtime (milliseconds, log scale)")
    ax.set_title("Greedy DSN Scheduler: Log-Log Runtime")
    ax.legend()
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    fig.tight_layout()

    loglog_plot = outdir / "runtime_loglog.png"
    fig.savefig(loglog_plot, dpi=160)
    plt.close(fig)

    print("CSV:", csv_path.resolve())
    print("Plot:", runtime_plot.resolve())
    print("Plot:", comparison_plot.resolve())
    print("Plot:", loglog_plot.resolve())
    print("Note: scaled n log2(n) is a visual reference, not a fitted model.")



if __name__ == "__main__":
    main()
