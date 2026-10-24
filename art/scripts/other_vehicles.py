"""The rest of the vehicle list (#357): motorcycle, ATV, jeep, flatbed trailer, semi truck with box and tanker trailers, school bus, fire truck.

Built with the road-vehicle helpers of vehicles.py (`body_loft`, `glasshouse`, `car_wheel`, `arch`, `mirror`) the way cars.py builds its cars: faceted, palette colours
only, facing -Y, origin on the ground at the centre of the footprint, wheels on z = 0, 1 unit = 1 m. cars.py calls these through its family table, so every
one comes in its paint jobs and as New and Damaged; they are not run on their own.
"""

import importlib
import math
import sys
from math import cos, radians, sin
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Blender is shared by several sessions, each running scripts from its own checkout: drop modules another checkout imported first (as vehicles.py does)
for _n in ("common", "props_lib", "emitters", "ship_hulls", "vehicles"):
    _m = sys.modules.get(_n)
    if _m is not None and Path(getattr(_m, "__file__", "") or "").resolve().parent != _HERE:
        sys.modules.pop(_n, None)
import common
import props_lib
import vehicles
for _m in (common, props_lib, vehicles):
    importlib.reload(_m)
Prop = props_lib.Prop
rod = props_lib.rod
V = vehicles.V


def srod(p, colour, a, b, w=0.06, h=None):
    """A beam that holds the model together (a fork leg, a frame tube, a landing leg): rod(), marked structural so Prop.damage() never drops it."""
    rod(p, colour, a, b, w, h)
    p.keep_solid(tuple((a[i] + b[i]) / 2 for i in range(3)), (0, 0, 0), new=True)


def keep(p, center):
    """Mark the part at `center` structural (see srod); the part must already be added."""
    p.keep_solid(tuple(center), (0, 0, 0), new=True)


# ===== Shared pieces ==============================================================================================================
def truck_wheel(p, trim, x, y, r, w, dual=False, n=12):
    """A truck wheel on the X axis (tyre, rim, dish, cap); dual adds the inner tyre of a pair and the hub that joins them."""
    out = 1 if x >= 0 else -1
    vehicles.car_wheel(p, trim, x, y, r, w, n=n)
    if dual:
        xi = x - out * (w + 0.03)
        p.cyl("rubber", (xi, y, r), r, w, n=n, axis="x")
        p.cyl("metal_dark", (x - out * (w + 0.03) / 2, y, r), r * 0.3, 2 * w + 0.03, n=8, axis="x")


def mudguard(p, colour, x, y, zc, r, width, thick=0.05, angles=(20, 50, 80, 100, 130, 160)):
    """A curved mudguard: wide beams on an arc over a wheel centred at (y, zc), radius r, `width` wide in X."""
    pts = [(y + r * cos(radians(a)), zc + r * sin(radians(a))) for a in angles]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        rod(p, colour, (x, y0, z0), (x, y1, z1), width, thick)


def lug_wheel(p, trim, x, y, r, w, lugs=10, n=10):
    """A knobby wheel on the X axis (an ATV's or a tractor's): a tyre a little smaller than r, radial lugs reaching r, a rim and a cap."""
    out = 1 if x >= 0 else -1
    rt = r - 0.04
    p.cyl("rubber", (x, y, r), rt, w, n=n, axis="x")
    for k in range(lugs):
        a = radians(k * 360.0 / lugs + 180.0 / lugs)
        rod(p, "rubber", (x, y + (rt - 0.02) * cos(a), r + (rt - 0.02) * sin(a)), (x, y + r * cos(a), r + r * sin(a)), w * 0.75, 0.07)
    xo = x + out * (w / 2 + 0.006)
    p.cyl(trim, (xo, y, r), r * 0.55, 0.02, n=n, axis="x")
    p.cyl("metal_dark", (xo + out * 0.012, y, r), r * 0.18, 0.02, n=6, axis="x")


def lamp(p, x, y, z, r, length=0.1, rim="metal_galv", lens="paint_yellow", facing=-1):
    """A round headlight or lamp on the Y axis: a rim and a lens that reaches back into it (facing -1 looks out the front, +1 out the back)."""
    p.cyl(rim, (x, y, z), r, length, n=8, axis="y")
    p.cyl(lens, (x, y + facing * length * 0.3, z), r * 0.75, length * 0.8, n=8, axis="y")


