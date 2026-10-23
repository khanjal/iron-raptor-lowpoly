"""Find parts of models that touch nothing else (a handle floating beside a tub, a seat above its frame): the check to run before exporting.

Run in Blender after building:  import runpy; runpy.run_path(r"<repo>/art/scripts/audit.py", run_name="__main__")
Optional globals: AUDIT_MARGIN (metres of gap still counted as touching, default 0.02), AUDIT_ALL (True lists every style and skin, not one per
base model), AUDIT_NAMES (limit to names starting with these prefixes).

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


if __name__ == "__main__":
    run()
