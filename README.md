# COT5405 — Analysis of Algorithms Project

## Project overview

This repository contains the implementation and experimental evaluation for the COT5405 Analysis of Algorithms project. The current completed component investigates greedy interval scheduling using historical Deep Space Network (DSN) scheduling data from the SatNet benchmark.

The project separates data auditing, candidate construction, scheduling, testing, and runtime experiments.

## Component 1: DSN antenna activity scheduling

### Problem definition

Each candidate activity is represented by a half-open interval \([s_i,f_i)\), where the interval includes antenna setup, transmission, and teardown.

The objective is to select the maximum number of mutually non-overlapping intervals from a **fixed candidate set**, treating each interval as having unit value. Intervals that touch at an endpoint are compatible.

### Algorithm

The earliest-finish-time greedy algorithm:

1. Sorts activities by finishing time.
2. Selects an activity if its start time is at or after the finish time of the last selected activity.
3. Continues until all candidates have been considered.

Time complexity: \(O(n\log n)\) for sorting and \(O(n)\) for the selection scan. The overall time complexity is \(O(n\log n)\).

### Scope limitation

This is a restricted model, not a solution to the complete SatNet scheduling problem. The data audit constructs one feasible candidate opportunity per retained request for a selected antenna. The greedy algorithm is optimal for the supplied fixed-interval set, but it is not guaranteed to be globally optimal across all visibility opportunities, resource assignments, or the full operational objective.

## Repository structure

- `greedy_dsn/src/` — greedy scheduling implementation.
- `greedy_dsn/scripts/` — data audits and runtime benchmark.
- `greedy_dsn/tests/` — unit tests and randomized optimality verification.
- `greedy_dsn/data/` — source dataset files.
- `greedy_dsn/results/audit_v1/` — initial audit results.
- `greedy_dsn/results/audit_v2/` — revised candidate audit results.
- `greedy_dsn/results/schedule/` — greedy schedule output and summary.
- `greedy_dsn/results/runtime/` — runtime CSV and plots.
- `docs/` — project notes and methodological documentation.

## Requirements

- Python 3.10 or later recommended.
- Matplotlib is required to generate runtime plots.
- The scheduler and audit tests use Python's standard `unittest` framework.

Activate your existing virtual environment before running the commands below.

## Reproduce the tests

From the repository root:

```bash
python -m unittest discover -s greedy_dsn/tests -p 'test_*.py' -v