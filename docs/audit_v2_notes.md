# SatNet Audit V2 — DSS-34 Candidate Construction

## Purpose

This audit constructs a fixed set of feasible activity intervals for the
DSS-34 antenna from the SatNet request data. It is a preprocessing step for
the greedy interval-scheduling component, not a complete SatNet scheduler.

## Method

The audit examines requests with at least one resource option consisting
solely of DSS-34. It checks the antenna's visibility periods and constructs
an earliest feasible full-duration opportunity while accounting for request
time windows, visibility bounds, setup and teardown, and antenna maintenance.

## Recorded results

- Requests examined: 1,452
- Candidate intervals retained: 874 (60.193%)
- W10_2018: 150 candidates
- W20_2018: 190 candidates
- W30_2018: 182 candidates
- W40_2018: 198 candidates
- W50_2018: 154 candidates

The audit output is stored in `greedy_dsn/results/audit_v2/`.

## Important limitations

The audit chooses one earliest feasible opportunity per retained request.
The greedy scheduler maximizes the number of mutually non-overlapping
intervals within this fixed candidate set. It does not optimize over every
possible visibility opportunity and does not solve the full multi-resource
SatNet scheduling problem.

Activity durations vary, so maximizing the number of scheduled activities
does not necessarily maximize total communication time.

## Reproduction

Run from the repository root:

```bash
python greedy_dsn/scripts/audit_satnet_v2.py \
  --problems greedy_dsn/data/problems.json \
  --maintenance greedy_dsn/data/maintenance.csv \
  --antenna DSS-34 \
  --out greedy_dsn/results/audit_v2

python greedy_dsn/src/greedy_satnet.py \
  --input greedy_dsn/results/audit_v2/candidate_intervals.csv \
  --out greedy_dsn/results/schedule
```
