"""Compare the models two builds of the project made, to show that a refactor of art/scripts/ changed nothing (standard library only, no Blender).

    python tools/compare_builds.py .claude/worktrees/verify-old .claude/worktrees/verify-new

Each argument is a checkout (a git worktree under .claude/worktrees, inside the project) in which tools/build_site_assets.py was run through the Blender MCP, so
it holds site/models/*.glb and out/meta/*.json. For every model: byte-identical, or different. A GLB that differs is looked at again: Blender does not always order
the vertices and the index buffer the same way between two builds from the very same code (the four humanoid aliens GP_Grey, GP_Nordic, GP_Reptilian and GP_Shadow
vary), so two files with the same JSON structure and the same set of triangles (each triangle as its three vertex positions) count as the same geometry. Exit
status 1 if anything differs beyond that, or a model is in only one build. The procedure is in .claude/skills/sonar-check.
"""

import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

from stamp_glb import project_path

COMPONENT = {5126: "f", 5123: "H", 5125: "I"}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_glb(path):
    """(JSON document, binary chunk) of a GLB."""
    raw = Path(path).read_bytes()
    json_len, _ = struct.unpack_from("<II", raw, 12)
    doc = json.loads(raw[20:20 + json_len])
    start = 20 + json_len
    bin_len, _ = struct.unpack_from("<II", raw, start)
    return doc, raw[start + 8:start + 8 + bin_len]


def read_accessor(doc, buf, index):
    """The elements of accessor `index` as tuples."""
    acc = doc["accessors"][index]
    view = doc["bufferViews"][acc["bufferView"]]
    code, width = COMPONENT[acc["componentType"]], WIDTH[acc["type"]]
    stride = view.get("byteStride") or struct.calcsize(code) * width
    base = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + code * width, buf, base + n * stride) for n in range(acc["count"])]


def triangle_set(path):
    """The triangles of a GLB as a multiset: each is (mesh name, its three vertex positions in sorted order)."""
    doc, buf = read_glb(path)
    triangles = collections.Counter()
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            positions = read_accessor(doc, buf, prim["attributes"]["POSITION"])
            indices = [i[0] for i in read_accessor(doc, buf, prim["indices"])]
            for n in range(0, len(indices) - 2, 3):
                corners = tuple(sorted(positions[indices[n + k]] for k in range(3)))
                triangles[(mesh.get("name"), corners)] += 1
    return triangles


def same_geometry(path_a, path_b):
    """Two GLBs with the same JSON structure and the same triangles, whatever the order of vertices and indices."""
    return read_glb(path_a)[0] == read_glb(path_b)[0] and triangle_set(path_a) == triangle_set(path_b)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_folder(folder_a, folder_b, pattern, deep=None):
    """{"identical": [...], "same_geometry": [...], "different": [...], "only_a": [...], "only_b": [...]} for the files of `pattern` in two folders.
    `deep(a, b)` decides a pair of files that are not byte-identical (default: they differ)."""
    names_a = {p.name for p in Path(folder_a).glob(pattern)}
    names_b = {p.name for p in Path(folder_b).glob(pattern)}
    out = {"identical": [], "same_geometry": [], "different": [], "only_a": sorted(names_a - names_b), "only_b": sorted(names_b - names_a)}
    for name in sorted(names_a & names_b):
        a, b = Path(folder_a, name), Path(folder_b, name)
        if digest(a) == digest(b):
            out["identical"].append(name)
        elif deep and deep(a, b):
            out["same_geometry"].append(name)
        else:
            out["different"].append(name)
    return out


def report(label, result):
    print(f"{label}: {len(result['identical'])} byte-identical, {len(result['same_geometry'])} same geometry (order only), {len(result['different'])} different, "
          f"{len(result['only_a'])} only in the first build, {len(result['only_b'])} only in the second")
    for key in ("same_geometry", "different", "only_a", "only_b"):
        if result[key]:
            print(f"  {key}: {', '.join(result[key][:20])}")
    return not (result["different"] or result["only_a"] or result["only_b"])


def main(argv):
    if len(argv) != 2:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    try:
        first, second = project_path(argv[0]), project_path(argv[1])
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    models = compare_folder(first / "site" / "models", second / "site" / "models", "*.glb", same_geometry)
    meta = compare_folder(first / "out" / "meta", second / "out" / "meta", "*.json")
    ok_models = report("site/models", models)
    ok_meta = report("out/meta", meta)
    return 0 if ok_models and ok_meta else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
