"""Vehicles and the crashed ship (asset list GV-01, GV-20, GV-30...): flat faceted models from simple solids.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/vehicles.py", run_name="__main__")
Optional global VEHICLE_LIST, e.g. ["pickup"]. Exports Assets/Art/<Global|Farm>/Vehicles/<name>.fbx.

Real sizes: the pickup is 5.4 x 2.0 x 1.9 m, the tractor 4.1 x 2.4 x 2.8 m, the sheriff cruiser 5.0 m. Vehicles face -Y with
their origin on the ground at the centre; wheels are separate boxes so Unity can spin them later (this first pass is one mesh).
Colours come from the palette (`truck_blue`, `tractor_green`, ...); recolour a variant by changing the first argument.
"""

import importlib
import sys
import contextlib
import math
from math import radians
from pathlib import Path

import bmesh
from mathutils import Vector

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Blender is shared by several sessions, each running scripts from its own checkout: a module another checkout imported first would make this one build with its
# code and write its FBX into that checkout. Drop modules that came from somewhere else so they are imported from here.
for _n in ("common", "props_lib", "emitters", "ship_hulls"):
    _m = sys.modules.get(_n)
    if _m is not None and Path(getattr(_m, "__file__", "") or "").resolve().parent != _HERE:
        sys.modules.pop(_n, None)
import common
import props_lib
import ship_hulls
for _m in (common, props_lib, ship_hulls):
    importlib.reload(_m)
Prop = props_lib.Prop
wheel = props_lib.wheel


def vec3(x, y, z):
    return Vector((x, y, z))


# ===== Shared pieces for every road vehicle (#344: more detail, same palette) =====================================================
def wheel_role(x, y):
    """The temporary name of the moving part for the wheel at (x, y): every tyre at the same side and the same y (a dual pair) is one part.
    name_wheels() turns these into Wheel_FL, Wheel_RR... once the whole vehicle is built and the axles are known."""
    if abs(x) < 0.05:
        side = "C"
    elif x > 0:
        side = "L"
    else:
        side = "R"
    return f"Wheel@{side}@{round(y, 2)}"


def wheel_part(p, x, y, z):
    """Everything added inside is one wheel that spins about the X axis through its centre (x, y, z)."""
    return p.part(wheel_role(x, y), pivot=(x, y, z), kind="spin", axis="x", limit=360.0)


def name_wheels(p):
    """Give the wheel parts of a finished vehicle their names: Wheel_FL, Wheel_FR, Wheel_RL, Wheel_RR for two axles (L is +X: the model faces -Y),
    Wheel_A1L, Wheel_A1R, Wheel_A2L... for more, Wheel_L and Wheel_R for one axle, Wheel_Front and Wheel_Rear for a motorcycle's centre-line wheels."""
    wheels = [r for r in p.groups if r.startswith("Wheel@")]
    ys = sorted({float(r.split("@")[2]) for r in wheels})
    names = {}
    for r in wheels:
        _, side, y = r.split("@")
        k = ys.index(float(y))
        if side == "C":
            names[r] = "Wheel_Front" if k == 0 else "Wheel_Rear"
        elif len(ys) == 1:
            names[r] = f"Wheel_{side}"
        elif len(ys) == 2:
            names[r] = f"Wheel_{'F' if k == 0 else 'R'}{side}"
        else:
            names[r] = f"Wheel_A{k + 1}{side}"
    p.groups = {names.get(r, r): g for r, g in p.groups.items()}


def car_wheel(p, trim, x, y, r, w, n=10, z=None):
    """A road wheel on the X axis, a spinning part: the tyre, then on the outer face a rim, a dark dish and a cap (the inner face is never seen)."""
    z = r if z is None else z
    out = 1 if x >= 0 else -1
    with wheel_part(p, x, y, z):
        p.cyl("rubber", (x, y, z), r, w, n=n, axis="x")
        xo = x + out * (w / 2 + 0.006)
        p.cyl(trim, (xo, y, z), r * 0.64, 0.014, n=n, axis="x")                                # rim
        p.cyl("black", (xo + out * 0.008, y, z), r * 0.42, 0.016, n=8, axis="x")               # dark dish
        p.cyl(trim, (xo + out * 0.016, y, z), r * 0.15, 0.016, n=6, axis="x")                  # cap


def arch(p, colour, x, y, zc, r, w=0.07, lo=10):
    """A wheel-arch lip: a symmetric ring of beams over a wheel centred at (y, zc) with the arch radius r, on the side plane x, from `lo` degrees
    above the horizontal at the rear to `lo` degrees above it at the front (raise `lo` when the body bottom is well above the axle)."""
    from math import cos, sin
    pts = [(y + r * cos(radians(a)), zc + r * sin(radians(a))) for a in [lo + k * (180 - 2 * lo) / 6 for k in range(7)]]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        props_lib.rod(p, colour, (x, y0, z0), (x, y1, z1), w)


