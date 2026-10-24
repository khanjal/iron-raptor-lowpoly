"""Household, garden and workshop tools, batch 3 at real size: mallet, clothes iron, bathroom scale, cordless drill, bench vise, snow shovel, car battery,
boot scraper, toilet brush and clip-on work light. Flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/tools_extra.py", run_name="__main__")
Optional global TOOL_LIST (piece names). Exports Assets/Art/Global/Tools/GT_<Name>_01.fbx.

Origin on the floor at the middle of the footprint. The mallet and the snow shovel lie on the floor along X, working end at +X; the rest stand as they are used,
front -Y. Sizes and details are in docs/assets/briefs/hand-tools-3.md.

Cylinders lying along X or Y use 8 or 12 sides with their axis at the radius above the floor (a vertex points straight down); six-sided bars use HEX.
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
    """A prop whose parts are all shifted along X by `ox` and along Y by `oy`, so the origin sits at the middle of the tool."""
    ox = 0.0
    oy = 0.0

    def box(self, colour, center, size, rot=(0, 0, 0), taper=1.0):
        super().box(colour, (center[0] + self.ox, center[1] + self.oy, center[2]), size, rot, taper)

    def cyl(self, colour, center, radius, height, n=8, axis="z", top_radius=None, rot=(0, 0, 0)):
        super().cyl(colour, (center[0] + self.ox, center[1] + self.oy, center[2]), radius, height, n, axis, top_radius, rot)


PIECES = {}


def piece(name):
    def deco(fn):
        PIECES[name] = fn
        return fn
    return deco


@piece("Mallet")
def mallet():
    """A 16 oz rubber mallet lying on its side: 0.3 m wooden handle along X, a rubber head across it at +X."""
    p = Prop("GT_Mallet_01")
    p.ox = -0.0225
    p.cyl("wood_light", (0.0, 0, 0.016), 0.016, 0.3, n=8, axis="x")                 # the handle
    p.box("rubber", (0.16, 0, 0.025), (0.07, 0.12, 0.05))                            # the head, across the handle (Y)
    return p


@piece("ClothesIron")
def clothes_iron():
    """A steam iron 0.27 m long standing on its sole plate: steel plate, white body, a handle arch over the back and a red dial."""
    p = Prop("GT_ClothesIron_01")
    p.box("metal_galv", (0, 0, 0.01), (0.12, 0.27, 0.02))                            # the sole plate
    p.box("paint_white", (0, 0.0, 0.05), (0.11, 0.23, 0.06))                         # the body
    p.box("paint_white", (0, 0.05, 0.1), (0.045, 0.14, 0.04))                         # the rise at the back the handle springs from
    p.box("black", (0, 0.1, 0.135), (0.035, 0.03, 0.05))                             # handle post, back
    p.box("black", (0, -0.0, 0.135), (0.035, 0.03, 0.05))                            # handle post, front
    p.box("black", (0, 0.05, 0.165), (0.04, 0.13, 0.03))                             # the handle bar
    p.cyl("cloth_red", (0, -0.075, 0.086), 0.02, 0.012, n=10)                         # the dial at the front
    return p


@piece("BathroomScale")
def bathroom_scale():
    """A bathroom scale 0.3 m square and 0.045 m high: white glass platform on four rubber feet with a digital display."""
    p = Prop("GT_BathroomScale_01")
    p.box("paint_white", (0, 0, 0.025), (0.3, 0.3, 0.03))                            # the platform
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.cyl("rubber", (sx * 0.12, sy * 0.12, 0.005), 0.02, 0.01, n=8)         # feet
    p.box("screen", (0, -0.1, 0.0425), (0.1, 0.035, 0.005))                          # the display
    return p


@piece("CordlessDrill")
def cordless_drill():
    """An 18 V cordless drill standing on its battery: yellow body with a black battery and trigger, a steel chuck and a bit, pointing to -Y."""
    p = Prop("GT_CordlessDrill_01")
    p.oy = 0.09
    p.box("black", (0, 0.04, 0.035), (0.06, 0.1, 0.07))                              # the battery
    p.box("paint_yellow", (0, 0.03, 0.135), (0.05, 0.05, 0.13))                      # the pistol grip
    p.box("paint_yellow", (0, -0.05, 0.22), (0.06, 0.2, 0.07))                       # the motor housing
    p.box("black", (0, -0.005, 0.17), (0.015, 0.02, 0.03))                           # the trigger
    p.cyl("metal_galv", (0, -0.18, 0.22), 0.02, 0.06, n=12, axis="y")                # the chuck
    p.cyl("metal_dark", (0, -0.24, 0.22), 0.004, 0.06, n=8, axis="y")                # the bit
    return p


@piece("BenchVise")
def bench_vise():
    """A 4 inch bench vise: red cast-iron body with a fixed and a moving jaw, a steel screw and a T-handle, on a base plate."""
    p = Prop("GT_BenchVise_01")
    p.oy = 0.048
    p.box("barn_red", (0, 0, 0.015), (0.16, 0.22, 0.03))                             # the base plate
    p.box("barn_red", (0, 0, 0.055), (0.12, 0.22, 0.05))                             # the body
    p.box("barn_red", (0, 0.09, 0.12), (0.1, 0.04, 0.08))                           # the fixed jaw
    p.box("barn_red", (0, -0.02, 0.12), (0.1, 0.04, 0.08))                          # the moving jaw
    p.cyl("metal_dark", (0, -0.105, 0.1), 0.012, 0.19, n=8, axis="y")                   # the screw
    p.cyl("metal_galv", (0, -0.2, 0.1), 0.006, 0.14, n=8, axis="x")                  # the T-handle
    return p


@piece("SnowShovel")
def snow_shovel():
    """A snow shovel lying on the floor along X: 0.84 m handle with a D grip at -X, a blue plastic scoop 0.45 m wide with side lips at +X."""
    p = Prop("GT_SnowShovel_01")
    p.ox = -0.1675
    p.cyl("wood_light", (0.03, 0, HEX * 0.014), 0.014, 0.84, n=6, axis="x")      # from the grip's crosspiece to the socket, not through the hand hole
    p.box("wood_light", (-0.45, 0, 0.015), (0.03, 0.14, 0.03))                       # the grip bar
    for s in (-1, 1):
        p.box("wood_light", (-0.42, s * 0.058, 0.015), (0.06, 0.024, 0.03))          # the sides of the D
    p.box("wood_light", (-0.39, 0, 0.015), (0.024, 0.14, 0.03))                      # the crosspiece closing the D around the handle
    p.box("truck_blue", (0.6, 0, 0.005), (0.4, 0.45, 0.01))                          # the scoop
    for s in (-1, 1):
        p.box("truck_blue", (0.6, s * 0.2165, 0.02), (0.4, 0.015, 0.04))             # the side lips
    p.box("metal_dark", (0.42, 0, 0.012), (0.08, 0.05, 0.024))                       # the socket joining handle and scoop
    return p


@piece("CarBattery")
def car_battery():
    """A 12 V car battery 0.24 x 0.17 x 0.19 m: black case with a white label, two steel terminals, the positive one with a red cap."""
    p = Prop("GT_CarBattery_01")
    p.oy = 0.0025
    p.box("black", (0, 0, 0.095), (0.24, 0.17, 0.19))                                # the case
    p.box("label_white", (0, -0.0875, 0.1), (0.14, 0.005, 0.08))                     # the label, on the front
    for s in (-1, 1):
        p.cyl("metal_galv", (s * 0.08, -0.05, 0.2), 0.012, 0.02, n=8)                # terminals
    p.cyl("cloth_red", (0.08, -0.05, 0.212), 0.016, 0.006, n=8)                      # the cap on the positive terminal
    return p


@piece("BootScraper")
def boot_scraper():
    """A cast-iron boot scraper 0.3 m wide and 0.125 m high: a base plate, two posts and a scraping blade between them."""
    p = Prop("GT_BootScraper_01")
    p.box("black", (0, 0, 0.01), (0.3, 0.12, 0.02))                                   # the base plate
    for s in (-1, 1):
        p.box("black", (s * 0.12, 0, 0.07), (0.02, 0.02, 0.1))                        # the two posts
    p.box("metal_dark", (0, 0, 0.105), (0.24, 0.012, 0.04))                           # the scraping blade
    return p


@piece("ToiletBrush")
def toilet_brush():
    """A toilet brush in its holder, 0.52 m tall: a white holder 0.1 m across and a black handle with a knob standing up out of it."""
    p = Prop("GT_ToiletBrush_01")
    p.cyl("paint_white", (0, 0, 0.1), 0.045, 0.2, n=10, top_radius=0.05)             # the holder
    p.cyl("black", (0, 0, 0.3), 0.01, 0.4, n=8)                                       # the handle, from inside the holder up
    p.cyl("black", (0, 0, 0.505), 0.017, 0.03, n=8)                                   # the knob
    p.cyl("tan", (0, 0, 0.2), 0.034, 0.08, n=10)                                      # the bristles, half out of the holder so they show
    return p


@piece("WorkLight")
def work_light():
    """A clip-on work light 0.25 m high: a black spring clamp on the floor, a pivot arm and a wide steel reflector pointing to -Y."""
    p = Prop("GT_WorkLight_01")
    p.oy = 0.0175
    p.box("black", (0, 0, 0.02), (0.08, 0.12, 0.04))                                  # the clamp
    rod(p, "black", (0, 0.01, 0.04), (0, 0.01, 0.14), w=0.025)                        # the pivot arm
    p.cyl("metal_galv", (0, -0.03, 0.14), 0.11, 0.1, n=12, axis="y", top_radius=0.06)  # the reflector, wide at the front (-Y)
    p.cyl("paint_yellow", (0, -0.08, 0.14), 0.035, 0.03, n=8, axis="y")              # the bulb in the mouth of the reflector
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
    print("tools batch 3 done", len(chosen))


if __name__ == "__main__":
    run()