# ===== Motorcycle ================================================================================================================
def motorcycle(body="cloth_red", name="GV_Motorcycle_01"):
    """A road motorcycle (2.2 m): spoked-look wheels, forks, a lofted tank and tail, an engine with cylinders, a seat, bars with mirrors, a round headlight,
    mudguards, swing arm and shocks, an exhaust and a tail light."""
    p = Prop(name)
    r, fy, ry = 0.32, -0.7, 0.7
    for y, w in ((fy, 0.14), (ry, 0.18)):
        p.cyl("rubber", (0, y, r), r, w, n=12, axis="x")
        for s in (-1, 1):
            p.cyl("metal_galv", (s * (w / 2 + 0.006), y, r), r * 0.62, 0.014, n=12, axis="x")           # rims
            p.cyl("black", (s * (w / 2 + 0.014), y, r), r * 0.4, 0.016, n=8, axis="x")
        p.cyl("metal_dark", (0, y, r), r * 0.14, w + 0.2, n=6, axis="x")                                 # the axle
    for s in (-1, 1):
        srod(p, "metal_galv", (s * 0.1, fy, r), (s * 0.09, -0.5, 1.0), 0.05)                             # fork legs
        srod(p, "metal_dark", (s * 0.1, 0.25, 0.46), (s * 0.1, ry, r), 0.045)                            # swing arm
        rod(p, "metal_galv", (s * 0.11, 0.55, 0.85), (s * 0.1, 0.68, 0.4), 0.04)                         # rear shocks
        p.box("black", (s * 0.4, -0.5, 1.03), (0.1, 0.05, 0.03))                                         # grips
        rod(p, "metal_dark", (s * 0.34, -0.5, 1.03), (s * 0.4, -0.52, 1.28), 0.02)                       # mirror stems
        p.box("black", (s * 0.4, -0.52, 1.3), (0.1, 0.03, 0.07))
        rod(p, "metal_dark", (s * 0.1, 0.0, 0.42), (s * 0.23, 0.08, 0.3), 0.04)                          # foot peg arms
        p.box("black", (s * 0.25, 0.1, 0.3), (0.1, 0.12, 0.03))
        p.cyl("metal_galv", (s * 0.11, -0.12, 0.7), 0.09, 0.3, n=8)                                      # cylinders
        p.cyl("metal_dark", (s * 0.11, -0.12, 0.88), 0.1, 0.06, n=8)
    p.box("black", (0, -0.5, 1.0), (0.26, 0.08, 0.06))                                                   # top clamp
    keep(p, (0, -0.5, 1.0))
    rod(p, "metal_dark", (-0.4, -0.5, 1.03), (0.4, -0.5, 1.03), 0.03)                                    # handlebar
    srod(p, "black", (0, -0.5, 0.95), (0, 0.55, 0.78), 0.07)                                             # frame spine
    srod(p, "black", (0, -0.5, 0.95), (0, -0.1, 0.4), 0.06)                                              # down tube
    srod(p, "black", (0, 0.1, 0.78), (0, 0.25, 0.46), 0.06)                                              # seat stay
    p.box("metal_dark", (0, -0.05, 0.45), (0.3, 0.42, 0.3))                                              # crankcase
    p.box("metal_dark", (0, 0.15, 0.4), (0.2, 0.2, 0.22))                                                # gearbox
    keep(p, (0, 0.15, 0.4))
    p.loft_rings(body, [common.ring_y(y, 0, z, w, h, n=8, p=2.4) for y, z, w, h in
                        ((-0.42, 0.9, 0.1, 0.07), (-0.3, 0.95, 0.17, 0.13), (0.0, 0.97, 0.18, 0.14), (0.2, 0.93, 0.13, 0.1))])   # the tank
    p.box("black", (0, 0.32, 0.9), (0.26, 0.55, 0.1), taper=0.9)                                         # seat
    p.loft_rings(body, [common.ring_y(y, 0, z, w, h, n=8, p=2.4) for y, z, w, h in
                        ((0.55, 0.93, 0.12, 0.08), (0.75, 0.93, 0.1, 0.08), (0.95, 0.9, 0.06, 0.05))])   # the tail cowl
    lamp(p, 0, -0.62, 0.95, 0.12, 0.12)                                                                 # headlight
    p.box(body, (0, -0.7, 0.68), (0.13, 0.5, 0.03))                                                      # front mudguard
    for s in (-1, 1):
        rod(p, body, (s * 0.06, -0.7, 0.66), (s * 0.09, -0.52, 0.92), 0.03)                              # its stays to the fork
    p.box(body, (0, 0.78, 0.66), (0.2, 0.42, 0.03))                                                      # rear mudguard
    rod(p, "black", (0, 0.6, 0.78), (0, 0.8, 0.66), 0.04)
    p.cyl("metal_galv", (0.17, 0.3, 0.35), 0.04, 0.9, n=6, axis="y")                                     # exhaust pipe
    p.cyl("metal_galv", (0.17, 0.82, 0.4), 0.065, 0.4, n=8, axis="y")                                    # muffler
    rod(p, "metal_galv", (0.11, -0.12, 0.55), (0.17, 0.0, 0.36), 0.04)                                   # header
    p.box("cloth_red", (0, 0.97, 0.9), (0.1, 0.07, 0.06))                                               # tail light, into the cowl
    p.box("paint_white", (0, 1.0, 0.64), (0.18, 0.04, 0.1))                                              # plate
    return p


# ===== ATV ========================================================================================================================
def atv(body="cloth_red", name="GV_ATV_01"):
    """A quad bike (1.9 m): knobby wheels on arms, a lofted body with a tank, seat and racks, handlebars, headlights, fenders, foot boards, exhaust."""
    p = Prop(name)
    p.box("black", (0, 0, 0.45), (0.5, 1.5, 0.18))                                                       # chassis
    p.loft_rings(body, [common.ring_y(y, 0, z, w, h, n=8, p=2.8) for y, z, w, h in
                        ((-1.0, 0.68, 0.3, 0.16), (-0.8, 0.72, 0.4, 0.2), (-0.2, 0.7, 0.38, 0.2), (0.1, 0.66, 0.32, 0.16))])   # front body
    p.box("black", (0, 0.35, 0.78), (0.34, 0.8, 0.14), taper=0.92)                                       # seat
    p.box(body, (0, 0.93, 0.69), (0.5, 0.4, 0.14))                                                       # rear body, up to the rack and back to the seat
    p.box("metal_dark", (0, 0.95, 0.76), (0.7, 0.5, 0.04))                                               # rear rack
    p.box("metal_dark", (0, -0.9, 0.9), (0.6, 0.4, 0.04))                                                # front rack
    p.box(body, (0, -0.2, 0.95), (0.3, 0.38, 0.18))                                                      # fuel tank
    for s in (-1, 1):
        for y in (-0.62, 0.6):
            lug_wheel(p, "metal_galv", s * 0.52, y, 0.3, 0.22)
            srod(p, "metal_dark", (s * 0.25, y, 0.48), (s * 0.48, y, 0.32), 0.06)                         # suspension arms
            mudguard(p, body, s * 0.52, y, 0.3, 0.37, 0.26, angles=(25, 55, 90, 125, 155))
            srod(p, "metal_dark", (s * 0.2, y, 0.5), (s * 0.52, y, 0.64), 0.06)                           # a stay from the chassis to the guard
        p.box("black", (s * 0.42, 0.05, 0.3), (0.36, 0.55, 0.04))                                        # foot boards
        rod(p, "metal_dark", (s * 0.25, 0.05, 0.42), (s * 0.28, 0.05, 0.32), 0.05)
        p.box("black", (s * 0.34, -0.45, 1.05), (0.1, 0.05, 0.03))                                       # grips
        lamp(p, s * 0.2, -1.04, 0.72, 0.09, 0.1)                                                         # headlights
        p.box("cloth_red", (s * 0.22, 1.14, 0.7), (0.1, 0.05, 0.07))
    srod(p, "metal_dark", (0, -0.3, 0.75), (0, -0.45, 1.05), 0.05)                                       # steering column
    rod(p, "metal_dark", (-0.36, -0.45, 1.05), (0.36, -0.45, 1.05), 0.035)                               # handlebar
    p.cyl("metal_galv", (0.3, 0.7, 0.42), 0.05, 0.6, n=6, axis="y")                                      # exhaust
    return p


