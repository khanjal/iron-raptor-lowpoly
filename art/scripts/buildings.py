"""Buildings for the Farmstead and the towns (asset list FM-B1..B17, GK-): exterior shells in many materials and conditions.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/buildings.py", run_name="__main__")
Optional globals: BUILDING_LIST (building names), SKIN_LIST (only these skins) and CONDITIONS (default New and Damaged). Exports
Assets/Art/<Farm|Global>/Buildings/<Building>/<name>.fbx, for example FM_Farmhouse_Brick_01.fbx and FM_Farmhouse_White_Damaged_01.fbx.

Each building is written once with logical colours (@wall, @trim, @roof, @door, @floor, @base) and then built once per SKIN, which maps
those to palette colours: white, yellow, blue or green siding, brick, stone, log, concrete block, corrugated metal, weathered boards.
The Damaged condition runs a skin through a wreck remap (paint faded, metal rusted, glass dark) and removes some wall pieces so
there are holes in the walls and gaps along the trim.

Exteriors only (interiors come from the kit): walls with real door and window openings (doors 1.2 x 2.2 m, windows 1.0 x 1.2 m), glass,
closed doors, a gable roof, a foundation slab. Footprints follow docs/levels/farmstead.md: farmhouse 24 x 18 m, barn 26 x 30 m, workshop
12 x 10 m. Buildings face -Y (the front), origin at the centre of the footprint on the ground. Add a building with a function that
returns a Prop and an entry in BUILDINGS (skins and conditions per building).
"""

import importlib
import math
import sys
from pathlib import Path

from mathutils import Vector

SLOT_TRIM = "@trim"
SLOT_ROOF = "@roof"
SLOT_DOOR = "@door"
SLOT_WALL = "@wall"
SLOT_BASE = "@base"
SLOT_FLOOR = "@floor"


sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop

from props_lib import T, wall_run, slab, gable_roof

