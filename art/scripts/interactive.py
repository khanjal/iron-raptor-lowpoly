"""Appliances and storage the player can open (asset list GH-, GT-): fridges, ovens, wardrobes, drawers, lockers, lids...

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/interactive.py", run_name="__main__")
Optional globals: INTERACTIVE_LIST (piece names or group names), STYLE_LIST (default Classic, Modern, Retro, Damaged).
Exports Assets/Art/Global/Interactive/<Style>/GI_<Name>[_<Style>]_01.fbx and writes art/data/interactions.json.

What "interactive" means in the model
  * Every door, drawer and lid is a separate child object whose ORIGIN IS ITS PIVOT, named for its role (Door, DoorL, Drawer1, Lid...).
    Unity opens it by rotating (hinge) or moving (slide) that transform about its own origin; nothing needs to be re-pivoted.
  * `art/data/interactions.json` lists each part's kind, axis and limit so a generic script can drive any prop: hinge limits are
    degrees to open (the sign is the direction), slide limits metres (negative is out towards the front).
  * Slot_<name> empties mark where loose items go (a shelf, a rail, a drawer bottom): the spawn position is the surface the item's
    base sits on, the size is the room above it. A slot with a `part` (Drawer1) rides on that part: parent the spawned items to it.
  * The shipped pose is shut, except Damaged, where parts hang ajar by different amounts (doors off true, a drawer left out).
    Styles are the colour themes of home_styles.py, except where a piece has a @variant here: a style with its own design (the Modern and Retro
    fridges). Everything faces -Y (the front); wall pieces have the origin at the centre.
"""

import importlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
import household
import decor
import home_styles
for _m in (common, props_lib, household, decor, home_styles):
    importlib.reload(_m)
Prop = props_lib.Prop
lathe = props_lib.lathe

ITEMS = {}
VARIANTS = {}      # (piece, style) -> builder, for a style that is a different design and not just the classic one in other colours


def variant(name, style):
    def deco(fn):
        VARIANTS[(name, style)] = fn
        return fn
    return deco


def item(group, name):
    def deco(fn):
        ITEMS[name] = (fn, group)
        return fn
    return deco


# ===== Building blocks ==========================================================================================
def _ajar(role):
    """How far open a part hangs in the Damaged pose, as a fraction of its limit: different for every part, the same every run."""
    return 0.35 + 0.15 * (sum(ord(c) for c in role) % 4)


def shell(p, col, w, d, h, t=0.03, z0=0.0, inner=None, top=True, bottom=True, front=False):
    """An open-fronted box: two sides, back, top and bottom, w x d x h with its base at z0. The front (-Y) is left open for doors.

    front=True closes it with a wall of thickness t (col outside, a thin skin of `inner` inside), up to the rim when the top is open.
    Use it for a lidded container with no front door; damage() then never drops any of its walls, so a Damaged container is still closed."""
    walls = [(col, (-(w - t) / 2, 0, z0 + h / 2), (t, d, h)), (col, ((w - t) / 2, 0, z0 + h / 2), (t, d, h))]
    if top:
        walls.append((col, (0, 0, z0 + h - t / 2), (w - 2 * t, d, t)))
    if bottom:
        walls.append((inner or col, (0, 0, z0 + t / 2), (w - 2 * t, d, t)))
    lo = t if bottom else 0.0
    hi = t if top else 0.0
    walls.append((inner or col, (0, d / 2 - t / 2, z0 + lo + (h - lo - hi) / 2), (w - 2 * t, t, h - lo - hi)))   # back wall, up to the rim when open
    for colour, centre, size in walls:
        p.box(colour, centre, size)
        if front:
            p.keep_solid(centre, size)                              # a closed container keeps all its walls when damaged
    if front:
        skin = min(0.006, t * 0.4)                                  # the inside face is the inner colour, the rest is the outer colour
        zc, fh = z0 + lo + (h - lo - hi) / 2, h - lo - hi
        for colour, y, th in ((col, -d / 2 + (t - skin) / 2, t - skin), (inner or col, -d / 2 + t - skin / 2, skin)):
            p.box(colour, (0, y, zc), (w - 2 * t, th, fh))
            p.keep_solid((0, y, zc), (w - 2 * t, th, fh), new=True)


def shelf(p, col, w, d, z, t=0.02, inset=0.03):
    p.box(col, (0, 0, z), (w - 2 * inset, d - 0.04, t))


def door(p, role, side, col, x0, x1, z0, z1, yf, a, thick=0.03, limit=105, handle="metal_galv", window=None, extra=None):
    """A hinged door in front of an opening spanning x0..x1, z0..z1 on a body whose front face is at y = yf.

    side: right/left (hinged on that vertical edge, turns about Z), bottom (drops down like an oven door), top (flap that lifts out)."""
    yc = yf - thick / 2
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    w, h = x1 - x0, z1 - z0
    if side == "right":
        pivot, axis, lim = (x1, yc, cz), "z", limit
    elif side == "left":
        pivot, axis, lim = (x0, yc, cz), "z", -limit
    elif side == "bottom":
        pivot, axis, lim = (cx, yc, z0), "x", limit
    else:
        pivot, axis, lim = (cx, yc, z1), "x", -limit
    with p.part(role, pivot=pivot, kind="hinge", axis=axis, limit=lim, rest=lim * _ajar(role) * a):
        p.box(col, (cx, yc, cz), (w, thick, h))
        fy = yf - thick - 0.01
        if window is not None:
            p.box("black" if window == "oven" else "metal_dark", (cx, yf - thick - 0.004, cz), (w * 0.8, 0.008, h * 0.66))
            p.box("glass", (cx, fy + 0.004, cz), (w * 0.72, 0.01, h * 0.56))
        if handle:
            if side in ("right", "left"):
                hx = (x0 + 0.06) if side == "right" else (x1 - 0.06)
                p.box(handle, (hx, fy - 0.01, cz), (0.025, 0.035, min(0.3, h * 0.4)))
            else:
                hz = z1 - 0.05 if side == "bottom" else z0 + 0.05
                p.box(handle, (cx, fy - 0.01, hz), (w * 0.7, 0.035, 0.025))
        if extra is not None:
            extra()


