# Objective comparison: cardinality versus communication hours

## Purpose

This experiment checks whether the current earliest-finish-time schedule also maximizes total communication hours on the candidate intervals already produced by `audit_satnet_v2.py`.

## Data and scope

- Source: the supplied SatNet benchmark files in `greedy_dsn/data/`.
- Candidate set: `greedy_dsn/results/audit_v2/candidate_intervals.csv`.
- 874 fixed opportunities on DSS-34 across five 2018 weekly instances.
- Each retained opportunity uses the full requested duration; setup and teardown are included in the occupied interval used for conflict checking.
- Candidate generation chooses only one earliest feasible opportunity per retained request.

## Method

For each week, compare:

1. Earliest-finish-time greedy, which maximizes the number of compatible intervals for a fixed interval set.
2. Weighted interval-scheduling dynamic programming, where each interval's weight is its requested communication duration in hours. The DP is exact for this fixed, single-resource interval set.

The predecessor for each interval is found by binary search over finishing times. Runtime is `O(n log n)` after sorting.

## Results

| Week | Candidates | Greedy count | Greedy hours | Exact weighted-DP hours | Greedy / DP |
|---|---:|---:|---:|---:|---:|
| W10_2018 | 150 | 27 | 52.5 | 97.3 | 53.96% |
| W20_2018 | 190 | 21 | 33.7 | 92.6 | 36.39% |
| W30_2018 | 182 | 24 | 43.6 | 100.4 | 43.43% |
| W40_2018 | 198 | 24 | 43.6 | 91.6 | 47.60% |
| W50_2018 | 154 | 23 | 60.9 | 94.3 | 64.58% |
| **Total** | **874** | **119** | **234.3** | **476.2** | **49.20%** |

## Interpretation

This experiment falsifies the claim that the current earliest-finish-time schedule maximizes communication hours on this fixed candidate set. It does not falsify the classical theorem that earliest-finish-time greedy maximizes the *number* of non-overlapping intervals under the standard interval-scheduling assumptions.

The weighted-DP solution is not a full SatNet optimum. It does not account for all possible start times, all antennas/resource alternatives, arrayed resources, variable or split durations, or the benchmark's fairness metrics. These limitations must remain explicit in any report.

## Reproduction

From repository root:

```bash
python greedy_dsn/scripts/compare_objectives.py
python -m unittest discover -s greedy_dsn/tests -v
```
