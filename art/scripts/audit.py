"""Find parts of models that touch nothing else (a handle floating beside a tub, a seat above its frame): the check to run before exporting.

Run in Blender after building:  import runpy; runpy.run_path(r"<repo>/art/scripts/audit.py", run_name="__main__")
Optional globals: AUDIT_MARGIN (metres of gap still counted as touching, default 0.02), AUDIT_ALL (True lists every style and skin, not one per
base model), AUDIT_NAMES (limit to names starting with these prefixes), AUDIT_CLIP (True also runs the clipping check below).

The clipping check (`clipping`, pure geometry): parts of one model that poke through each other, or share a coplanar face, so the model shows
glitching surfaces (a corn cob through its husk). It finds the surface crossings between two mesh islands with a BVH tree and keeps only
  clip       two parts whose surfaces cross each other (MIN_DEPTH, 1.5 mm, applies to two solids; a sheet that crosses anything is always reported) and where neither is just plugged into the other (a stalk set into an apple has
             more than half its corners inside the apple and none of the apple's inside the stalk: fine); open sheets (leaves, husks) that cross count too;
             the report gives how deep one solid's corners sink into the other (0 when a sheet is involved). Limit: two solids that pass through each other without a corner of either inside the other (a thin rod through a plate) are not seen
  coplanar   two faces of different parts in the same plane, facing the same way and overlapping: they flicker (z-fight). Faces that only touch back to
             back are fine
A crossing between triangles that share a corner is a joint, not a clip. `contents.py` with EXPORT = False builds the Food folder into the scene to run it on.

How it works: a model is one mesh made of separate boxes and cylinders, so a mesh "island" is one part. Islands whose bounding boxes touch
(within the margin) form a group; a model with more than one group has something floating. The report lists the smaller groups' bounds so you
can find them. It is a bounding-box test: it over-reports (a part nested inside another's box is fine) and misses a gap smaller than the
margin, so treat the list as places to look at, not as a verdict. Things that are meant to be separate: loose items (books, plates, logs lying
beside a chopping block), the Energy Being's orbs, decals a few millimetres off a surface, and moving parts (doors, drawers, lids are separate
objects, not islands).
"""

import re

import bmesh
import bpy


def islands(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    seen, out = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, pts = [v], []
        seen.add(v.index)
        while stack:
            a = stack.pop()
            pts.append(a.co.copy())
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index)
                    stack.append(b)
        out.append((tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3)), len(pts)))
    bm.free()
    return out


def groups_of(isl, margin):
    n = len(isl)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            a, b = isl[i], isl[j]
            if all(a[0][k] - margin <= b[1][k] and b[0][k] - margin <= a[1][k] for k in range(3)):
                parent[find(i)] = find(j)
    out = {}
    for i in range(n):
        out.setdefault(find(i), []).append(i)
    return sorted(out.values(), key=len, reverse=True)


def _closed(tris):
    """True when every edge of these triangles is shared by exactly two of them (a solid, so 'inside' means something)."""
    count = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            k = (min(a, b), max(a, b))
            count[k] = count.get(k, 0) + 1
    return all(c == 2 for c in count.values())


def _inside(tree, point):
    """Ray-parity test against a BVH tree (a point inside a closed surface sees an odd number of hits)."""
    from mathutils import Vector
    d = Vector((0.2346, 0.5671, 0.7892)).normalized()
    origin, hits = point.copy(), 0
    for _ in range(40):
        loc, _n, _i, _dist = tree.ray_cast(origin, d)
        if loc is None:
            break
        hits += 1
        origin = loc + d * 1e-5
    return hits % 2 == 1


MIN_DEPTH = 0.0015      # m: a crossing shallower than this (a label band, a rim) is not reported


def _straddles(verts, tri, other, n):
    """True when the corners of `tri` are strictly on both sides of the plane of triangle `other` (normal n): a real crossing, not two triangles that only touch."""
    d = [(verts[i] - verts[other[0]]).dot(n) for i in tri]
    return max(d) > 1e-4 and min(d) < -1e-4


def _sink(part, solid, verts):
    """How far the corners of `part` are inside the solid part `solid`: (deepest in metres, share of the corners inside).
    Corners only: the end caps of a label inside a can are hidden faces, not a glitch."""
    if not solid["closed"]:
        return 0.0, 0.0
    pts = [verts[i] for i in part["idx"]]
    deepest, inside = 0.0, 0
    for pt in pts:
        if _inside(solid["tree"], pt):
            inside += 1
            deepest = max(deepest, solid["tree"].find_nearest(pt)[3])
    return deepest, inside / len(pts)


