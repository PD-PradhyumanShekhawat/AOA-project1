
#!/usr/bin/env python3
"""Independent feasibility checks for expanded SatNet schedules."""

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("greedy_dsn/results/expanded_model")


def load_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def overlap(a, b, c, d):
    # Half-open intervals: adjacent activities are allowed.
    return a < d and c < b


def validate_schedule(rows, label):
    errors = []
    seen_tracks = set()
    antenna_intervals = defaultdict(list)
    total_hours = 0.0

    for line, row in enumerate(rows, start=2):
        week = row["week_key"]
        track = row["track_id"]
        key = (week, track)

        if key in seen_tracks:
            errors.append(
                f"{label}: duplicate request {track} in {week} (CSV line {line})"
            )
        seen_tracks.add(key)

        start = int(row["activity_start_epoch"])
        end = int(row["activity_end_epoch"])
        tx_start = int(row["tx_start_epoch"])
        tx_end = int(row["tx_end_epoch"])
        duration = float(row["duration_hours"])

        if not (start <= tx_start < tx_end <= end):
            errors.append(
                f"{label}: inconsistent activity/transmission bounds "
                f"at CSV line {line}"
            )

        if abs((tx_end - tx_start) / 3600 - duration) > 1.1 / 3600:
            errors.append(
                f"{label}: duration mismatch at CSV line {line}"
            )

        total_hours += duration

        for antenna in filter(None, row["antennas"].split(";")):
            antenna_intervals[(week, antenna)].append(
                (start, end, track, line)
            )

    conflict_count = 0
    for (week, antenna), intervals in antenna_intervals.items():
        intervals.sort()
        for i, first in enumerate(intervals):
            a, b, track_a, line_a = first
            for second in intervals[i + 1:]:
                c, d, track_b, line_b = second
                if c >= b:
                    break
                if overlap(a, b, c, d):
                    conflict_count += 1
                    errors.append(
                        f"{label}: antenna conflict on {antenna}, {week}: "
                        f"{track_a} (line {line_a}) vs "
                        f"{track_b} (line {line_b})"
                    )

    return {
        "schedule": label,
        "selected_count": len(rows),
        "unique_request_count": len(seen_tracks),
        "communication_hours": round(total_hours, 6),
        "antenna_conflict_count": conflict_count,
        "error_count": len(errors),
        "errors": errors[:30],
    }


def main():
    report_path = ROOT / "expanded_model_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    candidates = load_csv(ROOT / "expanded_candidates.csv")
    greedy = load_csv(ROOT / "greedy_selected.csv")
    milp = load_csv(ROOT / "milp_selected.csv")

    results = {
        "candidate_count": len(candidates),
        "greedy": validate_schedule(greedy, "greedy"),
        "milp": validate_schedule(milp, "milp"),
        "reported_greedy_hours": report["greedy_communication_hours"],
        "reported_milp_hours": report["milp_communication_hours"],
        "scope_warning": (
            "This validates internal schedule consistency only. It does not "
            "independently establish visibility, maintenance, setup/teardown, "
            "resource-option, or full SatNet benchmark feasibility."
        ),
    }

    for label, rows, key in (
        ("greedy", greedy, "reported_greedy_hours"),
        ("milp", milp, "reported_milp_hours"),
    ):
        actual = results[label]["communication_hours"]
        if abs(actual - float(results[key])) > 1e-5:
            results[label]["errors"].append(
                f"Objective mismatch: selected rows sum to {actual}, "
                f"report says {results[key]}"
            )
            results[label]["error_count"] += 1

    output = ROOT / "independent_validation.json"
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))

    if results["greedy"]["error_count"] or results["milp"]["error_count"]:
        print("\nVALIDATION FAILED")
        sys.exit(1)

    print("\nINTERNAL SCHEDULE CHECKS PASSED")
    print("Full SatNet feasibility is not established by this validator.")


if __name__ == "__main__":
    main()
