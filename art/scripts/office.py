"""Office furniture and equipment: desks, a chair, a modular cubicle kit (panels, worksurface, overhead bin, an assembled pod), a copier, a desktop printer,
a water cooler, a filing cabinet, a whiteboard, a shredder and the small things on a desk. Flat faceted models, real size.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/office.py", run_name="__main__")
Optional global OFFICE_LIST (names or group names: desks, seating, cubicle, equipment, storage, desktop). Exports Assets/Art/Global/Office/<Group>/GO_<Name>_01.fbx
and adds the moving parts to art/data/interactions.json.

Origin on the floor at the middle of the base, the front is -Y. The cubicle kit is on a 1.5 m module: a panel is 1.5 m long and 0.06 m thick, centred on its
origin and lying along X; turn it 90 degrees for a side wall. The overhead bin is the one wall piece: its origin is the middle of its back face (it hangs on
the face of a panel, its bottom 0.2 m below the origin). Drawers, trays and lids are separate parts that move (see interactive.py for the conventions).
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
rod, lathe, ball = props_lib.rod, props_lib.lathe, props_lib.ball

PIECES = {}


def piece(group, name):
    def deco(fn):
        PIECES[name] = (fn, group)
        return fn
    return deco


# ===== Helpers ==================================================================================================
def shell(p, col, cx, w, d, z0, h, yf, t=0.02, inner=None):
    """An open-fronted carcass whose front face is at y = yf and which runs back d metres: two sides, a back, a top and a bottom."""
    inner = inner or col
    for s in (-1, 1):
        p.box(col, (cx + s * (w - t) / 2, yf + d / 2, z0 + h / 2), (t, d, h))
    p.box(inner, (cx, yf + d - t / 2, z0 + h / 2), (w - 2 * t, t, h))
    p.box(col, (cx, yf + d / 2, z0 + h - t / 2), (w, d, t))
    p.box(inner, (cx, yf + d / 2, z0 + t / 2), (w - 2 * t, d, t))


def drawer(p, role, col, inner, cx, zc, w, h, d, yf, travel, handle="metal_galv", thick=0.02):
    """A drawer flush with a body front at y = yf, running back d metres; slides out towards -Y by `travel`."""
    depth = d - 0.05
    with p.part(role, pivot=(cx, yf, zc), kind="slide", axis="y", limit=-travel, rest=0.0):
        p.box(col, (cx, yf - thick / 2, zc), (w, thick, h))
        tw, th = w - 0.06, h * 0.72
        zf = zc - h / 2 + 0.02
        p.box(inner, (cx, yf + depth / 2, zf), (tw, depth, 0.015))
        for s in (-1, 1):
            p.box(inner, (cx + s * (tw - 0.015) / 2, yf + depth / 2, zf + th / 2), (0.015, depth, th))
        p.box(inner, (cx, yf + depth - 0.0075, zf + th / 2), (tw, 0.015, th))
        if handle:
            p.box(handle, (cx, yf - thick - 0.012, zc + h * 0.18), (min(0.14, w * 0.3), 0.025, 0.02))


def hinged(p, role, side, col, x0, x1, z0, z1, yf, thick=0.02, limit=105, handle="metal_galv"):
    """A door in front of an opening x0..x1, z0..z1 on a body whose front is at y = yf: side right or left (turns about Z), top (a flap that lifts out)."""
    yc = yf - thick / 2
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    if side == "right":
        pivot, axis, lim = (x1, yc, cz), "z", limit
    elif side == "left":
        pivot, axis, lim = (x0, yc, cz), "z", -limit
    else:
        pivot, axis, lim = (cx, yc, z1), "x", -limit
    with p.part(role, pivot=pivot, kind="hinge", axis=axis, limit=lim, rest=0.0):
        p.box(col, (cx, yc, cz), (x1 - x0, thick, z1 - z0))
        if handle:
            if side == "top":
                p.box(handle, (cx, yf - thick - 0.012, z0 + 0.04), (min(0.3, (x1 - x0) * 0.4), 0.025, 0.02))
            else:
                hx = (x0 + 0.05) if side == "right" else (x1 - 0.05)
                p.box(handle, (hx, yf - thick - 0.012, cz), (0.02, 0.025, min(0.2, (z1 - z0) * 0.4)))


# ===== Desks ====================================================================================================
def _desk(name, top, body, edge):
    p = Prop(name)
    w, d, h = 1.6, 0.75, 0.74
    p.box(top, (0, 0, 0.725), (w, d, 0.03))
    p.box(edge, (0, -d / 2 + 0.006, 0.725), (w, 0.012, 0.032))
    p.box(body, (-0.775, 0.0, 0.355), (0.03, 0.66, 0.71))                       # a panel leg
    p.box(body, (-0.1, 0.3, 0.52), (1.3, 0.02, 0.4))                            # the modesty panel
    yf = -0.33
    px, pw, pd = 0.57, 0.42, 0.66
    shell(p, body, px, pw, pd, 0.0, 0.71, yf, inner="office_grey")
    for k, zc in enumerate((0.12, 0.34, 0.56)):
        drawer(p, f"Drawer{k + 1}", body, "office_grey", px, zc, pw - 0.04, 0.2, pd, yf, 0.4)
    return p


@piece("desks", "Desk_Wood")
def desk_wood():
    return _desk("GO_Desk_Wood_01", "laminate", "wood_dark", "wood_dark")


@piece("desks", "Desk_Steel")
def desk_steel():
    return _desk("GO_Desk_Steel_01", "black", "fabric_grey", "metal_galv")


@piece("desks", "Desk_L")
def desk_l():
    """A modern corner desk: a 1.6 m run along X and a 1.2 m return coming forward on the left, on steel tube legs."""
    p = Prop("GO_Desk_L_01")
    p.box("paint_white", (0, 0.0, 0.725), (1.6, 0.7, 0.03))
    p.box("paint_white", (-0.5, -0.65, 0.725), (0.6, 0.6, 0.03))
    for x, y in ((0.76, 0.31), (0.76, -0.31), (-0.76, 0.31), (-0.76, -0.9), (-0.24, -0.9), (0.0, 0.31)):
        p.box("metal_dark", (x, y, 0.355), (0.04, 0.04, 0.71))
    p.box("metal_dark", (0, 0.31, 0.65), (1.5, 0.02, 0.06))
    p.box("metal_dark", (-0.5, -0.9, 0.65), (0.5, 0.02, 0.06))
    p.box("metal_dark", (-0.76, -0.3, 0.65), (0.02, 1.2, 0.06))
    return p


@piece("desks", "ConferenceTable")
def conference_table():
    p = Prop("GO_ConferenceTable_01")
    p.box("laminate", (0, 0, 0.725), (3.0, 1.2, 0.04), taper=1.0)
    p.box("wood_dark", (0, 0, 0.69), (3.0, 1.2, 0.03))
    for s in (-1, 1):
        p.box("office_dark", (s * 1.1, 0, 0.35), (0.08, 0.9, 0.68))
        p.box("office_dark", (s * 1.1, 0, 0.02), (0.1, 1.0, 0.04))
    p.box("black", (0, 0, 0.746), (0.4, 0.12, 0.004))
    return p


# ===== Seating ==================================================================================================
@piece("seating", "Chair_Office")
def chair_office():
    p = Prop("GO_Chair_Office_01")
    for k in range(5):
        a = math.radians(90 + 72 * k)
        tip = (0.32 * math.cos(a), 0.32 * math.sin(a), 0.07)
        rod(p, "black", (0, 0, 0.09), tip, 0.045, 0.03)
        p.cyl("rubber", (tip[0], tip[1], 0.03), 0.03, 0.06, n=6)
    p.cyl("metal_galv", (0, 0, 0.27), 0.03, 0.3, n=6)
    p.cyl("black", (0, 0, 0.1), 0.05, 0.04, n=6)
    p.box("black", (0, 0, 0.43), (0.3, 0.3, 0.04))
    p.box("office_dark", (0, -0.02, 0.48), (0.5, 0.5, 0.08), taper=0.96)
    p.box("black", (0, 0.2, 0.62), (0.08, 0.05, 0.2), rot=(-8, 0, 0))
    p.box("office_dark", (0, 0.27, 0.82), (0.48, 0.07, 0.5), rot=(-8, 0, 0), taper=0.95)
    for s in (-1, 1):
        p.box("black", (s * 0.27, 0.0, 0.58), (0.03, 0.03, 0.17))
        p.box("black", (s * 0.27, -0.02, 0.68), (0.06, 0.3, 0.03))
    return p


# ===== Cubicle kit (1.5 m module) ================================================================================
def _panel(p, cx, cy, length, h, along="x", glass_from=None, t=0.06):
    """One cubicle panel centred on (cx, cy): fabric body, trim posts and cap, feet; glass_from = height above which the panel is glass."""
    def B(col, a, b, z, sx, sy, sz):
        if along == "x":
            p.box(col, (cx + a, cy + b, z), (sx, sy, sz))
        else:
            p.box(col, (cx + b, cy + a, z), (sy, sx, sz))
    top = glass_from if glass_from else h - 0.04
    B("office_grey", 0, 0, 0.03 + (top - 0.03) / 2, length - 0.06, t - 0.01, top - 0.03)
    if glass_from:
        B("clear_glass", 0, 0, (glass_from + h - 0.04) / 2, length - 0.06, t - 0.03, h - 0.04 - glass_from)
        B("office_dark", 0, 0, glass_from, length - 0.06, t, 0.03)
    B("office_dark", 0, 0, h - 0.02, length, t, 0.04)
    for s in (-1, 1):
        B("office_dark", s * (length / 2 - 0.015), 0, h / 2, 0.03, t, h)
        B("office_dark", s * (length / 2 - 0.2), 0, 0.015, 0.06, 0.34, 0.03)


@piece("cubicle", "Panel_Low")
def panel_low():
    p = Prop("GO_Cubicle_Panel_Low_01")
    _panel(p, 0, 0, 1.5, 1.2)
    return p


@piece("cubicle", "Panel_High")
def panel_high():
    p = Prop("GO_Cubicle_Panel_High_01")
    _panel(p, 0, 0, 1.5, 1.6)
    return p


@piece("cubicle", "Panel_Glass")
def panel_glass():
    p = Prop("GO_Cubicle_Panel_Glass_01")
    _panel(p, 0, 0, 1.5, 1.6, glass_from=1.1)
    return p


def _worksurface(p, x0, y0, x1, y1, z=0.72):
    p.box("laminate", ((x0 + x1) / 2, (y0 + y1) / 2, z + 0.015), (x1 - x0, y1 - y0, 0.03))
    p.box("wood_dark", ((x0 + x1) / 2, y0 + 0.006, z + 0.015), (x1 - x0, 0.012, 0.032))


@piece("cubicle", "Worksurface_Corner")
def worksurface_corner():
    """A corner worksurface: a 1.5 m run along the back with a 0.9 m return on the left, hung from the panels (a steel bracket at each end)."""
    p = Prop("GO_Cubicle_Worksurface_01")
    _worksurface(p, -0.75, 0.05, 0.75, 0.7)
    _worksurface(p, -0.75, -0.85, -0.1, 0.05)
    for x, y in ((0.7, 0.62), (-0.7, 0.62), (-0.68, -0.8)):
        p.box("metal_dark", (x, y, 0.69), (0.05, 0.05, 0.06))
    p.box("metal_dark", (0.0, 0.67, 0.67), (1.5, 0.02, 0.05))
    return p


@piece("cubicle", "OverheadBin")
def overhead_bin():
    """A storage bin that hangs on the face of a panel. Origin: the middle of its back face; the flap lifts out."""
    p = Prop("GO_Cubicle_OverheadBin_01")
    w, d, h = 1.5, 0.36, 0.4
    yf = -d
    for s in (-1, 1):
        p.box("office_grey", (s * (w - 0.04) / 2, -d / 2, 0.0), (0.04, d, h))
    p.box("office_grey", (0, -d / 2, h / 2 - 0.02), (w, d, 0.04))
    p.box("office_grey", (0, -d / 2, -h / 2 + 0.02), (w, d, 0.04))
    p.box("office_dark", (0, -0.01, 0.0), (w - 0.08, 0.02, h - 0.08))
    hinged(p, "Door", "top", "office_grey", -w / 2 + 0.04, w / 2 - 0.04, -h / 2 + 0.04, h / 2 - 0.04, yf, thick=0.02, limit=100, handle="office_dark")
    return p


@piece("cubicle", "Pod")
def cubicle_pod():
    """An assembled cubicle 3 m wide and 1.5 m deep, open to the front: two high panels at the back, a high panel on each side, a corner desk, a drawer pedestal and an overhead bin."""
    p = Prop("GO_Cubicle_Pod_01")
    _panel(p, -0.75, 0.75, 1.5, 1.6)
    _panel(p, 0.75, 0.75, 1.5, 1.6)
    _panel(p, -1.5, 0.0, 1.5, 1.6, along="y")
    _panel(p, 1.5, 0.0, 1.5, 1.6, along="y")
    _worksurface(p, -1.47, 0.07, 1.47, 0.72)
    _worksurface(p, -1.47, -0.83, -0.82, 0.07)
    for x, y in ((0.2, 0.69), (-0.8, -0.8), (-1.45, -0.8)):
        p.box("metal_dark", (x, y, 0.35), (0.04, 0.04, 0.7))
    p.box("wood_dark", (0.95, 0.4, 0.34), (0.42, 0.58, 0.68))
    for k, zc in enumerate((0.13, 0.34, 0.55)):
        p.box("office_grey", (0.95, 0.1, zc), (0.38, 0.02, 0.19))
        p.box("metal_galv", (0.95, 0.085, zc + 0.04), (0.12, 0.02, 0.02))
    for s in (-1, 1):
        p.box("office_grey", (s * 0.7, 0.58, 1.3), (0.04, 0.34, 0.4))
    p.box("office_grey", (0.0, 0.58, 1.5), (1.44, 0.34, 0.04))
    p.box("office_grey", (0.0, 0.58, 1.1), (1.44, 0.34, 0.04))
    p.box("office_dark", (0.0, 0.58, 1.3), (1.4, 0.02, 0.36))
    return p


# ===== Equipment ================================================================================================
@piece("equipment", "Copier")
def copier():
    """A floor-standing office copier: three paper trays that slide out, a lid over the glass that lifts, a control panel and a side output tray."""
    p = Prop("GO_Copier_01")
    w, d = 0.65, 0.7
    yf = -d / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.cyl("rubber", (sx * 0.27, sy * 0.3, 0.02), 0.03, 0.04, n=6)
    shell(p, "enamel_white", 0, w, d, 0.04, 0.68, yf, inner="office_grey")
    for z in (0.255, 0.475):
        p.box("enamel_white", (0, yf + d / 2, z), (w - 0.04, d - 0.04, 0.02))
    for k, zc in enumerate((0.14, 0.36, 0.58)):
        drawer(p, f"Tray{k + 1}", "office_grey", "office_dark", 0, zc, w - 0.04, 0.2, d, yf, 0.35, handle="black")
    p.box("office_grey", (0, 0, 0.82), (w, d, 0.2))
    p.box("office_dark", (0, yf - 0.002, 0.74), (w, 0.004, 0.025))
    p.box("glass", (0, 0.0, 0.9205), (0.6, 0.5, 0.004))
    y_back, z_top = d / 2, 0.92
    with p.part("Lid", pivot=(0, y_back, z_top), kind="hinge", axis="x", limit=-80, rest=0.0):
        p.box("enamel_white", (0, y_back - 0.31, z_top + 0.03), (w, 0.62, 0.06))
        p.box("office_dark", (0, y_back - 0.31, z_top + 0.062), (w - 0.1, 0.5, 0.004))
    p.box("office_dark", (0.16, -0.32, 0.95), (0.3, 0.1, 0.04), rot=(15, 0, 0))
    p.box("screen", (0.1, -0.325, 0.973), (0.14, 0.06, 0.004), rot=(15, 0, 0))
    p.box("glow_cyan", (0.1, -0.325, 0.976), (0.11, 0.04, 0.002), rot=(15, 0, 0))
    p.box("glow_green", (0.22, -0.31, 0.973), (0.03, 0.025, 0.006), rot=(15, 0, 0))
    p.box("cloth_red", (0.255, -0.31, 0.973), (0.03, 0.025, 0.006), rot=(15, 0, 0))
    p.box("office_grey", (-0.43, 0.0, 0.76), (0.22, 0.36, 0.012))
    p.box("office_grey", (-0.535, 0.0, 0.775), (0.012, 0.36, 0.03))
    p.box("paper", (-0.43, 0.0, 0.7685), (0.2, 0.28, 0.003))
    return p


@piece("equipment", "Printer_Desktop")
def printer_desktop():
    """A desktop laser printer: a paper tray that slides out of the bottom, a top cover that lifts, an output ramp with a sheet, a small display."""
    p = Prop("GO_Printer_Desktop_01")
    w, d = 0.42, 0.38
    yf = -d / 2
    shell(p, "office_dark", 0, w, d, 0.0, 0.22, yf, t=0.015, inner="black")
    drawer(p, "Tray", "office_grey", "office_grey", 0, 0.045, w - 0.03, 0.07, d, yf, 0.14, handle=None)
    p.box("office_dark", (0, yf - 0.002, 0.13), (w, 0.004, 0.12))
    p.box("black", (0, yf - 0.004, 0.19), (0.3, 0.005, 0.01))
    y_back, z_top = d / 2, 0.22
    with p.part("Cover", pivot=(0, y_back, z_top), kind="hinge", axis="x", limit=-70, rest=0.0):
        p.box("office_grey", (0, y_back - 0.17, z_top + 0.015), (w, 0.34, 0.03))
    p.box("black", (0.0, 0.06, 0.234), (0.3, 0.22, 0.004))
    p.box("paper", (0.0, 0.1, 0.24), (0.21, 0.28, 0.004), rot=(-12, 0, 0))
    p.box("screen", (0.12, yf - 0.006, 0.16), (0.1, 0.006, 0.05))
    p.box("glow_cyan", (0.12, yf - 0.0095, 0.16), (0.08, 0.002, 0.03))
    p.box("glow_green", (0.17, yf - 0.006, 0.2), (0.012, 0.006, 0.012))
    return p


@piece("equipment", "WaterCooler")
def water_cooler():
    """A bottled-water cooler: cabinet with a hinged door, hot and cold taps over a drip tray, and a blue jug on top."""
    p = Prop("GO_WaterCooler_01")
    w, d, h = 0.32, 0.34, 0.95
    yf = -d / 2
    shell(p, "enamel_white", 0, w, d, 0.02, h - 0.02, yf, inner="office_grey")
    p.box("office_dark", (0, 0, 0.01), (w - 0.02, d - 0.02, 0.02))
    p.box("office_dark", (0, yf + d / 2, h + 0.01), (w + 0.01, d + 0.01, 0.02))
    hinged(p, "Door", "right", "office_grey", -w / 2 + 0.02, w / 2 - 0.02, 0.05, 0.58, yf, thick=0.02, limit=105, handle="metal_galv")
    p.box("office_dark", (0, yf - 0.006, 0.78), (0.26, 0.012, 0.2))
    p.box("cloth_red", (-0.06, yf - 0.03, 0.83), (0.04, 0.05, 0.04))
    p.box("label_blue", (0.06, yf - 0.03, 0.83), (0.04, 0.05, 0.04))
    p.box("metal_galv", (0, yf - 0.05, 0.7), (0.24, 0.1, 0.02))
    p.box("black", (0, yf - 0.05, 0.712), (0.2, 0.08, 0.004))
    p.box("glow_cyan", (0.1, yf - 0.012, 0.88), (0.012, 0.004, 0.012))
    p.box("glow_red", (-0.1, yf - 0.012, 0.88), (0.012, 0.004, 0.012))
    lathe(p, "water_blue", [(0.0, 0.04), (0.04, 0.04), (0.12, 0.12), (0.22, 0.15), (0.5, 0.15), (0.52, 0.1)], n=10, z0=h + 0.02)
    lathe(p, "label_white", [(0.26, 0.152), (0.4, 0.152)], n=10, z0=h + 0.02, cap=False)
    return p


# ===== Storage ==================================================================================================
@piece("storage", "FilingCabinet")
def filing_cabinet():
    """A four-drawer steel filing cabinet; each drawer slides out and has a label holder."""
    p = Prop("GO_FilingCabinet_01")
    w, d, h = 0.46, 0.62, 1.32
    yf = -d / 2
    shell(p, "fabric_grey", 0, w, d, 0.0, h, yf, inner="office_grey")
    for z in (0.33, 0.66, 0.99):
        p.box("fabric_grey", (0, yf + d / 2, z), (w - 0.04, d - 0.02, 0.012))
    for k, zc in enumerate((0.165, 0.495, 0.825, 1.155)):
        drawer(p, f"Drawer{k + 1}", "fabric_grey", "office_grey", 0, zc, w - 0.03, 0.31, d, yf, 0.5, handle="metal_galv")
    return p


@piece("storage", "Whiteboard_Stand")
def whiteboard_stand():
    """A 1.2 x 0.9 m whiteboard on a wheeled stand, with a marker tray, three markers and some scribbles."""
    p = Prop("GO_Whiteboard_Stand_01")
    bz = 1.4
    p.box("label_white", (0, 0, bz), (1.16, 0.02, 0.86))
    for dz in (-0.44, 0.44):
        p.box("metal_galv", (0, 0, bz + dz), (1.2, 0.035, 0.03))
    for dx in (-0.59, 0.59):
        p.box("metal_galv", (dx, 0, bz), (0.03, 0.035, 0.9))
        p.box("metal_dark", (dx, 0.045, 0.95), (0.04, 0.04, 1.9))
        p.box("metal_dark", (dx, 0.1, 0.045), (0.05, 0.6, 0.05))
        for dy in (-0.15, 0.35):
            p.cyl("rubber", (dx, 0.1 + dy * 0.9, 0.03), 0.03, 0.06, n=6)
    p.box("metal_galv", (0, -0.04, bz - 0.46), (1.0, 0.07, 0.02))
    for x, c in ((-0.2, "label_blue"), (0.0, "cloth_red"), (0.2, "black")):
        p.cyl(c, (x, -0.05, bz - 0.44), 0.01, 0.12, n=4, axis="x")
    p.box("label_blue", (-0.2, -0.0115, bz + 0.2), (0.5, 0.003, 0.025), rot=(0, 0, 4))
    p.box("label_blue", (-0.25, -0.0115, bz + 0.12), (0.36, 0.003, 0.025))
    p.box("cloth_red", (0.2, -0.0115, bz - 0.02), (0.26, 0.003, 0.02), rot=(0, 0, -20))
    p.box("black", (0.0, -0.0115, bz - 0.2), (0.6, 0.003, 0.02))
    return p


@piece("storage", "Shredder")
def shredder():
    """A paper shredder: a head with a feed slot on a bin whose front drawer slides out."""
    p = Prop("GO_Shredder_01")
    w, d = 0.38, 0.26
    yf = -d / 2
    shell(p, "black", 0, w, d, 0.0, 0.5, yf, inner="office_dark")
    drawer(p, "Bin", "black", "office_dark", 0, 0.22, w - 0.04, 0.4, d, yf, 0.2, handle="office_grey")
    p.box("office_dark", (0, 0, 0.55), (0.4, 0.28, 0.1))
    p.box("black", (0, 0.0, 0.6015), (0.3, 0.02, 0.004))
    p.box("glass", (0, -0.141, 0.54), (0.2, 0.004, 0.03))
    p.box("glow_green", (0.14, -0.141, 0.58), (0.016, 0.004, 0.016))
    return p


@piece("storage", "Wastebasket")
def wastebasket():
    p = Prop("GO_Wastebasket_01")
    lathe(p, "metal_dark", [(0.0, 0.11), (0.3, 0.15)], n=8)
    p.cyl("metal_galv", (0, 0, 0.3), 0.158, 0.02, n=8)
    p.cyl("black", (0, 0, 0.305), 0.14, 0.01, n=8)
    ball(p, "paper", (0.03, 0.0, 0.33), 0.05, n=5, rings=2)
    ball(p, "paper", (-0.04, 0.05, 0.325), 0.04, n=5, rings=2)
    return p


# ===== Desktop ==================================================================================================
@piece("desktop", "Workstation")
def workstation():
    """A flat monitor on a stand, a keyboard and a mouse."""
    p = Prop("GO_Workstation_01")
    p.cyl("office_dark", (0, 0.1, 0.01), 0.1, 0.02, n=8)
    p.box("office_dark", (0, 0.1, 0.12), (0.05, 0.03, 0.2))
    p.box("black", (0, 0.1, 0.34), (0.56, 0.04, 0.34))
    p.box("screen", (0, 0.078, 0.34), (0.52, 0.004, 0.3))
    p.box("glow_cyan", (-0.17, 0.0755, 0.38), (0.12, 0.002, 0.02))
    p.box("office_grey", (0, -0.2, 0.012), (0.44, 0.14, 0.024), taper=0.97)
    for k in range(3):
        p.box("office_dark", (0, -0.2 + (k - 1) * 0.04, 0.0245), (0.4, 0.028, 0.002))
    p.box("office_grey", (0.32, -0.2, 0.014), (0.06, 0.1, 0.028), taper=0.9)
    return p


@piece("desktop", "Phone")
def phone():
    """A desk telephone with its handset on the cradle and a keypad."""
    p = Prop("GO_Phone_01")
    p.box("office_dark", (0, 0, 0.025), (0.2, 0.22, 0.05), taper=0.92)
    p.box("black", (0, -0.05, 0.052), (0.12, 0.1, 0.004), rot=(-12, 0, 0))
    for r in range(3):
        p.box("office_grey", (0, -0.075 + r * 0.03, 0.056), (0.1, 0.014, 0.004), rot=(-12, 0, 0))
    for s in (-1, 1):
        p.box("office_dark", (s * 0.075, 0.07, 0.075), (0.03, 0.05, 0.05))             # the cradle's two posts
        p.box("black", (s * 0.095, 0.07, 0.125), (0.05, 0.075, 0.05))                   # earpiece and mouthpiece
    p.box("black", (0, 0.07, 0.145), (0.2, 0.05, 0.03))                                 # the handset
    p.box("glow_green", (0.075, -0.09, 0.052), (0.01, 0.01, 0.004))
    return p


def run():
    names = globals().get("OFFICE_LIST")
    chosen = [k for k, (fn, g) in PIECES.items() if not names or k in names or g in names]
    x, row, y = 0.0, None, 0.0
    for key in chosen:
        fn, group = PIECES[key]
        if group != row:
            row, x, y = group, 0.0, y + 4.0 if row is not None else 0.0
        prop = fn()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Office/{group.title()}/{prop.name}.fbx")
        obj.location = (x, y, 0)
        x += max(0.4, obj.dimensions.x + 0.4)
    props_lib.write_interactions()
    print("office done", len(chosen))


if __name__ == "__main__":
    run()
