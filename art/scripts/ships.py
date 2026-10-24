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
        p.box("alien_grey", (x, 0, 0.065 - abs(k - 2) * 0.012), (0.17, 0.5, 0.03), rot=(0, a, 0))
    p.box("glow_cyan", (0, -0.1, 0.095), (0.7, 0.025, 0.018))
    p.box("alien_dark", (0.2, 0.1, 0.085), (0.22, 0.2, 0.034), rot=(0, 5, 20))      # a scorch mark
    p.box("metal_dark", (0, 0.24, 0.065), (0.75, 0.03, 0.04))
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
        x, z = 0.55 * math.sin(a), 0.55 * math.cos(a) - 0.7
        p.box("alien_grey", (x, 0, z + 0.4), (0.12, 0.2, 0.1), rot=(0, math.degrees(a), 0))
        p.box("glow_cyan", (x * 1.01, -0.103, z + 0.4 + 0.0), (0.08, 0.008, 0.04), rot=(0, math.degrees(a), 0))
    for s in (-1, 1):
        p.box("metal_dark", (s * 0.42, 0, 0.1), (0.06, 0.24, 0.08))
    return p


@piece("parts", "LandingLeg")
def landing_leg():
    p = Prop("SH_LandingLeg_01")
    p.box("alien_grey", (0, 0, 0.4), (0.07, 0.07, 0.8), rot=(0, 0, 0))
    p.box("metal_dark", (0.1, 0, 0.55), (0.04, 0.04, 0.45), rot=(0, -30, 0))
    p.cyl("alien_grey", (0, 0, 0.08), 0.2, 0.06, n=6, top_radius=0.12)
    p.cyl("metal_dark", (0, 0, 0.75), 0.06, 0.12, n=6)
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
    p.cyl("clear_glass", (0, 0, 0.15), 0.12, 0.3, n=8)
    p.cyl("metal_dark", (0, 0, 0.01), 0.125, 0.02, n=8)
    p.cyl("metal_dark", (0, 0, 0.31), 0.125, 0.03, n=8)
    p.cyl("alien_green", (0, 0, 0.12), 0.06, 0.16, n=6, top_radius=0.03)
    p.cyl("alien_green", (0.04, 0, 0.22), 0.015, 0.1, n=4)
    return p


@piece("parts", "ContainmentPod")
def containment_pod():
    p = Prop("SH_ContainmentPod_01")
    lathe(p, "alien_grey", [(0.0, 0.01), (0.06, 0.2), (0.3, 0.32), (0.9, 0.32), (1.14, 0.2), (1.2, 0.01)], n=8, z0=0.03)
    p.box("glow_cyan", (0, -0.3, 0.65), (0.3, 0.03, 0.5))
    p.box("clear_glass", (0, -0.31, 0.65), (0.26, 0.01, 0.46))
    p.box("metal_dark", (0, 0, 0.03), (0.5, 0.5, 0.06))
    for z in (0.35, 1.0):
        p.cyl("metal_dark", (0, 0, z + 0.03), 0.325, 0.03, n=8)
    return p


@piece("tools", "RepairTool")
def repair_tool():
    p = Prop("SH_RepairTool_01")
    p.box("alien_grey", (0, 0, 0.14), (0.1, 0.28, 0.1))
    p.box("metal_dark", (0, 0.06, 0.07), (0.06, 0.07, 0.12), rot=(-15, 0, 0))
    p.cyl("metal_dark", (0, -0.2, 0.14), 0.03, 0.14, n=6, axis="y")
    p.cyl("glow_cyan", (0, -0.28, 0.14), 0.02, 0.03, n=6, axis="y")
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


# ===== Helpers for the ships (#356: more detail, same palette) ===================================================================
def surf(profile, z):
    """The radius of a (z, r) hull profile at height z (linear between its points)."""
    if z <= profile[0][0]:
        return profile[0][1]
    for (z0, r0), (z1, r1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0) if z1 > z0 else r0
    return profile[-1][1]


