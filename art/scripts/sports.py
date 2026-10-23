"""Sports gear: balls, nets and goals, and equipment (bats, rackets, sticks, a helmet, a skateboard...). Flat faceted models, real size.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/sports.py", run_name="__main__")
Optional global SPORT_LIST (names or group names: balls, nets, gear). Exports Assets/Art/Global/Sports/<Group>/GS_<Name>_01.fbx.

Origin on the floor at the middle of the base; the front (the side a player faces, a goal's open side) is -Y. Long things (bats, sticks, a racket) lie on the
floor along X (the racket and the hockey stick point along Y and X as noted in each). A net is made of thin three-sided strands (8 triangles each), so a
goal stays under about 700 triangles; the mesh is coarse on purpose.
"""

import importlib
import math
import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
rod, lathe, ball = props_lib.rod, props_lib.lathe, props_lib.ball

PIECES = {}


def piece(group, name):
    def deco(fn):
        PIECES[name] = (fn, group)
        return fn
    return deco


# ===== Helpers ==================================================================================================
def _basis(direction):
    d = Vector(direction).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    return d, u, d.cross(u)


def strand(p, colour, a, b, r=0.004):
    """A thin three-sided bar from a to b (a net cord, a string)."""
    a, b = Vector(a), Vector(b)
    _, u, v = _basis(b - a)
    ring = lambda c: [c + u * r * math.cos(t) + v * r * math.sin(t) for t in (math.tau * k / 3 for k in range(3))]
    p.loft_rings(colour, [ring(a), ring(b)])


def patch(p, colour, centre, direction, R, radius, n=5):
    """A flat marking on the surface of a ball of radius R about `centre`, facing `direction` (a soccer ball's black pentagons, a bowling ball's holes)."""
    d, u, v = _basis(direction)
    c = Vector(centre)
    ring = lambda dist, rad: [c + d * dist + u * rad * math.cos(t) + v * rad * math.sin(t) for t in (math.tau * k / n for k in range(n))]
    p.loft_rings(colour, [ring(R * 0.96, radius), ring(R * 1.012, radius * 0.9)])


def belt(p, colour, centre, R, axis, w, n):
    """A band of width w around a ball of radius R (n sides, like the ball), about the given axis: a seam or stripe."""
    cx, cy, cz = centre
    r = R * 1.012
    if axis == "z":
        rings = [common.ring_z(cz + s * w / 2, cx, cy, r, r, n=n) for s in (-1, 1)]
    elif axis == "x":
        rings = [common.ring_x(cx + s * w / 2, cy, cz, r, r, n=n) for s in (-1, 1)]
    else:
        rings = [common.ring_y(cy + s * w / 2, cx, cz, r, r, n=n) for s in (-1, 1)]
    p.loft_rings(colour, rings, cap=False)


def seam(p, colour, centre, R, r, count=14):
    """The curved seam of a baseball or a tennis ball, as strands along a curve that winds twice round the ball."""
    pts = []
    for k in range(count + 1):
        t = math.tau * k / count
        v = Vector((math.cos(t) + 0.3 * math.cos(3 * t), math.sin(t) - 0.3 * math.sin(3 * t), 0.9 * math.cos(2 * t))).normalized()
        pts.append(Vector(centre) + v * R * 1.035)
    for a, b in zip(pts, pts[1:]):
        strand(p, colour, a, b, r)


# ===== Balls ====================================================================================================
@piece("balls", "Basketball")
def basketball():
    p = Prop("GS_Basketball_01")
    R, c = 0.121, (0, 0, 0.121)
    ball(p, "basket_orange", c, R, n=12, rings=5)
    for ax in "xyz":
        belt(p, "black", c, R, ax, 0.008, 12)
    return p