# ===== Jeep ======================================================================================================================
def jeep(body="tractor_green", name="GV_Jeep_01"):
    """A 4x4 (3.6 m): a lofted hood and open tub, a seven-slot grille with round lights, a windscreen frame, roll bar, seats, fender flares, bumpers with tow
    hooks, a spare wheel on the tail and fat wheels."""
    p = Prop(name)
    p.box("black", (0, 0, 0.5), (1.4, 3.4, 0.15))                                                        # frame
    vehicles.body_loft(p, body, [(-1.78, 0.78, 0.6, 1.05, 0.04), (-1.6, 0.84, 0.55, 1.12, 0.04), (-0.55, 0.85, 0.55, 1.12, 0.04)])   # hood
    for k in range(7):
        p.box("black", (-0.42 + k * 0.14, -1.78, 0.86), (0.07, 0.04, 0.22))                             # grille slots
    for s in (-1, 1):
        lamp(p, s * 0.62, -1.76, 0.9, 0.13, 0.12)                                                        # round headlights
        mudguard(p, body, s * 0.9, -1.15, 0.38, 0.5, 0.24, angles=(15, 45, 75, 105, 135, 165))
        mudguard(p, body, s * 0.9, 1.15, 0.38, 0.5, 0.24, angles=(15, 45, 75, 105, 135, 165))
        p.box(body, (s * 0.85, 0.6, 0.85), (0.1, 2.2, 0.55))                                             # tub sides
        p.box("black", (s * 0.85, 0.6, 1.14), (0.12, 2.2, 0.05))                                         # their top rail
        for y in (-1.15, 1.15):
            vehicles.car_wheel(p, "metal_galv", s * 0.88, y, 0.38, 0.3, n=12)
        rod(p, "black", (s * 0.8, -0.55, 1.1), (s * 0.78, -0.5, 1.6), 0.06)                              # windscreen posts
        rod(p, "black", (s * 0.8, 0.5, 1.1), (s * 0.8, 0.5, 1.8), 0.07)                                  # roll bar uprights
        rod(p, "black", (s * 0.8, 1.5, 1.1), (s * 0.8, 1.5, 1.7), 0.06)
        rod(p, "black", (s * 0.8, 0.5, 1.8), (s * 0.8, 1.5, 1.7), 0.06)
        vehicles.mirror(p, body, s, 0.76, -0.5, 1.4)
        rod(p, "black", (s * 0.55, -1.9, 0.52), (s * 0.55, -1.98, 0.62), 0.05)                           # tow hooks
        p.box("fabric_brown", (s * 0.4, 0.15, 0.72), (0.5, 0.5, 0.18))                                   # front seats
        p.box("fabric_brown", (s * 0.4, 0.2, 1.05), (0.5, 0.1, 0.5), rot=(-8, 0, 0))
    p.box(body, (0, 0.6, 0.6), (1.7, 2.2, 0.06))                                                         # tub floor
    for s in (-1, 1):
        p.box(body, (s * 0.74, 1.15, 0.78), (0.12, 1.0, 0.3))                                            # wheel wells: the rear tyres reach up into the tub
    p.box("fabric_brown", (0, 1.15, 0.72), (1.4, 0.5, 0.18))                                             # rear bench
    rod(p, "black", (-0.78, -0.5, 1.6), (0.78, -0.5, 1.6), 0.06)                                         # windscreen header
    p.box("glass", (0, -0.52, 1.35), (1.5, 0.04, 0.45), rot=(-10, 0, 0))                                 # windscreen
    rod(p, "black", (-0.8, 0.5, 1.8), (0.8, 0.5, 1.8), 0.07)                                             # roll bar
    rod(p, "black", (-0.8, 1.5, 1.7), (0.8, 1.5, 1.7), 0.06)
    p.box("black", (0, -1.88, 0.55), (1.8, 0.2, 0.2))                                                    # bumpers
    p.box("black", (0, 1.8, 0.55), (1.8, 0.2, 0.2))
    p.box(body, (0, 1.73, 0.85), (1.7, 0.06, 0.5))                                                        # tailgate
    p.box(body, (0, -0.3, 0.95), (1.6, 0.5, 0.3))                                                         # dashboard
    p.box("black", (0, -1.6, 0.52), (1.6, 0.4, 0.04))
    p.cyl("rubber", (0, 2.12, 0.85), 0.36, 0.22, n=12, axis="y")                                         # spare wheel on the tail
    p.cyl("metal_galv", (0, 2.24, 0.85), 0.22, 0.03, n=10, axis="y")
    srod(p, "black", (0, 1.74, 0.75), (0, 2.05, 0.85), 0.08)                                               # its mount
    p.cyl("black", (0.4, -0.02, 1.0), 0.17, 0.03, n=8, rot=(-35, 0, 0))                                  # steering wheel, driver on the left (+X)
    rod(p, "black", (0.4, -0.2, 0.95), (0.4, -0.02, 1.0), 0.05)
    p.box("cloth_red", (0.78, 1.78, 0.9), (0.12, 0.05, 0.1))                                             # tail lights
    p.box("cloth_red", (-0.78, 1.78, 0.9), (0.12, 0.05, 0.1))
    return p


