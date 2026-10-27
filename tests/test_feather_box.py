"""biped_bird._feather_box puts one flat box of a turkey's fan feather where the old per-feather lambda put it: `m` metres along the feather from its base."""

import sys
import types
import unittest
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "art" / "scripts"))

# biped_bird.py imports Blender modules at the top but uses them only inside functions: import it with stand-ins, then take the stand-ins away again
_stubs = [n for n in ("bpy", "bmesh", "common", "quadruped_rig") if n not in sys.modules]
for _n in _stubs:
    sys.modules[_n] = types.ModuleType(_n)
try:
    import biped_bird
finally:
    for _n in _stubs:
        del sys.modules[_n]


class Recorder:
    def __init__(self):
        self.calls = []

    def add_box(self, bm, centre, size, rot_deg):
        self.calls.append((bm, centre, size, rot_deg))
        return "box"


class FeatherBox(unittest.TestCase):
    SPEC = {"base": (1.0, 2.0, 3.0), "dir": (0.1, 0.2, 0.3), "width": 0.05, "angle": 20.0}

    def test_the_box_sits_along_the_feather(self):
        c = Recorder()
        built = partial(biped_bird._feather_box, c, self.SPEC, 0.5, 0.27, 0.02)("BM")
        self.assertEqual(built, "box")
        self.assertEqual(c.calls, [("BM", (1.0 + 0.1 * 0.5, 2.0 + 0.2 * 0.5, 3.0 + 0.3 * 0.5), (0.05, 0.27, 0.02), (-6, 0, -20.0))])

    def test_each_feather_keeps_its_own_values(self):
        # partial binds its values when it is made, so a second feather made afterwards does not change what the first one builds
        other = {"base": (0.0, 0.0, 0.0), "dir": (1.0, 0.0, 0.0), "width": 0.1, "angle": 5.0}
        c = Recorder()
        first = partial(biped_bird._feather_box, c, self.SPEC, 0.5, 0.27, 0.02)
        second = partial(biped_bird._feather_box, c, other, 0.4, 0.09, 0.022)
        second("B2")
        first("B1")
        self.assertEqual([call[0] for call in c.calls], ["B2", "B1"])
        self.assertEqual(c.calls[0][1], (0.4, 0.0, 0.0))
        self.assertEqual(c.calls[1][3], (-6, 0, -20.0))


class DroopedFan(unittest.TestCase):
    def test_a_drooped_plate_lies_along_its_bone(self):
        c = Recorder()
        biped_bird._feather_box(c, dict(FeatherBox.SPEC, droop=28.0), 0.1, 0.48, 0.02, "BM")
        self.assertEqual(c.calls[0][3], (-28.0, 0, -20.0))

    def test_the_folded_fan_hangs_and_its_feathers_are_stacked(self):
        import math
        sp = {"tail_fan": {"count": 5, "rest": 3.0, "open": 13.0, "length": 0.4, "width": 0.09, "base": (0.0, 0.4, 0.6), "droop": 30.0, "stack": 0.005}}
        specs = biped_bird.feather_specs(sp)
        self.assertEqual([s["bone"] for s in specs], [f"TailF{i}" for i in range(5)])
        for s in specs:
            self.assertAlmostEqual(math.sqrt(sum(v * v for v in s["dir"])), 1.0)
            self.assertAlmostEqual(math.degrees(math.asin(-s["dir"][2])), 30.0, places=6)
            self.assertAlmostEqual(s["base"][2], 0.6 - 0.005 * abs(s["k"]))


if __name__ == "__main__":
    unittest.main()