@piece("balls", "Soccerball")
def soccerball():
    p = Prop("GS_Soccerball_01")
    R, c = 0.11, (0, 0, 0.11)
    ball(p, "label_white", c, R, n=10, rings=5)
    phi = (1 + 5 ** 0.5) / 2
    dirs = [(0, s1, s2 * phi) for s1 in (-1, 1) for s2 in (-1, 1)] + [(s1, s2 * phi, 0) for s1 in (-1, 1) for s2 in (-1, 1)] + [(s2 * phi, 0, s1) for s1 in (-1, 1) for s2 in (-1, 1)]
    for d in dirs:
        patch(p, "black", c, d, R, 0.034)
    return p


@piece("balls", "Baseball")
def baseball():
    p = Prop("GS_Baseball_01")
    R, c = 0.037, (0, 0, 0.037)
    ball(p, "label_white", c, R, n=10, rings=5)
    seam(p, "cloth_red", c, R, 0.0032, count=28)
    return p


@piece("balls", "TennisBall")
def tennis_ball():
    p = Prop("GS_TennisBall_01")
    R, c = 0.033, (0, 0, 0.033)
    ball(p, "tennis_yellow", c, R, n=10, rings=5)
    seam(p, "label_white", c, R, 0.0034, count=24)
    return p


@piece("balls", "Football")
def football():
    """An American football lying on its side, laces up."""
    p = Prop("GS_Football_01")
    L, R, z = 0.28, 0.085, 0.085
    rad = lambda x: max(R * max(0.0, 1 - (2 * x / L) ** 2) ** 0.6, 0.004)
    xs = [L * (k / 8 - 0.5) for k in range(9)]
    p.loft_rings("leather_brown", [common.ring_x(x, 0, z, rad(x), rad(x), n=8) for x in xs])
    for s in (-1, 1):
        x = s * 0.085
        p.loft_rings("label_white", [common.ring_x(x + d, 0, z, rad(x) * 1.02, rad(x) * 1.02, n=8) for d in (-0.006, 0.006)], cap=False)
    p.box("label_white", (0, 0, 2 * z + 0.002), (0.12, 0.012, 0.006))
    for x in (-0.045, -0.015, 0.015, 0.045):
        p.box("label_white", (x, 0, 2 * z + 0.004), (0.008, 0.04, 0.006))
    return p


@piece("balls", "Volleyball")
def volleyball():
    p = Prop("GS_Volleyball_01")
    R, c = 0.105, (0, 0, 0.105)
    ball(p, "paint_yellow", c, R, n=12, rings=5)
    for ax in "xyz":
        belt(p, "label_blue", c, R, ax, 0.026, 12)
    return p


@piece("balls", "GolfBall")
def golf_ball():
    p = Prop("GS_GolfBall_01")
    ball(p, "label_white", (0, 0, 0.0214), 0.0214, n=8, rings=3)
    return p


@piece("balls", "BowlingBall")
def bowling_ball():
    p = Prop("GS_BowlingBall_01")
    R, c = 0.108, (0, 0, 0.108)
    ball(p, "alien_violet", c, R, n=12, rings=5)
    for d, rad in (((-0.2, -0.6, 0.77), 0.013), ((0.2, -0.6, 0.77), 0.013), ((0.0, -0.85, 0.42), 0.017)):
        patch(p, "black", c, d, R, rad, n=6)
    return p


@piece("balls", "HockeyPuck")
def hockey_puck():
    p = Prop("GS_HockeyPuck_01")
    p.cyl("black", (0, 0, 0.0127), 0.038, 0.0254, n=12)
    return p


# ===== Nets and goals ===========================================================================================
def goal_frame(p, colour, hw, h, d, hb, r):
    """A goal's tube frame: two posts and a crossbar at the front (y = 0), a lower back bar at y = d (height hb), the ground bars and the sloping roof bars."""
    for s in (-1, 1):
        p.cyl(colour, (s * hw, 0, h / 2), r, h, n=8)
        p.cyl(colour, (s * hw, d, hb / 2), r, hb, n=8)
        p.cyl(colour, (s * hw, d / 2, r), r, d, n=8, axis="y")
        rod(p, colour, (s * hw, 0, h), (s * hw, d, hb), 2 * r)
    p.cyl(colour, (0, 0, h), r, 2 * hw, n=8, axis="x")
    p.cyl(colour, (0, d, hb), r, 2 * hw, n=8, axis="x")
    p.cyl(colour, (0, d, r), r, 2 * hw, n=8, axis="x")


