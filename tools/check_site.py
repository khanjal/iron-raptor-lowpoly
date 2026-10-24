"""Check that site/ is consistent: the manifest, the models, the thumbnails and the page itself. Plain Python (standard library only), no Blender, no browser.

    python tools/check_site.py            # prints every problem, exits 1 if there is one

What it checks:
  manifest   parses; ids are unique; every field is there with the right type; type is a lowercase category path; tags are lowercase words; size is positive
  files      every entry's glb exists and is a valid GLB (header, JSON chunk), its thumbnail is a 256 x 256 PNG
  against the GLB   the credit line is in asset.copyright (tools/stamp_glb.py); the triangle count equals the manifest's; `rigged` matches the GLB having a skin; the clip names equal the GLB's animation names;
             every `parts` entry names a node that exists in the GLB, and the node sits at the part's pivot (the axis conversion
             Blender -> glTF) plus `rest` along the axis for a slide
  interactions  an entry's `interactions` file exists, is the model's own and agrees with `parts` and `lights`
  materials  only GlobalPaletteGlass is blended (see-through), and anything blended is called that
  variants   name existing ids, and are symmetric
  page       index.html: every script, stylesheet and import-map target exists; every id app.js looks up exists in index.html; app.js imports a file that exists
"""

import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paints  # noqa: E402
import stamp_glb  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TYPE_RE = re.compile(r"^[a-z0-9-]+(/[a-z0-9-]+)+$")
TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIELDS = dict(id=str, name=str, type=str, tags=list, rigged=bool, interactive=bool, triangles=int, size=list, glb=str, thumb=str, parts=dict, clips=list, variants=list)
GLASS_MATERIAL = "GlobalPaletteGlass"   # art/scripts/common.py GLASS_MATERIAL_NAME
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_glb(path):
    """(json document, error) of a binary glTF."""
    raw = Path(path).read_bytes()
    if len(raw) < 20 or raw[:4] != b"glTF":
        return None, "not a GLB (bad magic)"
    version, length = struct.unpack_from("<II", raw, 4)
    if version != 2 or length != len(raw):
        return None, f"bad GLB header (version {version}, length {length} vs {len(raw)} bytes)"
    jlen, jtype = struct.unpack_from("<II", raw, 12)
    if jtype != 0x4E4F534A:
        return None, "first chunk is not JSON"
    try:
        return json.loads(raw[20:20 + jlen].decode("utf-8")), None
    except ValueError as e:
        return None, f"bad JSON chunk: {e}"


def triangles(doc):
    n = 0
    acc = doc.get("accessors", [])
    for mesh in doc.get("meshes", []):
        for prim in mesh["primitives"]:
            if prim.get("mode", 4) != 4:
                continue
            idx = prim.get("indices")
            n += (acc[idx]["count"] if idx is not None else acc[prim["attributes"]["POSITION"]]["count"]) // 3
    return n


def png_size(path):
    raw = Path(path).read_bytes()[:24]
    if raw[:8] != PNG_MAGIC:
        return None
    return struct.unpack(">II", raw[16:24])


