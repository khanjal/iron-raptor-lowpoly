"""Write site/manifest.json from the facts the Blender build left in out/meta/, the descriptions in tools/catalog.py and art/data/interactions.json.

    python tools/make_manifest.py

Plain Python, no Blender. Needs the models: run tools/build_site_assets.py in Blender first (see README.md).

Axes. The models are built in Blender's space (x right, y back, z up, the front faces -y). The GLB exporter turns that into glTF's (x, z, -y), so everything
the viewer uses is converted here, once:
  size   [width, height, depth] in metres (glTF x, y, z)
  parts  pivot = the part's origin as the GLB node holds it; axis = a unit vector in glTF space (Blender x stays x, Blender z becomes y, Blender y becomes -z).
         The mapping is a proper rotation, so a hinge turns by `limit` degrees about `axis` in the same direction as in Blender, and a slide moves
         `limit` metres along `axis`. `rest` is how far open the part already is in the exported pose (0 = shut).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import catalog
import paints as paints_tool

AXES = {"x": [1, 0, 0], "y": [0, 0, -1], "z": [0, 1, 0]}


def to_gltf(v):
    return [round(v[0], 4), round(v[2], 4), round(-v[1], 4)]


def glow_swatches():
    """The palette's glowing swatches (names starting glow_), read from common.py without importing Blender: the viewer lights these up."""
    text = (ROOT / "art" / "scripts" / "common.py").read_text(encoding="utf-8")
    body = text[text.index("PALETTE = ["):text.index("GRID = 16")]
    out = []
    for i, m in enumerate(re.finditer(r'\("([a-z0-9_]+)",\s*"([0-9A-Fa-f]{6})"\)', body)):
        if m.group(1).startswith("glow_"):
            out.append(dict(name=m.group(1), index=i, hex="#" + m.group(2).upper()))
    return out


def convert_part(p):
    """One part of art/data/interactions.json (Blender space) as the manifest stores it (glTF space)."""
    return dict(kind=p["kind"], axis=AXES[p["axis"]], pivot=to_gltf(p["pivot"]), limit=p["limit"], rest=p["rest"])


def size_of(meta):
    """[width, height, depth] in metres from the Blender bounding box (x, z, y)."""
    lo, hi = meta["bbox_min"], meta["bbox_max"]
    return [round(hi[0] - lo[0], 3), round(hi[2] - lo[2], 3), round(hi[1] - lo[1], 3)]


SIDECAR_ABOUT = ("What can be done with this model: moving parts, slots for loose items, emitters (lights, sounds, switches) and traits. "
                 "Same fields as art/data/interactions.json, in Blender space (X right, Y back, Z up, front is -Y), metres; the GLB itself is glTF space (x, z, -y). "
                 "Written by tools/make_manifest.py; see art/scripts/emitters.py for the fields.")


def sidecar_name(aid):
    return f"{aid}.interactions.json"


def write_sidecars(assets, inter, models):
    """Write models/<id>.interactions.json for every model that has an entry in interactions.json, and remove the ones no model has any more.
    Returns the set of ids that got one."""
    have = set()
    for aid in assets:
        entry = inter.get(aid)
        if not entry:
            continue
        doc = dict(about=SIDECAR_ABOUT, id=aid, space="blender", **entry)
        (models / sidecar_name(aid)).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        have.add(aid)
    for old in models.glob("*.interactions.json"):
        if old.name[:-len(".interactions.json")] not in have:
            old.unlink()
    return have


def build_entry(aid, a, meta, inter, groups):
    """The manifest entry of one model: a = its catalog row, meta = out/meta/<id>.json, inter = its entry in interactions.json, groups = group -> ids."""
    parts = {}
    for role, p in ((inter or {}).get("parts") or {}).items():
        if role not in meta["part_nodes"]:
            raise ValueError(f"{aid}: part {role} is in interactions.json but not in the GLB")
        parts[role] = convert_part(p)
    for role in meta["part_nodes"]:
        if role not in parts:
            raise ValueError(f"{aid}: node {role} is a child mesh but interactions.json has no part for it")
    entry = dict(
        id=aid, name=a["name"], type=a["type"], tags=sorted(set(a["tags"])),
        rigged=meta["rigged"], interactive=bool(parts), triangles=meta["triangles"], size=size_of(meta),
        glb=f"models/{aid}.glb", thumb=f"thumbs/{aid}.png",
        parts=parts, clips=list(meta["clips"]),
        variants=[v for v in groups.get(a["group"], []) if v != aid] if a["group"] else [],
    )
    if inter:
        entry["interactions"] = f"models/{sidecar_name(aid)}"   # the model's own file: parts, slots, emitters, traits
        lights = sum(1 for e in (inter.get("emitters") or {}).values() if e.get("kind") == "light" and e.get("working", True))
        if lights:
            entry["lights"] = lights
    return entry


def variant_groups(assets):
    groups = {}
    for aid, a in assets.items():
        if a["group"]:
            groups.setdefault(a["group"], []).append(aid)
    return groups


def apply_paints(assets, paints, pal):
    """Put the colour variants of art/data/paints.json on their base model: entry["paints"] = [{name, hex (for the chip), swap {swatch index: hex}}], the base's own
    paint first with an empty swap. The models those paints used to be have no entry of their own, so they come out of every `variants` list."""
    ids = {a["id"] for a in assets}
    for a in assets:
        a["variants"] = [v for v in a["variants"] if v in ids]
        spec = paints.get(a["id"])
        if not spec:
            continue
        swatches = sorted({k for sw in spec["paints"].values() for k in sw}, key=int)
        a["paints"] = [dict(name=spec["base"], hex=pal[int(swatches[0])], swap={})]
        for name, sw in spec["paints"].items():
            a["paints"].append(dict(name=name, hex=sw[swatches[0]] if swatches[0] in sw else pal[int(swatches[0])], swap=sw))


def main():
    meta_dir = ROOT / "out" / "meta"
    inter = json.loads((ROOT / "art" / "data" / "interactions.json").read_text(encoding="utf-8"))["props"]
    groups = variant_groups(catalog.ASSETS)
    assets = []
    for aid, a in catalog.ASSETS.items():
        if not (ROOT / "site" / "models" / f"{aid}.glb").exists():
            raise SystemExit(f"missing site/models/{aid}.glb")
        meta = json.loads((meta_dir / f"{aid}.json").read_text(encoding="utf-8"))
        try:
            assets.append(build_entry(aid, a, meta, inter.get(aid), groups))
        except ValueError as e:
            raise SystemExit(str(e))
    assets.sort(key=lambda x: (x["type"], x["id"]))
    apply_paints(assets, json.loads((ROOT / "art" / "data" / "paints.json").read_text(encoding="utf-8")), paints_tool.palette())
    write_sidecars([x["id"] for x in assets], inter, ROOT / "site" / "models")
    doc = dict(version=1, generated_from="tools/make_manifest.py", palette=dict(glow=glow_swatches()), assets=assets)
    (ROOT / "site" / "manifest.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    counts = {}
    for x in assets:
        counts[x["type"].split("/")[0]] = counts.get(x["type"].split("/")[0], 0) + 1
    print("wrote site/manifest.json:", len(assets), "assets", counts)


if __name__ == "__main__":
    main()
