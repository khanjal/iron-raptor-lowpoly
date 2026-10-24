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

NAMES = {"truck_blue": "Blue", "cloth_red": "Red", "paint_white": "White", "tractor_green": "Green", "paint_yellow": "Yellow",
         "black": "Black", "tan": "Tan", "fabric_grey": "Grey", "rust_dark": "Brown", "navy": "Navy", "orange_cat": "Orange",
         "golden": "Gold", "cream": "Cream", "alien_violet": "Purple", "fabric_green": "Sage"}

WRECK = {   # the Damaged colour remap: paint faded, rusted, lights and glass gone dark
    "truck_blue": "rust", "cloth_red": "rust_dark", "paint_white": "concrete", "tractor_green": "dead_wood", "paint_yellow": "wood_grey",
    "tan": "wood_grey", "navy": "fabric_grey", "fabric_grey": "dead_wood", "orange_cat": "rust", "golden": "wood_grey", "cream": "wood_grey",
    "metal_galv": "rust", "glass": "screen", "black": "rust_dark", "fabric_green": "dead_wood", "alien_violet": "fabric_grey",
}

KINDS = {   # length, width, hood, cabin, body height, cabin height, wheel radius, windscreen run, rear window run, solid (no glass behind the front doors)
    "sedan": dict(L=4.6, W=1.8, hood=1.35, cabin=1.9, bh=0.55, ch=0.5, wr=0.33, rf=0.5, rr=0.45),
    "wagon": dict(L=4.8, W=1.85, hood=1.3, cabin=3.0, bh=0.55, ch=0.58, wr=0.33, rf=0.5, rr=0.2),
    "suv": dict(L=4.7, W=1.95, hood=1.25, cabin=3.0, bh=0.72, ch=0.62, wr=0.4, rf=0.45, rr=0.2),
    "minivan": dict(L=5.0, W=1.9, hood=1.0, cabin=3.6, bh=0.62, ch=0.78, wr=0.34, rf=0.7, rr=0.15),
    "van": dict(L=5.4, W=2.0, hood=0.7, cabin=4.4, bh=0.8, ch=1.3, wr=0.36, rf=0.3, rr=0.0, solid=True),
}


