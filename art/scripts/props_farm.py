"""Farm props, tools and fittings (asset list GT-, GI-, GL-, FM-): flat faceted models from simple solids.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/props_farm.py", run_name="__main__")
Optional global PROP_LIST to build only some, e.g. PROP_LIST = ["barrel", "crate"]. Each exports to
Assets/Art/<Global or Farm>/Props/<name>.fbx. Props stand in a row along X for looking at.

Sizes are real: a rake is 1.6 m, a barrel 0.9 m tall, a square bale 0.9 x 0.45 x 0.45 m. Every prop is built facing -Y with its
origin on the floor at the centre of its base. Add a prop by writing a function that returns a Prop and listing it in PROPS.
"""

import importlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
from props_lib import Prop, wheel
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
wheel = props_lib.wheel
gable_roof = props_lib.gable_roof


def rake():
    p = Prop("GT_Rake_01")
    p.cyl("wood_light", (0, 0, 0.82), 0.016, 1.4, n=6)                                  # from inside the socket (up from z 0.12) to the top
    p.box("metal_dark", (0, -0.0, 0.03), (0.42, 0.03, 0.03))
    for i in range(8):
        p.box("metal_galv", (-0.18 + i * 0.0514, 0.0, 0.035), (0.012, 0.012, 0.07), taper=0.5)
    p.box("metal_dark", (0, 0, 0.095), (0.036, 0.036, 0.15))                            # the socket: from the head bar (z 0.015-0.045) up to z 0.17
    return p


def shovel():
    p = Prop("GT_Shovel_01")
    p.cyl("wood_light", (0, 0, 0.775), 0.016, 1.01, n=6)                                 # from inside the socket (z 0.27) to inside the D handle (z 1.28)
    p.box("wood_light", (0, 0, 1.28), (0.12, 0.02, 0.03))              # D handle
    p.box("metal_galv", (0, -0.03, 0.15), (0.22, 0.012, 0.30), taper=0.55)
    p.box("metal_dark", (0, -0.01, 0.32), (0.035, 0.056, 0.12))                         # the socket: it holds the shaft and touches the blade
    return p


def pitchfork():
    p = Prop("GT_Pitchfork_01")
    p.cyl("wood_light", (0, 0, 0.99), 0.016, 1.48, n=6)                                  # from inside the socket (z 0.25) to the top
    p.box("metal_dark", (0, 0, 0.3), (0.035, 0.035, 0.12))                              # the socket the handle sits in
    p.box("metal_dark", (0, 0, 0.26), (0.20, 0.014, 0.014))
    for x in (-0.09, 0.0, 0.09):
        p.box("metal_dark", (x, 0, 0.13), (0.012, 0.012, 0.26), taper=0.3)
    return p


def barrel():
    p = Prop("GT_Barrel_01")
    p.cyl("wood_dark", (0, 0, 0.45), 0.29, 0.9, n=10, top_radius=0.27)
    for z in (0.14, 0.45, 0.76):
        p.cyl("metal_dark", (0, 0, z), 0.305, 0.04, n=10)
    p.cyl("wood_light", (0, 0, 0.9), 0.26, 0.012, n=10)
    return p


def crate():
    p = Prop("GT_Crate_01")
    p.box("wood_light", (0, 0, 0.25), (0.5, 0.5, 0.5))
    for z in (0.06, 0.25, 0.44):
        p.box("wood_dark", (0, -0.255, z), (0.52, 0.01, 0.07))
        p.box("wood_dark", (0, 0.255, z), (0.52, 0.01, 0.07))
        p.box("wood_dark", (-0.255, 0, z), (0.01, 0.52, 0.07))
        p.box("wood_dark", (0.255, 0, z), (0.01, 0.52, 0.07))
    return p


def milk_can():
    p = Prop("GT_MilkCan_01")
    p.cyl("metal_galv", (0, 0, 0.22), 0.17, 0.44, n=8, top_radius=0.15)
    p.cyl("metal_galv", (0, 0, 0.5), 0.09, 0.12, n=8, top_radius=0.085)
    p.cyl("metal_galv", (0, 0, 0.575), 0.12, 0.03, n=8)
    p.cyl("metal_dark", (0, 0, 0.605), 0.04, 0.05, n=6)
    for s in (-1, 1):
        p.box("metal_dark", (s * 0.17, 0, 0.36), (0.03, 0.05, 0.1))
    return p


