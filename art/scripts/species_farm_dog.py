"""The farm dog (issue #275): a medium collie / shepherd cross that reads as a dog at a glance, in five coats.

    make_farm_dog("DogCollie", "black_tan")  ->  a species dict for quadruped_builder.py (see species.py for the format)
    SKINS                                    ->  the five coats: black_tan, brown_white, grey_merle, yellow, brindle

The farm's first dog looked like a sheep with a dark face (the owner's play-test): a tube of a body as deep as a barrel, the head a plain continuation of the neck,
ears flat on top of it, a stub of a tail, and a black back over a white belly. This one is built from the real animal (docs/art/animal-notes.md, "Farm dog"):

    * a **deep, keeled chest** (0.28 m) reaching forward of the front legs, **a tucked loin** (the belly at 0.32 m) and a croup that falls to the tail (issue #125's rework:
      the sections follow a border collie's side profile, `_COLLIE_BODY`)
    * a **neck** that leaves the top of the chest forward and up at about 45 degrees into **a skull with a stop** and a muzzle about as long as the skull, a nose and a
      lip line, the lower jaw in a lighter colour
    * **half-folded ears** (an upright base, the tips folded forward), set on the crown at the sides of the skull
    * a **ruff** of fur round the neck, a **medium coat** (no wool: the colour only changes at the markings) and a **tail** carried low with a hook in its tip
    * **legs that start inside the body**: the front from a shoulder joint with the upper arm's muscle a little proud of the chest, the hind from the hip with a thigh, the
      stifle forward and the hock back (`_COLLIE_FRONT`, `_COLLIE_HIND`)
    * **dark eyes with a highlight**, set in the front of the skull, looking forward

The gait clips are fitted to a leg of 0.28 m (`gait_leg`, the old collie's), so their speeds are as before the rework. The husky and the other breeds are `make_breed` on
the same numbers. Every coat is the same mesh (the same vertices, the same bones) with the faces painted differently, so the game can swap one for another on a dog that is
already in the scene (`DogSkin`).
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


_ELBOW, _STIFLE = 0.25, 0.28            # the collie's elbow and stifle heights: a breed's legs are squashed below them and its body lowered above them
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
    if c.z < _ELBOW - 0.01:                                         # a leg below the elbow and the stifle (the upper arm and thigh are the body's colour)
        return sk["legs"]
    low = c.z - (0.395 if c.y < -0.05 else 0.42)                  # how far below the centre line the face is
    if c.y < -0.18 and abs(c.x) < 0.075 and ((low < -0.04 and n.y < -0.2) or (c.y < -0.31 and n.y < -0.9)):
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


def _farm_nose_and_ruff(ctx, st):
    """The nose pad at the tip of the muzzle and the ruff of fur round the neck."""
    cm, head, shape, sk = ctx.common, st.head, st.shape, st.sk
    # the nose: a black pad at the tip
    tip = head[-1]
    pad = shape.get("nose_k", 1.0)
    ctx.make("nose", lambda bm: cm.add_box(bm, (0, tip[0] - 0.004, tip[1] + 0.004), (0.050 * pad, 0.032 * pad, 0.036 * pad), taper=0.9),
             lambda c, n: "black", ["Head"], sub=0, smooth=False)

    # the ruff: a collar of fur round the base of the neck, a little proud of it (None: a short-coated dog has none). It is drawn for the collie's neck (_NECK_ROOT) and moved
    # and scaled with the breed's (st.neck: the root's y and z, the head's scale, the neck's width factor)
    rw = shape.get("ruff", 1.0)
    if rw is None:
        return
    ny, nz, nk, nw = st.neck
    y0, z0 = _NECK_ROOT
    rings = [cm.ring_y(ny + (y - y0) * nk, 0, nz + (z - z0) * nk, hw * rw * nk * nw, hh * rw * nk, n=8)
             for y, z, hw, hh in ((-0.25, 0.445, 0.090, 0.118), (-0.30, 0.480, 0.082, 0.108), (-0.35, 0.530, 0.074, 0.096))]
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
    _farm_nose_and_ruff(ctx, st)
    y, cz, r, w = _farm_eyes(ctx, st)
    _farm_lips_and_brows(ctx, st, y, cz, r, w)


def _tb(y, top, bottom, w):
    """A section given by its top and bottom heights: (y, centre height, half width, half height)."""
    return (y, (top + bottom) / 2, w, (top - bottom) / 2)


# ---- the collie (issue #125's rework): a border collie's side profile, 0.535 m to the withers. The back is highest over the shoulders and slopes a little to a croup that
# falls to the tail; the chest is deep (0.28 m) and reaches forward of the front legs, its underside a keel (the sections' lower halves narrowed by _COLLIE_BODY_KEEL); behind
# the ribs the belly tucks up to 0.32 m. y, top, bottom, half width (metres)
_COLLIE_BODY = [_tb(y, top, bottom, w) for y, top, bottom, w in (
    (-0.34, 0.470, 0.340, 0.060),       # the point of the breastbone, forward of the front legs
    (-0.303, 0.510, 0.280, 0.085),
    (-0.230, 0.535, 0.255, 0.105),       # the withers over the deepest chest
    (-0.138, 0.530, 0.260, 0.112),
    (-0.046, 0.520, 0.280, 0.105),       # the end of the rib cage
    (0.046, 0.515, 0.320, 0.088),        # the loin, the belly tucked up
    (0.120, 0.520, 0.330, 0.092),
    (0.194, 0.515, 0.330, 0.098),        # the hips
    (0.258, 0.500, 0.350, 0.088),        # the croup falls away
    (0.299, 0.475, 0.390, 0.050))]
_COLLIE_BODY_KEEL = [0.20, 0.35, 0.45, 0.45, 0.40, 0.25, 0.15, 0.10, 0.10, 0.0]
# ---- the neck leaves the top of the chest forward and up at about 45 degrees (not up out of the back) into a skull with a stop and a long muzzle; the lower halves narrow to
# the throat and the jaw
_NECK_ROOT = (-0.27, 0.44)
_COLLIE_HEAD = [_tb(y, top, bottom, w) for y, top, bottom, w in (
    (-0.27, 0.540, 0.340, 0.078),       # the root of the neck, inside the top of the chest
    (-0.33, 0.585, 0.415, 0.068),
    (-0.38, 0.635, 0.475, 0.062),       # the back of the skull
    (-0.42, 0.655, 0.505, 0.064),       # the skull at the ears, the widest (the cheeks)
    (-0.465, 0.645, 0.505, 0.058),      # the forehead
    (-0.495, 0.615, 0.505, 0.050),      # the stop: the top steps down to the muzzle
    (-0.55, 0.598, 0.508, 0.046),
    (-0.605, 0.590, 0.512, 0.042),
    (-0.635, 0.585, 0.518, 0.035))]     # the nose
_COLLIE_HEAD_KEEL = [0.25, 0.20, 0.15, 0.20, 0.25, 0.25, 0.20, 0.15, 0.10]
_STOP = 5                                # the head's ring at the stop: the muzzle in front of it is scaled on its own (make_breed's snout)
# ---- the legs (z, dy, half width, half depth, dx): the front leg from the shoulder joint inside the chest, the upper arm's muscle (a little proud of the chest), the elbow
# under the chest, the forearm, the pastern and a paw longer than it is wide; the hind leg from the hip joint, the thigh, the stifle (forward), the shin back to the hock and the
# cannon down to the foot. Their joints: the front's elbow (2) and pastern (4), the hind's stifle (2) and hock (4)
_COLLIE_FRONT = [(0.44, 0.030, 0.045, 0.060, -0.030), (0.34, 0.025, 0.036, 0.058), (0.25, 0.010, 0.031, 0.040), (0.13, 0.000, 0.026, 0.030),
                 (0.05, -0.004, 0.027, 0.034), (0.0, -0.024, 0.034, 0.056)]
_COLLIE_HIND = [(0.48, 0.000, 0.050, 0.070, -0.030), (0.38, -0.005, 0.046, 0.078), (0.28, -0.035, 0.035, 0.045), (0.19, 0.010, 0.028, 0.032),
                (0.12, 0.050, 0.025, 0.028), (0.05, 0.030, 0.025, 0.030), (0.0, 0.030, 0.030, 0.045)]
# ---- the tail: set on at the end of the croup, bushy in the middle, a hook forward at the tip (height, y, radius)
_COLLIE_TAIL = [(0.460, 0.295, 0.026), (0.380, 0.365, 0.036), (0.280, 0.420, 0.042), (0.190, 0.425, 0.027)]


def _legs(profile, ref, drop, thick):
    """A leg profile on a breed's legs: the rings above `ref` (the elbow or stifle, inside or beside the body) move down with the body by `drop`, the ones below are squashed
    to fit, and every ring's girth is times `thick`."""
    k = (ref - drop) / ref
    return [(r[0] - drop if r[0] > ref else r[0] * k, r[1], r[2] * thick, r[3] * thick, *r[4:]) for r in profile]


