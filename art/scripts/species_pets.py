"""Dogs and cats as parameter sets: one generator each, many breeds and coats.

    make_dog(...)  and  DOGS = {"dog_collie": ..., "dog_retriever": ..., ...}
    make_cat(...)  and  CATS = {"cat_tabby": ..., "cat_black": ..., ...}

Each returns a species dict for quadruped_builder.py (see species.py for the format). Body length, width and depth, leg
length, head size, snout length, ear type, tail type and the coat pattern are arguments, so a new breed is one line.
Sizes are real-world: a collie stands about 0.55 m at the shoulder, a house cat about 0.25 m.
"""

import math

import species_farm_dog


def _blobs(c, blobs):
    return sum(math.exp(-((c.x - x) ** 2 + (c.y - y) ** 2 + (c.z - z) ** 2) / (2 * s * s)) for x, y, z, s in blobs)


# ===== Dogs ====================================================================================================
def make_dog(name, length=1.0, width=1.0, depth=1.0, leg=0.30, head=1.0, head_w=1.0, snout=1.0, ear="floppy", tail="down",
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

    def coat(c, n):
        h = c.z - cz0
        if c.z < 0.045 * (leg / 0.30 + 0.3):
            return c2 if pattern in ("bicolor", "tri", "mask", "saddle") else c1
        if pattern == "solid":
            return c1
        if pattern == "bicolor":                           # collie: dark above, light below
            return c1 if h > -0.02 else c2
        if pattern == "saddle":                            # shepherd: tan with a dark saddle
            return c1 if (h > 0.05 * sz and abs(c.x) < 0.10 * sx and abs(c.y) < 0.20 * sy) else c3
        if pattern == "tri":                               # beagle: white below, tan sides, dark back
            if h < -0.03:
                return c2
            return c1 if (h > 0.06 * sz and abs(c.y) < 0.2 * sy) else c3
        if pattern == "mask":                              # husky: grey back, white below
            return c1 if h > 0.0 else c2
        if pattern == "patches":                           # stray: tan with a few darker patches
            return c1 if _blobs(c, [(0.08, 0.0, cz0 + 0.1, 0.1), (-0.07, 0.15 * sy, cz0, 0.08)]) > 0.5 else c3
        return c1

    def head_coat(c, n):
        if c.y < hd[-2][0]:
            return nose
        if pattern == "bicolor":
            return c2 if (abs(c.x) < 0.02 and n.z > 0.3) else c1
        if pattern == "mask":
            return c2 if c.z < hd[3][1] - 0.01 else c1
        if pattern == "saddle":
            return c1 if c.y < hd[4][0] and n.z > 0.2 else c3
        if pattern == "tri":
            return c3
        return coat(c, n)

    def extras(ctx):
        cm = ctx.common
        ey, ez = skull[0], skull[1]
        if ear == "upright":
            def ears(bm):
                for s in (-1, 1):
                    cm.add_box(bm, (s * ear_x * 0.8, ey + 0.01, ez + skull[3] * 0.9), (0.05 * head, 0.03 * head, 0.11 * head), taper=0.25)
        elif ear == "rose":
            def ears(bm):
                for s in (-1, 1):
                    cm.add_box(bm, (s * ear_x * 0.95, ey - 0.005, ez + skull[3] * 0.55), (0.045 * head, 0.05 * head, 0.045 * head),
                               rot_deg=(15, 0, s * 25), taper=0.5)
        else:
            long_ = 1.6 if ear == "long" else 1.0

            def ears(bm):
                for s in (-1, 1):
                    cm.add_box(bm, (s * ear_x * 0.85, ey, ez + skull[3] * 0.3 - 0.05 * long_), (0.02 * head, 0.075 * head, 0.12 * head * long_),
                               rot_deg=(0, s * 10, 0), taper=0.8)

        ctx.make("ears", ears, lambda c, n: c1 if pattern != "tri" else c3, ["Ear_L", "Ear_R"], sub=0, smooth=False)
        ctx.make("nose", lambda bm: cm.add_box(bm, (0, hd[-1][0] - 0.005, hd[-1][1] + 0.005), (0.03 * head, 0.02, 0.025 * head)),
                 lambda c, n: "black", ["Head"], sub=0, smooth=False)

    return dict(
        name=name, body=body, head=hd,
        front=dict(x=0.065 * sx, y=-0.18 * sy, joints=(1, 3), profile=fr),
        hind=dict(x=0.065 * sx, y=0.20 * sy, joints=(2, 4), profile=hn),
        tail=tl, ear_x=ear_x, ear_y=skull[0], ear_z=skull[1] + skull[3] * 0.5,
        coat=coat, head_coat=head_coat,
        tail_coat=lambda c, n: (c2 if pattern == "bicolor" and c.z < cz0 - 0.1 else (c3 if pattern == "tri" else c1)),
        eyes=dict(gap=0.20, inset=0.55, up=0.34, forward=0.80, size=0.19),                  # a dog's eyes face forward, towards the nose
        extras=extras)


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
def make_cat(name, size=1.0, pattern="solid", c1="orange_cat", c2="paint_white", c3="dark_brown", tail_len=1.0, fluff=1.0):
    """A house cat, 0.27 m to the back (about 0.25 at the shoulder). Patterns: solid, tabby, tuxedo, calico, siamese."""
    k = size
    cz0 = 0.19 * k                                         # the centre line of the barrel; the back is 0.27 m, the chest hangs to 0.115 m (docs/assets/briefs/animals.md)
    body = [(yy * k, cz0 + dz * k, ww * k * fluff, hh * k * fluff) for yy, dz, ww, hh in
            [(-0.17, -0.005, 0.045, 0.055), (-0.12, 0.0, 0.068, 0.075), (-0.02, 0.005, 0.075, 0.075), (0.07, 0.003, 0.063, 0.068),
             (0.15, 0.014, 0.066, 0.072), (0.19, -0.01, 0.045, 0.058)]]
    head = [(yy * k, dz * k, hw * k, hh * k) for yy, dz, hw, hh in                 # neck root first; the skull (ring 2) carries the ears, the cheeks (3) are the widest
            [(-0.13, 0.215, 0.060, 0.070), (-0.18, 0.255, 0.054, 0.064), (-0.222, 0.272, 0.052, 0.058), (-0.250, 0.270, 0.057, 0.058),
             (-0.285, 0.256, 0.052, 0.050), (-0.312, 0.245, 0.040, 0.038), (-0.326, 0.240, 0.030, 0.030), (-0.332, 0.237, 0.024, 0.024)]]
    fr = [(z * k, dy * k, hx * k, hy * k) for z, dy, hx, hy in
          [(0.20, 0, 0.028, 0.036), (0.12, 0, 0.021, 0.026), (0.06, 0, 0.017, 0.021), (0.03, 0, 0.015, 0.02), (0.0, -0.014, 0.024, 0.03)]]
    hn = [(z * k, dy * k, hx * k, hy * k) for z, dy, hx, hy in
          [(0.215, 0, 0.040, 0.055), (0.14, 0.03, 0.026, 0.034), (0.09, 0.045, 0.02, 0.024), (0.05, 0.03, 0.016, 0.02), (0.02, 0.01, 0.015, 0.02), (0.0, -0.01, 0.024, 0.03)]]
    tl = [(z * k, y * k * tail_len, r * k) for z, y, r in ((0.20, 0.17, 0.020), (0.25, 0.235, 0.018), (0.31, 0.26, 0.016), (0.37, 0.245, 0.014))]
    skull = head[2]

    def coat(c, n):
        h = c.z - cz0
        if pattern == "solid":
            return c1
        if pattern == "tabby":
            return c3 if (math.sin(c.y * 70 / k) > 0.25 and h > -0.02 * k) else c1
        if pattern == "tuxedo":                            # black with a white chest, belly and paws
            return c2 if (h < -0.03 * k or c.z < 0.03 * k or (c.y < -0.05 * k and h < 0.03 * k)) else c1
        if pattern == "calico":
            t = _blobs(c, [(0.04 * k, 0.0, cz0 + 0.06 * k, 0.07 * k), (-0.05 * k, 0.14 * k, cz0 + 0.04 * k, 0.06 * k)])
            u = _blobs(c, [(-0.05 * k, -0.1 * k, cz0 + 0.05 * k, 0.06 * k), (0.05 * k, 0.17 * k, cz0 + 0.02 * k, 0.05 * k)])
            return c1 if t > 0.5 else (c3 if u > 0.5 else c2)
        if pattern == "siamese":                           # pale body, dark points
            return c3 if (c.z < 0.07 * k or c.y < -0.28 * k) else c1
        return c1

    def head_coat(c, n):
        if pattern == "siamese":
            return c3 if c.y < -0.27 * k else c1
        if pattern == "tuxedo":
            return c2 if (c.y < -0.28 * k and c.z < head[4][1] + 0.01) else c1
        if pattern == "tabby":
            return c3 if (abs(c.x) < 0.012 * k and n.z > 0.3) else c1
        return coat(c, n)

    def extras(ctx):
        cm = ctx.common

        def ears(bm):
            for s in (-1, 1):
                cm.add_box(bm, (s * skull[2] * 0.7, skull[0] + 0.005 * k, skull[1] + skull[3] * 0.85), (0.045 * k, 0.016 * k, 0.06 * k),
                           taper=0.2, rot_deg=(0, s * 10, 0))

        ctx.make("ears", ears, lambda c, n: c3 if pattern in ("siamese", "tuxedo") else c1, ["Ear_L", "Ear_R"], sub=0, smooth=False)
        ctx.make("nose", lambda bm: cm.add_box(bm, (0, head[-1][0], head[-1][1] + 0.004), (0.014 * k, 0.012 * k, 0.012 * k)),
                 lambda c, n: "pink", ["Head"], sub=0, smooth=False)

    return dict(name=name, body=body, head=head,
                front=dict(x=0.046 * k, y=-0.12 * k, joints=(1, 3), profile=fr),
                hind=dict(x=0.046 * k, y=0.14 * k, joints=(2, 4), profile=hn),
                tail=tl, ear_x=skull[2] * 0.7, ear_y=skull[0], ear_z=skull[1] + skull[3] * 0.9,
                coat=coat, head_coat=head_coat,
                tail_coat=lambda c, n: c3 if pattern in ("siamese", "tuxedo") else c1,
                eyes=dict(gap=0.22, inset=0.55, up=0.34, forward=0.85, size=0.24), eye_colour="paint_yellow",     # round, golden, looking ahead
                extras=extras)


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
