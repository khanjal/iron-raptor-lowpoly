"""Wildlife species for quadruped_builder.py (see species.py for the description format): raccoon, opossum, skunk, red fox, white-tailed deer
(doe, buck, fawn) and black bear. All face -Y, Z up, feet on z = 0, sizes in metres.

The turkey is a bird: biped_bird.py (TURKEY_TOM, TURKEY_HEN).

Eyes and nostrils come from quadruped_builder (`eyes=` picks where: EYES_FRONT for the animals that look ahead, EYES_SIDE for the ones with an eye on each
side of the head); the parts audit (audit_animals.py) lists what each species must have.
"""

import math

import common
import species as sp_mod                                           # for tube(): this module is imported at the end of species.py, after tube exists

W, B = "paint_white", "black"


def _hash(x, y, z):
    """A cheap deterministic pseudo-random number in 0..1 for a point (for spots)."""
    return (math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453) % 1.0


def _box(bm, *a, **k):
    common.add_box(bm, *a, **k)


# ===== Raccoon: a chunky cat-sized animal, a black mask and a ringed tail ============================================================
def _raccoon_head(c, n):
    if c.y < -0.505:
        return B                                                       # the nose
    if abs(c.z - 0.335) < 0.024 and -0.47 < c.y < -0.30:
        return B                                                       # the mask across the eyes
    if c.y < -0.375 and c.z < 0.318:
        return W                                                       # the white muzzle and cheeks
    return "fur_grey"


def _raccoon_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.055, -0.37, 0.41), (0.045, 0.02, 0.05), taper=0.5)
    ctx.make("ears", ears, lambda c_, n: "fur_grey", ["Ear_L", "Ear_R"], sub=0, smooth=False)


RACCOON = {
    "name": "Raccoon", "scale": 0.72, "body_n": 10, "head_n": 8,                                   # real: 0.23-0.30 m at the shoulder, 0.40-0.70 m long
    "body": [(-0.26, 0.25, 0.09, 0.10), (-0.16, 0.27, 0.13, 0.14), (0.02, 0.27, 0.15, 0.15), (0.18, 0.27, 0.14, 0.14), (0.30, 0.25, 0.10, 0.10)],
    "head": [(-0.20, 0.33, 0.085, 0.10), (-0.28, 0.34, 0.080, 0.095), (-0.34, 0.34, 0.075, 0.09), (-0.38, 0.33, 0.075, 0.085),
          (-0.43, 0.31, 0.062, 0.066), (-0.47, 0.30, 0.050, 0.052), (-0.50, 0.295, 0.038, 0.04), (-0.52, 0.295, 0.028, 0.03)],
    "front": {"x": 0.06, "y": -0.16, "joints": (1, 3),
               "profile": [(0.20, 0.0, 0.04, 0.05), (0.13, 0.0, 0.03, 0.035), (0.08, 0.0, 0.025, 0.03), (0.03, -0.01, 0.028, 0.04), (0.0, -0.02, 0.03, 0.05)]},
    "hind": {"x": 0.07, "y": 0.20, "joints": (2, 4),
              "profile": [(0.22, 0.0, 0.055, 0.07), (0.16, 0.04, 0.04, 0.05), (0.10, 0.06, 0.03, 0.04), (0.05, 0.04, 0.03, 0.04), (0.02, 0.01, 0.03, 0.045),
                       (0.0, -0.01, 0.03, 0.05)]},
    "tail": [(0.25, 0.30, 0.05), (0.21, 0.40, 0.055), (0.16, 0.48, 0.055), (0.11, 0.53, 0.045), (0.07, 0.56, 0.03)],
    "ear_x": 0.055, "ear_y": -0.37, "ear_z": 0.41,
    "coat": lambda c, n: B if c.z < 0.045 else "fur_grey", "head_coat": _raccoon_head,
    "tail_coat": lambda c, n: B if int((c.y - 0.28) / 0.055) % 2 == 1 else "fur_grey",     # the rings
    "eyes": {"gap": 0.12, "inset": 0.55, "up": 0.30, "forward": 0.55, "size": 0.16},
    "extras": _raccoon_extras,
}


# ===== Opossum: low, a pale pointed face, big bare ears and a long bald tail =============================================================
def _possum_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.05, -0.285, 0.275), (0.05, 0.015, 0.055), taper=0.6)
    ctx.make("ears", ears, lambda c_, n: B, ["Ear_L", "Ear_R"], sub=0, smooth=False)


