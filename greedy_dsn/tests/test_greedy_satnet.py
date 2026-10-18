import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from greedy_satnet import greedy_schedule, validate_schedule

def item(name, start, end):
    return {"week_key":"W10_2018","track_id":name,
            "activity_start_epoch":str(start),"activity_end_epoch":str(end)}

class GreedyTests(unittest.TestCase):
    def test_classic_example(self):
        data=[item("A",1,4),item("B",3,5),item("C",0,6),item("D",5,7),
              item("E",3,9),item("F",5,9),item("G",6,10),item("H",8,11),
              item("I",8,12),item("J",2,14),item("K",12,16)]
        self.assertEqual([x["track_id"] for x in greedy_schedule(data)],["A","D","H","K"])
    def test_touching_intervals_compatible(self):
        self.assertEqual(len(greedy_schedule([item("A",0,10),item("B",10,20)])),2)
    def test_conflict(self):
        self.assertEqual(len(greedy_schedule([item("A",0,10),item("B",5,15)])),1)
    def test_different_durations_maximize_count(self):
        data=[item("long",0,10),item("s1",0,3),item("s2",3,6),item("s3",6,9)]
        self.assertEqual([x["track_id"] for x in greedy_schedule(data)],["s1","s2","s3"])
    def test_invalid_interval(self):
        with self.assertRaises(ValueError): greedy_schedule([item("bad",5,5)])

if __name__ == "__main__": unittest.main()
