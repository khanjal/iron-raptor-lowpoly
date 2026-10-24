"""A small builder for hard-surface props, vehicles and buildings in the flat (faceted) style.

    p = Prop("GT_Barrel_01")
    p.cyl("wood_dark", (0, 0, 0.45), 0.28, 0.9, n=10)           # colour, centre, radius, height
    p.box("metal_dark", (0, 0, 0.2), (0.6, 0.6, 0.04))          # colour, centre, size
    obj, coll = p.finish()                                      # one mesh, one material, origin on the floor
    common.export_fbx(coll, "Assets/Art/Global/Props/GT_Barrel_01.fbx")

Everything is flat shaded with palette colours, no subdivision, origin on the floor at the centre of the base, 1 unit = 1 m,
facing -Y. Parts are collected per colour and joined, so a prop is one object with one material.
"""

import importlib

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector
from math import radians

import common
import emitters
importlib.reload(emitters)


INTERACTIONS = {}   # prop name -> {"parts": {...}, "slots": {...}}, filled by Prop.finish() and written out by interactive.py
THEME = {}     # colour remap applied to every part added while set: {"wood_dark": "black", ...} (see home_styles.py)


class Prop:
    def __init__(self, name):
        self.name = name
        self.parts = {}
        self.post = None                      # optional hook run on the joined object (rotate, sink into the ground...)
        self.groups = {}                      # role -> moving part (see part())
        self.slots = {}                       # name -> (position, size): where loose items can sit inside or on the prop
        self.emitters = []                    # (kind, name, position or None, frac or None, info): lights, sounds and switches (emitters.py)
        self.traits = set()                   # power, possess, jam, blackout, noisy: what the alien abilities can do with it
        self.keep = []                        # (centre, size) of boxes damage() must never drop: walls that close a container (interactive.shell)
        self.settled = None                   # (rotation matrix, drop) of the tilt damage() gave the body, so the moving parts can follow it
        self._cur = None

    def _bm(self, colour):
        colour = THEME.get(colour, colour)
        parts = self._cur["parts"] if self._cur is not None else self.parts
        if colour not in parts:
            parts[colour] = bmesh.new()
        return parts[colour]

    def part(self, role, pivot=(0, 0, 0), kind="hinge", axis="z", limit=100.0, rest=0.0):
        """Context manager: everything added inside becomes a separate moving part called `role` (Door, Drawer1, Lid...).

        pivot  the point it turns or slides about, in the prop's coordinates; the part's origin is put there so Unity can rotate it
        kind   hinge (turns about `axis` through the pivot, `limit` degrees to open; the sign picks the swing direction),
               slide (moves along `axis`, `limit` metres to open) or
               spin (a wheel: turns freely about `axis` through the pivot; limit is 360 and rest 0)
        rest   how far open the part is in the exported model (0 = shut); a damaged fridge can hang ajar

            with p.part("Door", pivot=(-0.3, -0.35, 0.9), kind="hinge", axis="z", limit=105):
                p.box("enamel_white", ...)"""
        from contextlib import contextmanager

        @contextmanager
        def _ctx():
            g = self.groups.setdefault(role, dict(parts={}, pivot=Vector(pivot), kind=kind, axis=axis, limit=limit, rest=rest))
            prev, self._cur = self._cur, g
            try:
                yield
            finally:
                self._cur = prev
        return _ctx()

    def slot(self, name, position, size=(0.2, 0.2, 0.2), part=None):
        """Mark where loose items can sit (a fridge shelf, a wardrobe rail, a drawer): exported as an empty called Slot_<name>.

        `position` is where the slot is with every part shut. `part` names the moving part the items ride on (a drawer's slot has the
        drawer's role), so Unity parents spawned items to it and they come out with the drawer."""
        self.slots[name] = (tuple(position), tuple(size), part)

    def emit(self, kind, name, pos=None, frac=None, **info):
        """Mark a light, sound or switch (kind: light, sound, switch): exported as an empty Light_<name>, Sound_<name> or Switch_<name>
        with `info` in art/data/interactions.json. Give pos (metres) or frac, a fraction (fx, fy, fz) of the model's bounding box."""
        self.emitters.append((kind, name, tuple(pos) if pos is not None else None, tuple(frac) if frac is not None else None, info))

    def trait(self, *names):
        """What the abilities can do with this prop: power, possess, jam, blackout, noisy (see emitters.py)."""
        self.traits.update(names)

    def box(self, colour, center, size, rot=(0, 0, 0), taper=1.0):
        common.add_box(self._bm(colour), center, size, rot_deg=rot, taper=taper)

    def sbox(self, colour, center, size, rot=(0, 0, 0), taper=1.0):
        """A box that holds the model together (a rocker panel, a post, the panel beside a door): damage() never drops it, however small it is."""
        self.box(colour, center, size, rot, taper)
        self.keep_solid(center, size, new=True)

    def cyl(self, colour, center, radius, height, n=8, axis="z", top_radius=None, rot=(0, 0, 0)):
        """A cylinder (or cone frustum) about centre. axis is z (upright), x or y. top_radius tapers the far end."""
        bm = self._bm(colour)
        r0 = radius
        r1 = radius if top_radius is None else top_radius
        h = height / 2
        cx, cy, cz = center
        if axis == "z":
            rings = [common.ring_z(cz - h, cx, cy, r0, r0, n=n), common.ring_z(cz + h, cx, cy, r1, r1, n=n)]
        elif axis == "x":
            rings = [common.ring_x(cx - h, cy, cz, r0, r0, n=n), common.ring_x(cx + h, cy, cz, r1, r1, n=n)]
        else:
            rings = [common.ring_y(cy - h, cx, cz, r0, r0, n=n), common.ring_y(cy + h, cx, cz, r1, r1, n=n)]
        if any(rot):                                       # rotate about the centre
            m = Matrix.Translation(Vector(center)) @ Euler([radians(a) for a in rot], "XYZ").to_matrix().to_4x4() @ Matrix.Translation(-Vector(center))
            rings = [[m @ p for p in ring] for ring in rings]
        common.loft(bm, rings)

    def loft_rings(self, colour, rings, cap=True):
        common.loft(self._bm(colour), rings, cap=cap)

    def keep_solid(self, center, size, new=False):
        """Mark the box at `center` (size `size`) as structural: damage() never drops it, however small it is.

        new=True is for a box that did not exist before it was marked: damage() then skips it without drawing a random number, so the parts
        built after it are dropped exactly as they were. A box that existed (the walls of a shell) still draws, and the draw is ignored."""
        self.keep.append((tuple(center), tuple(size), new))

    def _kept(self, xs, ys, zs):
        """None for an island that is not marked with keep_solid(), else "new" or "old" (see keep_solid)."""
        c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
        for k in self.keep:
            if all(abs(c[i] - k[0][i]) < 1e-4 for i in range(3)):
                return "new" if k[2] else "old"
        return None

    def _orient(self, faces, facing=None, away_from=None, toward=None):
        """Flip all of `faces` together so they face a direction (`facing`), away from a point or toward one, judged over the whole set."""
        score = 0.0
        for f in faces:
            c = f.calc_center_median()
            ref = Vector(facing) if facing is not None else (c - Vector(away_from) if away_from is not None else Vector(toward) - c)
            score += f.normal.dot(ref)
        if score < 0:
            for f in faces:
                f.normal_flip()

    def quads(self, colour, grid, thick=0.0, walls=True, wrap=False, facing=None, away_from=None, toward=None):
        """A curved sheet from a grid of points (rows of equal length), for leaves, husks and shells that a box or lathe cannot make.

        wrap       the last column joins the first (a tube); otherwise the sheet is open
        facing / away_from / toward   which way the front faces (a direction, away from a point, toward a point); the whole sheet is flipped to suit
        thick      a back surface this far behind the front (a leaf seen from both sides), with walls on the open edges unless walls=False
        A sheet without thick is one-sided: it is invisible from behind (Unity culls back faces)."""
        bm = self._bm(colour)
        rows = [[bm.verts.new(Vector(pt)) for pt in row] for row in grid]
        nr, nc = len(rows), len(rows[0])
        ncols = nc if wrap else nc - 1
        front = [bm.faces.new((rows[i][j], rows[i][(j + 1) % nc], rows[i + 1][(j + 1) % nc], rows[i + 1][j])) for i in range(nr - 1) for j in range(ncols)]
        bm.normal_update()
        self._orient(front, facing, away_from, toward)
        if not thick:
            return
        bm.normal_update()
        back = {v: bm.verts.new(v.co - v.normal * thick) for row in rows for v in row}
        faces = list(front)
        for f in front:                                    # the back is the oriented front reversed (the front may have been flipped above)
            faces.append(bm.faces.new([back[v] for v in reversed(list(f.verts))]))
        if walls:
            edges = [(rows[0][j], rows[0][(j + 1) % nc]) for j in range(ncols)] + [(rows[-1][j], rows[-1][(j + 1) % nc]) for j in range(ncols)]
            if not wrap:
                edges += [(rows[i][0], rows[i + 1][0]) for i in range(nr - 1)] + [(rows[i][-1], rows[i + 1][-1]) for i in range(nr - 1)]
            faces += [bm.faces.new((a, b, back[b], back[a])) for a, b in edges]
            bmesh.ops.recalc_face_normals(bm, faces=faces)

    def poly(self, colour, points, facing=None, away_from=None, toward=None):
        """One flat or slightly bent face from 3 or more points, turned to face a direction, away from a point or toward one."""
        bm = self._bm(colour)
        f = bm.faces.new([bm.verts.new(Vector(pt)) for pt in points])
        bm.normal_update()
        self._orient([f], facing, away_from, toward)

    def damage(self, seed=0, drop=0.2, tilt=5.0, grime=2, max_part=0.0015, grime_scale=1.0):
        """Make the prop look broken and neglected: drop some small parts, tilt and sag the whole thing, and splash dark grime on it.

        Deterministic for a given seed. Parts are the loose boxes and cylinders a prop is built from; the small ones (loose handles,
        knobs, books, rungs) each have a chance `drop` of going missing, the big ones never do; max_part is the bounding-box volume in m3
        below which a part counts as small (raise it for vehicles and buildings, whose loose parts are bigger). `post` is set so finish() tilts the
        result by up to `tilt` degrees and re-seats it on the floor."""
        import random
        rng = random.Random(seed)
        for colour, bm in list(self.parts.items()):
            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            parent = list(range(len(bm.verts)))

            def find(i):
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i
            for e in bm.edges:
                a, b = find(e.verts[0].index), find(e.verts[1].index)
                if a != b:
                    parent[a] = b
            islands = {}
            for v in bm.verts:
                islands.setdefault(find(v.index), []).append(v)
            kill = []
            for verts in islands.values():
                xs = [v.co.x for v in verts]; ys = [v.co.y for v in verts]; zs = [v.co.z for v in verts]
                vol = (max(xs) - min(xs)) * (max(ys) - min(ys)) * (max(zs) - min(zs))
                if vol < max_part:
                    kept = self._kept(xs, ys, zs)
                    if kept == "new":
                        continue                                  # no draw: the random sequence of every other part stays what it was
                    if rng.random() < drop and kept is None:
                        kill.extend(verts)
            if kill:
                bmesh.ops.delete(bm, geom=kill, context="VERTS")
        # grime: dark flat patches lying on flat upward-facing surfaces that nothing covers (never floating, buried or hidden)
        from mathutils.bvhtree import BVHTree
        trees = [BVHTree.FromBMesh(bm) for bm in self.parts.values() if len(bm.faces)]
        up = Vector((0.0, 0.0, 1.0))
        faces = []
        for bm in self.parts.values():
            bm.normal_update()
            for f in bm.faces:
                if f.normal.z > 0.999 and f.calc_area() > 0.004:
                    c = f.calc_center_median() + up * 0.003
                    if any(t.ray_cast(c, up)[0] is not None for t in trees):
                        continue                                  # something is above it: roof, lid, cabin
                    cs = [v.co for v in f.verts]
                    faces.append((f.calc_area(), (min(v.x for v in cs), max(v.x for v in cs)), (min(v.y for v in cs), max(v.y for v in cs)), cs[0].z))
        if faces and grime:
            for _ in range(grime):
                _, (x0, x1), (y0, y1), z = rng.choices(faces, weights=[f[0] for f in faces])[0]
                sx = min(rng.uniform(0.06, 0.18) * grime_scale, (x1 - x0) * 0.9)
                sy = min(rng.uniform(0.05, 0.14) * grime_scale, (y1 - y0) * 0.9)
                cx = rng.uniform(x0 + sx / 2, x1 - sx / 2); cy = rng.uniform(y0 + sy / 2, y1 - sy / 2)
                self.box("rust_dark", (cx, cy, z + 0.002), (sx, sy, 0.004))

        def settle(obj):
            import bpy
            obj.rotation_euler = (radians(rng.uniform(-tilt, tilt)), radians(rng.uniform(-tilt, tilt)), radians(rng.uniform(-tilt, tilt)))
            rot = obj.rotation_euler.to_matrix()                   # the moving parts are built untilted: finish() puts them through the same turn and drop
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            low = min(v.co.z for v in obj.data.vertices)
            for g in self.groups.values():                         # a wheel is a moving part: the lowest point is the body's or a part's, whichever is lower
                for bm in g["parts"].values():
                    low = min([low] + [(rot @ v.co).z for v in bm.verts])
            for v in obj.data.vertices:
                v.co.z -= low
            self.settled = (rot, low)
        if tilt:
            self.post = settle

    def finish(self, collection_name=None):
        emitters.apply(self)
        coll = common.fresh_collection(collection_name or self.name)
        common.setup_scene()
        objs = []
        for colour, bm in self.parts.items():
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
            objs.append(common.new_mesh_object(f"{self.name}_{colour}", bm, coll, colour, flat=True))
        obj = common.join(objs, self.name)
        obj.location = (0, 0, 0)
        if self.post is not None:
            self.post(obj)
        # moving parts: one object per role, its origin on the pivot, parented to the body
        pre = common.name_prefix()                                   # (set while building in a shared Blender file: see common.configure)
        for role in [o.name for o in bpy.data.objects if o.name in {pre + r for r in self.groups}]:
            stale = bpy.data.objects[role]
            stale.name = f"{role}__old"                              # free the plain role names for this prop
            if stale.data is not None:
                stale.data.name = f"{role}__old"                     # and the mesh names, so new meshes are not called Door.101
        reg = {"parts": {}, "slots": {}}
        for role, g in self.groups.items():
            gobjs = []
            if self.settled is not None:                             # a tilted body: tilt the part with it, pivot and all (the axis stays world x, y or z, so a wrecked door or wheel is a few degrees off its true hinge line)
                rot, low = self.settled
                m = rot.to_4x4()
                for bm in g["parts"].values():
                    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
                    for v in bm.verts:
                        v.co.z -= low
                g["pivot"] = m @ g["pivot"]
                g["pivot"].z -= low
            for colour, bm in g["parts"].items():
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
                gobjs.append(common.new_mesh_object(f"{self.name}_{role}_{colour}", bm, coll, colour, flat=True))
            if not gobjs:
                continue
            part_obj = common.join(gobjs, role)
            piv = g["pivot"]
            for v in part_obj.data.vertices:
                v.co -= piv
            part_obj.location = piv
            part_obj.parent = obj
            idx = {"x": 0, "y": 1, "z": 2}[g["axis"]]
            if g["rest"]:
                if g["kind"] == "hinge":
                    e = list(part_obj.rotation_euler); e[idx] = radians(g["rest"]); part_obj.rotation_euler = e
                else:
                    loc = list(part_obj.location); loc[idx] += g["rest"]; part_obj.location = loc
            reg["parts"][role] = dict(kind=g["kind"], axis=g["axis"], pivot=[round(v, 4) for v in piv], limit=g["limit"], rest=g["rest"])
        for name, (pos, size, on_part) in self.slots.items():
            stale = bpy.data.objects.get(f"{pre}Slot_{name}")
            if stale is not None:
                stale.name = f"{pre}Slot_{name}__old"
            e = bpy.data.objects.new(f"{pre}Slot_{name}", None)
            e.empty_display_type = "PLAIN_AXES"
            e.empty_display_size = 0.05
            coll.objects.link(e)
            g = self.groups.get(on_part) if on_part else None
            where = Vector(pos)
            if g is not None and g["rest"]:
                idx = {"x": 0, "y": 1, "z": 2}[g["axis"]]
                if g["kind"] == "slide":
                    where[idx] += g["rest"]
                else:
                    where = g["pivot"] + (Matrix.Rotation(radians(g["rest"]), 3, g["axis"].upper()) @ (where - g["pivot"]))
            e.parent = obj                                          # hung off the body: a parent chain would not survive the FBX axis bake
            e.location = where                                      # where the part's contents are in the exported pose
            reg["slots"][name] = dict(position=[round(v, 4) for v in pos], size=[round(v, 4) for v in size], part=on_part)
        if self.emitters:
            reg["emitters"] = {}
            lo = [min(v.co[i] for v in obj.data.vertices) for i in range(3)]
            hi = [max(v.co[i] for v in obj.data.vertices) for i in range(3)]
            for kind, name, pos, frac, info in self.emitters:
                where = Vector(pos) if pos is not None else Vector([lo[i] + (hi[i] - lo[i]) * frac[i] for i in range(3)])
                label = f"{kind.capitalize()}_{name}"
                stale = bpy.data.objects.get(pre + label)
                if stale is not None:
                    stale.name = f"{pre}{label}__old"
                e = bpy.data.objects.new(pre + label, None)
                e.empty_display_type = {"light": "SPHERE", "sound": "CIRCLE", "switch": "CUBE"}.get(kind, "PLAIN_AXES")
                e.empty_display_size = 0.06
                coll.objects.link(e)
                e.parent = obj
                e.location = where
                reg["emitters"][label] = dict(kind=kind, position=[round(v, 4) for v in where], **info)
        if self.traits:
            reg["traits"] = sorted(self.traits)
        if reg["parts"] or reg["slots"] or self.emitters or self.traits:
            INTERACTIONS[self.name] = reg
        self.parts = {}
        self.groups = {}
        self.settled = None
        return obj, coll


