# Hand-off: what needs Blender

Written 2026-10-24 for a Claude Code session on a computer that has Blender 5.2.3 and the Blender MCP connected. The cloud session that did the rest had no Blender, so everything below is unbuilt and unseen.

Work on branch `claude/alien-investigation-assets-jy5lbt` (pull it first). Read `NOTES.md` (the last four sections), `README.md` ("Rebuilding the assets") and `art/README.md`. Do not touch `khanjal/alien-investigation`: this repo makes the models now.

## What changed without being built

1. **Fridges** (`art/scripts/interactive.py`, `fridge_retro`, `fridge_modern`, chosen by `VARIANTS`): the owner wants three designs. Classic = two doors, freezer on top (unchanged). Retro = one tall rounded door with one long handle. Modern = French doors over a pull-out freezer drawer. Written blind. The `GI_Fridge_Modern_01` and `GI_Fridge_Retro_01` GLBs in `site/` are the old colour-only ones.
2. **Vehicles and ships** (`vehicles.py`, `cars.py`, `ships.py`, new `other_vehicles.py`): synced from game PRs #358, #359 and the open #357, merged over this repo's edits (GLB export, `clear_*` glass). `other_vehicles` is a `build_all` group but has no entry in `tools/catalog.py` `BUILD` yet.
3. **Colour paints** (`tools/catalog.PAINTS`, `tools/paints.py`): 10 models stand in for the colour variants that used to be built separately (sedan, tractor, apple, bananas, grapes, butterfly, window wall, baseball bat). The declared colours were verified against the old GLBs, but the sedan and tractor scripts have since been replaced by #358.

## Do these, in order

1. `python -m unittest discover -s tests -t .` and `python tools/check_site.py` should pass before you start.
2. **Fridges.** In Blender: `runpy.run_path(r"<repo>\tools\build_site_assets.py", init_globals={"GROUPS": ["int_fridge"]}, run_name="__main__")`. Look at all four fridges (Classic, Modern, Retro, Damaged) in the viewport or in the site. Check: Retro reads as one rounded door with a long handle (only the door edges are round: if the body looks too boxy, rework it); Modern has two doors that open and a freezer drawer that slides out; nothing floats (`art/scripts/audit_props.py`, the `blender-assets` rules in the game repo's skill if you have it); moving parts have the right axes and limits in `site/models/GI_Fridge_*.interactions.json`; the slots sit on the shelves. Fix `interactive.py` until they look right.
3. **Vehicles and ships** (`cars_sedan`, `cars_taxi`, `cars_van`, `cars_police`, `cars_ambulance`, `cars_moto`, `cars_tractor`, `cars_pickup`, `ships`): rebuild each group, one per call. Compare triangle counts and look for floating parts (`audit.py`; #358 says 1,500 to 1,850 tris per car, #356 560 to 2,730 per ship).
4. **Re-check the paints on the new shapes.** The sedan and tractor presets assume the body swatch is used for the body only. Temporarily add `GV_Sedan_Red_01` and `GV_Tractor_Red_01` to the `ids` of `cars_sedan` and `cars_tractor` in `tools/catalog.py`, rebuild those two groups, and run `python tools/paints.py check`. If it prints a difference, fix the preset in `catalog.PAINTS` (or the script, if two parts share a swatch). Then take the two extra ids out again and delete their GLBs.
5. `python tools/make_manifest.py` (needs `out/meta` from the builds), `python tools/stamp_glb.py` if it says a GLB lacks the credit, thumbnails (`python tools/thumb_server.py`, then `http://localhost:8766/tools/thumbs.html`), `python tools/check_site.py`, the unit tests.
6. Commit and push to the branch. Do not open a pull request unless the owner asks.

## Then, if there is time

- Add `other_vehicles` (semi, bus, fire truck...) to `BUILD` and `ASSETS` in `tools/catalog.py`, with `PAINTS` for the plain colour sets.
- The game repo has about 760 distinct models (1,270 files with variants); this repo ships about 120. `docs/from-game/art/prop-catalogue.md` and `asset-list.md` list the rest. Before building a colour or style variant as its own model, read `NOTES.md` ("Colour variants are paints") and `docs/style-audit.md`: a variant that is only a recolour should be a paint or a theme, and one that differs in design (like the fridges) stays a model.
- Issue #48 (https://github.com/khanjal/lowpoly-assets/issues/48) has the plan for Modern/Retro styles as themes. Ask the owner before folding a style: the old generator only recoloured some pieces that the owner wants to look different.

## Facts that are easy to get wrong

- Palette indices are baked into every GLB's UVs and the palette is append-only. `textures/palette/GlobalPalette.png` is made by `python tools/palette_png.py` (a test checks it is current).
- A paint is a swap `{palette swatch index: '#RRGGBB'}` on a copy of the palette image; `tools/paints.py A B` says whether two GLBs are a pure recolour (it compares every mesh and pose, not only the main mesh).
- `--catalog-only` (`python tools/make_manifest.py --catalog-only`) refreshes names, tags, paints and themes without Blender; `--part-names` applies only `art/data/part_names.json` (area names of the colour-picker parts) to the committed manifest. A normal run needs `out/meta`.
- Say plainly in the commit message and `NOTES.md` what you built and looked at, and what you did not.

## Prompt to paste

> Read `docs/HANDOFF-blender.md` in this repo (branch `claude/alien-investigation-assets-jy5lbt`) and do what it says, starting with the fridges. Blender is connected. Report what you built and looked at, what looked wrong, and what you changed.
