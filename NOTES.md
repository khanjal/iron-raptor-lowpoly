# Notes: turning the art pipeline into its own project

Tracked in the game repo: issue #355 (the plan and the asset browser) and #344 (the quality pass).

## Done
- This folder, with `art/` copied from the game repo's `main` (commit 9a3d59ce).
- Pushed to a **private** GitHub repo, https://github.com/khanjal/lowpoly-assets (2026-10-23), under the working name; renaming it later is cheap.

## First slice of the asset browser (branch `viewer-slice-1`)
Done: an output-folder setting and GLB export in `art/scripts/common.py`; 63 models (13 vehicles, 6 animals, 5 people, 11 furniture, 5 appliances, 5 decor, 5 food, 7 farm, 4 building kit, 2 trees) built through the Blender MCP; thumbnails; `site/manifest.json`; the static site in `site/`; a Pages workflow (not enabled). How to run and rebuild it: README.md.

Not done in the slice:
- Not all assets (the catalog in `tools/catalog.py` lists 63 of the many hundreds the scripts can make); no Blender CI (the GLBs, thumbnails and manifest are committed for now); the generic / game-specific split; the licence; renaming the repo.
- Animals and people play their clips, but nothing else in the browser is data-driven from the art scripts yet: the category path and tags are written by hand in `tools/catalog.py`.
- Clip lists: dogs have Idle, Walk, Trot, Run; other animals Idle, Walk; people Idle, Walk, Run, Sit; the hen has no clips (the art scripts have none for birds). Carry / CarryOne and the turkey's Display clip are not exported.
- Lights, sounds, switches and item slots (`interactions.json` emitters and slots) are not shown.
- The thumbnails are rendered by the site's own viewer in a browser (`tools/thumbs.html`), not by Blender: a Blender render would have needed a second scene in the shared Blender, and two earlier tries at that (a new scene with `temp_override`) closed Blender's connection.
- Cars, ships and the food scripts here are the versions from the game repo's `main`; the open PRs #357-#359 (lofted vehicle and ship bodies) are not in.
- Not checked: a real phone, Safari / Firefox, touch dragging, iOS WebGL limits, a keyboard-only pass over the viewer.

