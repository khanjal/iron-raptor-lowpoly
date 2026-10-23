"""Home decoration in several styles: Modern, Retro and Damaged (for the trailer park and abandoned houses).

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/home_styles.py", run_name="__main__")
Optional globals: THEME_LIST (default all three), STYLE_PIECES (piece names to limit the run). Exports
Assets/Art/Global/<Household|Decor>/<Theme>/<name with the theme>.fbx, for example
Assets/Art/Global/Household/Modern/GH_Sofa_Modern_01.fbx.

Every piece in household.py and decor.py gets all three treatments:

1. A colour theme. THEMES remaps the palette swatches a piece uses (Modern: white, grey, black, light oak and steel; Retro: orange,
   avocado, mustard, teak and chrome; Damaged: the same wood and fabric gone grey, rusted, stained). No new geometry.
2. For the hero pieces a bespoke variant with a different shape (a slab sofa on steel legs vs a tufted one on tapered wooden legs;
   a steel two-door fridge vs a rounded cream one; a sunburst clock vs a minimalist ring). VARIANTS below.
3. For Damaged, props_lib's damage(): small parts go missing, the piece sags and tilts, grime patches appear; plus bespoke wrecks for
   the pieces where it matters (a slashed sofa spilling stuffing, a smashed CRT, a rusty fridge with its door hanging, an overturned
   table, a tipped bookcase with books spilled).

Add a bespoke variant with @variant("Sofa", "Modern") on a function that returns a Prop named GH_Sofa_Modern_01.
"""

import importlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
import household
import decor
for _m in (common, props_lib, household, decor):
    importlib.reload(_m)
Prop = props_lib.Prop

THEMES = {
    "Modern": {
        "wood_dark": "black", "fabric_brown": "black", "fabric_blue": "fabric_grey", "fabric_green": "fabric_grey",
        "fabric_mustard": "paint_white", "fabric_red": "fabric_grey", "fabric_pink": "paint_white", "cloth_red": "black",
        "linen": "paint_white", "wallpaper": "paint_white", "enamel_cream": "metal_galv", "enamel_white": "metal_galv",
        "lamp_shade": "paint_white", "metal_dark": "black", "tractor_green": "metal_dark", "truck_blue": "fabric_grey",
        "brick": "concrete", "rust_dark": "black", "copper": "metal_galv", "terracotta": "paint_white", "teddy": "fabric_grey",
        "book_red": "black", "book_blue": "fabric_grey", "book_green": "paint_white", "plant_green": "plant_green",
    },
    "Retro": {
        "wood_light": "fabric_brown", "wood_dark": "rust_dark", "fabric_blue": "orange_cat", "fabric_green": "tractor_green",
        "fabric_grey": "fabric_mustard", "fabric_red": "orange_cat", "fabric_pink": "fabric_mustard", "cloth_red": "orange_cat",
        "enamel_white": "enamel_cream", "paint_white": "cream", "lamp_shade": "paint_yellow", "linen": "cream",
        "wallpaper": "fabric_mustard", "tile_blue": "tile_green", "metal_dark": "fabric_brown", "concrete": "wallpaper",
        "paint_yellow": "orange_cat", "book_blue": "tractor_green", "book_green": "orange_cat", "porcelain": "enamel_cream",
    },
    "Damaged": {
        "wood_light": "wood_grey", "wood_dark": "rust_dark", "fabric_blue": "fabric_grey", "fabric_green": "fabric_brown",
        "fabric_red": "fabric_brown", "fabric_mustard": "fabric_brown", "fabric_pink": "fabric_grey", "fabric_grey": "dead_wood",
        "paint_white": "concrete", "enamel_white": "enamel_cream", "enamel_cream": "wood_grey", "metal_galv": "rust",
        "metal_dark": "rust_dark", "linen": "fabric_grey", "wallpaper": "wood_grey", "lamp_shade": "wood_grey", "cloth_red": "rust_dark",
        "plant_green": "dead_wood", "leaf_dark": "dead_wood", "terracotta": "rust_dark", "porcelain": "enamel_cream", "glass": "glass",
        "paint_yellow": "wood_grey", "tile_blue": "dead_wood", "teddy": "wood_grey", "book_red": "rust_dark", "book_blue": "wood_grey",
        "book_green": "dead_wood", "cream": "wood_grey", "tractor_green": "dead_wood", "truck_blue": "fabric_grey",
    },
}

VARIANTS = {}


def variant(name, theme):
    def deco(fn):
        VARIANTS[(name, theme)] = fn
        return fn
    return deco


def _legs(p, colour, w, d, h, t=0.04, inset=0.04, splay=0.0, cx=0.0, cy=0.0):
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box(colour, (cx + sx * (w / 2 - inset), cy + sy * (d / 2 - inset), h / 2), (t, t, h), rot=(sy * splay, -sx * splay, 0))


# ===== Modern ==================================================================================================
@variant("Sofa", "Modern")
def sofa_modern():
    p = Prop("GH_Sofa_Modern_01")
    p.box("fabric_grey", (0, 0, 0.28), (2.2, 0.95, 0.22))
    for x in (-0.55, 0.55):
        p.box("paint_white", (x, -0.05, 0.47), (1.0, 0.78, 0.18))
        p.box("fabric_grey", (x, 0.36, 0.62), (1.0, 0.14, 0.42), rot=(-8, 0, 0))
    p.box("fabric_grey", (-1.12, 0, 0.45), (0.12, 0.95, 0.4))
    p.box("fabric_grey", (1.12, 0, 0.45), (0.12, 0.95, 0.4))
    _legs(p, "black", 2.2, 0.95, 0.17, 0.04, 0.12)
    return p


