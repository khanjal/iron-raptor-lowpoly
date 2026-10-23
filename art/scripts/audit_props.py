"""Audit the prop models: are their parts joined, not through each other, on the floor, the right way round and the right size?

Run in Blender (the MCP), from the checkout you want audited:

    import runpy
    runpy.run_path(r"<repo>/art/scripts/audit_props.py", run_name="__main__")
    # optional globals (init_globals=): ONLY=["GT_Rake_01", "Washer"] (names or short names), WRITE=True (also write art/data/prop_geometry.json),
    # SCRIPTS=r"<other folder>" (audit the scripts in another folder, for example a scratch copy of an older props_farm.py), QUIET=True (problems only)

It builds every prop in props_farm.py, household.py, decor.py, interactive.py, ship_props.py and ship_hulls.py the way the export does, but does NOT call Prop.finish(): nothing is added to the
Blender scene, no collection is cleared and nothing is exported, so it is safe in a Blender file other sessions are using. The scripts are imported from the
folder given (modules of the same names that are loaded already are put aside while it runs and put back after). A recorder wraps the builder, so every
box, cylinder and loft is kept as a part of its own (the builder joins them into one mesh), with the line of the prop's script that made it.

Tests (one line per problem, "FAIL <test> <prop>: <what>"; the problem count is printed as the summary and left in the global PROBLEMS):

  origin    the lowest point is on the floor (z = 0, 1 cm): "origin on the floor at the centre of the base". Wall and ceiling pieces are exempt (their origin is the mount).
  size      the size is in the real range for its kind (SIZES: a washer 0.6 x 0.65 x 0.85 m, a table top at 0.75 m ...); the measured sizes are printed as a table.
  front     the front faces -Y: a seat has its back rest behind it (+Y); a piece with doors and drawers has their hinges and slides on the -Y side.
  floating  every part touches another within 1 cm (parts overlapping or sharing a face count); the groups that do not are listed. LOOSE says which props are loose items by design.
  through   a rod-like part (a handle, a beam, a leg) that passes right through another part: it enters one face and leaves by the opposite one with both its ends outside
            (a handle through the head bar, a beam through a tray). A rod that ends inside the part it joins is fine. THROUGH_OK lists the ones that are meant (a rail through
            its posts), each with a reason.
  hinge     (reported under `front`) a door or lid whose pivot is not on the edge of the part it turns (the washer's door).
  pipes     a pipe, cable or duct part (copper, or a script line that says pipe, cable, duct, hose, wire) has both ends in another part; a free end is listed and must be declared
            in audit_layout.CONNECTED (the layout audit then checks that it reaches a wall, the ceiling or the floor).

With WRITE=True it also writes art/data/prop_geometry.json (next to the scripts folder audited: with SCRIPTS= that is the scratch copy's data folder) (size and the heights of the exposed horizontal tops of every prop) for audit_layout.py: a lamp stands on the
top of a nightstand, not on the top of its bounding box.
"""

import ast
import importlib.util
import json
import linecache
import math
import re
import sys
from contextlib import contextmanager
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
_g = globals()
SCRIPTS = Path(_g.get("SCRIPTS") or HERE)
ONLY = _g.get("ONLY")
WRITE = bool(_g.get("WRITE"))
QUIET = bool(_g.get("QUIET"))

# =====================================================================================================================
# THE DATA
# =====================================================================================================================

TOUCH = 0.01            # m: parts closer than this are joined
HINGE_EDGE = 0.03       # m: a hinge pivot is this near an edge of the part it turns
FLOOR_TOLERANCE = 0.01  # m
PIPE_COLOURS = {"copper"}
PIPE_WORDS = re.compile(r"\b(pipe|cable|duct|hose|wire|conduit|cord)\b", re.I)
PIPE_MIN_LENGTH = 0.1   # m: a copper part shorter than this is a fitting, not a pipe
PIPE_NOT = r"^KeroseneLamp$"   # copper is its burner
PIPE_GAP = 0.05
PIPE_ASPECT = 1.5       # a pipe stub is at least this much longer than it is thick
ROD_ASPECT = 2.5        # a part is rod-like when its length is this many times its thickness
PIERCE_FACE_DOT = -0.85 # the faces a rod leaves through are opposite (their normals dot below this)
TOP_AREA = 0.02         # m2: a horizontal top this big can carry things

