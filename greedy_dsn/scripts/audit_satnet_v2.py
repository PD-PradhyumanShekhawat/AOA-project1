#!/usr/bin/env python3
"""Audit SatNet requests for fixed opportunities on one selected antenna.

This is an audit, not a scheduler for the full SatNet problem.
"""
import argparse, csv, json, math, sys
from collections import Counter
from pathlib import Path

EPS = 1e-9

def overlaps(a, b, c, d):
    return a < d and c < b  # half-open intervals

def read_maintenance(path):
    out = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"week", "year", "starttime", "endtime", "antenna"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"maintenance.csv needs columns {sorted(required)}; got {reader.fieldnames}")
        for rownum, row in enumerate(reader, 2):
            key = (int(float(row["week"])), int(float(row["year"])), row["antenna"].strip())
            a, b = float(row["starttime"]), float(row["endtime"])
            if b <= a:
                raise ValueError(f"Invalid maintenance interval at row {rownum}")
            out.setdefault(key, []).append((a, b))
    for intervals in out.values():
        intervals.sort()
    return out

def has_single_antenna_option(req, antenna):
    resources = req.get("resources")
    return isinstance(resources, list) and any(
        isinstance(option, list) and len(option) == 1 and option[0] == antenna
        for option in resources
    )

def make_candidate(req, week_key, antenna, maintenance):
    if not has_single_antenna_option(req, antenna):
        return None, "no_single_antenna_resource_option_for_selected_antenna"
    vpd = req.get("resource_vp_dict")
    if not isinstance(vpd, dict) or antenna not in vpd:
        return None, "missing_visibility_data_for_selected_antenna"
    vps = vpd[antenna]
    if not isinstance(vps, list) or not vps:
        return None, "no_visibility_periods_for_selected_antenna"
    try:
        duration = float(req["duration"])
        duration_min = float(req["duration_min"])
        setup = float(req.get("setup_time", 0)) * 60
        teardown = float(req.get("teardown_time", 0)) * 60
        req_start, req_end = float(req["time_window_start"]), float(req["time_window_end"])
        week, year = int(req["week"]), int(req["year"])
        track_id = str(req["track_id"])
    except (KeyError, TypeError, ValueError):
        return None, "missing_or_invalid_timing_field"
    values = (duration, duration_min, setup, teardown, req_start, req_end)
    if not all(math.isfinite(x) for x in values):
        return None, "non_finite_timing_field"
    if duration <= 0 or duration_min <= 0 or setup < 0 or teardown < 0:
        return None, "invalid_duration_or_setup_teardown"
    if duration_min > duration + EPS:
        return None, "minimum_duration_exceeds_requested_duration"
    if req_end <= req_start:
        return None, "invalid_request_window"

    duration_s = duration * 3600
    maint = maintenance.get((week, year, antenna), [])
    feasible = []
    for idx, vp in enumerate(vps):
        if not isinstance(vp, dict):
            continue
        try:
            vp_start, vp_end = float(vp["TRX ON"]), float(vp["TRX OFF"])
        except (KeyError, TypeError, ValueError):
            continue
        if not math.isfinite(vp_start) or not math.isfinite(vp_end) or vp_end <= vp_start:
            continue
        tx_start0 = max(req_start, vp_start)
        latest = min(req_end, vp_end) - duration_s
        if tx_start0 > latest + EPS:
            continue
        tx_start = tx_start0
        for _ in range(len(maint) + 2):
            tx_end = tx_start + duration_s
            activity_start, activity_end = tx_start - setup, tx_end + teardown
            conflicts = [(a,b) for a,b in maint if overlaps(activity_start, activity_end, a,b)]
            if not conflicts:
                break
            shifted = max(b + setup for _, b in conflicts)
            if shifted <= tx_start + EPS:
                tx_start = math.inf
                break
            tx_start = shifted
        else:
            tx_start = math.inf
        if not math.isfinite(tx_start):
            continue
        tx_end = tx_start + duration_s
        if tx_start < req_start - EPS or tx_end > req_end + EPS:
            continue
        if tx_start < vp_start - EPS or tx_end > vp_end + EPS:
            continue
        if any(overlaps(tx_start-setup, tx_end+teardown, a,b) for a,b in maint):
            continue
        feasible.append({
            "week_key": week_key, "week": week, "year": year, "track_id": track_id,
            "subject": req.get("subject", ""), "antenna": antenna,
            "visibility_period_index": idx, "requested_duration_hours": duration,
            "minimum_duration_hours": duration_min, "setup_minutes": setup/60,
            "teardown_minutes": teardown/60, "tx_start_epoch": int(round(tx_start)),
            "tx_end_epoch": int(round(tx_end)), "activity_start_epoch": int(round(tx_start-setup)),
            "activity_end_epoch": int(round(tx_end+teardown)),
            "visibility_start_epoch": int(round(vp_start)), "visibility_end_epoch": int(round(vp_end)),
            "request_window_start_epoch": int(round(req_start)), "request_window_end_epoch": int(round(req_end)),
            "maintenance_shifted": tx_start > tx_start0 + EPS
        })
    if not feasible:
        return None, "no_full_requested_duration_opportunity_fits_constraints"
    feasible.sort(key=lambda x: (x["tx_start_epoch"], x["tx_end_epoch"], x["visibility_period_index"]))
    return feasible[0], None

