"""The ship's control panels (issue #118): the console, the bank terminal (green), the launch terminal (red).

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/terminals.py", run_name="__main__")
Optional global TERMINAL_LIST, e.g. ["bank", "launch"] (keys of TERMINALS), and STATE_LAMPS=False to leave out the three swappable lamps (the asset browser build). Each exports to Assets/Art/Global/Vehicles/<name>.fbx.

What is here (design notes: docs/art/terminal-notes.md):
  GV_ShipConsole_01         the desk along the ship's back wall: a sloped control ledge with button groups, a holo-ring between the two
                            terminals, glow strips and cables into the deck. Origin on the deck, centre of its base; 3.4 x 0.9 m like the
                            collider block FarmsteadBuilder puts there; the two terminals stand on its top plate at z = 0.93
  GV_ShipTerminalBank_01    the bank terminal: GREEN housing and a green curved screen, an intake slot with chevrons and rings that
                            stack up like a hologram, a bar graph (a ledger). Origin on the console top, over the middle of the console (the footing runs from y = -0.22 to +0.30); stands on the console
  GV_ShipTerminalLaunch_01  the launch terminal: RED housing and a red screen with a warning mark, a guarded button and a throw lever

Every terminal has three lamps as separate objects, `Lamp_Locked` (red), `Lamp_Ready` (green), `Lamp_Working` (amber): the game shows
the one that matches the terminal's state by turning their renderers on and off (Assets/Scripts/Interactables/TerminalLamps.cs).
In the FBX they are called `<model>_Lamp_Locked` and so on: Blender object names are unique across the file.

Like everything here the models face -Y, +X is the right of whoever looks at the screen, origin on the base. The sign rule (see the
blender-assets skill): a rotation about X by +t lowers the -Y end of a part, so Plane(tilt=+t) is a surface that leans its front down.
"""

import importlib
import math
import sys
from math import cos, radians, sin
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Blender is shared by several sessions, each running scripts from its own checkout: a `common` another checkout imported first would
# make this one write its FBX into that checkout. Drop modules that came from somewhere else so they are imported from here.
for _n in ("common", "props_lib", "emitters"):
    _m = sys.modules.get(_n)
    if _m is not None and Path(getattr(_m, "__file__", "") or "").resolve().parent != _HERE:
        sys.modules.pop(_n, None)

import bmesh
import bpy
from mathutils import Matrix, Vector

import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop
rod = props_lib.rod


# ===== Helpers ===================================================================================================================

class Plane:
    """A tilted surface. At tilt 0 it is horizontal (v along +Y, normal up); tilt > 0 leans the front (-Y) down, 90 stands it up facing -Y,
    so a screen that leans back 12 degrees is tilt 78: v runs up it, the normal looks forward and a little up.
    at(u, v, h): u along X, v up the surface, h out along the normal."""

    def __init__(self, origin, tilt):
        self.o = Vector(origin)
        self.tilt = tilt
        self.t = radians(tilt)

    def at(self, u, v, h=0.0):
        c, s = cos(self.t), sin(self.t)
        return self.o + Vector((u, v * c - h * s, v * s + h * c))

    def box(self, p, colour, u, v, h, size, taper=1.0, spin=0.0):
        """A box lying on the surface: centre (u, v, h) in the surface's own axes, size (along X, up the surface, along the normal).
        spin turns it about the surface's normal (degrees), for chevrons and slanted marks."""
        rot = (self.tilt, 0, 0)
        if spin:
            e = (Matrix.Rotation(radians(self.tilt), 3, "X") @ Matrix.Rotation(radians(spin), 3, "Z")).to_euler("XYZ")
            rot = (math.degrees(e.x), math.degrees(e.y), math.degrees(e.z))
        p.box(colour, tuple(self.at(u, v, h)), size, rot=rot, taper=taper)


SCREEN_TILT = 90 - 12      # a standing screen is a work surface turned up to 78 degrees: it leans back 12 degrees from the vertical