# the options of a drawer, all but the first 11 with defaults and passed by keyword; a parameter object would change every caller
def drawer(p, role, col, inner, cx, zc, w, h, d, yf, a, travel=0.35, thick=0.025, handle="metal_galv", pull="bar"):  # NOSONAR
    """A drawer whose front sits flush with a body front at y = yf and runs back d metres; slides out towards -Y by `travel`."""
    depth = d - 0.06
    with p.part(role, pivot=(cx, yf, zc), kind="slide", axis="y", limit=-travel, rest=-travel * _ajar(role) * a):
        p.box(col, (cx, yf - thick / 2, zc), (w, thick, h))
        tw, th = w - 0.08, h * 0.72
        z_floor = zc - h / 2 + 0.03
        p.box(inner, (cx, yf + depth / 2, z_floor), (tw, depth, 0.02))
        for s in (-1, 1):
            p.box(inner, (cx + s * (tw - 0.02) / 2, yf + depth / 2, z_floor + th / 2), (0.02, depth, th))
        p.box(inner, (cx, yf + depth - 0.01, z_floor + th / 2), (tw, 0.02, th))
        if handle:
            if pull == "bar":
                p.box(handle, (cx, yf - thick - 0.012, zc), (min(0.16, w * 0.3), 0.025, 0.02))
            else:
                for s in (-1, 1):
                    p.box(handle, (cx + s * w * 0.28, yf - thick - 0.012, zc), (0.03, 0.025, 0.03))
    p.slot(role, (cx, yf + depth / 2, z_floor + 0.01), (tw - 0.04, depth - 0.04, th), part=role)


def lid_back(p, role, col, cx, y_back, z_top, w, d, thick, a, limit=-110, extra=None, taper=1.0):
    """A lid hinged along the back top edge, y = y_back, resting on a body whose rim is at z_top; opens up and back."""
    with p.part(role, pivot=(cx, y_back, z_top), kind="hinge", axis="x", limit=limit, rest=limit * _ajar(role) * a):
        p.box(col, (cx, y_back - d / 2, z_top + thick / 2), (w, d, thick), taper=taper)
        if extra is not None:
            extra()


# ===== Kitchen ==================================================================================================
@item("kitchen", "Fridge")
def fridge(a=0.0):
    p = Prop("GI_Fridge_01")
    w, d, h = 0.7, 0.7, 1.8
    yf = -d / 2
    p.box("metal_dark", (0, 0, 0.05), (0.66, 0.66, 0.1))
    shell(p, "enamel_cream", w, d, h - 0.1, z0=0.1, inner="paint_white")
    p.box("paint_white", (0, 0, 1.2), (w - 0.06, d - 0.06, 0.03))
    for z in (0.45, 0.75, 1.0, 1.5):
        shelf(p, "clear_glass", w, d, z, t=0.015)
    door(p, "Door", "right", "enamel_cream", -w / 2, w / 2, 0.1, 1.19, yf, a, thick=0.04, limit=100)
    door(p, "DoorFreezer", "right", "enamel_cream", -w / 2, w / 2, 1.21, 1.8, yf, a, thick=0.04, limit=100)
    p.slot("Crisper", (0, 0, 0.13), (0.6, 0.55, 0.3))
    p.slot("Shelf1", (0, 0, 0.46), (0.6, 0.55, 0.27))
    p.slot("Shelf2", (0, 0, 0.76), (0.6, 0.55, 0.22))
    p.slot("Shelf3", (0, 0, 1.01), (0.6, 0.55, 0.17))
    p.slot("Freezer1", (0, 0, 1.215), (0.6, 0.55, 0.27))
    p.slot("Freezer2", (0, 0, 1.51), (0.6, 0.55, 0.27))
    return p


