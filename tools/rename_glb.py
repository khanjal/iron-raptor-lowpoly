"""Give a model another id (standard library only, no Blender): the generator keeps building `GV_Tractor_Green_01`, the browser calls it `GV_Tractor_01`.

    python tools/rename_glb.py                       # every catalog.SITE_IDS entry whose old file is still there
    python tools/rename_glb.py OLD NEW               # one model

Moves site/models/OLD.glb to NEW.glb (the node and mesh named OLD are renamed inside it too, so the GLB's own names match its file), OLD.interactions.json
with its `id`, site/thumbs/OLD.png and out/meta/OLD.json (its `id`). tools/build_site_assets.py calls rename_group after a build, so a rebuild lands under the new id.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = re.compile(r"\w+", re.ASCII)
sys.path.insert(0, str(ROOT / "tools"))
import stamp_glb  # noqa: E402


def rename_bytes(raw, old, new):
    """The GLB bytes with the nodes and meshes called `old` called `new` (the same bytes when there are none)."""
    def mutate(doc):
        hit = False
        for key in ("nodes", "meshes"):
            for x in doc.get(key, []):
                if x.get("name") == old:
                    x["name"] = new
                    hit = True
        return hit
    return stamp_glb.rewrite_json(raw, mutate)


def _move_json(src, dst):
    doc = json.loads(src.read_text(encoding="utf-8"))
    doc["id"] = dst.name.split(".")[0]
    dst.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    src.unlink()


def _model_id(x):
    if not MODEL_ID.fullmatch(x):
        raise ValueError(f"not a model id: {x!r}")
    return x


def rename_model(old, new, root=ROOT):
    """Move one model's files to its new id; returns the names of the files moved (nothing for a model that is not there under its old id)."""
    old = _model_id(old)
    new = _model_id(new)
    root = Path(root)
    moved = []
    glb = root / "site" / "models" / f"{old}.glb"
    if glb.is_file():
        (root / "site" / "models" / f"{new}.glb").write_bytes(rename_bytes(glb.read_bytes(), old, new))
        glb.unlink()
        moved.append(glb.name)
    for src, dst in ((root / "site" / "models" / f"{old}.interactions.json", root / "site" / "models" / f"{new}.interactions.json"),
                     (root / "out" / "meta" / f"{old}.json", root / "out" / "meta" / f"{new}.json")):
        if src.is_file():
            _move_json(src, dst)
            moved.append(src.name)
    thumb = root / "site" / "thumbs" / f"{old}.png"
    if thumb.is_file():
        thumb.replace(root / "site" / "thumbs" / f"{new}.png")
        moved.append(thumb.name)
    return moved


def rename_group(ids, site_ids, root=ROOT):
    """Rename the models of `ids` (generator names) that site_ids ({generator name: browser id}) gives another id; returns the browser ids of all of them."""
    out = []
    for gen in ids:
        new = site_ids.get(gen, gen)
        if new != gen:
            rename_model(gen, new, root)
        out.append(new)
    return out


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(rename_model(sys.argv[1], sys.argv[2]))
    else:
        import catalog
        for gen, new in catalog.SITE_IDS.items():
            m = rename_model(gen, new)
            if m:
                print(gen, "->", new, m)
