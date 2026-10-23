"""Alien set dressing for the landed ship's inner wall ring (issue #143): lockers, a stasis pod, specimen jars, a cable conduit, a holo-map table,
a medical couch, a tool rack and a sample rack. Low-poly (a few hundred triangles each), the shared faceted palette, no new colours.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/ship_props.py", run_name="__main__")
Optional global SHIP_PROP_LIST, e.g. ["pod", "jars"] (keys of SHIP_PROPS). Each exports to Assets/Art/Global/Vehicles/<name>.fbx.
Optional global SHIP_PROP_LAYOUT = True lays the finished props out in the ship's plan (LAYOUT, which Assets/Editor/FarmsteadShipInterior.cs
repeats) in the scene, for a look; it is for pictures only and nothing is exported from it.

Every model is a prop like the rest: it faces -Y (the front is the side you walk up to), the origin is on the floor at the middle of its
footprint, 1 unit = 1 m. A wall piece has its BACK on +Y (the ship's wall) and is placed with its back flush on one of the ship's flat
wall panels. run() prints how far each model's back is behind its origin (the `Back` numbers in Assets/Editor/FarmsteadShipInterior.cs: copy
them there when a model changes) and FarmsteadSelfTest checks the built pieces against the ship's walls, deck, ceiling and the clear areas.

Nothing hangs in the air: every part rests on, or is fixed to, something else in the same model (a hologram stands on a beam, a hanging
tool on a hook on the back plate, a jar's specimen on a plinth inside it).
"""

import importlib
import math
import sys
from math import cos, radians, sin
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Blender is shared by several sessions, each running scripts from its own checkout: a `common` another checkout imported first would
# make this one write its FBX into that checkout. Drop modules that came from somewhere else so they are imported from here.
for _n in ("common", "props_lib", "emitters"):
    _m = sys.modules.get(_n)
    if _m is not None and Path(getattr(_m, "__file__", "") or "").resolve().parent != _HERE:
        sys.modules.pop(_n, None)

import bpy
from mathutils import Vector

import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
rod = props_lib.rod
lathe = props_lib.lathe
ball = props_lib.ball

GREY, DARK, METAL, CYAN, GREEN, AMBER, VIOLET, GLASS = "alien_grey", "alien_dark", "metal_dark", "glow_cyan", "glow_green", "glow_amber", "alien_violet", "glass"

# nominal depth (into the room from the wall) and width along the wall, metres; the models are built from these
DEPTH = {"lockers": 0.55, "pod": 0.90, "jars": 0.62, "conduit": 0.34, "holo": 1.50, "couch": 0.95, "tools": 0.46, "samples": 0.40,
         "helm": 1.30, "navscreen": 0.50, "radar": 0.90, "crates": 0.90, "drums": 0.80, "bunk": 0.95, "mess": 1.10}
WIDTH = {"lockers": 2.10, "pod": 0.90, "jars": 2.00, "conduit": 1.30, "holo": 1.50, "couch": 2.00, "tools": 1.50, "samples": 1.20,
         "helm": 1.40, "navscreen": 1.90, "radar": 0.90, "crates": 2.30, "drums": 1.50, "bunk": 2.00, "mess": 1.60}


# ===== Pieces ====================================================================================================================

def plinth(p, w, d, h=0.12, colour=METAL, y=0.0):
    """A low dark foot under a cabinet, a little inside its outline."""
    p.box(colour, (0, y, h / 2), (w - 0.06, d - 0.06, h))


def glow_strip(p, w, y, z, colour=CYAN, t=0.03):
    p.box(colour, (0, y, z), (w, t, t))


# ----- Lockers --------------------------------------------------------------------------------------------------------------------

def lockers(name="GV_ShipLockers_01"):
    """A bank of three tall storage lockers along the wall: grey doors with a lit slit and a vertical handle, a dark plinth and cap.
    2.1 x 0.55 m, 2.1 m tall."""
    p = Prop(name)
    W, D, H = WIDTH["lockers"], DEPTH["lockers"], 2.1
    plinth(p, W, D, 0.14)
    p.box(DARK, (0, 0.015, 0.14 + (H - 0.14 - 0.1) / 2), (W, D + 0.03, H - 0.24))              # the carcass (its back is the cap's)
    p.box(METAL, (0, 0.0, H - 0.05), (W + 0.06, D + 0.06, 0.10))                               # cap
    p.box(CYAN, (0, -D / 2 - 0.035, H - 0.05), (W - 0.3, 0.012, 0.03))                          # a glow strip along the front of the cap
    dw = (W - 0.08) / 3
    for k in range(3):
        x = -W / 2 + 0.04 + dw * (k + 0.5)
        y = -D / 2 - 0.02
        z0, z1 = 0.20, H - 0.20
        p.box(GREY, (x, y, (z0 + z1) / 2), (dw - 0.04, 0.04, z1 - z0))                         # door
        p.box(DARK, (x, y - 0.025, z1 - 0.28), (0.07, 0.012, 0.34))                            # slit frame
        p.box(CYAN if k != 1 else AMBER, (x, y - 0.03, z1 - 0.28), (0.035, 0.012, 0.28))       # the lit slit
        p.box(METAL, (x + dw / 2 - 0.12, y - 0.045, (z0 + z1) / 2 + 0.05), (0.035, 0.035, 0.40))   # handle bar
        p.box(METAL, (x + dw / 2 - 0.12, y - 0.0, (z0 + z1) / 2 + 0.20), (0.035, 0.05, 0.05))   # its two standoffs, in the door behind it
        p.box(METAL, (x + dw / 2 - 0.12, y - 0.0, (z0 + z1) / 2 - 0.10), (0.035, 0.05, 0.05))
        for zz in (z0 + 0.22, z0 + 0.42, z0 + 0.62):
            p.box(DARK, (x - 0.1, y - 0.022, zz), (0.34, 0.012, 0.035))                         # vent slats on the lower door
    return p


