"""The farm dog (issue #275): a medium collie / shepherd cross that reads as a dog at a glance, in five coats.

    make_farm_dog("DogCollie", "black_tan")  ->  a species dict for quadruped_builder.py (see species.py for the format)
    SKINS                                    ->  the five coats: black_tan, brown_white, grey_merle, yellow, brindle

The farm's first dog looked like a sheep with a dark face (the owner's play-test): a tube of a body as deep as a barrel, the head a plain continuation of the neck,
ears flat on top of it, a stub of a tail, and a black back over a white belly. This one is built from the real animal (docs/art/animal-notes.md, "Farm dog"):

    * a **deep chest and a tucked waist** (the body is 0.27 m deep at the chest and 0.20 m at the loin, not 0.34 m the whole way), so the belly rises and the legs show
    * a **narrow wedge of a head**: a skull 12 cm wide, a stop, and a muzzle as long as the skull with a nose and a lip line, the lower jaw in a lighter colour
    * **half-folded ears** (an upright base, the tips folded forward), set on the crown at the sides of the skull
    * a **ruff** of fur round the neck, a **medium coat** (no wool: the colour only changes at the markings) and a **tail** carried low with a hook in its tip
    * a **haunch** and a **shoulder** over the top of each leg (the legs' tops are the old collie's, set lower than the new, slimmer body's sides, so a lofted blob joins each to the body)
    * **dark eyes with a highlight**, set in the front of the skull, looking forward

The legs' profiles (the knee and ankle joints and the foot) are the old collie's (the same numbers as the old `species_pets.make_dog` with `leg=0.22`, removed in issue #125), so the leg bones keep their lengths and
with them the gait clips' strides and the speeds in `Anims/gait-speeds.json` (regenerated: they moved by under 1%); the legs stand 1-2 cm further out and back and the body above
them is new, so the other bones' positions moved a little (the bone names and the hierarchy are the shared quadruped rig's, unchanged). Every coat is the same mesh (the same vertices, the
same bones) with the faces painted differently, so the game can swap one for another on a dog that is already in the scene (`DogSkin`).
"""

import math
from types import SimpleNamespace


def _blobs(c, blobs):
    return sum(math.exp(-((c.x - x) ** 2 + (c.y - y) ** 2 + (c.z - z) ** 2) / (2 * s * s)) for x, y, z, s in blobs)


W = "paint_white"

# The coats. Every key is a palette swatch (common.PALETTE) or None (= the coat's body colour):
#   body     the back, sides and the top of the head          under    belly and the underside of the chest      legs   the legs above the socks
#   sock     the feet                                         ruff     the collar of fur round the neck          chest  the front of the chest (a bib)
#   muzzle   the sides and top of the muzzle                  jaw      the lower jaw                             ears   the ears                   tip   the tail's tip
#   tail_under  the underside of the tail                     blaze    a stripe up the forehead and muzzle       brows  two spots over the eyes (a part of its own, None = none)
# pattern: "plain", "stripes" (brindle) or "merle" (dark blotches)
SKINS = {
    "black_tan":   {"body": "black", "under": "tan", "legs": "tan", "sock": "tan", "ruff": "black", "chest": "tan", "muzzle": "tan", "jaw": "tan", "ears": "black", "tip": None, "tail_under": "tan",
                        "blaze": None, "brows": "tan", "pattern": "plain", "label": "a black and tan shepherd cross"},
    "brown_white": {"body": "brown_coat", "under": W, "legs": W, "sock": W, "ruff": W, "chest": W, "muzzle": "brown_coat", "jaw": W, "ears": "brown_coat", "tip": W, "tail_under": "brown_coat",
                        "blaze": W, "brows": None, "pattern": "plain", "label": "a brown and white collie"},
    "grey_merle":  {"body": "grey_cat", "under": W, "legs": "grey_cat", "sock": W, "ruff": W, "chest": W, "muzzle": "grey_cat", "jaw": W, "ears": "black", "tip": W, "tail_under": "grey_cat",
                        "blaze": W, "brows": "tan", "pattern": "merle", "label": "a blue merle collie"},
    "yellow":      {"body": "golden", "under": "cream", "legs": "golden", "sock": "cream", "ruff": "golden", "chest": "cream", "muzzle": "golden", "jaw": "cream", "ears": "tan", "tip": None,
                        "tail_under": "cream", "blaze": None, "brows": None, "pattern": "plain", "label": "a plain yellow farm dog"},
    "brindle":     {"body": "tan", "under": "cream", "legs": "tan", "sock": W, "ruff": "tan", "chest": W, "muzzle": "dark_brown", "jaw": "dark_brown", "ears": "dark_brown", "tip": None,
                        "tail_under": "tan", "blaze": None, "brows": None, "pattern": "stripes", "label": "a brindle cattle dog"},
}
DEFAULT_SKIN = "black_tan"


