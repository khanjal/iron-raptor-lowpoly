"""The beetle, ladybug and firefly walk on three legs a side that come out of the underside of the thorax (art/scripts/insect_legs.py)."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "art" / "scripts"))
import insect_legs as L


def bodies(spec):
    return [spec[k] for k in ("elytra", "pronotum", "head", "tail", "belly") if k in spec]


class LegJoints(unittest.TestCase):
    def each(self):
        for name, spec in L.BODIES.items():
            for side in (1, -1):
                for i in range(3):
                    yield name, spec, side, i, L.leg_joints(spec, side, i)

    def test_three_legs_a_side(self):
        for name, spec in L.BODIES.items():
            self.assertEqual(len(spec["legs"]), 3, name)
            ys = [leg[0] for leg in spec["legs"]]
            self.assertEqual(ys, sorted(ys), f"{name}: legs are numbered from the head")
            self.assertEqual(len(set(ys)), 3, name)

    def test_hips_are_on_the_thorax_underside(self):
        for name, spec, side, i, (hip, knee, foot) in self.each():
            y0, y1 = spec["thorax"]
            self.assertTrue(y0 <= hip[1] <= y1, f"{name} leg {i}: hip y {hip[1]} is outside the thorax {y0}..{y1}")
            carriers = [spec[k] for k in spec["carriers"]]
            self.assertTrue(any(L.inside(c, *hip) for c in carriers), f"{name} leg {i}: the hip floats off the body")
            low = min(z for z in (L.underside(c, abs(hip[0]), hip[1]) for c in carriers) if z is not None)
            self.assertLessEqual(hip[2] - low, spec["w"] + 1e-6, f"{name} leg {i}: the hip is buried deep inside")

    def test_shin_is_outside_the_body(self):
        """From the knee down the leg is in the open: no point of the shin is inside any part of the body."""
        for name, spec, side, i, (hip, knee, foot) in self.each():
            for k in range(1, 11):
                t = k / 10
                pt = tuple(knee[j] + (foot[j] - knee[j]) * t for j in range(3))
                for b in bodies(spec):
                    self.assertFalse(L.inside(b, *pt), f"{name} leg {i}: the shin is in the body at t={t}")

    def test_knee_is_clear_of_the_body(self):
        for name, spec, side, i, (hip, knee, foot) in self.each():
            for b in bodies(spec):
                self.assertFalse(L.inside(b, *knee, margin=-spec["w"] * 0.5), f"{name} leg {i}: the knee is inside the body")
            self.assertGreater(abs(knee[0]), abs(hip[0]), f"{name} leg {i}: the thigh goes out")
            self.assertGreaterEqual(knee[2], hip[2], f"{name} leg {i}: the knee is not below the hip")

    def test_foot_stands_on_the_ground_outside_the_body(self):
        for name, spec, side, i, (hip, knee, foot) in self.each():
            self.assertAlmostEqual(foot[2], spec["w"] * 0.5, places=6)
            self.assertGreater(abs(foot[0]), abs(knee[0]), f"{name} leg {i}: the shin goes out")
            self.assertLess(foot[2], knee[2])
            for b in bodies(spec):
                self.assertFalse(L.inside(b, *foot), f"{name} leg {i}: the foot is in the body")

    def test_thigh_and_shin_are_in_proportion(self):
        for name, spec, side, i, (hip, knee, foot) in self.each():
            femur, tibia = math.dist(hip, knee), math.dist(knee, foot)
            self.assertTrue(0.5 < femur / tibia < 1.7, f"{name} leg {i}: femur {femur:.2f} tibia {tibia:.2f}")

    def test_front_legs_reach_forward_and_hind_legs_back(self):
        for name, spec in L.BODIES.items():
            self.assertLess(spec["legs"][0][3], spec["legs"][1][3], name)
            self.assertLess(spec["legs"][1][3], spec["legs"][2][3], name)
            self.assertLess(spec["legs"][0][3], 0, name)
            self.assertGreater(spec["legs"][2][3], 0, name)

    def test_sides_mirror(self):
        for name, spec in L.BODIES.items():
            for i in range(3):
                a, b = L.leg_joints(spec, 1, i), L.leg_joints(spec, -1, i)
                for p, q in zip(a, b):
                    self.assertEqual((p[0], p[1], p[2]), (-q[0], q[1], q[2]))

    def test_ladybug_is_a_dome(self):
        d = L.LADYBUG["elytra"]
        self.assertEqual(d["kind"], "dome")
        self.assertTrue(0.7 <= d["r"][2] / d["r"][0] <= 1.0, "near hemispherical: the dome is nearly as tall as it is wide from the middle")
        self.assertTrue(0.5 < d["base"] < 2.5, "it stands clear of the ground on its legs")


if __name__ == "__main__":
    unittest.main()
