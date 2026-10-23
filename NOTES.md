# Notes: turning the art pipeline into its own project

Tracked in the game repo: khanjal/alien-investigation issue #355 (the plan and the asset browser) and #344 (the quality pass).

## Done
- This folder, with `art/` copied from the game repo's `main` (commit 9a3d59ce). Nothing is on GitHub yet.

## Not copied yet (open PRs in the game repo, merge first or copy by hand)
- #358: road vehicles rebuilt (`vehicles.py`, `cars.py`).
- #359: the nine flying ships (`ships.py`).
- the other-vehicles batch (#357: `other_vehicles.py`, semi, bus, fire truck...).

## To decide before a GitHub repo exists
- Repo name and owner account (the folder name here is a placeholder).
- Licence for the code (MIT?) and the models (CC0 or CC-BY?). Permanent once public.
- Private first, flipped to public when the licence and the split are done? (A private repo uses limited Actions minutes; a public one is free.)
- Whether anything under `art/` came from third-party assets (audit first; the UAL skeleton data in `art/data/ual_skeleton.json` is CC0 and credited).

## Known work in the split
- Every script writes to `Assets/Art/...` (Unity's layout) through `common.REPO` and `export_fbx`: needs an output folder setting.
- Separate generic library (`common.py`, builders, rigs, clip generators, `audit.py`, `build_all.py`, palette) from this game's content (aliens, the named cast, farm props, `emitters.py` and `interactions.json` data for its abilities).
- Models are published as release assets or on the Pages site, not Git LFS.
- Blender-only CI: build every generator, run the audits, report triangles.
- The GitHub Pages asset browser (search, categories, 3D viewer, open moving parts): see #355.
