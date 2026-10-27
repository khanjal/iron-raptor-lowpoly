"""Dogs and cats as parameter sets: one generator each, many breeds and coats.

    make_dog(...)  and  DOGS = {"dog_collie": ..., "dog_retriever": ..., ...}
    make_cat(...)  and  CATS = {"cat_tabby": ..., "cat_black": ..., ...}

Each returns a species dict for quadruped_builder.py (see species.py for the format). Body length, width and depth, leg
length, head size, snout length, ear type, tail type and the coat pattern are arguments, so a new breed is one line.
Sizes are real-world: a collie stands about 0.55 m at the shoulder, a house cat about 0.25 m.
"""

import math
from functools import partial
from types import SimpleNamespace

import species_farm_dog


def _blobs(c, blobs):
    return sum(math.exp(-((c.x - x) ** 2 + (c.y - y) ** 2 + (c.z - z) ** 2) / (2 * s * s)) for x, y, z, s in blobs)


# ===== Dogs ====================================================================================================
_DOG_TWO_TONE = ("bicolor", "tri", "mask", "saddle")


def _dog_saddle(d, c, h):
    """Shepherd: tan with a dark saddle."""
    return d.c1 if (h > 0.05 * d.sz and abs(c.x) < 0.10 * d.sx and abs(c.y) < 0.20 * d.sy) else d.c3


def _dog_tri(d, c, h):
    """Beagle: white below, tan sides, dark back."""
    if h < -0.03:
        return d.c2
    return d.c1 if (h > 0.06 * d.sz and abs(c.y) < 0.2 * d.sy) else d.c3


# how each pattern paints the body, by the height h of the face above the barrel's centre line; "solid" and any other pattern is c1
_DOG_COATS = {
    "bicolor": lambda d, c, h: d.c1 if h > -0.02 else d.c2,        # collie: dark above, light below
    "saddle": _dog_saddle,
    "tri": _dog_tri,
    "mask": lambda d, c, h: d.c1 if h > 0.0 else d.c2,             # husky: grey back, white below
    "patches": lambda d, c, h: d.c1 if _blobs(c, [(0.08, 0.0, d.cz0 + 0.1, 0.1), (-0.07, 0.15 * d.sy, d.cz0, 0.08)]) > 0.5 else d.c3,   # stray: tan with a few darker patches
}

# the head's own colouring for the patterns that have one (the rest use the body's)
_DOG_HEAD_COATS = {
    "bicolor": lambda d, c, n: d.c2 if (abs(c.x) < 0.02 and n.z > 0.3) else d.c1,
    "mask": lambda d, c, n: d.c2 if c.z < d.hd[3][1] - 0.01 else d.c1,
    "saddle": lambda d, c, n: d.c1 if c.y < d.hd[4][0] and n.z > 0.2 else d.c3,
    "tri": lambda d, c, n: d.c3,
}


def _dog_coat(d, c):
    h = c.z - d.cz0
    if c.z < 0.045 * (d.leg / 0.30 + 0.3):
        return d.c2 if d.pattern in _DOG_TWO_TONE else d.c1
    paint = _DOG_COATS.get(d.pattern)
    return paint(d, c, h) if paint else d.c1


def _dog_head_coat(d, c, n):
    if c.y < d.hd[-2][0]:
        return d.nose
    paint = _DOG_HEAD_COATS.get(d.pattern)
    return paint(d, c, n) if paint else _dog_coat(d, c)


def _dog_tail_coat(d, c):
    if d.pattern == "bicolor" and c.z < d.cz0 - 0.1:
        return d.c2
    return d.c3 if d.pattern == "tri" else d.c1


def _ears_upright(cm, d, ey, ez, bm):
    for s in (-1, 1):
        cm.add_box(bm, (s * d.ear_x * 0.8, ey + 0.01, ez + d.skull[3] * 0.9), (0.05 * d.head, 0.03 * d.head, 0.11 * d.head), taper=0.25)


def _ears_rose(cm, d, ey, ez, bm):
    for s in (-1, 1):
        cm.add_box(bm, (s * d.ear_x * 0.95, ey - 0.005, ez + d.skull[3] * 0.55), (0.045 * d.head, 0.05 * d.head, 0.045 * d.head),
                   rot_deg=(15, 0, s * 25), taper=0.5)