def hay_square():
    p = Prop("GT_HayBale_Square_01")
    p.box("hay", (0, 0, 0.225), (0.9, 0.45, 0.45))
    for x in (-0.22, 0.22):
        p.box("wood_dark", (x, 0, 0.23), (0.02, 0.47, 0.46))                # the twine
    return p


def hay_round():
    p = Prop("GT_HayBale_Round_01")
    p.cyl("hay", (0, 0, 0.6), 0.6, 1.2, n=12, axis="y")
    p.cyl("wood_dark", (0, 0, 0.6), 0.605, 0.03, n=12, axis="y")
    p.cyl("hay", (0, -0.6, 0.6), 0.45, 0.01, n=12, axis="y")
    return p


def wheelbarrow():
    p = Prop("GT_Wheelbarrow_01")
    # two wooden beams from the front fork, under the tub, rising to the handles at the back
    for sx in (-1, 1):
        p.box("wood_light", (sx * 0.29, 0.225, 0.425), (0.04, 1.4, 0.04), rot=(14.5, 0, 0))   # beside the tub (its sloping sides reach x 0.29 at the top), not through it
        p.box("wood_light", (sx * 0.29, 0.75, 0.27), (0.04, 0.04, 0.54))                  # legs, up to the beams
        p.box("metal_dark", (sx * 0.185, -0.43, 0.23), (0.23, 0.03, 0.05))                # fork, beam to axle
        p.box("metal_dark", (sx * 0.07, -0.45, 0.18), (0.03, 0.03, 0.1))                  # hanger, to the hub (x +-0.06)
    # the tub is an open tray: a floor and four sloping sides, wider at the top
    p.box("metal_dark", (0, 0.0, 0.43), (0.44, 0.7, 0.03))
    p.box("wood_light", (0, 0.22, 0.395), (0.58, 0.05, 0.04))                              # the tub rests on a cross-member at the back, from beam to beam...
    for sx in (-1, 1):
        p.box("wood_light", (sx * 0.245, -0.22, 0.375), (0.06, 0.05, 0.09))                # ...and on a block on each beam at the front
    for sx in (-1, 1):
        p.box("metal_dark", (sx * 0.255, 0.0, 0.53), (0.03, 0.76, 0.22), rot=(0, sx * 12, 0))
    for sy in (-1, 1):
        p.box("metal_dark", (0, sy * 0.37, 0.53), (0.52, 0.03, 0.22), rot=(-sy * 12, 0, 0))
    p.cyl("rubber", (0, -0.45, 0.18), 0.18, 0.06, n=10, axis="x")                         # wheel
    p.cyl("metal_galv", (0, -0.45, 0.18), 0.05, 0.12, n=6, axis="x")
    return p


def jerrycan():
    p = Prop("GT_Jerrycan_01")
    p.box("cloth_red", (0, 0, 0.225), (0.34, 0.16, 0.45))
    p.box("cloth_red", (-0.08, 0, 0.47), (0.12, 0.16, 0.04))
    p.cyl("black", (0.1, 0, 0.48), 0.03, 0.06, n=6)
    return p


def feed_sack():
    p = Prop("GT_FeedSack_01")
    p.box("cream", (0, 0, 0.3), (0.42, 0.22, 0.6), taper=0.9)
    p.box("cream", (0, 0, 0.62), (0.34, 0.16, 0.06), taper=0.7)
    p.box("cloth_red", (0, -0.1, 0.3), (0.22, 0.02, 0.14))
    return p


def fence_section():
    p = Prop("GI_FenceSection_01")
    for x in (-1.2, 1.2):
        p.box("wood_grey", (x, 0, 0.6), (0.12, 0.12, 1.2))
    for z in (0.35, 0.7, 1.05):
        p.box("wood_grey", (0, 0.02, z), (2.4, 0.04, 0.12))
    return p


def gate():
    p = Prop("GI_Gate_01")
    p.box("wood_grey", (-1.45, 0, 0.7), (0.14, 0.14, 1.4))
    for z in (0.3, 0.65, 1.0, 1.3):
        p.box("wood_light", (0, 0, z), (2.8, 0.05, 0.1))
    for x in (-1.3, 0.0, 1.3):
        p.box("wood_light", (x, 0.0, 0.8), (0.08, 0.04, 1.1))
    p.box("wood_light", (0, 0, 0.8), (2.3, 0.04, 0.08), rot=(0, 24, 0))
    p.box("metal_dark", (1.35, -0.03, 1.0), (0.1, 0.04, 0.04))
    return p