_BODY_Z0 = 0.26
SADDLE, PATCHES, PATCH, TAIL_TOP = "saddle", "patches", "patch", "tail_top"     # the coat keys of the breeds' patterns (make_breed, BREED_SKINS)


def _blotches(c):
    return _blobs(c, [(0.06, -0.12, 0.42, 0.05), (-0.07, 0.0, 0.43, 0.06), (0.07, 0.10, 0.40, 0.05), (-0.06, 0.24, 0.40, 0.05),
                      (0.0, -0.02, 0.46, 0.04), (-0.04, 0.32, 0.38, 0.04), (0.08, -0.20, 0.40, 0.04)]) > 0.45


def _stripes(c):
    return math.sin((c.y * 62.0 + c.z * 40.0 + abs(c.x) * 25.0)) > 0.35


def _pattern(sk, c, saddle=True, stripes=True):
    """The colour the coat's pattern puts at c, or None (saddle, stripes: whether that pattern may show there)."""
    pattern = sk["pattern"]
    if pattern == "stripes" and stripes and _stripes(c):
        return "dark_brown"
    if pattern in ("merle", PATCHES) and _blotches(c):
        return "black" if pattern == "merle" else sk[PATCH]
    if pattern == SADDLE and saddle and c.z > sk.get("saddle_z", 0.445) and -0.24 < c.y < 0.30:
        return sk[SADDLE]                                       # a dark blanket over the back (a shepherd's, a beagle's)
    return None


def _farm_coat(sk, c, n):
    if c.z < 0.075:
        return sk["sock"]
    if c.z < _BODY_Z0 - 0.01:                                       # a leg
        return sk["legs"]
    low = c.z - (0.40 if c.y < -0.05 else 0.39)                   # how far below the centre line the face is
    if c.y < -0.16 and abs(c.x) < 0.075 and ((low < -0.04 and n.y < -0.2) or (c.y < -0.28 and n.y < -0.9)):
        return sk["chest"]                                       # the front of the chest: its underside and the breast (the body's front cap)
    if n.z < -0.45 or low < -0.085:
        return sk["under"]
    return _pattern(sk, c) or sk["body"]


def _farm_head_coat(sk, head, c, n, to_collie):
    if c.y > head[1][0] + 0.01:                                   # the neck
        return _farm_coat(sk, to_collie(c), n)
    if c.y < head[-1][0] + 0.03 and n.y < -0.4:
        return "black"                                            # the nose
    if sk["blaze"] and abs(c.x) < 0.03 and n.z > 0.7 and c.y < head[3][0] + 0.01:
        return sk["blaze"]                                        # a blaze up the forehead and the muzzle (the two faces on the crown: the head's top vertex is on its middle line, so their centres are off it)
    if c.y < head[4][0] and (n.z < -0.30 or c.z < head[5][1] - 0.012):
        return sk["jaw"]                                          # the lower jaw: a lighter line along the underside of the muzzle
    if c.y < head[4][0] - 0.01:
        return sk["muzzle"]
    return _pattern(sk, c, saddle=False, stripes=c.y > head[3][0] - 0.03) or sk["body"]