def make_farm_dog(name, skin=DEFAULT_SKIN, shape=None):
    """shape: optional overrides for another dog on the same builder (the husky, the breeds of make_breed): body, head, tail (the section lists: _COLLIE_BODY, _COLLIE_HEAD, _COLLIE_TAIL above), front_x and hind_x (the
    legs' distance from the middle), ears ("fold": the collie's half-folded ear, "up": an upright triangle, "drop", "long": hanging flaps, "rose": a small flap folded back) and
    ear_k (their size), ruff (the collar's width factor, None for none), leg (the legs' height to the elbow, 0.22), length and width (factors on the legs' positions), thick (on
    the legs' girth), neck ((y, z, scale, width) of the head's root, for the ruff), tip_at (see _farm_tail_coat) and size (the rig's scale: the whole dog drawn at the
    collie's size and scaled to the breed's)."""
    sk = SKINS[skin] if isinstance(skin, str) else skin
    shape = shape or {}
    leg, ly, wx, thick = shape.get("leg", _ELBOW), shape.get("length", 1.0), shape.get("width", 1.0), shape.get("thick", 1.0)
    drop = _ELBOW - leg                                           # how much lower the body is than the collie's
    body, head, tail = shape.get("body", _COLLIE_BODY), shape.get("head", _COLLIE_HEAD), shape.get("tail", _COLLIE_TAIL)
    front_leg = {"x": 0.064 * wx, "y": -0.195 * ly, "joints": (2, 4), "profile": _legs(_COLLIE_FRONT, _ELBOW, drop, thick)}
    hind_leg = {"x": 0.062 * wx, "y": 0.175 * ly, "joints": (2, 4), "profile": _legs(_COLLIE_HIND, _STIFLE, drop, thick)}
    skull = head[3]
    ear_x = skull[2] * 0.85
    st = SimpleNamespace(sk=sk, shape=shape, head=head, skull=skull, ear_x=ear_x, front_leg=front_leg, hind_leg=hind_leg, drop=drop, thick=thick,
                         neck=shape.get("neck", (*_NECK_ROOT, 1.0, 1.0)))
    if drop or ly != 1.0 or wx != 1.0:                            # a breed: its coat is worked out where the point would be on the collie
        def to_collie(c):
            z = c.z * _ELBOW / leg if c.z < leg else c.z + drop   # below the elbow the leg is squashed, above it the body is lowered
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
        "body_keel": _COLLIE_BODY_KEEL, "head_keel": _COLLIE_HEAD_KEEL,
        "body_n": 10, "head_n": 8, "leg_n": 6, "tail_n": 6, "uv_jitter": True, "scale": shape.get("size", 1.0),
        "gait_leg": leg + 0.03,                                   # the gait's leg length as before the rework (0.28 m for the collie: its speeds stay as they were)                 # (see quadruped_builder._jitter_uvs: every coat keeps the same vertex count)
        "extras": lambda ctx: _farm_extras(st, ctx)}