def mailbox():
    p = Prop("GT_MailboxPost_01")
    p.box("wood_grey", (0, 0, 0.55), (0.08, 0.08, 1.1))
    p.box("metal_dark", (0, 0, 1.15), (0.24, 0.42, 0.2))
    p.box("cloth_red", (0.125, 0.05, 1.22), (0.03, 0.1, 0.08))
    return p


def bare_bulb():
    p = Prop("GL_BareBulb_01")
    p.cyl("black", (0, 0, 0.6), 0.008, 1.2, n=4)                          # the cord, hanging from the origin upwards
    p.cyl("metal_dark", (0, 0, 0.02), 0.03, 0.05, n=6)
    p.cyl("glow_cyan", (0, 0, -0.04), 0.035, 0.08, n=8, top_radius=0.02)
    return p


def pole_lamp():
    p = Prop("GL_PoleLamp_01")
    p.cyl("wood_dark", (0, 0, 3.0), 0.09, 6.0, n=8, top_radius=0.07)
    p.box("wood_dark", (0, -0.4, 5.85), (0.07, 0.8, 0.07))
    p.cyl("metal_dark", (0, -0.8, 5.78), 0.18, 0.1, n=8, top_radius=0.06)
    p.cyl("glow_cyan", (0, -0.8, 5.7), 0.1, 0.06, n=8)
    return p


def doghouse():
    """Hollow: a floor, four plank walls with a real doorway, a gable roof. Room for a dog inside."""
    p = Prop("FM_DogHouse_01")
    t = 0.04
    p.box("wood_light", (0, 0, 0.02), (0.8, 1.0, 0.04))                                   # floor
    p.box("wood_light", (0, 0.48, 0.37), (0.8, t, 0.66))                                  # back
    for sx in (-1, 1):
        p.box("wood_light", (sx * 0.38, 0.0, 0.37), (t, 1.0, 0.66))                       # sides
        p.box("wood_light", (sx * 0.285, -0.48, 0.37), (0.23, t, 0.66))                   # front, either side of the doorway
    p.box("wood_light", (0, -0.48, 0.59), (0.34, t, 0.22))                                # front, above the doorway
    gable_roof(p, "wood_dark", 0, 0, 0.8, 1.0, 0.7, 0.3, overhang=0.08, along="y")           # a solid gable roof: front and back are closed
    return p


def generator():
    p = Prop("FM_Generator_01")
    p.box("metal_dark", (0, 0, 0.5), (0.9, 0.6, 0.7))
    p.box("paint_yellow", (0, 0.0, 0.88), (0.86, 0.56, 0.08))
    p.box("metal_dark", (0, -0.31, 0.5), (0.5, 0.02, 0.4))
    p.cyl("metal_galv", (0.3, 0.25, 1.05), 0.04, 0.3, n=6)
    for x in (-0.38, 0.38):
        p.box("rubber", (x, 0.2, 0.08), (0.06, 0.4, 0.16))
        p.box("rubber", (x, -0.2, 0.08), (0.06, 0.4, 0.16))
    p.cyl("glow_cyan", (-0.25, -0.325, 0.62), 0.04, 0.012, n=6, axis="y")
    return p


def water_trough():
    p = Prop("FM_WaterTrough_01")
    p.box("wood_grey", (0, 0, 0.05), (1.6, 0.5, 0.1))                                   # the bottom
    for sy in (-1, 1):
        p.box("wood_grey", (0, sy * 0.22, 0.3), (1.6, 0.06, 0.6))                        # the long sides
    for sx in (-1, 1):
        p.box("wood_grey", (sx * 0.77, 0, 0.3), (0.06, 0.5, 0.6))                        # the ends
    p.box("glass", (0, 0, 0.45), (1.48, 0.38, 0.03))                                     # the water, 13 cm below the rim
    for x in (-0.7, 0.7):
        p.box("wood_dark", (x, 0, 0.15), (0.08, 0.56, 0.3))
    return p