def clipping(obj, eps=1e-4):
    """Parts of obj (its mesh islands) that clip each other. Returns [(kind, bounds of part a, bounds of part b, number of triangle pairs, depth in mm)] (depth 0 for coplanar)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    verts = [v.co.copy() for v in bm.verts]
    key = lambda i: (round(verts[i].x / eps), round(verts[i].y / eps), round(verts[i].z / eps))
    parent = list(range(len(verts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for e in bm.edges:
        parent[find(e.verts[0].index)] = find(e.verts[1].index)
    tris_of = {}
    for f in bm.faces:
        t = tuple(v.index for v in f.verts)
        tris_of.setdefault(find(t[0]), []).append(t)
    parts = []
    for tris in tris_of.values():
        idx = {i for t in tris for i in t}
        lo = tuple(min(verts[i][k] for i in idx) for k in range(3))
        hi = tuple(max(verts[i][k] for i in idx) for k in range(3))
        parts.append({"tris": tris, "idx": idx, "lo": lo, "hi": hi, "tree": BVHTree.FromPolygons(verts, tris), "closed": _closed(tris)})
    out = []
    for a in range(len(parts)):
        for b in range(a + 1, len(parts)):
            A, B = parts[a], parts[b]
            if any(A["lo"][k] > B["hi"][k] + eps or B["lo"][k] > A["hi"][k] + eps for k in range(3)):
                continue
            crossing = 0
            for ta, tb in A["tree"].overlap(B["tree"]):
                tri_a, tri_b = A["tris"][ta], B["tris"][tb]
                if {key(i) for i in tri_a} & {key(i) for i in tri_b}:
                    continue                                                   # they share a corner: a joint
                na = (verts[tri_a[1]] - verts[tri_a[0]]).cross(verts[tri_a[2]] - verts[tri_a[0]]).normalized()
                nb = (verts[tri_b[1]] - verts[tri_b[0]]).cross(verts[tri_b[2]] - verts[tri_b[0]]).normalized()
                if abs(na.dot(nb)) <= 0.999 and _straddles(verts, tri_a, tri_b, nb) and _straddles(verts, tri_b, tri_a, na):
                    crossing += 1
            if crossing:
                (da, fa), (db, fb) = _sink(A, B, verts), _sink(B, A, verts)
                if A["closed"] and B["closed"] and max(da, db) < MIN_DEPTH:
                    continue                                                   # a band or label standing a millimetre proud, not a clip
                if (A["closed"] and fa >= 0.5 and fb <= 0.15) or (B["closed"] and fb >= 0.5 and fa <= 0.15):
                    continue                                                   # one solid is plugged into the other (a stem in an apple)
                out.append(("clip", (A["lo"], A["hi"]), (B["lo"], B["hi"]), crossing, round(max(da, db) * 1000, 1), (len(A["tris"]), A["closed"], len(B["tris"]), B["closed"])))
    out += _coplanar(parts, verts)
    bm.free()
    return out


def _coplanar(parts, verts):
    """Faces of different parts in the same plane, facing the same way, that overlap (shrunk by 10% so a shared edge is not an overlap)."""
    from mathutils.geometry import intersect_tri_tri_2d
    from mathutils import Vector
    planes = {}
    for pi_, part in enumerate(parts):
        for t in part["tris"]:
            a, b, c = (verts[i] for i in t)
            n = (b - a).cross(c - a)
            if n.length < 1e-12:
                continue
            n.normalize()
            if n.z < -0.999 and abs(a.z) < 1e-4:
                continue                                                      # the underside on the floor is never seen
            planes.setdefault((round(n.x, 2), round(n.y, 2), round(n.z, 2), round(n.dot(a) / 5e-4)), []).append((pi_, t, n))
    found = {}
    for items in planes.values():
        if len({i[0] for i in items}) < 2:
            continue
        for x in range(len(items)):
            for y in range(x + 1, len(items)):
                (pa, ta, na), (pb, tb, nb) = items[x], items[y]
                if pa == pb or na.dot(nb) < 0.999:
                    continue
                drop = max(range(3), key=lambda k, na=na: abs(na[k]))
                keep = [k for k in range(3) if k != drop]

                def shrink(t):
                    pts = [verts[i] for i in t]
                    cen = sum(pts, Vector()) / 3
                    return [Vector(((cen + (p_ - cen) * 0.9)[keep[0]], (cen + (p_ - cen) * 0.9)[keep[1]])) for p_ in pts]
                if intersect_tri_tri_2d(*shrink(ta), *shrink(tb)):
                    found[(pa, pb)] = found.get((pa, pb), 0) + 1
    return [("coplanar", (parts[a]["lo"], parts[a]["hi"]), (parts[b]["lo"], parts[b]["hi"]), n, 0.0, None) for (a, b), n in found.items()]


def gaps(obj, gap=0.002):
    """Parts (mesh islands) that touch nothing: every corner of the part is more than `gap` metres from every other part's surface. Unlike the floating check
    above (bounding boxes, 2 cm), this is a contact test, so a decoration hovering a few millimetres over a curved surface shows. Returns [(bounds, distance)]."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.verts.ensure_lookup_table()
    verts = [v.co.copy() for v in bm.verts]
    parent = list(range(len(verts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for e in bm.edges:
        parent[find(e.verts[0].index)] = find(e.verts[1].index)
    tris = {}
    for f in bm.faces:
        t = tuple(v.index for v in f.verts)
        tris.setdefault(find(t[0]), []).append(t)
    out = []
    if len(tris) > 1:
        for root, own in tris.items():
            rest = [t for r, ts in tris.items() if r != root for t in ts]
            tree = BVHTree.FromPolygons(verts, rest)
            idx = {i for t in own for i in t}
            near = min(tree.find_nearest(verts[i])[3] for i in idx)
            if near > gap:                                                    # a big part (a tray) may touch only with the other parts' corners
                mine = BVHTree.FromPolygons(verts, own)
                near = min(near, min(mine.find_nearest(verts[i])[3] for i in {i for t in rest for i in t}))
                if near > gap and mine.overlap(tree):
                    near = 0.0                                                # a bone through the end of a drumstick: no corner is near, but the surfaces cross
            if near > gap:
                out.append(((tuple(round(min(verts[i][k] for i in idx), 3) for k in range(3)), tuple(round(max(verts[i][k] for i in idx), 3) for k in range(3))), round(near * 1000, 1)))
    bm.free()
    return out


def run_clipping(prefixes=()):
    """Run `clipping` over every top-level model in the scene (names starting with `prefixes`) and print the ones that clip."""
    bodies = [o for o in bpy.data.objects if o.type == "MESH" and o.parent is None and not o.name.endswith("__old") and len(o.data.vertices)
              and (not prefixes or o.name.startswith(prefixes))]
    found = {}
    for o in sorted(bodies, key=lambda o: o.name):
        res = clipping(o)
        if res:
            found[o.name] = res
            kinds = {}
            for kind, a, b, n, _d, _i in res:
                kinds[kind] = kinds.get(kind, 0) + 1
            where = ", ".join(f"{k} x{n}" for k, n in kinds.items())
            ex = res[0]
            fmt = lambda bb: "(" + ",".join(f"{c:.3f}" for c in bb[0]) + ")-(" + ",".join(f"{c:.3f}" for c in bb[1]) + ")"
            deep = max(r[4] for r in res)
            print(f"{o.name}: {where}{f', deepest {deep} mm' if deep else ''}, e.g. {ex[0]} {fmt(ex[1])} / {fmt(ex[2])}")
    print(f"clip audit: {len(bodies)} models, {len(found)} with clipping parts")
    hover = 0
    for o in sorted(bodies, key=lambda o: o.name):
        g = gaps(o)
        if g:
            hover += 1
            print(f"{o.name}: {len(g)} part(s) touching nothing (contact test, 2 mm), nearest {max(d for _, d in g)} mm, e.g. {g[0][0]}")
    print(f"contact audit: {hover} models with a part that touches nothing")
    return found


STYLE = re.compile(r"_(Classic|Modern|Retro|Damaged|Clapboard|Barn|Corrugated|Brick|Concrete|Interior|Weathered|White|Red|Blue|Green|Yellow|Tan|Black|Grey|Beige|Teal|Cream|Log|Stone|Metal|Block|Orange|Sage|Navy|Olive|Brown|Mail|Checker|Rotten)(?=_|$)")


def run():
    margin = globals().get("AUDIT_MARGIN", 0.02)
    every = globals().get("AUDIT_ALL", False)
    prefixes = tuple(globals().get("AUDIT_NAMES") or ())
    bodies = [o for o in bpy.data.objects if o.type == "MESH" and o.parent is None and not o.name.endswith("__old") and len(o.data.vertices)
              and (not prefixes or o.name.startswith(prefixes))]
    seen, found = set(), 0
    for o in sorted(bodies, key=lambda o: o.name):
        isl = islands(o)
        if len(isl) < 2:
            continue
        groups = groups_of(isl, margin)
        if len(groups) < 2:
            continue
        found += 1
        base = STYLE.sub("", o.name)
        if not every and base in seen:
            continue
        seen.add(base)
        loose = [(tuple(round(c, 2) for c in isl[i][0]), tuple(round(c, 2) for c in isl[i][1])) for g in groups[1:] for i in g][:3]
        print(f"{o.name}: {len(groups)} groups, {sum(len(g) for g in groups[1:])} floating islands, e.g. {loose[:2]}")
    print(f"audit: {len(bodies)} models, {found} with floating parts (margin {margin} m)")
    if globals().get("AUDIT_CLIP"):
        run_clipping(prefixes)


if __name__ == "__main__":
    run()
