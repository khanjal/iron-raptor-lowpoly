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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
import vehicles
for _m in (common, props_lib, vehicles):
    importlib.reload(_m)
Prop = props_lib.Prop
wheel = props_lib.wheel

NAMES = {"truck_blue": "Blue", "cloth_red": "Red", "paint_white": "White", "tractor_green": "Green", "paint_yellow": "Yellow",
         "black": "Black", "tan": "Tan", "fabric_grey": "Grey", "rust_dark": "Brown", "navy": "Navy", "orange_cat": "Orange",
         "golden": "Gold", "cream": "Cream", "alien_violet": "Purple", "fabric_green": "Sage"}

WRECK = {   # the Damaged colour remap: paint faded, rusted, lights and glass gone dark
    "truck_blue": "rust", "cloth_red": "rust_dark", "paint_white": "concrete", "tractor_green": "dead_wood", "paint_yellow": "wood_grey",
    "tan": "wood_grey", "navy": "fabric_grey", "fabric_grey": "dead_wood", "orange_cat": "rust", "golden": "wood_grey", "cream": "wood_grey",
    "metal_galv": "rust", "glass": "screen", "black": "rust_dark", "fabric_green": "dead_wood", "alien_violet": "fabric_grey",
}

KINDS = {   # length, width, hood, cabin, body height, cabin height, wheel radius
    "sedan": dict(L=4.6, W=1.8, hood=1.35, cabin=1.9, bh=0.55, ch=0.5, wr=0.33),
    "wagon": dict(L=4.8, W=1.85, hood=1.3, cabin=3.0, bh=0.55, ch=0.58, wr=0.33),
    "suv": dict(L=4.7, W=1.95, hood=1.25, cabin=3.0, bh=0.72, ch=0.62, wr=0.4),
    "minivan": dict(L=5.0, W=1.9, hood=1.0, cabin=3.6, bh=0.62, ch=0.78, wr=0.34),
    "van": dict(L=5.4, W=2.0, hood=0.7, cabin=4.4, bh=0.8, ch=1.3, wr=0.36),
}


