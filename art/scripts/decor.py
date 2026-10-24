"""Small household objects and decoration (asset list GH-07..GH-12, GE-, GL-, GT-07, GT-08): lamps, electronics, wall decor, plants,
toys, books, clothing and the clutter that makes a room look lived in. Flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/decor.py", run_name="__main__")
Optional global DECOR_LIST (names or group names). Exports Assets/Art/Global/Decor/<name>.fbx.

Real sizes. Wall-mounted pieces (frames, clock, calendar, board, camera, switch...) have their origin at the centre of the mount, facing -Y;
everything else stands on the floor at the centre of its base. Pieces meant to light a room (lamps, screens, neon) use the palette's
`glow_cyan` or `lamp_shade` swatches for the lit parts; the real Light components are added in Unity.
Add a piece with the @piece(group) decorator.
"""

import importlib
import math
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


# ===== Lamps (GL-06, GL-07, GL-09) =============================================================================
@piece("lamps", "TableLamp")
def table_lamp():
    p = Prop("GD_TableLamp_01")
    p.cyl("wood_dark", (0, 0, 0.02), 0.09, 0.04, n=8)
    p.cyl("wood_dark", (0, 0, 0.17), 0.025, 0.28, n=6)
    p.cyl("lamp_shade", (0, 0, 0.34), 0.14, 0.2, n=8, top_radius=0.09)
    return p


@piece("lamps", "FloorLamp")
def floor_lamp():
    p = Prop("GD_FloorLamp_01")
    p.cyl("metal_dark", (0, 0, 0.02), 0.17, 0.04, n=8)
    p.cyl("metal_dark", (0, 0, 0.8), 0.02, 1.5, n=6)
    p.cyl("lamp_shade", (0, 0, 1.6), 0.22, 0.28, n=8, top_radius=0.13)
    return p


@piece("lamps", "DeskLamp")
def desk_lamp():
    p = Prop("GD_DeskLamp_01")
    p.cyl("metal_dark", (0, 0, 0.015), 0.09, 0.03, n=8)
    p.box("metal_dark", (0, 0.02, 0.2), (0.02, 0.02, 0.34), rot=(15, 0, 0))
    p.box("metal_dark", (0, -0.08, 0.37), (0.02, 0.2, 0.02), rot=(-15, 0, 0))
    p.cyl("paint_yellow", (0, -0.17, 0.35), 0.06, 0.1, n=8, top_radius=0.03, rot=(20, 0, 0))
    return p


@piece("lamps", "CeilingShade")
def ceiling_shade():                       # hangs from the origin at the ceiling
    p = Prop("GD_CeilingShade_01")
    p.cyl("black", (0, 0, -0.2), 0.008, 0.4, n=4)
    p.cyl("lamp_shade", (0, 0, -0.5), 0.2, 0.18, n=8, top_radius=0.06)
    p.cyl("glow_cyan", (0, 0, -0.56), 0.04, 0.06, n=6)
    return p


@piece("lamps", "Fluorescent")
def fluorescent():                         # a ceiling fixture, origin at the ceiling
    p = Prop("GD_Fluorescent_01")
    p.box("metal_dark", (0, 0, -0.04), (1.25, 0.14, 0.06))
    p.box("glow_cyan", (0, 0, -0.085), (1.2, 0.06, 0.03))
    return p


@piece("lamps", "Chandelier")
def chandelier():
    p = Prop("GD_Chandelier_01")
    p.cyl("black", (0, 0, -0.25), 0.01, 0.5, n=4)
    p.cyl("copper", (0, 0, -0.55), 0.05, 0.1, n=6)
    for a in range(6):
        x, y = 0.3 * math.cos(math.radians(a * 60)), 0.3 * math.sin(math.radians(a * 60))
        p.box("copper", (x / 2, y / 2, -0.58), (0.3, 0.02, 0.02), rot=(0, 0, a * 60))
        p.cyl("paint_white", (x, y, -0.55), 0.015, 0.1, n=4)
        p.cyl("glow_cyan", (x, y, -0.49), 0.015, 0.03, n=4)
    return p


@piece("lamps", "KeroseneLamp")
def kerosene_lamp():
    p = Prop("GD_KeroseneLamp_01")
    p.cyl("copper", (0, 0, 0.05), 0.06, 0.1, n=8)
    p.cyl("clear_glass", (0, 0, 0.18), 0.045, 0.16, n=8)
    p.cyl("glow_cyan", (0, 0, 0.16), 0.02, 0.08, n=6)
    p.cyl("copper", (0, 0, 0.27), 0.03, 0.03, n=6)
    p.box("copper", (0, 0, 0.32), (0.01, 0.1, 0.06), rot=(0, 90, 0))
    return p


