---
name: asset-brief
description: Research a real-world object family before modelling or reworking it (balls, fruit, vehicles, tools, jewelry...) and write a brief that lists the real sizes, variants, recognisable details and missing family members. Use this before adding or changing any model in art/scripts, when auditing a category (issue #15), or when a model "looks generic" and you are not sure what is wrong with it.
---

# Brief before build

A model that has the right size and one colour is not done. The sports balls were: nine models, one of each kind, no size classes, and a golf ball with no dimples. Fruit and vehicles got variants because someone asked "what does the real family look like?". Ask that first, for every category, and write the answer down before opening Blender.

The United States is the reference region (issue #346 covers the rest: do not build other regions). Style stays better-made low-poly with the shared palette; reference images are looked at, never traced, copied or committed.

## Steps

1. **Name the family, not the item.** "Basketball" is a family: sizes 7 / 6 / 5 / 3, leather indoor, rubber outdoor, mini. List every member a player of the game could plausibly meet. Include the near neighbours that are missing from the repo (a softball next to a baseball, a pickleball next to a tennis ball).
2. **Per member, record the real facts** (look them up, do not trust memory for numbers; name the governing body or maker in words):
   - **Size**: official dimension(s) in metres, and the range, with the size classes.
   - **Recognisable features**: 3 to 5 things that make it read as that object at game distance (panel layout, seams, laces, dimples, holes, valve, logo band, edge ridge). Say which the low-poly model keeps, fakes with a palette colour, or drops.
   - **Colours and materials** in use today (orange leather vs rubber, optic-yellow felt, white vs coloured balls).
   - **Condition**: new, worn, deflated, rotten, damaged, if the game can show it (`Prop.damage()`, `props_lib.THEME`).
   - **Variants**: size classes, regional or sport-level versions, colour themes. Variants are a colour remap or a size change of one script, never a second copy of the model.
3. **Check what exists**: `out/meta/*.json` (triangles, bbox), `tools/catalog.py` (ids, search tags), the generator in `art/scripts/`. Compare the bbox with step 2, then look at the model from a 3/4 angle with several in one image.
4. **Verdict per model**: fine / needs detail / wrong size / wrong shape / missing variants, plus the list of variants and new members to add. Each gets a one-line reason.
5. **Triangle budget and moving parts**: state the ceiling (the class table in `docs/from-game/asset-list.md` 2.1) and whether any part needs a `hinge` or `slide` (a lid, a drawer), a light or a sound marker.
6. **Write it** to `docs/assets/briefs/<category>.md` (table of members with size, features, variants, verdict) and file one issue per batch of new work with the `area:generators` label. Do not build until the brief exists.
7. **Build in order**: blockout, secondary features, small detail. Keep existing ids and file names (a rework never renames), add new ids for new variants, rebuild with the generator, update `tools/catalog.py` and the manifest, then run the audits.

## Questions that catch what the sports balls missed

- Is there more than one size, and does the sport name them (youth, women's, junior, regulation)?
- Does the surface detail define the object (golf dimples, tennis seam, bowling holes, pickleball holes)? If a feature is the identity, it needs to show at least as colour.
- Are the family members that sit next to it also in the repo (pool balls, ping-pong, lacrosse, beach ball, exercise ball)?
- Is the colour the real one, or a placeholder from the palette (a violet bowling ball is fine as a variant, not as the only one)?
- Does it have a condition the game uses (flat, worn, wet)?

## Output checklist

- [ ] Real dimensions per member, with the source named in words
- [ ] Features kept / faked / dropped
- [ ] Variants (size, colour, condition) and missing family members listed
- [ ] Verdict per existing model
- [ ] Budget and markers stated
- [ ] Brief committed, issues filed, nothing built yet
