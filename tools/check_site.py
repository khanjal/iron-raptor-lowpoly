"""Check that site/ is consistent: the manifest, the models, the thumbnails and the page itself. Plain Python (standard library only), no Blender, no browser.

    python tools/check_site.py            # prints every problem, exits 1 if there is one

What it checks:
  manifest   parses; ids are unique; every field is there with the right type; type is a lowercase category path; tags are lowercase words; size is positive
  files      every entry's glb exists and is a valid GLB (header, JSON chunk), its thumbnail is a 256 x 256 PNG
  against the GLB   the triangle count equals the manifest's; `rigged` matches the GLB having a skin; the clip names equal the GLB's animation names;
             every `parts` entry names a node that exists in the GLB, and the node sits at the part's pivot (the axis conversion
             Blender -> glTF) plus `rest` along the axis for a slide
  variants   name existing ids, and are symmetric
  page       index.html: every script, stylesheet and import-map target exists; every id app.js looks up exists in index.html; app.js imports a file that exists
"""

import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPE_RE = re.compile(r"^[a-z0-9-]+(/[a-z0-9-]+)+$")
TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIELDS = dict(id=str, name=str, type=str, tags=list, rigged=bool, interactive=bool, triangles=int, size=list, glb=str, thumb=str, parts=dict, clips=list, variants=list)
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
        if p.get("kind") not in ("hinge", "slide"):
            err(f"part {role}: kind {p.get('kind')!r}")
        if not (isinstance(p.get("axis"), list) and len(p["axis"]) == 3 and abs(sum(v * v for v in p["axis"]) - 1) < 1e-6):
            err(f"part {role}: axis should be a unit vector")
        if not (isinstance(p.get("pivot"), list) and len(p["pivot"]) == 3):
            err(f"part {role}: pivot should be three numbers")
        if not p.get("limit"):
            err(f"part {role}: limit is zero or missing")
        if "rest" not in p:
            err(f"part {role}: rest missing")

    glb, thumb = site / a["glb"], site / a["thumb"]
    if not glb.is_file():
        err(f"{a['glb']} does not exist")
    else:
        doc, e = read_glb(glb)
        if e:
            err(f"{a['glb']}: {e}")
        else:
            check_against_glb(a, doc, err)
    if not thumb.is_file():
        err(f"{a['thumb']} does not exist")
    elif png_size(thumb) != (256, 256):
        err(f"{a['thumb']} is not a 256 x 256 PNG (got {png_size(thumb)})")


def check_against_glb(a, doc, err):
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
    for a in assets:
        check_entry(a, site, errors)
        for v in a.get("variants", []):
            if v not in byid:
                errors.append(f"{a.get('id')}: variant {v} is not in the manifest")
            elif a.get("id") not in byid[v].get("variants", []):
                errors.append(f"{a.get('id')}: variant {v} does not list it back")
    for g in doc.get("palette", {}).get("glow", []):
        if not re.match(r"^#[0-9A-F]{6}$", g.get("hex", "")):
            errors.append(f"palette glow {g.get('name')}: bad hex")
    check_page(site, errors)
    return errors


if __name__ == "__main__":
    problems = check(sys.argv[1] if len(sys.argv) > 1 else None)
    for p in problems:
        print("FAIL", p)
    print(f"{len(problems)} problem(s)" if problems else "site ok")
    sys.exit(1 if problems else 0)