def check_paints(a, err):
    """paintable: [{part, swatch, hex}] (the parts a person can colour); paints: [{name, hex, swap {swatch index: hex}, was?}], the first the model as exported
    (empty swap), the others each swapping only swatches that are paintable parts; names and chip colours all different.
    `paints` may be missing: the model then offers palette.common for its first part."""
    hexre = re.compile(r"^#[0-9A-F]{6}$")
    parts, ps = a.get("paintable"), a.get("paints")
    if not (isinstance(parts, list) and parts):
        err("paints needs paintable: at least one part")
        return
    if "paints" not in a:
        ps = None
    elif not (isinstance(ps, list) and len(ps) >= 2):
        err("paints: the model's own paint and at least one more")
        return
    for i, p in enumerate(parts):
        if not (isinstance(p, dict) and isinstance(p.get("part"), str) and p["part"].strip() and isinstance(p.get("swatch"), int) and 0 <= p["swatch"] < 256 and hexre.match(str(p.get("hex")))):
            err(f"paintable[{i}] should be {{part, swatch, hex '#RRGGBB'}}")
            return
    if len({p["swatch"] for p in parts}) != len(parts) or len({p["part"] for p in parts}) != len(parts):
        err("paintable: parts and swatches should all differ")
    swatches = {str(p["swatch"]) for p in parts}
    for i, p in enumerate(ps or []):
        if not (isinstance(p, dict) and isinstance(p.get("name"), str) and p["name"].strip() and hexre.match(str(p.get("hex"))) and isinstance(p.get("swap"), dict)):
            err(f"paints[{i}] should be {{name, hex '#RRGGBB', swap}}")
            return
        if bool(p["swap"]) == (i == 0):
            err(f"paints[{i}]: only the first paint (the model as exported) has an empty swap")
        for k, v in p["swap"].items():
            if k not in swatches or not hexre.match(str(v)):
                err(f"paints[{i}]: swap entry {k!r}: {v!r} should be a paintable swatch index and '#RRGGBB'")
    if ps and len({p["name"] for p in ps}) != len(ps):
        err("paints: names should all differ")


def check_themes(a, err):
    """themes: [{name, was?}], names of themes the manifest defines at the top level (check_manifest looks them up)."""
    ts = a["themes"]
    if not (isinstance(ts, list) and ts and all(isinstance(t, dict) and isinstance(t.get("name"), str) and t["name"].strip() for t in ts)):
        err("themes should be a list of {name, was?}")
    elif len({t["name"] for t in ts}) != len(ts):
        err("themes: names should all differ")


def check_entry(a, site, errors):
    where = a.get("id", "?")
    err = lambda m: errors.append(f"{where}: {m}")
    for k, t in FIELDS.items():
        if k not in a:
            err(f"missing field {k}")
        elif not isinstance(a[k], t) or (t is int and isinstance(a[k], bool)):
            err(f"field {k} should be {t.__name__}")
    if any(k not in a for k in FIELDS):
        return
    if not a["name"].strip():
        err("empty name")
    if not TYPE_RE.match(a["type"]):
        err(f"type {a['type']!r} is not a lowercase category path like vehicles/road/bus")
    if not a["tags"]:
        err("no tags")
    for t in a["tags"]:
        if not isinstance(t, str) or not TAG_RE.match(t):
            err(f"tag {t!r} is not a lowercase word")
    if len(set(a["tags"])) != len(a["tags"]):
        err("duplicate tags")
    if len(a["size"]) != 3 or not all(isinstance(v, (int, float)) and v > 0 for v in a["size"]):
        err(f"size {a['size']} should be three positive numbers")
    if a["triangles"] <= 0:
        err("triangles should be positive")
    if a["interactive"] != bool(a["parts"]):
        err("interactive does not match parts")
    for role, p in a["parts"].items():
        if p.get("kind") not in ("hinge", "slide", "spin"):
            err(f"part {role}: kind {p.get('kind')!r}")
        if not (isinstance(p.get("axis"), list) and len(p["axis"]) == 3 and abs(sum(v * v for v in p["axis"]) - 1) < 1e-6):
            err(f"part {role}: axis should be a unit vector")
        if not (isinstance(p.get("pivot"), list) and len(p["pivot"]) == 3):
            err(f"part {role}: pivot should be three numbers")
        if not p.get("limit"):
            err(f"part {role}: limit is zero or missing")
        if "rest" not in p:
            err(f"part {role}: rest missing")

    if "paints" in a or "paintable" in a:
        check_paints(a, err)
    if "themes" in a:
        check_themes(a, err)
    if "interactions" in a:
        check_interactions(a, site, err)
    glb, thumb = site / a["glb"], site / a["thumb"]
    if not glb.is_file():
        err(f"{a['glb']} does not exist")
    else:
        doc, e = read_glb(glb)
        if e:
            err(f"{a['glb']}: {e}")
        else:
            check_against_glb(a, doc, err)
            if a.get("paintable") and isinstance(a["paintable"], list):
                used = paints.used_swatches(glb)
                for p in a["paintable"]:
                    if isinstance(p, dict) and p.get("swatch") not in used:
                        err(f"paintable {p.get('part')}: swatch {p.get('swatch')} is not used by the GLB")
    if not thumb.is_file():
        err(f"{a['thumb']} does not exist")
    elif png_size(thumb) != (256, 256):
        err(f"{a['thumb']} is not a 256 x 256 PNG (got {png_size(thumb)})")