# Short names (GH_Chair_Kitchen_01 -> Chair_Kitchen) whose origin is the middle of a wall mount or a ceiling fixing, not the floor. Taken from audit_layout.
# Kinds that are loose items by design (several separate objects in one model): floating parts are not reported.
LOOSE = r"^(Books|BookStack|FirewoodPile_Loose|FirewoodStack|Plates|ToyBlocks|Boots|Cans|Fruit|Eggs|Clutter|Debris|Coins|Cards|Dice|Papers|Newspaper|ShipEgg|ShipFreighter)"
# A ship hull (ship_hulls.py) is skins written straight into the mesh, which the recorder does not see (so everything that touches a skin looks loose), and its landing legs are
# built folded up (so its lowest point is not the ground): floating and the origin are not checked for them.
HULL = re.compile(r"^Ship(Egg|Freighter)$")

# Real sizes in metres, (width x, depth y, height z) ranges, by regex on the short name. None = not checked in that axis.
SIZES = {
    r"^Washer$": ((0.58, 0.70), (0.58, 0.75), (0.80, 0.95)),
    r"^Dryer$": ((0.58, 0.70), (0.58, 0.75), (0.80, 0.95)),
    r"^Fridge": ((0.55, 0.95), (0.55, 0.85), (1.40, 1.95)),
    r"^Stove$": ((0.50, 0.85), (0.55, 0.80), (0.84, 0.96)),
    r"^Counter_Kitchen$": ((0.6, 2.5), (0.55, 0.75), (0.84, 0.96)),
    r"^Sink_Kitchen$": ((0.6, 2.2), (0.5, 0.75), (0.80, 1.30)),
    r"^Table_Dining$": ((0.7, 2.2), (0.6, 1.2), (0.70, 0.80)),
    r"^Table_Side$": ((0.3, 0.7), (0.3, 0.7), (0.45, 0.70)),
    r"^Table_Coffee$": ((0.7, 1.4), (0.4, 0.9), (0.35, 0.55)),
    r"^Desk_Wood$": ((1.0, 1.8), (0.5, 0.85), (0.70, 0.80)),
    r"^Chair_(Dining|Kitchen|Office)$": ((0.35, 0.65), (0.35, 0.7), (0.80, 1.15)),
    r"^Sofa$": ((1.5, 2.4), (0.75, 1.1), (0.7, 1.05)),
    r"^Armchair$": ((0.7, 1.1), (0.7, 1.1), (0.75, 1.1)),
    r"^Bed_Double$": ((1.3, 1.9), (1.9, 2.3), (0.4, 1.4)),
    r"^Bed_Child$": ((0.7, 1.0), (1.4, 1.9), (0.4, 1.0)),
    r"^Wardrobe$": ((0.8, 1.6), (0.45, 0.7), (1.7, 2.2)),
    r"^Bookcase$": ((0.7, 1.3), (0.2, 0.45), (1.5, 2.2)),
    r"^Toilet$": ((0.35, 0.5), (0.55, 0.8), (0.60, 0.9)),
    r"^Tub$": ((1.4, 1.9), (0.65, 0.85), (0.45, 0.80)),
    r"^WaterHeater$": ((0.4, 0.65), (0.4, 0.65), (1.0, 1.7)),
    r"^Door(_|$)": ((0.75, 1.0), (0.02, 0.12), (1.95, 2.15)),
}

# Props whose parts are meant to pass through each other: regex on the short name -> reason. Keep this short; every row is a model that looks right and breaks the rule.
THROUGH_OK = [
    (r"^(Bed_Bunk|Cot|Gurney|Chair_Dining|Scarecrow|Shower|Doll|BootsPair|Fireplace|FirewoodPile_Loose|ShipBunk|ShipConduit)$", None, None,
     "frames and bundles: posts, rails, logs and limbs that cross each other and run on past the crossing (a bunk's posts through its decks, a scarecrow's arms through its post, a clamp across the pipes it holds)"),
    (r"^Pitchfork$", "metal_dark", "wood_light", "the tine bar crosses the handle's lower end, which sits in the socket round it"),
    (r"^(Rake|Pitchfork)$", "metal_dark", "metal_dark", "the head bar runs through its socket: a fork or rake head is a bar with a sleeve round the handle, and the bar's ends show on both sides"),
]

SEAT = re.compile(r"^(Chair_|Stool|Bench|Armchair|RockingChair|Sofa)")