# ----- Stasis pod -----------------------------------------------------------------------------------------------------------------

def pod(name="GV_ShipPod_01"):
    """An upright stasis pod: a grey eight-sided capsule on a dark base, a lit green window with a small grey silhouette in it, a cyan
    glow ring at the top and a cable into the wall. 0.9 m wide and deep, 2.2 m tall."""
    p = Prop(name)
    R, H = 0.45, 2.2
    ap = R * cos(radians(22.5))                                                               # an eight-sided cylinder turned so a flat faces the front: flat-to-flat 2 * ap
    p.cyl(DARK, (0, 0, 0.12), R, 0.24, n=8, rot=(0, 0, 22.5))                                   # base
    p.cyl(METAL, (0, 0, 0.275), R * 0.95, 0.07, n=8, rot=(0, 0, 22.5))                         # a collar
    p.cyl(GREY, (0, 0, 1.25), R * 0.88, 1.88, n=8, rot=(0, 0, 22.5))                            # the capsule
    p.cyl(DARK, (0, 0, H - 0.18), R * 0.98, 0.18, n=8, rot=(0, 0, 22.5))                        # top housing
    p.cyl(CYAN, (0, 0, H - 0.30), R * 0.95, 0.05, n=8, rot=(0, 0, 22.5))                        # a ring of light
    p.cyl(METAL, (0, 0, H + 0.01), R * 0.7, 0.04, n=8, top_radius=R * 0.55, rot=(0, 0, 22.5))   # a cap, on the capsule's top (z 2.19)
    fy = -R * 0.88 * cos(radians(22.5))                                                       # the capsule's front face
    p.box(DARK, (0, fy - 0.012, 1.3), (0.50, 0.03, 1.36))                                       # window frame
    p.box(GREEN, (0, fy - 0.032, 1.3), (0.42, 0.012, 1.28))                                     # the green glass
    # the sleeper: a flat silhouette on the glass, a grey head with two big dark eyes, narrow shoulders
    p.box(GREY, (0, fy - 0.045, 1.52), (0.19, 0.012, 0.26), taper=0.8)
    for s in (-1, 1):
        p.box(DARK, (s * 0.055, fy - 0.054, 1.54), (0.07, 0.01, 0.045), rot=(0, 0, s * 18))
    p.box(GREY, (0, fy - 0.045, 1.14), (0.30, 0.012, 0.50), taper=0.55)                         # the body
    for z in (0.62, 2.0):                                                                     # latches on the frame
        p.box(METAL, (0.0, fy - 0.012, z), (0.20, 0.03, 0.05))
    # a cable down the back into the floor, and the wall bracket it hangs on
    p.box(METAL, (0, R * 0.88 * cos(radians(22.5)) + 0.03, H - 0.5), (0.30, 0.06, 0.12))
    rod(p, "black", (0.15, ap, H - 0.5), (0.15, ap + 0.08, 0.03), 0.05)
    return p


# ----- Specimen jars --------------------------------------------------------------------------------------------------------------

def jar(p, cx, cy, specimen, jh=1.0, jr=0.21, z0=0.80):
    """A specimen jar standing on a surface at z0: a base and lid with four thin glass bars between, a lit liquid line at the bottom and
    the specimen on a plinth inside. The bars, not a panel: the palette has no alpha, a solid jar would hide what is in it."""
    p.cyl(METAL, (cx, cy, z0 + 0.04), jr + 0.03, 0.08, n=6)
    p.cyl(GREEN, (cx, cy, z0 + 0.09), jr - 0.02, 0.02, n=6)                                    # the liquid, a lit disc where it lies
    p.cyl(METAL, (cx, cy, z0 + jh - 0.04), jr + 0.03, 0.08, n=6)
    for k in range(4):
        a = radians(45 + 90 * k)
        p.box(GLASS, (cx + jr * cos(a), cy + jr * sin(a), z0 + jh / 2), (0.04, 0.04, jh - 0.08), rot=(0, 0, math.degrees(a)))
    p.cyl(DARK, (cx, cy, z0 + 0.13), 0.09, 0.06, n=6)                                           # the plinth the specimen stands on
    z = z0 + 0.16
    if specimen == "cow":                                                                     # a cow: white body, dark patches, head, legs and a pink muzzle
        k = 0.72                                                                              # scaled to stand inside the bars (head and muzzle within 0.2 m of the middle)

        def at(dx, dy, dz):
            return (cx + dx * k, cy + dy * k, z + dz * k)

        def sz(w, d, h):
            return (w * k, d * k, h * k)
        for lx in (-0.07, 0.07):
            for ly in (-0.11, 0.11):
                p.box("fur_grey", at(lx, ly, 0.06), sz(0.04, 0.04, 0.12))
        p.box("paint_white", at(0, 0, 0.17), sz(0.20, 0.34, 0.16))
        p.box(DARK, at(0.05, 0.04, 0.26), sz(0.10, 0.12, 0.02))
        p.box("paint_white", at(0, -0.20, 0.22), sz(0.13, 0.12, 0.13))
        p.box("pink", at(0, -0.27, 0.19), sz(0.09, 0.04, 0.07))
        for sx in (-1, 1):
            p.box("horn_cream", at(sx * 0.06, -0.20, 0.30), sz(0.025, 0.025, 0.05))
        rod(p, "black", at(0, 0.17, 0.20), at(0, 0.19, 0.30), 0.02)                            # a tail
        back = z + 0.27 * k                                                                   # the top of the dark patch on its back
        lid = z0 + jh - 0.02                                                                  # the underside of the lid
        p.cyl(METAL, (cx, cy + 0.04 * k, (back + lid) / 2), 0.015, lid - back, n=4)            # a probe from the lid down to the animal's back
    elif specimen == "plant":                                                                 # a plant with a root ball
        p.box("dirt", (cx, cy, z + 0.05), (0.18, 0.18, 0.10), taper=0.7)
        p.cyl("plant_green", (cx, cy, z + 0.32), 0.02, 0.46, n=4)
        for k, a in enumerate((0, 100, 200, 300)):
            zz = z + 0.16 + 0.09 * k
            rod(p, "leaf_dark", (cx, cy, zz), (cx + 0.14 * cos(radians(a)), cy + 0.14 * sin(radians(a)), zz + 0.07), 0.035)
        p.cyl("plant_green", (cx, cy, z + 0.58), 0.05, 0.08, n=6, top_radius=0.0)               # a bud
    else:                                                                                     # a little alien: a lit green body with three legs and a head
        ball(p, GREEN, (cx, cy, z + 0.29), 0.12, n=6, rings=3)
        p.cyl("alien_green", (cx, cy, z + 0.2), 0.05, 0.14, n=6)
        for a in (90, 210, 330):
            rod(p, "alien_green", (cx + 0.03 * cos(radians(a)), cy + 0.03 * sin(radians(a)), z + 0.2), (cx + 0.07 * cos(radians(a)), cy + 0.07 * sin(radians(a)), z + 0.0), 0.03)      # the legs end on the plinth
        for s in (-1, 1):
            p.box(DARK, (cx + s * 0.05, cy - 0.10, z + 0.33), (0.05, 0.03, 0.04))