@variant("Armchair", "Modern")
def armchair_modern():
    p = Prop("GH_Armchair_Modern_01")
    p.box("fabric_grey", (0, 0, 0.3), (0.85, 0.85, 0.24))
    p.box("paint_white", (0, -0.04, 0.5), (0.7, 0.7, 0.16))
    p.box("fabric_grey", (0, 0.36, 0.65), (0.85, 0.14, 0.5), rot=(-12, 0, 0))
    for s in (-1, 1):
        p.box("fabric_grey", (s * 0.4, 0, 0.5), (0.08, 0.8, 0.3))
    _legs(p, "black", 0.85, 0.85, 0.18, 0.035, 0.1, splay=6)
    return p


@variant("Chair_Kitchen", "Modern")
def chair_kitchen_modern():
    p = Prop("GH_Chair_Kitchen_Modern_01")
    p.box("paint_white", (0, 0, 0.46), (0.45, 0.44, 0.05))
    p.box("paint_white", (0, 0.2, 0.7), (0.44, 0.05, 0.4), rot=(-10, 0, 0))
    p.box("paint_white", (0, 0.18, 0.5), (0.1, 0.05, 0.12))
    _legs(p, "metal_galv", 0.45, 0.42, 0.45, 0.025, 0.04, splay=8)
    return p


@variant("Chair_Dining", "Modern")
def chair_dining_modern():
    p = Prop("GH_Chair_Dining_Modern_01")
    p.box("fabric_grey", (0, 0, 0.47), (0.46, 0.46, 0.08))
    p.box("fabric_grey", (0, 0.21, 0.75), (0.44, 0.06, 0.5), rot=(-8, 0, 0))
    _legs(p, "black", 0.46, 0.46, 0.45, 0.03, 0.04)
    return p


@variant("Table_Dining", "Modern")
def table_dining_modern():
    p = Prop("GH_Table_Dining_Modern_01")
    p.box("wood_light", (0, 0, 0.74), (1.9, 0.95, 0.05))
    for s in (-1, 1):
        p.box("black", (s * 0.8, 0, 0.36), (0.06, 0.8, 0.72))
        p.box("black", (s * 0.8, 0, 0.02), (0.08, 0.7, 0.04))
    p.box("black", (0, 0, 0.5), (1.6, 0.04, 0.04))
    return p


@variant("Table_Coffee", "Modern")
def table_coffee_modern():
    p = Prop("GH_Table_Coffee_Modern_01")
    p.box("glass", (0, 0, 0.42), (1.1, 0.6, 0.03))
    p.box("black", (0, 0, 0.2), (1.0, 0.5, 0.03))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("black", (sx * 0.5, sy * 0.25, 0.21), (0.03, 0.03, 0.42))
    return p


@variant("Desk_Wood", "Modern")
def desk_modern():
    p = Prop("GH_Desk_Modern_01")
    p.box("wood_light", (0, 0, 0.74), (1.5, 0.7, 0.04))
    for s in (-1, 1):
        p.box("black", (s * 0.7, 0, 0.36), (0.05, 0.6, 0.72))
        p.box("black", (s * 0.7, 0, 0.02), (0.07, 0.65, 0.04))
    p.box("paint_white", (0.45, 0, 0.55), (0.45, 0.5, 0.35))                  # a drawer unit
    p.box("black", (0.45, -0.26, 0.55), (0.1, 0.02, 0.02))
    return p


@variant("Bed_Double", "Modern")
def bed_double_modern():
    p = Prop("GH_Bed_Double_Modern_01")
    p.box("black", (0, 0, 0.14), (1.7, 2.1, 0.28))
    p.box("paint_white", (0, 0, 0.36), (1.6, 1.95, 0.2))
    p.box("fabric_grey", (0, -0.3, 0.48), (1.62, 1.3, 0.05))
    for x in (-0.38, 0.38):
        p.box("paint_white", (x, 0.82, 0.52), (0.62, 0.34, 0.12))
    p.box("fabric_grey", (0, 1.07, 0.7), (1.76, 0.1, 0.9))
    return p


@variant("TV_Flat", "Modern")
def tv_modern():
    p = Prop("GD_TV_Flat_Modern_01")
    p.box("black", (0, 0, 0.62), (1.3, 0.04, 0.75))
    p.box("screen", (0, -0.022, 0.62), (1.28, 0.01, 0.73))
    p.box("wood_light", (0, 0.1, 0.18), (1.6, 0.4, 0.36))                      # the media unit
    p.box("black", (0, -0.1, 0.18), (1.5, 0.01, 0.2))
    p.box("black", (0, 0.1, 0.38), (0.4, 0.14, 0.03))
    return p


@variant("FloorLamp", "Modern")
def floor_lamp_modern():
    p = Prop("GD_FloorLamp_Modern_01")
    p.box("black", (0, 0, 0.03), (0.35, 0.35, 0.06))
    p.cyl("black", (0, 0, 0.9), 0.015, 1.7, n=4)
    for k in range(5):                                                         # an arc leaning out
        a = math.radians(k * 17)
        p.box("black", (0.0, -0.18 - 0.3 * math.sin(a) * 1.2, 1.7 + 0.12 * k), (0.02, 0.35, 0.02), rot=(-30 + k * 10, 0, 0))
    p.cyl("paint_white", (0, -0.95, 1.95), 0.18, 0.2, n=8, top_radius=0.1)
    return p


@variant("TableLamp", "Modern")
def table_lamp_modern():
    p = Prop("GD_TableLamp_Modern_01")
    p.cyl("black", (0, 0, 0.1), 0.07, 0.2, n=8)
    p.cyl("paint_white", (0, 0, 0.3), 0.13, 0.2, n=8, top_radius=0.13)
    p.cyl("glow_cyan", (0, 0, 0.3), 0.125, 0.14, n=8)
    return p


@variant("Fridge", "Modern")
def fridge_modern():
    p = Prop("GH_Fridge_Modern_01")
    p.box("metal_galv", (0, 0, 0.93), (0.9, 0.72, 1.86))
    p.box("black", (0, -0.362, 0.93), (0.9, 0.01, 0.02))
    p.box("black", (0, -0.362, 0.5), (0.02, 0.01, 0.9))
    p.box("black", (-0.06, -0.38, 1.3), (0.02, 0.03, 0.4))
    p.box("black", (0.06, -0.38, 1.3), (0.02, 0.03, 0.4))
    p.box("glow_cyan", (0.3, -0.365, 1.5), (0.1, 0.005, 0.06))
    return p