@piece("lamps", "Candle")
def candle():
    p = Prop("GD_Candle_01")
    p.cyl("copper", (0, 0, 0.01), 0.05, 0.02, n=8)
    p.cyl("paint_white", (0, 0, 0.1), 0.02, 0.16, n=6)
    p.cyl("paint_yellow", (0, 0, 0.2), 0.012, 0.04, n=4, top_radius=0.002)
    return p


@piece("lamps", "NeonSign")
def neon_sign():
    p = Prop("GD_NeonSign_01")
    p.box("black", (0, 0.02, 0.0), (1.0, 0.04, 0.35))
    p.box("glow_cyan", (0, -0.01, 0.1), (0.8, 0.03, 0.05))
    p.box("cloth_red", (0, -0.01, -0.06), (0.6, 0.03, 0.05))
    p.box("cloth_red", (-0.4, -0.01, 0.02), (0.04, 0.03, 0.22))
    p.box("cloth_red", (0.4, -0.01, 0.02), (0.04, 0.03, 0.22))
    return p


# ===== Electronics (GE-) =======================================================================================
@piece("electronics", "TV_CRT")
def tv_crt():
    p = Prop("GD_TV_CRT_01")
    p.box("wood_dark", (0, 0, 0.2), (0.6, 0.5, 0.4))                                  # a little cabinet under it
    p.box("fabric_grey", (0, 0.0, 0.62), (0.56, 0.46, 0.44), taper=0.9)
    p.box("screen", (-0.04, -0.235, 0.62), (0.4, 0.02, 0.32))
    p.box("black", (0.22, -0.235, 0.62), (0.07, 0.02, 0.3))
    p.box("metal_dark", (0, 0.28, 0.62), (0.3, 0.2, 0.3), taper=0.5)
    return p


@piece("electronics", "TV_Flat")
def tv_flat():
    p = Prop("GD_TV_Flat_01")
    p.box("black", (0, 0, 0.5), (0.95, 0.05, 0.57))
    p.box("screen", (0, -0.026, 0.5), (0.9, 0.01, 0.52))
    p.box("black", (0, 0.04, 0.03), (0.35, 0.18, 0.04))
    p.box("black", (0, 0.04, 0.12), (0.06, 0.04, 0.2))
    return p


@piece("electronics", "Radio_Retro")
def radio_retro():
    p = Prop("GD_Radio_Retro_01")
    p.box("wood_light", (0, 0, 0.14), (0.4, 0.17, 0.28))
    p.box("lamp_shade", (-0.06, -0.09, 0.15), (0.18, 0.01, 0.12))
    p.cyl("black", (0.12, -0.09, 0.18), 0.025, 0.02, n=6, axis="y")
    p.cyl("black", (0.12, -0.09, 0.1), 0.025, 0.02, n=6, axis="y")
    p.cyl("black", (-0.06, -0.09, 0.07), 0.025, 0.02, n=6, axis="y")
    p.box("metal_galv", (0.1, 0.0, 0.4), (0.01, 0.01, 0.25), rot=(0, 20, 0))
    return p


@piece("electronics", "Radio_CB")
def radio_cb():
    p = Prop("GD_Radio_CB_01")
    p.box("black", (0, 0, 0.04), (0.2, 0.14, 0.07))
    p.box("glow_cyan", (-0.04, -0.072, 0.045), (0.07, 0.005, 0.025))
    p.cyl("metal_galv", (0.06, -0.072, 0.045), 0.015, 0.01, n=6, axis="y")
    return p


@piece("electronics", "Radio_Handheld")
def radio_handheld():
    p = Prop("GD_Radio_Handheld_01")
    p.box("black", (0, 0, 0.1), (0.06, 0.035, 0.2))
    p.cyl("black", (0.02, 0, 0.27), 0.008, 0.14, n=4)
    p.box("fabric_grey", (0, -0.019, 0.14), (0.04, 0.004, 0.05))
    p.box("cloth_red", (0.02, -0.019, 0.2), (0.015, 0.004, 0.015))
    return p


@piece("electronics", "MobilePhone")
def mobile_phone():
    p = Prop("GD_MobilePhone_01")
    p.box("black", (0, 0, 0.004), (0.07, 0.14, 0.008))
    p.box("glow_cyan", (0, -0.005, 0.0085), (0.06, 0.1, 0.001))
    return p


@piece("electronics", "RotaryPhone")
def rotary_phone():
    p = Prop("GD_RotaryPhone_01")
    p.box("black", (0, 0, 0.06), (0.2, 0.24, 0.12), taper=0.9)
    p.cyl("paint_white", (0, -0.03, 0.125), 0.07, 0.01, n=10)
    p.box("black", (0, 0.0, 0.16), (0.24, 0.06, 0.04))
    for s in (-1, 1):
        p.box("black", (s * 0.11, 0.0, 0.18), (0.05, 0.08, 0.05))
    return p