def jars(name="GV_ShipJars_01"):
    """A low cabinet with three specimen jars on it: a cow, a plant, a small green alien. 2.0 x 0.62 m, 1.85 m tall."""
    p = Prop(name)
    W, D = WIDTH["jars"], DEPTH["jars"]
    plinth(p, W, D, 0.12)
    p.box(DARK, (0, 0, 0.12 + 0.32), (W, D, 0.64))                                             # the cabinet
    p.box(GREY, (0, 0, 0.78), (W + 0.04, D + 0.04, 0.04))                                      # its top
    p.box(CYAN, (0, -D / 2 - 0.006, 0.62), (W - 0.4, 0.012, 0.035))                             # a lit strip on its front
    for k in range(3):
        x = -W / 2 + 0.30 + k * 0.70
        p.box(METAL, (x, -D / 2 - 0.012, 0.35), (0.50, 0.02, 0.34))                            # three small hatches
        p.box(AMBER if k == 1 else CYAN, (x + 0.16, -D / 2 - 0.026, 0.46), (0.04, 0.01, 0.04))
    for k, kind in enumerate(("cow", "plant", "alien")):
        jar(p, -W / 2 + 0.34 + k * 0.66, 0.0, kind, z0=0.80)
    return p


# ----- Cable conduit --------------------------------------------------------------------------------------------------------------

def cable_run(name="GV_ShipConduit_01"):
    """A run of pipes and cable bundles up the wall, floor to ceiling, with lit junction boxes and a hose that loops out and into the deck.
    1.3 x 0.34 m, 2.8 m tall (the wall is 2.9 m over the deck)."""
    p = Prop(name)
    W, D, H = WIDTH["conduit"], DEPTH["conduit"], 2.8
    back = D / 2 + 0.05                                                                       # the back of the plate and of the footing: the model's back
    yb = back - 0.03                                                                          # the plate's front face is at y = yb - 0.01
    p.box(DARK, (0, back - 0.02, H / 2), (W, 0.04, H))                                        # back plate against the wall
    p.box(METAL, (0, back - 0.07, 0.06), (W, 0.14, 0.12))                                     # footing
    ys = yb - 0.07
    for k, x in enumerate((-0.42, -0.14, 0.18, 0.44)):                                       # four vertical runs: two pipes and two cable bundles
        if k % 2 == 0:
            p.cyl(METAL, (x, ys, H / 2), 0.075, H - 0.1, n=6)
            p.cyl(GREY, (x, ys, H / 2), 0.09, 0.08, n=6)                                       # a flange at mid height
        else:
            for dx in (-0.03, 0.03):
                p.cyl("black", (x + dx, ys + 0.02 * (1 if dx > 0 else -1), H / 2), 0.035, H - 0.1, n=6)
    for z in (0.5, 1.2, 1.9, 2.6):                                                            # clamps across all of them, bolted to the plate
        p.box(METAL, (0, ys + 0.005, z), (W - 0.1, 0.05, 0.06))
        p.box(METAL, (0, back - 0.06, z), (W - 0.1, 0.06, 0.05))
    for z, x, c in ((0.85, -0.14, CYAN), (1.55, 0.44, AMBER), (2.25, -0.42, CYAN)):           # junction boxes with a lit eye
        p.box(DARK, (x, ys - 0.05, z), (0.26, 0.14, 0.26))
        p.box(c, (x, ys - 0.125, z), (0.10, 0.015, 0.10))
    p.box(CYAN, (0.0, ys - 0.07, H - 0.05), (W - 0.2, 0.03, 0.03))                              # a lit strip across the top
    # a hose that leaves the bundle, loops out into the room and goes into the deck: pieces end on each other
    pts = [(-0.14, ys - 0.02, 0.35), (-0.14, -0.05, 0.28), (0.10, -0.12, 0.20), (0.30, -0.10, 0.02)]
    for a, b in zip(pts, pts[1:]):
        rod(p, "black", a, b, 0.05)
    for a in pts[1:-1]:
        p.cyl("black", a, 0.032, 0.07, n=6)
    return p


# ----- Holo-map table -------------------------------------------------------------------------------------------------------------