@variant("Stove", "Modern")
def stove_modern():
    p = Prop("GH_Stove_Modern_01")
    p.box("metal_galv", (0, 0, 0.45), (0.6, 0.65, 0.9))
    p.box("black", (0, 0, 0.905), (0.6, 0.65, 0.01))
    for x, y in ((-0.14, -0.12), (0.14, -0.12), (-0.14, 0.14), (0.14, 0.14)):
        p.cyl("glow_cyan", (x, y, 0.912), 0.09, 0.004, n=12)
    p.box("black", (0, -0.331, 0.42), (0.5, 0.01, 0.4))
    p.box("metal_dark", (0, -0.35, 0.68), (0.5, 0.03, 0.03))
    return p


@variant("Clock_Wall", "Modern")
def clock_modern():
    p = Prop("GD_Clock_Wall_Modern_01")
    p.cyl("black", (0, 0, 0), 0.17, 0.02, n=16, axis="y")
    p.cyl("paint_white", (0, -0.012, 0), 0.155, 0.006, n=16, axis="y")
    p.box("black", (0, -0.018, 0.06), (0.008, 0.004, 0.12))
    p.box("black", (0.045, -0.018, 0.0), (0.09, 0.004, 0.008))
    return p


@variant("Radio_Retro", "Modern")
def speaker_modern():
    p = Prop("GD_Radio_Modern_01")
    p.cyl("fabric_grey", (0, 0, 0.1), 0.06, 0.2, n=12)
    p.cyl("black", (0, 0, 0.205), 0.06, 0.01, n=12)
    p.cyl("glow_cyan", (0, 0, 0.21), 0.04, 0.004, n=12)
    return p


@variant("Wardrobe", "Modern")
def wardrobe_modern():
    p = Prop("GH_Wardrobe_Modern_01")
    p.box("paint_white", (0, 0, 1.0), (1.6, 0.6, 2.0))
    p.box("black", (0, -0.31, 1.0), (0.01, 0.01, 1.95))
    for x in (-0.4, 0.4):
        p.box("metal_galv", (x, -0.315, 1.0), (0.02, 0.02, 0.4))
    return p


@variant("Dresser", "Modern")
def dresser_modern():
    p = Prop("GH_Dresser_Modern_01")
    p.box("paint_white", (0, 0, 0.45), (1.5, 0.45, 0.7))
    for x in (-0.37, 0.37):
        for z in (0.25, 0.5, 0.75 - 0.15):
            p.box("paint_white", (x, -0.231, z), (0.7, 0.01, 0.2))
    p.box("black", (0, -0.24, 0.2), (1.4, 0.01, 0.01))
    _legs(p, "black", 1.4, 0.4, 0.1, 0.03, 0.05)
    return p


@variant("Bookcase", "Modern")
def bookcase_modern():
    p = Prop("GH_Bookcase_Modern_01")
    for k in range(4):
        p.box("black", (0, 0, 0.03 + k * 0.5), (1.2, 0.34, 0.03))
    for k in range(4):
        p.box("black", (-0.6 + k * 0.4, 0, 0.78), (0.03, 0.34, 1.5))
    p.box("black", (0, 0.17, 0.78), (1.2, 0.02, 1.5))
    cols = ["black", "paint_white", "fabric_grey", "wood_light"]
    for row in range(3):
        for k in range(6):
            p.box(cols[(k + row) % 4], (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + 0.2), (0.07, 0.22, 0.34 - 0.03 * (k % 2)))
    return p


@variant("Nightstand", "Modern")
def nightstand_modern():
    p = Prop("GH_Nightstand_Modern_01")
    p.box("paint_white", (0, 0, 0.4), (0.4, 0.4, 0.3))
    p.box("black", (0, -0.205, 0.4), (0.3, 0.01, 0.01))
    _legs(p, "black", 0.4, 0.4, 0.25, 0.025, 0.04)
    return p


@variant("Rug", "Modern")
def rug_modern():
    p = Prop("GH_Rug_Modern_01")
    p.box("fabric_grey", (0, 0, 0.008), (2.4, 1.7, 0.016))
    for k in range(5):
        p.box("black" if k % 2 else "paint_white", (-0.8 + k * 0.4, 0, 0.018), (0.2, 1.3, 0.004))
    return p


# ===== Retro ===================================================================================================
@variant("Sofa", "Retro")
def sofa_retro():
    p = Prop("GH_Sofa_Retro_01")
    p.box("rust_dark", (0, 0.0, 0.36), (2.0, 0.9, 0.12))                       # wooden frame
    p.box("orange_cat", (0, -0.02, 0.5), (1.9, 0.8, 0.2))
    for x in (-0.46, 0.46):
        p.box("orange_cat", (x, -0.06, 0.64), (0.9, 0.7, 0.12))
    p.box("orange_cat", (0, 0.36, 0.78), (1.9, 0.18, 0.56))
    for k in range(6):                                                         # button tufting
        p.box("fabric_brown", (-0.8 + k * 0.32, 0.265, 0.82), (0.04, 0.02, 0.04))
    for s in (-1, 1):
        p.box("orange_cat", (s * 0.98, 0, 0.62), (0.18, 0.9, 0.34))
        p.box("rust_dark", (s * 0.98, 0, 0.82), (0.2, 0.92, 0.04))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("rust_dark", (sx * 0.9, sy * 0.38, 0.14), (0.05, 0.05, 0.28), rot=(sy * 10, -sx * 10, 0), taper=0.7)
    return p