def box_car(name, kind, body, trim="metal_galv", glass="glass", stripe=None, extras=()):
    """A road car from its dimensions (#344): a lofted body shell with a low nose, a rising hood and a tail; a glasshouse with a slanted
    windscreen, side windows that lean in and a rear window, carried on A, B and C pillars under a roof panel; door seams and handles,
    sills, mirrors, wheel arches and detailed wheels, a grille with bars, headlight and tail light housings, bumpers, a plate, an exhaust."""
    k = KINDS[kind]
    L, W, hood, cab, bh, ch, wr = k["L"], k["W"], k["hood"], k["cabin"], k["bh"], k["ch"], k["wr"]
    rf, rr, solid = k["rf"], k["rr"], k.get("solid", False)
    p = Prop(name)
    base = 0.3
    ytop = base + bh                                              # top of the lower body
    hw = W / 2
    y_front, y_rear = -L / 2, L / 2
    y_c0 = y_front + hood                                         # the cabin starts here
    y_c1 = min(y_c0 + cab, y_rear - 0.3)
    cab_mid = (y_c0 + y_c1) / 2
    cab_len = y_c1 - y_c0
    boot = y_c1 < y_rear - 0.35                                   # a sedan's boot lid
    p.box("black", (0, 0, base - 0.05), (W - 0.3, L - 0.5, 0.15))                       # underbody

    # the lower body, lofted: a low nose, a hood that rises to the cowl, the flanks, a tail
    st = [(y_front, hw * 0.93, base + 0.1, ytop - 0.14, 0.06), (y_front + 0.22, hw * 0.99, base + 0.04, ytop - 0.05, 0.07),
          (y_front + hood * 0.6, hw, base + 0.02, ytop - 0.01, 0.07), (y_c0, hw, base + 0.02, ytop + 0.02, 0.07),
          (y_c1, hw, base + 0.02, ytop + (0.03 if boot else 0.0), 0.07)]
    if boot:
        st.append((y_rear - 0.3, hw, base + 0.02, ytop + 0.04, 0.07))
    st += [(y_rear - 0.08, hw * 0.99, base + 0.06, ytop - 0.02, 0.06), (y_rear, hw * 0.94, base + 0.1, ytop - 0.1, 0.05)]
    vehicles.body_loft(p, body, st)

    # the glasshouse: windscreen run rf, rear window run rr, sides leaning in; a van is solid behind the front doors
    hb, ht = hw - 0.12, hw - 0.25
    zt = ytop + ch - 0.03
    s1, s2 = y_c0 + rf, y_c1 - rr
    dl = min(1.0, (cab_len - 0.3) / 2)                            # a door's length
    y_b = y_c0 + 0.12 + dl                                        # the B pillar, at the seam between the doors
    ends = lambda y: (y, hb, hb - 0.02, ytop, ytop + 0.02)
    if solid:
        y_k = y_b + 0.04                                          # the glass stops at the back edge of the B pillar
        vehicles.glasshouse(p, glass, [ends(y_c0), (s1, hb, ht, ytop, zt), (y_k, hb, ht, ytop, zt)])
        vehicles.glasshouse(p, body, [(y_k, hb, ht, ytop, zt), (y_c1, hb, ht, ytop, zt)])      # the cargo box: a vertical back
    else:
        vehicles.glasshouse(p, glass, [ends(y_c0), (s1, hb, ht, ytop, zt), (s2, hb, ht, ytop, zt), ends(y_c1)])
    p.box(body, (0, (s1 + s2) / 2, zt + 0.025), (2 * ht + 0.06, s2 - s1 + 0.06, 0.07))                          # roof panel
    z_roof = zt + 0.06
    for sx in (-1, 1):
        props_lib.rod(p, body, (sx * hb, y_c0, ytop + 0.02), (sx * ht, s1, zt), 0.08)                           # A pillars
        props_lib.rod(p, body, (sx * hb, y_b, ytop), (sx * ht, y_b, zt), 0.07)                                  # B pillars
        if not solid:
            props_lib.rod(p, body, (sx * ht, s2, zt), (sx * hb, y_c1, ytop + 0.02), 0.11)                        # C pillars
            if cab_len > 3.2:
                props_lib.rod(p, body, (sx * hb, y_b + 1.2, ytop), (sx * ht, y_b + 1.2, zt), 0.07)              # a third pair on a long cabin
            if kind in ("suv", "wagon"):
                p.box("black", (sx * (ht - 0.04), (s1 + s2) / 2, z_roof + 0.015), (0.04, s2 - s1 - 0.3, 0.04))        # roof rails
        # door seams, handles, sills, mirrors
        seams = [y_c0 + 0.12, y_b] + ([] if solid else [y_b + dl])
        clear = lambda y: all(abs(y - wy) > wr + 0.12 for wy in (y_front + 0.95, y_rear - 0.95))             # not through a wheel arch
        for y in [y for y in seams if clear(y)]:
            p.box("black", (sx * (hw - 0.015), y, base + 0.02 + (ytop - base) * 0.45), (0.04, 0.03, bh * 0.66))
        for y in [y for y in seams[1:] if clear(y - 0.18)]:
            p.box(trim, (sx * (hw + 0.005), y - 0.18, ytop - 0.17), (0.04, 0.14, 0.035))
        p.box("black", (sx * (hw - 0.01), 0, base + 0.07), (0.06, L - 1.9 - 2 * wr - 0.24, 0.07))
        vehicles.mirror(p, body, sx, hw - 0.12, y_c0 + 0.1, ytop + 0.03)
        # lights: bezel and lens at the front, housing and lens at the back, indicators, fog lights
        p.box(trim, (sx * (hw - 0.3), y_front - 0.012, ytop - 0.24), (0.34, 0.06, 0.17))
        p.box("paint_yellow", (sx * (hw - 0.3), y_front - 0.025, ytop - 0.24), (0.28, 0.08, 0.12))
        p.box("orange_cat", (sx * (hw - 0.06), y_front + 0.01, ytop - 0.34), (0.1, 0.06, 0.07))
        p.box("black", (sx * (hw - 0.3), y_rear + 0.006, ytop - 0.2), (0.38, 0.05, 0.16))
        p.box("cloth_red", (sx * (hw - 0.3), y_rear + 0.015, ytop - 0.2), (0.34, 0.07, 0.12))
        p.box("paint_white", (sx * (hw - 0.62), y_rear + 0.015, ytop - 0.2), (0.1, 0.07, 0.1))                  # reversing lights
        p.box("paint_yellow", (sx * (hw - 0.22), y_front - 0.02, base + 0.27), (0.1, 0.04, 0.07))               # fog lights
        # bumper ends that wrap the corners
        p.box(trim, (sx * (hw - 0.04), y_front - 0.02, base + 0.14), (0.1, 0.26, 0.18))
        p.box(trim, (sx * (hw - 0.04), y_rear + 0.02, base + 0.14), (0.1, 0.26, 0.18))
        for yy in (y_front + 0.95, y_rear - 0.95):
            vehicles.car_wheel(p, trim, sx * (hw - 0.1), yy, wr, 0.24, n=12)
            vehicles.arch(p, "black", sx * (hw + 0.005), yy, wr, wr + 0.1)
    if solid:                                                                                                   # rear doors: a seam down the middle and a window in each
        p.box("black", (0, y_c1 + 0.006, ytop + ch * 0.5), (0.025, 0.03, ch * 0.92))
        for sx in (-1, 1):
            p.box(glass, (sx * 0.4, y_c1 + 0.006, ytop + ch * 0.62), (0.58, 0.03, 0.42))
            p.box(trim, (sx * 0.08, y_c1 + 0.012, ytop + ch * 0.35), (0.04, 0.03, 0.12))
    p.box(trim, (0, y_front - 0.05, base + 0.14), (W * 0.98, 0.16, 0.18))                                      # bumpers
    p.box(trim, (0, y_rear + 0.05, base + 0.14), (W * 0.98, 0.16, 0.18))
    p.box("black", (0, y_front - 0.03, base + 0.04), (W * 0.8, 0.12, 0.1))                                     # valances
    p.box("black", (0, y_rear + 0.03, base + 0.04), (W * 0.8, 0.12, 0.1))
    p.box("black", (0, y_front - 0.012, ytop - 0.25), (W - 1.0, 0.04, 0.2))                                    # grille
    for z in (ytop - 0.31, ytop - 0.25, ytop - 0.19):
        p.box(trim, (0, y_front - 0.035, z), (W - 1.04, 0.02, 0.025))                                          # its bars
    p.box("paint_white", (0, y_rear + 0.01, base + 0.31), (0.4, 0.04, 0.15))                                   # plate, above the bumper
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
        elif e == "cross":
            p.box("cloth_red", (0, 0, ytop + ch * 0.45), (2 * (hw - 0.16), 0.9, 0.22)); p.box("cloth_red", (0, 0, ytop + ch * 0.45), (2 * (hw - 0.16), 0.22, 0.9))
        elif e == "roofrack":
            p.box("black", (0, cab_mid, z_roof + 0.1), (W - 0.5, y_c1 - y_c0 - 0.3, 0.06))
            for sy in (-0.7, 0.7):
                p.box("black", (0, cab_mid + sy, z_roof + 0.06), (W - 0.5, 0.05, 0.1))
        elif e == "deliverysign":
            p.box("fabric_brown" if body != "fabric_brown" else "paint_white", (0, cab_mid + 0.2, z_roof - 0.5), (2 * (hw - 0.18), 1.8, 0.6))
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
    f["Semi"] = [(n, "special", dict(fn="semi", body=c)) for n, c in (("Red", "cloth_red"), ("Blue", "truck_blue"), ("White", "paint_white"), ("Black", "black"))]
    f["SemiTrailer"] = [("Box_White", "special", dict(fn="boxtrailer", body="paint_white")), ("Box_Blue", "special", dict(fn="boxtrailer", body="truck_blue")),
                        ("Tanker_Silver", "special", dict(fn="tanker"))]
    f["Bus"] = [("School", "special", dict(fn="bus"))]
    f["FireTruck"] = [("Red", "special", dict(fn="fire"))]
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
    return p