def holo_table(name="GV_ShipHoloTable_01"):
    """A holo-map table: a hexagonal top on a tapering pedestal, a glowing rim, and over it a projected map of the farm (a hex of light with a few
    lit blocks for buildings and an amber marker) held on a beam. 1.5 m across (hexagon, corner to corner), 1.86 m tall."""
    p = Prop(name)
    lathe(p, DARK, [(0.0, 0.62), (0.12, 0.60), (0.20, 0.30), (0.72, 0.30)], n=6)               # a flared foot to a column
    lathe(p, METAL, [(0.72, 0.42), (0.80, 0.42)], n=6)
    lathe(p, GREY, [(0.80, 0.74), (0.88, 0.74)], n=6)                                          # the top plate
    lathe(p, CYAN, [(0.88, 0.70), (0.90, 0.70)], n=6, cap=False)                               # a lit ring on it
    lathe(p, DARK, [(0.88, 0.42), (0.91, 0.42)], n=6)                                          # the emitter plate
    p.cyl(CYAN, (0, 0, 1.28), 0.02, 0.74, n=4)                                                 # the beam from the plate up to the map
    lathe(p, CYAN, [(1.64, 0.62), (1.66, 0.62)], n=6, z0=0.0)                                   # the map: a hex of light
    for a, r, w, h, c in ((20, 0.30, 0.16, 0.12, CYAN), (140, 0.32, 0.22, 0.09, CYAN), (250, 0.24, 0.12, 0.16, VIOLET), (80, 0.42, 0.10, 0.08, CYAN)):
        p.box(c, (r * cos(radians(a)), r * sin(radians(a)), 1.66 + h / 2), (w, w * 0.8, h), rot=(0, 0, a))        # buildings
    p.box(AMBER, (0.0, 0.0, 1.66 + 0.08), (0.04, 0.04, 0.16))                                  # an amber marker pin ...
    p.box(AMBER, (0.0, 0.0, 1.66 + 0.18), (0.08, 0.08, 0.04), rot=(0, 0, 45))                  # ... with a head
    rod(p, CYAN, (-0.35, -0.2, 1.67), (0.1, -0.05, 1.67), 0.02)                                # a lit route across the map
    rod(p, CYAN, (0.1, -0.05, 1.67), (0.05, 0.3, 1.67), 0.02)
    return p


# ----- Medical couch --------------------------------------------------------------------------------------------------------------

def couch(name="GV_ShipCouch_01"):
    """A medical (examination) couch with restraint straps, a raised head end and a scanner arm that rises behind it and bends over it with a
    lamp. 2.0 x 0.95 m, 1.8 m tall to the lamp."""
    p = Prop(name)
    W = 2.0
    p.box(DARK, (0, 0.05, 0.08), (1.5, 0.7, 0.16))                                            # foot plate
    p.box(METAL, (0, 0.05, 0.36), (0.5, 0.32, 0.40))                                           # the column the bed sits on
    p.box(GREY, (0.15, 0.0, 0.62), (1.6, 0.72, 0.16), taper=1.0)                               # the padded bed
    p.box(DARK, (0.15, 0.0, 0.535), (1.5, 0.64, 0.03))                                         # a dark skirt under it
    p.box(GREY, (-0.78, 0.0, 0.76), (0.46, 0.72, 0.14), rot=(0, 12, 0))                        # the raised head end (a pillow slope: +Y rotation lowers the +X end, so the -X end rises)
    for x in (-0.25, 0.30, 0.78):                                                              # straps across the bed, a lit buckle at each
        p.box(AMBER, (x, 0.0, 0.705), (0.08, 0.80, 0.018))
        p.box(METAL, (x, -0.375, 0.745), (0.10, 0.05, 0.03))                                   # a buckle on the rail
        p.box(CYAN, (x, -0.375, 0.766), (0.035, 0.03, 0.012))
    for s in (-1, 1):                                                                          # side rails, on the bed's edges
        p.box(METAL, (0.15, s * 0.375, 0.72), (1.6, 0.03, 0.04))
    # the scanner arm: up behind the head end (back, +Y), over the bed, ending in a lamp
    rod(p, METAL, (-0.2, 0.62, 0.04), (-0.2, 0.62, 1.55), 0.09)
    p.box(DARK, (-0.2, 0.45, 0.06), (0.30, 0.50, 0.12))
    rod(p, METAL, (-0.2, 0.62, 1.55), (-0.2, 0.05, 1.75), 0.07)
    p.cyl(DARK, (-0.2, 0.05, 1.75), 0.20, 0.10, n=8)
    p.cyl(CYAN, (-0.2, 0.05, 1.69), 0.15, 0.04, n=8)
    return p


# ----- Tool rack ------------------------------------------------------------------------------------------------------------------