def body_loft(p, colour, stations, shoulder=0.8):
    """A body shell skinned along Y from cross-sections (y, half_width, z_bottom, z_top, tuck): a six-point ring with its shoulder `shoulder` of the
    way up and a top that is `tuck` narrower each side, so the sides lean in a little (a real car's tumblehome)."""
    rings = []
    for y, hw, zb, zt, tuck in stations:
        zs = zb + (zt - zb) * shoulder
        rings.append([vec3(-hw + 0.04, y, zb), vec3(hw - 0.04, y, zb), vec3(hw, y, zs), vec3(hw - tuck, y, zt), vec3(-hw + tuck, y, zt), vec3(-hw, y, zs)])
    p.loft_rings(colour, rings)


def _cut(st, drop):
    """For one body station (y, half_width, z_bottom, z_top, tuck): the points of the cut `drop` below its top, as body_loft's ring is built:
    (z of the cut, x of the side at that height, z of the shoulder)."""
    _, hw, zb, zt, _ = st
    zs = zb + (zt - zb) * 0.8
    zc = zt - drop
    assert zc < zs and zc > zb, (st, drop)
    return zc, (hw - 0.04) + 0.04 * (zc - zb) / (zs - zb), zs


def low_loft(p, colour, stations, drop):
    """The part of body_loft's shell that stays put under a lid (a hood, a boot lid, a tailgate): everything up to `drop` below the top."""
    rings = []
    for st in stations:
        y, hw, zb, _, _ = st
        zc, xc, _ = _cut(st, drop)
        rings.append([vec3(-(hw - 0.04), y, zb), vec3(hw - 0.04, y, zb), vec3(xc, y, zc), vec3(-xc, y, zc)])
    p.loft_rings(colour, rings)


def lid_loft(p, colour, stations, drop):
    """The lid that goes with low_loft: the top `drop` of the same shell, a solid piece (whatever sits under it, an engine or a spare wheel, is inside it while it is shut)."""
    rings = []
    for st in stations:
        y, hw, _, zt, tuck = st
        zc, xc, zs = _cut(st, drop)
        rings.append([vec3(-xc, y, zc), vec3(xc, y, zc), vec3(hw, y, zs), vec3(hw - tuck, y, zt), vec3(-(hw - tuck), y, zt), vec3(-hw, y, zs)])
    p.loft_rings(colour, rings)


def lean_box(p, colour, sx, hb, ht, zlo, zhi, ya, yb, z0, z1, thick, outset=0.0):
    """A panel lying on the leaning side of a glasshouse whose side runs from half-width hb at height zlo to ht at zhi, from y ya to yb and height z0 to z1
    (outset is how far it stands off the surface): a door window, a quarter window, a decal."""
    a = math.atan2(hb - ht, zhi - zlo)
    zc = (z0 + z1) / 2
    xc = hb + (ht - hb) * (zc - zlo) / (zhi - zlo) + outset * math.cos(a)
    p.box(colour, (sx * xc, (ya + yb) / 2, zc + outset * math.sin(a)), (thick, yb - ya, (z1 - z0) / math.cos(a)), rot=(0, -sx * math.degrees(a), 0))


def core_loft(p, colour, stations, thick):
    """body_loft's shell without its side panels: what stays when the sides below the shoulder come off (the panels are panel_loft, `thick` thick)."""
    rings = []
    for y, hw, zb, zt, tuck in stations:
        zs = zb + (zt - zb) * 0.8
        rings.append([vec3(-(hw - 0.04 - thick), y, zb), vec3(hw - 0.04 - thick, y, zb), vec3(hw - thick, y, zs), vec3(hw, y, zs), vec3(hw - tuck, y, zt),
                      vec3(-(hw - tuck), y, zt), vec3(-hw, y, zs), vec3(-(hw - thick), y, zs)])
    p.loft_rings(colour, rings)


def panel_loft(p, colour, stations, sx, thick):
    """The side panel (side sx) that goes with core_loft: the shell below its shoulder, `thick` thick."""
    rings = []
    for y, hw, zb, zt, tuck in stations:
        zs = zb + (zt - zb) * 0.8
        rings.append([vec3(sx * (hw - 0.04), y, zb), vec3(sx * hw, y, zs), vec3(sx * (hw - thick), y, zs), vec3(sx * (hw - 0.04 - thick), y, zb)])
    p.loft_rings(colour, rings)


def glasshouse(p, colour, stations):
    """The cabin skinned from (y, half_width_base, half_width_top, z_base, z_top): slanted windscreen, side windows leaning in, rear window."""
    p.loft_rings(colour, [[vec3(-hb, y, zb), vec3(hb, y, zb), vec3(ht, y, zt), vec3(-ht, y, zt)] for y, hb, ht, zb, zt in stations])


def mirror(p, colour, sx, x, y, z):
    """A door mirror: one chunky housing whose inner end is buried in the body (one part, so a Damaged model never keeps a mirror head in mid-air)."""
    p.box(colour, (sx * (x + 0.08), y, z), (0.2, 0.12, 0.13))


def seat(p, colour, x, y, z, w, ch):
    """One seat facing -Y standing on a floor at height z: a cushion and a back that leans a little. ch is the headroom the roof leaves."""
    back = max(0.2, min(0.5, ch - 0.18))
    p.box(colour, (x, y, z + 0.05), (w, 0.5, 0.1))
    p.box(colour, (x, y + 0.24, z + 0.1 + back / 2), (w, 0.1, back), rot=(-8, 0, 0))