@piece("electronics", "SecurityCamera")
def security_camera():
    p = Prop("GD_SecurityCamera_01")
    p.box("metal_dark", (0, 0.06, 0.0), (0.06, 0.04, 0.06))
    p.box("metal_dark", (0, 0.0, 0.0), (0.04, 0.12, 0.04))
    p.box("fabric_grey", (0, -0.12, -0.02), (0.08, 0.16, 0.08))
    p.box("glass", (0, -0.205, -0.02), (0.05, 0.01, 0.05))
    p.box("cloth_red", (0.03, -0.1, 0.03), (0.01, 0.01, 0.01))
    return p


@piece("electronics", "LightSwitch")
def light_switch():
    p = Prop("GD_LightSwitch_01")
    p.box("paint_white", (0, 0, 0), (0.08, 0.012, 0.12))
    p.box("fabric_grey", (0, -0.012, 0.0), (0.025, 0.012, 0.05), rot=(-15, 0, 0))
    return p


@piece("electronics", "Monitor")
def monitor():
    p = Prop("GD_Monitor_01")
    p.box("fabric_grey", (0, 0.0, 0.32), (0.46, 0.18, 0.38), taper=0.95)
    p.box("screen", (0, -0.092, 0.32), (0.38, 0.01, 0.3))
    p.box("fabric_grey", (0, 0.0, 0.07), (0.26, 0.22, 0.04))
    return p


@piece("electronics", "Keyboard")
def keyboard():
    p = Prop("GD_Keyboard_01")
    p.box("fabric_grey", (0, 0, 0.012), (0.44, 0.16, 0.024), rot=(-3, 0, 0))
    for r in range(4):
        p.box("black", (0, -0.05 + r * 0.035, 0.026), (0.4, 0.025, 0.006))
    return p


@piece("electronics", "ComputerTower")
def computer_tower():
    p = Prop("GD_ComputerTower_01")
    p.box("fabric_grey", (0, 0, 0.22), (0.2, 0.45, 0.44))
    p.box("black", (0, -0.226, 0.34), (0.16, 0.01, 0.04))
    p.box("glow_cyan", (0.06, -0.232, 0.15), (0.02, 0.005, 0.02))
    return p


@piece("electronics", "Laptop")
def laptop():
    p = Prop("GD_Laptop_01")
    p.box("fabric_grey", (0, 0, 0.01), (0.34, 0.24, 0.02))
    p.box("fabric_grey", (0, 0.12, 0.13), (0.34, 0.015, 0.23), rot=(-12, 0, 0))
    p.box("screen", (0, 0.108, 0.13), (0.3, 0.005, 0.2), rot=(-12, 0, 0))
    return p


@piece("electronics", "Intercom")
def intercom():
    p = Prop("GD_Intercom_01")
    p.box("metal_dark", (0, 0, 0), (0.12, 0.04, 0.2))
    p.box("fabric_grey", (0, -0.022, 0.05), (0.08, 0.005, 0.06))
    p.box("cloth_red", (0, -0.022, -0.06), (0.04, 0.005, 0.04))
    return p


# ===== Wall decor and story details (GH-08, GD-) ===============================================================
def _frame(p, w, h, picture="paper"):
    p.box("wood_dark", (0, 0, 0), (w, 0.03, h))
    p.box(picture, (0, -0.016, 0), (w - 0.06, 0.005, h - 0.06))


@piece("walldecor", "Frame_Landscape")
def frame_landscape():
    p = Prop("GD_Frame_Landscape_01")
    _frame(p, 0.6, 0.45, "tile_blue")
    p.box("grass", (0, -0.019, -0.1), (0.54, 0.004, 0.14))
    p.box("paint_yellow", (0.15, -0.019, 0.08), (0.06, 0.004, 0.06))
    return p


@piece("walldecor", "Frame_Portrait")
def frame_portrait():
    p = Prop("GD_Frame_Portrait_01")
    _frame(p, 0.36, 0.5, "wallpaper")
    p.box("skin", (0, -0.019, 0.07), (0.12, 0.004, 0.14))
    p.box("fabric_brown", (0, -0.019, -0.11), (0.2, 0.004, 0.14))
    return p


@piece("walldecor", "Frame_Landscape_02")
def frame_landscape_02():
    p = Prop("GD_Frame_Landscape_02")                                              # mountains under a pale sky
    _frame(p, 0.6, 0.45, "paper")
    p.box("rock", (-0.1, -0.019, -0.04), (0.3, 0.004, 0.22), taper=0.3)
    p.box("rock", (0.14, -0.019, -0.07), (0.24, 0.004, 0.16), taper=0.3)
    p.box("pine", (0.0, -0.019, -0.15), (0.54, 0.004, 0.06))
    return p


@piece("walldecor", "Frame_Landscape_03")
def frame_landscape_03():
    p = Prop("GD_Frame_Landscape_03")                                              # the sea at sunset: a sail on the water
    _frame(p, 0.5, 0.4, "pink")
    p.box("tile_blue", (0, -0.019, -0.1), (0.44, 0.004, 0.12))
    p.box("paint_yellow", (-0.1, -0.019, 0.06), (0.07, 0.004, 0.07))
    p.box("cream", (0.1, -0.019, -0.02), (0.08, 0.004, 0.1))
    return p


