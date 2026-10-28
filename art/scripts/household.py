"""Furniture and fixtures for houses, motels, diners, offices and labs (asset list GH-01..GH-11): flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/household.py", run_name="__main__")
Optional global HOUSEHOLD_LIST (names or group names such as "seating"). Exports Assets/Art/Global/Household/<name>.fbx.

Real sizes (a dining chair seat is 0.45 m high, a fridge 1.8 m). Everything faces -Y with its origin on the floor at the centre of
the base; wall-mounted pieces (shelf, mirror, towel rail, fuse box, air conditioner) have their origin at the centre of the mount. Add a piece by writing a function with the @piece(group) decorator; it returns a Prop. Small decor, lamps and
electronics are in decor.py.
"""

import importlib
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop

PIECES = {}


def piece(group, name):
    def deco(fn):
        PIECES[name] = (fn, group)
        return fn
    return deco


def legs(p, colour, w, d, h, t=0.05, inset=0.03, cx=0.0, cy=0.0):
    """Four square legs under a w x d top, h tall."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box(colour, (cx + sx * (w / 2 - inset - t / 2), cy + sy * (d / 2 - inset - t / 2), h / 2), (t, t, h))


# ===== Seating (GH-01) =========================================================================================
@piece("seating", "Chair_Kitchen")
def chair_kitchen():
    p = Prop("GH_Chair_Kitchen_01")
    legs(p, "wood_light", 0.42, 0.42, 0.45, 0.04)
    p.box("wood_light", (0, 0, 0.47), (0.44, 0.44, 0.04))
    p.box("wood_light", (0, 0.2, 0.7), (0.4, 0.03, 0.4))
    for x in (-0.12, 0.0, 0.12):
        p.box("wood_light", (x, 0.2, 0.7), (0.03, 0.035, 0.38))
    return p


@piece("seating", "Chair_Dining")
def chair_dining():
    p = Prop("GH_Chair_Dining_01")
    legs(p, "wood_dark", 0.44, 0.44, 0.46, 0.045)
    p.box("fabric_brown", (0, 0, 0.485), (0.44, 0.44, 0.06))
    for x in (-0.19, 0.19):
        p.box("wood_dark", (x, 0.2, 0.75), (0.04, 0.04, 0.58))
    p.box("wood_dark", (0, 0.2, 0.92), (0.42, 0.04, 0.12))
    p.box("wood_dark", (0, 0.2, 0.74), (0.34, 0.03, 0.14))
    return p


@piece("seating", "Chair_Office")
def chair_office():
    p = Prop("GH_Chair_Office_01")
    p.cyl("black", (0, 0, 0.3), 0.04, 0.4, n=6)
    for a in range(5):
        p.box("black", (0.1 * math.cos(math.radians(a * 72)), 0.1 * math.sin(math.radians(a * 72)), 0.08), (0.2, 0.04, 0.04), rot=(0, 0, a * 72))
    p.box("fabric_blue", (0, 0, 0.5), (0.5, 0.5, 0.08))
    p.box("fabric_blue", (0, 0.22, 0.79), (0.46, 0.08, 0.5))
    for s in (-1, 1):
        p.box("black", (s * 0.27, 0, 0.66), (0.04, 0.3, 0.04))
        p.box("black", (s * 0.27, 0, 0.6), (0.04, 0.04, 0.12))                                      # armrest posts, up from the seat
    return p


@piece("seating", "Armchair")
def armchair():
    p = Prop("GH_Armchair_01")
    p.box("fabric_green", (0, 0, 0.2), (0.9, 0.85, 0.3))
    p.box("fabric_green", (0, 0.05, 0.43), (0.62, 0.7, 0.16))                 # seat cushion
    p.box("fabric_green", (0, 0.36, 0.65), (0.9, 0.18, 0.62))                 # back
    for s in (-1, 1):
        p.box("fabric_green", (s * 0.4, 0, 0.5), (0.14, 0.8, 0.4))            # arms
        p.box("wood_dark", (s * 0.38, -0.34, 0.04), (0.06, 0.06, 0.08))
        p.box("wood_dark", (s * 0.38, 0.34, 0.04), (0.06, 0.06, 0.08))
    return p


@piece("seating", "RockingChair")
def rocking_chair():
    p = Prop("GH_RockingChair_01")
    for s in (-1, 1):
        p.box("wood_dark", (s * 0.27, 0, 0.04), (0.04, 0.95, 0.05), rot=(0, 0, 0))             # the rockers
        p.box("wood_dark", (s * 0.27, -0.28, 0.25), (0.04, 0.04, 0.45), rot=(8, 0, 0))
        p.box("wood_dark", (s * 0.27, 0.28, 0.3), (0.04, 0.04, 0.55), rot=(-8, 0, 0))
        p.box("wood_dark", (s * 0.27, 0.0, 0.62), (0.04, 0.5, 0.04))                           # arm
    p.box("wood_light", (0, -0.02, 0.45), (0.5, 0.5, 0.04))
    p.box("wood_light", (0, 0.3, 0.82), (0.5, 0.04, 0.6), rot=(-10, 0, 0))
    for x in (-0.15, 0, 0.15):
        p.box("wood_dark", (x, 0.3, 0.82), (0.03, 0.05, 0.56), rot=(-10, 0, 0))
    return p


@piece("seating", "Sofa")
def sofa():
    p = Prop("GH_Sofa_01")
    p.box("fabric_blue", (0, 0, 0.22), (2.0, 0.9, 0.34))
    for x in (-0.46, 0.46):
        p.box("fabric_blue", (x, -0.04, 0.5), (0.9, 0.7, 0.2))
    p.box("fabric_blue", (0, 0.36, 0.7), (2.0, 0.2, 0.56))
    for s in (-1, 1):
        p.box("fabric_blue", (s * 0.95, 0, 0.5), (0.2, 0.9, 0.5))
        p.box("wood_dark", (s * 0.9, -0.38, 0.04), (0.07, 0.07, 0.08))
        p.box("wood_dark", (s * 0.9, 0.38, 0.04), (0.07, 0.07, 0.08))
    return p


@piece("seating", "Bench")
def bench():
    p = Prop("GH_Bench_01")
    p.box("wood_grey", (0, 0, 0.45), (1.5, 0.4, 0.05))
    for x in (-0.6, 0.6):
        p.box("wood_grey", (x, 0, 0.22), (0.06, 0.34, 0.44))
    return p


@piece("seating", "BarStool")
def bar_stool():
    p = Prop("GH_BarStool_01")
    p.cyl("cloth_red", (0, 0, 0.74), 0.19, 0.08, n=8)
    p.cyl("metal_galv", (0, 0, 0.36), 0.03, 0.72, n=6)
    p.cyl("metal_galv", (0, 0, 0.02), 0.22, 0.04, n=8)
    p.cyl("metal_galv", (0, 0, 0.3), 0.15, 0.02, n=8)
    return p


# ===== Tables (GH-02) ==========================================================================================
@piece("tables", "Table_Dining")
def table_dining():
    p = Prop("GH_Table_Dining_01")
    p.box("wood_light", (0, 0, 0.74), (1.6, 0.9, 0.05))
    legs(p, "wood_dark", 1.6, 0.9, 0.72, 0.08, 0.05)
    return p


@piece("tables", "Table_Coffee")
def table_coffee():
    p = Prop("GH_Table_Coffee_01")
    p.box("wood_dark", (0, 0, 0.42), (1.0, 0.55, 0.04))
    legs(p, "wood_dark", 1.0, 0.55, 0.4, 0.05, 0.03)
    p.box("wood_dark", (0, 0, 0.16), (0.9, 0.45, 0.02))
    return p


@piece("tables", "Table_Side")
def table_side():
    p = Prop("GH_Table_Side_01")
    p.cyl("wood_light", (0, 0, 0.55), 0.25, 0.04, n=8)
    p.cyl("wood_dark", (0, 0, 0.27), 0.03, 0.54, n=6)
    p.cyl("wood_dark", (0, 0, 0.02), 0.17, 0.04, n=8)
    return p


@piece("tables", "Desk_Wood")
def desk_wood():
    p = Prop("GH_Desk_Wood_01")
    p.box("wood_dark", (0, 0, 0.74), (1.4, 0.7, 0.04))
    for s in (-1, 1):
        p.box("wood_dark", (s * 0.6, 0, 0.36), (0.18, 0.62, 0.72))                       # pedestals
    p.box("wood_dark", (0, 0.3, 0.36), (1.0, 0.04, 0.7))                                # modesty panel
    for z in (0.2, 0.42, 0.62):
        p.box("wood_light", (0.6, -0.31, z), (0.14, 0.02, 0.17))                        # drawer fronts
        p.box("metal_dark", (0.6, -0.33, z), (0.05, 0.02, 0.02))
    return p


@piece("tables", "Desk_Office")
def desk_office():
    p = Prop("GH_Desk_Office_01")
    p.box("wood_light", (0, 0, 0.74), (1.6, 0.8, 0.04))
    for s in (-1, 1):
        p.box("metal_dark", (s * 0.76, 0, 0.36), (0.04, 0.72, 0.72))
    p.box("metal_dark", (0, 0.35, 0.5), (1.5, 0.03, 0.4))
    return p


@piece("tables", "Workbench")
def workbench():
    p = Prop("GH_Workbench_01")
    p.box("wood_light", (0, 0, 0.9), (2.0, 0.7, 0.06))
    legs(p, "wood_dark", 2.0, 0.7, 0.88, 0.1, 0.04)
    p.box("wood_dark", (0, 0, 0.25), (1.8, 0.6, 0.04))
    p.box("wood_dark", (0, 0.32, 1.15), (2.0, 0.04, 0.5))                              # pegboard back
    p.box("metal_dark", (0.85, -0.2, 0.98), (0.14, 0.24, 0.12))                         # a vise
    return p


@piece("tables", "Counter_Kitchen")
def counter_kitchen():
    p = Prop("GH_Counter_Kitchen_01")
    p.box("wood_dark", (0, 0, 0.42), (2.0, 0.6, 0.8))
    p.box("concrete", (0, -0.02, 0.88), (2.04, 0.64, 0.05))
    for x in (-0.66, 0.0, 0.66):
        p.box("wood_light", (x, -0.305, 0.45), (0.6, 0.02, 0.64))
        p.box("metal_galv", (x + 0.22, -0.325, 0.62), (0.02, 0.02, 0.12))
    return p


@piece("tables", "Counter_Bar")
def counter_bar():
    p = Prop("GH_Counter_Bar_01")
    p.box("wood_dark", (0, 0, 0.55), (2.6, 0.6, 1.1))
    p.box("wood_light", (0, -0.05, 1.12), (2.7, 0.75, 0.05))
    p.box("metal_galv", (0, -0.36, 0.2), (2.4, 0.04, 0.04))
    return p


# ===== Beds (GH-03) ============================================================================================
@piece("beds", "Bed_Double")
def bed_double():
    p = Prop("GH_Bed_Double_01")
    p.box("wood_dark", (0, 0, 0.2), (1.6, 2.0, 0.24))                                  # frame
    p.box("linen", (0, 0.0, 0.42), (1.5, 1.9, 0.22))                                    # mattress
    p.box("fabric_blue", (0, -0.25, 0.54), (1.52, 1.35, 0.06))                          # blanket
    p.box("linen", (-0.38, 0.8, 0.58), (0.55, 0.3, 0.1))
    p.box("linen", (0.38, 0.8, 0.58), (0.55, 0.3, 0.1))
    p.box("wood_dark", (0, 1.04, 0.62), (1.66, 0.08, 0.9))                              # headboard
    p.box("wood_dark", (0, -1.02, 0.34), (1.66, 0.06, 0.4))                             # footboard
    return p


@piece("beds", "Bed_Single")
def bed_single():
    p = Prop("GH_Bed_Single_01")
    p.box("wood_light", (0, 0, 0.2), (0.95, 2.0, 0.22))
    p.box("linen", (0, 0, 0.4), (0.88, 1.9, 0.2))
    p.box("fabric_red", (0, -0.2, 0.5), (0.9, 1.4, 0.05))
    p.box("linen", (0, 0.8, 0.54), (0.5, 0.3, 0.1))
    p.box("wood_light", (0, 1.04, 0.5), (0.98, 0.06, 0.7))
    return p


@piece("beds", "Bed_Bunk")
def bed_bunk():
    p = Prop("GH_Bed_Bunk_01")
    for z in (0.35, 1.45):
        p.box("wood_light", (0, 0, z), (0.95, 2.0, 0.1))
        p.box("linen", (0, 0, z + 0.14), (0.88, 1.9, 0.18))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("wood_dark", (sx * 0.46, sy * 0.96, 0.9), (0.07, 0.07, 1.8))
    p.box("wood_dark", (-0.47, 0.0, 1.7), (0.03, 1.6, 0.18))                            # top guard rail
    for z in (0.5, 0.8, 1.1):
        p.box("wood_dark", (0.47, -0.97, z), (0.4, 0.03, 0.04), rot=(0, 0, 0))          # ladder rungs
    return p


@piece("beds", "Bed_Child")
def bed_child():
    p = Prop("GH_Bed_Child_01")
    p.box("wood_light", (0, 0, 0.18), (0.8, 1.6, 0.18))
    p.box("fabric_pink", (0, 0, 0.34), (0.74, 1.5, 0.16))
    p.box("linen", (0, 0.6, 0.46), (0.45, 0.28, 0.1))
    p.box("wood_light", (0, 0.82, 0.45), (0.84, 0.05, 0.6))
    return p


@piece("beds", "Cot")
def cot():
    p = Prop("GH_Cot_01")
    p.box("wood_light", (0, 0, 0.3), (0.65, 1.25, 0.05))
    p.box("linen", (0, 0, 0.36), (0.6, 1.2, 0.07))
    for sx in (-1, 1):
        p.box("wood_light", (sx * 0.32, 0, 0.75), (0.04, 1.25, 0.06))
        for k in range(8):
            p.box("wood_light", (sx * 0.32, -0.52 + k * 0.15, 0.55), (0.03, 0.03, 0.5))
    for sy in (-1, 1):
        p.box("wood_light", (0, sy * 0.62, 0.62), (0.65, 0.04, 0.7))
    return p


@piece("beds", "Gurney")
def gurney():
    p = Prop("GH_Gurney_01")
    p.box("metal_galv", (0, 0, 0.8), (0.7, 1.9, 0.05))
    p.box("linen", (0, 0, 0.86), (0.66, 1.85, 0.07))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("metal_dark", (sx * 0.28, sy * 0.8, 0.4), (0.04, 0.04, 0.8))
            p.cyl("rubber", (sx * 0.28, sy * 0.8, 0.07), 0.07, 0.04, n=6, axis="x")
    return p


# ===== Storage (GH-04) =========================================================================================
@piece("storage", "Wardrobe")
def wardrobe():
    p = Prop("GH_Wardrobe_01")
    p.box("wood_dark", (0, 0, 0.95), (1.0, 0.55, 1.9))
    for x in (-0.25, 0.25):
        p.box("wood_light", (x, -0.285, 0.95), (0.46, 0.02, 1.8))
        p.box("metal_galv", (x * 0.35, -0.305, 0.95), (0.03, 0.02, 0.18))
    p.box("wood_light", (0, 0, 1.92), (1.04, 0.58, 0.04))
    return p


@piece("storage", "Dresser")
def dresser():
    p = Prop("GH_Dresser_01")
    p.box("wood_dark", (0, 0, 0.45), (1.2, 0.5, 0.9))
    for k, z in enumerate((0.2, 0.45, 0.7)):
        p.box("wood_light", (0, -0.255, z), (1.1, 0.02, 0.2))
        for x in (-0.3, 0.3):
            p.box("metal_galv", (x, -0.275, z), (0.1, 0.02, 0.025))
    p.box("wood_light", (0, 0, 0.91), (1.24, 0.54, 0.04))
    return p


@piece("storage", "Nightstand")
def nightstand():
    p = Prop("GH_Nightstand_01")
    p.box("wood_light", (0, 0, 0.28), (0.45, 0.4, 0.56))
    p.box("wood_dark", (0, -0.205, 0.38), (0.4, 0.02, 0.18))
    p.box("wood_dark", (0, -0.205, 0.16), (0.4, 0.02, 0.18))
    p.box("metal_galv", (0, -0.225, 0.38), (0.08, 0.02, 0.02))
    return p


BOOK_COLOURS = ["book_red", "book_blue", "book_green", "fabric_brown", "fabric_mustard", "navy", "paper", "terracotta", "fabric_grey", "cloth_red"]


def _books(p, rng, x0, x1, z0, clearance, colours, gap=0.15, lean=0.15, thin=(0.03, 0.07), tall=(0.2, 0.37), depth=(0.14, 0.24)):
    """A run of books standing on a shelf board (top face at z0) between x0 and x1: random widths, heights and colours, now and then a gap, and a
    book that leans on its neighbour (it stands on one corner: lifted by half its width times the lean's sine)."""
    x = x0
    prev_h = 0.0
    while x < x1 - 0.04:
        if rng.random() < gap:
            x += rng.uniform(0.04, 0.16)
            prev_h = 0.0                                       # nothing to lean on after a gap
            continue
        w = rng.uniform(*thin)
        h = min(clearance - 0.03, rng.uniform(*tall))
        d = rng.uniform(*depth)
        col = rng.choice(colours)
        if x + w > x1:
            break
        a = rng.uniform(10, 22)
        if rng.random() < lean and x > x0 + 0.05 and prev_h >= h and x + w * math.cos(math.radians(a)) + h * math.sin(math.radians(a)) < x1:
            # leaning on the book before it (taller than this one, so the top touches it): the bottom-left corner stands on the board, the top end
            # tilts towards -X (a rotation about Y by -a); this corner is the lowest point, the top-left corner the leftmost, which is where x is
            c = math.cos(math.radians(a))
            sn = math.sin(math.radians(a))
            cx = x + (w / 2) * c + (h / 2) * sn
            zc = z0 + (w / 2) * sn + (h / 2) * c
            p.box(col, (cx, 0.0, zc), (w, d, h), rot=(0, -a, 0))
            x = x + w * c + h * sn + 0.01
            prev_h = 0.0                                       # only a standing book can be leant on
            continue
        else:
            p.box(col, (x + w / 2, 0.0, z0 + h / 2), (w, d, h))
            x += w + 0.004
        prev_h = h
    return x


def _bookcase_frame(p, wood="wood_dark"):
    for s_ in (-1, 1):
        p.box(wood, (s_ * 0.4, 0, 0.9), (0.04, 0.3, 1.8))
    p.box(wood, (0, 0.14, 0.9), (0.8, 0.02, 1.8))
    for z in (0.02, 0.45, 0.9, 1.35, 1.78):
        p.box(wood, (0, 0, z), (0.8, 0.3, 0.04))


# row tops: the boards' top faces (0.04 thick boards at 0.02, 0.45, 0.9, 1.35) and the clear height above each
_ROWS = ((0.04, 0.39), (0.47, 0.41), (0.92, 0.41), (1.37, 0.39))


def _shelf_novels(p, rng, z0, clear, colours):
    """Full rows of paperbacks, a few leaning."""
    _books(p, rng, -0.38, 0.38, z0, clear, colours, gap=0.05, lean=0.2)


def _shelf_sparse(p, rng, row, z0, clear, colours):
    """Half the shelf: books, then a vase, a frame, a plant, an empty stretch."""
    _books(p, rng, -0.38, rng.uniform(-0.05, 0.12), z0, clear, colours, gap=0.1, lean=0.3)
    if row == 1:
        p.cyl("terracotta", (0.22, 0.0, z0 + 0.11), 0.07, 0.22, n=6, top_radius=0.05)
    elif row == 2:
        p.box("gold", (0.2, 0.06, z0 + 0.13), (0.2, 0.02, 0.26), rot=(-8, 0, 0))     # a photo frame, leaning back
        p.box("paper", (0.2, 0.05, z0 + 0.13), (0.15, 0.01, 0.2), rot=(-8, 0, 0))
    elif row == 3:
        p.cyl("plant_green", (0.22, 0.0, z0 + 0.14), 0.09, 0.28, n=6, top_radius=0.14)


def _shelf_binders(p, rng, z0, clear):
    """A study's: tall dark binders and box files, a stack of papers lying flat."""
    _books(p, rng, -0.38, 0.1, z0, clear, ["navy", "fabric_grey", "black", "fabric_brown"], gap=0.03, lean=0.0, thin=(0.05, 0.09), tall=(0.28, 0.37), depth=(0.2, 0.26))
    # seeded modelling variation, not security
    for k in range(rng.randint(2, 4)):  # NOSONAR
        p.box(rng.choice(["paper", "linen", "cream"]), (0.25, 0.0, z0 + 0.02 + k * 0.04), (0.28 - 0.03 * (k % 2), 0.22, 0.04))  # NOSONAR


def _shelf_bright(p, rng, row, z0, clear, colours):
    """A child's: fat colourful picture books, a pile on the floor of the shelf, a toy."""
    _books(p, rng, -0.38, 0.0 if row == 0 else 0.38, z0, clear, colours, gap=0.15, lean=0.25, thin=(0.05, 0.1), tall=(0.2, 0.32), depth=(0.18, 0.26))
    if row == 0:
        p.box("fabric_red", (0.2, 0.0, z0 + 0.05), (0.14, 0.14, 0.1))                 # a toy block, in the free stretch


def _shelf_mixed(p, rng, z0, clear, colours):
    """An ordinary shelf with a stack of books lying down on each of two shelves."""
    _books(p, rng, -0.38, 0.15, z0, clear, colours, gap=0.1, lean=0.2)
    # seeded modelling variation, not security
    for k in range(rng.randint(2, 4)):  # NOSONAR
        p.box(rng.choice(colours), (0.26, 0.0, z0 + 0.025 + k * 0.05), (0.2 + 0.04 * (k % 2), 0.15, 0.05))  # NOSONAR


def _bookcase(name, seed, colours, kind):
    """Five bookcases, all 0.8 x 0.3 x 1.8 m so they swap one for another: a variant is a seed and a mood (the books, the gaps, a few things that are not books)."""
    rng = random.Random(seed)
    p = Prop(name)
    _bookcase_frame(p)
    for row, (z0, clear) in enumerate(_ROWS):
        if kind == "novels":
            _shelf_novels(p, rng, z0, clear, colours)
        elif kind == "sparse":
            _shelf_sparse(p, rng, row, z0, clear, colours)
        elif kind == "binders":
            _shelf_binders(p, rng, z0, clear)
        elif kind == "bright":
            _shelf_bright(p, rng, row, z0, clear, colours)
        else:
            _shelf_mixed(p, rng, z0, clear, colours)
    return p


@piece("storage", "Bookcase")
def bookcase():
    return _bookcase("GH_Bookcase_01", 11, BOOK_COLOURS, "mixed")


@piece("storage", "Bookcase_02")
def bookcase_02():
    return _bookcase("GH_Bookcase_02", 22, ["book_red", "book_blue", "book_green", "paper", "cream", "fabric_mustard"], "novels")


@piece("storage", "Bookcase_03")
def bookcase_03():
    return _bookcase("GH_Bookcase_03", 33, ["book_green", "fabric_brown", "terracotta", "paper"], "sparse")


@piece("storage", "Bookcase_04")
def bookcase_04():
    return _bookcase("GH_Bookcase_04", 44, ["navy", "fabric_grey"], "binders")


@piece("storage", "Bookcase_05")
def bookcase_05():
    return _bookcase("GH_Bookcase_05", 55, ["pink", "paint_yellow", "fabric_blue", "cloth_red", "fabric_green", "book_blue"], "bright")


@piece("storage", "Cabinet")
def cabinet():
    p = Prop("GH_Cabinet_01")
    p.box("wood_light", (0, 0, 0.6), (0.8, 0.38, 1.2))
    for x in (-0.2, 0.2):
        p.box("glass", (x, -0.2, 0.75), (0.34, 0.02, 0.6))
        p.box("wood_dark", (x, -0.2, 0.2), (0.36, 0.02, 0.3))
    return p


@piece("storage", "Locker")
def locker():
    p = Prop("GH_Locker_01")
    p.box("tractor_green", (0, 0, 0.9), (0.4, 0.5, 1.8))
    p.box("metal_dark", (0, -0.255, 1.4), (0.3, 0.02, 0.18))                             # vents
    p.box("metal_dark", (0, -0.255, 0.4), (0.3, 0.02, 0.18))
    p.box("metal_galv", (0.12, -0.265, 0.95), (0.03, 0.02, 0.1))
    return p


@piece("storage", "FilingCabinet")
def filing_cabinet():
    p = Prop("GH_FilingCabinet_01")
    p.box("metal_dark", (0, 0, 0.65), (0.45, 0.6, 1.3))
    for z in (0.3, 0.65, 1.0):
        p.box("metal_galv", (0, -0.305, z), (0.4, 0.02, 0.3))
        p.box("black", (0, -0.325, z + 0.08), (0.14, 0.02, 0.03))
    return p


@piece("storage", "Safe")
def safe():
    p = Prop("GH_Safe_01")
    p.box("metal_dark", (0, 0, 0.3), (0.5, 0.5, 0.6))
    p.box("metal_galv", (0, -0.255, 0.3), (0.38, 0.02, 0.48))
    p.cyl("black", (0.0, -0.275, 0.3), 0.08, 0.03, n=8, axis="y")
    p.box("metal_galv", (-0.14, -0.28, 0.3), (0.03, 0.03, 0.2))
    return p


@piece("storage", "Chest")
def chest():
    p = Prop("GH_Chest_01")
    p.box("wood_dark", (0, 0, 0.22), (0.9, 0.5, 0.44))
    p.box("wood_light", (0, 0, 0.5), (0.9, 0.5, 0.12), taper=0.85)
    for x in (-0.3, 0.3):
        p.box("metal_dark", (x, 0, 0.3), (0.06, 0.52, 0.5))
    p.box("metal_galv", (0, -0.27, 0.42), (0.08, 0.02, 0.1))
    return p


@piece("storage", "Shelf_Wall")
def shelf_wall():
    p = Prop("GH_Shelf_Wall_01")
    p.box("wood_light", (0, 0, 0.0), (1.0, 0.22, 0.03))
    for x in (-0.38, 0.38):
        p.box("metal_dark", (x, 0.05, -0.08), (0.03, 0.12, 0.14), rot=(0, 0, 0))
    return p


@piece("storage", "Shelf_Wall_02")
def shelf_wall_02():
    p = Prop("GH_Shelf_Wall_02")                                                    # a dark plank on two black L brackets
    p.box("wood_dark", (0, 0, 0.0), (1.0, 0.22, 0.035))
    for x in (-0.4, 0.4):
        p.box("black", (x, 0.1, -0.07), (0.025, 0.02, 0.14))
        p.box("black", (x, 0.0, -0.032), (0.025, 0.2, 0.025))
    return p


@piece("storage", "Shelf_Wall_03")
def shelf_wall_03():
    p = Prop("GH_Shelf_Wall_03")                                                    # a white-painted board on three wooden corbels
    p.box("paint_white", (0, 0, 0.0), (1.0, 0.22, 0.03))
    for x in (-0.42, 0.0, 0.42):
        p.box("wood_dark", (x, 0.06, -0.055), (0.04, 0.1, 0.08), taper=0.6)
    return p


@piece("storage", "Shelf_Wall_04")
def shelf_wall_04():
    p = Prop("GH_Shelf_Wall_04")                                                    # an old grey plank on galvanised brackets
    p.box("wood_grey", (0, 0, 0.0), (1.0, 0.22, 0.03))
    for x in (-0.36, 0.36):
        p.box("metal_galv", (x, 0.09, -0.07), (0.03, 0.03, 0.14))
        p.box("metal_galv", (x, 0.0, -0.03), (0.03, 0.2, 0.025))
    return p


@piece("storage", "Shelf_Wall_05")
def shelf_wall_05():
    p = Prop("GH_Shelf_Wall_05")                                                    # two thin boards side by side on rusty rod brackets
    p.box("wood_light", (0, -0.055, 0.0), (1.0, 0.105, 0.025))
    p.box("wood_light", (0, 0.055, 0.0), (1.0, 0.105, 0.025))
    for x in (-0.4, 0.4):
        p.box("rust", (x, 0.1, -0.08), (0.02, 0.02, 0.15))
        p.box("rust", (x, 0.0, -0.04), (0.02, 0.2, 0.02))
    return p


# ===== Kitchen (GH-05) =========================================================================================
@piece("kitchen", "Stove")
def stove():
    p = Prop("GH_Stove_01")
    p.box("enamel_white", (0, 0, 0.45), (0.6, 0.65, 0.9))
    p.box("black", (0, -0.331, 0.4), (0.46, 0.02, 0.4))                                  # oven door window
    p.box("glass", (0, -0.34, 0.42), (0.36, 0.01, 0.22))
    p.box("metal_galv", (0, -0.36, 0.64), (0.4, 0.03, 0.03))
    for x in (-0.2, -0.07, 0.07, 0.2):
        p.cyl("black", (x, -0.34, 0.8), 0.02, 0.03, n=6, axis="y")
    for x, y in ((-0.14, -0.12), (0.14, -0.12), (-0.14, 0.14), (0.14, 0.14)):
        p.cyl("black", (x, y, 0.91), 0.1, 0.02, n=8)
    p.box("enamel_white", (0, 0.3, 1.0), (0.6, 0.05, 0.2))
    return p


@piece("kitchen", "Fridge")
def fridge():
    p = Prop("GH_Fridge_01")
    p.box("enamel_cream", (0, 0, 0.9), (0.7, 0.7, 1.8))
    p.box("metal_dark", (0, -0.351, 1.2), (0.7, 0.01, 0.02))                              # the door split
    p.box("metal_galv", (0.28, -0.37, 1.45), (0.03, 0.04, 0.3))
    p.box("metal_galv", (0.28, -0.37, 0.7), (0.03, 0.04, 0.3))
    p.box("metal_dark", (0, 0, 0.05), (0.66, 0.66, 0.06))
    return p


@piece("kitchen", "Sink_Kitchen")
def sink_kitchen():
    p = Prop("GH_Sink_Kitchen_01")
    p.box("wood_light", (0, 0, 0.42), (1.2, 0.6, 0.8))
    p.box("concrete", (0, 0, 0.85), (1.24, 0.64, 0.06))
    p.box("metal_galv", (-0.2, -0.0, 0.86), (0.5, 0.4, 0.06))                              # basin
    p.box("metal_dark", (-0.2, 0.0, 0.88), (0.42, 0.32, 0.02))
    p.cyl("metal_galv", (-0.2, 0.22, 1.0), 0.02, 0.28, n=6)
    p.box("metal_galv", (-0.2, 0.12, 1.12), (0.03, 0.2, 0.03))
    for x in (0.1, 0.45):
        p.box("wood_dark", (x, -0.305, 0.45), (0.5 if x < 0.3 else 0.25, 0.02, 0.62))
    return p


@piece("kitchen", "Microwave")
def microwave():
    p = Prop("GH_Microwave_01")
    p.box("enamel_white", (0, 0, 0.15), (0.5, 0.38, 0.3))
    p.box("black", (-0.07, -0.195, 0.15), (0.3, 0.01, 0.22))
    p.box("fabric_grey", (0.19, -0.195, 0.15), (0.08, 0.01, 0.22))
    return p


@piece("kitchen", "Toaster")
def toaster():
    p = Prop("GH_Toaster_01")
    p.box("metal_galv", (0, 0, 0.1), (0.3, 0.17, 0.2))
    p.box("black", (0, 0, 0.205), (0.22, 0.03, 0.01))
    p.box("black", (0.17, 0, 0.12), (0.04, 0.04, 0.03))
    return p


@piece("kitchen", "Kettle")
def kettle():
    p = Prop("GH_Kettle_01")
    p.cyl("metal_galv", (0, 0, 0.1), 0.1, 0.2, n=8, top_radius=0.07)
    p.box("metal_dark", (0.1, 0, 0.17), (0.04, 0.03, 0.12), rot=(0, -20, 0))
    p.cyl("metal_galv", (-0.115, 0, 0.14), 0.02, 0.1, n=4, rot=(0, 40, 0))
    p.cyl("black", (0, 0, 0.215), 0.03, 0.03, n=6)
    return p


@piece("kitchen", "Pot")
def pot():
    p = Prop("GH_Pot_01")
    p.cyl("metal_dark", (0, 0, 0.1), 0.12, 0.2, n=8)
    p.cyl("metal_galv", (0, 0, 0.205), 0.125, 0.012, n=8)
    p.box("black", (0.16, 0, 0.17), (0.1, 0.03, 0.02))
    return p


@piece("kitchen", "Plates")
def plates():
    p = Prop("GH_Plates_01")
    for k in range(5):
        p.cyl("porcelain", (0, 0, 0.012 + k * 0.016), 0.11, 0.014, n=10)
    return p


@piece("kitchen", "Mug")
def mug():
    p = Prop("GH_Mug_01")
    p.cyl("cloth_red", (0, 0, 0.05), 0.04, 0.1, n=8)
    p.box("cloth_red", (0.055, 0, 0.06), (0.03, 0.012, 0.06))
    return p


@piece("kitchen", "BreadBox")
def bread_box():
    p = Prop("GH_BreadBox_01")
    p.box("enamel_cream", (0, 0, 0.1), (0.4, 0.25, 0.2))
    p.box("enamel_cream", (0, -0.05, 0.22), (0.4, 0.15, 0.06), rot=(-20, 0, 0))
    return p


# ===== Bathroom (GH-06) ========================================================================================
@piece("bath", "Toilet")
def toilet():
    p = Prop("GH_Toilet_01")
    p.box("porcelain", (0, 0.2, 0.43), (0.38, 0.2, 0.4))                                  # cistern
    p.cyl("porcelain", (0, -0.05, 0.2), 0.17, 0.4, n=8, top_radius=0.2)
    p.cyl("porcelain", (0, -0.05, 0.4), 0.21, 0.04, n=8)
    p.cyl("enamel_white", (0, 0.2, 0.64), 0.05, 0.02, n=6)
    return p


@piece("bath", "Sink_Bath")
def sink_bath():
    p = Prop("GH_Sink_Bath_01")
    p.cyl("porcelain", (0, 0.06, 0.42), 0.07, 0.84, n=6)
    p.box("porcelain", (0, 0, 0.86), (0.55, 0.42, 0.14))
    p.box("metal_galv", (0, 0.1, 0.98), (0.04, 0.04, 0.1))
    p.box("metal_galv", (0, 0.04, 1.03), (0.03, 0.14, 0.03))
    return p


@piece("bath", "Tub")
def tub():
    p = Prop("GH_Tub_01")
    p.box("porcelain", (0, 0, 0.28), (1.7, 0.75, 0.56))
    p.box("tile_blue", (0, 0, 0.5), (1.5, 0.55, 0.1))
    p.box("metal_galv", (0.7, 0.3, 0.68), (0.04, 0.04, 0.14))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("metal_galv", (sx * 0.75, sy * 0.3, 0.03), (0.07, 0.07, 0.06))
    return p


@piece("bath", "Shower")
def shower():
    p = Prop("GH_Shower_01")
    p.box("porcelain", (0, 0, 0.04), (0.9, 0.9, 0.08))
    for k, (x, y, w, d) in enumerate(((0, 0.44, 0.9, 0.04), (-0.44, 0, 0.04, 0.9))):
        p.box("tile_blue", (x, y, 1.0), (w, d, 2.0))
    p.box("clear_glass", (0.44, 0, 1.0), (0.02, 0.88, 1.9))
    p.box("clear_glass", (0, -0.44, 1.0), (0.88, 0.02, 1.9))
    p.cyl("metal_galv", (-0.3, 0.38, 1.9), 0.01, 0.4, n=4, axis="y")
    p.cyl("metal_galv", (-0.3, 0.28, 1.88), 0.07, 0.03, n=8, axis="y")
    return p


@piece("bath", "Mirror")
def mirror():
    p = Prop("GH_Mirror_01")
    p.box("wood_dark", (0, 0, 0.0), (0.5, 0.03, 0.7))
    p.box("glass", (0, -0.016, 0.0), (0.42, 0.01, 0.62))
    return p


@piece("bath", "TowelRail")
def towel_rail():
    p = Prop("GH_TowelRail_01")
    p.box("metal_galv", (0, 0, 0.0), (0.7, 0.04, 0.03))
    for x in (-0.33, 0.33):
        p.box("metal_galv", (x, 0.04, 0.0), (0.03, 0.1, 0.03))
    p.box("fabric_blue", (0, -0.02, -0.18), (0.5, 0.02, 0.36))
    return p


# ===== Soft furnishings (GH-07) ================================================================================
@piece("soft", "Rug")
def rug():
    p = Prop("GH_Rug_01")
    p.box("fabric_red", (0, 0, 0.008), (2.0, 1.4, 0.016))
    p.box("wallpaper", (0, 0, 0.018), (1.7, 1.1, 0.004))
    p.box("fabric_red", (0, 0, 0.02), (1.4, 0.8, 0.004))
    return p


@piece("soft", "Rug_Runner")
def rug_runner():
    p = Prop("GH_Rug_02")                                                           # a hall runner: blue with a cream border, 0.8 x 2.4 m
    p.box("fabric_blue", (0, 0, 0.008), (0.8, 2.4, 0.016))
    p.box("cream", (0, 0, 0.018), (0.68, 2.28, 0.004))
    p.box("fabric_blue", (0, 0, 0.02), (0.5, 2.1, 0.004))
    for y in (-0.8, 0.0, 0.8):
        p.box("fabric_mustard", (0, y, 0.022), (0.3, 0.12, 0.004))
    return p


@piece("soft", "Rug_Round")
def rug_round():
    p = Prop("GH_Rug_03")                                                           # a round braided rug, 1.6 m across
    p.cyl("fabric_green", (0, 0, 0.008), 0.8, 0.016, n=14)
    p.cyl("cream", (0, 0, 0.018), 0.65, 0.004, n=14)
    p.cyl("terracotta", (0, 0, 0.02), 0.5, 0.004, n=14)
    p.cyl("cream", (0, 0, 0.022), 0.2, 0.004, n=14)
    return p


@piece("soft", "Rug_Oval")
def rug_oval():
    p = Prop("GH_Rug_04")                                                           # a big plain living-room carpet in mustard and brown, 2.8 x 1.9 m
    p.box("fabric_brown", (0, 0, 0.008), (2.8, 1.9, 0.016))
    p.box("fabric_mustard", (0, 0, 0.018), (2.5, 1.6, 0.004))
    p.box("fabric_brown", (0, 0, 0.02), (2.2, 1.3, 0.004))
    p.box("fabric_mustard", (0, 0, 0.022), (1.9, 1.0, 0.004))
    return p


@piece("soft", "ToyBox")
def toy_box():
    p = Prop("GH_ToyBox_01")                                                        # a painted wooden toy chest with a few toys over the rim
    p.box("fabric_blue", (0, 0, 0.2), (0.8, 0.45, 0.4))
    p.box("paint_yellow", (0, -0.226, 0.2), (0.3, 0.01, 0.12))                      # a stripe on the front
    p.box("wood_light", (0, 0, 0.42), (0.82, 0.47, 0.04))
    p.box("cloth_red", (-0.2, 0.0, 0.51), (0.14, 0.14, 0.14))                        # a block
    p.box("paint_yellow", (0.1, 0.05, 0.50), (0.12, 0.12, 0.12), rot=(0, 0, 20))
    p.cyl("pink", (0.25, -0.05, 0.51), 0.07, 0.14, n=6)                              # a bucket
    return p


@piece("soft", "CoatRack")
def coat_rack():
    p = Prop("GH_CoatRack_01")                                                      # a standing rack with a coat and a hat
    p.cyl("wood_dark", (0, 0, 0.02), 0.22, 0.04, n=8)
    p.cyl("wood_dark", (0, 0, 0.9), 0.025, 1.76, n=6)
    for k in range(4):
        a = math.radians(45 + k * 90)
        p.box("wood_dark", (0.07 * math.cos(a), 0.07 * math.sin(a), 1.7), (0.14, 0.03, 0.03), rot=(0, 0, math.degrees(a)))
        p.box("wood_dark", (0.12 * math.cos(a), 0.12 * math.sin(a), 1.74), (0.03, 0.03, 0.06))
    p.box("fabric_grey", (0.13, 0.13, 1.37), (0.34, 0.2, 0.74), rot=(0, 0, 135), taper=0.45)    # a coat on the hook at 45 degrees (its top at 1.74), its width across the hook and clear of the pole: narrow at the shoulders
    p.box("fabric_brown", (-0.15, -0.15, 1.78), (0.28, 0.28, 0.04), rot=(0, 0, 45))   # a hat on the opposite hook, its brim clear of the pole
    p.cyl("fabric_brown", (-0.15, -0.15, 1.82), 0.09, 0.08, n=8)
    return p


@piece("kitchen", "JarShelf")
def jar_shelf():
    p = Prop("GH_JarShelf_01")                                                      # a wall shelf unit of preserves: three boards with jars and tins; origin at the mount's centre
    for z in (-0.3, 0.0, 0.3):
        p.box("wood_light", (0, 0.07, z), (0.9, 0.16, 0.025))
    p.box("wood_dark", (-0.44, 0.07, 0.0), (0.025, 0.16, 0.7))
    p.box("wood_dark", (0.44, 0.07, 0.0), (0.025, 0.16, 0.7))
    cols = ["cloth_red", "terracotta", "plant_green", "fabric_mustard", "book_blue", "paint_yellow"]
    for row, z in enumerate((-0.3, 0.0, 0.3)):
        for k in range(6):
            x = -0.36 + k * 0.145
            hgt = 0.14 + 0.03 * ((k + row) % 3)
            p.cyl(cols[(k + row * 2) % len(cols)], (x, 0.07, z + 0.0125 + hgt / 2), 0.045, hgt, n=6)
            p.cyl("metal_galv", (x, 0.07, z + 0.0125 + hgt + 0.008), 0.047, 0.016, n=6)       # the lid
    return p


@piece("soft", "Curtains_Open")
def curtains_open():
    p = Prop("GH_Curtains_Open_01")
    p.cyl("wood_dark", (0, 0, 2.0), 0.015, 1.7, n=4, axis="x")
    for s in (-1, 1):
        for k in range(4):
            p.box("fabric_green", (s * (0.6 + k * 0.05) , 0, 1.0), (0.08, 0.06 + (k % 2) * 0.02, 2.0), taper=1.0)
    return p


@piece("soft", "Curtains_Closed")
def curtains_closed():
    p = Prop("GH_Curtains_Closed_01")
    p.cyl("wood_dark", (0, 0, 2.0), 0.015, 1.7, n=4, axis="x")
    for k in range(14):
        p.box("fabric_green", (-0.78 + k * 0.12, (k % 2) * 0.04, 1.0), (0.12, 0.05, 2.0))
    return p


@piece("soft", "Pillow")
def pillow():
    p = Prop("GH_Pillow_01")
    p.box("linen", (0, 0, 0.07), (0.5, 0.3, 0.14), taper=0.85)
    return p


@piece("soft", "Blanket")
def blanket():
    p = Prop("GH_Blanket_01")
    p.box("fabric_mustard", (0, 0, 0.04), (0.7, 0.5, 0.08))
    p.box("fabric_red", (0, 0, 0.085), (0.7, 0.5, 0.01))
    return p


@piece("soft", "Cushion")
def cushion():
    p = Prop("GH_Cushion_01")
    p.box("fabric_mustard", (0, 0, 0.09), (0.4, 0.4, 0.14), taper=0.8, rot=(0, 0, 0))
    return p


# ===== Heating and utilities (GH-09) ===========================================================================
@piece("utilities", "Fireplace")
def fireplace():
    p = Prop("GH_Fireplace_01")
    p.box("brick", (0, 0.1, 1.0), (1.8, 0.5, 2.0))
    p.box("black", (0, -0.16, 0.5), (0.9, 0.04, 0.8))                                       # the firebox opening
    p.box("wood_dark", (0, -0.2, 1.1), (2.0, 0.34, 0.1))                                    # mantel
    p.box("concrete", (0, -0.4, 0.04), (1.6, 0.6, 0.08))                                    # hearth
    p.box("rust_dark", (-0.2, -0.1, 0.12), (0.5, 0.06, 0.06), rot=(0, 0, 20))               # logs
    p.box("rust_dark", (0.1, -0.1, 0.14), (0.5, 0.06, 0.06), rot=(0, 0, -15))
    p.box("glow_cyan", (0, -0.1, 0.28), (0.3, 0.05, 0.16), taper=0.3)
    p.box("brick", (0, 0.2, 2.6), (0.8, 0.5, 1.2))
    return p


@piece("utilities", "WoodStove")
def wood_stove():
    p = Prop("GH_WoodStove_01")
    p.box("black", (0, 0, 0.45), (0.55, 0.45, 0.6))
    p.box("metal_dark", (0, -0.231, 0.45), (0.28, 0.01, 0.3))
    p.box("glow_cyan", (0, -0.238, 0.45), (0.2, 0.005, 0.18))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("black", (sx * 0.22, sy * 0.17, 0.08), (0.05, 0.05, 0.16))
    p.cyl("black", (0, 0.1, 1.2), 0.07, 1.2, n=6)
    return p


def pipe_to_wall(p, x, y0, z_from, z_to, y_wall, r=0.025):
    """A copper pipe from the top of a tank straight up to z_to, then back (+Y) to the wall at y_wall and into a round flange there, so the pipe
    ends in the wall, not in the air. Everything is built so that the pipe's last face is the model's back: placed against a wall, the flange touches it."""
    p.cyl("copper", (x, y0, (z_from + z_to) / 2), r, z_to - z_from, n=6)                            # up
    p.box("copper", (x, y0, z_to), (2 * r, 2 * r, 2 * r))                                           # the elbow
    p.cyl("copper", (x, (y0 + y_wall) / 2, z_to), r, y_wall - y0, n=6, axis="y")                   # back
    p.cyl("metal_galv", (x, y_wall - 0.006, z_to), r * 2.2, 0.012, n=8, axis="y")                  # the escutcheon plate on the wall


@piece("utilities", "Boiler")
def boiler():
    p = Prop("GH_Boiler_01")
    p.cyl("enamel_cream", (0, 0, 0.7), 0.35, 1.4, n=10)
    p.cyl("metal_dark", (0, 0, 1.42), 0.36, 0.04, n=10)
    pipe_to_wall(p, 0.15, 0.1, 1.44, 1.85, 0.42, r=0.035)                                           # the flow pipe: up, then back into the wall
    pipe_to_wall(p, -0.12, 0.1, 1.44, 1.65, 0.42, r=0.03)                                           # the return
    p.box("metal_dark", (0, -0.34, 0.9), (0.16, 0.04, 0.2))
    return p


@piece("utilities", "WaterHeater")
def water_heater():
    p = Prop("GH_WaterHeater_01")
    p.cyl("enamel_white", (0, 0, 0.6), 0.26, 1.2, n=10)
    p.box("black", (0, -0.26, 0.3), (0.14, 0.03, 0.1))
    pipe_to_wall(p, -0.1, 0.0, 1.2, 1.5, 0.33)                                                      # cold in
    pipe_to_wall(p, 0.1, 0.0, 1.2, 1.35, 0.33)                                                      # hot out
    return p


@piece("utilities", "FuseBox")
def fuse_box():
    p = Prop("GH_FuseBox_01")
    p.box("metal_dark", (0, 0, 0.0), (0.4, 0.1, 0.5))
    p.box("fabric_grey", (0, -0.055, 0.0), (0.34, 0.01, 0.44))
    for k in range(6):
        p.box("black", (-0.1 + (k % 2) * 0.2, -0.065, 0.14 - (k // 2) * 0.1), (0.07, 0.01, 0.05))
    p.box("cloth_red", (0.1, -0.066, -0.18), (0.08, 0.012, 0.05))
    return p


@piece("utilities", "Radiator")
def radiator():
    p = Prop("GH_Radiator_01")
    for k in range(10):
        p.box("enamel_white", (-0.45 + k * 0.1, 0, 0.35), (0.08, 0.1, 0.6))
    p.box("enamel_white", (0, 0, 0.66), (1.0, 0.1, 0.04))
    p.box("enamel_white", (0, 0, 0.1), (1.0, 0.1, 0.04))
    return p


@piece("utilities", "AirConditioner")
def air_conditioner():
    p = Prop("GH_AirConditioner_01")
    p.box("enamel_cream", (0, 0, 0.0), (0.6, 0.45, 0.4))
    for k in range(5):
        p.box("metal_dark", (0, -0.226, -0.12 + k * 0.06), (0.5, 0.005, 0.025))
    p.box("fabric_grey", (0, -0.23, 0.14), (0.4, 0.005, 0.07))
    return p


# ===== Office and lab (GH-10) ==================================================================================
@piece("office", "Whiteboard")
def whiteboard():
    p = Prop("GH_Whiteboard_01")
    p.box("metal_galv", (0, 0, 1.4), (1.5, 0.04, 1.0))
    p.box("enamel_white", (0, -0.025, 1.4), (1.44, 0.01, 0.94))
    p.box("metal_galv", (0, -0.05, 0.9), (1.5, 0.08, 0.03))
    for s in (-1, 1):
        p.box("metal_dark", (s * 0.7, 0.18, 0.45), (0.04, 0.5, 0.9))
        p.box("metal_dark", (s * 0.7, 0.0, 0.04), (0.04, 0.5, 0.08))
    return p


@piece("office", "LabBench")
def lab_bench():
    p = Prop("GH_LabBench_01")
    p.box("metal_dark", (0, 0, 0.45), (2.0, 0.8, 0.9))
    p.box("fabric_grey", (0, 0, 0.92), (2.04, 0.84, 0.05))
    for x in (-0.5, 0.5):
        p.box("metal_galv", (x, -0.405, 0.5), (0.8, 0.02, 0.7))
    p.cyl("metal_galv", (0.7, 0.2, 1.1), 0.02, 0.4, n=5)
    return p


@piece("office", "ServerRack")
def server_rack():
    p = Prop("GH_ServerRack_01")
    p.box("black", (0, 0, 1.0), (0.6, 0.8, 2.0))
    for k in range(10):
        p.box("metal_dark", (0, -0.405, 0.2 + k * 0.18), (0.52, 0.02, 0.15))
        p.box("glow_cyan", (0.2, -0.42, 0.2 + k * 0.18), (0.03, 0.01, 0.03))
    return p


@piece("office", "Microscope")
def microscope():
    p = Prop("GH_Microscope_01")
    p.box("black", (0, 0, 0.02), (0.18, 0.24, 0.04))
    p.box("black", (0, 0.08, 0.18), (0.05, 0.05, 0.3))
    p.cyl("metal_galv", (0, -0.02, 0.28), 0.025, 0.22, n=6, rot=(35, 0, 0))
    p.box("metal_galv", (0, -0.02, 0.1), (0.1, 0.1, 0.01))
    return p


# ===== Food service (GH-11) ====================================================================================
def _front_outline(r, z_arc, z_low, y, n=8):
    """The outline of an arched front: a half circle of radius r about (0, z_arc) from the right round to the left, then down to z_low. Points at depth y."""
    pts = [(r * math.cos(math.pi * k / n), y, z_arc + r * math.sin(math.pi * k / n)) for k in range(n + 1)]
    if z_low < z_arc:
        pts += [(-r, y, z_low), (r, y, z_low)]
    return pts


def _slab(p, colour, r, z_arc, z_low, y_front, y_back):
    """A flat arched slab (the outline of _front_outline) between depths y_front and y_back."""
    p.loft_rings(colour, [_front_outline(r, z_arc, z_low, y_front), _front_outline(r, z_arc, z_low, y_back)])


def _disc(p, colour, r, cx, cz, y_front, y_back, n=16):
    """A round disc facing -Y (a true circle: Prop.cyl's y axis rings are rounded squares), between depths y_front and y_back."""
    ring = [(cx + r * math.cos(2 * math.pi * k / n), 0.0, cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    p.loft_rings(colour, [[(x, y_front, z) for x, _, z in ring], [(x, y_back, z) for x, _, z in ring]])


@piece("service", "Jukebox")
def jukebox():
    """A 1940s arched-top floor jukebox (a generic design, not a copy of any maker's): lit arch and pilasters with bubble tubes, a window
    showing the record, a slanted selection strip, a speaker grille, a coin entry. Brief and parts table: docs/assets/briefs/service-appliances.md."""
    p = Prop("GH_Jukebox_01")
    w, d, plinth_h, arch_z = 0.84, 0.62, 0.06, 1.10
    yf = -d / 2
    sink = 0.002
    r_arch = (w - 0.04) / 2                                                            # the arch is as wide as the cabinet
    p.box("black", (0, 0, plinth_h / 2), (w, d, plinth_h))                              # plinth
    p.box("wood_dark", (0, 0, (plinth_h + arch_z) / 2), (w - 0.04, d, arch_z - plinth_h))  # cabinet, on the plinth
    _slab(p, "wood_dark", r_arch, arch_z, arch_z, yf, -yf)                             # the arched top, on the cabinet

    # the light: a band round the arch and down both sides as pilasters, 2.5 cm proud of the front, with bubble tubes
    band_r, band_w, band_d = 0.345, 0.07, 0.027
    band_y = yf - band_d / 2 + sink
    n_seg = 10
    for k in range(n_seg):
        a = math.pi * (k + 0.5) / n_seg
        length = 2 * band_r * math.sin(math.pi / n_seg / 2) + 0.012                     # each segment overlaps the next
        p.box("glow_amber", (band_r * math.cos(a), band_y, arch_z + band_r * math.sin(a)), (length, band_d, band_w), rot=(0, 90 - math.degrees(a), 0))
    for sx in (-1, 1):
        p.box("glow_amber", (sx * band_r, band_y, (plinth_h + arch_z) / 2), (band_w, band_d, arch_z - plinth_h))
        for z in (0.3, 0.6, 0.85):
            p.box("glow_red", (sx * band_r, band_y - 0.002, z), (band_w - 0.004, band_d + 0.004, 0.02))   # a bubble tube, 4 mm prouder

    # the window in the arch: a dark backing, the record with its label and the tone arm, the glass in front with its edge in the band
    win_r, win_low = band_r - band_w / 2, 0.98
    back_front = yf - 0.006
    _slab(p, "metal_dark", win_r + 0.01, arch_z, win_low, back_front, yf + sink)       # its edge inside the band, like the glass's
    rec_z, rec_t = 1.17, 0.008
    rec_front = back_front - rec_t + sink
    _disc(p, "black", 0.13, 0, rec_z, rec_front, back_front + sink)
    _disc(p, "cloth_red", 0.04, 0, rec_z, rec_front - 0.0035, rec_front + 0.0005, n=10)
    tip, pivot = (0.1, rec_z - 0.05), (0.17, rec_z + 0.1)                                # the tone arm: from its pivot at the upper right down onto the record
    arm = math.hypot(pivot[0] - tip[0], pivot[1] - tip[1])
    p.box("metal_galv", ((tip[0] + pivot[0]) / 2, rec_front - 0.0005, (tip[1] + pivot[1]) / 2), (0.016, 0.002, arm),
          rot=(0, math.degrees(math.atan2(pivot[0] - tip[0], pivot[1] - tip[1])), 0))
    _disc(p, "metal_galv", 0.012, pivot[0], pivot[1], rec_front - 0.001, back_front + sink, n=8)   # the arm's pivot post, from the backing
    glass_back = rec_front - 0.004 + 0.0015                                             # touches the label
    _slab(p, "clear_glass", win_r + 0.01, arch_z, win_low, glass_back - 0.008, glass_back)

    # the selection strip under the window, tilted towards the player: title cards and a row of buttons on its face
    strip, tilt, strip_t = (0, yf - 0.005, 0.95), 30, 0.05
    p.box("metal_galv", strip, (0.6, 0.1, strip_t), rot=(tilt, 0, 0))

    def on_strip(x, ly, lz):
        """A point x across, ly along and lz above the middle of the tilted strip."""
        c, sn = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        return (x, strip[1] + ly * c - lz * sn, strip[2] + ly * sn + lz * c)
    p.box("label_white", on_strip(0, 0.0, strip_t / 2 + 0.002 - sink / 4), (0.54, 0.05, 0.004), rot=(tilt, 0, 0))
    for k in range(10):
        p.box("black", on_strip(-0.27 + 0.06 * k, -0.033, strip_t / 2 + 0.006 - sink), (0.03, 0.015, 0.012), rot=(tilt, 0, 0))

    # the speaker grille: cloth behind chrome bars; the coin entry above it
    cloth_t, cloth_lo, cloth_hi = 0.008, 0.18, 0.70
    p.box("fabric_mustard", (0, yf - cloth_t / 2 + sink, (cloth_lo + cloth_hi) / 2), (0.6, cloth_t, cloth_hi - cloth_lo))
    cloth_front = yf - cloth_t + sink
    for k in range(7):
        p.box("metal_galv", (0, cloth_front - 0.007 + sink, cloth_lo + 0.04 + k * (cloth_hi - cloth_lo - 0.08) / 6), (0.58, 0.014, 0.02))
    plate_t = 0.012
    p.box("metal_galv", (0.2, yf - plate_t / 2 + sink, 0.8), (0.08, plate_t, 0.12))
    p.box("black", (0.2, yf - plate_t + sink - 0.002 + 0.0005, 0.82), (0.006, 0.004, 0.04))
    return p


# ===== Arcade machines (brief: docs/assets/briefs/service-appliances.md) ======================================
SINK = 0.002          # m: a part fixed on a face sinks this far into it


def _prism_x(p, colour, profile, x0, x1):
    """A prism across x0..x1 of a convex (y, z) profile: a cabinet's side outline extruded across its width."""
    p.loft_rings(colour, [[(x0, y, z) for y, z in profile], [(x1, y, z) for y, z in profile]])


def _tilted(centre, tilt, x, ly, lz):
    """A point x across, ly along and lz out from the middle of a face tilted `tilt` degrees about X (+ lowers its -Y end)."""
    c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    return (x, centre[1] + ly * c - lz * s, centre[2] + ly * s + lz * c)


SCREEN_BLOCKS = [                                                              # an abstract maze game: walls, dots, a player, a chaser
    (-0.12, 0.10, 0.12, 0.012, "glow_cyan"), (0.12, 0.10, 0.12, 0.012, "glow_cyan"), (0.0, -0.02, 0.28, 0.012, "glow_cyan"),
    (-0.17, -0.07, 0.012, 0.10, "glow_cyan"), (0.17, -0.07, 0.012, 0.10, "glow_cyan"), (0.0, -0.13, 0.16, 0.012, "glow_cyan"),
    (-0.07, 0.05, 0.012, 0.012, "glow_amber"), (0.0, 0.05, 0.012, 0.012, "glow_amber"), (0.07, 0.05, 0.012, 0.012, "glow_amber"),
    (0.05, -0.07, 0.03, 0.03, "glow_amber"), (-0.08, -0.07, 0.03, 0.03, "glow_red"),
]


def _joystick(p, base):
    """A ball-top joystick standing on the point `base`."""
    p.cyl("metal_galv", (base[0], base[1], base[2] + 0.03 - SINK), 0.008, 0.06, n=6)
    props_lib.ball(p, "black", (base[0], base[1], base[2] + 0.06 - SINK), 0.02, n=8, rings=3)


def _coin_door(p, x, y_face, z, w=0.26, h=0.3):
    """A coin door on a front face at y = y_face, with two lit coin slots."""
    t = 0.012
    p.box("metal_dark", (x, y_face - t / 2 + SINK, z), (w, t, h))
    for dx in (-0.06, 0.06):
        p.box("glow_red", (x + dx, y_face - t + SINK - 0.001, z + h * 0.2), (0.03, 0.004, 0.05))


def _upright_screen(p, w, foot, head):
    """The bezel, screen and lit blocks on the sloping face from foot (y, z) up to head (y, z)."""
    tilt = -math.degrees(math.atan2(head[0] - foot[0], head[1] - foot[1]))      # the face leans back: its top is further +Y
    mid = (0, (foot[0] + head[0]) / 2, (foot[1] + head[1]) / 2)
    p.box("metal_dark", _tilted(mid, tilt, 0, -(0.004 - SINK), 0.0), (w - 0.08, 0.008, 0.52), rot=(tilt, 0, 0))       # bezel
    p.box("screen", _tilted(mid, tilt, 0, -(0.007 - SINK), 0.02), (0.44, 0.006, 0.36), rot=(tilt, 0, 0))
    pix = 0.008 + 0.002 - SINK / 2                                               # the blocks' middle: 1 mm into the screen's face

    def at(x, t):
        return _tilted(mid, tilt, x, -pix, 0.02 + t)
    for x, t, bw, bh, colour in SCREEN_BLOCKS:
        p.box(colour, at(x, t), (bw, 0.004, bh), rot=(tilt, 0, 0))


@piece("service", "ArcadeUpright")
def arcade_upright():
    """A one-player upright video arcade cabinet (generic, no game's art): the side profile with the control panel at the waist, the screen
    leaning back above it, a lit marquee overhanging the top; side art; a coin door. 0.66 x 0.84 x 1.75 m (0.64 wide without the side art, 0.72 deep without the control panel)."""
    p = Prop("GH_ArcadeUpright_01")
    w, y_front, y_back, base_h = 0.64, -0.30, 0.42, 0.86
    foot, head = (y_front, base_h), (-0.14, 1.50)                                # the sloping screen face
    marquee_y, top = -0.24, 1.75
    p.box("black", (0, (y_front + y_back) / 2, base_h / 2), (w, y_back - y_front, base_h))
    _prism_x(p, "black", [foot, (y_back, base_h), (y_back, head[1]), head], -w / 2, w / 2)
    p.box("black", (0, (marquee_y + y_back) / 2, (head[1] + top) / 2), (w, y_back - marquee_y, top - head[1]))
    p.box("glow_amber", (0, marquee_y - 0.006 + SINK, (head[1] + top) / 2), (w - 0.06, 0.012, 0.17))           # the lit marquee
    _upright_screen(p, w, foot, head)
    tilt, panel = 12, (0, -0.33, 0.877)                                         # the control panel, leaning towards the player; its underside meets the base's front edge
    p.box("cloth_red", panel, (w - 0.004, 0.18, 0.05), rot=(tilt, 0, 0))
    _joystick(p, _tilted(panel, tilt, -0.15, -0.01, 0.025))
    for k in range(3):
        p.cyl("label_blue", _tilted(panel, tilt, 0.02 + 0.07 * k, -0.01, 0.025 + 0.006 - SINK), 0.016, 0.012, n=8, rot=(tilt, 0, 0))
    _coin_door(p, 0, y_front, 0.45)
    for sx in (-1, 1):                                                          # side art: a blue panel with a red stripe across it
        p.box("label_blue", (sx * (w / 2 + 0.003 - SINK), 0.1, 0.5), (0.006, 0.5, 0.6))
        p.box("cloth_red", (sx * (w / 2 + 0.003 + 0.004 - SINK), 0.1, 0.5), (0.006, 0.06, 0.5), rot=(30, 0, 0))
    return p


@piece("service", "ArcadeCocktail")
def arcade_cocktail():
    """A sit-down cocktail-table arcade game: a black box with the screen facing up under a glass top, a control panel at each short end
    (the two players face each other across it), a coin door on the front. 0.92 x 0.53 x 0.75 m at the glass, 0.83 m to the joystick tops."""
    p = Prop("GH_ArcadeCocktail_01")
    w, d, h = 0.7, 0.5, 0.74
    p.box("black", (0, 0, h / 2), (w, d, h))
    p.box("screen", (0, 0, h + 0.001), (0.4, 0.3, 0.004))                       # 1 mm into the top, under the glass
    for x, t, bw, bh, colour in SCREEN_BLOCKS:                                  # the blocks lie flat on the screen: depth along y
        p.box(colour, (x, t * 0.8, h + 0.0035), (bw, bh, 0.002))
    p.box("clear_glass", (0, 0, h + 0.004), (w + 0.04, d + 0.03, 0.012))        # the glass top, its underside 2 mm below the cabinet's top
    for sx in (-1, 1):
        cx = sx * (w / 2 + 0.06 - 0.01)                                         # the panels: 1 cm into the cabinet's ends
        panel_top = h + 0.012                                                   # the controls are at the table's top, 2 mm above the glass's edge in them
        p.box("cloth_red", (cx, 0, panel_top - 0.025), (0.12, 0.3, 0.05))
        _joystick(p, (cx + sx * 0.02, -0.07, panel_top))
        for dy in (0.04, 0.1):
            p.cyl("label_blue", (cx, dy, panel_top + 0.006 - SINK), 0.016, 0.012, n=8)
    _coin_door(p, 0, -d / 2, 0.35, w=0.2, h=0.24)
    return p


def _pinball_legs(p, centre, tilt, length, height):
    """Four chrome legs from the floor up into the tilted cabinet's underside (the front ones shorter)."""
    c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    for ly in (-length / 2 + 0.08, length / 2 - 0.12):
        y = centre[1] + ly * c + height / 2 * s
        z = centre[2] + ly * s - height / 2 * c + 0.02                             # 2 cm into the cabinet
        for x in (-0.3, 0.3):
            p.box("metal_galv", (x, y, z / 2), (0.05, 0.05, z))


def _playfield(p, centre, tilt, height, field_end):
    """The playfield under glass on the tilted top, from the front up to `field_end` (along the cabinet, where the backbox stands): a blue
    field with bumpers, lanes and flippers, the glass on two side rails, its far end 2 cm into the backbox."""
    top = height / 2
    field_start = -0.53
    p.box("label_blue", _tilted(centre, tilt, 0, (field_start + field_end) / 2, top + 0.003 - SINK), (0.62, field_end - field_start, 0.006), rot=(tilt, 0, 0))
    art = top + 0.004 + 0.002 - SINK / 2                                        # the decals, 1 mm into the field
    for x, ly in ((-0.12, 0.15), (0.12, 0.15), (0.0, 0.26)):
        p.cyl("cloth_red", _tilted(centre, tilt, x, ly, art), 0.045, 0.004, n=10, rot=(tilt, 0, 0))
    for x in (-0.12, 0.0, 0.12):
        p.box("paint_yellow", _tilted(centre, tilt, x, 0.37, art), (0.02, 0.1, 0.004), rot=(tilt, 0, 0))
    for sx in (-1, 1):
        p.box("paint_white", _tilted(centre, tilt, sx * 0.08, -0.42, art), (0.1, 0.025, 0.004), rot=(tilt, 0, 0))
        p.box("paint_yellow", _tilted(centre, tilt, sx * 0.2, -0.3, art), (0.04, 0.14, 0.004), rot=(tilt, 0, 0))
        p.box("metal_galv", _tilted(centre, tilt, sx * 0.333, 0, top + 0.015 - SINK), (0.03, 1.296, 0.03), rot=(tilt, 0, 0))   # inside the cabinet's sides and ends
    glass_start, glass_end = -0.61, field_end + 0.02
    p.box("clear_glass", _tilted(centre, tilt, 0, (glass_start + glass_end) / 2, top + 0.013), (0.66, glass_end - glass_start, 0.008), rot=(tilt, 0, 0))


def _backbox(p, w, y0, y1, z0, z1):
    """The pinball's upright backbox: a lit backglass with blocks of art, a speaker panel below it."""
    p.box("black", (0, (y0 + y1) / 2, (z0 + z1) / 2), (w, y1 - y0, z1 - z0))
    face = y0 - 0.006 + SINK
    p.box("glow_amber", (0, face, z1 - 0.28), (w - 0.08, 0.012, 0.4))
    art = y0 - 0.012 + SINK - 0.001
    for x, dz, bw, bh, colour in ((-0.15, 0.06, 0.16, 0.16, "cloth_red"), (0.12, 0.02, 0.2, 0.08, "label_blue"), (0.0, -0.1, 0.36, 0.04, "glow_cyan")):
        p.box(colour, (x, art, z1 - 0.28 + dz), (bw, 0.004, bh))
    p.box("metal_dark", (0, face, z1 - 0.62), (w - 0.08, 0.012, 0.2))
    for k in range(4):
        p.box("black", (0, art, z1 - 0.69 + k * 0.045), (w - 0.16, 0.004, 0.015))


@piece("service", "Pinball")
def pinball():
    """A pinball machine (generic): a long cabinet sloping down towards the player on four chrome legs, the playfield under glass, a tall lit
    backbox at the far end, a coin door, flipper buttons on the sides and a plunger at the front right. 0.73 x 1.40 x 1.93 m with the plunger."""
    p = Prop("GH_Pinball_01")
    w, length, height, tilt = 0.7, 1.3, 0.3, 6.5
    centre = (0, -0.06, 0.85)
    p.box("black", centre, (w, length, height), rot=(tilt, 0, 0))
    _pinball_legs(p, centre, tilt, length, height)
    box_front, box_back = 0.37, 0.6
    c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    field_end = (box_front - centre[1] + height / 2 * s) / c                      # along the cabinet, where the backbox's front meets the top
    _playfield(p, centre, tilt, height, field_end)
    _backbox(p, w, box_front, box_back, 1.0, 1.93)
    front = -length / 2                                                         # the front face, across the cabinet's length
    p.box("metal_dark", _tilted(centre, tilt, 0, front - 0.006 + SINK, -0.03), (0.3, 0.012, 0.16), rot=(tilt, 0, 0))
    for dx in (-0.06, 0.06):
        p.box("glow_red", _tilted(centre, tilt, dx, front - 0.012 + SINK - 0.001, 0.0), (0.03, 0.004, 0.05), rot=(tilt, 0, 0))
    p.cyl("metal_galv", _tilted(centre, tilt, 0.27, front - 0.03 + SINK, 0.08), 0.008, 0.06, n=6, axis="y", rot=(tilt, 0, 0))   # plunger rod
    p.cyl("black", _tilted(centre, tilt, 0.27, front - 0.06 - 0.012 + 2 * SINK, 0.08), 0.02, 0.024, n=8, axis="y", rot=(tilt, 0, 0))  # and knob
    for sx in (-1, 1):
        p.cyl("label_white", _tilted(centre, tilt, sx * (w / 2 + 0.008 - SINK), front + 0.12, 0.06), 0.015, 0.016, n=8, axis="x", rot=(tilt, 0, 0))
    return p


@piece("service", "VendingMachine")
def vending_machine():
    p = Prop("GH_VendingMachine_01")
    p.box("cloth_red", (0, 0, 0.95), (0.85, 0.8, 1.9))
    p.box("glass", (-0.1, -0.405, 1.1), (0.55, 0.01, 1.2))
    p.box("glow_cyan", (-0.1, -0.41, 1.1), (0.5, 0.005, 1.1))
    p.box("black", (0.3, -0.405, 0.8), (0.18, 0.01, 0.5))
    p.box("black", (-0.1, -0.405, 0.2), (0.5, 0.01, 0.2))
    return p


@piece("service", "CoffeeMachine")
def coffee_machine():
    p = Prop("GH_CoffeeMachine_01")
    p.box("black", (0, 0, 0.18), (0.3, 0.3, 0.36))
    p.box("metal_dark", (0, -0.0, 0.4), (0.3, 0.3, 0.06))
    p.box("clear_glass", (0, -0.12, 0.12), (0.14, 0.14, 0.18))
    p.box("fabric_grey", (0, 0.15, 0.2), (0.2, 0.01, 0.3))
    return p


@piece("service", "Cooler")
def cooler():
    p = Prop("GH_Cooler_01")
    p.box("truck_blue", (0, 0, 0.2), (0.7, 0.4, 0.4))
    p.box("paint_white", (0, 0, 0.42), (0.72, 0.42, 0.06))
    for sx in (-1, 1):
        p.box("metal_dark", (sx * 0.38, 0, 0.3), (0.04, 0.12, 0.04))
    return p


def run():
    names = globals().get("HOUSEHOLD_LIST")
    chosen = [k for k, (fn, g) in PIECES.items() if not names or k in names or g in names]
    x, row, y = 0.0, None, 0.0
    for key in chosen:
        fn, group = PIECES[key]
        if group != row:
            row, x, y = group, 0.0, y + 4.0 if row is not None else 0.0
        prop = fn()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Household/{prop.name}.fbx")
        obj.location = (x, y, 0)
        x += max(0.7, obj.dimensions.x + 0.4)
    props_lib.write_interactions()
    print("household done", len(chosen))


if __name__ == "__main__":
    run()