def _seats(p, colour, x, y0, rows, bench, sz, width, ch):
    """The rows of seats of a cab_interior on a floor at height sz: two seats at +-x in the first row unless bench, benches behind."""
    for k, off in enumerate(rows):
        if k == 0 and not bench:
            for sx in (-1, 1):
                seat(p, colour, sx * x, y0 + off, sz, 0.5, ch)
        else:
            seat(p, colour, 0, y0 + off, sz, width - 0.5, ch)


def cab_interior(p, y0, y1, z, width, ch, rows=(0.9,), bench=False, colour="office_dark", floor=None):
    """What you see through the glass of a cabin from y0 (the windscreen end) to y1 on a floor at height z, `width` wide and ch under the roof:
    a floor mat, a dashboard, a steering wheel on the left (-X), and a row of seats for each y offset in rows (the first row is the front;
    bench=True makes it one seat across, otherwise two seats; later rows are benches).
    floor= puts the floor lower than z (a car whose doors open: the floor is the car's, z is the window sill): the dashboard reaches down to it,
    the seats stand on it and the steering wheel stays up where z is."""
    fz = z if floor is None else floor
    lift = z - fz
    x = width / 2 - 0.42
    p.box("black", (0, (y0 + y1) / 2, fz + 0.01), (width - 0.1, y1 - y0 - 0.1, 0.02))                        # floor mat
    p.box("black", (0, y0 + 0.22, fz + (0.24 + lift) / 2), (width - 0.1, 0.36, 0.24 + lift))                # dashboard
    p.cyl("black", (-x, y0 + 0.62, z + min(0.36, ch * 0.7)), 0.16, 0.03, n=6, axis="y")                      # steering wheel
    if lift:
        props_lib.rod(p, "metal_dark", (-x, y0 + 0.4, fz + (0.24 + lift) * 0.7), (-x, y0 + 0.62, z + min(0.36, ch * 0.7)), 0.05)   # its column
    _seats(p, colour, x, y0, rows, bench, fz + (0.1 if lift else 0), width, ch + lift)


def _pickup_doors(p, body, s, ytop, z_f, zmid):
    """The two doors on one side of the pickup, each a part (the front one carries the mirror)."""
    side = "L" if s > 0 else "R"
    for role, ya, yb, front in ((f"Door_F{side}", -0.93, -0.13, True), (f"Door_R{side}", -0.11, 0.79, False)):
        with p.part(role, pivot=(s * 0.96, ya, zmid), kind="hinge", axis="z", limit=-70.0 * s):
            p.box(body, (s * 0.935, (ya + yb) / 2, zmid), (0.09, yb - ya, ytop - z_f))
            p.box("black", (s * 0.89, (ya + yb) / 2, zmid + 0.02), (0.016, yb - ya - 0.08, ytop - z_f - 0.1))     # the door card
            lean_box(p, "clear_glass", s, 0.87, 0.78, 1.13, 1.58, max(ya + 0.04, -0.68) if front else ya + 0.04, yb - 0.04, 1.135, 1.57, 0.03)
            p.box("metal_galv", (s * 0.985, yb - 0.15, 1.02), (0.04, 0.16, 0.04))      # handle
            if front:
                mirror(p, body, s, 0.9, -0.9, 1.2)


def _pickup_bed(p, body, gate):
    """The open bed of the pickup: floor, side walls with rails, ribs and wheel wells, the tailgate (a part when `gate`) and the front wall."""
    p.box(body, (0, 1.75, 0.72), (1.9, 2.0, 0.1))                                    # bed floor
    for s in (-1, 1):
        p.box(body, (s * 0.93, 1.75, 1.0), (0.1, 2.0, 0.5))                         # side walls
        p.box("black", (s * 0.93, 1.75, 1.27), (0.14, 2.0, 0.06))                   # rails
        for y in (1.15, 1.6, 2.05, 2.45):
            p.box(body, (s * 0.985, y, 1.0), (0.03, 0.09, 0.46))                    # ribs pressed into the walls
        p.box(body, (s * 0.7, 1.7, 0.87), (0.4, 0.8, 0.22))                         # wheel wells inside the bed (under the tow deck, z 1.0)
    with (p.part("Tailgate", pivot=(0, 2.7, 0.75), kind="hinge", axis="x", limit=-88.0) if gate else contextlib.nullcontext()):
        p.box(body, (0, 2.7, 1.0), (1.9, 0.1, 0.5))                                  # tailgate
        p.box("black", (0, 2.77, 1.22), (0.5, 0.04, 0.06))                          # its handle
        p.box("black", (0, 2.762, 1.03), (1.2, 0.02, 0.1))                          # badge strip
        p.box("paint_white", (0, 2.76, 0.86), (0.45, 0.02, 0.2))                    # plate
        for s in (-1, 1):
            p.box("black", (s * 0.86, 2.74, 1.0), (0.2, 0.05, 0.36))                # tail light housings
            p.box("cloth_red", (s * 0.86, 2.745, 1.0), (0.16, 0.08, 0.3))           # tail lights (reach back into the tailgate)
    p.box(body, (0, 0.78, 1.0), (1.9, 0.1, 0.5))                                     # bed front wall


