"""Species descriptions for quadruped_builder.py. All animals face -Y, Z up, feet on z = 0.

Each entry gives, in metres:
    body    sections front to back:  (y, centre z, half width, half height)
    head    neck and head sections, neck root first, nose last:  (y, centre z, half width, half height)
    front / hind   x, y of the leg, joints = (knee-or-hock ring, ankle ring), profile rings top to ground:
                   (z, y offset, half x, half y). Front legs have 5 rings, hind legs 6.
    tail    (z, y, radius) top to tip
    ear_x, ear_y, ear_z   where the ear bone sits (left side)
    coat(c, n) / head_coat / tail_coat / leg_coat   -> palette swatch for a face centred at c with normal n (leg_coat optional, defaults to coat)
    facet                                  -> optional {"ratio": r, "sub": n}: the lofted parts subdivided n times, then decimated to r of their faces (common.facet)
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
    if c.z < 0.10:
        return B
    return B if _cow_patch(c) else W


def _cow_head(c, n):
    if c.y < -1.48:
        return K
    if c.y < -1.06:
        return W if (abs(c.x) < 0.04 and n.z + n.y * -0.3 > 0.2) else B
    return B if _cow_patch(c) else W


def _cow_extras(ctx):
    c = ctx.common
    # the top ring is inside the belly (the belly's underside is at z 0.73 here), so the udder grows out of the body and does not hang under it
    ctx.make("udder", lambda bm: c.loft(bm, [c.ring_z(0.80, 0, 0.64, 0.12, 0.15, n=8), c.ring_z(0.62, 0, 0.64, 0.14, 0.17, n=8),
                                              c.ring_z(0.50, 0, 0.64, 0.12, 0.14, n=8), c.ring_z(0.43, 0, 0.64, 0.07, 0.08, n=8)]), lambda c_, n: K, ["Hips"])

    def teats(bm):
        for dx in (-0.06, 0.06):
            for dy in (0.57, 0.71):
                c.loft(bm, [c.ring_z(0.47, dx, dy, 0.02, 0.02, n=6), c.ring_z(0.37, dx, dy, 0.016, 0.016, n=6)])

    ctx.make("teats", teats, lambda c_, n: K, ["Hips"], sub=0)

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.21, -1.15, 1.25), (0.22, 0.14, 0.04), rot_deg=(8, s * 20, s * -8))      # the base overlaps the head

    ctx.make("ears", ears, lambda c_, n: B, ["Ear_L", "Ear_R"], sub=min(1, ctx.style["sub"]))

    def horns(bm):
        for s in (-1, 1):
            c.loft(bm, [c.ring_z(1.30, s * 0.10, -1.14, 0.035, 0.035, n=6), c.ring_z(1.38, s * 0.13, -1.14, 0.028, 0.028, n=6),
                        c.ring_z(1.44, s * 0.17, -1.14, 0.008, 0.008, n=6)])

    ctx.make("horns", horns, lambda c_, n: "horn_cream", ["Head"], sub=0)


COW = {
    "name": "Cow", "body_n": 10, "head_n": 8,
    # a Holstein cow: 1.45 m at the withers, a deep barrel 0.82 m through the ribs, a long head carried level with the back and tipped down, the knee at 0.46 m (the elbow at 43 % of the height)
    "body": [(-0.86, 1.03, 0.21, 0.30), (-0.62, 1.04, 0.30, 0.40), (-0.30, 1.04, 0.32, 0.41), (0.05, 1.01, 0.32, 0.40),
          (0.38, 1.03, 0.31, 0.37), (0.66, 1.08, 0.30, 0.35), (0.88, 1.05, 0.22, 0.28)],
    "head": [(-0.60, 1.14, 0.24, 0.31), (-0.84, 1.22, 0.20, 0.27), (-0.98, 1.21, 0.17, 0.23), (-1.12, 1.20, 0.145, 0.20),
          (-1.20, 1.12, 0.145, 0.20), (-1.34, 1.02, 0.12, 0.17), (-1.46, 0.95, 0.11, 0.14), (-1.54, 0.90, 0.125, 0.11), (-1.58, 0.88, 0.115, 0.095)],
    # the legs start inside the barrel at the shoulder and the hip (the first ring, set in by dx), the upper arm and the thigh a little proud of it; the stifle forward
    "front": {"x": 0.20, "y": -0.50, "joints": (2, 4),
               "profile": [(1.02, 0.04, 0.10, 0.15, -0.06), (0.86, 0.02, 0.112, 0.15), (0.46, 0.00, 0.074, 0.09), (0.28, 0.00, 0.060, 0.07),
                        (0.12, 0.00, 0.062, 0.07), (0.0, -0.005, 0.072, 0.078)]},
    "hind": {"x": 0.19, "y": 0.58, "joints": (3, 5),
              "profile": [(1.10, 0.00, 0.12, 0.18, -0.06), (0.92, -0.02, 0.15, 0.21), (0.68, -0.07, 0.10, 0.13), (0.48, 0.08, 0.06, 0.09),
                       (0.30, 0.06, 0.052, 0.07), (0.12, 0.02, 0.056, 0.064), (0.0, 0.0, 0.068, 0.078)]},
    "body_keel": [0.20, 0.30, 0.30, 0.25, 0.15, 0.10, 0.10],
    "tail": [(1.28, 0.88, 0.035), (1.00, 0.95, 0.028), (0.65, 0.98, 0.024), (0.48, 0.99, 0.04), (0.30, 0.99, 0.05), (0.26, 0.99, 0.012)],
    "ear_x": 0.23, "ear_y": -1.12, "ear_z": 1.22,
    "coat": _cow_coat, "head_coat": _cow_head, "tail_coat": lambda c, n: B if c.z < 0.5 else W,
    "extras": _cow_extras,
}


# ===== Horse: long legs, a long neck carried high, a small head ==============================================
def _horse_coat(c, n):
    if c.z < 0.11:
        return B
    return B if c.z < 0.50 else "brown_coat"


def _horse_head(c, n):
    return "black" if c.y < -1.45 else "brown_coat"


def _horse_extras(ctx):
    c = ctx.common

    def mane(bm):                                      # a thick mane of hair down the crest of the neck, and a forelock between the ears
        crest = ((-0.62, 1.78), (-0.72, 1.84), (-0.82, 1.90), (-0.92, 1.96), (-1.00, 2.00), (-1.06, 2.02))     # (y, z) of the top of the neck
        for y, z in crest:
            c.add_box(bm, (0, y + 0.03, z - 0.01), (0.08, 0.13, 0.26), rot_deg=(30, 0, 0))                   # hangs a little down the neck's far side
        c.add_box(bm, (0, -1.12, 1.97), (0.07, 0.09, 0.14), rot_deg=(-10, 0, 0))                           # the forelock, its foot inside the forehead

    ctx.make("mane", mane, lambda c_, n: B, ["Neck1", "Neck2", "Head"], sub=0, smooth=False)

    def ears(bm):                                      # tall, pointed ears on the crown (they were 12 cm: a horse's are about 20)
        for s in (-1, 1):
            c.add_box(bm, (s * 0.075, -1.03, 2.08), (0.075, 0.045, 0.24), rot_deg=(0, s * 8, 0), taper=0.4)

    ctx.make("ears", ears, lambda c_, n: "brown_coat", ["Ear_L", "Ear_R"], sub=0, smooth=False)


HORSE = {
    "name": "Horse", "body_n": 10, "head_n": 8,
    # a riding horse of about 15.2 hands: 1.57 m at the withers, a body as deep as its legs are long, a long neck, a head 0.66 m long tipped 45 degrees
    "body": [(-0.78, 1.15, 0.20, 0.30), (-0.58, 1.16, 0.27, 0.39), (-0.30, 1.18, 0.27, 0.39), (0.05, 1.15, 0.27, 0.37),
          (0.38, 1.17, 0.27, 0.35), (0.66, 1.22, 0.27, 0.33), (0.84, 1.18, 0.20, 0.28)],
    "head": [(-0.55, 1.30, 0.19, 0.27), (-0.78, 1.64, 0.15, 0.24), (-0.94, 1.76, 0.125, 0.21), (-1.04, 1.82, 0.11, 0.19),
          (-1.14, 1.75, 0.115, 0.17), (-1.30, 1.55, 0.10, 0.14), (-1.43, 1.42, 0.09, 0.115), (-1.49, 1.38, 0.095, 0.095), (-1.52, 1.36, 0.085, 0.085)],
    # the legs start inside the barrel at the shoulder and the hip (set in by dx), the forearm's and the gaskin's muscle above the knee and the hock, the stifle forward
    "gait_leg": 1.00,                                              # the gait's leg length as before the rework (the leg's top under the barrel)
    "front": {"x": 0.15, "y": -0.50, "joints": (2, 4),
               "profile": [(1.12, 0.0, 0.085, 0.14, -0.05), (0.92, 0.0, 0.092, 0.13), (0.50, 0.00, 0.064, 0.08), (0.30, 0.00, 0.050, 0.058),
                        (0.13, 0.00, 0.054, 0.062), (0.0, 0.00, 0.064, 0.076)]},
    "hind": {"x": 0.14, "y": 0.58, "joints": (3, 5),
              "profile": [(1.20, 0.00, 0.10, 0.16, -0.05), (1.02, -0.02, 0.13, 0.19), (0.80, -0.05, 0.08, 0.11), (0.54, 0.14, 0.05, 0.07),
                       (0.30, 0.09, 0.045, 0.055), (0.13, 0.04, 0.05, 0.057), (0.0, 0.03, 0.062, 0.075)]},
    "body_keel": [0.25, 0.35, 0.35, 0.25, 0.15, 0.10, 0.10],
    "tail": [(1.40, 0.88, 0.035), (1.15, 0.97, 0.05), (0.85, 1.00, 0.06), (0.60, 1.02, 0.05), (0.42, 1.03, 0.03)],
    "ear_x": 0.07, "ear_y": -1.04, "ear_z": 1.98,
    "coat": _horse_coat, "head_coat": _horse_head, "tail_coat": lambda c, n: B,
    "extras": _horse_extras,
}


# ===== Sheep: a woolly barrel on thin dark legs, a narrow dark face ===========================================
def _sheep_coat(c, n):
    return B if c.z < 0.30 else W


def _sheep_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.13, -0.57, 0.74), (0.12, 0.06, 0.025), rot_deg=(0, s * 25, s * -8))

    ctx.make("ears", ears, lambda c_, n: B, ["Ear_L", "Ear_R"], sub=0, smooth=False)

    def topknot(bm):                                    # a tuft of wool on the crown, as a ewe has
        c.add_box(bm, (0, -0.54, 0.86), (0.075, 0.085, 0.055), taper=0.6)

    ctx.make("topknot", topknot, lambda c_, n: W, ["Head"], sub=0, smooth=False)


SHEEP = {
    "name": "Sheep", "body_n": 10, "head_n": 8,
    # an adult ewe in full wool: 0.79 m at the withers, 0.44 m wide with the fleece, a head 0.27 m long, legs 0.35 m from the elbow
    "body": [(-0.42, 0.56, 0.17, 0.19), (-0.26, 0.57, 0.22, 0.22), (0.00, 0.56, 0.22, 0.22), (0.26, 0.56, 0.22, 0.22),
          (0.42, 0.55, 0.18, 0.19)],
    "head": [(-0.30, 0.61, 0.14, 0.18), (-0.42, 0.70, 0.12, 0.16), (-0.52, 0.72, 0.09, 0.13), (-0.58, 0.72, 0.07, 0.12),
          (-0.65, 0.66, 0.07, 0.105), (-0.73, 0.60, 0.058, 0.08), (-0.78, 0.57, 0.052, 0.065), (-0.80, 0.56, 0.048, 0.055)],
    "front": {"x": 0.11, "y": -0.24, "joints": (2, 4),
               "profile": [(0.50, 0.02, 0.05, 0.06, -0.04), (0.40, 0.01, 0.045, 0.055), (0.22, 0.00, 0.032, 0.038), (0.12, 0.00, 0.03, 0.034),
                        (0.055, 0.00, 0.03, 0.034), (0.0, 0.00, 0.034, 0.042)]},
    "hind": {"x": 0.11, "y": 0.26, "joints": (3, 5),
              "profile": [(0.54, 0.00, 0.06, 0.08, -0.04), (0.44, -0.01, 0.065, 0.085), (0.32, -0.03, 0.04, 0.05), (0.21, 0.05, 0.032, 0.038),
                       (0.11, 0.025, 0.03, 0.034), (0.05, 0.01, 0.03, 0.034), (0.0, 0.0, 0.034, 0.042)]},
    "body_keel": [0.10, 0.12, 0.12, 0.08, 0.05],
    "tail": [(0.52, 0.42, 0.04), (0.42, 0.46, 0.035), (0.32, 0.47, 0.03), (0.26, 0.47, 0.02)],
    "ear_x": 0.13, "ear_y": -0.58, "ear_z": 0.74,
    "coat": _sheep_coat, "head_coat": lambda c, n: W if c.y > -0.50 else B, "tail_coat": lambda c, n: W,
    "extras": _sheep_extras,
}


# ===== Pig: low, barrel body, flat snout, floppy ears, curly tail ===============================================
def _pig_extras(ctx):
    c = ctx.common

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.12, -0.80, 0.70), (0.12, 0.10, 0.025), rot_deg=(25, s * 30, s * -10))

    ctx.make("ears", ears, lambda c_, n: K, ["Ear_L", "Ear_R"], sub=0, smooth=False)


PIG = {
    "name": "Pig", "body_n": 10, "head_n": 8,
    # a market hog: 0.81 m at the shoulder, 1.12 m of trunk, nearly as deep as it is wide, the chest 0.26 m off the ground, ham at the rear, a head 0.39 m long
    "body": [(-0.52, 0.52, 0.21, 0.22), (-0.36, 0.54, 0.28, 0.27), (-0.10, 0.55, 0.30, 0.27), (0.18, 0.54, 0.30, 0.27),
          (0.42, 0.52, 0.29, 0.26), (0.60, 0.48, 0.22, 0.22)],
    "head": [(-0.45, 0.57, 0.21, 0.24), (-0.62, 0.59, 0.19, 0.22), (-0.70, 0.58, 0.16, 0.20), (-0.80, 0.56, 0.13, 0.19),
          (-0.88, 0.50, 0.13, 0.17), (-0.99, 0.44, 0.115, 0.13), (-1.10, 0.40, 0.085, 0.085), (-1.15, 0.395, 0.09, 0.09)],
    "front": {"x": 0.15, "y": -0.27, "joints": (2, 4),
               "profile": [(0.52, 0.02, 0.08, 0.10, -0.06), (0.40, 0.01, 0.08, 0.095), (0.22, 0.00, 0.05, 0.056), (0.13, 0.00, 0.046, 0.05),
                        (0.06, 0.00, 0.046, 0.05), (0.0, 0.00, 0.05, 0.054)]},
    "hind": {"x": 0.14, "y": 0.31, "joints": (3, 5),
              "profile": [(0.56, 0.00, 0.10, 0.13, -0.06), (0.42, -0.02, 0.11, 0.13), (0.30, -0.045, 0.065, 0.075), (0.20, 0.06, 0.048, 0.055),
                       (0.11, 0.03, 0.044, 0.05), (0.05, 0.01, 0.044, 0.05), (0.0, 0.0, 0.05, 0.056)]},
    "body_keel": [0.10, 0.12, 0.12, 0.10, 0.08, 0.05],
    "tail": [(0.66, 0.59, 0.025), (0.72, 0.63, 0.02), (0.74, 0.67, 0.018), (0.69, 0.69, 0.015)],
    "ear_x": 0.12, "ear_y": -0.80, "ear_z": 0.72,
    "coat": lambda c, n: "black" if c.z < 0.05 else K, "head_coat": lambda c, n: K,
    "tail_coat": lambda c, n: K,
    "extras": _pig_extras,
}


# ===== Goat: slim, a little taller than a sheep, horns and a beard ==============================================
def _goat_coat(c, n):
    if c.z < 0.07:
        return B
    return "brown_coat" if (c.z > 0.62 and abs(c.x) < 0.12) or c.z < 0.28 else W


def _goat_extras(ctx):
    c = ctx.common

    def horns(bm):                                     # scimitar horns: up from the crown, then sweeping back (+y is back) and out, the tips pointing down
        for s in (-1, 1):
            tube(bm, [(s * 0.050, -0.64, 0.89), (s * 0.056, -0.62, 1.00), (s * 0.066, -0.56, 1.11), (s * 0.078, -0.47, 1.17), (s * 0.090, -0.38, 1.16), (s * 0.096, -0.32, 1.11)],
                 [0.030, 0.027, 0.022, 0.017, 0.011, 0.005], n=5)

    ctx.make("horns", horns, lambda c_, n: "horn_cream", ["Head"], sub=0, smooth=False)

    def beard(bm):
        c.add_box(bm, (0, -0.84, 0.55), (0.035, 0.04, 0.09), taper=0.5, rot_deg=(180, 0, 0))

    ctx.make("beard", beard, lambda c_, n: W, ["Head"], sub=0, smooth=False)

    def ears(bm):
        for s in (-1, 1):
            c.add_box(bm, (s * 0.105, -0.68, 0.87), (0.13, 0.07, 0.02), rot_deg=(0, s * 20, s * -12))

    ctx.make("ears", ears, lambda c_, n: "brown_coat", ["Ear_L", "Ear_R"], sub=0, smooth=False)


GOAT = {
    "name": "Goat", "body_n": 10, "head_n": 8,
    # a dairy goat: 0.82 m at the withers, 0.92 m long, a straight back, a head 0.28 m long, legs 0.40 m from the elbow
    "body": [(-0.46, 0.60, 0.13, 0.18), (-0.30, 0.61, 0.165, 0.21), (0.00, 0.60, 0.165, 0.20), (0.28, 0.60, 0.165, 0.20),
          (0.46, 0.62, 0.12, 0.17)],
    "head": [(-0.38, 0.67, 0.09, 0.15), (-0.52, 0.78, 0.075, 0.13), (-0.61, 0.81, 0.07, 0.12), (-0.66, 0.80, 0.07, 0.12),
          (-0.72, 0.74, 0.065, 0.10), (-0.80, 0.67, 0.055, 0.075), (-0.86, 0.63, 0.05, 0.06), (-0.88, 0.62, 0.04, 0.05)],
    "front": {"x": 0.09, "y": -0.30, "joints": (2, 4),
               "profile": [(0.58, 0.03, 0.045, 0.065, -0.03), (0.46, 0.01, 0.048, 0.058), (0.26, 0.00, 0.03, 0.036), (0.14, 0.00, 0.026, 0.03),
                        (0.06, 0.00, 0.026, 0.03), (0.0, 0.00, 0.032, 0.04)]},
    "hind": {"x": 0.085, "y": 0.32, "joints": (3, 5),
              "profile": [(0.62, 0.00, 0.055, 0.075, -0.03), (0.50, -0.01, 0.065, 0.085), (0.36, -0.03, 0.04, 0.048), (0.24, 0.06, 0.03, 0.034),
                       (0.13, 0.03, 0.026, 0.03), (0.06, 0.01, 0.026, 0.03), (0.0, 0.0, 0.032, 0.04)]},
    "body_keel": [0.25, 0.30, 0.28, 0.18, 0.10],
    "tail": [(0.70, 0.45, 0.025), (0.76, 0.48, 0.022), (0.78, 0.50, 0.018), (0.78, 0.52, 0.01)],
    "ear_x": 0.10, "ear_y": -0.68, "ear_z": 0.87,
    "coat": _goat_coat, "head_coat": lambda c, n: "brown_coat" if c.y > -0.72 else W, "tail_coat": lambda c, n: W,
    "extras": _goat_extras,
}


SPECIES = {"cow": COW, "horse": HORSE, "sheep": SHEEP, "pig": PIG, "goat": GOAT}

import species_pets
SPECIES.update(species_pets.DOGS)
SPECIES.update(species_pets.DOG_SKINS)
SPECIES.update(species_pets.CATS)
import species_wild
SPECIES.update(species_wild.WILD)
