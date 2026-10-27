"""Heads, faces, hands and joints for the humanoid aliens (Grey, Shadow Entity, Reptilian, Nordic), used by gp_builder.py.

Everything is in the person builder's own units, before the rig's scale and the head's scale are applied (gp_builder scales the head about the neck's
top, so a face made here sits on the head at any head_scale). The skeleton is the shared one (humanoid_rig.py); nothing here moves a bone.

 Skull          the lofted head as a surface: where its front is at (x, z) and which way it faces, so a feature can sit ON it instead of hanging in front of it
 dome()         a faceted cap that follows that surface: an eye, a pupil, a brow, a nostril; its rim is buried in the skull, its middle stands proud
 HEADS          one ring table per race (z, centre y, half x, half y), the same shape as gp_builder.HEAD
 face_parts()   the parts of a face as (name, builder, palette colour): the builder draws into a bmesh, gp_builder makes each one a mesh weighted to the Head bone
 fingers()      the long fingers of the Grey and the Shadow Entity (thin, no claws) and the clawed ones of the Reptilian, a thumb each, joined to the end of the arm
 pelvis_rings() / shoulder_ball()   the hip block that covers both hip joints and the ball that covers a shoulder joint, so the legs and arms do not open a
                                    gap against the torso when they swing (the limbs hinge at the skeleton's joints, which are outside the narrow torsos)
"""

from math import cos, isclose, radians, sin, sqrt

import bmesh
from mathutils import Vector

import common

# ----------------------------------------------------------------------------------------------------------------------
# Heads: (z, centre y, half width x, half depth y) like gp_builder.HEAD. The first ring is where the neck goes in (z 1.60), the top is about z 1.845-1.86.
# ----------------------------------------------------------------------------------------------------------------------

HEADS = {
    # the Grey: wide across the temples and the back of the skull, a small narrow chin; head_scale 2.05 makes it the huge head
    "grey": [(1.60, 0.002, 0.056, 0.060), (1.65, -0.002, 0.078, 0.082), (1.705, -0.006, 0.100, 0.102), (1.765, 0.000, 0.108, 0.112),
             (1.815, 0.010, 0.092, 0.104), (1.845, 0.014, 0.050, 0.062)],
    # the Shadow Entity: long and narrow, a pointed chin, a smooth skull
    "shadow": [(1.60, 0.000, 0.056, 0.056), (1.650, -0.002, 0.068, 0.082), (1.710, -0.004, 0.084, 0.098), (1.785, -0.002, 0.086, 0.100),
               (1.835, 0.004, 0.068, 0.082), (1.862, 0.008, 0.036, 0.046)],
    # the Reptilian: a broad flat skull with a heavy brow and cheeks, the snout is a separate part
    "reptilian": [(1.60, -0.008, 0.056, 0.064), (1.65, -0.016, 0.082, 0.092), (1.705, -0.012, 0.094, 0.100), (1.760, 0.000, 0.092, 0.098),
                  (1.808, 0.010, 0.074, 0.084), (1.836, 0.014, 0.042, 0.052)],
}


