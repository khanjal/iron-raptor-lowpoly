# Notes: turning the art pipeline into its own project

Tracked in the game repo: khanjal/alien-investigation issue #355 (the plan and the asset browser) and #344 (the quality pass).

## Done
- This folder, with `art/` copied from the game repo's `main` (commit 9a3d59ce).
- Pushed to a **private** GitHub repo, https://github.com/khanjal/lowpoly-assets (2026-10-23), under the working name; renaming it later is cheap.

## First slice of the asset browser (branch `viewer-slice-1`)
Done: an output-folder setting and GLB export in `art/scripts/common.py`; 63 models (13 vehicles, 6 animals, 5 people, 11 furniture, 5 appliances, 5 decor, 5 food, 7 farm, 4 building kit, 2 trees) built through the Blender MCP; thumbnails; `site/manifest.json`; the static site in `site/`; a Pages workflow (not enabled). How to run and rebuild it: README.md.

Not done in the slice:
- Not all assets (the catalog in `tools/catalog.py` lists 63 of roughly 1,000); no Blender CI (the GLBs, thumbnails and manifest are committed for now); the generic / game-specific split; the licence; renaming the repo.
- Animals and people play their clips, but nothing else in the browser is data-driven from the art scripts yet: the category path and tags are written by hand in `tools/catalog.py`.
- Clip lists: dogs have Idle, Walk, Trot, Run; other animals Idle, Walk; people Idle, Walk, Run, Sit; the hen has no clips (the art scripts have none for birds). Carry / CarryOne and the turkey's Display clip are not exported.
- Lights, sounds, switches and item slots (`interactions.json` emitters and slots) are not shown.
- The thumbnails are rendered by the site's own viewer in a browser (`tools/thumbs.html`), not by Blender: a Blender render would have needed a second scene in the shared Blender, and two earlier tries at that (a new scene with `temp_override`) closed Blender's connection.
- Cars, ships and the food scripts here are the versions from the game repo's `main`; the open PRs #357-#359 (lofted vehicle and ship bodies) are not in.
- Not checked: a real phone, Safari / Firefox, touch dragging, iOS WebGL limits, a keyboard-only pass over the viewer.

### GitHub Pages and a private repository
Pages is not available for a private repository on the Free plan. The docs (docs.github.com, "Creating a GitHub Pages site"): "If the account that owns the repository uses GitHub Free or GitHub Free for organizations, the repository must be public." ("GitHub's plans": GitHub Pro and Team list Pages for private repositories, and "To publish a GitHub Pages site privately, you need to have an organization account" on GitHub Enterprise Cloud.) So: test locally now; publish when the repo is made public (which needs the licence and third-party decisions below) or the plan is upgraded; then enable Settings > Pages > Source: GitHub Actions and merge `.github/workflows/pages.yml`.

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