# ---- the husky: the same builder with its own numbers. A compact northern dog, 0.55 m at the shoulder: the same deep chest as the farm dog but broader (a thick coat), a head
# a little broader, with a fuller, blunter muzzle, small erect triangular ears set close, a full ruff and a brush tail curled over the back. Its coat is grey above and white below,
# with a white mask (muzzle, jaw, blaze and brows). Docs/assets/briefs/animals.md.
HUSKY_SKIN = {"body": "grey_cat", "under": W, "legs": W, "sock": W, "ruff": "grey_cat", "chest": W, "muzzle": W, "jaw": W, "ears": "black", "tip": None, "tail_under": W,
                  "blaze": W, "brows": W, "pattern": "plain", "label": "a grey and white husky"}
def make_husky(name="DogHusky"):
    """The husky: the collie's build a little broader and heavier (a thick coat), a broader head with a blunter muzzle, upright ears, a full ruff and a tail curled over the back."""
    return make_breed(name, HUSKY_SKIN, size=1.0, width=1.08, head_w=1.05, snout=0.92, neck_w=1.08, thick=1.05, ears="up", ruff=1.12,
                      tail=[(0.460, 0.270, 0.034), (0.535, 0.340, 0.050), (0.610, 0.320, 0.050), (0.645, 0.245, 0.038)])


