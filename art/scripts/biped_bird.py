"""The shared biped-bird rig and builder: chicken, duck, goose, turkey, owl, crow, pigeon (asset list GN-05..GN-59).

    import biped_bird
    biped_bird.build(biped_bird.CHICKEN_HEN, style="faceted")

Like quadruped_builder.py, an animal is a description (cross-sections for the body, the neck and head, the legs,
the tail, colours) and the builder lofts, skins and rigs it, so every bird has the same bone names and the same
clips play on all of them. Birds face -Y, Z up, feet on z = 0.

    Root - Hips - Spine - Neck1 - Neck2 - Head
                |                     (Beak is part of the head)
                +-- Wing1_L - Wing2_L, Wing1_R - Wing2_R
                +-- Tail1 - Tail2
                +-- LegUpper_L - LegLower_L - Foot_L, and _R
"""

import bmesh

import common
import quadruped_rig

HIERARCHY = {
    "Root": None, "Hips": "Root", "Spine": "Hips", "Neck1": "Spine", "Neck2": "Neck1", "Head": "Neck2",
    "Wing1_L": "Spine", "Wing2_L": "Wing1_L",
    "Tail1": "Hips", "Tail2": "Tail1",
    "LegUpper_L": "Hips", "LegLower_L": "LegUpper_L", "Foot_L": "LegLower_L",
}

STYLES = {
    "faceted": {"body_n": 8, "neck_n": 5, "leg_n": 4, "sub": 0, "sub_body": 0, "smooth": False},
    "smooth": {"body_n": 12, "neck_n": 8, "leg_n": 6, "sub": 1, "sub_body": 2, "smooth": True},
}


def feather_specs(sp):
    """The tail feathers of a bird that has `tail_fan` (count, rest, open, length, width, base): for each, its bone name, its direction in the rest pose (the
    feathers lie close together, `rest` degrees apart), its length and the root. The Display clip opens them to `open` degrees apart."""
    import math
    fan = sp.get("tail_fan")
    if not fan:
        return []
    half = fan["count"] // 2
    out = []
    for k in range(-half, half + 1):
        a = math.radians(k * fan["rest"])
        d = (math.sin(a), math.cos(a), -0.03)
        n = math.sqrt(sum(v * v for v in d))
        out.append({"k": k, "bone": f"TailF{k + half}", "base": tuple(fan["base"]), "dir": tuple(v / n for v in d), "angle": k * fan["rest"],
                        "length": fan["length"] * (1.0 - 0.18 * (abs(k) / max(half, 1)) ** 2), "width": fan["width"]})
    return out


def skeleton(sp):
    """Left-side bones from the spec: body rings give hips and spine, the neck rings the neck, legs and wings as given."""
    body, neck = sp["body"], sp["neck"]
    (y0, z0, *_), (y1, z1, *_) = body[0], body[-1]
    ym, zm = (y0 + y1) / 2, (z0 + z1) / 2
    leg = sp["leg"]
    bones = {
        "Root": ((0, 0, 0), (0, y0 * 0.4, 0)),
        "Hips": ((0, y1 * 0.55, zm), (0, ym * 0.3, zm)),
        "Spine": ((0, ym * 0.3, zm), (0, neck[0][1], neck[0][0])),
        "Neck1": ((0, neck[0][1], neck[0][0]), (0, neck[1][1], neck[1][0])),
        "Neck2": ((0, neck[1][1], neck[1][0]), (0, neck[2][1], neck[2][0])),
        "Head": ((0, neck[2][1], neck[2][0]), (0, neck[-1][1] - sp["beak"], neck[-1][0] - 0.01)),
        "Wing1_L": ((sp["wing_x"] * 0.8, sp["wing_y"][0], sp["wing_z"]), (sp["wing_x"] * 1.1, sp["wing_y"][1], sp["wing_z"] - 0.01)),
        "Wing2_L": ((sp["wing_x"] * 1.1, sp["wing_y"][1], sp["wing_z"] - 0.01), (sp["wing_x"] * 1.1, sp["wing_y"][2], sp["wing_z"] - 0.03)),
        "Tail1": ((0, y1 * 0.85, z1), (0, sp["tail"][1][1], sp["tail"][1][0])),
        "Tail2": ((0, sp["tail"][1][1], sp["tail"][1][0]), (0, sp["tail"][-1][1], sp["tail"][-1][0])),
    }
    for spec in feather_specs(sp):                                       # one bone per tail feather (the turkeys): a bone along the feather, from the tail's root
        bones[spec["bone"]] = (spec["base"], tuple(b + 0.2 * d for b, d in zip(spec["base"], spec["dir"])))
    x, p = leg["x"], leg["profile"]
    pt = lambda i: (x, p[i][1], p[i][0])
    bones["LegUpper_L"] = (pt(0), pt(leg["joints"][0]))
    bones["LegLower_L"] = (pt(leg["joints"][0]), pt(leg["joints"][1]))
    bones["Foot_L"] = (pt(leg["joints"][1]), (x, p[-1][1] - leg["toe"], 0.0))
    return bones


