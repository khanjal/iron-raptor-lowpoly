---
name: blender-assets
description: How the models in khanjal/iron-raptor-lowpoly are made and checked (Python scripts in art/ driven through the Blender MCP, exported to out/ as FBX and GLB, shown by the site/ browser): the conventions, the sign rule that tilts parts the wrong way, the brief before a build, the checks that catch floating or hollow-looking parts, gaps and clipping between parts, animation clips (loops that must close, limbs through bodies, foot slide), moving parts and markers, and what has to be re-run after a change (GLB, thumbnail, manifest). Use this whenever creating or changing a model, variant or palette colour under art/, when a model looks wrong in the browser or an engine (flipped, floating, upside down, hollow, z-fighting, gaps), when a clip hitches or bobs, or when re-exporting models.
---

# Making and fixing models (art/)

Models are code: Python in `art/scripts/` run inside Blender through the Blender MCP, exported under the output folder (`out/` by default, `LOWPOLY_OUT` or `common.configure(out=...)`), then shown by `site/`. Read `art/README.md` for the file list and the README for the pipeline; this skill is what is *not* obvious from them, mostly learned from mistakes in the game repo this was extracted from.

Adapted from the `blender-assets` skill in the game repo (Unity, Git LFS and `.meta` parts removed; GLB and the site added).

## Running scripts

- `runpy.run_path(path, run_name="__main__")`: always pass `run_name`; most scripts build only under `if __name__ == "__main__"`, so without it they import and do nothing. Options go in `init_globals` (e.g. `{"SPECIES_LIST": ["goat"]}`, `{"GROUPS": ["props"]}` for `build_all.py`).
- GLB is only written when asked: `common.configure(formats="fbx,glb")`. `only={...}` limits the exporters to some names; `prefix=` keeps a build from replacing same-named collections in a Blender file other work shares.
- A long run (buildings 50 s, cars 70 s, home styles 90 s, interactive 2 min) makes the MCP call fail with "No data received" while Blender carries on and finishes. Do not re-run: look at the scene (`get_scene_info`; the last object built is active) or `git status`. Run the heavy groups one per call.
- After changing `common.py` (palette) or `props_lib.py`, rebuild everything that uses it: `build_all.py` re-exports the FBX files (it does not cover `insects.py`, `office.py` or `sports.py`), and the site's GLBs come only from `tools/build_site_assets.py`, so run every `BUILD` group of `tools/catalog.py` (one per call), then `make_manifest.py`, the thumbnails and `check_site.py`. The scripts reload their imports.
- Do not run two renders or build a second scene in the shared Blender (`temp_override` closed the connection twice). Thumbnails are rendered by the site's own viewer, not Blender.

## Brief before build

