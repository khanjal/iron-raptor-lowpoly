"""Plants and rocks (asset list GB-, FM-V): flat faceted trees, bushes, boulders and the corn.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/vegetation.py", run_name="__main__")
Optional global VEG_LIST. Exports Assets/Art/Farm/Vegetation/<name>.fbx.

Corn (FM-V1) is the performance-critical one: hundreds of strips are instanced over the field, so a strip must stay near 500 tris. A
strip is 4 m of row (along Y) drawn as double-sided *cards*, each card a flat plant silhouette (tapered stalk, arching leaves, husked ears and a
tassel) built from real triangles instead of an alpha texture, with each position holding two crossed cards (turned 90 degrees, with a little
per-position twist) so the strip looks full from any side. There are six kinds of plant (CORN_KINDS: two ears, one, one high up, none yet, leaning, dry) and four strips
(FM_CornStrip_01..04) that mix them, so the field is not one stalk repeated. A plant is 1.85-2.4 m tall; the field's vision-blocking volumes are separate.
"""

import importlib
import sys
from math import cos, pi, radians, sin
from pathlib import Path

import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop


def blob(p, colour, centre, radius, n=7, squash=1.0, rings=5, jitter=0.12, seed=0, flat_bottom=False, base_z=-0.02):
    """A lumpy faceted ball (canopies, bushes, rocks): rings of n points with a deterministic wobble in radius. The rings run from the bottom (k = 0) to the
    top (k = rings). flat_bottom makes the bottom a flat, capped base at height base_z (a little under the ground at z = 0, so the shape sits on it: a ball
    would touch the ground at a single point and look as if it hovered)."""
    cx, cy, cz = centre
    ring_pts = []
    for k in range(rings + 1):
        phi = pi * k / rings
        r = radius * max(sin(phi), 0.0001)
        z = cz - radius * squash * cos(phi)
        if flat_bottom and k == 0:
            r = radius * sin(pi / rings)               # as wide as the ring above it: the side comes (nearly) straight down to the ground, no skirt
            z = base_z
        pts = []
        for i in range(n):
            a = 2 * pi * i / n
            wob = 1.0 + jitter * sin(a * 3 + k * 1.7 + seed) + jitter * 0.6 * cos(a * 2 + k * 0.9 + seed * 2)
            pts.append(Vector((cx + r * wob * cos(a), cy + r * wob * sin(a), z)))
        ring_pts.append(pts)
    p.loft_rings(colour, ring_pts)


def oak(name="FM_TreeOak_01", scale=1.0):
    p = Prop(name)
    p.cyl("bark", (0, 0, 1.4), 0.32, 2.8, n=7, top_radius=0.2)
    for az, z in ((0, 2.5), (180, 2.7)):
        branch(p, "bark", z, az, 38, 1.4, 0.1, 0.06, 0.32 - 0.12 * z / 2.8)
    blob(p, "leaf_dark", (0, 0, 5.2), 2.4, n=8, squash=0.85, seed=1)
    blob(p, "leaf_dark", (1.7, 0.4, 4.4), 1.6, n=7, squash=0.8, seed=2)
    blob(p, "leaf_dark", (-1.6, -0.5, 4.6), 1.7, n=7, squash=0.8, seed=3)
    blob(p, "corn_leaf", (0.2, -0.3, 6.5), 1.3, n=7, squash=0.8, seed=4)
    return p


def pine(name="FM_TreePine_01"):
    p = Prop(name)
    p.cyl("bark", (0, 0, 1.0), 0.22, 2.0, n=6, top_radius=0.16)
    for z, r, h in ((1.8, 1.9, 2.2), (3.2, 1.5, 2.0), (4.6, 1.1, 1.8), (5.8, 0.7, 1.5)):
        p.cyl("pine", (0, 0, z + h / 2), r, h, n=7, top_radius=0.0001)
    return p


def branch(p, colour, z, azimuth, tilt, length, r0, r1, trunk_r):
    """A limb that starts at the trunk's surface at height z, azimuth degrees round, leaning out `tilt` degrees from vertical."""
    a, t = radians(azimuth), radians(tilt)
    base = Vector(((trunk_r - 0.03) * cos(a), (trunk_r - 0.03) * sin(a), z))               # a little inside the trunk so it joins
    direction = Vector((sin(t) * cos(a), sin(t) * sin(a), cos(t)))
    centre = base + direction * (length / 2)
    p.cyl(colour, (centre.x, centre.y, centre.z), r0, length, n=5, top_radius=r1, rot=(0, tilt, azimuth))


def dead_tree(name="FM_TreeDead_01"):
    p = Prop(name)
    trunk_r = lambda z: 0.28 - (0.28 - 0.1) * z / 4.0
    p.cyl("dead_wood", (0, 0, 2.0), 0.28, 4.0, n=6, top_radius=0.1)
    for z, az, tilt, ln in ((2.4, 0, 50, 1.7), (3.0, 140, 55, 1.5), (3.5, 250, 40, 1.1), (2.8, 300, 45, 1.3), (3.8, 60, 30, 0.9)):
        branch(p, "dead_wood", z, az, tilt, ln, 0.08, 0.02, trunk_r(z))
    return p


