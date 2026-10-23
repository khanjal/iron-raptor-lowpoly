"""Colour variants as a recolour instead of a second model (standard library only).

Every model's colours are swatches of one 16 x 16 palette image (swatch i = column i % 16, row i // 16, every UV points at a swatch's middle), so two
GLBs that are the same shape in another paint differ only in which swatch some vertices point at. A paint is therefore a swap {swatch index: '#RRGGBB'}
that the viewer (or the game) applies to a copy of the palette image: no second mesh, no second file, and any colour at all (a purple apple) is just
another swap.

tools/catalog.PAINTS declares, per model, its paintable parts (a part = a palette swatch the model uses only for that part) and its presets:

    "FD_Apple_01": dict(base="Red", parts={"Skin": "cloth_red"},
                        presets={"Green": dict(was="FD_Apple_Green_01", set={"Skin": "#8FBF3A"})})

`was` is the id of the model that used to be built for the preset (old links keep working); `set` gives a swatch name or a hex per part.

    python tools/paints.py check      # every preset with a `was` whose GLB is still around must equal the swap worked out from the two GLBs
    python tools/paints.py A B        # print the swap that turns GLB A into GLB B, or say why it is not a pure recolour
"""
import json
import re
import struct
import sys
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
GRID = 16


def palette_entries():
    """[(name, '#RRGGBB')] by swatch index, read from art/scripts/common.py without importing Blender."""
    text = (ROOT / "art" / "scripts" / "common.py").read_text(encoding="utf-8")
    body = text[text.index("PALETTE = ["):text.index("GRID = 16")]
    return [(m.group(1), "#" + m.group(2).upper()) for m in re.finditer(r'\("([a-z0-9_]+)",\s*"([0-9A-Fa-f]{6})"\)', body)]


def palette():
    """swatch index -> '#RRGGBB'."""
    return [h for _, h in palette_entries()]


HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def colour(value, entries):
    """'#rrggbb' or a swatch name -> '#RRGGBB'."""
    if HEX.match(value):
        return value.upper()
    for name, h in entries:
        if name == value:
            return h
    raise ValueError(f"{value!r} is neither a swatch name nor a #RRGGBB colour")


def resolve(spec, entries):
    """One catalog.PAINTS entry -> (paintable, paints) as the manifest stores them.
    paintable: [{part, swatch, hex}]; paints: [{name, hex (the chip), swap {swatch index: hex}, was?}], the model's own paint first with an empty swap."""
    names = [n for n, _ in entries]
    parts = []
    for part, swatch in spec["parts"].items():
        if swatch not in names:
            raise ValueError(f"part {part}: no swatch named {swatch}")
        parts.append(dict(part=part, swatch=names.index(swatch), hex=entries[names.index(swatch)][1]))
    out = [dict(name=spec["base"], hex=parts[0]["hex"], swap={})]
    for name, p in spec["presets"].items():
        swap = {}
        for part, value in p["set"].items():
            row = next((x for x in parts if x["part"] == part), None)
            if row is None:
                raise ValueError(f"preset {name}: {part} is not a part of the model")
            swap[str(row["swatch"])] = colour(value, entries)
        if not swap:
            raise ValueError(f"preset {name} sets nothing")
        chip = swap.get(str(parts[0]["swatch"]), parts[0]["hex"])
        entry = dict(name=name, hex=chip, swap=swap)
        if p.get("was"):
            entry["was"] = p["was"]
        out.append(entry)
    return parts, out


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


def check():
    """Compare every declared preset that still has its old GLB with the swap worked out from the GLBs. Returns the number of mismatches."""
    import catalog
    entries = palette_entries()
    pal = [h for _, h in entries]
    models = ROOT / "site" / "models"
    bad = checked = 0
    for base, spec in catalog.PAINTS.items():
        _, paints = resolve(spec, entries)
        for p in paints[1:]:
            if not p.get("was") or not (models / f"{p['was']}.glb").exists() or not (models / f"{base}.glb").exists():
                continue
            checked += 1
            got = derive(models / f"{base}.glb", models / f"{p['was']}.glb", pal)
            if got != p["swap"]:
                bad += 1
                print(f"{base} {p['name']}: declared {p['swap']}, GLBs say {got}")
    print(f"{checked} presets checked against their GLBs, {bad} differ")
    return bad


def main(argv):
    models = ROOT / "site" / "models"
    if argv == ["check"]:
        return 1 if check() else 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        print(json.dumps(derive(models / f"{argv[0]}.glb", models / f"{argv[1]}.glb", palette())))
    except ValueError as e:
        print("no:", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