def _ears_floppy(cm, d, ey, ez, long_, bm):
    for s in (-1, 1):
        cm.add_box(bm, (s * d.ear_x * 0.85, ey, ez + d.skull[3] * 0.3 - 0.05 * long_), (0.02 * d.head, 0.075 * d.head, 0.12 * d.head * long_),
                   rot_deg=(0, s * 10, 0), taper=0.8)


def _dog_extras(d, ctx):
    cm = ctx.common
    ey, ez = d.skull[0], d.skull[1]
    if d.ear == "upright":
        ears = partial(_ears_upright, cm, d, ey, ez)
    elif d.ear == "rose":
        ears = partial(_ears_rose, cm, d, ey, ez)
    else:
        ears = partial(_ears_floppy, cm, d, ey, ez, 1.6 if d.ear == "long" else 1.0)
    ctx.make("ears", ears, lambda c, n: d.c1 if d.pattern != "tri" else d.c3, ["Ear_L", "Ear_R"], sub=0, smooth=False)
    ctx.make("nose", lambda bm: cm.add_box(bm, (0, d.hd[-1][0] - 0.005, d.hd[-1][1] + 0.005), (0.03 * d.head, 0.02, 0.025 * d.head)),
             lambda c, n: "black", ["Head"], sub=0, smooth=False)


# the options of a breed, all but the name with defaults and passed by keyword (a parameter object would change every breed's line)
def make_dog(name, length=1.0, width=1.0, depth=1.0, leg=0.30, head=1.0, head_w=1.0, snout=1.0, ear="floppy", tail="down",  # NOSONAR
             thick=1.0, pattern="bicolor", c1="black", c2="paint_white", c3="tan", nose="black"):
    """A dog. length/width/depth scale the barrel (1.0 = collie), leg is the leg height in metres, snout the muzzle
    length factor, ear is floppy | long | upright | rose, tail is down | up | curl | stub, pattern picks the coat.
    Shoulder height is about leg + 0.31 * depth metres."""
    sy, sx, sz = length, width, depth
    cz0 = leg + 0.14 * sz
    body = [(yy * sy, cz0 + dz, ww * sx, hh * sz) for yy, dz, ww, hh in
            [(-0.28, -0.01, 0.10, 0.13), (-0.16, 0.01, 0.14, 0.17), (0.0, 0.0, 0.15, 0.17), (0.16, 0.01, 0.13, 0.15), (0.28, 0.0, 0.09, 0.12)]]
    y_neck = -0.26 * sy
    base = [(-0.26, 0.09, 0.09, 0.12), (-0.34, 0.14, 0.08, 0.11), (-0.40, 0.16, 0.075, 0.10), (-0.44, 0.15, 0.08, 0.095),
            (-0.52, 0.11, 0.05, 0.065), (-0.58, 0.095, 0.045, 0.055), (-0.62, 0.09, 0.045, 0.05), (-0.64, 0.09, 0.035, 0.04)]
    hd = []
    for i, (yy, dz, hw, hh) in enumerate(base):
        if i < 4:
            y = y_neck + (yy + 0.26) * head
        else:                                              # the muzzle's length is scaled separately from the skull's
            y = y_neck + (-0.44 + 0.26) * head + (yy + 0.44) * head * snout
        hd.append((y, cz0 + 0.09 * sz + (dz - 0.09) * head, hw * head * head_w, hh * head))
    kz = (leg + 0.06) / 0.36
    fr = [(z * kz, dy, hx * thick, hy * thick) for z, dy, hx, hy in
          [(0.36, 0.00, 0.04, 0.05), (0.22, 0.00, 0.03, 0.035), (0.12, 0.00, 0.024, 0.028), (0.05, 0.00, 0.025, 0.03), (0.0, -0.01, 0.03, 0.045)]]
    hn = [(z * kz, dy, hx * thick, hy * thick) for z, dy, hx, hy in
          [(0.38, 0.00, 0.055, 0.07), (0.26, 0.03, 0.035, 0.045), (0.17, 0.06, 0.026, 0.03), (0.09, 0.03, 0.024, 0.028),
           (0.04, 0.01, 0.025, 0.03), (0.0, 0.0, 0.03, 0.045)]]
    tails = {"down": [(0.06, 0.28), (0.02, 0.35), (-0.06, 0.40), (-0.14, 0.41)], "up": [(0.05, 0.28), (0.12, 0.34), (0.20, 0.37), (0.25, 0.36)],
             "curl": [(0.05, 0.28), (0.14, 0.32), (0.20, 0.30), (0.18, 0.24)], "stub": [(0.04, 0.28), (0.07, 0.31), (0.08, 0.33), (0.08, 0.34)]}[tail]
    tl = [(cz0 + dz, y * sy, r) for (dz, y), r in zip(tails, (0.025, 0.03, 0.035, 0.02))]

    skull = hd[3]                                          # y, z, half width, half height of the ring the ears sit on
    ear_x = skull[2] * 0.95
    d = SimpleNamespace(leg=leg, pattern=pattern, c1=c1, c2=c2, c3=c3, nose=nose, sx=sx, sy=sy, sz=sz, cz0=cz0, hd=hd, skull=skull, ear=ear, ear_x=ear_x, head=head)

    return {
        "name": name, "body": body, "head": hd,
        "front": {"x": 0.065 * sx, "y": -0.18 * sy, "joints": (1, 3), "profile": fr},
        "hind": {"x": 0.065 * sx, "y": 0.20 * sy, "joints": (2, 4), "profile": hn},
        "tail": tl, "ear_x": ear_x, "ear_y": skull[0], "ear_z": skull[1] + skull[3] * 0.5,
        "coat": lambda c, n: _dog_coat(d, c), "head_coat": lambda c, n: _dog_head_coat(d, c, n),
        "tail_coat": lambda c, n: _dog_tail_coat(d, c),
        "eyes": {"gap": 0.20, "inset": 0.55, "up": 0.34, "forward": 0.80, "size": 0.19},                  # a dog's eyes face forward, towards the nose
        "extras": lambda ctx: _dog_extras(d, ctx)}