def _pickup_front_and_rear(p):
    """The pickup's bumpers, grille, headlights, indicators and exhaust."""
    p.box("metal_galv", (0, -2.7, 0.6), (2.0, 0.18, 0.22))
    p.box("black", (0, -2.66, 0.43), (1.5, 0.1, 0.14))                              # valance
    p.box("metal_galv", (0, 2.82, 0.58), (2.0, 0.18, 0.2))
    p.box("black", (0, 2.95, 0.5), (0.12, 0.28, 0.12))                              # tow receiver
    p.box("black", (0, -2.64, 0.82), (0.9, 0.06, 0.26))                             # grille
    for z in (0.74, 0.82, 0.9):
        p.box("metal_galv", (0, -2.675, z), (0.88, 0.03, 0.03))
    for s in (-1, 1):
        p.box("metal_galv", (s * 0.7, -2.64, 0.84), (0.34, 0.07, 0.22))             # headlight bezels
        p.box("paint_yellow", (s * 0.7, -2.665, 0.84), (0.28, 0.09, 0.16))          # headlights (reach back into the nose)
        p.box("orange_cat", (s * 0.93, -2.64, 0.64), (0.1, 0.06, 0.1))              # indicators
    p.cyl("metal_dark", (0.6, 2.9, 0.47), 0.05, 0.3, n=6, axis="y")                 # exhaust, up into the bumper


def pickup(body="truck_blue", name="GV_Pickup_01", gate=True):
    """A farm pickup truck. A lofted hood and cab with a slanted windscreen, pillars, wheel arches, an open bed with ribs and wheel wells, bumpers,
    a grille with bars, headlight and tail light housings, mirrors, running boards and four wheels.

    It opens: four doors (Door_FL, Door_FR, Door_RL, Door_RR; L is +X) on a hollow cab with a floor and seats, the hood (Hood) over an engine, and the
    tailgate (Tailgate), which drops flat. The wheels spin."""
    p = Prop(name)
    z_f, ytop = 0.65, 1.13                                                          # the cab floor, and the sill the windows stand on
    zmid = (z_f + ytop) / 2
    p.box("black", (0, 0, 0.5), (1.7, 5.0, 0.18))                                    # frame
    A = (-2.62, 0.88, 0.58, 0.98, 0.06); B = (-2.45, 0.97, 0.52, 1.06, 0.07); C = (-1.7, 0.98, 0.52, 1.12, 0.07); D = (-1.05, 0.98, 0.52, 1.14, 0.06)
    body_loft(p, body, [A, B])                                                       # the nose
    low_loft(p, body, [B, C, D], 0.17)                                               # the engine bay
    with p.part("Hood", pivot=(0, -1.05, 0.97), kind="hinge", axis="x", limit=-60.0):
        lid_loft(p, body, [B, C, D], 0.17)
        p.box(body, (0, -1.85, 1.15), (0.55, 0.75, 0.07))                           # hood scoop
        p.box("black", (0, -2.21, 1.14), (0.42, 0.03, 0.05))                        # its intake
    p.box("metal_dark", (0, -1.5, 1.0), (0.5, 0.8, 0.22))                           # engine, inside the hood while it is shut
    p.box("black", (-0.55, -2.0, 1.0), (0.2, 0.16, 0.2))
    p.box("black", (0, -2.2, 1.0), (1.3, 0.08, 0.22))                               # radiator
    glasshouse(p, "clear_glass", [(-0.95, 0.87, 0.86, 1.13, 1.15), (-0.68, 0.87, 0.78, 1.13, 1.58)])                       # the windscreen
    glasshouse(p, "clear_glass", [(0.6, 0.87, 0.78, 1.13, 1.58), (0.85, 0.87, 0.84, 1.13, 1.17)])                          # the rear window
    cab_interior(p, -0.7, 0.7, ytop, 1.5, 0.4, rows=(0.5, 1.15), bench=True, floor=z_f)                                 # dashboard, wheel and seats you can see
    p.box("black", (0, -0.1, z_f - 0.05), (1.76, 1.9, 0.1))                         # the floor
    p.box(body, (0, 0.8, (0.52 + ytop) / 2), (1.9, 0.1, ytop - 0.52))              # the back wall of the cab
    p.box(body, (0, -0.04, 1.63), (1.64, 1.38, 0.1))                               # roof (its top where the tow truck beacon expects it)
    for s in (-1, 1):
        props_lib.rod(p, body, (s * 0.88, -0.95, 1.13), (s * 0.8, -0.68, 1.58), 0.09)     # A pillars
        props_lib.rod(p, body, (s * 0.88, -0.12, 1.12), (s * 0.79, -0.12, 1.58), 0.08)    # B pillars
        props_lib.rod(p, body, (s * 0.79, 0.6, 1.58), (s * 0.88, 0.85, 1.13), 0.13)       # C pillars
        p.sbox(body, (s * 0.935, -0.99, (0.52 + ytop) / 2), (0.09, 0.1, ytop - 0.52))      # the panel in front of the door
        p.sbox(body, (s * 0.935, -0.12, (0.52 + z_f) / 2), (0.09, 1.82, z_f - 0.52))       # rocker panel
        for y in (-0.96, -0.12):
            p.sbox("black", (s * 0.84, y, zmid), (0.1, 0.08, ytop - z_f))                   # the posts the doors shut against
        _pickup_doors(p, body, s, ytop, z_f, zmid)
        p.box("black", (s * 1.0, -0.5, 0.5), (0.14, 1.5, 0.06))                    # running boards
    for x in (-0.3, 0.0, 0.3):
        p.box("paint_yellow", (x, -0.745, 1.63), (0.1, 0.05, 0.06))                # cab lights, on the roof front edge
    _pickup_bed(p, body, gate)
    _pickup_front_and_rear(p)
    # wheels and arches
    for s in (-1, 1):
        for y in (-1.75, 1.7):
            car_wheel(p, "metal_galv", s * 0.9, y, 0.38, 0.28, n=12)
            arch(p, "black", s * 0.99, y, 0.38, 0.5, lo=25)
    return p


