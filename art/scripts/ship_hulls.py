"""The crew's ship in several varieties (issue #212): one walkable interior shell, three outsides, each with a ramp and (two of them) landing legs that are named parts.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/ship_hulls.py", run_name="__main__")
Optional global HULL_LIST, e.g. ["egg"] (keys of HULLS). Each exports to Assets/Art/Global/Vehicles/<name>.fbx and its parts to art/data/interactions.json.

What every variety has in common, because the colliders are shared (Assets/Editor/FarmsteadBuilder.BuildLandedShip builds them from FarmsteadLayout's Ship*
numbers and puts whichever outside the mission seed picks over them):
  - the same walkable inside: a 12-sided deck at 0.5 m, a ring of 12 wall panels at r 5.2 (panel 0 is the doorway, 2.9 wide and 2.4 high, in front, -Y), a flat
    ceiling at 3.4, two seats and a power core. Only the colours (THEMES) differ. The console (terminals.py) and the set dressing (ship_props.py) are models of
    their own, placed by FarmsteadShipInterior.cs: those, not the hull, are what the interior TYPES change
  - the doorway: a sill, jambs and a head between the wall ring and the skin, so the way in is a tunnel through the hull, centred on the front
  - a ramp, 2.4 m wide, 3.6 m long, from the sill (y -5.95, 0.44 m up) down to the ground, like the collider

What differs: the outside (a saucer is vehicles.py `crashed_ship`; here an egg (a tall rounded pod on four feet) and a freighter (a box with containers on top, a
bridge and engines)), the colours, the glow and the way the landing gear folds.

THE PARTS (for the arrival and take-off, issue #213; also listed in art/data/interactions.json and docs/art/ship-varieties.md). The model is EXPORTED OPEN, as the
ship stands once it has landed: the ramp down, the legs out. Each part is an object of its own with its origin on its pivot:
    ShipRamp   a hinge about X at the sill's outer edge, (0, -5.95, 0.44). Open = down to the ground (the exported pose). `limit` 85 degrees: closed it stands almost
               upright in front of the doorway, closing it like a drawbridge
    ShipLeg_n  (egg and freighter) a slide along Z: open = out to the ground (the exported pose), `limit` metres up into the hull (negative = the way it moves to open)
The saucer has a ramp part and four fixed legs (the crashed ship sits on them: it settles).

Models face -Y, origin on the ground at the centre, 1 unit = 1 m.
"""

import importlib
import math
import sys
from math import cos, radians, sin
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Blender is shared by several sessions, each running scripts from its own checkout: a `common` another checkout imported first would make this one write
# its FBX into that checkout. Drop modules that came from somewhere else so they are imported from here.
for _n in ("common", "props_lib", "emitters"):
    _m = sys.modules.get(_n)
    if _m is not None and Path(getattr(_m, "__file__", "") or "").resolve().parent != _HERE:
        sys.modules.pop(_n, None)

import bmesh
from mathutils import Vector

import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
rod = props_lib.rod
lathe = props_lib.lathe

# The walkable inside, shared with FarmsteadLayout.cs (Ship* constants) and vehicles.py: change all three
SHIP_INNER_RADIUS = 5.2
SHIP_WALL = 0.5
SHIP_DECK = 0.5
SHIP_CEILING = 3.4
SHIP_PANELS = 12
SHIP_DOOR_HEIGHT = 2.4
SHIP_RAMP_RUN = 3.6
SHIP_RAMP_WIDTH = 2.4
RAMP_PIVOT = (0.0, -5.95, SHIP_DECK - 0.06)                 # the ramp's top edge: the hinge
RAMP_OPEN_DEGREES = 85.0

HULL_N = 40                                                  # sides of a round hull skin: 9 degrees each, so three of them are the width of the doorway
HULL_PHASE = 4.5                                             # turned so a face is centred on the front (-Y)

