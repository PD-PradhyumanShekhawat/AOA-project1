
#!/usr/bin/env python3
"""
Expanded SatNet candidate model.

Scope:
- All listed resource options, including multi-antenna options.
- All combinations of visibility periods for an option.
- Full requested transmission duration.
- Request windows, antenna visibility, setup/teardown, and maintenance.
- Greedy versus exact MILP for the generated fixed candidates.

This is not the full SatNet optimization model because candidate start
times are fixed at their earliest feasible values.
"""
import argparse
import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def read_maintenance(path):
    data = defaultdict(list)
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            key = (int(float(row["week"])), int(float(row["year"])),
                   row["antenna"].strip())
            a, b = float(row["starttime"]), float(row["endtime"])
            if b > a:
                data[key].append((a, b))
    return data


def overlaps(a, b, c, d):
    return a < d and c < b


def earliest_feasible(start, end, duration, setup, teardown, maintenance):
    """Earliest transmission start that fits bounds and avoids maintenance."""
    t = start
    for _ in range(len(maintenance) + 2):
        tx_end = t + duration
        act_start, act_end = t - setup, tx_end + teardown
        conflicts = [(a, b) for a, b in maintenance
                     if overlaps(act_start, act_end, a, b)]
        if not conflicts:
            if t >= start and tx_end <= end:
                return t
            return None
        new_t = max(b + setup for _, b in conflicts)
        if new_t <= t:
            return None
        t = new_t
        if t + duration > end:
            return None
    return None



def generate_candidates(problems, maintenance):
    candidates = []
    rejected = defaultdict(int)

    for week_key, requests in problems.items():
        for req in requests:
            track = str(req.get("track_id", ""))

            try:
                duration = float(req["duration"]) * 3600
                req_start = float(req["time_window_start"])
                req_end = float(req["time_window_end"])
                setup = float(req.get("setup_time", 0)) * 60
                teardown = float(req.get("teardown_time", 0)) * 60
                week = int(req["week"])
                year = int(req["year"])
                options = req["resources"]
                visibility = req["resource_vp_dict"]
            except (KeyError, TypeError, ValueError):
                rejected["invalid_request_fields"] += 1
                continue

            if duration <= 0 or req_end <= req_start:
                rejected["invalid_request_timing"] += 1
                continue

            seen = set()
            found = 0

            for option_index, option in enumerate(options):
                antennas = tuple(sorted(set(option)))

                if not antennas or any(a not in visibility for a in antennas):
                    rejected["missing_resource_visibility"] += 1
                    continue

                period_lists = []
                for antenna in antennas:
                    periods = []
                    for j, vp in enumerate(visibility[antenna]):
                        try:
                            a = float(vp["TRX ON"])
                            b = float(vp["TRX OFF"])
                            if b > a:
                                periods.append((j, a, b))
                        except (KeyError, TypeError, ValueError):
                            continue
                    period_lists.append(periods)

                if any(not periods for periods in period_lists):
                    continue

                for combination in itertools.product(*period_lists):
                    vis_start = max(period[1] for period in combination)
                    vis_end = min(period[2] for period in combination)

                    lower = max(req_start, vis_start)
                    upper = min(req_end, vis_end)

                    if upper - lower < duration:
                        continue

                    # Gather maintenance intervals for every antenna in
                    # this resource option. Each interval is (start, end).
                    maintenance_intervals = []
                    for antenna in antennas:
                        intervals = maintenance.get((week, year, antenna), [])
                        for interval in intervals:
                            if len(interval) != 2:
                                continue
                            maintenance_start = float(interval[0])
                            maintenance_end = float(interval[1])
                            if maintenance_end > maintenance_start:
                                maintenance_intervals.append(
                                    (maintenance_start, maintenance_end)
                                )

                    maintenance_intervals.sort()

                    # earliest_feasible expects a flat list of (start, end)
                    # intervals and accounts for setup and teardown.
                    t = earliest_feasible(
                        lower, upper, duration, setup, teardown,
                        maintenance_intervals
                    )

                    if t is None or t + duration > upper:
                        continue

                    activity_start = int(round(t - setup))
                    activity_end = int(round(t + duration + teardown))
                    tx_start = int(round(t))
                    tx_end = int(round(t + duration))

                    candidate_key = (track, antennas, tx_start, tx_end)
                    if candidate_key in seen:
                        continue
                    seen.add(candidate_key)

                    candidates.append({
                        "week_key": week_key,
                        "track_id": track,
                        "subject": str(req.get("subject", "")),
                        "option_index": option_index,
                        "antennas": ";".join(antennas),
                        "visibility_indices": ";".join(
                            str(period[0]) for period in combination
                        ),
                        "duration_hours": duration / 3600,
                        "tx_start_epoch": tx_start,
                        "tx_end_epoch": tx_end,
                        "activity_start_epoch": activity_start,
                        "activity_end_epoch": activity_end,
                    })
                    found += 1

            if found == 0:
                rejected["no_full_duration_candidate"] += 1

    return candidates, dict(rejected)