def _tractor_rear_wheel(p, body, s):
    """One side's rear wheel of the tractor, the curved mudguard over it and the footplate."""
    # the rear wheel: a tyre, a treaded ring of lugs, a hub in the body colour and a cap
    x, y, z, r, w = s * 1.12, 0.5, 0.85, 0.85, 0.55
    with wheel_part(p, x, y, z):
        rt = r - 0.05                                                                   # the lugs reach the full radius
        p.cyl("rubber", (x, y, z), rt, w, n=14, axis="x")
        for k in range(14):
            a = radians(k * 360 / 14 + 360 / 28)
            props_lib.rod(p, "rubber", (x, y + (rt - 0.02) * math.cos(a), z + (rt - 0.02) * math.sin(a)),
                          (x, y + r * math.cos(a), z + r * math.sin(a)), w * 0.85, 0.09)
        xo = x + s * (w / 2 + 0.006)
        p.cyl(body, (xo, y, z), r * 0.55, 0.02, n=10, axis="x")
        p.cyl("metal_dark", (xo + s * 0.012, y, z), r * 0.3, 0.02, n=8, axis="x")
        p.cyl("metal_galv", (xo + s * 0.024, y, z), r * 0.1, 0.02, n=6, axis="x")
    # the curved mudguard over it, and the step below the cab
    zc, rg = z, r + 0.13                                                        # the chords sag inside the arc, so stand it well off the lugs
    pts = [(y + rg * math.cos(radians(a)), zc + rg * math.sin(radians(a))) for a in (15, 45, 75, 105, 135, 165)]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        props_lib.rod(p, body, (x, y0, z0), (x, y1, z1), 0.68, 0.06)
    for a in (60, 120):                                                         # stays from the rear body to the guard
        props_lib.rod(p, "metal_dark", (s * 0.5, y + rg * math.cos(radians(a)), 1.3),
                      (s * 0.82, y + rg * math.cos(radians(a)), zc + rg * math.sin(radians(a))), 0.07)
    p.box("metal_dark", (s * 0.68, 0.5, 1.15), (0.26, 1.5, 0.1))                 # footplate, between the body and the wheel


def _tractor_front_wheel(p, body, s):
    """One side's front wheel of the tractor."""
    # the front wheel: smaller, with its own lugs
    x, y, z, r, w = s * 0.85, -1.55, 0.5, 0.5, 0.28
    with wheel_part(p, x, y, z):
        rt = r - 0.04
        p.cyl("rubber", (x, y, z), rt, w, n=10, axis="x")
        for k in range(10):
            a = radians(k * 36 + 18)
            props_lib.rod(p, "rubber", (x, y + (rt - 0.02) * math.cos(a), z + (rt - 0.02) * math.sin(a)),
                          (x, y + r * math.cos(a), z + r * math.sin(a)), w * 0.7, 0.07)
        xo = x + s * (w / 2 + 0.006)
        p.cyl(body, (xo, y, z), r * 0.55, 0.02, n=8, axis="x")
        p.cyl("metal_galv", (xo + s * 0.012, y, z), r * 0.14, 0.02, n=6, axis="x")