def tool_rack(name="GV_ShipToolRack_01"):
    """An equipment rack: a back plate with three shelves holding crates and canisters, and a row of tools hung on hooks above them. 1.5 x 0.46 m,
    2.0 m tall."""
    p = Prop(name)
    W, D, H = WIDTH["tools"], DEPTH["tools"], 2.0
    p.box(GREY, (0, D / 2 - 0.02, H / 2), (W, 0.04, H))
    for s in (-1, 1):
        p.box(DARK, (s * (W / 2 - 0.03), 0.0, H / 2), (0.06, D, H))                            # side frames
    p.box(METAL, (0, 0.0, 0.05), (W, D, 0.10))                                                 # bottom
    p.box(METAL, (0, 0.0, H - 0.03), (W, D, 0.06))                                             # top
    for z in (0.55, 1.0):                                                                      # two shelves (the top of the rack, hooks above them, is open)
        p.box(GREY, (0, 0.0, z), (W - 0.1, D - 0.04, 0.04))
        p.box(CYAN, (0, -(D - 0.04) / 2 - 0.006, z - 0.03), (W - 0.2, 0.012, 0.02))                  # a strip on the shelf's front edge
    # what is on them: crates and canisters standing on the shelf tops (the shelf at z has its top at z + 0.02)
    p.box("metal_galv", (-0.42, 0.02, 0.10 + 0.17), (0.40, 0.30, 0.34))
    p.box("alien_gold", (0.05, 0.02, 0.10 + 0.10), (0.30, 0.30, 0.20))
    p.box("metal_galv", (0.48, 0.02, 0.10 + 0.13), (0.26, 0.30, 0.26))
    for k, x in enumerate((-0.45, -0.25, -0.05)):
        p.cyl("alien_green" if k != 1 else AMBER, (x, 0.02, 0.57 + 0.15), 0.07, 0.30, n=6)    # canisters
        p.cyl(METAL, (x, 0.02, 0.57 + 0.32), 0.04, 0.04, n=6)
    p.box("alien_gold", (0.35, 0.0, 0.57 + 0.11), (0.50, 0.28, 0.22))
    p.box(DARK, (0.35, -0.145, 0.57 + 0.11), (0.30, 0.012, 0.05))
    p.box(GREY, (-0.3, 0.0, 1.02 + 0.08), (0.60, 0.26, 0.16))                                    # a toolbox
    p.box(CYAN, (-0.3, -0.135, 1.02 + 0.08), (0.2, 0.012, 0.03))
    p.cyl(METAL, (0.30, 0.0, 1.02 + 0.10), 0.10, 0.20, n=6)
    p.cyl(CYAN, (0.30, 0.0, 1.02 + 0.22), 0.07, 0.04, n=6)                                      # a lamp unit
    # tools on hooks along the back plate, above the shelves: each hook is a stub from the plate, the tool hangs from it
    yh = D / 2 - 0.06
    for x in (-0.55, -0.25, 0.1, 0.45):
        p.box(METAL, (x, yh, 1.62), (0.05, 0.08, 0.04))
    rod(p, METAL, (-0.55, yh - 0.03, 1.60), (-0.55, yh - 0.03, 1.15), 0.035)                  # a probe with a lit tip
    p.cyl(CYAN, (-0.55, yh - 0.03, 1.13), 0.03, 0.05, n=6)
    p.box(METAL, (-0.25, yh - 0.03, 1.40), (0.05, 0.04, 0.42))                                  # tongs: two arms
    p.box(METAL, (-0.19, yh - 0.03, 1.40), (0.05, 0.04, 0.42), rot=(0, 8, 0))
    p.box(DARK, (-0.22, yh - 0.03, 1.60), (0.14, 0.05, 0.05))
    p.box(DARK, (0.1, yh - 0.04, 1.43), (0.12, 0.08, 0.34))                                      # a scanner wand: a body ...
    p.box(CYAN, (0.1, yh - 0.085, 1.5), (0.07, 0.012, 0.10))                                     # ... with a lit pad
    p.box(METAL, (0.45, yh - 0.03, 1.38), (0.08, 0.05, 0.50))                                    # a long wrench
    p.box(METAL, (0.45, yh - 0.03, 1.15), (0.16, 0.05, 0.08))
    return p


# ----- Sample rack ----------------------------------------------------------------------------------------------------------------

def sample_rack(name="GV_ShipSampleRack_01"):
    """A rack of sample vials: a dark frame on the wall with three shelves, four vials on each, lit in four colours. 1.2 x 0.40 m, 1.6 m tall."""
    p = Prop(name)
    W, D, H = WIDTH["samples"], DEPTH["samples"], 1.6
    p.box(DARK, (0, D / 2 - 0.02, H / 2 + 0.05), (W, 0.04, H - 0.1))
    p.box(METAL, (0, 0.0, 0.05), (W, D, 0.10))
    for s in (-1, 1):
        p.box(METAL, (s * (W / 2 - 0.025), 0.0, H / 2 + 0.05), (0.05, D, H - 0.1))
    p.box(METAL, (0, 0.0, H - 0.025), (W, D, 0.05))
    cols = (GREEN, AMBER, CYAN, VIOLET)
    for r, z in enumerate((0.40, 0.78, 1.16)):
        p.box(GREY, (0, 0.0, z), (W - 0.1, D - 0.06, 0.04))
        p.box(DARK, (0, -D / 2 + 0.03, z - 0.04), (W - 0.1, 0.02, 0.04))
        for c in range(4):
            x = -W / 2 + 0.21 + c * 0.26
            cc = cols[(r + c) % 4]
            p.cyl(cc, (x, -0.02, z + 0.02 + 0.085), 0.045, 0.17, n=5)                           # the vial, lit in its colour (opaque glass would hide it)
            p.cyl(GLASS, (x, -0.02, z + 0.02 + 0.185), 0.05, 0.03, n=5)                         # a glass shoulder
            p.box(METAL, (x, -0.02, z + 0.02 + 0.215), (0.07, 0.07, 0.03))                      # the cap
    p.box(CYAN, (0, -D / 2 - 0.006, 0.06), (W - 0.2, 0.012, 0.035))                          # on the bottom plate's front
    for k in range(3):                                                                         # an index plate on the top frame: lit ticks
        p.box(CYAN if k != 1 else AMBER, (-0.2 + k * 0.2, -D / 2 - 0.005, H - 0.025), (0.08, 0.012, 0.025))
    return p


# ----- Bridge: helm, nav screen, radar post ------------------------------------------------------------------------------------------

