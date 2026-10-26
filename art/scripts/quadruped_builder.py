"""Build any four-legged animal from a species description, in one of two styles, on the shared quadruped rig.

    import quadruped_builder, species
    quadruped_builder.build(species.SPECIES["cow"], style="smooth")      # our own, rounded
    quadruped_builder.build(species.SPECIES["cow"], style="faceted")     # the Quaternius-style, hard facets

A species (species.py) lists cross-sections for the body and the neck-and-head, a profile for the front and hind
legs, the tail, a colour function and an optional extras(ctx) hook for udders, horns, manes and the like. The
builder lofts them, skins each part to the right bones and derives the skeleton from the same numbers, so every
animal gets the identical bone names and hierarchy (quadruped_rig.py) and the walk and idle clips apply to it.

Styles, from studying the Quaternius farm pack (about 300-400 verts, quads, hard facets, 2-3 flat colours):
    faceted  8-sided body, 6-sided head, 5-sided legs, no subdivision, flat shaded      ~500-900 tris
    smooth   12-sided body, subdivided once or twice, smooth shaded                      ~2000-4500 tris
"""

import importlib

import bmesh
import bpy

import common
import quadruped_rig

LAST_PARTS = {}                  # the parts of the last animal built (see the end of build)

STYLES = {
    "faceted": {"body_n": 8, "head_n": 6, "leg_n": 5, "tail_n": 4, "sub_body": 0, "sub": 0, "smooth": False},
    "smooth": {"body_n": 12, "head_n": 10, "leg_n": 6, "tail_n": 5, "sub_body": 2, "sub": 1, "smooth": True},
}


class Context:
    """What a species' extras() hook is given."""

    def __init__(self, name, coll, rig, style, parts):
        self.name, self.coll, self.rig, self.style, self._parts = name, coll, rig, style, parts
        self.common = common

    def make(self, part, build, colour, bones, sub=None, smooth=None):
        """One mesh part: build(bm) then subdivide, shade, colour and skin it. sub/smooth default to the style's."""
        bm = bmesh.new()
        build(bm)
        obj = common.new_mesh_object(f"{self.name}_{part}", bm, self.coll, "paint_white")
        s = self.style["sub"] if sub is None else sub
        if s:
            common.subsurf(obj, s)
        common.smooth(obj, self.style["smooth"] if smooth is None else smooth)
        common.paint_faces(obj, colour)
        quadruped_rig.weights(obj, self.rig, bones)
        self._parts.append(obj)
        return obj