THEMES = {
    # wall panels, the dark band round them, the glow colour, the seats' colour, the colour of the power core's caps
    "saucer": dict(wall="alien_grey", band="alien_dark", glow="glow_cyan", seat="alien_dark", cap="alien_dark", floor="alien_grey"),
    "egg": dict(wall="alien_gold", band="alien_violet", glow="glow_green", seat="alien_violet", cap="alien_dark", floor="alien_dark"),
    "freighter": dict(wall="concrete", band="metal_dark", glow="glow_amber", seat="rust", cap="metal_dark", floor="metal_galv"),
}


# ===== Pieces shared by every variety ============================================================================================

def front_faces():
    """The three faces of a HULL_N-sided skin (turned by HULL_PHASE) that are centred on the front (270 degrees): the doorway is cut out of them."""
    front = int(round((270 - HULL_PHASE) / (360 / HULL_N) - 0.5))
    return (front - 1, front, front + 1)


def skin(p, colour, profile, n=HULL_N, phase=HULL_PHASE, cut_rings=(), cut_faces=(), cap=True, cap_bottom=None, cap_top=None):
    """A solid of revolution skinned by hand so a doorway can be left out of it: faces k in cut_faces between the rings in cut_rings (the quad between ring i
    and ring i + 1 is i) are not made. cap closes both ends; cap_bottom and cap_top override it for one end."""
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


def profile_r(profile, z):
    """The radius of a (z, r) profile at height z (linear between its points)."""
    for (z0, r0), (z1, r1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0) if z1 > z0 else r0
    return profile[-1][1]


def door_side():
    """The width of a wall panel (and of the doorway), a little over the chord of its 30 degrees."""
    return 2 * SHIP_INNER_RADIUS * math.tan(math.radians(180 / SHIP_PANELS)) + 0.06


def shell(p, th, deck_bottom=0.18, deck_radius_bottom=3.3):
    """The walkable inside every variety has: the deck, the doorway's sill, jambs and head, the ring of 12 wall panels with its dark band, the ceiling with its
    lit rim, two seats, the power core and a lit strip down the deck. th is a THEMES entry. Nothing here is a collider: the colliders are FarmsteadBuilder's."""
    r_in, deck, ceil = SHIP_INNER_RADIUS, SHIP_DECK, SHIP_CEILING
    side = door_side()
    ph = 180 / SHIP_PANELS

    # the deck, with a dark trim along its edge that follows its chamfer
    lathe(p, th["floor"], [(deck_bottom, deck_radius_bottom), (deck, 5.9)], n=12, phase=ph)
    lathe(p, "metal_dark", [(deck - 0.04, 5.60), (deck - 0.005, 5.915)], n=12, cap=False, phase=ph)

    # a sill across the threshold, as wide as the doorway (the deck's front flat is at 5.70 m, the ramp starts at 5.95: without it a slot shows the ground there; its
    # top is 1 mm under the deck's so the two never fight). Jambs and a head close the sides and the top of the doorway between the wall ring and the skin
    p.box(th["floor"], (0, -5.9, deck - 0.061), (2.9, 0.5, 0.12))
    for sx in (-1, 1):
        p.box(th["wall"], (sx * (side / 2 - 0.05), -5.625, (deck + 3.0) / 2), (0.1, 0.85, 3.0 - deck))
    p.box(th["wall"], (0, -5.625, 2.95), (side, 0.85, 0.1))

    # the interior skin: a thin ring of panels at the inner radius, a dark band round it
    for k in range(SHIP_PANELS):
        a = math.radians(-90 + k * 360 / SHIP_PANELS)
        rot = (0, 0, math.degrees(a) + 90)
        if k == 0:
            h = ceil - (deck + SHIP_DOOR_HEIGHT)
            p.box(th["wall"], (r_in * math.cos(a), r_in * math.sin(a), deck + SHIP_DOOR_HEIGHT + h / 2), (side, 0.06, h), rot=rot)
            continue
        p.box(th["wall"], (r_in * math.cos(a), r_in * math.sin(a), (deck + ceil) / 2), (side, 0.06, ceil - deck), rot=rot)
        p.box(th["band"], ((r_in - 0.05) * math.cos(a), (r_in - 0.05) * math.sin(a), deck + 1.1), (side - 0.4, 0.04, 0.5), rot=rot)

    # the ceiling: a flat disc, a lit rim and a light
    lathe(p, th["wall"], [(ceil, r_in + 0.05), (ceil + 0.15, r_in + 0.05)], n=12, phase=ph)
    lathe(p, th["glow"], [(ceil - 0.15, r_in), (ceil + 0.0, r_in)], n=12, cap=False, phase=ph)
    p.cyl(th["glow"], (0, 0, ceil - 0.02), 0.5, 0.04, n=6)

    # two seats and a glowing power core (the console along the back wall is a model of its own: terminals.py)
    for sx in (-1, 1):
        p.box(th["seat"], (sx * 1.0, 2.6, deck + 0.3), (0.7, 0.7, 0.6))
        p.box(th["seat"], (sx * 1.0, 2.25, deck + 0.9), (0.7, 0.1, 0.8))
    p.cyl(th["glow"], (-3.6, 1.8, deck + 1.1), 0.3, 2.2, n=6)
    p.cyl(th["cap"], (-3.6, 1.8, deck + 0.1), 0.45, 0.2, n=6)
    p.cyl(th["cap"], (-3.6, 1.8, deck + 2.15), 0.45, 0.2, n=6)
    p.box(th["glow"], (0, 0, deck), (0.05, 6.0, 0.02))                                           # a lit strip inlaid in the deck: 1 cm proud of it


