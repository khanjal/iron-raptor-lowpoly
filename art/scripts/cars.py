"""Cars, vans and light vehicles in many paint jobs and conditions (asset list GV-01..GV-22): flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/cars.py", run_name="__main__")
Optional globals: CAR_LIST (family names such as "Sedan", "Pickup") and CONDITIONS (default New and Damaged). Exports
Assets/Art/Global/Vehicles/<Family>/GV_<Family>_<Variant>_01.fbx.

One parametric body builder (box_car) makes a sedan, wagon, SUV, minivan, van or taxi from its dimensions, and a table lists the
variants: paint colours for civilians, the sheriff and state police cruisers, the FBI SUV, the Man in Black sedan, an ambulance, a tow truck,
an ATV and a motorcycle. Every family can also be built Damaged: rusted and faded paint, smashed glass, lights and mirrors gone,
tilted, grimy; and the farm pickup and tractor from vehicles.py get the same set of paint jobs. All face -Y, wheels on the ground,
origin at the centre of the footprint.
"""

import importlib
import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Blender is shared by several sessions, each running scripts from its own checkout: drop modules another checkout imported first (as vehicles.py does)
for _n in ("common", "props_lib", "emitters", "ship_hulls", "vehicles", "other_vehicles"):
    _m = sys.modules.get(_n)
    if _m is not None and Path(getattr(_m, "__file__", "") or "").resolve().parent != _HERE:
        sys.modules.pop(_n, None)
import common
import props_lib
import vehicles
import other_vehicles
for _m in (common, props_lib, vehicles, other_vehicles):
    importlib.reload(_m)
Prop = props_lib.Prop
wheel = props_lib.wheel
V = vehicles.V

NAMES = {"truck_blue": "Blue", "cloth_red": "Red", "paint_white": "White", "tractor_green": "Green", "paint_yellow": "Yellow",
         "black": "Black", "tan": "Tan", "fabric_grey": "Grey", "rust_dark": "Brown", "navy": "Navy", "orange_cat": "Orange",
         "golden": "Gold", "cream": "Cream", "alien_violet": "Purple", "fabric_green": "Sage"}

WRECK = {   # the Damaged colour remap: paint faded, rusted, lights and glass gone dark
    "truck_blue": "rust", "cloth_red": "rust_dark", "paint_white": "concrete", "tractor_green": "dead_wood", "paint_yellow": "wood_grey",
    "tan": "wood_grey", "navy": "fabric_grey", "fabric_grey": "dead_wood", "orange_cat": "rust", "golden": "wood_grey", "cream": "wood_grey",
    "metal_galv": "rust", "glass": "screen", "clear_glass": "screen", "black": "rust_dark", "fabric_green": "dead_wood", "alien_violet": "fabric_grey",
}

KINDS = {   # length, width, hood, cabin, body height, cabin height, wheel radius, windscreen run, rear window run, solid (no glass behind the front doors)
    "sedan": {"L": 4.6, "W": 1.8, "hood": 1.35, "cabin": 1.9, "bh": 0.55, "ch": 0.5, "wr": 0.33, "rf": 0.5, "rr": 0.45},
    "wagon": {"L": 4.8, "W": 1.85, "hood": 1.3, "cabin": 3.0, "bh": 0.55, "ch": 0.58, "wr": 0.33, "rf": 0.5, "rr": 0.2},
    "suv": {"L": 4.7, "W": 1.95, "hood": 1.25, "cabin": 3.0, "bh": 0.72, "ch": 0.62, "wr": 0.4, "rf": 0.45, "rr": 0.2},
    "minivan": {"L": 5.0, "W": 1.9, "hood": 1.0, "cabin": 3.6, "bh": 0.62, "ch": 0.78, "wr": 0.34, "rf": 0.7, "rr": 0.15},
    "van": {"L": 5.4, "W": 2.0, "hood": 0.7, "cabin": 4.8, "bh": 0.8, "ch": 1.3, "wr": 0.36, "rf": 0.3, "rr": 0.0, "solid": True, "tail": 0.1},
}


