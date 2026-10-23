"""Colour variants as a recolour instead of a second model (standard library only).

Every model's colours are swatches of one 16 x 16 palette image (swatch i = column i % 16, row i // 16, every UV points at a swatch's middle), so two
GLBs that are the same shape in another paint differ only in which swatch some vertices point at. This works out that difference as a swap
{swatch index: new colour} that the viewer (or the game) applies to a copy of the palette image, with no second mesh.

    python tools/paints.py GV_Sedan_Blue_01 GV_Sedan_Red_01     # print the swap that turns the first into the second, or say why it is not a pure recolour
    python tools/paints.py --write                              # work out every paint in tools/catalog.PAINTS from the GLBs and write art/data/paints.json

art/data/paints.json is the record the manifest is built from: it is what lets the second GLB be left out.
"""
import json
import struct
import sys
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
GRID = 16


def palette():
    """swatch index -> '#RRGGBB', read from art/scripts/common.py without importing Blender."""
    import re
    text = (ROOT / "art" / "scripts" / "common.py").read_text(encoding="utf-8")
    body = text[text.index("PALETTE = ["):text.index("GRID = 16")]
    return ["#" + m.group(2).upper() for m in re.finditer(r'\("([a-z0-9_]+)",\s*"([0-9A-Fa-f]{6})"\)', body)]


def read_vertices(path):
    """[(position, normal, swatch)] of the first mesh primitive of a GLB, positions and normals rounded so two exports compare equal."""
    raw = Path(path).read_bytes()
    jlen = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + jlen])
    blob = raw[20 + jlen + 8:]

    def column(i, n):
        a = doc["accessors"][i]
        bv = doc["bufferViews"][a["bufferView"]]
        vals = array("f")
        start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        vals.frombytes(blob[start:start + a["count"] * n * 4])
        return [tuple(vals[k * n:(k + 1) * n]) for k in range(a["count"])]

    prim = doc["meshes"][0]["primitives"][0]["attributes"]
    pos, nor, uv = column(prim["POSITION"], 3), column(prim["NORMAL"], 3), column(prim["TEXCOORD_0"], 2)
    out = []
    for p, n, t in zip(pos, nor, uv):
        out.append((tuple(round(x, 3) for x in p), tuple(round(x, 2) for x in n), int(t[0] * GRID) + GRID * int(t[1] * GRID)))
    return out


def derive(path_a, path_b, pal):
    """The swap {swatch of A: hex colour in B} that turns A into B, checked vertex by vertex. Raises ValueError when B is not A in other paint."""
    groups_a, groups_b = {}, {}
    for key_pos, key_nor, sw in read_vertices(path_a):
        groups_a.setdefault((key_pos, key_nor), []).append(sw)
    for key_pos, key_nor, sw in read_vertices(path_b):
        groups_b.setdefault((key_pos, key_nor), []).append(sw)
    if groups_a.keys() != groups_b.keys() or any(len(groups_a[k]) != len(groups_b[k]) for k in groups_a):
        raise ValueError("different shape (positions or normals do not match)")
    votes = {}   # swatch in A -> {swatch in B: how many vertices}
    for k, sa in groups_a.items():
        sb = groups_b[k]
        if len(sa) == 1:
            votes.setdefault(sa[0], {}).setdefault(sb[0], 0)
            votes[sa[0]][sb[0]] += 1
    swap = {}
    for a, vs in votes.items():
        b = max(vs, key=vs.get)
        if b != a:
            swap[a] = b
    # verify: apply the swap to A and compare with B, vertex group by vertex group
    for k, sa in groups_a.items():
        if sorted(swap.get(s, s) for s in sa) != sorted(groups_b[k]):
            raise ValueError("not a pure recolour: one swatch of the first model becomes two different swatches in the second")
    return {str(a): pal[b] for a, b in sorted(swap.items())}


def main(argv):
    pal = palette()
    models = ROOT / "site" / "models"
    if argv and argv[0] == "--write":
        import catalog
        out = {}
        for base, spec in catalog.PAINTS.items():
            entry = dict(base=spec["name"], paints={})
            for name, other in spec["others"].items():
                swap = derive(models / f"{base}.glb", models / f"{other}.glb", pal)
                entry["paints"][name] = swap
            out[base] = entry
            print(base, {n: s for n, s in entry["paints"].items()})
        (ROOT / "art" / "data" / "paints.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        print(json.dumps(derive(models / f"{argv[0]}.glb", models / f"{argv[1]}.glb", pal)))
    except ValueError as e:
        print("no:", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