def write_interactions():
    """Merge this session's INTERACTIONS into art/data/interactions.json (entries from props built earlier stay)."""
    import json
    out = common.REPO / "art" / "data" / "interactions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    merged = {}
    if out.exists():
        try:
            merged = json.loads(out.read_text(encoding="utf-8")).get("props", {})
        except ValueError:
            merged = {}
    merged.update(INTERACTIONS)
    doc = {
        "about": "What can be done with each prop (interactive.py, emitters.py). Coordinates are Blender space (X right, Y back, Z up, "
                 "front is -Y), metres. parts: hinge turns about `axis` through `pivot`, `limit` degrees to open (sign = direction); slide moves "
                 "along `axis`, `limit` metres to open; spin (a wheel) turns freely about `axis` through `pivot`, `limit` is 360; `rest` is the exported pose (0 = shut). slots: where loose items go; one with a `part` rides "
                 "on that moving part. emitters: lights, sounds and switches (Light_/Sound_/Switch_ empties) with what they do; traits: power, "
                 "possess, jam, blackout, noisy (what the alien abilities can do with it). See emitters.py for the fields.",
        "props": dict(sorted(merged.items())),
    }
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return out


def wheel(p, colour_tyre, colour_hub, x, y, z, radius, width, n=10):
    """A wheel on the X axis centred at (x, y, z); the hub disc faces outwards."""
    p.cyl(colour_tyre, (x, y, z), radius, width, n=n, axis="x")
    out = 1 if x >= 0 else -1
    p.cyl(colour_hub, (x + out * (width / 2 + 0.004), y, z), radius * 0.55, 0.012, n=n, axis="x")