# ---- the other breeds (issue #125): the same builder, the collie's sections moved and scaled. A breed is drawn at about the collie's size (legs lowered by `leg`, the body
# stretched by `length`, `width` and `depth`, the head by `head`, `head_w` and `snout`) and its rig is scaled to its real size (`size`). Docs/assets/briefs/animals.md has their numbers.
def make_breed(name, skin, size, leg=_ELBOW, length=1.0, width=1.0, depth=1.0, head=1.0, head_w=1.0, snout=1.0, neck_w=1.0, thick=1.0,  # NOSONAR
               ears="drop", ear_k=1.0, tail=None, tip_at=None, ruff=None, body_w=None, neck_len=1.0, head_low=0.0, nose_k=1.0):
    """skin: a coat dict like SKINS' (with "saddle" for the saddle pattern, "patch" for patches, optionally "tail_top"); leg: the height to the elbow before scaling (the
    collie's 0.25); body_w: a width factor per body section (a bulldog is wider at the chest than the hips); tail: (height, y, radius) points as drawn for the collie's rump,
    moved with it; tip_at: (y, height, radius) of the tail's tip as drawn, for a coloured tip on a tail carried up; ruff: the collar's width factor or None; neck_len: the
    neck's length factor (the head comes back towards the shoulders) and head_low how far the head is carried lower (a bulldog's sits on its shoulders); nose_k: the nose pad's size."""
    drop = _ELBOW - leg
    bw = body_w or (1.0,) * len(_COLLIE_BODY)
    if len(bw) != len(_COLLIE_BODY):
        raise ValueError(f"{name}: {len(bw)} body_w factors for {len(_COLLIE_BODY)} body sections")
    body = [(y * length, z - drop, w * width * k, h * depth) for (y, z, w, h), k in zip(_COLLIE_BODY, bw)]
    y0, z0 = _NECK_ROOT
    ny, nz = y0 + _COLLIE_BODY[0][0] * (length - 1), z0 - drop - head_low       # the neck's root keeps its place behind the front of the chest
    stop = _COLLIE_HEAD[_STOP][0]
    hd = []
    for i, (y, z, w, h) in enumerate(_COLLIE_HEAD):
        dy = y - y0 if i <= _STOP else (stop - y0) + (y - stop) * snout       # the muzzle (in front of the stop) is scaled on its own
        if i:
            dy += (1.0 - neck_len) * (y0 - _COLLIE_HEAD[1][0])    # a shorter neck brings the head back towards the root
        hd.append((ny + dy * head, nz + (z - z0) * head, w * head * (neck_w if i < 2 else head_w), h * head))
    rear = _COLLIE_BODY[-1][0] * (length - 1)
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