def check_interactions(a, site, err):
    """The model's own interactions file: it exists, parses, is this model's, and lists the moving parts the manifest lists."""
    rel = a["interactions"]
    if not isinstance(rel, str) or not (site / rel).is_file():
        err(f"{rel} does not exist")
        return
    try:
        doc = json.loads((site / rel).read_text(encoding="utf-8"))
    except ValueError as e:
        err(f"{rel}: bad JSON ({e})")
        return
    if doc.get("id") != a["id"]:
        err(f"{rel}: id is {doc.get('id')!r}")
    if sorted((doc.get("parts") or {})) != sorted(a["parts"]):
        err(f"{rel}: parts {sorted(doc.get('parts') or {})} differ from the manifest's {sorted(a['parts'])}")
    lights = sum(1 for e in (doc.get("emitters") or {}).values() if e.get("kind") == "light" and e.get("working", True))
    if lights != a.get("lights", 0):
        err(f"{rel} has {lights} working lights, the manifest says {a.get('lights', 0)}")


def check_against_glb(a, doc, err):
    if doc.get("asset", {}).get("copyright") != stamp_glb.COPYRIGHT:
        err("the GLB has no credit line in asset.copyright (run tools/stamp_glb.py)")
    for m in doc.get("materials", []):                                  # only the glass twin of the palette is see-through
        blended = m.get("alphaMode") == "BLEND"
        if blended != (m.get("name") == GLASS_MATERIAL):
            err(f"material {m.get('name')!r} is {'blended' if blended else 'opaque'}; only {GLASS_MATERIAL} should be blended")
    t = triangles(doc)
    if t != a["triangles"]:
        err(f"manifest says {a['triangles']} triangles, the GLB has {t}")
    if bool(doc.get("skins")) != a["rigged"]:
        err(f"rigged is {a['rigged']} but the GLB has {len(doc.get('skins', []))} skins")
    names = [x.get("name") for x in doc.get("animations", [])]
    if sorted(names) != sorted(a["clips"]):
        err(f"clips {a['clips']} differ from the GLB's animations {names}")
    nodes = {n.get("name"): n for n in doc.get("nodes", [])}
    for role, p in a["parts"].items():
        n = nodes.get(role)
        if n is None:
            err(f"part {role} has no node of that name in the GLB")
            continue
        pos = list(n.get("translation", [0, 0, 0]))
        if p.get("kind") == "slide":
            pos = [pos[i] - p["axis"][i] * p.get("rest", 0) for i in range(3)]   # the node is already `rest` along its axis
        if any(abs(pos[i] - p["pivot"][i]) > 1e-3 for i in range(3)):
            err(f"part {role}: pivot {p['pivot']} is not where the GLB node is ({pos})")


