# art/: how our Blender assets are made

Models are built by Python scripts run inside Blender (through the Blender MCP tool), not modelled by hand, so any
asset can be regenerated, diffed and tweaked by changing numbers. Sources live here; exports go to `Assets/Art/...`.
Conventions are in [`docs/assets/asset-list.md`](../docs/assets/asset-list.md) section 2.

## Running a script

In Blender (the MCP add-on running), `execute_blender_code` with:

```python
import runpy
runpy.run_path(r"<repo>\art\scripts\gt_bucket.py", run_name="__main__")
```

**Where files go.** Exports are written under an output folder: `out/` in this repo by default (`common.configure(out=r"<folder>")` or the `LOWPOLY_OUT` environment variable change it; set it to a Unity project's root to build into `Assets/Art/...` as before). `common.configure(formats="fbx,glb")` also writes GLB files for the web viewer (`export_glb`); `only={...}` limits the exporters to some model names and `prefix=` keeps a build from replacing same-named collections in a Blender file that other work shares.

Scripts take optional settings through `init_globals`, for example
`runpy.run_path(path, init_globals={"SPECIES_LIST": ["goat"], "STYLES_LIST": ["faceted"]}, run_name="__main__")`.
Always pass `run_name="__main__"`: most scripts build only under `if __name__ == "__main__"`, so without it they import and do nothing.

## What is here

| File | Does |
|---|---|
| `scripts/common.py` | Shared helpers: the 16 x 16 **palette** (append-only; indices are baked into UVs), lofting, subdivision, per-face colouring, FBX and clip export |
| `scripts/gt_bucket.py` | A prop (`GT-03`): the pipeline test |
| `scripts/quadruped_builder.py`, `species.py`, `species_pets.py`, `species_farm_dog.py` | **Any four-legged animal from a description**; dogs and cats are generators with breed and coat arguments; the farm dog (`species_farm_dog.py`, issue #275) has its own shape and five coats that are one mesh painted five ways (`GN_DogCollie<Coat>_faceted_01.fbx`: the game swaps the mesh, `DogSkin`) |
| `scripts/gn_animals.py` | Builds and exports every species: cow, horse, sheep, pig, goat, 8 dog breeds, 8 cat coats and the wildlife of `species_wild.py` (raccoon, opossum, skunk, fox, deer doe, buck and fawn, bear) |
| `scripts/quadruped_rig.py` | The shared quadruped skeleton (bone names, skinning by distance) |
| `scripts/quadruped_walk.py`, `quadruped_idle.py`, `gn_animal_clips.py` | Walk and idle clips that adapt to each animal's legs; one FBX per clip. `quadruped_walk.py` takes a `GAIT` (walk, trot or run): the dogs also get `@Trot` and `@Run` (a diagonal trot; a rotary gallop with the legs gathered and the back arching), and a walk, trot and run whose legs also slide along the body (the legs are too short from the elbow down to take a real stride) so every planted hoof moves back exactly as fast as the body moves forward. It prints each clip's ground speed and foot slide, and `gn_animal_clips.py` writes the speeds to `Anims/gait-speeds.json` for the animator tool (`docs/art/animal-notes.md`, "Dog gaits"). It touches only its own action, so it can run in a Blender file others are using |
| `scripts/biped_bird.py`, `gn_birds.py` | The same idea for birds on a shared biped-bird rig (18 bones); a chicken hen and the turkey tom and hen so far. No walk or idle clips yet (the tom has a **Display** clip: `turkey_display.py`, below) |
| `scripts/humanoid_rig.py`, `gp_builder.py` | The humanoid rig and a person builder: palette outfit, hair, hat and extras (badge, tie, sunglasses, beard, vest); `mf=` gives the person a **build** (a belly, thighs, neck, arms and face of their own: `data/content/builds.json`, `builds.py`, [`docs/art/human-builds.md`](../docs/art/human-builds.md)) |
| `data/content/builds.json`, `scripts/builds.py`, `dev/builds_check.py` | The body builds of the people (#269): each cast role's mass factor `mf`, the limits, the region factors at the anchors 0.8 to 1.6 that `gp_builder.py` interpolates, the design's gameplay hooks as data (nothing reads them yet). `builds.py` is the reader (no Blender), `builds_check.py` the checker `dev/check.py` runs |
| `scripts/gp_humanoid.py`, `gp_cast.py` | The plain base person and the named cast: farmer, farmer's spouse, farmer's kid, sheriff, deputy, two FBI agents, Man in Black, worker, waitress, grandparent |
| `scripts/props_lib.py`, `props_farm.py` | A box-and-cylinder builder and 32 farm props (the FBI's tripod **floodlight stand** `GL_FloodlightStand_01` among them; tools, containers, fences, lamps, doghouse, generator, scarecrow, and the power line's **utility poles** (plain, corner with a second arm, transformer) and the **service entry** (meter box, riser, weatherhead: `GL_UtilityPole_01`, `GL_UtilityPoleCorner_01`, `GL_UtilityPoleTransformer_01`, `GL_ServiceEntry_01`; the wires are made in Unity, `FarmsteadPowerLines.cs`)...) |
| `scripts/vehicles.py` | Pickup, tractor, sheriff cruiser, crashed ship (importable: `cars.py` reuses it) |
| `scripts/ship_props.py` | **Alien set dressing for the landed ship's inner wall ring** (#143, #212: four interior types, `LAYOUTS`): stasis pod, specimen jars (a cow, a plant, a little alien), medical couch, lockers, tool rack, sample rack, cable run and a holo-map table (the lab), a pilot's station, nav screen and radar post (the bridge), crates and drums (the cargo hold), a bunk and a mess table (the quarters), 190-870 triangles each, no new palette colours; `LAYOUTS` (repeated in `FarmsteadShipInterior.cs`) lays them out in the ship's plan for a picture with `SHIP_PROP_LAYOUT = True`; `Assets/Art/Global/Vehicles/GV_ShipPod_01`, `GV_ShipJars_01`, `GV_ShipCouch_01`, `GV_ShipLockers_01`, `GV_ShipToolRack_01`, `GV_ShipSampleRack_01`, `GV_ShipConduit_01`, `GV_ShipHoloTable_01`, `GV_ShipHelm_01`, `GV_ShipNavScreen_01`, `GV_ShipRadarPost_01`, `GV_ShipCrates_01`, `GV_ShipDrums_01`, `GV_ShipBunk_01`, `GV_ShipMess_01` |
| `scripts/ship_hulls.py` | **The ship's varieties** (#212, `docs/art/ship-varieties.md`): the shared walkable shell (`shell`: deck, doorway, 12 wall panels, ceiling, seats, power core), the egg and the freighter hulls with their ramp (`ShipRamp`, a hinge) and landing legs (`ShipLeg_n`, slides) as named parts exported open and listed in `art/data/interactions.json`; `GV_ShipEgg_01`, `GV_ShipFreighter_01` (the saucer is `vehicles.py`, which now has a `ShipRamp` part too) |
| `scripts/terminals.py` | **The ship's control panels** (`docs/art/terminal-notes.md`): the console (sloped ledge, button groups, holo-ring, cables into the deck), the green bank terminal, and the red launch terminal, each a curved screen on a leaning control face with glow strips, dials, a hologram and three state lamps (`Lamp_Locked`, `Lamp_Ready`, `Lamp_Working`, separate objects that `TerminalLamps.cs` switches in Unity); about 1450-1850 triangles each; `Assets/Art/Global/Vehicles/GV_ShipConsole_01`, `GV_ShipTerminalBank_01`, `GV_ShipTerminalLaunch_01` |
| `scripts/cars.py` | Sedan, wagon, SUV, minivan, van, taxi, ambulance, tow truck, ATV, motorcycle in civilian paint jobs plus the sheriff, state police, FBI and Man in Black liveries, each New and Damaged, and the farm pickup and tractor in the same paint jobs (106 files) |
| `scripts/buildings.py` | Farmhouse, barn, workshop and town shells from `wall_run()` (walls with door and window openings), gable roofs; each building in several **skins** (white, yellow, blue and green siding, brick, stone, log, block, corrugated, weathered boards) and **conditions** (New, Damaged with holes in the walls) |
| `scripts/kit.py` | The modular building kit on a 3 m grid: wall, floor, ceiling, roof, door, window, stair and trim pieces; wall-type pieces in 6 skins (clapboard, barn, corrugated, brick, concrete, interior), 160 files |
| `scripts/vegetation.py` | Oak, pine, dead tree, bush, boulder, stump and the corn (a 4 m strip of crossed silhouette cards, about 350 tris, built from triangles instead of an alpha texture) |
| `scripts/household.py`, `decor.py` | 79 pieces of furniture and fixtures (since #146 also five seeded bookcases `GH_Bookcase_01..05`, three more rugs, a toy box, a coat rack and a shelf of jars; the water heater's and boiler's pipes run into the wall) (seating, tables, beds, storage, kitchen, bath, soft furnishings, heating, office, diner) and 71 small decor items (lamps, electronics, wall decor, plants, toys, paper, clutter) |
| `scripts/home_styles.py` | **Modern, Retro and Damaged versions of every household and decor piece** (409 files): colour themes, about 40 bespoke shapes (slab sofa vs tufted sofa vs a slashed one; steel fridge vs rounded cream vs rusty with the door hanging), automatic damage (missing parts, sag and tilt, grime) and wrecks such as an overturned table and a tipped bookcase; also `GK_Window_Boarded` |
| `scripts/ships.py` | Alien ships (scout, dart, cigar, triangle, escape pod, probe drone, dropship, MIB craft, mothership), 15 carriable ship parts to find (power cell, hull panel, nav crystal, engine coil...), tools and debris |
| `scripts/ufo.py` | **The abduction UFO** (#148): `SH_AbductionUfo_01`, a 6.7 m saucer (dark belly, pale hull, glass dome, glowing rim band, emitter disc and belly lamps) that flies in for a tagged cow; a flyer, so the origin is the centre of the underside. Run on its own; not part of `build_all.py` |
| `scripts/ground.py` | Tileable 256 px ground textures (grass, dirt, gravel, asphalt, concrete, sand, snow, carpet (a red one and a near-white one to tint), tile...), transparent decals (road lines, puddles, oil, scorch, crop circle, tyre tracks) and road, sidewalk and curb pieces (and `Tex_Crop_Green/Gold`, crop rows for the far fields); `data/ground_surfaces.json` says how many metres one tile covers and which footstep sound it plays |
| `scripts/insects.py` | Twelve insects and a spider in resting poses, real size (a ladybug is 8 mm; modelled in millimetres and scaled when finished): ladybug, beetle, firefly (a `glow_amber` tail), honeybee, two butterflies (monarch, blue: one function, two fill colours), moth, dragonfly, ant, grasshopper, caterpillar, spider. Not rigged; wings are thin outline-and-fill prisms (`wing()`), so a game can flap them with its own code. 60 to 570 triangles |
| `scripts/sports.py` | Sports gear at real size: nine balls (basketball, soccer, baseball, tennis, American football, volleyball, golf, bowling, hockey puck), the nets and goals (basketball hoop, soccer and hockey goals, tennis and volleyball nets: nets are coarse grids of three-sided strands, `goal_net()`), and equipment (wood and metal bats, glove, home plate, base, tennis racket, hockey stick, golf club, football helmet, skateboard, dumbbell, training cone, frisbee). `GS_` prefix |
| `scripts/office.py` | Office furniture and equipment, `GO_` prefix: desks (wood and steel with a drawer pedestal, a corner desk, a conference table), a chair, a filing cabinet, a whiteboard on a stand, a **cubicle kit on a 1.5 m module** (low, high and glass-topped panels, a corner worksurface, an overhead bin with a flap, and an assembled pod), a copier (three trays and a lid that move), a desktop printer, a water cooler (door), a shredder (bin drawer), a wastebasket, a monitor with keyboard, a desk phone. Drawers, trays, doors and lids are parts in `data/interactions.json` |
| `scripts/contents.py` | Things that go inside things: 68 foods, drinks, groceries, pet treats and clothes (all real size, origin on the base), and a **Rotten** version of every fresh food for abandoned houses and the trailer park; the produce has the apple in red, green and golden (one dimpled shape, three palette colours), a banana bunch (five fingers on a crown), lemon, pear, two grapes and a strawberry; `EXPORT = False` builds them in the scene without writing files |
| `scripts/food_shapes.py` | The shaped foods (#344, notes in [`docs/art/food-notes.md`](../docs/art/food-notes.md)): banana (a loft along a curve, five ridges), cabbage (core and five leaf shells), lettuce (three rings of cupped leaves), corn (cob and two layers of husk), the egg carton (12 cups, 12 eggs in white, brown and blue, a hinged `Lid` exported open) and the cheese wedge (rind, sloped top, cut faces with holes); batch 2 (#344): apple, orange, tomato, potato, onion, carrot, pumpkin, watermelon, bread loaf, baguette, sausages, drumstick, fish, chips bag, flour and sugar sacks, pickle jar; built with `Prop.quads` (a curved sheet) and `Prop.poly` (an oriented face) from `props_lib.py` |
| `scripts/interactive.py` | **Appliances and storage that open**: fridge, stove, microwave, toaster, washer, dryer, kitchen counter, bread box, wardrobe, dresser, nightstand, cabinet, locker, filing cabinet, safe, chest, suitcase, toolbox, medicine cabinet, fuse box, vending machine, cooler, dumpster, trash can, mailbox, each in Classic, Modern, Retro and Damaged (the Damaged ones hang ajar). Writes `data/interactions.json` |
| `scripts/emitters.py` | Lights, sounds and switches for props (a lamp's bulb and switch, a radio's sound, a fridge's hum and light, the fuse box's main breaker) and traits for the alien abilities (power, possess, jam, blackout, noisy); a table per prop, applied when the prop finishes |
| `scripts/inventory.py` | **The asset inventory** (#345, `docs/assets/inventory.md`): plain Python, no Blender, Unity or LFS objects. Lists every FBX under `Assets/Art` (not `Anims/`) with its category, size (from the Git LFS pointer) and its emitters, parts and traits from `data/interactions.json`; the Tris and Mats columns fill from `Logs/dev_world_inventory.json` (a list of `{id, tris, materials}`) when the Unity dev test world writes it. `python art/scripts/inventory.py` rewrites the table, `--check` says whether it is current |
| `scripts/audit.py` | The check to run before exporting: lists models with parts that touch nothing else (floating handles, seats above frames); with `AUDIT_CLIP = True` also the models whose parts **pass through each other** or share a coplanar face (a corn cob through its husk), with how deep; run it over the Food folder as `docs/art/food-notes.md` says |
| `scripts/build_all.py` | Re-runs the asset scripts (the groups in its `SCRIPTS` table, `ship_props` and `ship_hulls` among them) and re-exports every FBX they make (a few minutes; the home styles and interactive groups take about a minute each); needed after a palette change. `GROUPS=[...]` limits it, `WITH_CLIPS=True` also redoes the animal clips. Not in it: `ufo.py`, `gp_clips.py`, `turkey_display.py`, the animal clips unless `WITH_CLIPS=True`, and the audits; run those directly. `insectoid.py` is the `insectoid` group, although the docstring says it is in none |
| `scripts/aliens.py` | Non-humanoid aliens (the Energy Being: a static floating mesh, a glowing core with orbiting shards and two dark slanted eyes on its front). The humanoid aliens are in `gp_cast.py`: Grey (a big egg of a head over a small chin, huge slanted black eyes, three long fingers and a thumb), Shadow Entity (a long head with two glowing slits, long thin fingers), Reptilian (scaled green, a snout with teeth, gold slit eyes on the sides under a heavy brow, a tail and a crest of fins: `face="reptilian"` and the `tail` and `crest` extras of `gp_builder.py`) and Nordic (tall, pale, long hair, a robe, glowing eyes under brows, a small nose). Their heads and faces are in `alien_parts.py` |
| `scripts/alien_parts.py` | The alien parts `gp_builder.py` adds when `face=`, `joints=` or `hands=` is set: a head shape per race (`HEADS`), faces made of caps that sit ON the skull (`Skull`: where the head's front is at any x and z; `dome`: a faceted cap with its rim buried and its middle proud: eyes, pupils, brows, nostrils), long fingers (`HANDS`), the hip block that covers both hip joints and the ball over each shoulder joint (the skeleton's joints are outside a narrow torso, so a bare limb opens a gap when it swings). Also used by `aliens.py` for the Energy Being's eyes |
| `scripts/species_wild.py` | The wildlife for `quadruped_builder.py`: raccoon (black mask, ringed tail), opossum (pale face, bald tail), skunk (two back stripes, big raised tail), red fox (black stockings, white-tipped tail), white-tailed deer (doe, buck with antlers, spotted fawn) and black bear (level back, tan muzzle, tall ears, a very short tail), each scaled to its real size (`docs/art/animal-notes.md` holds the research and sizes); the turkeys (tom with a wattle, beard and a tail of one plate per feather, each on its own bone, that lies folded together and flat behind him; hen with a smaller one) are in `biped_bird.py`, and `turkey_display.py` makes the tom's **Display** clip (`TurkeyTom_faceted@Display.fbx`: the tail rises 80 degrees, the feathers open from 3 to 13 degrees apart into the fan, it quivers, and folds back). Idle and Walk clips for the quadrupeds come from `gn_animal_clips.py` |
| `scripts/audit_animals.py` | The animal audit (skill `body-audit`): builds every species and checks that all the parts are there (eyes, ears, nose, tail, four legs, and the species' own: mane, horns, udder...), that each one joins the animal (a surface test), that the eyes and ears are spaced and placed right, and that the size matches the real animal (`REFERENCE`) |
| `scripts/audit_bodies.py` | The body audit (skill `body-audit`): imports each person and alien FBX (the Insectoid and the Energy Being too) and checks that the parts join (neck, arms, legs, shoes, nothing floating: for an alien the surfaces must touch), that every alien has eyes that show, and that the lengths are proportional (head, neck, arms, legs, feet); people in human ranges, aliens a little looser, with each allowed deviation written down in the script. The people are also audited **at their build and at the lightest and heaviest build the data allows** (joins, the measures of the build in `HUMAN_BUILD`, the arm clearance in the clips' poses: [`docs/art/human-builds.md`](../docs/art/human-builds.md)). It removes only the objects it imported, so it can run in a Blender file others are working in |
| `scripts/audit_props.py` | The prop audit (skill `layout-audit`): builds every prop in `props_farm.py`, `household.py`, `decor.py` and `interactive.py` part by part without touching the Blender scene, and checks origin on the floor, real sizes, the front facing -Y, floating parts (1 cm), parts running through each other (the handle through the head, the wheelbarrow beams) and pipes ending in the air; `WRITE=True` writes `data/prop_geometry.json` (sizes and the heights of the tops things stand on) |
| `scripts/audit_layout.py` | The layout audit (skill `layout-audit`): plain Python on `Logs/farmstead_layout.json`, which `FarmsteadLayoutDump.Run` writes from Unity: people sunk in floors, lamps off their tables, things facing or too close to walls, duplicated appliances and a washer without a dryer, pipes in the air, doors that cannot swing, empty rooms, twins, identical bookshelves. `dev/check.py` runs it when the JSON exists |
| `scripts/insectoid.py` | The Insectoid: a 2.3 m mantis-like biped with a 17-bone Generic rig (rigid skinning), the abdomen carried out behind as a counterweight, a triangular head with big compound eyes (a dark centre each), mandibles and antennae, a ball over every joint (shoulder, elbow, hip, knee, ankle, neck, abdomen) so the rods do not open a wedge on the outside of a bend, and its Idle, Walk, Run and Carry clips **inside the same FBX** (so the clip paths match the model's: no remapping in Unity) |
| `scripts/gp_clips.py` | Six hand-made Humanoid loops for the people, `People/Anims/GP_Humanoid@Idle.fbx` (relaxed standing, breathing, a slow weight shift), `@Sit.fbx` (seated, hands in the lap), `@Carry.fbx` and `@CarryOne.fbx` (carrying), `@Walk.fbx` and `@Run.fbx` (in place, no root motion: the game moves the player and the Animator blends the loops), because the people are exported in a T-pose and the Universal Animation Library's own clips are not in the repo. They play on every person and humanoid alien |
| `data/ual_skeleton.json` | The 65-bone humanoid skeleton of Quaternius's Universal Animation Library (CC0), so the rig rebuilds without the download |

## Quality bar and brief

Models are **better-made low-poly** (issue #344): the shared palette and these generators, not realism, and never scanned, library or `generate_3d` models. The bar (proposed triangle budgets, bevels, hollow things hollow) is `docs/assets/asset-list.md` §2.1; the procedure is the `blender-assets` skill, "Brief before build". In short:

- **Write the brief first** (real object and variant, size, 3-5 recognisable features, palette colours, how the game uses it, moving parts and markers), kept in the category's notes file next to `animal-notes.md` and `terminal-notes.md` in `docs/art/`. Build a blockout, look at it, then add trim and detail.
- **Keep what works:** a rework never renames or replaces rigs, clips, moving parts, markers, `data/interactions.json`, ids or file names; the animals stay faceted unless the owner says otherwise.
- **Alien tech on starships (the look):** ramps, doors, hatches and landing legs telescope, extend or open like an iris, with a lit edge, and landing legs come out of a recess in the hull and end in a foot pad. Only the two part kinds the game can pose exist, `hinge` and `slide` (telescoping = several slide stages, an iris = several hinged leaves); existing parts (`ShipRamp`, `ShipLeg_N`) keep their names and kinds. A part that scales or shrinks needs a Unity change first: #364.
- **Vehicle lights are emitters at their real positions** (`emitters.py`), and each `Light_` becomes a real Unity Light, so only the headlights (front, aimed forward), red tail and brake lights (rear) and the light bar of police and ambulance liveries are `Light_` markers; indicators and the plate light are glow only (emissive palette colour). Not one point in the middle.
- **The United States is the reference** (ambulance types, police liveries, signs, appliances, packaging). Other regions are #346 (`needs-decision`): do not build them.
- **Reference images and models are looked at, never traced, copied or committed.**

## Adding an animal

1. Add an entry to `scripts/species.py`: body and head cross-sections, the two leg profiles, the tail, a colour
   function, and an `extras` hook for horns, ears, udders and so on. Copy the closest species and change the numbers.
2. `gn_animals.py` with `SPECIES_LIST = ["yours"]` builds both styles and exports them. Look at it, adjust, repeat.
3. `gn_animal_clips.py` with the same list makes its walk and idle (and, for a dog, trot and run: `CLIPS` picks which; `EXPORT=False`
   only reports). The walk solves each hoof onto the ground, so
   it needs no hand tuning, but it caps the stride to what the legs can reach.

**House style: `faceted`** (flat, hard-edged, no subdivision), matching the Quaternius packs (CC0, about 300-400 verts,
quads, 2-3 flat colours). Everything builds faceted by default. A rounded `smooth` variant exists
(`STYLES_LIST = ["smooth"]` for animals, `STYLE = "smooth"` for people) but it was judged not to look right and is not exported.

| | faceted | smooth |
|---|---|---|
| Animals | 8-sided body, 6-sided head, 5-sided legs, flat shaded: about 400-700 tris | 12-sided, subdivided 1-2 times: 3,000-4,500 tris |
| People | 6-8 sided limbs and torso, flat shaded: about 800-900 tris | subdivided once: about 3,500-4,000 tris |

## Adding a person

Add an entry to `CAST` in `scripts/gp_cast.py`: palette colours for skin, shirt, pants, shoes and hair, a hair style,
a hat and extras, plus `scale` (height), `head_scale` and `shape` (neutral, masculine, feminine) for proportions, and, for a person, a role with an `mf` (build) in `data/content/builds.json` (an alien keeps `girth`). A new hat or extra is a few lines in `gp_builder.py`. The people share one rig, so the same
clips play on every one of them.

## On the farm

`Assets/Editor/FarmsteadArt.cs` puts these models on the Farmstead graybox when you run `Tools > Alien Investigation > Build Farmstead Layout`
(or Auto Setup Scene). The graybox primitives keep every collider, so the NavMesh and `FarmsteadSelfTest` do not change; the model hides the
primitive's renderer and stands in its place (`Dress`). Fences, the cover groups (bushes, boulders, stumps, dead trees in `FarmsteadLayout.CoverGroups`) and the set dressing in
`FarmsteadLayout.ArtProps` have no colliders, except the boulders and the tractor (cover you can bump into; the NavMesh goes round them). The ground, roads, drive, yard and cornfield soil use the tiling `Tex_*.png` from `ground.py`.
If a model or texture is missing the graybox stays visible and one warning is logged. Add a prop by adding a row to `ArtProps`.

The building interiors are furnished the same way: `FarmsteadBuildings.cs` lists each piece (`At` centres it, `Back` puts it against a wall, `Hang` mounts it at a height; models are found by file name, and the footprint and collider come from the model itself), and `BuildingGenerator` stands the model on it. A missing model leaves a grey box.

## Facing and axes

Everything is modelled facing **-Y**, +X is the character's left (`_l`), Z up, feet on z = 0 (it arrives facing +Z in Unity). Static meshes export
with transforms baked in; rigged ones do not (baking rotates bones), so check Bake Axis Conversion on import in Unity.

Every exported model carries two empties, **`Socket_Front`** and **`Socket_Back`**, just outside its front and back faces (added by
`export_fbx`). Place a prop against a wall by lining its `Socket_Back` up with the wall; stand a person or open a door at
`Socket_Front`. Wall-mounted pieces have their origin at the centre of the mount.

## Variants

Most categories come in several versions made from one definition, not drawn twice: furniture and decor in Modern, Retro and Damaged
(`home_styles.py`); buildings in skins and New/Damaged; cars in paint jobs and New/Damaged; fresh food in Rotten; interactive props in all
four styles. A variant is a colour remap (`props_lib.THEME`) plus, where the shape differs, its own function; `Prop.damage()` makes
anything look neglected (missing small parts, grime, tilt) with a seed so the result is the same every run.

## Interactive props

`interactive.py` builds props whose doors, drawers and lids are **separate child objects with the origin on the pivot**, named for their
role (`Door`, `DoorL`, `Drawer1`, `Lid`...). Unity opens a part by rotating (hinge) or moving (slide) that transform about its own origin.
`data/interactions.json` lists each part's `kind`, `axis`, `pivot`, `limit` (hinge: degrees to open, the sign is the direction; slide:
metres, negative is out the front) and `rest` (the exported pose, 0 = shut), plus each **slot**: an empty called `Slot_<name>` marking where
loose items go (a fridge shelf, a wardrobe rail, a drawer floor). A slot's position is the surface an item's base sits on, its size the room
above it, and a slot with a `part` rides on that part (parent the spawned item to the drawer). The items are the models from
`contents.py` and the small decor, spawned by game code. The axes in the JSON are Blender's; Unity's axes differ (a rotation about Blender Z is
about Unity Y, and handedness may flip the sign), so try one prop in Unity and the rest follow.
**Lights, sounds and switches.** Props also export `Light_<name>`, `Sound_<name>` and `Switch_<name>` empties, listed under `emitters` in the
same JSON with what they do (colour and range, which clip, how far the noise carries, what a switch controls and who may use it), and `traits`:
`power` (the fuse box turns it off), `possess` (an Energy Being can take it over), `jam` (an Energy Being can jam it), `blackout` (a Shadow Entity can
switch it off), `noisy` (its sound alerts humans). They come from the table in `emitters.py`, keyed by the prop's base name, so every style of a
prop gets them (the Damaged ones are marked `working: false`). Nothing plays or lights in Blender: in Unity `Assets/Scripts/Props/PropRuntime.cs` does it. `Assets/Editor/PropRuntimeSetup.cs` reads this JSON when `FarmsteadArt.Place` stands a model on the map, converts it to Unity's axes and bakes it into a networked `PropRuntime` on the model (lights from the `Light_` empties, an `AudioSource` for each `Sound_`, an aimable point at each `Switch_`, doors, drawers and lids that swing or slide, the traits for the abilities); the server decides whether a lamp is on or a door open and every machine shows it. A sound's `event` is `Resources/PropAudio/<event>` (missing = a generated placeholder tone in the editor, silence in a release build). Changing this file needs *Build Farmstead Layout* to re-bake the props. Cars are not in the JSON yet: `PropRuntimeSetup` gives every car an alarm in code (move it into `emitters.py` when the art side wants it).

To add a prop, write a function in `interactive.py` with `door()`, `drawer()` or `lid_back()` for the moving parts and `p.slot()` for the slots. A lidded container with no door or drawer on its front (cooler, bread box, chest, toolbox, suitcase, dumpster) must call `shell(..., top=False, front=True)`: `shell()` leaves the front open for doors, so without `front=True` you see straight into the box. `front=True` also protects every wall of the shell from `Prop.damage()` (`keep_solid`), so a Damaged one is still a closed box (the lid hangs ajar, the grime stays).

## Humanoid clips

Quaternius's Universal Animation Library (CC0, 43 free clips: idle, walk, jog, sprint, crouch, sit, drive, push,
interact...) plays on our humanoid because it shares the skeleton in `data/ual_skeleton.json`. The clips themselves
are not in the repo (22 MB). Download `Universal Animation Library[Standard].zip` from
<https://quaternius.itch.io/universal-animation-library> (free, "No thanks, just take me to the downloads") if you
need them in Blender; in Unity, import its FBX and use a Humanoid avatar.

## Unity import checklist (done: `Assets/Editor/ArtImportRules.cs` applies all of it)

Found while assembling a test room in Blender from the exported FBX files (walls, floor, furniture and decor all lined up at the right
scale, so the round trip works):

- **The palette texture needs Point filtering and no mipmaps.** Each swatch is only 4 px, so with the default bilinear filtering and mip
  maps the colours smear into their neighbours at a distance (the test room's walls showed stripes until I forced nearest-neighbour).
  `ArtImportRules` sets `GlobalPalette.png` to Filter Mode: Point, Generate Mip Maps: off, Compression: None on every import, so a
  re-export cannot undo it. Ground textures tile (Repeat); decals clamp and use alpha as transparency.
- **One shared material.** Every FBX references a material called `GlobalPalette` with that texture. Remap it to a single URP Lit material
  (smoothness low) rather than letting Unity create one per file. Run `Tools > Alien Investigation > Set Up Art Materials` once (it
  creates `M_GlobalPalette.mat` and re-imports every model); the importer then applies the remap to each FBX on import.
- **Axes.** Static meshes are exported with the axis conversion baked in; rigged ones are not (baking rotates bones). Check that both come in
  upright with scale 1 and that rigged ones have no stray -90 degree rotation (turn on Bake Axis Conversion if they do).
- Humanoid rigs: everything under `People/` imports as Humanoid and the avatars map cleanly; animal and bird rigs use Generic.
  Clips named `@Idle`, `@Walk`, `@Trot`, `@Sit`, `@Run`, `@Carry` and `@CarryOne` loop (and so do the Insectoid's four clips); the People clips also get the root's height, position and turn baked into the pose. The Insectoid is a Generic rig whose avatar is created from its own model (`ArtImportRules` has a rule for `GA_Insectoid_01.fbx` alone; the rest of `Aliens/` has none), and Unity names its clips `GA_Insectoid_01_Rig|Idle`, `|Walk`, `|Run` and `|Carry`. It has no `Socket_Front`/`Socket_Back` empties.
- Floors: the kit's floor pieces have their origin on the walking surface (the slab hangs below), so furniture and walls placed at z = 0
  stand on them.