@variant("Fridge", "Retro")
def fridge_retro(a=0.0):
    """One tall rounded door with a single long handle (a 1950s fridge): the classic one is two doors with a freezer on top."""
    p = Prop("GI_Fridge_01")
    w, d, h, z0 = 0.72, 0.68, 1.5, 0.1
    r, thick = 0.03, 0.06                       # the door's edges are half-round: a cylinder as thick as the door
    yf = -d / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.cyl("metal_galv", (sx * (w / 2 - 0.1), sy * (d / 2 - 0.12), z0 / 2), 0.035, z0, n=6, top_radius=0.025)      # round chrome feet
    shell(p, "enamel_cream", w, d, h, z0=z0, inner="paint_white")
    p.box("paint_white", (0, 0.05, z0 + h - 0.18), (w - 0.12, d - 0.18, 0.28))                                          # the little freezer box inside
    p.box("metal_galv", (0, yf + 0.06, z0 + h - 0.18), (w - 0.12, 0.01, 0.28))
    for z in (0.4, 0.7, 1.0):
        shelf(p, "clear_glass", w, d, z, t=0.015)
    z_lo, z_hi = z0 + 0.02 + r, z0 + h - r
    yc, zc = yf - thick / 2, (z_lo + z_hi) / 2

    def rounded_edges():
        for sx in (-1, 1):
            p.cyl("enamel_cream", (sx * (w / 2 - r), yc, zc), r, z_hi - z_lo, n=8)                                      # the two upright edges
        for z in (z_lo, z_hi):
            p.cyl("enamel_cream", (0, yc, z), r, w - 2 * r, n=8, axis="x")                                               # the top and bottom edges
        hx = -w / 2 + 0.08                                                                                              # one long chrome handle, away from the hinge
        for z in (zc + 0.55, zc + 0.05):
            p.box("metal_galv", (hx, yc - thick / 2 - 0.015, z), (0.02, 0.03, 0.03))
        p.box("metal_galv", (hx, yc - thick / 2 - 0.035, zc + 0.3), (0.025, 0.02, 0.7))
        p.box("metal_galv", (0, yc - thick / 2 - 0.002, z_hi - 0.12), (w - 0.1, 0.006, 0.03))                          # a chrome trim band and a badge
        p.box("metal_galv", (0.17, yc - thick / 2 - 0.004, z_hi - 0.12), (0.12, 0.008, 0.05))

    door(p, "Door", "right", "enamel_cream", -w / 2 + r, w / 2 - r, z_lo, z_hi, yf, a, thick=thick, limit=100, handle=None, extra=rounded_edges)
    p.slot("Crisper", (0, 0, z0 + 0.03), (0.6, 0.55, 0.3))
    p.slot("Shelf1", (0, 0, 0.41), (0.6, 0.55, 0.27))
    p.slot("Shelf2", (0, 0, 0.71), (0.6, 0.55, 0.27))
    p.slot("Shelf3", (0, 0, 1.01), (0.6, 0.55, 0.22))
    p.slot("Freezer1", (0, 0.05, z0 + h - 0.32), (0.55, 0.45, 0.25))
    return p


def _french_door_fridge(name, a, dispenser=False):
    p = Prop(name)
    w, d, h = 0.9, 0.72, 1.85
    yf = -d / 2
    p.box("black", (0, 0, 0.05), (w - 0.06, d - 0.06, 0.1))
    shell(p, "metal_galv", w, d, h - 0.1, z0=0.1, inner="paint_white")
    p.box("paint_white", (0, 0, 0.64), (w - 0.06, d - 0.06, 0.03))                                                    # the floor of the fresh-food side
    for z in (0.92, 1.22, 1.52):
        shelf(p, "clear_glass", w, d, z, t=0.015)

    def dispenser_parts():
        """An ice and water dispenser in the left door: a dark recess, a paddle for the glass, a drip grille, a lit ice/water selector."""
        yd = yf - 0.04                                                                                                # the door's front face
        p.box("black", (-0.22, yd - 0.004, 1.3), (0.22, 0.008, 0.4))                                                  # the recess
        p.box("metal_dark", (-0.22, yd - 0.016, 1.34), (0.1, 0.016, 0.16))                                            # the chute housing
        p.box("metal_galv", (-0.22, yd - 0.03, 1.27), (0.07, 0.012, 0.09))                                            # the paddle the glass pushes
        p.box("metal_galv", (-0.22, yd - 0.035, 1.12), (0.2, 0.07, 0.014))                                            # the drip tray
        p.box("black", (-0.22, yd - 0.035, 1.123), (0.17, 0.05, 0.004))                                               # its grille
        p.box("glow_cyan", (-0.22, yd - 0.01, 1.46), (0.1, 0.006, 0.035))                                             # the selector display

    door(p, "DoorL", "left", "metal_galv", -w / 2, 0.0, 0.66, h, yf, a, thick=0.04, limit=100, handle="black",
         extra=dispenser_parts if dispenser else None)
    door(p, "DoorR", "right", "metal_galv", 0.0, w / 2, 0.66, h, yf, a, thick=0.04, limit=100, handle="black",
         extra=lambda: p.box("glow_cyan", (0.26, yf - 0.047, 1.5), (0.1, 0.006, 0.06)))                               # the display
    drawer(p, "DrawerFreezer", "metal_galv", "paint_white", 0.0, 0.38, w - 0.02, 0.54, d, yf, a, travel=0.4, handle="black", pull="bar")
    p.slot("Shelf1", (0, 0, 0.93), (0.8, 0.6, 0.27))
    p.slot("Shelf2", (0, 0, 1.23), (0.8, 0.6, 0.27))
    p.slot("Shelf3", (0, 0, 1.53), (0.8, 0.6, 0.27))
    p.slot("Crisper", (0, 0, 0.66), (0.8, 0.6, 0.24))
    if dispenser:
        p.slot("DispenserGlass", (-0.22, yf - 0.1, 1.2), (0.12, 0.1, 0.16))                                        # where a glass stands under the chute
    return p


@variant("Fridge", "Modern")
def fridge_modern(a=0.0):
    """Two French doors on top and a pull-out freezer drawer below, in steel with black pulls."""
    return _french_door_fridge("GI_Fridge_01", a)


@item("kitchen", "FridgeDispenser")
def fridge_dispenser(a=0.0):
    """The French-door fridge with an ice and water dispenser in the left door (steel, black pulls)."""
    return _french_door_fridge("GI_Fridge_Dispenser_01", a, dispenser=True)


