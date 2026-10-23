"""Species descriptions for quadruped_builder.py. All animals face -Y, Z up, feet on z = 0.

Each entry gives, in metres:
    body    sections front to back:  (y, centre z, half width, half height)
    head    neck and head sections, neck root first, nose last:  (y, centre z, half width, half height)
    front / hind   x, y of the leg, joints = (knee-or-hock ring, ankle ring), profile rings top to ground:
                   (z, y offset, half x, half y). Front legs have 5 rings, hind legs 6.
    tail    (z, y, radius) top to tip
    ear_x, ear_y, ear_z   where the ear bone sits (left side)
    coat(c, n) / head_coat / tail_coat   -> palette swatch for a face centred at c with normal n
    extras(ctx) optional hook that adds parts with ctx.make(name, build(bm), colour, bones)
"""

import math

import common

B, W, K = "black", "paint_white", "pink"


def _box(bm, *a, **k):
    common.add_box(bm, *a, **k)


def tube(bm, points, radii, n=6):
    """A round tube along a path (horns, tusks, a curved tail): a ring of n points perpendicular to the path at every point, radii[i] wide at
    points[i]; the ends are closed. Lofted rings in a plane (ring_z) would go flat where a horn turns to the horizontal."""
    from math import cos, pi, sin
    from mathutils import Vector
    pts = [Vector(p) for p in points]
    rings = []
    u = None
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if u is None:
            up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((0, 1, 0))
            u = t.cross(up).normalized()
        else:
            u = (u - t * t.dot(u)).normalized()                  # carry the frame along the path (parallel transport): a ring never turns about the path
        v = t.cross(u).normalized()
        rings.append([p + radii[i] * (cos(2 * pi * k / n) * u + sin(2 * pi * k / n) * v) for k in range(n)])
    common.loft(bm, rings)


# ===== Cow (Holstein): the original hand-tuned numbers =======================================================
COW_BLOBS = [
    (0.36, -0.40, 1.10, 0.24), (0.34, 0.22, 0.88, 0.20), (-0.36, -0.05, 1.12, 0.26),
    (-0.33, 0.52, 0.98, 0.19), (0.02, 0.18, 1.42, 0.20), (-0.30, -0.62, 0.86, 0.15),
    (0.30, 0.68, 1.22, 0.13), (0.18, -1.00, 1.22, 0.14), (-0.20, -0.95, 1.05, 0.12),
]


def _cow_patch(c):
    total = sum(math.exp(-((c.x - bx) ** 2 + (c.y - by) ** 2 + (c.z - bz) ** 2) / (2 * s * s)) for bx, by, bz, s in COW_BLOBS)
    return total > 0.5


def _cow_coat(c, n):
    if c.z < 0.085:
        return B
    return B if _cow_patch(c) else W


def _cow_head(c, n):
    if c.y < -1.54:
        return K
    if c.y < -1.14:
        return W if (abs(c.x) < 0.04 and n.z + n.y * -0.3 > 0.2) else B
    return B if _cow_patch(c) else W


def _cow_extras(ctx):
    c = ctx.common
    # the top ring is inside the belly (the belly's underside is at z 0.71 here), so the udder grows out of the body and does not hang under it
    ctx.make("udder", lambda bm: c.loft(bm, [c.ring_z(0.80, 0, 0.64, 0.12, 0.15, n=8), c.ring_z(0.62, 0, 0.64, 0.14, 0.17, n=8),
                                              c.ring_z(0.50, 0, 0.64, 0.12, 0.14, n=8), c.ring_z(0.43, 0, 0.64, 0.07, 0.08, n=8)]), lambda c_, n: K, ["Hips"])

    def teats(bm):
        for dx in (-0.06, 0.06):
            for dy in (0.57, 0.71):
                c.loft(bm, [c.ring_z(0.47, dx, dy, 0.02, 0.02, n=6), c.ring_z(0.37, dx, dy, 0.016, 0.016, n=6)])

    ctx.make("teats", teats, lambda c_, n: K, ["Hips"], sub=0)

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.20, -1.21, 1.24), (0.20, 0.14, 0.035), rot_deg=(8, s * 38, s * -10))      # the base overlaps the head

    ctx.make("ears", ears, lambda c_, n: B, ["Ear_L", "Ear_R"], sub=min(1, ctx.style["sub"]))

    def horns(bm):
        for s in (-1, 1):
            c.loft(bm, [c.ring_z(1.30, s * 0.11, -1.19, 0.035, 0.035, n=6), c.ring_z(1.36, s * 0.14, -1.19, 0.028, 0.028, n=6),
                        c.ring_z(1.41, s * 0.18, -1.19, 0.008, 0.008, n=6)])

    ctx.make("horns", horns, lambda c_, n: "horn_cream", ["Head"], sub=0)