# =====================================================================================================================
# Loading the scripts without disturbing the session
# =====================================================================================================================

MODULES = ("common", "emitters", "props_lib", "household", "decor", "interactive", "home_styles", "ship_props", "ship_hulls")


@contextmanager
def isolated(scripts):
    """Put aside any loaded modules of the same names, import from `scripts`, and put the old ones back after."""
    saved = {n: sys.modules.pop(n) for n in MODULES if n in sys.modules}
    saved_path = list(sys.path)                  # the scripts insert their own folder into sys.path again when they are imported
    sys.path.insert(0, str(scripts))
    real_reload = importlib.reload
    importlib.reload = lambda module: module        # the scripts reload each other on import, which would undo the recorder's wrapping
    try:
        yield
    finally:
        importlib.reload = real_reload
        for n in MODULES:
            sys.modules.pop(n, None)
        sys.modules.update(saved)
        sys.path[:] = saved_path


def load_plain(name, path):
    """Load a plain Python file under a private module name (no sys.modules entry that others could find)."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.modules.pop(name, None)
    return mod


def load_props_farm(path):
    """props_farm.py builds and exports everything when it is run: execute everything except the module-level loops and expressions."""
    src = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(src)
    keep = [n for n in tree.body if not isinstance(n, (ast.For, ast.Expr)) or (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    mod = ast.Module(body=keep, type_ignores=[])
    ns = {"__file__": str(path), "__name__": "props_farm_audit"}
    exec(compile(mod, str(path), "exec"), ns)
    return ns


# =====================================================================================================================
# The recorder: every box, cylinder and loft the builder makes, as a part of its own
# =====================================================================================================================

class Part:
    def __init__(self, kind, colour, role, src, verts, polys, ends, length, cross):
        self.kind, self.colour, self.role, self.src = kind, colour, role, src
        self.verts, self.polys = verts, polys
        self.ends = ends            # the two ends of the part's long axis
        self.length, self.cross = length, cross
        xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
        self.lo = Vector((min(xs), min(ys), min(zs)))
        self.hi = Vector((max(xs), max(ys), max(zs)))
        self._tree = None
        self.normals = []
        for p in polys:
            a, b, c = verts[p[0]], verts[p[1]], verts[p[2]]
            n = (b - a).cross(c - a)
            self.normals.append(n.normalized() if n.length > 1e-12 else Vector((0, 0, 1)))

    @property
    def tree(self):
        if self._tree is None:
            self._tree = BVHTree.FromPolygons([tuple(v) for v in self.verts], [tuple(p) for p in self.polys])
        return self._tree

    @property
    def rodlike(self):
        return self.cross > 0 and self.length / self.cross >= ROD_ASPECT

    def label(self):
        return f"{self.kind} {self.colour}{'/' + self.role if self.role else ''} at ({(self.lo.x + self.hi.x) / 2:.2f}, {(self.lo.y + self.hi.y) / 2:.2f}, {(self.lo.z + self.hi.z) / 2:.2f}) [{self.src[:90]}]"


class Recorder:
    def __init__(self):
        self.parts = []
        self.ctx = None

    def add(self, kind, bm, n0, ends, length, cross):
        if self.ctx is None:
            return
        bm.faces.ensure_lookup_table()
        verts, polys, index = [], [], {}
        for f in bm.faces[n0:]:
            poly = []
            for v in f.verts:
                if v.index not in index:
                    index[v.index] = len(verts)
                    verts.append(v.co.copy())
                poly.append(index[v.index])
            polys.append(poly)
        if verts:
            self.parts.append(Part(kind, self.ctx["colour"], self.ctx["role"], self.ctx["src"], verts, polys, ends, length, cross))


def install(common, props_lib, rec):
    """Wrap the leaf builders of this (isolated) copy of the scripts so the recorder sees every primitive."""
    orig_box, orig_loft = common.add_box, common.loft

    def add_box(bm, center, size, rot_deg=(0, 0, 0), taper=1.0):
        bm.faces.ensure_lookup_table()
        n0 = len(bm.faces)
        result = orig_box(bm, center, size, rot_deg, taper)
        rot = Euler([math.radians(a) for a in rot_deg], "XYZ").to_matrix()
        dims = sorted(range(3), key=lambda i: -size[i])
        axis = rot @ Vector([1.0 if i == dims[0] else 0.0 for i in range(3)])
        half = size[dims[0]] / 2
        c = Vector(center)
        rec.add("box", bm, n0, (c - axis * half, c + axis * half), size[dims[0]], size[dims[1]])
        return result

    def loft(bm, rings, cap=True):
        bm.faces.ensure_lookup_table()
        n0 = len(bm.faces)
        orig_loft(bm, rings, cap)
        cen = lambda ring: sum((Vector(p) for p in ring), Vector()) / len(ring)
        a, b = cen(rings[0]), cen(rings[-1])
        cross = max((max((Vector(q) - cen(r)).length for q in r) * 2 for r in rings), default=0)
        rec.add("loft", bm, n0, (a, b), (b - a).length, cross)

    common.add_box, common.loft = add_box, loft

    Prop = props_lib.Prop

    def role_of(prop):
        if prop._cur is None:
            return None
        for name, g in prop.groups.items():
            if g is prop._cur:
                return name
        return None

    def caller():
        f = sys._getframe(2)
        while f is not None and Path(f.f_code.co_filename).name == "props_lib.py":
            f = f.f_back
        if f is None:
            return "?"
        line = linecache.getline(f.f_code.co_filename, f.f_lineno).strip()
        return f"{f.f_code.co_name}:{f.f_lineno} {line}"

    for name in ("box", "cyl", "loft_rings"):
        orig = getattr(Prop, name)

        def wrapped(self, colour, *a, _orig=orig, **k):
            rec.ctx = {"colour": props_lib.THEME.get(colour, colour), "role": role_of(self), "src": caller()}
            try:
                return _orig(self, colour, *a, **k)
            finally:
                rec.ctx = None
        setattr(Prop, name, wrapped)


def build_all(scripts):
    """Return {prop name: (module name, Prop, [Part])} for every prop in the scripts folder, built but not finished."""
    out = {}
    scripts = Path(scripts)
    with isolated(scripts):
        import common, props_lib
        import household, decor, interactive, ship_props, ship_hulls
        sources = []
        farm = scripts / "props_farm.py"
        if farm.exists():
            ns = load_props_farm(farm)
            sources.append(("props_farm", [fn for fn, _area in ns["PROPS"].values()]))
        sources.append(("household", [fn for fn, _g in household.PIECES.values()]))
        sources.append(("decor", [fn for fn, _g in decor.PIECES.values()]))
        sources.append(("interactive", [fn for fn, _g in interactive.ITEMS.values()]))
        sources.append(("ship_props", list(ship_props.SHIP_PROPS.values())))                       # the ship's set dressing (issue #212)
        sources.append(("ship_hulls", [fn for fn, _area in ship_hulls.HULLS.values()]))            # and the new hulls (the saucer is vehicles.py)
        rec = Recorder()
        install(common, props_lib, rec)

        for module, fns in sources:
            for fn in fns:
                rec.parts = []
                try:
                    prop = fn()
                except Exception as e:                         # a prop that does not build is its own problem
                    out[f"{module}.{fn.__name__}"] = (module, None, [], repr(e))
                    continue
                out[prop.name] = (module, prop, rec.parts, None)
    return out


# =====================================================================================================================
# Geometry helpers
# =====================================================================================================================

def inside(parts, p, skip=None):
    """True if p is inside any of the parts (ray parity)."""
    d = Vector((0.2673, 0.5346, 0.8018)).normalized()
    for part in parts:
        if part is skip:
            continue
        if not (part.lo.x - 1e-6 <= p.x <= part.hi.x + 1e-6 and part.lo.y - 1e-6 <= p.y <= part.hi.y + 1e-6 and part.lo.z - 1e-6 <= p.z <= part.hi.z + 1e-6):
            continue
        count, origin = 0, p.copy()
        for _ in range(40):
            hit = part.tree.ray_cast(origin, d)
            if hit[0] is None:
                break
            count += 1
            origin = hit[0] + d * 1e-5
        if count % 2 == 1:
            return True
    return False


def distance_to_part(part, p):
    hit = part.tree.find_nearest(p)
    return hit[3] if hit[0] is not None else 1e9


def touching(a, b):
    """Parts overlap, share a face or are within TOUCH of each other."""
    pad = TOUCH
    if any(a.lo[i] - pad > b.hi[i] or b.lo[i] - pad > a.hi[i] for i in range(3)):
        return False
    if a.tree.overlap(b.tree):
        return True
    if any(distance_to_part(b, v) <= pad for v in a.verts):
        return True
    return any(distance_to_part(a, v) <= pad for v in b.verts)


def short(name):
    s = re.sub(r"^[A-Z]{2}_", "", name)
    return re.sub(r"_\d\d$", "", s)


# =====================================================================================================================
# The tests
# =====================================================================================================================

def whole(parts):
    lo = Vector((min(p.lo.x for p in parts), min(p.lo.y for p in parts), min(p.lo.z for p in parts)))
    hi = Vector((max(p.hi.x for p in parts), max(p.hi.y for p in parts), max(p.hi.z for p in parts)))
    return lo, hi


def test_origin(name, prop, parts, mounted, lo, hi):
    if mounted:
        return []
    if abs(lo.z) > FLOOR_TOLERANCE:
        return [f"lowest point is z {lo.z:+.3f} m: the origin must be on the floor at the base"]
    return []


def test_size(name, prop, parts, mounted, lo, hi, table):
    out = []
    s = short(name)
    size = hi - lo
    for pat, ranges in SIZES.items():
        if not re.search(pat, s):
            continue
        row = []
        for axis, label, rng in zip(range(3), "wdh", ranges):
            v = size[axis]
            ok = rng is None or rng[0] <= v <= rng[1]
            row.append(f"{label} {v:.2f}" + ("" if ok else f" (real {rng[0]:.2f}-{rng[1]:.2f})"))
            if not ok:
                out.append(f"{label} is {v:.2f} m, a real {s} is {rng[0]:.2f}-{rng[1]:.2f} m")
        table.append(f"{name:28} " + "  ".join(row))
    return out


def test_front(name, prop, parts, mounted, lo, hi):
    out = []
    s = short(name)
    mid_y = (lo.y + hi.y) / 2
    if SEAT.search(s):
        # the back rest: everything above 60% of the height (a tall back, arms or a head board); its middle must be behind the seat's middle (+Y)
        z0 = lo.z + 0.6 * (hi.z - lo.z)
        high = [p for p in parts if p.hi.z > z0 and (p.hi.z - p.lo.z) > 0.05]
        if high and (hi.z - lo.z) > 0.6:
            cy = sum((p.lo.y + p.hi.y) / 2 * max(p.hi.z - max(p.lo.z, z0), 0) for p in high) / max(sum(max(p.hi.z - max(p.lo.z, z0), 0) for p in high), 1e-9)
            if cy < mid_y - 0.02:
                out.append(f"the back rest is on the front (-Y) side (its middle y {cy:+.2f}, the seat's {mid_y:+.2f}): the seat faces +Y")
    # Details: knobs, handles, dials, screens and lamps are on the front. Count the small parts sitting on the -Y face and on the +Y face (their middle within 4 cm of it).
    depth = hi.y - lo.y
    if depth > 0.25 and not SEAT.search(s):
        def small(p):
            d = p.hi - p.lo
            return max(d.x, d.y, d.z) < 0.2 and d.y < 0.08
        fronts = sum(1 for p in parts if small(p) and (p.lo.y + p.hi.y) / 2 <= lo.y + 0.04)
        backs = sum(1 for p in parts if small(p) and (p.lo.y + p.hi.y) / 2 >= hi.y - 0.04)
        if backs >= fronts + 3:
            out.append(f"{backs} small details (knobs, handles, dials) are on the back (+Y) face and {fronts} on the front: the front may face +Y")
    for role, g in prop.groups.items():
        pivot = g["pivot"]
        if re.match(r"^(Door|Drawer|Lid)", role) and g["kind"] in ("hinge", "slide") and pivot.y > mid_y + 0.02 and not re.match(r"^Lid", role):
            out.append(f"{role} is hinged at y {pivot.y:+.2f}, behind the middle ({mid_y:+.2f}): its front faces +Y")
        # a hinge is on the edge of what it turns: its pivot is within 3 cm of an end of the part, in the two axes across the hinge axis
        if g["kind"] == "hinge" and re.match(r"^(Door|Lid)", role):
            mine = [p for p in parts if p.role == role]
            if mine:
                mlo = Vector((min(p.lo.x for p in mine), min(p.lo.y for p in mine), min(p.lo.z for p in mine)))
                mhi = Vector((max(p.hi.x for p in mine), max(p.hi.y for p in mine), max(p.hi.z for p in mine)))
                axes = {"z": (0, 1), "x": (1, 2), "y": (0, 2)}[g["axis"]]
                for i in axes:
                    off = min(abs(pivot[i] - mlo[i]), abs(pivot[i] - mhi[i]))
                    if off > HINGE_EDGE and (mhi[i] - mlo[i]) > 0.05:
                        out.append(f"{role} turns about ({pivot.x:+.2f}, {pivot.y:+.2f}, {pivot.z:+.2f}), {off * 100:.0f} cm from the nearest edge of the part "
                                   f"({'xyz'[i]} {mlo[i]:+.2f}..{mhi[i]:+.2f}): the hinge is not on the {role.lower()}'s edge")
                        break
    return out


def test_floating(name, prop, parts, mounted, lo, hi):
    s = short(name)
    if re.search(LOOSE, s) or len(parts) < 2:
        return []
    n = len(parts)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if find(i) != find(j) and touching(parts[i], parts[j]):
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    if len(groups) < 2:
        return []
    ordered = sorted(groups.values(), key=len, reverse=True)
    out = []
    for grp in ordered[1:]:
        # how far from the nearest other part
        gap = min(min(distance_to_part(parts[k], v) for v in parts[i].verts) for i in grp for k in ordered[0])
        p = parts[grp[0]]
        out.append(f"{len(grp)} part(s) float {gap * 100:.1f} cm from the rest: {p.label()}")
    return out


def min_dimension(part):
    d = part.hi - part.lo
    return min(d.x, d.y, d.z)


def test_through(name, prop, parts, mounted, lo, hi):
    """A rod-like part (a handle, a beam, a leg) that passes right through another part and ends free on the far side: it pokes out of it."""
    s = short(name)
    allowed = [(ca, cb) for pat, ca, cb, _why in THROUGH_OK if re.search(pat, s)]
    if (None, None) in allowed:
        return []
    out, seen = [], {}
    for a in parts:
        if not a.rodlike:
            continue
        others = [b for b in parts if b is not a]
        for near, far in ((a.ends[0], a.ends[1]), (a.ends[1], a.ends[0])):
            near, far = Vector(near), Vector(far)
            if inside(others, far):
                continue                          # this end is buried in something: a joint
            d = far - near
            if d.length < 1e-6:
                continue
            dn = d.normalized()
            for b in others:
                if any(a.lo[i] > b.hi[i] or b.lo[i] > a.hi[i] for i in range(3)):
                    continue
                if (a.colour, b.colour) in allowed:
                    continue
                if min_dimension(b) < a.cross * 0.9:
                    continue                      # b is thinner than the rod: it is the one threaded on it (a tine on a bar), not pierced
                if inside([b], near):
                    continue                      # the rod starts inside b: it ends there, not passes through
                if b.rodlike and abs((Vector(b.ends[1]) - Vector(b.ends[0])).normalized().dot(dn)) < 0.5 and any(inside([a], Vector(e)) for e in b.ends):
                    continue                      # one end of b is inside the rod and b crosses it: a T joint (a handle on a shaft). A socket round the shaft is parallel to it and does not count
                hit = b.tree.ray_cast(near, dn, d.length)
                if hit[0] is None:
                    continue
                # it must come out the far side too: from the far end back toward b there is a face to hit
                back = b.tree.ray_cast(far, -dn, d.length)
                if back[0] is None:
                    continue
                stub = (far - back[0]).length
                key = (a.src, b.src)                  # a loop makes many copies of the same pair: report the line once
                if key in seen:
                    seen[key][1] += 1
                    continue
                seen[key] = [f"{a.label()} passes right through {b.label()} and ends free {stub * 100:.1f} cm beyond it", 1]
    return [msg + (f" (and {n - 1} more like it)" if n > 1 else "") for msg, n in seen.values()]


def test_pipes(name, prop, parts, mounted, lo, hi):
    """Free ends of pipe-like parts. Returns (problems, free ends)."""
    out, free = [], []
    for a in parts:
        if not (a.colour in PIPE_COLOURS or PIPE_WORDS.search(a.src)) or a.cross <= 0 or a.length / a.cross < PIPE_ASPECT or a.length < PIPE_MIN_LENGTH or re.search(PIPE_NOT, short(name)):
            continue
        for e in a.ends:
            e = Vector(e)
            joined = any(b is not a and (inside([b], e) or distance_to_part(b, e) <= TOUCH) for b in parts)
            if not joined and min((distance_to_part(b, e) for b in parts if b is not a), default=1e9) > PIPE_GAP:
                free.append(e)           # a pipe 1-5 cm off its neighbour is a gap (the floating test reports it); a free end is one with nothing near it
    return out, free


def exposed_tops(parts):
    """Heights of the horizontal faces that face up, are not inside another part, and add up to TOP_AREA or more."""
    levels = {}
    for part in parts:
        for poly, n in zip(part.polys, part.normals):
            if n.z < 0.99:
                continue
            vs = [part.verts[i] for i in poly]
            area = 0.0
            for k in range(1, len(vs) - 1):
                area += (vs[k] - vs[0]).cross(vs[k + 1] - vs[0]).length / 2
            c = sum(vs, Vector()) / len(vs)
            if inside(parts, c + Vector((0, 0, 0.002)), skip=None):
                continue
            key = round(vs[0].z, 3)
            levels[key] = levels.get(key, 0.0) + area
    return sorted(z for z, a in levels.items() if a >= TOP_AREA)


# =====================================================================================================================
# Run
# =====================================================================================================================

def main():
    layout = load_plain("audit_layout_for_props", SCRIPTS / "audit_layout.py") if (SCRIPTS / "audit_layout.py").exists() else load_plain("audit_layout_for_props", HERE / "audit_layout.py")
    mounted_re = re.compile(layout.WALL_HUNG + "|" + layout.CEILING_HUNG)

    built = build_all(SCRIPTS)
    problems = 0
    table = []
    geometry = {}
    declared = {k: [tuple(e[1]) for e in v] for k, v in layout.CONNECTED.items()}
    checked = 0
    for name in sorted(built):
        module, prop, parts, error = built[name]
        if ONLY and not any(o == name or o == short(name) for o in ONLY):
            continue
        if error:
            print(f"FAIL build {name}: did not build: {error}")
            problems += 1
            continue
        if not parts:
            continue
        checked += 1
        lo, hi = whole(parts)
        s = short(name)
        mounted = bool(mounted_re.search(s)) or bool(HULL.search(s))
        found = []
        found += [("origin", m) for m in test_origin(name, prop, parts, mounted, lo, hi)]
        found += [("size", m) for m in test_size(name, prop, parts, mounted, lo, hi, table)]
        found += [("front", m) for m in test_front(name, prop, parts, mounted, lo, hi)]
        found += [("floating", m) for m in test_floating(name, prop, parts, mounted, lo, hi)]
        found += [("through", m) for m in test_through(name, prop, parts, mounted, lo, hi)]
        _, free = test_pipes(name, prop, parts, mounted, lo, hi)
        want = declared.get(name, [])
        for e in free:
            if not any((e - Vector(w)).length <= 0.03 for w in want):
                found.append(("pipes", f"a pipe end hangs free at ({e.x:.2f}, {e.y:.2f}, {e.z:.2f}) and is not declared in audit_layout.CONNECTED"))
        for w in want:
            if not any((e - Vector(w)).length <= 0.03 for e in free):
                found.append(("pipes", f"audit_layout.CONNECTED lists a pipe end at {tuple(w)} but the model has no free pipe end there"))
        for test, message in found:
            print(f"FAIL {test} {name}: {message}")
            problems += 1
        geometry[name] = {"size": [round(v, 3) for v in (hi - lo)], "zmin": round(lo.z, 3), "surfaces": [round(z, 3) for z in exposed_tops(parts)]}

    if table and not QUIET:
        print("\nmeasured size against the real table (w x d x h, metres):")
        for row in table:
            print("  " + row)
    if WRITE:
        out = SCRIPTS.parent / "data" / "prop_geometry.json"
        doc = {"about": "Written by art/scripts/audit_props.py (WRITE=True): the size of every prop and the lowest point (zmin) and the heights above the origin of its exposed horizontal tops (a lamp "
                        "stands on a table top, not on the top of its bounding box). Blender coordinates, metres. audit_layout.py reads it.",
               "props": geometry}
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, indent=0, sort_keys=True), encoding="utf-8")
        print(f"wrote {out} ({len(geometry)} props)")
    print(f"\nprop audit: {checked} props, {problems} problem(s)")
    return problems


if __name__ == "__main__":
    PROBLEMS = main()