def build(sp, style="smooth", scale=1.0):
    import math
    st = STYLES[style]
    name = f"GN_{sp['name']}_{style}"
    common.setup_scene()
    coll = common.fresh_collection(name)
    hierarchy = dict(HIERARCHY)
    hierarchy.update({spec["bone"]: "Tail1" for spec in feather_specs(sp)})
    rig = quadruped_rig.build(f"{name}_Rig", skeleton(sp), coll, hierarchy=hierarchy)
    parts = []

    def make(part, build_fn, colour, bones, sub=None, smooth=None):
        bm = bmesh.new()
        build_fn(bm)
        obj = common.new_mesh_object(f"{name}_{part}", bm, coll, "paint_white")
        s = st["sub"] if sub is None else sub
        if s:
            common.subsurf(obj, s)
        common.smooth(obj, st["smooth"] if smooth is None else smooth)
        common.paint_faces(obj, colour)
        quadruped_rig.weights(obj, rig, bones)
        parts.append(obj)

    make("body", lambda bm: common.loft(bm, [common.ring_y(y, 0, z, w, h, n=st["body_n"]) for y, z, w, h in sp["body"]]),
         sp["coat"], ["Hips", "Spine", "Neck1"], sub=st["sub_body"])
    make("neck", lambda bm: common.loft(bm, [common.ring_z(z, 0, y, rx, ry, n=st["neck_n"]) for z, y, rx, ry in sp["neck"]]),
         sp.get("neck_coat", sp["coat"]), ["Spine", "Neck1", "Neck2", "Head"])
    leg = sp["leg"]
    for s, tag in ((1, "L"), (-1, "R")):
        make(f"leg_{tag.lower()}",
             lambda bm, s=s: common.loft(bm, [common.ring_z(z, s * leg["x"], y, hx, hy, n=st["leg_n"]) for z, y, hx, hy in leg["profile"]]),
             lambda c, n: sp["leg_colour"], ["Hips", f"LegUpper_{tag}", f"LegLower_{tag}", f"Foot_{tag}"], sub=0)
        make(f"toes_{tag.lower()}",
             lambda bm, s=s: [common.add_box(bm, (s * leg["x"] + dx, leg["profile"][-1][1] - leg["toe"] / 2 + dy, 0.008),
                                              (0.012, leg["toe"] * ln, 0.012), rot_deg=(0, 0, ang))
                              for dx, dy, ln, ang in ((0, 0, 1.0, 0), (-0.02 * s, -0.005, 0.8, -25 * s), (0.02 * s, -0.005, 0.8, 25 * s), (0, 0.035, 0.45, 0))],
             lambda c, n: sp["leg_colour"], [f"Foot_{tag}"], sub=0, smooth=False)
        make(f"wing_{tag.lower()}",
             lambda bm, s=s: common.loft(bm, [common.ring_y(y, s * cx, cz, hw, hh, n=6) for y, cx, cz, hw, hh in sp["wing"]]),
             sp.get("wing_coat", sp["coat"]), [f"Wing1_{tag}", f"Wing2_{tag}", "Spine"])
    if sp.get("tail_boxes", True):
        make("tail", lambda bm: [common.add_box(bm, (sx * sp["tail_spread"], sp["tail"][0][1] + 0.03, sp["tail"][0][0] + 0.07),
                                                 (0.014, 0.10, 0.13), rot_deg=(sp.get("tail_rise", 25), 0, sx * 28), taper=1.0) for sx in (-1, 0, 1)],
             sp.get("tail_coat", sp["coat"]), ["Tail1", "Tail2"], sub=0, smooth=False)
    if "extras" in sp:
        sp["extras"](type("Ctx", (), {"make": staticmethod(make), "common": common, "sp": sp})())
    mesh = common.join(parts, name)
    mesh.location = (0, 0, 0)
    quadruped_rig.bind(mesh, rig)
    if not math.isclose(scale, 1.0):
        rig.scale = (scale, scale, scale)
    return mesh, rig, coll


