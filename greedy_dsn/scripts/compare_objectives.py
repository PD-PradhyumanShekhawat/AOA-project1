#!/usr/bin/env python3
"""Compare cardinality-greedy with exact weighted interval scheduling.

Scope: the supplied fixed candidate intervals in audit_v2/candidate_intervals.csv.
This does not solve the full multi-resource SatNet problem.
"""
import argparse
import bisect
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GREEDY_SRC = REPO_ROOT / "greedy_dsn" / "src"
if str(GREEDY_SRC) not in sys.path:
    sys.path.insert(0, str(GREEDY_SRC))

from greedy_satnet import greedy_schedule


def weighted_interval_optimum(rows):
    """Return max summed requested communication hours for fixed intervals."""
    ordered = sorted(rows, key=lambda r: (int(r["activity_end_epoch"]), int(r["activity_start_epoch"]), r["track_id"]))
    ends = [int(r["activity_end_epoch"]) for r in ordered]
    dp = [0.0] * (len(ordered) + 1)
    for i, row in enumerate(ordered, start=1):
        start = int(row["activity_start_epoch"])
        predecessor_count = bisect.bisect_right(ends, start, 0, i - 1)
        weight = float(row["requested_duration_hours"])
        dp[i] = max(dp[i - 1], dp[predecessor_count] + weight)
    return dp[-1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", default="greedy_dsn/results/audit_v2/candidate_intervals.csv")
    parser.add_argument("--out", default="greedy_dsn/results/objective_comparison")
    args = parser.parse_args()
    with Path(args.candidates).open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if rows and not {"week_key", "track_id", "activity_start_epoch", "activity_end_epoch", "requested_duration_hours"}.issubset(rows[0]):
        raise ValueError("Candidate CSV lacks required interval/objective fields")
    by_week = defaultdict(list)
    for row in rows:
        by_week[row["week_key"]].append(row)
    results = []
    for week in sorted(by_week):
        candidates = by_week[week]
        greedy = greedy_schedule(candidates)
        greedy_hours = sum(float(r["requested_duration_hours"]) for r in greedy)
        optimum_hours = weighted_interval_optimum(candidates)
        results.append({
            "week_key": week,
            "candidate_count": len(candidates),
            "greedy_interval_count": len(greedy),
            "greedy_communication_hours": round(greedy_hours, 6),
            "exact_weighted_dp_hours": round(optimum_hours, 6),
            "greedy_to_weighted_optimum_ratio": round(greedy_hours / optimum_hours, 8) if optimum_hours else 1.0,
            "scope": "fixed candidate intervals; one antenna; full requested durations; setup/teardown included in conflict intervals",
        })
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    with (out / "objective_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "week_key",
            "candidate_count",
            "greedy_interval_count",
            "greedy_communication_hours",
            "exact_weighted_dp_hours",
            "greedy_to_weighted_optimum_ratio",
            "scope",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(results)
    greedy_total = sum(r["greedy_communication_hours"] for r in results)
    opt_total = sum(r["exact_weighted_dp_hours"] for r in results)
    report = {
        "candidate_count": len(rows),
        "greedy_total_intervals": sum(r["greedy_interval_count"] for r in results),
        "greedy_total_communication_hours": round(greedy_total, 6),
        "weighted_dp_total_communication_hours": round(opt_total, 6),
        "greedy_to_weighted_optimum_ratio": round(greedy_total / opt_total, 8) if opt_total else 1.0,
        "weekly_results": results,
        "interpretation": "The earliest-finish-time rule is optimal for maximum cardinality on fixed intervals, not for maximizing summed durations. Weighted DP is exact only for this fixed single-antenna candidate set; this is not a full SatNet optimum.",
    }
    (out / "objective_comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