class Skull:
    """A lofted head as a surface. front_y(x, z) is where the front of the polygon is, normal(x, z) points out of it (towards -y)."""

    def __init__(self, rings, n=8, p=2.4):
        self.rings, self.n = rings, n
        self.unit = common._superellipse(n, p)

    def params(self, z):
        r = self.rings
        z = min(max(z, r[0][0]), r[-1][0])
        for a, b in zip(r, r[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0])
                return tuple(a[i] + (b[i] - a[i]) * t for i in (1, 2, 3))
        return r[-1][1:]

    def front_y(self, x, z):
        cy, hx, hy = self.params(z)
        x = max(-hx * 0.97, min(hx * 0.97, x))              # a feature never runs off the side of the head: it stays on the front surface
        pts = [(hx * u, cy + hy * v) for u, v in self.unit]
        best = None
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            lo, hi = min(x0, x1), max(x0, x1)
            if hi - lo < 1e-9 or not (lo - 1e-9 <= x <= hi + 1e-9):
                continue
            y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            if best is None or y < best:
                best = y
        if best is None:                                  # beyond the widest point: the side of the head
            best = cy
        return best

    def point(self, x, z, off=0.0):
        """The surface point at (x, z), moved out along the normal by off (negative is into the skull)."""
        x = self.clamp_x(x, z)
        y = self.front_y(x, z)
        if isclose(off, 0.0, abs_tol=1e-9):
            return Vector((x, y, z))
        n = self.normal(x, z)
        return Vector((x, y, z)) + n * off

    def clamp_x(self, x, z):
        """x kept on the head's front: a feature that would run off the side of the head is held at its edge, never in the air beside it."""
        hx = self.params(z)[1] * 0.97
        return max(-hx, min(hx, x))

    def normal(self, x, z, h=0.004):
        dydx = (self.front_y(x + h, z) - self.front_y(x - h, z)) / (2 * h)
        dydz = (self.front_y(x, z + h) - self.front_y(x, z - h)) / (2 * h)
        return Vector((dydx, -1.0, dydz)).normalized()


# ----------------------------------------------------------------------------------------------------------------------
# dome: a faceted cap on the skull
# ----------------------------------------------------------------------------------------------------------------------

def _almond(n=12):
    """A lens with pointed ends, the lower edge a little flatter than the upper."""
    pts = []
    for i in range(n):
        a = 2 * 3.141592653589793 * i / n
        c, s_ = cos(a), sin(a)
        z = (abs(s_) ** 1.45) * (1 if s_ >= 0 else -0.82)
        pts.append((c, z))
    return pts


ALMOND = _almond()
ROUND = [(cos(radians(a)), sin(radians(a))) for a in range(0, 360, 45)]
SLIT = [(0.0, 1.0), (0.7, 0.0), (0.0, -1.0), (-0.7, 0.0)]
BAR = [(-1.0, 0.0), (-0.5, 0.8), (0.5, 0.8), (1.0, 0.0), (0.5, -0.8), (-0.5, -0.8)]


def dome(bm, skull, cx, cz, hw, hh, sx=1, outline=ROUND, tilt=0.0, bulge=0.012, rim=0.003, base=0.0, lift=None, rings=(1.0, 0.6)):
    """A cap on the skull at (cx, cz): the outline (a polygon in units of hw and hh around the centre, tilted tilt degrees) sits on the surface with its
    rim buried rim into the skull and the middle bulge above it, in rings that shrink to an apex. sx = -1 mirrors it to the other side of the head
    (cx stays the distance from the middle). lift(x, z) adds a height at a point: a pupil that follows an eyeball's curve."""
    t = radians(tilt)
    ct, st = cos(t), sin(t)

    def spot(u, w, s):
        a, b = u * s * hw, w * s * hh
        return sx * (cx + a * ct - b * st), cz + a * st + b * ct

    layers = []
    for k, s in enumerate(rings):
        layer = []
        for u, w in outline:
            x, z = spot(u, w, s)
            off = base + (-rim if k == 0 else bulge * sqrt(max(0.0, 1.0 - s * s))) + (lift(x, z) if lift else 0.0)
            layer.append(bm.verts.new(skull.point(x, z, off)))
        layers.append(layer)
    x, z = spot(0.0, 0.0, 0.0)
    apex = bm.verts.new(skull.point(x, z, base + bulge + (lift(x, z) if lift else 0.0)))
    m = len(outline)
    made = []
    for a, b in zip(layers, layers[1:]):
        for i in range(m):
            made.append(bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i])))
    for i in range(m):
        made.append(bm.faces.new((layers[-1][i], layers[-1][(i + 1) % m], apex)))
    out = skull.normal(*spot(0.0, 0.0, 0.0))
    for f in made:
        f.normal_update()
        if f.normal.dot(out) < 0:
            f.normal_flip()
    return layers


