"""Hand tools at real size: hammer, sledgehammer, axe, hand saw, wrench, screwdriver, pliers, hoe, spade and a watering can. Flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/hand_tools.py", run_name="__main__")
Optional global TOOL_LIST (piece names). Exports Assets/Art/Global/Tools/GT_<Name>_01.fbx.

Origin on the floor at the middle of the base. Long tools lie on the floor along X, working end at +X (the hoe and spade too: a handle is a long thing),
front -Y. Sizes and details are in docs/assets/briefs/hand-tools.md.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
rod = props_lib.rod

PIECES = {}


def piece(name):
    def deco(fn):
        PIECES[name] = fn
        return fn
    return deco


@piece("Hammer")
def hammer():
    """A 16 oz claw hammer: 0.33 m hickory handle, steel head with a face at +X and a curved claw at -X."""
    p = Prop("GT_Hammer_01")
    p.cyl("wood_light", (-0.02, 0, 0.014), 0.014, 0.3, n=6, axis="x")             # handle, resting on the floor
    p.cyl("rubber", (-0.1, 0, 0.015), 0.0165, 0.12, n=6, axis="x")                 # grip
    p.box("metal_dark", (0.135, 0, 0.03), (0.04, 0.034, 0.06))                    # head body, on the handle's end
    p.cyl("metal_galv", (0.17, 0, 0.03), 0.019, 0.03, n=8, axis="x")              # striking face
    p.box("metal_dark", (0.097, 0, 0.034), (0.034, 0.03, 0.052), taper=1.0)       # neck of the claw
    p.box("metal_dark", (0.065, 0, 0.03), (0.04, 0.022, 0.04), rot=(0, 18, 0))     # claw, curving down and back
    p.box("metal_dark", (0.045, 0, 0.022), (0.03, 0.014, 0.026), rot=(0, 28, 0))
    return p


@piece("Sledgehammer")
def sledgehammer():
    """A 6 lb sledge: 0.9 m handle, 0.25 m double-faced steel head."""
    p = Prop("GT_Sledgehammer_01")
    p.cyl("wood_light", (0, 0, 0.018), 0.018, 0.9, n=6, axis="x")
    p.cyl("rubber", (-0.38, 0, 0.02), 0.021, 0.14, n=6, axis="x")
    p.box("metal_dark", (0.42, 0, 0.05), (0.07, 0.1, 0.1))                         # eye block on the handle's end
    for s in (-1, 1):                                                              # the head runs across the handle (Y), a face at each end
        p.box("metal_galv", (0.42, s * 0.085, 0.05), (0.09, 0.09, 0.1), taper=1.0)
        p.box("metal_dark", (0.42, s * 0.125, 0.05), (0.095, 0.01, 0.105))
    return p


@piece("Axe")
def axe():
    """A felling axe: 0.85 m handle with a swell at the end, head with a bit and a poll."""
    p = Prop("GT_Axe_01")
    p.cyl("wood_light", (-0.02, 0, 0.018), 0.017, 0.8, n=6, axis="x")
    p.box("wood_light", (-0.4, 0, 0.02), (0.06, 0.04, 0.036))                      # the knob
    p.box("metal_dark", (0.37, 0, 0.02), (0.06, 0.08, 0.04))                       # eye and poll (the axe lies on its side: the blade is flat on the floor)
    p.box("metal_dark", (0.43, 0, 0.012), (0.08, 0.14, 0.024))                     # cheek, widening to the bit
    p.box("metal_galv", (0.485, 0, 0.007), (0.03, 0.2, 0.014))                     # the cutting edge
    return p


@piece("HandSaw")
def hand_saw():
    """A 20 inch hand saw lying on its side: tapered steel blade with a toothed edge, wooden pistol grip at -X."""
    p = Prop("GT_HandSaw_01")
    p.box("metal_galv", (0.1, 0, 0.003), (0.5, 0.11, 0.006))                       # blade, 0.5 m
    for k in range(10):                                                          # teeth along the -Y edge
        p.box("metal_galv", (-0.1 + k * 0.045, -0.057, 0.003), (0.03, 0.014, 0.006), rot=(0, 0, 25))
    p.box("wood_dark", (-0.2, 0, 0.012), (0.14, 0.1, 0.024))                       # handle plate
    p.box("black", (-0.2, 0, 0.012), (0.04, 0.045, 0.026))                         # the hand hole
    return p


@piece("Wrench")
def wrench():
    """A 10 inch open-end spanner: a flat steel bar with a jaw at each end."""
    p = Prop("GT_Wrench_01")
    p.box("metal_galv", (0, 0, 0.005), (0.2, 0.022, 0.01))
    for s in (-1, 1):
        x = s * 0.1
        p.box("metal_galv", (x, 0, 0.005), (0.036, 0.05, 0.01))                  # head
        p.box("metal_dark", (x + s * 0.01, 0, 0.005), (0.024, 0.022, 0.012))     # the jaw opening
    return p


@piece("Screwdriver")
def screwdriver():
    """A slotted screwdriver: 0.1 m yellow handle, 0.15 m shaft, flat tip."""
    p = Prop("GT_Screwdriver_01")
    p.cyl("paint_yellow", (-0.075, 0, 0.0175), 0.0175, 0.1, n=6, axis="x")
    p.cyl("black", (-0.125, 0, 0.0175), 0.018, 0.012, n=6, axis="x")
    p.cyl("metal_galv", (0.05, 0, 0.005), 0.005, 0.15, n=6, axis="x")
    p.box("metal_dark", (0.133, 0, 0.005), (0.02, 0.012, 0.008), taper=1.0)
    return p


@piece("Pliers")
def pliers():
    """Slip-joint pliers 0.2 m long lying open: two crossed arms with rubber grips and a toothed jaw each."""
    p = Prop("GT_Pliers_01")
    for s in (-1, 1):
        rod(p, "metal_dark", (0.0, 0, 0.012), (-0.1, s * 0.035, 0.012), w=0.016, h=0.01)    # handles spreading to -X
        rod(p, "rubber", (-0.045, s * 0.017, 0.013), (-0.1, s * 0.035, 0.013), w=0.02, h=0.016)
        rod(p, "metal_galv", (0.0, 0, 0.012), (0.09, s * 0.012, 0.012), w=0.016, h=0.01)    # jaws
    p.cyl("metal_dark", (0.0, 0, 0.012), 0.012, 0.014, n=6)                                  # the pivot
    return p


@piece("Hoe")
def hoe():
    """A garden hoe: 1.5 m wooden handle, a goose-neck of steel and a flat blade 0.15 m wide."""
    p = Prop("GT_Hoe_01")
    p.cyl("wood_light", (-0.05, 0, 0.0125), 0.0125, 1.4, n=6, axis="x")
    rod(p, "metal_dark", (0.63, 0, 0.0125), (0.7, 0, 0.0), w=0.018, h=0.014)                # neck, bending down to the floor
    p.box("metal_dark", (0.725, 0, 0.0035), (0.05, 0.15, 0.007))                            # blade, flat on the floor
    return p


@piece("Spade")
def spade():
    """A digging spade: 0.9 m handle with a D grip at -X and a rounded steel blade 0.2 x 0.28 m."""
    p = Prop("GT_Spade_01")
    p.cyl("wood_light", (0.0, 0, 0.0125), 0.0125, 0.8, n=6, axis="x")
    p.box("wood_light", (-0.4, 0, 0.0125), (0.03, 0.2, 0.025))                              # D grip bar
    for s in (-1, 1):
        p.box("wood_light", (-0.4, s * 0.1, 0.0125), (0.03, 0.025, 0.025))
    p.box("metal_dark", (0.42, 0, 0.012), (0.06, 0.05, 0.024))                              # socket
    p.box("metal_galv", (0.6, 0, 0.004), (0.28, 0.2, 0.008), taper=1.0)                     # blade
    p.box("metal_galv", (0.72, 0, 0.004), (0.06, 0.12, 0.008))                              # narrowing to the tip
    return p


@piece("WateringCan")
def watering_can():
    """A galvanised 10 litre watering can: 0.2 m round body, long spout with a rose, an arched handle over the top."""
    p = Prop("GT_WateringCan_01")
    p.cyl("metal_galv", (0, 0, 0.12), 0.1, 0.24, n=10, top_radius=0.095)
    p.cyl("metal_dark", (0, 0, 0.243), 0.095, 0.006, n=10)                                  # the lid ring
    rod(p, "metal_galv", (0.09, 0, 0.05), (0.38, 0, 0.3), w=0.04)                           # spout, rising to the front (+X)
    p.cyl("metal_dark", (0.4, 0, 0.318), 0.05, 0.03, n=8, rot=(0, 55, 0))                   # the rose
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
