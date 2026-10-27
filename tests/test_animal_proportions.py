"""The animals' proportion ranges (art/scripts/animal_proportions.py) agree with the brief (docs/assets/briefs/animals.md), make sense, and hold for the rebuilt species."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "art" / "scripts"))
import types
import animal_proportions as A
import species_pets

# species.py and biped_bird.py import Blender modules at the top but only use them inside functions: import them with stand-ins, then take the stand-ins away again
_stubs = [n for n in ("bpy", "bmesh", "common", "quadruped_rig") if n not in sys.modules]
for _n in _stubs:
    sys.modules[_n] = types.ModuleType(_n)
try:
    import species
    import biped_bird
finally:
    for _n in _stubs:
        del sys.modules[_n]

NAMES = ("LH", "width", "depth", "elbow", "head", "head_w", "carry", "leg_top", "leg_low", "paw")
SPECIES = {"cat": species_pets.CATS["cat_tabby"], "collie": species_pets.DOGS["dog_collie"], "husky": species_pets.DOGS["dog_husky"],
           **{k: species_pets.DOGS["dog_" + k] for k in ("retriever", "shepherd", "beagle", "bulldog", "dachshund")},
           **{k: species.SPECIES[k] for k in ("cow", "horse", "pig", "sheep", "goat")}}


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
        self.assertLessEqual(A.ENFORCED, set(A.RANGES))

    def test_check_reports_a_miss(self):
        sp = dict(SPECIES["collie"])
        sp["head"] = [(y * 0.5, z, w, h) for y, z, w, h in sp["head"]]            # a head half as long
        sp["ear_y"] = sp["ear_y"] * 0.5
        self.assertTrue(any(m.startswith("head ") for m in A.check("collie", sp)))


class Rebuilt(unittest.TestCase):
    def test_the_rebuilt_species_are_within_the_ranges(self):
        for row in sorted(A.ENFORCED):
            self.assertEqual(A.check(row, SPECIES[row]), [], row)

    def test_the_rebuilt_species_have_the_shape(self):
        for row in sorted(A.ENFORCED):
            self.assertEqual(A.check_shape(row, SPECIES[row]), [], row)

    def test_every_cat_and_dog_has_the_shape(self):
        for key, sp in {**species_pets.DOGS, **species_pets.CATS}.items():
            self.assertEqual(A.check_shape(A.KEYS[key], sp), [], key)

    def test_the_shape_check_fails_a_tube_on_posts(self):
        sp = dict(SPECIES["collie"])
        bottom = min(z - h for _, z, _, h in sp["body"])
        top = max(z + h for _, z, _, h in sp["body"])
        sp["body"] = [(y, (top + bottom) / 2, w, (top - bottom) / 2) for y, _, w, _ in sp["body"]]          # a straight tube: no tuck
        posts = lambda leg: {**leg, "profile": [(min(r[0], bottom), 0.0, r[2], r[3]) for r in leg["profile"]]}      # straight posts that end at the underside
        sp["front"], sp["hind"] = posts(sp["front"]), posts(sp["hind"])
        misses = A.check_shape("collie", sp)
        for name in ("tuck", "front_in", "hind_in", "stifle", "hock"):
            self.assertTrue(any(m.startswith(name + " ") for m in misses), (name, misses))

    def test_the_hen_is_within_its_ranges(self):
        self.assertEqual(A.check_bird(biped_bird.CHICKEN_HEN), [])
        self.assertEqual(set(A.HEN), set(A.measure_bird(biped_bird.CHICKEN_HEN)) - {"H"})

    def test_the_brief_has_the_hens_ranges(self):
        text = (ROOT / "docs" / "assets" / "briefs" / "animals.md").read_text(encoding="utf-8")
        row = [l for l in text.splitlines() if l.startswith("| hen |")][0]
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        head = [l for l in text.splitlines() if l.startswith("| | LH | width | depth | legs")][0]
        names = [c.strip() for c in head.strip().strip("|").split("|")][1:]
        self.assertEqual(names, list(A.HEN))
        self.assertEqual({n: tuple(float(x) for x in c.split("-")) for n, c in zip(names, cells[1:])}, A.HEN)

    def test_farm_animals_are_all_enforced(self):
        self.assertEqual(A.ENFORCED, set(A.RANGES))

    def test_real_sizes(self):
        self.assertTrue(0.22 <= A.measure(SPECIES["cat"])["H"] <= 0.32)
        self.assertTrue(0.46 <= A.measure(SPECIES["collie"])["H"] <= 0.62)
        self.assertTrue(0.50 <= A.measure(SPECIES["husky"])["H"] <= 0.62)
        for key, (lo, hi) in {"dog_retriever": (0.55, 0.62), "dog_shepherd": (0.55, 0.66), "dog_beagle": (0.33, 0.41), "dog_bulldog": (0.31, 0.40),
                              "dog_dachshund": (0.20, 0.25), "dog_stray": (0.40, 0.55)}.items():
            self.assertTrue(lo <= A.measure(species_pets.DOGS[key])["H"] <= hi, key)
        self.assertTrue(0.13 <= A.measure(species_pets.CATS["cat_kitten"])["H"] <= 0.18)
        for row, (lo, hi) in {"cow": (1.30, 1.55), "horse": (1.45, 1.65), "pig": (0.75, 1.0), "sheep": (0.65, 0.85), "goat": (0.70, 0.90)}.items():
            self.assertTrue(lo <= A.measure(SPECIES[row])["H"] <= hi, row)


if __name__ == "__main__":
    unittest.main()