class Curved:
    """A screen bent round the viewer: `cols` flat segments across `width`, the edges `bow` metres in front of the middle, on a Plane.
    Everything laid on it (strips, bars) uses the same columns so the pieces meet without gaps."""

    def __init__(self, plane, width, bow, cols):
        self.pl, self.w, self.bow, self.cols = plane, width, bow, cols

    def u(self, i):
        return -self.w / 2 + self.w * i / self.cols

    def hh(self, u):
        return self.bow * (u / (self.w / 2)) ** 2

    def strip(self, p, colour, c0, c1, v0, v1, h0, thick):
        """Columns c0..c1, from v0 up to v1, a slab `thick` deep whose back is h0 in front of the curved reference surface."""
        assert c1 > c0, "a strip needs at least one column"
        rings = []
        for i in range(c0, c1 + 1):
            u = self.u(i)
            base = h0 + self.hh(u)
            rings.append([self.pl.at(u, v0, base), self.pl.at(u, v1, base), self.pl.at(u, v1, base + thick), self.pl.at(u, v0, base + thick)])
        common.loft(p._bm(colour), rings)


def lamp_objects(prop_name, body, coll, plane, v, h, us, size=0.06):
    """The three state lamps: separate meshes (Lamp_Locked red, Lamp_Ready green, Lamp_Working amber) parented to the body. Returns them."""
    made = []
    for key, colour, u in zip(("Locked", "Ready", "Working"), ("glow_red", "glow_green", "glow_amber"), us):
        orphan = bpy.data.meshes.get(f"{prop_name}_Lamp_{key}")
        if orphan is not None and orphan.users == 0:
            bpy.data.meshes.remove(orphan)                    # a leftover of an earlier build would give this mesh a .00N name in the FBX
        bm = bmesh.new()
        common.add_box(bm, tuple(plane.at(u, v, h)), (size, size, size * 0.8), rot_deg=(plane.tilt, 0, 0))
        o = common.new_mesh_object(f"{prop_name}_Lamp_{key}", bm, coll, colour, flat=True)
        o.parent = body
        made.append(o)
    return made


def cable(p, pts, w=0.045, colour="black"):
    """A cable through points, as straight lengths (faceted): each length is a rod, so the bends read as kinks, like a thick hose."""
    for a, b in zip(pts, pts[1:]):
        rod(p, colour, a, b, w)
    for a in pts[1:-1]:
        p.cyl(colour, a, w * 0.62, w * 1.2, n=6, axis="z")        # a knuckle at each bend hides the gap


def button_grid(p, plane, u0, v0, cols, rows, pitch, colours, h=0.03, size=0.045, high=0.02):
    """A block of square buttons on a surface; colours cycle through the list."""
    k = 0
    for r in range(rows):
        for c in range(cols):
            plane.box(p, colours[k % len(colours)], u0 + c * pitch, v0 + r * pitch, h + high / 2, (size, size, high))
            k += 1


def dial(p, plane, u, v, h=0.03, r=0.055, colour="metal_galv", mark="glow_cyan", turn=40):
    """A knob with a tick on it (the tick turns by `turn` degrees about the surface normal)."""
    c = plane.at(u, v, h + 0.015)
    p.cyl("metal_dark", tuple(plane.at(u, v, h + 0.005)), r * 1.25, 0.012, n=8, rot=(plane.tilt, 0, 0))
    p.cyl(colour, tuple(c), r, 0.03, n=8, rot=(plane.tilt, 0, 0))
    t = radians(turn)
    plane.box(p, mark, u + sin(t) * r * 0.5, v + cos(t) * r * 0.5, h + 0.032, (0.012, r * 0.9, 0.012), spin=-turn)       # lies in the surface, pointing at `turn`


