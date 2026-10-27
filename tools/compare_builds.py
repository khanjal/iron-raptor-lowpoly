"""Compare the models two builds of the project made, to show that a refactor of art/scripts/ changed nothing (standard library only, no Blender).

    python tools/compare_builds.py .claude/worktrees/verify-old .claude/worktrees/verify-new

Each argument is a checkout (a git worktree under .claude/worktrees, inside the project) in which tools/build_site_assets.py was run through the Blender MCP, so
it holds site/models/*.glb and out/meta/*.json; art/data/interactions.json (hinge pivots, axes, limits: it is not in the GLB) is compared too. For every file:
byte-identical, or different. A GLB that differs is looked at again, because Blender does not always order the vertices and the index buffer the same way between
two builds from the very same code (the four humanoid aliens GP_Grey, GP_Nordic, GP_Reptilian and GP_Shadow vary). It counts as the same geometry when the JSON
structure is equal and so are, in any order of vertices and triangles: every triangle with its winding and the full attributes of its three corners (position,
normal, UV, joints, weights, ...), every accessor that is not a primitive's (animation times and values, inverse bind matrices), and every buffer view that no
accessor reads (embedded images). Anything else that differs, a model in only one build, or a missing or empty folder makes the exit status 1 (2 for a wrong call).
The procedure is in .claude/skills/sonar-check.
"""

import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

from stamp_glb import project_path

COMPONENT = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}
IDENTICAL, SAME_GEOMETRY, DIFFERENT, ONLY_FIRST, ONLY_SECOND = "identical", "same_geometry", "different", "only_first", "only_second"
UNREADABLE = (ValueError, KeyError, IndexError, TypeError, struct.error)


def read_glb(path):
    """(JSON document, binary chunk) of a GLB."""
    raw = Path(path).read_bytes()
    json_len, _ = struct.unpack_from("<II", raw, 12)
    doc = json.loads(raw[20:20 + json_len])
    start = 20 + json_len
    bin_len, _ = struct.unpack_from("<II", raw, start)
    return doc, raw[start + 8:start + 8 + bin_len]


def read_accessor(doc, buf, index):
    """The elements of accessor `index` as tuples (raw component values). ValueError for an accessor this tool does not read (sparse, or without a buffer view)."""
    acc = doc["accessors"][index]
    if "sparse" in acc or "bufferView" not in acc:
        raise ValueError(f"accessor {index} is sparse or has no buffer view")
    view = doc["bufferViews"][acc["bufferView"]]
    code, width = COMPONENT[acc["componentType"]], WIDTH[acc["type"]]
    stride = view.get("byteStride") or struct.calcsize(code) * width
    base = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + code * width, buf, base + n * stride) for n in range(acc["count"])]


def primitive_accessors(doc):
    """The indices of the accessors that mesh primitives read (attributes, indices, morph targets)."""
    used = set()
    for mesh in doc.get("meshes", []):
        for prim in mesh["primitives"]:
            used.update(prim["attributes"].values())
            if "indices" in prim:
                used.add(prim["indices"])
            for target in prim.get("targets", []):
                used.update(target.values())
    return used


def canonical_triangle(corners):
    """The three corners rotated so the smallest comes first: the same triangle with the same winding gives the same tuple, a flipped one does not."""
    start = corners.index(min(corners))
    return tuple(corners[start:] + corners[:start])


def triangle_set(doc, buf):
    """The triangles of a GLB as a multiset: (mesh name, primitive material, canonical corners), each corner the tuple of all its attribute values."""
    triangles = collections.Counter()
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            attributes = {name: read_accessor(doc, buf, index) for name, index in sorted(prim["attributes"].items())}
            vertices = list(zip(*attributes.values()))
            indices = [i[0] for i in read_accessor(doc, buf, prim["indices"])] if "indices" in prim else list(range(len(vertices)))
            for n in range(0, len(indices) - 2, 3):
                corners = [vertices[indices[n + k]] for k in range(3)]
                triangles[(mesh.get("name"), prim.get("material"), canonical_triangle(corners))] += 1
    return triangles