def _farm_tail_coat(sk, c, n, tip_at=None):
    """tip_at: (y, z, radius) of the tail's tip for a tail that is not carried low (the tip is what is within the radius of it); None = below 0.21 m."""
    if sk["tip"] and (c.z < 0.21 if tip_at is None else math.hypot(c.y - tip_at[0], c.z - tip_at[1]) < tip_at[2]):
        return sk["tip"]
    if n.z < -0.25 or n.y < -0.4:
        return sk["tail_under"]
    if sk["pattern"] == "stripes" and _stripes(c):
        return "dark_brown"
    return sk.get(TAIL_TOP) or sk["body"]


def _ear_rings(cm, kind, s, st, zb, k):
    """The rings one ear is lofted through (s: -1 right, 1 left; zb: the height of its base; k: its size factor) for an ear of this kind."""
    skull, ear_x = st.skull, st.ear_x
    ey = skull[0]
    if kind == "up":                                              # an upright triangle, set close together (k: a shepherd's are bigger)
        return [cm.ring_z(zb, s * ear_x * 0.80, ey + 0.012, 0.036 * k, 0.018 * k, n=4),
                cm.ring_z(zb + 0.055 * k, s * ear_x * 0.86, ey + 0.004, 0.027 * k, 0.013 * k, n=4),
                cm.ring_z(zb + 0.115 * k, s * ear_x * 0.92, ey - 0.004, 0.009 * k, 0.006 * k, n=4)]
    if kind in ("drop", "long"):                                  # a hanging flap from inside the crown down the outside of the cheek (a long one hangs below the jaw)
        out, ln = skull[2] + 0.010 * k, k * (1.6 if kind == "long" else 1.0)     # the flap stands just off the cheek, the widest ring of the head
        return [cm.ring_z(zb, s * ear_x * 0.85, ey + 0.004, 0.012 * k, 0.026 * k, n=4),
                cm.ring_z(zb - 0.045 * ln, s * (out + 0.002 * k), ey - 0.002, 0.007 * k, 0.034 * k, n=4),
                cm.ring_z(zb - 0.095 * ln, s * (out + 0.006 * k), ey - 0.006, 0.006 * k, 0.030 * k, n=4),
                cm.ring_z(zb - 0.125 * ln, s * (out + 0.006 * k), ey - 0.008, 0.004 * k, 0.016 * k, n=4)]
    if kind == "rose":                                            # a small flap folded back and out from the top of the skull (a bulldog's)
        return [cm.ring_z(zb, s * ear_x * 0.88, ey + 0.010 * k, 0.022 * k, 0.016 * k, n=4),
                cm.ring_z(zb + 0.022 * k, s * ear_x * 1.10, ey + 0.022 * k, 0.018 * k, 0.012 * k, n=4),
                cm.ring_z(zb + 0.030 * k, s * ear_x * 1.28, ey + 0.036 * k, 0.006 * k, 0.006 * k, n=4)]
    # a collie's half-folded ear: upright for most of its height and then tipped forward
    return [cm.ring_z(zb, s * ear_x * 0.78, ey + 0.010, 0.028, 0.015, n=4),
            cm.ring_z(zb + 0.062, s * ear_x * 0.88, ey + 0.006, 0.025, 0.013, n=4),
            cm.ring_z(zb + 0.105, s * ear_x * 1.00, ey - 0.020, 0.012, 0.008, n=4)]


def _farm_ears(ctx, st):
    """The ears: lofted up from inside the sides of the crown."""
    cm, shape, skull, sk = ctx.common, st.shape, st.skull, st.sk
    zb = skull[1] + skull[3] - 0.034
    kind, k = shape.get("ears"), shape.get("ear_k", 1.0)
    ctx.make("ears", lambda bm: [cm.loft(bm, _ear_rings(cm, kind, s, st, zb, k)) for s in (-1, 1)], lambda c, n: sk["ears"], ["Ear_L", "Ear_R"],
             sub=0, smooth=False)


