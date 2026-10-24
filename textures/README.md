# Textures

Not models, so not in the asset browser. Copied from the game repo (`khanjal/alien-investigation`, `Assets/Art/Global/`) on 2026-10-23; from here on they are made by `art/scripts/ground.py` (Blender) and `tools/palette_png.py`.

| Folder | What | Made by |
|---|---|---|
| `ground/` | 26 seamless 256 x 256 ground textures (`Tex_*.png`) and 11 transparent decals (`Decal_*.png`), flat hard-edged patches in the same style as the models. `art/data/ground_surfaces.json` says how many metres one tile covers and its footstep surface. | `art/scripts/ground.py`, in Blender |
| `palette/GlobalPalette.png` | The 64 x 64 colour palette every model's UVs point into (16 x 16 swatches of 4 x 4 pixels, slots past the last swatch magenta). | `python tools/palette_png.py` (no Blender); `python tools/palette_png.py --check` says if it is out of date |

The game repo's copy of the palette was stale: it predates the 20 swatches added here (fruit, sports, offices), which were magenta in it. This one is regenerated from `art/scripts/common.py`.

The road, sidewalk and curb pieces `ground.py` also writes are geometry, not textures, and are not built yet. `M_GlobalPalette.mat` is a Unity material, so it stays with the game.

Licence: CC BY 4.0, like the models (see `docs/PUBLISHING.md`).