@variant("Armchair", "Retro")
def armchair_retro():
    p = Prop("GH_Armchair_Retro_01")
    p.box("tractor_green", (0, 0, 0.42), (0.8, 0.8, 0.18))
    p.box("tractor_green", (0, -0.03, 0.56), (0.62, 0.66, 0.12))
    p.box("tractor_green", (0, 0.34, 0.85), (0.8, 0.16, 0.7), rot=(-6, 0, 0))
    for s in (-1, 1):
        p.box("tractor_green", (s * 0.37, 0, 0.62), (0.12, 0.8, 0.3))
        p.box("tractor_green", (s * 0.52, 0.34, 1.0), (0.14, 0.14, 0.5), taper=0.8)          # the wings
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("rust_dark", (sx * 0.3, sy * 0.3, 0.17), (0.05, 0.05, 0.36), rot=(sy * 12, -sx * 12, 0), taper=0.6)
    return p


@variant("Chair_Kitchen", "Retro")
def chair_kitchen_retro():                                                     # a diner chair: chrome tube, vinyl seat
    p = Prop("GH_Chair_Kitchen_Retro_01")
    p.box("cloth_red", (0, 0, 0.47), (0.44, 0.44, 0.07))
    p.box("cloth_red", (0, 0.2, 0.78), (0.42, 0.06, 0.34), rot=(-6, 0, 0))
    p.box("metal_galv", (0, 0.2, 0.55), (0.4, 0.02, 0.02))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("metal_galv", (sx * 0.19, sy * 0.19, 0.22), (0.025, 0.025, 0.44))
        p.box("metal_galv", (sx * 0.19, 0, 0.2), (0.02, 0.4, 0.02))
    return p


@variant("Table_Dining", "Retro")
def table_dining_retro():                                                      # formica top with a chrome edge on splayed legs
    p = Prop("GH_Table_Dining_Retro_01")
    p.box("cream", (0, 0, 0.74), (1.5, 0.85, 0.04))
    p.box("metal_galv", (0, 0, 0.72), (1.54, 0.89, 0.03))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("metal_galv", (sx * 0.62, sy * 0.3, 0.36), (0.04, 0.04, 0.72), rot=(sy * 6, -sx * 6, 0), taper=0.8)
    return p


@variant("Table_Coffee", "Retro")
def table_coffee_retro():                                                      # a round teak table on three tapered legs
    p = Prop("GH_Table_Coffee_Retro_01")
    p.cyl("rust_dark", (0, 0, 0.4), 0.42, 0.04, n=12)
    for a in (90, 210, 330):
        p.box("rust_dark", (0.3 * math.cos(math.radians(a)), 0.3 * math.sin(math.radians(a)), 0.19), (0.05, 0.05, 0.38),
              rot=(math.sin(math.radians(a)) * 10, -math.cos(math.radians(a)) * 10, 0), taper=0.6)
    p.cyl("metal_galv", (0, 0, 0.42), 0.43, 0.01, n=12)
    return p


@variant("Bed_Double", "Retro")
def bed_double_retro():
    p = Prop("GH_Bed_Double_Retro_01")
    p.box("rust_dark", (0, 0, 0.22), (1.6, 2.0, 0.2))
    p.box("cream", (0, 0, 0.42), (1.5, 1.9, 0.2))
    p.box("fabric_mustard", (0, -0.3, 0.54), (1.52, 1.3, 0.06))
    p.box("orange_cat", (0, -0.9, 0.54), (1.54, 0.2, 0.07))
    for x in (-0.38, 0.38):
        p.box("cream", (x, 0.8, 0.58), (0.55, 0.3, 0.1))
    p.box("rust_dark", (0, 1.04, 0.8), (1.66, 0.08, 1.2))
    for k in range(7):
        p.box("rust_dark", (-0.7 + k * 0.233, 1.0, 1.0), (0.04, 0.04, 0.5))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("rust_dark", (sx * 0.75, sy * 0.95, 0.06), (0.07, 0.07, 0.12), taper=0.7)
    return p


@variant("TV_CRT", "Retro")
def tv_crt_retro():                                                            # a wood-grain console TV with rabbit ears
    p = Prop("GD_TV_CRT_Retro_01")
    p.box("rust_dark", (0, 0, 0.35), (0.85, 0.5, 0.7))
    p.box("screen", (-0.1, -0.255, 0.42), (0.5, 0.01, 0.42))
    p.box("fabric_brown", (0.28, -0.255, 0.42), (0.18, 0.01, 0.42))
    for k in range(3):
        p.cyl("metal_galv", (0.28, -0.265, 0.55 - k * 0.1), 0.03, 0.012, n=6, axis="y")
    for s in (-1, 1):
        p.box("rust_dark", (s * 0.36, -0.1, 0.04), (0.05, 0.05, 0.08), taper=0.7)
    p.box("black", (0, 0.0, 0.72), (0.4, 0.2, 0.04))
    for s in (-1, 1):
        p.box("metal_galv", (s * 0.12, 0.0, 0.9), (0.01, 0.01, 0.4), rot=(0, s * 30, 0))
    return p


@variant("FloorLamp", "Retro")
def floor_lamp_retro():                                                        # a tripod lamp with a drum shade
    p = Prop("GD_FloorLamp_Retro_01")
    for a in (90, 210, 330):
        p.box("rust_dark", (0.14 * math.cos(math.radians(a)), 0.14 * math.sin(math.radians(a)), 0.45), (0.035, 0.035, 0.95),
              rot=(math.sin(math.radians(a)) * 9, -math.cos(math.radians(a)) * 9, 0), taper=0.8)
    p.cyl("rust_dark", (0, 0, 1.0), 0.05, 0.1, n=6)
    p.cyl("paint_yellow", (0, 0, 1.2), 0.24, 0.3, n=8, top_radius=0.22)
    return p