def box_car(name, kind, body, trim="metal_galv", glass="clear_glass", stripe=None, extras=()):
    k = KINDS[kind]
    L, W, hood, cab, bh, ch, wr = k["L"], k["W"], k["hood"], k["cabin"], k["bh"], k["ch"], k["wr"]
    p = Prop(name)
    base = 0.3
    ytop = base + bh                                              # top of the lower body
    y_front, y_rear = -L / 2, L / 2
    y_c0 = y_front + hood                                         # the cabin starts here
    y_c1 = min(y_c0 + cab, y_rear - 0.3)
    p.box("black", (0, 0, base - 0.05), (W - 0.3, L - 0.5, 0.15))                       # underbody
    p.box(body, (0, 0, base + bh / 2), (W, L - 0.2, bh))                                 # lower body
    p.box(body, (0, y_front + hood / 2 + 0.1, ytop + 0.03), (W - 0.1, hood, 0.07), rot=(-3, 0, 0))   # hood
    if y_c1 < y_rear - 0.35:                                                             # a sedan's boot lid
        p.box(body, (0, (y_c1 + y_rear) / 2 - 0.1, ytop + 0.04), (W - 0.1, y_rear - y_c1, 0.08))
    cab_mid = (y_c0 + y_c1) / 2
    vehicles.open_cabin(p, body, glass, W, y_c0, y_c1, ytop, ch, cargo=(kind == "van"))                  # roof, posts, glass, seats
    for sx in (-1, 1):
        p.box("black", (sx * (W / 2 + 0.01), cab_mid - (y_c1 - y_c0) * 0.17, ytop - 0.25), (0.03, 0.04, 0.03))   # door handles
        p.box("black", (sx * (W / 2 + 0.01), cab_mid + (y_c1 - y_c0) * 0.17, ytop - 0.25), (0.03, 0.04, 0.03))
        p.box(body, (sx * (W / 2 + 0.09), y_c0 + 0.1, ytop + 0.12), (0.12, 0.12, 0.08))                       # mirrors
        p.box("paint_yellow", (sx * (W / 2 - 0.35), y_front - 0.01, ytop - 0.14), (0.3, 0.05, 0.14))          # headlights
        p.box("cloth_red", (sx * (W / 2 - 0.3), y_rear + 0.0, ytop - 0.14), (0.26, 0.05, 0.14))               # tail lights
    p.box(trim, (0, y_front - 0.08, base + 0.12), (W + 0.02, 0.16, 0.2))                                       # bumpers
    p.box(trim, (0, y_rear + 0.06, base + 0.12), (W + 0.02, 0.16, 0.2))
    p.box("black", (0, y_front - 0.03, ytop - 0.18), (W - 0.9, 0.04, 0.2))                                     # grille
    p.box("paint_white", (0, y_rear + 0.02, ytop - 0.28), (0.4, 0.02, 0.15))                                  # plate
    if stripe:
        p.box(stripe, (0, 0, ytop - 0.12), (W + 0.02, L - 0.4, 0.16))
    for sx in (-1, 1):
        for yy in (y_front + 0.95, y_rear - 0.95):
            wheel(p, "rubber", trim, sx * (W / 2 - 0.1), yy, wr, wr, 0.24, n=10)
            p.box("black", (sx * (W / 2 + 0.0), yy, wr + 0.34), (0.08, wr * 2.3, 0.12))                     # wheel arch lips
    z_roof = ytop + ch
    for e in extras:
        if e == "lightbar":
            p.box("cloth_red", (-0.25, cab_mid, z_roof + 0.08), (0.45, 0.22, 0.1)); p.box("truck_blue", (0.25, cab_mid, z_roof + 0.08), (0.45, 0.22, 0.1))
        elif e == "taxi":
            p.box("paint_yellow", (0, cab_mid, z_roof + 0.1), (0.7, 0.22, 0.16)); p.box("glow_cyan", (0, cab_mid - 0.12, z_roof + 0.1), (0.5, 0.01, 0.1))
        elif e == "antenna":
            p.cyl("black", (0.5, y_c1 - 0.2, z_roof + 0.35), 0.008, 0.7, n=4)
            p.cyl("black", (-0.5, y_c1 - 0.2, z_roof + 0.25), 0.008, 0.5, n=4)
        elif e == "cross":
            p.box("cloth_red", (0, 0, ytop + ch * 0.45), (W + 0.03, 0.9, 0.22)); p.box("cloth_red", (0, 0, ytop + ch * 0.45), (W + 0.03, 0.22, 0.9))
        elif e == "roofrack":
            p.box("black", (0, cab_mid, z_roof + 0.1), (W - 0.5, y_c1 - y_c0 - 0.3, 0.06))
            for sy in (-0.7, 0.7):
                p.box("black", (0, cab_mid + sy, z_roof + 0.06), (W - 0.5, 0.05, 0.1))
        elif e == "deliverysign":
            p.box("fabric_brown" if body != "fabric_brown" else "paint_white", (0, cab_mid + 0.2, z_roof - 0.5), (W + 0.02, 1.8, 0.6))
    return p


def tow_truck(body="paint_yellow", name="GV_TowTruck_01"):
    p = vehicles.pickup(body=body, name=name)
    p.box("black", (0, 2.0, 0.95), (1.9, 2.2, 0.1))
    props_lib.rod(p, "metal_dark", (0, 2.0, 1.0), (0, 2.1, 2.4), 0.22)                               # the mast, up from the bed
    props_lib.rod(p, "metal_dark", (0, 2.1, 2.4), (0, 3.3, 1.7), 0.16)                               # the boom, out over the tail
    p.cyl("metal_galv", (0, 3.3, 1.45), 0.03, 0.5, n=4)                                               # the cable
    p.box("black", (0, 3.3, 1.15), (0.14, 0.14, 0.12))                                                # the hook block
    p.box("cloth_red", (0, 0.0, 1.73), (0.5, 0.2, 0.1)); p.box("paint_yellow", (0, 0.0, 1.83), (0.5, 0.2, 0.1))              # the beacon, on the cab roof
    p.cyl("metal_galv", (0, 0.5, 1.0), 0.08, 0.3, n=6)
    p.box("black", (0, 3.0, 0.5), (0.1, 1.2, 0.25))
    return p