def helm(name="GV_ShipHelm_01"):
    """A pilot's station: a control desk against the wall (a leaning control face with lit buttons, two sticks, a screen over it) and a pilot's chair in front, facing it.
    1.4 m wide, 1.35 m deep, 1.65 m tall."""
    p = Prop(name)
    W = WIDTH["helm"]
    p.box(DARK, (0, 0.05, 0.40), (W, 0.50, 0.80))                                                # the desk's body
    p.box(METAL, (0, 0.05, 0.03), (W + 0.06, 0.56, 0.06))                                        # its foot
    p.box(GREY, (0, -0.02, 0.86), (W, 0.46, 0.08), rot=(14, 0, 0))                               # the control face: its front leans down (+X rotation lowers the -Y end)
    for k, c in enumerate((CYAN, AMBER, GREEN, CYAN, VIOLET)):                                     # buttons on it
        p.box(c, (-0.45 + 0.225 * k, -0.07, 0.905), (0.09, 0.07, 0.03), rot=(14, 0, 0))
    for sx in (-1, 1):                                                                           # two sticks
        p.cyl(METAL, (sx * 0.52, -0.02, 0.98), 0.025, 0.2, n=6)
        p.cyl(AMBER, (sx * 0.52, -0.02, 1.1), 0.045, 0.06, n=6)
    p.box(DARK, (0, 0.2, 1.27), (W - 0.1, 0.05, 0.72))                                          # the screen's frame, standing on the desk's back edge
    p.box("screen", (0, 0.173, 1.32), (W - 0.24, 0.012, 0.5))
    for k in range(5):                                                                           # lines of lit text on the screen
        p.box(CYAN if k % 2 == 0 else GREEN, (-0.18, 0.165, 1.48 - 0.1 * k), (0.62 - 0.07 * k, 0.012, 0.03))
    p.box(AMBER, (0.38, 0.165, 1.28), (0.2, 0.012, 0.2))                                         # and a chart
    # the pilot's chair, facing the desk: a foot and a pillar, the seat, a back rest at the room side and two arms
    p.box(METAL, (0, -0.4, 0.03), (0.14, 0.7, 0.06))                                             # a floor rail the chair slides on, from the desk's foot
    p.cyl(METAL, (0, -0.78, 0.05), 0.3, 0.1, n=6)
    p.cyl(DARK, (0, -0.78, 0.25), 0.07, 0.4, n=6)
    p.box(DARK, (0, -0.78, 0.52), (0.55, 0.55, 0.12))
    p.box(GREY, (0, -1.03, 0.9), (0.55, 0.1, 0.7))
    p.box(CYAN, (0, -1.09, 1.02), (0.3, 0.02, 0.06))
    for sx in (-1, 1):
        p.box(METAL, (sx * 0.31, -0.8, 0.68), (0.06, 0.45, 0.05))
        p.box(METAL, (sx * 0.31, -0.58, 0.6), (0.05, 0.05, 0.16))
    return p


def navscreen(name="GV_ShipNavScreen_01"):
    """A navigation display: a low cabinet with a lit strip, and over it a tall screen showing a star chart (a dark pane with lit dots and a route), bolted to the wall by
    two arms. 1.9 m wide, 0.5 m deep, 2.1 m tall."""
    p = Prop(name)
    W, D = WIDTH["navscreen"], DEPTH["navscreen"]
    plinth(p, W, D, 0.1)
    p.box(DARK, (0, 0.0, 0.1 + 0.3), (W, D - 0.06, 0.6))
    p.box(GREY, (0, 0.0, 0.72), (W + 0.04, D - 0.02, 0.04))
    p.box(CYAN, (0, -(D - 0.06) / 2 - 0.006, 0.5), (W - 0.4, 0.012, 0.035))
    p.box(DARK, (0, 0.13, 1.4), (W, 0.1, 1.4))                                                   # the frame, standing on the cabinet's top
    p.box("screen", (0, 0.075, 1.45), (W - 0.2, 0.012, 1.1))                                     # the pane
    p.box(CYAN, (0, 0.067, 1.45), (0.9, 0.012, 0.012), rot=(0, 25, 0))                           # a route
    p.box(CYAN, (0.25, 0.067, 1.62), (0.7, 0.012, 0.012), rot=(0, -20, 0))
    for x, z, c in ((-0.6, 1.8, CYAN), (-0.2, 1.3, GREEN), (0.3, 1.75, AMBER), (0.55, 1.2, CYAN), (-0.45, 1.05, GREEN), (0.05, 1.85, CYAN), (0.7, 1.9, VIOLET)):
        p.box(c, (x, 0.067, z), (0.07, 0.012, 0.07))                                           # stars
    for sx in (-1, 1):                                                                           # two arms from the frame to the wall
        p.box(METAL, (sx * (W / 2 - 0.2), 0.2, 1.45), (0.1, 0.1, 0.1))
    return p


def radar_post(name="GV_ShipRadarPost_01"):
    """A radar post: a round pedestal with a lit ring, a column, and over it a dish with a ring on three struts, a sweep line and a blip. 0.9 m across, 1.75 m tall."""
    p = Prop(name)
    p.cyl(DARK, (0, 0.0, 0.3), 0.42, 0.6, n=8, top_radius=0.34, rot=(0, 0, 22.5))
    p.cyl(CYAN, (0, 0.0, 0.62), 0.36, 0.04, n=8, rot=(0, 0, 22.5))
    p.cyl(GREY, (0, 0.0, 0.7), 0.4, 0.14, n=8, rot=(0, 0, 22.5))                                  # the pedestal's top
    p.cyl(METAL, (0, 0.0, 1.03), 0.07, 0.56, n=6)                                                # the column
    p.cyl(DARK, (0, 0.0, 1.3), 0.3, 0.06, n=8)                                                   # the dish: a flat bowl
    p.cyl(GREY, (0, 0.0, 1.34), 0.22, 0.04, n=8)
    p.cyl(CYAN, (0, 0.0, 1.38), 0.03, 0.12, n=6)
    for a in (0, 120, 240):                                                                      # three struts holding a ring over the dish
        x, y = 0.26 * cos(radians(a + 90)), 0.26 * sin(radians(a + 90))
        rod(p, METAL, (x, y, 1.32), (x * 0.5, y * 0.5, 1.7), 0.03)
    p.cyl(CYAN, (0, 0.0, 1.72), 0.14, 0.03, n=8)
    p.box(GREEN, (0.0, -0.06, 1.365), (0.3, 0.02, 0.01), rot=(0, 0, 35))                          # a sweep line on the dish
    p.box(AMBER, (0.13, -0.05, 1.375), (0.04, 0.04, 0.03))                                        # a blip
    return p


# ----- Cargo: crates, drums -------------------------------------------------------------------------------------------------------

