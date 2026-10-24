"""Write site/manifest.json from the facts the Blender build left in out/meta/, the descriptions in tools/catalog.py and art/data/interactions.json.

    python tools/make_manifest.py
    python tools/make_manifest.py --catalog-only    # no Blender: refresh names, tags, folded colour variants (paints) in the existing manifest

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


def apply_paints(assets, paint_specs, entries, models=None):
    """Put the colour variants of catalog.PAINTS on their base model: entry["paintable"] (its parts) and entry["paints"] (the presets, the model's own paint first),
    and make the preset names searchable tags. The models those presets used to be have no entry of their own, so they come out of every `variants` list.
    A model with no entry in PAINTS gets `paintable` alone, worked out from its GLB in `models` (default site/models): the viewer offers the common colours
    (palette.common) for its first part and a colour box for each part. A GLB that is not there leaves the model without."""
    ids = {a["id"] for a in assets}
    models = Path(models or ROOT / "site" / "models")
    for a in assets:
        a["variants"] = [v for v in a["variants"] if v in ids]
        spec = paint_specs.get(a["id"])
        if not spec:
            glb = models / f"{a['id']}.glb"
            parts = paints_tool.auto_parts(glb, entries) if glb.is_file() else []
            if parts:
                a["paintable"] = parts
            continue
        a["paintable"], a["paints"] = paints_tool.resolve(spec, entries)
        a["tags"] = sorted(set(a["tags"]) | {re.sub(r"[^a-z0-9]+", "-", p["name"].lower()).strip("-") for p in a["paints"]})


def apply_aliases(assets):
    """entry["aliases"] = the ids a model had before catalog.SITE_IDS gave it its browser id, so old links, search and the game's lookups still find it."""
    for a in assets:
        if a["id"] in catalog.ALIASES:
            a["aliases"] = [catalog.ALIASES[a["id"]]]


def apply_themes(doc, assets, entries):
    """doc["themes"] = {theme: {swatch index: hex}} once, and entry["themes"] = [{name, was?}] on the models catalog.THEMED lists (their style variants are not models of
    their own). The style names become tags so a search for "retro" still finds the model."""
    wanted = {t for styles in catalog.THEMED.values() for t in styles}
    doc["themes"] = {t: swap for t, swap in paints_tool.themes(entries).items() if t in wanted}
    for a in assets:
        styles = catalog.THEMED.get(a["id"])
        if not styles:
            continue
        a["themes"] = [dict(name=t, was=was) for t, was in styles.items()]
        a["tags"] = sorted(set(a["tags"]) | {t.lower() for t in styles})
        a["variants"] = [v for v in a["variants"] if v not in styles.values()]


def catalog_only():
    """Bring site/manifest.json in line with tools/catalog.py (names, tags, which models exist, variants, paints) without the Blender facts: for a change of
    description or of what is folded into a paint. Facts about a model (size, triangles, parts, clips) are kept as they are."""
    path = ROOT / "site" / "manifest.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    groups = variant_groups(catalog.ASSETS)
    assets = []
    for a in doc["assets"]:
        if a["id"] in catalog.SITE_IDS:                      # an entry still under the generator's name: move it to the browser's id
            new = catalog.SITE_IDS[a["id"]]
            a.update(id=new, glb=f"models/{new}.glb", thumb=f"thumbs/{new}.png")
            if "interactions" in a:
                a["interactions"] = f"models/{sidecar_name(new)}"
        a.pop("aliases", None)
        row = catalog.ASSETS.get(a["id"])
        if row is None:
            continue
        a.pop("paintable", None)
        a.pop("paints", None)
        a.pop("themes", None)
        a.update(name=row["name"], type=row["type"], tags=sorted(set(row["tags"])), variants=[v for v in groups.get(row["group"], []) if v != a["id"]] if row["group"] else [])
        assets.append(a)
    assets.sort(key=lambda x: (x["type"], x["id"]))
    entries = paints_tool.palette_entries()
    apply_paints(assets, catalog.PAINTS, entries)
    apply_aliases(assets)
    apply_themes(doc, assets, entries)
    doc.setdefault("palette", {})["common"] = paints_tool.common_colours(entries)
    doc["assets"] = assets
    path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print("updated site/manifest.json from the catalog:", len(assets), "assets")


def main():
    if "--catalog-only" in sys.argv:
        return catalog_only()
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
    apply_paints(assets, catalog.PAINTS, paints_tool.palette_entries())
    apply_aliases(assets)
    write_sidecars([x["id"] for x in assets], inter, ROOT / "site" / "models")
    doc = dict(version=1, generated_from="tools/make_manifest.py", palette=dict(glow=glow_swatches(), common=paints_tool.common_colours(paints_tool.palette_entries())), assets=assets)
    apply_themes(doc, assets, paints_tool.palette_entries())
    (ROOT / "site" / "manifest.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    counts = {}
    for x in assets:
        counts[x["type"].split("/")[0]] = counts.get(x["type"].split("/")[0], 0) + 1
    print("wrote site/manifest.json:", len(assets), "assets", counts)


if __name__ == "__main__":
    main()