def box_car(name, kind, body, trim="metal_galv", glass="clear_glass", stripe=None, extras=()):
    """A road car from its dimensions (#344): a lofted body shell with a low nose, a rising hood and a tail; a glasshouse with a slanted
    windscreen, side windows that lean in and a rear window, carried on A, B and C pillars under a roof panel; sills, mirrors, wheel arches and
    detailed wheels, a grille with bars, headlight and tail light housings, bumpers, a plate, an exhaust.

    It opens: the cabin is hollow (a floor, seats, a dashboard) and every door is a part with its window, handle and mirror, hinged at its front
    edge (Door_FL, Door_FR, Door_RL, Door_RR; L is +X, the model faces -Y); the hood is a part hinged at the cowl (Hood), over an engine; a sedan's boot
    lid (Trunk) lifts off a spare wheel; a wagon, SUV or minivan has a tailgate (Tailgate) hinged at the roof with the rear window in it; a van has two
    rear doors (RearDoor_L, RearDoor_R) on an empty cargo bay. The wheels spin (vehicles.name_wheels)."""
    k = KINDS[kind]
    L, W, hood, cab, bh, ch, wr = k["L"], k["W"], k["hood"], k["cabin"], k["bh"], k["ch"], k["wr"]
    rf, rr, solid = k["rf"], k["rr"], k.get("solid", False)
    p = Prop(name)
    base = 0.3
    ytop = base + bh                                              # top of the lower body
    hw = W / 2
    y_front, y_rear = -L / 2, L / 2
    y_c0 = y_front + hood                                         # the cabin starts here
    y_c1 = min(y_c0 + cab, y_rear - k.get("tail", 0.3))
    cab_mid = (y_c0 + y_c1) / 2
    cab_len = y_c1 - y_c0
    boot = y_c1 < y_rear - 0.35                                   # a sedan's boot lid
    z_f = base + 0.11                                             # the cabin floor
    zmid = (z_f + ytop) / 2                                       # half way up a door
    drop = 0.17                                                   # how deep a lid is: the hood, boot lid or tailgate is the top `drop` of the shell
    p.box("black", (0, 0, base - 0.05), (W - 0.3, L - 0.5, 0.15))                       # underbody

    # the body shell, lofted: a low nose, a hood that rises to the cowl, [the cabin is hollow], a tail
    S0 = (y_front, hw * 0.93, base + 0.1, ytop - 0.14, 0.06)
    S1 = (y_front + 0.22, hw * 0.99, base + 0.04, ytop - 0.05, 0.07)
    S2 = (y_front + hood * 0.6, hw, base + 0.02, ytop - 0.01, 0.07)
    S3 = (y_c0, hw, base + 0.02, ytop + 0.02, 0.07)
    S4 = (y_c1, hw, base + 0.02, ytop + (0.03 if boot else 0.0), 0.07)
    S5 = (y_rear - 0.3, hw, base + 0.02, ytop + 0.04, 0.07)
    S6 = (y_rear - 0.08, hw * 0.99, base + 0.06, ytop - 0.02, 0.06)
    S7 = (y_rear, hw * 0.94, base + 0.1, ytop - 0.1, 0.05)
    vehicles.body_loft(p, body, [S0, S1])                                                # the nose, which stays when the hood goes up
    vehicles.low_loft(p, body, [S1, S2, S3], drop)                                        # the engine bay, under the hood
    with p.part("Hood", pivot=(0, y_c0, ytop - drop), kind="hinge", axis="x", limit=-60.0):
        vehicles.lid_loft(p, body, [S1, S2, S3], drop)
    p.box("metal_dark", (0, y_c0 - 0.45, ytop - 0.17), (0.5, 0.5, 0.18))                 # engine, battery, air filter and radiator: inside the hood while it is shut
    p.box("black", (-0.45, y_front + 0.75, ytop - 0.2), (0.22, 0.14, 0.18))
    p.cyl("metal_galv", (0.4, y_front + 0.8, ytop - 0.17), 0.1, 0.14, n=8)
    p.box("black", (0, y_front + 0.32, ytop - 0.17), (W - 0.9, 0.08, 0.2))
    lid_st = [S4, S5] if boot else [S4, S6]
    if not solid:                                                                         # a van's tail is its two rear doors
        vehicles.body_loft(p, body, [S5, S6, S7] if boot else [S6, S7])                   # the tail, which stays
        vehicles.low_loft(p, body, lid_st, drop)                                          # the floor of the boot or the luggage bay
    # the glasshouse: windscreen run rf, rear window run rr, sides leaning in; the side windows are in the doors
    hb, ht = hw - 0.12, hw - 0.25
    zt = ytop + ch - 0.03
    s1, s2 = y_c0 + rf, y_c1 - rr
    dl = min(1.0, (cab_len - 0.3) / 2)                            # a door's length
    y0f = y_c0 + 0.12                                             # the front door's front edge
    y_b = y0f + dl                                                # the B pillar, at the seam between the doors
    y_rd = y_b + dl                                               # the back edge of the rear door
    ends = lambda y: (y, hb, hb - 0.02, ytop, ytop + 0.02)
    lean_a = math.degrees(math.atan2(hb - ht, zt - ytop))        # how far the glasshouse sides lean in
    cos_a, sin_a = math.cos(math.radians(lean_a)), math.sin(math.radians(lean_a))

    def lean(colour, sx, ya, yb, z0, z1, thick, outset=0.0):
        """A panel on the leaning side of the glasshouse from y ya to yb and height z0 to z1 (outset is how far it stands off the surface)."""
        zc = (z0 + z1) / 2
        xc = hb + (ht - hb) * (zc - ytop) / (zt - ytop) + outset * cos_a
        p.box(colour, (sx * xc, (ya + yb) / 2, zc + outset * sin_a), (thick, yb - ya, (z1 - z0) / cos_a), rot=(0, -sx * lean_a, 0))

    vehicles.glasshouse(p, glass, [ends(y_c0), (s1, hb, ht, ytop, zt)])                  # the windscreen, with the little triangle of glass at each side
    if solid:
        y_k = y_b + 0.04                                          # the cab ends at the back edge of the B pillar
        y_i1 = y_k - 0.1
        y_floor = y_k
    else:
        y_i1 = y_c1 - 0.1
        y_floor = y_c1
        wedge = [(s2, hb, ht, ytop, zt), ends(y_c1)]
        if kind == "sedan":
            vehicles.glasshouse(p, glass, wedge)                  # the rear window
            with p.part("Trunk", pivot=(0, y_c1, ytop - 0.14), kind="hinge", axis="x", limit=60.0):
                vehicles.lid_loft(p, body, lid_st, drop)
            p.cyl("rubber", (0, (y_c1 + y_rear - 0.3) / 2, ytop - 0.1), 0.3, 0.1, n=10)       # the spare wheel and its hub: inside the lid while it is shut
            p.cyl("metal_galv", (0, (y_c1 + y_rear - 0.3) / 2, ytop - 0.04), 0.1, 0.04, n=6)
        else:                                                     # the tailgate: the rear window and the deck behind it, hinged along the roof
            with p.part("Tailgate", pivot=(0, s2, zt), kind="hinge", axis="x", limit=70.0):
                vehicles.glasshouse(p, glass, wedge)
                vehicles.lid_loft(p, body, lid_st, drop)
    vehicles.cab_interior(p, y_c0 + 0.05, y_i1, ytop, 2 * hb - 0.1, ch - 0.1, floor=z_f, rows=[0.9] + ([1.6] if (y_i1 - y_c0) > 2.0 and not solid else []))   # dashboard, wheel and seats
    p.box("black", (0, (y_c0 + y_floor) / 2, z_f - 0.04), (2 * (hw - 0.08), y_floor - y_c0, 0.1))               # the floor
    p.box(body, (0, (s1 + s2) / 2, zt + 0.025), (2 * ht + 0.06, s2 - s1 + 0.06, 0.07))                          # roof panel
    z_roof = zt + 0.06
    for sx in (-1, 1):
        props_lib.rod(p, body, (sx * hb, y_c0, ytop + 0.02), (sx * ht, s1, zt), 0.08)                           # A pillars
        props_lib.rod(p, body, (sx * hb, y_b, ytop), (sx * ht, y_b, zt), 0.07)                                  # B pillars
        if not solid:
            props_lib.rod(p, body, (sx * ht, s2, zt), (sx * hb, y_c1, ytop + 0.02), 0.11)                        # C pillars
            if cab_len > 3.2:
                props_lib.rod(p, body, (sx * hb, y_rd, ytop), (sx * ht, y_rd, zt), 0.07)                         # a third pair on a long cabin
            if kind in ("suv", "wagon"):
                p.box("black", (sx * (ht - 0.04), (s1 + s2) / 2, z_roof + 0.015), (0.04, s2 - s1 - 0.3, 0.04))        # roof rails
        # the body round the doors: rocker panels, the panel in front of the first door, the posts they shut against, the panel behind the last door
        p.sbox(body, (sx * (hw - 0.045), (y_c0 + y_floor) / 2, (base + 0.02 + z_f) / 2), (0.09, y_floor - y_c0, z_f - base - 0.02))
        p.sbox(body, (sx * (hw - 0.045), (y_c0 + y0f - 0.006) / 2, (base + 0.02 + ytop) / 2), (0.09, y0f - 0.006 - y_c0, ytop - base - 0.02))
        for y in (y_c0 + 0.07, y_b):
            p.sbox("black", (sx * (hw - 0.14), y, zmid), (0.1, 0.08, ytop - z_f))
        if not solid:
            p.sbox("black", (sx * (hw - 0.14), min(y_rd, y_c1 - 0.05), zmid), (0.1, 0.08, ytop - z_f))
            if y_c1 - y_rd > 0.03:
                p.sbox(body, (sx * (hw - 0.045), (y_rd + 0.006 + y_c1) / 2, (base + 0.02 + ytop) / 2), (0.09, y_c1 - y_rd - 0.006, ytop - base - 0.02))
                if s2 - (y_rd + 0.02) > 0.15:
                    lean(glass, sx, y_rd + 0.02, s2, ytop + 0.005, zt - 0.01, 0.03)           # the quarter window
        p.box("black", (sx * (hw - 0.01), 0, base + 0.07), (0.06, L - 1.9 - 2 * wr - 0.24, 0.07))               # sills
        # the doors, each a part: panel, card, window, handle (the front ones carry the mirror)
        side = "L" if sx > 0 else "R"
        doors = [(f"Door_F{side}", y0f + 0.006, y_b - 0.006, True)] + ([] if solid else [(f"Door_R{side}", y_b + 0.006, y_rd - 0.006, False)])
        for role, ya, yb, front in doors:
            with p.part(role, pivot=(sx * (hw - 0.02), ya, zmid), kind="hinge", axis="z", limit=-70.0 * sx):
                p.box(body, (sx * (hw - 0.045), (ya + yb) / 2, zmid), (0.09, yb - ya, ytop - z_f))
                p.box("black", (sx * (hw - 0.098), (ya + yb) / 2, zmid + 0.02), (0.016, yb - ya - 0.08, ytop - z_f - 0.1))     # the door card
                wa = max(ya + 0.04, s1) if front else ya + 0.04
                wb = yb - 0.035 if front or solid else min(yb - 0.04, s2)
                if wb - wa > 0.1:
                    lean(glass, sx, wa, wb, ytop + 0.005, zt - 0.01, 0.03)
                p.box(trim, (sx * (hw + 0.005), yb - 0.15, ytop - 0.17), (0.04, 0.14, 0.035))                 # handle
                if front:
                    vehicles.mirror(p, body, sx, hw - 0.12, y_c0 + 0.1, ytop + 0.03)
        # lights: bezel and lens at the front, housing and lens at the back, indicators, fog lights
        p.box(trim, (sx * (hw - 0.3), y_front - 0.012, ytop - 0.24), (0.34, 0.06, 0.17))
        p.box("paint_yellow", (sx * (hw - 0.3), y_front - 0.025, ytop - 0.24), (0.28, 0.08, 0.12))
        p.box("orange_cat", (sx * (hw - 0.06), y_front + 0.01, ytop - 0.34), (0.1, 0.06, 0.07))
        if not solid:
            p.box("black", (sx * (hw - 0.3), y_rear + 0.006, ytop - 0.2), (0.38, 0.05, 0.16))
            p.box("cloth_red", (sx * (hw - 0.3), y_rear + 0.015, ytop - 0.2), (0.34, 0.07, 0.12))
            p.box("paint_white", (sx * (hw - 0.62), y_rear + 0.015, ytop - 0.2), (0.1, 0.07, 0.1))              # reversing lights
        p.box("paint_yellow", (sx * (hw - 0.22), y_front - 0.02, base + 0.27), (0.1, 0.04, 0.07))               # fog lights
        # bumper ends that wrap the corners
        p.box(trim, (sx * (hw - 0.04), y_front - 0.02, base + 0.14), (0.1, 0.26, 0.18))
        p.box(trim, (sx * (hw - 0.04), y_rear + 0.02, base + 0.14), (0.1, 0.26, 0.18))
        for yy in (y_front + 0.95, y_rear - 0.95):
            vehicles.car_wheel(p, trim, sx * (hw - 0.1), yy, wr, 0.24, n=12)
            vehicles.arch(p, "black", sx * (hw + 0.005), yy, wr, wr + 0.1)
    if solid:
        # a van: the cargo bay is a box of two walls, a floor, the cab's bulkhead and the roof, shut at the back by two doors that swing wide
        for sx in (-1, 1):
            p.box(body, (sx * (hw - 0.045), (y_b + y_c1) / 2, (base + 0.02 + ytop) / 2), (0.09, y_c1 - y_b, ytop - base - 0.02))
            lean(body, sx, y_b, y_c1, ytop, zt, 0.06)
        p.box("metal_dark", (0, (y_b + y_rear) / 2, z_f - 0.04), (2 * (hw - 0.09), y_rear - y_b, 0.1))               # the cargo floor, out to the bumper
        p.box(body, (0, y_rear - 0.05, (base + 0.02 + base + 0.23) / 2), (2 * hw - 0.04, 0.1, 0.21))               # the panel under the doors
        xa, xt = hw - 0.09, ht - 0.01
        p.loft_rings("black", [[V(-xa, y, z_f), V(xa, y, z_f), V(xa, y, ytop), V(xt, y, zt), V(-xt, y, zt), V(-xa, y, ytop)] for y in (y_k, y_k + 0.06)])
        xo = hw - 0.02
        for sx in (-1, 1):
            side = "L" if sx > 0 else "R"
            with p.part(f"RearDoor_{side}", pivot=(sx * xo, y_rear, (base + 0.23 + zt) / 2), kind="hinge", axis="z", limit=-100.0 * sx):
                p.loft_rings(body, [[V(sx * 0.006, y, base + 0.23), V(sx * xo, y, base + 0.23), V(sx * xo, y, ytop), V(sx * (ht + 0.01), y, zt), V(sx * 0.006, y, zt)]
                                    for y in (y_c1, y_rear)])
                p.box(glass, (sx * 0.4, y_rear + 0.006, ytop + ch * 0.62), (0.58, 0.03, 0.42))
                p.box(trim, (sx * 0.08, y_rear + 0.012, ytop + ch * 0.35), (0.04, 0.03, 0.12))
                p.box("black", (sx * (hw - 0.3), y_rear + 0.006, ytop - 0.2), (0.38, 0.05, 0.16))               # tail lights, on the door
                p.box("cloth_red", (sx * (hw - 0.3), y_rear + 0.015, ytop - 0.2), (0.34, 0.07, 0.12))
                p.box("paint_white", (sx * (hw - 0.62), y_rear + 0.015, ytop - 0.2), (0.1, 0.07, 0.1))
                if sx > 0:
                    p.box("paint_white", (0, y_rear + 0.01, base + 0.31), (0.4, 0.04, 0.15))                    # plate
                    p.box("black", (0, y_rear + 0.006, ytop + ch * 0.5), (0.025, 0.03, ch * 0.92))              # the seam between the doors
    p.box(trim, (0, y_front - 0.05, base + 0.14), (W * 0.98, 0.16, 0.18))                                      # bumpers
    p.box(trim, (0, y_rear + 0.05, base + 0.14), (W * 0.98, 0.16, 0.18))
    p.box("black", (0, y_front - 0.03, base + 0.04), (W * 0.8, 0.12, 0.1))                                     # valances
    p.box("black", (0, y_rear + 0.03, base + 0.04), (W * 0.8, 0.12, 0.1))
    p.box("black", (0, y_front - 0.012, ytop - 0.25), (W - 1.0, 0.04, 0.2))                                    # grille
    for z in (ytop - 0.31, ytop - 0.25, ytop - 0.19):
        p.box(trim, (0, y_front - 0.035, z), (W - 1.04, 0.02, 0.025))                                          # its bars
    if not solid:
        p.box("paint_white", (0, y_rear + 0.01, base + 0.31), (0.4, 0.04, 0.15))                               # plate, above the bumper
    p.cyl("metal_dark", (hw * 0.55, y_rear + 0.08, base + 0.05), 0.04, 0.2, n=6, axis="y")                     # exhaust
    if stripe:
        p.box(stripe, (0, 0, ytop - 0.2), (W + 0.02, L - 0.4, 0.16))
    for e in extras:
        if e == "lightbar":
            p.box("cloth_red", (-0.25, cab_mid, z_roof + 0.04), (0.45, 0.22, 0.1)); p.box("truck_blue", (0.25, cab_mid, z_roof + 0.04), (0.45, 0.22, 0.1))
        elif e == "taxi":
            p.box("paint_yellow", (0, cab_mid, z_roof + 0.07), (0.7, 0.22, 0.16)); p.box("glow_cyan", (0, cab_mid - 0.12, z_roof + 0.07), (0.5, 0.01, 0.1))
        elif e == "antenna":
            p.cyl("black", (0.5, y_c1 - 0.2, z_roof + 0.35), 0.008, 0.7, n=4)
            p.cyl("black", (-0.5, y_c1 - 0.2, z_roof + 0.25), 0.008, 0.5, n=4)
        elif e == "cross":                                                                                  # a red cross on each side of the cargo bay
            zc, cy = ytop + ch * 0.45, (y_b + y_c1) / 2
            for sx in (-1, 1):
                lean("cloth_red", sx, cy - 0.45, cy + 0.45, zc - 0.11, zc + 0.11, 0.04, outset=0.02)
                lean("cloth_red", sx, cy - 0.11, cy + 0.11, zc - 0.45, zc + 0.45, 0.04, outset=0.02)
        elif e == "roofrack":
            p.box("black", (0, cab_mid, z_roof + 0.1), (W - 0.5, y_c1 - y_c0 - 0.3, 0.06))
            for sy in (-0.7, 0.7):
                p.box("black", (0, cab_mid + sy, z_roof + 0.06), (W - 0.5, 0.05, 0.1))
        elif e == "deliverysign":                                                                           # a panel on each side of the cargo bay
            for sx in (-1, 1):
                lean("fabric_brown" if body != "fabric_brown" else "paint_white", sx, cab_mid + 0.2 - 0.9, cab_mid + 0.2 + 0.9, zt - 0.8, zt - 0.2, 0.04, outset=0.02)
    return p