def crates(name="GV_ShipCrates_01"):
    """A stack of cargo crates: two big crates side by side on a pallet with a smaller one on each, strapped, with stencilled marks, a hazard label and a lit lock.
    2.3 m wide, 0.9 m deep, 1.55 m tall."""
    p = Prop(name)
    p.box("wood_dark", (0, 0.0, 0.06), (2.3, 0.9, 0.12))                                         # the pallet
    for sx, colour, w, h in ((-0.6, "metal_galv", 1.05, 0.95), (0.6, "alien_gold", 1.05, 0.8)):
        p.box(colour, (sx, 0.0, 0.12 + h / 2), (w, 0.8, h))
        p.box(METAL, (sx, 0.0, 0.12 + h * 0.5), (w + 0.03, 0.82, 0.07))                          # a strap round it
        p.box(METAL, (sx, 0.0, 0.12 + h * 0.18), (w + 0.03, 0.82, 0.05))
        p.box("paint_yellow", (sx - 0.2, -0.405, 0.12 + h * 0.72), (0.3, 0.012, 0.16))           # a stencil
        p.box("black", (sx - 0.2, -0.41, 0.12 + h * 0.72), (0.2, 0.012, 0.04))
    p.box("rust", (-0.6, 0.0, 0.12 + 0.95 + 0.2), (0.95, 0.7, 0.4))                              # a smaller crate on the left one
    p.box(AMBER, (-0.6, -0.355, 0.12 + 0.95 + 0.25), (0.1, 0.012, 0.06))                        # its lit lock
    p.box("alien_dark", (0.6, 0.0, 0.12 + 0.8 + 0.18), (0.85, 0.7, 0.36))                       # and a dark one on the right
    p.box("label_red", (0.6, -0.355, 0.12 + 0.8 + 0.2), (0.3, 0.012, 0.16))                      # a hazard label
    p.box("label_white", (0.6, -0.36, 0.12 + 0.8 + 0.2), (0.1, 0.012, 0.08))
    return p


def drums(name="GV_ShipDrums_01"):
    """Three fuel drums standing on a pallet, with hazard bands and caps, and a fourth lying along the back edge. 1.5 m wide, 0.8 m deep, 0.95 m tall."""
    p = Prop(name)
    p.box("wood_dark", (0, 0.0, 0.05), (1.5, 0.8, 0.1))
    for k, colour in enumerate(("truck_blue", "rust", "truck_blue")):
        x = -0.5 + 0.5 * k
        p.cyl(colour, (x, -0.1, 0.1 + 0.4), 0.22, 0.8, n=8)
        p.cyl("paint_yellow", (x, -0.1, 0.1 + 0.55), 0.225, 0.1, n=8)
        p.cyl(METAL, (x, -0.1, 0.1 + 0.82), 0.1, 0.04, n=6)
        p.cyl("black", (x, -0.1, 0.1 + 0.2), 0.225, 0.05, n=8)
    p.cyl("alien_gold", (0.0, 0.26, 0.1 + 0.2), 0.2, 1.3, n=8, axis="x")                         # the drum lying on the pallet's back edge
    p.cyl("paint_yellow", (-0.3, 0.26, 0.1 + 0.2), 0.205, 0.1, n=8, axis="x")
    p.cyl("paint_yellow", (0.3, 0.26, 0.1 + 0.2), 0.205, 0.1, n=8, axis="x")
    return p


# ----- Quarters: bunk, mess table -------------------------------------------------------------------------------------------------

def bunk(name="GV_ShipBunk_01"):
    """A two-level bunk along the wall: four posts, two mattresses (blue under, grey over) with pillows and a folded blanket, a ladder at one end and a lit reading
    light. 2.0 m long, 0.95 m deep, 1.9 m tall."""
    p = Prop(name)
    L, D = WIDTH["bunk"], 0.95
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box(METAL, (sx * (L / 2 - 0.05), sy * (D / 2 - 0.05), 1.0), (0.08, 0.08, 1.8))       # the posts, from the floor frame up
    p.box(METAL, (0, 0.0, 0.05), (L, D, 0.1))                                                    # the floor frame
    for z, colour in ((0.36, "fabric_blue"), (1.28, "fabric_grey")):
        p.box(DARK, (0, 0.0, z - 0.08), (L - 0.04, D - 0.04, 0.05))                              # the bed's base
        p.box(colour, (0, 0.0, z), (L - 0.14, D - 0.14, 0.12))                                   # the mattress
        p.box("linen", (-L / 2 + 0.3, 0.0, z + 0.09), (0.45, 0.5, 0.07))                         # the pillow
        p.box("fabric_red", (0.35, 0.0, z + 0.075), (0.7, D - 0.2, 0.04))                        # a folded blanket
        p.box(METAL, (0, -D / 2 + 0.04, z + 0.2), (L - 0.04, 0.04, 0.04))                        # a rail along the open side
    for z in (0.6, 0.9, 1.2):                                                                    # a ladder at the foot end: rungs between its two posts
        p.box(METAL, (L / 2 - 0.05, 0.0, z), (0.04, D - 0.1, 0.04))
    p.box(AMBER, (-L / 2 + 0.05, D / 2 - 0.05, 1.7), (0.12, 0.12, 0.06))                         # a reading light on the top bunk's back post
    return p