def _farm_haunches(ctx, st):
    """A haunch over each hind leg and a shoulder over each front leg."""
    cm, hind_leg, front_leg, sk, drop, thick = ctx.common, st.hind_leg, st.front_leg, st.sk, st.drop, st.thick
    # a haunch over the top of each hind leg and a shoulder over each front leg: the legs' top rings are the old collie's, and the body above them is slimmer, so a blob
    # lofted from inside the body down to the leg's own top ring fills the join (skinned to the body bone and the leg's upper bone: the clips slide the upper bones along the body, and the top of the blob must stay with the body while its bottom follows the leg)
    for kind, leg_, top, wide, inset in (("hind", hind_leg, 0.385 - drop, 0.038 * thick, 0.026), ("front", front_leg, 0.375 - drop, 0.05 * thick, 0.008)):
        for s in (-1, 1):
            side = "R" if s < 0 else "L"
            ring0 = leg_["profile"][0]
            rings = [cm.ring_z(top, s * (leg_["x"] - inset), leg_["y"] - 0.005, wide, ring0[3] + 0.015, n=6),
                     cm.ring_z(ring0[0], s * leg_["x"], leg_["y"] + ring0[1], ring0[2], ring0[3], n=6)]
            blob = ctx.make(f"{'haunch' if kind == 'hind' else 'shoulder'}_{side.lower()}", lambda bm, r=rings: cm.loft(bm, r), lambda c, n: sk["body"],
                            ["Hips" if kind == "hind" else "Chest", f"{kind.capitalize()}Upper_{side}"], sub=0, smooth=False)
            # the weights by height, not by distance: the top of the blob (inside the body) is the body bone's alone and the bottom (the leg's own top ring) the leg's alone, with a
            # smooth blend between, so a clip that slides the leg's upper bone along the body (the dogs' walk, trot and run) drags the bottom of the blob and not its top
            body_bone, leg_bone = blob.vertex_groups[0].name, blob.vertex_groups[1].name
            z0 = ring0[0]
            for v in blob.data.vertices:
                t = min(max((v.co.z - z0) / (top - z0), 0.0), 1.0)
                t = t * t * (3.0 - 2.0 * t)
                blob.vertex_groups[body_bone].add([v.index], t, "REPLACE")
                blob.vertex_groups[leg_bone].add([v.index], 1.0 - t, "REPLACE")


def _farm_nose_and_ruff(ctx, st):
    """The nose pad at the tip of the muzzle and the ruff of fur round the neck."""
    cm, head, shape, sk = ctx.common, st.head, st.shape, st.sk
    # the nose: a black pad at the tip
    tip = head[-1]
    pad = shape.get("nose_k", 1.0)
    ctx.make("nose", lambda bm: cm.add_box(bm, (0, tip[0] - 0.004, tip[1] + 0.004), (0.050 * pad, 0.032 * pad, 0.036 * pad), taper=0.9),
             lambda c, n: "black", ["Head"], sub=0, smooth=False)

    # the ruff: a collar of fur round the base of the neck, a little proud of it (None: a short-coated dog has none). It is drawn for the collie's neck (root at y -0.24,
    # z 0.50) and moved and scaled with the breed's (st.neck: the root's y and z, the head's scale, the neck's width factor)
    rw = shape.get("ruff", 1.0)
    if rw is None:
        return
    ny, nz, nk, nw = st.neck
    rings = [cm.ring_y(ny + (y + 0.24) * nk, 0, nz + (z - 0.50) * nk, hw * rw * nk * nw, hh * rw * nk, n=8)
             for y, z, hw, hh in ((-0.215, 0.500, 0.088, 0.118), (-0.275, 0.525, 0.078, 0.104), (-0.335, 0.560, 0.072, 0.095))]
    ctx.make("ruff", lambda bm: cm.loft(bm, rings), lambda c, n: sk["ruff"], ["Chest", "Neck1", "Neck2"], sub=0, smooth=False)


