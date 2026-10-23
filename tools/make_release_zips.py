"""Zip the models for a GitHub release (standard library only): one zip of every GLB and one per top-level category.

    python tools/make_release_zips.py            # writes dist/lowpoly-assets-glb-all.zip, dist/lowpoly-assets-glb-<category>.zip ...
    python tools/make_release_zips.py OUTDIR

Each zip holds `<id>.glb` files at its top level, plus CREDIT.txt (how to credit under CC BY 4.0) and LICENSE-MODELS. Which models go into which zip
comes from site/manifest.json (the first part of `type`). Only GLB: the FBX files are not committed, so they cannot be zipped without Blender.
"""

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDIT = """These models are licensed under Creative Commons Attribution 4.0 (CC BY 4.0): free to use in any project, commercial or not, with credit.
Full text: LICENSE-MODELS (in this zip), https://creativecommons.org/licenses/by/4.0/

A line like this is enough, in a credits screen, README, store page or video description:

  3D models by khanjal, from lowpoly-assets (https://github.com/khanjal/lowpoly-assets), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

If you changed a model, say so. More: https://github.com/khanjal/lowpoly-assets/blob/main/LICENSES.md
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
        p = out_dir / f"lowpoly-assets-glb-{key}.zip"
        write_zip(p, members, site, root)
        paths.append(p)
    return paths


if __name__ == "__main__":
    for p in build(sys.argv[1] if len(sys.argv) > 1 else ROOT / "dist"):
        print(f"{p}  {p.stat().st_size / 1e6:.1f} MB")