def band(p, colour, profile, z, h=0.12, out=0.05, n=16):
    """A thin ring standing a little proud of a hull of revolution at height z: a panel line, a rim, a glow strip. Capped, so its end discs cut
    into the hull (an open skin would float `out` metres off it)."""
    zs = [z - h / 2] + [pz for pz, _ in profile if z - h / 2 < pz < z + h / 2] + [z + h / 2]          # one ring at every profile point in its height
    p.loft_rings(colour, [common.ring_z(q, 0, 0, surf(profile, q) + out, surf(profile, q) + out, n=n) for q in zs], cap=True)


def seams(p, colour, profile, z0, z1, count, w=0.1):
    """Radial seams between two heights of a hull of revolution (the count must divide the hull's sides so they sit on its edges)."""
    r0, r1 = surf(profile, z0), surf(profile, z1)
    for k in range(count):
        a = math.radians(k * 360.0 / count)
        props_lib.rod(p, colour, (r0 * math.cos(a), r0 * math.sin(a), z0), (r1 * math.cos(a), r1 * math.sin(a), z1), w)


def lamps(p, colour, radius, count, size, z, phase=0.0):
    """A ring of small lamps round the vertical axis, each turned to face outwards."""
    for k in range(count):
        a = math.radians(phase + k * 360.0 / count)
        p.box(colour, (radius * math.cos(a), radius * math.sin(a), z), size, rot=(0, 0, math.degrees(a) + 90))


def strut_leg(p, hip, knee, foot, pad=0.5, w=0.3):
    """A landing leg: an upper strut from the hull, a thinner lower strut to the foot and a pad on the ground (all points (x, y, z))."""
    props_lib.rod(p, "alien_grey", hip, knee, w)
    props_lib.rod(p, "metal_dark", knee, foot, w * 0.65)
    p.cyl("alien_grey", (foot[0], foot[1], 0.05), pad, 0.1, n=8, top_radius=pad * 0.7)


def nozzle(p, x, y, z, r, length, glow="glow_cyan", body="metal_dark"):
    """An engine nozzle on the Y axis facing the back (+Y): a flared bell with a glowing core, its front end at y."""
    p.cyl(body, (x, y + length / 2, z), r * 0.8, length, n=8, axis="y", top_radius=r)
    p.cyl(glow, (x, y + length + 0.02, z), r * 0.72, 0.06, n=8, axis="y")


# ===== Ships ===================================================================================================
SCOUT = [(0.8, 0.6), (0.85, 1.6), (1.0, 3.0), (1.25, 4.1), (1.5, 4.6), (1.8, 4.45), (2.1, 3.9), (2.5, 3.1), (2.9, 2.3), (3.3, 1.5), (3.6, 0.8), (3.7, 0.5)]


@piece("ships", "Scout")
def scout():
    """A 9 m scout saucer on three legs: a faceted hull with a rim, glow strip and panel lines, a canopy on a frame, belly lamps and an engine."""
    p = Prop("SH_Scout_01")
    lathe(p, "alien_grey", SCOUT, n=16)
    band(p, "metal_dark", SCOUT, 1.5, h=0.34, out=0.07)                         # rim
    band(p, "glow_cyan", SCOUT, 2.15, h=0.16, out=0.04)                         # glow strip
    band(p, "metal_dark", SCOUT, 2.9, h=0.08, out=0.03)                         # panel lines
    band(p, "metal_dark", SCOUT, 1.05, h=0.08, out=0.03)
    for za, zb in ((2.2, 2.5), (2.5, 2.9), (2.9, 3.3)):
        seams(p, "metal_dark", SCOUT, za, zb, 8, 0.1)
    lathe(p, "glass", [(3.2, 1.45), (3.45, 1.15), (3.7, 0.7), (3.9, 0.0001)], n=16)
    canopy = [(3.2, 1.45), (3.45, 1.15), (3.7, 0.7), (3.9, 0.0001)]
    for a in (0, 90, 180, 270):                                                  # canopy frame, along the glass
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        for (za, ra), (zb, rb) in zip(canopy, canopy[1:]):
            props_lib.rod(p, "metal_dark", (ra * c, ra * s_, za), (rb * c, rb * s_, zb), 0.12)
    p.cyl("metal_dark", (0, 0, 0.6), 0.7, 0.5, n=12, top_radius=0.55)           # engine bell under the belly
    p.cyl("glow_cyan", (0, 0, 0.33), 0.5, 0.05, n=12)
    for k in range(6):                                                           # belly lamps
        a = math.radians(k * 60)
        p.cyl("metal_dark", (2.2 * math.cos(a), 2.2 * math.sin(a), 0.85), 0.3, 0.2, n=8)
        p.cyl("glow_cyan", (2.2 * math.cos(a), 2.2 * math.sin(a), 0.74), 0.2, 0.04, n=8)
    for a in (30, 150, 270):                                                     # three landing legs, each with a brace to the belly
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        strut_leg(p, (2.3 * c, 2.3 * s, 0.95), (2.6 * c, 2.6 * s, 0.5), (2.85 * c, 2.85 * s, 0.1), pad=0.55, w=0.32)
        props_lib.rod(p, "metal_dark", (1.5 * c, 1.5 * s, 0.9), (2.55 * c, 2.55 * s, 0.6), 0.14)
    lamps(p, "paint_white", 4.66, 1, (0.3, 0.3, 0.3), 1.5, phase=247.5)
    lamps(p, "paint_white", 4.66, 1, (0.3, 0.3, 0.3), 1.5, phase=292.5)
    lamps(p, "alien_green", 4.66, 1, (0.3, 0.3, 0.3), 1.5, phase=90)
    props_lib.rod(p, "metal_dark", (0, 0.45, 3.7), (0, 1.2, 4.9), 0.09)          # antenna, out of the canopy
    p.cyl("glow_cyan", (0, 1.2, 4.95), 0.07, 0.1, n=6)
    return p