def _opossum_head_coat(c, n):
    if c.y < -0.455:
        return B
    return "pink" if c.y < -0.44 else W


OPOSSUM = {
    "name": "Opossum", "scale": 0.68, "body_n": 10, "head_n": 8,                                  # real: 0.15-0.25 m at the shoulder, 0.36-0.50 m long
    "body": [(-0.22, 0.19, 0.06, 0.07), (-0.14, 0.21, 0.09, 0.10), (0.00, 0.21, 0.10, 0.11), (0.14, 0.20, 0.09, 0.10), (0.22, 0.18, 0.06, 0.07)],
    "head": [(-0.16, 0.22, 0.055, 0.06), (-0.22, 0.22, 0.052, 0.058), (-0.27, 0.22, 0.050, 0.055), (-0.30, 0.21, 0.050, 0.052),
          (-0.35, 0.19, 0.040, 0.04), (-0.40, 0.17, 0.030, 0.03), (-0.44, 0.16, 0.022, 0.022), (-0.46, 0.155, 0.016, 0.016)],
    "front": {"x": 0.05, "y": -0.12, "joints": (1, 3),
               "profile": [(0.14, 0.0, 0.03, 0.035), (0.09, 0.0, 0.022, 0.025), (0.05, 0.0, 0.02, 0.022), (0.02, -0.005, 0.022, 0.03), (0.0, -0.01, 0.025, 0.04)]},
    "hind": {"x": 0.055, "y": 0.14, "joints": (2, 4),
              "profile": [(0.15, 0.0, 0.04, 0.05), (0.11, 0.02, 0.028, 0.032), (0.07, 0.03, 0.022, 0.026), (0.04, 0.02, 0.022, 0.028), (0.015, 0.005, 0.022, 0.03),
                       (0.0, -0.005, 0.024, 0.034)]},
    "tail": [(0.18, 0.22, 0.02), (0.14, 0.32, 0.017), (0.08, 0.42, 0.014), (0.03, 0.50, 0.012), (0.0, 0.55, 0.008)],
    "ear_x": 0.05, "ear_y": -0.285, "ear_z": 0.275,
    "coat": lambda c, n: "pink" if c.z < 0.03 else "grey_cat",
    "head_coat": _opossum_head_coat,
    "tail_coat": lambda c, n: "pink",
    "eyes": {"gap": 0.12, "inset": 0.48, "up": 0.30, "forward": 0.6, "size": 0.20},
    "extras": _possum_extras,
}


# ===== Skunk: black with two white stripes, a small face and a big bushy tail carried up ===============================================
def _skunk_coat(c, n):
    if n.z > 0.35 and 0.015 < abs(c.x) < 0.075 and c.z > 0.20:
        return W                                                       # the stripes down the back
    return B


def _skunk_tail(c, n):
    return W if (c.z > 0.31 or abs(c.x) < 0.02) else B


def _skunk_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.04, -0.20, 0.245), (0.03, 0.015, 0.03), taper=0.6)
    ctx.make("ears", ears, lambda c_, n: B, ["Ear_L", "Ear_R"], sub=0, smooth=False)

    def blaze(bm):                                                     # the white stripe up the face
        c.add_box(bm, (0, -0.19, 0.228), (0.022, 0.12, 0.012))
    ctx.make("blaze", blaze, lambda c_, n: W, ["Head"], sub=0, smooth=False)