def tow_truck(body="paint_yellow", name="GV_TowTruck_01"):
    p = vehicles.pickup(body=body, name=name, gate=False)                                            # the deck over the bed would be in the way of a dropping gate
    p.box("black", (0, 2.0, 0.95), (1.9, 2.2, 0.1))
    props_lib.rod(p, "metal_dark", (0, 2.0, 1.0), (0, 2.1, 2.4), 0.22)                               # the mast, up from the bed
    props_lib.rod(p, "metal_dark", (0, 2.1, 2.4), (0, 3.3, 1.7), 0.16)                               # the boom, out over the tail
    p.cyl("metal_galv", (0, 3.3, 1.45), 0.03, 0.5, n=4)                                               # the cable
    p.box("black", (0, 3.3, 1.15), (0.14, 0.14, 0.12))                                                # the hook block
    p.box("cloth_red", (0, 0.0, 1.73), (0.5, 0.2, 0.1)); p.box("paint_yellow", (0, 0.0, 1.83), (0.5, 0.2, 0.1))              # the beacon, on the cab roof
    p.cyl("metal_galv", (0, 0.5, 1.0), 0.08, 0.3, n=6)
    p.box("black", (0, 3.0, 0.5), (0.1, 1.2, 0.25))
    return p


# family -> list of (variant name, builder, kwargs)
def families():
    f = {}
    f["Pickup"] = [(NAMES[c], "pickup", {"body": c}) for c in ("truck_blue", "cloth_red", "paint_white", "tractor_green", "tan", "black")]
    f["Tractor"] = [(n, "tractor", {"body": c}) for n, c in (("Green", "tractor_green"), ("Red", "cloth_red"), ("Orange", "orange_cat"), ("Blue", "truck_blue"), ("Yellow", "paint_yellow"))]
    f["Sedan"] = [(NAMES[c], "sedan", {"body": c}) for c in ("truck_blue", "cloth_red", "paint_white", "tan", "fabric_grey", "tractor_green", "black")]
    f["Wagon"] = [(NAMES[c], "wagon", {"body": c}) for c in ("fabric_green", "paint_white", "tan", "truck_blue")]
    f["SUV"] = [(NAMES[c], "suv", {"body": c}) for c in ("black", "paint_white", "fabric_grey", "cloth_red", "navy")]
    f["Minivan"] = [(NAMES[c], "minivan", {"body": c}) for c in ("truck_blue", "paint_white", "cloth_red", "fabric_grey")]
    f["Van"] = [(n, "van", {"body": c, "extras": ex}) for n, c, ex in (("White", "paint_white", ()), ("Brown", "fabric_brown", ("deliverysign",)), ("Blue", "truck_blue", ()), ("Mail", "paint_white", ("deliverysign",)))]
    f["Taxi"] = [("Yellow", "sedan", {"body": "paint_yellow", "extras": ("taxi",)}), ("Checker", "sedan", {"body": "paint_yellow", "stripe": "black", "extras": ("taxi",)})]
    f["Police"] = [
        ("Sheriff", "sedan", {"body": "paint_white", "stripe": "tan_uniform", "extras": ("lightbar",)}),
        ("Deputy", "suv", {"body": "paint_white", "stripe": "tan_uniform", "extras": ("lightbar",)}),
        ("StatePolice", "sedan", {"body": "navy", "stripe": "paint_white", "extras": ("lightbar",)}),
        ("FBI_SUV", "suv", {"body": "black", "glass": "black", "extras": ("antenna",)}),
        ("FBI_Van", "van", {"body": "black", "glass": "black", "trim": "black", "extras": ("antenna", "roofrack")}),   # the FBI's van (#19): black, dark glass, an antenna and a rack on the roof
        ("MIB_Sedan", "sedan", {"body": "black", "glass": "black", "trim": "black"}),
    ]
    f["Ambulance"] = [("White", "van", {"body": "paint_white", "stripe": "cloth_red", "extras": ("cross", "lightbar")})]
    f["TowTruck"] = [("Yellow", "special", {"fn": "tow"})]
    f["ATV"] = [(n, "special", {"fn": "atv", "body": c}) for n, c in (("Red", "cloth_red"), ("Green", "tractor_green"), ("Yellow", "paint_yellow"))]
    f["Motorcycle"] = [(n, "special", {"fn": "moto", "body": c}) for n, c in (("Red", "cloth_red"), ("Black", "black"), ("Blue", "truck_blue"))]
    f["Jeep"] = [(n, "special", {"fn": "jeep", "body": c}) for n, c in (("Olive", "tractor_green"), ("Tan", "tan"))]
    f["Trailer"] = [("Flatbed", "special", {"fn": "flatbed"})]
    f["Semi"] = [(n, "special", {"fn": "semi", "body": c}) for n, c in (("Red", "cloth_red"), ("Blue", "truck_blue"), ("White", "paint_white"), ("Black", "black"))]
    f["SemiTrailer"] = [("Box_White", "special", {"fn": "boxtrailer", "body": "paint_white"}), ("Box_Blue", "special", {"fn": "boxtrailer", "body": "truck_blue"}),
                        ("Tanker_Silver", "special", {"fn": "tanker"})]
    f["Bus"] = [("School", "special", {"fn": "bus"})]
    f["FireTruck"] = [("Red", "special", {"fn": "fire"})]
    return f