def door_frame(p, colour, y=-6.1):
    """Two glowing posts and a lintel round the doorway, at y (just outside the wall ring's jambs)."""
    side = door_side()
    for sx in (-1, 1):
        p.box(colour, (sx * (side / 2 - 0.05), y, SHIP_DECK + SHIP_DOOR_HEIGHT / 2), (0.1, 0.1, SHIP_DOOR_HEIGHT))
    p.box(colour, (0, y, SHIP_DECK + SHIP_DOOR_HEIGHT + 0.04), (side, 0.1, 0.1))


def _hinge_x(point, pivot, degrees):
    """A point turned about the X axis through pivot by degrees (right-handed: +y turns towards +z)."""
    y, z = point[1] - pivot[1], point[2] - pivot[2]
    c, s = cos(radians(degrees)), sin(radians(degrees))
    return (point[0], pivot[1] + y * c - z * s, pivot[2] + y * s + z * c)


def ramp(p, colour, rail_colour, edge_colour=None):
    """The ramp as the part `ShipRamp`: a slab from the sill (RAMP_PIVOT) down to the ground 3.6 m out, with a lit rail along each edge, and for the freighter a
    stripe of `edge_colour` across the foot. Built CLOSED (turned up about the hinge by RAMP_OPEN_DEGREES) and exported open (`rest` = `limit`): turning it by +limit
    about +X lays it down, which is the pose in the model and the one the collider has."""
    top = RAMP_PIVOT
    bottom = (0.0, -5.95 - SHIP_RAMP_RUN, 0.0)

    def closed(pt):
        return _hinge_x(pt, top, -RAMP_OPEN_DEGREES)

    with p.part("ShipRamp", pivot=top, kind="hinge", axis="x", limit=RAMP_OPEN_DEGREES, rest=RAMP_OPEN_DEGREES):
        rod(p, colour, closed(top), closed(bottom), SHIP_RAMP_WIDTH, 0.12)
        for sx in (-1, 1):
            rod(p, rail_colour, closed((sx * 1.15, -5.95, SHIP_DECK + 0.02)), closed((sx * 1.15, -5.95 - SHIP_RAMP_RUN, 0.06)), 0.06, 0.05)
        if edge_colour:
            for t in (0.82, 0.9):                                                              # two cross stripes near the foot
                a = (0.0, top[1] + (bottom[1] - top[1]) * t, top[2] + (bottom[2] - top[2]) * t + 0.062)
                rod(p, edge_colour, closed((-1.0, a[1], a[2])), closed((1.0, a[1], a[2])), 0.1, 0.012)