def goal_net(p, colour, hw, h, d, hb, spacing, r=0.004):
    """The net of a goal (frame at y = 0 .. d): a roof sloping from the crossbar to the back bar, a back, and two sides, as coarse grids of strands."""
    nx = max(2, round(2 * hw / spacing))
    xs = [-hw + 2 * hw * i / nx for i in range(nx + 1)]
    top = lambda y: h + (hb - h) * y / d
    for x in xs:
        strand(p, colour, (x, 0, h), (x, d, hb), r)
        strand(p, colour, (x, d, 0), (x, d, hb), r)
    for k in (1, 2, 3):
        f = k / 4
        strand(p, colour, (-hw, d * f, top(d * f)), (hw, d * f, top(d * f)), r)
    for k in (1, 2):
        strand(p, colour, (-hw, d, hb * k / 3), (hw, d, hb * k / 3), r)
    for s in (-1, 1):
        for k in range(1, 5):
            z = h * k / 5
            y_end = d if z <= hb else d * (h - z) / (h - hb)
            strand(p, colour, (s * hw, 0, z), (s * hw, y_end, z), r)
        for k in (1, 2, 3):
            y = d * k / 4
            strand(p, colour, (s * hw, y, 0), (s * hw, y, top(y)), r)


@piece("nets", "BasketballHoop")
def basketball_hoop():
    p = Prop("GS_BasketballHoop_01")
    p.box("concrete", (0, 1.25, 0.125), (1.0, 1.0, 0.25))
    p.cyl("metal_dark", (0, 1.25, 2.075), 0.065, 3.65, n=8)
    for z in (3.15, 3.65):
        rod(p, "metal_dark", (0, 1.25, z), (0, 0.55, z), 0.07)
    y = 0.5
    p.box("glass", (0, y, 3.425), (1.8, 0.04, 1.05))
    for dz in (-0.525, 0.525):
        p.box("label_white", (0, y, 3.425 + dz), (1.84, 0.05, 0.04))
    for dx in (-0.9, 0.9):
        p.box("label_white", (dx, y, 3.425), (0.04, 0.05, 1.09))
    yf = y - 0.022
    p.box("cloth_red", (0, yf, 3.52), (0.59, 0.006, 0.03))
    p.box("cloth_red", (0, yf, 3.08), (0.59, 0.006, 0.03))
    for dx in (-0.28, 0.28):
        p.box("cloth_red", (dx, yf, 3.3), (0.03, 0.006, 0.47))
    cy, R, rim_z = 0.10, 0.23, 3.05
    top = [Vector((R * math.cos(math.tau * k / 12), cy + R * math.sin(math.tau * k / 12), rim_z)) for k in range(12)]
    low = [Vector((0.15 * math.cos(math.tau * k / 12), cy + 0.15 * math.sin(math.tau * k / 12), rim_z - 0.4)) for k in range(12)]
    for k in range(12):
        rod(p, "basket_orange", top[k], top[(k + 1) % 12], 0.02)
        strand(p, "label_white", top[k], low[k], 0.004)
        strand(p, "label_white", top[k], low[(k + 1) % 12], 0.004)
        strand(p, "label_white", low[k], low[(k + 1) % 12], 0.004)
    rod(p, "basket_orange", (0, y - 0.022, rim_z), (0, cy + R, rim_z), 0.03)
    return p


@piece("nets", "SoccerGoal")
def soccer_goal():
    p = Prop("GS_SoccerGoal_01")
    hw, h, d, hb = 1.83, 1.83, 1.2, 0.9
    goal_frame(p, "paint_white", hw, h, d, hb, 0.05)
    goal_net(p, "label_white", hw, h, d, hb, 0.366)
    return p