@piece("ships", "Dart")
def dart():
    """A 6 m swept fighter: a lens-shaped fuselage, a bubble canopy standing proud of it, swept wings with tip fins and cannons, twin engines."""
    p = Prop("SH_Dart_01")
    st = ((-3.1, 1.0, 0.08, 0.06), (-2.6, 1.0, 0.25, 0.16), (-1.8, 1.05, 0.55, 0.3), (-0.6, 1.1, 0.95, 0.45), (0.8, 1.1, 1.5, 0.5),
          (2.0, 1.05, 1.7, 0.48), (3.0, 1.0, 1.4, 0.34), (3.2, 1.0, 1.2, 0.3))
    p.loft_rings("alien_grey", [common.ring_y(y, 0, z, w, h, n=8, p=3.0) for y, z, w, h in st])
    p.loft_rings("glass", [common.ring_y(y, 0, z, w, h, n=8, p=2.2) for y, z, w, h in
                           ((-1.9, 1.3, 0.2, 0.1), (-1.3, 1.5, 0.4, 0.22), (-0.4, 1.62, 0.46, 0.3), (0.5, 1.58, 0.4, 0.22), (1.1, 1.42, 0.3, 0.1))])
    for s in (-1, 1):
        p.box("alien_grey", (s * 1.8, 1.2, 1.0), (1.6, 1.8, 0.07), rot=(0, 0, s * 25))               # wings, swept back
        props_lib.rod(p, "metal_dark", (s * 0.75, 1.7, 1.0), (s * 2.1, 2.33, 1.0), 0.1)                 # their dark trailing edge
        p.box("alien_grey", (s * 2.5, 1.6, 1.27), (0.08, 1.0, 0.55), rot=(0, s * 12, 0))              # tip fins
        p.cyl("metal_dark", (s * 2.3, 0.0, 1.0), 0.07, 1.6, n=6, axis="y")                           # cannons
        p.cyl("glow_cyan", (s * 2.3, -0.82, 1.0), 0.05, 0.05, n=6, axis="y")
        p.cyl("metal_dark", (s * 0.75, 2.5, 1.0), 0.38, 1.4, n=8, axis="y")                          # engines
        p.cyl("glow_cyan", (s * 0.75, 3.22, 1.0), 0.3, 0.06, n=8, axis="y")
        p.box("black", (s * 0.45, -1.7, 1.0), (0.3, 0.5, 0.18))                                      # intakes
    p.box("metal_dark", (0, 2.6, 1.3), (0.14, 1.2, 0.8))                                             # tail fin
    p.box("glow_cyan", (0, 3.22, 1.0), (0.5, 0.06, 0.3))
    props_lib.rod(p, "metal_dark", (0, -3.0, 1.0), (0, -3.9, 1.0), 0.06)                             # nose probe
    p.cyl("glow_cyan", (0, -3.93, 1.0), 0.05, 0.06, n=6, axis="y")
    for s in (-1, 1):
        p.box("cloth_red" if s < 0 else "alien_green", (s * 2.53, 1.54, 1.0), (0.16, 0.22, 0.12))     # wing tip lamps
        props_lib.rod(p, "metal_dark", (s * 1.5, 0.06, 1.05), (s * 2.85, 0.7, 1.05), 0.08)           # leading edge strips
        p.cyl("alien_grey", (s * 0.75, 3.0, 1.0), 0.43, 0.14, n=8, axis="y")                         # engine rings
        props_lib.rod(p, "metal_dark", (s * 0.5, -0.2, 1.55), (s * 0.55, 1.9, 1.52), 0.06)           # seams along the back
    return p


