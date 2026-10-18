#!/usr/bin/env python3
"""
Audit the official SatNet DSN benchmark for a narrowly restricted
single-antenna, single-visibility-period, fixed-duration interval-scheduling
candidate.

This is a DATA AUDIT, not the greedy scheduler. It does not claim to solve
the full SatNet scheduling problem.

Usage:
    python audit_satnet.py
    python audit_satnet.py --problems problems.json --maintenance maintenance.csv
    python audit_satnet.py --problems problems.json --maintenance maintenance.csv --out audit_output

If input paths are omitted, the script attempts to download the official
files from the SatNet GitHub repository. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

PROBLEMS_URL = (
    "problems.json"
)
MAINTENANCE_URL = (
    "maintenance.csv"
)
EPSILON = 1e-9


def obtain_file(path_arg: str | None, default_name: str, url: str, out_dir: Path) -> Path:
    if path_arg:
        path = Path(path_arg).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")
        return path

    path = out_dir / default_name
    if path.is_file() and path.stat().st_size > 0:
        return path

    print(f"Downloading {default_name} from the official SatNet repository...")
    request = urllib.request.Request(
        url, headers={"User-Agent": "COT5405-SatNet-data-audit/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
    except Exception as exc:
        raise RuntimeError(
            f"Could not download {url}. Download it in a browser and rerun with "
            f"--{ 'problems' if default_name.endswith('.json') else 'maintenance' } "
            f"<local-path>. Original error: {exc}"
        ) from exc

    if not content:
        raise RuntimeError(f"Downloaded an empty file from {url}")
    path.write_bytes(content)
    return path


def read_maintenance(path: Path) -> dict[tuple[int, int, str], list[tuple[float, float]]]:
    intervals: dict[tuple[int, int, str], list[tuple[float, float]]] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"week", "year", "starttime", "endtime", "antenna"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(
                f"maintenance.csv must contain columns {sorted(required)}; "
                f"found {reader.fieldnames}"
            )
        for row_num, row in enumerate(reader, start=2):
            try:
                key = (int(float(row["week"])), int(float(row["year"])), row["antenna"].strip())
                start, end = float(row["starttime"]), float(row["endtime"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid maintenance row {row_num}: {row}") from exc
            if end <= start:
                raise ValueError(f"Non-positive maintenance interval on row {row_num}: {row}")
            intervals.setdefault(key, []).append((start, end))
    for values in intervals.values():
        values.sort()
    return intervals


def overlaps(a_start: float, a_end: float, b_start: float, b_end: float) -> bool:
    # Half-open intervals: touching endpoints do not overlap.
    return a_start < b_end and b_start < a_end


def candidate_for_request(
    req: dict[str, Any],
    week_key: str,
    maintenance: dict[tuple[int, int, str], list[tuple[float, float]]],
) -> tuple[dict[str, Any] | None, str | None]:
    """Return candidate row and None, or no row and a first-failure reason."""
    resources = req.get("resources")
    if not isinstance(resources, list) or len(resources) != 1:
        return None, "not_exactly_one_resource_option"
    option = resources[0]
    if not isinstance(option, list) or len(option) != 1 or not isinstance(option[0], str):
        return None, "resource_option_not_single_antenna"
    antenna = option[0]

    vp_map = req.get("resource_vp_dict")
    if not isinstance(vp_map, dict) or antenna not in vp_map:
        return None, "missing_visibility_data_for_selected_antenna"
    vps = vp_map[antenna]
    if not isinstance(vps, list) or len(vps) != 1:
        return None, "not_exactly_one_visibility_period"
    vp = vps[0]

    try:
        duration = float(req["duration"])
        duration_min = float(req["duration_min"])
        setup_sec = float(req.get("setup_time", 0)) * 60.0
        teardown_sec = float(req.get("teardown_time", 0)) * 60.0
        window_start = float(req["time_window_start"])
        window_end = float(req["time_window_end"])
        vp_start = float(vp["TRX ON"])
        vp_end = float(vp["TRX OFF"])
        week = int(req["week"])
        year = int(req["year"])
    except (KeyError, TypeError, ValueError) as exc:
        return None, "missing_or_invalid_timing_field"

    if not all(math.isfinite(x) for x in (
        duration, duration_min, setup_sec, teardown_sec,
        window_start, window_end, vp_start, vp_end
    )):
        return None, "non_finite_timing_field"
    if duration <= 0 or duration_min <= 0 or setup_sec < 0 or teardown_sec < 0:
        return None, "non_positive_duration_or_negative_setup_teardown"
    if abs(duration - duration_min) > EPSILON:
        return None, "duration_is_not_fixed_at_requested_value"
    if window_end <= window_start or vp_end <= vp_start:
        return None, "invalid_time_window_or_visibility_period"

    # Conservative source-consistency checks. The communication interval,
    # not setup/teardown, must fit in both the request window and TRX window.
    earliest_tracking_on = max(window_start, vp_start)
    latest_tracking_off = min(window_end, vp_end)
    tracking_duration_sec = duration * 3600.0
    if earliest_tracking_on + tracking_duration_sec > latest_tracking_off + EPSILON:
        return None, "requested_duration_does_not_fit_visibility_and_request_window"

    maintenance_key = (week, year, antenna)
    maint = maintenance.get(maintenance_key, [])

    # Find the earliest transmission start for which the complete activity
    # [tracking_on - setup, tracking_off + teardown) does not overlap maintenance.
    tracking_on = earliest_tracking_on
    for _ in range(len(maint) + 2):
        tracking_off = tracking_on + tracking_duration_sec
        activity_start = tracking_on - setup_sec
        activity_end = tracking_off + teardown_sec

        conflicts = [
            (m_start, m_end)
            for m_start, m_end in maint
            if overlaps(activity_start, activity_end, m_start, m_end)
        ]
        if not conflicts:
            break

        # Any overlapping maintenance interval means the activity must begin
        # after that maintenance interval. Setup begins setup_sec before TX.
        next_tracking_on = max(m_end + setup_sec for _, m_end in conflicts)
        if next_tracking_on <= tracking_on + EPSILON:
            return None, "maintenance_adjustment_did_not_advance"
        tracking_on = next_tracking_on
    else:
        return None, "maintenance_adjustment_did_not_converge"

    tracking_off = tracking_on + tracking_duration_sec
    activity_start = tracking_on - setup_sec
    activity_end = tracking_off + teardown_sec

    # Final source constraint checks after shifting around maintenance.
    if tracking_on < window_start - EPSILON or tracking_off > window_end + EPSILON:
        return None, "candidate_outside_request_time_window"
    if tracking_on < vp_start - EPSILON or tracking_off > vp_end + EPSILON:
        return None, "candidate_outside_transmission_visibility_period"
    if any(overlaps(activity_start, activity_end, ms, me) for ms, me in maint):
        return None, "candidate_overlaps_antenna_maintenance"

    track_id = str(req.get("track_id", ""))
    if not track_id:
        return None, "missing_track_id"

    return {
        "week_key": week_key,
        "week": week,
        "year": year,
        "track_id": track_id,
        "mission_subject": req.get("subject", ""),
        "antenna": antenna,
        "duration_hours": duration,
        "setup_minutes": setup_sec / 60.0,
        "teardown_minutes": teardown_sec / 60.0,
        "tracking_on_epoch": int(round(tracking_on)),
        "tracking_off_epoch": int(round(tracking_off)),
        "activity_start_epoch": int(round(activity_start)),
        "activity_end_epoch": int(round(activity_end)),
        "visibility_start_epoch": int(round(vp_start)),
        "visibility_end_epoch": int(round(vp_end)),
        "request_window_start_epoch": int(round(window_start)),
        "request_window_end_epoch": int(round(window_end)),
        "maintenance_adjusted": tracking_on > earliest_tracking_on + EPSILON,
    }, None


def audit(problems_path: Path, maintenance_path: Path, out_dir: Path) -> int:
    with problems_path.open("r", encoding="utf-8") as handle:
        problems = json.load(handle)
    if not isinstance(problems, dict):
        raise ValueError("problems.json must be a JSON object keyed by week.")
    maintenance = read_maintenance(maintenance_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    rejection_rows: list[dict[str, Any]] = []
    total_requests = total_candidates = 0

    for week_key, requests in problems.items():
        if not isinstance(requests, list):
            print(f"WARNING: {week_key} value is not a request list; skipping.")
            continue

        reasons: Counter[str] = Counter()
        candidates_this_week: list[dict[str, Any]] = []
        malformed = 0
        for req in requests:
            if not isinstance(req, dict):
                reasons["request_is_not_an_object"] += 1
                malformed += 1
                continue
            candidate, reason = candidate_for_request(req, week_key, maintenance)
            if reason:
                reasons[reason] += 1
                rejection_rows.append({
                    "week_key": week_key,
                    "track_id": req.get("track_id", ""),
                    "reason": reason,
                })
            else:
                candidates_this_week.append(candidate)

        n = len(requests)
        c = len(candidates_this_week)
        total_requests += n
        total_candidates += c
        candidate_rows.extend(candidates_this_week)

        row: dict[str, Any] = {
            "week_key": week_key,
            "requests_total": n,
            "candidates_retained": c,
            "retained_percent": round(100.0 * c / n, 3) if n else 0.0,
            "rejected_total": n - c,
            "maintenance_adjusted_candidates": sum(
                bool(x["maintenance_adjusted"]) for x in candidates_this_week
            ),
            "distinct_antennas_in_candidates": len({x["antenna"] for x in candidates_this_week}),
        }
        for reason, count in sorted(reasons.items()):
            row[f"reject__{reason}"] = count
        summary_rows.append(row)

    def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        fieldnames: list[str] = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    write_csv(out_dir / "weekly_summary.csv", summary_rows)
    write_csv(out_dir / "candidate_intervals.csv", candidate_rows)
    write_csv(out_dir / "rejected_requests.csv", rejection_rows)

    report = {
        "audit_type": "restricted_single_antenna_interval_candidate_data_audit",
        "source_problems_file": str(problems_path),
        "source_maintenance_file": str(maintenance_path),
        "weeks_processed": len(summary_rows),
        "total_requests": total_requests,
        "total_candidates": total_candidates,
        "retained_percent": round(100.0 * total_candidates / total_requests, 3)
        if total_requests else 0.0,
        "interpretation": (
            "These are earliest feasible fixed-duration candidates under the stated "
            "filter, not a schedule and not a solution to the full SatNet problem. "
            "Review the restrictions and candidate counts before accepting the project model."
        ),
        "filter": [
            "exactly one resource option, containing exactly one antenna",
            "exactly one visibility period for that antenna",
            "duration equals duration_min",
            "communication interval fits within the request window and TRX ON/OFF window",
            "complete activity including setup and teardown does not overlap antenna maintenance",
        ],
        "important_modeling_note": (
            "The audit models setup/teardown as part of antenna occupancy, while only the "
            "communication interval must fit within the TRX ON/OFF visibility period. "
            "It uses the earliest feasible transmission start. The source benchmark's "
            "full objective is not optimized by this audit."
        ),
    }
    (out_dir / "audit_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    print("\nSATNET DATA AUDIT")
    print("=" * 72)
    print(f"Requests examined: {total_requests}")
    print(f"Candidates retained: {total_candidates}")
    print(f"Retained: {report['retained_percent']}%")
    print("\nWeekly summary:")
    for row in summary_rows:
        print(
            f"  {row['week_key']}: {row['candidates_retained']}/"
            f"{row['requests_total']} retained "
            f"({row['retained_percent']}%)"
        )
    print(f"\nOutputs written to: {out_dir.resolve()}")
    print("  - weekly_summary.csv")
    print("  - candidate_intervals.csv")
    print("  - rejected_requests.csv")
    print("  - audit_report.json")
    print("\nIMPORTANT: These counts test a restricted candidate model; they do not")
    print("establish that earliest-finish-time greedy solves the full SatNet problem.")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problems", help="Path to official problems.json (downloads if omitted)")
    parser.add_argument("--maintenance", help="Path to official maintenance.csv (downloads if omitted)")
    parser.add_argument("--out", default="satnet_audit_output", help="Output directory (default: satnet_audit_output)")
    args = parser.parse_args()

    out_dir = Path(args.out).expanduser().resolve()
    try:
        problems_path = obtain_file(args.problems, "problems.json", PROBLEMS_URL, out_dir)
        maintenance_path = obtain_file(args.maintenance, "maintenance.csv", MAINTENANCE_URL, out_dir)
        return audit(problems_path, maintenance_path, out_dir)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