def greedy_duration_first(candidates):
    """Feasible heuristic: prefer longer transmissions first."""
    chosen = []
    used_tracks = set()
    used_by_antenna = defaultdict(list)

    ordered = sorted(
        candidates,
        key=lambda c: (-c["duration_hours"],
                       c["activity_end_epoch"],
                       c["activity_start_epoch"],
                       c["track_id"])
    )

    for c in ordered:
        track = (c["week_key"], c["track_id"])
        if track in used_tracks:
            continue
        a, b = c["activity_start_epoch"], c["activity_end_epoch"]
        antennas = c["antennas"].split(";")
        if any(any(overlaps(a, b, x, y)
                   for x, y in used_by_antenna[(c["week_key"], ant)])
               for ant in antennas):
            continue
        chosen.append(c)
        used_tracks.add(track)
        for ant in antennas:
            used_by_antenna[(c["week_key"], ant)].append((a, b))
    return chosen


def solve_milp(candidates):
    """Maximize total communication hours over the fixed candidates."""
    n = len(candidates)
    if n == 0:
        return [], "no_candidates"

    # Every request can be selected at most once.
    track_groups = defaultdict(list)
    antenna_groups = defaultdict(list)
    for i, c in enumerate(candidates):
        track_groups[(c["week_key"], c["track_id"])].append(i)
        for ant in c["antennas"].split(";"):
            antenna_groups[(c["week_key"], ant)].append(i)

    rows = []
    limits = []

    for indices in track_groups.values():
        rows.append({i: 1.0 for i in indices})
        limits.append(1.0)

    # For every pair of overlapping activities on an antenna: x_i+x_j<=1.
    for indices in antenna_groups.values():
        indices.sort(key=lambda i: candidates[i]["activity_start_epoch"])
        for pos, i in enumerate(indices):
            ci = candidates[i]
            for j in indices[pos + 1:]:
                cj = candidates[j]
                if cj["activity_start_epoch"] >= ci["activity_end_epoch"]:
                    break
                if overlaps(ci["activity_start_epoch"], ci["activity_end_epoch"],
                            cj["activity_start_epoch"], cj["activity_end_epoch"]):
                    rows.append({i: 1.0, j: 1.0})
                    limits.append(1.0)

    matrix = lil_matrix((len(rows), n), dtype=float)
    for r, coefficients in enumerate(rows):
        for i, value in coefficients.items():
            matrix[r, i] = value

    # scipy.milp minimizes; negate weights to maximize communication hours.
    weights = np.array([c["duration_hours"] for c in candidates])
    result = milp(
        c=-weights,
        integrality=np.ones(n),
        bounds=Bounds(np.zeros(n), np.ones(n)),
        constraints=LinearConstraint(
            matrix.tocsr(),
            np.zeros(len(rows)),
            np.array(limits)
        ),
        options={"time_limit": 300}
    )

    if result.x is None:
        return [], str(result.message)
    selected = [candidates[i] for i, x in enumerate(result.x) if x > 0.5]
    status = ("optimal" if result.success else
              "feasible_but_not_certified_optimal") + ": " + str(result.message)
    return selected, status


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problems", default="greedy_dsn/data/problems.json")
    parser.add_argument("--maintenance", default="greedy_dsn/data/maintenance.csv")
    parser.add_argument("--out", default="greedy_dsn/results/expanded_model")
    args = parser.parse_args()

    problems = json.loads(Path(args.problems).read_text(encoding="utf-8"))
    maintenance = read_maintenance(Path(args.maintenance))
    candidates, rejected = generate_candidates(problems, maintenance)
    greedy = greedy_duration_first(candidates)
    exact, solver_status = solve_milp(candidates)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "expanded_candidates.csv", candidates)
    write_csv(out / "greedy_selected.csv", greedy)
    write_csv(out / "milp_selected.csv", exact)

    report = {
        "requests_in_dataset": sum(len(v) for v in problems.values()),
        "expanded_candidate_count": len(candidates),
        "greedy_selected_count": len(greedy),
        "greedy_communication_hours": round(
            sum(c["duration_hours"] for c in greedy), 6
        ),
        "milp_selected_count": len(exact),
        "milp_communication_hours": round(
            sum(c["duration_hours"] for c in exact), 6
        ),
        "milp_status": solver_status,
        "rejected_request_reasons": rejected,
        "scope": (
            "Fixed earliest-start candidates across listed resource options "
            "and visibility-period combinations; full requested durations only. "
            "Not the full SatNet optimization problem."
        ),
        "limitations": [
            "Start times are fixed to earliest feasible candidate times.",
            "Shortened durations down to duration_min are not modeled.",
            "The MILP optimum applies only to generated fixed candidates.",
            "The duration-priority greedy heuristic has no optimality guarantee."
        ]
    }
    (out / "expanded_model_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