@piece("nets", "HockeyGoal")
def hockey_goal():
    p = Prop("GS_HockeyGoal_01")
    hw, h, d, hb = 0.915, 1.22, 1.0, 0.6
    goal_frame(p, "cloth_red", hw, h, d, hb, 0.035)
    goal_net(p, "label_white", hw, h, d, hb, 0.305)
    return p


@piece("nets", "TennisNet")
def tennis_net():
    """A net across a court: 12.8 m between the posts, 0.914 m high in the middle (1.07 at the posts), the top band sagging between."""
    p = Prop("GS_TennisNet_01")
    hw = 6.4
    zt = lambda x: 0.914 + (1.07 - 0.914) * (x / hw) ** 2
    for s in (-1, 1):
        p.cyl("metal_dark", (s * hw, 0, 0.535), 0.04, 1.07, n=8)
    segs = 8
    for i in range(segs):
        x0, x1 = -hw + 2 * hw * i / segs, -hw + 2 * hw * (i + 1) / segs
        rod(p, "label_white", (x0, 0, zt(x0) - 0.03), (x1, 0, zt(x1) - 0.03), 0.02, 0.07)
    for i in range(17):
        x = -hw + 2 * hw * i / 16
        strand(p, "black", (x, 0, 0.03), (x, 0, zt(x) - 0.06), 0.004)
    for z in (0.2, 0.45, 0.7):
        strand(p, "black", (-hw, 0, z), (hw, 0, z), 0.004)
    p.box("label_white", (0, 0, 0.45), (0.05, 0.02, 0.84))
    return p


@piece("nets", "VolleyballNet")
def volleyball_net():
    """A net 9.5 m wide and 1 m deep, its top at 2.43 m, between two posts with base plates."""
    p = Prop("GS_VolleyballNet_01")
    hw, z0, z1 = 4.75, 1.43, 2.43
    for s in (-1, 1):
        p.box("metal_dark", (s * (hw + 0.4), 0, 0.015), (0.5, 0.5, 0.03))
        p.cyl("metal_galv", (s * (hw + 0.4), 0, 1.3), 0.05, 2.55, n=8)
        p.box("label_white", (s * hw, 0, (z0 + z1) / 2), (0.03, 0.03, z1 - z0))
        rod(p, "metal_dark", (s * hw, 0, 1.95), (s * (hw + 0.4), 0, 1.95), 0.02)
    p.box("label_white", (0, 0, z1 - 0.035), (2 * hw, 0.02, 0.07))
    p.box("label_white", (0, 0, z0 + 0.025), (2 * hw, 0.02, 0.05))
    for i in range(1, 19):
        x = -hw + 2 * hw * i / 19
        strand(p, "black", (x, 0, z0 + 0.05), (x, 0, z1 - 0.07), 0.004)
    for k in (1, 2, 3):
        z = z0 + (z1 - z0) * k / 4
        strand(p, "black", (-hw, 0, z), (hw, 0, z), 0.004)
    return p


# ===== Equipment ================================================================================================
def _bat(name, wood, grip):
    """A baseball bat lying on its side along X, the knob at -X: knob, handle, barrel, end cap."""
    p = Prop(name)
    prof = [(0.0, 0.004), (0.008, 0.02), (0.03, 0.021), (0.05, 0.0135), (0.3, 0.0135), (0.5, 0.03), (0.68, 0.033), (0.82, 0.032), (0.86, 0.026)]
    z = 0.033
    p.loft_rings(wood, [common.ring_x(-0.43 + s, 0, z, r, r, n=8) for s, r in prof])
    p.loft_rings(grip, [common.ring_x(-0.43 + s, 0, z, 0.0143, 0.0143, n=8) for s in (0.06, 0.28)], cap=False)
    return p


@piece("gear", "BaseballBat_Wood")
def bat_wood():
    return _bat("GS_BaseballBat_Wood_01", "wood_light", "black")


@piece("gear", "BaseballBat_Metal")
def bat_metal():
    return _bat("GS_BaseballBat_Metal_01", "truck_blue", "rubber")