@piece("walldecor", "Frame_Portrait_02")
def frame_portrait_02():
    p = Prop("GD_Frame_Portrait_02")                                               # a woman with dark hair
    _frame(p, 0.36, 0.5, "paper")
    p.box("hair_black", (0, -0.019, 0.08), (0.16, 0.004, 0.16))
    p.box("skin", (0, -0.021, 0.07), (0.1, 0.004, 0.12))
    p.box("cloth_red", (0, -0.019, -0.11), (0.22, 0.004, 0.14))
    return p


@piece("walldecor", "KidDrawing_02")
def kid_drawing_02():
    p = Prop("GD_KidDrawing_02")                                                   # a red house under a yellow sun
    p.box("paper", (0, 0, 0), (0.3, 0.004, 0.4), rot=(0, -3, 0))
    p.box("barn_red", (0, -0.005, -0.06), (0.14, 0.002, 0.1))
    p.box("wood_dark", (0, -0.005, 0.02), (0.18, 0.002, 0.03))
    p.box("paint_yellow", (0.09, -0.005, 0.14), (0.06, 0.002, 0.06))
    p.box("grass", (0, -0.005, -0.15), (0.26, 0.002, 0.04))
    return p


@piece("walldecor", "PhotoFrame_Standing")
def photo_frame():
    p = Prop("GD_PhotoFrame_01")
    p.box("wood_dark", (0, 0, 0.1), (0.2, 0.02, 0.16), rot=(-12, 0, 0))
    p.box("paper", (0, -0.012, 0.1), (0.16, 0.004, 0.12), rot=(-12, 0, 0))
    p.box("skin", (-0.03, -0.015, 0.11), (0.03, 0.004, 0.04), rot=(-12, 0, 0))
    p.box("wood_dark", (0, 0.04, 0.05), (0.04, 0.05, 0.1), rot=(20, 0, 0))
    return p


@piece("walldecor", "Clock_Wall")
def clock_wall():
    p = Prop("GD_Clock_Wall_01")
    p.cyl("wood_dark", (0, 0, 0), 0.17, 0.04, n=12, axis="y")
    p.cyl("paint_white", (0, -0.022, 0), 0.15, 0.006, n=12, axis="y")
    p.box("black", (0, -0.03, 0.05), (0.012, 0.004, 0.1))
    p.box("black", (0.03, -0.03, 0.0), (0.07, 0.004, 0.012))
    return p


@piece("walldecor", "Calendar")
def calendar():
    p = Prop("GD_Calendar_01")
    p.box("paper", (0, 0, 0), (0.3, 0.01, 0.42))
    p.box("cloth_red", (0, -0.006, 0.17), (0.3, 0.004, 0.08))
    p.box("fabric_grey", (0, -0.006, -0.05), (0.26, 0.004, 0.24))
    return p


@piece("walldecor", "BulletinBoard")
def bulletin_board():
    p = Prop("GD_BulletinBoard_01")
    p.box("wood_dark", (0, 0, 0), (0.9, 0.03, 0.6))
    p.box("copper", (0, -0.016, 0), (0.84, 0.006, 0.54))
    for x, z, c in ((-0.25, 0.12, "paper"), (0.05, 0.15, "paint_yellow"), (0.28, 0.05, "paper"), (-0.1, -0.12, "fabric_pink"), (0.25, -0.15, "paper")):
        p.box(c, (x, -0.021, z), (0.18, 0.004, 0.22), rot=(0, (x * 40), 0))
        p.box("cloth_red", (x, -0.025, z + 0.09), (0.015, 0.004, 0.015))
    return p


@piece("walldecor", "NewspaperClippings")
def clippings():
    p = Prop("GD_NewspaperClippings_01")
    for k, (x, z, w, h, r) in enumerate(((0, 0.1, 0.28, 0.2, 4), (-0.3, -0.12, 0.2, 0.28, -6), (0.22, -0.1, 0.24, 0.18, 8), (0.05, -0.28, 0.16, 0.12, -3))):
        p.box("paper", (x, 0, z), (w, 0.004, h), rot=(0, r, 0))
        p.box("black", (x, -0.003, z + h * 0.3), (w * 0.8, 0.002, 0.02), rot=(0, r, 0))
        p.box("fabric_grey", (x, -0.003, z - h * 0.1), (w * 0.8, 0.002, h * 0.4), rot=(0, r, 0))
    p.box("cloth_red", (0.0, -0.004, 0.0), (0.58, 0.002, 0.006), rot=(0, 25, 0))
    return p