def bulb(cx, cz, hw, hh, bulge, tilt=0.0, rim=0.003, rings=(1.0, 0.6)):
    """The height of a dome(...) of this size above the skull at world (x, z), as the faceted cap really is: straight lines in the normalized radius
    through its rings (the rim buried rim, each inner ring bulge * sqrt(1 - s^2), the apex bulge). For lift=, so a pupil or a glint lies on the eye and
    not above it (0 outside it)."""
    t = radians(tilt)
    ct, st = cos(t), sin(t)
    knots = [(1.0, -rim)] + [(s_, bulge * sqrt(max(0.0, 1.0 - s_ * s_))) for s_ in rings[1:]] + [(0.0, bulge)]

    def h(x, z):
        a, b = abs(x) - cx, z - cz
        u, w = (a * ct + b * st) / hw, (-a * st + b * ct) / hh
        r = sqrt(u * u + w * w)
        if r >= 1.0:
            return 0.0
        for (s0, h0), (s1, h1) in zip(knots, knots[1:]):
            if s1 <= r <= s0:
                return h1 + (h0 - h1) * (r - s1) / (s0 - s1)
        return bulge
    return h


# ----------------------------------------------------------------------------------------------------------------------
# Faces
# ----------------------------------------------------------------------------------------------------------------------

def _grey(skull, o):
    def eyes(bm):
        for sx in (-1, 1):
            dome(bm, skull, 0.050, 1.703, 0.042, 0.034, sx, ALMOND, tilt=20, bulge=0.006, rim=0.003)

    eye_h = bulb(0.050, 1.703, 0.042, 0.034, 0.006, tilt=20, rim=0.003)

    def glints(bm):                                   # a slightly paler gleam on the top outer edge of each eye: the black reads as a curved glassy surface
        for sx in (-1, 1):
            dome(bm, skull, 0.062, 1.711, 0.009, 0.0055, sx, ROUND, tilt=20, bulge=0.0020, rim=-0.0014, lift=eye_h, rings=(1.0,))

    def nostrils_mouth(bm):
        for sx in (-1, 1):
            dome(bm, skull, 0.0075, 1.664, 0.0045, 0.0030, sx, SLIT, bulge=0.0015, rim=0.002, rings=(1.0,))
        dome(bm, skull, 0.0, 1.634, 0.024, 0.0028, 1, BAR, bulge=0.0015, rim=0.002, rings=(1.0,))
    return [("eyes", eyes, "black"), ("glints", glints, "alien_dark"), ("mouth", nostrils_mouth, "metal_dark")]


def _shadow(skull, o):
    def eyes(bm):                                     # narrow glowing slits that wrap round the face, their outer ends raised (a scowl)
        for sx in (-1, 1):
            dome(bm, skull, 0.040, 1.714, 0.036, 0.0135, sx, ALMOND, tilt=16, bulge=0.005, rim=0.003)
    return [("eyes", eyes, o["eyes"])]


def _nordic(skull, o):
    def eyes(bm):
        for sx in (-1, 1):
            dome(bm, skull, 0.038, 1.710, 0.020, 0.0125, sx, ALMOND, tilt=8, bulge=0.005, rim=0.002)

    def brows(bm):
        for sx in (-1, 1):
            dome(bm, skull, 0.038, 1.733, 0.026, 0.0045, sx, BAR, tilt=10, bulge=0.004, rim=0.003, rings=(1.0,))

    def nose(bm):                                     # a small wedge with a point, a bridge and a base
        common.loft(bm, [common.ring_y(y, 0.0, cz, hx, hz, n=4, p=2.0)
                         for y, cz, hx, hz in ((-0.090, 1.700, 0.009, 0.020), (-0.110, 1.687, 0.008, 0.019), (-0.117, 1.674, 0.010, 0.010))])

    def mouth(bm):
        dome(bm, skull, 0.0, 1.640, 0.020, 0.0045, 1, BAR, bulge=0.003, rim=0.002, rings=(1.0,))
    return [("eyes", eyes, o["eyes"]), ("brows", brows, o["hair"]), ("nose", nose, o["skin"]), ("mouth", mouth, "skin")]


