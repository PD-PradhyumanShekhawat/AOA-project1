import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from compare_objectives import weighted_interval_optimum
from greedy_satnet import greedy_schedule


def row(track, start, end, hours):
    return {"week_key":"W", "track_id":str(track), "activity_start_epoch":str(start), "activity_end_epoch":str(end), "requested_duration_hours":str(hours)}


class ObjectiveComparisonTests(unittest.TestCase):
    def test_weighted_dp_beats_cardinality_greedy_on_counterexample(self):
        intervals = [
            row("A", 0, 2, 1),
            row("B", 2, 4, 1),
            row("C", 0, 4, 5),
        ]
        greedy = greedy_schedule(intervals)
        greedy_hours = sum(float(r["requested_duration_hours"]) for r in greedy)

        self.assertAlmostEqual(greedy_hours, 2.0)
        self.assertAlmostEqual(weighted_interval_optimum(intervals), 5.0)
        self.assertLess(greedy_hours, weighted_interval_optimum(intervals))

    def test_weighted_dp_uses_duration_weights(self):
        intervals = [row("short1", 0, 2, 1), row("short2", 2, 4, 1), row("long", 0, 4, 4)]
        self.assertAlmostEqual(weighted_interval_optimum(intervals), 4.0)
        greedy = greedy_schedule(intervals)
        greedy_hours = sum(float(r["requested_duration_hours"]) for r in greedy)
        self.assertLess(greedy_hours, weighted_interval_optimum(intervals))

    def test_empty_input(self):
        self.assertEqual(weighted_interval_optimum([]), 0.0)

if __name__ == "__main__":
    unittest.main()