def atv(body="cloth_red", name="GV_ATV_01"):
    p = Prop(name)
    p.box("black", (0, 0, 0.45), (0.5, 1.5, 0.2))
    p.box(body, (0, -0.4, 0.62), (0.7, 0.8, 0.28))                                                  # front fairing
    p.box(body, (0, 0.5, 0.58), (0.65, 0.7, 0.2))                                                    # rear fender
    p.box("black", (0, 0.1, 0.72), (0.34, 0.8, 0.14))                                                # seat
    for yy in (-0.62, 0.6):
        p.box("metal_dark", (0, yy, 0.3), (1.0, 0.08, 0.08))                                         # the axles, chassis to wheel hubs
    p.box("metal_dark", (0, -0.55, 0.98), (0.8, 0.06, 0.06)); p.box("metal_dark", (0, -0.4, 0.8), (0.05, 0.05, 0.4), rot=(-15, 0, 0))
    for sx in (-1, 1):
        for yy in (-0.62, 0.6):
            p.cyl("rubber", (sx * 0.5, yy, 0.3), 0.3, 0.22, n=8, axis="x")
            p.cyl("metal_galv", (sx * 0.5, yy, 0.3), 0.14, 0.24, n=6, axis="x")
    p.box("paint_yellow", (0.2, -0.82, 0.7), (0.16, 0.05, 0.1)); p.box("paint_yellow", (-0.2, -0.82, 0.7), (0.16, 0.05, 0.1))
    return p


def motorcycle(body="cloth_red", name="GV_Motorcycle_01"):
    p = Prop(name)
    p.cyl("rubber", (0, -0.7, 0.32), 0.32, 0.12, n=10, axis="x"); p.cyl("rubber", (0, 0.7, 0.32), 0.32, 0.14, n=10, axis="x")
    p.box("black", (0, 0.0, 0.5), (0.2, 1.2, 0.12))
    p.box(body, (0, -0.2, 0.69), (0.3, 0.5, 0.26), taper=0.9)                                        # tank, on the frame
    p.box("black", (0, 0.3, 0.63), (0.28, 0.6, 0.1))                                                  # seat, on the frame
    props_lib.rod(p, "metal_galv", (0, -0.72, 0.32), (0, -0.55, 0.98), 0.06)                          # forks: from the front axle to the bars
    p.box("black", (0, -0.55, 0.98), (0.7, 0.06, 0.06))                                               # bars
    p.cyl("metal_dark", (0.14, 0.45, 0.4), 0.05, 0.9, n=6, axis="y"); p.box("paint_yellow", (0, -0.78, 0.82), (0.14, 0.05, 0.12))
    return p


def jeep(body="tractor_green", name="GV_Jeep_01"):
    p = Prop(name)
    p.box("black", (0, 0, 0.5), (1.5, 3.4, 0.15))
    p.box(body, (0, 0, 0.9), (1.7, 3.5, 0.6))
    p.box(body, (0, -1.1, 1.28), (1.6, 1.0, 0.16)); p.box("black", (0, -1.7, 1.0), (1.2, 0.06, 0.3))   # hood, grille
    p.box("clear_glass", (0, -0.57, 1.5), (1.4, 0.05, 0.5), rot=(-10, 0, 0))
    for s in (-1, 1):
        p.box("black", (s * 0.8, 0.5, 1.6), (0.05, 1.6, 0.05)); p.box("fabric_brown", (s * 0.5, 0.9, 1.15), (0.5, 0.5, 0.2))
        for yy in (-0.3, 1.3):
            p.box("black", (s * 0.8, yy, 1.4), (0.05, 0.05, 0.4))                                       # roll-bar posts, from the body to the rail
        for yy in (-1.15, 1.15):
            wheel(p, "rubber", body, s * 0.9, yy, 0.38, 0.38, 0.3, n=10)
        p.box("paint_yellow", (s * 0.55, -1.76, 1.0), (0.2, 0.05, 0.2))
    return p


def trailer_flatbed(name="GV_TrailerFlatbed_01"):
    p = Prop(name)
    p.box("wood_grey", (0, 0, 0.8), (2.2, 4.0, 0.12))
    for x in (-0.6, 0.6):
        p.box("metal_dark", (x, 0, 0.67), (0.1, 4.0, 0.14))
    for s in (-1, 1):
        wheel(p, "rubber", "metal_galv", s * 1.2, 0.8, 0.45, 0.45, 0.25, n=10)
        wheel(p, "rubber", "metal_galv", s * 1.2, 1.5, 0.45, 0.45, 0.25, n=10)
        p.box("wood_dark", (s * 1.05, 0, 1.1), (0.08, 4.0, 0.45))
    p.box("wood_dark", (0, 1.96, 1.1), (2.2, 0.08, 0.45))
    p.box("metal_dark", (0, -2.8, 0.7), (0.1, 1.6, 0.1))                                              # the drawbar
    p.box("metal_galv", (0, -3.5, 0.7), (0.2, 0.2, 0.15))
    return p