def _farm_eyes(ctx, st):
    """The eyes, pupils and glints; returns (y, cz, r, w) for the brows."""
    import quadruped_builder as qb
    head = st.head
    # the eyes: dark, set into the front of the skull and looking forward, each with a small highlight
    y = head[4][0] + 0.018
    z, w, h = qb._head_at(head, y)
    r = 0.0145
    cz = z + 0.30 * h
    cx = qb._surface_x(ctx, y, cz, 0.8 * w) - 0.50 * r
    dx, dy = 0.55, 0.83                                           # the way they look: forward and a little out
    ctx.make("eyes", lambda bm: [qb._ball(bm, (s * cx, y, cz), r, n=6) for s in (-1, 1)], lambda c, n: "dark_brown", ["Head"], sub=0, smooth=False)
    ctx.make("pupils", lambda bm: [qb._ball(bm, (s * (cx + dx * 0.55 * r), y - dy * 0.55 * r, cz), 0.62 * r, n=6) for s in (-1, 1)],
             lambda c, n: "black", ["Head"], sub=0, smooth=False)
    ctx.make("glints", lambda bm: [qb._ball(bm, (s * (cx + dx * 0.95 * r), y - dy * 0.55 * r - 0.003, cz + 0.45 * r), 0.22 * r, n=4) for s in (-1, 1)],
             lambda c, n: W, ["Head"], sub=0, smooth=False)

    return y, cz, r, w


def _farm_lips_and_brows(ctx, st, y, cz, r, w):
    """The lip line along the muzzle and the two spots over the eyes."""
    import quadruped_builder as qb
    cm, head, sk = ctx.common, st.head, st.sk
    # the lip line: a thin dark line along each side of the muzzle, from the nose back to under the eye
    def lips(bm):
        n0, n1 = head[-1][0], head[5][0] + 0.03
        for yy0, yy1 in ((n0 + (n1 - n0) * i / 3, n0 + (n1 - n0) * (i + 1) / 3) for i in range(3)):
            ym = 0.5 * (yy0 + yy1)
            zz, ww, hh = qb._head_at(head, ym)
            for s in (-1, 1):
                xs = qb._surface_x(ctx, ym, zz - 0.18 * hh, ww) - 0.002
                cm.add_box(bm, (s * xs, ym, zz - 0.18 * hh), (0.006, abs(yy1 - yy0) + 0.003, 0.004))
    ctx.make("lips", lips, lambda c, n: "black", ["Head"], sub=0, smooth=False)


    # two small spots over the eyes (a black and tan dog's "eyebrows"). Every coat has the part, in the head's own colour when it has no spots, so that all the coats are
    # one mesh (the same vertices and bones) and the game can swap one for another
    def brows(bm):
        for s in (-1, 1):
            xs = qb._surface_x(ctx, y - 0.005, cz + 1.9 * r, w) - 0.003
            cm.add_box(bm, (s * xs, y - 0.004, cz + 1.9 * r), (0.008, 0.018, 0.012))
    ctx.make("brows", brows, lambda c, n: sk["brows"] or sk["body"], ["Head"], sub=0, smooth=False)


def _farm_extras(st, ctx):
    _farm_ears(ctx, st)
    _farm_haunches(ctx, st)
    _farm_nose_and_ruff(ctx, st)
    y, cz, r, w = _farm_eyes(ctx, st)
    _farm_lips_and_brows(ctx, st, y, cz, r, w)


# ---- the collie's body: y runs front (negative) to back, z is the height of the section's centre, then its half width and half height (metres; shoulder height 0.53)
_COLLIE_BODY = [(-0.30, 0.375, 0.078, 0.098),       # the front of the chest
                (-0.22, 0.392, 0.112, 0.138),       # the deep chest: 0.27 m from the withers to the breastbone
                (-0.10, 0.394, 0.112, 0.138),
                (0.03, 0.404, 0.092, 0.100),        # the tucked waist: the belly rises to 0.30 m
                (0.17, 0.396, 0.097, 0.112),        # the hips
                (0.30, 0.382, 0.082, 0.100),
                (0.35, 0.372, 0.055, 0.075)]
# ---- the head: neck, skull, stop, long muzzle; y, centre height, half width, half height
_COLLIE_HEAD = [(-0.24, 0.500, 0.074, 0.105),       # the base of the neck
                (-0.31, 0.545, 0.066, 0.092),
                (-0.36, 0.580, 0.062, 0.082),       # the back of the skull
                (-0.41, 0.588, 0.063, 0.074),       # the widest: the cheeks (the head from the cheeks to the nose is 35 % of the trunk; docs/assets/briefs/animals.md)
                (-0.47, 0.572, 0.055, 0.062),       # the stop
                (-0.52, 0.552, 0.046, 0.054),       # the muzzle starts narrow
                (-0.58, 0.541, 0.042, 0.050),
                (-0.635, 0.533, 0.038, 0.045)]      # the nose