def mess(name="GV_ShipMess_01"):
    """A mess table against the wall: a table with a lit edge, a bench along its front, a few plates and a mug, a vent on two posts over it. 1.6 m wide, 1.1 m deep,
    1.3 m tall."""
    p = Prop(name)
    W = WIDTH["mess"]
    p.box(DARK, (0, 0.0, 0.37), (0.12, 0.5, 0.74))                                               # a pedestal
    p.box(METAL, (0, 0.0, 0.03), (0.7, 0.6, 0.06))
    p.box(GREY, (0, 0.0, 0.77), (W, 0.7, 0.06))                                                  # the table top
    p.box(CYAN, (0, -0.352, 0.77), (W - 0.1, 0.012, 0.04))                                       # a lit edge
    for sx in (-1, 1):
        p.box(DARK, (sx * 0.6, -0.62, 0.22), (0.08, 0.3, 0.44))                                  # the bench's legs ...
    p.box("fabric_brown", (0, -0.62, 0.46), (W - 0.1, 0.3, 0.06))                                # ... and seat
    p.box(METAL, (0, -0.31, 0.2), (0.06, 0.62, 0.06))                                            # a stretcher from the bench to the pedestal
    p.box(DARK, (0, -0.62, 0.22), (0.08, 0.3, 0.44))                                             # and a middle leg under the bench, where it ends
    for k, x in enumerate((-0.5, 0.0, 0.5)):
        p.cyl("porcelain", (x, -0.1, 0.81), 0.1, 0.02, n=8)                                      # plates
        p.box("food_orange" if k != 1 else "meat_red", (x, -0.1, 0.835), (0.08, 0.06, 0.03))
    p.cyl("copper", (0.7, 0.15, 0.85), 0.045, 0.1, n=6)                                          # a mug
    for sx in (-1, 1):                                                                           # a vent on the wall over the table, on two posts from the table's back edge
        p.box(METAL, (sx * 0.4, 0.3, 0.97), (0.05, 0.05, 0.38))
    p.box(DARK, (0, 0.3, 1.2), (0.9, 0.1, 0.3))
    p.box(AMBER, (0, 0.245, 1.2), (0.5, 0.012, 0.03))
    return p


# ===== Build, layout and export ==========================================================================================================

SHIP_PROPS = {
    "lockers": lockers, "pod": pod, "jars": jars, "conduit": cable_run, "holo": holo_table, "couch": couch, "tools": tool_rack, "samples": sample_rack,
    "helm": helm, "navscreen": navscreen, "radar": radar_post, "crates": crates, "drums": drums, "bunk": bunk, "mess": mess,
}

# The interior types' plans, repeated in Assets/Editor/FarmsteadShipInterior.cs (Plans): (model key, wall panel k, offset along the panel, free-standing radius or 0).
# Panel 0 is the doorway, panel 6 the back wall with the console on it, the numbers count clockwise from above in the game and (the FBX importer mirrors a model's X,
# which makes the plan come out the same way round) clockwise here too. Offsets are along the panel towards the next number. A free-standing piece (the holo table) has
# its origin that far from the middle instead of its back on the wall. Panel 4 is in front of the power core: only shallow pieces (the conduit) go there.
LAYOUTS = {
    "lab": [
        ("pod", 1, 0.5, 0), ("jars", 2, 0.0, 0), ("couch", 3, 0.0, 0), ("conduit", 4, 0.0, 0), ("samples", 5, -0.5, 0),
        ("tools", 7, 0.5, 0), ("lockers", 8, 0.0, 0), ("holo", 9, 0.0, 3.95), ("conduit", 10, 0.0, 0), ("pod", 11, -0.5, 0),
    ],
    "bridge": [
        ("helm", 1, 0.5, 0), ("navscreen", 2, 0.0, 0), ("helm", 3, 0.0, 0), ("conduit", 4, 0.0, 0), ("radar", 5, -0.5, 0),
        ("radar", 7, 0.5, 0), ("navscreen", 8, 0.0, 0), ("holo", 9, 0.0, 3.95), ("helm", 10, 0.0, 0), ("helm", 11, -0.5, 0),
    ],
    "cargo": [
        ("drums", 1, 0.5, 0), ("crates", 2, 0.0, 0), ("crates", 3, 0.0, 0), ("conduit", 4, 0.0, 0), ("drums", 5, -0.5, 0),
        ("tools", 7, 0.5, 0), ("crates", 8, 0.0, 0), ("drums", 9, 0.0, 0), ("crates", 10, 0.0, 0), ("drums", 11, -0.5, 0),
    ],
    "quarters": [
        ("pod", 1, 0.5, 0), ("bunk", 2, 0.0, 0), ("bunk", 3, 0.0, 0), ("conduit", 4, 0.0, 0), ("samples", 5, -0.5, 0),
        ("pod", 7, 0.5, 0), ("mess", 8, 0.0, 0), ("bunk", 9, 0.0, 0), ("bunk", 10, 0.0, 0), ("pod", 11, -0.5, 0),
    ],
}
LAYOUT = LAYOUTS["lab"]


def lay_out(objs, plan="lab"):
    """Put the built props where LAYOUTS[plan] says, in the ship's plan (Blender frame: front -Y, the ring numbered clockwise), for a picture. Returns the copies."""
    out = []
    r_wall = 5.16                                                       # where the backs stand: FarmsteadShipInterior.WallFace
    for key, k, off, free in LAYOUTS[plan]:
        a = radians(-90 - 30 * k)
        o = objs[key]
        back = max(v.co.y for v in o.data.vertices)
        inst = o.copy()
        inst.data = o.data
        bpy.context.scene.collection.objects.link(inst)
        radial = Vector((cos(a), sin(a), 0.0))
        tangent = Vector((sin(a), -cos(a), 0.0))                         # towards the next panel number
        inst.rotation_euler = (0, 0, a - radians(90))                    # the prop's back (+Y) turns to the wall: its +Y points along the radial
        inst.location = radial * (free if free else r_wall - back) + tangent * off
        out.append(inst)
    return out


def run():
    names = globals().get("SHIP_PROP_LIST") or list(SHIP_PROPS)
    x = 0.0
    out = {}
    for key in names:
        prop = SHIP_PROPS[key]()
        obj, coll = prop.finish()
        print(common.stats(obj), "back %.3f m behind the origin" % max(v.co.y for v in obj.data.vertices))
        common.export_fbx(coll, f"Assets/Art/Global/Vehicles/{prop.name}.fbx")
        obj.location.x = x
        x += max(1.0, obj.dimensions.x + 0.6)
        out[key] = obj
    plan = globals().get("SHIP_PROP_LAYOUT")
    if plan and all(k in out for k in SHIP_PROPS):
        globals()["PLACED"] = lay_out(out, plan if isinstance(plan, str) else "lab")
    print("ship props done", names)
    return out


if __name__ == "__main__":
    run()
    for _n in ("common", "props_lib", "emitters"):          # leave the next session's import to find its own copy
        sys.modules.pop(_n, None)