# family -> list of (variant name, builder, kwargs)
def families():
    P = lambda body, label: (label, "pickup", dict(body=body))
    f = {}
    f["Pickup"] = [(NAMES[c], "pickup", dict(body=c)) for c in ("truck_blue", "cloth_red", "paint_white", "tractor_green", "tan", "black")]
    f["Tractor"] = [(n, "tractor", dict(body=c)) for n, c in (("Green", "tractor_green"), ("Red", "cloth_red"), ("Orange", "orange_cat"), ("Blue", "truck_blue"), ("Yellow", "paint_yellow"))]
    f["Sedan"] = [(NAMES[c], "sedan", dict(body=c)) for c in ("truck_blue", "cloth_red", "paint_white", "tan", "fabric_grey", "tractor_green", "black")]
    f["Wagon"] = [(NAMES[c], "wagon", dict(body=c)) for c in ("fabric_green", "paint_white", "tan", "truck_blue")]
    f["SUV"] = [(NAMES[c], "suv", dict(body=c)) for c in ("black", "paint_white", "fabric_grey", "cloth_red", "navy")]
    f["Minivan"] = [(NAMES[c], "minivan", dict(body=c)) for c in ("truck_blue", "paint_white", "cloth_red", "fabric_grey")]
    f["Van"] = [(n, "van", dict(body=c, extras=ex)) for n, c, ex in (("White", "paint_white", ()), ("Brown", "fabric_brown", ("deliverysign",)), ("Blue", "truck_blue", ()), ("Mail", "paint_white", ("deliverysign",)))]
    f["Taxi"] = [("Yellow", "sedan", dict(body="paint_yellow", extras=("taxi",))), ("Checker", "sedan", dict(body="paint_yellow", stripe="black", extras=("taxi",)))]
    f["Police"] = [
        ("Sheriff", "sedan", dict(body="paint_white", stripe="tan_uniform", extras=("lightbar",))),
        ("Deputy", "suv", dict(body="paint_white", stripe="tan_uniform", extras=("lightbar",))),
        ("StatePolice", "sedan", dict(body="navy", stripe="paint_white", extras=("lightbar",))),
        ("FBI_SUV", "suv", dict(body="black", glass="black", extras=("antenna",))),
        ("FBI_Van", "van", dict(body="black", glass="black", trim="black", extras=("antenna", "roofrack"))),   # the FBI's van (#19): black, dark glass, an antenna and a rack on the roof
        ("MIB_Sedan", "sedan", dict(body="black", glass="black", trim="black")),
    ]
    f["Ambulance"] = [("White", "van", dict(body="paint_white", stripe="cloth_red", extras=("cross", "lightbar")))]
    f["TowTruck"] = [("Yellow", "special", dict(fn="tow"))]
    f["ATV"] = [(n, "special", dict(fn="atv", body=c)) for n, c in (("Red", "cloth_red"), ("Green", "tractor_green"), ("Yellow", "paint_yellow"))]
    f["Motorcycle"] = [(n, "special", dict(fn="moto", body=c)) for n, c in (("Red", "cloth_red"), ("Black", "black"), ("Blue", "truck_blue"))]
    f["Jeep"] = [(n, "special", dict(fn="jeep", body=c)) for n, c in (("Olive", "tractor_green"), ("Tan", "tan"))]
    f["Trailer"] = [("Flatbed", "special", dict(fn="flatbed"))]
    return f


def build(family, label, kind, kw, condition):
    name = f"GV_{family}_{label}_01"
    if kind == "special":
        kw = dict(kw)
        which = kw.pop("fn")
        p = {"tow": tow_truck, "atv": atv, "moto": motorcycle, "jeep": jeep, "flatbed": trailer_flatbed}[which](name=name, **kw)
    elif kind == "pickup":
        p = vehicles.pickup(name=name, **kw)
    elif kind == "tractor":
        p = vehicles.tractor(name=name, **kw)
    else:
        p = box_car(name, kind, **kw)
    return p


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
                    prop.damage(seed=sum(ord(c) for c in prop.name) % 1000, drop=0.35, tilt=3.0, grime=4, max_part=0.03, grime_scale=3.0)
                obj, coll = prop.finish()
                common.export_fbx(coll, f"Assets/Art/Global/Vehicles/{family}/{prop.name}.fbx")
                obj.location = (x, (0 if cond == "New" else 7), 0)
                count += 1
            x += 4.0
    print("cars done", count)


if __name__ == "__main__":
    run()
