"""Vehicles and the crashed ship (asset list GV-01, GV-20, GV-30...): flat faceted models from simple solids.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/vehicles.py", run_name="__main__")
Optional global VEHICLE_LIST, e.g. ["pickup"]. Exports Assets/Art/<Global|Farm>/Vehicles/<name>.fbx.

Real sizes: the pickup is 5.4 x 2.0 x 1.9 m, the tractor 4.1 x 2.4 x 2.8 m, the sheriff cruiser 5.0 m. Vehicles face -Y with
their origin on the ground at the centre; wheels are separate boxes so Unity can spin them later (this first pass is one mesh).
Colours come from the palette (`truck_blue`, `tractor_green`, ...); recolour a variant by changing the first argument.
"""

import importlib
import sys
import math
from math import radians
from pathlib import Path

import bmesh
from mathutils import Vector

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Blender is shared by several sessions, each running scripts from its own checkout: a module another checkout imported first would make this one build with its
# code and write its FBX into that checkout. Drop modules that came from somewhere else so they are imported from here.
for _n in ("common", "props_lib", "emitters", "ship_hulls"):
    _m = sys.modules.get(_n)
    if _m is not None and Path(getattr(_m, "__file__", "") or "").resolve().parent != _HERE:
        sys.modules.pop(_n, None)
import common
import props_lib
import ship_hulls
for _m in (common, props_lib, ship_hulls):
    importlib.reload(_m)
Prop = props_lib.Prop
wheel = props_lib.wheel


def pickup(body="truck_blue", name="GV_Pickup_01"):
    """A farm pickup truck. Hood, cab with glass, open bed, bumpers, lights, four wheels."""
    p = Prop(name)
    # chassis and body shell
    p.box("black", (0, 0, 0.5), (1.7, 5.0, 0.18))                                    # frame
    p.box(body, (0, -1.85, 0.82), (1.96, 1.5, 0.62))                                # hood and front wings
    p.box(body, (0, -1.85, 1.13), (1.8, 1.5, 0.1))                                  # hood top, flat, level with the base of the windscreen
    p.box(body, (0, -0.1, 0.92), (1.96, 1.9, 0.5))                                   # cab lower
    p.box(body, (0, 0.05, 1.62), (1.82, 1.4, 0.12))                                  # roof
    for s in (-1, 1):
        p.box(body, (s * 0.88, 0.05, 1.37), (0.08, 1.2, 0.5), rot=(0, 0, 0))       # door pillars
        p.box("glass", (s * 0.925, -0.12, 1.35), (0.02, 0.95, 0.4))                 # side windows
    p.box("glass", (0, -0.78, 1.37), (1.6, 0.06, 0.42), rot=(-24, 0, 0))             # windscreen
    p.box("glass", (0, 0.82, 1.37), (1.5, 0.05, 0.36), rot=(10, 0, 0))               # rear window
    # bed
    p.box(body, (0, 1.75, 0.72), (1.9, 2.0, 0.1))                                    # bed floor
    for s in (-1, 1):
        p.box(body, (s * 0.93, 1.75, 1.0), (0.1, 2.0, 0.5))                         # side walls
        p.box("black", (s * 0.93, 1.75, 1.27), (0.12, 2.0, 0.06))                   # rails
    p.box(body, (0, 2.7, 1.0), (1.9, 0.1, 0.5))                                      # tailgate
    p.box(body, (0, 0.78, 1.0), (1.9, 0.1, 0.5))                                     # bed front wall
    # bumpers, grille, lights
    p.box("metal_galv", (0, -2.68, 0.58), (2.0, 0.18, 0.22))
    p.box("metal_galv", (0, 2.8, 0.58), (2.0, 0.16, 0.2))
    p.box("black", (0, -2.62, 0.9), (1.1, 0.06, 0.34))                              # grille
    for s in (-1, 1):
        p.box("paint_yellow", (s * 0.72, -2.63, 0.98), (0.3, 0.06, 0.18))           # headlights
        p.box("cloth_red", (s * 0.8, 2.78, 0.9), (0.18, 0.06, 0.2))                 # tail lights
    # wheels
    for s in (-1, 1):
        for y in (-1.75, 1.7):
            wheel(p, "rubber", "metal_galv", s * 0.9, y, 0.38, 0.38, 0.28, n=10)
            p.box("black", (s * 0.94, y, 0.62), (0.2, 0.9, 0.12))                   # wheel arch lip
    return p


