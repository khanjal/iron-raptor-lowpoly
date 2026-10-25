"""The people's proportion ranges (art/scripts/people_proportions.py) agree with the brief (docs/assets/briefs/people.md), make sense, and hold for the body gp_builder.py builds."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "art" / "scripts"))
import people_proportions as P


def brief_rows():
    text = (ROOT / "docs" / "assets" / "briefs" / "people.md").read_text(encoding="utf-8")
    block = text.split("## Proportion table", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in block.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in P.RANGES:
            rows[cells[0]] = (float(cells[1]), float(cells[2]))
    return rows


class Ranges(unittest.TestCase):
    def test_every_range_is_ordered(self):
        for name, (lo, hi) in P.RANGES.items():
            self.assertTrue(0 < lo < hi, name)

    def test_the_brief_has_the_same_numbers(self):
        self.assertEqual(brief_rows(), P.RANGES)

    def test_the_body_is_inside_the_ranges(self):
        self.assertEqual(P.check(), [])

    def test_measure_covers_every_range(self):
        self.assertEqual(set(P.measure()), set(P.RANGES))

    def test_check_reports_a_miss(self):
        t = P.tables()
        t["HAND"] = [(0.80, *t["HAND"][0][1:]), (0.87, *t["HAND"][-1][1:])]      # the old short paddle of a hand
        problems = P.check(P.measure(t))
        self.assertTrue(any(p.startswith("hand ") for p in problems), problems)

    def test_check_reports_the_old_stick_figure(self):
        t = P.tables()
        t["TORSO"] = [(0.90, 0.01, 0.170, 0.105), (1.05, 0.01, 0.160, 0.100), (1.20, 0.00, 0.150, 0.095),
                      (1.32, 0.00, 0.185, 0.110), (1.43, 0.00, 0.215, 0.108), (1.50, 0.00, 0.110, 0.080)]
        t["LEG"] = [list(r) for r in t["LEG"]]
        t["LEG"][3][2] = 0.058                                                    # the old calf
        problems = " ".join(P.check(P.measure(t)))
        for name in ("chest_d", "seat", "calf"):
            self.assertIn(name + " ", problems)

    def test_the_builder_uses_the_hand_table(self):
        self.assertIn("ARM[:5] + HAND", P.SOURCE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
