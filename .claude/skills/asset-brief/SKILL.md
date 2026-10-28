---
name: asset-brief
description: Research a real-world object family before modelling or reworking it (balls, fruit, vehicles, tools, jewelry...) and write a brief that lists the real sizes, variants, recognisable details and missing family members. Use this before adding or changing any model in art/scripts, when auditing a category (issue #15), or when a model "looks generic" and you are not sure what is wrong with it.
---

# Brief before build

A model that has the right size and one colour is not done. The sports balls were: nine models, one of each kind, no size classes, and a golf ball with no dimples. Fruit and vehicles got variants because someone asked "what does the real family look like?". Ask that first, for every category, and write the answer down before opening Blender.

The United States is the reference region (issue #346 covers the rest: do not build other regions). Style stays better-made low-poly with the shared palette; reference images are looked at, never traced, copied or committed (a side-view silhouette may be kept in the git-ignored `out/reference/` for `tools/silhouette.py`: `blender-assets`).

## Steps

1. **Name the family, not the item.** "Basketball" is a family: sizes 7 / 6 / 5 / 3, leather indoor, rubber outdoor, mini. List every member a player of the game could plausibly meet. Include the near neighbours that are missing from the repo (a softball next to a baseball, a pickleball next to a tennis ball).
2. **Per member, record the real facts** (look them up, do not trust memory for numbers; name the governing body or maker in words):
   - **Size**: official dimension(s) in metres, and the range, with the size classes.
   - **Recognisable features**: 3 to 5 things that make it read as that object at game distance (panel layout, seams, laces, dimples, holes, valve, logo band, edge ridge). Say which the low-poly model keeps, fakes with a palette colour, or drops.
   - **Colours and materials** in use today (orange leather vs rubber, optic-yellow felt, white vs coloured balls).
   - **Condition**: new, worn, deflated, rotten, damaged, if the game can show it (`Prop.damage()`, `props_lib.THEME`).
   - **Variants**: size classes, regional or sport-level versions, colour themes. Variants are a colour remap or a size change of one script, never a second copy of the model.
3. **Look at other low-poly work for direction.** Real sizes say what the object is; good low-poly models of it say how to make it read. The cats and dogs of issue #125 had the right sizes and still read as thin and generic next to them.
   - **Where to look**: if `docs/assets/style-comparison.md` exists, read its section for the category first. Then look at a few published low-poly models or renders of the family on the web (search for "low poly <object>"), viewed in the browser and never saved. References the owner hands over (images, an STL or another model file) may sit outside the repository or in `out/` (git ignores it) for the comparison below, and an owner's model may be imported into Blender to be measured and rendered beside ours; none of them is ever committed. Not through the Blender MCP's `search_assets` / `import_asset`: they download a model. If you cannot browse, or find only paid previews, say so in the brief and do not invent what you saw.
   - **What to write down**, in words: which features they push past real proportions (a cat's head and ears, a car's wheels), how colour sits in blocks rather than patterns (a pale chest and feet, not stripes round the body), the silhouette, chunky ends (paws, feet, handles), the face, how the thumbnail is framed.
   - **How far ours stylises**: take what several of them do (the habits of the style), never one model's particular choices; that would be copying its design. Stylising past the real numbers is allowed when the brief says how much and why. For an animal held by `art/scripts/animal_proportions.py`, a row in `RANGES` or `HEN` is widened in the brief's table (`docs/assets/briefs/animals.md`, "Proportion table") and in the script in the same change, and `tests/test_animal_proportions.py` checks the two agree; a `SHAPE` limit has no row in the brief, so write the new limit and the reason in the brief by hand. Run the unit tests. A limit is never widened only to make a model pass.
   - **The reference card**: with the owner, pick three to five references that show the look wanted, and measure them where you can (a model file outright; pictures by their proportions) into a short table in units of the head's or the body's width: for an animal the head's width, height and length, the ears' height above the crown and the width of their base, how far the nose stands out from the face, the eyes' size, height and spacing, the neck's width, the facet size (how many triangles across the head). Write how ours compares, row by row, and which rows it will match. The owner agrees the card before the model is built: it is what the comparison sheets are judged against.
   - **Direction, not material**: nothing is downloaded, saved, traced, copied or committed. Looking needs no `CREDITS.md` entry. The brief may name the sites or well-known collections looked at, as it names the sources of real sizes, but not link or describe individual people's models.
   - **Record it** in the brief (this step's section is the record, with the reference card; the references themselves are named, not included). If `docs/assets/style-comparison.md` exists, add a short note to the category's section that points at the brief; do not create the file.
4. **Check what exists**: `out/meta/*.json` (triangles, bbox), `tools/catalog.py` (ids, search tags), the generator in `art/scripts/`. Compare the bbox with step 2, then look at the model from a 3/4 angle with several in one image, next to what step 3 found.
5. **Verdict per model**: fine / needs detail / wrong size / wrong shape / reads generic (the answer to "does it read at a glance next to them?" below is no) / missing variants, plus the list of variants and new members to add. Each gets a one-line reason.
6. **Triangle budget and moving parts**: state the ceiling (the class table in `docs/from-game/asset-list.md` 2.1) and whether any part needs a `hinge` or `slide` (a lid, a drawer), a light or a sound marker.
7. **Write it** to `docs/assets/briefs/<category>.md` (table of members with size, features, variants, verdict) and file one issue per batch of new work with the `area:generators` label. Do not build until the brief exists.
8. **Build in order**: blockout, secondary features, small detail. Keep existing ids and file names (a rework never renames), add new ids for new variants, rebuild with the generator, update `tools/catalog.py` and the manifest, then run the audits.

## Questions that catch what the sports balls missed

- Is there more than one size, and does the sport name them (youth, women's, junior, regulation)?
- Does the surface detail define the object (golf dimples, tennis seam, bowling holes, pickleball holes)? If a feature is the identity, it needs to show at least as colour.
- Are the family members that sit next to it also in the repo (pool balls, ping-pong, lacrosse, beach ball, exercise ball)?
- Is the colour the real one, or a placeholder from the palette (a violet bowling ball is fine as a variant, not as the only one)?
- Does it have a condition the game uses (flat, worn, wet)?
- Next to good low-poly models of the same thing, does ours read at a glance, or only once you know what it is?

## Output checklist

- [ ] Real dimensions per member, with the source named in words
- [ ] Features kept / faked / dropped
- [ ] Low-poly examples looked at, what makes them read written down in words, and how far this model stylises
- [ ] Variants (size, colour, condition) and missing family members listed
- [ ] Verdict per existing model
- [ ] Budget and markers stated
- [ ] Brief committed, issues filed, nothing built yet
