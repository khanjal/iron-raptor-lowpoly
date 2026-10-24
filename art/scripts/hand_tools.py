"""Hand tools at real size: hammer, sledgehammer, axe, hand saw, wrench, screwdriver, pliers, hoe, spade and a watering can. Flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/hand_tools.py", run_name="__main__")
Optional global TOOL_LIST (piece names). Exports Assets/Art/Global/Tools/GT_<Name>_01.fbx.

Origin on the floor at the middle of the tool's length. Long tools lie on the floor along X, working end at +X (the hoe and spade too: a handle is a long
thing), front -Y; the watering can stands. Sizes and details are in docs/assets/briefs/hand-tools.md.
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
HEX = 0.866          # a six-sided handle of radius r rests on a flat at 0.866 r below its axis, so its axis sits at HEX * r to touch the floor


class Prop(props_lib.Prop):
    """A prop whose parts are all shifted along X by `ox`, so each tool's origin sits at the middle of its length."""
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


@piece("Hammer")
def hammer():
    """A 16 oz claw hammer lying on its side: 0.28 m hickory handle along X, the head across it, a round face to +Y and a long claw to -Y."""
    p = Prop("GT_Hammer_01")
    p.ox = -0.01
    p.cyl("wood_light", (-0.04, 0, HEX * 0.014), 0.014, 0.28, n=6, axis="x")        # handle
    p.cyl("rubber", (-0.1, 0, HEX * 0.0165), 0.0165, 0.12, n=6, axis="x")           # grip
    p.box("metal_dark", (0.11, 0, 0.017), (0.036, 0.04, 0.034))                    # eye block, the handle passes through it
    p.cyl("metal_galv", (0.11, 0.045, 0.0166), 0.018, 0.03, n=8, axis="y")         # the striking face, to +Y
    p.box("metal_dark", (0.11, -0.04, 0.0125), (0.03, 0.06, 0.025))                # claw, to -Y
    p.box("metal_dark", (0.11, -0.082, 0.009), (0.02, 0.03, 0.018))                # claw tip, lower
    return p


@piece("Sledgehammer")
def sledgehammer():
    """A sledge of about 6 lb (a 0.16 m head with 0.06 m square faces) on a 0.9 m handle; the head runs across the handle."""
    p = Prop("GT_Sledgehammer_01")
    p.ox = -0.02
    p.cyl("wood_light", (0, 0, HEX * 0.018), 0.018, 0.9, n=6, axis="x")
    p.cyl("rubber", (-0.38, 0, HEX * 0.021), 0.021, 0.14, n=6, axis="x")
    p.box("metal_dark", (0.42, 0, 0.03), (0.05, 0.16, 0.06))                       # head, across the handle (Y)
    for s in (-1, 1):
        p.box("metal_galv", (0.42, s * 0.085, 0.03), (0.058, 0.012, 0.06))         # the two striking faces
    return p


@piece("Axe")
def axe():
    """A felling axe lying on its side: 0.8 m handle with a knob, the head to one side of the handle's end (poll to -Y, bit to +Y, edge parallel to the handle)."""
    p = Prop("GT_Axe_01")
    p.ox = -0.035
    p.cyl("wood_light", (-0.02, 0, HEX * 0.017), 0.017, 0.8, n=6, axis="x")
    p.box("wood_light", (-0.4, 0, 0.018), (0.06, 0.04, 0.036))                     # the knob
    p.box("metal_dark", (0.37, 0, 0.0225), (0.06, 0.04, 0.045))                    # eye, the handle passes through it
    p.box("metal_dark", (0.37, -0.04, 0.02), (0.05, 0.04, 0.04))                   # poll, to -Y
    p.box("metal_dark", (0.375, 0.055, 0.012), (0.09, 0.07, 0.024))                # cheek, to +Y
    p.box("metal_galv", (0.385, 0.1, 0.007), (0.1, 0.014, 0.014))                  # the cutting edge, 0.1 m
    return p


@piece("HandSaw")
def hand_saw():
    """A 20 inch hand saw lying on its side: steel blade (0.5 m) with a toothed edge, wooden grip with a hand hole at -X."""
    p = Prop("GT_HandSaw_01")
    p.ox = -0.04
    p.box("metal_galv", (0.1, 0, 0.003), (0.5, 0.11, 0.006))                       # blade
    for k in range(10):                                                          # teeth along the -Y edge
        p.box("metal_galv", (-0.1 + k * 0.045, -0.057, 0.003), (0.03, 0.014, 0.006), rot=(0, 0, 25))
    p.box("wood_dark", (-0.2, 0, 0.012), (0.14, 0.1, 0.024))                       # handle plate
    p.box("black", (-0.2, 0, 0.01225), (0.04, 0.045, 0.0245))                      # the hand hole
    return p