def _bird_eyes(ctx, sp):
    """Round eyes on the sides of the head (neck ring `eye_ring`, 3 by default): a white eyeball set into the skull and a black pupil looking out and
    a little forward, like the quadrupeds' (quadruped_builder._ball)."""
    import quadruped_builder as qb
    z, y, rx, ry = sp["neck"][sp.get("eye_ring", 3)]
    r = 0.36 * rx
    cx, cy, cz = rx - 0.35 * r, y - 0.2 * ry, z + 0.25 * ry
    ctx.make("eyes", lambda bm: [qb._ball(bm, (s * cx, cy, cz), r) for s in (-1, 1)], lambda c, n: "paint_white", ["Head"], sub=0, smooth=False)
    ctx.make("pupils", lambda bm: [qb._ball(bm, (s * (cx + 0.5 * r), cy - 0.3 * r, cz), 0.62 * r) for s in (-1, 1)], lambda c, n: "black", ["Head"], sub=0, smooth=False)


def _chicken_extras(ctx):
    c = ctx.common

    def head_bits(bm):
        c.add_box(bm, (0, -0.222, 0.47), (0.024, 0.048, 0.02), taper=0.55)                              # beak
    ctx.make("beak", head_bits, lambda c_, n: "straw", ["Head"], sub=0, smooth=False)

    def comb(bm):
        c.add_box(bm, (0, -0.195, 0.532), (0.013, 0.07, 0.04))                                           # comb
        c.add_box(bm, (0, -0.232, 0.435), (0.015, 0.015, 0.045))                                         # wattle
    ctx.make("comb", comb, lambda c_, n: "cloth_red", ["Head"], sub=0, smooth=False)

    _bird_eyes(ctx, CHICKEN_HEN)
    _hen_tail(ctx)


def _hen_tail(ctx, count=7, apart=13.0, length=0.27, root=(0.15, 0.335)):
    """A raised, curved fan of tapering, pointed tail feathers: `count` of them `apart` degrees apart, the middle one the longest, each rising from the rump at 36 degrees and
    curling up to 60 at the tip, rooted inside the body (root = y, z). A feather is a flat leaf (a diamond ring that is wide and thin, five stations from the root to the tip)."""
    import math
    from mathutils import Vector
    c = ctx.common
    half = count // 2

    def feather(bm, k):
        yaw = math.radians(k * apart)
        ln = length * (1.0 - 0.14 * (abs(k) / max(half, 1)) ** 2)
        p = Vector((0.0, root[0], root[1]))
        rings = []
        for i in range(6):
            t = i / 5
            rise = math.radians(36 + 24 * t)
            d = Vector((math.sin(yaw) * math.cos(rise), math.cos(yaw) * math.cos(rise), math.sin(rise)))
            u = Vector((math.cos(yaw), -math.sin(yaw), 0.0))               # across the feather
            n = d.cross(u).normalized()                                    # through it
            width = (0.014, 0.034, 0.042, 0.034, 0.018, 0.002)[i]
            thick = 0.007 if i < 5 else 0.0015
            rings.append([p + u * width, p + n * thick, p - u * width, p - n * thick])
            p = p + d * (ln / 5)
        c.loft(bm, rings)

    ctx.make("tail_feathers", lambda bm: [feather(bm, k) for k in range(-half, half + 1)], lambda c_, n: "black", ["Tail1", "Tail2"], sub=0, smooth=False)