CIGAR = ((-9.0, 0.15), (-8.4, 0.7), (-7.5, 1.2), (-6.0, 1.6), (-3.5, 1.85), (0.0, 1.9), (3.5, 1.85), (6.0, 1.7), (7.8, 1.3), (8.8, 0.8), (9.0, 0.4))


@piece("ships", "Cigar")
def cigar():
    """An 18 m cigar ship: a faceted hull in 11 sections with panel rings, two rows of lit windows, a spine, tail fins and a cluster of engines."""
    p = Prop("SH_Cigar_01")
    p.loft_rings("alien_grey", [common.ring_y(y, 0, 3.0, r, r, n=12) for y, r in CIGAR])
    ry = lambda y: next((r0 + (r1 - r0) * (y - y0) / (y1 - y0) for (y0, r0), (y1, r1) in zip(CIGAR, CIGAR[1:]) if y0 <= y <= y1), 0.4)
    for y in (-4.0, -2.4, -0.8, 0.8, 2.4, 4.0):
        p.loft_rings("metal_dark", [common.ring_y(y - 0.07, 0, 3.0, ry(y - 0.07) + 0.04, ry(y - 0.07) + 0.04, n=12),
                                    common.ring_y(y + 0.07, 0, 3.0, ry(y + 0.07) + 0.04, ry(y + 0.07) + 0.04, n=12)], cap=True)
    for k in range(9):                                                                               # windows: a row on the side and a row above it
        y = -6.4 + k * 1.6
        for s in (-1, 1):
            p.box("glow_cyan", (s * ry(y), y, 3.0), (0.07, 0.6, 0.32))
            p.box("glow_cyan", (s * ry(y) * 0.866, y, 3.0 + ry(y) * 0.5), (0.07, 0.6, 0.3), rot=(0, -s * 30, 0))
    p.box("metal_dark", (0, 0, 4.9), (0.2, 7.0, 0.2))                                               # spine
    p.box("alien_grey", (0, 1.25, 5.2), (0.12, 4.5, 0.7), taper=0.6)
    for s in (-1, 1):
        p.box("alien_grey", (s * 1.9, 7.6, 3.0), (1.6, 1.8, 0.1), rot=(0, 0, s * -20))              # tail fins
    p.box("alien_grey", (0, 7.6, 4.5), (0.1, 1.8, 1.4), rot=(0, 0, 0))
    for (x, z) in ((-0.6, 3.6), (0.6, 3.6), (-0.6, 2.4), (0.6, 2.4)):                               # engine cluster
        nozzle(p, x, 8.4, z, 0.38, 0.6)
    p.cyl("glow_cyan", (0, -9.05, 3.0), 0.14, 0.2, n=6, axis="y")                                  # nose beacon, on the tip
    return p


def _tri_ring(z, k, cut=0.94):
    """A triangle with its corners cut off (6 points), scaled by k, at height z: the black triangle's outline."""
    corners = ((0.0, -6.0), (5.5, 4.5), (-5.5, 4.5))
    pts = []
    for i in range(3):
        a, b, c = corners[i - 1], corners[i], corners[(i + 1) % 3]
        pts.append(V3(b[0] + (a[0] - b[0]) * (1 - cut), b[1] + (a[1] - b[1]) * (1 - cut), z))
        pts.append(V3(b[0] + (c[0] - b[0]) * (1 - cut), b[1] + (c[1] - b[1]) * (1 - cut), z))
    return [V3(q.x * k, q.y * k, z) for q in pts]