def stool():
    p = Prop("GT_Stool_01")
    p.cyl("wood_light", (0, 0, 0.46), 0.17, 0.05, n=8)
    for a, (x, y) in enumerate(((0.1, 0.1), (-0.1, 0.1), (0.1, -0.1), (-0.1, -0.1))):
        p.cyl("wood_dark", (x, y, 0.22), 0.025, 0.44, n=5, top_radius=0.02)
    return p


def _pile(p, rows, r=0.09, length=0.5):
    """Split logs lying along Y, touching: `rows` is the log count of each row from the bottom, each row centred on the one below."""
    for row, count in enumerate(rows):
        for i in range(count):
            x = (i - (count - 1) / 2) * 2 * r
            z = r * 0.887 + row * r * 1.732                       # the lowest log lies on a flat face
            p.cyl("wood_dark" if (i + row) % 2 else "wood_light", (x, 0, z), r, length, n=6, axis="y")


def firewood_stack():
    """The rack: a rectangular stack, 8 and 7 logs alternating, held by a pair of stakes at each end."""
    p = Prop("GT_FirewoodStack_01")
    r, rows = 0.09, (8, 7, 8, 7, 8)
    _pile(p, rows, r)
    half = 8 * r + 0.05
    for sx in (-1, 1):
        for sy in (-0.2, 0.2):
            p.box("wood_grey", (sx * half, sy, 0.45), (0.06, 0.06, 0.9))
    for sy in (-0.2, 0.2):
        p.box("wood_grey", (0, sy, 0.9), (2 * half, 0.05, 0.05))                          # a rail across the top of each pair
    return p


def firewood_triangle():
    """A self-supporting triangular pile: 6 logs in the bottom row, one on top, a stake at each end."""
    p = Prop("GT_FirewoodStack_Triangle_01")
    r, rows = 0.085, 6
    _pile(p, tuple(range(rows, 0, -1)), r)
    for sx in (-1, 1):
        p.box("wood_grey", (sx * (rows * r + 0.03), 0, 0.3), (0.05, 0.06, 0.6))
    return p


def firewood_small():
    """A low, short stack of four rows against nothing: 5, 4, 3, 2."""
    p = Prop("GT_FirewoodStack_Small_01")
    _pile(p, (5, 4, 3, 2), 0.085, 0.45)
    return p


def firewood_loose():
    """A loose heap of split logs thrown down in different directions, deterministic."""
    import random
    rng = random.Random(7)
    p = Prop("GT_FirewoodPile_Loose_01")
    layers = ((7, 0.32, 0.0665), (5, 0.24, 0.16), (3, 0.14, 0.25), (1, 0.0, 0.33))
    for count, spread, z in layers:
        for _ in range(count):
            a = rng.uniform(0, 360)
            d = rng.uniform(0, spread)
            x, y = d * math.cos(math.radians(a)), d * math.sin(math.radians(a))
            # seeded modelling variation, not security
            p.cyl("wood_dark" if rng.random() < 0.5 else "wood_light", (x, y, z), 0.075, rng.uniform(0.4, 0.55), n=6, axis="y",  # NOSONAR
                  rot=(0, 0, rng.uniform(0, 180)))
    return p


def chopping_block():
    """A stump with an axe in it and a few split logs beside it."""
    p = Prop("GT_ChoppingBlock_01")
    p.cyl("bark", (0, 0, 0.2), 0.26, 0.4, n=8, top_radius=0.24)
    p.cyl("wood_light", (0, 0, 0.405), 0.23, 0.01, n=8)
    p.cyl("wood_dark", (0.116, 0.0, 0.67), 0.018, 0.55, n=5, rot=(0, 25, 0))                # the handle, up from the head
    p.box("metal_galv", (0.0, 0.0, 0.46), (0.04, 0.16, 0.1))                                 # the head, bitten into the top of the block
    for k, (x, y, yaw) in enumerate(((0.5, 0.3, 20), (0.62, -0.1, 80), (0.45, -0.35, 150))):
        p.cyl("wood_grey", (x, y, 0.0621), 0.07, 0.4, n=6, axis="y", rot=(0, 0, yaw))
    return p