def bush(name="FM_Bush_01"):
    p = Prop(name)
    blob(p, "leaf_dark", (0, 0, 0.55), 0.7, n=7, squash=0.75, rings=4, seed=5, flat_bottom=True)
    blob(p, "corn_leaf", (0.5, 0.2, 0.4), 0.45, n=6, squash=0.8, rings=4, seed=6, flat_bottom=True)
    blob(p, "leaf_dark", (-0.5, -0.2, 0.4), 0.5, n=6, squash=0.8, rings=4, seed=7, flat_bottom=True)
    return p


def boulder(name="FM_Boulder_01"):
    p = Prop(name)
    blob(p, "rock", (0, 0, 0.55), 0.9, n=7, squash=0.65, rings=4, jitter=0.2, seed=8, flat_bottom=True)
    blob(p, "rock", (0.7, 0.3, 0.3), 0.45, n=6, squash=0.7, rings=3, jitter=0.2, seed=9, flat_bottom=True)
    return p


def stump(name="FM_Stump_01"):
    p = Prop(name)
    p.cyl("bark", (0, 0, 0.25), 0.4, 0.5, n=8, top_radius=0.34)
    p.cyl("wood_light", (0, 0, 0.51), 0.33, 0.02, n=8)
    return p


# The corn plants. Each kind is one plant: how tall, how many ears (and where on the stalk), how the leaves hang, how far it leans, its colours.
# `ears`: (height of the node, which side it grows out of, size 0.7-1.2); `droop` 0 (leaves held up) to 1 (hanging); `reach` the leaf length
CORN_KINDS = {
    "two":    {"height": 2.35, "ears": [(1.00, 1, 1.0), (1.42, -1, 0.9)], "droop": 0.6, "reach": 0.50, "lean": 0.0},                # a heavy plant: two ears
    "one":    {"height": 2.30, "ears": [(1.12, -1, 1.0)], "droop": 0.5, "reach": 0.46, "lean": 0.0},
    "one_hi": {"height": 2.40, "ears": [(1.35, 1, 1.1)], "droop": 0.7, "reach": 0.52, "lean": 0.0},                                 # a tall plant with its ear high up
    "young":  {"height": 1.85, "ears": [], "droop": 0.1, "reach": 0.32, "lean": 0.0},                                               # not yet in ear: short, leaves held up
    "lean":   {"height": 2.25, "ears": [(1.05, 1, 0.9)], "droop": 0.6, "reach": 0.46, "lean": 0.5},                                 # leaning over from the wind
    "dry":    {"height": 2.20, "ears": [(0.95, 1, 1.2), (1.30, -1, 1.1)], "droop": 1.0, "reach": 0.40, "lean": 0.15, "dry": True},    # gone brown, ears fat and hanging
}


