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
# Back heights in metres (docs/assets/briefs/animals.md): collie 0.53, retriever 0.58, beagle 0.38, bulldog 0.38, dachshund 0.22, husky 0.54, shepherd 0.62, stray 0.47
DOGS = {
    "dog_collie":    species_farm_dog.make_farm_dog("DogCollie", species_farm_dog.DEFAULT_SKIN),   # the farm dog (issue #275): its own shape and coats, see species_farm_dog.py
    "dog_retriever": species_farm_dog.make_breed("DogRetriever", species_farm_dog.BREED_SKINS["retriever"], size=1.09, length=0.95, width=1.12, head=0.97,
                                                 head_w=1.12, snout=0.95, neck_w=1.1, thick=1.1, ear_k=1.1,
                                                 tail=[(0.455, 0.285, 0.030), (0.390, 0.350, 0.036), (0.310, 0.390, 0.032), (0.230, 0.405, 0.020)]),
    "dog_beagle":    species_farm_dog.make_breed("DogBeagle", species_farm_dog.BREED_SKINS["beagle"], size=0.74, leg=0.23, width=1.08, head=1.08,
                                                 snout=0.9, thick=1.05, ears="long",
                                                 tail=[(0.460, 0.285, 0.024), (0.530, 0.320, 0.026), (0.610, 0.335, 0.024), (0.680, 0.325, 0.018)], tip_at=(0.325, 0.68, 0.05)),
    "dog_bulldog":   species_farm_dog.make_breed("DogBulldog", species_farm_dog.BREED_SKINS["bulldog"], size=0.86, leg=0.15, length=0.84, width=1.45, depth=1.05,
                                                 body_w=(1.15, 1.12, 1.1, 1.06, 1.0, 0.92, 0.86, 0.82, 0.8, 0.8), head=1.05, head_w=1.5, snout=0.35, neck_w=1.4, thick=1.35, neck_len=0.3, head_low=0.07, nose_k=0.8,
                                                 ears="rose", ear_k=1.1, tail=[(0.425, 0.255, 0.030), (0.410, 0.280, 0.030), (0.390, 0.295, 0.025), (0.370, 0.300, 0.015)]),
    "dog_dachshund": species_farm_dog.make_breed("DogDachshund", species_farm_dog.BREED_SKINS["dachshund"], size=0.58, leg=0.10, length=1.1, width=0.95,
                                                 depth=0.92, head=1.05, snout=1.25, thick=1.1, ears="long",
                                                 tail=[(0.440, 0.285, 0.028), (0.430, 0.370, 0.026), (0.400, 0.450, 0.020), (0.360, 0.510, 0.013)]),
    "dog_husky":     species_farm_dog.make_husky("DogHusky"),                                     # built on the farm dog's builder with its own numbers (issue #87)
    "dog_shepherd":  species_farm_dog.make_breed("DogShepherd", species_farm_dog.BREED_SKINS["shepherd"], size=1.165, length=0.97, head=0.93, head_w=1.02,
                                                 snout=1.1, ears="up", ear_k=1.35, ruff=0.95,
                                                 tail=[(0.455, 0.285, 0.030), (0.370, 0.350, 0.042), (0.270, 0.390, 0.045), (0.190, 0.400, 0.030)]),
    "dog_stray":     species_farm_dog.make_breed("DogStray", species_farm_dog.BREED_SKINS["stray"], size=0.88, ears="fold"),
}


# The farm dog's other coats (issue #275): the same mesh with the faces painted differently, one FBX each (GN_DogCollie<Coat>_faceted_01.fbx, the model only: the game swaps its mesh
# onto the dog that is in the scene, which keeps the one skeleton and the one set of clips). They are not in DOGS, and gn_animal_clips.py skips them: no clips are made for them.
DOG_SKINS = {
    "dog_collie_" + skin: species_farm_dog.make_farm_dog("DogCollie" + "".join(w.capitalize() for w in skin.split("_")), skin)
    for skin in species_farm_dog.SKINS if skin != species_farm_dog.DEFAULT_SKIN
}


