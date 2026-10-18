#!/usr/bin/env python3
"""Greedy scheduler for the restricted, fixed-interval SatNet candidate set."""
import argparse, csv, json
from collections import defaultdict
from pathlib import Path

def greedy_schedule(intervals):
    ordered = sorted(intervals, key=lambda x: (
        int(x["activity_end_epoch"]), int(x["activity_start_epoch"]),
        str(x.get("week_key", "")), str(x.get("track_id", ""))))
    chosen, last_end = [], None
    for item in ordered:
        start, end = int(item["activity_start_epoch"]), int(item["activity_end_epoch"])
        if end <= start:
            raise ValueError(f"Invalid interval for {item.get('track_id')}: {start}..{end}")
        if last_end is None or start >= last_end:
            chosen.append(item)
            last_end = end
    return chosen

def validate_schedule(chosen):
    ordered = sorted(chosen, key=lambda x: int(x["activity_start_epoch"]))
    for a, b in zip(ordered, ordered[1:]):
        if int(a["activity_end_epoch"]) > int(b["activity_start_epoch"]):
            raise AssertionError(f"Overlap: {a.get('track_id')} and {b.get('track_id')}")
    return True

def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    required = {"week_key", "track_id", "activity_start_epoch", "activity_end_epoch"}
    if rows and not required.issubset(rows[0]):
        raise ValueError(f"Input CSV needs columns: {sorted(required)}")
    return rows

def write_rows(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default="satnet_audit_v2_output/candidate_intervals.csv")
    p.add_argument("--out", default="satnet_greedy_output")
    args = p.parse_args()
    rows = read_rows(Path(args.input))
    by_week = defaultdict(list)
    for row in rows: by_week[row["week_key"]].append(row)
    out, summary = [], []
    for week in sorted(by_week):
        candidates = by_week[week]
        selected = greedy_schedule(candidates)
        validate_schedule(selected)
        ids = {(x["week_key"], x["track_id"]) for x in selected}
        for row in candidates:
            r = dict(row)
            r["selected_by_greedy"] = "true" if (r["week_key"], r["track_id"]) in ids else "false"
            out.append(r)
        summary.append({"week_key": week, "candidate_count": len(candidates),
            "scheduled_count": len(selected), "rejected_by_conflict_count": len(candidates)-len(selected)})
    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    write_rows(outdir/"greedy_schedule_all_candidates.csv", out)
    write_rows(outdir/"greedy_schedule_selected.csv", [r for r in out if r["selected_by_greedy"]=="true"])
    write_rows(outdir/"greedy_schedule_summary.csv", summary)
    report = {"input_candidate_count": len(rows),
        "scheduled_count": sum(int(r["scheduled_count"]) for r in summary),
        "weeks_scheduled_independently": len(summary),
        "interval_definition": "activity_start_epoch to activity_end_epoch (setup + transmission + teardown)",
        "objective": "maximum number of non-overlapping fixed candidate activity intervals",
        "complexity": "O(n log n) time for sorting plus O(n) scan",
        "scope_warning": "Optimal only for the fixed intervals supplied. Audit v2 selected one earliest feasible opportunity per request, so this is not globally optimal over all possible visibility periods and does not solve full multi-resource SatNet scheduling."}
    (outdir/"greedy_schedule_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("GREEDY SCHEDULER — FIXED CANDIDATE INTERVALS")
    print(f"Candidates: {len(rows)}; scheduled: {report['scheduled_count']}; conflicts skipped: {len(rows)-report['scheduled_count']}")
    for r in summary: print(f"{r['week_key']}: {r['scheduled_count']} of {r['candidate_count']} scheduled")
    print("Outputs:", outdir.resolve())
    print("Scope warning:", report["scope_warning"])

if __name__ == "__main__": main()