def rod(p, colour, a, b, w=0.06, h=None):
    """A beam between two points a and b (its ends sit exactly on them), w wide and h deep (h defaults to w)."""
    from math import degrees, pi
    a, b = Vector(a), Vector(b)
    d = b - a
    if d.normalized().dot(Vector((0.0, 1.0, 0.0))) < -0.9999:                 # straight back along -Y: the quaternion's axis is arbitrary, so turn about X
        e = Euler((pi, 0.0, 0.0))
    else:
        e = Vector((0.0, 1.0, 0.0)).rotation_difference(d.normalized()).to_euler("XYZ")
    p.box(colour, tuple((a + b) / 2), (w, d.length, h or w), rot=(degrees(e.x), degrees(e.y), degrees(e.z)))


def lathe(p, colour, profile, n=6, cx=0.0, cy=0.0, z0=0.0, cap=True, phase=0.0):
    """A solid of revolution about the vertical axis from (height, radius) pairs, bottom to top.

    cap=False leaves the ends open (a band or ring: a capped thin band would put a disc across the model).
    phase turns the polygon by that many degrees about the axis (so a 12-sided deck can line up with a ring of wall panels)."""
    from math import cos, radians, sin
    rings = [common.ring_z(z0 + z, cx, cy, max(r, 0.0001), max(r, 0.0001), n=n) for z, r in profile]
    if phase:
        c, s = cos(radians(phase)), sin(radians(phase))
        rings = [[Vector((cx + (pt.x - cx) * c - (pt.y - cy) * s, cy + (pt.x - cx) * s + (pt.y - cy) * c, pt.z)) for pt in ring] for ring in rings]
    p.loft_rings(colour, rings, cap=cap)