OTHER_FAMILIES = {"ATV", "Motorcycle", "Jeep", "Trailer", "Semi", "SemiTrailer", "Bus", "FireTruck"}   # the families of #357: only these get the length-scaled tilt and prune_floating, so a rebuild leaves the Damaged cars of #344 as exported


def prune_floating(prop, margin=0.01):
    """After Prop.damage() has dropped small parts at random, drop what is left with nothing to touch (a mirror head whose arm went, a lens whose bezel went,
    a handlebar whose clamp went). Two parts touch when their surfaces overlap or come within `margin` metres; whatever is not connected to the biggest
    group of parts is removed (the same test as the contact check the art PRs report). Returns how many parts went."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    isl = []
    for colour, bm in prop.parts.items():
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
        bi, vi, loi, hii, ti, ci = isl[i]
        bj, vj, loj, hij, tj, cj = isl[j]
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
        if g is main or any(isl[i][5] == "rubber" for i in g):                 # a tyre is never dropped: it would take a wheel off the model
            continue
        for i in g:
            bmesh.ops.delete(isl[i][0], geom=isl[i][1], context="VERTS")
            removed += 1
    return removed


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
                obj, coll = prop.finish()
                common.export_fbx(coll, f"Assets/Art/Global/Vehicles/{family}/{prop.name}.fbx")
                obj.location = (x, (0 if cond == "New" else 7), 0)
                count += 1
            x += 4.0
    print("cars done", count)


if __name__ == "__main__":
    run()