def scarecrow():
    p = Prop("FM_Scarecrow_01")
    p.cyl("wood_dark", (0, 0, 0.9), 0.04, 1.8, n=5)
    p.box("wood_dark", (0, 0, 1.45), (1.3, 0.05, 0.05))
    p.box("cloth_red", (0, 0, 1.3), (0.4, 0.2, 0.55))
    for s in (-1, 1):
        p.box("cloth_red", (s * 0.4, 0, 1.4), (0.5, 0.12, 0.1))
        p.box("denim", (s * 0.12, 0, 0.8), (0.14, 0.14, 0.7))
    p.cyl("hay", (0, 0, 1.72), 0.15, 0.28, n=8)
    p.box("black", (0, -0.15, 1.74), (0.2, 0.01, 0.03))
    p.cyl("wood_dark", (0, 0, 1.88), 0.24, 0.02, n=10)
    p.cyl("wood_dark", (0, 0, 1.96), 0.12, 0.16, n=8)
    return p


def landline_phone():
    p = Prop("GE_LandlinePhone_01")
    p.box("black", (0, 0, 0.05), (0.22, 0.24, 0.1))
    p.box("black", (0, 0, 0.115), (0.24, 0.07, 0.04))
    p.box("black", (-0.1, 0, 0.13), (0.05, 0.09, 0.05))
    p.box("black", (0.1, 0, 0.13), (0.05, 0.09, 0.05))
    p.cyl("metal_galv", (0, -0.075, 0.1), 0.05, 0.012, n=8)
    return p


# ---- The power line (issue #144): utility poles with a crossarm and insulators, and the meter box on the farmhouse wall -------------
# Wire attach points (the Unity side, Assets/Editor/FarmsteadPowerLines.cs, hangs the wires from these; pole at the origin, arm along X
# on the +Z side of the pole after the import; Blender's +X arrives as -X in Unity, so what is at Blender +X is on the pole's -X side there): top arm at 7.45 m, insulators at x = -0.9 and +0.9, wire sits 7.70 m up; the middle wire sits on a pin on the pole top, 8.215 m up. The corner pole has its top
# arm along Y (the road line) and a lower arm along X at 6.35 m, wire 6.60 m up. The transformer pole has two spools on its Unity -X side (Blender +X, the side facing the house) at 6.15 and 6.50, the can on its Unity +X side.

ARM_Z = 7.45
ARM_FACE = -0.185          # arms are bolted on the front (-Y) face of the pole


def pin_insulator(p, x, y, z):
    """A pin insulator standing on z: an iron pin, a wide skirt and a narrower head; the wire sits 0.17 m above z."""
    p.cyl("metal_dark", (x, y, z + 0.04), 0.018, 0.08, n=5)
    p.cyl("porcelain", (x, y, z + 0.085), 0.058, 0.05, n=7, top_radius=0.05)
    p.cyl("porcelain", (x, y, z + 0.14), 0.04, 0.06, n=7, top_radius=0.03)


def utility_pole_body(p):
    """A tapered 8 m pole (0.34 m across at the foot, 0.22 at the top), a weathered butt band and a cap."""
    p.cyl("wood_grey", (0, 0, 4.0), 0.17, 8.0, n=8, top_radius=0.11)
    p.cyl("wood_dark", (0, 0, 1.0), 0.175, 0.5, n=8, top_radius=0.17)        # the creosoted butt
    p.cyl("wood_dark", (0, 0, 8.02), 0.10, 0.05, n=8, top_radius=0.05)       # a little cap
    pin_insulator(p, 0, 0, 8.045)                                            # the middle wire sits on a pin on the top of the pole (wire 8.215 m up), not on the arm: it would run through the pole
    p.box("metal_dark", (0, -0.13, 3.0), (0.03, 0.02, 2.4))                  # the ground wire's strap down the front


def _crossarm_x(p, z, face, reach, braces, middle):
    """A crossarm on the front face of the pole (along x)."""
    p.box("wood_dark", (0, face + 0.02, z), (2.0 * reach, 0.15, 0.13))      # 0.15 deep, its front face stays at face - 0.055 and its back goes into the pole
    for x in ((-0.9 * reach, 0.0, 0.9 * reach) if middle else (-0.9 * reach, 0.9 * reach)):
        pin_insulator(p, x, face, z + 0.065)
    if braces:
        for s in (-1, 1):
            props_lib.rod(p, "metal_galv", (s * 0.06, face * 0.54, z - 0.75), (s * 0.7, face, z - 0.05), w=0.035, h=0.05)


