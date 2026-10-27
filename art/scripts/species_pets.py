"""Dogs and cats as parameter sets: one generator each, many breeds and coats.

    DOGS = {"dog_collie": ..., "dog_retriever": ..., ...}   (species_farm_dog.make_farm_dog, make_husky and make_breed)
    make_cat(...)  and  CATS = {"cat_tabby": ..., "cat_black": ..., ...}

Each is a species dict for quadruped_builder.py (see species.py for the format). A cat's size, coat pattern, tail, head and eyes are
arguments of make_cat, a breed's body, legs, head, ears, tail and coat those of species_farm_dog.make_breed, so a new one is one line.
Sizes are real-world: a collie stands about 0.55 m at the shoulder, a house cat about 0.25 m.
"""

import math
from functools import partial
from types import SimpleNamespace

import species_farm_dog


def _blobs(c, blobs):
    return sum(math.exp(-((c.x - x) ** 2 + (c.y - y) ** 2 + (c.z - z) ** 2) / (2 * s * s)) for x, y, z, s in blobs)


# ===== Dogs ====================================================================================================
# The collie and the husky are species_farm_dog's farm dog and husky; the other breeds are species_farm_dog.make_breed on the same builder (issue #125: the old
# simple dog generator, make_dog, failed every proportion of the brief).
# Back heights in metres (docs/assets/briefs/animals.md): collie 0.53, retriever 0.58, beagle 0.38, bulldog 0.39, dachshund 0.22, husky 0.54, shepherd 0.62, stray 0.47
DOGS = {
    "dog_collie":    species_farm_dog.make_farm_dog("DogCollie", species_farm_dog.DEFAULT_SKIN),   # the farm dog (issue #275): its own shape and coats, see species_farm_dog.py
    "dog_retriever": species_farm_dog.make_breed("DogRetriever", species_farm_dog.BREED_SKINS["retriever"], size=1.09, length=1.05, width=1.12, head=1.03,
                                                 head_w=1.12, snout=0.95, neck_w=1.1, thick=1.1, ear_k=1.1,
                                                 tail=[(0.395, 0.335, 0.030), (0.330, 0.400, 0.036), (0.250, 0.440, 0.032), (0.170, 0.455, 0.020)]),
    "dog_beagle":    species_farm_dog.make_breed("DogBeagle", species_farm_dog.BREED_SKINS["beagle"], size=0.74, leg=0.20, width=1.08, head=1.08,
                                                 snout=0.9, thick=1.05, ears="long",
                                                 tail=[(0.400, 0.335, 0.024), (0.470, 0.370, 0.026), (0.550, 0.385, 0.024), (0.620, 0.375, 0.018)], tip_at=(0.375, 0.62, 0.05)),
    "dog_bulldog":   species_farm_dog.make_breed("DogBulldog", species_farm_dog.BREED_SKINS["bulldog"], size=0.88, leg=0.12, length=0.82, width=1.45, depth=1.05,
                                                 body_w=(1.15, 1.1, 1.05, 1.0, 0.85, 0.8, 0.8), head=1.15, head_w=1.45, snout=0.35, neck_w=1.4, thick=1.35, neck_len=0.3, head_low=0.07, nose_k=0.8,
                                                 ears="rose", ear_k=1.1, tail=[(0.385, 0.335, 0.030), (0.370, 0.360, 0.030), (0.350, 0.375, 0.025), (0.330, 0.380, 0.015)]),
    "dog_dachshund": species_farm_dog.make_breed("DogDachshund", species_farm_dog.BREED_SKINS["dachshund"], size=0.58, leg=0.07, length=1.1, width=0.95,
                                                 depth=0.92, head=1.05, snout=1.25, thick=1.1, ears="long",
                                                 tail=[(0.380, 0.335, 0.028), (0.370, 0.420, 0.026), (0.340, 0.500, 0.020), (0.300, 0.560, 0.013)]),
    "dog_husky":     species_farm_dog.make_husky("DogHusky"),                                     # built on the farm dog's builder with its own numbers (issue #87)
    "dog_shepherd":  species_farm_dog.make_breed("DogShepherd", species_farm_dog.BREED_SKINS["shepherd"], size=1.165, length=1.05, head=1.05, head_w=0.98,
                                                 snout=1.1, ears="up", ear_k=1.35, ruff=0.95,
                                                 tail=[(0.395, 0.335, 0.030), (0.310, 0.400, 0.042), (0.210, 0.440, 0.045), (0.130, 0.450, 0.030)]),
    "dog_stray":     species_farm_dog.make_breed("DogStray", species_farm_dog.BREED_SKINS["stray"], size=0.88, ears="fold"),
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
        cm.add_box(bm, (s * skull[2] * 0.7, skull[0] + 0.005 * d.k, skull[1] + skull[3] * 0.85), (0.045 * d.k * d.hk, 0.016 * d.k * d.hk, 0.06 * d.k * d.hk),
                   taper=0.2, rot_deg=(0, s * 10, 0))


def _cat_extras(d, ctx):
    cm = ctx.common
    ctx.make("ears", partial(_cat_ears, cm, d), lambda c, n: d.c3 if d.pattern in ("siamese", "tuxedo") else d.c1, ["Ear_L", "Ear_R"], sub=0, smooth=False)
    ctx.make("nose", lambda bm: cm.add_box(bm, (0, d.head[-1][0], d.head[-1][1] + 0.004), (0.014 * d.k, 0.012 * d.k, 0.012 * d.k)),
             lambda c, n: "pink", ["Head"], sub=0, smooth=False)


def make_cat(name, size=1.0, pattern="solid", c1="orange_cat", c2="paint_white", c3="dark_brown", tail_len=1.0, fluff=1.0, head_k=1.0, eye=0.24):  # NOSONAR
    """A house cat, 0.27 m to the back (about 0.25 at the shoulder). Patterns: solid, tabby, tuxedo, calico, siamese.
    head_k scales the head about the root of the neck (a kitten's head is large for its body), eye is the eyes' size factor."""
    k = size
    cz0 = 0.19 * k                                         # the centre line of the barrel; the back is 0.27 m, the chest hangs to 0.115 m (docs/assets/briefs/animals.md)
    body = [(yy * k, cz0 + dz * k, ww * k * fluff, hh * k * fluff) for yy, dz, ww, hh in
            [(-0.17, -0.005, 0.045, 0.055), (-0.12, 0.0, 0.068, 0.075), (-0.02, 0.005, 0.075, 0.075), (0.07, 0.003, 0.063, 0.068),
             (0.15, 0.014, 0.066, 0.072), (0.19, -0.01, 0.045, 0.058)]]
    head = [(yy * k, dz * k, hw * k, hh * k) for yy, dz, hw, hh in                 # neck root first; the skull (ring 2) carries the ears, the cheeks (3) are the widest
            [(-0.13, 0.215, 0.060, 0.070), (-0.18, 0.255, 0.054, 0.064), (-0.222, 0.272, 0.052, 0.058), (-0.250, 0.270, 0.053, 0.058),
             (-0.285, 0.256, 0.052, 0.050), (-0.312, 0.245, 0.040, 0.038), (-0.326, 0.240, 0.030, 0.030), (-0.332, 0.237, 0.024, 0.024)]]
    if not math.isclose(head_k, 1.0):                                      # the neck root (ring 0) stays inside the shoulders; the rest grows about it
        y0, z0 = head[0][:2]
        head = head[:1] + [(y0 + (y - y0) * head_k, z0 + (z - z0) * head_k, w * head_k, h * head_k) for y, z, w, h in head[1:]]
    fr = [(z * k, dy * k, hx * k, hy * k) for z, dy, hx, hy in
          [(0.20, 0, 0.028, 0.036), (0.12, 0, 0.021, 0.026), (0.06, 0, 0.017, 0.021), (0.03, 0, 0.015, 0.02), (0.0, -0.014, 0.024, 0.03)]]
    hn = [(z * k, dy * k, hx * k, hy * k) for z, dy, hx, hy in
          [(0.215, 0, 0.040, 0.055), (0.14, 0.03, 0.026, 0.034), (0.09, 0.045, 0.02, 0.024), (0.05, 0.03, 0.016, 0.02), (0.02, 0.01, 0.015, 0.02), (0.0, -0.01, 0.024, 0.03)]]
    tl = [(z * k, y * k * tail_len, r * k) for z, y, r in ((0.20, 0.17, 0.020), (0.25, 0.235, 0.018), (0.31, 0.26, 0.016), (0.37, 0.245, 0.014))]
    skull = head[2]
    d = SimpleNamespace(k=k, hk=head_k, cz0=cz0, pattern=pattern, c1=c1, c2=c2, c3=c3, head=head, skull=skull)

    return {"name": name, "body": body, "head": head,
                "front": {"x": 0.046 * k, "y": -0.12 * k, "joints": (1, 3), "profile": fr},
                "hind": {"x": 0.046 * k, "y": 0.14 * k, "joints": (2, 4), "profile": hn},
                "tail": tl, "ear_x": skull[2] * 0.7, "ear_y": skull[0], "ear_z": skull[1] + skull[3] * 0.9,
                "coat": lambda c, n: _cat_coat(d, c), "head_coat": lambda c, n: _cat_head_coat(d, c, n),
                "tail_coat": lambda c, n: c3 if pattern in ("siamese", "tuxedo") else c1,
                "eyes": {"gap": 0.22, "inset": 0.55, "up": 0.34, "forward": 0.85, "size": eye}, "eye_colour": "paint_yellow",     # round, golden, looking ahead
                "extras": lambda ctx: _cat_extras(d, ctx)}


CATS = {
    "cat_tabby":   make_cat("CatTabby", pattern="tabby", c1="orange_cat", c3="rust"),
    "cat_black":   make_cat("CatBlack", pattern="solid", c1="black"),
    "cat_orange":  make_cat("CatOrange", pattern="solid", c1="orange_cat"),
    "cat_tuxedo":  make_cat("CatTuxedo", pattern="tuxedo", c1="black", c2="paint_white", c3="black"),
    "cat_calico":  make_cat("CatCalico", pattern="calico", c1="orange_cat", c2="paint_white", c3="black"),
    "cat_siamese": make_cat("CatSiamese", pattern="siamese", c1="cream", c3="dark_brown", size=1.05),
    "cat_grey":    make_cat("CatGrey", pattern="solid", c1="grey_cat", fluff=1.1),
    "cat_kitten":  make_cat("CatKitten", pattern="tabby", c1="cream", c3="tan", size=0.55, tail_len=0.9, head_k=1.15, eye=0.30),   # a big head and eyes
}