# ===== Flatbed trailer ===========================================================================================================
def trailer_flatbed(name="GV_TrailerFlatbed_01"):
    """A 4 m flatbed trailer: a plank deck on a frame with cross members, an axle with springs and two wheels under mudguards, low sides on posts,
    a headboard, an A-frame drawbar with a coupler, a jack and tail lights."""
    p = Prop(name)
    for k in range(7):
        p.box("wood_grey", (-0.93 + k * 0.31, 0, 0.86), (0.29, 4.0, 0.06))                              # deck planks
    for s in (-1, 1):
        p.box("metal_dark", (s * 1.05, 0, 0.76), (0.1, 4.0, 0.14))                                       # side rails
        vehicles.car_wheel(p, "metal_galv", s * 1.2, 0.8, 0.45, 0.25, n=12)
        mudguard(p, "metal_dark", s * 1.2, 0.8, 0.45, 0.55, 0.3, angles=(20, 50, 80, 100, 130, 160))
        rod(p, "metal_dark", (s * 0.8, 0.8, 0.7), (s * 1.1, 0.8, 0.45), 0.06)                            # axle ends
        for y in (-1.6, -0.5, 0.6, 1.7):
            p.box("wood_dark", (s * 1.05, y, 1.0), (0.08, 0.08, 0.4))                                    # side posts
        p.box("wood_dark", (s * 1.05, 0, 1.17), (0.06, 4.0, 0.1))                                        # side top rails
        p.box("wood_dark", (s * 1.05, 0, 1.06), (0.04, 4.0, 0.1))                                        # side boards
        p.box("cloth_red", (s * 1.0, 2.03, 0.92), (0.12, 0.05, 0.1))                                     # tail lights
        p.box("paint_yellow", (s * 1.09, 1.5, 1.06), (0.05, 0.12, 0.05))                                 # side markers
        srod(p, "metal_dark", (s * 0.5, -1.9, 0.76), (s * 0.06, -3.2, 0.74), 0.1)                        # A-frame drawbar
    for y in (-1.9, -0.6, 0.6, 1.8):
        p.box("metal_dark", (0, y, 0.74), (2.2, 0.1, 0.1))                                               # cross members
        keep(p, (0, y, 0.74))
    p.box("metal_dark", (0, 0.8, 0.45), (2.4, 0.08, 0.08))                                               # axle
    for s in (-1, 1):
        rod(p, "metal_dark", (s * 0.4, 0.4, 0.5), (s * 0.4, 1.2, 0.5), 0.06)                             # leaf springs
    p.box("wood_dark", (0, -1.96, 1.1), (2.2, 0.08, 0.45))                                               # headboard
    p.box("wood_dark", (0, 1.96, 1.06), (2.2, 0.06, 0.1))                                                # tail board
    p.box("metal_galv", (0, -3.3, 0.72), (0.2, 0.3, 0.15))                                               # coupler
    keep(p, (0, -3.3, 0.72))
    p.cyl("metal_dark", (0, -3.3, 0.6), 0.06, 0.2, n=6)
    p.box("metal_dark", (0, -2.8, 0.74), (0.5, 0.1, 0.1))                                              # jack bracket
    keep(p, (0, -2.8, 0.74))
    srod(p, "metal_dark", (0, -2.8, 0.74), (0, -2.8, 0.08), 0.07)                                        # jack
    p.cyl("metal_galv", (0, -2.8, 0.04), 0.14, 0.08, n=6)
    for s in (-1, 1):
        rod(p, "black", (s * 0.12, -3.25, 0.72), (s * 0.45, -1.8, 0.8), 0.02)                           # safety chains
    return p


