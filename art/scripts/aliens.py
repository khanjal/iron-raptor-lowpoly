"""Aliens that are not humanoid (asset list GA-03...): built as faceted solids, no humanoid rig.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/aliens.py", run_name="__main__")
Exports Assets/Art/Global/Aliens/<name>.fbx. The humanoid aliens (Grey, Shadow Entity, Nordic) are in gp_cast.py.

Energy Being (GA-03): a floating, glowing lozenge of light with orbiting shards and trailing wisps, and two dark slanted eyes on the front
of the core (so it faces somewhere, and the other players can read it as somebody). Its race is a flyer with a custom rig, so this first pass
is a static mesh with the parts as separate pieces for Unity to animate; the emission comes from the palette's glow colour (give that swatch's
material an emission in Unity, or a separate emissive material later).
"""

import importlib
import sys
from math import cos, radians, sin
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import alien_parts
import common
import props_lib
for _m in (common, props_lib, alien_parts):
    importlib.reload(_m)
Prop = props_lib.Prop


def energy_being(name="GA_EnergyBeing_01"):
    p = Prop(name)
    z0 = 1.2                                                        # floats about a metre off the ground
    core = ((-0.55, 0.0001), (-0.3, 0.18), (0.0, 0.30), (0.3, 0.18), (0.55, 0.0001))
    p.loft_rings("glow_cyan", [common.ring_z(z0 + z, 0, 0, r, r, n=6) for z, r in core])      # the core
    p.loft_rings("paint_white", [common.ring_z(z0 + z, 0, 0, r, r, n=6) for z, r in
                                 ((-0.3, 0.0001), (-0.12, 0.10), (0.0, 0.16), (0.12, 0.10), (0.3, 0.0001))])    # a bright heart
    for i in range(6):                                              # orbiting shards
        a = radians(i * 60 + 15)
        p.box("glow_cyan", (cos(a) * 0.55, sin(a) * 0.55, z0 + (0.15 if i % 2 else -0.15)), (0.10, 0.04, 0.26), rot=(0, 0, i * 60 + 15), taper=0.3)
    for i in range(4):                                              # trailing wisps below
        a = radians(i * 90 + 45)
        for k in range(3):
            p.box("glow_cyan", (cos(a) * (0.08 + k * 0.05), sin(a) * (0.08 + k * 0.05), z0 - 0.7 - k * 0.22), (0.06 - k * 0.015, 0.06 - k * 0.015, 0.2), taper=0.5)
    skull = alien_parts.Skull([(z0 + z, 0.0, r, r) for z, r in core], n=6, p=2.0)   # the core's front is flat: two dark eyes sit on it, last so no later loft re-orients them
    bm = p._bm("black")
    for sx in (-1, 1):
        alien_parts.dome(bm, skull, 0.095, z0 + 0.09, 0.085, 0.040, sx, alien_parts.ALMOND, tilt=11, bulge=0.022, rim=0.004)
    return p


ALIENS = {"energy_being": energy_being}   # the Insectoid is in insectoid.py: it has a rig and clips
if __name__ == "__main__":
    names = globals().get("ALIEN_LIST") or list(ALIENS)
    for key in names:
        prop = ALIENS[key]()
        obj, coll = prop.finish()
        print(common.stats(obj))
        common.export_fbx(coll, f"Assets/Art/Global/Aliens/{prop.name}.fbx")
    print("aliens done", names)