@variant("TableLamp", "Retro")
def table_lamp_retro():                                                        # a ceramic gourd lamp
    p = Prop("GD_TableLamp_Retro_01")
    p.cyl("tractor_green", (0, 0, 0.12), 0.1, 0.24, n=8, top_radius=0.06)
    p.cyl("rust_dark", (0, 0, 0.02), 0.09, 0.04, n=8)
    p.cyl("paint_yellow", (0, 0, 0.34), 0.17, 0.22, n=8, top_radius=0.12)
    return p


@variant("Fridge", "Retro")
def fridge_retro():
    p = Prop("GH_Fridge_Retro_01")
    p.box("enamel_cream", (0, 0, 0.8), (0.72, 0.7, 1.6), taper=0.96)
    p.box("enamel_cream", (0, 0, 1.62), (0.7, 0.68, 0.06))
    p.box("metal_galv", (0, -0.355, 1.1), (0.7, 0.01, 0.03))
    p.box("metal_galv", (0.28, -0.38, 1.35), (0.03, 0.05, 0.3))
    p.box("metal_galv", (0.28, -0.38, 0.8), (0.03, 0.05, 0.3))
    p.box("metal_galv", (-0.0, -0.362, 1.45), (0.2, 0.01, 0.05))
    for sx in (-1, 1):
        p.box("rust_dark", (sx * 0.3, 0, 0.04), (0.06, 0.6, 0.08))
    return p


@variant("Stove", "Retro")
def stove_retro():
    p = Prop("GH_Stove_Retro_01")
    p.box("enamel_cream", (0, 0, 0.45), (0.65, 0.68, 0.9), taper=0.98)
    p.box("black", (0, -0.351, 0.38), (0.46, 0.01, 0.36))
    p.box("glass", (0, -0.357, 0.4), (0.36, 0.01, 0.22))
    for x, y in ((-0.15, -0.12), (0.15, -0.12), (-0.15, 0.14), (0.15, 0.14)):
        p.cyl("black", (x, y, 0.91), 0.1, 0.02, n=8)
        p.cyl("metal_galv", (x, y, 0.925), 0.04, 0.006, n=8)
    p.box("enamel_cream", (0, 0.31, 1.0), (0.65, 0.08, 0.22))
    for x in (-0.22, -0.07, 0.07, 0.22):
        p.cyl("metal_galv", (x, 0.265, 1.0), 0.025, 0.03, n=6, axis="y")
    return p


@variant("Clock_Wall", "Retro")
def clock_retro():                                                             # a sunburst clock
    p = Prop("GD_Clock_Wall_Retro_01")
    p.cyl("copper", (0, 0, 0), 0.1, 0.03, n=12, axis="y")
    p.cyl("paint_white", (0, -0.017, 0), 0.085, 0.006, n=12, axis="y")
    for k in range(12):
        a = k * 30
        p.box("paint_yellow", (0.19 * math.sin(math.radians(a)), 0.0, 0.19 * math.cos(math.radians(a))), (0.025, 0.012, 0.18), rot=(0, a, 0), taper=0.5)
    p.box("black", (0, -0.025, 0.035), (0.01, 0.004, 0.07))
    p.box("black", (0.03, -0.025, 0.0), (0.06, 0.004, 0.01))
    return p


@variant("Wardrobe", "Retro")
def wardrobe_retro():
    p = Prop("GH_Wardrobe_Retro_01")
    p.box("rust_dark", (0, 0, 1.0), (1.1, 0.55, 1.7))
    for x in (-0.27, 0.27):
        p.box("fabric_brown", (x, -0.285, 1.05), (0.5, 0.01, 1.5))
    p.box("glass", (0.27, -0.292, 1.15), (0.36, 0.005, 1.0))
    p.box("metal_galv", (-0.04, -0.3, 1.0), (0.025, 0.025, 0.14))
    p.box("metal_galv", (0.04, -0.3, 1.0), (0.025, 0.025, 0.14))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("rust_dark", (sx * 0.48, sy * 0.2, 0.08), (0.05, 0.05, 0.16), rot=(sy * 8, -sx * 8, 0), taper=0.7)
    return p


@variant("Dresser", "Retro")
def dresser_retro():                                                           # mid-century: long, low, on tapered legs
    p = Prop("GH_Dresser_Retro_01")
    p.box("rust_dark", (0, 0, 0.56), (1.4, 0.45, 0.6))
    for k, x in enumerate((-0.45, 0.0, 0.45)):
        p.box("fabric_brown", (x, -0.231, 0.62), (0.4, 0.01, 0.42))
        p.box("metal_galv", (x, -0.245, 0.62), (0.1, 0.02, 0.02))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("rust_dark", (sx * 0.62, sy * 0.16, 0.14), (0.05, 0.05, 0.28), rot=(sy * 10, -sx * 10, 0), taper=0.6)
    return p


@variant("Nightstand", "Retro")
def nightstand_retro():
    p = Prop("GH_Nightstand_Retro_01")
    p.box("rust_dark", (0, 0, 0.42), (0.42, 0.38, 0.3))
    p.box("fabric_brown", (0, -0.195, 0.42), (0.34, 0.01, 0.22))
    p.cyl("metal_galv", (0, -0.21, 0.42), 0.02, 0.02, n=6, axis="y")
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("rust_dark", (sx * 0.17, sy * 0.15, 0.13), (0.04, 0.04, 0.26), rot=(sy * 9, -sx * 9, 0), taper=0.6)
    return p


@variant("Bookcase", "Retro")
def bookcase_retro():
    p = Prop("GH_Bookcase_Retro_01")
    p.box("rust_dark", (0, 0.15, 0.95), (1.0, 0.04, 1.4))
    for z in (0.25, 0.65, 1.05, 1.65):
        p.box("rust_dark", (0, 0, z), (1.0, 0.3, 0.035))
    for x in (-0.5, 0.5):
        p.box("rust_dark", (x, 0, 0.95), (0.035, 0.3, 1.45))
    for sx in (-1, 1):
        p.box("rust_dark", (sx * 0.42, 0, 0.1), (0.04, 0.26, 0.4), rot=(0, -sx * 12, 0), taper=0.6)
    cols = ["book_red", "tractor_green", "orange_cat", "fabric_mustard"]
    for row, z0 in enumerate((0.28, 0.68, 1.08)):
        x = -0.42
        for k in range(8):
            w = 0.05 + 0.01 * ((k + row) % 3)
            p.box(cols[(k + row) % 4], (x + w / 2, 0.0, z0 + 0.15), (w, 0.2, 0.3))
            x += w + 0.01
    return p


