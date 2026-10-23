"""The modular building kit (asset list section 4.12, GK-): wall, floor, roof, door, window, stair and trim pieces on a 3 m grid.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/kit.py", run_name="__main__")
Optional globals: KIT_LIST (piece names or group names) and SKIN_LIST (skin names). Exports Assets/Art/Global/Kit/<name>.fbx.

Metrics follow docs/levels/farmstead.md: doors 1.2 x 2.2 m, ceilings 2.7 m, stairs 0.18 high x 0.28 deep x 1.0 wide, corridors at least
1.5 m. Floor pieces have their origin on the walking surface (the slab hangs below it), so anything placed at z = 0 stands on them, walls included.
Every wall piece is 3.0 m long (half wall 1.5 m), 2.7 m high, lying along X with its origin at the bottom centre; the exterior
faces -Y. Rotate pieces in Unity to build any plan. Doors and windows are separate pieces: the wall pieces leave a framed gap, and
door leaves have their pivot on the hinge edge at floor level so they can swing.

Skins re-colour the same geometry: clapboard (white house), barn (red board), corrugated (metal shed), brick (town) and concrete
(base and lab), plus interior (thin partitions, wallpaper). Wall, floor, roof and trim pieces are exported once per skin
(GK_Wall_Door_Clapboard_01.fbx); doors, windows, stairs and fittings once.
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
wall_run = props_lib.wall_run

W, H = 3.0, 2.7                                       # module length and wall height

SKINS = {   # wall colour, trim colour, roof colour, thickness, floor colour
    "Clapboard": dict(wall="paint_white", trim="paint_white", roof="metal_dark", thick=0.25, floor="wood_light"),
    "Barn": dict(wall="barn_red", trim="paint_white", roof="metal_galv", thick=0.25, floor="wood_grey"),
    "Corrugated": dict(wall="metal_galv", trim="metal_dark", roof="metal_galv", thick=0.2, floor="concrete"),
    "Brick": dict(wall="brick", trim="paint_white", roof="metal_dark", thick=0.3, floor="concrete"),
    "Concrete": dict(wall="concrete", trim="metal_dark", roof="concrete", thick=0.3, floor="concrete"),
    "Interior": dict(wall="wallpaper", trim="wood_dark", roof="wallpaper", thick=0.12, floor="wood_light"),
}

SKINNED = {}      # name -> (fn(skin) -> Prop, group)
PLAIN = {}        # name -> (fn() -> Prop, group)


def skinned(group, name):
    def deco(fn):
        SKINNED[name] = (fn, group)
        return fn
    return deco


def plain(group, name):
    def deco(fn):
        PLAIN[name] = (fn, group)
        return fn
    return deco


def _wall(p, sk, openings=(), length=W, height=H):
    wall_run(p, sk["wall"], (-length / 2, 0), (length / 2, 0), 0, height, openings, thick=sk["thick"], trim=sk["trim"], fill=False)


# ===== Structure: walls ========================================================================================
@skinned("walls", "Wall_Solid")
def wall_solid(sk):
    p = Prop("GK_Wall_Solid")
    _wall(p, sk)
    return p


@skinned("walls", "Wall_Door")
def wall_door(sk):
    p = Prop("GK_Wall_Door")
    _wall(p, sk, [(0.9, 1.2, 0, 2.2)])
    return p


@skinned("walls", "Wall_Window")
def wall_window(sk):
    p = Prop("GK_Wall_Window")
    _wall(p, sk, [(1.0, 1.0, 0.9, 1.2)])
    return p


@skinned("walls", "Wall_DoubleWindow")
def wall_double_window(sk):
    p = Prop("GK_Wall_DoubleWindow")
    _wall(p, sk, [(0.3, 1.0, 0.9, 1.2), (1.7, 1.0, 0.9, 1.2)])
    return p


@skinned("walls", "Wall_WideGap")
def wall_wide_gap(sk):
    p = Prop("GK_Wall_WideGap")
    _wall(p, sk, [(0.3, 2.4, 0, 2.2)])
    return p


@skinned("walls", "Wall_Half")
def wall_half(sk):
    p = Prop("GK_Wall_Half")
    _wall(p, sk, length=1.5)
    return p


@skinned("walls", "Wall_Low")
def wall_low(sk):                                                    # a half-height wall: porch walls, knee walls, counters
    p = Prop("GK_Wall_Low")
    _wall(p, sk, height=1.1)
    return p


@skinned("walls", "Corner_Post")
def corner_post(sk):
    p = Prop("GK_Corner_Post")
    t = sk["thick"] + 0.06
    p.box(sk["trim"], (0, 0, H / 2), (t, t, H))
    return p


@skinned("walls", "Pillar_T")
def pillar_t(sk):                                                    # where a partition meets another wall
    p = Prop("GK_Pillar_T")
    t = sk["thick"]
    p.box(sk["wall"], (0, 0, H / 2), (t * 1.6, t * 1.6, H))
    p.box(sk["trim"], (0, 0, 0.1), (t * 1.7, t * 1.7, 0.2))
    return p


# ===== Structure: floors, ceilings, foundation =================================================================
@skinned("floors", "Floor_Tile")
def floor_tile(sk):
    p = Prop("GK_Floor_Tile")
    p.box(sk["floor"], (0, 0, -0.075), (W, W, 0.15))
    return p


@skinned("floors", "Floor_Planks")
def floor_planks(sk):
    p = Prop("GK_Floor_Planks")
    for k in range(6):
        p.box(sk["floor"] if k % 2 else "wood_dark", (0, -1.25 + k * 0.5, -0.075), (W, 0.49, 0.15))
    return p


@skinned("floors", "Ceiling_Tile")
def ceiling_tile(sk):                                                # origin at the ceiling plane, hangs below it
    p = Prop("GK_Ceiling_Tile")
    p.box(sk["roof"] if sk["roof"] != "metal_dark" else "paint_white", (0, 0, -0.04), (W, W, 0.08))
    return p


@skinned("floors", "Foundation_Block")
def foundation_block(sk):
    p = Prop("GK_Foundation_Block")
    p.box("concrete", (0, 0, 0.2), (W, 0.5, 0.6))
    return p


@skinned("floors", "Loft_Floor")
def loft_floor(sk):
    p = Prop("GK_Loft_Floor")
    p.box("wood_grey", (0, 0, -0.1), (W, W, 0.2))
    for x in (-1.2, 0, 1.2):
        p.box("wood_dark", (x, 0, -0.3), (0.2, W, 0.2))
    return p


@skinned("floors", "Beam")
def beam(sk):
    p = Prop("GK_Beam")
    p.box("wood_dark", (0, 0, 0.0), (W, 0.2, 0.28))
    return p


# ===== Structure: roof =========================================================================================
@skinned("roof", "Roof_Slope")
def roof_slope(sk):                                                  # one 3 m x 4 m pitch panel at 35 degrees, origin at its lower edge
    p = Prop("GK_Roof_Slope")
    p.box(sk["roof"], (0, 1.64, 1.15), (W + 0.05, 4.0, 0.1), rot=(-35, 0, 0))
    p.box("wood_dark", (0, 0.0, 0.0), (W + 0.05, 0.1, 0.18))                     # fascia
    return p


@skinned("roof", "Roof_Ridge")
def roof_ridge(sk):
    p = Prop("GK_Roof_Ridge")
    p.box(sk["trim"] if sk["roof"] == "metal_dark" else "metal_dark", (0, 0, 0.0), (W, 0.34, 0.12), rot=(0, 0, 0))
    p.box(sk["roof"], (0, 0, -0.1), (W, 0.2, 0.1))
    return p


@skinned("roof", "Gable_End")
def gable_end(sk):                                                   # a triangular wall for the end of a 6 m wide building
    p = Prop("GK_Gable_End")
    from mathutils import Vector
    t = sk["thick"] / 2
    tri = lambda y: [Vector((-3.0, y, 0)), Vector((0, y, 2.1)), Vector((3.0, y, 0)), Vector((0, y, 0.001))]
    p.loft_rings(sk["wall"], [tri(-t), tri(t)])
    return p


@skinned("roof", "Eave_Gutter")
def eave_gutter(sk):
    p = Prop("GK_Eave_Gutter")
    p.box("metal_galv", (0, 0, 0.0), (W, 0.12, 0.08))
    p.box("metal_dark", (0, 0.04, -0.04), (W, 0.04, 0.06))
    return p


# ===== Doors and windows (separate pieces) =====================================================================
def _leaf(p, w, h, colour, trim="wood_dark", panels=True):
    p.box(colour, (w / 2, 0, h / 2), (w, 0.06, h))                                  # hinge edge at x = 0
    if panels:
        for z0, z1 in ((0.1, h * 0.45), (h * 0.5, h - 0.1)):
            p.box(trim, (w / 2, -0.034, (z0 + z1) / 2), (w - 0.3, 0.012, z1 - z0 - 0.05))
    p.box("metal_galv", (w - 0.1, -0.05, 1.0), (0.04, 0.04, 0.04))


@plain("doors", "Door_Interior")
def door_interior():
    p = Prop("GK_Door_Interior")
    _leaf(p, 1.1, 2.1, "wood_light")
    return p


@plain("doors", "Door_Exterior")
def door_exterior():
    p = Prop("GK_Door_Exterior")
    _leaf(p, 1.1, 2.1, "wood_dark", trim="wood_light")
    p.box("glass", (0.55, -0.036, 1.7), (0.5, 0.01, 0.3))
    return p


@plain("doors", "Door_Screen")
def door_screen():
    p = Prop("GK_Door_Screen")
    for x0, x1, z0, z1 in ((0, 1.1, 0, 0.1), (0, 1.1, 2.0, 2.1), (0, 0.1, 0, 2.1), (1.0, 1.1, 0, 2.1), (0, 1.1, 0.95, 1.05)):
        p.box("wood_light", ((x0 + x1) / 2, 0, (z0 + z1) / 2), (x1 - x0, 0.04, z1 - z0))
    p.box("fabric_grey", (0.55, 0, 1.5), (0.95, 0.004, 0.9))
    p.box("fabric_grey", (0.55, 0, 0.5), (0.95, 0.004, 0.85))
    return p


@plain("doors", "Door_Double")
def door_double():
    p = Prop("GK_Door_Double")
    for s in (-1, 1):
        p.box("wood_dark", (s * 0.6, 0, 1.05), (1.2, 0.06, 2.1))
        p.box("wood_light", (s * 0.6, -0.034, 1.05), (0.9, 0.012, 1.8))
        p.box("metal_galv", (s * 0.08, -0.05, 1.0), (0.04, 0.04, 0.2))
    return p


@plain("doors", "Door_BarnSliding")
def door_barn_sliding():                                                # one 4 x 5 m leaf of the big doors
    p = Prop("GK_Door_BarnSliding")
    p.box("barn_red", (0, 0, 2.5), (4.0, 0.12, 5.0))
    p.box("paint_white", (0, -0.07, 0.1), (4.0, 0.03, 0.2))
    p.box("paint_white", (0, -0.07, 4.9), (4.0, 0.03, 0.2))
    p.box("paint_white", (-1.95, -0.07, 2.5), (0.1, 0.03, 5.0))
    p.box("paint_white", (1.95, -0.07, 2.5), (0.1, 0.03, 5.0))
    p.box("paint_white", (0, -0.07, 2.5), (4.2, 0.03, 0.14), rot=(0, 51, 0))
    p.box("metal_dark", (0, 0.08, 5.15), (4.0, 0.1, 0.1))                        # the track hanger
    p.box("metal_dark", (1.7, -0.08, 1.0), (0.1, 0.06, 0.3))
    return p


@plain("doors", "Door_Garage")
def door_garage():
    p = Prop("GK_Door_Garage")
    for k in range(5):
        p.box("paint_white", (0, 0, 0.2 + k * 0.4), (2.6, 0.05, 0.38))
    for x in (-0.6, 0.6):
        p.box("glass", (x, -0.027, 1.75), (0.5, 0.01, 0.2))
    return p


@plain("doors", "Door_StormCellar")
def door_storm_cellar():                                                # two slanted doors over the cellar stairs, origin at the lower edge
    p = Prop("GK_Door_StormCellar")
    for s in (-1, 1):
        p.box("wood_grey", (s * 0.55, 0.62, 0.38), (1.05, 1.3, 0.07), rot=(-18, 0, 0))
        p.box("wood_dark", (s * 0.55, 0.62, 0.43), (1.0, 0.1, 0.05), rot=(-18, 0, 0))
        p.box("metal_dark", (s * 0.12, 1.0, 0.5), (0.05, 0.12, 0.04), rot=(-18, 0, 0))
    p.box("concrete", (0, 0, 0.1), (2.4, 0.2, 0.2))
    p.box("concrete", (-1.2, 0.65, 0.2), (0.2, 1.4, 0.4))
    p.box("concrete", (1.2, 0.65, 0.2), (0.2, 1.4, 0.4))
    return p


@plain("doors", "Door_Loft")
def door_loft():
    p = Prop("GK_Door_Loft")
    for s in (-1, 1):
        p.box("barn_red", (s * 0.5, 0, 1.0), (1.0, 0.07, 2.0))
        p.box("paint_white", (s * 0.5, -0.04, 1.0), (0.8, 0.012, 1.8), rot=(0, 0, 0))
    p.box("metal_dark", (0, -0.08, 1.0), (0.04, 0.04, 0.3))
    return p


@plain("windows", "Window_Single")
def window_single():
    p = Prop("GK_Window_Single")
    p.box("clear_glass", (0, 0, 0.6), (0.9, 0.04, 1.1))
    for x in (-0.46, 0.46):
        p.box("paint_white", (x, 0, 0.6), (0.08, 0.1, 1.2))
    for z in (0.02, 1.18):
        p.box("paint_white", (0, 0, z), (1.0, 0.1, 0.08))
    p.box("paint_white", (0, 0, 0.6), (0.04, 0.08, 1.1))
    p.box("paint_white", (0, 0, 0.6), (0.9, 0.08, 0.04))
    return p


@plain("windows", "Window_Double")
def window_double():
    p = Prop("GK_Window_Double")
    p.box("clear_glass", (0, 0, 0.6), (1.9, 0.04, 1.1))
    for x in (-0.96, 0.0, 0.96):
        p.box("paint_white", (x, 0, 0.6), (0.08, 0.1, 1.2))
    for z in (0.02, 1.18):
        p.box("paint_white", (0, 0, z), (2.0, 0.1, 0.08))
    return p


@plain("windows", "Window_Sash")
def window_sash():
    p = Prop("GK_Window_Sash")
    p.box("clear_glass", (0, 0, 0.3), (0.9, 0.03, 0.54))
    p.box("clear_glass", (0, -0.03, 0.9), (0.9, 0.03, 0.54))
    for z in (0.02, 0.6, 1.18):
        p.box("wood_dark", (0, 0, z), (1.0, 0.1, 0.07))
    for x in (-0.47, 0.47):
        p.box("wood_dark", (x, 0, 0.6), (0.07, 0.1, 1.2))
    return p


@plain("windows", "Window_Broken")
def window_broken():
    p = Prop("GK_Window_Broken")
    p.box("wood_dark", (-0.46, 0, 0.6), (0.08, 0.1, 1.2))
    p.box("wood_dark", (0.46, 0, 0.6), (0.08, 0.1, 1.2))
    for z in (0.02, 1.18):
        p.box("wood_dark", (0, 0, z), (1.0, 0.1, 0.08))
    for k, (x, z, w, h, r) in enumerate(((-0.3, 0.2, 0.3, 0.3, 10), (0.35, 1.0, 0.25, 0.28, -15), (0.3, 0.3, 0.2, 0.2, 30))):
        p.box("clear_glass", (x, 0, z), (w, 0.02, h), rot=(0, r, 0))
    return p


@plain("windows", "Shutter_Pair")
def shutters():
    p = Prop("GK_Shutter_Pair")
    for s in (-1, 1):
        p.box("tractor_green", (s * 0.75, 0, 0.6), (0.45, 0.04, 1.2))
        for k in range(8):
            p.box("leaf_dark", (s * 0.75, -0.025, 0.12 + k * 0.14), (0.4, 0.01, 0.07))
    return p


@plain("windows", "Awning")
def awning():
    p = Prop("GK_Awning")
    p.box("fabric_red", (0, -0.5, 0.0), (1.4, 1.1, 0.04), rot=(18, 0, 0))
    for x in (-0.65, 0.65):
        p.box("metal_dark", (x, -0.45, -0.2), (0.03, 0.9, 0.03), rot=(25, 0, 0))
    return p


# ===== Circulation =============================================================================================
def _stairs(p, steps, rise, run, width, colour="wood_light", stringer="wood_dark"):
    for k in range(steps):
        p.box(colour, (0, -k * run - run / 2, rise * (k + 1) - 0.02), (width, run, 0.05))                     # tread
        p.box(colour, (0, -k * run, rise * k + rise / 2), (width, 0.03, rise))                                  # riser
    for s in (-1, 1):
        p.box(stringer, (s * (width / 2 + 0.03), -steps * run / 2, steps * rise / 2), (0.06, steps * run * 1.1, 0.25),
              rot=(-math.degrees(math.atan2(rise, run)), 0, 0))


@plain("circulation", "Stairs_Run")
def stairs_run():                                                        # 15 steps, 2.7 m rise, runs toward -Y, origin at the foot
    p = Prop("GK_Stairs_Run")
    _stairs(p, 15, 0.18, 0.28, 1.0)
    return p


@plain("circulation", "Stairs_Cellar")
def stairs_cellar():
    p = Prop("GK_Stairs_Cellar")
    _stairs(p, 13, 0.18, 0.26, 0.9, colour="concrete", stringer="concrete")
    return p


@plain("circulation", "Stairs_Porch")
def stairs_porch():
    p = Prop("GK_Stairs_Porch")
    for k in range(3):
        p.box("wood_grey", (0, -k * 0.3 - 0.15, 0.17 * k + 0.085), (1.4, 0.3, 0.17))
    return p


@plain("circulation", "Ladder")
def ladder():
    p = Prop("GK_Ladder")
    for s in (-1, 1):
        p.box("wood_light", (s * 0.22, 0, 1.35), (0.06, 0.05, 2.7), rot=(0, 0, 0))
    for k in range(9):
        p.box("wood_dark", (0, 0, 0.25 + k * 0.28), (0.4, 0.04, 0.04))
    return p


@plain("circulation", "Ramp")
def ramp():
    p = Prop("GK_Ramp")
    p.box("wood_grey", (0, -1.0, 0.25), (1.2, 2.1, 0.06), rot=(14, 0, 0))
    for s in (-1, 1):
        p.box("wood_dark", (s * 0.6, -1.0, 0.25), (0.05, 2.1, 0.18), rot=(14, 0, 0))
    return p


@plain("circulation", "Handrail")
def handrail():
    p = Prop("GK_Handrail")
    p.box("wood_dark", (0, 0, 0.9), (W, 0.07, 0.05))
    for k in range(4):
        p.box("wood_dark", (-1.4 + k * 0.93, 0, 0.45), (0.05, 0.05, 0.9))
    return p


# ===== Trim and exterior details ===============================================================================
@skinned("trim", "Skirting")
def skirting(sk):
    p = Prop("GK_Skirting")
    p.box("wood_dark" if sk["trim"] == "paint_white" else sk["trim"], (0, 0, 0.06), (W, 0.03, 0.12))
    return p


@skinned("trim", "Porch_Rail")
def porch_rail(sk):
    p = Prop("GK_Porch_Rail")
    p.box(sk["trim"], (0, 0, 0.95), (W, 0.1, 0.08))
    p.box(sk["trim"], (0, 0, 0.12), (W, 0.1, 0.08))
    for k in range(12):
        p.box(sk["trim"], (-1.375 + k * 0.25, 0, 0.5), (0.05, 0.05, 0.8))
    return p


@skinned("trim", "Chimney")
def chimney(sk):
    p = Prop("GK_Chimney")
    p.box("brick", (0, 0, 2.0), (1.0, 1.0, 4.0))
    p.box("concrete", (0, 0, 4.05), (1.2, 1.2, 0.1))
    p.box("black", (0, 0, 4.12), (0.7, 0.7, 0.06))
    return p


@skinned("trim", "Vent")
def vent(sk):
    p = Prop("GK_Vent")
    p.box(sk["trim"], (0, 0, 0.0), (0.6, 0.05, 0.4))
    for k in range(5):
        p.box("metal_dark", (0, -0.03, -0.14 + k * 0.07), (0.5, 0.02, 0.03))
    return p


@plain("trim", "Skylight")
def skylight():
    p = Prop("GK_Skylight")
    p.box("metal_dark", (0, 0, 0.1), (1.0, 1.0, 0.2))
    p.box("clear_glass", (0, 0, 0.22), (0.86, 0.86, 0.03))
    return p


@plain("trim", "FloorGrate")
def floor_grate():
    p = Prop("GK_FloorGrate")
    p.box("metal_dark", (0, 0, 0.01), (0.6, 0.6, 0.02))
    for k in range(7):
        p.box("black", (0, -0.24 + k * 0.08, 0.021), (0.56, 0.03, 0.004))
    return p


def run():
    names = globals().get("KIT_LIST")
    skins = globals().get("SKIN_LIST") or list(SKINS)
    x, y, row = 0.0, 0.0, None
    count = 0
    for key, (fn, group) in SKINNED.items():
        if names and key not in names and group not in names:
            continue
        for si, sname in enumerate(skins):
            prop = fn(SKINS[sname])
            prop.name = f"{prop.name}_{sname}_01"
            obj, coll = prop.finish()
            common.export_fbx(coll, f"Assets/Art/Global/Kit/{prop.name}.fbx")
            obj.location = (si * 3.6, y, 0)
            count += 1
        y += 4.0
    for key, (fn, group) in PLAIN.items():
        if names and key not in names and group not in names:
            continue
        prop = fn()
        prop.name = f"{prop.name}_01"
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Kit/{prop.name}.fbx")
        obj.location = (x, y + 4.0, 0)
        x += max(1.6, obj.dimensions.x + 0.8)
        count += 1
    print("kit done", count)


run()