def ring_band(p, colour, cx, cy, z0, r_out, width, height=0.02, n=6):
    """A flat hexagonal ring (an annulus): outer radius r_out, `width` wide, `height` tall, standing at z0. Solid, so it shows from both sides."""
    r_in = r_out - width
    rings = []
    for k in range(n + 1):
        a = radians(60 * k) if n == 6 else radians(360 * k / n)
        ca, sa = cos(a), sin(a)
        rings.append([Vector((cx + r_in * ca, cy + r_in * sa, z0)), Vector((cx + r_out * ca, cy + r_out * sa, z0)),
                      Vector((cx + r_out * ca, cy + r_out * sa, z0 + height)), Vector((cx + r_in * ca, cy + r_in * sa, z0 + height))])
    common.loft(p._bm(colour), rings, cap=False)     # the seam (first ring = last ring) is merged when the prop finishes


def holo_rings(p, colour, cx, cy, z0, radii, gap, n=6, strut="metal_dark", base_z=None, beam_top=None):
    """Rings that stack up like a hologram, held by three thin struts from the surface they float over (base_z: where the struts start) and
    threaded on a thin lit beam up the middle (to beam_top, default the top of the last ring), so every ring is part of one piece."""
    for k, r in enumerate(radii):
        ring_band(p, colour, cx, cy, z0 + k * gap, r, 0.028 + 0.004 * (len(radii) - k), 0.018, n)
    r0 = radii[0]
    zb = z0 - 0.09 if base_z is None else base_z
    for a in (90, 210, 330):
        x, y = cx + r0 * 0.92 * cos(radians(a)), cy + r0 * 0.92 * sin(radians(a))
        rod(p, strut, (cx + (x - cx) * 0.3, cy + (y - cy) * 0.3, zb), (x, y, z0 + 0.006), 0.016)
    top = z0 + (len(radii) - 1) * gap + 0.018 if beam_top is None else beam_top
    p.cyl(colour, (cx, cy, (zb + top) / 2), 0.011, top - zb, n=4)


# ===== The console ===============================================================================================================