@piece("walldecor", "Poster")
def poster():
    p = Prop("GD_Poster_01")
    p.box("paper", (0, 0, 0), (0.5, 0.004, 0.7))
    p.box("truck_blue", (0, -0.003, 0.0), (0.46, 0.002, 0.66))
    p.cyl("alien_grey", (0, -0.005, 0.05), 0.12, 0.002, n=6, axis="y")
    p.box("black", (-0.05, -0.006, 0.07), (0.05, 0.002, 0.02))
    p.box("black", (0.05, -0.006, 0.07), (0.05, 0.002, 0.02))
    return p


@piece("walldecor", "KidDrawing")
def kid_drawing():
    p = Prop("GD_KidDrawing_01")
    p.box("paper", (0, 0, 0), (0.3, 0.004, 0.4), rot=(0, 3, 0))
    p.cyl("alien_grey", (0, -0.004, 0.06), 0.05, 0.002, n=6, axis="y")
    p.box("black", (-0.02, -0.006, 0.07), (0.03, 0.002, 0.012))
    p.box("black", (0.02, -0.006, 0.07), (0.03, 0.002, 0.012))
    p.box("alien_grey", (0, -0.005, -0.05), (0.03, 0.002, 0.12))
    p.box("paint_yellow", (-0.1, -0.005, 0.15), (0.04, 0.002, 0.04))
    return p


@piece("walldecor", "DeerTrophy")
def deer_trophy():
    p = Prop("GD_DeerTrophy_01")
    p.box("wood_dark", (0, 0.02, 0.0), (0.3, 0.03, 0.35))
    p.box("teddy", (0, -0.08, 0.02), (0.14, 0.2, 0.16), taper=0.7)
    for s in (-1, 1):
        p.box("horn_cream", (s * 0.12, -0.06, 0.18), (0.02, 0.02, 0.3), rot=(10, s * 25, 0))
    return p


@piece("walldecor", "Mirror_Wall")
def mirror_wall():
    p = Prop("GD_Mirror_Wall_01")
    p.box("wood_light", (0, 0, 0), (0.6, 0.03, 0.9))
    p.box("glass", (0, -0.016, 0), (0.52, 0.006, 0.82))
    return p


# ===== Plants (GB-02 houseplants) ==============================================================================
@piece("plants", "PottedPlant")
def potted_plant():
    p = Prop("GD_PottedPlant_01")
    p.cyl("terracotta", (0, 0, 0.12), 0.13, 0.24, n=8, top_radius=0.16)
    p.cyl("dirt", (0, 0, 0.24), 0.14, 0.01, n=8)
    for k in range(7):
        a = k * 51
        p.box("plant_green", (0.1 * math.cos(math.radians(a)), 0.1 * math.sin(math.radians(a)), 0.45 + (k % 3) * 0.06), (0.05, 0.14, 0.3), rot=(25, 0, a))
    return p


@piece("plants", "Cactus")
def cactus():
    p = Prop("GD_Cactus_01")
    p.cyl("terracotta", (0, 0, 0.06), 0.07, 0.12, n=8, top_radius=0.08)
    p.cyl("plant_green", (0, 0, 0.26), 0.05, 0.3, n=6, top_radius=0.04)
    p.cyl("plant_green", (0.07, 0, 0.27), 0.025, 0.1, n=5, axis="x")
    p.cyl("plant_green", (0.11, 0, 0.32), 0.025, 0.1, n=5)
    return p


@piece("plants", "VaseFlowers")
def vase_flowers():
    p = Prop("GD_VaseFlowers_01")
    p.cyl("clear_glass", (0, 0, 0.1), 0.06, 0.2, n=8, top_radius=0.045)
    for k, (x, y, c) in enumerate(((0, 0, "cloth_red"), (0.04, 0.02, "paint_yellow"), (-0.04, 0.02, "fabric_pink"), (0.0, -0.05, "paint_white"))):
        p.cyl("plant_green", (x, y, 0.3), 0.004, 0.2, n=3)
        p.box(c, (x, y, 0.41 + (k % 2) * 0.03), (0.06, 0.06, 0.04))
    return p


@piece("plants", "HangingPlant")
def hanging_plant():
    p = Prop("GD_HangingPlant_01")
    p.cyl("black", (0, 0, -0.25), 0.004, 0.5, n=3)
    p.cyl("terracotta", (0, 0, -0.58), 0.1, 0.16, n=8, top_radius=0.13)
    for k in range(6):
        p.box("plant_green", (0.1 * math.cos(math.radians(k * 60)), 0.1 * math.sin(math.radians(k * 60)), -0.7), (0.04, 0.04, 0.3), rot=(10, 0, k * 60))
    return p


# ===== Toys (GT-07) ============================================================================================
@piece("toys", "TeddyBear")
def teddy():
    p = Prop("GD_TeddyBear_01")
    p.box("teddy", (0, 0, 0.14), (0.16, 0.12, 0.18))
    p.box("teddy", (0, 0, 0.29), (0.12, 0.11, 0.11))
    for s in (-1, 1):
        p.box("teddy", (s * 0.07, 0, 0.35), (0.04, 0.04, 0.04))
        p.box("teddy", (s * 0.11, 0, 0.16), (0.05, 0.06, 0.13))
        p.box("teddy", (s * 0.045, -0.02, 0.04), (0.06, 0.08, 0.08))
    p.box("black", (0, -0.06, 0.29), (0.03, 0.02, 0.025))
    return p