CHICKEN_HEN = {
    "name": "ChickenHen",
    # a laying hen (2-2.5 kg): an egg-shaped body with a full, low breast and a tail raised behind, a thick neck that rises into a small round head, legs a
    # third of the height, a drumstick over a shank with four toes. Drawn 0.52 m to the top of the head, 0.55 to the comb tip (and 0.8 of that when exported: gn_birds.SIZE)
    "body": [(-0.17, 0.30, 0.06, 0.09), (-0.09, 0.28, 0.105, 0.135), (0.00, 0.28, 0.112, 0.145), (0.10, 0.30, 0.095, 0.125),
          (0.19, 0.345, 0.06, 0.08)],
    "neck": [(0.32, -0.12, 0.062, 0.065), (0.39, -0.155, 0.045, 0.048), (0.45, -0.175, 0.036, 0.04), (0.485, -0.19, 0.04, 0.044),
          (0.52, -0.195, 0.034, 0.038)],
    "beak": 0.03,
    "wing": [(-0.06, 0.125, 0.30, 0.022, 0.07), (0.02, 0.136, 0.29, 0.026, 0.09), (0.11, 0.127, 0.285, 0.02, 0.075), (0.18, 0.108, 0.275, 0.012, 0.04)],
    "wing_x": 0.125, "wing_y": (0.0, 0.06, 0.15), "wing_z": 0.30,
    "leg": {"x": 0.055, "joints": (1, 2), "toe": 0.085,
             "profile": [(0.24, 0.02, 0.034, 0.034), (0.13, 0.00, 0.02, 0.02), (0.06, 0.03, 0.015, 0.015), (0.0, 0.03, 0.015, 0.015)]},
    "leg_colour": "straw",
    "tail": [(0.40, 0.19), (0.46, 0.23), (0.51, 0.265)], "tail_boxes": False,
    "coat": lambda c, n: "brown_coat",
    "tail_coat": lambda c, n: "black",
    "neck_coat": lambda c, n: "brown_coat",
    "extras": _chicken_extras,
}


def _turkey_extras(ctx):
    c = ctx.common
    z, y, _, _ = ctx.sp["neck"][3]

    def beak(bm):
        c.add_box(bm, (0, y - 0.045, z - 0.012), (0.028, 0.06, 0.026), taper=0.5)                       # a short, pointed beak
    ctx.make("beak", beak, lambda c_, n: "straw", ["Head"], sub=0, smooth=False)
    _bird_eyes(ctx, ctx.sp)

    _turkey_fan(ctx)
    if ctx.sp.get("tom"):
        def head_bits(bm):
            c.add_box(bm, (0, y - 0.03, z - 0.075), (0.026, 0.026, 0.09))                               # the wattle, hanging under the chin
            c.add_box(bm, (0, y - 0.065, z + 0.04), (0.022, 0.07, 0.05))                                # the snood over the beak
        ctx.make("wattle", head_bits, lambda c_, n: "cloth_red", ["Head"], sub=0, smooth=False)

        def beard(bm):
            c.add_box(bm, (0, -0.30, 0.50), (0.02, 0.025, 0.16), rot_deg=(8, 0, 0), taper=0.5)          # the beard on the breast
        ctx.make("beard", beard, lambda c_, n: "black", ["Spine"], sub=0, smooth=False)



def _turkey_fan(ctx):
    """The tail: a plate and a tan tip band for every feather (feather_specs), each skinned to its own TailF bone. At rest the feathers lie close together
    behind the bird, flat and a little down (a folded tail); the Display clip (turkey_display.py) raises Tail1 and opens the feathers into a fan."""
    import math
    c = ctx.common
    for spec in feather_specs(ctx.sp):
        bx, by, bz = spec["base"]
        dx, dy, dz = spec["dir"]
        a = spec["angle"]
        ln, w = spec["length"], spec["width"]
        mid = 0.5 * ln - 0.03                                      # the root is 3 cm inside the body
        tip = ln - 0.075
        ctx.make(f"feather_{spec['k']}", lambda bm, m=mid: c.add_box(bm, (bx + dx * m, by + dy * m, bz + dz * m), (w, ln, 0.02), rot_deg=(-6, 0, -a)),
                 lambda c_, n: "brown_coat", [spec["bone"]], sub=0, smooth=False)
        ctx.make(f"tip_{spec['k']}", lambda bm, m=tip: c.add_box(bm, (bx + dx * m, by + dy * m, bz + dz * m), (w, 0.09, 0.022), rot_deg=(-6, 0, -a)),
                 lambda c_, n: "tan", [spec["bone"]], sub=0, smooth=False)