def ship_console(name="GV_ShipConsole_01"):
    """The desk along the ship's back wall. Plan 3.4 x 0.9 m (a little more at the front where the ledge leans out), 0.9 m high."""
    p = Prop(name)
    W = 3.4
    # plinth, recessed, with a glowing kick strip
    p.box("metal_dark", (0, 0, 0.05), (W - 0.1, 0.80, 0.10))
    p.box("glow_cyan", (0, -0.405, 0.075), (W - 0.5, 0.02, 0.035))
    # body: a profile (y, z) lofted along X: bulging front, the control ledge leaning back and up, a flat top for the two terminals
    prof = [(0.45, 0.10), (-0.40, 0.10), (-0.46, 0.46), (-0.50, 0.58), (-0.22, 0.90), (0.45, 0.90)]
    p.loft_rings("alien_dark", [[Vector((x, y, z)) for y, z in prof] for x in (-W / 2, W / 2)])
    # top plate (alien_grey), 3 cm over the body's top, with a dark rim and the strips the terminals stand beside
    p.box("alien_grey", (0, 0.115, 0.915), (W, 0.67, 0.03))
    p.box("metal_dark", (0, 0.45, 0.915), (W, 0.03, 0.035))
    # the ledge: panels along it
    sl = Plane((0, -0.50, 0.58), math.degrees(math.atan2(0.32, 0.28)))        # tilts the front down by the ledge's own slope
    sl_len = math.hypot(0.28, 0.32)
    sl.box(p, "metal_dark", 0, sl_len / 2, 0.012, (W - 0.1, sl_len - 0.02, 0.025))
    sl.box(p, "glow_cyan", 0, 0.025, 0.03, (W - 0.3, 0.018, 0.012))             # a glow strip along the lower edge of the ledge
    hi = 0.04
    cyan, amber, violet = "glow_cyan", "glow_amber", "alien_violet"
    for cx, kind in ((-1.45, 0), (-0.85, 1), (0.0, 2), (0.85, 1), (1.45, 0)):
        if kind == 0:                                       # two rows of square buttons and a slider
            button_grid(p, sl, cx - 0.12, 0.12, 4, 2, 0.065, [cyan, violet, cyan, amber], h=hi - 0.012, size=0.045)
            sl.box(p, "alien_dark", cx, 0.30, hi - 0.012 + 0.006, (0.34, 0.025, 0.012))
            sl.box(p, "glow_cyan", cx - 0.07, 0.30, hi - 0.012 + 0.014, (0.05, 0.035, 0.016))
        elif kind == 1:                                     # a dial and a row of round buttons
            dial(p, sl, cx - 0.09, 0.21, h=hi - 0.012, turn=35 if cx < 0 else -50)
            for k in range(3):
                p.cyl(amber if k == 1 else cyan, tuple(sl.at(cx + 0.02 + k * 0.065, 0.11, hi + 0.002)), 0.025, 0.02, n=6, rot=(sl.tilt, 0, 0))
            sl.box(p, "glow_cyan", cx, 0.30, hi - 0.012 + 0.006, (0.30, 0.012, 0.012))
        else:                                               # the middle: a wide status bar of segments in three groups
            for k in range(9):
                colour = amber if k % 4 == 3 else cyan
                sl.box(p, colour, cx + (k - 4) * 0.075, 0.30, hi - 0.012 + 0.006, (0.05, 0.05, 0.012))
            dial(p, sl, cx - 0.14, 0.15, h=hi - 0.012, r=0.045, turn=-20)
            dial(p, sl, cx + 0.14, 0.15, h=hi - 0.012, r=0.045, turn=60)
            button_grid(p, sl, cx - 0.045, 0.10, 2, 2, 0.065, [amber, cyan, cyan, violet], h=hi - 0.012, size=0.045)
    # end caps: the body's flanks step in, with a glow strip each, and a fin on the front corners
    for s in (-1, 1):
        p.box("alien_grey", (s * (W / 2 - 0.02), 0.0, 0.50), (0.06, 0.86, 0.80))
        p.box("glow_cyan", (s * (W / 2 + 0.012), -0.15, 0.42), (0.02, 0.5, 0.045), rot=(0, 0, 0))
        p.box("glow_cyan", (s * (W / 2 + 0.012), -0.15, 0.62), (0.02, 0.42, 0.03), rot=(0, 0, 0))
    # cables into the deck, out of each end: hoses that leave the flank low, kink out along the floor and go in
    for s in (-1, 1):
        for k, y in enumerate((-0.12, 0.18)):
            x0 = s * (W / 2 + 0.03)
            cable(p, [(x0, y, 0.34 - k * 0.1), (s * (W / 2 + 0.25), y + 0.04, 0.2 - k * 0.07), (s * (W / 2 + 0.5), y + 0.1 + k * 0.06, 0.02)])
    # the front, under the ledge: vent slats either side of the middle, access panels with handles, and a row of small lights above the plinth
    for s in (-1, 1):
        for k in range(4):
            p.box("black", (s * 1.0, -0.425, 0.2 + k * 0.07), (0.66, 0.012, 0.03))
        for sx in (s * 0.4, s * 1.52):
            p.box("alien_grey", (sx, -0.428, 0.30), (0.32, 0.012, 0.26))                    # an access panel
            p.box("metal_dark", (sx, -0.436, 0.30), (0.08, 0.012, 0.02))                    # its handle
    for k in range(14):
        p.box("glow_amber" if k % 5 == 2 else ("alien_violet" if k % 5 == 4 else "glow_cyan"), (-0.78 + k * 0.12, -0.418, 0.13), (0.04, 0.012, 0.025))
    # the holo-ring between the two terminals: a stub with a lens, three stacked rings, struts
    mid = 0.9
    p.cyl("metal_dark", (0, 0.04, mid + 0.04), 0.13, 0.08, n=6, top_radius=0.08)
    p.cyl("glow_cyan", (0, 0.04, mid + 0.09), 0.06, 0.02, n=6)
    holo_rings(p, "glow_cyan", 0, 0.04, mid + 0.20, (0.22, 0.17, 0.11), 0.07, base_z=mid + 0.07, beam_top=mid + 0.42)
    p.cyl("glow_cyan", (0, 0.04, mid + 0.44), 0.025, 0.05, n=6, top_radius=0.0)
    return p