@variant("Rug", "Retro")
def rug_retro():                                                               # concentric orange, brown and mustard rings
    p = Prop("GH_Rug_Retro_01")
    for k, c in enumerate(("rust_dark", "orange_cat", "fabric_mustard", "cream", "orange_cat")):
        p.cyl(c, (0, 0, 0.008 + k * 0.003), 1.0 - k * 0.17, 0.016, n=14)
    return p


@variant("Radio_Retro", "Retro")
def radio_retro_style():                                                       # the existing retro radio, in teak and cream
    p = Prop("GD_Radio_Retro_Retro_01")
    p.box("rust_dark", (0, 0, 0.15), (0.45, 0.2, 0.3))
    p.box("cream", (-0.06, -0.105, 0.17), (0.22, 0.01, 0.14))
    p.cyl("orange_cat", (0.15, -0.105, 0.2), 0.03, 0.02, n=8, axis="y")
    p.cyl("orange_cat", (0.15, -0.105, 0.1), 0.03, 0.02, n=8, axis="y")
    p.box("metal_galv", (0.15, 0.0, 0.42), (0.01, 0.01, 0.25), rot=(0, 15, 0))
    return p


# ===== Damaged (bespoke wrecks) ===============================================================================
@variant("Sofa", "Damaged")
def sofa_damaged():
    p = Prop("GH_Sofa_Damaged_01")
    p.box("fabric_brown", (0, 0, 0.2), (2.0, 0.9, 0.3))
    p.box("fabric_brown", (-0.46, -0.04, 0.46), (0.9, 0.7, 0.18), rot=(0, 0, 0))
    p.box("fabric_brown", (0.46, -0.04, 0.38), (0.9, 0.7, 0.12), rot=(0, 8, 0))                   # a collapsed cushion
    p.box("fabric_brown", (0, 0.36, 0.62), (2.0, 0.18, 0.5), rot=(-8, 0, 0))
    p.box("fabric_brown", (-0.95, 0, 0.5), (0.2, 0.9, 0.5))
    p.box("wood_grey", (0.95, 0.1, 0.3), (0.16, 0.7, 0.04), rot=(20, 0, 14))                       # the right arm torn off
    p.box("black", (0.3, -0.34, 0.47), (0.5, 0.01, 0.04), rot=(0, 5, 0))                          # a slash
    for k, (x, y, z, r) in enumerate(((0.35, -0.5, 0.5, 20), (0.5, -0.45, 0.45, -30), (0.2, -0.55, 0.42, 70))):
        p.box("linen", (x, y, z), (0.16, 0.1, 0.05), rot=(10, 0, r))                              # stuffing spilling out
    p.box("rust_dark", (-0.4, -0.04, 0.56), (0.3, 0.25, 0.005))                                   # a stain
    for sx, sy in ((-0.9, -0.38), (0.9, -0.38), (-0.9, 0.38)):
        p.box("wood_grey", (sx, sy, 0.04), (0.07, 0.07, 0.08))
    p.post = _lean(6, 1)
    return p


def _lean(deg, seed):
    import random

    def settle(obj):
        import bpy
        rng = random.Random(seed)
        obj.rotation_euler = (math.radians(rng.uniform(-deg, deg)), math.radians(rng.uniform(-deg, deg)), math.radians(rng.uniform(-deg, deg)))
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        low = min(v.co.z for v in obj.data.vertices)
        for v in obj.data.vertices:
            v.co.z -= low
    return settle


@variant("Armchair", "Damaged")
def armchair_damaged():
    p = Prop("GH_Armchair_Damaged_01")
    p.box("fabric_brown", (0, 0, 0.2), (0.9, 0.85, 0.3))
    p.box("fabric_brown", (0, 0.05, 0.4), (0.62, 0.7, 0.1), rot=(8, 0, 0))
    p.box("fabric_brown", (0, 0.36, 0.65), (0.9, 0.18, 0.62), rot=(-14, 0, 6))
    p.box("fabric_brown", (-0.4, 0, 0.5), (0.14, 0.8, 0.4))
    p.box("wood_grey", (0.46, -0.1, 0.12), (0.5, 0.14, 0.05), rot=(0, 0, 70))                   # the right arm, lying on the floor
    p.box("black", (0.0, -0.4, 0.45), (0.4, 0.01, 0.05), rot=(0, 20, 0))
    for k, (x, y) in enumerate(((0.1, -0.5), (0.3, -0.45), (-0.1, -0.52))):
        p.box("linen", (x, y, 0.12), (0.14, 0.1, 0.05), rot=(0, 0, k * 50))
    p.post = _lean(5, 2)
    return p


@variant("Chair_Kitchen", "Damaged")
def chair_kitchen_damaged():                                                   # three legs, leaning on the back of the fourth
    p = Prop("GH_Chair_Kitchen_Damaged_01")
    p.box("wood_grey", (0, 0, 0.47), (0.44, 0.44, 0.04), rot=(0, 0, 0))
    p.box("wood_grey", (0, 0.2, 0.7), (0.4, 0.03, 0.4))
    for x in (-0.12, 0.0, 0.12):
        p.box("rust_dark", (x, 0.2, 0.7), (0.03, 0.035, 0.38))
    for sx, sy in ((-1, -1), (1, -1), (-1, 1)):                                                   # the fourth leg is gone
        p.box("wood_grey", (sx * 0.19, sy * 0.19, 0.22), (0.04, 0.04, 0.44))
    p.box("wood_grey", (0.19, 0.19, 0.04), (0.04, 0.04, 0.12), rot=(0, 0, 40))                    # the stump
    p.post = _lean(0, 3)

    def tip(obj):
        import bpy
        obj.rotation_euler = (math.radians(-8), math.radians(10), math.radians(15))
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        low = min(v.co.z for v in obj.data.vertices)
        for v in obj.data.vertices:
            v.co.z -= low
    p.post = tip
    return p


