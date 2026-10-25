"""The animals' proportion ranges (art/scripts/animal_proportions.py) agree with the brief (docs/assets/briefs/animals.md), make sense, and hold for the rebuilt species."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "art" / "scripts"))
import animal_proportions as A
import species_pets

NAMES = ("LH", "width", "depth", "elbow", "head", "head_w", "carry", "leg_top", "leg_low", "paw")
SPECIES = {"cat": species_pets.CATS["cat_tabby"], "collie": species_pets.DOGS["dog_collie"], "husky": species_pets.DOGS["dog_husky"]}


def brief_rows():
    """The rows of the brief's proportion table: {species: {ratio: (low, high)}}."""
    text = (ROOT / "docs" / "assets" / "briefs" / "animals.md").read_text(encoding="utf-8")
    block = text.split("## Proportion table", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in block.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == len(NAMES) + 1 and cells[0] in A.RANGES:
            rows[cells[0]] = {n: tuple(float(x) for x in c.split("-")) for n, c in zip(NAMES, cells[1:])}
    return rows


class Ranges(unittest.TestCase):
    def test_every_range_is_ordered_and_complete(self):
        for row, ranges in A.RANGES.items():
            self.assertEqual(set(ranges), set(NAMES), row)
            for name, (lo, hi) in ranges.items():
                self.assertTrue(0 < lo < hi, f"{row} {name}: {lo}-{hi}")

    def test_the_brief_has_the_same_numbers(self):
        rows = brief_rows()
        self.assertEqual(set(rows), set(A.RANGES), "the brief's proportion table and animal_proportions.RANGES list different species")
        for row, ranges in A.RANGES.items():
            self.assertEqual(rows[row], ranges, f"{row}: the brief and the script disagree")

    def test_keys_point_at_rows(self):
        for key, row in A.KEYS.items():
            self.assertIn(row, A.RANGES, key)
        self.assertTrue(A.ENFORCED <= set(A.RANGES))

    def test_check_reports_a_miss(self):
        sp = dict(SPECIES["collie"])
        sp["head"] = [(y * 0.5, z, w, h) for y, z, w, h in sp["head"]]            # a head half as long
        sp["ear_y"] = sp["ear_y"] * 0.5
        self.assertTrue(any(m.startswith("head ") for m in A.check("collie", sp)))


class Rebuilt(unittest.TestCase):
    def test_the_rebuilt_species_are_within_the_ranges(self):
        for row in sorted(A.ENFORCED):
            self.assertEqual(A.check(row, SPECIES[row]), [], row)

    def test_real_sizes(self):
        self.assertTrue(0.22 <= A.measure(SPECIES["cat"])["H"] <= 0.32)
        self.assertTrue(0.46 <= A.measure(SPECIES["collie"])["H"] <= 0.62)
        self.assertTrue(0.50 <= A.measure(SPECIES["husky"])["H"] <= 0.62)


if __name__ == "__main__":
    unittest.main()