# ===== Semi truck and trailers ====================================================================================================
def semi_tractor(body="cloth_red", name="GV_Semi_01"):
    """A conventional semi tractor (7.4 m, 3.9 m with the stacks): a long lofted hood, a big chrome grille, bumper and lights, a tall cab with a sleeper,
    a roof deflector, two chrome stacks, fuel tanks, a fifth wheel, a steering axle and two driven axles on dual tyres, mirrors, steps and mud flaps."""
    p = Prop(name)
    rail = lambda s: p.box("black", (s * 0.55, 0.1, 0.9), (0.2, 7.0, 0.3))                               # frame rails
    for s in (-1, 1):
        rail(s)
    for y in (-2.6, -0.4, 1.6, 3.0):
        p.box("black", (0, y, 0.9), (1.1, 0.2, 0.2))                                                     # cross members
    vehicles.body_loft(p, body, [(-3.7, 0.8, 0.85, 1.75, 0.06), (-3.55, 0.9, 0.78, 1.9, 0.07), (-1.6, 0.95, 0.78, 2.0, 0.07), (-1.15, 0.97, 0.78, 2.05, 0.05)])   # hood
    p.box("black", (0, -3.7, 1.3), (1.3, 0.05, 0.85))                                                    # grille, on the nose
    for k in range(5):
        p.box("metal_galv", (-0.5 + k * 0.25, -3.745, 1.3), (0.05, 0.04, 0.85))                          # chrome bars
    p.box("metal_galv", (0, -3.8, 0.65), (2.5, 0.3, 0.4))                                                # bumper
    for s in (-1, 1):
        lamp(p, s * 0.78, -3.62, 1.55, 0.16, 0.14)
        mudguard(p, body, s * 1.1, -2.1, 0.5, 0.62, 0.45, angles=(20, 50, 80, 100, 130, 160))
    vehicles.body_loft(p, body, [(-1.15, 1.22, 0.85, 2.05, 0.06), (1.8, 1.22, 0.85, 2.05, 0.06)])        # the cab's lower body
    vehicles.glasshouse(p, "glass", [(-1.1, 1.1, 1.08, 2.05, 2.1), (-0.8, 1.1, 0.98, 2.05, 3.05), (0.35, 1.1, 0.98, 2.05, 3.05), (0.5, 1.1, 1.08, 2.05, 2.1)])
    vehicles.glasshouse(p, body, [(0.5, 1.1, 0.98, 2.05, 3.05), (1.8, 1.1, 0.98, 2.05, 3.05)])         # the sleeper
    p.box(body, (0, 0.5, 3.07), (2.0, 2.6, 0.1))                                                         # cab roof
    p.box(body, (0, 0.2, 3.3), (2.2, 1.3, 0.5), rot=(10, 0, 0))                                          # roof deflector
    for s in (-1, 1):
        rod(p, body, (s * 1.1, -1.1, 2.07), (s * 0.98, -0.8, 3.05), 0.1)                                  # A pillars
        rod(p, body, (s * 1.1, 0.5, 2.05), (s * 0.98, 0.5, 3.05), 0.1)                                    # B pillars
        p.box("black", (s * 1.2, -0.3, 1.5), (0.04, 0.03, 0.9))                                          # door seams
        p.box("black", (s * 1.2, 0.5, 1.5), (0.04, 0.03, 0.9))
        p.box("metal_galv", (s * 1.23, 0.4, 1.75), (0.04, 0.2, 0.04))                                   # handles
        p.box("black", (s * 1.3, -0.1, 1.14), (0.5, 0.7, 0.06))                                          # steps, on the fuel tanks
        rod(p, "metal_galv", (s * 1.0, -0.95, 2.4), (s * 1.5, -1.0, 2.7), 0.04)                         # mirror arms
        p.box("black", (s * 1.55, -1.0, 2.65), (0.1, 0.12, 0.55))
        p.cyl("metal_galv", (s * 1.35, 1.3, 2.4), 0.1, 2.6, n=8)                                         # chrome stacks
        rod(p, "metal_galv", (s * 1.15, 1.3, 1.5), (s * 1.35, 1.3, 1.5), 0.08)
        rod(p, "metal_galv", (s * 1.0, 1.3, 2.9), (s * 1.35, 1.3, 2.9), 0.08)
        p.cyl("metal_galv", (s * 1.3, 0.1, 0.7), 0.4, 1.2, n=12, axis="y")                               # fuel tanks, between the steer and drive tyres
        p.box("black", (s * 0.78, 0.1, 0.85), (0.5, 0.3, 0.15))                                          # tank straps to the frame
        rod(p, "black", (s * 0.55, -3.4, 0.9), (s * 0.55, -3.75, 0.7), 0.12)                              # bumper brackets
        p.box("cloth_red", (s * 0.6, 3.61, 0.95), (0.2, 0.05, 0.12))                                     # tail lights
        p.box("black", (s * 1.0, 3.35, 0.6), (0.7, 0.04, 0.5))                                           # mud flaps
        truck_wheel(p, "metal_galv", s * 1.05, -2.1, 0.5, 0.3, dual=False)                               # steer axle
        for y in (1.5, 2.8):
            truck_wheel(p, "metal_galv", s * 1.05, y, 0.5, 0.3, dual=True)                               # driven axles
        for y in (1.5, 2.8):
            mudguard(p, "black", s * 0.7, y, 0.5, 0.56, 0.9, angles=(45, 75, 105, 135))             # one guard per drive axle, clear of the dual tyres
    p.box("black", (0, -2.1, 0.52), (2.2, 0.12, 0.12))                                                   # axles
    p.box("black", (0, 1.5, 0.52), (2.2, 0.12, 0.12))
    p.box("black", (0, 2.8, 0.52), (2.2, 0.12, 0.12))
    p.cyl("black", (0, 2.2, 1.15), 0.62, 0.12, n=12)                                                     # fifth wheel
    p.box("metal_dark", (0, 2.2, 1.04), (1.0, 1.0, 0.12))
    for x in (-0.6, -0.3, 0.0, 0.3, 0.6):
        p.box("orange_cat", (x, -0.75, 3.15), (0.14, 0.06, 0.08))                                        # roof marker lights
    for s in (-1, 1):
        p.cyl("metal_dark", (s * 0.4, -0.9, 0.7), 0.14, 0.5, n=8, axis="y")                              # air tanks
    return p