def ball(p, colour, centre, radius, n=7, squash=1.0, rings=5):
    """A faceted sphere (n sides, `rings` latitude rings between the poles), flattened vertically by `squash`."""
    from math import cos, pi, sin
    cx, cy, cz = centre
    profile = []
    for k in range(rings + 2):
        phi = pi * k / (rings + 1)
        profile.append((cz - radius * squash * cos(phi), radius * sin(phi)))
    p.loft_rings(colour, [common.ring_z(z, cx, cy, max(r, 0.0001), max(r, 0.0001), n=n) for z, r in profile])


# ===== Walls, slabs and roofs shared by buildings.py and kit.py =================================================
T = 0.25                                                          # wall thickness


def wall_run(p, colour, a, b, z0, height, openings=(), thick=T, glass=True, door_colour="wood_dark", trim="paint_white", fill=True, frame=True):
    """A straight axis-aligned wall from a=(x, y) to b=(x, y) with openings [(offset, width, sill, height), ...].

    Openings with a sill of 0 are doors (filled with a closed door); the others are windows (filled with glass and framed).
    fill=False leaves the openings empty but framed, for the modular kit where doors and windows are separate pieces;
    frame=False also leaves out the frame (a bare hole: a pop hole, a vent)."""
    ax, ay = a
    bx, by = b
    length = abs(bx - ax) + abs(by - ay)
    along_x = abs(bx - ax) > abs(by - ay)
    sign = (1 if bx > ax else -1) if along_x else (1 if by > ay else -1)

    def put(off0, off1, zz0, zz1, col, th=thick, inset=0.0):
        if off1 - off0 < 1e-4 or zz1 - zz0 < 1e-4:
            return
        mid = (off0 + off1) / 2
        w = off1 - off0
        h = zz1 - zz0
        if along_x:
            p.box(col, (ax + sign * mid, ay + inset, z0 + zz0 + h / 2), (w, th, h))
        else:
            p.box(col, (ax + inset, ay + sign * mid, z0 + zz0 + h / 2), (th, w, h))

    cursor = 0.0
    for off, w, sill, oh in sorted(openings):
        put(cursor, off, 0, height, colour)                        # solid wall up to the opening
        put(off, off + w, 0, sill, colour)                         # under a window
        put(off, off + w, sill + oh, height, colour)               # the header
        if sill == 0:
            if fill:
                put(off + 0.08, off + w - 0.08, 0, oh - 0.06, door_colour, th=0.08)       # a closed door
            if frame:
                put(off - 0.06, off, 0, oh, trim, th=thick + 0.04)                          # jambs
                put(off + w, off + w + 0.06, 0, oh, trim, th=thick + 0.04)
        else:
            if glass and fill:
                put(off + 0.05, off + w - 0.05, sill + 0.05, sill + oh - 0.05, "glass", th=0.05)
            if frame:
                put(off - 0.05, off + w + 0.05, sill - 0.06, sill, trim, th=thick + 0.1)    # sill
                put(off - 0.05, off, sill, sill + oh, trim, th=thick + 0.04)
                put(off + w, off + w + 0.05, sill, sill + oh, trim, th=thick + 0.04)
                put(off + w / 2 - 0.02, off + w / 2 + 0.02, sill, sill + oh, trim, th=0.06) # a mullion
        cursor = off + w
    put(cursor, length, 0, height, colour)


def slab(p, colour, cx, cy, w, d, z, thick=0.2):
    p.box(colour, (cx, cy, z + thick / 2), (w, d, thick))


def gable_roof(p, colour, cx, cy, w, d, z_eave, rise, overhang=0.6, along="x", thick=0.0):
    """A solid prism roof: eaves at z_eave, ridge z_eave + rise, ridge running along x or y, overhanging by overhang."""
    if along == "x":
        hw, hd = w / 2 + overhang, d / 2 + overhang
        tri = lambda x: [Vector((x, cy - hd, z_eave)), Vector((x, cy, z_eave + rise)), Vector((x, cy + hd, z_eave)), Vector((x, cy, z_eave - 0.15))]
        p.loft_rings(colour, [tri(cx - hw), tri(cx + hw)])
    else:
        hw, hd = w / 2 + overhang, d / 2 + overhang
        tri = lambda y: [Vector((cx - hw, y, z_eave)), Vector((cx, y, z_eave + rise)), Vector((cx + hw, y, z_eave)), Vector((cx, y, z_eave - 0.15))]
        p.loft_rings(colour, [tri(cy - hd), tri(cy + hd)])


