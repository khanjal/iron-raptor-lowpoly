"""Household, garden and workshop tools, batch 2 at real size: plunger, rope coil, sawhorse, paint can, pruning shears, fire poker, hose coil, sprinkler,
extension cord reel and hand truck. Flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/tools_more.py", run_name="__main__")
Optional global TOOL_LIST (piece names). Exports Assets/Art/Global/Tools/GT_<Name>_01.fbx.

Origin on the floor at the middle of the footprint. Small hand tools (shears, poker) lie on the floor along X, working end at +X; the rest stand as they are used (the hand truck's toe plate and the
sprinkler's bar face +X, the working side).
Front -Y for the rest. Sizes and details are in docs/assets/briefs/hand-tools-2.md.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
rod = props_lib.rod
HEX = 0.866          # a six-sided bar of radius r lying on the floor rests on a flat at 0.866 r below its axis


class Prop(props_lib.Prop):
    """A prop whose parts are all shifted along X by `ox`, so the origin sits at the middle of the tool."""
    ox = 0.0

    def box(self, colour, center, size, rot=(0, 0, 0), taper=1.0):
        super().box(colour, (center[0] + self.ox, center[1], center[2]), size, rot, taper)

    def cyl(self, colour, center, radius, height, n=8, axis="z", top_radius=None, rot=(0, 0, 0)):
        super().cyl(colour, (center[0] + self.ox, center[1], center[2]), radius, height, n, axis, top_radius, rot)


PIECES = {}


def piece(name):
    def deco(fn):
        PIECES[name] = fn
        return fn
    return deco


@piece("Plunger")
def plunger():
    """A sink plunger 0.55 m tall: black rubber cup 0.15 m across, wooden handle, a small knob on top."""
    p = Prop("GT_Plunger_01")
    p.cyl("rubber", (0, 0, 0.04), 0.075, 0.08, n=10, top_radius=0.03)                # the cup, wide end on the floor
    p.cyl("wood_light", (0, 0, 0.3), 0.013, 0.46, n=8)                               # handle, from inside the cup up
    p.cyl("wood_dark", (0, 0, 0.53), 0.02, 0.03, n=8)                                # knob
    return p


@piece("RopeCoil")
def rope_coil():
    """A coil of thick (about 25 mm) rope, 0.3 m across and 0.09 m high: three layers around an open middle, one end laid out along the floor."""
    p = Prop("GT_RopeCoil_01")
    p.ox = -0.06
    p.cyl("tan", (0, 0, 0.015), 0.15, 0.03, n=12)
    p.cyl("hay", (0, 0, 0.045), 0.15, 0.03, n=12)
    p.cyl("tan", (0, 0, 0.075), 0.15, 0.03, n=12)
    p.cyl("dark_brown", (0, 0, 0.045), 0.07, 0.09, n=12)                             # the open middle, a dark core as tall as the coil
    p.box("tan", (0.2, 0.0, 0.01), (0.14, 0.02, 0.02))                               # the free end, along the floor from the coil's side
    return p


@piece("Sawhorse")
def sawhorse():
    """A 2x4 sawhorse 0.8 m long and 0.6 m high: a top beam on two pairs of splayed legs."""
    p = Prop("GT_Sawhorse_01")
    p.box("wood_light", (0, 0, 0.555), (0.8, 0.09, 0.09))                           # top beam
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod(p, "wood_dark", (sx * 0.32, sy * 0.03, 0.52), (sx * 0.34, sy * 0.19, 0.0078), w=0.045, h=0.045)
    for sx in (-1, 1):
        p.box("wood_dark", (sx * 0.33, 0, 0.3), (0.03, 0.2, 0.04))                  # a brace across each pair of legs
    return p


@piece("PaintCan")
def paint_can():
    """A one gallon paint can (0.16 m across, 0.17 m high): label, rim, wire bail, paint at the open top and a drip of yellow paint down the side."""
    p = Prop("GT_PaintCan_01")
    p.cyl("metal_galv", (0, 0, 0.085), 0.08, 0.17, n=12)
    p.cyl("label_red", (0, 0, 0.09), 0.0808, 0.07, n=12)                            # the paper label, just proud of the can
    p.cyl("metal_galv", (0, 0, 0.172), 0.084, 0.012, n=12)                          # the rim
    p.cyl("paint_yellow", (0, 0, 0.174), 0.07, 0.006, n=12)                         # paint at the top where the lid is off
    p.box("paint_yellow", (0.0, -0.0815, 0.15), (0.03, 0.006, 0.05))                 # a drip on the front
    rod(p, "metal_dark", (-0.08, 0, 0.17), (0.0, 0, 0.23), w=0.006)                  # the wire bail
    rod(p, "metal_dark", (0.0, 0, 0.23), (0.08, 0, 0.17), w=0.006)
    return p


@piece("PruningShears")
def pruning_shears():
    """Bypass pruning shears 0.2 m long lying open on the floor: two red-gripped handles, a pivot bolt and a hooked and a flat blade."""
    p = Prop("GT_PruningShears_01")
    p.ox = 0.0065
    for s in (-1, 1):
        rod(p, "metal_dark", (0.0, 0, 0.005), (-0.1, s * 0.04, 0.005), w=0.014, h=0.01)       # handle arms spreading to -X
        rod(p, "label_red", (-0.04, s * 0.016, 0.007), (-0.1, s * 0.04, 0.007), w=0.02, h=0.014)  # the grips
    rod(p, "metal_galv", (0.0, 0, 0.005), (0.09, 0.012, 0.005), w=0.016, h=0.01)              # the cutting blade, straight
    rod(p, "metal_dark", (0.0, 0, 0.005), (0.08, -0.01, 0.005), w=0.016, h=0.01)              # the hook blade, a little to the side
    p.cyl("metal_dark", (0.0, 0, 0.0075), 0.01, 0.015, n=6)                                    # the pivot bolt
    return p


@piece("FirePoker")
def fire_poker():
    """A wrought iron fireplace poker 0.7 m long lying on the floor: a square loop handle at one end, a bent point at the other."""
    p = Prop("GT_FirePoker_01")
    p.ox = 0.0085
    p.cyl("metal_dark", (0, 0, HEX * 0.007), 0.007, 0.6, n=6, axis="x")                      # the shaft
    for s in (-1, 1):
        p.box("metal_dark", (-0.33, s * 0.025, 0.005), (0.07, 0.01, 0.01))                  # the loop's two long sides
    p.box("metal_dark", (-0.365, 0, 0.005), (0.01, 0.06, 0.01))                              # its end
    p.box("metal_dark", (-0.295, 0, 0.005), (0.01, 0.06, 0.01))                              # and the side joining the shaft
    rod(p, "metal_dark", (0.3, 0, 0.005), (0.35, 0.035, 0.005), w=0.012, h=0.01)             # the bent point
    return p


@piece("HoseCoil")
def hose_coil():
    """A garden hose coiled flat: 0.45 m across and 0.12 m high in four layers, with a brass nozzle at the end of a short tail."""
    p = Prop("GT_HoseCoil_01")
    p.ox = -0.1
    for k in range(4):
        p.cyl("corn_green" if k % 2 == 0 else "leaf_dark", (0, 0, 0.015 + k * 0.03), 0.225, 0.03, n=14)
    p.cyl("shadow", (0, 0, 0.06), 0.1, 0.12, n=14)                                         # the open middle
    p.box("corn_green", (0.27, 0.0, 0.0125), (0.12, 0.025, 0.025))                           # the tail, along the floor from the coil's side
    p.cyl("copper", (0.375, 0, 0.0175), 0.0175, 0.1, n=8, axis="x")                          # the brass nozzle
    return p


@piece("Sprinkler")
def sprinkler():
    """An oscillating lawn sprinkler 0.39 m long, fitting included: a steel spray bar with a row of holes on two yellow skids, a brass hose fitting at one end."""
    p = Prop("GT_Sprinkler_01")
    p.ox = 0.0225
    for s in (-1, 1):
        p.box("paint_yellow", (s * 0.12, 0, 0.0075), (0.06, 0.16, 0.015))                  # the two skids
    p.box("metal_galv", (0, 0, 0.04), (0.34, 0.07, 0.05))                                  # the spray bar
    for k in range(8):
        p.cyl("black", (-0.14 + k * 0.04, 0, 0.066), 0.005, 0.006, n=6)                      # the spray holes
    p.cyl("copper", (-0.19, 0, 0.04), 0.017, 0.04, n=8, axis="x")                           # hose fitting
    return p


@piece("CordReel")
def cord_reel():
    """A 50 foot extension cord reel 0.28 m across and 0.33 m high: orange cord between two yellow discs, a black frame with a carry handle."""
    p = Prop("GT_CordReel_01")
    p.box("black", (0, 0, 0.01), (0.28, 0.16, 0.02))                                         # the base plate
    for s in (-1, 1):
        p.cyl("paint_yellow", (0, s * 0.055, 0.15), 0.13, 0.01, n=12, axis="y")              # the two side discs
        p.box("black", (0, s * 0.066, 0.23), (0.016, 0.016, 0.16))                           # the handle posts
    p.cyl("basket_orange", (0, 0, 0.15), 0.11, 0.1, n=12, axis="y")                          # the wound cord
    p.box("black", (0, 0, 0.318), (0.02, 0.15, 0.02))                                        # the handle across the top
    return p


@piece("HandTruck")
def hand_truck():
    """A two-wheeled hand truck 1.1 m high: blue steel frame, a handle at the top, a toe plate and two rubber wheels."""
    p = Prop("GT_HandTruck_01")
    p.ox = -0.06
    for s in (-1, 1):
        p.box("truck_blue", (0, s * 0.17, 0.55), (0.025, 0.025, 1.1))                       # the two rails
        p.cyl("rubber", (0, s * 0.2, 0.1), 0.1, 0.035, n=12, axis="y")                       # the wheels
    for z in (0.35, 0.65, 0.95):
        p.box("truck_blue", (0, 0, z), (0.02, 0.34, 0.02))                                   # cross bars
    p.box("truck_blue", (0, 0, 1.1), (0.04, 0.36, 0.03))                                     # the handle
    p.box("metal_galv", (0.11, 0, 0.006), (0.22, 0.32, 0.012))                               # the toe plate
    p.cyl("metal_dark", (0, 0, 0.1), 0.008, 0.38, n=6, axis="y")                             # the axle
    return p


def run():
    names = globals().get("TOOL_LIST")
    chosen = [k for k in PIECES if not names or k in names]
    x = 0.0
    for key in chosen:
        prop = PIECES[key]()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Tools/{prop.name}.fbx")
        obj.location = (x, 0, 0)
        x += max(0.3, obj.dimensions.x + 0.4)
    print("tools batch 2 done", len(chosen))


if __name__ == "__main__":
    run()