@variant("Table_Dining", "Damaged")
def table_dining_overturned():
    p = Prop("GH_Table_Dining_Overturned_01")
    p.box("wood_grey", (0, 0, 0.0), (1.6, 0.9, 0.05))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box("rust_dark", (sx * 0.7, sy * 0.38, -0.36), (0.08, 0.08, 0.72))
    p.box("rust_dark", (0.9, 0.2, -0.2), (0.7, 0.04, 0.04), rot=(0, 0, 30))                      # a loose brace

    def flip(obj):
        import bpy
        obj.rotation_euler = (math.radians(180 - 12), math.radians(8), math.radians(20))           # upside down, resting on a corner
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        low = min(v.co.z for v in obj.data.vertices)
        for v in obj.data.vertices:
            v.co.z -= low
    p.post = flip
    return p


@variant("TV_CRT", "Damaged")
def tv_crt_smashed():
    p = Prop("GD_TV_CRT_Smashed_01")
    p.box("wood_grey", (0, 0, 0.2), (0.6, 0.5, 0.4))
    p.box("fabric_grey", (0, 0.0, 0.62), (0.56, 0.46, 0.44), taper=0.9)
    p.box("black", (-0.04, -0.235, 0.62), (0.34, 0.02, 0.26))
    for k, (x, z, r) in enumerate(((-0.16, 0.72, 30), (0.02, 0.5, -40), (0.1, 0.66, 70))):
        p.box("glass", (x, -0.245, z), (0.14, 0.01, 0.03), rot=(0, r, 0))                      # crack lines
    p.box("glass", (0.0, -0.3, 0.42), (0.07, 0.06, 0.003), rot=(0, 10, 25))                     # shards on the floor
    p.box("glass", (-0.15, -0.35, 0.0), (0.08, 0.06, 0.004), rot=(0, 0, 40))
    p.box("metal_dark", (0, 0.28, 0.62), (0.3, 0.2, 0.3), taper=0.5)
    p.box("black", (0.22, -0.236, 0.62), (0.07, 0.02, 0.3))
    p.post = _lean(7, 4)
    return p


@variant("Fridge", "Damaged")
def fridge_damaged():
    p = Prop("GH_Fridge_Damaged_01")
    p.box("rust", (0, 0.0, 0.9), (0.7, 0.7, 1.8))
    p.box("enamel_cream", (0, 0.1, 1.5), (0.66, 0.5, 0.5), taper=1.0)
    p.box("black", (0, -0.34, 0.5), (0.62, 0.02, 1.1))                                          # the dark open interior
    p.box("enamel_cream", (0.42, -0.5, 0.55), (0.05, 0.7, 1.12), rot=(0, 0, -50))              # the door, hanging open
    p.box("metal_galv", (0.7, -0.75, 0.6), (0.03, 0.04, 0.3))
    for z in (0.35, 0.7):
        p.box("wood_grey", (0, -0.3, z), (0.6, 0.35, 0.02), rot=(6, 0, 0))                      # sagging shelves
    p.box("rust_dark", (0, -0.36, 1.2), (0.2, 0.01, 0.2))
    p.post = _lean(3, 5)
    return p


@variant("Bed_Single", "Damaged")
def bed_single_damaged():                                                       # a stained mattress on the floor, the frame gone
    p = Prop("GH_Bed_Single_Damaged_01")
    p.box("linen", (0, 0, 0.1), (0.9, 1.95, 0.2), rot=(0, 0, 4))
    p.box("fabric_grey", (0, -0.2, 0.21), (0.88, 1.2, 0.04), rot=(0, 0, 4))
    p.box("rust_dark", (0.1, 0.2, 0.225), (0.34, 0.3, 0.004))
    p.box("rust_dark", (-0.15, -0.5, 0.225), (0.2, 0.18, 0.004))
    p.box("wood_grey", (0.7, 0.4, 0.04), (0.06, 0.6, 0.08), rot=(0, 0, 25))                      # splintered frame pieces
    p.box("wood_grey", (-0.7, -0.5, 0.05), (0.06, 0.8, 0.1), rot=(0, 20, -15))
    return p


@variant("FloorLamp", "Damaged")
def floor_lamp_fallen():
    p = Prop("GD_FloorLamp_Fallen_01")
    p.cyl("metal_dark", (0, 0, 0.03), 0.17, 0.04, n=8, rot=(80, 0, 0))
    p.cyl("metal_dark", (0, 0.8, 0.05), 0.02, 1.5, n=6, axis="y")
    p.cyl("wood_grey", (0, 1.65, 0.12), 0.22, 0.28, n=8, top_radius=0.13, axis="y")

    def lay(obj):
        low = min(v.co.z for v in obj.data.vertices)
        for v in obj.data.vertices:
            v.co.z -= low
    p.post = lay
    return p