def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        if fields:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

def run(problems_path, maintenance_path, antenna, out_dir):
    problems = json.loads(problems_path.read_text(encoding="utf-8"))
    if not isinstance(problems, dict):
        raise ValueError("problems.json must be an object keyed by week")
    maintenance = read_maintenance(maintenance_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    weekly, candidates, rejected = [], [], []
    for week_key, requests in problems.items():
        reasons = Counter()
        week_candidates = []
        for req in requests:
            if not isinstance(req, dict):
                reasons["request_is_not_an_object"] += 1
                continue
            candidate, reason = make_candidate(req, week_key, antenna, maintenance)
            if reason:
                reasons[reason] += 1
                rejected.append({"week_key": week_key, "track_id": req.get("track_id",""), "reason": reason})
            else:
                week_candidates.append(candidate)
        candidates.extend(week_candidates)
        n = len(requests)
        durations = [x["requested_duration_hours"] for x in week_candidates]
        row = {"week_key": week_key, "requests_total": n, "candidates_retained": len(week_candidates),
               "retained_percent": round(100*len(week_candidates)/n, 3) if n else 0,
               "distinct_duration_values": len(set(durations)),
               "min_duration_hours": min(durations, default=""), "max_duration_hours": max(durations, default=""),
               "maintenance_shifted": sum(bool(x["maintenance_shifted"]) for x in week_candidates)}
        row.update({"reject__"+k:v for k,v in sorted(reasons.items())})
        weekly.append(row)
    write_csv(out_dir/"weekly_summary.csv", weekly)
    write_csv(out_dir/"candidate_intervals.csv", candidates)
    write_csv(out_dir/"rejected_requests.csv", rejected)
    total = sum(x["requests_total"] for x in weekly)
    report = {"antenna": antenna, "requests_total": total, "candidates_retained": len(candidates),
              "retained_percent": round(100*len(candidates)/total,3) if total else 0,
              "warning": "Audit only, not a schedule. Candidates may conflict. Requested durations may differ; earliest-finish-time maximizes count only when selected intervals have equal value, not total communication hours.",
              "candidate_rule": ["at least one resource option contains only selected antenna",
                "evaluate all visibility periods for selected antenna", "use full requested duration",
                "choose earliest feasible opportunity", "include setup/teardown in antenna occupancy and avoid maintenance"]}
    (out_dir/"audit_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSATNET AUDIT V2 — {antenna}\nRequests: {total}\nCandidates: {len(candidates)} ({report['retained_percent']}%)")
    for row in weekly:
        print(f"{row['week_key']}: {row['candidates_retained']}/{row['requests_total']} retained; duration range {row['min_duration_hours']}–{row['max_duration_hours']} h")
    print(f"Outputs: {out_dir.resolve()}")
    print("Review duration values before accepting earliest-finish-time as the final greedy model.")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--problems", required=True)
    p.add_argument("--maintenance", required=True)
    p.add_argument("--antenna", default="DSS-34")
    p.add_argument("--out", default="satnet_audit_v2_output")
    a = p.parse_args()
    try:
        run(Path(a.problems), Path(a.maintenance), a.antenna, Path(a.out))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