# Shoulder heights in metres: collie 0.53, retriever 0.58, beagle 0.38, bulldog 0.42, dachshund 0.28, husky 0.55, shepherd 0.60, stray 0.46
DOGS = {
    "dog_collie":    species_farm_dog.make_farm_dog("DogCollie", species_farm_dog.DEFAULT_SKIN),   # the farm dog (issue #275): its own shape and coats, see species_farm_dog.py
    "dog_retriever": make_dog("DogRetriever", length=1.15, width=1.15, depth=1.1, leg=0.24, head=1.1, ear="floppy", tail="down",
                              pattern="solid", c1="golden", thick=1.15),
    "dog_beagle":    make_dog("DogBeagle", length=0.95, depth=0.9, leg=0.10, head=1.0, ear="long", tail="up", pattern="tri",
                              c1="dark_brown", c2="paint_white", c3="tan", thick=0.9),
    "dog_bulldog":   make_dog("DogBulldog", length=0.85, width=1.45, depth=1.1, leg=0.08, head=1.25, head_w=1.25, snout=0.45,
                              ear="rose", tail="stub", pattern="solid", c1="cream", thick=1.35),
    "dog_dachshund": make_dog("DogDachshund", length=1.5, width=0.8, depth=0.78, leg=0.08, head=0.85, snout=1.15, ear="long",
                              tail="down", pattern="solid", c1="dark_brown", thick=0.75),
    "dog_husky":     species_farm_dog.make_husky("DogHusky"),                                     # built on the farm dog's builder with its own numbers (issue #87)
    "dog_shepherd":  make_dog("DogShepherd", length=1.2, width=1.1, depth=1.1, leg=0.26, head=1.1, snout=1.1, ear="upright",
                              tail="down", pattern="saddle", c1="black", c3="tan", thick=1.1),
    "dog_stray":     make_dog("DogStray", length=0.9, width=0.9, depth=0.95, leg=0.17, ear="floppy", tail="down",
                              pattern="patches", c1="dark_brown", c3="tan", thick=0.9),
}