def foot_anchor(p, index, x, y, width, depth):
    """The contact anchor of a foot: an empty `Slot_ShipFoot_<index>` on the ground (z 0) under the middle of the pad, `width` x `depth` metres (the pad's footprint),
    exported with the model in its landed pose and listed in art/data/interactions.json under `slots`. The game builds the dent in the ground under it
    (Assets/Editor/FarmsteadShipMarks.cs), so the mark follows the ship wherever it lands, and a sequence that places the ship reads these to place its own. A variety
    with no feet that settles on its hull has one anchor instead, `Slot_ShipBelly` (see `belly_anchor`). The names are part of the model's interface: keep them."""
    p.slot(f"ShipFoot_{index}", (x, y, 0.0), size=(width, depth, 0.0))


def belly_anchor(p, radius):
    """The contact anchor of a variety that has no feet and settles on its hull: `Slot_ShipBelly`, on the ground under the middle of the hull, `radius` m of it touching."""
    p.slot("ShipBelly", (0.0, 0.0, 0.0), size=(2 * radius, 2 * radius, 0.0))


def leg(p, index, x, y, strut_colour, pad_colour, height, travel, strut=(0.3, 0.3), pad=(0.9, 0.9)):
    """A landing leg as the part `ShipLeg_<index>`: a vertical strut with a foot pad, out (on the ground, `height` tall) in the exported pose and `travel` metres
    higher, up into the hull, when it is retracted. A slide along Z (limit and rest are -travel: the way it moves to open)."""
    with p.part(f"ShipLeg_{index}", pivot=(x, y, 0.0), kind="slide", axis="z", limit=-travel, rest=-travel):
        z0 = travel                                                                            # built retracted: everything `travel` above where it ends up
        p.box(strut_colour, (x, y, z0 + height / 2), (strut[0], strut[1], height))
        p.box(pad_colour, (x, y, z0 + 0.06), (pad[0], pad[1], 0.12))
    foot_anchor(p, index, x, y, pad[0], pad[1])                                                # on the body, not the part: where the pad stands when the leg is out


# ===== The egg ===================================================================================================================

EGG_BELLY = [(0.30, 5.40), (0.50, 6.00), (1.40, 6.05)]
EGG_HULL = [(1.40, 6.05), (2.60, 6.20), (3.00, 6.22), (4.00, 6.35), (5.20, 6.25), (6.40, 5.70), (7.60, 4.80), (8.80, 3.60), (9.80, 2.30), (10.60, 1.10), (11.10, 0.0001)]