SKUNK = {
    "name": "Skunk", "scale": 0.80, "body_n": 10, "head_n": 8,                                     # real: 0.14-0.24 m at the shoulder, 0.33-0.46 m long
    "body": [(-0.18, 0.17, 0.06, 0.07), (-0.10, 0.18, 0.09, 0.10), (0.02, 0.18, 0.10, 0.105), (0.14, 0.18, 0.09, 0.095), (0.22, 0.17, 0.06, 0.07)],
    "head": [(-0.12, 0.20, 0.055, 0.06), (-0.17, 0.21, 0.050, 0.058), (-0.21, 0.21, 0.048, 0.055), (-0.24, 0.20, 0.048, 0.052),
          (-0.27, 0.19, 0.040, 0.04), (-0.30, 0.185, 0.030, 0.03), (-0.32, 0.18, 0.025, 0.025), (-0.335, 0.18, 0.020, 0.02)],
    "front": {"x": 0.045, "y": -0.09, "joints": (1, 3),
               "profile": [(0.12, 0.0, 0.03, 0.035), (0.08, 0.0, 0.022, 0.025), (0.05, 0.0, 0.02, 0.022), (0.02, -0.005, 0.022, 0.03), (0.0, -0.01, 0.024, 0.034)]},
    "hind": {"x": 0.05, "y": 0.11, "joints": (2, 4),
              "profile": [(0.13, 0.0, 0.04, 0.05), (0.09, 0.02, 0.028, 0.032), (0.06, 0.03, 0.022, 0.026), (0.035, 0.02, 0.022, 0.028), (0.015, 0.005, 0.022, 0.03),
                       (0.0, -0.005, 0.024, 0.034)]},
    "tail": [(0.19, 0.22, 0.035), (0.26, 0.28, 0.06), (0.34, 0.33, 0.08), (0.42, 0.36, 0.075), (0.48, 0.37, 0.04)],
    "ear_x": 0.04, "ear_y": -0.20, "ear_z": 0.245,
    "coat": _skunk_coat, "head_coat": lambda c, n: B, "tail_coat": _skunk_tail,
    "eyes": {"gap": 0.12, "inset": 0.40, "up": 0.28, "forward": 0.6, "size": 0.20},
    "extras": _skunk_extras,
}


# ===== Red fox: slim, long black legs, big ears, a white chest and a big bushy tail with a white tip ====================================
def _fox_coat(c, n):
    if c.z < 0.17:
        return B                                                       # black stockings
    if n.z < -0.45 and c.y < 0.05:
        return W                                                       # the white chest
    return "orange_cat"


def _fox_head(c, n):
    if c.y < -0.635:
        return B                                                       # the nose
    if c.z < 0.478 and c.y < -0.38:
        return W                                                       # white cheeks and jaw
    return "orange_cat"


def _fox_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.05, -0.42, 0.62), (0.05, 0.016, 0.11), taper=0.3, rot_deg=(0, s * 6, 0))
    ctx.make("ears", ears, lambda c_, n: "orange_cat", ["Ear_L", "Ear_R"], sub=0, smooth=False)

    def ear_tips(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.05, -0.42, 0.665), (0.03, 0.017, 0.04), taper=0.2, rot_deg=(0, s * 6, 0))
    ctx.make("ear_tips", ear_tips, lambda c_, n: B, ["Ear_L", "Ear_R"], sub=0, smooth=False)


FOX = {
    "name": "Fox", "scale": 0.88, "body_n": 10, "head_n": 8,                                         # real: 0.35-0.50 m at the shoulder, 0.45-0.90 m long
    "body": [(-0.32, 0.40, 0.07, 0.10), (-0.20, 0.41, 0.10, 0.13), (0.00, 0.40, 0.11, 0.13), (0.20, 0.40, 0.10, 0.12), (0.34, 0.39, 0.07, 0.10)],
    "head": [(-0.26, 0.47, 0.07, 0.09), (-0.34, 0.51, 0.065, 0.085), (-0.40, 0.53, 0.060, 0.08), (-0.44, 0.53, 0.065, 0.08),
          (-0.52, 0.50, 0.045, 0.055), (-0.58, 0.48, 0.035, 0.04), (-0.62, 0.47, 0.028, 0.03), (-0.64, 0.47, 0.022, 0.024)],
    "front": {"x": 0.05, "y": -0.20, "joints": (1, 3),
               "profile": [(0.30, 0.0, 0.035, 0.045), (0.20, 0.0, 0.025, 0.03), (0.12, 0.0, 0.02, 0.024), (0.05, 0.0, 0.02, 0.025), (0.0, -0.01, 0.022, 0.032)]},
    "hind": {"x": 0.055, "y": 0.22, "joints": (2, 4),
              "profile": [(0.32, 0.0, 0.045, 0.06), (0.22, 0.03, 0.03, 0.04), (0.13, 0.05, 0.022, 0.028), (0.07, 0.03, 0.02, 0.026), (0.03, 0.01, 0.02, 0.028),
                       (0.0, -0.01, 0.022, 0.032)]},
    "tail": [(0.38, 0.35, 0.04), (0.33, 0.46, 0.07), (0.27, 0.58, 0.085), (0.20, 0.68, 0.075), (0.14, 0.74, 0.04)],
    "ear_x": 0.05, "ear_y": -0.42, "ear_z": 0.62,
    "coat": _fox_coat, "head_coat": _fox_head,
    "tail_coat": lambda c, n: W if c.y > 0.66 else "orange_cat",
    "eyes": {"gap": 0.14, "inset": 0.55, "up": 0.34, "forward": 0.6, "size": 0.15},
    "extras": _fox_extras,
}


