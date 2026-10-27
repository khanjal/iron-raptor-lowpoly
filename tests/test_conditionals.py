"""Functions whose nested conditional expressions became if-chains answer exactly as before: vehicles.wheel_role (which side a wheel is on) and species._horse_head (the horse's head colours)."""

import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "art" / "scripts"))

# these scripts import Blender modules at the top but use them only inside functions: import them with stand-ins, then take the stand-ins away again
_stubs = [n for n in ("bpy", "bmesh", "mathutils", "common", "props_lib", "quadruped_rig", "quadruped_builder") if n not in sys.modules]
for _n in _stubs:
    sys.modules[_n] = types.ModuleType(_n)
sys.modules["mathutils"].Vector = lambda *a: a
sys.modules["mathutils"].Matrix = sys.modules["mathutils"].Euler = object
try:
    import species
    import vehicles
finally:
    for _n in _stubs:
        sys.modules.pop(_n, None)


class Point:
    def __init__(self, y):
        self.y = y


class Conditionals(unittest.TestCase):
    def test_wheel_role_names_the_side(self):
        self.assertEqual(vehicles.wheel_role(0.0, 1.234), "Wheel@C@1.23")
        self.assertEqual(vehicles.wheel_role(0.0499, 0.0), "Wheel@C@0.0")
        self.assertEqual(vehicles.wheel_role(0.05, 0.0), "Wheel@L@0.0")
        self.assertEqual(vehicles.wheel_role(0.9, -2.5), "Wheel@L@-2.5")
        self.assertEqual(vehicles.wheel_role(-0.9, -2.5), "Wheel@R@-2.5")
        self.assertEqual(vehicles.wheel_role(-0.05, 2.0), "Wheel@R@2.0")

    def test_horse_head_is_black_only_on_the_muzzle(self):
        for y, colour in ((0.0, "brown_coat"), (-1.26, "brown_coat"), (-1.2601, "brown_coat"), (-1.45, "brown_coat"), (-1.4501, "black"), (-2.0, "black")):
            self.assertEqual(species._horse_head(Point(y), 0), colour, y)


if __name__ == "__main__":
    unittest.main()
