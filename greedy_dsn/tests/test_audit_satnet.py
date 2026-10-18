import importlib.util
import unittest
from pathlib import Path

script_path = Path(__file__).resolve().parents[1] / "scripts" / "audit_satnet.py"
spec = importlib.util.spec_from_file_location("audit_satnet", script_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SatNetAuditTests(unittest.TestCase):
    def test_half_open_intervals_touching_do_not_overlap(self):
        self.assertFalse(module.overlaps(0, 10, 10, 20))

    def test_actual_overlap_is_detected(self):
        self.assertTrue(module.overlaps(0, 11, 10, 20))

    def test_duration_mismatch_is_rejected(self):
        req = {
            "resources": [["DSS-34"]],
            "resource_vp_dict": {
                "DSS-34": [{"TRX ON": 1000, "TRX OFF": 20000}]
            },
            "duration": 2.0,
            "duration_min": 1.0,
            "setup_time": 60,
            "teardown_time": 15,
            "time_window_start": 1000,
            "time_window_end": 20000,
            "week": 10,
            "year": 2018,
            "track_id": "test-1",
        }
        result, reason = module.candidate_for_request(req, "W10_2018", {})
        self.assertIsNone(result)
        self.assertEqual(reason, "duration_is_not_fixed_at_requested_value")

    def test_valid_request_yields_activity_including_setup_teardown(self):
        req = {
            "resources": [["DSS-34"]],
            "resource_vp_dict": {
                "DSS-34": [{"TRX ON": 1000, "TRX OFF": 10000}]
            },
            "duration": 1.0,
            "duration_min": 1.0,
            "setup_time": 10,
            "teardown_time": 5,
            "time_window_start": 1000,
            "time_window_end": 10000,
            "week": 10,
            "year": 2018,
            "track_id": "test-2",
            "subject": 1,
        }
        result, reason = module.candidate_for_request(req, "W10_2018", {})
        self.assertIsNone(reason)
        self.assertEqual(result["tracking_on_epoch"], 1000)
        self.assertEqual(result["tracking_off_epoch"], 4600)
        self.assertEqual(result["activity_start_epoch"], 400)
        self.assertEqual(result["activity_end_epoch"], 4900)

    def test_maintenance_causes_candidate_to_shift(self):
        req = {
            "resources": [["DSS-34"]],
            "resource_vp_dict": {
                "DSS-34": [{"TRX ON": 1000, "TRX OFF": 20000}]
            },
            "duration": 1.0,
            "duration_min": 1.0,
            "setup_time": 10,
            "teardown_time": 5,
            "time_window_start": 1000,
            "time_window_end": 20000,
            "week": 10,
            "year": 2018,
            "track_id": "test-3",
            "subject": 1,
        }
        maint = {(10, 2018, "DSS-34"): [(500, 2000)]}
        result, reason = module.candidate_for_request(req, "W10_2018", maint)
        self.assertIsNone(reason)
        self.assertTrue(result["maintenance_adjusted"])
        self.assertEqual(result["tracking_on_epoch"], 2600)


if __name__ == "__main__":
    unittest.main()