def _reptilian(skull, o):
    eye = {"cx": 0.066, "cz": 1.740, "hw": 0.024, "hh": 0.024, "bulge": 0.019}
    bulge_fn = bulb(eye["cx"], eye["cz"], eye["hw"], eye["hh"], eye["bulge"], rim=0.004)

    def snout(bm):                                    # the upper jaw: broad at the face and tapering to the nostrils, a ridge down its top
        common.loft(bm, [common.ring_y(y, 0.0, cz, hx, hz, n=6, p=2.2)
                         for y, cz, hx, hz in ((-0.060, 1.704, 0.050, 0.044), (-0.105, 1.698, 0.047, 0.040), (-0.155, 1.691, 0.041, 0.034),
                                               (-0.205, 1.685, 0.032, 0.027), (-0.236, 1.682, 0.025, 0.022))])
        for sx in (-1, 1):                            # the nostril bumps at its tip
            common.add_box(bm, (sx * 0.011, -0.222, 1.700), (0.010, 0.016, 0.010))

    def jaw(bm):                                      # the lower jaw, a little shorter and deeper
        common.loft(bm, [common.ring_y(y, 0.0, cz, hx, hz, n=6, p=2.2)
                         for y, cz, hx, hz in ((-0.040, 1.652, 0.046, 0.020), (-0.095, 1.652, 0.046, 0.021), (-0.150, 1.655, 0.039, 0.017),
                                               (-0.200, 1.656, 0.028, 0.013), (-0.222, 1.656, 0.020, 0.010))])

    def mouth(bm):                                    # the dark line where the jaws meet, and the nostrils
        common.add_box(bm, (0, -0.145, 1.663), (0.056, 0.150, 0.0045))
        for sx in (-1, 1):
            common.add_box(bm, (sx * 0.0110, -0.2325, 1.703), (0.004, 0.006, 0.006))

    def teeth(bm):                                    # a row of small points along the upper jaw's edge
        for sx in (-1, 1):
            for y, hx in ((-0.095, 0.045), (-0.130, 0.041), (-0.165, 0.037), (-0.200, 0.030)):
                common.add_box(bm, (sx * (hx - 0.004), y, 1.678), (0.0055, 0.0070, 0.026), rot_deg=(180, 0, 0), taper=0.25)      # tall: its top is inside the snout, the point hangs out of it

    def eyes(bm):
        for sx in (-1, 1):
            dome(bm, skull, eye["cx"], eye["cz"], eye["hw"], eye["hh"], sx, ROUND, bulge=eye["bulge"], rim=0.004)

    def pupils(bm):
        for sx in (-1, 1):
            dome(bm, skull, eye["cx"] - 0.007, eye["cz"], 0.0048, 0.014, sx, SLIT, bulge=0.0025, rim=-0.0016, lift=bulge_fn, rings=(1.0, 0.5))

    def brows(bm):                                    # a heavy ridge over each eye, its outer end lifted
        for sx in (-1, 1):
            dome(bm, skull, 0.046, 1.772, 0.030, 0.009, sx, BAR, tilt=12, bulge=0.013, rim=0.004, rings=(1.0,))
    return [("snout", snout, o["skin"]), ("jaw", jaw, "mould"), ("mouth", mouth, "black"), ("teeth", teeth, "horn_cream"),
            ("eyes", eyes, "paint_yellow"), ("pupils", pupils, "black"), ("brows", brows, o["skin"])]