def check_page(site, errors):
    html_path = site / "index.html"
    if not html_path.is_file():
        errors.append("index.html does not exist")
        return
    html = html_path.read_text(encoding="utf-8")
    refs = re.findall(r'(?:src|href)="([^"#?:]+)"', html)
    importmap = re.search(r'<script type="importmap">(.*?)</script>', html, re.S)
    if importmap:
        refs += [v for v in json.loads(importmap.group(1))["imports"].values()]
    for r in refs:
        if not (site / r).exists():
            errors.append(f"index.html refers to {r}, which does not exist")
    ids = set(re.findall(r'id="([^"]+)"', html))
    for js in ("app.js", "viewer.js"):
        path = site / js
        if not path.is_file():
            errors.append(f"{js} does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.findall(r"\$\('([^']+)'\)", text) + re.findall(r"getElementById\('([^']+)'\)", text):
            if js == "app.js" and m not in ids:
                errors.append(f"app.js looks up #{m}, which index.html does not have")
        for imp in re.findall(r"from '(\.[^']+)'", text):
            if not (site / imp).exists():
                errors.append(f"{js} imports {imp}, which does not exist")


def check(site=None):
    """All the problems found in a site folder (a list of strings; empty when it is fine)."""
    site = Path(site or ROOT / "site")
    errors = []
    try:
        doc = json.loads((site / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"manifest.json: {e}"]
    assets = doc.get("assets")
    if not isinstance(assets, list) or not assets:
        return ["manifest.json has no assets"]
    ids = [a.get("id") for a in assets]
    for i in {x for x in ids if ids.count(x) > 1}:
        errors.append(f"duplicate id {i}")
    byid = {a.get("id"): a for a in assets}
    seen_alias = {}
    for a in assets:
        al = a.get("aliases", [])
        if not (isinstance(al, list) and all(isinstance(x, str) and x for x in al)):
            errors.append(f"{a.get('id')}: aliases should be a list of ids")
            continue
        for x in al:
            if x in byid:
                errors.append(f"{a.get('id')}: alias {x} is the id of another model")
            if seen_alias.setdefault(x, a.get("id")) != a.get("id"):
                errors.append(f"alias {x} is claimed by {seen_alias[x]} and {a.get('id')}")
    for a in assets:
        check_entry(a, site, errors)
        for v in a.get("variants", []):
            if v not in byid:
                errors.append(f"{a.get('id')}: variant {v} is not in the manifest")
            elif a.get("id") not in byid[v].get("variants", []):
                errors.append(f"{a.get('id')}: variant {v} does not list it back")
    themes = doc.get("themes", {})
    hexre = re.compile(r"^#[0-9A-F]{6}$")
    if not isinstance(themes, dict) or not all(isinstance(t, dict) and t and all(k.isdigit() and int(k) < 256 and hexre.match(str(v)) for k, v in t.items()) for t in themes.values()):
        errors.append("themes should be {name: {swatch index: '#RRGGBB'}}")
        themes = {}
    for a in assets:
        for t in a.get("themes", []) if isinstance(a.get("themes"), list) else []:
            if isinstance(t, dict) and t.get("name") not in themes:
                errors.append(f"{a.get('id')}: theme {t.get('name')!r} is not defined in the manifest's themes")
    for g in doc.get("palette", {}).get("glow", []):
        if not re.match(r"^#[0-9A-F]{6}$", g.get("hex", "")):
            errors.append(f"palette glow {g.get('name')}: bad hex")
    common = doc.get("palette", {}).get("common", [])
    if not (isinstance(common, list) and all(isinstance(c, dict) and isinstance(c.get("name"), str) and re.match(r"^#[0-9A-F]{6}$", str(c.get("hex"))) for c in common)):
        errors.append("palette.common should be a list of {name, hex '#RRGGBB'}")
    elif any(a.get("paintable") and "paints" not in a for a in assets) and not common:
        errors.append("models offer common colours but palette.common is empty")
    check_page(site, errors)
    return errors


if __name__ == "__main__":
    problems = check(sys.argv[1] if len(sys.argv) > 1 else None)
    for p in problems:
        print("FAIL", p)
    print(f"{len(problems)} problem(s)" if problems else "site ok")
    sys.exit(1 if problems else 0)