SKINS = {   # logical colour -> palette colour
    "White": {SLOT_WALL: "paint_white", SLOT_TRIM: "paint_white", SLOT_ROOF: "metal_dark", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
    "Yellow": {SLOT_WALL: "siding_yellow", SLOT_TRIM: "paint_white", SLOT_ROOF: "roof_red", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
    "Blue": {SLOT_WALL: "siding_blue", SLOT_TRIM: "paint_white", SLOT_ROOF: "shingle", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
    "Green": {SLOT_WALL: "siding_green", SLOT_TRIM: "paint_white", SLOT_ROOF: "roof_green", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
    "Grey": {SLOT_WALL: "siding_grey", SLOT_TRIM: "paint_white", SLOT_ROOF: "shingle", SLOT_DOOR: "tractor_green", SLOT_FLOOR: "wood_grey", SLOT_BASE: "concrete"},
    "Brick": {SLOT_WALL: "brick", SLOT_TRIM: "paint_white", SLOT_ROOF: "shingle", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
    "Stone": {SLOT_WALL: "rock", SLOT_TRIM: "wood_dark", SLOT_ROOF: "roof_red", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_dark", SLOT_BASE: "rock"},
    "Log": {SLOT_WALL: "log", SLOT_TRIM: "wood_dark", SLOT_ROOF: "roof_green", SLOT_DOOR: "wood_light", SLOT_FLOOR: "wood_dark", SLOT_BASE: "rock"},
    "Block": {SLOT_WALL: "concrete", SLOT_TRIM: "metal_dark", SLOT_ROOF: "metal_galv", SLOT_DOOR: "metal_dark", SLOT_FLOOR: "concrete", SLOT_BASE: "concrete"},
    "Metal": {SLOT_WALL: "metal_galv", SLOT_TRIM: "metal_dark", SLOT_ROOF: "metal_galv", SLOT_DOOR: "metal_dark", SLOT_FLOOR: "concrete", SLOT_BASE: "concrete"},
    "Weathered": {SLOT_WALL: "wood_grey", SLOT_TRIM: "dead_wood", SLOT_ROOF: "rust", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_grey", SLOT_BASE: "concrete"},
    "Red": {SLOT_WALL: "barn_red", SLOT_TRIM: "paint_white", SLOT_ROOF: "metal_galv", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_grey", SLOT_BASE: "concrete"},
    "Beige": {SLOT_WALL: "wallpaper", SLOT_TRIM: "paint_white", SLOT_ROOF: "metal_galv", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
    "Teal": {SLOT_WALL: "trailer_teal", SLOT_TRIM: "paint_white", SLOT_ROOF: "paint_white", SLOT_DOOR: "paint_white", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
    "Cream": {SLOT_WALL: "stucco", SLOT_TRIM: "tractor_green", SLOT_ROOF: "roof_red", SLOT_DOOR: "wood_dark", SLOT_FLOOR: "wood_light", SLOT_BASE: "concrete"},
}

WRECK = {   # applied after the skin for the Damaged condition: paint faded, metal rusted, glass dark
    "paint_white": "concrete", "siding_yellow": "wood_grey", "siding_blue": "siding_grey", "siding_green": "dead_wood", "siding_grey": "dead_wood",
    "brick": "rust_dark", "stucco": "wood_grey", "trailer_teal": "dead_wood", "wallpaper": "wood_grey", "barn_red": "rust_dark",
    "wood_dark": "rust_dark", "wood_light": "wood_grey", "metal_galv": "rust", "metal_dark": "rust_dark", "roof_red": "rust_dark",
    "roof_green": "dead_wood", "shingle": "rust_dark", "glass": "screen", "tractor_green": "dead_wood", "log": "wood_dark", "rock": "dead_wood",
}


# one openings list per wall plus the style options, nine buildings call it positionally: a parameter object would be a refactor of its own
def box_building(p, wall, w, d, floors, floor_h, front=(), back=(), left=(), right=(), upper=None, trim=SLOT_TRIM, door=SLOT_DOOR, base=0.0):  # NOSONAR
    """Four walls of a rectangular building, floor by floor. Openings are for the ground floor; `upper` is a 4-tuple for upper floors."""
    x0, x1, y0, y1 = -w / 2, w / 2, -d / 2, d / 2
    for f in range(floors):
        z = base + f * floor_h
        oc = (front, back, left, right) if f == 0 else (upper or ((), (), (), ()))
        kw = {"trim": trim, "door_colour": door}
        wall_run(p, wall, (x0, y0), (x1, y0), z, floor_h, oc[0], **kw)
        wall_run(p, wall, (x1, y1), (x0, y1), z, floor_h, oc[1], **kw)                # the back wall runs the other way round
        wall_run(p, wall, (x0, y1), (x0, y0), z, floor_h, oc[2], **kw)
        wall_run(p, wall, (x1, y0), (x1, y1), z, floor_h, oc[3], **kw)
        if f > 0:
            slab(p, SLOT_FLOOR, 0, 0, w - T, d - T, z - 0.1, thick=0.2)                 # the floor between storeys


win = lambda off, w=1.0, sill=0.9, h=1.2: (off, w, sill, h)


def farmhouse():
    p = Prop("FM_Farmhouse")
    w, d = 24.0, 18.0
    slab(p, SLOT_BASE, 0, 0, w + 0.6, d + 0.6, -0.4, thick=0.5)
    front = [(2.5, 1.2, 0, 2.2)] + [win(o) for o in (6.0, 9.5, 13.0, 17.0, 20.5)]
    back = [(3.0, 1.2, 0, 2.2)] + [win(o) for o in (7.0, 11.0, 15.0, 19.0)]
    upper = ([win(o) for o in (4.0, 8.5, 13.0, 17.5, 21.0)], [win(o) for o in (4.0, 9.0, 14.0, 19.0)], [win(5.0), win(11.0)], [win(5.0), win(11.0)])
    box_building(p, SLOT_WALL, w, d, 2, 2.7, front, back, [win(4.0), win(9.0), win(13.5)], [(5.0, 1.2, 0, 2.2), win(10.0), win(14.0)], upper)
    slab(p, SLOT_FLOOR, 0, 0, w - T, d - T, 0.0, thick=0.15)
    gable_roof(p, SLOT_ROOF, 0, 0, w, d, 5.4, 3.6, overhang=0.7, along="x")
    slab(p, "wood_grey", -6.0, -d / 2 - 1.5, 13.0, 3.0, 0.0, thick=0.25)                # the porch
    for x in (-12.0, -9.0, -6.0, -3.0, 0.0):
        p.box(SLOT_TRIM, (x, -d / 2 - 2.8, 1.5), (0.18, 0.18, 3.0))
    p.box(SLOT_ROOF, (-6.0, -d / 2 - 1.6, 3.15), (13.4, 3.4, 0.14), rot=(6, 0, 0))                          # the porch roof slopes down away from the house
    for i in range(4):
        p.box("wood_grey", (-9.5, -d / 2 - 3.15 - i * 0.3, 0.2 - i * 0.05 - 0.05), (1.6, 0.3, 0.15))
    p.box("rust_dark", (8.5, 2.0, 7.4), (1.2, 1.2, 4.4))
    p.box("black", (8.5, 2.0, 9.65), (1.0, 1.0, 0.1))
    return p


def barn():
    p = Prop("FM_Barn")
    w, d = 26.0, 30.0
    slab(p, SLOT_BASE, 0, 0, w + 0.6, d + 0.6, -0.4, thick=0.5)
    box_building(p, SLOT_WALL, w, d, 1, 5.0, [(w / 2 - 4.0, 8.0, 0, 5.0)], [(w / 2 - 1.0, 2.0, 0, 3.0)],
                 [(5.0, 1.0, 1.6, 1.2), (12.0, 1.0, 1.6, 1.2), (19.0, 1.0, 1.6, 1.2), (25.0, 1.0, 1.6, 1.2)],
                 [(5.0, 1.0, 1.6, 1.2), (12.0, 1.0, 1.6, 1.2), (19.0, 1.0, 1.6, 1.2), (25.0, 1.0, 1.6, 1.2)])
    kw = {"trim": SLOT_TRIM, "door_colour": SLOT_DOOR}
    wall_run(p, SLOT_WALL, (-w / 2, -d / 2), (w / 2, -d / 2), 5.0, 2.2, [(w / 2 - 1.0, 2.0, 0, 2.0)], **kw)
    wall_run(p, SLOT_WALL, (w / 2, d / 2), (-w / 2, d / 2), 5.0, 2.2, **kw)
    wall_run(p, SLOT_WALL, (-w / 2, d / 2), (-w / 2, -d / 2), 5.0, 2.2, **kw)
    wall_run(p, SLOT_WALL, (w / 2, -d / 2), (w / 2, d / 2), 5.0, 2.2, **kw)
    slab(p, "wood_light", 0, 0, w - T, d - T, 4.9, thick=0.2)
    gable_roof(p, SLOT_ROOF, 0, 0, w, d, 7.2, 3.8, overhang=0.8, along="y")
    p.box("wood_dark", (w / 2 - 1.0, -d / 2 - 0.9, 8.4), (0.2, 1.8, 0.2))
    for x in (-6, 0, 6):
        p.box(SLOT_TRIM, (x, -d / 2 - 0.02, 2.5), (0.12, 0.05, 5.0))
    p.box(SLOT_TRIM, (0, -d / 2 - 0.02, 5.0), (w, 0.05, 0.14))
    return p


def workshop():
    p = Prop("FM_Workshop")
    w, d = 12.0, 10.0
    slab(p, SLOT_BASE, 0, 0, w + 0.4, d + 0.4, -0.3, thick=0.4)
    box_building(p, SLOT_WALL, w, d, 1, 3.2, [(2.5, 1.2, 0, 2.2)], [(w - 4.0, 1.0, 1.0, 1.2)], [], [])
    slab(p, "concrete", 0, 0, w - T, d - T, 0.0, thick=0.12)
    gable_roof(p, SLOT_ROOF, 0, 0, w, d, 3.2, 1.7, overhang=0.5, along="x")
    p.box(SLOT_ROOF, (-3.0, -d / 2 - 0.4, 3.0), (3.5, 0.8, 0.08), rot=(10, 0, 0))
    return p


def trailer():
    """A single-wide mobile home, 14 x 3.6 m, on piers behind a skirt, with a door, steps, windows, an A/C unit and a hitch."""
    p = Prop("GB_Trailer")
    w, d, h = 14.0, 3.6, 2.5
    z0 = 0.5                                                                          # raised on piers
    box_building(p, SLOT_WALL, w, d, 1, h, [(2.0, 0.9, 0, 2.0), win(5.0, 1.2), win(9.0, 1.2), win(12.0, 0.9)],
                 [win(2.0, 1.0), win(6.0, 1.2), win(10.0, 1.2)], [win(1.0, 1.0, 1.0, 1.0)], [(1.2, 0.9, 0, 2.0)], base=z0)
    p.box(SLOT_TRIM, (0, 0, 0.25), (w + 0.1, d + 0.1, 0.5))                              # the skirt, under the raised shell
    slab(p, SLOT_FLOOR, 0, 0, w - T, d - T, z0, thick=0.15)
    gable_roof(p, SLOT_ROOF, 0, 0, w, d, h + z0, 0.55, overhang=0.35, along="x")
    for k in range(3):                                                                # steps and landing at the front door
        p.box("wood_grey", (-w / 2 + 2.45, -d / 2 - 0.5 - k * 0.0, 0.18 + k * 0.0), (1.2, 1.0, 0.1))
    p.box("wood_grey", (-w / 2 + 2.45, -d / 2 - 1.1, 0.12), (1.2, 0.4, 0.24))
    p.box("wood_grey", (-w / 2 + 2.45, -d / 2 - 0.6, 0.4), (1.4, 1.0, 0.1))
    for sx in (-1, 1):
        p.box("metal_galv", (-w / 2 + 2.45 + sx * 0.65, -d / 2 - 0.6, 0.9), (0.04, 1.0, 0.04))
        p.box("metal_galv", (-w / 2 + 2.45 + sx * 0.65, -d / 2 - 1.05, 0.65), (0.04, 0.04, 0.5))
    p.box("metal_galv", (3.5, 0.0, h + z0 + 0.75), (0.9, 0.7, 0.4))                         # a roof air conditioner
    p.box("black", (3.5, -0.36, h + z0 + 0.75), (0.7, 0.01, 0.3))
    p.cyl("metal_dark", (w / 2 + 0.4, 0.6, 0.55), 0.22, 0.9, n=8, axis="x")            # the propane tank
    p.box("metal_dark", (w / 2 + 2.0, 0.0, 0.5), (2.6, 0.25, 0.12))                    # the hitch tongue
    p.box("metal_galv", (w / 2 + 3.2, 0.0, 0.52), (0.3, 0.3, 0.2))
    p.box("metal_galv", (-4.0, d / 2 + 0.01, 1.4), (0.4, 0.05, 0.4))                    # a vent
    return p


def shed():
    p = Prop("FM_Shed")
    w, d = 3.2, 4.0
    slab(p, SLOT_BASE, 0, 0, w + 0.3, d + 0.3, -0.2, thick=0.25)
    box_building(p, SLOT_WALL, w, d, 1, 2.4, [(0.9, 1.2, 0, 2.0)], [], [win(1.0, 0.8, 1.0, 0.6)], [])
    gable_roof(p, SLOT_ROOF, 0, 0, w, d, 2.4, 0.9, overhang=0.3, along="y")
    return p


def garage():
    p = Prop("GB_Garage")
    w, d = 6.4, 6.0
    slab(p, SLOT_BASE, 0, 0, w + 0.4, d + 0.4, -0.3, thick=0.4)
    box_building(p, SLOT_WALL, w, d, 1, 2.8, [(0.8, 5.0, 0, 2.3)], [win(2.5, 1.2, 1.2, 0.8)], [(1.5, 0.9, 0, 2.0)], [])
    gable_roof(p, SLOT_ROOF, 0, 0, w, d, 2.8, 1.2, overhang=0.4, along="y")
    p.box(SLOT_DOOR, (-0.0 + 0.8 - w / 2 + 2.5, -d / 2 - 0.02, 1.1), (4.8, 0.06, 2.2))     # the garage door, closed
    for k in range(5):
        p.box(SLOT_TRIM, (-w / 2 + 3.3, -d / 2 - 0.06, 0.25 + k * 0.42), (4.8, 0.02, 0.05))
    return p


def town_house():
    p = Prop("GB_TownHouse")
    w, d = 10.0, 8.0
    slab(p, SLOT_BASE, 0, 0, w + 0.5, d + 0.5, -0.35, thick=0.45)
    box_building(p, SLOT_WALL, w, d, 1, 2.8, [(1.0, 1.0, 0.9, 1.2), (3.8, 1.2, 0, 2.2), (7.0, 1.0, 0.9, 1.2)], [win(2.0), win(6.0)], [win(2.0), win(5.5)], [win(2.0), win(5.5)])
    slab(p, SLOT_FLOOR, 0, 0, w - T, d - T, 0.0, thick=0.15)
    gable_roof(p, SLOT_ROOF, 0, 0, w, d, 2.8, 2.6, overhang=0.5, along="x")
    slab(p, "wood_grey", -1.2, -d / 2 - 1.1, 3.4, 2.2, 0.0, thick=0.25)
    for x in (-2.7, 0.3):
        p.box(SLOT_TRIM, (x, -d / 2 - 2.0, 1.4), (0.14, 0.14, 2.8))
    p.box(SLOT_ROOF, (-1.2, -d / 2 - 1.2, 2.9), (3.8, 2.4, 0.12), rot=(8, 0, 0))
    p.box("rust_dark", (3.0, 1.0, 5.2), (0.9, 0.9, 2.2))
    return p


def diner():
    p = Prop("GB_Diner")
    w, d = 18.0, 8.0
    slab(p, SLOT_BASE, 0, 0, w + 0.4, d + 0.4, -0.3, thick=0.4)
    box_building(p, SLOT_WALL, w, d, 1, 3.4, [(7.8, 1.6, 0, 2.2), win(1.0, 2.5, 0.8, 1.8), win(3.8, 3.0, 0.8, 1.8), win(10.2, 3.0, 0.8, 1.8), win(13.6, 3.0, 0.8, 1.8)],
                 [(3.0, 1.2, 0, 2.2), win(8.0, 1.0)], [win(3.0, 1.2)], [win(3.0, 1.2)])
    slab(p, SLOT_FLOOR, 0, 0, w - T, d - T, 0.0, thick=0.15)
    p.box(SLOT_ROOF, (0, 0, 3.6), (w + 0.6, d + 0.6, 0.3))                               # a flat roof with a deep fascia
    p.box("metal_galv", (0, -d / 2 - 0.15, 3.4), (w + 0.6, 0.12, 0.45))
    p.box("cloth_red", (0, -d / 2 - 0.15, 3.0), (w, 0.05, 0.1))
    p.box("metal_dark", (-6.0, -d / 2 - 0.2, 5.0), (0.2, 0.2, 3.0))                    # a pole sign
    p.box("cloth_red", (-6.0, -d / 2 - 0.2, 6.6), (3.0, 0.3, 1.0))
    p.box("glow_cyan", (-6.0, -d / 2 - 0.37, 6.6), (2.6, 0.05, 0.6))
    return p


def silo():
    p = Prop("FM_Silo")
    n = 12
    p.loft_rings(SLOT_WALL, [common.ring_z(z, 0, 0, 2.5, 2.5, n=n) for z in (0.0, 14.0)])
    for z in range(1, 14, 2):
        p.loft_rings(SLOT_TRIM, [common.ring_z(z, 0, 0, 2.54, 2.54, n=n), common.ring_z(z + 0.12, 0, 0, 2.54, 2.54, n=n)])
    p.loft_rings(SLOT_ROOF, [common.ring_z(14.0, 0, 0, 2.5, 2.5, n=n), common.ring_z(14.7, 0, 0, 2.0, 2.0, n=n), common.ring_z(15.2, 0, 0, 1.0, 1.0, n=n), common.ring_z(15.4, 0, 0, 0.2, 0.2, n=n)])
    p.box(SLOT_DOOR, (0, -2.55, 1.1), (1.0, 0.1, 2.0))
    p.box("metal_dark", (2.52, 0.0, 7.0), (0.06, 0.5, 14.0))                             # the chute and ladder
    for z in range(1, 14):
        p.box("metal_dark", (2.57, 0, z), (0.1, 0.5, 0.05))
    return p


def windmill():
    p = Prop("FM_Windmill")
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box(SLOT_WALL, (sx * 0.85, sy * 0.85, 4.5), (0.14, 0.14, 9.4), rot=(sy * 4.5, -sx * 4.5, 0))                       # legs lean in towards the top
    for z in (2.0, 4.5, 7.0):
        half = 0.85 + (4.5 - z) * math.tan(math.radians(4.5))                              # where the legs are at this height
        for s in (-1, 1):                                                                  # a square of rails round the four legs
            p.box(SLOT_TRIM, (0, s * half, z), (2 * half, 0.08, 0.08))
            p.box(SLOT_TRIM, (s * half, 0, z), (0.08, 2 * half, 0.08))
    p.box(SLOT_FLOOR, (0, 0, 9.2), (1.6, 1.6, 0.14))
    p.box("metal_dark", (0, 0, 9.7), (0.7, 1.4, 0.7))                                    # the gearbox
    p.cyl("metal_dark", (0, -0.85, 9.7), 0.2, 0.4, n=6, axis="y")
    for k in range(8):                                                                    # the rotor
        a = k * 45
        p.box(SLOT_TRIM, (0.9 * math.sin(math.radians(a)), -1.06, 9.7 + 0.9 * math.cos(math.radians(a))), (0.35, 0.06, 1.8), rot=(0, a, 0))
    p.box(SLOT_WALL, (0, 1.9, 9.7), (0.04, 2.0, 0.9))                                      # the tail vane
    p.cyl(SLOT_ROOF, (0.0, 0.0, 0.8), 1.2, 1.6, n=8)                                       # the tank at the base
    return p


def coop():
    """Hollow house on legs (floor, walls with a pop hole and a nesting-box door, roosts, straw), a ramp and a fenced run."""
    p = Prop("FM_ChickenCoop")
    t = 0.06
    z0, h = 0.4, 1.2
    p.box("wood_grey", (0, 0.4, z0 + 0.03), (2.4, 1.6, 0.06))                              # the floor
    p.box("hay", (0, 0.4, z0 + 0.075), (2.2, 1.4, 0.03))                                  # straw
    xe, ys, yn = 1.2 - t / 2, -0.4 + t / 2, 1.2 - t / 2
    wall_run(p, SLOT_WALL, (-xe, ys), (xe, ys), z0, h, [(xe - 0.2, 0.4, 0.35, 0.5)], thick=t, fill=False, frame=False)      # front, with the pop hole
    wall_run(p, SLOT_WALL, (xe, yn), (-xe, yn), z0, h, [], thick=t)
    wall_run(p, SLOT_WALL, (-xe, yn), (-xe, ys), z0, h, [], thick=t)
    wall_run(p, SLOT_WALL, (xe, ys), (xe, yn), z0, h, [(0.62, 0.3, 0.55, 0.3)], thick=t, fill=False, frame=False)          # east, with the nesting-box hatch
    for y in (0.7, 1.0):
        p.cyl("wood_dark", (0, y, z0 + 0.55), 0.025, 2.3, n=5, axis="x")                      # roosts, wall to wall
    for x in (-1.0, 1.0):
        for y in (-0.2, 1.0):
            p.box("wood_dark", (x, y, 0.2), (0.1, 0.1, 0.4))                                  # legs
    gable_roof(p, SLOT_ROOF, 0, 0.4, 2.4, 1.6, 1.6, 0.5, overhang=0.15, along="x")
    # the nesting box on the east side: hollow too
    p.box("wood_dark", (1.35, 0.4, 0.95), (0.3, 0.8, 0.04))
    p.box("wood_dark", (1.35, 0.4, 1.37), (0.36, 0.86, 0.04), rot=(0, 10, 0))
    p.box("wood_dark", (1.5, 0.4, 1.16), (0.04, 0.8, 0.4))
    for y in (0.0, 0.8):
        p.box("wood_dark", (1.35, y, 1.16), (0.3, 0.04, 0.4))
    # its ramp: from the sill of the pop hole (z 0.75) down to the ground, 22 degrees, with cleats
    top_y, top_z = -0.4, 0.75
    length = top_z / math.sin(math.radians(22))
    p.box("wood_light", (0.0, top_y - length / 2 * math.cos(math.radians(22)), top_z - length / 2 * math.sin(math.radians(22))), (0.4, length, 0.04), rot=(22, 0, 0))
    for k in range(1, 6):
        d = k * length / 6
        p.box("wood_dark", (0.0, top_y - d * math.cos(math.radians(22)), top_z - d * math.sin(math.radians(22)) + 0.03), (0.4, 0.03, 0.03))
    # the run: attached to the front of the house, as wide as the house, 3 m out, wire on three sides
    for x in (-1.2, 1.2):
        p.box("wood_grey", (x, -3.4, 0.6), (0.08, 0.08, 1.2))
        p.box("wood_grey", (x, -1.9, 1.2), (0.06, 3.0, 0.06))                                # the top rails, house to front posts
    p.box("wood_grey", (0, -3.4, 1.2), (2.4, 0.06, 0.06))
    # the run's wire: thin bars you can see through (a solid panel hides the hens), a vertical bar every 12 cm and three rails
    for i in range(21):
        p.box("fabric_grey", (-1.2 + i * 0.12, -3.4, 0.6), (0.012, 0.012, 1.1))
    for j in range(26):
        for x in (-1.2, 1.2):
            p.box("fabric_grey", (x, -0.45 - j * 0.12, 0.6), (0.012, 0.012, 1.1))
    for z in (0.1, 0.6, 1.1):
        p.box("fabric_grey", (0, -3.4, z), (2.4, 0.012, 0.012))
        for x in (-1.2, 1.2):
            p.box("fabric_grey", (x, -1.9, z), (0.012, 3.0, 0.012))
    return p


# The outhouse is a hiding place, so it is big enough for a player (a capsule 1 m wide): 2 m square outside, a 1.2 m door. Repeated in
# Assets/Editor/FarmsteadBuildings.cs (Outhouse): change both.
OUTHOUSE_SIZE = 2.0
OUTHOUSE_DOOR = 1.2


def outhouse():
    """A hut you can go inside and hide in: 2 m square, thin walls, a seat against the back wall, a gable roof, a vent, and a door that is
    its own part (hinged on its left, opening inward)."""
    p = Prop("FM_Outhouse")
    w, t, h = OUTHOUSE_SIZE, 0.12, 2.4
    e = w / 2 - t / 2                                                                  # wall centre lines
    dw = OUTHOUSE_DOOR
    wall_run(p, SLOT_WALL, (-e, -e), (e, -e), 0, h, [(e - dw / 2, dw, 0, 2.2)], thick=t, fill=False)        # front, with the doorway
    wall_run(p, SLOT_WALL, (e, e), (-e, e), 0, h, [], thick=t)
    wall_run(p, SLOT_WALL, (-e, e), (-e, -e), 0, h, [], thick=t)
    wall_run(p, SLOT_WALL, (e, -e), (e, e), 0, h, [(e - 0.2, 0.4, 1.7, 0.3)], thick=t, fill=False, frame=False)    # a small vent high on the side
    p.box("wood_grey", (0, 0, 0.02), (w, w, 0.04))                                      # the floor
    p.box("wood_light", (0, e - 0.25, 0.22), (1.2, 0.5, 0.44))                          # the seat, against the back wall
    p.cyl("black", (0, e - 0.25, 0.45), 0.14, 0.02, n=8)                                # and its hole
    p.cyl("paper", (-0.7, e - 0.08, 1.0), 0.06, 0.1, n=6, axis="x")                     # a roll of paper on the back wall
    gable_roof(p, SLOT_ROOF, 0, 0, w, w, h, 0.55, overhang=0.15, along="y")
    hinge_x = -dw / 2
    with p.part("Door", pivot=(hinge_x, -e, 0.0), kind="hinge", axis="z", limit=100):
        p.box(SLOT_DOOR, (hinge_x + (dw - 0.04) / 2, -e, 1.09), (dw - 0.04, 0.05, 2.18))
        p.box("black", (hinge_x + (dw - 0.04) / 2, -e - 0.03, 1.8), (0.16, 0.01, 0.2))   # the crescent cut-out
        p.box("metal_dark", (hinge_x + dw - 0.12, -e - 0.04, 1.0), (0.06, 0.03, 0.05))   # the latch
    return p


def well():
    p = Prop("FM_Well")
    props_lib.lathe(p, "rock", [(0.0, 0.0001), (0.0, 0.85), (0.9, 0.85), (0.9, 0.6), (0.1, 0.58), (0.1, 0.0001)], n=10)   # a hollow stone ring, a shaft 0.8 m deep
    p.cyl("navy", (0, 0, 0.14), 0.58, 0.02, n=10)                                          # dark water at the bottom
    for s in (-1, 1):
        p.box(SLOT_TRIM, (s * 0.8, 0, 1.4), (0.12, 0.12, 2.0))
    p.box(SLOT_TRIM, (0, 0, 2.3), (1.8, 0.1, 0.12))
    for s in (-1, 1):
        p.box(SLOT_ROOF, (0, s * 0.45, 2.2), (1.9, 0.9, 0.06), rot=(-s * 25, 0, 0))                           # ridge edges meet the beam, eaves reach the posts
    p.cyl("wood_dark", (0, 0, 1.75), 0.1, 1.94, n=6, axis="x")                           # the windlass roller, through the posts
    p.cyl("tan", (0, 0, 1.75), 0.13, 0.5, n=8, axis="x")                                 # rope wound on it
    p.box("metal_dark", (0.99, 0.0, 1.75), (0.1, 0.08, 0.08))                            # the crank: a stub, an arm and a handle
    p.box("metal_dark", (1.01, 0.0, 1.5), (0.04, 0.04, 0.5))
    p.box("wood_dark", (1.01, 0.0, 1.25), (0.16, 0.04, 0.04))
    p.cyl("tan", (0, 0, 1.52), 0.015, 0.5, n=4)                                          # the rope hanging from the roller to the bucket
    p.cyl("wood_dark", (0, 0, 1.17), 0.15, 0.28, n=8, top_radius=0.18)                   # the bucket
    p.cyl("metal_galv", (0, 0, 1.06), 0.152, 0.03, n=8)
    p.cyl("metal_galv", (0, 0, 1.29), 0.182, 0.03, n=8)
    return p


# building: (function, folder, skins for New, skins for Damaged)
BUILDINGS = {
    "farmhouse": (farmhouse, "Farm", ["White", "Yellow", "Blue", "Green", "Brick", "Stone", "Log", "Weathered"], ["White", "Weathered", "Brick"]),
    "barn": (barn, "Farm", ["Red", "White", "Weathered", "Yellow"], ["Red", "Weathered"]),
    "workshop": (workshop, "Farm", ["Weathered", "Metal", "Block", "Red"], ["Metal", "Weathered"]),
    "shed": (shed, "Farm", ["Weathered", "Red", "Metal", "White"], ["Weathered", "Metal"]),
    "coop": (coop, "Farm", ["Red", "Weathered", "White"], ["Weathered"]),
    "outhouse": (outhouse, "Farm", ["Weathered", "White", "Log"], ["Weathered"]),
    "well": (well, "Farm", ["Weathered", "Stone"], ["Weathered"]),
    "silo": (silo, "Farm", ["Block", "Metal", "Weathered"], ["Weathered"]),
    "windmill": (windmill, "Farm", ["Weathered", "White", "Metal"], ["Weathered"]),
    "trailer": (trailer, "Global", ["Beige", "White", "Teal", "Yellow", "Green"], ["Beige", "White", "Teal", "Yellow", "Green"]),
    "garage": (garage, "Global", ["White", "Grey", "Brick", "Weathered"], ["Weathered", "White"]),
    "town_house": (town_house, "Global", ["White", "Yellow", "Blue", "Brick", "Grey", "Cream"], ["White", "Grey", "Brick"]),
    "diner": (diner, "Global", ["Cream", "White", "Teal"], ["Cream"]),
}


def _build_skin(key, fn, folder, cond, skin):
    """Build one building in one skin and condition, export it as FBX and return its object."""
    theme = dict(SKINS[skin])
    if cond == "Damaged":
        theme = {**WRECK, **{k: WRECK.get(v, v) for k, v in theme.items()}}          # literal colours (glass, trim...) rot too
    props_lib.THEME = theme
    try:
        prop = fn()
    finally:
        props_lib.THEME = {}
    prop.name = f"{prop.name}_{skin}" + ("" if cond == "New" else "_Damaged") + "_01"
    if cond == "Damaged":
        prop.damage(seed=sum(ord(c) for c in prop.name) % 1000, drop=0.10, tilt=0.0, grime=8, max_part=12.0, grime_scale=4.0)
    obj, coll = prop.finish()
    common.export_fbx(coll, f"Assets/Art/{folder}/Buildings/{key.title().replace('_', '')}/{prop.name}.fbx")
    return obj


def _skins(new_skins, dmg_skins, cond, skin_only):
    """The skins to build for a condition: those of its list that SKIN_LIST names (all of them without it)."""
    return [skin for skin in (new_skins if cond == "New" else dmg_skins) if not skin_only or skin in skin_only]


def run():
    names = globals().get("BUILDING_LIST") or list(BUILDINGS)
    conds = globals().get("CONDITIONS") or ["New", "Damaged"]
    skin_only = globals().get("SKIN_LIST")
    y, count = 0.0, 0
    for key in names:
        fn, folder, new_skins, dmg_skins = BUILDINGS[key]
        x = 0.0
        for cond in conds:
            for skin in _skins(new_skins, dmg_skins, cond, skin_only):
                obj = _build_skin(key, fn, folder, cond, skin)
                obj.location = (x, y, 0)
                x += obj.dimensions.x + 6
                count += 1
        y += 45.0
    props_lib.write_interactions()                                                          # the outhouse door is a moving part
    print("buildings done", count)


if __name__ == "__main__":
    run()