def V3(x, y, z):
    from mathutils import Vector
    return Vector((x, y, z))


@piece("ships", "Triangle")
def triangle():
    """A black triangle (11 m): a flat hull with bevelled edges and cut corners, a raised centre, edge trim, corner lamps and a glowing core."""
    p = Prop("SH_Triangle_01")
    p.loft_rings("shadow", [_tri_ring(0.95, 0.98), _tri_ring(1.05, 1.0), _tri_ring(1.4, 0.97), _tri_ring(1.75, 0.8), _tri_ring(2.0, 0.45), _tri_ring(2.1, 0.2)])
    for i in range(3):                                                                              # edge trim along the three sides
        a = _tri_ring(1.05, 1.0)
        q0, q1 = a[2 * i + 1], a[(2 * i + 2) % 6]
        props_lib.rod(p, "metal_dark", (q0.x, q0.y, 1.12), (q1.x, q1.y, 1.12), 0.12)
    for (x, y) in ((0, -5.0), (4.7, 3.8), (-4.7, 3.8)):                                             # corner lamps on the underside
        p.cyl("metal_dark", (x, y, 0.9), 0.5, 0.2, n=8)
        p.cyl("paint_white", (x, y, 0.78), 0.35, 0.06, n=8)
    r1, r2, r3 = _tri_ring(1.4, 0.97), _tri_ring(1.75, 0.8), _tri_ring(2.0, 0.45)
    for i in range(6):                                                                              # panel lines up the bevel and the raised centre
        props_lib.rod(p, "metal_dark", (r1[i].x, r1[i].y, 1.4), (r2[i].x, r2[i].y, 1.75), 0.09)
        props_lib.rod(p, "metal_dark", (r2[i].x, r2[i].y, 1.75), (r3[i].x, r3[i].y, 2.0), 0.09)
    e = _tri_ring(1.05, 1.0)
    for i in range(3):                                                                              # lamps along each edge
        q0, q1 = e[2 * i + 1], e[(2 * i + 2) % 6]
        for t in (0.25, 0.5, 0.75):
            p.box("paint_white", (q0.x + (q1.x - q0.x) * t, q0.y + (q1.y - q0.y) * t, 1.1), (0.22, 0.22, 0.16))
    p.cyl("metal_dark", (0, 1.0, 0.9), 1.2, 0.2, n=6)                                              # the core
    p.cyl("glow_cyan", (0, 1.0, 0.8), 0.9, 0.06, n=6)
    return p


EPOD = [(0.35, 0.01), (0.4, 0.5), (0.5, 0.62), (0.8, 0.85), (1.0, 0.9), (1.3, 0.85), (1.6, 0.75), (1.9, 0.5), (2.1, 0.3), (2.3, 0.01)]


@piece("ships", "EscapePod")
def escape_pod():
    """A 2.3 m escape pod: a ribbed capsule on three legs with a framed hatch and window, hazard band, thruster and a beacon."""   # legs: one strut each
    p = Prop("SH_EscapePod_01")
    lathe(p, "alien_grey", EPOD, n=12)
    band(p, "metal_dark", EPOD, 0.62, h=0.1, out=0.03, n=12)
    band(p, "paint_yellow", EPOD, 1.5, h=0.16, out=0.03, n=12)
    band(p, "metal_dark", EPOD, 1.85, h=0.08, out=0.03, n=12)
    for za, zb in ((0.8, 1.0), (1.0, 1.3), (1.3, 1.6)):
        seams(p, "metal_dark", EPOD, za, zb, 6, 0.06)
    p.box("alien_dark", (0, -0.7, 1.2), (0.76, 0.5, 1.0))                                           # hatch frame, deep enough to reach the curved hull
    p.box("glow_cyan", (0, -0.93, 1.2), (0.62, 0.05, 0.84))
    p.box("glass", (0, -0.955, 1.2), (0.48, 0.05, 0.64))
    p.cyl("metal_dark", (0, 0, 0.22), 0.3, 0.26, n=8, top_radius=0.2)                               # thruster
    p.cyl("glow_cyan", (0, 0, 0.08), 0.22, 0.04, n=8)
    for a in (60, 180, 300):                                                                         # three legs
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        props_lib.rod(p, "metal_dark", (0.55 * c, 0.55 * s, 0.62), (1.15 * c, 1.15 * s, 0.08), 0.12)
        p.cyl("alien_grey", (1.15 * c, 1.15 * s, 0.04), 0.24, 0.08, n=6, top_radius=0.16)
    props_lib.rod(p, "metal_dark", (0, 0, 2.2), (0, 0, 2.7), 0.05)                                    # antenna and beacon
    p.cyl("glow_cyan", (0, 0, 2.72), 0.08, 0.1, n=6)
    return p