# ===== The terminals =============================================================================================================

PALETTES = {
    # housing, light housing, glow, lit-edge
    "bank": {"housing": "plant_green", "light": "alien_green", "glow": "glow_green"},
    "launch": {"housing": "barn_red", "light": "label_red", "glow": "glow_red"},
}


def _terminal_body(p, pal):
    """What the two ship terminals share: footing, pedestal, a leaning control face, a leaning curved screen, side fins and a lamp rail.
    Returns the screen's plane/curve and the control face so each kind can add its own things."""
    H, L, G = pal["housing"], pal["light"], pal["glow"]
    # footing, a step and the pedestal that holds the control face. The footprint runs from y = -0.22 to +0.30 (the console's flat top starts at -0.2)
    p.box("alien_dark", (0, 0.04, 0.025), (1.30, 0.52, 0.05))
    p.box("metal_dark", (0, 0.04, 0.062), (1.22, 0.46, 0.024))
    p.box(H, (0, 0.06, 0.20), (1.16, 0.44, 0.27), taper=0.94)
    p.box("glow_cyan", (0, -0.168, 0.085), (0.9, 0.012, 0.025))                   # a lit strip round the foot, in the ship's own colour
    # the control face
    cf = Plane((0, -0.10, 0.36), 22)
    cf.box(p, "alien_dark", 0, 0.17, 0.0, (1.20, 0.38, 0.06))
    cf.box(p, L, 0, -0.012, 0.012, (1.20, 0.024, 0.07))                          # a coloured lip along the front edge
    # the curved screen, leaning back 12 degrees: bezel (dark), glass (glow), edge posts
    sp = Plane((0, 0.16, 0.50), SCREEN_TILT)
    cur = Curved(sp, 1.16, 0.10, 22)
    cur.strip(p, "alien_dark", 0, 22, 0.0, 0.50, -0.05, 0.05)                    # bezel, curved too, so the edges meet the glass
    cur.strip(p, G, 1, 21, 0.045, 0.455, 0.0, 0.03)                              # the glass
    # a solid back to the screen: the housing behind it, a wedge from the pedestal up
    sp.box(p, H, 0, 0.22, -0.13, (1.04, 0.44, 0.22))
    # side fins: a coloured wing either side of the screen, with a glowing edge
    for s in (-1, 1):
        sp.box(p, L, s * 0.62, 0.24, 0.0, (0.07, 0.52, 0.10))
        sp.box(p, G, s * 0.62, 0.24, 0.058, (0.022, 0.46, 0.016))
        p.box(H, (s * 0.60, 0.10, 0.28), (0.10, 0.3, 0.3), taper=0.8)            # a buttress from the foot to the fin
    # the lamp rail across the top of the screen and a coloured crown above it
    sp.box(p, "alien_dark", 0, 0.535, 0.0, (0.50, 0.075, 0.10))
    sp.box(p, G, 0, 0.58, 0.0, (0.62, 0.014, 0.07))
    return cf, sp, cur


def _screen_lines(p, cur, rows):
    """Dark lines on the lit glass, like a display: rows of (c0, c1, v0, v1)."""
    for c0, c1, v0, v1 in rows:
        cur.strip(p, "alien_dark", c0, c1, v0, v1, 0.03, 0.006)