# ===== White-tailed deer: long legs, a long neck, a small head, big ears and a white flag of a tail (doe, buck with antlers, spotted fawn) =====
def _deer_coat(c, n):
    if c.z < 0.06:
        return B                                                       # hooves
    if n.z < -0.35 and c.z < 0.9:
        return "cream"                                                 # the pale belly
    return "tan"


def _deer_head(c, n):
    if c.y < -1.215:
        return B                                                       # the nose
    if c.y < -1.06 and c.z < 1.40:
        return "cream"
    return "tan"


def _deer_ears(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.10, -0.86, 1.69), (0.115, 0.022, 0.20), taper=0.6, rot_deg=(0, s * 32, 0))      # big ears, held out to the sides
    ctx.make("ears", ears, lambda c_, n: "tan", ["Ear_L", "Ear_R"], sub=0, smooth=False)


def _deer_extras(ctx):
    _deer_ears(ctx)


def _buck_extras(ctx):
    _deer_ears(ctx)

    def antlers(bm):                                                   # a main beam sweeping up and forward from each side, with four tines
        for s in (-1, 1):
            beam = [(s * 0.06, -0.84, 1.60), (s * 0.09, -0.84, 1.74), (s * 0.13, -0.89, 1.87), (s * 0.15, -0.97, 1.95), (s * 0.15, -1.05, 1.98)]
            sp_mod.tube(bm, beam, [0.022, 0.02, 0.017, 0.014, 0.008], n=5)
            for (px, py, pz), (tx, ty, tz) in (((s * 0.09, -0.84, 1.74), (s * 0.11, -0.81, 1.90)), ((s * 0.13, -0.89, 1.87), (s * 0.15, -0.87, 2.04)),
                                               ((s * 0.15, -0.97, 1.95), (s * 0.15, -0.97, 2.10)), ((s * 0.06, -0.84, 1.60), (s * 0.05, -0.95, 1.66))):
                sp_mod.tube(bm, [(px, py, pz), ((px + tx) / 2, (py + ty) / 2, (pz + tz) / 2), (tx, ty, tz)], [0.013, 0.011, 0.005], n=4)
    ctx.make("antlers", antlers, lambda c_, n: "horn_cream", ["Head"], sub=0, smooth=False)


def _fawn_coat(c, n):
    base = _deer_coat(c, n)
    if base == "tan" and c.z > 0.5 and _hash(round(c.x * 18), round(c.y * 18), round(c.z * 18)) > 0.82:
        return W                                                       # the spots
    return base


DEER_DOE = {
    "name": "DeerDoe", "scale": 0.82, "body_n": 10, "head_n": 8,      # real: 0.80-1.00 m at the shoulder, a trunk about as long as it is tall (docs/assets/briefs/animals.md)
    "body": [(-0.66, 0.96, 0.13, 0.20), (-0.50, 0.99, 0.17, 0.27), (-0.25, 0.99, 0.19, 0.275), (0.05, 0.99, 0.18, 0.24), (0.35, 1.00, 0.18, 0.23),
             (0.55, 0.99, 0.16, 0.21), (0.66, 0.97, 0.11, 0.16)],
    # a long neck that carries the head well above the back, a long narrow muzzle
    "head": [(-0.56, 1.10, 0.11, 0.16), (-0.70, 1.28, 0.09, 0.14), (-0.80, 1.45, 0.08, 0.12), (-0.86, 1.52, 0.08, 0.11),
             (-0.98, 1.48, 0.07, 0.09), (-1.10, 1.41, 0.058, 0.068), (-1.19, 1.37, 0.05, 0.055), (-1.24, 1.35, 0.043, 0.046)],
    "front": {"x": 0.10, "y": -0.48, "joints": (1, 3),
               "profile": [(0.80, 0.0, 0.07, 0.09), (0.50, 0.0, 0.045, 0.055), (0.28, 0.0, 0.032, 0.036), (0.10, 0.0, 0.032, 0.036), (0.0, -0.01, 0.035, 0.05)]},
    "hind": {"x": 0.11, "y": 0.48, "joints": (2, 4),
              "profile": [(0.86, 0.0, 0.085, 0.12), (0.60, 0.05, 0.05, 0.07), (0.40, 0.10, 0.034, 0.04), (0.22, 0.06, 0.03, 0.034), (0.08, 0.02, 0.032, 0.036),
                       (0.0, 0.0, 0.035, 0.05)]},
    "tail": [(1.05, 0.64, 0.035), (0.99, 0.71, 0.05), (0.90, 0.75, 0.05), (0.83, 0.76, 0.03)],
    "ear_x": 0.10, "ear_y": -0.86, "ear_z": 1.62,
    "coat": _deer_coat, "head_coat": _deer_head, "tail_coat": lambda c, n: W if n.z < 0.2 else "tan",
    "eyes": {"gap": 0.13, "inset": 0.55, "up": 0.30, "forward": 0.2, "size": 0.14},
    "extras": _deer_extras,
}

