"""Zip the models for a GitHub release (standard library only): one zip of every GLB and one per top-level category.

    python tools/make_release_zips.py            # writes dist/iron-raptor-lowpoly-glb-all.zip, dist/iron-raptor-lowpoly-glb-<category>.zip ...
    python tools/make_release_zips.py OUTDIR     # OUTDIR must be inside the project

Each zip holds `<id>.glb` files at its top level (and `<id>.interactions.json` next to the ones that have moving parts, lights, sounds or switches), plus CREDIT.txt (how to credit under CC BY 4.0) and LICENSE-MODELS. Which models go into which zip
comes from site/manifest.json (the first part of `type`). Only GLB: the FBX files are not committed, so they cannot be zipped without Blender.
"""

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import stamp_glb  # noqa: E402
CREDIT = """These models are licensed under Creative Commons Attribution 4.0 (CC BY 4.0): free to use in any project, commercial or not, with credit.
Full text: LICENSE-MODELS (in this zip), https://creativecommons.org/licenses/by/4.0/

A line like this is enough, in a credits screen, README, store page or video description:

  3D models by khanjal, from Iron Raptor Lowpoly (https://github.com/khanjal/iron-raptor-lowpoly), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

If you changed a model, say so. More: https://github.com/khanjal/iron-raptor-lowpoly/blob/main/LICENSES.md
"""


def groups(assets):
    """{zip name suffix: [asset, ...]}: 'all' plus one entry per top-level category."""
    out = {"all": list(assets)}
    for a in assets:
        out.setdefault(a["type"].split("/")[0], []).append(a)
    return out


def write_zip(path, assets, site, root):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for a in sorted(assets, key=lambda a: a["id"]):
            z.write(site / a["glb"], f"{a['id']}.glb")
            if a.get("interactions"):
                z.write(site / a["interactions"], Path(a["interactions"]).name)
        z.writestr("CREDIT.txt", CREDIT)
        z.write(root / "LICENSE-MODELS", "LICENSE-MODELS")


def build(out_dir, site=None, root=None):
    """Write the zips; returns their paths."""
    root = Path(root or ROOT)
    site = Path(site or root / "site")
    assets = json.loads((site / "manifest.json").read_text(encoding="utf-8"))["assets"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for key, members in sorted(groups(assets).items()):
        p = out_dir / f"iron-raptor-lowpoly-glb-{key}.zip"
        write_zip(p, members, site, root)
        paths.append(p)
    return paths


if __name__ == "__main__":
    try:
        target = stamp_glb.project_path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    for p in build(target):
        print(f"{p}  {p.stat().st_size / 1e6:.1f} MB")