def bank_terminal(name="GV_ShipTerminalBank_01"):
    """Green. Intake slot with chevrons, rings that stack up above it, a ledger bar graph, groups of buttons."""
    p = Prop(name)
    pal = PALETTES["bank"]
    cf, sp, cur = _terminal_body(p, pal)
    G, L = pal["glow"], pal["light"]
    # the screen: a ledger. Bars on the left (the banked items), lines of text on the right, a header bar
    _screen_lines(p, cur, [(2, 20, 0.395, 0.425)])
    for k, top in enumerate((0.20, 0.27, 0.15, 0.32, 0.24)):
        cur.strip(p, "alien_dark", 3 + k * 2, 4 + k * 2, 0.06, top, 0.03, 0.006)
    for k, (c1, v) in enumerate(((20, 0.34), (18, 0.30), (20, 0.26), (17, 0.22), (19, 0.18), (16, 0.14))):
        cur.strip(p, "alien_dark", 14, c1, v, v + 0.022, 0.03, 0.006)
    # the control face: the intake slot in the middle, a button group either side
    cf.box(p, "black", 0, 0.17, 0.032, (0.46, 0.10, 0.012))                       # the slot
    cf.box(p, "glow_green", 0, 0.17, 0.040, (0.40, 0.03, 0.010))
    for k in range(3):                                                           # chevrons pointing down into the slot
        v = 0.36 - k * 0.055
        cf.box(p, G, -0.055, v, 0.036, (0.12, 0.022, 0.012), spin=-32)
        cf.box(p, G, 0.055, v, 0.036, (0.12, 0.022, 0.012), spin=32)
    button_grid(p, cf, -0.52, 0.06, 3, 2, 0.065, ["glow_green", "glow_amber", "glow_cyan", "alien_dark"], h=0.03)
    dial(p, cf, 0.38, 0.12, turn=30, mark="glow_green")
    for k in range(3):
        p.cyl("glow_green" if k < 2 else "glow_amber", tuple(cf.at(0.30 + k * 0.07, 0.30, 0.04)), 0.022, 0.02, n=6, rot=(cf.tilt, 0, 0))
    cf.box(p, "alien_dark", 0.44, 0.30, 0.034, (0.03, 0.025, 0.012))
    # rings stacking up above the slot: the deposit hologram
    holo_rings(p, G, 0, 0.0, 0.60, (0.15, 0.11, 0.07), 0.06, base_z=0.43)
    # lamps' rail is on the screen's top (sp, v 0.535): nothing more to build; cables from the back to the console top
    for x in (-0.35, 0.0, 0.35):
        cable(p, [(x, 0.28, 0.30), (x + 0.04, 0.36, 0.12), (x + 0.06, 0.42, 0.02)], w=0.04)
    return p, {"plane": sp, "v": 0.535, "h": 0.05, "us": (-0.12, 0.0, 0.12)}