DRONE = [(1.0, 0.0001), (1.06, 0.22), (1.2, 0.34), (1.45, 0.42), (1.7, 0.36), (1.85, 0.2), (1.9, 0.0001)]


@piece("ships", "ProbeDrone")
def probe_drone():
    """A 1.9 m probe drone: a faceted body with an equator band, six angled sensor spines, an eye with a lens ring, a nozzle and an antenna."""
    p = Prop("SH_ProbeDrone_01")
    lathe(p, "alien_grey", DRONE, n=12)
    band(p, "metal_dark", DRONE, 1.45, h=0.12, out=0.04, n=12)
    band(p, "metal_dark", DRONE, 1.2, h=0.06, out=0.02, n=12)
    for k in range(6):
        a = math.radians(k * 60)
        c, s = math.cos(a), math.sin(a)
        props_lib.rod(p, "metal_dark", (0.42 * c, 0.42 * s, 1.47), (0.98 * c, 0.98 * s, 1.3), 0.07)
        p.cyl("glow_cyan", (1.0 * c, 1.0 * s, 1.29), 0.07, 0.08, n=6)
    p.cyl("metal_dark", (0, -0.38, 1.5), 0.18, 0.12, n=8, axis="y")                                  # the eye
    p.cyl("glow_cyan", (0, -0.45, 1.5), 0.11, 0.05, n=8, axis="y")
    p.cyl("metal_dark", (0, 0, 0.9), 0.12, 0.2, n=6, top_radius=0.04)                                # nozzle
    p.cyl("glow_cyan", (0, 0, 0.78), 0.09, 0.04, n=6)
    props_lib.rod(p, "metal_dark", (0, 0, 1.88), (0, 0, 2.3), 0.04)
    p.cyl("glow_cyan", (0, 0, 2.32), 0.06, 0.08, n=6)
    return p


@piece("ships", "DropShip")
def drop_ship():
    """A 9 m dropship: a lofted fuselage with a canopy, side doors, stub wings with flaps, two engine pods with intakes, landing gear and a rear ramp."""
    p = Prop("SH_DropShip_01")
    st = ((-4.4, 1.4, 0.25, 0.2), (-3.7, 1.5, 0.9, 0.6), (-2.5, 1.6, 1.3, 0.85), (-0.5, 1.65, 1.55, 1.0), (2.0, 1.65, 1.5, 1.0), (3.4, 1.6, 1.3, 0.9), (3.6, 1.55, 1.2, 0.8))
    p.loft_rings("alien_grey", [common.ring_y(y, 0, z, w, h, n=8, p=3.5) for y, z, w, h in st])
    p.loft_rings("glass", [common.ring_y(y, 0, z, w, h, n=8, p=2.4) for y, z, w, h in
                           ((-3.9, 1.95, 0.35, 0.18), (-3.1, 2.3, 0.75, 0.4), (-2.1, 2.45, 0.85, 0.4), (-1.5, 2.3, 0.8, 0.2))])
    for s in (-1, 1):
        p.box("alien_grey", (s * 2.8, 1.0, 1.7), (2.4, 3.0, 0.12), rot=(0, 0, s * -10))               # stub wings
        p.box("metal_dark", (s * 3.0, 2.5, 1.72), (2.0, 0.6, 0.1), rot=(0, 0, s * -10))               # flaps
        p.box("alien_grey", (s * 1.7, 1.9, 1.7), (0.9, 2.6, 0.12))                                    # wing root, out to the stub wing
        p.cyl("metal_dark", (s * 3.4, 1.5, 1.6), 0.55, 2.2, n=8, axis="y")                           # engine pods
        p.cyl("alien_grey", (s * 3.4, 0.35, 1.6), 0.62, 0.2, n=8, axis="y")                           # intake ring
        p.cyl("black", (s * 3.4, 0.22, 1.6), 0.42, 0.06, n=8, axis="y")
        p.cyl("glow_cyan", (s * 3.4, 2.62, 1.6), 0.4, 0.06, n=8, axis="y")
        p.box("alien_dark", (s * 1.52, 0.8, 1.65), (0.14, 2.0, 0.6))                                   # a sliding door on each side (on the hull's side ridge)
        p.box("glow_cyan", (s * 1.6, 0.2, 1.65), (0.06, 0.08, 0.5))
        for y in (-1.0, 2.2):                                                                         # landing gear: a strut, an actuator and a pad
            props_lib.rod(p, "metal_dark", (s * 1.25, y, 1.25), (s * 1.5, y, 0.1), 0.16)
            props_lib.rod(p, "alien_grey", (s * 0.9, y, 0.95), (s * 1.45, y, 0.4), 0.1)
            p.cyl("alien_grey", (s * 1.5, y, 0.05), 0.35, 0.1, n=8, top_radius=0.25)
    p.box("alien_dark", (0, 3.58, 1.4), (1.8, 0.16, 1.5))                                              # rear ramp
    p.box("glow_cyan", (0, 3.66, 1.5), (1.2, 0.06, 0.7))
    p.cyl("metal_dark", (0, -0.5, 2.7), 0.35, 0.3, n=8)                                                # sensor dome
    return p