@item("kitchen", "Stove")
def stove(a=0.0):
    p = Prop("GI_Stove_01")
    w, d = 0.6, 0.65
    yf = -d / 2
    shell(p, "enamel_white", w, d, 0.74, z0=0.0, inner="metal_dark", top=False)
    p.box("metal_galv", (0, 0.0, 0.3), (0.5, 0.5, 0.015))
    p.box("enamel_white", (0, 0, 0.82), (w, d, 0.16))
    p.box("black", (0, 0, 0.905), (w - 0.04, d - 0.06, 0.012))
    for x, y in ((-0.14, -0.12), (0.14, -0.12), (-0.14, 0.14), (0.14, 0.14)):
        p.cyl("metal_dark", (x, y, 0.915), 0.09, 0.012, n=8)
    p.box("enamel_white", (0, d / 2 - 0.025, 1.0), (w, 0.05, 0.2))
    for x in (-0.2, -0.07, 0.07, 0.2):
        p.cyl("black", (x, yf - 0.015, 0.8), 0.025, 0.03, n=6, axis="y")
    door(p, "Door", "bottom", "enamel_white", -0.27, 0.27, 0.06, 0.72, yf, a, thick=0.04, limit=90, window="oven")
    p.slot("Oven", (0, 0, 0.31), (0.46, 0.46, 0.4))
    p.slot("BurnerL", (-0.14, -0.12, 0.921), (0.2, 0.2, 0.3))
    p.slot("BurnerR", (0.14, -0.12, 0.921), (0.2, 0.2, 0.3))
    return p


@item("kitchen", "Microwave")
def microwave(a=0.0):
    p = Prop("GI_Microwave_01")
    w, d, h = 0.5, 0.38, 0.3
    shell(p, "enamel_white", w, d, h, t=0.02, inner="metal_dark")
    p.box("fabric_grey", (0.19, -d / 2 - 0.008, h / 2), (0.1, 0.016, 0.26))
    p.box("black", (0.19, -d / 2 - 0.018, h * 0.7), (0.07, 0.006, 0.04))
    door(p, "Door", "left", "enamel_white", -0.25, 0.14, 0.02, h - 0.02, -d / 2, a, thick=0.025, limit=105, window="glass", handle="black")
    p.slot("Inside", (-0.05, 0, 0.04), (0.3, 0.28, 0.2))
    return p


@item("kitchen", "Toaster")
def toaster(a=0.0):
    p = Prop("GI_Toaster_01")
    p.box("metal_galv", (0, 0, 0.09), (0.28, 0.16, 0.18), taper=0.94)
    for x in (-0.06, 0.06):
        p.box("black", (x, 0, 0.181), (0.03, 0.12, 0.008))
    p.box("metal_dark", (0, 0, 0.005), (0.26, 0.15, 0.01))
    with p.part("Lever", pivot=(0.14, 0, 0.14), kind="slide", axis="z", limit=-0.05, rest=0.0):
        p.box("black", (0.15, 0, 0.14), (0.02, 0.025, 0.012))
        p.box("black", (0.142, 0, 0.14), (0.004, 0.012, 0.03))
    p.slot("SlotL", (-0.06, 0, 0.1), (0.03, 0.11, 0.1))
    p.slot("SlotR", (0.06, 0, 0.1), (0.03, 0.11, 0.1))
    return p


@item("kitchen", "Counter_Kitchen")
def counter_kitchen(a=0.0):
    p = Prop("GI_Counter_Kitchen_01")
    w, d, h = 1.2, 0.6, 0.87
    yf = -d / 2
    shell(p, "wood_light", w, d, h, inner="wood_dark", top=False)
    p.box("wood_light", (0, 0, 0.45), (0.03, d, h - 0.06))
    p.box("concrete", (0, 0, 0.89), (w + 0.04, d + 0.04, 0.04))
    p.box("wood_light", (0.3, 0, 0.42), (0.55, d - 0.04, 0.02))
    drawer(p, "Drawer1", "wood_dark", "wood_light", -0.3, 0.74, 0.56, 0.24, d, yf, a, travel=0.4)
    drawer(p, "Drawer2", "wood_dark", "wood_light", -0.3, 0.46, 0.56, 0.28, d, yf, a, travel=0.4)
    drawer(p, "Drawer3", "wood_dark", "wood_light", -0.3, 0.2, 0.56, 0.24, d, yf, a, travel=0.4)
    door(p, "Door", "right", "wood_dark", 0.02, 0.58, 0.04, h - 0.03, yf, a, limit=105)
    p.slot("Cabinet", (0.3, 0, 0.03), (0.5, 0.5, 0.37))
    p.slot("CabinetUpper", (0.3, 0, 0.43), (0.5, 0.5, 0.4))
    p.slot("Top", (0, 0, 0.91), (1.1, 0.5, 0.4))
    return p


@item("kitchen", "BreadBox")
def bread_box(a=0.0):
    p = Prop("GI_BreadBox_01")
    shell(p, "enamel_cream", 0.4, 0.25, 0.2, t=0.015, top=False, inner="paint_white", front=True)
    lid_back(p, "Lid", "enamel_cream", 0, 0.125, 0.2, 0.4, 0.25, 0.03, a, limit=-100,
             extra=lambda: p.box("metal_galv", (0, -0.12, 0.24), (0.06, 0.02, 0.02)))
    p.slot("Inside", (0, 0, 0.015), (0.35, 0.2, 0.17))
    return p