def _body_at(body, y):
    """Centre height of the body at y, by linear interpolation of its sections (y runs front to back)."""
    for (y0, z0, *_), (y1, z1, *_) in zip(body, body[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0) if y1 != y0 else 0.0
            return z0 + (z1 - z0) * t
    return body[0][1] if y < body[0][0] else body[-1][1]


def skeleton(sp):
    """Bone positions (left side, mirrored by quadruped_rig.build) derived from the species numbers."""
    body, head, tail = sp["body"], sp["head"], sp["tail"]
    y_front, y_rear = body[0][0], body[-1][0]
    length = y_rear - y_front
    ys = [y_rear - 0.20 * length, y_rear - 0.39 * length, y_rear - 0.67 * length, head[0][0]]
    zs = [_body_at(body, y) for y in ys]
    bones = {
        "Root": ((0, 0, 0), (0, y_front * 0.14, 0)),
        "Hips": ((0, ys[0], zs[0]), (0, ys[1], zs[1])),
        "Spine": ((0, ys[1], zs[1]), (0, ys[2], zs[2])),
        "Chest": ((0, ys[2], zs[2]), (0, ys[3] + 0.04, _body_at(body, ys[3]) + 0.06)),
        "Neck1": ((0, head[0][0] + 0.04, head[0][1]), (0, head[1][0], head[1][1])),
        "Neck2": ((0, head[1][0], head[1][1]), (0, head[2][0], head[2][1])),
        "Head": ((0, head[2][0], head[2][1]), (0, head[-1][0], head[-1][1])),
        "Ear_L": ((sp["ear_x"] * 0.6, sp["ear_y"], sp["ear_z"]), (sp["ear_x"] * 1.25, sp["ear_y"], sp["ear_z"] - 0.03)),
    }
    for kind, leg in (("Front", sp["front"]), ("Hind", sp["hind"])):
        p, (knee, ankle), x, y0 = leg["profile"], leg["joints"], leg["x"], leg["y"]
        pt = lambda i: (x, y0 + p[i][1], p[i][0])
        bones[f"{kind}Upper_L"] = (pt(0), pt(knee))
        bones[f"{kind}Lower_L"] = (pt(knee), pt(ankle))
        bones[f"{kind}Foot_L"] = (pt(ankle), (x, y0 + p[-1][1], 0.0))
    t = [(0, y, z) for z, y, _ in tail]
    a, b = len(t) // 3, 2 * len(t) // 3
    bones["Tail1"] = (t[0], t[a])
    bones["Tail2"] = (t[a], t[b])
    bones["Tail3"] = (t[b], t[-1])
    return bones


def _ball(bm, centre, radius, n=6):
    """A faceted ball (5 rings round the X axis), for an eyeball: rounder than a box and no corners to stand off the head."""
    from math import cos, pi, sin
    cx, cy, cz = centre
    rings = [common.ring_x(cx + radius * cos(pi * k / 4), cy, cz, max(radius * sin(pi * k / 4), 0.0001), max(radius * sin(pi * k / 4), 0.0001), n=n)
             for k in range(5)]
    common.loft(bm, rings)


# where the eyes sit: behind the nose by `gap` of the head's length from the ears (the head runs neck to nose, the ears are at sp["ear_y"]), `inset` how far
# the eyeball's centre is set into the head, as a fraction of the eyeball's radius, below the head's measured surface (0.55: a bit under half the ball shows), `up` a fraction of its half height above its centre, `forward` how much they look forward rather than
# sideways, `size` the eyeball's radius as a fraction of the head's half height: a prey animal's are on the sides of the head, a predator's face forward
EYES_SIDE = {"gap": 0.14, "inset": 0.55, "up": 0.32, "forward": 0.15, "size": 0.16}
EYES_FRONT = {"gap": 0.20, "inset": 0.55, "up": 0.34, "forward": 0.80, "size": 0.16}


def _head_at(head, y):
    """(centre z, half width, half height) of the head at y, interpolated between its rings (they run neck to nose: y falls)."""
    for a, b in zip(head, head[1:]):
        if a[0] >= y >= b[0]:
            f = (a[0] - y) / (a[0] - b[0]) if a[0] != b[0] else 0.0
            return tuple(a[i] + (b[i] - a[i]) * f for i in (1, 2, 3))
    last = head[-1] if y < head[-1][0] else head[0]
    return last[1], last[2], last[3]


def _surface_x(ctx, y, z, fallback):
    """The x of the head's side surface at (y, z): a ray from the middle of the head, out along +X, against the head part (the head is a polygon that
    curves away from the face, so its width at a given height is not a fraction of its ring's half width)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    head = next((o for o in ctx._parts if o.name.endswith("_head")), None)
    if head is None:
        return fallback
    me = head.data
    tree = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    hit = tree.ray_cast(Vector((0.0, y, z)), Vector((1.0, 0.0, 0.0)))
    return hit[0].x if hit[0] is not None else fallback


def _eyes_and_nose(ctx, sp):
    """Every animal gets eyes, and a muzzle with nostrils, unless its species made its own (cats, dogs' noses): a white eyeball set into each side of the
    head in front of the ears with a black pupil on the side it looks towards, and two nostrils at the tip of the nose. The eyeballs are round and their
    centres are inside the skull, so they bulge out of it instead of standing off it (the head is a polygon that curves away from the face).
    sp["eyes"] (EYES_SIDE by default; a species can pass its own dict: the dogs and cats do, and EYES_FRONT is the preset for a forward-looking one) says where."""
    from math import hypot
    head = sp["head"]
    have = {o.name[len(ctx.name) + 1:].split(".")[0] for o in ctx._parts}
    pos = sp.get("eyes", EYES_SIDE)
    length = abs(head[0][0] - head[-1][0])
    y = sp["ear_y"] - pos["gap"] * length                              # in front of the ears
    z, w, h = _head_at(head, y)
    r = pos["size"] * h
    cz = z + pos["up"] * h
    cx = _surface_x(ctx, y, cz, 0.8 * w) - pos["inset"] * r                 # the head's surface at the eye's height, measured, less the inset
    cy = y
    dx, dy = 1.0 - pos["forward"], pos["forward"]                      # the way the eyes look: out to the side and forward
    norm = hypot(dx, dy)
    dx, dy = dx / norm, dy / norm
    if "eyes" not in have:
        ctx.make("eyes", lambda bm: [_ball(bm, (s * cx, cy, cz), r) for s in (-1, 1)], lambda c, n: sp.get("eye_colour", "paint_white"), ["Head"], sub=0, smooth=False)
        ctx.make("pupils", lambda bm: [_ball(bm, (s * (cx + dx * 0.62 * r), cy - dy * 0.62 * r, cz), 0.62 * r) for s in (-1, 1)],
                 lambda c, n: sp.get("pupil_colour", "black"), ["Head"], sub=0, smooth=False)
    if "nose" not in have and "nostrils" not in have:
        tip = head[-1]

        def nostrils(bm):
            for s in (-1, 1):
                common.add_box(bm, (s * 0.40 * tip[2], tip[0] + 0.004, tip[1] + 0.20 * tip[3]), (0.22 * tip[2], 0.02, 0.24 * tip[3]))
        ctx.make("nostrils", nostrils, lambda c, n: "black", ["Head"], sub=0, smooth=False)


def _jitter_uvs(mesh):
    """Move each face's UVs a hair (under 0.004 of the palette, inside its swatch) by its index, so that neighbouring faces (their indices differ by less than 25, which they do in a loft) do not share a corner's attributes.
    Unity merges the corners of a model that have the same position, normal and UV, so a model whose coats are the same mesh painted differently ends up with a different
    vertex count in each coat (a flat stretch of two neighbours is one vertex in a coat where they are the same colour and two in another): this keeps every coat's
    vertex order and count the same (species_farm_dog.py; the game swaps one coat's mesh for another's, DogSkin)."""
    uv = mesh.data.uv_layers.active.data
    for poly in mesh.data.polygons:
        du = ((poly.index % 5) - 2) * 0.0015
        dv = (((poly.index // 5) % 5) - 2) * 0.0015
        for li in poly.loop_indices:
            uv[li].uv = (uv[li].uv[0] + du, uv[li].uv[1] + dv)


def build(sp, style="smooth", rig_name=None):
    """Build the species in the given style; returns (mesh object, rig object). Exports nothing."""
    st = STYLES[style]
    name = f"GN_{sp['name']}_{style}"
    common.setup_scene()
    coll = common.fresh_collection(name)
    rig = quadruped_rig.build(rig_name or f"{name}_Rig", skeleton(sp), coll)
    parts = []
    ctx = Context(name, coll, rig, st, parts)
    side = lambda s: "R" if s < 0 else "L"

    # a species can ask for its own number of sides, whatever the style (the farm dog's head and tail need theirs to read as a dog's; they do not follow the style's)
    body_n = sp.get("body_n", st["body_n"])
    head_n, tail_n = sp.get("head_n", st["head_n"]), sp.get("tail_n", st["tail_n"])
    ctx.make("body", lambda bm: common.loft(bm, [common.ring_y(y, 0, z, w, h, n=body_n) for y, z, w, h in sp["body"]]),
             sp["coat"], ["Hips", "Spine", "Chest"], sub=st["sub_body"])
    ctx.make("head", lambda bm: common.loft(bm, [common.ring_y(y, 0, z, w, h, n=head_n) for y, z, w, h in sp["head"]]),
             sp.get("head_coat", sp["coat"]), ["Chest", "Neck1", "Neck2", "Head"])
    for s in (-1, 1):
        for kind in ("front", "hind"):
            leg = sp[kind]
            K = kind.capitalize()
            ctx.make(f"leg_{kind}_{side(s).lower()}",
                     lambda bm, l=leg, s=s: common.loft(
                         bm, [common.ring_z(z, s * l["x"], l["y"] + dy, hx, hy, n=st["leg_n"]) for z, dy, hx, hy in l["profile"]]),
                     sp["coat"], [f"{K}{p}_{side(s)}" for p in ("Upper", "Lower", "Foot")])
    ctx.make("tail", lambda bm: common.loft(bm, [common.ring_z(z, 0, y, r, r, n=tail_n) for z, y, r in sp["tail"]]),
             sp.get("tail_coat", sp["coat"]), ["Tail1", "Tail2", "Tail3"], sub=0)
    if "extras" in sp:
        sp["extras"](ctx)
    _eyes_and_nose(ctx, sp)

    # what the parts were, for audit_animals.py: name -> (world vertices, triangles), taken before they are joined into one mesh
    LAST_PARTS.clear()
    for o in parts:
        o.data.calc_loop_triangles()
        LAST_PARTS[o.name[len(name) + 1:].split(".")[0]] = ([o.matrix_world @ v.co for v in o.data.vertices], [tuple(t.vertices) for t in o.data.loop_triangles])

    mesh = common.join(parts, name)
    mesh.location = (0, 0, 0)
    if sp.get("uv_jitter"):
        _jitter_uvs(mesh)
    quadruped_rig.bind(mesh, rig)
    if sp.get("scale", 1.0) != 1.0:                                 # the drawn animal scaled to its real size (the wildlife, the fawn)
        rig.scale = (sp["scale"],) * 3
    return mesh, rig, coll