# ===== Cats ====================================================================================================
def _cat_light(d, c, h):
    """The pale blocks a low-poly cat reads by: a bib down the chest, the belly and white socks."""
    return (c.y < -0.07 * d.k and h < 0.015 * d.k) or h < -0.045 * d.k or c.z < 0.045 * d.k


def _cat_leg_coat(d, c):
    """A tabby's legs are the coat's colour down to white socks; the other patterns paint the legs as the body."""
    if d.pattern == "tabby":
        return d.c2 if c.z < 0.045 * d.k else d.c1
    return _cat_coat(d, c)


def _cat_tabby(d, c, h):
    """Colour in blocks, not stripes round the body: a pale bib, belly and socks, and two or three broad saddle stripes on the top of the back."""
    if _cat_light(d, c, h):
        return d.c2
    return d.c3 if (math.sin(c.y * 40 / d.k) > 0.35 and h > 0.035 * d.k) else d.c1


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


def _cat_tabby_head(d, c, n):
    """A tabby's face: a white muzzle below the cheeks, a dark stripe down the middle of the forehead, the rest the coat."""
    if c.y < -0.25 * d.k * d.hk and c.z < d.head[4][1] + 0.005:
        return d.c2
    if abs(c.x) < 0.014 * d.k and n.z > 0.3:
        return d.c3
    return d.c1


# how each pattern paints the body; "solid" and any other pattern is c1
_CAT_COATS = {"tabby": _cat_tabby, "tuxedo": _cat_tuxedo, "calico": _cat_calico, "siamese": _cat_siamese}

# the head's own colouring for the patterns that have one (the rest use the body's)
_CAT_HEAD_COATS = {
    "siamese": lambda d, c, n: d.c3 if c.y < -0.245 * d.k else d.c1,
    "tuxedo": lambda d, c, n: d.c2 if (c.y < -0.25 * d.k and c.z < d.head[4][1] + 0.01) else d.c1,
    "tabby": _cat_tabby_head,
}


def _cat_coat(d, c):
    h = c.z - d.cz0
    paint = _CAT_COATS.get(d.pattern)
    return paint(d, c, h) if paint else d.c1


def _cat_head_coat(d, c, n):
    paint = _CAT_HEAD_COATS.get(d.pattern)
    return paint(d, c, n) if paint else _cat_coat(d, c)


def _cat_ears(cm, d, bm):
    """Large upright ears, wide at the base and set wide on the crown, tipped a little outwards; about 1.4 times a real cat's, as low-poly cats have them."""
    skull = d.skull
    e = d.k * d.hk
    for s in (-1, 1):
        cm.add_box(bm, (s * skull[2] * 0.62, skull[0] - 0.004 * d.k, skull[1] + skull[3] * 0.80), (0.064 * e, 0.030 * e, 0.085 * e),
                   taper=0.12, rot_deg=(0, s * 14, 0))


def _cat_ear_coat(d, c, n):
    """The ear in the coat's colour all over (the pink inside is its own part, _cat_ear_inner)."""
    return d.c3 if d.pattern in ("siamese", "tuxedo") else d.c1


def _cat_ear_inner(cm, d, bm):
    """The pink inside of each ear, smaller than its front, as low-poly cats have it: the ear's forward face with its corners pulled two thirds of
    the way in towards a point a little above its middle (the ear's lower part is inside the skull), standing 0.8 mm in front of it so the two
    never share a plane."""
    import bmesh
    from mathutils import Vector
    tmp = bmesh.new()
    _cat_ears(cm, d, tmp)
    tmp.normal_update()
    for f in tmp.faces:
        if f.normal.y < -0.5:
            pts = [v.co.copy() for v in f.verts]
            centre = sum(pts, Vector()) / len(pts)
            centre.z -= (min(p.z for p in pts) - centre.z) * 0.22
            bm.faces.new([bm.verts.new(centre + (p - centre) * 0.66 + f.normal * 0.0008) for p in pts])
    tmp.free()