# ---- the tail: hangs from the rump, bushy in the middle, a hook forward at the tip (height, y, radius)
_COLLIE_TAIL = [(0.395, 0.335, 0.026), (0.325, 0.415, 0.036), (0.235, 0.475, 0.042), (0.150, 0.470, 0.027)]


def make_farm_dog(name, skin=DEFAULT_SKIN, shape=None):
    """shape: optional overrides for another dog on the same builder (the husky, the breeds of make_breed): body, head, tail (the section lists: _COLLIE_BODY, _COLLIE_HEAD, _COLLIE_TAIL above), front_x and hind_x (the
    legs' distance from the middle), ears ("fold": the collie's half-folded ear, "up": an upright triangle, "drop", "long": hanging flaps, "rose": a small flap folded back) and
    ear_k (their size), ruff (the collar's width factor, None for none), leg (the legs' height to the elbow, 0.22), length and width (factors on the legs' positions), thick (on
    the legs' girth), neck ((y, z, scale, width) of the head's root, for the ruff), tip_at (see _farm_tail_coat) and size (the rig's scale: the whole dog drawn at the
    collie's size and scaled to the breed's)."""
    sk = SKINS[skin] if isinstance(skin, str) else skin
    shape = shape or {}
    body, head = _COLLIE_BODY, _COLLIE_HEAD
    # ---- the legs' profiles: the old collie's (the removed make_dog, leg=0.22)
    leg, ly, wx, thick = shape.get("leg", 0.22), shape.get("length", 1.0), shape.get("width", 1.0), shape.get("thick", 1.0)
    kz = (leg + 0.06) / 0.36
    fr = [(z * kz, dy, hx * thick, hy * thick) for z, dy, hx, hy in
          [(0.36, 0.00, 0.04, 0.05), (0.22, 0.00, 0.03, 0.035), (0.12, 0.00, 0.026, 0.03), (0.05, -0.004, 0.027, 0.034), (0.0, -0.024, 0.034, 0.056)]]   # a paw that is longer than it is wide
    hn = [(z * kz, dy, hx * thick, hy * thick) for z, dy, hx, hy in
          [(0.38, 0.00, 0.055, 0.07), (0.26, 0.03, 0.035, 0.045), (0.17, 0.06, 0.026, 0.03), (0.09, 0.03, 0.024, 0.028),
           (0.04, 0.01, 0.025, 0.03), (0.0, 0.0, 0.03, 0.045)]]
    body, head, tail = shape.get("body", body), shape.get("head", head), shape.get("tail", _COLLIE_TAIL)
    front_leg = {"x": shape.get("front_x", 0.068 * wx), "y": -0.17 * ly, "joints": (1, 3), "profile": fr}
    hind_leg = {"x": shape.get("hind_x", 0.078 * wx), "y": 0.22 * ly, "joints": (2, 4), "profile": hn}
    skull = head[3]
    ear_x = skull[2] * 0.85
    drop = 0.22 - leg                                             # how much lower the body is than the collie's
    st = SimpleNamespace(sk=sk, shape=shape, head=head, skull=skull, ear_x=ear_x, front_leg=front_leg, hind_leg=hind_leg, drop=drop, thick=thick,
                         neck=shape.get("neck", (-0.24, 0.50, 1.0, 1.0)))
    if "leg" in shape or "length" in shape or "width" in shape:   # a breed: its coat is worked out where the point would be on the collie
        def to_collie(c):
            top = leg + 0.06                                      # the legs' top ring: below it the leg is squashed, above it the body is lowered
            z = c.z * 0.28 / top if c.z < top else c.z + drop
            return SimpleNamespace(x=c.x / wx, y=c.y / ly, z=z)
    else:
        def to_collie(c):
            return c
    tip_at = shape.get("tip_at")

    return {
        "name": name, "body": body, "head": head,
        "front": front_leg, "hind": hind_leg,
        "tail": tail, "ear_x": ear_x, "ear_y": skull[0], "ear_z": skull[1] + skull[3] * 0.72,
        "coat": lambda c, n: _farm_coat(sk, to_collie(c), n), "head_coat": lambda c, n: _farm_head_coat(sk, head, c, n, to_collie),
        "tail_coat": lambda c, n: _farm_tail_coat(sk, c if tip_at else to_collie(c), n, tip_at),
        "body_n": 8, "head_n": 8, "tail_n": 6, "uv_jitter": True, "scale": shape.get("size", 1.0),                 # (see quadruped_builder._jitter_uvs: every coat keeps the same vertex count)
        "extras": lambda ctx: _farm_extras(st, ctx)}