@piece("toys", "Doll")
def doll():
    p = Prop("GD_Doll_01")
    p.box("fabric_pink", (0, 0, 0.12), (0.12, 0.07, 0.2), taper=1.4)
    p.box("skin", (0, 0, 0.27), (0.08, 0.08, 0.09))
    p.box("paint_yellow", (0, 0.01, 0.3), (0.09, 0.09, 0.05))
    for s in (-1, 1):
        p.box("skin", (s * 0.075, 0, 0.17), (0.03, 0.03, 0.12))
        p.box("skin", (s * 0.03, 0, 0.01), (0.03, 0.03, 0.06))
    return p


@piece("toys", "ToyTruck")
def toy_truck():
    p = Prop("GD_ToyTruck_01")
    p.box("paint_yellow", (0, 0.04, 0.07), (0.1, 0.18, 0.08))
    p.box("cloth_red", (0, -0.07, 0.09), (0.1, 0.08, 0.12))
    for sx in (-1, 1):
        for y in (-0.07, 0.08):
            p.cyl("rubber", (sx * 0.055, y, 0.025), 0.025, 0.02, n=6, axis="x")
    return p


@piece("toys", "Football")
def football():
    p = Prop("GD_Football_01")
    p.cyl("fabric_brown", (0, 0, 0.1), 0.1, 0.14, n=8, axis="y")                   # a prolate ball: a barrel with a cone at each end, 0.28 m long
    p.cyl("fabric_brown", (0, -0.14, 0.1), 0.1, 0.1, n=8, axis="y", top_radius=0.02, rot=(0, 0, 180))
    p.cyl("fabric_brown", (0, 0.14, 0.1), 0.1, 0.1, n=8, axis="y", top_radius=0.02)
    p.box("paper", (0, 0, 0.2), (0.012, 0.1, 0.012))                               # the laces
    return p


@piece("toys", "ToyBlocks")
def toy_blocks():
    p = Prop("GD_ToyBlocks_01")
    for x, y, z, c in ((0, 0, 0.03, "cloth_red"), (0.07, 0.01, 0.03, "truck_blue"), (0.035, 0.0, 0.09, "paint_yellow"), (-0.07, 0.05, 0.03, "tractor_green")):
        p.box(c, (x, y, z), (0.06, 0.06, 0.06))
    return p


# ===== Books and paper (GH-08) =================================================================================
@piece("paper", "BookStack")
def book_stack():
    p = Prop("GD_BookStack_01")
    z = 0.0
    for k, c in enumerate(("book_red", "book_blue", "book_green", "fabric_brown")):
        h = 0.03 + 0.01 * (k % 2)
        p.box(c, (0.01 * (k % 2), 0, z + h / 2), (0.24 - 0.01 * k, 0.17, h), rot=(0, 0, (k * 9) % 20))
        z += h
    return p


@piece("paper", "OpenBook")
def open_book():
    p = Prop("GD_OpenBook_01")
    for s in (-1, 1):
        p.box("paper", (s * 0.1, 0, 0.012), (0.2, 0.26, 0.012), rot=(0, s * 4, 0))
    p.box("book_red", (0, 0, 0.004), (0.42, 0.28, 0.008))
    return p


@piece("paper", "Newspaper")
def newspaper():
    p = Prop("GD_Newspaper_01")
    p.box("paper", (0, 0, 0.01), (0.4, 0.3, 0.02))
    p.box("black", (0, -0.1, 0.021), (0.34, 0.03, 0.002))
    p.box("fabric_grey", (0, 0.03, 0.021), (0.34, 0.14, 0.002))
    return p


@piece("paper", "MailPile")
def mail_pile():
    p = Prop("GD_MailPile_01")
    for k, (x, y, r, c) in enumerate(((0, 0, 0, "paper"), (0.01, 0.02, 12, "paint_white"), (-0.02, -0.01, -9, "paint_yellow"), (0.02, 0.0, 22, "paper"))):
        p.box(c, (x, y, 0.004 + k * 0.006), (0.23, 0.11, 0.005), rot=(0, 0, r))
    return p


# ===== Household clutter and clothing (GH-, GT-) ===============================================================
@piece("clutter", "UmbrellaStand")
def umbrella_stand():
    p = Prop("GD_UmbrellaStand_01")
    p.cyl("metal_dark", (0, 0, 0.25), 0.12, 0.5, n=8)
    for k, (x, y, r, c) in enumerate(((0.03, 0, 6, "navy"), (-0.04, 0.03, -10, "cloth_red"))):
        p.cyl(c, (x, y, 0.55), 0.02, 0.65, n=4, rot=(r, 0, 0))
    p.box("wood_dark", (0.03, 0, 0.9), (0.03, 0.03, 0.08))
    return p