def _crossarm_y(p, z, face, reach, braces, middle):
    """A crossarm on the Blender -X face of the pole (along y)."""
    x0 = face                                                            # the Blender -X face: Unity +X, where the road wires are tied
    p.box("wood_dark", (x0 + 0.02, 0, z), (0.15, 2.0 * reach, 0.13))
    for y in ((-0.9 * reach, 0.0, 0.9 * reach) if middle else (-0.9 * reach, 0.9 * reach)):
        pin_insulator(p, x0, y, z + 0.065)
    if braces:
        for s in (-1, 1):
            props_lib.rod(p, "metal_galv", (x0 * 0.54, s * 0.06, z - 0.75), (x0, s * 0.7, z - 0.05), w=0.05, h=0.035)


def crossarm(p, z, along="x", face=-0.185, reach=1.0, braces=True, middle=False):
    """A crossarm 2 m long with a pin insulator at each end (and in the middle if `middle`: only the lower arm, the top arm's middle wire sits on the pole top) and two angle braces. along x: on the front face, along y: on the +X face."""
    if along == "x":
        _crossarm_x(p, z, face, reach, braces, middle)
    else:
        _crossarm_y(p, z, face, reach, braces, middle)


def utility_pole():
    p = Prop("GL_UtilityPole_01")
    utility_pole_body(p)
    crossarm(p, ARM_Z)
    return p


def utility_pole_corner():
    """Where the line turns: the road line on the top arm (along Y), the branch to the farm on a lower arm (along X)."""
    p = Prop("GL_UtilityPoleCorner_01")
    utility_pole_body(p)
    crossarm(p, ARM_Z, along="y")
    crossarm(p, 6.35, along="x", middle=True)
    return p


def utility_pole_transformer():
    """The last pole of the farm's branch: a pole-top transformer on the Unity +X side and the secondary spools on the Unity -X side (Blender +X: the X axis is mirrored on import), where the service drop starts."""
    p = Prop("GL_UtilityPoleTransformer_01")
    utility_pole_body(p)
    crossarm(p, ARM_Z)
    p.box("metal_dark", (-0.2, 0, 6.85), (0.34, 0.07, 0.07))                 # the hanger
    p.cyl("metal_galv", (-0.5, 0, 6.45), 0.2, 0.64, n=10)                    # the can
    p.cyl("metal_galv", (-0.5, 0, 6.8), 0.2, 0.06, n=10, top_radius=0.15)    # its lid
    for y in (-0.08, 0.08):
        p.cyl("porcelain", (-0.5, y, 6.88), 0.035, 0.1, n=6, top_radius=0.025)  # the bushings
    p.box("metal_dark", (0.14, 0, 6.32), (0.1, 0.05, 0.55))                 # the secondary rack on the Unity -X side
    for z in (6.15, 6.5):
        p.cyl("porcelain", (0.22, 0, z), 0.04, 0.07, n=6, axis="x")         # the spools the drop wires are tied to
    return p


def service_entry():
    """Wall-mounted: a meter box (origin = its middle, the back flat on the wall), the disconnect below it and a conduit riser up to a weatherhead
    3.5 m above the meter, where the drop from the pole ends. Faces -Y like everything (Unity +Z): turn it to face out of the wall."""
    p = Prop("GL_ServiceEntry_01")
    d = 0.14                                                                 # depth of the box
    p.box("metal_galv", (0, -d / 2, 0.0), (0.32, d, 0.44))                   # the meter box
    p.cyl("glass", (0, -d - 0.005, 0.03), 0.105, 0.05, n=10, axis="y")        # the meter's glass
    p.cyl("metal_dark", (0, -d + 0.015, 0.03), 0.115, 0.03, n=10, axis="y")  # its ring
    p.box("porcelain", (0, -d + 0.005, 0.03), (0.15, 0.01, 0.15))            # the dial
    p.box("metal_dark", (0, -d / 2, 0.255), (0.12, 0.1, 0.06))               # the hub on top
    p.box("metal_galv", (0, -0.065, -0.39), (0.26, 0.13, 0.34))              # the disconnect box
    p.box("metal_dark", (0.0, -0.135, -0.39), (0.04, 0.02, 0.2))             # its lever
    p.cyl("metal_galv", (0, -0.07, 1.9), 0.026, 3.3, n=6)                    # the riser conduit (0.25 m up to 3.55 m)
    for z in (1.0, 2.3, 3.2):
        p.box("metal_dark", (0, -0.035, z), (0.07, 0.07, 0.03))              # clamps
    p.cyl("metal_dark", (0, -0.07, 3.56), 0.05, 0.1, n=7, top_radius=0.035)  # the weatherhead body
    p.box("metal_dark", (0, -0.12, 3.62), (0.09, 0.1, 0.07))                 # its hood, bent out and down
    p.box("metal_dark", (0, -0.17, 3.57), (0.09, 0.03, 0.12))
    return p


