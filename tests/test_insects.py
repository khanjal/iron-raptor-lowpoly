"""The ant and the caterpillar keep their anatomy: the moving parts the rigged GLBs carry (insects.py marks them, insect_anim.py turns them into bones)."""
import json
import struct
import unittest
from pathlib import Path

MODELS = Path(__file__).resolve().parents[1] / "site" / "models"


def node_names(model_id):
    data = (MODELS / f"{model_id}.glb").read_bytes()
    length = struct.unpack("<I", data[12:16])[0]
    return [n.get("name", "") for n in json.loads(data[20:20 + length])["nodes"]]


class Ant(unittest.TestCase):
    def test_six_legs_three_per_side_and_two_antennae(self):
        names = node_names("GN_Ant_01")
        for side in "LR":
            self.assertEqual(sorted(n for n in names if n.startswith(f"Leg_{side}")), [f"Leg_{side}{i}" for i in range(3)])
        self.assertEqual(sorted(n for n in names if n.startswith("Antenna_")), ["Antenna_L", "Antenna_R"])


class Caterpillar(unittest.TestCase):
    def test_head_and_ten_to_thirteen_body_segments(self):
        names = node_names("GN_Caterpillar_01")
        self.assertIn("Head", names)
        segs = sorted(int(n[3:]) for n in names if n.startswith("Seg") and n[3:].isdigit())
        # Seg0 is the body the others move against and is not a bone: Seg1..SegN are all there, with no gap
        self.assertEqual(segs, list(range(1, len(segs) + 1)))
        self.assertTrue(10 <= len(segs) + 1 <= 13, f"{len(segs) + 1} body segments")


if __name__ == "__main__":
    unittest.main()