def _plant(p, kind, yaw_deg, y):
    """One corn plant as a double-sided card standing at (0, y), turned yaw_deg about Z; built from real triangles (about 50 a card)."""
    k = CORN_KINDS[kind]
    dry = k.get("dry", False)
    bm_stem = p._bm("hay" if dry else "corn_green")
    bm_leaf = p._bm("dead_wood" if dry else "corn_leaf")
    bm_husk = p._bm("hay" if dry else "leaf_dark")
    bm_cob = p._bm("corn_cob")
    bm_tassel = p._bm("hay")
    height = k["height"]
    a = radians(yaw_deg)
    ca, sa = cos(a), sin(a)

    def bend(z):                                                  # how far the stalk has leaned sideways by height z
        return k["lean"] * 0.35 * (z / height) ** 2

    def P(x, z):                                                  # a point in the card's plane, rotated about the vertical axis
        return Vector(((x + bend(z)) * ca, y + (x + bend(z)) * sa, z))

    def poly(bm, pts):
        vs = [bm.verts.new(P(*pt)) for pt in pts]
        bm.faces.new(vs)                                          # front
        off = Vector((-sa * 0.003, ca * 0.003, 0))                # the back face on its own vertices, a hair behind, so the
        vb = [bm.verts.new(P(*pt) + off) for pt in pts]           # card shows from both sides and the weld in finish() keeps it
        bm.faces.new(vb[::-1])

    # the stalk: thick at the foot, thin at the top, in two pieces so it can lean
    zm = height * 0.5
    poly(bm_stem, [(-0.032, 0.0), (0.032, 0.0), (0.024, zm), (-0.024, zm)])
    poly(bm_stem, [(-0.024, zm), (0.024, zm), (0.015, height * 0.93), (-0.015, height * 0.93)])

    # leaves: a pair at each node, alternating sides, longest at the middle; a blade rises from the stalk, arches and droops at the tip
    nodes = [0.38, 0.72, 1.06, 1.40, 1.72] if height > 2.0 else [0.34, 0.62, 0.90, 1.18]
    for i, z in enumerate(nodes):
        scale = 1.0 - abs(i - (len(nodes) - 1) / 2) * 0.16
        for sgn in (1, -1):
            r = k["reach"] * scale * (1.0 if sgn == 1 else 0.88)
            tip_drop = -0.06 - 0.30 * k["droop"]                   # the tip's height relative to the node
            poly(bm_leaf, [(0, z + 0.01), (sgn * r * 0.5, z + 0.13 - 0.05 * k["droop"]), (sgn * r, z + tip_drop), (sgn * r * 0.45, z + 0.015)])   # a long blade, pointed

    # ears: a fat husked spindle growing out of a node and slanting up, with the gold cob showing at its tip and brown silk above it; bigger when riper
    from math import hypot
    for z, side, size in k["ears"]:
        ln = 0.34 * size
        tilt = 0.10 + 0.10 * (1 - k["droop"] * 0.5)                # how far out the tip of the ear is
        ax, az = side * 0.03, z                                    # the base, on the stalk
        bx, bz = side * (0.03 + tilt * size), z + ln               # the tip
        dx, dz = bx - ax, bz - az
        nx, nz = -dz, dx
        nl = hypot(nx, nz)
        nx, nz = nx / nl, nz / nl
        w = 0.065 * size                                           # half the width at the fattest part, 40% of the way up
        mx, mz = ax + dx * 0.40, az + dz * 0.40
        poly(bm_husk, [(ax, az), (mx + nx * w, mz + nz * w), (ax + dx * 0.86, az + dz * 0.86), (mx - nx * w, mz - nz * w)])
        poly(bm_cob, [(ax + dx * 0.80, az + dz * 0.80), (mx + nx * w * 0.55 + dx * 0.4, mz + nz * w * 0.55 + dz * 0.4), (bx + dx * 0.10, bz + dz * 0.10),
                      (mx - nx * w * 0.55 + dx * 0.4, mz - nz * w * 0.55 + dz * 0.4)])
        poly(bm_tassel, [(bx + dx * 0.05, bz + dz * 0.05), (bx + dx * 0.10 + side * 0.04, bz + dz * 0.10 + 0.10 * size), (bx + dx * 0.10 - side * 0.01, bz + dz * 0.10 + 0.07 * size)])   # silk

    # the tassel at the top: a frond up and two out
    zt = height * 0.93
    poly(bm_tassel, [(0, zt), (-0.015, zt + 0.12), (0.0, height + 0.06), (0.015, zt + 0.12)])
    poly(bm_tassel, [(0, zt), (-0.17, height - 0.10), (-0.14, height - 0.03), (-0.02, zt + 0.10)])
    poly(bm_tassel, [(0, zt), (0.17, height - 0.10), (0.14, height - 0.03), (0.02, zt + 0.10)])


# Four strips of row, 4 m each, no two alike: the kind of plant at each of the four positions; the field picks a strip at random.
CORN_STRIPS = {
    "FM_CornStrip_01": ["two", "one", "one_hi", "young"],
    "FM_CornStrip_02": ["one", "two", "lean", "one_hi"],
    "FM_CornStrip_03": ["young", "one_hi", "two", "one"],
    "FM_CornStrip_04": ["one_hi", "one", "dry", "lean"],
}


def corn_strip(name="FM_CornStrip_01", length=4.0):
    p = Prop(name)
    kinds = CORN_STRIPS[name]
    for i, kind in enumerate(kinds):
        y = -length / 2 + (i + 0.5) * length / len(kinds)
        for yaw in (0, 90):                                        # two crossed cards per plant
            _plant(p, kind, yaw + (i * 23 + len(name) * 7) % 50, y)
    return p


def corn_strip_1(): return corn_strip("FM_CornStrip_01")
def corn_strip_2(): return corn_strip("FM_CornStrip_02")
def corn_strip_3(): return corn_strip("FM_CornStrip_03")
def corn_strip_4(): return corn_strip("FM_CornStrip_04")


def corn_stalk(name="FM_CornStalk_01"):
    """A single plant from three sides, for dressing a spot where a strip would be too long."""
    p = Prop(name)
    for yaw in (0, 60, 120):
        _plant(p, "two", yaw, 0.0)
    return p


VEG = {"oak": oak, "pine": pine, "dead_tree": dead_tree, "bush": bush, "boulder": boulder, "stump": stump, "corn_strip": corn_strip_1, "corn_strip_2": corn_strip_2, "corn_strip_3": corn_strip_3, "corn_strip_4": corn_strip_4, "corn_stalk": corn_stalk}
names = globals().get("VEG_LIST") or list(VEG)
x = 0.0
for key in names:
    prop = VEG[key]()
    obj, coll = prop.finish()
    print(common.stats(obj))
    common.export_fbx(coll, f"Assets/Art/Farm/Vegetation/{prop.name}.fbx")
    obj.location.x = x
    x += obj.dimensions.x + 2.5
print("vegetation done", names)