@variant("Bookcase", "Damaged")
def bookcase_tipped():                                                          # leaning at 25 degrees, books on the floor
    p = Prop("GH_Bookcase_Tipped_01")
    for s in (-1, 1):
        p.box("wood_grey", (s * 0.4, 0, 0.9), (0.04, 0.3, 1.8))
    p.box("wood_grey", (0, 0.14, 0.9), (0.8, 0.02, 1.8))
    for z in (0.02, 0.45, 0.9, 1.35, 1.78):
        p.box("wood_grey", (0, 0, z), (0.8, 0.3, 0.04))
    cols = ["book_red", "wood_grey", "dead_wood", "fabric_brown"]
    for k in range(5):
        p.box(cols[k % 4], (-0.3 + k * 0.1, 0.0, 1.0 + 0.15), (0.06, 0.2, 0.3), rot=(0, 20 - k * 8, 0))
    for k, (x, y, r) in enumerate(((0.5, -0.6, 25), (0.2, -0.8, -40), (-0.3, -0.65, 80), (0.0, -0.45, 10))):
        p.box(cols[k % 4], (x, y, 0.03), (0.2, 0.15, 0.05), rot=(0, 0, r))

    def tip(obj):
        import bpy
        obj.rotation_euler = (math.radians(-25), 0, math.radians(8))
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        low = min(v.co.z for v in obj.data.vertices)
        for v in obj.data.vertices:
            v.co.z -= low
    p.post = tip
    return p


@variant("Curtains_Closed", "Damaged")
def curtains_torn():
    p = Prop("GH_Curtains_Torn_01")
    p.cyl("wood_grey", (0.15, 0, 2.0), 0.015, 1.4, n=4, axis="x", rot=(0, 0, 0))
    p.box("wood_grey", (-0.65, 0, 1.95), (0.5, 0.02, 0.02), rot=(0, 35, 0))                       # the rod, snapped and hanging
    for k in range(8):
        h = 2.0 if k > 3 else 1.1 + 0.15 * k
        p.box("fabric_brown", (0.1 + k * 0.1, (k % 2) * 0.04, 2.0 - h / 2), (0.1, 0.05, h))
    p.box("fabric_brown", (-0.55, 0.0, 0.05), (0.45, 0.2, 0.1), rot=(0, 0, 25))                   # a heap on the floor
    return p


@variant("Wardrobe", "Damaged")
def wardrobe_damaged():
    p = Prop("GH_Wardrobe_Damaged_01")
    p.box("wood_grey", (0, 0, 0.95), (1.0, 0.55, 1.9))
    p.box("black", (-0.25, -0.285, 0.95), (0.46, 0.01, 1.8))                                      # an empty doorway, door off
    p.box("wood_grey", (0.25, -0.285, 0.95), (0.46, 0.02, 1.8))
    p.box("wood_grey", (-0.55, -0.6, 0.9), (0.46, 0.02, 1.8), rot=(0, 25, 0))                    # the left door, fallen
    p.box("fabric_brown", (-0.2, -0.45, 0.06), (0.4, 0.3, 0.12), rot=(0, 0, 20))                 # clothes on the floor
    p.box("fabric_grey", (0.1, -0.6, 0.04), (0.3, 0.2, 0.08), rot=(0, 0, -30))
    p.post = _lean(4, 7)
    return p


@variant("Dresser", "Damaged")
def dresser_damaged():
    p = Prop("GH_Dresser_Damaged_01")
    p.box("wood_grey", (0, 0, 0.45), (1.2, 0.5, 0.9))
    for z in (0.2, 0.7):
        p.box("rust_dark", (0, -0.255, z), (1.1, 0.02, 0.2))
    p.box("wood_grey", (0.1, -0.5, 0.42), (1.0, 0.5, 0.18), rot=(0, 0, 0))                       # a drawer hanging out
    p.box("black", (0, -0.255, 0.45), (1.1, 0.01, 0.2))
    p.box("fabric_brown", (0.2, -0.55, 0.52), (0.4, 0.3, 0.06), rot=(0, 10, 15))
    p.box("wood_grey", (-0.6, 0.0, 0.92), (0.02, 0.5, 0.06))
    p.post = _lean(5, 8)
    return p


def window_boarded():                                                           # a kit piece: a window nailed shut with planks
    p = Prop("GK_Window_Boarded_01")
    p.box("wood_dark", (-0.46, 0, 0.6), (0.08, 0.1, 1.2))
    p.box("wood_dark", (0.46, 0, 0.6), (0.08, 0.1, 1.2))
    for z in (0.02, 1.18):
        p.box("wood_dark", (0, 0, z), (1.0, 0.1, 0.08))
    for z, r in ((0.3, 3), (0.62, -2), (0.95, 4)):
        p.box("wood_grey", (0, -0.07, z), (1.08, 0.04, 0.2), rot=(0, r, 0))
        for x in (-0.4, 0.4):
            p.box("metal_dark", (x, -0.095, z), (0.03, 0.02, 0.03))
    return p


def _named(prop, theme):
    if prop.name.endswith("_01") and f"_{theme}_" not in prop.name:
        prop.name = prop.name[:-3] + f"_{theme}_01"
    return prop


def run():
    themes = globals().get("THEME_LIST") or list(THEMES)
    only = globals().get("STYLE_PIECES")
    count = 0
    y = 0.0
    for module, folder in ((household, "Household"), (decor, "Decor")):
        for name, (fn, group) in module.PIECES.items():
            if only and name not in only:
                continue
            x = 0.0
            for theme in themes:
                key = (name, theme)
                if name == "Radio_Retro" and theme == "Retro" and key not in VARIANTS:
                    continue
                var = VARIANTS.get(key)
                props_lib.THEME = {} if var else THEMES[theme]
                try:
                    prop = var() if var else fn()
                finally:
                    props_lib.THEME = {}
                if not var:
                    prop = _named(prop, theme)
                    if theme == "Damaged":
                        prop.damage(seed=sum(ord(c) * (i + 1) for i, c in enumerate(name)) % 1000)
                obj, coll = prop.finish()
                common.export_fbx(coll, f"Assets/Art/Global/{folder}/{theme}/{prop.name}.fbx")
                obj.location = (x, y, 0)
                x += max(1.2, obj.dimensions.x + 0.4)
                count += 1
            y += 2.5
    # the boarded window belongs with the kit
    if (not only or "Window" in only) and "Damaged" in themes:
        prop = window_boarded()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Kit/{prop.name}.fbx")
        count += 1
    props_lib.write_interactions()
    print("home styles done", count)


if __name__ == "__main__":
    run()