COW = dict(
    name="Cow",
    body=[(-0.88, 1.02, 0.20, 0.28), (-0.68, 1.03, 0.29, 0.37), (-0.38, 1.01, 0.33, 0.40), (-0.02, 0.98, 0.35, 0.40),
          (0.34, 1.00, 0.33, 0.37), (0.66, 1.05, 0.30, 0.34), (0.90, 1.03, 0.21, 0.27)],
    head=[(-0.74, 1.16, 0.23, 0.29), (-0.95, 1.15, 0.19, 0.25), (-1.10, 1.13, 0.16, 0.21), (-1.20, 1.14, 0.17, 0.22),
          (-1.36, 1.06, 0.145, 0.19), (-1.50, 0.97, 0.125, 0.15), (-1.58, 0.94, 0.13, 0.115), (-1.63, 0.93, 0.115, 0.095)],
    front=dict(x=0.21, y=-0.60, joints=(1, 3),
               profile=[(0.82, 0.00, 0.12, 0.15), (0.52, 0.00, 0.085, 0.09), (0.30, 0.00, 0.055, 0.06),
                        (0.11, 0.00, 0.06, 0.065), (0.0, -0.01, 0.075, 0.095)]),
    hind=dict(x=0.21, y=0.60, joints=(2, 4),
              profile=[(0.86, 0.00, 0.14, 0.20), (0.62, 0.05, 0.09, 0.12), (0.44, 0.10, 0.06, 0.07),
                       (0.22, 0.04, 0.05, 0.06), (0.10, 0.01, 0.058, 0.064), (0.0, 0.0, 0.075, 0.095)]),
    tail=[(1.18, 0.88, 0.035), (0.95, 0.94, 0.028), (0.65, 0.97, 0.024), (0.48, 0.98, 0.04), (0.30, 0.98, 0.05), (0.26, 0.98, 0.012)],
    ear_x=0.23, ear_y=-1.21, ear_z=1.22,
    coat=_cow_coat, head_coat=_cow_head, tail_coat=lambda c, n: B if c.z < 0.5 else W,
    extras=_cow_extras,
)


# ===== Horse: long legs, a long neck carried high, a small head ==============================================
def _horse_coat(c, n):
    if c.z < 0.10:
        return B
    return B if c.z < 0.45 else "brown_coat"


def _horse_head(c, n):
    return "brown_coat" if c.y > -1.20 else ("black" if c.y < -1.50 else "brown_coat")


def _horse_extras(ctx):
    c = ctx.common

    def mane(bm):                                      # a thick mane of hair down the crest of the neck, and a forelock between the ears
        crest = ((-0.62, 1.71), (-0.72, 1.78), (-0.82, 1.84), (-0.92, 1.90), (-1.00, 1.94), (-1.06, 1.96))     # (y, z) of the top of the neck
        for y, z in crest:
            c.add_box(bm, (0, y + 0.03, z - 0.01), (0.08, 0.13, 0.26), rot_deg=(30, 0, 0))                   # hangs a little down the neck's far side
        c.add_box(bm, (0, -1.10, 1.92), (0.07, 0.09, 0.14), rot_deg=(-10, 0, 0))                           # the forelock, its foot inside the forehead

    ctx.make("mane", mane, lambda c_, n: B, ["Neck1", "Neck2", "Head"], sub=0, smooth=False)

    def ears(bm):                                      # tall, pointed ears on the crown (they were 12 cm: a horse's are about 20)
        for s in (-1, 1):
            c.add_box(bm, (s * 0.075, -1.07, 2.04), (0.075, 0.045, 0.24), rot_deg=(0, s * 8, 0), taper=0.4)

    ctx.make("ears", ears, lambda c_, n: "brown_coat", ["Ear_L", "Ear_R"], sub=0, smooth=False)