def tractor(body="tractor_green", name="GV_Tractor_01"):
    """A farm tractor: hood, open cab with a roof, big rear wheels, small front wheels, exhaust."""
    p = Prop(name)
    p.box("black", (0, 0, 0.7), (1.0, 3.6, 0.3))                                     # chassis
    p.box(body, (0, -1.15, 1.25), (1.0, 1.7, 0.85), taper=0.9)                       # engine hood
    p.box("black", (0, -2.02, 1.2), (0.7, 0.05, 0.5))                                # grille
    p.box(body, (0, 0.45, 1.1), (1.1, 1.3, 0.6))                                     # rear body
    p.box("black", (0, 0.2, 1.5), (0.45, 0.45, 0.2))                                 # seat base, on the body
    p.box("rubber", (0, 0.4, 1.83), (0.5, 0.1, 0.46))                                # seat back, on the base
    for sx in (-1, 1):
        for sy in (-0.4, 1.0):
            p.box(body, (sx * 0.5, sy, 2.14), (0.08, 0.08, 1.48))                    # cab posts, from the body up to the roof
    p.box(body, (0, 0.3, 2.88), (1.45, 1.8, 0.1))                                    # canopy roof
    p.cyl("black", (0.3, -1.4, 2.25), 0.05, 1.2, n=6)                                 # exhaust stack
    p.cyl("metal_dark", (0.3, -1.4, 2.88), 0.08, 0.08, n=6)
    for s in (-1, 1):
        wheel(p, "rubber", body, s * 1.12, 0.5, 0.85, 0.85, 0.55, n=12)              # big rear wheels
        p.box("metal_dark", (s * 0.75, 0.5, 1.15), (0.5, 1.5, 0.1))                  # mudguards
        wheel(p, "rubber", body, s * 0.85, -1.55, 0.5, 0.5, 0.28, n=10)              # small front wheels
        p.box("paint_yellow", (s * 0.4, -2.04, 1.55), (0.22, 0.05, 0.14))            # headlights
    p.box("black", (0, -1.55, 0.5), (1.5, 0.08, 0.08))                               # front axle
    return p


def cruiser(body="paint_white", stripe="navy", name="GV_SheriffCruiser_01"):
    """A police-style sedan: used for the sheriff (white/tan) and, recoloured, for FBI SUVs and the MIB sedan."""
    p = Prop(name)
    p.box("black", (0, 0, 0.45), (1.7, 4.6, 0.2))
    p.box(body, (0, 0, 0.75), (1.84, 4.8, 0.5))                                      # body
    p.box(body, (0, -0.1, 1.2), (1.6, 2.2, 0.45), taper=0.88)                        # cabin
    p.box("glass", (0, -0.1, 1.2), (1.66, 2.0, 0.34), taper=0.9)
    p.box(stripe, (0, 0, 0.75), (1.88, 4.0, 0.14))                                   # side stripe
    p.box("metal_galv", (0, -2.45, 0.55), (1.9, 0.14, 0.2))
    p.box("metal_galv", (0, 2.45, 0.55), (1.9, 0.14, 0.2))
    p.box("cloth_red", (-0.2, 0.0, 1.48), (0.45, 0.2, 0.1))                           # light bar: red and blue
    p.box("truck_blue", (0.2, 0.0, 1.48), (0.45, 0.2, 0.1))
    for s in (-1, 1):
        p.box("paint_yellow", (s * 0.65, -2.42, 0.82), (0.3, 0.05, 0.14))
        p.box("cloth_red", (s * 0.7, 2.42, 0.82), (0.26, 0.05, 0.14))
        for y in (-1.5, 1.5):
            wheel(p, "rubber", "metal_galv", s * 0.88, y, 0.34, 0.34, 0.24, n=10)
    return p


# The landed ship's dimensions, shared with Assets/Editor/FarmsteadLayout.cs (Ship* constants) which builds the colliders: change both.
SHIP_INNER_RADIUS = 5.2          # inside the walls
SHIP_WALL = 0.5                  # wall thickness
SHIP_DECK = 0.5                  # the deck is this high; a ramp climbs to it
SHIP_CEILING = 3.4               # underside of the ceiling
SHIP_PANELS = 12                 # wall panels round the ring; panel 0 (the front) is the doorway
SHIP_DOOR_HEIGHT = 2.4           # above the deck
SHIP_RAMP_RUN = 3.6              # how far the ramp reaches out from the deck edge