def _box_trailer_underside(p, y0, y1):
    """The running gear shared by the semi trailers: frame rails, tandem axles on dual tyres, landing legs, mud flaps, a rear bumper and lights."""
    for s in (-1, 1):
        p.box("black", (s * 0.6, (y0 + y1) / 2, 1.05), (0.2, y1 - y0, 0.2))                              # frame rails
        for y in (4.2, 5.5):
            truck_wheel(p, "metal_galv", s * 1.05, y, 0.5, 0.3, dual=True)
        p.box("black", (s * 1.0, 6.62, 0.7), (0.8, 0.04, 0.55))                                          # mud flaps
        p.box("black", (s * 1.0, 3.35, 0.7), (0.8, 0.04, 0.55))
        srod(p, "metal_dark", (s * 0.9, -5.2, 1.3), (s * 0.9, -5.2, 0.1), 0.14)                          # landing legs, up into the box or its saddle
        p.box("metal_dark", (s * 0.9, -5.2, 0.05), (0.4, 0.4, 0.1))
        keep(p, (s * 0.9, -5.2, 0.05))
        p.box("cloth_red", (s * 1.0, 7.07, 0.98), (0.2, 0.05, 0.12))                                      # tail lights, on the bar's back face
        p.box("orange_cat", (s * 1.0, 7.07, 0.84), (0.2, 0.05, 0.08))
        p.box("paint_white", (s * 0.75, 7.07, 0.9), (0.12, 0.05, 0.1))
        rod(p, "metal_dark", (s * 0.9, 5.5, 1.0), (s * 1.05, 5.5, 0.5), 0.1)                              # axle ends
        rod(p, "metal_dark", (s * 0.9, 4.2, 1.0), (s * 1.05, 4.2, 0.5), 0.1)
    for y in (-4.0, -1.5, 1.0, 3.5, 5.0):
        p.box("black", (0, y, 1.05), (1.2, 0.15, 0.2))
    p.box("metal_dark", (0, 4.2, 0.52), (2.2, 0.12, 0.12))
    p.box("metal_dark", (0, 5.5, 0.52), (2.2, 0.12, 0.12))
    p.box("metal_dark", (0, -6.3, 0.95), (1.0, 1.0, 0.1))                                                # kingpin plate, near the front
    p.box("metal_dark", (0, 6.95, 0.9), (2.4, 0.2, 0.3))                                                 # rear underride bar


def box_trailer(body="paint_white", name="GV_SemiTrailer_Box_01"):
    """A 14 m dry-van trailer: a ribbed box on a frame, roof edge rails, rear doors with lock bars, an aero skirt, marker lights, tandem axles, landing legs."""
    p = Prop(name)
    _box_trailer_underside(p, -6.9, 6.9)
    p.box(body, (0, -0.1, 2.625), (2.5, 14.0, 2.95))                                                     # the box
    for y in [-6.4 + k * 1.0 for k in range(13)]:
        for s in (-1, 1):
            p.box("metal_galv", (s * 1.255, y, 2.625), (0.05, 0.08, 2.85))                                # side ribs
    for s in (-1, 1):
        p.box("metal_dark", (s * 1.25, -0.1, 4.12), (0.1, 14.0, 0.08))                                   # roof rails
        p.box("metal_dark", (s * 1.25, -0.1, 1.2), (0.1, 14.0, 0.1))                                     # bottom rails
        p.box("black", (s * 1.05, -0.1, 0.9), (0.04, 7.0, 0.5))                                          # aero skirts
        for y in [-6.0 + k * 1.6 for k in range(8)]:
            p.box("orange_cat", (s * 1.27, y, 1.6), (0.04, 0.12, 0.07))                                  # side marker lights
        p.box(body, (s * 0.62, 6.93, 2.625), (1.2, 0.04, 2.85))                                           # rear doors
        rod(p, "metal_galv", (s * 0.15, 6.97, 1.4), (s * 0.15, 6.97, 3.9), 0.05)                         # lock bars
        for z in (1.8, 3.1, 3.8):
            p.box("metal_galv", (s * 1.2, 6.96, z), (0.1, 0.05, 0.1))                                    # hinges
    p.box("black", (0, 6.93, 2.625), (0.05, 0.05, 2.85))                                                  # door seam
    for z in (1.9, 2.7, 3.5):
        p.box("metal_galv", (0, -7.1, z), (2.3, 0.05, 0.08))                                             # front corrugations
    p.box("black", (0, 0, 4.12), (2.3, 13.6, 0.04))                                                      # roof panel line
    return p


def tanker_trailer(name="GV_SemiTrailer_Tanker_01"):
    """A 13 m tanker trailer: a faceted cylinder tank with ring bands and end domes, a walkway with rails and hatches, a rear valve box and ladder."""
    p = Prop(name)
    _box_trailer_underside(p, -6.9, 6.9)
    ring = lambda y, r: common.ring_y(y, 0, 2.55, r, r, n=12)
    p.loft_rings("metal_galv", [ring(-6.9, 0.5), ring(-6.5, 1.0), ring(-5.5, 1.2), ring(5.5, 1.2), ring(6.5, 1.05), ring(6.9, 0.55)])   # the tank
    for y in (-3.0, 0.0, 3.0):
        p.loft_rings("metal_dark", [ring(y - 0.07, 1.25), ring(y + 0.07, 1.25)])                         # ring bands
    for s in (-1, 1):
        p.box("metal_dark", (s * 0.8, 0.0, 1.27), (0.3, 11.0, 0.25))                                     # saddles to the frame, long enough to meet the landing legs
        for y in (-3.0, 3.0):
            p.box("metal_dark", (s * 0.8, y, 1.4), (0.3, 0.4, 0.6))
    p.box("black", (0, 0, 3.73), (0.5, 9.0, 0.16))                                                       # walkway (thick enough to meet the faceted top at its edges)
    for s in (-1, 1):
        rod(p, "metal_dark", (s * 0.25, -4.5, 3.8), (s * 0.25, -4.5, 4.2), 0.04)                         # rail posts
        rod(p, "metal_dark", (s * 0.25, 4.5, 3.8), (s * 0.25, 4.5, 4.2), 0.04)
        rod(p, "metal_dark", (s * 0.25, -4.5, 4.2), (s * 0.25, 4.5, 4.2), 0.04)
    for y in (-3.0, 0.0, 3.0):
        p.cyl("metal_dark", (0, y, 3.9), 0.28, 0.2, n=8)                                                  # hatches
        p.cyl("metal_galv", (0, y, 4.02), 0.2, 0.06, n=8)
    p.box("metal_dark", (0, 6.7, 1.5), (1.2, 0.5, 0.6))                                                  # valve box
    p.cyl("black", (0.3, 6.95, 1.5), 0.08, 0.2, n=6, axis="y")
    p.cyl("black", (-0.3, 6.95, 1.5), 0.08, 0.2, n=6, axis="y")
    for s in (-1, 1):
        rod(p, "metal_dark", (s * 0.3, 6.93, 1.3), (s * 0.3, 6.93, 3.0), 0.05)                           # ladder rails, up the rear dome
    for z in (1.5, 1.85, 2.2, 2.55, 2.9):
        p.box("metal_dark", (0, 6.93, z), (0.6, 0.04, 0.04))
    return p