def tractor(body="tractor_green", name="GV_Tractor_01"):
    """A farm tractor: a lofted engine hood with grille bars, vents and lights, an open cab with a canopy, seat, steering wheel and pedals,
    big treaded rear wheels under curved mudguards, small front wheels, exhaust, air cleaner, lift arms and a hitch."""
    p = Prop(name)
    p.box("black", (0, 0, 0.7), (1.0, 3.6, 0.3))                                     # chassis
    H0, H1, H2, H3 = (-2.0, 0.34, 0.9, 1.55, 0.09), (-1.85, 0.43, 0.82, 1.68, 0.08), (-0.5, 0.5, 0.8, 1.7, 0.08), (-0.3, 0.5, 0.8, 1.62, 0.05)
    body_loft(p, body, [H0, H1])                                                     # the nose
    core_loft(p, body, [H1, H2, H3], 0.09)                                           # the engine bay: a fixed top, and the side panels come off
    for sx in (-1, 1):
        p.box("metal_dark", (sx * 0.43, -1.1, 1.1), (0.07, 0.7, 0.3))                # engine block and manifold: inside the side panel while it is shut
        p.box("black", (sx * 0.43, -1.65, 1.1), (0.07, 0.25, 0.3))                   # radiator
        p.box("black", (sx * 0.43, -0.65, 1.0), (0.07, 0.2, 0.2))                    # battery and filter
        with p.part("Engine_L" if sx > 0 else "Engine_R", pivot=(sx * 0.5, -1.1, 1.5), kind="hinge", axis="y", limit=-55.0 * sx):
            panel_loft(p, body, [H1, H2, H3], sx, 0.09)
            for z in (0.98, 1.14, 1.3):
                p.box("black", (sx * 0.49, -1.2, z), (0.04, 0.6, 0.04))              # engine vents
    p.box("black", (0, -2.02, 1.2), (0.56, 0.05, 0.5))                               # grille
    for z in (1.02, 1.2, 1.38):
        p.box("metal_galv", (0, -2.045, z), (0.58, 0.02, 0.04))                      # grille bars
    p.box("metal_dark", (0, -2.05, 0.8), (0.9, 0.14, 0.25))                          # front bumper bar, into the nose
    p.cyl("black", (0.0, -1.9, 1.68), 0.07, 0.1, n=6)                                # radiator cap, on the hood
    p.cyl("black", (-0.28, -1.2, 1.8), 0.1, 0.25, n=8)                               # air cleaner
    p.cyl("black", (0.3, -1.4, 2.25), 0.05, 1.2, n=6, top_radius=0.08)               # exhaust stack with its flared cap, one part
    p.cyl("metal_galv", (0.3, -1.4, 1.75), 0.08, 0.08, n=6)                          # and clamp
    p.box(body, (0, 0.45, 1.1), (1.1, 1.3, 0.6))                                     # rear body
    p.box("black", (0, 1.12, 1.1), (1.0, 0.04, 0.4))                                 # its back panel
    p.box("black", (0, 0.2, 1.5), (0.45, 0.45, 0.2))                                 # seat base, on the body
    p.box("rubber", (0, 0.4, 1.83), (0.5, 0.1, 0.46))                                # seat back, on the base
    for s in (-1, 1):
        p.box("black", (s * 0.25, 0.2, 1.72), (0.06, 0.4, 0.06))                     # armrests
        p.box("black", (s * 0.25, 0.0, 1.62), (0.06, 0.06, 0.16))
        for sy in (-0.4, 1.0):
            p.box(body, (s * 0.5, sy, 2.14), (0.08, 0.08, 1.48))                     # cab posts, from the body up to the roof
    p.box(body, (0, 0.3, 2.88), (1.45, 1.8, 0.1))                                    # canopy roof
    p.box("metal_dark", (0, 0.3, 2.81), (1.2, 1.55, 0.05))                           # its underside
    props_lib.rod(p, "metal_dark", (0, -0.3, 1.4), (0, -0.17, 1.84), 0.06)           # steering column, up to the wheel
    p.cyl("black", (0, -0.17, 1.84), 0.17, 0.03, n=8, rot=(-35, 0, 0))               # steering wheel
    p.box("metal_dark", (0, -0.1, 1.43), (0.3, 0.14, 0.06))                          # pedals
    props_lib.rod(p, "metal_dark", (0.3, 0.7, 1.4), (0.3, 0.55, 1.95), 0.05)         # gear lever
    p.cyl("metal_galv", (0, 1.2, 0.8), 0.05, 0.3, n=6, axis="y")                     # power take-off shaft
    p.box("metal_dark", (0, 1.65, 0.62), (0.34, 0.3, 0.12))                          # drawbar
    for s in (-1, 1):
        props_lib.rod(p, "metal_dark", (s * 0.35, 1.0, 1.0), (s * 0.35, 1.78, 0.74), 0.07)   # lift arms
        _tractor_rear_wheel(p, body, s)
        _tractor_front_wheel(p, body, s)
        p.box("metal_galv", (s * 0.33, -2.04, 1.5), (0.2, 0.07, 0.17))               # headlight bezels
        p.box("paint_yellow", (s * 0.33, -2.07, 1.5), (0.16, 0.05, 0.13))            # headlights
        p.box("paint_yellow", (s * 0.5, 1.22, 2.88), (0.14, 0.05, 0.07))              # work lights on the canopy's rear edge
    p.box("black", (0, -1.55, 0.52), (1.5, 0.08, 0.08))                              # front axle, up into the chassis
    return p


def cruiser(body="paint_white", stripe="navy", name="GV_SheriffCruiser_01"):
    """A police-style sedan: used for the sheriff (white/tan) and, recoloured, for FBI SUVs and the MIB sedan."""
    p = Prop(name)
    p.box("black", (0, 0, 0.45), (1.7, 4.6, 0.2))
    p.box(body, (0, 0, 0.75), (1.84, 4.8, 0.5))                                      # body
    p.box(body, (0, -0.1, 1.2), (1.6, 2.2, 0.45), taper=0.88)                        # cabin
    p.box("glass", (0, -0.1, 1.2), (1.66, 2.0, 0.34), taper=0.9)
    p.box(stripe, (0, 0, 0.75), (1.88, 4.0, 0.14))                                   # side stripe
    p.box("metal_galv", (0, -2.45, 0.55), (1.9, 0.14, 0.2))
    p.box("metal_galv", (0, 2.45, 0.55), (1.9, 0.14, 0.2))
    p.box("cloth_red", (-0.2, 0.0, 1.48), (0.45, 0.2, 0.1))                           # light bar: red and blue
    p.box("truck_blue", (0.2, 0.0, 1.48), (0.45, 0.2, 0.1))
    for s in (-1, 1):
        p.box("paint_yellow", (s * 0.65, -2.42, 0.82), (0.3, 0.05, 0.14))
        p.box("cloth_red", (s * 0.7, 2.42, 0.82), (0.26, 0.05, 0.14))
        for y in (-1.5, 1.5):
            wheel(p, "rubber", "metal_galv", s * 0.88, y, 0.34, 0.34, 0.24, n=10)
    return p


