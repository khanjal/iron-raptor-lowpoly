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


def main():
    meta_dir = ROOT / "out" / "meta"
    inter = json.loads((ROOT / "art" / "data" / "interactions.json").read_text(encoding="utf-8"))["props"]
    groups = {}
    for aid, a in catalog.ASSETS.items():
        if a["group"]:
            groups.setdefault(a["group"], []).append(aid)
    assets = []
    for aid, a in catalog.ASSETS.items():
        m = json.loads((meta_dir / f"{aid}.json").read_text(encoding="utf-8"))
        glb = ROOT / "site" / "models" / f"{aid}.glb"
        if not glb.exists():
            raise SystemExit(f"missing {glb}")
        lo, hi = m["bbox_min"], m["bbox_max"]
        size = [round(hi[0] - lo[0], 3), round(hi[2] - lo[2], 3), round(hi[1] - lo[1], 3)]
        parts = {}
        for role, p in (inter.get(aid, {}).get("parts") or {}).items():
            if role not in m["part_nodes"]:
                raise SystemExit(f"{aid}: part {role} is in interactions.json but not in the GLB")
            parts[role] = dict(kind=p["kind"], axis=AXES[p["axis"]], pivot=to_gltf(p["pivot"]), limit=p["limit"], rest=p["rest"])
        for role in m["part_nodes"]:
            if role not in parts:
                raise SystemExit(f"{aid}: node {role} is a child mesh but interactions.json has no part for it")
        tags = sorted(set(a["tags"]))
        assets.append(dict(
            id=aid, name=a["name"], type=a["type"], tags=tags,
            rigged=m["rigged"], interactive=bool(parts), triangles=m["triangles"], size=size,
            glb=f"models/{aid}.glb", thumb=f"thumbs/{aid}.png",
            parts=parts, clips=m["clips"],
            variants=[v for v in groups.get(a["group"], []) if v != aid] if a["group"] else [],
        ))
    assets.sort(key=lambda x: (x["type"], x["id"]))
    doc = dict(version=1, generated_from="tools/make_manifest.py", palette=dict(glow=glow_swatches()), assets=assets)
    (ROOT / "site" / "manifest.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    counts = {}
    for x in assets:
        counts[x["type"].split("/")[0]] = counts.get(x["type"].split("/")[0], 0) + 1
    print("wrote site/manifest.json:", len(assets), "assets", counts)


if __name__ == "__main__":
    main()