@item("kitchen", "Washer")
def washer(a=0.0):
    p = Prop("GI_Washer_01")
    w, d, h = 0.6, 0.65, 0.9
    yf = -d / 2
    shell(p, "enamel_white", w, d, h, inner="metal_dark")
    t = 0.03                                                       # front panel around a square opening, 0.44 m, centred at z 0.4
    p.box("enamel_white", (0, yf + t / 2, 0.76), (w, t, 0.28))
    p.box("enamel_white", (0, yf + t / 2, 0.09), (w, t, 0.18))
    for sx in (-1, 1):
        p.box("enamel_white", (sx * 0.26, yf + t / 2, 0.4), (0.08, t, 0.44))
    p.box("fabric_grey", (0.0, yf - 0.006, 0.82), (0.5, 0.012, 0.1))
    p.cyl("black", (0.2, yf - 0.02, 0.82), 0.025, 0.02, n=6, axis="y")
    # the round door is centred on the opening (x 0) and hinged on its left edge, 0.26 m from the middle; the pivot and the disc used to be
    # given in different frames, which put the disc 0.26 m too far right (hanging past the machine's side) and made it swing about its own edge
    with p.part("Door", pivot=(-0.26, yf - 0.02, 0.4), kind="hinge", axis="z", limit=-110, rest=-110 * _ajar("Door") * a):
        p.cyl("paint_white", (0.0, yf - 0.02, 0.4), 0.26, 0.03, n=10, axis="y")
        p.cyl("glass", (0.0, yf - 0.045, 0.4), 0.2, 0.012, n=10, axis="y")
        p.box("metal_galv", (0.2, yf - 0.06, 0.4), (0.03, 0.03, 0.12))                       # the handle, on the free edge
    p.slot("Drum", (0, 0, 0.04), (0.4, 0.5, 0.36))
    return p


@item("kitchen", "Dryer")
def dryer(a=0.0):
    """The washer's partner (they stand side by side): the same 0.6 x 0.65 x 0.9 m box, the door hinged on the right so
    that the two doors open away from each other."""
    p = Prop("GI_Dryer_01")
    w, d, h = 0.6, 0.65, 0.9
    yf = -d / 2
    shell(p, "enamel_cream", w, d, h, inner="metal_dark")
    t = 0.03
    p.box("enamel_cream", (0, yf + t / 2, 0.76), (w, t, 0.28))
    p.box("enamel_cream", (0, yf + t / 2, 0.09), (w, t, 0.18))
    for sx in (-1, 1):
        p.box("enamel_cream", (sx * 0.26, yf + t / 2, 0.4), (0.08, t, 0.44))
    p.box("fabric_grey", (-0.1, yf - 0.006, 0.82), (0.3, 0.012, 0.1))                          # the display
    for dx in (0.12, 0.22):
        p.cyl("black", (dx, yf - 0.02, 0.82), 0.025, 0.02, n=6, axis="y")                     # two dials
    p.box("metal_dark", (0.0, yf - 0.006, 0.08), (0.4, 0.012, 0.04))                           # the lint filter slot
    with p.part("Door", pivot=(0.26, yf - 0.02, 0.4), kind="hinge", axis="z", limit=110, rest=110 * _ajar("Door") * a):
        p.cyl("paint_white", (0.0, yf - 0.02, 0.4), 0.26, 0.03, n=10, axis="y")
        p.cyl("glass", (0.0, yf - 0.045, 0.4), 0.2, 0.012, n=10, axis="y")
        p.box("metal_galv", (-0.2, yf - 0.06, 0.4), (0.03, 0.03, 0.12))
    p.slot("Drum", (0, 0, 0.04), (0.4, 0.5, 0.36))
    return p


# ===== Bedroom and storage ======================================================================================
@item("storage", "Wardrobe")
def wardrobe(a=0.0):
    p = Prop("GI_Wardrobe_01")
    w, d, h = 1.0, 0.55, 1.9
    yf = -d / 2
    shell(p, "wood_dark", w, d, h, inner="wood_light")
    shelf(p, "wood_light", w, d, 0.5)
    p.cyl("metal_galv", (0, 0.0, 1.72), 0.015, w - 0.08, n=5, axis="x")
    door(p, "DoorL", "left", "wood_light", -0.5, 0.0, 0.03, 1.88, yf, a, thick=0.025, limit=110)
    door(p, "DoorR", "right", "wood_light", 0.0, 0.5, 0.03, 1.88, yf, a, thick=0.025, limit=110)
    p.slot("Rail", (0, 0, 0.98), (0.9, 0.4, 0.74))                      # hung clothes: base 0.74 m below the rail
    p.slot("Shelf", (0, 0, 0.51), (0.9, 0.45, 0.45))
    p.slot("Floor", (0, 0, 0.06), (0.9, 0.45, 0.42))
    return p


@item("storage", "Dresser")
def dresser(a=0.0):
    p = Prop("GI_Dresser_01")
    w, d, h = 1.2, 0.5, 0.88
    yf = -d / 2
    shell(p, "wood_dark", w, d, h, inner="wood_light", top=False)
    for z in (0.31, 0.59):
        p.box("wood_dark", (0, 0, z), (w - 0.06, d, 0.02))
    p.box("wood_light", (0, 0, 0.9), (w + 0.04, d + 0.04, 0.04))
    for k, zc in enumerate((0.17, 0.45, 0.73)):
        drawer(p, f"Drawer{k + 1}", "wood_light", "wood_dark", 0, zc, w - 0.08, 0.26, d, yf, a, travel=0.38, pull="knob")
    p.slot("Top", (0, 0, 0.92), (1.1, 0.4, 0.4))
    return p