def launch_terminal(name="GV_ShipTerminalLaunch_01"):
    """Red. A warning mark on the screen, a guarded button, a throw lever, a ring of segment lights; hazard stripes."""
    p = Prop(name)
    pal = PALETTES["launch"]
    cf, sp, cur = _terminal_body(p, pal)
    G, L = pal["glow"], pal["light"]
    # the screen: header, a stack of segment bars (a countdown) on the left, a big "!" on the right
    _screen_lines(p, cur, [(2, 20, 0.395, 0.425)])
    for k in range(6):
        cur.strip(p, "alien_dark", 3, 4 + (k % 4) * 2 + 3, 0.06 + k * 0.05, 0.095 + k * 0.05, 0.03, 0.006)
    cur.strip(p, "alien_dark", 15, 17, 0.14, 0.34, 0.03, 0.006)                  # the bar of the "!"
    cur.strip(p, "alien_dark", 15, 17, 0.065, 0.105, 0.03, 0.006)                # and its dot
    # hazard stripes across the front lip: alternating amber/black blocks
    for k in range(12):
        cf.box(p, "glow_amber" if k % 2 == 0 else "black", -0.55 + k * 0.1, 0.012, 0.04, (0.05, 0.024, 0.012))
    # the guarded button, left: a frame, a big red button, and a safety cage of hazard-yellow posts and rails over it
    gu, gv = -0.36, 0.20
    cf.box(p, "metal_dark", gu, gv, 0.045, (0.24, 0.24, 0.03))
    p.cyl("glow_red", tuple(cf.at(gu, gv, 0.075)), 0.075, 0.03, n=8, rot=(cf.tilt, 0, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cf.box(p, "hi_vis", gu + sx * 0.105, gv + sy * 0.105, 0.105, (0.022, 0.022, 0.12))              # the four posts
    for sx in (-1, 1):
        cf.box(p, "hi_vis", gu + sx * 0.105, gv, 0.172, (0.022, 0.232, 0.022))                              # two rails along the top
    cf.box(p, "black", gu, gv - 0.105, 0.172, (0.232, 0.022, 0.022))                                        # and a black one across the front
    cf.box(p, "hi_vis", gu, gv + 0.105, 0.172, (0.232, 0.022, 0.022))
    # the throw lever, right: a slot, a base block, an arm tilted towards you and a ball
    lu = 0.46
    cf.box(p, "black", lu, 0.19, 0.034, (0.07, 0.30, 0.012))
    cf.box(p, "metal_dark", lu, 0.06, 0.05, (0.14, 0.09, 0.04))
    rod(p, "metal_galv", tuple(cf.at(lu, 0.07, 0.07)), (lu, -0.25, 0.30), 0.04)
    p.cyl("glow_red", (lu, -0.25, 0.32), 0.05, 0.05, n=7)
    # two dials and a button group between: the middle of the face
    dial(p, cf, -0.04, 0.24, turn=-30, mark="glow_red")
    dial(p, cf, 0.14, 0.24, turn=50, mark="glow_red")
    button_grid(p, cf, -0.08, 0.07, 4, 1, 0.065, ["glow_amber", "glow_red", "glow_red", "glow_cyan"], h=0.03)
    # a radar ring of six segments above the face: a ring and a rod to a cone
    holo_rings(p, G, 0.0, 0.0, 0.62, (0.15, 0.10), 0.07, base_z=0.43)
    for x in (-0.35, 0.0, 0.35):
        cable(p, [(x, 0.28, 0.30), (x - 0.04, 0.36, 0.12), (x - 0.06, 0.42, 0.02)], w=0.04)
    return p, {"plane": sp, "v": 0.535, "h": 0.05, "us": (-0.12, 0.0, 0.12)}


# ===== Build and export ==========================================================================================================

TERMINALS = {
    "console": (ship_console, "Global/Vehicles"),
    "bank": (bank_terminal, "Global/Vehicles"),
    "launch": (launch_terminal, "Global/Vehicles"),
}


def run():
    names = globals().get("TERMINAL_LIST") or list(TERMINALS)
    x = 0.0
    out = {}
    for key in names:
        fn, area = TERMINALS[key]
        built = fn()
        prop, lamps = built if isinstance(built, tuple) else (built, None)
        obj, coll = prop.finish()
        if lamps is not None and globals().get("STATE_LAMPS", True):      # the asset browser has no state to show: it builds without the three swappable lamps
            lamp_objects(prop.name, obj, coll, lamps["plane"], lamps["v"], lamps["h"], lamps["us"], lamps.get("size", 0.06))
        print(common.stats(obj))
        common.export_fbx(coll, f"Assets/Art/{area}/{prop.name}.fbx")
        obj.location.x = x
        x += max(1.0, obj.dimensions.x + 0.6)
        out[key] = obj
    print("terminals done", names)
    return out


if __name__ == "__main__":
    run()
    for _n in ("common", "props_lib", "emitters"):          # leave the next session's import to find its own copy
        sys.modules.pop(_n, None)