@piece("gear", "BaseballGlove")
def baseball_glove():
    """A glove lying palm up, fingers toward +Y."""
    p = Prop("GS_BaseballGlove_01")
    p.box("leather_brown", (0, -0.03, 0.02), (0.2, 0.2, 0.04))
    p.box("fabric_brown", (0, 0.03, 0.043), (0.14, 0.12, 0.012))
    for x, rz, ln in ((-0.075, 10, 0.2), (-0.028, 3, 0.22), (0.028, -3, 0.21), (0.075, -9, 0.17)):
        p.box("leather_brown", (x + rz * 0.002, 0.1 + ln / 2, 0.025), (0.044, ln, 0.05), rot=(0, 0, rz))
    p.box("leather_brown", (-0.15, 0.03, 0.025), (0.05, 0.16, 0.05), rot=(0, 0, -40))
    p.box("wood_dark", (-0.085, 0.16, 0.052), (0.05, 0.05, 0.008), rot=(0, 0, 20))
    p.box("fabric_brown", (0, -0.15, 0.04), (0.15, 0.05, 0.06))
    p.box("wood_light", (0, -0.12, 0.052), (0.1, 0.01, 0.01))
    return p


@piece("gear", "HomePlate")
def home_plate():
    p = Prop("GS_HomePlate_01")
    pts = [(-0.216, -0.216), (0.216, -0.216), (0.216, 0.0), (0.0, 0.216), (-0.216, 0.0)]
    p.loft_rings("label_white", [[Vector((x, y, z)) for x, y in pts] for z in (0.0, 0.025)])
    return p


@piece("gear", "BaseballBase")
def baseball_base():
    p = Prop("GS_BaseballBase_01")
    p.box("label_white", (0, 0, 0.04), (0.38, 0.38, 0.08), taper=0.96)
    return p