@item("storage", "Nightstand")
def nightstand(a=0.0):
    p = Prop("GI_Nightstand_01")
    w, d, h = 0.45, 0.4, 0.56
    yf = -d / 2
    shell(p, "wood_light", w, d, h, inner="wood_dark", top=False)
    p.box("wood_light", (0, 0, 0.58), (w + 0.03, d + 0.03, 0.03))
    p.box("wood_light", (0, 0, 0.3), (w - 0.06, d, 0.02))
    drawer(p, "Drawer1", "wood_dark", "wood_light", 0, 0.45, w - 0.06, 0.2, d, yf, a, travel=0.3, pull="knob")
    door(p, "Door", "right", "wood_dark", -0.21, 0.21, 0.04, 0.29, yf, a, thick=0.02, limit=100)
    p.slot("Shelf", (0, 0, 0.04), (0.36, 0.3, 0.25))
    p.slot("Top", (0, 0, 0.595), (0.4, 0.35, 0.3))
    return p


@item("storage", "Cabinet")
def cabinet(a=0.0):
    p = Prop("GI_Cabinet_01")
    w, d, h = 0.8, 0.38, 1.2
    yf = -d / 2
    shell(p, "wood_light", w, d, h, inner="paint_white")
    shelf(p, "wood_light", w, d, 0.6)
    door(p, "DoorUL", "left", "wood_light", -0.4, 0.0, 0.62, 1.17, yf, a, thick=0.025, limit=105, window="glass")
    door(p, "DoorUR", "right", "wood_light", 0.0, 0.4, 0.62, 1.17, yf, a, thick=0.025, limit=105, window="glass")
    door(p, "DoorLL", "left", "wood_dark", -0.4, 0.0, 0.03, 0.58, yf, a, thick=0.025, limit=105)
    door(p, "DoorLR", "right", "wood_dark", 0.0, 0.4, 0.03, 0.58, yf, a, thick=0.025, limit=105)
    p.slot("ShelfUpper", (0, 0, 0.61), (0.7, 0.3, 0.5))
    p.slot("ShelfLower", (0, 0, 0.03), (0.7, 0.3, 0.55))
    p.slot("Top", (0, 0, 1.2), (0.7, 0.3, 0.3))
    return p


@item("storage", "Locker")
def locker(a=0.0):
    p = Prop("GI_Locker_01")
    w, d, h = 0.4, 0.5, 1.8
    yf = -d / 2
    shell(p, "tractor_green", w, d, h, inner="metal_dark")
    shelf(p, "metal_galv", w, d, 1.4)
    p.cyl("metal_galv", (0, 0, 1.3), 0.012, w - 0.06, n=5, axis="x")
    door(p, "Door", "right", "tractor_green", -w / 2 + 0.01, w / 2, 0.02, 1.78, yf, a, thick=0.025, limit=110,
         extra=lambda: [p.box("metal_dark", (0, yf - 0.03, z), (0.3, 0.012, 0.16)) for z in (1.45, 0.4)])
    p.slot("Shelf", (0, 0, 1.41), (0.32, 0.4, 0.35))
    p.slot("Floor", (0, 0, 0.03), (0.32, 0.4, 1.25))
    return p


@item("storage", "FilingCabinet")
def filing_cabinet(a=0.0):
    p = Prop("GI_FilingCabinet_01")
    w, d, h = 0.45, 0.6, 1.3
    yf = -d / 2
    shell(p, "metal_dark", w, d, h, inner="fabric_grey", top=False)
    p.box("metal_dark", (0, 0, 1.32), (w + 0.02, d + 0.02, 0.03))
    for z in (0.43, 0.86):
        p.box("metal_dark", (0, 0, z), (w - 0.06, d, 0.02))
    for k, zc in enumerate((0.22, 0.65, 1.08)):
        drawer(p, f"Drawer{k + 1}", "metal_galv", "fabric_grey", 0, zc, w - 0.06, 0.4, d, yf, a, travel=0.5, handle="black")
    p.slot("Top", (0, 0, 1.335), (0.4, 0.5, 0.3))
    return p


@item("storage", "Safe")
def safe(a=0.0):
    p = Prop("GI_Safe_01")
    w, d, h = 0.5, 0.5, 0.6
    yf = -d / 2
    shell(p, "metal_dark", w, d, h, t=0.06, inner="fabric_grey")
    door(p, "Door", "right", "metal_galv", -0.22, 0.25, 0.04, h - 0.04, yf, a, thick=0.05, limit=110, handle=None,
         extra=lambda: (p.cyl("black", (0.0, yf - 0.065, 0.3), 0.08, 0.03, n=8, axis="y"),
                        p.box("metal_dark", (-0.14, yf - 0.07, 0.3), (0.03, 0.03, 0.2))))
    p.slot("Inside", (0, 0, 0.065), (0.34, 0.34, 0.35))
    return p


@item("storage", "Chest")
def chest(a=0.0):
    p = Prop("GI_Chest_01")
    w, d, h = 0.9, 0.5, 0.44
    shell(p, "wood_dark", w, d, h, t=0.04, top=False, inner="wood_light", front=True)
    for x in (-0.3, 0.3):
        for sy in (-1, 1):
            p.box("metal_dark", (x, sy * (d / 2 + 0.005), 0.22), (0.06, 0.012, h))              # straps on the outside only
    p.box("metal_galv", (0, -d / 2 - 0.005, h - 0.1), (0.08, 0.02, 0.1))                          # the latch stays on the body
    lid_back(p, "Lid", "wood_light", 0, d / 2, h, w, d, 0.12, a, limit=-110, taper=0.85,
             extra=lambda: (p.box("metal_dark", (-0.3, -d / 2, 0.06 + h), (0.06, 0.02, 0.13)),
                            p.box("metal_dark", (0.3, -d / 2, 0.06 + h), (0.06, 0.02, 0.13))))
    p.slot("Inside", (0, 0, 0.04), (0.8, 0.4, 0.38))
    return p