# ===== School bus ================================================================================================================
def school_bus(body="paint_yellow", name="GV_Bus_School_01"):
    """A conventional school bus (10.5 m): a lofted hood and body, a row of side windows between yellow pillars, black stripes, a destination board,
    flashing lights, a swing-out stop arm, crossview mirrors, a folding door, a rear emergency door, roof hatches and dual rear wheels."""
    p = Prop(name)
    p.box("black", (0, 0.2, 0.62), (1.4, 9.4, 0.25))                                                     # chassis
    vehicles.body_loft(p, body, [(-5.25, 0.85, 0.65, 1.2, 0.05), (-5.1, 1.0, 0.55, 1.4, 0.06), (-4.0, 1.1, 0.55, 1.5, 0.06), (-3.8, 1.2, 0.55, 1.85, 0.05)])   # hood
    vehicles.body_loft(p, body, [(-3.8, 1.2, 0.55, 1.85, 0.05), (4.9, 1.2, 0.55, 1.85, 0.05)])           # the body
    vehicles.glasshouse(p, "glass", [(-3.8, 1.18, 1.14, 1.85, 1.9), (-3.65, 1.18, 1.1, 1.85, 3.0), (4.7, 1.18, 1.1, 1.85, 3.0), (4.9, 1.18, 1.14, 1.85, 1.9)])
    p.box(body, (0, 0.5, 3.04), (2.3, 8.6, 0.12))                                                        # roof
    for y in [-2.7 + k * 0.95 for k in range(8)]:
        for s in (-1, 1):
            rod(p, body, (s * 1.18, y, 1.87), (s * 1.1, y, 3.0), 0.09)                                    # window pillars
    for s in (-1, 1):
        for z in (0.95, 1.3, 1.55):
            p.box("black", (s * 1.19, 0.5, z), (0.06, 8.6, 0.07))                                       # stripes
        rod(p, body, (s * 1.18, -3.8, 1.87), (s * 1.12, -3.65, 3.0), 0.1)
        vehicles.mirror(p, "black", s, 1.0, -3.72, 2.6)
        rod(p, "metal_dark", (s * 1.0, -4.6, 1.4), (s * 1.3, -5.0, 2.1), 0.04)                           # crossview mirror arms
        p.cyl("metal_galv", (s * 1.3, -5.0, 2.2), 0.14, 0.06, n=8, axis="y")
        for y in (-5.2,):
            lamp(p, s * 0.7, y, 1.0, 0.14, 0.12)
        p.box("cloth_red", (s * 0.75, 4.92, 1.15), (0.2, 0.06, 0.2))                                      # tail lights
        p.box("orange_cat", (s * 0.75, 4.92, 1.45), (0.2, 0.06, 0.12))
        vehicles.arch(p, "black", s * 1.21, -3.4, 0.5, 0.6, lo=20)
        vehicles.arch(p, "black", s * 1.21, 2.8, 0.5, 0.6, lo=20)
        truck_wheel(p, "metal_galv", s * 1.05, -3.4, 0.5, 0.3, dual=False)
        truck_wheel(p, "metal_galv", s * 1.05, 2.8, 0.5, 0.3, dual=True)
        for z in (3.1,):
            p.box("cloth_red", (s * 0.95, -3.7, z), (0.2, 0.06, 0.16))                                   # roof flashers, front and rear
            p.box("orange_cat", (s * 0.6, -3.7, z), (0.16, 0.06, 0.14))
            p.box("cloth_red", (s * 0.95, 4.75, z), (0.2, 0.06, 0.16))
            p.box("orange_cat", (s * 0.6, 4.75, z), (0.16, 0.06, 0.14))
    p.box("black", (0, -3.74, 2.85), (2.0, 0.05, 0.25))                                                  # destination board, above the windscreen
    p.box("black", (0, 4.74, 2.85), (2.0, 0.05, 0.25))
    p.box("black", (0, -5.3, 0.6), (2.5, 0.3, 0.35))                                                     # bumpers
    p.box("black", (0, 5.0, 0.6), (2.5, 0.3, 0.35))
    p.box("black", (0, -5.26, 0.95), (1.1, 0.06, 0.6))                                                   # grille
    for z in (0.8, 0.95, 1.1):
        p.box("metal_galv", (0, -5.3, z), (1.08, 0.03, 0.04))
    p.box("paint_white", (0, 5.17, 0.6), (0.5, 0.04, 0.15))                                              # plate, on the bumper
    p.box("black", (-1.19, -2.35, 1.55), (0.1, 0.8, 1.5))                                                # the folding door, on the right (-X), behind the front wheel
    p.box("glass", (-1.23, -2.35, 1.75), (0.03, 0.7, 1.1))
    rod(p, "black", (1.1, -2.3, 1.95), (1.5, -2.45, 1.95), 0.06)                                         # the stop arm, folded out on the left (+X)
    p.cyl("cloth_red", (1.55, -2.45, 1.95), 0.28, 0.04, n=8, axis="y")
    p.box("black", (0, 4.92, 1.5), (0.9, 0.04, 1.3))                                                     # rear emergency door
    p.box("glass", (0, 4.94, 2.0), (0.7, 0.03, 0.5))
    p.box("metal_galv", (0, 4.95, 1.4), (0.5, 0.04, 0.05))
    for y in (-0.6, 2.2):
        p.box("metal_galv", (0, y, 3.14), (0.7, 0.9, 0.08))                                              # roof hatches
    return p