HULL_N = 40                      # sides of the saucer hull: 9 degrees each, so three of them are the width of the doorway (2.9 m at the rim)
HULL_PHASE = 4.5                 # turned so a hull face is centred on the front (-Y)
# the saucer's outline, (height, radius): a belly under the deck, a skirt, the widest rim, then a dome up to the cockpit. At the wall panels' height
# (the interior ring below) it stays outside them, so nothing of the walkable shell shows through the skin, and the rim stays within 0.4 m of
# the deck edge so the player cannot walk under a visible overhang.
BELLY_PROFILE = [(0.18, 3.4), (0.5, 6.0), (1.2, 6.05)]                                  # dark, under the rim
HULL_PROFILE = [(1.2, 6.05), (2.0, 6.25), (2.6, 6.1), (3.0, 5.9), (3.4, 5.6), (3.8, 4.9), (4.2, 4.0), (4.5, 3.0), (4.7, 2.0), (4.8, 1.0)]   # light, rim to dome


def _skin(p, colour, profile, n=HULL_N, phase=HULL_PHASE, cut_rings=(), cut_faces=(), cap=True, cap_bottom=None, cap_top=None):
    """A solid of revolution skinned by hand so a doorway can be left out of it: faces k in cut_faces between the rings in cut_rings (the quad
    between ring i and ring i + 1 is i) are not made. cap closes both ends; cap_bottom and cap_top override it for one end (the belly and the hull
    meet at z 1.2, and a disc at each end there would be a second floor 0.7 m over the deck)."""
    from math import cos, radians, sin
    c, s = cos(radians(phase)), sin(radians(phase))
    bm = p._bm(colour)
    vr = []
    for z, r in profile:
        ring = common.ring_z(z, 0.0, 0.0, max(r, 0.0001), max(r, 0.0001), n=n)
        vr.append([bm.verts.new(Vector((pt.x * c - pt.y * s, pt.x * s + pt.y * c, pt.z))) for pt in ring])
    for i in range(len(vr) - 1):
        for k in range(n):
            if i in cut_rings and k in cut_faces:
                continue
            a, b = vr[i], vr[i + 1]
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if cap if cap_bottom is None else cap_bottom:
        bm.faces.new(vr[0])
    if cap if cap_top is None else cap_top:
        bm.faces.new(vr[-1][::-1])
    bmesh.ops.delete(bm, geom=[v for ring in vr for v in ring if not v.link_faces], context="VERTS")      # the ring points of the cut faces, left with no face
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def crashed_ship(name="GV_CrashedShip_01"):
    """The crew's ship, landed hard: a flying saucer you can walk into. A saucer hull (belly, a glowing rim, a dome and a glass cockpit) with the
    doorway cut out of the front, a ramp down from it, an interior with a raised deck, a thin ring of wall panels, a flat ceiling, seats and
    a power core (the console is a separate model: terminals.py), belly thrusters, swept tail fins, a bent antenna and a torn patch. Level on purpose: the floor has to be walkable (the colliders
    are the cylinders and panels of FarmsteadBuilder.BuildLandedShip, under the skin). Front is -Y (the ramp), origin at the centre on the ground."""
    p = Prop(name)
    r_in, t, deck, ceil = SHIP_INNER_RADIUS, SHIP_WALL, SHIP_DECK, SHIP_CEILING
    side = 2 * r_in * math.tan(math.radians(180 / SHIP_PANELS)) + 0.06
    ph = 180 / SHIP_PANELS
    # the three hull faces round the front (-Y, 270 degrees). Face k is the quad between ring points k and k + 1, which sit at 360 * k / HULL_N + HULL_PHASE
    # degrees, so the face centred on 270 is k = 29 and the doorway is 28, 29, 30. (It was 29, 30, 31: centred on 279 degrees, a doorway 0.9 m off the
    # glow posts, the ramp and the wall panel that is the doorway in the colliders.)
    front = int(round((270 - HULL_PHASE) / (360 / HULL_N) - 0.5))
    door = (front - 1, front, front + 1)

    # the saucer: the skin with the doorway left out, a glowing rim band, two dark panel lines, the cockpit and the underside
    # (open where they meet, at z 1.2: capped there they were a disc 0.7 m above the deck, a second floor inside the ship)
    _skin(p, "alien_dark", BELLY_PROFILE, cut_rings=(1,), cut_faces=door, cap_top=False)
    _skin(p, "alien_grey", HULL_PROFILE, cut_rings=(0, 1, 2), cut_faces=door, cap_bottom=False)
    _skin(p, "glow_cyan", [(1.9, 6.28), (2.1, 6.28)], cut_rings=(0,), cut_faces=door, cap=False)
    _skin(p, "metal_dark", [(3.76, 4.95), (3.84, 4.95)], cap=False)
    _skin(p, "glass", [(4.7, 1.2), (5.0, 1.15), (5.5, 0.75), (5.9, 0.0001)], n=16, phase=0.0)
    for k in range(16):                                                                      # radial seams down the dome, so it reads as plates
        a = math.radians(k * 22.5 + 11.25)
        if abs(math.degrees(a) - 270) < 14:
            continue
        props_lib.rod(p, "metal_dark", (5.1 * math.cos(a), 5.1 * math.sin(a), 3.56), (1.5 * math.cos(a), 1.5 * math.sin(a), 4.72), 0.05)   # from inside the ceiling slab, not under it
    for k in range(4):                                                                       # belly thrusters
        a = math.radians(45 + k * 90)
        p.cyl("metal_dark", (2.4 * math.cos(a), 2.4 * math.sin(a), 0.1), 0.55, 0.22, n=8)
        p.cyl("glow_cyan", (2.4 * math.cos(a), 2.4 * math.sin(a), 0.02), 0.38, 0.05, n=8)

    # the inside, shared with the other varieties (ship_hulls.py): the deck, the sill and jambs of the doorway, the ring of wall panels, the ceiling, two seats, the
    # power core and a lit strip. The deck stays inside the dark belly (the belly runs from r 3.4 at z 0.18 to r 6.0 at z 0.5)
    ship_hulls.door_frame(p, "glow_cyan")
    ship_hulls.shell(p, ship_hulls.THEMES["saucer"])

    # outside: the ramp down from the doorway, as the part ShipRamp (hinged at the sill, exported open: ship_hulls.ramp), then swept tail fins, engine nacelles,
    # landing legs (fixed: the crashed ship sits on them), a bent antenna on the dome and a torn patch on the rim
    ship_hulls.ramp(p, "alien_grey", "glow_cyan")
    for sx in (-1, 1):
        p.box("metal_dark", (sx * 1.8, 6.5, 2.7), (0.14, 2.0, 2.0), rot=(0, sx * -14, 0))                 # swept tail fins
        p.cyl("metal_dark", (sx * 3.4, 5.6, 1.7), 0.5, 2.6, n=8, axis="y")                                  # engine nacelles, back of the rim
        p.cyl("glow_cyan", (sx * 3.4, 7.0, 1.7), 0.36, 0.08, n=8, axis="y")
    for k in range(4):                                                                       # landing legs under the rim, with pads
        a = math.radians(45 + k * 90)
        props_lib.rod(p, "metal_dark", (5.4 * math.cos(a), 5.4 * math.sin(a), 1.2), (6.5 * math.cos(a), 6.5 * math.sin(a), 0.08), 0.16)
        p.cyl("metal_dark", (6.5 * math.cos(a), 6.5 * math.sin(a), 0.04), 0.4, 0.08, n=8)
        ship_hulls.foot_anchor(p, k + 1, 6.5 * math.cos(a), 6.5 * math.sin(a), 0.8, 0.8)                  # where the pad stands on the ground
    # No scorch: the ship does not leave a burn mark. Where it stands on the ground it leaves dents under its feet (the contact anchors above: the game builds them,
    # FarmsteadShipMarks), so the mark follows the ship wherever it lands
    a = math.radians(40)
    # the torn plate on the rim: 1.7 m along the rim (tangent), 0.25 m out of it. It was built the other way round, 1.7 m long along the radius, which
    # put its inner end at r 5.15, through the wall panels (inner face 5.17) and into the room
    p.box("metal_dark", (6.25 * math.cos(a), 6.25 * math.sin(a), 2.15), (1.7, 0.25, 1.1), rot=(0, 0, 40 + 90))
    props_lib.rod(p, "metal_dark", (-1.2, 1.2, 4.7), (-2.0, 1.8, 6.6), 0.1)
    p.cyl("glow_cyan", (-2.0, 1.8, 6.7), 0.1, 0.18, n=6)
    return p


VEHICLES = {
    "pickup": (pickup, "Global"), "tractor": (tractor, "Global"), "cruiser": (cruiser, "Global"), "ship": (crashed_ship, "Global"),
}

def run():
    names = globals().get("VEHICLE_LIST") or list(VEHICLES)
    y = 0.0
    for key in names:
        fn, area = VEHICLES[key]
        prop = fn()
        obj, coll = prop.finish()
        print(common.stats(obj))
        common.export_fbx(coll, f"Assets/Art/{area}/Vehicles/{prop.name}.fbx")
        obj.location.y = y
        y += obj.dimensions.y + 3
    props_lib.write_interactions()                                    # the ship's ramp part (ship_hulls.py) goes into art/data/interactions.json
    print("vehicles done", names)


if __name__ == "__main__":
    run()