HORSE = dict(
    name="Horse",
    body=[(-0.80, 1.28, 0.20, 0.30), (-0.62, 1.30, 0.25, 0.34), (-0.30, 1.27, 0.26, 0.36), (0.05, 1.25, 0.26, 0.35),
          (0.40, 1.27, 0.25, 0.33), (0.70, 1.32, 0.24, 0.31), (0.88, 1.30, 0.18, 0.26)],
    head=[(-0.62, 1.45, 0.15, 0.26), (-0.85, 1.62, 0.12, 0.22), (-1.00, 1.74, 0.11, 0.20), (-1.08, 1.77, 0.115, 0.19),
          (-1.30, 1.64, 0.10, 0.15), (-1.46, 1.55, 0.09, 0.12), (-1.54, 1.51, 0.095, 0.10), (-1.58, 1.50, 0.085, 0.085)],
    front=dict(x=0.16, y=-0.55, joints=(1, 3),
               profile=[(1.00, 0.00, 0.10, 0.13), (0.62, 0.00, 0.065, 0.075), (0.34, 0.00, 0.045, 0.05),
                        (0.14, 0.00, 0.05, 0.055), (0.0, 0.00, 0.06, 0.075)]),
    hind=dict(x=0.16, y=0.62, joints=(2, 4),
              profile=[(1.05, 0.00, 0.12, 0.18), (0.76, 0.06, 0.075, 0.10), (0.50, 0.12, 0.05, 0.06),
                       (0.26, 0.07, 0.042, 0.05), (0.11, 0.03, 0.05, 0.055), (0.0, 0.02, 0.06, 0.07)]),
    tail=[(1.28, 0.88, 0.035), (1.00, 0.96, 0.04), (0.72, 1.00, 0.045), (0.50, 1.02, 0.04), (0.35, 1.03, 0.025)],
    ear_x=0.07, ear_y=-1.05, ear_z=1.88,
    coat=_horse_coat, head_coat=_horse_head, tail_coat=lambda c, n: B,
    extras=_horse_extras,
)


# ===== Sheep: round, woolly, short dark legs and a dark face ==================================================
def _sheep_coat(c, n):
    return B if c.z < 0.26 else W


def _sheep_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.15, -0.58, 0.70), (0.13, 0.07, 0.025), rot_deg=(0, s * 25, s * -8))

    ctx.make("ears", ears, lambda c_, n: B, ["Ear_L", "Ear_R"], sub=0, smooth=False)


SHEEP = dict(
    name="Sheep",
    body=[(-0.40, 0.56, 0.20, 0.22), (-0.25, 0.58, 0.26, 0.27), (0.00, 0.57, 0.28, 0.28), (0.25, 0.58, 0.26, 0.26),
          (0.40, 0.56, 0.20, 0.21)],
    head=[(-0.34, 0.66, 0.13, 0.17), (-0.46, 0.68, 0.11, 0.15), (-0.55, 0.66, 0.10, 0.14), (-0.62, 0.62, 0.08, 0.12),
          (-0.72, 0.57, 0.065, 0.09), (-0.77, 0.55, 0.06, 0.07), (-0.80, 0.54, 0.055, 0.065), (-0.82, 0.54, 0.045, 0.055)],
    front=dict(x=0.12, y=-0.26, joints=(1, 3),
               profile=[(0.42, 0.00, 0.05, 0.06), (0.26, 0.00, 0.035, 0.04), (0.14, 0.00, 0.03, 0.034),
                        (0.06, 0.00, 0.03, 0.034), (0.0, 0.00, 0.036, 0.048)]),
    hind=dict(x=0.12, y=0.27, joints=(2, 4),
              profile=[(0.44, 0.00, 0.07, 0.09), (0.32, 0.03, 0.045, 0.055), (0.22, 0.05, 0.035, 0.04),
                       (0.12, 0.025, 0.03, 0.034), (0.05, 0.01, 0.03, 0.034), (0.0, 0.0, 0.036, 0.048)]),
    tail=[(0.52, 0.42, 0.035), (0.44, 0.45, 0.03), (0.37, 0.46, 0.025), (0.31, 0.46, 0.018)],
    ear_x=0.14, ear_y=-0.58, ear_z=0.70,
    coat=_sheep_coat, head_coat=lambda c, n: B, tail_coat=lambda c, n: W,
    extras=_sheep_extras,
)


# ===== Pig: low, barrel body, flat snout, floppy ears, curly tail ===============================================
def _pig_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.12, -0.68, 0.70), (0.12, 0.10, 0.025), rot_deg=(25, s * 30, s * -10))

    ctx.make("ears", ears, lambda c_, n: K, ["Ear_L", "Ear_R"], sub=0, smooth=False)


PIG = dict(
    name="Pig",
    body=[(-0.50, 0.55, 0.20, 0.22), (-0.30, 0.58, 0.27, 0.29), (0.00, 0.57, 0.30, 0.30), (0.30, 0.58, 0.28, 0.28),
          (0.50, 0.55, 0.22, 0.24)],
    head=[(-0.42, 0.58, 0.18, 0.20), (-0.58, 0.58, 0.16, 0.19), (-0.68, 0.56, 0.15, 0.18), (-0.80, 0.52, 0.12, 0.14),
          (-0.90, 0.48, 0.10, 0.11), (-0.96, 0.47, 0.095, 0.10), (-0.99, 0.47, 0.10, 0.10), (-1.01, 0.47, 0.09, 0.09)],
    front=dict(x=0.13, y=-0.30, joints=(1, 3),
               profile=[(0.36, 0.00, 0.07, 0.08), (0.24, 0.00, 0.05, 0.055), (0.15, 0.00, 0.04, 0.045),
                        (0.07, 0.00, 0.04, 0.045), (0.0, 0.00, 0.05, 0.06)]),
    hind=dict(x=0.13, y=0.30, joints=(2, 4),
              profile=[(0.38, 0.00, 0.09, 0.11), (0.28, 0.03, 0.06, 0.07), (0.20, 0.05, 0.045, 0.05),
                       (0.12, 0.03, 0.04, 0.045), (0.06, 0.01, 0.04, 0.045), (0.0, 0.0, 0.05, 0.06)]),
    tail=[(0.62, 0.52, 0.025), (0.66, 0.56, 0.02), (0.64, 0.60, 0.018), (0.58, 0.58, 0.015)],
    ear_x=0.12, ear_y=-0.68, ear_z=0.70,
    coat=lambda c, n: "black" if c.z < 0.06 else K, head_coat=lambda c, n: ("black" if c.y < -0.99 and False else K),
    tail_coat=lambda c, n: K,
    extras=_pig_extras,
)