def egg(name="GV_ShipEgg_01"):
    """An egg: a tall rounded pod, gold plating over a dark skirt, a violet band and a ring of windows round its upper half, a spire, three fins and four feet that
    fold up into its skirt. 12.7 m across, 11.1 m tall (13 with the spire). The doorway is cut out of the skirt and the plating; inside is the shared shell (gold walls, violet
    trim, green light)."""
    th = THEMES["egg"]
    p = Prop(name)
    door = front_faces()
    skin(p, "alien_dark", EGG_BELLY, cut_rings=(0, 1), cut_faces=door, cap_top=False)
    skin(p, "alien_gold", EGG_HULL, cut_rings=(0, 1), cut_faces=door, cap_bottom=False)
    skin(p, "alien_violet", [(2.2, 6.28), (2.45, 6.28)], cut_rings=(0,), cut_faces=door, cap=False)             # a violet band round the waist
    skin(p, "glow_green", [(6.5, profile_r(EGG_HULL, 6.5) + 0.03), (6.62, profile_r(EGG_HULL, 6.62) + 0.03)], cap=False)             # a thin lit ring over the windows, a little proud of the skin
    r_win = profile_r(EGG_HULL, 5.9) * cos(radians(HULL_PHASE)) + 0.02
    for k in range(12):                                                                                       # windows: dark panes round the upper half
        a = math.radians(k * 30 + 15)
        p.box("glass", (r_win * math.cos(a), r_win * math.sin(a), 5.9), (0.9, 0.08, 0.7), rot=(0, 0, math.degrees(a) + 90))
    rod(p, "alien_violet", (0, 0, 10.9), (0, 0, 12.6), 0.14)                                                  # the spire
    p.cyl("glow_green", (0, 0, 12.65), 0.16, 0.2, n=6)
    for k in range(3):                                                                                        # three fins, swept, on the back half of the skirt
        a = math.radians(90 + (k - 1) * 70)
        p.box("alien_violet", (7.3 * math.cos(a), 7.3 * math.sin(a), 2.6), (0.16, 2.2, 3.2), rot=(0, 0, math.degrees(a) - 90))      # 2.2 m along the radius, from the skin (r 6.2) outwards: not through the wall ring
    door_frame(p, "glow_green")
    shell(p, th)
    ramp(p, "alien_gold", "glow_green")
    for index, (x, y) in enumerate(((4.5, 4.5), (-4.5, 4.5), (-4.5, -4.5), (4.5, -4.5))):                    # four feet against the skirt (r 6.4), the front two beside the ramp
        leg(p, index + 1, x, y, "metal_dark", "alien_violet", height=1.5, travel=1.2, strut=(0.4, 0.4), pad=(1.0, 1.0))
    return p


# ===== The freighter =============================================================================================================

FREIGHTER_X = 6.6            # half the width of the box
FREIGHTER_FRONT = -6.2       # the front wall's outer face
FREIGHTER_BACK = 8.6         # the back wall's outer face
FREIGHTER_ROOF = 4.6         # the roof slab's underside