def build(family, label, kind, kw, condition):
    name = f"GV_{family}_{label}_01"
    if kind == "special":
        kw = dict(kw)
        which = kw.pop("fn")
        p = {"tow": tow_truck, "atv": other_vehicles.atv, "moto": other_vehicles.motorcycle, "jeep": other_vehicles.jeep, "flatbed": other_vehicles.trailer_flatbed,
             "semi": other_vehicles.semi_tractor, "boxtrailer": other_vehicles.box_trailer, "tanker": other_vehicles.tanker_trailer,
             "bus": other_vehicles.school_bus, "fire": other_vehicles.fire_truck}[which](name=name, **kw)
    elif kind == "pickup":
        p = vehicles.pickup(name=name, **kw)
    elif kind == "tractor":
        p = vehicles.tractor(name=name, **kw)
    else:
        p = box_car(name, kind, **kw)
    vehicles.name_wheels(p)
    return p


OTHER_FAMILIES = {"ATV", "Motorcycle", "Jeep", "Trailer", "Semi", "SemiTrailer", "Bus", "FireTruck"}   # the families of #357: only these get the length-scaled tilt and prune_floating, so a rebuild leaves the Damaged cars of #344 as exported


def prune_floating(prop, margin=0.01):
    """After Prop.damage() has dropped small parts at random, drop what is left with nothing to touch (a mirror head whose arm went, a lens whose bezel went,
    a handlebar whose clamp went). Two parts touch when their surfaces overlap or come within `margin` metres; whatever is not connected to the biggest
    group of parts is removed (the same test as the contact check the art PRs report). Returns how many parts went."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    isl = []
    pieces = list(prop.parts.items()) + [("__part__", bm) for g in prop.groups.values() for bm in g["parts"].values()]      # a wheel or a door is something to touch, and is never dropped
    for colour, bm in pieces:
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()                                   # the grime boxes damage() added since its own index_update() have index -1
        seen = set()
        for v in bm.verts:
            if v.index in seen:
                continue
            stack, vs = [v], []
            seen.add(v.index)
            while stack:
                a = stack.pop()
                vs.append(a)
                for e in a.link_edges:
                    o = e.other_vert(a)
                    if o.index not in seen:
                        seen.add(o.index)
                        stack.append(o)
            local = {a.index: k for k, a in enumerate(vs)}
            faces = {f for a in vs for f in a.link_faces}
            tree = BVHTree.FromPolygons([a.co.copy() for a in vs], [tuple(local[x.index] for x in f.verts) for f in faces], epsilon=0.0) if faces else None
            lo = [min(a.co[i] for a in vs) for i in range(3)]
            hi = [max(a.co[i] for a in vs) for i in range(3)]
            isl.append((bm, vs, lo, hi, tree, colour))
    n = len(isl)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def touch(i, j):
        _, vi, _, _, ti, _ = isl[i]
        _, vj, _, _, tj, _ = isl[j]
        if ti is None or tj is None:
            return False
        if ti.overlap(tj):
            return True
        for va, tb in ((vi, tj), (vj, ti)):
            for a in va[:64]:
                hit = tb.find_nearest(a.co)
                if hit[0] is not None and hit[3] <= margin:
                    return True
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if find(i) != find(j) and all(isl[i][2][k] <= isl[j][3][k] + margin and isl[j][2][k] <= isl[i][3][k] + margin for k in range(3)) and touch(i, j):
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    if len(groups) < 2:
        return 0
    main = max(groups.values(), key=lambda g: sum(len(isl[i][1]) for i in g))
    removed = 0
    for g in groups.values():
        if g is main or any(isl[i][5] in ("rubber", "__part__") for i in g):                 # a tyre is never dropped: it would take a wheel off the model
            continue
        for i in g:
            bmesh.ops.delete(isl[i][0], geom=isl[i][1], context="VERTS")
            removed += 1
    return removed


def ajar(prop):
    """A wrecked vehicle is left with some of its doors, hood and lids hanging open by different amounts (a wheel never moves: it spins)."""
    import random
    rng = random.Random(sum(ord(c) for c in prop.name) % 1000)
    for role, g in sorted(prop.groups.items()):
        # seeded modelling variation, not security
        if g["kind"] == "hinge" and rng.random() < 0.4:  # NOSONAR
            g["rest"] = round(g["limit"] * rng.uniform(0.12, 0.45), 1)


def run():
    only = globals().get("CAR_LIST")
    only_variants = globals().get("VARIANT_LIST")   # build only these variants of the families (their labels, e.g. "FBI_Van"): the rest of a family is left as it is
    conds = globals().get("CONDITIONS") or ["New", "Damaged"]
    count, x = 0, 0.0
    for family, variants in families().items():
        if only and family not in only:
            continue
        for label, kind, kw in variants:
            if only_variants and label not in only_variants:
                continue
            for cond in conds:
                props_lib.THEME = WRECK if cond == "Damaged" else {}
                try:
                    prop = build(family, label, kind, kw, cond)
                finally:
                    props_lib.THEME = {}
                if cond == "Damaged":
                    prop.name = prop.name.replace(f"_{label}_01", f"_{label}_Damaged_01")
                    tilt = 3.0
                    if family in OTHER_FAMILIES:                                                      # #357: the 3 degrees of a 4.6 m car lift one end of a 14 m trailer by 0.7 m; this keeps an end within about 8 cm
                        ys = [v.co.y for bm in prop.parts.values() for v in bm.verts]
                        tilt = min(3.0, math.degrees(0.08 / ((max(ys) - min(ys)) / 2)))
                    prop.damage(seed=sum(ord(c) for c in prop.name) % 1000, drop=0.35, tilt=tilt, grime=4, max_part=0.03, grime_scale=3.0)
                    if family in OTHER_FAMILIES:
                        prune_floating(prop)
                    ajar(prop)
                obj, coll = prop.finish()
                common.export_fbx(coll, f"Assets/Art/Global/Vehicles/{family}/{prop.name}.fbx")
                obj.location = (x, (0 if cond == "New" else 7), 0)
                count += 1
            x += 4.0
    props_lib.write_interactions()                                                    # the moving parts of every vehicle built (art/data/interactions.json)
    print("cars done", count)


if __name__ == "__main__":
    run()
