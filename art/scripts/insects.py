"""Insects and a spider for the wild (ladybug, bee, butterflies, dragonfly, beetle, ant, grasshopper, firefly, moth, spider, caterpillar, and the wider cast of
issue #80: stink bug, housefly, mosquito, wasp, cockroach, cricket, praying mantis, earwig, aphid, weevil, stag beetle, scarab, scorpion, wolf spider,
orb-weaver and jumping spider). Flat faceted
models. The FBX is a resting pose (not rigged). For the web viewer, insect_anim.py rigs each one from the moving parts marked here (wings, legs,
antennae, caterpillar segments: `moving()`), and gives it Idle plus Fly, Walk, Hop or the ladybug's Open clips; see build_rigged().

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/insects.py", run_name="__main__")
Optional global INSECT_LIST (names). Exports Assets/Art/Global/Animals/Insects/GN_<Name>_01.fbx.

Real size (a ladybug is 8 mm, a dragonfly 6.5 cm long): the parts are modelled in millimetres and scaled by `new()` when the model is finished. The head
points to -Y and the feet stand on z = 0, centred on the body. Wings are thin flat prisms (an outline colour under a smaller fill colour); the firefly's
tail uses the palette's glow_amber, which the asset browser lights up.
"""

import importlib
import math
import sys
from contextlib import nullcontext
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import insect_legs
import props_lib
for _m in (common, insect_legs, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
rod = props_lib.rod

CRITTERS = {}
RIGGED = False                  # True while insect_anim.py builds the rigged models: moving() then makes separate pieces
MM = 0.001


def critter(group, name):
    def deco(fn):
        CRITTERS[name] = (fn, group)
        return fn
    return deco


def _to_metres(obj):
    for v in obj.data.vertices:
        v.co *= MM


def new(name):
    """A Prop whose parts are given in millimetres (scaled to metres when it is finished)."""
    p = Prop(name)
    p.post = _to_metres
    p.bones = {}                    # role -> pivot (mm): the pieces insect_anim.py turns into bones
    p.motion = None                 # which clips insect_anim.py gives it
    return p


def moving(p, role, pivot):
    """Everything added inside becomes a piece that turns about `pivot` (mm) in the rigged build; in the FBX it is still part of the one mesh."""
    if not RIGGED:
        return nullcontext()
    p.bones[role] = tuple(pivot)
    return p.part(role, pivot=pivot)


def _profile(c, r, n, rings):
    cx, cy, cz = c
    rx, ry, rz = r
    out = []
    for k in range(rings + 2):
        phi = math.pi * k / (rings + 1)
        s = math.sin(phi)
        out.append(common.ring_y(cy - ry * math.cos(phi), cx, cz, max(rx * s, 0.001), max(rz * s, 0.001), n=n, p=2.0))
    return out


def blob(p, colour, c, r, n=6, rings=2):
    """An ellipsoid with its long axis along Y: centre c, radii r = (x, y, z)."""
    p.loft_rings(colour, _profile(c, r, n, rings))


def banded(p, colours, c, r, n=6, rings=4):
    """The same ellipsoid cut into stripes along Y, coloured in turn from `colours` (a bee's abdomen)."""
    rg = _profile(c, r, n, rings)
    for i in range(len(rg) - 1):
        p.loft_rings(colours[i % len(colours)], rg[i:i + 2], cap=False)


def ball_at(p, colour, c, r, n=5):
    props_lib.ball(p, colour, c, r, n=n, rings=2)


def legs(p, colour, x, ys, z_hip, out, knee_up, w, dy=0.0, move=True, shins=False):
    """Three-jointed legs on both sides: hip under the body at (±x, y, z_hip), knee out and up, foot on the ground. Each is a moving piece
    Leg_<L|R><n> (n counts from the head) pivoting at its hip, unless move is False (legs tucked up in flight). With shins the thigh is Leg_<L|R><n>
    and the shin its own piece Shin_<L|R><n> pivoting at the knee, so a clip can swing the thigh and let the shin hang."""
    for s in (-1, 1):
        for i, y in enumerate(ys):
            hip = (s * x, y, z_hip)
            knee = (s * (x + out * 0.7), y + dy * 0.5, z_hip + knee_up)
            foot = (s * (x + out), y + dy, 0.0)
            side = 'L' if s > 0 else 'R'
            with _maybe(p, move, f"Leg_{side}{i}", hip):
                rod(p, colour, hip, knee, w)
                if not shins:
                    rod(p, colour, knee, foot, w)
            if shins:
                with _maybe(p, move, f"Shin_{side}{i}", knee):
                    rod(p, colour, knee, foot, w)


def _maybe(p, move, role, pivot):
    """moving() when move is true, else a context that adds to the body."""
    return moving(p, role, pivot) if move else nullcontext()


def antennae(p, colour, base, tip, w, spread=1.0):
    for s in (-1, 1):
        b = (s * base[0], base[1], base[2])
        with moving(p, f"Antenna_{'L' if s > 0 else 'R'}", b):
            rod(p, colour, b, (s * tip[0] * spread, tip[1], tip[2]), w)


def ellipse_pts(cx, cy, a, b, n=8):
    return [(cx + a * math.cos(math.tau * k / n), cy + b * math.sin(math.tau * k / n)) for k in range(n)]


def wing(p, edge, fill, pts, z0, tilt=25.0, side=1, thick=0.5, inset=0.8):
    """A wing: the 2D outline `pts` (x outwards from the body, y along it) as a thin prism, raised `tilt` degrees about the body line, with a
    smaller fill-colour prism on top (so the outline shows as a border). side is 1 for the right wing, -1 for the left."""
    t = math.radians(tilt)
    d = Vector((side * math.cos(t), 0, math.sin(t)))
    n = Vector((-side * math.sin(t), 0, math.cos(t)))

    def ring(poly, h):
        return [Vector((0, y, z0)) + d * x + n * h for x, y in poly]
    p.loft_rings(edge, [ring(pts, 0), ring(pts, thick)])
    if fill:
        cx = sum(x for x, _ in pts) / len(pts)
        cy = sum(y for _, y in pts) / len(pts)
        small = [(cx + (x - cx) * inset, cy + (y - cy) * inset) for x, y in pts]
        p.loft_rings(fill, [ring(small, thick), ring(small, thick * 1.8)])


def flap(p, role, side, pivot):
    """The wings added inside are one moving piece (Wing_L / Wing_R, or `role` + _L / _R) that flaps about the lengthwise line through `pivot`. A model with two wing pieces a side (WingF, WingH) must give both the same pivot x and z, or the two turn about different lines and their planes cross during the beat."""
    return moving(p, f"{role}_{'L' if side > 0 else 'R'}", pivot)


# ===== Insects ===================================================================================================
def thorax_legs(p, colour, spec):
    """The three legs a side of a beetle (insect_legs.py says where): each hip is on the thorax underside, thigh out, shin down to the ground. Leg_<L|R><n>
    (n counts from the head) pivots at its hip."""
    for s in (-1, 1):
        for i in range(3):
            hip, knee, foot = insect_legs.leg_joints(spec, s, i)
            with moving(p, f"Leg_{'L' if s > 0 else 'R'}{i}", hip):
                rod(p, colour, hip, knee, spec["w"])
                rod(p, colour, knee, foot, spec["w"])


def dome_rings(shape, side=0, rings=4, arcs=6):
    """Cross-sections along Y of a dome (insect_legs.dome): a half-ellipse on the flat base. side 0 is the whole dome, 1 or -1 only the half on that side of x = 0."""
    (cx, cy, _), (rx, ry, rz) = shape["c"], shape["r"]
    base = shape["base"]
    out = []
    for k in range(rings + 2):
        phi = math.pi * k / (rings + 1)
        s = math.sin(phi)
        hw, hh = max(rx * s, 0.001), max(rz * s, 0.001)
        y = cy - ry * math.cos(phi)
        if side == 0:
            pts = [(cx + hw * math.cos(math.pi * j / arcs), base + hh * math.sin(math.pi * j / arcs)) for j in range(arcs + 1)]
        else:
            m = arcs // 2
            pts = [(cx + side * hw * math.cos(0.5 * math.pi * j / m), base + hh * math.sin(0.5 * math.pi * j / m)) for j in range(m + 1)]
            pts.append((cx + side * 0.001, base))
        out.append([Vector((x, y, z)) for x, z in pts])
    return out


def on_dome(p, colour, shape, x, y, r, thick=0.3, n=6, lift=0.0):
    """A flat disc of radius r lying on the dome's surface above (x, y), tilted to follow it (a spot, a patch)."""
    z = insect_legs.surface_z(shape, x, y)
    nx, ny, nz = insect_legs.surface_normal(shape, x, y, z)
    e = Vector((0, 0, 1)).rotation_difference(Vector((nx, ny, nz))).to_euler("XYZ")
    c = (x + nx * (lift - thick * 0.35), y + ny * (lift - thick * 0.35), z + nz * (lift - thick * 0.35))
    p.cyl(colour, c, r, thick, n=n, rot=tuple(math.degrees(a) for a in (e.x, e.y, e.z)))


# A seven-spot ladybug: on each wing cover three spots, and one more shared at the suture behind the pronotum (drawn as a half on each side).
LADYBUG_SPOTS = ((2.25, -0.5, 0.7), (1.0, 1.1, 0.75), (2.0, 2.9, 0.6))
SCUTELLAR_HALF = (0.36, -1.85, 0.34)


@critter("beetles", "Ladybug")
def ladybug():
    """A seven-spot ladybug (Coccinella septempunctata, about 8 mm): a red dome with a flat black underside, a black head with white face patches and a
    black pronotum with a white patch at each front corner, short legs under the thorax and short clubbed antennae. The wing covers are two halves
    (Elytron_L/R in the rigged model) that lift to show the hindwings (WingH_L/R) folded under them."""
    p = new("GN_Ladybug_01")
    p.motion = "ladybug"
    B = insect_legs.LADYBUG
    belly, head, pron, ely = B["belly"], B["head"], B["pronotum"], B["elytra"]
    blob(p, "black", belly["c"], belly["r"], n=8, rings=2)
    blob(p, "black", head["c"], head["r"], n=6, rings=2)
    p.loft_rings("black", dome_rings(pron, rings=3, arcs=6))
    for s in (-1, 1):
        on_dome(p, "paint_white", pron, s * 1.45, -3.95, 0.6, thick=0.35)
        ball_at(p, "paint_white", (s * 0.85, -5.45, 2.2), 0.32, n=4)
        pivot = (s * 0.3, -2.6, 4.0)
        side = "L" if s > 0 else "R"
        with moving(p, f"WingH_{side}", (s * 0.7, -1.0, 2.5)):                 # the flying wing, folded away under the cover
            wing(p, "clear_glass", None, ellipse_pts(0.7 + 0.8, 1.0, 0.8, 2.3, n=8), 2.45, tilt=0, side=s, thick=0.12)
        with moving(p, f"Elytron_{side}", pivot):
            p.loft_rings("cloth_red", dome_rings(ely, side=s, rings=4, arcs=6))
            for x, y, r in LADYBUG_SPOTS:
                on_dome(p, "black", ely, s * x, y, r)
            on_dome(p, "black", ely, s * SCUTELLAR_HALF[0], SCUTELLAR_HALF[1], SCUTELLAR_HALF[2], n=6)
            ys = (-2.8, -1.0, 1.0, 3.0, 4.6)                                      # the dark seam between the covers
            seam = [(s * 0.14, y, (insect_legs.surface_z(ely, 0.14, y) or ely["base"]) + 0.02) for y in ys]
            for a, b in zip(seam, seam[1:]):
                rod(p, "black", a, b, 0.22)
        with moving(p, f"Antenna_{side}", (s * 0.5, -5.7, 1.9)):                # short, ending in a club
            rod(p, "black", (s * 0.5, -5.7, 1.9), (s * 1.0, -6.6, 2.3), 0.2)
            ball_at(p, "black", (s * 1.15, -6.9, 2.3), 0.4, n=5)
    thorax_legs(p, "black", B)
    return p


@critter("beetles", "Beetle")
def beetle():
    p = new("GN_Beetle_01")
    p.motion = "walk"
    B = insect_legs.BEETLE
    blob(p, "beetle_green", B["elytra"]["c"], B["elytra"]["r"], n=8, rings=3)
    blob(p, "leaf_dark", B["pronotum"]["c"], B["pronotum"]["r"], n=8)
    blob(p, "black", B["head"]["c"], B["head"]["r"], n=6)
    for s in (-1, 1):
        rod(p, "black", (s * 1.2, -13.0, 5.3), (s * 1.0, -16.5, 5.3), 1.0)
    thorax_legs(p, "black", B)
    antennae(p, "black", (1.5, -13.0, 6.5), (3.0, -17.0, 8.5), 0.5)
    return p


@critter("beetles", "Firefly")
def firefly():
    p = new("GN_Firefly_01")
    p.motion = "walk"
    B = insect_legs.FIREFLY
    blob(p, "dark_brown", B["elytra"]["c"], B["elytra"]["r"], n=6)
    blob(p, "glow_amber", B["tail"]["c"], B["tail"]["r"], n=6)
    blob(p, "cloth_red", B["pronotum"]["c"], B["pronotum"]["r"], n=6)
    blob(p, "black", B["head"]["c"], B["head"]["r"], n=6, rings=1)
    thorax_legs(p, "black", B)
    antennae(p, "black", (0.4, -5.0, 2.8), (1.2, -7.5, 4.0), 0.25)
    return p


@critter("flyers", "Honeybee")
def honeybee():
    p = new("GN_Honeybee_01")
    p.motion = "bee"
    banded(p, ("golden", "black"), (0, 3.0, 4.2), (2.8, 4.8, 2.6), n=6, rings=5)
    blob(p, "golden", (0, -2.2, 4.4), (2.7, 2.4, 2.5), n=6)
    blob(p, "black", (0, -5.2, 4.0), (1.8, 1.3, 1.7), n=6, rings=1)
    for s in (-1, 1):
        with flap(p, "WingF", s, (s * 0.41, -1.5, 5.95)):                                      # each wing is rooted on the thorax's side and turns about its own root
            wing(p, "clear_glass", None, ellipse_pts(0.5 + 4.5, -1.5, 4.5, 2.0), 5.91, tilt=35, side=s, thick=0.2)
        with flap(p, "WingH", s, (s * 0.41, -1.0, 5.95)):
            wing(p, "clear_glass", None, ellipse_pts(0.5 + 3.2, -1.0, 3.2, 1.5), 5.41, tilt=35, side=s, thick=0.2)
    legs(p, "black", 1.6, (-3.0, -1.6, -0.2), 3.0, 2.0, 0.8, 0.4, dy=0.8, move=False)
    antennae(p, "black", (0.6, -6.2, 4.6), (1.6, -8.5, 6.0), 0.3)
    return p


def _butterfly(name, fill, tilt=28.0):
    p = new(name)
    p.motion = "butterfly"
    blob(p, "black", (0, 0, 3.0), (1.1, 10, 1.1), n=6, rings=3)
    blob(p, "black", (0, -6, 3.2), (2.0, 3.0, 2.0), n=6)
    blob(p, "black", (0, -10.5, 3.2), (1.6, 1.4, 1.6), n=6, rings=1)
    fore = [(1.5, -6), (12, -22), (30, -27), (44, -21), (46, -12), (38, -2), (22, 3), (4, 2)]
    hind = [(1.5, 0), (20, 2), (32, 10), (30, 22), (18, 26), (8, 18), (2, 8)]
    for s in (-1, 1):
        with flap(p, "Wing", s, (s * 1.0, -4.0, 2.6)):
            wing(p, "black", fill, hind, 2.0, tilt=tilt, side=s, thick=0.6)
            wing(p, "black", fill, fore, 3.2, tilt=tilt, side=s, thick=0.6)
        with moving(p, f"Antenna_{'L' if s > 0 else 'R'}", (s * 0.5, -11.0, 3.5)):
            rod(p, "black", (s * 0.5, -11.0, 3.5), (s * 5.0, -24.0, 9.0), 0.4)
            ball_at(p, "black", (s * 5.0, -24.0, 9.0), 0.8, n=4)
    for s in (-1, 1):
        for y in (-6.0, -3.0):
            rod(p, "black", (s * 0.8, y, 2.2), (s * 2.2, y - 1.0, 0.0), 0.5)
    return p


@critter("flyers", "Butterfly_Monarch")
def butterfly_monarch():
    return _butterfly("GN_Butterfly_Monarch_01", "food_orange")


@critter("flyers", "Butterfly_Blue")
def butterfly_blue():
    return _butterfly("GN_Butterfly_Blue_01", "wing_blue")


@critter("flyers", "Moth")
def moth():
    p = new("GN_Moth_01")
    p.motion = "moth"
    blob(p, "wood_grey", (0, 0, 3.0), (2.4, 7.0, 2.4), n=6, rings=3)
    blob(p, "wood_grey", (0, -8.0, 3.0), (2.0, 1.5, 2.0), n=6, rings=1)
    fore = [(1.5, -6), (14, -9), (24, -3), (22, 5), (10, 10), (2, 6)]
    hind = [(1.5, 2), (14, 6), (14, 14), (2, 12)]
    for s in (-1, 1):
        with flap(p, "Wing", s, (s * 1.0, 0.0, 2.7)):
            wing(p, "dead_wood", "wood_grey", hind, 2.2, tilt=6, side=s, thick=0.4)
            wing(p, "dead_wood", "linen", fore, 3.2, tilt=6, side=s, thick=0.4, inset=0.75)
        with moving(p, f"Antenna_{'L' if s > 0 else 'R'}", (s * 0.8, -9.0, 3.4)):
            rod(p, "wood_grey", (s * 0.8, -9.0, 3.4), (s * 4.5, -14.0, 5.0), 0.5)
    legs(p, "wood_grey", 1.6, (-5.0, -2.0), 1.8, 2.0, 0.8, 0.5, move=False)
    return p


@critter("flyers", "Dragonfly")
def dragonfly():
    p = new("GN_Dragonfly_01")
    p.motion = "dragonfly"
    banded(p, ("trailer_teal", "black"), (0, 22, 6.0), (1.4, 25, 1.4), n=6, rings=7)
    blob(p, "tile_green", (0, -6, 6.5), (3.5, 5, 3.5), n=8)
    blob(p, "black", (0, -12, 6.8), (3.0, 2.2, 2.8), n=6, rings=1)
    for s in (-1, 1):
        ball_at(p, "tile_blue", (s * 2.6, -12.5, 7.8), 2.3, n=6)
        with flap(p, "WingF", s, (s * 1.5, -6.0, 9.4)):
            wing(p, "clear_glass", None, ellipse_pts(11, -6, 11, 2.8, n=10), 9.6, tilt=6, side=s, thick=0.3)
        with flap(p, "WingH", s, (s * 1.5, -1.0, 8.8)):
            wing(p, "clear_glass", None, ellipse_pts(11, -1, 11, 3.5, n=10), 9.0, tilt=6, side=s, thick=0.3)
    legs(p, "black", 1.5, (-9.0, -6.0, -3.0), 4.5, 3.0, 1.5, 0.5, move=False)
    return p


@critter("hoppers", "Ant")
def ant():
    """Three body parts joined by a waist: head, mesosoma (the thorax with the six legs on it), a small petiole node and the big gaster; elbowed antennae."""
    p = new("GN_Ant_01")
    p.motion = "walk"
    blob(p, "black", (0, -3.7, 2.3), (1.2, 1.3, 1.1), n=6, rings=1)                         # head
    for s in (-1, 1):
        p.box("rust_dark", (s * 0.6, -4.7, 1.9), (0.35, 0.8, 0.3), rot=(0, 0, s * -20))    # mandibles
    blob(p, "rust_dark", (0, -1.0, 2.5), (0.9, 2.0, 0.9), n=6, rings=2)                    # mesosoma
    blob(p, "rust_dark", (0, 1.2, 2.8), (0.5, 0.8, 0.6), n=6, rings=1)                     # petiole: the narrow waist
    blob(p, "black", (0, 3.9, 2.4), (1.5, 2.6, 1.3), n=6, rings=2)                         # gaster
    legs(p, "black", 0.5, (-2.0, -1.0, 0.0), 2.0, 2.3, 0.9, 0.3, dy=0.6)                   # all three pairs hang from the mesosoma
    for s in (-1, 1):
        base = (s * 0.3, -4.6, 2.5)
        with moving(p, f"Antenna_{'L' if s > 0 else 'R'}", base):                          # scape forward and up, then the bend, then the funiculus
            rod(p, "black", base, (s * 1.2, -6.4, 3.5), 0.2)
            rod(p, "black", (s * 1.2, -6.4, 3.5), (s * 1.6, -7.6, 2.5), 0.2)
    return p


@critter("hoppers", "Grasshopper")
def grasshopper():
    p = new("GN_Grasshopper_01")
    p.motion = "hop"
    blob(p, "corn_leaf", (0, 8, 8.0), (3.5, 14, 3.5), n=6, rings=3)
    blob(p, "corn_leaf", (0, -6, 8.5), (4.0, 5, 4.0), n=6)
    blob(p, "corn_leaf", (0, -13, 8.0), (3.5, 4, 4.0), n=6)
    for s in (-1, 1):
        ball_at(p, "black", (s * 3.2, -13, 9.5), 1.2, n=5)
        p.box("leaf_dark", (s * 1.8, 9, 11.6), (3.2, 24, 0.8), rot=(0, s * 10, 0))
        with moving(p, f"Hind_{'L' if s > 0 else 'R'}", (s * 3.0, 2, 8.0)):          # the big jumping leg: thigh up and back, shin down to the ground
            rod(p, "corn_leaf", (s * 3.0, 2, 8.0), (s * 6.0, 12, 14.0), 3.0)
            rod(p, "fabric_brown", (s * 6.0, 12, 14.0), (s * 7.5, 6, 0.0), 1.4)
        rod(p, "corn_leaf", (s * 2.5, -6, 6.0), (s * 6.0, -9, 3.0), 1.3)
        rod(p, "corn_leaf", (s * 6.0, -9, 3.0), (s * 6.5, -12, 0.0), 1.0)
        rod(p, "corn_leaf", (s * 2.5, -3, 6.0), (s * 6.5, -2, 3.0), 1.3)
        rod(p, "corn_leaf", (s * 6.5, -2, 3.0), (s * 7.5, -3, 0.0), 1.0)
        with moving(p, f"Antenna_{'L' if s > 0 else 'R'}", (s * 1.0, -16, 10.0)):
            rod(p, "black", (s * 1.0, -16, 10.0), (s * 4.0, -30, 16.0), 0.5)
    return p


THORAX_SEGMENTS = 3             # a caterpillar: head capsule, 3 thoracic segments (true legs), then abdominal segments (prolegs on four, claspers on the last)
ABDOMEN_SEGMENTS = 8
PROLEG_SEGMENTS = (2, 3, 4, 5)  # abdominal segments, counted from 0 at the thorax (A3 to A6), that carry a pair of prolegs


@critter("hoppers", "Caterpillar")
def caterpillar():
    p = new("GN_Caterpillar_01")
    p.motion = "caterpillar"
    last = THORAX_SEGMENTS + ABDOMEN_SEGMENTS - 1
    for i in range(THORAX_SEGMENTS + ABDOMEN_SEGMENTS):
        y = -9.0 + 2.8 * i
        z = 2.8 + 1.0 * math.sin(math.pi * i / last)
        thorax = i < THORAX_SEGMENTS
        w = 2.1 if thorax else (2.9 if i < last else 2.2)                                  # the thorax is slimmer, the tail tapers
        with (moving(p, f"Seg{i}", (0, y, 1.0)) if i else nullcontext()):                  # the first segment is the body the others move against
            blob(p, "corn_leaf" if i % 2 == 0 else "plant_green", (0, y, z), (w, 2.3, w * 0.92), n=6, rings=2)
            if not thorax:
                p.box("paint_yellow", (0, y, z + w * 0.7), (1.4, 1.0, 0.4))
            for s in (-1, 1):
                if thorax:                                                                  # a true leg: a thin straight rod to the ground
                    rod(p, "dark_brown", (s * 1.2, y, z - 1.2), (s * 1.8, y - 0.6, 0.0), 0.35)
                elif i - THORAX_SEGMENTS in PROLEG_SEGMENTS or i == last:                  # a proleg (stubby) or an anal clasper at the tail
                    p.box("plant_green", (s * 1.5, y - (1.0 if i == last else 0.0), 1.0), (1.2, 1.8, 2.0))
    with moving(p, "Head", (0, -11.0, 2.0)):
        blob(p, "cloth_red", (0, -12.4, 3.3), (2.2, 1.8, 2.1), n=6, rings=1)               # head capsule
    return p


@critter("arachnids", "Spider")
def spider():
    p = new("GN_Spider_01")
    p.motion = "spider"
    blob(p, "dark_brown", (0, -2, 3.0), (2.6, 2.6, 1.8), n=8)
    blob(p, "dark_brown", (0, 3.2, 3.4), (3.2, 4.0, 3.0), n=8, rings=3)
    p.box("tan", (0, 3.0, 6.3), (1.4, 3.0, 0.4))
    for s in (-1, 1):
        p.box("paint_white", (s * 0.8, -4.5, 3.6), (0.5, 0.4, 0.5))
        for i, (y, dy) in enumerate(((-3.0, -3.5), (-1.8, -1.5), (-0.5, 1.5), (0.8, 3.5))):
            hip = (s * 1.6, y, 3.0)
            knee = (s * 8.0, y + dy * 0.8, 7.0)
            foot = (s * 13.0, y + dy * 1.6, 0.0)
            with moving(p, f"Leg_{'L' if s > 0 else 'R'}{i}", hip):
                rod(p, "black", hip, knee, 0.6)
                rod(p, "black", knee, foot, 0.6)
    return p


# ===== The wider cast (issue #80: the creature list of Grounded, as real species), batch 1 ==========================
@critter("beetles", "StinkBug")
def stink_bug():
    """A brown marmorated stink bug (about 15 mm): a shield-shaped body with a broad pronotum, a small head, long antennae and six legs."""
    p = new("GN_StinkBug_01")
    p.motion = "walk"
    blob(p, "fabric_brown", (0, 1.5, 3.2), (5.5, 6.5, 2.8), n=6, rings=3)                   # the shield: scutellum and wing covers
    blob(p, "tan", (0, -3.3, 3.5), (5.0, 2.4, 2.2), n=6, rings=2)                           # the broad pronotum with its pale edge
    blob(p, "dark_brown", (0, -6.4, 3.1), (2.4, 1.8, 1.6), n=6, rings=1)                    # the head
    antennae(p, "dark_brown", (1.0, -7.0, 3.3), (3.4, -12.0, 5.0), 0.4)
    legs(p, "dark_brown", 3.2, (-3.5, -0.5, 3.0), 2.4, 3.5, 2.0, 0.5, dy=0.5)
    return p


@critter("flyers", "Housefly")
def housefly():
    """A housefly (about 7 mm): a grey thorax and abdomen, big red eyes, two clear wings held out over the back (folded back along it when landed in the rigged Idle clip), bristly black legs."""
    p = new("GN_Housefly_01")
    p.motion = "fold"
    blob(p, "fabric_grey", (0, 1.9, 2.0), (1.4, 2.1, 1.2), n=6, rings=2)                    # abdomen
    blob(p, "fabric_grey", (0, -0.6, 2.25), (1.45, 1.45, 1.3), n=6, rings=2)                # thorax
    blob(p, "black", (0, -2.4, 2.0), (1.05, 0.8, 1.0), n=6, rings=1)                        # head
    for s in (-1, 1):
        ball_at(p, "cloth_red", (s * 0.8, -2.55, 2.3), 0.7, n=5)                            # the compound eyes
        with flap(p, "Wing", s, (s * 0.48, -0.3, 3.2)):                                       # the root is on the thorax's side, inside the faceted loft, and the wing is centred on the pivot
            wing(p, "clear_glass", None, ellipse_pts(0.5 + 2.3, -0.3, 2.3, 1.0), 3.045, tilt=18, side=s, thick=0.1)
    legs(p, "black", 0.8, (-1.3, -0.3, 1.0), 1.5, 0.9, 0.65, 0.2, dy=0.3, move=False)
    return p


@critter("flyers", "Mosquito")
def mosquito():
    """A mosquito (about 6 mm): a slim banded body, a long proboscis, narrow wings and very long thin legs."""
    p = new("GN_Mosquito_01")
    p.motion = "mosquito"
    banded(p, ("wood_grey", "black"), (0, 2.0, 2.2), (0.5, 2.3, 0.5), n=6, rings=5)         # the abdomen, with bands
    blob(p, "wood_grey", (0, -0.6, 2.3), (0.6, 1.0, 0.6), n=6, rings=2)                     # thorax
    blob(p, "black", (0, -1.8, 2.3), (0.42, 0.42, 0.42), n=6, rings=1)                      # head
    rod(p, "black", (0, -2.1, 2.2), (0, -4.1, 1.9), 0.12)                                   # the proboscis
    for s in (-1, 1):
        with flap(p, "Wing", s, (s * 0.24, -0.2, 2.65)):                                      # root on the thorax's side, inside the faceted loft; the wing is centred on the pivot
            wing(p, "clear_glass", None, ellipse_pts(0.25 + 1.6, -0.2, 1.6, 0.5), 2.585, tilt=15, side=s, thick=0.06)
    antennae(p, "black", (0.2, -1.9, 2.5), (0.6, -3.2, 3.0), 0.07)
    legs(p, "black", 0.36, (-1.1, -0.2, 0.8), 2.0, 2.1, 1.8, 0.09, dy=0.6, shins=True)
    return p


@critter("flyers", "Wasp")
def wasp():
    """A common wasp (about 16 mm): a yellow and black banded abdomen on a thin waist, a black thorax, a yellow face and four clear wings."""
    p = new("GN_Wasp_01")
    p.motion = "wasp"
    banded(p, ("paint_yellow", "black"), (0, 5.2, 4.2), (2.6, 5.0, 2.5), n=6, rings=5)       # the abdomen
    blob(p, "black", (0, 0.4, 4.2), (0.7, 0.9, 0.7), n=6, rings=1)                          # the waist
    blob(p, "black", (0, -2.4, 4.4), (2.5, 2.4, 2.4), n=6, rings=2)                         # the thorax
    blob(p, "paint_yellow", (0, -6.0, 4.3), (2.1, 1.6, 1.9), n=6, rings=1)                  # the face
    for s in (-1, 1):
        ball_at(p, "black", (s * 1.5, -6.3, 4.8), 0.8, n=5)                                 # the eyes
        with flap(p, "WingF", s, (s * 0.45, -2.6, 6.15)):                                     # each wing is rooted on the thorax's side and turns about its own root
            wing(p, "clear_glass", None, ellipse_pts(0.5 + 6.0, -2.6, 6.0, 1.8), 5.94, tilt=25, side=s, thick=0.18)
        with flap(p, "WingH", s, (s * 0.45, -1.0, 6.15)):                                      # same flap line as the fore wing (z), 0.35 mm under it (0.18 thick each)
            wing(p, "clear_glass", None, ellipse_pts(0.5 + 4.2, -1.0, 4.2, 1.3), 5.59, tilt=25, side=s, thick=0.18)
    legs(p, "paint_yellow", 1.4, (-3.8, -2.4, -1.0), 3.0, 3.0, 1.6, 0.4, dy=0.5, move=False)
    antennae(p, "black", (0.6, -6.7, 4.8), (1.6, -11.0, 6.8), 0.3)
    return p


@critter("beetles", "Cockroach")
def cockroach():
    """An American cockroach (about 35 mm): a flat reddish-brown oval body with a shield-like pronotum, a small head, spiny legs and antennae as long as the body."""
    p = new("GN_Cockroach_01")
    p.motion = "walk"
    blob(p, "rust_dark", (0, 2.4, 4.0), (7.0, 14.4, 3.0), n=8, rings=3)                     # the wings, folded over the abdomen
    blob(p, "dark_brown", (0, -10.0, 4.3), (7.0, 4.2, 2.5), n=8, rings=2)                   # the pronotum
    blob(p, "dark_brown", (0, -15.2, 3.7), (3.0, 2.4, 2.3), n=6, rings=1)                   # the head
    for s in (-1, 1):
        p.box("dark_brown", (s * 1.5, 15.4, 3.4), (0.9, 2.8, 0.9))                         # the cerci at the tail
    legs(p, "dark_brown", 4.8, (-7.2, -1.2, 6.0), 4.0, 10.5, 3.6, 1.0, dy=1.8)
    antennae(p, "dark_brown", (1.2, -16.0, 4.1), (9.0, -38.0, 6.8), 0.45)
    return p


@critter("hoppers", "Cricket")
def cricket():
    """A house cricket (about 20 mm): a dark brown body with a big head, folded wings, two big hind legs that kick and very long thin antennae."""
    p = new("GN_Cricket_01")
    p.motion = "hop"
    blob(p, "dark_brown", (0, 4.0, 5.0), (3.2, 8.0, 3.2), n=6, rings=3)
    blob(p, "black", (0, -3.0, 5.6), (3.0, 2.2, 2.6), n=6, rings=1)                         # the pronotum
    blob(p, "dark_brown", (0, -6.5, 5.2), (2.8, 2.6, 2.8), n=6, rings=1)                    # the head
    for s in (-1, 1):
        p.box("fabric_brown", (s * 1.8, 3.0, 7.6), (3.0, 12.0, 0.6), rot=(0, s * 12, 0))   # the wing covers
        with moving(p, f"Hind_{'L' if s > 0 else 'R'}", (s * 2.6, 2.5, 5.0)):                # the jumping leg: thigh up and back, shin down to the ground
            rod(p, "dark_brown", (s * 2.6, 2.5, 5.0), (s * 5.5, 9.0, 10.0), 2.2)
            rod(p, "fabric_brown", (s * 5.5, 9.0, 10.0), (s * 6.5, 5.0, 0.0), 1.0)
        rod(p, "dark_brown", (s * 1.8, -3.5, 5.0), (s * 5.5, -5.5, 2.5), 1.1)
        rod(p, "dark_brown", (s * 5.5, -5.5, 2.5), (s * 6.0, -8.0, 0.0), 0.8)
        rod(p, "dark_brown", (s * 2.0, -0.5, 5.0), (s * 6.0, 0.5, 2.5), 1.1)
        rod(p, "dark_brown", (s * 6.0, 0.5, 2.5), (s * 7.0, -0.5, 0.0), 0.8)
        with moving(p, f"Antenna_{'L' if s > 0 else 'R'}", (s * 0.6, -8.0, 6.0)):
            rod(p, "black", (s * 0.6, -8.0, 6.0), (s * 3.0, -26.0, 12.0), 0.35)
    return p


@critter("hoppers", "Mantis")
def mantis():
    """A praying mantis (about 60 mm): a long green body, a triangular head with big eyes, folded raptorial forelegs and four walking legs."""
    p = new("GN_Mantis_01")
    p.motion = "walk"
    blob(p, "plant_green", (0, 12.0, 9.0), (3.2, 18.0, 3.0), n=6, rings=3)                  # the abdomen with the folded wings on it
    blob(p, "corn_leaf", (0, -13.5, 11.0), (2.2, 11.5, 2.2), n=6, rings=2)                  # the long prothorax, from the head to the abdomen
    blob(p, "plant_green", (0, -25.0, 12.0), (4.0, 2.2, 3.2), n=6, rings=1)                 # the triangular head
    for s in (-1, 1):
        ball_at(p, "black", (s * 3.6, -25.5, 13.0), 1.5, n=5)                               # the big eyes
        p.box("leaf_dark", (s * 1.6, 8.0, 11.8), (1.8, 30.0, 0.6), rot=(0, s * 8, 0))      # the wing covers
        rod(p, "plant_green", (s * 2.2, -14.0, 10.5), (s * 4.4, -26.5, 13.0), 2.2)           # the raptorial foreleg: the big femur held forward,
        rod(p, "plant_green", (s * 4.4, -26.5, 13.0), (s * 3.6, -15.0, 9.4), 1.6)            # the tibia folded back under it
    legs(p, "plant_green", 1.8, (-2.0, 8.0), 8.5, 9.0, 6.0, 1.0, dy=1.5)
    antennae(p, "plant_green", (1.0, -25.5, 13.5), (3.0, -32.0, 18.0), 0.3)
    return p


@critter("beetles", "Earwig")
def earwig():
    """A common earwig (about 14 mm without the pincers): a slim dark brown body, a reddish head and pronotum and a pair of curved pincers at the tail."""
    p = new("GN_Earwig_01")
    p.motion = "walk"
    blob(p, "dark_brown", (0, 1.6, 1.8), (1.9, 5.6, 1.45), n=6, rings=3)
    blob(p, "rust_dark", (0, -3.6, 1.95), (2.0, 1.45, 1.35), n=6, rings=1)                  # the pronotum
    blob(p, "rust_dark", (0, -5.6, 1.85), (1.6, 1.3, 1.3), n=6, rings=1)                    # the head
    for s in (-1, 1):
        rod(p, "black", (s * 0.55, 6.5, 1.6), (s * 1.8, 10.0, 1.6), 0.56)                   # the pincers: out and then curving in
        rod(p, "black", (s * 1.8, 10.0, 1.6), (s * 1.1, 12.0, 1.6), 0.44)
    legs(p, "rust_dark", 1.4, (-3.2, -1.2, 1.2), 1.3, 2.8, 1.3, 0.28, dy=0.65)
    antennae(p, "rust_dark", (0.5, -6.1, 2.1), (1.9, -10.0, 3.2), 0.24)
    return p


# ===== The wider cast, batch 2: more beetles, an aphid and the arachnids (issue #80) ================================
def arachnid_legs(p, colour, x, ys, dys, z_hip, reach, up, w):
    """Eight walking legs, four a side, each a moving piece Leg_<L|R><n> (n counts from the head) pivoting at its hip inside the cephalothorax:
    hip at (+-0.7 x, y, z_hip), knee out and up, foot on the ground, the front pair reaching forward and the back pair backward (dys)."""
    for s in (-1, 1):
        for i, (y, dy) in enumerate(zip(ys, dys)):
            hip = (s * x * 0.7, y, z_hip)
            knee = (s * (x + reach * 0.55), y + dy * 0.8, z_hip + up)
            foot = (s * (x + reach), y + dy * 1.6, 0.0)
            with moving(p, f"Leg_{'L' if s > 0 else 'R'}{i}", hip):
                rod(p, colour, hip, knee, w)
                rod(p, colour, knee, foot, w * 0.8)


@critter("beetles", "Aphid")
def aphid():
    """A green aphid (about 3 mm): a soft pear-shaped body, a small head with long antennae, two short cornicles at the tail and six thin legs."""
    p = new("GN_Aphid_01")
    p.motion = "walk"
    blob(p, "plant_green", (0, 0.65, 1.05), (0.76, 1.1, 0.72), n=6, rings=2)                # the abdomen
    blob(p, "plant_green", (0, -0.8, 1.05), (0.44, 0.44, 0.4), n=6, rings=1)                # the head and thorax
    for s in (-1, 1):
        rod(p, "black", (s * 0.36, 1.45, 1.12), (s * 0.44, 2.15, 1.36), 0.13)               # the cornicles
    legs(p, "leaf_dark", 0.2, (-0.5, -0.1, 0.4), 0.9, 0.75, 0.5, 0.08, dy=0.16)
    antennae(p, "leaf_dark", (0.16, -0.95, 1.2), (0.64, -2.55, 1.85), 0.065)
    return p


@critter("beetles", "Weevil")
def weevil():
    """A weevil (about 8 mm without the snout): a rounded dark body, a small head drawn out into a long curved snout, elbowed antennae from the middle of the snout."""
    p = new("GN_Weevil_01")
    p.motion = "walk"
    blob(p, "dark_brown", (0, 1.2, 2.4), (1.9, 2.7, 1.9), n=6, rings=3)                     # the wing covers
    blob(p, "dark_brown", (0, -1.9, 2.4), (1.45, 1.1, 1.35), n=6, rings=1)                  # the pronotum
    blob(p, "rust_dark", (0, -3.2, 2.25), (0.9, 0.8, 0.9), n=6, rings=1)                    # the head
    rod(p, "black", (0, -3.7, 2.15), (0, -6.3, 1.5), 0.65)                                  # the rostrum
    rod(p, "black", (0, -6.3, 1.5), (0, -7.1, 1.1), 0.5)
    for s in (-1, 1):
        with moving(p, f"Antenna_{'L' if s > 0 else 'R'}", (s * 0.35, -5.6, 1.8)):           # elbowed: first out and forward, then bent outward
            rod(p, "black", (s * 0.35, -5.6, 1.8), (s * 0.9, -6.5, 2.4), 0.12)
            rod(p, "black", (s * 0.9, -6.5, 2.4), (s * 1.8, -7.0, 1.9), 0.12)
    legs(p, "black", 0.9, (-1.8, -0.4, 1.3), 1.45, 1.6, 1.1, 0.32, dy=0.4)
    return p


@critter("beetles", "StagBeetle")
def stag_beetle():
    """A male stag beetle (about 40 mm with the jaws): chestnut wing covers, a black pronotum and head, huge branched jaws, a short clubbed antenna and strong legs."""
    p = new("GN_StagBeetle_01")
    p.motion = "walk"
    blob(p, "rust_dark", (0, 6.0, 6.0), (7.0, 12.0, 5.5), n=8, rings=3)                     # the wing covers
    blob(p, "black", (0, -8.0, 6.2), (7.5, 4.0, 4.2), n=8, rings=2)                         # the pronotum
    blob(p, "black", (0, -13.0, 6.0), (6.0, 3.2, 3.8), n=6, rings=1)                        # the head
    for s in (-1, 1):
        rod(p, "rust_dark", (s * 3.0, -13.5, 6.0), (s * 5.5, -19.5, 6.5), 2.4)               # the jaws: out and forward,
        rod(p, "rust_dark", (s * 5.5, -19.5, 6.5), (s * 2.0, -24.0, 7.0), 1.9)               # then curving in toward each other
        rod(p, "rust_dark", (s * 4.9, -18.2, 6.4), (s * 2.6, -18.6, 6.4), 1.2)               # and a tooth on the inside
    antennae(p, "black", (1.8, -12.5, 7.5), (5.0, -19.0, 10.5), 0.8)
    legs(p, "black", 4.6, (-9.0, -1.0, 6.5), 4.5, 9.0, 5.0, 1.4, dy=2.0)
    return p


@critter("beetles", "Scarab")
def scarab():
    """A scarab (dung) beetle (about 25 mm): a rounded blue-black body, a flat shovel-shaped head, short clubbed antennae and broad legs."""
    p = new("GN_Scarab_01")
    p.motion = "walk"
    blob(p, "navy", (0, 3.0, 6.6), (9.0, 9.0, 5.4), n=8, rings=3)                           # the domed wing covers, belly clear of the ground
    blob(p, "navy", (0, -7.0, 5.8), (8.0, 3.5, 4.0), n=8, rings=2)                          # the pronotum
    blob(p, "black", (0, -11.0, 4.8), (6.5, 2.5, 2.6), n=8, rings=1)                        # the flat clypeus, the digging head
    antennae(p, "black", (2.5, -11.6, 5.5), (5.0, -15.0, 7.0), 0.7)
    legs(p, "black", 6.0, (-6.0, -1.0, 6.0), 4.2, 9.0, 4.5, 1.6, dy=1.5)
    return p


@critter("arachnids", "Scorpion")
def scorpion():
    """A scorpion (about 55 mm long with the claws): a flat tan body, two big claws, eight legs and a five-segment tail carried curled over the back to a stinger."""
    p = new("GN_Scorpion_01")
    p.motion = "spider"
    blob(p, "tan", (0, -6.0, 4.0), (6.0, 8.0, 3.0), n=8, rings=2)                           # the carapace
    blob(p, "tan", (0, 8.0, 4.0), (6.5, 10.0, 3.2), n=8, rings=3)                           # the abdomen
    tail = [(0, 15, 4.5), (0, 21, 5.5), (0, 24, 10.5), (0, 20, 16.5), (0, 13, 19.5), (0, 8, 18.0)]
    for a, b in zip(tail, tail[1:]):
        rod(p, "tan", a, b, 3.2)                                                            # the five tail segments, curling up and forward over the back
    ball_at(p, "dark_brown", (0, 8.0, 18.0), 2.3, n=6)                                      # the venom gland
    rod(p, "dark_brown", (0, 8.0, 18.0), (0, 5.0, 15.5), 1.2)                               # the stinger, hooked down and forward
    for s in (-1, 1):
        rod(p, "tan", (s * 3.0, -10.0, 4.0), (s * 9.0, -20.0, 4.0), 2.6)                    # the pedipalp arm
        ball_at(p, "dark_brown", (s * 9.6, -21.6, 4.0), 3.2, n=6)                           # the claw's palm
        rod(p, "dark_brown", (s * 9.6, -21.6, 4.0), (s * 7.5, -29.0, 4.0), 1.4)             # the two fingers
        rod(p, "dark_brown", (s * 9.6, -21.6, 4.0), (s * 12.5, -29.0, 4.0), 1.4)
    arachnid_legs(p, "tan", 4.6, (-8.0, -3.0, 2.0, 7.0), (-2.0, -1.0, 1.0, 2.0), 3.2, 12.0, 4.0, 1.2)
    return p


@critter("arachnids", "WolfSpider")
def wolf_spider():
    """A wolf spider (about 25 mm body): a brown body with a pale stripe down the back, two big forward eyes and long strong legs."""
    p = new("GN_WolfSpider_01")
    p.motion = "spider"
    blob(p, "dark_brown", (0, -5.0, 5.0), (6.0, 6.5, 4.0), n=8, rings=2)                    # the cephalothorax
    blob(p, "fabric_brown", (0, 7.0, 5.0), (5.5, 9.0, 4.5), n=8, rings=3)                   # the abdomen
    p.box("tan", (0, -5.0, 8.4), (1.6, 5.0, 0.6))                                           # the pale stripe
    for s in (-1, 1):
        ball_at(p, "black", (s * 2.3, -10.5, 7.0), 1.4, n=5)                                # the two big front eyes
    arachnid_legs(p, "dark_brown", 5.5, (-9.0, -6.0, -2.0, 1.5), (-5.0, -2.0, 3.0, 7.0), 4.5, 16.0, 8.0, 1.3)
    return p


@critter("arachnids", "OrbWeaver")
def orb_weaver():
    """An orb-weaver spider (about 21 mm body): a big round abdomen with a bright patch, a small cephalothorax and long legs."""
    p = new("GN_OrbWeaver_01")
    p.motion = "spider"
    blob(p, "fabric_brown", (0, 3.0, 9.0), (6.5, 7.4, 6.5), n=8, rings=3)                   # the big abdomen
    ball_at(p, "food_orange", (0, 3.0, 14.6), 2.0, n=5)                                   # the bright spot on top
    blob(p, "rust_dark", (0, -5.0, 5.0), (4.0, 4.2, 3.2), n=8, rings=2)                     # the cephalothorax
    for s in (-1, 1):
        ball_at(p, "black", (s * 1.4, -8.9, 5.8), 0.7, n=5)                                 # the small eyes
    arachnid_legs(p, "rust_dark", 3.4, (-8.0, -5.5, -3.0, -1.0), (-5.0, -2.5, 1.5, 4.0), 4.4, 16.0, 9.0, 0.9)
    return p


@critter("arachnids", "JumpingSpider")
def jumping_spider():
    """A jumping spider (about 8 mm): a stocky black cephalothorax with two huge front eyes, a brown abdomen with a pale chevron and short strong legs."""
    p = new("GN_JumpingSpider_01")
    p.motion = "spider"
    blob(p, "black", (0, -1.3, 2.0), (2.1, 2.1, 1.7), n=8, rings=2)                         # the cephalothorax
    blob(p, "fabric_brown", (0, 2.2, 1.9), (1.7, 2.3, 1.6), n=8, rings=2)                   # the abdomen
    p.box("paint_white", (0, 2.0, 3.3), (0.9, 1.0, 0.3))                                    # the pale chevron
    for s in (-1, 1):
        ball_at(p, "black", (s * 0.8, -3.1, 2.7), 0.7, n=5)                                 # the huge front eyes
        ball_at(p, "paint_white", (s * 0.8, -3.7, 2.8), 0.2, n=4)                           # their highlight
    arachnid_legs(p, "dark_brown", 1.8, (-2.6, -1.8, -0.7, 0.8), (-1.3, -0.7, 0.7, 1.6), 1.6, 3.6, 2.3, 0.55)
    return p


def run():
    names = globals().get("INSECT_LIST")
    chosen = [k for k, (fn, g) in CRITTERS.items() if not names or k in names or g in names]
    x = 0.0
    for key in chosen:
        fn, group = CRITTERS[key]
        prop = fn()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Animals/Insects/{prop.name}.fbx")
        obj.location = (x, 0, 0)
        x += max(0.02, obj.dimensions.x + 0.01)
    print("insects done", len(chosen))


if __name__ == "__main__":
    run()