def other_data(doc, buf):
    """What the primitives do not read: every other accessor's elements (animations, inverse bind matrices) and the bytes of every buffer view no accessor uses (images)."""
    used = primitive_accessors(doc)
    accessors = {i: read_accessor(doc, buf, i) for i in range(len(doc.get("accessors", []))) if i not in used}
    covered = {a["bufferView"] for a in doc.get("accessors", []) if "bufferView" in a}
    views = {}
    for i, view in enumerate(doc.get("bufferViews", [])):
        if i not in covered:
            start = view.get("byteOffset", 0)
            views[i] = buf[start:start + view["byteLength"]]
    return accessors, views


def same_geometry(path_a, path_b):
    """True when two GLBs agree as the module docstring says; False when they differ or one cannot be read."""
    try:
        doc_a, buf_a = read_glb(path_a)
        doc_b, buf_b = read_glb(path_b)
        return (doc_a == doc_b and triangle_set(doc_a, buf_a) == triangle_set(doc_b, buf_b) and other_data(doc_a, buf_a) == other_data(doc_b, buf_b))
    except UNREADABLE + (json.JSONDecodeError,):
        return False


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_folder(folder_a, folder_b, pattern, deep=None):
    """{IDENTICAL: [...], SAME_GEOMETRY: [...], DIFFERENT: [...], ONLY_FIRST: [...], ONLY_SECOND: [...]} for the files of `pattern` in two folders.
    `deep(a, b)` decides a pair that is not byte-identical (default: it is different)."""
    names_a = {p.name for p in Path(folder_a).glob(pattern)}
    names_b = {p.name for p in Path(folder_b).glob(pattern)}
    out = {IDENTICAL: [], SAME_GEOMETRY: [], DIFFERENT: [], ONLY_FIRST: sorted(names_a - names_b), ONLY_SECOND: sorted(names_b - names_a)}
    for name in sorted(names_a & names_b):
        a, b = Path(folder_a, name), Path(folder_b, name)
        if digest(a) == digest(b):
            out[IDENTICAL].append(name)
        elif deep and deep(a, b):
            out[SAME_GEOMETRY].append(name)
        else:
            out[DIFFERENT].append(name)
    return out


def compared(result):
    return len(result[IDENTICAL]) + len(result[SAME_GEOMETRY]) + len(result[DIFFERENT])


def report(label, result):
    """Print one line per folder (and the names that matter); True when something was compared and nothing differs."""
    print(f"{label}: {compared(result)} compared: {len(result[IDENTICAL])} byte-identical, {len(result[SAME_GEOMETRY])} same geometry (order only), "
          f"{len(result[DIFFERENT])} different, {len(result[ONLY_FIRST])} only in the first build, {len(result[ONLY_SECOND])} only in the second")
    for key in (SAME_GEOMETRY, DIFFERENT, ONLY_FIRST, ONLY_SECOND):
        names = result[key]
        if names:
            print(f"  {key}: {', '.join(names[:20])}" + (f" ... and {len(names) - 20} more" if len(names) > 20 else ""))
    return compared(result) > 0 and not (result[DIFFERENT] or result[ONLY_FIRST] or result[ONLY_SECOND])


def interactions_agree(first, second):
    """art/data/interactions.json (written by the build, not part of any GLB) is the same in both trees; a file missing from both counts as agreeing."""
    a, b = first / "art" / "data" / "interactions.json", second / "art" / "data" / "interactions.json"
    agree = a.exists() == b.exists() and (not a.exists() or digest(a) == digest(b))
    print("art/data/interactions.json:", "identical" if agree else "DIFFERENT or missing in one build")
    return agree


def main(argv):
    if len(argv) != 2:
        print("\n\n".join(__doc__.split("\n\n")[:2]), file=sys.stderr)
        return 2
    try:
        first, second = project_path(argv[0]), project_path(argv[1])
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    models = compare_folder(first / "site" / "models", second / "site" / "models", "*.glb", same_geometry)
    meta = compare_folder(first / "out" / "meta", second / "out" / "meta", "*.json")
    if not compared(models):
        print(f"no GLBs to compare in {first / 'site' / 'models'} and {second / 'site' / 'models'}: was the build run in both trees?", file=sys.stderr)
        return 2
    checks = [report("site/models", models), report("out/meta", meta), interactions_agree(first, second)]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