# The landed ship's dimensions, shared with Assets/Editor/FarmsteadLayout.cs (Ship* constants) which builds the colliders: change both.
SHIP_INNER_RADIUS = 5.2          # inside the walls
SHIP_WALL = 0.5                  # wall thickness
SHIP_DECK = 0.5                  # the deck is this high; a ramp climbs to it
SHIP_CEILING = 3.4               # underside of the ceiling
SHIP_PANELS = 12                 # wall panels round the ring; panel 0 (the front) is the doorway
SHIP_DOOR_HEIGHT = 2.4           # above the deck
SHIP_RAMP_RUN = 3.6              # how far the ramp reaches out from the deck edge


HULL_N = 40                      # sides of the saucer hull: 9 degrees each, so three of them are the width of the doorway (2.9 m at the rim)
HULL_PHASE = 4.5                 # turned so a hull face is centred on the front (-Y)
# the saucer's outline, (height, radius): a belly under the deck, a skirt, the widest rim, then a dome up to the cockpit. At the wall panels' height
# (the interior ring below) it stays outside them, so nothing of the walkable shell shows through the skin, and the rim stays within 0.4 m of
# the deck edge so the player cannot walk under a visible overhang.
BELLY_PROFILE = [(0.18, 3.4), (0.5, 6.0), (1.2, 6.05)]                                  # dark, under the rim
HULL_PROFILE = [(1.2, 6.05), (2.0, 6.25), (2.6, 6.1), (3.0, 5.9), (3.4, 5.6), (3.8, 4.9), (4.2, 4.0), (4.5, 3.0), (4.7, 2.0), (4.8, 1.0)]   # light, rim to dome