@piece("gear", "TennisRacket")
def tennis_racket():
    """A racket lying flat, handle toward -Y, head toward +Y."""
    p = Prop("GS_TennisRacket_01")
    hx, hy, cy, z = 0.13, 0.17, 0.17, 0.007
    pts = [(hx * math.cos(math.tau * k / 12), cy + hy * math.sin(math.tau * k / 12)) for k in range(12)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        rod(p, "truck_blue", (x0, y0, z), (x1, y1, z), 0.014)
    for x in (-0.09, -0.045, 0.0, 0.045, 0.09):
        half = hy * math.sqrt(1 - (x / hx) ** 2) * 0.96
        strand(p, "label_white", (x, cy - half, z), (x, cy + half, z), 0.0016)
    for dy in (-0.12, -0.08, -0.04, 0.0, 0.04, 0.08, 0.12):
        half = hx * math.sqrt(1 - (dy / hy) ** 2) * 0.96
        strand(p, "label_white", (-half, cy + dy, z), (half, cy + dy, z), 0.0016)
    for s in (-1, 1):
        rod(p, "truck_blue", (s * 0.06, 0.012, z), (s * 0.012, -0.08, z), 0.014)
    rod(p, "truck_blue", (0, -0.08, z), (0, -0.16, z), 0.02)
    p.box("black", (0, -0.27, 0.0095), (0.036, 0.22, 0.019))
    p.box("rubber", (0, -0.39, 0.0095), (0.044, 0.02, 0.019))
    return p


@piece("gear", "HockeyStick")
def hockey_stick():
    """A stick lying on its side along X, the blade at +X."""
    p = Prop("GS_HockeyStick_01")
    p.box("black", (-0.1, 0, 0.0125), (1.25, 0.028, 0.025))
    p.box("label_white", (-0.65, 0, 0.0135), (0.22, 0.03, 0.027))
    p.box("wood_light", (0.7, -0.04, 0.0125), (0.34, 0.07, 0.025), rot=(0, 0, 10))
    p.box("label_white", (0.7, -0.04, 0.0265), (0.3, 0.06, 0.004), rot=(0, 0, 10))
    return p


@piece("gear", "GolfClub")
def golf_club():
    """A driver lying along X, the head at +X."""
    p = Prop("GS_GolfClub_01")
    p.cyl("metal_galv", (-0.05, 0, 0.006), 0.006, 1.05, n=6, axis="x")
    p.cyl("black", (-0.45, 0, 0.0095), 0.0095, 0.25, n=6, axis="x")
    ball(p, "metal_dark", (0.51, 0.02, 0.03), 0.05, n=8, rings=3, squash=0.6)
    p.box("metal_dark", (0.5, 0.0, 0.016), (0.03, 0.03, 0.03))
    return p


@piece("gear", "FootballHelmet")
def football_helmet():
    p = Prop("GS_FootballHelmet_01")
    lathe(p, "truck_blue", [(0.0, 0.11), (0.06, 0.145), (0.14, 0.155), (0.2, 0.125), (0.245, 0.06)], n=10)
    p.box("label_white", (0, 0, 0.243), (0.035, 0.2, 0.012))
    for s in (-1, 1):
        p.cyl("black", (s * 0.15, 0.0, 0.09), 0.04, 0.012, n=8, axis="x")
        p.box("metal_galv", (s * 0.075, -0.17, 0.09), (0.014, 0.014, 0.1))
    for z in (0.045, 0.09, 0.135):
        p.box("metal_galv", (0, -0.17, z), (0.2, 0.014, 0.014))
        for s in (-1, 1):
            rod(p, "metal_galv", (s * 0.1, -0.17, z), (s * 0.145, -0.07, z), 0.014)
    return p


@piece("gear", "Skateboard")
def skateboard():
    p = Prop("GS_Skateboard_01")
    p.box("cloth_red", (0, 0, 0.082), (0.2, 0.56, 0.012))
    p.box("black", (0, 0, 0.0885), (0.19, 0.55, 0.001))
    for s in (-1, 1):
        p.box("cloth_red", (0, s * 0.327, 0.099), (0.2, 0.1, 0.012), rot=(s * 20, 0, 0))
        p.box("metal_galv", (0, s * 0.2, 0.065), (0.15, 0.04, 0.025))
        for x in (-1, 1):
            p.cyl("label_white", (x * 0.095, s * 0.2, 0.027), 0.027, 0.036, n=8, axis="x")
    return p


@piece("gear", "Dumbbell")
def dumbbell():
    p = Prop("GS_Dumbbell_01")
    p.cyl("metal_dark", (0, 0, 0.06), 0.016, 0.2, n=8, axis="x")
    for s in (-1, 1):
        p.cyl("black", (s * 0.085, 0, 0.06), 0.06, 0.05, n=6, axis="x")
        p.cyl("metal_galv", (s * 0.12, 0, 0.06), 0.022, 0.02, n=6, axis="x")
    return p


@piece("gear", "TrainingCone")
def training_cone():
    p = Prop("GS_TrainingCone_01")
    p.box("basket_orange", (0, 0, 0.01), (0.24, 0.24, 0.02))
    p.cyl("basket_orange", (0, 0, 0.16), 0.09, 0.28, n=8, top_radius=0.02)
    p.cyl("label_white", (0, 0, 0.18), 0.0585, 0.05, n=8, top_radius=0.0455)
    return p


@piece("gear", "Frisbee")
def frisbee():
    p = Prop("GS_Frisbee_01")
    lathe(p, "truck_blue", [(0.0, 0.08), (0.012, 0.12), (0.022, 0.13), (0.028, 0.115), (0.03, 0.06)], n=12)
    return p


def run():
    names = globals().get("SPORT_LIST")
    chosen = [k for k, (fn, g) in PIECES.items() if not names or k in names or g in names]
    x, row, y = 0.0, None, 0.0
    for key in chosen:
        fn, group = PIECES[key]
        if group != row:
            row, x, y = group, 0.0, y + 4.0 if row is not None else 0.0
        prop = fn()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Sports/{group.title()}/{prop.name}.fbx")
        obj.location = (x, y, 0)
        x += max(0.3, obj.dimensions.x + 0.4)
    print("sports done", len(chosen))


if __name__ == "__main__":
    run()