@item("storage", "Suitcase")
def suitcase(a=0.0):
    p = Prop("GI_Suitcase_01")
    w, d, h = 0.6, 0.4, 0.14
    shell(p, "fabric_brown", w, d, h, t=0.02, top=False, inner="fabric_mustard", front=True)
    lid_back(p, "Lid", "fabric_brown", 0, d / 2, h, w, d, 0.08, a, limit=-115,
             extra=lambda: [p.box("metal_galv", (x, -d / 2 - 0.005, h + 0.03), (0.04, 0.015, 0.05)) for x in (-0.2, 0.2)])
    p.box("black", (0, -d / 2 - 0.01, h - 0.02), (0.14, 0.03, 0.03))
    p.slot("Inside", (0, 0, 0.02), (0.52, 0.32, 0.12))
    return p


@item("storage", "Toolbox")
def toolbox(a=0.0):
    p = Prop("GI_Toolbox_01")
    shell(p, "cloth_red", 0.5, 0.22, 0.14, t=0.015, top=False, inner="metal_dark", front=True)
    p.box("metal_dark", (0, 0.0, 0.1), (0.015, 0.2, 0.08))
    lid_back(p, "Lid", "cloth_red", 0, 0.11, 0.14, 0.5, 0.22, 0.05, a, limit=-110,
             extra=lambda: p.box("metal_dark", (0, 0.0, 0.215), (0.24, 0.03, 0.03)))
    p.slot("Inside", (0, 0, 0.02), (0.44, 0.18, 0.1))
    return p


@item("storage", "MedicineCabinet")
def medicine_cabinet(a=0.0):
    p = Prop("GI_MedicineCabinet_01")
    w, d, h = 0.4, 0.14, 0.55
    shell(p, "paint_white", w, d, h, t=0.015, z0=-h / 2, inner="fabric_grey")
    shelf(p, "clear_glass", w, d, -0.07, t=0.01, inset=0.015)
    shelf(p, "clear_glass", w, d, 0.1, t=0.01, inset=0.015)
    door(p, "Door", "left", "paint_white", -0.2, 0.2, -h / 2 + 0.015, h / 2 - 0.015, -d / 2, a, thick=0.02, limit=110, handle="metal_galv",
         extra=lambda: p.box("clear_glass", (0, -d / 2 - 0.021, 0), (0.34, 0.006, 0.46)))
    p.slot("ShelfLow", (0, 0, -0.06), (0.34, 0.1, 0.15))
    p.slot("ShelfHigh", (0, 0, 0.11), (0.34, 0.1, 0.15))
    return p