DEER_BUCK = dict(DEER_DOE, name="DeerBuck", scale=0.86, extras=_buck_extras,                 # heavier in the chest and neck than the doe
                 body=[(-0.66, 0.97, 0.14, 0.21), (-0.50, 1.00, 0.19, 0.285), (-0.25, 1.00, 0.21, 0.29), (0.05, 0.99, 0.20, 0.25), (0.35, 1.00, 0.19, 0.235),
                       (0.55, 0.99, 0.165, 0.21), (0.66, 0.97, 0.11, 0.16)])
DEER_FAWN = dict(DEER_DOE, name="DeerFawn", scale=0.50, coat=_fawn_coat)


# ===== Black bear: heavy, a LEVEL back (no hump: that is the grizzly), a big head carried low, tall oval ears, a tan muzzle, a very short tail ==================================
def _bear_head(c, n):
    if c.y < -1.255:
        return B                                                       # the nose
    if c.y < -1.06:
        return "tan"                                                   # the muzzle
    return "hair_black"


def _bear_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.13, -0.95, 1.00), (0.11, 0.05, 0.15), taper=0.7)              # round ears, standing clear of the skull
    ctx.make("ears", ears, lambda c_, n: "hair_black", ["Ear_L", "Ear_R"], sub=0, smooth=False)


BEAR = {
    "name": "Bear", "scale": 0.92, "body_n": 10, "head_n": 8,                                      # real: 0.75-1.05 m at the shoulder, 1.2-2.0 m long, a tail of 8-14 cm
    "body": [(-0.75, 0.72, 0.16, 0.20), (-0.55, 0.76, 0.24, 0.28), (-0.25, 0.78, 0.29, 0.30), (0.10, 0.76, 0.31, 0.30), (0.45, 0.74, 0.30, 0.29), (0.72, 0.70, 0.22, 0.24)],
    "head": [(-0.62, 0.80, 0.20, 0.22), (-0.80, 0.80, 0.17, 0.20), (-0.92, 0.77, 0.16, 0.19), (-0.98, 0.75, 0.16, 0.18),
          (-1.08, 0.70, 0.13, 0.14), (-1.18, 0.65, 0.10, 0.10), (-1.24, 0.63, 0.09, 0.085), (-1.27, 0.63, 0.08, 0.075)],
    "front": {"x": 0.20, "y": -0.40, "joints": (1, 3),
               "profile": [(0.62, 0.0, 0.14, 0.16), (0.40, 0.0, 0.10, 0.11), (0.22, 0.0, 0.085, 0.09), (0.08, 0.0, 0.09, 0.10), (0.0, -0.02, 0.095, 0.13)]},
    "hind": {"x": 0.21, "y": 0.45, "joints": (2, 4),
              "profile": [(0.64, 0.0, 0.16, 0.20), (0.44, 0.04, 0.11, 0.13), (0.28, 0.08, 0.09, 0.10), (0.13, 0.06, 0.09, 0.10), (0.05, 0.02, 0.09, 0.11),
                       (0.0, -0.02, 0.095, 0.14)]},
    "tail": [(0.68, 0.72, 0.04), (0.64, 0.76, 0.035), (0.60, 0.79, 0.03)],
    "ear_x": 0.12, "ear_y": -0.95, "ear_z": 0.97,
    "coat": lambda c, n: "hair_black", "head_coat": _bear_head, "tail_coat": lambda c, n: "hair_black",
    "eyes": {"gap": 0.12, "inset": 0.55, "up": 0.30, "forward": 0.4, "size": 0.11},
    "extras": _bear_extras,
}


WILD = {"raccoon": RACCOON, "opossum": OPOSSUM, "skunk": SKUNK, "fox": FOX, "deer_doe": DEER_DOE, "deer_buck": DEER_BUCK, "deer_fawn": DEER_FAWN, "bear": BEAR}