@piece("ships", "MIBCraft")
def mib_craft():
    """An 8 m black craft: a smooth flattened wedge with a dark canopy, a ring of edge lamps, twin rear emitters, a tail fin and two antennae."""
    p = Prop("SH_MIBCraft_01")
    st = ((-4.0, 0.12, 0.08), (-3.4, 0.7, 0.2), (-2.4, 1.6, 0.4), (-1.0, 2.5, 0.55), (0.5, 3.0, 0.62), (2.0, 3.0, 0.6), (3.2, 2.2, 0.45), (3.9, 1.4, 0.3), (4.1, 1.0, 0.22))
    p.loft_rings("shadow", [common.ring_y(y, 0, 2.5, w, h, n=10, p=2.6) for y, w, h in st])
    p.loft_rings("glass", [common.ring_y(y, 0, z, w, h, n=8, p=2.2) for y, z, w, h in
                           ((-2.6, 2.8, 0.3, 0.1), (-1.8, 3.05, 0.8, 0.3), (-0.4, 3.12, 1.0, 0.32), (0.6, 3.0, 0.8, 0.2))])
    for y0 in (-2.0, 0.5, 2.6):                                                                          # panel rings round the hull
        def wh(y):
            for (ya, wa, ha), (yb, wb, hb) in zip(st, st[1:]):
                if ya <= y <= yb:
                    t = (y - ya) / (yb - ya)
                    return wa + (wb - wa) * t, ha + (hb - ha) * t
            return 1.0, 0.2
        (wa, ha), (wb, hb) = wh(y0 - 0.06), wh(y0 + 0.06)
        p.loft_rings("metal_dark", [common.ring_y(y0 - 0.06, 0, 2.5, wa + 0.04, ha + 0.04, n=10, p=2.6),
                                    common.ring_y(y0 + 0.06, 0, 2.5, wb + 0.04, hb + 0.04, n=10, p=2.6)], cap=True)
    for y, w in ((-1.0, 2.5), (0.5, 3.0), (2.0, 3.0), (3.2, 2.2)):                                      # edge lamps
        for s in (-1, 1):
            p.box("paint_white", (s * w, y, 2.5), (0.2, 0.2, 0.14))
    for s in (-1, 1):
        nozzle(p, s * 1.0, 4.0, 2.5, 0.3, 0.3)
        props_lib.rod(p, "shadow", (s * 2.9, 1.5, 2.6), (s * 3.3, 2.6, 2.9), 0.16)                    # wing tip fins
    p.box("shadow", (0, 3.0, 3.2), (0.12, 1.8, 1.0), taper=0.5)                                        # tail fin
    p.cyl("metal_dark", (0, 0.0, 1.9), 0.6, 0.1, n=6)                                                   # under the flat belly (z 1.93)
    p.cyl("glow_cyan", (0, 0.0, 1.83), 0.5, 0.06, n=6)
    props_lib.rod(p, "metal_dark", (-0.8, 2.6, 3.0), (-1.0, 3.4, 3.9), 0.05)
    props_lib.rod(p, "metal_dark", (0.8, 2.6, 3.0), (1.0, 3.4, 3.9), 0.05)
    p.box("black", (0, 3.9, 2.5), (1.6, 0.2, 0.2))
    return p