# ===== Utilities and service ====================================================================================
@item("utilities", "FuseBox")
def fuse_box(a=0.0):
    p = Prop("GI_FuseBox_01")
    w, d, h = 0.4, 0.1, 0.5
    shell(p, "metal_dark", w, d, h, t=0.015, z0=-h / 2, inner="fabric_grey")
    for k in range(6):
        p.box("black", (-0.1 + (k % 2) * 0.2, -0.03, 0.14 - (k // 2) * 0.1), (0.07, 0.03, 0.05))
    door(p, "Door", "left", "metal_dark", -0.2, 0.2, -h / 2, h / 2, -d / 2, a, thick=0.015, limit=110, handle="metal_galv",
         extra=lambda: p.box("cloth_red", (0.1, -d / 2 - 0.02, -0.18), (0.08, 0.008, 0.05)))
    p.slot("Inside", (0, 0.0, -0.23), (0.3, 0.06, 0.1))
    return p


@item("service", "VendingMachine")
def vending_machine(a=0.0):
    p = Prop("GI_VendingMachine_01")
    w, d, h = 0.85, 0.8, 1.9
    yf = -d / 2
    shell(p, "cloth_red", w, d, h, inner="metal_dark")
    rows = (0.55, 0.85, 1.15, 1.45)
    for z in rows:
        shelf(p, "metal_galv", w, d, z, t=0.015)
    p.box("cloth_red", (0.3, yf - 0.01, 1.1), (0.25, 0.02, 1.2))
    p.box("black", (0.3, yf - 0.025, 1.3), (0.16, 0.012, 0.3))
    p.box("cloth_red", (0, yf - 0.01, 0.41), (w - 0.06, 0.02, 0.18))             # lower front, open where the flap is (x -0.3..0.1)
    p.box("cloth_red", (-0.35, yf - 0.01, 0.175), (0.1, 0.02, 0.29))
    p.box("cloth_red", (0.25, yf - 0.01, 0.175), (0.3, 0.02, 0.29))
    p.box("glow_cyan", (0, yf - 0.012, 1.8), (0.5, 0.012, 0.1))
    door(p, "Door", "left", "cloth_red", -0.385, 0.175, 0.5, 1.7, yf, a, thick=0.03, limit=100, handle="metal_galv",
         extra=lambda: (p.box("glass", (-0.105, yf - 0.032, 1.1), (0.5, 0.008, 1.1)),))
    door(p, "Flap", "top", "black", -0.3, 0.1, 0.08, 0.3, yf - 0.02, a, thick=0.02, limit=60, handle=None)
    for k, z in enumerate(rows):
        p.slot(f"Row{k + 1}", (-0.1, 0, z + 0.0075), (0.5, 0.55, 0.27))
    p.slot("Tray", (-0.1, yf + 0.15, 0.04), (0.3, 0.2, 0.2))
    return p


@item("service", "Cooler")
def cooler(a=0.0):
    p = Prop("GI_Cooler_01")
    w, d, h = 0.7, 0.4, 0.4
    shell(p, "truck_blue", w, d, h, t=0.04, top=False, inner="paint_white", front=True)
    for sx in (-1, 1):
        p.box("metal_dark", (sx * 0.37, 0, 0.3), (0.04, 0.14, 0.04))
    lid_back(p, "Lid", "paint_white", 0, d / 2, h, w + 0.02, d + 0.02, 0.06, a, limit=-110)
    p.slot("Inside", (0, 0, 0.04), (0.6, 0.3, 0.34))
    return p


@item("outdoor", "Dumpster")
def dumpster(a=0.0):
    p = Prop("GI_Dumpster_01")
    w, d, h = 1.8, 0.9, 0.9
    z0 = 0.14
    shell(p, "tractor_green", w, d, h, t=0.05, z0=z0, top=False, inner="metal_dark", front=True)
    p.box("metal_dark", (0, -d / 2 - 0.005, z0 + h - 0.05), (w, 0.03, 0.06))
    p.box("metal_dark", (0, d / 2 + 0.005, z0 + h - 0.05), (w, 0.03, 0.06))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.cyl("rubber", (sx * (w / 2 - 0.12), sy * (d / 2 - 0.12), 0.07), 0.07, 0.05, n=8, axis="x")
    top = z0 + h
    lid_back(p, "LidL", "black", -w / 4, d / 2 + 0.02, top, w / 2 - 0.01, d + 0.04, 0.04, a, limit=-115)
    lid_back(p, "LidR", "black", w / 4, d / 2 + 0.02, top, w / 2 - 0.01, d + 0.04, 0.04, a, limit=-115)
    p.slot("Inside", (0, 0, z0 + 0.05), (1.6, 0.8, 0.7))
    return p


@item("outdoor", "TrashCan")
def trash_can(a=0.0):
    p = Prop("GI_TrashCan_01")
    lathe(p, "metal_galv", [(0.0, 0.0001), (0.0, 0.22), (0.58, 0.26), (0.58, 0.24), (0.03, 0.2), (0.03, 0.0001)], n=8)
    p.cyl("metal_dark", (0, 0, 0.45), 0.262, 0.03, n=8)
    with p.part("Lid", pivot=(0, 0.26, 0.6), kind="hinge", axis="x", limit=-100, rest=-100 * _ajar("Lid") * a):
        p.cyl("metal_dark", (0, 0.0, 0.615), 0.27, 0.03, n=8)
        p.box("black", (0, -0.2, 0.64), (0.1, 0.03, 0.03))
    p.slot("Inside", (0, 0, 0.04), (0.38, 0.38, 0.5))
    return p


@item("outdoor", "Mailbox")
def mailbox(a=0.0):
    p = Prop("GI_Mailbox_01")
    p.box("wood_dark", (0, 0.0, 0.525), (0.08, 0.08, 1.05))
    shell(p, "metal_dark", 0.2, 0.4, 0.2, t=0.012, z0=1.05, inner="fabric_grey")
    door(p, "Flap", "bottom", "metal_dark", -0.1, 0.1, 1.05, 1.25, -0.2, a, thick=0.012, limit=90, handle=None)
    with p.part("Flag", pivot=(0.11, 0.0, 1.2), kind="hinge", axis="y", limit=90, rest=0.0):
        p.box("cloth_red", (0.11, 0.0, 1.27), (0.012, 0.03, 0.14))
    p.slot("Inside", (0, 0, 1.062), (0.16, 0.34, 0.15))
    return p


# ===== Build all, in every style ===============================================================================
STYLES = ("Classic", "Modern", "Retro", "Damaged")


def _name(prop, style):
    if style != "Classic" and prop.name.endswith("_01") and f"_{style}_" not in prop.name:
        prop.name = prop.name[:-3] + f"_{style}_01"
    return prop


def run():
    names = globals().get("INTERACTIVE_LIST")
    styles = globals().get("STYLE_LIST") or STYLES
    count, y = 0, 0.0
    props_lib.INTERACTIONS.clear()
    for key, (fn, group) in ITEMS.items():
        if names and key not in names and group not in names:
            continue
        x = 0.0
        for style in styles:
            props_lib.THEME = {} if style == "Classic" else home_styles.THEMES[style]
            try:
                prop = VARIANTS.get((key, style), fn)(a=1.0 if style == "Damaged" else 0.0)
            finally:
                props_lib.THEME = {}
            prop = _name(prop, style)
            if style == "Damaged":
                seed = sum(ord(c) * (i + 1) for i, c in enumerate(key)) % 1000
                prop.damage(seed=seed, drop=0.25, tilt=0.0, grime=2)
                prop.post = None                      # parts are parented after the body, so the body must not move
            obj, coll = prop.finish()
            common.export_fbx(coll, f"Assets/Art/Global/Interactive/{style}/{prop.name}.fbx")
            obj.location = (x, y, 0)
            x += max(1.4, obj.dimensions.x + 0.5)
            count += 1
        y += 2.6
    out = props_lib.write_interactions()
    print("interactive done", count, "props written to", out.name)


if __name__ == "__main__":
    run()