Tests and CI (added after the first push): `tests/` (39 unit tests: the Blender-to-glTF axis conversion, the manifest builder, catalog rules, the site checks including a pivot check against the real GLBs), `tools/check_site.py`, `.github/workflows/tests.yml` (manual only; GitHub refused to start its one trial run because of the account's billing state, so it has never run on GitHub) and `pages.yml` (manual only). `docs/ci.md` has the proposals for a browser smoke test and a Blender job (`bpy` 5.2.3 is on PyPI, Python 3.13 only, a 403 MB Linux wheel; not tried). The README now has a section on using the models in Unity, Godot and Unreal, with what is documented and what is untested.

### GitHub Pages and a private repository
Pages is not available for a private repository on the Free plan. The docs (docs.github.com, "Creating a GitHub Pages site"): "If the account that owns the repository uses GitHub Free or GitHub Free for organizations, the repository must be public." ("GitHub's plans": GitHub Pro and Team list Pages for private repositories, and "To publish a GitHub Pages site privately, you need to have an organization account" on GitHub Enterprise Cloud.) So: test locally now; publish when the repo is made public (which needs the licence and third-party decisions below) or the plan is upgraded; then enable Settings > Pages > Source: GitHub Actions and merge `.github/workflows/pages.yml`.

## From now on this repo makes the models (2026-10-23)
The game repo no longer makes its own art; it consumes what is built here. The planned assets, the open issues and PRs about models, and what the game expects to stay stable are in [`docs/from-game/README.md`](docs/from-game/README.md) (with copies of the asset list, the prop catalogue and the art notes). Syncing the `art/` changes merged in the game repo since 9a3d59ce is the first job there.

## Synced from the game repo (2026-10-23, later)
Pulled in game PRs #358 (road vehicles: `vehicles.py`, `cars.py`), #359 (flying ships: `ships.py`) and the open #357 (`other_vehicles.py`, `cars.py`), merged over our local edits (GLB export, `clear_*` glass). `other_vehicles` is a new `build_all.py` group. None of it is built or exported yet.

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

## Licence and publishing (2026-10-23)
- Chosen on the `licence` branch: MIT for the code, CC BY 4.0 for the models and data, with a credits file. The copyright line uses the GitHub handle; confirm it.
- The plan for replacing the commit email and publishing safely (publish from a NEW repository, because pull-request refs keep old commits) is in `docs/PUBLISHING.md`. The repository stays private until then.

## Public since 2026-10-23
- The repository was made public (owner's decision) on 2026-10-23, with the commit email still in the history (`docs/PUBLISHING.md` describes the safer route that was not taken). GitHub Pages is set to deploy from Actions; the Tests and Pages workflows now run automatically.

## Downloads and credit (2026-10-23, branch `licence`)
- Release zips: `tools/make_release_zips.py` (one zip of every GLB, one per category, each with `CREDIT.txt` and `LICENSE-MODELS`) and `.github/workflows/release.yml` (on a `v*` tag, or by hand; runs the tests first, uses only the `gh` CLI). GLB only: FBX is not committed. **Not run on GitHub yet**: push a tag to try it.
- Credit travels with the files: `asset.copyright` in every GLB (`tools/stamp_glb.py` for the existing 131, `GLB_COPYRIGHT` in `common.py` for new Blender builds; `check_site.py` and a test keep the two in step), a note under the viewer's Download button and in the page footer.
- The game's name is gone from the docs (README, NOTES, `art/README.md`, `docs/from-game/`); "the game" / "the game repo" instead. Issue numbers (#355, #364...) are the game repo's. Unity menu paths read `Tools > <game name> > ...`. The repo's earlier commits still have the name.

## More families (2026-10-23, branch `licence`)
Added on request: produce variety, insects, sports gear, office gear. 68 new models, so the browser now has 131.
- **Produce** (`contents.py`): the apple is one dimpled shape in `cloth_red`, `apple_green` and `apple_yellow` (the old FD_Apple_01 changed shape too); a banana bunch (+ Rotten), lemon, pear, purple and green grapes, strawberry.
- **Insects** (`insects.py`, new): 12 models, real size in millimetres, resting poses, no rig. The viewer's camera floor and ground shadow were lowered (`site/viewer.js`: 0.05 to 0.004 m, 0.1 to 0.01 m) so a 1 cm model fills the frame.
- **Sports** (`sports.py`, new, `GS_`): 27 models, a new top-level category `sports`. The tennis net is 12.8 m wide and the soccer goal 3.7 m, real size.
- **Office** (`office.py`, new, `GO_`): 20 models, including a cubicle kit on a 1.5 m module and 8 with moving parts (drawers, trays, lids, doors, a flap). `art/data/interactions.json` grew by 281 lines.
- **Palette**: 17 swatches appended (indices 108 to 124): apple, banana, lemon, pear, grape, berry, basketball orange, tennis yellow, leather, wing blue, beetle green, office grey and dark, laminate, water blue. Existing models are unchanged (append-only).
- Checks: `tools/check_site.py` and the 40 unit tests pass. The new models have been looked at as thumbnails and the copier's parts opened in the viewer; the prop audit (`audit_props.py`, which covers only the older scripts) has not been run on them, and none was checked in Unity, Godot or Unreal.
- Rough spots: the baseball glove is blocky, the baseball and tennis ball seams are chunky strands on a faceted ball, the golf ball has no dimples, the dragonfly's abdomen floats (no perch). The game repo's `GD_Football_01` (a tapered box in `decor.py`) is not in the browser; `GS_Football_01` is the proper one.
- Not done: the Rotten twins other than the banana bunch are built by `contents.py` but not in the browser; no `build_all.py` entries for the three new scripts (it is the game's list; add them when that file is split).

## Colour variants are paints, not models (2026-10-23)
A model whose only difference from another is colour is built and shipped once; its other colours are `paints` in the manifest (`tools/catalog.PAINTS`, explained in `tools/paints.py`). A paint is a swap `{palette swatch index: '#RRGGBB'}` applied to a copy of the palette image, so a person can also pick any colour for any paintable part (a purple apple). The game applies the same swap at load: copy the palette texture, fill the swatch cells (cell = 4 px in the 64 px image, index % 16 and index / 16 from the top), assign it to that instance's material.
- Done for 11 models in the slice (sedan and tractor colours, apple, bananas, grapes, butterfly, desk, window wall, bat); the old ids still open in the viewer (`was`).
- The generators are unchanged: they still build every colour, and `catalog.BUILD` keeps only the base in `ids`. The folded GLBs are deleted, so `tools/paints.py check` only compares a declared swap with its GLBs while both exist (build the pair in Blender first).
- Does not fold: shape changes (Damaged cars, Retro/Modern sets with their own design) and decal liveries. The desk (steel to wood) was folded at first and put back: it is not a pure recolour (one steel swatch becomes steel and wood), which only the full comparison of every mesh shows.
- Styles are themes, not paints (issue #48): `catalog.THEMED` lists the models whose Modern / Retro are only `home_styles.THEMES` (none yet); the manifest carries the themes once and the viewer's Style row applies one to the palette (`tools/paints.py check` compares a theme with the GLBs it replaces). `docs/style-audit.md` has the counts. Damaged is never a theme: it drops parts and tilts, and the Damaged fridge and wardrobe have doors hanging open.
- The three fridges are three designs, not colours (asked for by the owner): Classic = two doors, freezer on top; Retro = one tall rounded door with one long handle; Modern = French doors over a pull-out freezer drawer (`fridge_retro`, `fridge_modern` in `interactive.py`, picked per style by `VARIANTS`). **Written without Blender, not built or looked at**: build `int_fridge` and check the shapes, then replace `GI_Fridge_Modern_01` and `GI_Fridge_Retro_01` in `site/` (the GLBs there are the old colour-only ones and show the classic shape).
- The next real build runs `make_manifest.py` with the same `apply_paints`; `--catalog-only` refreshed the manifest here without Blender.