# The farm dog's other coats (issue #275): the same mesh with the faces painted differently, one FBX each (GN_DogCollie<Coat>_faceted_01.fbx, the model only: the game swaps its mesh
# onto the dog that is in the scene, which keeps the one skeleton and the one set of clips). They are not in DOGS, and gn_animal_clips.py skips them: no clips are made for them.
DOG_SKINS = {
    "dog_collie_" + skin: species_farm_dog.make_farm_dog("DogCollie" + "".join(w.capitalize() for w in skin.split("_")), skin)
    for skin in species_farm_dog.SKINS if skin != species_farm_dog.DEFAULT_SKIN
}


# ===== Cats ====================================================================================================
def _cat_tabby(d, c, h):
    return d.c3 if (math.sin(c.y * 70 / d.k) > 0.25 and h > -0.02 * d.k) else d.c1


def _cat_tuxedo(d, c, h):
    """Black with a white chest, belly and paws."""
    return d.c2 if (h < -0.03 * d.k or c.z < 0.03 * d.k or (c.y < -0.05 * d.k and h < 0.03 * d.k)) else d.c1


def _cat_calico(d, c, h):
    t = _blobs(c, [(0.04 * d.k, 0.0, d.cz0 + 0.06 * d.k, 0.07 * d.k), (-0.05 * d.k, 0.14 * d.k, d.cz0 + 0.04 * d.k, 0.06 * d.k)])
    u = _blobs(c, [(-0.05 * d.k, -0.1 * d.k, d.cz0 + 0.05 * d.k, 0.06 * d.k), (0.05 * d.k, 0.17 * d.k, d.cz0 + 0.02 * d.k, 0.05 * d.k)])
    if t > 0.5:
        return d.c1
    return d.c3 if u > 0.5 else d.c2


def _cat_siamese(d, c, h):
    """Pale body, dark points."""
    return d.c3 if (c.z < 0.07 * d.k or c.y < -0.28 * d.k) else d.c1


# how each pattern paints the body; "solid" and any other pattern is c1
_CAT_COATS = {"tabby": _cat_tabby, "tuxedo": _cat_tuxedo, "calico": _cat_calico, "siamese": _cat_siamese}

# the head's own colouring for the patterns that have one (the rest use the body's)
_CAT_HEAD_COATS = {
    "siamese": lambda d, c, n: d.c3 if c.y < -0.27 * d.k else d.c1,
    "tuxedo": lambda d, c, n: d.c2 if (c.y < -0.28 * d.k and c.z < d.head[4][1] + 0.01) else d.c1,
    "tabby": lambda d, c, n: d.c3 if (abs(c.x) < 0.012 * d.k and n.z > 0.3) else d.c1,
}


def _cat_coat(d, c):
    h = c.z - d.cz0
    paint = _CAT_COATS.get(d.pattern)
    return paint(d, c, h) if paint else d.c1


def _cat_head_coat(d, c, n):
    paint = _CAT_HEAD_COATS.get(d.pattern)
    return paint(d, c, n) if paint else _cat_coat(d, c)


def _cat_ears(cm, d, bm):
    skull = d.skull
    for s in (-1, 1):
        cm.add_box(bm, (s * skull[2] * 0.7, skull[0] + 0.005 * d.k, skull[1] + skull[3] * 0.85), (0.045 * d.k, 0.016 * d.k, 0.06 * d.k),
                   taper=0.2, rot_deg=(0, s * 10, 0))


def _cat_extras(d, ctx):
    cm = ctx.common
    ctx.make("ears", partial(_cat_ears, cm, d), lambda c, n: d.c3 if d.pattern in ("siamese", "tuxedo") else d.c1, ["Ear_L", "Ear_R"], sub=0, smooth=False)
    ctx.make("nose", lambda bm: cm.add_box(bm, (0, d.head[-1][0], d.head[-1][1] + 0.004), (0.014 * d.k, 0.012 * d.k, 0.012 * d.k)),
             lambda c, n: "pink", ["Head"], sub=0, smooth=False)