@piece("Wrench")
def wrench():
    """A 10 inch open-end spanner: a flat steel bar with a jaw at each end."""
    p = Prop("GT_Wrench_01")
    p.box("metal_galv", (0, 0, 0.005), (0.2, 0.022, 0.01))
    for s in (-1, 1):
        x = s * 0.1
        p.box("metal_galv", (x, 0, 0.005), (0.036, 0.05, 0.01))                  # head
        p.box("metal_dark", (x + s * 0.01, 0, 0.006), (0.024, 0.022, 0.012))     # the jaw opening
    return p


@piece("Screwdriver")
def screwdriver():
    """A slotted screwdriver: 0.1 m yellow handle, 0.15 m shaft on the handle's axis, flat tip."""
    p = Prop("GT_Screwdriver_01")
    z = HEX * 0.0175
    p.cyl("paint_yellow", (-0.075, 0, z), 0.0175, 0.1, n=6, axis="x")
    p.cyl("black", (-0.125, 0, z), 0.018, 0.012, n=6, axis="x")
    p.cyl("metal_galv", (0.05, 0, z), 0.005, 0.15, n=6, axis="x")
    p.box("metal_dark", (0.133, 0, z), (0.02, 0.012, 0.008))
    return p


@piece("Pliers")
def pliers():
    """Slip-joint pliers 0.2 m long lying open: two crossed arms with rubber grips and a toothed jaw each."""
    p = Prop("GT_Pliers_01")
    for s in (-1, 1):
        rod(p, "metal_dark", (0.0, 0, 0.005), (-0.1, s * 0.035, 0.005), w=0.016, h=0.01)    # handles spreading to -X
        rod(p, "rubber", (-0.045, s * 0.017, 0.008), (-0.1, s * 0.035, 0.008), w=0.02, h=0.016)
        rod(p, "metal_galv", (0.0, 0, 0.005), (0.09, s * 0.012, 0.005), w=0.016, h=0.01)    # jaws
    p.cyl("metal_dark", (0.0, 0, 0.007), 0.012, 0.014, n=6)                                  # the pivot
    return p


@piece("Hoe")
def hoe():
    """A garden hoe: 1.5 m wooden handle, a goose-neck of steel and a flat blade 0.15 m wide."""
    p = Prop("GT_Hoe_01")
    p.cyl("wood_light", (-0.05, 0, HEX * 0.0125), 0.0125, 1.4, n=6, axis="x")
    rod(p, "metal_dark", (0.63, 0, 0.0108), (0.7, 0, 0.007), w=0.018, h=0.014)              # neck, bending down to the floor
    p.box("metal_dark", (0.725, 0, 0.0035), (0.05, 0.15, 0.007))                            # blade, flat on the floor
    return p


@piece("Spade")
def spade():
    """A digging spade: 0.8 m handle with a D grip at -X, a socket and a steel blade 0.2 x 0.28 m."""
    p = Prop("GT_Spade_01")
    p.ox = -0.2
    p.cyl("wood_light", (0.0, 0, HEX * 0.0125), 0.0125, 0.8, n=6, axis="x")
    p.box("wood_light", (-0.4, 0, 0.0125), (0.03, 0.14, 0.025))                             # grip bar
    for s in (-1, 1):                                                                     # the two sides of the D, back toward the handle
        p.box("wood_light", (-0.365, s * 0.058, 0.0125), (0.06, 0.024, 0.025))
    p.box("metal_dark", (0.43, 0, 0.012), (0.08, 0.05, 0.024))                              # socket, overlapping the blade's top
    p.box("metal_galv", (0.62, 0, 0.004), (0.3, 0.2, 0.008))                                # blade
    p.box("metal_galv", (0.79, 0, 0.004), (0.06, 0.12, 0.008))                              # narrowing to the tip
    return p


@piece("WateringCan")
def watering_can():
    """A galvanised watering can of about 7 litres: 0.2 m round body, long spout with a rose, an arched handle over the top."""
    p = Prop("GT_WateringCan_01")
    p.cyl("metal_galv", (0, 0, 0.12), 0.1, 0.24, n=10, top_radius=0.095)
    p.cyl("metal_dark", (0, 0, 0.243), 0.095, 0.006, n=10)                                  # the lid ring
    rod(p, "metal_galv", (0.09, 0, 0.05), (0.38, 0, 0.3), w=0.04)                           # spout, rising to the front (+X)
    p.cyl("metal_dark", (0.38, 0, 0.3), 0.05, 0.03, n=8, rot=(0, 55, 0))                    # the rose, on the spout's end
    rod(p, "metal_dark", (-0.09, 0, 0.06), (-0.17, 0, 0.17), w=0.022, h=0.03)               # handle: back, up and over
    rod(p, "metal_dark", (-0.17, 0, 0.17), (-0.08, 0, 0.3), w=0.022, h=0.03)
    rod(p, "metal_dark", (-0.08, 0, 0.3), (0.0, 0, 0.245), w=0.022, h=0.03)
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
    print("hand tools done", len(chosen))


if __name__ == "__main__":
    run()