def _skin(p, colour, profile, n=HULL_N, phase=HULL_PHASE, cut_rings=(), cut_faces=(), cap=True, cap_bottom=None, cap_top=None):
    """A solid of revolution skinned by hand so a doorway can be left out of it: faces k in cut_faces between the rings in cut_rings (the quad
    between ring i and ring i + 1 is i) are not made. cap closes both ends; cap_bottom and cap_top override it for one end (the belly and the hull
    meet at z 1.2, and a disc at each end there would be a second floor 0.7 m over the deck)."""
    from math import cos, radians, sin
    c, s = cos(radians(phase)), sin(radians(phase))
    bm = p._bm(colour)
    vr = []
    for z, r in profile:
        ring = common.ring_z(z, 0.0, 0.0, max(r, 0.0001), max(r, 0.0001), n=n)
        vr.append([bm.verts.new(Vector((pt.x * c - pt.y * s, pt.x * s + pt.y * c, pt.z))) for pt in ring])
    for i in range(len(vr) - 1):
        for k in range(n):
            if i in cut_rings and k in cut_faces:
                continue
            a, b = vr[i], vr[i + 1]
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if cap if cap_bottom is None else cap_bottom:
        bm.faces.new(vr[0])
    if cap if cap_top is None else cap_top:
        bm.faces.new(vr[-1][::-1])
    bmesh.ops.delete(bm, geom=[v for ring in vr for v in ring if not v.link_faces], context="VERTS")      # the ring points of the cut faces, left with no face
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def crashed_ship(name="GV_CrashedShip_01"):
    """The crew's ship, landed hard: a flying saucer you can walk into. A saucer hull (belly, a glowing rim, a dome and a glass cockpit) with the
    doorway cut out of the front, a ramp down from it, an interior with a raised deck, a thin ring of wall panels, a flat ceiling, seats and
    a power core (the console is a separate model: terminals.py), belly thrusters, swept tail fins, a bent antenna and a torn patch. Level on purpose: the floor has to be walkable (the colliders
    are the cylinders and panels of FarmsteadBuilder.BuildLandedShip, under the skin). Front is -Y (the ramp), origin at the centre on the ground."""
    p = Prop(name)
    # the three hull faces round the front (-Y, 270 degrees). Face k is the quad between ring points k and k + 1, which sit at 360 * k / HULL_N + HULL_PHASE
    # degrees, so the face centred on 270 is k = 29 and the doorway is 28, 29, 30. (It was 29, 30, 31: centred on 279 degrees, a doorway 0.9 m off the
    # glow posts, the ramp and the wall panel that is the doorway in the colliders.)
    front = int(round((270 - HULL_PHASE) / (360 / HULL_N) - 0.5))
    door = (front - 1, front, front + 1)

    # the saucer: the skin with the doorway left out, a glowing rim band, two dark panel lines, the cockpit and the underside
    # (open where they meet, at z 1.2: capped there they were a disc 0.7 m above the deck, a second floor inside the ship)
    _skin(p, "alien_dark", BELLY_PROFILE, cut_rings=(1,), cut_faces=door, cap_top=False)
    _skin(p, "alien_grey", HULL_PROFILE, cut_rings=(0, 1, 2), cut_faces=door, cap_bottom=False)
    _skin(p, "glow_cyan", [(1.9, 6.28), (2.1, 6.28)], cut_rings=(0,), cut_faces=door, cap=False)
    _skin(p, "metal_dark", [(3.76, 4.95), (3.84, 4.95)], cap=False)
    _skin(p, "glass", [(4.7, 1.2), (5.0, 1.15), (5.5, 0.75), (5.9, 0.0001)], n=16, phase=0.0)
    for k in range(16):                                                                      # radial seams down the dome, so it reads as plates
        a = math.radians(k * 22.5 + 11.25)
        if abs(math.degrees(a) - 270) < 14:
            continue
        props_lib.rod(p, "metal_dark", (5.1 * math.cos(a), 5.1 * math.sin(a), 3.56), (1.5 * math.cos(a), 1.5 * math.sin(a), 4.72), 0.05)   # from inside the ceiling slab, not under it
    for k in range(4):                                                                       # belly thrusters
        a = math.radians(45 + k * 90)
        p.cyl("metal_dark", (2.4 * math.cos(a), 2.4 * math.sin(a), 0.1), 0.55, 0.22, n=8)
        p.cyl("glow_cyan", (2.4 * math.cos(a), 2.4 * math.sin(a), 0.02), 0.38, 0.05, n=8)

    # the inside, shared with the other varieties (ship_hulls.py): the deck, the sill and jambs of the doorway, the ring of wall panels, the ceiling, two seats, the
    # power core and a lit strip. The deck stays inside the dark belly (the belly runs from r 3.4 at z 0.18 to r 6.0 at z 0.5)
    ship_hulls.door_frame(p, "glow_cyan")
    ship_hulls.shell(p, ship_hulls.THEMES["saucer"])

    # outside: the ramp down from the doorway, as the part ShipRamp (hinged at the sill, exported open: ship_hulls.ramp), then swept tail fins, engine nacelles,
    # landing legs (fixed: the crashed ship sits on them), a bent antenna on the dome and a torn patch on the rim
    ship_hulls.ramp(p, "alien_grey", "glow_cyan")
    for sx in (-1, 1):
        p.box("metal_dark", (sx * 1.8, 6.5, 2.7), (0.14, 2.0, 2.0), rot=(0, sx * -14, 0))                 # swept tail fins
        p.cyl("metal_dark", (sx * 3.4, 5.6, 1.7), 0.5, 2.6, n=8, axis="y")                                  # engine nacelles, back of the rim
        p.cyl("glow_cyan", (sx * 3.4, 7.0, 1.7), 0.36, 0.08, n=8, axis="y")
    for k in range(4):                                                                       # landing legs under the rim, with pads
        a = math.radians(45 + k * 90)
        props_lib.rod(p, "metal_dark", (5.4 * math.cos(a), 5.4 * math.sin(a), 1.2), (6.5 * math.cos(a), 6.5 * math.sin(a), 0.08), 0.16)
        p.cyl("metal_dark", (6.5 * math.cos(a), 6.5 * math.sin(a), 0.04), 0.4, 0.08, n=8)
        ship_hulls.foot_anchor(p, k + 1, 6.5 * math.cos(a), 6.5 * math.sin(a), 0.8, 0.8)                  # where the pad stands on the ground
    # No scorch: the ship does not leave a burn mark. Where it stands on the ground it leaves dents under its feet (the contact anchors above: the game builds them,
    # FarmsteadShipMarks), so the mark follows the ship wherever it lands
    a = math.radians(40)
    # the torn plate on the rim: 1.7 m along the rim (tangent), 0.25 m out of it. It was built the other way round, 1.7 m long along the radius, which
    # put its inner end at r 5.15, through the wall panels (inner face 5.17) and into the room
    p.box("metal_dark", (6.25 * math.cos(a), 6.25 * math.sin(a), 2.15), (1.7, 0.25, 1.1), rot=(0, 0, 40 + 90))
    props_lib.rod(p, "metal_dark", (-1.2, 1.2, 4.7), (-2.0, 1.8, 6.6), 0.1)
    p.cyl("glow_cyan", (-2.0, 1.8, 6.7), 0.1, 0.18, n=6)
    return p


VEHICLES = {
    "pickup": (pickup, "Global"), "tractor": (tractor, "Global"), "cruiser": (cruiser, "Global"), "ship": (crashed_ship, "Global"),
}

def run():
    names = globals().get("VEHICLE_LIST") or list(VEHICLES)
    y = 0.0
    for key in names:
        fn, area = VEHICLES[key]
        prop = fn()
        name_wheels(prop)                                             # Wheel_FL..., not the Wheel@L@-1.5 placeholders, which would be written to interactions.json
        obj, coll = prop.finish()
        print(common.stats(obj))
        common.export_fbx(coll, f"Assets/Art/{area}/Vehicles/{prop.name}.fbx")
        obj.location.y = y
        y += obj.dimensions.y + 3
    props_lib.write_interactions()                                    # the ship's ramp part (ship_hulls.py) goes into art/data/interactions.json
    print("vehicles done", names)


if __name__ == "__main__":
    run()