@piece("clutter", "CoatHooks")
def coat_hooks():                          # against a wall, origin at the centre of the rail at 1.7 m
    p = Prop("GD_CoatHooks_01")
    p.box("wood_dark", (0, 0, 0.0), (1.0, 0.03, 0.1))
    for x in (-0.35, 0.0, 0.35):
        p.box("metal_dark", (x, -0.04, 0.0), (0.02, 0.07, 0.02))
    p.box("fabric_brown", (-0.35, -0.08, -0.45), (0.4, 0.07, 0.9), taper=0.9)
    p.box("fabric_blue", (0.0, -0.08, -0.4), (0.36, 0.06, 0.8), taper=0.9)
    p.box("tan", (0.35, -0.08, -0.35), (0.34, 0.06, 0.7), taper=0.9)
    return p


@piece("clutter", "BootsPair")
def boots_pair():
    p = Prop("GD_BootsPair_01")
    for s in (-1, 1):
        p.box("wood_dark", (s * 0.08, 0.02, 0.1), (0.1, 0.12, 0.2))
        p.box("wood_dark", (s * 0.08, -0.07, 0.04), (0.1, 0.16, 0.08))
        p.box("rubber", (s * 0.08, -0.03, 0.01), (0.105, 0.3, 0.02))
    return p


@piece("clutter", "Doormat")
def doormat():
    p = Prop("GD_Doormat_01")
    p.box("fabric_brown", (0, 0, 0.01), (0.7, 0.45, 0.02))
    p.box("fabric_mustard", (0, 0, 0.022), (0.5, 0.25, 0.004))
    return p


@piece("clutter", "TrashCan_Indoor")
def trash_can():
    p = Prop("GD_TrashCan_01")
    p.cyl("metal_galv", (0, 0, 0.2), 0.17, 0.4, n=8, top_radius=0.2)
    p.box("metal_dark", (0.0, 0.0, 0.41), (0.1, 0.02, 0.02))
    return p


@piece("clutter", "LaundryBasket")
def laundry_basket():
    p = Prop("GD_LaundryBasket_01")
    p.box("wood_light", (0, 0, 0.25), (0.5, 0.35, 0.5), taper=1.1)
    p.box("linen", (0, 0, 0.5), (0.42, 0.3, 0.08))
    p.box("fabric_blue", (0.05, 0, 0.55), (0.3, 0.2, 0.06), rot=(0, 10, 12))
    return p


@piece("clutter", "IroningBoard")
def ironing_board():
    p = Prop("GD_IroningBoard_01")
    p.box("fabric_grey", (0, 0, 0.85), (1.2, 0.32, 0.03), taper=1.0)
    for s in (-1, 1):
        p.box("metal_galv", (0.3, s * 0.1, 0.42), (0.02, 0.02, 0.85), rot=(s * 12, 0, 0))
        p.box("metal_galv", (-0.3, s * 0.1, 0.42), (0.02, 0.02, 0.85), rot=(s * -12, 0, 0))
    return p


@piece("clutter", "Broom")
def broom():
    p = Prop("GD_Broom_01")
    p.cyl("wood_light", (0, 0, 0.7), 0.014, 1.3, n=6)
    p.box("straw", (0, 0, 0.12), (0.3, 0.05, 0.24), taper=1.0)
    p.box("wood_dark", (0, 0, 0.26), (0.32, 0.06, 0.03))
    return p


@piece("clutter", "MopBucket")
def mop_bucket():
    p = Prop("GD_MopBucket_01")
    p.box("truck_blue", (0, 0, 0.17), (0.34, 0.34, 0.34), taper=1.15)
    p.cyl("wood_light", (0.05, 0.05, 0.75), 0.014, 1.2, n=6, rot=(8, 0, 0))
    p.box("paint_white", (0.05, 0.1, 0.38), (0.12, 0.12, 0.1))
    return p


@piece("clutter", "FireExtinguisher")
def fire_extinguisher():
    p = Prop("GD_FireExtinguisher_01")
    p.cyl("cloth_red", (0, 0, 0.22), 0.07, 0.44, n=8)
    p.cyl("metal_dark", (0, 0, 0.47), 0.03, 0.06, n=6)
    p.box("black", (0.04, 0, 0.5), (0.1, 0.02, 0.02))
    p.cyl("black", (0.08, 0, 0.4), 0.01, 0.18, n=4, rot=(0, 40, 0))
    return p


@piece("clutter", "FirstAidKit")
def first_aid():
    p = Prop("GD_FirstAidKit_01")
    p.box("paint_white", (0, 0, 0.0), (0.26, 0.09, 0.2))
    p.box("cloth_red", (0, -0.047, 0.0), (0.12, 0.004, 0.04))
    p.box("cloth_red", (0, -0.047, 0.0), (0.04, 0.004, 0.12))
    return p


