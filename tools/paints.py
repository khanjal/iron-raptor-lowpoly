"""Colour variants as a recolour instead of a second model (standard library only).

Every model's colours are swatches of one 16 x 16 palette image (swatch i = column i % 16, row i // 16, every UV points at a swatch's middle), so two
GLBs that are the same shape in another paint differ only in which swatch some vertices point at. A paint is therefore a swap {swatch index: '#RRGGBB'}
that the viewer (or the game) applies to a copy of the palette image: no second mesh, no second file, and any colour at all (a purple apple) is just
another swap.

tools/catalog.PAINTS declares, per model, its paintable parts (a part = a palette swatch the model uses only for that part) and its presets:

    "FD_Apple_01": dict(base="Red", parts={"Skin": "cloth_red"},
                        presets={"Green": dict(was="FD_Apple_Green_01", set={"Skin": "#8FBF3A"})})

`was` is the id of the model that used to be built for the preset (old links keep working); `set` gives a swatch name or a hex per part.

    python tools/paints.py check [DIR]  # (DIR = a folder of GLBs instead of site/models) every preset with a `was` whose GLB is still around must equal the swap worked out from the two GLBs
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


# The colours every model offers when it has no presets of its own: name -> swatch name of the palette (so the colours stay the palette's)
COMMON = [("Red", "cloth_red"), ("Orange", "basket_orange"), ("Yellow", "paint_yellow"), ("Green", "tractor_green"), ("Blue", "truck_blue"), ("Purple", "alien_violet"),
          ("Pink", "pink"), ("Brown", "fabric_brown"), ("White", "paint_white"), ("Grey", "fabric_grey"), ("Black", "black")]
MAX_PARTS = 5          # a model offers at most this many colour boxes
MIN_SHARE = 0.03       # a swatch that covers less of the surface than this is not offered


def common_colours(entries):
    """[{name, hex}] of COMMON, for the manifest's palette.common."""
    return [dict(name=n, hex=colour(sw, entries)) for n, sw in COMMON]


def neutral(hex_):
    """True for black, white and greys (little colour, or very dark): they are not what a person means by 'the colour' of a model."""
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hi, lo = max(r, g, b), min(r, g, b)
    return hi < 0.18 or (hi - lo) / hi < 0.25


def part_names():
    """art/data/part_names.json: {model id: {palette swatch name: the area it colours, "$main": the name of the only part of a single-colour model}}, for the models whose colours are named by area
    ("Handle", "Blade", "Tyres") instead of by the swatch's own name ("Metal dark"). A swatch with no entry keeps `part_label`."""
    path = ROOT / "art" / "data" / "part_names.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def part_label(swatch_name):
    """'skin_tan' -> 'Skin tan': what the swatch is called in the palette (the colour word says which swatch it is, even after the person repaints it)."""
    return swatch_name.replace("_", " ").capitalize()


