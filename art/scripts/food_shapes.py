"""The shaped foods of contents.py: the ones a box or a ball cannot make (issue #344, notes in docs/art/food-notes.md).

Each function adds its model to a Prop `p` (origin on the floor, facing -Y, real size). They use `Prop.quads` (a curved sheet: leaves, husks, cups) and
`Prop.poly` (an oriented face) as well as lofts, with the sheets kept apart by a few millimetres so the parts of a model never pass through each other:
`audit.py` with AUDIT_CLIP = True checks that.
"""

from math import cos, pi, radians, sin

from mathutils import Vector

import common
import props_lib


def _table(rows, t):
    """Piecewise-linear value of rows [(t, value), ...] at t (clamped at the ends)."""
    if t <= rows[0][0]:
        return rows[0][1]
    for (t0, v0), (t1, v1) in zip(rows, rows[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return rows[-1][1]


# ===== Banana ===================================================================================================
# A crescent about 20 cm along its curve lying on its back (the bend is a smile seen from the front), a five-ridged skin
# (ten points round, every other one pulled in), a green stalk with a cut brown end at the left and a black tip at the right.
BANANA_RADIUS = ((0.0, 0.0065), (0.14, 0.0085), (0.26, 0.0140), (0.42, 0.0172), (0.58, 0.0178), (0.74, 0.0160), (0.88, 0.0110), (0.96, 0.0070), (1.0, 0.0058))


def banana(p):
    length, bend = 0.20, 0.175                       # along the curve, radius of the curve
    arc = length / bend
    n = 10

    def ring(t):
        a = (t - 0.5) * arc
        centre = Vector((bend * sin(a), 0.0, bend * (1 - cos(a))))
        up = Vector((-sin(a), 0.0, cos(a)))          # towards the inside of the bend
        r = _table(BANANA_RADIUS, t)
        pts = []
        for k in range(n):
            f = 1.0 if k % 2 == 0 else 0.84          # ridge, valley
            ang = 2 * pi * k / n
            pts.append(centre + up * (r * f * cos(ang)) + Vector((0.0, r * f * sin(ang), 0.0)))
        return pts

    stations = [-0.04, 0.0, 0.065, 0.13, 0.26, 0.42, 0.58, 0.74, 0.88, 0.96, 1.0]
    rings = {t: ring(t) for t in stations}
    dz = -min(v.z for r in rings.values() for v in r)
    lift = Vector((0.0, 0.0, dz))

    def loft(colour, ts, cap):
        p.loft_rings(colour, [[v + lift for v in rings[t]] for t in ts], cap=cap)

    loft("bark", [-0.04, 0.0], True)                  # the cut end of the stalk
    loft("corn_green", [0.0, 0.065, 0.13], False)
    loft("banana_yellow", [0.13, 0.26, 0.42, 0.58, 0.74, 0.88, 0.96], False)
    loft("black", [0.96, 1.0], True)                  # the dark tip


# ===== Cabbage ==================================================================================================
# A pale core ball with its stem cut flat, wrapped in five leaves: each a shell over a spread of the head, one layer outside the last, lighter inside and
# darker outside, with a ruffled (zig-zag) edge and a pale midrib raised a millimetre on it.
CABBAGE_LEAVES = ("corn_leaf", "corn_green", "grass", "leaf_dark", "leaf_dark")


def cabbage(p):
    core, sq, cz = 0.060, 0.92, 0.072
    ball_rings = [(cz + sq * core * cos(phi), core * sin(phi)) for phi in (2.70, 2.25, 1.75, 1.2, 0.7, 0.25)]       # the core, an ellipsoid
    props_lib.lathe(p, "siding_green", ball_rings, n=8)
    p.cyl("siding_green", (0, 0, ball_rings[0][0] / 2), 0.022, ball_rings[0][0], n=8)                              # the stem, cut flat on the floor
    jitter = (0.0, 9.0, -6.0, 11.0, -8.0)
    ncol, nrow = 6, 5
    for k, colour in enumerate(CABBAGE_LEAVES):
        radius = 0.071 + 0.006 * k
        centre_az = radians(72 * k + jitter[k])
        span = radians(68)
        top = 0.30 + 0.07 * k
        bottom = 2.55 - 0.03 * k

        def at(az, phi, r):
            return Vector((r * sin(phi) * cos(az), r * sin(phi) * sin(az), cz + sq * r * cos(phi)))
        grid = []
        for i in range(nrow):
            row = []
            for j in range(ncol):
                u = j / (ncol - 1)
                zig = 1 if j % 2 else 0
                phi0 = top + 0.07 * zig
                phi1 = bottom - 0.09 * (1 - zig)
                row.append(at(centre_az + span * (2 * u - 1), phi0 + (phi1 - phi0) * i / (nrow - 1), radius))
            grid.append(row)
        p.quads(colour, grid, away_from=(0, 0, cz), thick=0.0015, walls=False)
        rib = []
        for i in range(nrow):
            phi = (top + 0.035) + ((bottom - 0.045) - (top + 0.035)) * i / (nrow - 1)
            w = 0.05 * (0.4 + 0.6 * (1 - i / (nrow - 1)))
            rib.append([at(centre_az - w, phi, radius + 0.0006), at(centre_az + w, phi, radius + 0.0006)])
        p.quads("siding_green", rib, away_from=(0, 0, cz))


# ===== Lettuce ==================================================================================================
# A short pale stub, three rings of leaves round it: five wide flat outer leaves (darker, ruffled edges), three cupped middle leaves and three upright
# heart leaves (the palest). Each leaf is a cupped sheet seen from both sides: pale at the base, greener at the edge.
LETTUCE_RINGS = (
    # count, azimuth offset (deg), root radius, root height, tip radius, rise, half width, cup, ruffle, base colour, edge colour
    (5, 0.0, 0.021, 0.008, 0.088, 0.068, 0.042, 0.70, 0.007, "corn_leaf", "corn_green"),
    (3, 36.0, 0.012, 0.0185, 0.062, 0.088, 0.036, 0.70, 0.005, "lettuce_heart", "corn_leaf"),
    (3, 78.0, 0.005, 0.0185, 0.034, 0.100, 0.026, 0.60, 0.003, "lettuce_heart", "lettuce_heart"),
)
LEAF_WIDTH = (0.12, 0.85, 1.0, 0.5)                 # half width along the leaf (root to tip) as a fraction of the widest


def lettuce(p):
    p.cyl("lettuce_heart", (0, 0, 0.008), 0.020, 0.016, n=8)
    for ring_k, (count, az0, rho0, z0, rho1, rise, half, cup, ruffle, base_c, edge_c) in enumerate(LETTUCE_RINGS):
        step = radians(360.0 / count)
        for m in range(count):
            az = radians(az0) + m * step
            er = Vector((cos(az), sin(az), 0.0))
            et = Vector((-sin(az), cos(az), 0.0))
            ss = (0.0, 0.34, 0.68, 1.0)
            grid = []
            for i, s in enumerate(ss):
                rho = rho0 + (rho1 - rho0) * s
                z = z0 + rise * (s ** (1.8 if ring_k == 0 else 1.05))
                w = min(half * LEAF_WIDTH[i], 0.85 * rho * sin(step / 2))
                row = []
                for u in (-1.0, -0.5, 0.0, 0.5, 1.0):
                    zz = z + cup * w * u * u + ruffle * u * u * sin(s * 2 * pi * 1.5 + m)
                    row.append(er * rho + et * (w * u) + Vector((0, 0, zz)))
                grid.append(row)
            facing = er * -0.4 + Vector((0, 0, 0.6))
            split = 2                                    # rows 0..split in the base colour, split..3 in the edge colour (they share a row)
            p.quads(base_c, grid[:split + 1], thick=0.002, walls=False, facing=facing)
            p.quads(edge_c, grid[split:], thick=0.002, walls=False, facing=facing)


# ===== Corn =====================================================================================================
# The ear: a stalk end, the yellow cob, and six husk leaves in two layers (the outer five millimetres clear of the inner) wrapped round it, wide at the
# base and narrowing to a point that peels away from the cob at the tip, so the top of the ear shows yellow.
COB_RADIUS = ((0.03, 0.012), (0.06, 0.027), (0.12, 0.030), (0.17, 0.026), (0.20, 0.012), (0.207, 0.004))


def corn(p):
    p.cyl("corn_green", (0, 0, 0.015), 0.0165, 0.03, n=8)
    props_lib.lathe(p, "corn_cob", [(z, r) for z, r in COB_RADIUS], n=8)
    nrow, ncol = 5, 4
    for k in range(6):
        outer = k % 2
        colour = "corn_green" if outer else "corn_leaf"
        gap = 0.0125 if outer else 0.0055
        az = radians(60 * k + (30 if outer else 0))
        base_half = radians(53)
        length = 0.150 if outer else 0.135
        grid = []
        for i in range(nrow):
            s = i / (nrow - 1)
            z0 = 0.0315 + length * s
            peel = 0.040 * min(1.0, max(0.0, (z0 - 0.115) / 0.065)) ** 2        # by height, so the two layers peel together and never cross
            z = z0 - 0.35 * peel
            rho = _table(COB_RADIUS, z) + gap + peel
            if i == 0:
                rho = 0.0163 if not outer else 0.0215        # the root sits on the stalk's top
            half = base_half * (1 - 0.9 * s ** 1.5)
            grid.append([Vector((rho * cos(az + half * u), rho * sin(az + half * u), z)) for u in (-1.0, -1 / 3, 1 / 3, 1.0)])
        p.quads(colour, grid, thick=0.002, walls=False, away_from=(0, 0, 0.1))


# ===== Eggs and the carton ======================================================================================
EGG_RINGS = ((0.0, 0.0045), (0.016, 0.0150), (0.032, 0.0215), (0.046, 0.0175), (0.0577, 0.0040))      # (height from the point, radius): point down
EGG_COLOURS = ("egg_white", "egg_brown", "egg_white", "egg_white", "egg_brown", "egg_white",
               "egg_brown", "egg_white", "egg_blue", "egg_brown", "egg_blue", "egg_white")
CARTON = {"hx": 0.152, "hy": 0.053, "wall": 0.003, "floor": 0.004, "top": 0.034}     # outside half length and width of the tray, its walls, the rim height
CUP_BOTTOM, CUP_TOP, CUP_RIM = 0.0135, 0.0215, 0.030                       # cup radius at the floor and at the rim, rim height


def egg(p, colour, x, y, z):
    p.loft_rings(colour, [common.ring_z(z + h, x, y, r, r, n=6) for h, r in EGG_RINGS])


def egg_carton(p, rest=-105.0):
    c = CARTON
    hx, hy, t, fl, zt = c["hx"], c["hy"], c["wall"], c["floor"], c["top"]
    tray = "stucco"
    p.box(tray, (0, 0, fl / 2), (2 * hx, 2 * hy, fl))
    h = zt - fl
    for sy in (-1, 1):
        p.box(tray, (0, sy * (hy - t / 2), fl + h / 2), (2 * hx, t, h))
    for sx in (-1, 1):
        p.box(tray, (sx * (hx - t / 2), 0, fl + h / 2), (t, 2 * hy - 2 * t, h))
    p.box("label_red", (0, -hy - 0.0008, 0.019), (0.20, 0.0016, 0.016))              # the label band on the front
    k = 0
    for r in range(2):
        for col in range(6):
            x, y = (col - 2.5) * 0.0487, (r - 0.5) * 0.050
            rings = [common.ring_z(CUP_RIM, x, y, CUP_TOP, CUP_TOP, n=6), common.ring_z(fl + 0.0008, x, y, CUP_BOTTOM, CUP_BOTTOM, n=6)]
            p.quads(tray, [list(ring) for ring in rings], wrap=True, toward=(x, y, 0.017), thick=0.0015, walls=False)
            egg(p, EGG_COLOURS[k], x, y, fl)
            k += 1
    # the lid: a shallow box over the eggs, hinged along the back edge (opens up and back, exported open)
    HX, HY, zl = hx + 0.0045, hy + 0.0045, 0.070
    wl = zl - zt
    with p.part("Lid", pivot=(0, HY, zt), kind="hinge", axis="x", limit=-105.0, rest=rest):
        p.box(tray, (0, 0, zl + 0.0015), (2 * HX, 2 * HY, 0.003))
        p.box(tray, (0, -HY + 0.0015, zt + wl / 2), (2 * HX, 0.003, wl))
        p.box(tray, (0, HY - 0.0015, zt + wl / 2), (2 * HX, 0.003, wl))
        for sx in (-1, 1):
            p.box(tray, (sx * (HX - 0.0015), 0, zt + wl / 2), (0.003, 2 * HY - 0.006, wl))
        p.box("label_red", (0, 0, zl + 0.003 + 0.0008), (0.16, 0.050, 0.0016))


# ===== Cheese ===================================================================================================
# A wedge cut from a wheel: the curved rind at the front, a top that slopes down to the point at the back, and the two flat cut faces with a few holes (square
# dents, each with a darker floor) in a grid of cells.
def cheese(p):
    R, half = 0.09, radians(32)
    ay = R / 2                                           # the point of the wedge, at the back
    h0, h1 = 0.022, 0.052                                # thickness at the point and at the rind
    apex_b, apex_t = Vector((0, ay, 0)), Vector((0, ay, h0))
    arc = [(-half + 2 * half * i / 4) for i in range(5)]
    pb = [Vector((R * sin(a), ay - R * cos(a), 0.0)) for a in arc]
    pt = [Vector((v.x, v.y, h1)) for v in pb]
    inside = Vector((0, ay - R * 0.45, 0.02))
    for i in range(4):
        p.poly("cheese_rind", [pb[i], pb[i + 1], pt[i + 1], pt[i]], away_from=inside)
        p.poly("cheese_cut", [apex_t, pt[i], pt[i + 1]], facing=(0, 0, 1))
        p.poly("cheese_rind", [apex_b, pb[i], pb[i + 1]], facing=(0, 0, -1))
    nt, nv = 6, 4
    holes = (((3, 1), (4, 2), (2, 2)), ((2, 1), (3, 2), (4, 1)))
    for side, end in enumerate((0, 4)):
        d = pb[end] - apex_b
        d.z = 0.0
        out = Vector((d.y, -d.x, 0.0)).normalized()
        if out.x * pb[end].x < 0:
            out = -out

        def q(i, j):
            t = i / nt
            hh = h0 + (h1 - h0) * t
            return apex_b + d * t + Vector((0, 0, hh * j / nv))
        pits = holes[side]
        for i in range(nt):
            for j in range(nv):
                corners = [q(i, j), q(i + 1, j), q(i + 1, j + 1), q(i, j + 1)]
                if (i, j) in pits:
                    c = sum(corners, Vector()) / 4
                    inner = [c + (v - c) * 0.65 - out * 0.009 for v in corners]
                    for m in range(4):
                        p.poly("cheese_hole", [corners[m], corners[(m + 1) % 4], inner[(m + 1) % 4], inner[m]], toward=c - out * 0.004)
                    p.poly("cheese_hole", inner, facing=out)
                else:
                    p.poly("cheese_cut", corners, facing=out)


# ===== Batch 2: produce, bread, sausages, fish, drumstick, bags, pickle jar =====================================
def revolve(p, colour, rings, n=8, lobe=1.0):
    """A solid of revolution from (height, radius) rings, bottom to top; every other point is pulled in by `lobe` (ribs on a pumpkin, the lobes of a tomato)."""
    out = []
    for z, r in rings:
        out.append([Vector((max(r, 0.0001) * (1.0 if k % 2 == 0 else lobe) * cos(2 * pi * k / n), max(r, 0.0001) * (1.0 if k % 2 == 0 else lobe) * sin(2 * pi * k / n), z))
                    for k in range(n)])
    p.loft_rings(colour, out)


def loft_along(p, colour, axis, stations, n=8, cy=0.0, cz=0.0, sharp=2.0):
    """A solid along x or y from stations (position, half width, half height): a loaf, a sausage, a fish. sharp > 2 makes the section boxier."""
    rings = []
    for pos, hw, hh in stations:
        hw, hh = max(hw, 0.0001), max(hh, 0.0001)
        rings.append(common.ring_x(pos, cy, cz, hw, hh, n=n, p=sharp) if axis == "x" else common.ring_y(pos, cy, cz, hw, hh, n=n, p=sharp))
    p.loft_rings(colour, rings)


def apple(p, colour="cloth_red"):
    revolve(p, colour, [(0.0, 0.014), (0.006, 0.030), (0.022, 0.041), (0.044, 0.040), (0.062, 0.031), (0.071, 0.017), (0.064, 0.003)], n=8, lobe=0.96)
    props_lib.rod(p, "bark", (0, 0, 0.060), (0.004, 0, 0.088), w=0.005)
    p.quads("plant_green", [[(0.003, -0.005, 0.084), (0.003, 0.005, 0.084)], [(0.024, -0.009, 0.090), (0.024, 0.009, 0.090)]], thick=0.0015, facing=(0, 0, 1))


def orange(p):
    revolve(p, "food_orange", [(0.0, 0.012), (0.008, 0.028), (0.025, 0.039), (0.045, 0.0395), (0.062, 0.030), (0.077, 0.015), (0.0725, 0.003)], n=9)
    p.cyl("plant_green", (0, 0, 0.0765), 0.011, 0.003, n=6)


def tomato(p):
    revolve(p, "cloth_red", [(0.0, 0.016), (0.008, 0.031), (0.024, 0.040), (0.040, 0.040), (0.054, 0.032), (0.059, 0.017), (0.060, 0.006)], n=10, lobe=0.93)
    pts = [(r * cos(2 * pi * k / 10), r * sin(2 * pi * k / 10), z) for k, (r, z) in enumerate(((0.024, 0.0580) if k % 2 == 0 else (0.009, 0.0615) for k in range(10)))]
    for k in range(10):                                                        # the calyx star as a fan of triangles from its centre (a concave 10-gon would be triangulated by the engine)
        p.poly("plant_green", [(0.0, 0.0, 0.0620), pts[k], pts[(k + 1) % 10]], facing=(0, 0, 1))


def potato(p):
    rings = [(0.0, 0.016, 0.012, 0.0), (0.008, 0.036, 0.026, 0.002), (0.022, 0.046, 0.033, -0.003), (0.036, 0.044, 0.031, 0.003), (0.046, 0.030, 0.023, 0.0), (0.050, 0.012, 0.009, 0.0)]
    p.loft_rings("tan", [[Vector((dx + rx * cos(2 * pi * k / 7 + 0.3), ry * sin(2 * pi * k / 7 + 0.3), z)) for k in range(7)] for z, rx, ry, dx in rings])


def onion(p):
    revolve(p, "golden", [(0.0, 0.010), (0.006, 0.028), (0.022, 0.040), (0.040, 0.039), (0.056, 0.028), (0.068, 0.014), (0.078, 0.006), (0.088, 0.003)], n=8, lobe=0.95)
    p.cyl("dead_wood", (0, 0, 0.0925), 0.0035, 0.009, n=4)
    p.cyl("dead_wood", (0, 0, 0.002), 0.011, 0.004, n=6, top_radius=0.006)     # the root tuft


def carrot(p):
    revolve(p, "food_orange", [(0.0, 0.002), (0.02, 0.008), (0.07, 0.015), (0.12, 0.019), (0.145, 0.0205), (0.150, 0.014)], n=7)
    p.cyl("plant_green", (0, 0, 0.1535), 0.012, 0.007, n=7)
    for dx, dy in ((0.016, 0.0), (-0.01, 0.014), (-0.01, -0.014)):
        props_lib.rod(p, "plant_green", (0, 0, 0.152), (dx, dy, 0.205), w=0.006)


def pumpkin(p):
    k, w = 1.35, 0.92                                                          # taller and narrower than the first sketch: about 30 cm across, 23 cm tall
    revolve(p, "food_orange", [(z * k, r * w) for z, r in [(0.0, 0.07), (0.014, 0.125), (0.045, 0.158), (0.08, 0.162), (0.112, 0.14), (0.13, 0.085), (0.133, 0.04), (0.122, 0.012)]], n=12, lobe=0.90)
    revolve(p, "plant_green", [(0.108 * k, 0.018), (0.116 * k, 0.020), (0.122 * k, 0.022), (0.150 * k, 0.020), (0.168 * k + 0.01, 0.027)], n=5)


def watermelon(p):
    """A long melon lying on the floor, dark stripes from end to end: 12 strips of alternating colour as sheets over one set of rings."""
    n, rx, ry, rz, cz = 12, 0.18, 0.13, 0.125, 0.125
    rings = []
    for k in range(7):
        ph = pi * k / 6
        r = max(sin(ph), 0.0001)
        rings.append([Vector((-rx * cos(ph), ry * r * cos(2 * pi * j / n), cz + rz * r * sin(2 * pi * j / n))) for j in range(n)])
    for k in range(n):
        p.quads("grass" if k % 2 == 0 else "leaf_dark", [[ring[k], ring[(k + 1) % n]] for ring in rings], away_from=(0, 0, cz))


def bread_loaf(p):
    st = [(-0.125, 0.020, 0.018), (-0.115, 0.040, 0.034), (-0.09, 0.050, 0.040), (0.09, 0.050, 0.040), (0.115, 0.040, 0.034), (0.125, 0.020, 0.018)]
    loft_along(p, "crust", "x", st, n=12, cz=0.040, sharp=3.0)
    for x in (-0.05, 0.0, 0.05):                                              # slashes across the top
        p.box("dough", (x, 0, 0.0795), (0.012, 0.05, 0.004), rot=(0, 0, 25))


def baguette(p):
    st = []
    for k in range(9):
        t = k / 8
        r = 0.032 * max(sin(pi * (0.04 + 0.92 * t)), 0.1) ** 0.4
        st.append((-0.35 + 0.7 * t, r, r * 0.9))
    loft_along(p, "crust", "y", st, n=8, cz=0.0288)
    for k in range(5):                                                         # slashes sunk a millimetre into the crust, which is 0.9 r tall at that point
        y = -0.2 + 0.1 * k
        r = 0.032 * max(sin(pi * (0.04 + 0.92 * (y + 0.35) / 0.7)), 0.1) ** 0.4
        p.box("dough", (0, y, 0.0288 + 0.9 * r - 0.001), (0.02, 0.012, 0.004), rot=(0, 0, 35))


def sausages(p):
    p.box("paint_white", (0, 0, 0.004), (0.2, 0.1, 0.008))
    for y in (-0.03, 0.0, 0.03):
        loft_along(p, "rust", "x", [(-0.078, 0.004, 0.004), (-0.07, 0.011, 0.011), (-0.055, 0.0135, 0.0135), (0.055, 0.0135, 0.0135), (0.07, 0.011, 0.011), (0.078, 0.004, 0.004)],
                   n=8, cy=y, cz=0.0212)


def drumstick(p):
    loft_along(p, "crust", "x", [(-0.05, 0.004, 0.004), (-0.04, 0.026, 0.026), (-0.01, 0.036, 0.036), (0.02, 0.030, 0.030), (0.05, 0.016, 0.016), (0.065, 0.011, 0.011)], n=8, cz=0.036)
    p.cyl("horn_cream", (0.095, 0, 0.036), 0.007, 0.07, n=6, axis="x")
    props_lib.ball(p, "horn_cream", (0.135, 0, 0.036), 0.0105, n=6, rings=3)


def fish(p):
    """A fish lying on its side, head to the left: a lofted body, a flat forked tail and an eye."""
    loft_along(p, "fabric_grey", "x", [(-0.17, 0.004, 0.003), (-0.15, 0.028, 0.016), (-0.10, 0.044, 0.026), (0.0, 0.048, 0.028), (0.08, 0.036, 0.022), (0.12, 0.016, 0.012), (0.14, 0.010, 0.008)],
               n=8, cz=0.028)
    p.quads("metal_galv", [[(0.138, -0.008, 0.028), (0.138, 0.008, 0.028)], [(0.19, -0.045, 0.028), (0.19, 0.045, 0.028)]], thick=0.002, facing=(0, 0, 1))
    p.cyl("black", (-0.12, -0.012, 0.0495), 0.006, 0.004, n=6)


def _bag_ring(z, h, hx, hy):
    """Half width and half depth of a pillow bag at height z of h: pinched shut at the bottom and the top, fullest in the middle."""
    f = max(sin(pi * z / h), 0.0) ** 0.5
    return hx * (0.9 + 0.1 * f), 0.006 + (hy - 0.006) * f


def chips_bag(p):
    h, hx, hy = 0.26, 0.10, 0.035
    zs = [0.0, 0.012, 0.045, 0.09, 0.14, 0.19, 0.225, 0.248, 0.26]
    p.loft_rings("paint_yellow", [common.ring_z(z, 0, 0, *_bag_ring(z, h, hx, hy), n=12, p=2.6) for z in zs])
    p.box("paint_yellow", (0, 0, 0.0035), (0.2, 0.012, 0.007))
    p.box("paint_yellow", (0, 0, 0.2635), (0.2, 0.012, 0.007))
    grid = []                                                                  # the label lies on the front: a sheet over an arc of the sections, a millimetre proud
    for k in range(4):
        z = 0.05 + 0.14 * k / 3
        w, d = _bag_ring(z, h, hx, hy)
        grid.append([Vector(((w + 0.0025) * sin(a), -(d + 0.0025) * cos(a), z)) for a in (-0.55 + 1.1 * j / 4 for j in range(5))])
    p.quads("cloth_red", grid, facing=(0, -1, 0))


def sack(p, h, hx, hy, colour, label_colour):
    """A paper sack: a boxy section with a rounded base, the top gathered into a pinched fold with a flat flap, and a label on the front."""
    zs = [0.0, 0.012, 0.15 * h, 0.5 * h, 0.78 * h, 0.9 * h, 0.96 * h, h]
    ws = [0.90, 1.0, 1.0, 1.0, 0.97, 0.93, 0.85, 0.8]
    ds = [0.8, 0.98, 1.0, 1.0, 0.8, 0.45, 0.2, 0.12]
    p.loft_rings(colour, [common.ring_z(z, 0, 0, hx * w, hy * d, n=12, p=3.2) for z, w, d in zip(zs, ws, ds)])
    p.box(colour, (0, 0, h + 0.012), (hx * 1.6, 0.012, 0.024))
    p.box(label_colour, (0, -(hy + 0.0014 + 0.8 * hy) / 2, 0.35 * h), (hx * 1.1, hy * 0.2 + 0.0014, 0.4 * h))        # reaches back into the curved front


def flour_sack(p):
    sack(p, 0.30, 0.12, 0.06, "label_white", "label_blue")


def sugar_bag(p):
    sack(p, 0.24, 0.06, 0.03, "paint_white", "label_blue")


def jar_pickles(p):
    revolve(p, "corn_green", [(0.0, 0.044), (0.006, 0.050), (0.14, 0.050), (0.158, 0.040), (0.166, 0.036)], n=10)
    revolve(p, "label_white", [(0.045, 0.0512), (0.12, 0.0512)], n=10)
    p.cyl("metal_galv", (0, 0, 0.1785), 0.040, 0.025, n=10)