def floodlight_stand():
    """The FBI's floodlight (issue #19): a tripod with a mast and a big lamp head. The lamp looks along -Y (Unity +Z); origin on the ground at the middle of the legs.
    The head's middle is 3.1 m up: the beam in Unity starts there (FbiFloodlight.mountHeight)."""
    p = Prop("GL_FloodlightStand_01")
    for ang in (90, 210, 330):
        fx, fy = 0.8 * math.cos(math.radians(ang)), 0.8 * math.sin(math.radians(ang))
        props_lib.rod(p, "metal_dark", (0, 0, 1.05), (fx, fy, 0.03), w=0.05)                    # a leg, from the collar to its foot
        p.box("rubber", (fx, fy, 0.015), (0.12, 0.12, 0.03))                          # its foot
    p.cyl("metal_dark", (0, 0, 1.05), 0.07, 0.14, n=8)                                # the collar the legs meet at
    p.cyl("metal_galv", (0, 0, 2.05), 0.03, 2.1, n=8)                                 # the mast, from the collar up
    p.box("metal_dark", (0, 0, 3.1), (0.82, 0.24, 0.5))                               # the lamp head
    p.box("paint_white", (0, -0.125, 3.1), (0.7, 0.02, 0.38))                         # the lens
    p.box("metal_dark", (0, -0.14, 3.1), (0.72, 0.02, 0.04))                          # a bar across it
    for sx in (-1, 1):
        p.box("metal_dark", (sx * 0.43, 0.0, 3.1), (0.04, 0.2, 0.28))                 # the yoke it swings in
    p.box("metal_dark", (0, 0.18, 3.1), (0.5, 0.12, 0.34))                            # the housing at the back
    return p


PROPS = {
    "rake": (rake, "Global"), "shovel": (shovel, "Global"), "pitchfork": (pitchfork, "Global"), "barrel": (barrel, "Global"),
    "crate": (crate, "Global"), "milk_can": (milk_can, "Global"), "hay_square": (hay_square, "Global"), "hay_round": (hay_round, "Global"),
    "wheelbarrow": (wheelbarrow, "Global"), "jerrycan": (jerrycan, "Global"), "feed_sack": (feed_sack, "Global"),
    "stool": (stool, "Global"), "firewood": (firewood_stack, "Global"), "firewood_triangle": (firewood_triangle, "Global"), "firewood_small": (firewood_small, "Global"),
    "firewood_loose": (firewood_loose, "Global"), "chopping_block": (chopping_block, "Global"),
    "fence": (fence_section, "Global"), "gate": (gate, "Global"), "mailbox": (mailbox, "Global"),
    "bare_bulb": (bare_bulb, "Global"), "pole_lamp": (pole_lamp, "Global"), "phone": (landline_phone, "Global"),
    "utility_pole": (utility_pole, "Global"), "utility_pole_corner": (utility_pole_corner, "Global"), "utility_pole_transformer": (utility_pole_transformer, "Global"),
    "service_entry": (service_entry, "Global"), "floodlight_stand": (floodlight_stand, "Global"),
    "doghouse": (doghouse, "Farm"), "generator": (generator, "Farm"), "trough": (water_trough, "Farm"), "scarecrow": (scarecrow, "Farm"),
}

names = globals().get("PROP_LIST") or list(PROPS)
x = 0.0
for key in names:
    fn, area = PROPS[key]
    prop = fn()
    obj, coll = prop.finish()
    print(common.stats(obj))
    common.export_fbx(coll, f"Assets/Art/{area}/Props/{prop.name}.fbx")
    obj.location.x = x
    x += max(1.0, obj.dimensions.x + 0.5)
props_lib.write_interactions()
print("props done", len(names))