def _cat_extras(d, ctx):
    cm = ctx.common
    ctx.make("ears", partial(_cat_ears, cm, d), partial(_cat_ear_coat, d), ["Ear_L", "Ear_R"], sub=0, smooth=False)
    ctx.make("ear_inner", partial(_cat_ear_inner, cm, d), lambda c, n: "pink", ["Ear_L", "Ear_R"], sub=0, smooth=False)
    ctx.make("nose", lambda bm: cm.add_box(bm, (0, d.head[-1][0], d.head[-1][1] + 0.004), (0.014 * d.k, 0.012 * d.k, 0.012 * d.k)),
             lambda c, n: "pink", ["Head"], sub=0, smooth=False)


def make_cat(name, size=1.0, pattern="solid", c1="orange_cat", c2="paint_white", c3="dark_brown", tail_len=1.0, fluff=1.0, head_k=1.18, eye=0.38):  # NOSONAR
    """A house cat, 0.27 m to the back (about 0.25 at the shoulder). Patterns: solid, tabby, tuxedo, calico, siamese.
    head_k scales the head about the root of the neck (a kitten's head is large for its body), eye is the eyes' size factor.
    Stylised as low-poly cats are (docs/assets/briefs/animals.md, "Stylised"): the head 1.18 and the ears about 1.4 times real (coat-coloured, a smaller pink inside), the eyes large, thick legs ending in a paw block, the coat in blocks."""
    k = size
    cz0 = 0.19 * k                                         # the centre line of the barrel; the back is 0.27 m, the chest hangs to 0.115 m (docs/assets/briefs/animals.md)
    # a house cat's side profile (issue #125's rework): the back a shallow curve a little higher over the hips, a deep chest with a keel, the belly's loose skin low at the
    # back, the rump rounding down to the tail; y, top, bottom, half width
    body = [(yy * k, (top + bot) / 2 * k, ww * k * fluff, (top - bot) / 2 * k * fluff) for yy, top, bot, ww in
            [(-0.153, 0.235, 0.150, 0.040), (-0.126, 0.255, 0.125, 0.058), (-0.081, 0.265, 0.115, 0.068), (-0.018, 0.262, 0.118, 0.072),
             (0.045, 0.262, 0.125, 0.068), (0.099, 0.268, 0.120, 0.066), (0.144, 0.272, 0.130, 0.066), (0.180, 0.262, 0.150, 0.056), (0.2025, 0.245, 0.175, 0.035)]]
    # a short neck forward out of the chest, a round domed skull (ring 2 carries the ears, the cheeks, ring 4, are the widest), a steep short nose and whisker pads
    head = [(yy * k, (top + bot) / 2 * k, hw * k, (top - bot) / 2 * k) for yy, top, bot, hw in
            [(-0.12, 0.265, 0.165, 0.055), (-0.155, 0.290, 0.200, 0.052), (-0.185, 0.322, 0.222, 0.048), (-0.21, 0.335, 0.222, 0.050),
             (-0.235, 0.328, 0.218, 0.050), (-0.255, 0.312, 0.218, 0.046), (-0.27, 0.288, 0.222, 0.037), (-0.28, 0.272, 0.222, 0.029),
             (-0.287, 0.262, 0.228, 0.020)]]
    if not math.isclose(head_k, 1.0):                                      # the neck root (ring 0) stays inside the shoulders; the rest grows about it
        y0, z0 = head[0][:2]
        head = head[:1] + [(y0 + (y - y0) * head_k, z0 + (z - z0) * head_k, w * head_k, h * head_k) for y, z, w, h in head[1:]]
    # the legs (z, dy, half width, half depth, dx): the front from the shoulder inside the chest down a straight slim leg under it (the elbow at 2, the wrist at 3, the paw's
    # heel at 4); the hind
    # from the hip (its top ring narrower, so the leg's flat top stays inside the flank) through the thigh, the stifle forward (2), the shin back to a high hock (4) and the long foot to the paw
    fr = [(z * k, dy * k, hx * k, hy * k, dx * k) for z, dy, hx, hy, dx in
          [(0.21, 0.012, 0.032, 0.042, -0.012), (0.16, 0.010, 0.030, 0.038, 0.0), (0.11, 0.004, 0.023, 0.027, 0.0), (0.06, 0.0, 0.020, 0.024, 0.0),
           (0.025, -0.004, 0.020, 0.025, 0.0), (0.0, -0.016, 0.029, 0.039, 0.0)]]
    hn = [(z * k, dy * k, hx * k, hy * k, dx * k) for z, dy, hx, hy, dx in
          [(0.23, 0.0, 0.027, 0.050, -0.012), (0.17, -0.005, 0.038, 0.055, 0.0), (0.115, -0.030, 0.026, 0.034, 0.0), (0.09, 0.012, 0.022, 0.026, 0.0),
           (0.06, 0.040, 0.020, 0.024, 0.0), (0.02, 0.025, 0.020, 0.025, 0.0), (0.0, 0.020, 0.029, 0.039, 0.0)]]
    tl = [(z * k, y * k * tail_len, r * k) for z, y, r in ((0.215, 0.195, 0.025), (0.25, 0.24, 0.023), (0.31, 0.262, 0.020), (0.37, 0.25, 0.017))]
    skull = head[2]
    d = SimpleNamespace(k=k, hk=head_k, cz0=cz0, pattern=pattern, c1=c1, c2=c2, c3=c3, head=head, skull=skull)

    return {"name": name, "body": body, "head": head,
                "front": {"x": 0.040 * k, "y": -0.09 * k, "joints": (3, 4), "profile": fr},          # the wrist (3) folds the paw back
                "hind": {"x": 0.042 * k, "y": 0.135 * k, "joints": (2, 4), "profile": hn},
                "body_keel": [0.20, 0.30, 0.40, 0.40, 0.35, 0.20, 0.15, 0.10, 0.0], "head_keel": [0.20, 0.20, 0.15, 0.15, 0.15, 0.20, 0.25, 0.20, 0.10],
                "body_n": 10, "head_n": 8, "leg_n": 6, "gait_leg": 0.20 * k,                # the gait's leg length as before the rework (the old leg's top)
                "tail": tl, "ear_x": skull[2] * 0.7, "ear_y": skull[0], "ear_z": skull[1] + skull[3] * 0.9,
                "coat": lambda c, n: _cat_coat(d, c), "leg_coat": lambda c, n: _cat_leg_coat(d, c), "head_coat": lambda c, n: _cat_head_coat(d, c, n),
                "tail_coat": lambda c, n: c3 if pattern in ("siamese", "tuxedo") else c1,
                "eyes": {"gap": 0.40, "inset": 0.55, "up": 0.30, "forward": 0.85, "size": eye}, "eye_colour": "paint_yellow",     # round, golden, looking ahead
                "extras": lambda ctx: _cat_extras(d, ctx)}


CATS = {
    "cat_tabby":   make_cat("CatTabby", pattern="tabby", c1="orange_cat", c3="rust"),
    "cat_black":   make_cat("CatBlack", pattern="solid", c1="black"),
    "cat_orange":  make_cat("CatOrange", pattern="solid", c1="orange_cat"),
    "cat_tuxedo":  make_cat("CatTuxedo", pattern="tuxedo", c1="black", c2="paint_white", c3="black"),
    "cat_calico":  make_cat("CatCalico", pattern="calico", c1="orange_cat", c2="paint_white", c3="black"),
    "cat_siamese": make_cat("CatSiamese", pattern="siamese", c1="cream", c3="dark_brown", size=1.05),
    "cat_grey":    make_cat("CatGrey", pattern="solid", c1="grey_cat", fluff=1.1),
    "cat_kitten":  make_cat("CatKitten", pattern="tabby", c1="cream", c3="tan", size=0.55, tail_len=0.9, head_k=1.32, eye=0.46),   # a big head and eyes
}