Style: **better-made low-poly** with the shared palette and the Blender generators; not realism, and no scanned, library (Poly Pizza, Sketchfab, Poly Haven) or `generate_3d` models (wrong style, no rigs or markers, and the licence is the project's own; see LICENSES.md). Third-party material needs an entry in `CREDITS.md` first.

For every new or reworked model, write down before any code (use the `asset-brief` skill; the brief goes in `docs/assets/briefs/<category>.md`, and the PR description links it):

1. **Which real object, which variant**, and why (a wedge or a wheel of cheese; a Type I or Type II ambulance). **An existing id keeps its variant, name and file name.**
2. **Real size** in metres.
3. **3-5 features that make it recognisable.**
4. **Colours** as palette names (`common.PALETTE`), never RGB.
5. **Pivot and use**: where the origin goes decides how people place it.
6. **Moving parts and markers** (`hinge` / `slide` only), and their `interactions.json` entries. Keep what already works (rigs, clips, parts, ids, file names).
7. **Parts table**: each part's size, centre and what it attaches to (see "Parts, fit and clipping" below).

Reference pictures: describe what you learned in words; never trace, copy or commit an image or a model.

**Build order:** (1) blockout of the main shapes at the right proportions, and `look` at it before adding anything; (2) secondary features (bevels, trim, handles, feet, seams, wear; not bevels on the 3 m grid kit pieces, which must butt without a groove, nor on the faceted animals and people); hollow only what anyone can see into or put something in; (3) small details with the triangle budget left. Check from four angles and at 10 m, then against the brief: size, front faces -Y, pivot, palette-only colours, triangles, markers.

## Conventions that bite

- A model faces **-Y** in Blender (arrives facing **+Z** in a GLB and in Unity), origin on the floor at the centre of its base, 1 unit = 1 m. Wall-mounted pieces have the origin at the mount's centre.
- One shared palette (`common.PALETTE`, **append-only**: indices are baked into the UVs of every exported model). Colour names, not RGB. Variants are a colour remap (`props_lib.THEME`) plus own shapes where needed, never a second copy of a model.
- **The sign rule** (a rotation `rot=(rx, ry, rz)` is degrees, Euler XYZ, right-handed). Rotation about X by +θ moves a point at offset `dy` along Y by `dz = dy·sinθ`: **positive X rotation lowers the -Y end of a part that extends towards -Y** and raises the +Y end. Rotation about Y by +θ lowers the +X end. Roof halves, ramps, handles, hoods and porch roofs were built backwards six times. Never trust the sign; look at it. For a beam between two points use `props_lib.rod(p, colour, a, b, w)`.
- `Prop.box(taper=)` scales the **top** face: `taper < 1` narrows the top, `taper > 1` widens it. A bucket wider at the rim needs `taper > 1`.
- Hollow things must be hollow if anyone can see inside or put something in: floor + walls (+ roof) with openings (`wall_run(..., fill=False)`), not a solid box with a dark patch. A part that moves (door, lid, drawer) is a separate object with its origin on its pivot: `with p.part(role, pivot=..., kind="hinge"|"slide", axis=..., limit=...)`.
- Things that must be see-through (a fence, a grille) are thin bars, not a panel; a palette swatch named `clear_*` goes on the blended glass material.
- `Prop.damage()` puts grime only on flat, uncovered upward faces and re-seats the prop on the floor only when it tilts it.

## Check it before you export

1. Look: lay the objects out and `look` at them from a 3/4 angle (several models per image). Slopes, hinges, handles, hollowness, which way things face.
2. `art/scripts/audit.py` lists models with parts that touch nothing (floating handles, seats above frames). `audit_props.py`, `audit_animals.py` and `audit_bodies.py` cover props, animals and people (`audit_layout.py` needs a layout dump from the game's Unity project and does not run here). Fix the real ones; loose items (logs on the ground, books) are expected.
3. Re-import one exported file into Blender to check hierarchy and pivots survive (the FBX importer adds a 90 degree X rotation to the root; that is normal).
4. Look at it in the site's viewer (below). Things fine in Blender can be wrong in glTF (axes, pivots of moving parts).

## Parts, fit and clipping (every model)

Write the parts down before any code, as a short table in the brief or the script's docstring: **part, size (w x d x h, m), centre or origin, what it sits on or attaches to**. Sizes come from the real object (the brief) and positions from the parts they touch, not from numbers typed twice:

- Derive a position from its neighbour (`top = base_z + base_h`, `x = wall_x - t / 2`), so changing one size moves everything that depends on it. A literal that has to equal another literal is a gap or a clip waiting for the next edit.
- **No gaps.** Parts that should touch must touch or overlap slightly (a leg into the seat, a handle into the door, a neck into the head, a roof into the walls). A visible sliver of background between two parts is a bug even when each part is right.
- **No visible clipping.** Faces that are coplanar (flush boxes, a decal at the same depth, a lid exactly on a rim) z-fight; a part that pokes out through a surface shows as a spike or a hole. Overlap that is hidden inside another part is fine and is how things are joined; overlap that shows is not. Sink a joint by its own thickness, offset a decal by a millimetre, and give every thin plate its own depth.
- Check it with numbers first (`audit.py` (its default run is only a rough bounding-box check for floating parts with a 2 cm margin; with `AUDIT_CLIP=True` it also finds clipping, coplanar faces and parts that miss each other by more than 2 mm); `audit_props.py`, `audit_animals.py` and `audit_bodies.py` each cover only their own scripts (props, four-legged animals, people and aliens), so anything else (tools, office, sports, vehicles, buildings, food, insects) has only `audit.py`; or a bounding-box check of the parts against each other: touching, inside, intersecting), then with `look`: four angles, a close view of every joint and a view from below and behind. What is small in the full view is what shows at the joints.
- Moving parts get the same check at **both ends of their travel** (a door open as well as shut, a lid up, a drawer out): they clear the body, do not pass through a neighbour, and stay attached to their hinge.

## Animation (every clip)

The same rules hold in motion, and a clip has its own ways to go wrong:

- **The loop closes.** The last key equals the first, in the GLB, not only in the Blender action (`tests/test_glb_clips.py` checks the rotation and translation channels of every clip in `site/models/` and fails otherwise; a clip that is deliberately not a loop, such as a door that stays open, needs an exemption in the test). Key every clip on a rig with no other clip live (`stash_clip`, called by `tools/build_site_assets.py` after each clip is keyed, leaves its track muted, and the exporter writes muted tracks; unmute one to play it in Blender): a live track overrides the pose the next clip's keys are read from (issue #95).
- Reset every pose property (location, rotation **and scale**) between frames: setting a bone's matrix leaves a little scale behind that adds up over a loop (Sit's pelvis ended 4 mm from where it began). `gp_clips.reset` does this; `insect_anim.reset` does not yet.
- **No clipping at the extremes.** Pose the rig at each key and at the extreme of each swing (a stride at full reach, an arm fully raised, a wing at the top and the bottom of its stroke) and look: limbs do not pass through the body or each other, a foot does not sink into the floor or hover, a wing does not go through the thorax. Look at three or more frames of the loop, not only the first.
- **Joints stay joined.** At every frame the parts that touch at rest still touch (no gap opening at the shoulder, hip, neck or wing root). A rotated child bone keeps its distance from its parent's pivot, so measure the distance between the two pieces' surfaces (each vertex to the other piece's surface, as `audit_bodies.py` does for the arms) at the extreme frames, not between the pivots.
- **Ground and travel.** Planted feet do not slide (`quadruped_walk.py` prints the drift for the four-legged animals in Blender's console when the clip is built; read it; the people and insects need a measurement of their own), the body keeps its height above the ground, and the clip's speed matches the model's size.
- **Motion is the right size.** A bob or sway is measured against the model, not the world: millimetres on a small insect look huge once the viewer frames it (issue #96). A body that a real animal holds still stays still (a bee's, a fly's; a butterfly's does move a little).
- Check the exported GLB, not only the Blender scene: open it in the site's viewer and watch the loop wrap several times. Say which clips you watched.

## Markers and `interactions.json`

`Prop.part()` (moving parts), `Prop.slot()` (where items go), `Prop.emit()` / `Prop.trait()` (lights, sounds, switches; `emitters.py` has a table per prop) export marker empties (`Slot_`, `Light_`, `Sound_`, `Switch_`) and entries in `art/data/interactions.json` (and the per-model interactions files). The marker empties are not in the GLBs. Add a prop's markers to `emitters.SPECS` (position as a fraction of its bounding box), not inside every style's function.

## After the build: the site's files

A new or changed model is not finished until the browser has it. In this order:

1. Add or edit the entry in `tools/catalog.py` (three-level `category/group/kind` type, tags, variants; the rules are tested).
2. Build it: in Blender, `runpy.run_path(r"<repo>/tools/build_site_assets.py", init_globals={"GROUPS": ["<group>"]}, run_name="__main__")`, one group per call (group names are the keys of `BUILD` in `tools/catalog.py`; `ONLY=[...]` limits an animals or people group). It runs the art script, writes the GLB into `site/models/` and the facts file into `out/meta/`, and removes what it built. Writing GLBs with `common.configure(formats="fbx,glb")` alone goes to `out/glb/`, which the site does not read. New builds carry the credit line (`GLB_COPYRIGHT` in `common.py`); older files: `python tools/stamp_glb.py`.
3. `python tools/make_manifest.py`, then thumbnails: `python tools/thumb_server.py` and open `http://localhost:8766/tools/thumbs.html` (`?only=ID,ID` for some).
3b. Name the colour-picker parts in `art/data/part_names.json` (`{id: {swatch name: area}}`, and `"$main": "Case"` for a model with a single colour); a one-colour model left as "Main" fails `tests/test_paints.py`. `python tools/make_manifest.py --part-names` applies it to the committed manifest.
4. `python tools/check_site.py` and `python -m unittest discover -s tests -t .`.
5. Run the site (`cd site && python -m http.server 8000`) and open the model: size, which way it faces, moving parts turn about the right pivots, clips play. Say what you looked at.

Keep the counts in README and NOTES.md in step with the manifest (the count appears in the badge, the intro and "The asset browser"); docs whose counts did not match the code were a repeated review finding.

## Review lessons

Reviews of this pipeline found, repeatedly: grime and decals floating or buried; slot/pivot hierarchies that do not survive the axis conversion (hang empties off the body, not a part); sockets measured from stale bounds (call `view_layer.update()`); `.001` name suffixes from leftover objects; stale exports after a shared change. After a change to a shared helper, rebuild everything and check a few outputs by eye.