MOTHER = [(0.0, 6.0), (1.0, 16.0), (2.0, 34.0), (3.5, 40.0), (5.0, 40.0), (7.0, 36.0), (9.0, 30.0), (11.0, 23.0), (13.0, 16.0), (15.0, 11.0), (17.0, 8.0)]


@piece("ships", "Mothership")
def mothership():
    """An 80 m mothership: a 24-sided disc hull with a heavy rim, rows of lit windows, panel rings and seams, a spire with fins, six belly thrusters and hangar doors."""
    p = Prop("SH_Mothership_01")
    lathe(p, "alien_grey", MOTHER, n=24)
    band(p, "metal_dark", MOTHER, 4.2, h=1.6, out=0.5, n=24)                                           # rim
    band(p, "glow_cyan", MOTHER, 6.6, h=0.9, out=0.3, n=24)
    band(p, "metal_dark", MOTHER, 9.0, h=0.4, out=0.2, n=24)
    band(p, "metal_dark", MOTHER, 13.0, h=0.4, out=0.2, n=24)
    for za, zb in ((9.0, 11.0), (11.0, 13.0)):
        seams(p, "metal_dark", MOTHER, za, zb, 12, 0.5)
    seams(p, "glow_cyan", MOTHER, 5.4, 5.8, 24, 0.45)                                                  # two rows of lit windows, lying on the slope
    seams(p, "glow_cyan", MOTHER, 7.8, 8.2, 24, 0.45)
    lathe(p, "alien_grey", [(17.0, 2.5), (30.0, 1.5), (34.0, 0.0001)], n=12)                            # spire
    lathe(p, "glow_cyan", [(30.0, 1.6), (31.5, 1.7), (33.0, 0.5)], n=12)
    for k in range(4):
        a = math.radians(k * 90 + 45)
        props_lib.rod(p, "metal_dark", (6.0 * math.cos(a), 6.0 * math.sin(a), 17.0), (1.4 * math.cos(a), 1.4 * math.sin(a), 26.0), 0.9)    # spire fins
    for k in range(12):                                                                                  # underside lights
        a = math.radians(k * 30)
        zz = 1.0 + (30.0 - 16.0) / (34.0 - 16.0)                                                          # the underside's height at radius 30
        p.box("glow_cyan", (30.0 * math.cos(a), 30.0 * math.sin(a), zz - 0.05), (1.6, 0.5, 0.5), rot=(0, 0, math.degrees(a)))
    for k in range(6):                                                                                   # belly thrusters
        a = math.radians(k * 60 + 30)
        p.cyl("metal_dark", (20.0 * math.cos(a), 20.0 * math.sin(a), 0.7), 3.0, 1.4, n=8, top_radius=2.2)
        p.cyl("glow_cyan", (20.0 * math.cos(a), 20.0 * math.sin(a), 0.1), 2.0, 0.2, n=8)
    p.cyl("metal_dark", (0, 0, 0.25), 7.0, 0.5, n=12)                                                   # the dock under the centre
    for k in range(4):                                                                                   # hangar doors in the rim
        a = math.radians(k * 90)
        p.box("alien_dark", (39.6 * math.cos(a), 39.6 * math.sin(a), 4.2), (9.0, 1.4, 2.6), rot=(0, 0, math.degrees(a) + 90))
        p.box("glow_cyan", (40.35 * math.cos(a), 40.35 * math.sin(a), 3.1), (6.0, 0.2, 0.2), rot=(0, 0, math.degrees(a) + 90))
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


if __name__ == "__main__":
    run()