def freighter(name="GV_ShipFreighter_01"):
    """A freighter: a boxy hull, 13.2 m wide and 14.8 long, with a bridge block at the front, three cargo containers on the roof, a big engine block with three
    lit nozzles at the back, hazard stripes along the skirt and four landing legs that fold up beside the hull. The doorway is a cargo hatch cut in the front wall
    and the ramp a cargo ramp; inside is the shared shell (concrete walls, an amber light). The box is hollow round the shell: you only see the walls of the shell."""
    th = THEMES["freighter"]
    p = Prop(name)
    X, f, b, roof = FREIGHTER_X, FREIGHTER_FRONT, FREIGHTER_BACK, FREIGHTER_ROOF
    side = door_side()
    hull, trim = "metal_galv", "metal_dark"
    # the box: the floor plate, two side walls, the back wall, the front wall in three pieces round the hatch, the roof
    p.box(trim, (0, (f + b) / 2, 0.27), (2 * X, b - f, 0.06))
    for sx in (-1, 1):
        p.box(hull, (sx * (X - 0.15), (f + b) / 2, (0.3 + roof) / 2), (0.3, b - f, roof - 0.3))
    p.box(hull, (0, b - 0.15, (0.3 + roof) / 2), (2 * X, 0.3, roof - 0.3))
    half = side / 2 - 0.05
    for sx in (-1, 1):                                                                           # the front wall on either side of the hatch
        w = X - half
        p.box(hull, (sx * (half + w / 2), f + 0.15, (0.3 + roof) / 2), (w, 0.3, roof - 0.3))
    p.box(hull, (0, f + 0.15, (3.0 + roof) / 2), (2 * half, 0.3, roof - 3.0))                    # over the hatch
    p.box(hull, (0, (f + b) / 2, roof + 0.1), (2 * X, b - f, 0.2))                               # the roof
    for sx in (-1, 1):                                                                           # the hatch's sides, from the front wall to the wall ring
        p.box(trim, (sx * (half + 0.02), (f - 5.2) / 2, (0.3 + 3.0) / 2), (0.1, abs(f + 5.2), 3.0 - 0.3))
    # hazard stripes along the skirt: yellow bars on the side walls and across the front
    for sx in (-1, 1):
        for k in range(9):
            p.box("paint_yellow", (sx * (X + 0.005), -5.4 + k * 1.6, 0.75), (0.02, 0.7, 0.4))
    for k in range(4):
        for sx in (-1, 1):
            p.box("paint_yellow", (sx * (2.4 + k * 1.0), f - 0.005, 0.75), (0.7, 0.02, 0.4))
    p.box("glow_amber", (0, f - 0.01, 3.35), (2 * half, 0.03, 0.05))                              # a lit lintel over the hatch
    door_frame(p, "glow_amber", y=f - 0.05)
    # the roof: three containers in two colours, a bridge block with windows at the front, antennas
    for k, (cx, cy, colour) in enumerate(((-3.4, 2.4, "truck_blue"), (0.0, 2.4, "cloth_red"), (3.4, 2.4, "paint_yellow"), (-3.4, 6.2, "rust"), (3.4, 6.2, "truck_blue"))):
        p.box(colour, (cx, cy, roof + 0.2 + 1.3), (3.0, 3.4, 2.6))
        for r in (-1, 1):
            p.box(trim, (cx + r * 0.9, cy, roof + 0.2 + 1.3), (0.06, 3.42, 2.62))                 # ribs
    p.box(hull, (0, f + 2.4, roof + 0.2 + 1.0), (5.6, 4.4, 2.0))                                 # the bridge block
    p.box("glass", (0, f + 0.22, roof + 0.2 + 1.35), (5.0, 0.06, 0.7))
    p.box("glow_amber", (0, f + 0.2, roof + 0.2 + 0.7), (5.0, 0.04, 0.05))
    rod(p, trim, (2.4, f + 2.8, roof + 1.2), (2.4, f + 2.8, roof + 3.4), 0.1)
    p.cyl("glow_amber", (2.4, f + 2.8, roof + 3.45), 0.1, 0.12, n=6)
    # the engine block at the back with three lit nozzles
    p.box(trim, (0, b + 1.0, (0.3 + roof) / 2 + 0.2), (2 * X - 1.0, 2.0, roof - 0.5))
    for sx in (-1, 0, 1):
        p.cyl("metal_dark", (sx * 3.6, b + 2.2, 2.4), 1.1, 0.8, n=8, axis="y")
        p.cyl("glow_amber", (sx * 3.6, b + 2.64, 2.4), 0.8, 0.08, n=8, axis="y")
    shell(p, th)
    ramp(p, "metal_galv", "glow_amber", edge_colour="paint_yellow")
    for index, (x, y) in enumerate(((7.0, -4.2), (-7.0, -4.2), (7.0, 6.0), (-7.0, 6.0))):          # four legs, outside the side walls
        leg(p, index + 1, x, y, "metal_dark", "paint_yellow", height=1.9, travel=1.5, strut=(0.4, 0.4), pad=(1.1, 1.1))
    return p


# ===== Build and export ==========================================================================================================

HULLS = {"egg": (egg, "Global/Vehicles"), "freighter": (freighter, "Global/Vehicles")}


def run():
    names = globals().get("HULL_LIST") or list(HULLS)
    x = 40.0
    out = {}
    for key in names:
        fn, area = HULLS[key]
        prop = fn()
        obj, coll = prop.finish()
        print(common.stats(obj))
        common.export_fbx(coll, f"Assets/Art/{area}/{prop.name}.fbx")
        obj.location.x = x
        x += obj.dimensions.x + 8
        out[key] = obj
    props_lib.write_interactions()
    print("hulls done", names)
    return out


if __name__ == "__main__":
    run()
    for _n in ("common", "props_lib", "emitters"):          # leave the next session's import to find its own copy
        sys.modules.pop(_n, None)
