import random
from bisect import bisect_right
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GREEDY_SRC = REPO_ROOT / "greedy_dsn" / "src"
if str(GREEDY_SRC) not in sys.path:
    sys.path.insert(0, str(GREEDY_SRC))

from greedy_satnet import greedy_schedule


def dynamic_programming_optimum(intervals):
    ordered = sorted(
        intervals,
        key=lambda x: (
            int(x["activity_end_epoch"]),
            int(x["activity_start_epoch"]),
        ),
    )

    ends = [int(x["activity_end_epoch"]) for x in ordered]
    dp = [0] * (len(ordered) + 1)

    for i, interval in enumerate(ordered, start=1):
        start = int(interval["activity_start_epoch"])

        # Number of intervals ending no later than this interval's start,
        # among the intervals before the current one.
        p = bisect_right(ends, start, 0, i - 1)

        dp[i] = max(dp[i - 1], 1 + dp[p])

    return dp[-1]


def make_interval(index, start, end):
    return {
        "week_key": "SYNTHETIC",
        "track_id": str(index),
        "activity_start_epoch": str(start),
        "activity_end_epoch": str(end),
    }


def main():
    # First, run a deterministic sanity case.
    case = [
        (38, 50), (12, 18), (2, 16), (41, 47), (2, 8),
        (30, 32), (12, 26), (21, 24), (10, 17), (36, 44),
        (9, 12), (8, 9), (45, 46), (48, 53), (45, 55),
    ]
    intervals = [make_interval(i, s, e) for i, (s, e) in enumerate(case)]

    greedy_count = len(greedy_schedule(intervals))
    dp_count = dynamic_programming_optimum(intervals)
    print(f"Deterministic sanity case: greedy={greedy_count}, DP={dp_count}")

    if greedy_count != dp_count:
        raise SystemExit("FAIL: greedy and DP disagree on the counterexample.")

    rng = random.Random(5405)
    for case_number in range(1, 1001):
        n = rng.randint(1, 18)
        intervals = []
        for i in range(n):
            start = rng.randint(0, 50)
            end = start + rng.randint(1, 15)
            intervals.append(make_interval(i, start, end))

        greedy_count = len(greedy_schedule(intervals))
        dp_count = dynamic_programming_optimum(intervals)

        if greedy_count != dp_count:
            print(f"FAIL: random case {case_number}")
            print(f"Greedy={greedy_count}, DP={dp_count}")
            for item in intervals:
                print(item)
            raise SystemExit(1)

    print("PASS: all 1000 random cases matched the DP optimum.")


if __name__ == "__main__":
    main()
