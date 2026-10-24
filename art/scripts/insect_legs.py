"""Where the beetle, ladybug and firefly are put together, and where their legs join them (plain Python: no Blender, so tests/test_insect_legs.py can check it).

insects.py builds the three beetles from the shapes below, in millimetres, head to -Y, feet on z = 0. A shape is an ellipsoid `(centre, radii)`, or a dome
(`kind="dome"`: the top half of the ellipsoid on a flat base at z = base). The legs hang from the *thorax underside*: every hip sits just inside the
lowest of the `carriers` over it, the knee is out beyond the body (so the thigh really comes out from under it, and nothing pokes through the shell) and the
foot is on the ground, forward of the hip for the front pair and back of it for the hind pair. A leg is (y, hip x, reach, foot offset in y): the knee is
60 % of the reach out and `rise` above the hip.
"""

from math import sqrt

FOOT_Z = 0.5                       # the foot rod rests on z = 0: its centre line is half a width up


def ell(c, r):
    return dict(kind="ellipsoid", c=c, r=r)


def dome(c, r, base):
    """The top half of the ellipsoid (c, r), cut flat at z = base (the shape of a ladybug's back)."""
    return dict(kind="dome", c=c, r=r, base=base)


# ----------------------------------------------------------------------------------------------------------------------
BEETLE = dict(
    elytra=ell((0, 3, 7.0), (7, 10, 4.5)),
    pronotum=ell((0, -7.5, 6.5), (5.5, 3.5, 3.5)),
    head=ell((0, -11.5, 5.7), (3.0, 2.2, 2.5)),
    carriers=("pronotum", "elytra"),
    thorax=(-10.0, 1.0),                                          # y range the three hips lie in
    legs=((-8.0, 3.0, 5.5, -2.0), (-4.0, 3.0, 6.0, 0.4), (0.0, 3.0, 6.3, 2.4)),
    rise=0.6, w=1.2,
)

FIREFLY = dict(
    elytra=ell((0, 0.5, 2.9), (1.8, 3.6, 1.3)),
    tail=ell((0, 4.2, 2.4), (1.5, 1.6, 1.1)),
    pronotum=ell((0, -2.8, 2.9), (1.8, 1.4, 1.1)),
    head=ell((0, -4.4, 2.5), (1.0, 0.8, 0.8)),
    carriers=("pronotum", "elytra"),
    thorax=(-4.2, -0.2),
    legs=((-3.5, 0.9, 2.4, -0.7), (-2.3, 0.9, 2.6, 0.2), (-1.1, 0.9, 2.4, 0.9)),
    rise=0.5, w=0.3,
)

LADYBUG = dict(
    elytra=dome((0, 1.0, 1.5), (3.4, 4.0, 2.7), 1.5),             # the wing covers: one dome, two halves in the rigged model
    pronotum=dome((0, -3.1, 1.5), (2.4, 1.6, 2.0), 1.5),
    belly=ell((0, 1.0, 1.5), (3.0, 3.7, 0.6)),
    head=ell((0, -4.9, 1.9), (1.4, 1.0, 0.9)),
    carriers=("belly",),
    thorax=(-3.0, 1.2),
    legs=((-2.0, 1.2, 2.2, -0.9), (-0.7, 1.7, 3.1, 0.0), (0.7, 1.7, 3.4, 1.0)),
    rise=0.35, w=0.35,
)

BODIES = {"Beetle": BEETLE, "Firefly": FIREFLY, "Ladybug": LADYBUG}


# ----------------------------------------------------------------------------------------------------------------------
def inside(shape, x, y, z, margin=0.0):
    """True if (x, y, z) is within the shape grown by -margin mm (so a positive margin means that far in from the surface)."""
    (cx, cy, cz), (rx, ry, rz) = shape["c"], shape["r"]
    if shape["kind"] == "dome" and z < shape["base"] + margin:
        return False
    rx, ry, rz = rx - margin, ry - margin, rz - margin
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1.0


def underside(shape, x, y):
    """z of the lower surface of the shape over (x, y), or None if it does not reach there."""
    (cx, cy, cz), (rx, ry, rz) = shape["c"], shape["r"]
    t = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
    if t < 0:
        return None
    if shape["kind"] == "dome":
        return shape["base"]
    return cz - rz * sqrt(t)


def surface_z(shape, x, y):
    """z of the upper surface of the shape over (x, y), or None."""
    (cx, cy, cz), (rx, ry, rz) = shape["c"], shape["r"]
    t = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
    return None if t < 0 else cz + rz * sqrt(t)


def surface_normal(shape, x, y, z):
    """Unit normal of the ellipsoid through (x, y, z) (not exactly on it is fine): used to lay spots flat on a dome."""
    (cx, cy, cz), (rx, ry, rz) = shape["c"], shape["r"]
    n = ((x - cx) / rx ** 2, (y - cy) / ry ** 2, (z - cz) / rz ** 2)
    m = sqrt(sum(v * v for v in n)) or 1.0
    return tuple(v / m for v in n)


def hip_z(spec, x, y):
    """Height of the hip: the lowest carrier surface over (x, y), plus half a leg width so the hip rod is buried in the body, not hanging off it."""
    zs = [underside(spec[k], x, y) for k in spec["carriers"]]
    zs = [z for z in zs if z is not None]
    if not zs:
        raise ValueError(f"no carrier over ({x}, {y})")
    return min(zs) + spec["w"] * 0.5


def leg_joints(spec, side, i):
    """(hip, knee, foot) of leg i (0 = front) on `side` (+1 left, -1 right)."""
    y, x, reach, dy = spec["legs"][i]
    hz = hip_z(spec, x, y)
    hip = (side * x, y, hz)
    knee = (side * (x + reach * 0.6), y + dy * 0.45, hz + spec["rise"])
    foot = (side * (x + reach), y + dy, FOOT_Z * spec["w"])
    return hip, knee, foot
