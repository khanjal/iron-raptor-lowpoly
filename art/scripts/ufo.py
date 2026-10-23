"""The abduction UFO (issue #148): the small craft that flies in for a tagged cow. A smaller cousin of the crashed ship (GV_CrashedShip_01 in vehicles.py),
in the same design language: pale `alien_grey` hull, dark belly and trim, a glass dome, and `glow_cyan` wherever there is energy.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/ufo.py", run_name="__main__")
Exports Assets/Art/Global/Ships/SH_AbductionUfo_01.fbx.

6.7 m across and 3.3 m tall, a flyer: the origin is at the centre of the underside (the emitter disc the beam comes out of), facing -Y like every model.
The glow swatch (rim band, emitter, belly lamps, dome tip) is the one Unity makes emissive. Nothing here moves: Unity spins and tilts the whole model.
"""

import importlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop

NAME = "SH_AbductionUfo_01"


def abduction_ufo():
    p = Prop(NAME)
    lathe = props_lib.lathe

    # the dark belly, narrowing to the emitter; the pale hull over the rim; the dome on top
    lathe(p, "alien_dark", [(0.08, 0.95), (0.3, 1.8), (0.7, 3.0), (0.9, 3.3)], n=12)
    lathe(p, "alien_grey", [(0.9, 3.3), (1.15, 3.35), (1.45, 3.0), (1.8, 2.3), (2.05, 1.5)], n=12)
    lathe(p, "metal_dark", [(1.1, 3.37), (1.2, 3.37)], n=12, cap=False)                  # a dark panel line round the rim
    lathe(p, "glow_cyan", [(0.62, 3.14), (0.82, 3.3)], n=12, cap=False)                  # the glowing band under the rim
    lathe(p, "clear_glass", [(1.95, 1.35), (2.45, 1.1), (2.95, 0.55), (3.25, 0.0001)], n=8)    # the dome
    p.cyl("glow_cyan", (0, 0, 0.04), 0.9, 0.08, n=12)                                    # the emitter the beam comes out of
    p.cyl("metal_dark", (0, 0, 0.12), 1.05, 0.08, n=12)                                  # its dark collar (above the disc: the disc shows from below)

    # belly lamps, a ring of six; three stubby stabiliser fins and a short mast on the dome
    for k in range(6):
        a = math.radians(k * 60 + 30)
        p.box("glow_cyan", (2.35 * math.cos(a), 2.35 * math.sin(a), 0.42), (0.34, 0.34, 0.16), rot=(0, 0, math.degrees(a)))
    for k in range(3):
        a = math.radians(k * 120 + 90)
        p.box("metal_dark", (3.35 * math.cos(a), 3.35 * math.sin(a), 1.05), (0.9, 0.16, 0.42), rot=(0, 0, math.degrees(a)))
    p.cyl("metal_dark", (0, 0, 3.3), 0.05, 0.5, n=6)
    p.cyl("glow_cyan", (0, 0, 3.58), 0.1, 0.12, n=6)
    return p


def run():
    prop = abduction_ufo()
    obj, coll = prop.finish()
    print(common.stats(obj))
    common.export_fbx(coll, f"Assets/Art/Global/Ships/{prop.name}.fbx")
    print("ufo done")


if __name__ == "__main__":
    run()