# ===== Fire truck ================================================================================================================
def fire_truck(body="cloth_red", name="GV_FireTruck_01"):
    """A pumper (9.6 m): a cab-forward lofted cab with a light bar and chrome bumper, a long body with roller-shutter compartments and handles, a pump panel,
    a ladder on top, a hose bed, outriggers, a rear step, reflective stripes and dual rear wheels."""
    p = Prop(name)
    p.box("black", (0, 0.2, 0.75), (1.4, 9.0, 0.3))                                                      # chassis
    vehicles.body_loft(p, body, [(-4.7, 1.05, 0.75, 1.9, 0.06), (-4.5, 1.2, 0.7, 2.0, 0.06), (-2.2, 1.22, 0.7, 2.05, 0.06)])   # the cab
    vehicles.glasshouse(p, "glass", [(-4.5, 1.12, 1.05, 2.0, 2.05), (-4.35, 1.12, 1.0, 2.0, 2.9), (-2.4, 1.12, 1.0, 2.0, 2.9), (-2.25, 1.12, 1.05, 2.0, 2.05)])
    p.box(body, (0, -3.5, 2.93), (2.3, 2.5, 0.1))                                                        # cab roof
    vehicles.body_loft(p, body, [(-2.2, 1.25, 0.7, 2.65, 0.04), (4.6, 1.25, 0.7, 2.65, 0.04)])           # the body
    p.box("black", (0, 1.2, 2.675), (2.2, 5.6, 0.06))                                                   # the hose bed's top, on the body
    for k in range(3):
        p.cyl("cloth_red", (0, 0.8 + k * 1.4, 2.88), 0.28, 1.0, n=10, axis="x")                          # hose coils
    p.box("black", (0, -3.0, 3.04), (1.6, 0.6, 0.12))                                                     # light bar base
    p.box("cloth_red", (-0.4, -3.0, 3.14), (0.6, 0.5, 0.14))
    p.box("paint_white", (0.4, -3.0, 3.14), (0.6, 0.5, 0.14))
    for s in (-1, 1):
        rod(p, "metal_dark", (s * 0.5, -2.6, 3.25), (s * 0.5, 4.5, 3.25), 0.1)                            # ladder rails, above the hose coils
        rod(p, "metal_dark", (s * 0.5, -2.6, 2.7), (s * 0.5, -2.6, 3.25), 0.1)                            # ladder supports
        rod(p, "metal_dark", (s * 0.5, 4.2, 2.7), (s * 0.5, 4.2, 3.25), 0.1)
        for y in (-0.7, 1.2, 3.1):                                                                       # roller-shutter compartments
            p.box("metal_galv", (s * 1.25, y, 1.6), (0.08, 1.5, 1.1))
            p.box("metal_dark", (s * 1.3, y, 1.6), (0.04, 1.4, 1.0))
            for z in (1.2, 1.4, 1.6, 1.8):
                p.box("metal_galv", (s * 1.33, y, z), (0.02, 1.3, 0.03))
            p.box("metal_galv", (s * 1.34, y + 0.55, 1.15), (0.04, 0.12, 0.05))                           # handles
        p.box("paint_white", (s * 1.26, 1.2, 0.95), (0.08, 7.0, 0.14))                                   # reflective stripe, 1 cm proud of the compartments
        p.box("paint_yellow", (s * 1.26, 1.2, 0.8), (0.08, 7.0, 0.05))
        p.box("black", (s * 0.9, 1.6, 0.45), (0.4, 1.0, 0.05))                                           # outrigger feet, ahead of the rear tyres
        rod(p, "metal_dark", (s * 0.7, 1.6, 0.75), (s * 0.9, 1.6, 0.45), 0.12)
        lamp(p, s * 0.8, -4.78, 1.1, 0.16, 0.14)
        p.box("cloth_red", (s * 1.0, 4.62, 1.5), (0.2, 0.06, 0.3))                                       # tail lights
        p.box("black", (s * 1.2, -3.4, 1.4), (0.04, 0.03, 0.9))                                         # cab door seams
        p.box("metal_galv", (s * 1.22, -3.0, 1.6), (0.05, 0.2, 0.05))
        p.box("black", (s * 1.35, -2.55, 0.85), (0.4, 0.6, 0.06))                                        # cab steps, behind the front wheel
        vehicles.mirror(p, "black", s, 1.0, -4.4, 2.4)
        vehicles.arch(p, "black", s * 1.2, -3.4, 0.5, 0.62, lo=20)
        vehicles.arch(p, "black", s * 1.2, 3.1, 0.5, 0.62, lo=20)
        truck_wheel(p, "metal_galv", s * 1.05, -3.4, 0.5, 0.3, dual=False)
        truck_wheel(p, "metal_galv", s * 1.05, 3.1, 0.5, 0.3, dual=True)
    p.box("metal_galv", (0, -4.8, 0.75), (2.5, 0.3, 0.4))                                               # bumper
    p.box("black", (0, -4.72, 1.2), (1.2, 0.05, 0.6))                                                    # grille
    p.box("metal_galv", (0, 4.7, 0.72), (2.4, 0.25, 0.3))                                               # rear step
    p.box("black", (0, 4.62, 1.9), (1.8, 0.05, 1.4))                                                      # rear roller door
    for y in [-2.2 + k * 0.5 for k in range(14)]:
        rod(p, "metal_galv", (-0.5, y, 3.25), (0.5, y, 3.25), 0.05)                                    # ladder rungs
    p.box("cloth_red", (0, -4.6, 3.05), (0.3, 0.3, 0.2))                                                  # siren
    return p