def make_cat(name, size=1.0, pattern="solid", c1="orange_cat", c2="paint_white", c3="dark_brown", tail_len=1.0, fluff=1.0):
    """A house cat, 0.27 m to the back (about 0.25 at the shoulder). Patterns: solid, tabby, tuxedo, calico, siamese."""
    k = size
    cz0 = 0.19 * k                                         # the centre line of the barrel; the back is 0.27 m, the chest hangs to 0.115 m (docs/assets/briefs/animals.md)
    body = [(yy * k, cz0 + dz * k, ww * k * fluff, hh * k * fluff) for yy, dz, ww, hh in
            [(-0.17, -0.005, 0.045, 0.055), (-0.12, 0.0, 0.068, 0.075), (-0.02, 0.005, 0.075, 0.075), (0.07, 0.003, 0.063, 0.068),
             (0.15, 0.014, 0.066, 0.072), (0.19, -0.01, 0.045, 0.058)]]
    head = [(yy * k, dz * k, hw * k, hh * k) for yy, dz, hw, hh in                 # neck root first; the skull (ring 2) carries the ears, the cheeks (3) are the widest
            [(-0.13, 0.215, 0.060, 0.070), (-0.18, 0.255, 0.054, 0.064), (-0.222, 0.272, 0.052, 0.058), (-0.250, 0.270, 0.053, 0.058),
             (-0.285, 0.256, 0.052, 0.050), (-0.312, 0.245, 0.040, 0.038), (-0.326, 0.240, 0.030, 0.030), (-0.332, 0.237, 0.024, 0.024)]]
    fr = [(z * k, dy * k, hx * k, hy * k) for z, dy, hx, hy in
          [(0.20, 0, 0.028, 0.036), (0.12, 0, 0.021, 0.026), (0.06, 0, 0.017, 0.021), (0.03, 0, 0.015, 0.02), (0.0, -0.014, 0.024, 0.03)]]
    hn = [(z * k, dy * k, hx * k, hy * k) for z, dy, hx, hy in
          [(0.215, 0, 0.040, 0.055), (0.14, 0.03, 0.026, 0.034), (0.09, 0.045, 0.02, 0.024), (0.05, 0.03, 0.016, 0.02), (0.02, 0.01, 0.015, 0.02), (0.0, -0.01, 0.024, 0.03)]]
    tl = [(z * k, y * k * tail_len, r * k) for z, y, r in ((0.20, 0.17, 0.020), (0.25, 0.235, 0.018), (0.31, 0.26, 0.016), (0.37, 0.245, 0.014))]
    skull = head[2]
    d = SimpleNamespace(k=k, cz0=cz0, pattern=pattern, c1=c1, c2=c2, c3=c3, head=head, skull=skull)

    return {"name": name, "body": body, "head": head,
                "front": {"x": 0.046 * k, "y": -0.12 * k, "joints": (1, 3), "profile": fr},
                "hind": {"x": 0.046 * k, "y": 0.14 * k, "joints": (2, 4), "profile": hn},
                "tail": tl, "ear_x": skull[2] * 0.7, "ear_y": skull[0], "ear_z": skull[1] + skull[3] * 0.9,
                "coat": lambda c, n: _cat_coat(d, c), "head_coat": lambda c, n: _cat_head_coat(d, c, n),
                "tail_coat": lambda c, n: c3 if pattern in ("siamese", "tuxedo") else c1,
                "eyes": {"gap": 0.22, "inset": 0.55, "up": 0.34, "forward": 0.85, "size": 0.24}, "eye_colour": "paint_yellow",     # round, golden, looking ahead
                "extras": lambda ctx: _cat_extras(d, ctx)}


CATS = {
    "cat_tabby":   make_cat("CatTabby", pattern="tabby", c1="orange_cat", c3="rust"),
    "cat_black":   make_cat("CatBlack", pattern="solid", c1="black"),
    "cat_orange":  make_cat("CatOrange", pattern="solid", c1="orange_cat"),
    "cat_tuxedo":  make_cat("CatTuxedo", pattern="tuxedo", c1="black", c2="paint_white", c3="black"),
    "cat_calico":  make_cat("CatCalico", pattern="calico", c1="orange_cat", c2="paint_white", c3="black"),
    "cat_siamese": make_cat("CatSiamese", pattern="siamese", c1="cream", c3="dark_brown", size=1.05),
    "cat_grey":    make_cat("CatGrey", pattern="solid", c1="grey_cat", fluff=1.1),
    "cat_kitten":  make_cat("CatKitten", pattern="tabby", c1="cream", c3="tan", size=0.55, tail_len=0.9),
}
