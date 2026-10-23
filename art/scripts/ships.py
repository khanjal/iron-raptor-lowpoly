"""Alien ships, wreckage and the ship parts the crew finds (asset list GV-30/31, FM-O1..O3, GG-12, GG-13): flat faceted models.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/ships.py", run_name="__main__")
Optional global SHIP_LIST (names or group names: "parts", "ships", "debris", "tools"). Exports Assets/Art/Global/Ships/<name>.fbx.

One design language so the crew's things look like they came from the same hand: pale alien hull (`alien_grey`) with dark trim
(`metal_dark`), hexagonal sections (6-sided cylinders), and `glow_cyan` wherever there is energy. The glow swatch is the one to make
emissive in Unity, which is what lets a dropped part be found in the dark.

Parts to find are carriable: 0.2-0.9 m, each with a clear silhouette at a distance. Origin on the floor at the centre of the base.
Ships are real size (a scout 9 m, a mothership 80 m), facing -Y, origin at the centre on the ground (or the underside for flyers).
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


def lathe(p, colour, profile, n=6, cx=0.0, cy=0.0, z0=0.0):
    """A solid of revolution about the vertical axis from (height, radius) pairs, bottom to top."""
    p.loft_rings(colour, [common.ring_z(z0 + z, cx, cy, max(r, 0.0001), max(r, 0.0001), n=n) for z, r in profile])


def ring_of(p, colour, radius, count, size, z, rot_offset=0.0):
    for k in range(count):
        a = 2 * math.pi * k / count
        p.box(colour, (radius * math.cos(a), radius * math.sin(a), z), size, rot=(0, 0, math.degrees(a) + 90 + rot_offset))


# ===== Parts to find ===========================================================================================
@piece("parts", "PowerCell")
def power_cell():
    p = Prop("SH_PowerCell_01")
    lathe(p, "alien_grey", [(0.0, 0.09), (0.03, 0.12), (0.3, 0.12), (0.34, 0.09)])
    p.cyl("glow_cyan", (0, 0, 0.17), 0.075, 0.2, n=6)
    for z in (0.06, 0.28):
        p.cyl("metal_dark", (0, 0, z), 0.125, 0.025, n=6)
    p.box("metal_dark", (0, 0, 0.38), (0.16, 0.03, 0.05))
    return p


@piece("parts", "HullPanel")
def hull_panel():
    p = Prop("SH_HullPanel_01")
    for k in range(5):                                                       # a curved plate approximated by 5 tilted strips
        a = (k - 2) * 9
        x = (k - 2) * 0.17
        p.box("alien_grey", (x, 0, 0.3 - abs(k - 2) * 0.012), (0.17, 0.5, 0.03), rot=(0, a, 0))
    p.box("glow_cyan", (0, -0.1, 0.33), (0.7, 0.025, 0.018))
    p.box("alien_dark", (0.2, 0.1, 0.32), (0.22, 0.2, 0.034), rot=(0, 5, 20))      # a scorch mark
    p.box("metal_dark", (0, 0.24, 0.3), (0.75, 0.03, 0.04))
    return p


@piece("parts", "NavCrystal")
def nav_crystal():
    p = Prop("SH_NavCrystal_01")
    lathe(p, "alien_violet", [(0.18, 0.0001), (0.28, 0.1), (0.46, 0.1), (0.6, 0.0001)], n=6)
    lathe(p, "glow_cyan", [(0.26, 0.0001), (0.33, 0.05), (0.43, 0.05), (0.5, 0.0001)], n=6)
    p.cyl("metal_dark", (0, 0, 0.05), 0.12, 0.1, n=6, top_radius=0.09)
    for a in (0, 120, 240):
        p.box("metal_dark", (0.1 * math.cos(math.radians(a)), 0.1 * math.sin(math.radians(a)), 0.18), (0.03, 0.03, 0.2), rot=(0, 0, a))
    return p


@piece("parts", "EngineCoil")
def engine_coil():
    p = Prop("SH_EngineCoil_01")
    p.cyl("metal_dark", (0, 0, 0.03), 0.3, 0.06, n=6)
    ring_of(p, "alien_grey", 0.24, 12, (0.14, 0.07, 0.09), 0.2)
    ring_of(p, "glow_cyan", 0.24, 12, (0.07, 0.045, 0.05), 0.2)
    for a in (0, 120, 240):
        p.box("metal_dark", (0.24 * math.cos(math.radians(a)), 0.24 * math.sin(math.radians(a)), 0.1), (0.04, 0.04, 0.14))
    return p


@piece("parts", "ThrusterNozzle")
def thruster_nozzle():
    p = Prop("SH_ThrusterNozzle_01")
    lathe(p, "alien_grey", [(0.0, 0.3), (0.04, 0.3), (0.3, 0.18), (0.5, 0.1), (0.54, 0.12)], n=8)
    lathe(p, "alien_dark", [(0.0, 0.26), (0.02, 0.26), (0.02, 0.0001)], n=8)
    p.cyl("glow_cyan", (0, 0, 0.025), 0.12, 0.012, n=8)
    p.cyl("metal_dark", (0, 0, 0.22), 0.2, 0.03, n=8)
    return p


@piece("parts", "FuelCanister")
def fuel_canister():
    p = Prop("SH_FuelCanister_01")
    lathe(p, "alien_grey", [(0.0, 0.07), (0.04, 0.13), (0.1, 0.14), (0.4, 0.14), (0.46, 0.13), (0.5, 0.07)], n=8)
    p.cyl("alien_green", (0, 0, 0.25), 0.145, 0.1, n=8)
    p.cyl("metal_dark", (0, 0, 0.12), 0.145, 0.02, n=8)
    p.cyl("metal_dark", (0, 0, 0.38), 0.145, 0.02, n=8)
    p.box("metal_dark", (0, 0, 0.52), (0.14, 0.03, 0.04))
    return p


@piece("parts", "ShieldEmitter")
def shield_emitter():
    p = Prop("SH_ShieldEmitter_01")
    for a in (0, 120, 240):
        p.box("metal_dark", (0.12 * math.cos(math.radians(a)), 0.12 * math.sin(math.radians(a)), 0.2), (0.03, 0.03, 0.4), rot=(0, 0, a))
        p.box("alien_grey", (0.2 * math.cos(math.radians(a)), 0.2 * math.sin(math.radians(a)), 0.01), (0.12, 0.06, 0.02), rot=(0, 0, a))
    lathe(p, "glow_cyan", [(0.38, 0.0001), (0.44, 0.09), (0.52, 0.11), (0.6, 0.09), (0.66, 0.0001)], n=6)
    p.cyl("metal_dark", (0, 0, 0.4), 0.12, 0.03, n=6)
    return p


@piece("parts", "CommsArray")
def comms_array():
    p = Prop("SH_CommsArray_01")
    p.cyl("metal_dark", (0, 0, 0.3), 0.025, 0.6, n=6)
    p.cyl("metal_dark", (0, 0, 0.02), 0.14, 0.04, n=6)
    lathe(p, "alien_grey", [(0.6, 0.0001), (0.62, 0.05), (0.66, 0.24), (0.7, 0.26)], n=8, cy=-0.02)
    for a in (0, 120, 240):
        p.box("metal_dark", (0.1 * math.cos(math.radians(a)), -0.02 + 0.1 * math.sin(math.radians(a)), 0.78), (0.015, 0.015, 0.18), rot=(0, 0, a))
    p.cyl("glow_cyan", (0, -0.02, 0.88), 0.03, 0.04, n=6)
    return p


@piece("parts", "BlackBox")
def black_box():
    p = Prop("SH_BlackBox_01")
    p.box("paint_yellow", (0, 0, 0.1), (0.34, 0.22, 0.2), taper=0.95)
    p.box("black", (0, -0.112, 0.12), (0.3, 0.004, 0.05))
    p.box("glow_cyan", (0.1, -0.114, 0.12), (0.06, 0.004, 0.02))
    p.box("metal_dark", (0, 0, 0.22), (0.2, 0.04, 0.04))
    return p


@piece("parts", "WarpRingSegment")
def warp_ring():
    p = Prop("SH_WarpRingSegment_01")
    for k in range(8):
        a = math.radians(-45 + k * 12.86)
        x, z = 0.55 * math.sin(a), 0.55 * math.cos(a) - 0.4
        p.box("alien_grey", (x, 0, z + 0.4), (0.12, 0.2, 0.1), rot=(0, math.degrees(a), 0))
        p.box("glow_cyan", (x * 1.01, -0.103, z + 0.4 + 0.0), (0.08, 0.008, 0.04), rot=(0, math.degrees(a), 0))
    for s in (-1, 1):
        p.box("metal_dark", (s * 0.42, 0, 0.4), (0.06, 0.24, 0.08))
    return p


@piece("parts", "LandingLeg")
def landing_leg():
    p = Prop("SH_LandingLeg_01")
    p.box("alien_grey", (0, 0, 0.35), (0.07, 0.07, 0.8), rot=(0, 0, 0))
    p.box("metal_dark", (0.1, 0, 0.5), (0.04, 0.04, 0.45), rot=(0, -30, 0))
    p.cyl("alien_grey", (0, 0, 0.03), 0.2, 0.06, n=6, top_radius=0.12)
    p.cyl("metal_dark", (0, 0, 0.7), 0.06, 0.12, n=6)
    return p


@piece("parts", "ConsoleModule")
def console_module():
    p = Prop("SH_ConsoleModule_01")
    p.box("alien_grey", (0, 0, 0.2), (0.6, 0.4, 0.4))
    p.box("metal_dark", (0, -0.02, 0.45), (0.58, 0.34, 0.06), rot=(-25, 0, 0))
    p.box("glow_cyan", (-0.1, -0.06, 0.47), (0.28, 0.14, 0.01), rot=(-25, 0, 0))
    for k, c in enumerate(("alien_green", "cloth_red", "paint_yellow", "alien_violet")):
        p.box(c, (0.14 + (k % 2) * 0.07, -0.04 - (k // 2) * 0.07, 0.47), (0.04, 0.04, 0.015), rot=(-25, 0, 0))
    return p


@piece("parts", "Beacon")
def beacon():
    p = Prop("SH_Beacon_01")
    lathe(p, "alien_grey", [(0.0, 0.2), (0.06, 0.2), (0.1, 0.1), (0.9, 0.08), (1.0, 0.12)], n=6)
    for z in (0.3, 0.55, 0.8):
        p.cyl("glow_cyan", (0, 0, z), 0.11, 0.04, n=6)
    lathe(p, "glow_cyan", [(1.0, 0.0001), (1.06, 0.08), (1.18, 0.07), (1.3, 0.0001)], n=6)
    return p


@piece("parts", "SpecimenJar")
def specimen_jar():
    p = Prop("SH_SpecimenJar_01")
    p.cyl("glass", (0, 0, 0.15), 0.12, 0.3, n=8)
    p.cyl("metal_dark", (0, 0, 0.01), 0.125, 0.02, n=8)
    p.cyl("metal_dark", (0, 0, 0.31), 0.125, 0.03, n=8)
    p.cyl("alien_green", (0, 0, 0.12), 0.06, 0.16, n=6, top_radius=0.03)
    p.cyl("alien_green", (0.04, 0, 0.22), 0.015, 0.1, n=4)
    return p


@piece("parts", "ContainmentPod")
def containment_pod():
    p = Prop("SH_ContainmentPod_01")
    lathe(p, "alien_grey", [(0.0, 0.01), (0.06, 0.2), (0.3, 0.32), (0.9, 0.32), (1.14, 0.2), (1.2, 0.01)], n=8, z0=0.1)
    p.box("glow_cyan", (0, -0.3, 0.72), (0.3, 0.03, 0.5))
    p.box("glass", (0, -0.31, 0.72), (0.26, 0.01, 0.46))
    p.box("metal_dark", (0, 0, 0.1), (0.5, 0.5, 0.06))
    for z in (0.35, 1.0):
        p.cyl("metal_dark", (0, 0, z + 0.1), 0.325, 0.03, n=8)
    return p


@piece("tools", "RepairTool")
def repair_tool():
    p = Prop("SH_RepairTool_01")
    p.box("alien_grey", (0, 0, 0.1), (0.1, 0.28, 0.1))
    p.box("metal_dark", (0, 0.06, 0.03), (0.06, 0.07, 0.12), rot=(-15, 0, 0))
    p.cyl("metal_dark", (0, -0.2, 0.1), 0.03, 0.14, n=6, axis="y")
    p.cyl("glow_cyan", (0, -0.28, 0.1), 0.02, 0.03, n=6, axis="y")
    return p


@piece("tools", "Scanner")
def scanner():
    p = Prop("SH_Scanner_01")
    p.box("alien_grey", (0, 0, 0.1), (0.14, 0.04, 0.2))
    p.box("glow_cyan", (0, -0.022, 0.12), (0.1, 0.004, 0.1))
    p.box("metal_dark", (0, 0, 0.23), (0.04, 0.03, 0.06))
    p.cyl("glow_cyan", (0, 0, 0.27), 0.015, 0.02, n=6)
    return p


@piece("tools", "Translator")
def translator():
    p = Prop("SH_Translator_01")
    lathe(p, "alien_violet", [(0.0, 0.04), (0.05, 0.06), (0.16, 0.045), (0.2, 0.0001)], n=6)
    p.cyl("glow_cyan", (0, 0, 0.12), 0.047, 0.03, n=6)
    p.cyl("metal_dark", (0, 0, 0.02), 0.065, 0.04, n=6)
    return p


# ===== Debris =================================================================================================
@piece("debris", "HullShard_A")
def hull_shard_a():
    p = Prop("SH_HullShard_A_01")
    p.box("alien_grey", (0, 0, 0.1), (0.9, 0.5, 0.06), rot=(8, 4, 18))
    p.box("alien_dark", (0.2, 0.05, 0.14), (0.4, 0.3, 0.02), rot=(8, 4, 18))
    p.box("metal_dark", (-0.4, 0.1, 0.13), (0.1, 0.3, 0.1), rot=(0, 20, 18))
    return p


@piece("debris", "HullShard_B")
def hull_shard_b():
    p = Prop("SH_HullShard_B_01")
    p.box("alien_grey", (0, 0, 0.3), (0.12, 0.7, 0.6), rot=(0, 12, 25))
    p.box("glow_cyan", (0.04, -0.05, 0.4), (0.02, 0.5, 0.03), rot=(0, 12, 25))
    p.box("alien_dark", (0.0, 0.3, 0.1), (0.4, 0.2, 0.2), rot=(0, 0, 10))
    return p


@piece("debris", "Cable_Tangle")
def cable_tangle():
    p = Prop("SH_CableTangle_01")
    for k, (x, y, r) in enumerate(((0, 0, 20), (0.2, 0.1, -30), (-0.1, 0.2, 70), (0.1, -0.2, 110))):
        p.box("alien_violet" if k % 2 else "metal_dark", (x, y, 0.03 + k * 0.01), (0.7, 0.04, 0.04), rot=(0, 0, r))
    p.box("glow_cyan", (0.3, 0.1, 0.07), (0.1, 0.05, 0.05))
    return p


@piece("debris", "ScorchedGround")
def scorched_ground():
    p = Prop("SH_ScorchedGround_01")
    p.cyl("alien_dark", (0, 0, 0.005), 1.4, 0.01, n=10)
    p.cyl("black", (0.1, 0.1, 0.012), 0.9, 0.01, n=8)
    for k in range(6):
        a = math.radians(k * 60 + 15)
        p.box("alien_dark", (1.3 * math.cos(a), 1.3 * math.sin(a), 0.008), (0.5, 0.12, 0.01), rot=(0, 0, math.degrees(a)))
    return p


# ===== Ships ===================================================================================================
@piece("ships", "Scout")
def scout():
    p = Prop("SH_Scout_01")
    lathe(p, "alien_grey", [(0.8, 0.5), (1.0, 3.6), (1.5, 4.6), (2.1, 3.8), (2.7, 2.6), (3.3, 1.4), (3.7, 0.6)], n=12)
    lathe(p, "glass", [(3.2, 1.45), (3.5, 1.0), (3.8, 0.0001)], n=12)
    lathe(p, "metal_dark", [(1.35, 4.2), (1.6, 4.45)], n=12)
    lathe(p, "glow_cyan", [(2.15, 3.6), (2.35, 3.4)], n=12)
    for a in (30, 150, 270):                                                   # three landing legs
        x, y = 2.6 * math.cos(math.radians(a)), 2.6 * math.sin(math.radians(a))
        p.box("metal_dark", (x, y, 0.4), (0.18, 0.18, 0.8))
        p.cyl("alien_grey", (x, y, 0.04), 0.5, 0.08, n=6)
    return p


@piece("ships", "Dart")
def dart():
    p = Prop("SH_Dart_01")
    rings = [common.ring_y(y, 0, z, w, h, n=4, p=3.0) for y, z, w, h in
             ((3.0, 1.0, 1.4, 0.3), (1.0, 1.1, 1.8, 0.45), (-1.2, 1.05, 0.9, 0.42), (-2.6, 1.0, 0.2, 0.12))]
    p.loft_rings("alien_grey", rings)
    for s in (-1, 1):
        p.box("alien_grey", (s * 1.7, 1.2, 1.0), (1.6, 1.8, 0.07), rot=(0, 0, s * -25))
        p.box("glow_cyan", (s * 0.4, 3.0, 1.0), (0.3, 0.1, 0.15))
    p.box("glass", (0, -0.4, 1.38), (0.5, 1.0, 0.18), rot=(-8, 0, 0))
    p.box("metal_dark", (0, 2.6, 1.0), (0.14, 0.9, 0.5), rot=(0, 0, 0))
    return p


@piece("ships", "Cigar")
def cigar():
    p = Prop("SH_Cigar_01")
    p.loft_rings("alien_grey", [common.ring_y(y, 0, 3.0, r, r, n=8) for y, r in
                                ((-9.0, 0.15), (-7.0, 1.3), (-3.0, 1.9), (3.0, 1.9), (7.0, 1.3), (9.0, 0.15))])
    for k in range(7):
        for s in (-1, 1):
            p.box("glow_cyan", (s * 1.87, -5.4 + k * 1.8, 3.1), (0.04, 0.6, 0.3))
    p.box("metal_dark", (0, 0, 4.9), (0.2, 7.0, 0.2))
    p.box("glow_cyan", (0, 9.0, 3.0), (0.6, 0.15, 0.6))
    return p


@piece("ships", "Triangle")
def triangle():
    p = Prop("SH_Triangle_01")
    from mathutils import Vector
    tri = lambda z, k: [Vector((0, -6.0 * k, z)), Vector((5.5 * k, 4.5 * k, z)), Vector((-5.5 * k, 4.5 * k, z)), Vector((0, 0.0, z + 0.01))]
    p.loft_rings("shadow", [tri(1.0, 1.0), tri(1.5, 0.97), tri(2.0, 0.6)])
    for (x, y) in ((0, -5.0), (4.7, 3.8), (-4.7, 3.8)):
        p.cyl("paint_white", (x, y, 0.95), 0.35, 0.1, n=6)
    p.cyl("glow_cyan", (0, 1.0, 0.95), 0.9, 0.1, n=6)
    return p


@piece("ships", "EscapePod")
def escape_pod():
    p = Prop("SH_EscapePod_01")
    lathe(p, "alien_grey", [(0.35, 0.01), (0.5, 0.55), (1.0, 0.9), (1.6, 0.75), (2.1, 0.3), (2.3, 0.01)], n=8)
    p.box("glow_cyan", (0, -0.82, 1.2), (0.5, 0.05, 0.7), rot=(-8, 0, 0))
    p.box("glass", (0, -0.84, 1.2), (0.44, 0.02, 0.62), rot=(-8, 0, 0))
    for a in (60, 180, 300):
        p.box("metal_dark", (0.8 * math.cos(math.radians(a)), 0.8 * math.sin(math.radians(a)), 0.3), (0.12, 0.12, 0.6), rot=(0, 0, a))
    return p


@piece("ships", "ProbeDrone")
def probe_drone():
    p = Prop("SH_ProbeDrone_01")
    lathe(p, "alien_grey", [(0.0, 0.0001), (0.15, 0.3), (0.45, 0.4), (0.75, 0.3), (0.9, 0.0001)], n=8, z0=1.0)
    for k in range(6):
        a = k * 60
        p.cyl("metal_dark", (0.42 * math.cos(math.radians(a)), 0.42 * math.sin(math.radians(a)), 1.45), 0.03, 0.4, n=4, top_radius=0.005,
              rot=(0, 0, 0))
    p.cyl("glow_cyan", (0, -0.36, 1.45), 0.1, 0.08, n=6, axis="y")
    p.cyl("metal_dark", (0, 0, 0.9), 0.12, 0.2, n=6, top_radius=0.04)
    return p


@piece("ships", "DropShip")
def drop_ship():
    p = Prop("SH_DropShip_01")
    p.box("alien_grey", (0, 0, 1.6), (3.2, 7.0, 2.2), taper=0.9)
    p.box("alien_grey", (0, -3.7, 1.5), (2.6, 1.2, 1.5), taper=0.5)
    p.box("glass", (0, -4.0, 2.0), (1.6, 0.3, 0.7), rot=(-20, 0, 0))
    for s in (-1, 1):
        p.box("alien_grey", (s * 2.8, 1.0, 1.7), (2.4, 3.0, 0.12), rot=(0, 0, s * -10))
        p.cyl("metal_dark", (s * 3.4, 1.5, 1.6), 0.55, 2.2, n=8, axis="y")
        p.cyl("glow_cyan", (s * 3.4, 2.65, 1.6), 0.4, 0.06, n=8, axis="y")
        p.box("metal_dark", (s * 1.5, -1.0, 0.4), (0.14, 0.14, 0.8))
        p.box("metal_dark", (s * 1.5, 2.2, 0.4), (0.14, 0.14, 0.8))
    p.box("glow_cyan", (0, 3.55, 1.5), (1.2, 0.08, 0.7))
    return p


@piece("ships", "MIBCraft")
def mib_craft():
    p = Prop("SH_MIBCraft_01")
    rings = [common.ring_y(y, 0, 2.5, w, h, n=6, p=3.0) for y, w, h in ((-4.0, 0.15, 0.1), (-1.0, 2.6, 0.55), (2.5, 3.0, 0.6), (4.0, 1.4, 0.3))]
    p.loft_rings("shadow", rings)
    for s in (-1, 1):
        p.cyl("paint_white", (s * 2.5, 1.0, 2.0), 0.18, 0.06, n=6)
    p.cyl("glow_cyan", (0, 0.0, 1.96), 0.5, 0.06, n=6)
    p.box("black", (0, 3.9, 2.5), (1.6, 0.2, 0.2))
    return p


@piece("ships", "Mothership")
def mothership():
    p = Prop("SH_Mothership_01")
    lathe(p, "alien_grey", [(0.0, 6.0), (2.0, 34.0), (5.0, 40.0), (9.0, 32.0), (13.0, 18.0), (17.0, 8.0)], n=16, z0=0)
    lathe(p, "metal_dark", [(2.5, 38.0), (4.0, 39.5)], n=16)
    lathe(p, "glow_cyan", [(6.5, 36.0), (7.5, 35.0)], n=16)
    lathe(p, "alien_grey", [(17.0, 2.5), (30.0, 1.5), (34.0, 0.0001)], n=8)
    lathe(p, "glow_cyan", [(30.0, 1.6), (31.5, 1.7), (33.0, 0.5)], n=8)
    for k in range(12):
        a = math.radians(k * 30)
        p.box("glow_cyan", (30.0 * math.cos(a), 30.0 * math.sin(a), 2.5), (1.6, 0.5, 0.5), rot=(0, 0, math.degrees(a)))
    return p


def run():
    names = globals().get("SHIP_LIST")
    chosen = [k for k, (fn, g) in PIECES.items() if not names or k in names or g in names]
    y, row, x = 0.0, None, 0.0
    for key in chosen:
        fn, group = PIECES[key]
        if group != row:
            row, x, y = group, 0.0, (y + 90.0 if group == "ships" else y + 3.0) if row is not None else 0.0
        prop = fn()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Ships/{prop.name}.fbx")
        obj.location = (x, y, 0)
        x += max(0.8, obj.dimensions.x + (3.0 if group == "ships" else 0.4))
    print("ships done", len(chosen))


run()