def surface_by_swatch(path):
    """{swatch index: surface area} of a GLB (triangle areas in the model's own units; node transforms are not applied)."""
    path = Path(path)
    raw = path.read_bytes()
    jlen = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + jlen])
    blob = raw[20 + jlen + 8:]
    kinds = {5126: "f", 5123: "H", 5125: "I", 5121: "B"}

    def column(i):
        a = doc["accessors"][i]
        if "sparse" in a or a.get("normalized") or "bufferView" not in a:
            raise ValueError(f"{path.name}: accessor {i} is sparse, normalized or empty; only plain accessors are read")
        bv = doc["bufferViews"][a["bufferView"]]
        vals = array(kinds[a["componentType"]])
        n = dict(SCALAR=1, VEC2=2, VEC3=3)[a["type"]]
        start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        size = n * vals.itemsize
        stride = bv.get("byteStride") or size                       # interleaved buffers step by more than one element
        if stride == size:
            vals.frombytes(blob[start:start + a["count"] * size])
        else:
            for k in range(a["count"]):
                vals.frombytes(blob[start + k * stride:start + k * stride + size])
        return vals

    out = {}
    for node in doc.get("nodes", []):
        if "mesh" not in node:
            continue
        for prim in doc["meshes"][node["mesh"]]["primitives"]:
            at = prim["attributes"]
            pos, uv = column(at["POSITION"]), column(at["TEXCOORD_0"])
            idx = column(prim["indices"]) if "indices" in prim else range(len(pos) // 3)
            for t in range(0, len(idx) - 2, 3):
                a, b, c = idx[t], idx[t + 1], idx[t + 2]
                u = [pos[b * 3 + k] - pos[a * 3 + k] for k in range(3)]
                v = [pos[c * 3 + k] - pos[a * 3 + k] for k in range(3)]
                area = 0.5 * ((u[1] * v[2] - u[2] * v[1]) ** 2 + (u[2] * v[0] - u[0] * v[2]) ** 2 + (u[0] * v[1] - u[1] * v[0]) ** 2) ** 0.5
                sw = int(uv[a * 2] * GRID) + GRID * int(uv[a * 2 + 1] * GRID)
                out[sw] = out.get(sw, 0.0) + area
    return out


def auto_parts(path, entries):
    """The colours of a model as `paintable` parts [{part, swatch, hex}], without a catalog entry: the swatches that cover the most surface (not the glowing or
    see-through ones, not slivers), at most MAX_PARTS. The first is the main colour, the one the common presets repaint: the biggest swatch (not skin or hair), unless that is
    black, white or grey and a coloured one covers at least half as much. Recolouring a swatch recolours every face that uses it, which is what a part is here."""
    area = surface_by_swatch(path)
    total = sum(area.values()) or 1.0
    rows = [(sw, a / total) for sw, a in sorted(area.items(), key=lambda x: -x[1])
            if sw < len(entries) and not entries[sw][0].startswith(("glow_", "clear_")) and a / total >= MIN_SHARE]
    if not rows:
        return []
    body = [r for r in rows if not entries[r[0]][0].startswith(("skin", "hair"))] or rows      # a person's main colour is their clothes, not their skin
    main = next((r for r in body if not neutral(entries[r[0]][1]) and r[1] >= body[0][1] / 2), body[0])
    rows = ([main] + [r for r in rows if r is not main])[:MAX_PARTS]
    parts = [dict(part="Main" if i == 0 else part_label(entries[sw][0]), swatch=sw, hex=entries[sw][1]) for i, (sw, _) in enumerate(rows)]
    return parts


def themes(entries):
    """The colour themes of art/scripts/home_styles.py (THEMES: Modern, Retro, Damaged) as {theme: {swatch index: '#RRGGBB'}}, read without importing Blender.
    A theme maps a swatch to another one wherever a piece uses it; swatches a model does not use are simply not in its mesh. Identity entries are dropped."""
    import ast
    text = (ROOT / "art" / "scripts" / "home_styles.py").read_text(encoding="utf-8")
    start = text.index("THEMES = {")
    table = ast.literal_eval(text[start + len("THEMES = "):text.index("\n}\n", start) + 2])
    names = [n for n, _ in entries]
    out = {}
    for theme, remap in table.items():
        out[theme] = {}
        for a, b in remap.items():
            if a not in names or b not in names:
                raise ValueError(f"theme {theme}: {a} -> {b}: not a swatch")
            if a != b:
                out[theme][str(names.index(a))] = entries[names.index(b)][1]
    return out


def used_swatches(path):
    """The swatch indices a GLB's vertices point at."""
    return {sw for _, _, _, sw in read_vertices(path)}


def read_vertices(path):
    """[(where, position, normal, swatch)] of every mesh of a GLB. `where` is the node (its name, or ROOT for the model's own node) with its transform, so a part
    that sits in a different place or pose (a door left open) is a different shape. Positions and normals are rounded so two exports compare equal."""
    path = Path(path)
    raw = path.read_bytes()
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

    out = []
    for node in doc.get("nodes", []):
        if "mesh" not in node:
            continue
        name = node.get("name", "")
        where = ("ROOT" if name == path.stem else name,) + tuple(tuple(round(x, 3) for x in node.get(k, ())) for k in ("translation", "rotation", "scale"))
        for prim in doc["meshes"][node["mesh"]]["primitives"]:
            at = prim["attributes"]
            for pos, nor, uv in zip(column(at["POSITION"], 3), column(at["NORMAL"], 3), column(at["TEXCOORD_0"], 2)):
                out.append((where, tuple(round(x, 3) for x in pos), tuple(round(x, 2) for x in nor), int(uv[0] * GRID) + GRID * int(uv[1] * GRID)))
    return out


def derive(path_a, path_b, pal):
    """The swap {swatch of A: hex colour in B} that turns A into B, checked vertex by vertex. Raises ValueError when B is not A in other paint."""
    groups_a, groups_b = {}, {}
    for where, key_pos, key_nor, sw in read_vertices(path_a):
        groups_a.setdefault((where, key_pos, key_nor), []).append(sw)
    for where, key_pos, key_nor, sw in read_vertices(path_b):
        groups_b.setdefault((where, key_pos, key_nor), []).append(sw)
    if groups_a.keys() != groups_b.keys() or any(len(groups_a[k]) != len(groups_b[k]) for k in groups_a):
        raise ValueError("different shape (a mesh, a position or a part\'s pose does not match)")
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


def check(models=None):
    """Compare every declared preset that still has its old GLB with the swap worked out from the GLBs. Returns the number of mismatches."""
    import catalog
    entries = palette_entries()
    pal = [h for _, h in entries]
    models = Path(models) if models else ROOT / "site" / "models"
    bad = checked = 0
    for base, spec in catalog.PAINTS.items():
        _, paints = resolve(spec, entries)
        for p in paints[1:]:
            if not p.get("was") or not (models / f"{p['was']}.glb").exists() or not (models / f"{base}.glb").exists():
                continue
            checked += 1
            try:
                got = derive(models / f"{base}.glb", models / f"{p['was']}.glb", pal)
            except ValueError as e:
                bad += 1
                print(f"{base} {p['name']}: {e}")
                continue
            if got != p["swap"]:
                bad += 1
                print(f"{base} {p['name']}: declared {p['swap']}, GLBs say {got}")
    th = themes(entries)
    for base, styles in catalog.THEMED.items():
        if not (models / f"{base}.glb").exists():
            continue
        used = {str(i) for i in used_swatches(models / f"{base}.glb")}
        for style, was in styles.items():
            if not (models / f"{was}.glb").exists():
                continue
            checked += 1
            want = {k: v for k, v in th[style].items() if k in used}
            try:
                got = derive(models / f"{base}.glb", models / f"{was}.glb", pal)
            except ValueError as e:
                bad += 1
                print(f"{base} {style}: {e}")
                continue
            if got != want:
                bad += 1
                print(f"{base} {style}: the theme gives {want}, the GLBs say {got}")
    print(f"{checked} presets and themes checked against their GLBs, {bad} differ")
    return bad


def main(argv):
    models = ROOT / "site" / "models"
    if argv and argv[0] == "check":
        return 1 if check(argv[1] if len(argv) > 1 else None) else 0
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