# ===== Goat: slim, a little taller than a sheep, horns and a beard ==============================================
def _goat_coat(c, n):
    if c.z < 0.06:
        return B
    return "brown_coat" if (c.z > 0.62 and abs(c.x) < 0.12) or c.z < 0.26 else W


def _goat_extras(ctx):
    c = ctx.common

    def horns(bm):                                     # scimitar horns: up from the crown, then sweeping back (+y is back) and out, the tips pointing down
        for s in (-1, 1):
            tube(bm, [(s * 0.050, -0.60, 0.84), (s * 0.056, -0.58, 0.97), (s * 0.066, -0.52, 1.08), (s * 0.078, -0.43, 1.14), (s * 0.090, -0.34, 1.13), (s * 0.096, -0.28, 1.08)],
                 [0.030, 0.027, 0.022, 0.017, 0.011, 0.005], n=5)

    ctx.make("horns", horns, lambda c_, n: "horn_cream", ["Head"], sub=0, smooth=False)

    def beard(bm):
        c.add_box(bm, (0, -0.84, 0.54), (0.035, 0.04, 0.09), taper=0.5, rot_deg=(180, 0, 0))

    ctx.make("beard", beard, lambda c_, n: W, ["Head"], sub=0, smooth=False)

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.11, -0.66, 0.84), (0.13, 0.07, 0.02), rot_deg=(0, s * 20, s * -12))

    ctx.make("ears", ears, lambda c_, n: "brown_coat", ["Ear_L", "Ear_R"], sub=0, smooth=False)


GOAT = dict(
    name="Goat",
    body=[(-0.45, 0.58, 0.13, 0.19), (-0.28, 0.61, 0.16, 0.23), (0.00, 0.59, 0.17, 0.23), (0.27, 0.60, 0.16, 0.21),
          (0.45, 0.61, 0.12, 0.17)],
    head=[(-0.37, 0.70, 0.09, 0.15), (-0.50, 0.76, 0.075, 0.13), (-0.60, 0.79, 0.07, 0.12), (-0.65, 0.78, 0.075, 0.11),
          (-0.76, 0.69, 0.06, 0.085), (-0.85, 0.62, 0.05, 0.065), (-0.90, 0.59, 0.05, 0.058), (-0.93, 0.58, 0.04, 0.05)],
    front=dict(x=0.09, y=-0.30, joints=(1, 3),
               profile=[(0.46, 0.00, 0.04, 0.05), (0.30, 0.00, 0.03, 0.034), (0.17, 0.00, 0.024, 0.028),
                        (0.07, 0.00, 0.026, 0.03), (0.0, 0.00, 0.032, 0.04)]),
    hind=dict(x=0.09, y=0.32, joints=(2, 4),
              profile=[(0.50, 0.00, 0.06, 0.075), (0.36, 0.03, 0.04, 0.048), (0.24, 0.06, 0.03, 0.034),
                       (0.13, 0.03, 0.026, 0.03), (0.06, 0.01, 0.026, 0.03), (0.0, 0.0, 0.032, 0.04)]),
    tail=[(0.70, 0.45, 0.025), (0.76, 0.48, 0.022), (0.78, 0.50, 0.018), (0.78, 0.52, 0.01)],
    ear_x=0.11, ear_y=-0.66, ear_z=0.84,
    coat=_goat_coat, head_coat=lambda c, n: "brown_coat" if c.y > -0.72 else W, tail_coat=lambda c, n: W,
    extras=_goat_extras,
)


SPECIES = {"cow": COW, "horse": HORSE, "sheep": SHEEP, "pig": PIG, "goat": GOAT}

import species_pets
SPECIES.update(species_pets.DOGS)
SPECIES.update(species_pets.DOG_SKINS)
SPECIES.update(species_pets.CATS)
import species_wild
SPECIES.update(species_wild.WILD)