@piece("clutter", "Toolbox")
def toolbox():
    p = Prop("GD_Toolbox_01")
    p.box("cloth_red", (0, 0, 0.1), (0.5, 0.22, 0.2))
    p.box("metal_dark", (0, 0, 0.21), (0.5, 0.04, 0.02))
    p.box("metal_dark", (0, 0, 0.27), (0.3, 0.02, 0.1), rot=(0, 0, 0))
    return p


@piece("clutter", "Flashlight")
def flashlight():
    p = Prop("GD_Flashlight_01")
    p.cyl("black", (0, 0, 0.1), 0.02, 0.18, n=6, axis="y")
    p.cyl("metal_dark", (0, -0.12, 0.1), 0.03, 0.06, n=6, axis="y", top_radius=0.03)
    p.cyl("glow_cyan", (0, -0.152, 0.1), 0.026, 0.006, n=6, axis="y")
    return p


@piece("clutter", "Thermos")
def thermos():
    p = Prop("GD_Thermos_01")
    p.cyl("tractor_green", (0, 0, 0.14), 0.045, 0.28, n=8)
    p.cyl("metal_dark", (0, 0, 0.29), 0.04, 0.04, n=8)
    return p


@piece("clutter", "Lunchbox")
def lunchbox():
    p = Prop("GD_Lunchbox_01")
    p.box("metal_galv", (0, 0, 0.09), (0.25, 0.1, 0.18))
    p.box("cloth_red", (0, 0, 0.2), (0.25, 0.1, 0.04), taper=0.85)
    p.box("metal_dark", (0, 0, 0.23), (0.14, 0.02, 0.02))
    return p


@piece("clutter", "Suitcase")
def suitcase():
    p = Prop("GD_Suitcase_01")
    p.box("fabric_brown", (0, 0, 0.25), (0.6, 0.22, 0.5))
    p.box("metal_dark", (0, -0.115, 0.4), (0.4, 0.01, 0.02))
    for s in (-1, 1):
        p.box("metal_galv", (s * 0.12, -0.115, 0.5), (0.04, 0.02, 0.02))
    p.box("black", (0, 0, 0.54), (0.16, 0.03, 0.05))
    return p


@piece("clutter", "Backpack")
def backpack():
    p = Prop("GD_Backpack_01")
    p.box("tractor_green", (0, 0, 0.2), (0.3, 0.16, 0.4), taper=0.95)
    p.box("tractor_green", (0, -0.1, 0.1), (0.24, 0.05, 0.16))
    for s in (-1, 1):
        p.box("black", (s * 0.1, 0.09, 0.22), (0.04, 0.02, 0.36))
    return p


@piece("clutter", "PicnicBasket")
def picnic_basket():
    p = Prop("GD_PicnicBasket_01")
    p.box("wood_light", (0, 0, 0.12), (0.45, 0.3, 0.24), taper=1.1)
    p.box("wood_dark", (0, 0, 0.26), (0.4, 0.26, 0.03))
    p.box("fabric_red", (0, -0.15, 0.2), (0.4, 0.01, 0.12))
    p.box("wood_dark", (0, 0, 0.35), (0.04, 0.2, 0.16), rot=(0, 90, 0))
    return p


@piece("clutter", "TinfoilPane")
def tinfoil_pane():
    p = Prop("GD_TinfoilPane_01")
    p.box("metal_galv", (0, 0, 0.0), (0.9, 0.012, 1.1))                                    # a window covered in foil
    for k in range(5):
        p.box("fabric_grey", (-0.36 + k * 0.18, -0.008, 0.0), (0.05, 0.004, 1.06), rot=(0, 0, 0))
    return p


@piece("clutter", "HandLetteredSign")
def sign():
    p = Prop("GD_HandLetteredSign_01")
    p.box("wood_grey", (0, 0, 0.0), (0.6, 0.03, 0.3))
    p.box("black", (0, -0.017, 0.06), (0.46, 0.004, 0.04))
    p.box("black", (0, -0.017, -0.04), (0.38, 0.004, 0.04))
    p.box("cloth_red", (0, -0.017, -0.1), (0.26, 0.004, 0.03))
    return p


def run():
    names = globals().get("DECOR_LIST")
    chosen = [k for k, (fn, g) in PIECES.items() if not names or k in names or g in names]
    x, row, y = 0.0, None, 0.0
    for key in chosen:
        fn, group = PIECES[key]
        if group != row:
            row, x, y = group, 0.0, y + 2.0 if row is not None else 0.0
        prop = fn()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Decor/{prop.name}.fbx")
        obj.location = (x, y, 0)
        x += max(0.4, obj.dimensions.x + 0.25)
    props_lib.write_interactions()
    print("decor done", len(chosen))


if __name__ == "__main__":
    run()