# ---- the husky: the same builder with its own numbers. A compact northern dog, 0.55 m at the shoulder: the same deep chest as the farm dog but broader (a thick coat), a head
# a little broader, with a fuller, blunter muzzle, small erect triangular ears set close, a full ruff and a brush tail curled over the back. Its coat is grey above and white below,
# with a white mask (muzzle, jaw, blaze and brows). Docs/assets/briefs/animals.md.
HUSKY_SKIN = {"body": "grey_cat", "under": W, "legs": W, "sock": W, "ruff": "grey_cat", "chest": W, "muzzle": W, "jaw": W, "ears": "black", "tip": None, "tail_under": W,
                  "blaze": W, "brows": W, "pattern": "plain", "label": "a grey and white husky"}
HUSKY_SHAPE = {
    "body": [(-0.30, 0.380, 0.084, 0.100), (-0.22, 0.396, 0.120, 0.140), (-0.10, 0.398, 0.120, 0.140), (0.03, 0.405, 0.100, 0.104),
          (0.17, 0.398, 0.104, 0.115), (0.28, 0.385, 0.088, 0.100), (0.32, 0.375, 0.060, 0.076)],
    "head": [(-0.24, 0.500, 0.084, 0.108), (-0.31, 0.545, 0.074, 0.094), (-0.36, 0.578, 0.070, 0.082), (-0.41, 0.585, 0.071, 0.076),
          (-0.46, 0.570, 0.064, 0.066), (-0.50, 0.548, 0.054, 0.060), (-0.565, 0.538, 0.050, 0.055), (-0.625, 0.530, 0.045, 0.050)],
    "tail": [(0.395, 0.310, 0.034), (0.470, 0.385, 0.050), (0.545, 0.365, 0.050), (0.580, 0.290, 0.038)],           # up and over the back
    "front_x": 0.076, "hind_x": 0.086, "ears": "up", "ruff": 1.12}


def make_husky(name="DogHusky"):
    return make_farm_dog(name, HUSKY_SKIN, HUSKY_SHAPE)