def face_parts(face, skull, o):
    """[(part name, builder(bm), palette colour)] for a race's face."""
    return {"grey": _grey, "shadow": _shadow, "nordic": _nordic, "reptilian": _reptilian}[face](skull, o)


# ----------------------------------------------------------------------------------------------------------------------
# Hands: the arm ends in a flat paddle at |x| 0.87 (gp_builder.ARM); these fingers grow out of it
# ----------------------------------------------------------------------------------------------------------------------

HANDS = {   # fingers: (offset y from the arm's centre line, length, half thickness at the base, droop in metres at the tip); thumb: (unused, length, half thickness, droop)
    "grey": {"fingers": [(-0.018, 0.16, 0.0105, 0.030), (0.0, 0.18, 0.0105, 0.032), (0.018, 0.15, 0.0100, 0.028)],
                 "thumb": (0.15, 0.10, 0.0105, -0.045)},
    "shadow": {"fingers": [(-0.016, 0.24, 0.0075, 0.060), (0.0, 0.27, 0.0075, 0.064), (0.016, 0.22, 0.0075, 0.058)],
                   "thumb": (0.15, 0.13, 0.0075, -0.050)},
    "reptilian": {"fingers": [(-0.030, 0.10, 0.015, 0.020), (0.0, 0.11, 0.015, 0.022), (0.030, 0.095, 0.015, 0.020)],
                      "thumb": (0.15, 0.07, 0.015, -0.045), "claws": True},
}


def fingers(bm, side, spec):
    """The fingers of one hand (side +1 is the left, +x): lofted tapering prisms that start 2 cm inside the paddle (it ends at |x| 0.87). With claws=True a
    finger has a third ring, so its last 40% (the faces with |x| over 0.935, which gp_builder paints) is the claw."""
    x0 = 0.85
    ts = (0.0, 0.6, 1.0) if spec.get("claws") else (0.0, 1.0)
    for dy, length, r, droop in spec["fingers"]:
        rings = []
        for t in ts:
            x = x0 + (length + 0.02) * t
            rings.append(common.ring_x(side * x, 0.064 + dy * (1.0 + 0.25 * t), 1.440 - droop * t * t, r * (1.0 - 0.55 * t), r * (1.0 - 0.55 * t) * 0.8, n=4))
        common.loft(bm, rings)
    length, r, droop = spec["thumb"][1:]             # the thumb: from the heel of the hand, forward (-y) and down
    rings = []
    for t in (0.0, 1.0):
        x = 0.79 + 0.9 * length * t * cos(radians(35))
        rings.append(common.ring_x(side * x, 0.046 - 0.55 * length * t, 1.4385 + droop * t, r * (1.0 - 0.45 * t), r * 0.85 * (1.0 - 0.45 * t), n=4))
    common.loft(bm, rings)


# ----------------------------------------------------------------------------------------------------------------------
# Joints
# ----------------------------------------------------------------------------------------------------------------------

def pelvis_rings(girth):
    """The hip block: rings (z, centre y, half x, half y) from below the hip joints (z 0.932, x +-0.089) to inside the torso's first ring (z 0.90-1.05),
    as wide as the outer edge of the legs, so a leg swinging at the hip still meets something."""
    reach = 0.089 + 0.095 * girth                      # the outer edge of the leg's top
    return [(0.842, 0.010, reach * 0.86, 0.092 * girth + 0.020), (0.905, 0.012, reach, 0.112 * girth + 0.026),
            (0.965, 0.012, reach * 0.96, 0.108 * girth + 0.024), (1.030, 0.010, reach * 0.55, 0.066 * girth)]


def shoulder_ball(bm, side, girth):
    """A ball on the shoulder joint (the arm's pivot at |x| 0.192, y 0.065, z 1.441) a little larger than the top of the arm, so the arm swings inside it."""
    r = 0.082 * girth * 1.12 + 0.003
    res = bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=r)
    bmesh.ops.translate(bm, verts=res["verts"], vec=(side * 0.192, 0.065, 1.441))