TURKEY_TOM = {
    "name": "TurkeyTom", "tom": True,
    "body": [(-0.30, 0.55, 0.10, 0.14), (-0.15, 0.58, 0.18, 0.22), (0.05, 0.58, 0.22, 0.26), (0.25, 0.60, 0.18, 0.22), (0.40, 0.62, 0.09, 0.12)],
    "neck": [(0.72, -0.26, 0.085, 0.09), (0.84, -0.32, 0.055, 0.06), (0.93, -0.35, 0.042, 0.047), (0.99, -0.36, 0.042, 0.047), (1.02, -0.37, 0.036, 0.04)],
    "beak": 0.05,
    "wing": [(-0.15, 0.21, 0.58, 0.04, 0.12), (0.05, 0.24, 0.58, 0.05, 0.16), (0.28, 0.23, 0.56, 0.04, 0.14), (0.42, 0.19, 0.54, 0.025, 0.07)],
    "wing_x": 0.25, "wing_y": (0.0, 0.15, 0.38), "wing_z": 0.58,
    "leg": {"x": 0.09, "joints": (1, 2), "toe": 0.13,
             "profile": [(0.40, 0.02, 0.045, 0.045), (0.22, 0.0, 0.03, 0.03), (0.09, 0.04, 0.022, 0.022), (0.0, 0.04, 0.022, 0.022)]},
    "leg_colour": "pink",
    "tail": [(0.58, 0.38), (0.54, 0.50), (0.50, 0.62)], "tail_spread": 0.0, "tail_boxes": False,
    "tail_fan": {"count": 11, "rest": 3.0, "open": 13.0, "length": 0.48, "width": 0.098, "base": (0.0, 0.40, 0.58)},         # 11 feathers: 3 degrees apart folded, 13 apart in the display
    "coat": lambda c, n: "dark_brown" if c.z < 0.9 else "brown_coat",
    "wing_coat": lambda c, n: "brown_coat",
    "tail_coat": lambda c, n: "dark_brown",
    "neck_coat": lambda c, n: "fabric_blue" if c.z > 0.88 else "dark_brown",           # the bare blue head and upper neck
    "extras": _turkey_extras,
}

TURKEY_HEN = dict(
    TURKEY_TOM, name="TurkeyHen", tom=False,
    body=[(-0.24, 0.46, 0.08, 0.11), (-0.12, 0.48, 0.14, 0.17), (0.04, 0.48, 0.17, 0.20), (0.20, 0.50, 0.14, 0.17), (0.32, 0.52, 0.07, 0.09)],
    neck=[(0.60, -0.21, 0.065, 0.07), (0.70, -0.26, 0.042, 0.047), (0.78, -0.28, 0.034, 0.038), (0.83, -0.29, 0.034, 0.038), (0.86, -0.30, 0.03, 0.034)],
    beak=0.04,
    wing=[(-0.12, 0.17, 0.48, 0.032, 0.10), (0.04, 0.19, 0.48, 0.04, 0.13), (0.22, 0.18, 0.46, 0.032, 0.11), (0.34, 0.15, 0.44, 0.02, 0.06)],
    wing_x=0.20, wing_y=(0.0, 0.12, 0.30), wing_z=0.48,
    leg={"x": 0.07, "joints": (1, 2), "toe": 0.10,
             "profile": [(0.32, 0.02, 0.036, 0.036), (0.18, 0.0, 0.024, 0.024), (0.07, 0.03, 0.018, 0.018), (0.0, 0.03, 0.018, 0.018)]},
    tail=[(0.48, 0.30), (0.45, 0.40), (0.42, 0.50)], tail_boxes=False,
    tail_fan={"count": 7, "rest": 3.0, "open": 3.0, "length": 0.32, "width": 0.085, "base": (0.0, 0.32, 0.48)},          # the hen's tail does not open
    coat=lambda c, n: "brown_coat",
    neck_coat=lambda c, n: "fur_grey" if c.z > 0.74 else "brown_coat",               # a dull grey-brown head
)