# ---- the other breeds (issue #125): the same builder, the collie's sections moved and scaled. A breed is drawn at about the collie's size (legs lowered by `leg`, the body
# stretched by `length`, `width` and `depth`, the head by `head`, `head_w` and `snout`) and its rig is scaled to its real size (`size`). Docs/assets/briefs/animals.md has their numbers.
def make_breed(name, skin, size, leg=0.22, length=1.0, width=1.0, depth=1.0, head=1.0, head_w=1.0, snout=1.0, neck_w=1.0, thick=1.0,  # NOSONAR
               ears="drop", ear_k=1.0, tail=None, tip_at=None, ruff=None, body_w=None, neck_len=1.0, head_low=0.0, nose_k=1.0):
    """skin: a coat dict like SKINS' (with "saddle" for the saddle pattern, "patch" for patches, optionally "tail_top"); leg: the height to the elbow before scaling (the
    collie's 0.22); body_w: a width factor per body section (a bulldog is wider at the chest than the hips); tail: (height, y, radius) points as drawn for the collie's rump,
    moved with it; tip_at: (y, height, radius) of the tail's tip as drawn, for a coloured tip on a tail carried up; ruff: the collar's width factor or None; neck_len: the
    neck's length factor (the head comes back towards the shoulders) and head_low how far the head is carried lower (a bulldog's sits on its shoulders); nose_k: the nose pad's size."""
    drop = 0.22 - leg
    bw = body_w or (1.0,) * len(_COLLIE_BODY)
    body = [(y * length, z - drop, w * width * k, h * depth) for (y, z, w, h), k in zip(_COLLIE_BODY, bw)]
    ny, nz = -0.30 * length + 0.06, 0.50 - drop - head_low       # the neck's root, 6 cm behind the front of the chest as on the collie
    hd = []
    for i, (y, z, w, h) in enumerate(_COLLIE_HEAD):
        dy = y + 0.24 if i <= 4 else (-0.47 + 0.24) + (y + 0.47) * snout       # the muzzle (in front of the stop, ring 4) is scaled on its own
        if i:
            dy += (1.0 - neck_len) * 0.07                         # ring 1 is 7 cm in front of the neck's root on the collie
        hd.append((ny + dy * head, nz + (z - 0.50) * head, w * head * (neck_w if i < 2 else head_w), h * head))
    rear = 0.35 * (length - 1)
    shape = {"body": body, "head": hd, "tail": [(z - drop, y + rear, r) for z, y, r in (tail or _COLLIE_TAIL)], "leg": leg, "length": length, "width": width,
             "thick": thick, "ears": ears, "ear_k": ear_k, "ruff": ruff, "neck": (ny, nz, head, neck_w), "size": size, "nose_k": nose_k}
    if tip_at:
        shape["tip_at"] = (tip_at[0] + rear, tip_at[1] - drop, tip_at[2])
    return make_farm_dog(name, skin, shape)


BREED_SKINS = {
    "retriever": {"body": "golden", "under": "golden", "legs": "golden", "sock": "golden", "ruff": "golden", "chest": "golden", "muzzle": "golden", "jaw": "golden",
                      "ears": "golden", "tip": None, "tail_under": "cream", "blaze": None, "brows": None, "pattern": "plain", "label": "a golden retriever"},
    "shepherd": {"body": "tan", SADDLE: "black", "saddle_z": 0.40, TAIL_TOP: "black", "under": "tan", "legs": "tan", "sock": "tan", "ruff": "tan", "chest": "tan", "muzzle": "black",
                     "jaw": "tan", "ears": "black", "tip": None, "tail_under": "tan", "blaze": None, "brows": None, "pattern": SADDLE, "label": "a black and tan shepherd"},
    "beagle": {"body": "tan", SADDLE: "black", TAIL_TOP: "black", "under": W, "legs": W, "sock": W, "ruff": W, "chest": W, "muzzle": W, "jaw": W, "ears": "tan",
                   "tip": W, "tail_under": W, "blaze": W, "brows": None, "pattern": SADDLE, "label": "a tricolour beagle"},
    "dachshund": {"body": "dark_brown", "under": "dark_brown", "legs": "dark_brown", "sock": "dark_brown", "ruff": "dark_brown", "chest": "dark_brown",
                      "muzzle": "dark_brown", "jaw": "dark_brown", "ears": "dark_brown", "tip": None, "tail_under": "dark_brown", "blaze": None, "brows": None,
                      "pattern": "plain", "label": "a chocolate dachshund"},
    "bulldog": {"body": W, PATCH: "tan", "under": W, "legs": W, "sock": W, "ruff": W, "chest": W, "muzzle": W, "jaw": W, "ears": "tan", "tip": None, "tail_under": W,
                    "blaze": None, "brows": None, "pattern": PATCHES, "label": "a fawn and white bulldog"},
    "stray": {"body": "tan", PATCH: "dark_brown", "under": "cream", "legs": "tan", "sock": "cream", "ruff": "tan", "chest": "cream", "muzzle": "tan", "jaw": "cream",
                  "ears": "dark_brown", "tip": "cream", "tail_under": "tan", "blaze": None, "brows": None, "pattern": PATCHES, "label": "a tan mongrel with dark patches"},
}
