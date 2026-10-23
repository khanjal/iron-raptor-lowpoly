# Prop and object catalogue

One catalogue of the props and objects the game should consider, for **every location the game plans** (the farm, the trailer park,
the campground, a suburb, a laboratory, a military base and Area 51, a town with a diner, gas station, motel and hospital, a warehouse and
airport hangar and scrapyard, a forest cabin, and the drive-in, fairground and cemetery side maps), built from the repo as it stands and from
what game developers, environment artists and asset libraries use. It exists to plan art and the seeded randomizer (#153, #195, #196), and
it feeds #156 (detail pass), #265 (more props and the tech level), #266 (trees and vehicles), #267 (hidden oddities), #270 (storage), #262
(crop variety) and the interiors work (#146, #43).

**Documentation only.** Nothing here was compiled or run, no asset was made, and nothing under `Assets/`, `art/`, `game.md` or `README.md` changed.
Statuses were decided by reading the repo (see [How statuses were decided](#how-statuses-were-decided)), not by opening Unity or Blender.

- [Files and counts](#files-and-counts)
- [Columns and vocabularies](#columns-and-vocabularies)
- [How statuses were decided](#how-statuses-were-decided)
- [What the research says](#what-the-research-says)
- [Where we stand: status by location, and the gaps](#where-we-stand-status-by-location-and-the-gaps)
- [Next 50: seven PR-sized batches](#next-50-seven-pr-sized-batches)
- [Must-have 30 per location](#must-have-30-per-location)
- [Items games commonly use as interactive or stealth props](#items-games-commonly-use-as-interactive-or-stealth-props)
- [Not catalogued, and decisions waiting](#not-catalogued-and-decisions-waiting)
- [The catalogue by location, room and area](#the-catalogue-by-location-room-and-area)
- [Sources](#sources)

## Files and counts

**Rows are placements, not distinct assets.** A row is an object in the role or the place a level needs it: "Refrigerator" in the kitchen and
"Spare refrigerator" in the garage are two rows that cite the same model, and so are "Bench", "Bus stop with a bench" and "Cemetery bench". So the
`have` and `partial` counts say how many placements an existing model already covers, **not** how many models exist; the second table below gives the
number of distinct asset paths those rows cite. A row that fits two or more locations is a row of the shared file, and its `locations` column lists where it
fits; a row that fits one location only is a row of that location's file. So the "farm view" is every row whose `locations` contains `farm`, in the
shared file and in `props/farm.csv`. **Concept duplicates** (the same object listed twice under different names, such as "Clothesline" in the trailer
park and "Clothesline between poles" in the shared file) were merged in the review pass: the kept row lists every location and its notes say which
ids were folded into it (`merged here: ...`). Ids were **not** renumbered, so a gap in a file's numbering is a merged row. Only the clearest
duplicates were merged: rows that are the same model in a different role stay separate (see above), and so do pairs that live in two location
files and would need a new shared id, such as the diner's neon OPEN sign and the trailer park office's open sign, which cite the same model.

| file | holds | rows | have | partial | missing |
|---|---|---|---|---|---|
| [`prop-catalogue.csv`](prop-catalogue.csv) | shared (fits two or more locations) | 971 | 327 | 98 | 546 |
| [`props/farm.csv`](props/farm.csv) | farm | 184 | 49 | 34 | 101 |
| [`props/trailer-park.csv`](props/trailer-park.csv) | trailer-park | 96 | 17 | 23 | 56 |
| [`props/campground.csv`](props/campground.csv) | campground | 92 | 14 | 16 | 62 |
| [`props/suburb.csv`](props/suburb.csv) | suburb | 105 | 11 | 32 | 62 |
| [`props/laboratory.csv`](props/laboratory.csv) | laboratory | 67 | 10 | 13 | 44 |
| [`props/military-base.csv`](props/military-base.csv) | military-base | 89 | 21 | 28 | 40 |
| [`props/town.csv`](props/town.csv) | town | 115 | 25 | 29 | 61 |
| [`props/industrial.csv`](props/industrial.csv) | industrial | 59 | 3 | 12 | 44 |
| [`props/cabin.csv`](props/cabin.csv) | cabin | 33 | 6 | 7 | 20 |
| [`props/leisure.csv`](props/leisure.csv) | leisure | 52 | 7 | 14 | 31 |
| **total** |  | 1863 | 490 | 306 | 1067 |

Placements against distinct assets:

| status | rows (placements) | distinct asset paths those rows cite |
|---|---|---|
| `have` | 490 | 350 |
| `partial` | 306 | 182 |
| `have` or `partial` | 796 | 394 |

A path is one entry of `existing_asset` (a file, or a folder such as `Global/Vehicles/Sedan/` that holds the colour variants of one model). Several
`partial` rows cite a model that also backs a `have` row (the bench, the generator, the pole lamp), which is why the combined count is lower than the
sum.

Rows that fit each location (its own file plus the shared rows that list it):

| location | rows that fit it (own and shared) | have or partial | share built |
|---|---|---|---|
| farm | 846 | 429 | 50% |
| trailer-park | 665 | 351 | 52% |
| campground | 354 | 173 | 48% |
| suburb | 775 | 375 | 48% |
| laboratory | 263 | 135 | 51% |
| military-base | 337 | 180 | 53% |
| town | 540 | 302 | 55% |
| industrial | 326 | 157 | 48% |
| cabin | 586 | 318 | 54% |
| leisure | 192 | 107 | 55% |

Every "share built" percentage, in this table and in the gap tables below, is `have` plus `partial` over the rows, rounded **down** to a whole number.

There are 1863 rows in all. That is more than the 400 to 700 first asked for because the catalogue now covers ten locations. The **farm view**
(every row whose `locations` contains `farm`) is the first line of the second table, and 40 of those rows are the alien ship set that every map shares;
filter on `locations` to get any single location. Many rows are deliberately small things (a hose, a rope, a mug) because the slot pools (#195) and the
hidden-oddity containers (#267) need small things to place.

By kind:

| kind | rows |
|---|---|
| structure | 406 |
| decor | 202 |
| furniture | 198 |
| tech | 182 |
| tool | 146 |
| container | 141 |
| vehicle | 125 |
| appliance | 96 |
| clutter | 93 |
| plant | 63 |
| oddity | 56 |
| wildlife | 50 |
| toy | 42 |
| clothing | 28 |
| hazard | 19 |
| food | 16 |

By category (derived from the name and kind, so it is a browsing aid, not a hand-made taxonomy):

| category | rows |
|---|---|
| Buildings and structures | 170 |
| Hand and power tools | 104 |
| Doors, windows and building parts | 91 |
| Wall and surface decor | 88 |
| Clutter and small items | 81 |
| Lighting and fire | 75 |
| Toys, play and fairground | 65 |
| Plants, trees and crops | 63 |
| Seating | 61 |
| Containers, drums and tanks | 57 |
| Cars and trucks | 57 |
| Alien ship and alien tech | 55 |
| Oddities and gags | 54 |
| Boxes, crates and cases | 53 |
| Animals and pets | 50 |
| Kitchen and appliances | 49 |
| Phones, radio and communications | 45 |
| Roads, street furniture and utilities | 45 |
| Fences, gates and barriers | 35 |
| Electronics | 34 |
| Heating, cooling, water and power | 34 |
| Tables, desks and counters | 31 |
| Field gear and disguises | 30 |
| Security, sensors and smart devices | 29 |
| Shelving and racks | 28 |
| Cookware and tableware | 27 |
| Computing and office tech | 27 |
| Animal housing and farm fittings | 26 |
| Signs and flags | 25 |
| Bins, buckets and mailboxes | 24 |
| Soft furnishings | 24 |
| Screens and audio | 24 |
| Storage furniture | 24 |
| Farm and work machines | 24 |
| Beds and bedding | 22 |
| Clothing and personal items | 22 |
| Furniture | 20 |
| Hazards and traps | 19 |
| Food and drink | 16 |
| Lab equipment | 13 |
| Bikes and small vehicles | 12 |
| Laundry | 9 |
| Boats and water | 8 |
| Bathroom fixtures | 7 |
| Aircraft | 6 |

## Columns and vocabularies

`id, name, category, location, room_or_area, kind, tech_tag, rarity, size_class, interactive, stealth_role, status, existing_asset, locations, content, notes`

| Column | Values and meaning |
|---|---|
| `id` | `PC-SH-nnn` (shared), `PC-FA-nnn` (farm), `PC-TP` (trailer park), `PC-CG` (campground), `PC-SB` (suburb), `PC-LB` (laboratory), `PC-MB` (military base), `PC-TN` (town), `PC-IN` (industrial), `PC-CB` (cabin), `PC-LE` (leisure). Never renumbered or reused: a row merged into another leaves a gap, and the kept row's notes name it (`merged here: ...`) |
| `name` | The object, in plain words, no brand names and no real logos |
| `category` | A browsing group such as Seating, Lighting and fire, Alien ship and alien tech |
| `location` | `shared`, or the one location the row belongs to |
| `room_or_area` | The brief's list (kitchen, living room, bedroom, kids room, bathroom, office, laundry, cellar, attic, porch, yard, garden, barn, workshop, garage, coop, field, road, ship, wild) plus these, because the other locations need them: `any` (not tied to a room), `hall`, `dining room`, `farmhouse`, `house exterior`, `interior extras`, `street`, `main street`, `diner`, `gas station and truck stop`, `motel`, `hospital`, `sheriff's office`, `church`, `mobile home`, `RV pad`, `clubhouse`, `pool`, `playground`, `maintenance yard`, `tent site`, `ranger station`, `bathhouse`, `lake`, `amphitheater`, `lookout`, `lab floor`, `containment`, `security`, `chemical storage`, `support`, `perimeter`, `hangar`, `barracks`, `command`, `motor pool`, `helipad and airfield`, `bunker`, `warehouse`, `scrapyard`, `cabin`, `drive-in`, `fairground`, `cemetery` |
| `kind` | furniture, appliance, tech, tool, container, decor, clutter, toy, food, clothing, plant, vehicle, wildlife, hazard, oddity, and one more, **structure** (fixed built things: sheds, fences, towers, pumps), because the brief's list had no home for them |
| `tech_tag` | `low` (a remote farm: radio and phone), `normal`, `high` (devices in every room), as in #265. Most rows are `normal`, meaning "present at any tech level" |
| `rarity` | `common`, `uncommon`, `rare`: a starting weight for the pools, to be tuned |
| `size_class` | `small` (carryable, fits a drawer), `medium` (one person can move it, or it stands on a table or the floor), `large` (furniture, a vehicle or bigger) |
| `interactive` | `none`, `openable`, `switch`, `movable`, `carryable`, `possessable` (an Energy Being can take it over: `possess` and `jam` traits in `art/data/interactions.json`). A row may list several, joined with `;` |
| `stealth_role` | `none`, `cover`, `noise`, `light`, `distraction`, `hiding spot`, `objective candidate`, joined with `;` when several apply. `noise` covers both a noise the player risks and a noise that masks; the notes say which |
| `status` | `have`, `partial`, `missing` (next section) |
| `existing_asset` | Repo path(s) of the model, texture or folder the status rests on, joined with `;`. Empty for `missing` |
| `locations` | Every location the prop fits, joined with `;`, in the order farm, trailer-park, campground, suburb, laboratory, military-base, town, industrial, cabin, leisure |
| `content` | A content tag a seeded pool can filter on, from #267: empty for ordinary props, `comic` (weird and funny), `secret` (embarrassing and secret), `ufo` (alien-related jokes), `bodypart` (the cartoonish, non-gory body-part gags, so a pool can cap them or leave them out), `mature` (the tame adult-themed gags, left out of every pool unless the host's "Mature humour" setting is on). The same tags as the hidden-oddities design note (`docs/design/content/hidden-oddities.md`, draft PR #296) |
| `notes` | Why it matters, what a stand-in is, the issue it belongs to |

## How statuses were decided

For every row the repo was searched by name and by keyword, in this order: (1) the FBX and PNG
files under `Assets/Art` (1,346 FBX when first written, 1,350 on `origin/main` at `36bdf85`; about 509 base models once the Modern, Retro and Damaged variants, the kit pieces, the clips and the Rotten foods are set aside);
(2) the function names in `art/scripts` (`props_farm.py`, `props_lib.py`, `decor.py`, `household.py`, `interactive.py`, `contents.py`,
`ship_props.py`, `ships.py`, `vehicles.py`, `cars.py`, `vegetation.py`, `buildings.py`, `kit.py`, `home_styles.py`, `ground.py` and the rest);
(3) `art/README.md` and section 10 of `docs/assets/asset-list.md`; (4) `Assets/Editor/Farmstead*.cs` for what the farm places.
A throwaway script checked every `existing_asset` path against the files on disk, so no row points at a model that is not there, and a keyword
sweep of every `missing` row (plus targeted greps for about 110 nouns: bicycle, swing, slide, trampoline, clothesline, grill, tent, lantern,
canoe, pallet, speaker, antenna, mower, hose, gnome, hammock, roomba, centrifuge, fume hood and so on) caught the stand-ins noted below.

| Status | Meaning | Example |
|---|---|---|
| `have` | A standalone model (or decal) for that object exists in the repo and is exported under `Assets/Art` | Sofa (`GH_Sofa_01`), fridge (`GI_Fridge_01`), tractor, laptop, the eight dog breeds |
| `partial` | Something close stands in, or the object exists only as part of a bigger model or as a texture, or the model exists for a different use | The coop's nesting boxes (part of the coop model), a pantry shelf (only the jar shelf), propane tank (a part of the trailer shell), a laundry hamper (the laundry basket), a smart speaker (the Modern radio is a cylinder with a cyan glow), a lawn (a grass texture only) |
| `missing` | Nothing found by name or keyword | Swing set, bicycle, trampoline, clothesline, sandbox, tent, canoe, fume hood, centrifuge, hangar interior |

What the status does **not** say: whether a model is placed on a map, has light, sound or door data in `art/data/interactions.json`, or is wired in
`PropRuntime`. That was checked only in passing (for example the farmhouse's rooms in `FarmsteadBuildings.cs`), not row by row. The Unity scene and
prefabs were not opened. The 23 MarpaStudio prefabs have no mesh in the repo (`asset-list.md` section 1), so they were not counted as `have`.

**Review pass (2026-10-22).** A reviewer found decals marked `missing` that exist and `have` rows that rest on a stand-in. Every row was rechecked
by script against `origin/main` (1,350 FBX and 38 PNG under `Assets/Art` at `36bdf85`, and every `Prop("...")` name in `art/scripts`, all of which are exported):

- `missing` to `have`: the six ground decals (parking lines, oil stain, puddle, tyre tracks, alien footprint, scorch: `Global/Ground/Decal_*.png`)
  and the cellar floor drain (`GK_FloorGrate_01`, which already backed "Floor drains and grates").
- `missing` to `partial`, by the rule above: texture-only rows (wheat field and soybean rows on `Tex_Crop_Gold` and `Tex_Crop_Green`, barnyard mud,
  the worn path, a gravel path, moss, a mud patch, a vegetable bed on tilled soil); and rows whose object exists but not its setup (a wedding photo on
  the portrait frame, the two yard signs on the hand-lettered sign, the hidden bottle, the sweets stash, the very large cheese, the fish in the
  bathtub, the dog on a chain).
- `have` to `partial`: every row whose `existing_asset` is a differently named model standing in, or covers only part of a compound name: for example
  the bunk bed without its footlocker, the barn door as a hangar door, the garage door as a dock door, a candle as a votive rack or a grave lantern,
  the yard pole lamp as a floodlight, the sidewalk as a stoop, `GH_Cot_01` (a crib) as a camp, field or cell cot, and both dogs on a chain. Each
  row's notes say what stands in (`stand-in: ...`).
- Concept duplicates merged (see [Files and counts](#files-and-counts)); every id cited below was regenerated from the CSVs by script.

**Final review pass (2026-10-22).** A second reviewer read the finished PR; each finding was checked against `art/scripts` and the files on
`origin/main` before it was applied:

- `have` to `partial`, with a `stand-in:` note, for rows that cover only part of their name: the two-storey suburban house (`GB_TownHouse` is one
  storey, 2.8 m walls in `buildings.py`), the garage door with keypad (no keypad), the generator trailer (the generator only, as the fairground's
  generator trucks), the lab bench with sink and gas taps (`GH_LabBench_01` is a box, a top and one pipe), the cash box and box office safe (the
  safe only), the squeegee bucket (the bucket only) and the motel room door with a number (the door only).
- Compound names whose second object does exist now cite it and stay `have`: sinks and mirrors (`GH_Mirror_01`), shovel and wheelbarrow
  (`GT_Wheelbarrow_01`), coffee maker and mugs (`GH_Mug_01`), bench and bin (`GD_TrashCan_01`), fence and gate (`GI_FenceSection_01`), and the
  hospital's vending and coffee (`GH_CoffeeMachine_01`; the reviewer suggested `partial`, but both halves exist, so by the rule above it is `have`).
- `missing` to `partial` where a real model stands in: log benches (the bench), desert shrubs and yucca (the farm bush and the potted cactus),
  the home theatre (the armchair and the flat TV), the glass-door drink cooler (the refrigerator). Wire shelving units stay `missing`:
  `GH_Shelf_Wall_*` are single wall planks on brackets, and the shared "Metal wire or bolted steel rack" is `missing` for the same reason.
- The mobile home's parts that `buildings.py` `trailer()` builds into `GB_Trailer` (a 0.5 m skirt, steps with a landing, a roof air conditioner,
  a propane tank, a hitch tongue) are `partial` citing `Global/Buildings/Trailer/`: the skirting panels, the hitch and tongue jack, the steps or
  deck, and the roof vents and rooftop AC (whose note had said the AC does not exist). `GK_Skirting_*` is still a 0.12 m interior baseboard, not
  mobile-home skirting; the trailer's own skirt is the stand-in.
- Seven more duplicate pairs merged (`merged here:` in the kept row): hand truck, fuel tanker, motion sensor, flag pole, bathhouse showers,
  folding camp table, the campground gate barrier. The two neon open signs stay separate (see [Files and counts](#files-and-counts)).
- The farm must-have list cited the plastic play centre and the adult bicycle, whose `locations` did not include `farm`: both now do, so the farm
  view grew by two rows.
- Every `partial` row has a note saying what stands in; the two pole floodlights cite `GL_FloodlightStand_01` like the other floodlight rows
  (still `partial`: the tripod stand is not a pole-mounted light).

## What the research says

**Web access.** `WebFetch` could not fetch any page in this environment (every call failed with a DNS error, which points at the cloud environment's
network policy), so no page was read in full. Everything below comes from search-result summaries of the pages in [Sources](#sources), read through
`WebSearch`. Where a result did not list an item, the catalogue does not claim a pack has it. **Nothing was copied**: no model, texture or text from any
pack; only object names and categories (facts), paraphrased, with the URL. In the review pass (2026-10-22, from a session with web access) every source
link was requested over HTTP (the pages were not read or quoted): four that returned 404 were dropped (the Purdue machinery PDF, the Ohio and Idaho
inventory PDFs and one itch.io pack), the State Farm test host and the Unity fallback and marketplace hosts were replaced by the public ones
(`www.statefarm.com`, `assetstore.unity.com`, each answering 200), and the Game Maker's Toolkit citation now points at the video. A few hosts refuse
scripted requests (403, 429 or a timeout) and were kept.

1. **Libraries are organised by use as much as by room.** Poly Haven groups its models into 15 categories (Furniture, Containers and Storage, Decor and
   Art, Electronics and Appliances, Apparel and Personal Items, Architecture, Food and Kitchen, Industrial and Infrastructure, Leisure, Lighting, Nature,
   Office and Stationery, Tools and Equipment, Vehicles and Transport, Weapons) and Sketchfab uses 18 (Furniture and Home, Electronics and Gadgets,
   Food and Drink, Nature and Plants, Cars and Vehicles and so on). We use a similar `kind` plus `room_or_area` split, which suits slots and pools.
2. **Kenney** ships themed CC0 kits whose size shows what a "complete" set is: Furniture Kit (120 to 140 pieces), Survival Kit (80), Nature Kit (320, with
   camping equipment), Holiday Kit (100), Retro Urban Kit (120), Graveyard Kit (90), and City Kits (Commercial 50, Industrial 40). **Quaternius** has a
   Ultimate Furniture pack (about 20), a LowPoly House Interior pack (120 or more: doors, windows, kitchen and bathroom pieces), Farm Buildings (13),
   an Ultimate Crops pack (100 or more crops in five growth stages) and modular sci-fi environments. A complete farmhouse set in the free libraries is
   a couple of hundred objects, which is the order of magnitude of the farm view here.
3. **Paid and free "room packs" converge on the same lists.** Kitchen packs carry a toaster, kettle, blender, cutting board, pan, pot and utensil rack;
   bathroom packs a plunger, toilet-paper holder, bath mat, shower curtain, toothbrush and scale; garage and workshop packs a workbench with drawers, a
   bench vise, modular shelving, a metal locker, a tool trolley, a floor jack and jack stands, tyres, oil drums and hand tools; barnyard packs a
   pitchfork, shovel, hoe, rake, saw, mallet, wooden bucket, milk can, grain sack, basket, trough and an oil lantern; a basement pack a workbench, ladder,
   cardboard boxes, cabinet, barrel and pallet; an attic pack luggage, a sled, an old TV and an old washing machine. Those lists are the backbone of the
   room sections of the catalogue.
4. **What packs rarely have, and we will have to make.** Searches did not find a bear box, camp stove, cooler or fire ring as separate items in the
   camping packs; no sprinkler, garden gnome, hose reel or lawn mower in the suburban ones; no air machine, newspaper rack or car-wash vacuum in the gas
   station ones; no shipping container in the warehouse ones; no funhouse mirror in the carnival ones; no pegboard in the garage ones (one Daz garage kit
   does list a compressor and a lawn mower).
   Those are rows to expect to model, not to buy.
5. **Real inventories add the overlooked rooms.** Insurance home-inventory checklists (Missouri, Oklahoma, Co-operators; two state PDFs first cited have since gone) go room by room
   through furniture, appliances, electronics, clothing, artwork and equipment, tell the owner not to skip seldom-used gear, and name garages, attics
   and closets as the rooms people forget, with a reminder to photograph inside drawers. A garage inventory lists a lawn mower, shovels and rakes, a snow
   blower, paint and a compressor. Farm-machinery lists (TAFE, Mahindra) give the implement set: plough, harrow, baler (round,
   square), seed drill, sprayer, grain cart and auger, hay mower, chisel plough, field cultivator. A pilots' forum gives a hangar's contents: tool
   chest, engine hoist, wing jacks, ladder, tug, battery tender; a ground-equipment dictionary adds tow tractors, chocks and tow bars.
6. **Set dressing tells a story with ordinary objects.** Game Maker's Toolkit and several level-design write-ups (see Sources) say the same thing: do not
   just place a table; put a half-eaten meal, a spilled drink, a crumpled newspaper, a child's drawing or a discarded letter on it, repeat a motif so the
   world has a presence, keep vignettes optional and avoid clutter overuse. The television-production split of props (stage props, set dressings, hand
   props) maps to our slots: furniture, wall and surface items, and carryables. That is why the catalogue carries many small `clutter` and `oddity` rows.
7. **Games treat interactive props by what they do to the AI**, which is the next-to-last section of this document.

## Where we stand: status by location, and the gaps

Thin areas, sorted by the share of rows that are `have` or `partial` (fewest first). Rows are counted for the location, shared rows included, so a
share of 40 % means 6 of 10 things a person would expect there are still missing. Areas with fewer than four rows are left out.

### The farm

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| any | 78 | 7 | 7 | 64 | 17% |
| garage | 13 | 4 | 0 | 9 | 30% |
| field | 38 | 7 | 6 | 25 | 34% |
| barn | 58 | 10 | 11 | 37 | 36% |
| laundry | 11 | 4 | 0 | 7 | 36% |
| workshop | 47 | 14 | 4 | 29 | 38% |
| coop | 15 | 2 | 4 | 9 | 40% |
| wild | 56 | 22 | 2 | 32 | 42% |
| bathroom | 28 | 9 | 3 | 16 | 42% |
| yard | 68 | 20 | 10 | 38 | 44% |
| attic | 21 | 5 | 5 | 11 | 47% |
| cellar | 42 | 16 | 5 | 21 | 50% |
| garden | 20 | 1 | 9 | 10 | 50% |
| office | 18 | 9 | 0 | 9 | 50% |
| farmhouse | 19 | 6 | 4 | 9 | 52% |
| living room | 60 | 31 | 5 | 24 | 60% |
| kids room | 25 | 10 | 5 | 10 | 60% |
| porch | 33 | 19 | 2 | 12 | 63% |
| kitchen | 63 | 35 | 6 | 22 | 65% |
| bedroom | 30 | 16 | 4 | 10 | 66% |
| hall | 18 | 9 | 3 | 6 | 66% |
| road | 26 | 21 | 1 | 4 | 84% |
| dining room | 18 | 14 | 2 | 2 | 88% |
| ship | 40 | 40 | 0 | 0 | 100% |

**Gaps on the farm, in order of how much they hurt:**

1. **The cross-cutting `any` group (tech, oddities, hazards, field gear): about 17 % built.** The owner's #265 and #267 are almost entirely missing:
   no robot vacuum, tablet, game console, router, smoke detector or baby monitor; no hidden-oddity model (a few, such as the hidden bottle and the
   sweets stash, are existing food models placed, so `partial`); no squeaky floorboard or creaky door as props with a sound; no alarm clock, doorbell
   or cordless phone to ring. This is where the game's noise, light and distraction systems get their inputs, so it is the highest-value gap.
2. **Garage (33 %).** The farm has no garage, but the suburb, trailer park and a farmhouse with a car need one: the garage shell and door exist, nothing
   inside does (lawn mower, freezer, jack, compressor, bikes, paint, shelving).
3. **Fields and orchards (34 %).** Only corn exists as a real model; wheat and the soybean rows are crop-row textures for the far fields
   (`partial`). Sunflower, pumpkin vines, apple orchard rows, vineyard and the machinery (baler, plough, harrow, seed drill, sprayer, combine) are
   missing (#262).
4. **Barn (36 %).** The shell, sliding doors, loft floor, ladder and loft door exist; the stall, stall gate, feed trough, hay rack, hay pulley, saddle,
   tack and the small barn life (cat bed, mouse holes) do not, and the loose hay and the pasture fence are stand-ins. The cow objective sits in this room.
5. **Laundry (36 %).** Washer and dryer exist (and a basket and an ironing board); the utility sink, drying rack, clothesline (outside), iron and
   detergent do not.
6. **Workshop (38 %).** A bench, a generator, a bulb and a toolbox exist; hammer, saw, vise, grinder, drill, welder, sawhorses, chains, tyres and the
   pegboard and steel racks (#270) do not.
7. **Coop (40 %).** The coop model has roosts and nesting boxes built in (`partial`); feeder, waterer, egg basket and heat lamp are missing.
8. **Bathroom (42 %).** Fixtures exist (toilet, sink, tub, shower, mirror, towel rail, medicine cabinet); the small things that make it a bathroom do not
   (bath mat, toilet-paper roll, plunger, scale, toothbrush, curtain).
9. **Yard (44 %).** The swing set, play centre, clothesline, sandbox, trampoline, barbecue, picnic table, birdbath, bikes and lawn furniture are
   all missing (#265); the troughs, dog house, fence, gate, pole lamp and wheelbarrow exist, and the mud, worn path and yard signs are textures or
   stand-ins.
10. **Attic (47 %).** The farmhouse plan has no attic at all; the catalogue has 21 attic rows ready for a house that gets one (the kit has a loft floor,
    beams and a ladder).

The orchard and the porch: the **orchard** is all but missing (apple trees and orchard rows are `missing`, the ladder and crates are stand-ins; only the
fallen apples exist), and the **porch**
is the best-covered outdoor area (63 %): screen door, steps, rail, swing, mat and lamp are mostly built or standing in.

### The other locations

Almost everything specific to the other locations is missing, as expected; the shared rows (furniture, appliances, tools, vehicles, the ship set) carry
the `have` and `partial` counts.

<details><summary>Trailer park</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| pool | 8 | 0 | 0 | 8 | 0% |
| any | 60 | 6 | 6 | 48 | 20% |
| clubhouse | 9 | 1 | 1 | 7 | 22% |
| RV pad | 15 | 2 | 2 | 11 | 26% |
| yard | 61 | 8 | 9 | 44 | 27% |
| garage | 17 | 4 | 1 | 12 | 29% |
| laundry | 18 | 6 | 1 | 11 | 38% |
| bathroom | 27 | 9 | 2 | 16 | 40% |
| maintenance yard | 7 | 2 | 1 | 4 | 42% |
| workshop | 9 | 3 | 1 | 5 | 44% |
| office | 30 | 12 | 3 | 15 | 50% |
| attic | 8 | 3 | 1 | 4 | 50% |
| playground | 4 | 2 | 0 | 2 | 50% |
| cellar | 30 | 10 | 6 | 14 | 53% |
| mobile home | 27 | 4 | 11 | 12 | 55% |
| living room | 53 | 26 | 5 | 22 | 58% |
| street | 10 | 2 | 4 | 4 | 60% |
| porch | 36 | 19 | 3 | 14 | 61% |
| kids room | 24 | 10 | 5 | 9 | 62% |
| kitchen | 60 | 32 | 6 | 22 | 63% |
| road | 34 | 21 | 2 | 11 | 67% |
| bedroom | 28 | 15 | 5 | 8 | 71% |
| wild | 15 | 11 | 0 | 4 | 73% |
| garden | 4 | 0 | 3 | 1 | 75% |
| hall | 13 | 9 | 1 | 3 | 76% |
| dining room | 16 | 14 | 0 | 2 | 87% |
| ship | 39 | 39 | 0 | 0 | 100% |

</details>

<details><summary>Campground</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| lake | 12 | 0 | 1 | 11 | 8% |
| any | 37 | 5 | 2 | 30 | 18% |
| amphitheater | 10 | 1 | 1 | 8 | 20% |
| RV pad | 12 | 1 | 2 | 9 | 25% |
| tent site | 35 | 5 | 5 | 25 | 28% |
| lookout | 7 | 0 | 2 | 5 | 28% |
| wild | 45 | 13 | 3 | 29 | 35% |
| garage | 8 | 2 | 1 | 5 | 37% |
| ranger station | 13 | 2 | 3 | 8 | 38% |
| yard | 12 | 3 | 2 | 7 | 41% |
| porch | 8 | 3 | 1 | 4 | 50% |
| road | 47 | 24 | 2 | 21 | 55% |
| workshop | 10 | 4 | 2 | 4 | 60% |
| cellar | 8 | 4 | 1 | 3 | 62% |
| bathhouse | 7 | 3 | 2 | 2 | 71% |
| bathroom | 4 | 2 | 1 | 1 | 75% |
| laundry | 5 | 4 | 0 | 1 | 80% |
| living room | 8 | 7 | 0 | 1 | 87% |
| bedroom | 9 | 7 | 1 | 1 | 88% |
| ship | 40 | 40 | 0 | 0 | 100% |
| kitchen | 5 | 5 | 0 | 0 | 100% |

</details>

<details><summary>Suburb</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| any | 81 | 6 | 7 | 68 | 16% |
| yard | 61 | 6 | 7 | 48 | 21% |
| garage | 39 | 7 | 5 | 27 | 30% |
| workshop | 16 | 4 | 1 | 11 | 31% |
| garden | 11 | 0 | 4 | 7 | 36% |
| bathroom | 27 | 9 | 2 | 16 | 40% |
| laundry | 10 | 4 | 0 | 6 | 40% |
| house exterior | 31 | 5 | 9 | 17 | 45% |
| office | 20 | 9 | 0 | 11 | 45% |
| cellar | 39 | 11 | 7 | 21 | 46% |
| attic | 21 | 5 | 5 | 11 | 47% |
| kids room | 33 | 10 | 6 | 17 | 48% |
| wild | 22 | 11 | 0 | 11 | 50% |
| street | 22 | 5 | 6 | 11 | 50% |
| living room | 67 | 29 | 8 | 30 | 55% |
| porch | 41 | 19 | 4 | 18 | 56% |
| bedroom | 36 | 16 | 5 | 15 | 58% |
| kitchen | 65 | 32 | 7 | 26 | 60% |
| road | 41 | 25 | 1 | 15 | 63% |
| hall | 19 | 10 | 3 | 6 | 68% |
| interior extras | 16 | 1 | 10 | 5 | 68% |
| dining room | 19 | 14 | 2 | 3 | 84% |
| ship | 38 | 38 | 0 | 0 | 100% |

</details>

<details><summary>Laboratory</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| any | 36 | 4 | 1 | 31 | 13% |
| containment | 17 | 1 | 2 | 14 | 17% |
| security | 13 | 2 | 1 | 10 | 23% |
| wild | 4 | 1 | 0 | 3 | 25% |
| lab floor | 41 | 5 | 6 | 30 | 26% |
| cellar | 7 | 3 | 0 | 4 | 42% |
| support | 16 | 5 | 3 | 8 | 50% |
| office | 25 | 13 | 1 | 11 | 56% |
| chemical storage | 7 | 0 | 4 | 3 | 57% |
| porch | 4 | 2 | 1 | 1 | 75% |
| yard | 4 | 3 | 0 | 1 | 75% |
| road | 13 | 10 | 0 | 3 | 76% |
| workshop | 5 | 3 | 1 | 1 | 80% |
| ship | 39 | 39 | 0 | 0 | 100% |
| living room | 9 | 9 | 0 | 0 | 100% |
| bedroom | 5 | 5 | 0 | 0 | 100% |
| garage | 4 | 4 | 0 | 0 | 100% |

</details>

<details><summary>Military base and Area 51</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| containment | 5 | 0 | 0 | 5 | 0% |
| any | 38 | 5 | 0 | 33 | 13% |
| helipad and airfield | 7 | 0 | 1 | 6 | 14% |
| security | 13 | 2 | 1 | 10 | 23% |
| warehouse | 4 | 0 | 1 | 3 | 25% |
| perimeter | 18 | 3 | 2 | 13 | 27% |
| hangar | 16 | 0 | 5 | 11 | 31% |
| workshop | 17 | 4 | 2 | 11 | 35% |
| motor pool | 11 | 1 | 3 | 7 | 36% |
| wild | 12 | 4 | 1 | 7 | 41% |
| bunker | 14 | 3 | 3 | 8 | 42% |
| cellar | 13 | 6 | 1 | 6 | 53% |
| office | 23 | 13 | 1 | 9 | 60% |
| yard | 5 | 3 | 0 | 2 | 60% |
| road | 25 | 15 | 1 | 9 | 64% |
| garage | 10 | 5 | 2 | 3 | 70% |
| barracks | 14 | 2 | 8 | 4 | 71% |
| command | 19 | 6 | 8 | 5 | 73% |
| porch | 4 | 2 | 1 | 1 | 75% |
| bedroom | 7 | 5 | 1 | 1 | 85% |
| ship | 46 | 46 | 0 | 0 | 100% |
| living room | 6 | 6 | 0 | 0 | 100% |

</details>

<details><summary>Town (main street, diner, gas station, motel, sheriff, hospital, church)</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| any | 54 | 6 | 1 | 47 | 12% |
| gas station and truck stop | 18 | 0 | 3 | 15 | 16% |
| security | 4 | 1 | 0 | 3 | 25% |
| hospital | 20 | 3 | 4 | 13 | 35% |
| main street | 38 | 8 | 8 | 22 | 42% |
| bathroom | 23 | 9 | 1 | 13 | 43% |
| diner | 18 | 6 | 2 | 10 | 44% |
| road | 56 | 26 | 1 | 29 | 48% |
| laundry | 10 | 4 | 1 | 5 | 50% |
| wild | 10 | 5 | 0 | 5 | 50% |
| church | 4 | 1 | 1 | 2 | 50% |
| office | 33 | 16 | 2 | 15 | 54% |
| cellar | 14 | 9 | 0 | 5 | 64% |
| living room | 38 | 23 | 2 | 13 | 65% |
| workshop | 6 | 2 | 2 | 2 | 66% |
| motel | 14 | 4 | 6 | 4 | 71% |
| porch | 30 | 18 | 4 | 8 | 73% |
| bedroom | 23 | 13 | 4 | 6 | 73% |
| sheriff's office | 15 | 4 | 7 | 4 | 73% |
| kitchen | 35 | 25 | 2 | 8 | 77% |
| garage | 6 | 4 | 1 | 1 | 83% |
| yard | 8 | 5 | 2 | 1 | 87% |
| ship | 38 | 38 | 0 | 0 | 100% |
| hall | 10 | 9 | 1 | 0 | 100% |
| dining room | 7 | 7 | 0 | 0 | 100% |

</details>

<details><summary>Industrial (warehouse, hangar, scrapyard)</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| main street | 4 | 0 | 0 | 4 | 0% |
| any | 33 | 5 | 0 | 28 | 15% |
| hangar | 25 | 0 | 4 | 21 | 16% |
| workshop | 30 | 4 | 3 | 23 | 23% |
| warehouse | 30 | 2 | 7 | 21 | 30% |
| scrapyard | 18 | 1 | 5 | 12 | 33% |
| garage | 15 | 5 | 2 | 8 | 46% |
| wild | 8 | 4 | 0 | 4 | 50% |
| chemical storage | 4 | 0 | 2 | 2 | 50% |
| cellar | 21 | 9 | 3 | 9 | 57% |
| road | 34 | 20 | 2 | 12 | 64% |
| office | 19 | 12 | 1 | 6 | 68% |
| porch | 4 | 2 | 1 | 1 | 75% |
| yard | 4 | 3 | 0 | 1 | 75% |
| bedroom | 6 | 4 | 1 | 1 | 83% |
| ship | 38 | 38 | 0 | 0 | 100% |
| living room | 6 | 6 | 0 | 0 | 100% |
| laundry | 4 | 3 | 1 | 0 | 100% |

</details>

<details><summary>Forest cabin</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| any | 67 | 7 | 4 | 56 | 16% |
| garage | 9 | 2 | 1 | 6 | 33% |
| wild | 38 | 12 | 3 | 23 | 39% |
| cabin | 33 | 6 | 7 | 20 | 39% |
| bathroom | 27 | 9 | 2 | 16 | 40% |
| laundry | 10 | 4 | 0 | 6 | 40% |
| yard | 17 | 4 | 3 | 10 | 41% |
| attic | 14 | 4 | 3 | 7 | 50% |
| cellar | 37 | 13 | 6 | 18 | 51% |
| workshop | 19 | 8 | 2 | 9 | 52% |
| road | 23 | 14 | 0 | 9 | 60% |
| office | 15 | 9 | 0 | 6 | 60% |
| garden | 5 | 0 | 3 | 2 | 60% |
| living room | 55 | 31 | 3 | 21 | 61% |
| porch | 32 | 18 | 2 | 12 | 62% |
| kitchen | 63 | 35 | 6 | 22 | 65% |
| kids room | 22 | 10 | 5 | 7 | 68% |
| bedroom | 28 | 16 | 4 | 8 | 71% |
| hall | 13 | 9 | 1 | 3 | 76% |
| dining room | 16 | 14 | 0 | 2 | 87% |
| ship | 38 | 38 | 0 | 0 | 100% |

</details>

<details><summary>Leisure (drive-in, fairground, cemetery)</summary>

| room or area | catalogued | have | partial | missing | share built |
|---|---|---|---|---|---|
| any | 27 | 4 | 0 | 23 | 14% |
| wild | 4 | 1 | 0 | 3 | 25% |
| yard | 10 | 3 | 0 | 7 | 30% |
| drive-in | 13 | 1 | 4 | 8 | 38% |
| fairground | 23 | 3 | 6 | 14 | 39% |
| cemetery | 16 | 3 | 4 | 9 | 43% |
| cellar | 6 | 3 | 0 | 3 | 50% |
| church | 4 | 1 | 1 | 2 | 50% |
| road | 20 | 12 | 0 | 8 | 60% |
| porch | 5 | 2 | 1 | 2 | 60% |
| workshop | 4 | 2 | 1 | 1 | 75% |
| ship | 38 | 38 | 0 | 0 | 100% |
| living room | 5 | 5 | 0 | 0 | 100% |
| bedroom | 4 | 4 | 0 | 0 | 100% |

</details>

## Next 50: seven PR-sized batches

Picked for the most **variety and stealth value per unit of effort**, using the ideas already written in the open issues (#265 swing sets, jungle gyms,
clotheslines, bicycles, robot vacuum and devices; #266 trees and car types; #267 oddities; #270 storage racks and tubs; #156 the detail pass). Each batch
is 6 to 10 props, small enough for one PR with before and after pictures, and names the locations it serves. Effort assumes the existing `props_lib.py`
builder and the faceted style (a few hundred triangles each), plus a `props` entry in `art/data/interactions.json` where something opens, glows or
sounds. Every prop in these lists is `missing` or `partial` today.

### Batch 1: yard play and the clothesline (7) — serves farm, suburb, trailer park; leisure for the playground

Why first: the owner asked for exactly these (#265), they are big silhouettes that read in the dark, and sheets on a line are a sight-blocker, a rustle
and a hiding place all in one object.

1. Swing set (A-frame, 1 to 3 swings) (`PC-SH-513`, missing): random parts (which swings, chains, a missing seat), creaks and moves in the wind; the most requested yard prop.
2. Plastic play centre / jungle gym (`PC-SH-516`, missing): a kid-height hiding spot for a small alien; a large primary-colour shape.
3. Sandbox with toys (`PC-SH-521`, missing): cheap, flat, and a story prop (a half-built castle).
4. Trampoline (`PC-SH-522`, missing): a loud boing if bumped; the net is cover.
5. Tire swing on a branch (`PC-SH-515`, missing): the landmark oak's (#266) hook; swings when the wind driver blows.
6. Clothesline between poles (`PC-SH-527`, missing): cover and a rustle; random clothes or none (#265).
7. Laundry hung on the line (shirts, sheets, socks, overalls) (`PC-SH-529`, partial): the cheap variation that makes every clothesline different; the hanger clothes already exist.

### Batch 2: bicycles and things on wheels (6) — serves farm, suburb, trailer park, campground

Why: the owner named bicycle types (#265); they are leaned, lying or hung, so each placement tells a different story, and a thrown bike is a noise.

1. Bicycle (kid's) (`PC-SH-404`, missing): on its side in the grass, a trip hazard and a tell that children live here (#156).
2. Bicycle (adult road) (`PC-SH-402`, missing): leaning on a wall, with a kickstand pose.
3. Bicycle (mountain) (`PC-SH-403`, missing): a second adult silhouette for the garage and the cabin.
4. Bicycle (BMX) (`PC-SH-405`, missing): a teen's; stands on the drive.
5. Tricycle (`PC-SH-406`, missing): a toddler's, a small comic noise when kicked.
6. Skateboard and scooter (`PC-SH-407`, missing): rolling noise as a cheap distraction when pushed.

### Batch 3: storage racks and tubs (8) — serves every location with a cellar, garage, barn, workshop, warehouse or lab

Why: #270 is the container for the randomizer, the hidden oddities and the objective sites, and the cellar, barn and workshop are empty without it.

1. Wooden shelf unit (3 to 5 shelves) (`PC-SH-320`, partial): free-standing, tier slots for jars, tins and boxes (`Slot_` empties).
2. Metal wire or bolted steel rack (`PC-SH-321`, missing): the cellar and garage staple; it rattles; cover with gaps.
3. Plastic storage tub (tote) (`PC-SH-324`, missing): colours and mixed lids, stackable, carryable, openable (#270's headline).
4. Cardboard box (taped) (`PC-SH-326`, missing): the cheapest prop in the book, and a Mimic disguise.
5. Milk crate (`PC-SH-329`, missing): stackable cover and a hiding ledge.
6. Pegboard with hooks (`PC-SH-322`, missing): workshop and garage wall, tools outlined.
7. Shoe rack (`PC-SH-182`, missing): hall and mudroom dressing, a place for boots and a spot to hide a small thing.
8. Spice rack (`PC-SH-034`, missing): kitchen wall dressing that a pool can fill with jars.

### Batch 4: high-tech devices (8) — serves suburb, town, laboratory, trailer park; sets up the tech level

Why: #265's second half. A lit screen is a lit window in a dark room (it counts in `LightLevel`), a blinking LED is a possess or jam target, and `tech_tag: high` is how the seed thins devices out on a low-tech farm.

1. Robot vacuum (`PC-SH-794`, missing): the first moving prop; a slow NavMesh route, a "strange" noise source, possessable.
2. Game console (`PC-SH-098`, missing): a power LED and a TV: a living-room glow and a distraction.
3. Tablet (`PC-SH-273`, missing): a bright rectangle on a table, a story device (the kid's, the dad's).
4. Wi-Fi router and modem (`PC-SH-135`, missing): blinking LEDs; a jam target that a high-tech house has in every other room.
5. Smoke detector (`PC-SH-134`, missing): a chirp and a blink on the ceiling of every room; a noise when its battery is low.
6. Baby monitor (`PC-SH-143`, missing): a listening node that makes the nursery hostile.
7. Printer / scanner (`PC-SH-274`, missing): whirr and a light; an office and a lab staple.
8. Smart speaker (`PC-SB-005`, partial): partly there (the Modern radio): add its glow, `possess` and the "it listens" rule.

### Batch 5: the noise and distraction kit (8) — serves every home, the motel and the cabin

Why: games make their best stealth moments from ordinary objects that ring, chime or rattle (see the last section). These are cheap, each is a single light or sound emitter, and they give `NoiseSystem` and the Energy Being more to act on.

1. Bedside alarm clock (`PC-SH-176`, missing): an alarm set for a time, or thrown; a red glow at night.
2. Doorbell (`PC-SH-479`, missing): a ding that calls a human to the door.
3. Cordless phone and base (`PC-SH-139`, missing): a ringing phone lures a human; a Hello Neighbor classic.
4. Wind chimes (`PC-SH-483`, missing): a chime in the wind and a cue for how hard it blows.
5. Bug zapper (`PC-SH-484`, missing): a blue light and a crackle on the porch; a lit area that is not a lamp.
6. Boom box / portable stereo (`PC-SH-801`, missing): a lure and a cover noise.
7. Squeaky toy (`PC-SH-218`, missing): a planted distraction for a thrown or dropped item.
8. Dinner bell on the porch (`PC-FA-172`, missing): a bell the farmer rings; a clang you can ring from a distance.

### Batch 6: the first hidden oddities (7) — serves farm, trailer park, suburb, cabin and any house

Why: #267 asks for comic items in drawers and under beds; these seven are cheap (a few boxes and a cylinder each), non-explicit, and set up the container, drawer and find-counter work before more items come.

1. Locked diary (`PC-SH-819`, missing): a key and a story hint.
2. Wig and fake moustache (`PC-SH-818`, missing): the retired actor's secret.
3. Stack of love letters (`PC-SH-817`, missing): a clue and a smile.
4. Whoopee cushion (`PC-SH-219`, missing): a thrown or sat-on distraction.
5. Bag of cash in a flour tin (`PC-SH-823`, missing): an objective-style find in a kitchen cupboard.
6. Tinfoil hat (`PC-SH-788`, missing): the paranoid farmer's tell; the window pane already exists.
7. UFO sighting log (hand drawn) (`PC-SH-835`, missing): the farmer is paranoid (a faster reaction to noises).

### Batch 7: trees and vehicles (6) — serves farm, suburb, campground, town

Why: #266. One landmark tree per map changes every mission's look and cover, and the car types follow the tech level.

1. Willow tree (`PC-SH-666`, missing): a curtain of cover by the creek; sight-blocking at head height.
2. Maple tree (`PC-SH-667`, missing): a second large broadleaf for the suburb and the tree line.
3. Apple tree (`PC-SH-670`, missing): the orchard (#262) and fruit underfoot.
4. Classic 1950s pickup (`PC-SH-601`, missing): a loud classic with a key and a creaky door; the low-tech vehicle.
5. Futuristic electric car (`PC-SH-605`, missing): quiet, a charge port, possessable; the high-tech vehicle (an original design, no brand).
6. Electric-car charger / wall box (`PC-SH-606`, missing): a charge LED and a cable that the tech level can add or remove.

**After the 50**, in the order the gaps above suggest: the barn set (stall, gate, hay pulley, saddle, feed bin, hand pump, chicken feeder), the crop
rows (wheat, sunflower, pumpkin vines, orchard rows: #262), the garage set (lawn mower, compressor, jack, tyres, paint), then the other locations'
must-haves below, starting with the trailer park and the campground (the next maps in the campaign order).

## Must-have 30 per location

What a location needs before it looks like itself, from its design doc and the research. The status is the repo's today. Items that fit several
locations repeat; the shared ones are one row in the CSV.

### Farm (`docs/levels/farmstead.md`)

1. Cow stall (half-door, kick board, feed slot) (`PC-FA-028`, missing)
2. Stall gate and latch (`PC-FA-029`, missing)
3. Hay pulley, rope and hook (`PC-FA-043`, missing)
4. Saddle on a rack (`PC-FA-048`, missing)
5. Hay rack (`PC-FA-032`, missing)
6. Feed bin (wooden or metal) (`PC-FA-037`, missing)
7. Hand pump (`PC-FA-104`, missing)
8. Chicken feeder (hanging) (`PC-FA-086`, missing)
9. Egg basket (`PC-FA-088`, missing)
10. Burn barrel (`PC-FA-113`, partial)
11. Swing set (A-frame, 1 to 3 swings) (`PC-SH-513`, missing)
12. Plastic play centre / jungle gym (`PC-SH-516`, missing)
13. Clothesline between poles (`PC-SH-527`, missing)
14. Laundry hung on the line (shirts, sheets, socks, overalls) (`PC-SH-529`, partial)
15. Bicycle (kid's) (`PC-SH-404`, missing)
16. Bicycle (adult road) (`PC-SH-402`, missing)
17. Tire swing on a branch (`PC-SH-515`, missing)
18. Wheat / hay field (`PC-FA-135`, partial)
19. Orchard rows (apple trees) (`PC-FA-139`, missing)
20. Pumpkin patch with vines (`PC-FA-138`, partial)
21. Round baler (`PC-FA-151`, missing)
22. Combine harvester (`PC-FA-154`, missing)
23. Willow tree (`PC-SH-666`, missing)
24. Classic 1950s pickup (`PC-SH-601`, missing)
25. Wooden shelf unit (3 to 5 shelves) (`PC-SH-320`, partial)
26. Plastic storage tub (tote) (`PC-SH-324`, missing)
27. Locked diary (`PC-SH-819`, missing)
28. UFO sighting log (hand drawn) (`PC-SH-835`, missing)
29. Bedside alarm clock (`PC-SH-176`, missing)
30. Squeaky floorboard (`PC-SH-852`, missing)

### Trailer park (Cedar Flats, `docs/levels/trailer-park.md`)

1. Single-wide mobile home (4.3 x 16.5 m) (`PC-TP-003`, have)
2. Double-wide mobile home (7.3 x 16.5 m) (`PC-TP-004`, partial)
3. Skirting panels with a crawl-space hatch (`PC-TP-006`, partial)
4. Concrete-block steps / wooden deck (`PC-TP-009`, partial)
5. Aluminium storm door (`PC-TP-010`, missing)
6. Narrow hall (1.2 m) with doors (`PC-TP-018`, missing)
7. Laminate kitchenette (`PC-TP-016`, partial)
8. Living room recliner and TV on (`PC-TP-022`, partial)
9. Lawn chairs (webbed) in front (`PC-TP-029`, missing)
10. Charcoal grill and propane tank (`PC-TP-030`, missing)
11. Gnome-filled garden (`PC-TP-032`, missing)
12. Car on cinder blocks (`PC-TP-035`, partial)
13. Dog run with chain (`PC-TP-038`, missing)
14. Pig pen (`PC-TP-039`, missing)
15. Clothesline between poles (`PC-SH-527`, missing)
16. Satellite dish on a pole (`PC-TP-044`, missing)
17. Mailbox bank (cluster) (`PC-SH-494`, partial)
18. Power pedestal (30/50 amp) (`PC-SH-879`, missing)
19. Travel trailer (park model) (`PC-TP-048`, missing)
20. RV generator (`PC-SH-885`, partial)
21. Park phone (`PC-TP-053`, have)
22. Security camera monitors (`PC-TP-054`, partial)
23. Gate arm and keypad (`PC-TP-058`, missing)
24. Swimming pool (6 x 12 m) with underwater light (`PC-TP-069`, missing)
25. Coin-op washer and dryer bank (`PC-SH-261`, partial)
26. Swing set (A-frame, 1 to 3 swings) (`PC-SH-513`, missing)
27. Park transformer (pad-mount) (`PC-TP-089`, missing)
28. Parked car with alarm (`PC-TP-094`, partial)
29. Porch motion-sensor light (`PC-SH-481`, missing)
30. Door chime (`PC-TP-027`, missing)

### Campground (Spruce Lake, `docs/levels/campground.md`)

1. Dome tent (`PC-CG-001`, missing)
2. Cabin tent (family, 6 person) (`PC-CG-002`, missing)
3. Rain fly and guy-lines (`PC-CG-004`, missing)
4. Camp chair (folding) (`PC-CG-007`, missing)
5. Folding camp table (`PC-SH-887`, missing)
6. Camp stove (two burner) (`PC-CG-009`, missing)
7. Camp lantern (propane or LED) (`PC-CG-010`, partial)
8. Headlamp (`PC-CG-011`, missing)
9. Bear-proof food locker (bear box) (`PC-CG-016`, missing)
10. Bear-proof dumpster (`PC-CG-017`, partial)
11. Fire ring with grate (`PC-CG-018`, missing)
12. Campfire (burning) (`PC-CG-019`, missing)
13. Firewood bundle and kindling (`PC-CG-020`, partial)
14. Hammock between two trees (`PC-SH-538`, missing)
15. Picnic table with benches (`PC-SH-534`, missing)
16. Sleeping bag (`PC-SH-193`, missing)
17. Canoe (`PC-SH-616`, missing)
18. Lake dock (`PC-SH-685`, missing)
19. Boat ramp (6 x 15 m) (`PC-CG-061`, missing)
20. Lake with shallows (wadeable 1.2 m) (`PC-CG-058`, missing)
21. Ranger cabin (9 x 9 m) (`PC-CG-037`, missing)
22. Ranger truck (with spotlight) (`PC-CG-038`, partial)
23. Ranger desk and radio (`PC-CG-039`, partial)
24. Bathhouse (6 x 10 m) (`PC-CG-050`, missing)
25. Campfire amphitheater (60 seats) (`PC-CG-072`, missing)
26. Fire lookout tower (15 m, cab 4 x 4 m) (`PC-CG-082`, missing)
27. Trail cameras on game trails (`PC-CG-092`, missing)
28. Pine forest (700 trees) (`PC-CG-097`, have)
29. Black bear at the dumpster (`PC-CG-096`, have)
30. Camp host RV (`PC-CG-042`, missing)

### Suburb

1. Two-storey suburban house (`PC-SB-039`, partial)
2. Attached garage (single or double) (`PC-SB-040`, have)
3. Front lawn (mown) (`PC-SB-041`, partial)
4. Driveway (concrete) (`PC-SB-044`, partial)
5. Garage door with keypad (`PC-SB-045`, partial)
6. Backyard deck with railing (`PC-SB-059`, missing)
7. Patio with an umbrella (`PC-SB-060`, missing)
8. Pool (inground) with fence (`PC-SB-064`, missing)
9. Air-conditioner condenser (`PC-SB-054`, missing)
10. Neighbourhood watch sign (`PC-SB-051`, missing)
11. Seasonal lights and inflatables (`PC-SB-048`, missing)
12. Cul-de-sac bulb (`PC-SB-086`, partial)
13. Suburban street with parked cars (`PC-SB-087`, partial)
14. Garbage and recycling bins at the curb (`PC-SB-092`, partial)
15. Community mailbox cluster (`PC-SB-091`, partial)
16. Neighbourhood park (`PC-SB-100`, missing)
17. Basketball hoop on a pole (`PC-SH-560`, missing)
18. Swing set (A-frame, 1 to 3 swings) (`PC-SH-513`, missing)
19. Trampoline (`PC-SH-522`, missing)
20. Robot vacuum (`PC-SH-794`, missing)
21. Smart doorbell camera (`PC-SH-480`, missing)
22. Smart home hub (`PC-SB-084`, missing)
23. Alarm keypad by the door (`PC-SB-085`, missing)
24. Home office with two monitors (`PC-SB-076`, partial)
25. Nursery (crib, mobile, monitor) (`PC-SB-077`, partial)
26. Electric car in a driveway (`PC-SB-097`, missing)
27. Delivery van (`PC-SB-094`, have)
28. Lawn mower (push) (`PC-SH-395`, missing)
29. Bicycle (kid's) (`PC-SH-404`, missing)
30. Hose bib and sprinkler timer (`PC-SB-053`, missing)

### Laboratory (research station, `docs/levels/map-concepts.md`)

1. Lab bench with sink and gas taps (`PC-LB-001`, partial)
2. Microscope (`PC-LB-002`, have)
3. Fume hood (`PC-LB-003`, missing)
4. Biosafety cabinet (`PC-LB-004`, missing)
5. Centrifuge (`PC-LB-005`, missing)
6. Incubator (`PC-LB-006`, missing)
7. Autoclave (`PC-LB-007`, missing)
8. Ultra-low freezer (-80 C) (`PC-LB-008`, missing)
9. Laboratory refrigerator (`PC-LB-009`, partial)
10. Glove box (isolator) (`PC-LB-010`, missing)
11. Lab computer workstation (`PC-LB-016`, partial)
12. Server rack (`PC-LB-017`, have)
13. Glassware (beakers, flasks, test tubes) (`PC-LB-018`, missing)
14. Gas cylinder rack (`PC-LB-022`, missing)
15. Liquid nitrogen dewar (`PC-LB-023`, missing)
16. Specimen jars (shelf) (`PC-LB-025`, have)
17. Stasis / specimen tank (large) (`PC-LB-026`, partial)
18. Whiteboard with equations (`PC-LB-029`, have)
19. Eyewash and safety shower (`PC-LB-033`, missing)
20. Biohazard waste bin (`PC-LB-034`, missing)
21. Containment room (glass cell) (`PC-LB-041`, missing)
22. Observation window / two-way mirror (`PC-SH-907`, missing)
23. Alien artifact on a pedestal (`PC-LB-043`, missing)
24. Card reader / badge scanner (`PC-SH-913`, missing)
25. Security door (steel) (`PC-SH-916`, missing)
26. CCTV dome camera (`PC-SH-918`, have)
27. Airlock / decon chamber (`PC-LB-049`, missing)
28. Blast door (`PC-SH-909`, missing)
29. Emergency stop button (`PC-SH-910`, missing)
30. Rotating beacon light (`PC-SH-911`, missing)

### Military base and Area 51

1. Double chain-link fence with razor wire (`PC-MB-011`, missing)
2. Main gate and guard booth (`PC-MB-012`, missing)
3. Vehicle barrier arm (`PC-MB-013`, missing)
4. Concrete Jersey barrier (`PC-SH-934`, missing)
5. Sandbag wall (`PC-MB-016`, missing)
6. Guard tower with searchlight (`PC-MB-018`, missing)
7. Perimeter floodlight pole (`PC-MB-019`, partial)
8. Aircraft hangar (large) (`PC-SH-936`, missing)
9. Hangar sliding doors (huge) (`PC-SH-937`, partial)
10. Mock alien ship under a tarp (`PC-MB-027`, partial)
11. Bunk bed with a footlocker (`PC-MB-034`, partial)
12. Mess hall (long tables, steam trays) (`PC-MB-037`, missing)
13. Briefing room (tables, projector, map board) (`PC-MB-047`, partial)
14. Command centre consoles (`PC-MB-049`, partial)
15. Radar dish (large) (`PC-SH-947`, partial)
16. Radio mast and antenna array (`PC-MB-051`, partial)
17. Debrief room (table, mirror, recorders) (`PC-MB-052`, missing)
18. Interrogation room (table, two chairs, lamp) (`PC-MB-053`, partial)
19. Evidence lockers (`PC-MB-054`, have)
20. Motor pool lot (`PC-MB-064`, missing)
21. Military jeep (`PC-SH-595`, have)
22. Utility truck (canvas) (`PC-MB-066`, missing)
23. Helipad with lights (`PC-MB-073`, missing)
24. Control tower (`PC-MB-076`, missing)
25. Concrete bunker (door and vents) (`PC-MB-081`, missing)
26. Tunnel (concrete, pipes, cables) (`PC-MB-082`, missing)
27. Cold-storage vault (heavy door) (`PC-MB-083`, missing)
28. Shipping container (20 ft) (`PC-SH-976`, missing)
29. Light tower (mobile) (`PC-MB-071`, partial)
30. Card reader / badge scanner (`PC-SH-913`, missing)

### Town (main street, diner, gas station, motel, sheriff, hospital)

1. Brick shopfront (7 x 15 m) (`PC-TN-007`, partial)
2. Hardware store counter and shelves (`PC-TN-011`, missing)
3. Church (nave, pews, altar) (`PC-TN-021`, missing)
4. Church bell and rope (`PC-SH-956`, missing)
5. Bar counter and taps (`PC-TN-023`, have)
6. Grain elevator (`PC-TN-027`, partial)
7. Rail crossing signal (`PC-SH-959`, missing)
8. Main street road with parking (`PC-TN-029`, partial)
9. Diner building (chrome and neon) (`PC-TN-038`, have)
10. Diner counter with stools (`PC-TN-039`, have)
11. Diner booth (vinyl) (`PC-TN-040`, missing)
12. Jukebox (`PC-SH-962`, have)
13. Pie display case (`PC-TN-042`, missing)
14. Flat-top grill and fryer (`PC-TN-048`, missing)
15. Gas station canopy (18 x 8 m) (`PC-TN-055`, missing)
16. Fuel pump (island) (`PC-TN-056`, missing)
17. Convenience store (shelves, coolers) (`PC-TN-057`, missing)
18. Drink cooler (glass doors) (`PC-TN-058`, partial)
19. Payphone and satellite uplink (`PC-TN-067`, missing)
20. Motel row (rooms and numbers) (`PC-TN-073`, missing)
21. Vacancy sign (tall neon) (`PC-TN-083`, have)
22. Sheriff's office building (`PC-TN-087`, partial)
23. Holding cell (bars and bench) (`PC-TN-090`, missing)
24. Evidence locker room (`PC-TN-092`, partial)
25. Dispatcher console and radio (`PC-TN-089`, partial)
26. Hospital bed (adjustable) (`PC-TN-104`, partial)
27. Vital-signs monitor (`PC-SH-966`, missing)
28. Wheelchair (`PC-TN-106`, missing)
29. Privacy curtain on a track (`PC-TN-108`, missing)
30. ATM (`PC-TN-018`, missing)

### Industrial (warehouse, airport hangar, scrapyard)

1. Warehouse building (corrugated) (`PC-IN-003`, partial)
2. Pallet racking (steel, 4 tiers) (`PC-IN-004`, missing)
3. Pallet jack (`PC-SH-972`, missing)
4. Conveyor belt (`PC-IN-006`, missing)
5. Shrink-wrapped pallets (`PC-SH-973`, missing)
6. Stacked cardboard boxes (`PC-IN-007`, missing)
7. Roll-up dock doors (`PC-IN-008`, partial)
8. Loading dock with a truck (`PC-IN-010`, missing)
9. Metal drums (55 gal) (`PC-SH-974`, partial)
10. Shipping container (20 ft) (`PC-SH-976`, missing)
11. Forklift (`PC-SH-624`, missing)
12. Warehouse fan (big, ceiling) (`PC-IN-020`, missing)
13. High-bay light (`PC-IN-021`, missing)
14. Lockers (bank) (`PC-IN-024`, have)
15. Emergency exit door and sign (`PC-IN-026`, missing)
16. Small-aircraft hangar (T-hangar) (`PC-IN-030`, missing)
17. Single-engine airplane (original design) (`PC-IN-031`, missing)
18. Engine hoist (`PC-IN-035`, missing)
19. Rolling tool chest (`PC-IN-038`, partial)
20. Fuel truck (`PC-SH-948`, missing)
21. Hangar door (bifold) (`PC-IN-043`, missing)
22. Windsock (`PC-SH-935`, missing)
23. Scrapyard compound (chain-link, gate) (`PC-IN-047`, missing)
24. Stacked wrecked cars (three high) (`PC-IN-048`, partial)
25. Car crusher / baler (`PC-IN-049`, missing)
26. Magnet crane (25 m) (`PC-IN-050`, missing)
27. Weigh station and scale (`PC-IN-051`, missing)
28. Scrap metal piles (`PC-IN-052`, missing)
29. Tyre piles (`PC-SH-977`, missing)
30. Guard dog on a chain (`PC-IN-056`, partial)

### Forest cabin

1. Log cabin (single room and loft) (`PC-CB-001`, partial)
2. Cabin porch with a swing (`PC-CB-002`, missing)
3. Cabin stone chimney (`PC-CB-003`, partial)
4. Loft with a ladder (`PC-CB-004`, partial)
5. Wood stove (`PC-SH-108`, have)
6. Hand pump at the sink (`PC-CB-006`, missing)
7. Enamelware pots and cups (`PC-CB-007`, partial)
8. Cast-iron skillet on a hook (`PC-CB-008`, missing)
9. Quilt on the bunk (`PC-CB-009`, partial)
10. Bunk beds (`PC-CB-010`, have)
11. Bearskin rug (faux) (`PC-CB-011`, missing)
12. Antler chandelier (`PC-CB-012`, missing)
13. Kerosene lamp on the table (`PC-CB-018`, have)
14. Trail map on the wall (`PC-CB-019`, missing)
15. Guestbook on a stand (`PC-CB-020`, missing)
16. Woodpile under a lean-to (`PC-CB-021`, partial)
17. Axe and splitting block (`PC-CB-022`, have)
18. Outhouse (cabin) (`PC-CB-023`, have)
19. Root cellar (`PC-CB-024`, missing)
20. Solar panel and battery shed (`PC-CB-025`, missing)
21. Generator shed (`PC-CB-026`, partial)
22. Lake dock (`PC-SH-685`, missing)
23. Bear-resistant food box (`PC-CB-029`, missing)
24. Creaky floorboards (`PC-CB-030`, missing)
25. Taxidermy fish on a plaque (`PC-CB-031`, missing)
26. Fishing rods and a net (`PC-CB-015`, missing)
27. Snowshoes and skis on the wall (`PC-CB-016`, missing)
28. Rocking chair (`PC-SH-090`, have)
29. Fireplace (`PC-SH-105`, have)
30. Wood-burning sauna (`PC-CB-033`, missing)

### Leisure (drive-in, fairground, cemetery)

1. Movie screen (30 x 16 m) (`PC-LE-001`, missing)
2. Projection booth (on a rise) (`PC-LE-002`, missing)
3. Film projector (`PC-LE-003`, missing)
4. Snack bar (12 x 8 m) (`PC-LE-004`, missing)
5. Speaker post and speaker (car window) (`PC-LE-007`, missing)
6. Parked cars in fan-shaped rows (`PC-LE-008`, partial)
7. Ticket booth and gate (`PC-LE-009`, missing)
8. Marquee sign with letters (`PC-LE-010`, partial)
9. Ferris wheel (25 m) (`PC-LE-014`, missing)
10. Carousel (`PC-LE-015`, missing)
11. Bumper cars (`PC-LE-016`, missing)
12. Midway game booth (ring toss) (`PC-LE-018`, missing)
13. Duck shoot and can-knockdown booth (`PC-LE-019`, missing)
14. Prize plushies (giant) (`PC-LE-020`, partial)
15. Funhouse and hall of mirrors (`PC-LE-021`, missing)
16. Funhouse mirror (`PC-LE-022`, partial)
17. Cotton-candy and popcorn carts (`PC-LE-023`, missing)
18. Livestock barn (stalls and show rings) (`PC-LE-025`, partial)
19. Grandstand (60 x 12 m) (`PC-LE-027`, missing)
20. Sound board and speakers (`PC-LE-028`, missing)
21. Generator trucks (`PC-LE-029`, partial)
22. Carnie trailer (`PC-LE-030`, have)
23. String lights across the midway (`PC-LE-032`, missing)
24. Headstones (rows, 0.5 x 0.2 x 0.9 m) (`PC-LE-037`, missing)
25. Angel statue (`PC-LE-039`, missing)
26. Mausoleum / crypt (`PC-LE-040`, missing)
27. Chapel (8 x 14 m, steeple 16 m) (`PC-LE-041`, missing)
28. Bell rope (`PC-LE-042`, missing)
29. Grave lanterns and vigil candles (`PC-LE-044`, partial)
30. Wrought-iron fence and gate (`PC-LE-043`, missing)

## Items games commonly use as interactive or stealth props

A short synthesis from the game sources in [Sources](#sources) (search-result summaries; the pages themselves could not be fetched). Rows that name no
game are general stealth practice or this game's own design, not a sourced claim. It is what the catalogue's `interactive` and `stealth_role` columns are for.

| Role | What games use | In this catalogue |
|---|---|---|
| **Throwable distraction** (make a noise at a spot) | Hitman's coin, apple, radio and similar throwables (a coin or an apple makes one audible distraction; some items also lure when placed on the ground); Thief's noisemaker arrows; Metal Gear's empty magazine; Alien: Isolation's noisemaker, flare, flashbang and pipe bomb; Hello Neighbor's rocks, balls, bottles, boxes and lamps thrown at windows | Beer and soda cans, bottles, an apple, a ball, a squeaky toy, a bucket, a pan, a shoe, plates, a thermos, jars, a cushion (silent), a rubber duck; `carryable` plus `distraction` |
| **Placed or ringing distraction** (lures a person to a place) | A radio set to play (Hitman: Absolution), a cordless phone that makes the neighbour come (Hello Neighbor), a thrown device that keeps making noise (Alien: Isolation's noisemaker) | Alarm clock, doorbell, phones, radios, boom box, car alarm, dinner bell, church bell rope, kettle, wind chimes, a PA call, a jukebox |
| **Knock or tap** (a noise from the player's own body) | Metal Gear's wall knock (press a button while flat against a wall) | Needs no prop, but walls, doors, lockers and tin sheds are what it hits |
| **Hiding spot** | Closets and under beds (Hello Neighbor), Metal Gear's cardboard box (left in place as a decoy too) | Wardrobe, bed, bunk, toy box, dumpster, hay bale, bin, tent, phone booth, outhouse, shipping container; `hide` |
| **Cover and sight blockers** | General stealth practice, not tied to one source: tables, vehicles, tall plants | Sheets on a clothesline, hay bales, cars, willow curtain, sofas, racks; `cover` |
| **Disguise** | Metal Gear's box, posters that lure; a Mimic here | A speaker post, a crate, a mannequin, a cardboard box, a boulder; for the Mimic race |
| **Light that the AI counts** | Flares (holding an active flare raises detection like a lit room), campfires, screens | Lamps, TVs, laptops, router LEDs, porch and motion lights, fires, moonlit water, bug zapper, welding arc; `light` |
| **Noise masks** | Machines whose hum covers footsteps (a generator's hum masks sound within 15 m in the campground design) | Washer, dryer, dishwasher, fans, AC units, generators, running showers, flushing toilets, a vacuum; `noise` with a note "masks" |
| **Noise hazards the player triggers** | Creaky floors, loose gravel, glass, aluminium, stacks of cans | Squeaky floorboards and stair treads, broken glass, gravel paths, rattling racks, tarps; `noise` |
| **Carryables and objectives** | Goose Game's picnic set (radio, sandwich, apple, pumpkin, carrot, jam, thermos, basket) and its rake dragged across the garden | Ship parts, power cell, a photo, a hard drive, a diary, a key, a card, jars; `objective candidate` |
| **Items that change the player's own noise** | Goose Game's carried items that alter the honk (soap, a bottle, a harmonica, a bin lid) | A bell, a cowbell, a jar of coins: a comic carry penalty |
| **Machines the AI reacts to** | General practice: roaming robots, cameras and drones | Robot vacuum, drone, trail camera, security camera; `possessable` |

Design cautions the sources repeat, worth a line each in the issues that will use these props: the AI **learns** a trick used too often (Alien: Isolation's
creature stops falling for noisemakers and flares after repeated use, so give each lure a cooldown or a diminishing return); the AI notices the
**trajectory** as well as the landing point, so a thrown item aimed badly can lead people to the thrower; single-use items (Hitman's apple gives one distraction) are
easier to balance than reusable ones, which is a suggestion rather than a finding; and a distraction should have a **cost** (a thrown bottle is gone, a ringing phone wakes the household).

## Not catalogued, and decisions waiting

- **Adult-themed items** from #267: the owner decided on the issue (comment of 2026-10-22) that they may be **very tame**: a purple or pink novelty item
  or a gag ball, nothing explicit. The catalogue carries exactly those two rows, tagged `content: mature` and `missing`, under the owner's recorded
  rules: stylised and abstract (a faceted capsule or a ball on a strap, no anatomy, nothing realistic, never shown in use); a euphemism on the prompt
  and the results line ("a very personal item. You decide not to ask."), never a description; left out of every pool unless the host's
  **"Mature humour" setting** is on (its default is the owner's call); built in the last #267 slice; and **checked against Steam's content survey
  and the store rating before shipping**, so the setting can ship off by default or the items can be cut. Nothing else adult-themed is catalogued.
  The body-part gags are tagged `bodypart` so a pool can cap or drop them.
- **Real weapons** are not catalogued as props. The game is non-lethal (tranquilliser and net guns), so the sheriff's gun rack and a cabin's rack
  are decor only, and rows say so.
- **Brand names** (the issues' "Roomba" and "Tesla-like") became generic rows ("Robot vacuum", "Futuristic electric car (an original design)").
- **Animals and people** appear only where the prop catalogue needs them (the animals that exist, and ambient wildlife that lights, sounds and
  hazards depend on). The full lists are in `docs/assets/asset-list.md` sections 3 and 4.
- **Buildings and ground** appear as shells and kit pieces where they are the thing a prop stands in; terrain, sky and VFX are out of scope.

## The catalogue by location, room and area

Names only, grouped by `room_or_area` and by status (*have*, *partial*, *missing*); the CSVs hold every column. The shared set comes first, then each
location's own rows. A name that appears in the shared set fits two or more locations (the `locations` column says which).

### Shared set (`prop-catalogue.csv`): fits two or more locations

**any** (107). *have* (8): Backpack; CB radio; Flashlight (human); Hand-lettered sign; Handheld radio; Kid's drawing of a UFO; Lunchbox and thermos; Tripod floodlight · *partial* (10): "Believe" poster; Bluetooth speaker; Dog on a chain; Fish in the bathtub; Hidden bottle in the barn; Hidden stash of sweets; Pit trap / mud patch; Rotting food; Smart TV with a streaming stick; Very large cheese · *missing* (89): 3D printer; Alarm clock that rings at a set time; Bag of cash in a flour tin; Barbed wire; Baseball cap; Battery pack and power bank; Binoculars; Boom box / portable stereo; Broken glass; Burglar alarm panel; Camera (DSLR); Car alarm (siren); Car radio and dashboard; Charging cables; Classroom skeleton ("skeleton in the closet"); Clipboard and evidence bags; Command trailer / RV; Cowboy hat; Creaky door; Crop circle photograph; Drone (FBI / hobbyist); Dusty trophy; EMF meter; Electric scooter; Electronic key fob; Evidence flags and tent; Fake teeth in a glass; Floor safe or trapdoor; Garden gnome collection in a closet; Glass eye in a cup; Ham radio rig; Handcuffs and zip-ties; Hard hat; Hazmat suit; Hi-vis vest; Hidden floorboard stash; Homemade antenna; Hot stove or boiling pot; Hunting vest and boots; IP camera (indoor); Jar of "pickled something"; Jar of buttons; Lab coat; Lava lamp; Locked diary; Loose gate or shutter; MIB alien detector; Mannequin torso; Motion sensor; Net gun; Nettles and thorns; Night-vision goggles; Open well or manhole; Pet rock with a hat; Piled trash and bags; Police radio on the dash; Police scanner; Prosthetic leg by the bed; Robot vacuum; Rubber duck armada; Rubber or mannequin hand in a drawer; Shoebox of old photos; Singing fish plaque; Slippery wet floor; Smart thermostat; Solar lantern; Solar panels; Spilled marbles or tacks; Squeaking stair tread; Squeaky floorboard; Stack of love letters; Streaming webcam / podcasting setup; Sunglasses (the MIB's); Tangled cables drawer; Thermal camera; Tinfoil hat; Traffic roadblock; Trail camera; Tranquilliser rifle; Tripwire alarm / can on a string; UFO book collection; UFO sighting log (hand drawn); Unicycle; Walkie-talkie pair; Wasp nest; Weather radio; Wet paint; Wig and fake moustache; Wig on a stand

**road** (78). *have* (35): ATV; Ambulance; Crashed ship; Curb; Delivery van / mail truck; Dumpster; FBI SUV and van; Farm pickup truck; Flatbed trailer; Footprints (alien) decal; Gravel driveway; Man in Black sedan; Military jeep; Minivan; Motorcycle; Oil stain decal; Parking lines decal; Power line / service drop; Puddle decal; Road T-junction; Road curve; Road dirt (county road); Road section (asphalt, straight); SUV; Scorch decal and burn marks; Sedan (family car); Sheriff cruiser; Sidewalk; State police cruiser; Station wagon; Tow truck; Transformer pole; Trash can (street); Tyre tracks decal; Utility pole · *partial* (2): Rusty wreck / car on blocks; Street lamp (cobra head) · *missing* (41): Boat trailer with boat; Bridge; Bus stop shelter; Camper van (original design, no brand); Canoe; Class A motorhome; Class C motorhome; Classic 1950s pickup; Classic muscle car; Culvert and ditch; Electric pickup; Electric-car charger / wall box; Fifth-wheel trailer; Fire hydrant; Food truck; Forklift; Fuel tanker; Futuristic electric car; Garbage truck; Golf cart; Guard rail; Helicopter (FBI or military); Hitching post / bike rack; Hybrid compact car; Ice-cream truck; Mile marker; Newspaper vending box; Padmount transformer (green box); Pay phone; Pickup with a camper shell; Police tape; Railroad crossing sign and tracks; Rowboat / fishing boat; Sawhorse barricade; School bus; Semi truck and trailer; Speed bump; Stop sign and road signs; Traffic cones; Travel trailer / caravan; Vintage station wagon with wood sides

**living room** (77). *have* (35): Alien drawings and UFO clippings; Antler or deer trophy mount; Armchair / recliner; Bookcase; Books (stack); CRT television; Cactus in a pot; Ceiling lamp shade; Chandelier; Coffee table; Curtains; Cushion; Fireplace; Flat-screen television; Floor lamp; Hanging plant; Intercom; Landline phone; Light switch; Magazines and newspapers; Mail pile; Mobile phone; Open book; Poster; Potted plant; Radiator; Rocking chair; Rotary phone; Security camera; Side table / end table; Sofa; Throw blanket; Vase of flowers; Window air conditioner; Wood stove · *partial* (7): Firewood basket; Loveseat; Mantel clock; Recliner with footrest; TV stand / media console; Tin foil on the antenna; Wedding photo above the sofa · *missing* (35): Answering machine; Ashtray; Baby monitor; Candy dish; Ceiling fan; Ceramic figurines; Cordless phone and base; Dartboard; Fireplace screen; Fireplace tools and poker; Floor register / heater vent; Game console; Gamepad and headset; Guitar; Gun cabinet (non-lethal: tranq and nets only); Hunting trophy rifle rack; Knitting basket; Large floor plant (fern, ficus); Mounted fish or bass trophy; Needlepoint or embroidered sign; Ottoman / pouffe; Photo album; Piano; Piano stool; Pool table; Record player and records; Remote control; Sewing machine; Smoke detector; Space heater; Standing fan; VCR / DVD player; Wall thermostat; Wi-Fi router and modem; Window blinds

**kitchen** (67). *have* (35): Beer cans and bottles; Bottle of whiskey; Bread box; Bread loaf; Breakfast bar stool; Cake; Canned beans; Canned soup; Cereal box; Coffee maker; Cookie jar; Eggs (carton); Flour sack; Jam jar; Jar of pickles; Kettle; Kitchen counter with cabinets; Kitchen radio; Kitchen sink with tap; Kitchen trash can; Lunchbox; Microwave oven; Milk bottle; Mugs; Pie cooling; Plates and dishes; Pot; Refrigerator; Soda cans; Stove / oven; Thermos; Toaster; Wall calendar; Wall clock; Wine bottle · *partial* (6): Cutlery drawer; Fruit bowl; Pantry shelf unit; Pet food and water bowls; Wall landline phone; Window with curtains and sill items · *missing* (26): Blender; Cast-iron pot on the stove; Colander; Cutting board and knife; Dish rack with dishes; Dishwasher; Electric can opener; Frying pan / skillet; Glassware and tumblers; Kitchen scale; Knife block; Lazy Susan and napkin holder; Oven mitts and dish towels; Paper towel holder; Pet door / cat flap; Range hood and fan; Recycling bin; Rice cooker; Rolling pin; Salt and pepper shakers; Slow cooker; Spice rack; Stand mixer; Teapot; Toaster oven; Wooden spoon jar

**yard** (62). *have* (7): Cooler and beer cans; Dog house; Garden bench; Garden fence section; Garden gate; Wheelbarrow of weeds; Yard light (pole-mounted) · *partial* (8): Beware-of-dog sign; Garden shed; Hedge; Laundry hung on the line (shirts, sheets, socks, overalls); No-trespassing sign; Picket fence; Propane tank (20 lb); Rain barrel · *missing* (47): Above-ground pool; Adirondack chair; Barbecue tools; Basketball hoop on a pole; Bird feeder; Birdbath; Birdhouse; Chain-link fence; Charcoal barbecue grill; Clothes peg bag; Clothesline between poles; Cold frame and greenhouse; Compost bin; Dog chain and stake; Doghouse bowl; Fire pit / fire ring; Flag on a pole (US flag); Garden gnome; Garden hose coiled by the tap; Gas barbecue grill; Hammock between two trees; Inground pool with a light; Lawn mower left in the grass; Merry-go-round; Paddling pool; Patio chairs; Patio table with umbrella; Picnic table with benches; Pink flamingo and lawn ornaments; Plastic play centre / jungle gym; Pool noodle and toys; Pool skimmer and chemical shed; Privacy (wooden slat) fence; Rotary washing line; Sandbox with toys; Seesaw; Slide (stand-alone); Soccer goal; Sprinkler (oscillating); Swing set (A-frame, 1 to 3 swings); Swing set with slide and glider; Tire planter; Tire swing on a branch; Trampoline; Trellis and arbor; Wind spinner / pinwheel; Wooden playhouse or treehouse

**wild** (60). *have* (22): Black bear; Boulder; Bush; Cat; Chicken hen; Dead tree; Deer (doe, buck, fawn); Dog (farm, collie); Dog (guard, shepherd); Dog (stray); Fox; Kitten; Oak tree; Opossum; Other dog breeds (beagle, bulldog, husky, retriever); Pig; Pine tree; Raccoon; Skunk; Small yappy dog; Stump; Turkey · *partial* (3): Fallen log; Gravel path; Moss and lichen on rocks · *missing* (35): Anthill and burrow; Apple tree; Bats; Bees and wasps; Birch tree; Birds' nest; Branches and brush pile; Cedar and spruce; Coyote; Creek and shallows; Crows and ravens; Duck and goose; Ferns; Fireflies; Fish (pond or lake); Flagstone path; Footbridge; Frogs and crickets; Lake dock; Maple tree; Mice and rats; Moths and flies at the light; Mushrooms; Owl; Pear and cherry tree; Pond with reeds; Rabbit (wild and hutch); Reeds and cattails; Snakes and lizards; Songbirds and pigeons; Spider web with dew; Squirrel and chipmunk; Tall weeds and brush; Wildflowers; Willow tree

**workshop** (46). *have* (10): Firewood stack; Flashlight; Generator; Pitchfork; Power cell; Rake; Shovel; Stool; Wheelbarrow; Wood chopping block · *partial* (4): Fuel can and funnel; Lantern; Pallet; Stepladder · *missing* (32): Angle grinder; Axe and splitting maul; Battery tender and car battery; Bench grinder; Bench vise; Bricks and planks; Chainsaw; Cinder blocks; Come-along and chains; Cordless drill; Extension cord reel; Garden hose; Hammer; Hand saw; Hand truck / dolly; Hoe; Mallet and sledgehammer; Nuts and bolts jars; Paint shelf; Pliers, wrenches and screwdrivers; Pruning shears; Rope coil; Sawhorses; Scythe; Spade; Spare tyres; Sprinkler; Table saw; Tarp; Watering can; Welder and mask; Work light (clip-on)

**cellar** (45). *have* (15): Barrel; Basement stairs (cellar); Boiler; Broom; Bucket; Fire extinguisher; Floor drain; Jar shelf with jars; Jerry can; Mop bucket; Old TV (CRT); Suitcase; Trunk (steamer); Water heater; Wooden crate · *partial* (7): Canned goods shelf; Footlocker; Old sofa and discarded furniture; Pipes and valves; Wicker basket; Wooden shelf unit (3 to 5 shelves); Work lamp · *missing* (23): Ammo-style metal can; Artificial Christmas tree; Cardboard box (open flaps); Cardboard box (taped); Ceiling-hung storage rack; Chest freezer; Christmas decorations box; Cobwebs and dust; Dustpan and brush; Furnace and ducts; Hat box; Metal wire or bolted steel rack; Milk crate; Oil tank; Paint cans; Pegboard with hooks; Plastic storage tub (tote); Root-cellar potato and apple bins; Sheets draped over furniture; Shoebox-size plastic bin; Sump pump; Water pump and pressure tank; Wine rack

**porch** (44). *have* (20): Awning; Back door; Boarded window; Broken window pane; Cat on the porch rail; Chimney; Cooler by the chair; Front door; Gutters and downspout; Hanging flower basket; Mailbox on a post; Newspaper on the step; Porch bench; Porch rail; Porch rocking chair; Porch steps; Screen door; Shutters; Welcome mat; Window (with light spilling) · *partial* (4): Mailbox bank (cluster); Package on the porch; Porch light (wall lantern); Security light (flood) · *missing* (20): Ashtray stand / cigarette butts; Boot scraper; Bug zapper; Citronella candle; Door wreath; Doorbell; Fire escape or porch roof; Lawn chair (folding, webbed); Moths around the light; Patio heater; Porch motion-sensor light; Porch swing; Satellite dish; Smart doorbell camera; Solar path lights; String lights; TV antenna on the roof; Tiki torches; Weather vane; Wind chimes

**ship** (41). *have* (41): Abduction UFO; Bank terminal (green); Beacon; Black box; Cable tangle; Comms array; Console module; Containment pod; Egg-class ship; Engine coil; Escape pod; Freighter-class ship; Fuel canister; Holo-map table; Hull panel; Hull shards and debris; Landing leg; Launch terminal (red); Medical couch; Nav crystal; Pilot's helm and nav screen; Probe drone (alien); Radar post; Repair tool; Saucer-class crashed ship (shell); Scanner (alien); Scorched ground; Scout ship; Shield emitter; Ship bunk and mess table; Ship conduit / cable run; Ship control console; Ship crates and drums; Ship lockers; Ship sample rack; Ship tool rack; Specimen jars (cow, plant, little alien); Stasis pod; Thruster nozzle; Translator; Warp ring segment

**office** (37). *have* (16): Bookshelf of manuals; Bulletin board; Computer monitor; Desk (wood); Desk calendar; Desk lamp; Desk phone; Desktop computer tower; Filing cabinet; Keyboard and mouse; Laptop; Office chair; Office desk; Safe (office); Wall clock (office); Whiteboard · *partial* (2): Key cabinet; Office plant · *missing* (19): Clipboard; Copier; Fax machine; Headphones; Ledger / farm account books; Paper stack and folders; Power strip and extension cord; Printer / scanner; Rotary card file and address book; Shredder; Stapler, tape and pens; Tablet; Typewriter; UPS and battery backup; USB drive and hard drive; Wall map with red string; Wall safe behind a picture; Water cooler; Webcam and microphone

**garage** (35). *have* (7): Garage door (roll-up or sectional); Garbage cans (wheeled); Ladder (step or extension); Metal storage locker; Spare refrigerator; Toolbox; Workbench · *partial* (4): Camping gear (tent bag, cooler); Neon beer sign; Oil drum and oil cans; Tool chest (rolling) · *missing* (24): Air compressor; Basketball; Bicycle (BMX); Bicycle (adult road); Bicycle (kid's); Bicycle (mountain); Car battery and charger; Car jack and jack stands; Charcoal bag and propane; Fishing rods and tackle; Freezer in the garage; Garage shelving and bins; Garden hose and reel; Kayak or canoe on racks; Lawn mower (push); Paint cans and brushes; Recycling bin (blue); Ride-on mower; Shop vac; Skateboard and scooter; Snow blower and snow shovel; Tricycle; Tyre (loose) and rims; Wall-mounted tool rack

**bedroom** (34). *have* (16): Blanket; Boots and shoes; Bunk bed; Curtains (bedroom); Double bed; Dresser; Folded pants and towels; Full-length mirror; Hanging clothes (dress, jacket, shirt); Nightstand with drawer; Pillow; Safe (small); Scarf; Single bed; Trunk at the foot of the bed; Wardrobe · *partial* (5): Bedside lamp; Clothes hamper; Clothes on a chair; Cot / camp bed; Slippers · *missing* (13): Bed frame without mattress; Bedside alarm clock; Closet with sliding door; Gag ball (novelty); Jewelry box; Medicine on the nightstand; Night light; Shoe rack; Sleeping bag; Vanity table and stool; Very personal item (purple or pink novelty); Wall crucifix or framed saying; Window box fan

**bathroom** (28). *have* (9): Bathroom sink; Bathtub; First aid kit; Medicine cabinet; Mirror (bathroom); Shower stall; Toilet; Towel rail; Towels (folded and hung) · *partial* (3): Cabinet under the sink; Laundry hamper in the bathroom; Outhouse seat · *missing* (16): Bath mat; Bath towel hook; Bathrobe; Bathroom scale; Bathtub toys; Hair dryer; Night-time glow of the bathroom light; Plunger; Razor and shaving kit; Rubber duck; Shower curtain and rod; Soap and shampoo bottles; Toilet brush; Toilet paper holder and roll; Toothbrush and cup; Wall heater / exhaust fan

**kids room** (28). *have* (10): Building blocks; Child's bed; Cot / crib; Doll; Football; Kid's alien drawings; Kid's backpack; Teddy bear; Toy box; Toy truck · *partial* (5): Kid's desk and chair; Posters and stickers; School books and homework; Stuffed animal collection; Toy car track and cars · *missing* (13): Bean bag chair; Board games and puzzles; Crayons and colouring books; Dollhouse; Jigsaw puzzle on a table; Night light with stars projector; Playing cards; Rocking horse; Squeaky toy; Toy piano or xylophone; Toy robot (battery); Water guns and foam-dart blasters; Whoopee cushion

**attic** (22). *have* (5): Dormer lamp or bulb on a string; Dusty mirror; Old lamp and lampshades; Old luggage; Trunks and steamer chests · *partial* (5): Attic floor planks and joists; Attic window (round or gable); Baby crib and high chair (stored); Ceiling hatch and ladder (pull-down); Roof rafters and insulation · *missing* (12): Bats in the rafters; Boxes of records and tapes; Dress form / mannequin; Mouse droppings and nests; Old record player and 78s; Old toys and a rocking horse; Old trunk of costumes (clown suit); Old wedding dress on a dummy; Photo boxes and albums; Rolled rugs; Taxidermy squirrel; Ventriloquist dummy

**dining room** (18). *have* (14): Candlestick and candles; Centerpiece (vase of flowers); Dining chair; Dining table; Family photos on the sideboard; Kitchen chair; Mirror (wall); Oval rug; Round rug; Rug (room size); Runner rug; Table lamp; Wall frames and pictures; Wall shelf · *partial* (2): China cabinet with plates; Sideboard / buffet · *missing* (2): High chair; Tablecloth and runner

**hall** (18). *have* (10): Boots by the door; Breaker panel (modern); Coat hooks; Coat rack; Doormat; Fuse box; Hallway rug runner; Shoe bench; Stairs (runner and handrail); Umbrella stand · *partial* (3): Hall table; Landing window onto the porch roof; Mudroom bench and cubbies · *missing* (5): Attic access hatch and pull-down ladder; Dog bed; Grandfather clock; Key hooks and dish; Mailbox slot or mail table

**laundry** (16). *have* (5): Dryer; Ironing board; Laundry basket; Shower stalls (bathhouse); Washing machine · *partial* (1): Coin-op washer and dryer bank · *missing* (10): Clothes drying rack; Hand dryer; Hanging clothes line (indoor); Iron; Laundry cart; Laundry detergent and fabric softener; Laundry folding table; Lint trap and dryer hose; Sock odd one; Utility sink / laundry tub

**security** (13). *have* (2): CCTV dome camera; Guard's chair and thermos · *partial* (1): Security desk with monitor wall · *missing* (10): Biometric scanner; Card reader / badge scanner; Fire door (push bar); Key card on a lanyard; Keypad door lock; Metal detector arch; Security door (steel); Turnstile; Visitor badge and lanyard; X-ray bag scanner

**RV pad** (12). *have* (1): Cooler with ice · *partial* (2): Awning (RV, retractable); RV generator · *missing* (9): Fifth wheel with slide-out; Fire ring at the pad; Folding camp table; Leveling blocks and wheel chocks; Outdoor rug and patio mat; Power pedestal (30/50 amp); RV pad (4.5 x 14 m) with hookups; String lights on the awning; Water spigot and sewer cap

**garden** (12). *partial* (5): Flower bed (perennials); Fruit bush (berries); Herb pots; Rose bush; Vegetable garden bed · *missing* (7): Beehive; Garden stakes and twine; Potting bench; Raised bed (wood); Sunflowers; Terracotta pots; Tomato cage and stakes

**hangar** (10). *partial* (2): Hangar floor markings; Hangar sliding doors (huge) · *missing* (8): Aircraft hangar (large); Aircraft tug / tow tractor; Fire suppression foam cannon; Hangar bay lights (high-bay); Overhead gantry crane; Parts cages and bins; Rolling steps / maintenance stairs; Scaffold and work platforms

**main street** (7). *partial* (1): Church candles and votive rack · *missing* (6): Church bell and rope; Freight car (boxcar); Rail crossing signal; Railway tracks; Shopping cart; Steeple

**containment** (6). *missing* (6): Alarm panel; Blast door; Emergency stop button; Observation window / two-way mirror; Radiation hazard sign; Rotating beacon light

**chemical storage** (4). *partial* (2): Drum rack and drums; Flammable-liquids cabinet (yellow) · *missing* (2): Spill kit; Ventilated storage cage

**church** (4). *have* (1): Church doors (double) · *partial* (1): Vestry cupboard · *missing* (2): Altar; Hymn board and Bible rack

**warehouse** (4). *partial* (1): Metal drums (55 gal) · *missing* (3): Pallet jack; Shipping container (20 ft); Shrink-wrapped pallets

**clubhouse** (3). *missing* (3): Coffee urn; Ice machine; Trophy case

**hospital** (3). *missing* (3): Biohazard bin; IV stand with bag; Vital-signs monitor

**motor pool** (3). *missing* (3): Fuel truck; Jack stands and creepers; Tyre rack

**street** (3). *missing* (3): Dog waste station; Irrigation gate; Speed camera / radar sign

**support** (3). *have* (1): Backup generator · *missing* (2): Freight elevator; Loading dock door

**bunker** (2). *missing* (2): Hazard stripe markings; Pallets of supplies

**command** (2). *partial* (1): Radar dish (large) · *missing* (1): Briefing projector

**field** (2). *missing* (2): Deer stand / tree stand; Hunting blind

**maintenance yard** (2). *missing* (2): Gravel and sand piles; Pallets of pavers

**perimeter** (2). *missing* (2): Concrete Jersey barrier; Windsock

**scrapyard** (2). *partial* (1): Old appliance graveyard · *missing* (1): Tyre piles

**tent site** (2). *missing* (2): Camp guitar; Hatchet / axe

**diner** (1). *have* (1): Jukebox

**farmhouse** (1). *missing* (1): Work gloves

**helipad and airfield** (1). *missing* (1): Chocks and tie-downs

**lab floor** (1). *missing* (1): IV pole

**lookout** (1). *missing* (1): Weather station

**mobile home** (1). *have* (1): Window air-conditioning unit

**sheriff's office** (1). *missing* (1): Gun rack (non-lethal: tranq and net rifles)

### farm only (`props/farm.csv`)

**barn** (58). *have* (10): Barn bare bulb on a cord; Barn building (ten stalls, aisle, loft); Barn radio; Barn rear door; Barn sliding double doors (8 m); Cattle gate swing; Hay loft (floor at 5 m); Loft ladder (fixed); Manure fork and wheelbarrow; Rafters and trusses · *partial* (11): Barn floodlight above the big doors; Barn lantern (hung); Feed buckets and scoops; Feed trough / manger; Loft door and hay pulley; Loose hay (drift); Milk bucket rack and pails; Milking stand and stool; Paddock for horses; Pasture fence (wire and post); Wooden corral · *missing* (37): Barn cat bed; Barn fan; Barn owl perch on the ridge; Bridle and halter on a hook; Calf hutch (plastic igloo); Calf pen with nipple bucket; Cattle guard (grid); Cow brush (rotating); Cow stall (half-door, kick board, feed slot); Duck / goose house and pond; Electric fence charger; Electric fence tape and posts; Feed bin (wooden or metal); Goat pen and shed; Grain scoop; Grooming brush and hoof pick; Harness and collar (draft); Hay fork track / trolley; Hay pulley, rope and hook; Hay rack; Horse blanket; Manure pile and muck; Milk cooler tank; Mouse holes and nests; Pig sty with mud wallow; Round-bale feeder; Saddle on a rack; Saddle soap and tack tin; Salt lick block; Sheep shelter and pen; Stable (horse stalls); Stall gate and latch; Stanchion (cow head lock); Swallow nests in the eaves; Tack room (door and hooks); Veterinary kit (syringes, ear tags); Water tap with a hose bib

**field** (36). *have* (7): Corn stalk; Corn strips (4 m crossed cards); Crop circle (trace); Fence line with posts; Field gate; Round bales in the field; Scarecrow (field) · *partial* (6): Farm road gravel; Field edge hedgerow; Hay meadow / pasture grass; Pumpkin patch with vines; Soybean and potato rows; Wheat / hay field · *missing* (23): Boom sprayer; Combine harvester; Crater (impact); Disc harrow; Field cultivator; Front-end loader attachment; Grain cart and auger; Hay mower / conditioner; Hay rake / tedder; Irrigation pivot; Orchard rows (apple trees); Post-hole digger; Pump house; Rabbit hole and burrow; Round baler; Seed drill / planter; Square baler; Stone wall (field); Sunflower field; Tractor paths through the corn; Tractor-drawn plough; Trampled corn and broken stalks; Vineyard or hops on trellis

**yard** (33). *have* (13): Chopping block with axe; Farmhouse (two storeys, cellar); Gate lamp; Hay bale stack (field); Hay wagon / flatbed trailer; Outhouse; Shed; Silo; Water trough; Water well with a roof; Windmill with turning blades; Workshop building; Yard pole lamp · *partial* (5): Barnyard mud and puddles; Burn barrel; Farm sign and mailbox; Woodshed; Worn path (house to barn) · *missing* (15): Corn crib; Driveway culvert; Duck pond; Equipment lean-to / carport; Feed shed; Fuel tank on stand with pump; Grain bin; Hand pump; Hitching rail; Irrigation pipe and sprinkler; Livestock (stock) trailer; Manure spreader; Old machinery rusting; Tire pile; Water tank (stock tank, poly)

**farmhouse** (18). *have* (6): Farm boots and umbrella in the stand; Landline phone on the desk; Old rotary phone on the wall; Photograph on the desk; Preserved vegetables jars; Tinfoil-covered window · *partial* (4): Farmer's flannel shirt; Porch lamp with moths; Quilt on a rack; Wellington boots · *missing* (8): Butter churn; Cream separator; Dinner bell on the porch; Dog bed in the mudroom; Farm almanac; Farmer's overalls on a hook; Hanging cured ham; Straw hat

**coop** (15). *have* (2): Chicken coop with run; Egg crates / cartons · *partial* (4): Chicken wire panel; Nesting boxes; Roosts; Straw bedding · *missing* (9): Brooder box with chicks; Chicken feeder (hanging); Chicken waterer (founts); Coop door latch; Coop ladder; Egg basket; Feed bin for chickens; Heat lamp; Rooster weathervane

**garden** (8). *have* (1): Fallen apples · *partial* (4): Fruit crate; Orchard ladder; Pumpkin patch; Straw mulch · *missing* (3): Bean poles; Compost heap; Picking bin

**wild** (7). *have* (4): Cow; Goat; Horse; Sheep · *missing* (3): Donkey / llama; Poplar row (windbreak); Rooster

**workshop** (4). *have* (4): Feed sack; Hay bale (round); Hay bale (square); Milk can

**cellar** (2). *have* (1): Storm cellar doors · *missing* (1): Canning table and jars

**any** (1). *missing* (1): Electric fence wire

**hall** (1). *missing* (1): Wall phone nook

**road** (1). *have* (1): Tractor

### trailer-park only (`props/trailer-park.csv`)

**mobile home** (26). *have* (3): Cat on the window sill; Metal awning over the door; Single-wide mobile home (4.3 x 16.5 m) · *partial* (11): Concrete-block steps / wooden deck; Double-wide mobile home (7.3 x 16.5 m); Hall bath (2.4 x 1.8 m); Hitch and tongue jack; Laminate kitchenette; Lap siding in faded colour; Living room recliner and TV on; Roof vents and rooftop AC; Skirting panels with a crawl-space hatch; Small bedroom with built-in bunk; Water heater closet · *missing* (12): Aluminium storm door; Carport (aluminium); Cluttered kitchen table; Door chime; Fold-down dinette table; Narrow hall (1.2 m) with doors; Plastic window blinds; Tie-down straps and ground anchors; Vacant overgrown lot (pad); Wagon-wheel or ceramic wall decor; Wall-mounted furnace / floor heater; Wood-panel walls

**yard** (18). *have* (2): Backyard shed (metal); Trash cans in a row · *partial* (3): Car on cinder blocks; Doormat and porch light; Propane tank (100 lb) · *missing* (13): Boat on a trailer; Charcoal grill and propane tank; Chicken run; Dog run with chain; Fence (chain-link) between lots; Gnome-filled garden; Lawn chairs (webbed) in front; Lawn tractor with trailer; Pig pen; Pink flamingos and yard ornaments; Plastic kiddie pool; Satellite dish on a pole; Wind spinners and wind chimes

**office** (12). *have* (3): Open sign (neon); Park phone; Spine-road lamps · *partial* (2): Office counter and bell; Security camera monitors · *missing* (7): Brochure rack; Entrance sign; Gate arm and keypad; Lot number signs; Park office and manager's home; Rules sign board; Speed-limit signs

**pool** (8). *missing* (8): Depth signs and no-diving signs; Life ring and pole; Lounge chairs; Pool fence and gate with a latch; Pool ladder and rails; Pool towel rack; Swimming pool (6 x 12 m) with underwater light; Teens' phones and speakers

**street** (8). *have* (2): Parked cars (sedans and pickups); Tree strip (north) · *partial* (4): Hedge along the fence; Park street (6.5 m, one way); Parked car with alarm; Spine road · *missing* (2): Boats and campers parked on lots; Canal bank (concrete)

**clubhouse** (6). *have* (1): Vending machine · *partial* (1): Community kitchenette · *missing* (4): Bingo cage and cards; Clubhouse (14 x 10 m); Folding tables and stacking chairs; Piano (upright)

**maintenance yard** (5). *have* (2): Dumpsters (bank); Maintenance shed · *partial* (1): Utility trailer and mower · *missing* (2): Bulk propane tank; Park transformer (pad-mount)

**laundry** (4). *have* (1): Bulletin board with flyers · *missing* (3): Detergent vending; Folding tables; Laundry and bathhouse (12 x 10 m)

**playground** (4). *have* (2): Bench and bin; Playground lamp · *missing* (2): Slide and climbing frame; Spring riders

**RV pad** (3). *have* (1): Bud and Linda's fridge on the porch · *missing* (2): RV diesel tank (400 L); Travel trailer (park model)

**bedroom** (1). *partial* (1): Mattress on the floor

**living room** (1). *missing* (1): Electric fan heater

### campground only (`props/campground.csv`)

**tent site** (33). *have* (5): Bag of chips; Beer cans around the fire; Camping radio; Cooler; Fire pit chairs (stump seats) · *partial* (5): Bear-proof dumpster; Camp kitchen set (pots, kettle, enamel mugs); Camp lantern (propane or LED); Firewood bundle and kindling; Tent with a laptop and drone · *missing* (23): Audio recorder / parabolic mic; Bear-proof food locker (bear box); Cabin tent (family, 6 person); Camera tripod with a thermal scope; Camp chair (folding); Camp stove (two burner); Campfire (burning); Dish tub and soap; Dome tent; Dutch oven on coals; Fire ring with grate; Food hang bag and rope; Footprint casts and plaster kit; Headlamp; Marshmallow sticks and s'mores kit; Playing cards and board games; Pup / tunnel tent; Rain fly and guy-lines; Site number post; Sleeping pad / air mattress; Tarp shelter; Tent stakes and mallet; Water jug (5 gallon)

**ranger station** (13). *have* (2): First-aid box on the wall; Park map and bulletin board · *partial* (3): Ranger desk and radio; Ranger station floodlight; Ranger truck (with spotlight) · *missing* (8): Camp host RV; Camp store (counter, shelves, ice chest); Entry gate barrier; Firewood sales rack; Park brochure rack; Ranger cabin (9 x 9 m); Registration kiosk; Wildlife warning signs

**lake** (12). *partial* (1): Beach (sand) · *missing* (11): Boat ramp (6 x 15 m); Fishing net; Fishing rods and tackle box; Floating dock / swim platform; Kayaks and paddles; Lake fog; Lake with shallows (wadeable 1.2 m); Life jackets; Reeds and lily pads; Rowboat with oars; Swim line with buoys

**road** (11). *have* (3): Black bear at the dumpster; Loop road (gravel, 4 m); Pine forest (700 trees) · *partial* (2): Fern and leaf litter; Rocky ridge with cliff band · *missing* (6): Coyote pack; Creek ravine; Forest road bridge over the creek; Hunter's tree stand; Owl in a pine; Trail cameras on game trails

**amphitheater** (10). *have* (1): Split-rail fence · *partial* (1): Log benches · *missing* (8): Campfire amphitheater (60 seats); Embers in the fire pit; Interpretive signs; Log rails at trail edges; Pavilion (group shelter); Stage / speaker's podium; Trail markers and blazes; Trailhead sign and map

**bathhouse** (7). *have* (3): Changing bench; Sinks and mirrors; Trash and recycling station · *partial* (2): Lantern post; Vault toilet · *missing* (2): Bathhouse (6 x 10 m); Water spigot / hand pump

**lookout** (6). *partial* (2): Lookout stove and cot; Tower ladder and landings · *missing* (4): Binoculars on a hook; Fire lookout tower (15 m, cab 4 x 4 m); Lookout cab (windows, alidade table); Repeater antenna and radio

### suburb only (`props/suburb.csv`)

**house exterior** (31). *have* (5): Attached garage (single or double); Cat on the fence; Dog (pet, retriever); Electric meter and service entry; Side-yard gate · *partial* (9): Backyard shed (resin); Driveway (concrete); Foundation planting and shrubs; Front lawn (mown); Front walk and stoop; Garage door with keypad; House numbers and mailbox; Roof vents and solar panels; Two-storey suburban house · *missing* (17): Air-conditioner condenser; Backyard deck with railing; Chalk drawings on the sidewalk; Coach lights beside the garage; Dog door; Flag bracket and house flag; Gas and water meter boxes; Hose bib and sprinkler timer; Lawn sign (for sale or security company); Neighbourhood watch sign; Patio with an umbrella; Pool (inground) with fence; Pool equipment pad (pump and filter); Seasonal lights and inflatables; Slow children sign; Tree (front-yard maple); Yard sprinkler system

**street** (20). *have* (5): Delivery van; Parked minivan; Parked pickup; Power line pole; Streetscape trees · *partial* (6): Bus stop with a bench; Community mailbox cluster; Cul-de-sac bulb; Curb ramp and driveway apron; Garbage and recycling bins at the curb; Suburban street with parked cars · *missing* (9): Basketball court (half); Community pool house; Dog park / waste bag station; Electric car in a driveway; HOA entrance sign and lights; Neighbourhood park; Storm drain and manhole; Street sign (name and stop); Tennis court with net

**interior extras** (16). *have* (1): Mudroom lockers · *partial* (10): Attic with exposed rafters; Guest bedroom; Home office with two monitors; Home theatre room (recliners, screen); Laundry room (washer and dryer, upstairs); Man cave bar and neon; Nursery (crib, mobile, monitor); Pantry (walk-in); Staircase with a landing window; Utility room (water heater and furnace) · *missing* (5): Alarm keypad by the door; Basement finished (carpet, bar); Home gym; Smart home hub; Walk-in closet

**any** (7). *missing* (7): Doorbell camera (indoor chime); E-bike; Fitness tracker; Plaster foot cast; Smart lock; Smart plug and bulb; VR headset

**living room** (6). *partial* (3): Bar and bar stools (basement); Smart speaker; Soundbar and speakers · *missing* (3): Carbon monoxide detector; Dehumidifier; Humidifier

**kids room** (5). *partial* (1): Bunk bed with a slide · *missing* (4): Kid's bike helmet; Play tent; Toy chest of dress-up clothes; Toy kitchen and play food

**bedroom** (4). *partial* (1): Garment bag · *missing* (3): CPAP machine; Handheld hair dryer; White-noise machine

**garage** (4). *partial* (1): Car (parked in the garage) · *missing* (3): Garage door opener and wall button; Leaf blower and string trimmer; Sports gear bin (balls, bats, rackets)

**cellar** (2). *missing* (2): Exercise bike or treadmill; Weight bench and dumbbells

**kitchen** (2). *partial* (1): Kitchen island · *missing* (1): Under-sink water filter

**office** (2). *missing* (2): E-reader; Wireless charger and cables

**yard** (2). *missing* (2): Driveway basketball hoop (portable); Lawn sprinkler system heads

**attic** (1). *missing* (1): Attic fan

**dining room** (1). *missing* (1): Bar cart and decanters

**hall** (1). *missing* (1): Stair gate

**porch** (1). *missing* (1): Hot tub

### laboratory only (`props/laboratory.csv`)

**lab floor** (40). *have* (5): Fluorescent tube light; Microscope; Server rack; Specimen jars (shelf); Whiteboard with equations · *partial* (6): Exam / autopsy table (stylised, no gore); Lab bench with sink and gas taps; Lab computer workstation; Laboratory refrigerator; Sample vials in racks; Stasis / specimen tank (large) · *missing* (29): Analytical balance; Autoclave; Biohazard waste bin; Biosafety cabinet; Ceiling cable trays and pipes; Centrifuge; Emergency light and exit sign; Eyewash and safety shower; Fume hood; Gas cylinder rack; Glassware (beakers, flasks, test tubes); Glove box (isolator); Hot plate and stirrer; Incubator; Lab cart (trolley); Lab notebook and sample log; Liquid nitrogen dewar; Oscilloscope; Overhead surgical light; PCR machine / sequencer; Petri dishes and trays; Pipette stand; Rolling lab stool; Safety goggles and gloves; Sharps container; Spectrometer / mass spec; Test tube rack; Ultra-low freezer (-80 C); Wash station (foot pedal sink)

**support** (13). *have* (4): Changing room bench; Coffee station; Power cell (charged); Staff lockers · *partial* (3): Break room (table, fridge, vending); Control room console; Scientist's coat on a hook · *missing* (6): Air shower; Cleanroom gowning cabinet; Logbook; Pass-through hatch; Supply closet (shelves); Telescope dish / antenna (observatory)

**containment** (11). *have* (1): Intercom panel · *partial* (2): Dissected ship parts table; Holographic display · *missing* (8): Airlock / decon chamber; Alien artifact on a pedestal; Biohazard sign; Containment cell door with a keypad; Containment room (glass cell); Cryo storage locker; Glass partition with a door; Restraint table

**chemical storage** (3). *partial* (2): Acid / corrosives cabinet; Chemical bottle shelves · *missing* (1): Gas manifold and regulators

### military-base only (`props/military-base.csv`)

**command** (17). *have* (6): Briefing chairs (rows); Classified safe; Coffee maker and mugs; Evidence lockers; Filing cabinets (classified); Wall clocks (several time zones) · *partial* (7): Briefing room (tables, projector, map board); Command centre consoles; Intercom and PA speakers; Interrogation room (table, two chairs, lamp); Radio mast and antenna array; Radio room (rack and operator); Secure phone · *missing* (4): Debrief room (table, mirror, recorders); Paper stamps and rubber stamp "TOP SECRET"; Shredder and burn bags; Wall map with pins

**perimeter** (16). *have* (3): Dog (K9 shepherd); Guard dog kennel; Patrol road · *partial* (2): Perimeter floodlight pole; Perimeter motion sensors and cameras · *missing* (11): Double chain-link fence with razor wire; Flagpole; Gabion barrier (earth-filled); Guard tower with searchlight; Main gate and guard booth; Pop-up bollard / tire shredder; Restricted-area signs; Sandbag wall; Tank traps (hedgehogs); Vehicle barrier arm; Warning lights (red beacon)

**barracks** (14). *have* (2): Duty roster board; Wall locker · *partial* (8): Bunk bed with a footlocker; Field cot; Kitchen (commercial range, fridge); Laundry (commercial); Meal-ready-to-eat boxes; Mess trays and stacks; Rec room (TV, table tennis); Shower block · *missing* (4): Barracks building; Field tent (large); Latrine; Mess hall (long tables, steam trays)

**bunker** (12). *have* (3): Floor drains and grates; Fluorescent tunnel lights; Supply crates (stacked) · *partial* (3): Cable runs and conduit; Desert shrubs and yucca; Rocks and dry wash · *missing* (6): Ammo cans (empty, decor); Cold-storage vault (heavy door); Concrete bunker (door and vents); Elevator to the underground; Tunnel (concrete, pipes, cables); Vault door (round)

**motor pool** (8). *have* (1): Trailer (flatbed) · *partial* (3): Generator trailer; Light tower (mobile); Tool trolleys and benches · *missing* (4): Fuel depot (bladders, pumps); Motor pool lot; Utility truck (canvas); Water buffalo (trailer tank)

**hangar** (6). *partial* (3): Crates (stencilled); Mock alien ship under a tarp; Real alien ship (recovered) · *missing* (3): APC (original design); Black helicopter; Military transport truck

**helipad and airfield** (6). *partial* (1): Airfield apron · *missing* (5): Control tower; Helicopter (transport); Helipad with lights; Parked aircraft (static jet); Runway edge lights

**ship** (6). *have* (6): Black triangle craft; Cigar ship; Dart ship; Dropship; Man-in-Black craft; Mothership

**wild** (3). *partial* (1): Cactus (field) · *missing* (2): Palm / desert tree (Joshua); Tumbleweed

**any** (1). *missing* (1): Memory-wipe device (original design)

### town only (`props/town.csv`)

**main street** (31). *have* (8): Awning over a shop window; Bar counter and taps; Bar jukebox; Bar stools; Bulletin board on the street; Display window with lights on; Public bench; Shop sign (hanging or neon) · *partial* (7): Beer taps and bottle shelf; Brick shopfront (7 x 15 m); Grain elevator; Mailbox (blue, street); Main street road with parking; Post office (counter and mail boxes); Street lamps along main · *missing* (16): ATM; Bank (facade and ATM); Barber pole; Church (nave, pews, altar); Church pews; Grain elevator control panel; Grocery shelves and carts; Hardware store counter and shelves; Hardware store paint mixer; Hardware store tool displays; Key-cutting machine; Parking meters; Phone booth; Planter boxes and trees; Town hall clock tower; Town welcome sign

**gas station and truck stop** (18). *partial* (3): Drink cooler (glass doors); Ice chest (outdoor); Windshield squeegee bucket · *missing* (15): Air machine (tyre); Car wash vacuum; Convenience store (shelves, coolers); Drainage ditch and highway embankment; Fuel pump (island); Gas station canopy (18 x 8 m); Lottery sign and price sign; Newspaper rack; Oil and washer fluid rack; Payphone and satellite uplink; Propane exchange cage; Radio mast (truck stop); Truck bays (10); Truck wash and shower building; Trucker's cab (sleeper)

**diner** (17). *have* (5): Coffee pots and warmers; Diner building (chrome and neon); Diner counter with stools; Neon "OPEN" sign; Wall clock (diner) · *partial* (2): Diner dishes and trays; Napkin dispensers and condiments · *missing* (10): Diner booth (vinyl); Flat-top grill and fryer; Menus and table cards; Milkshake mixer; Order bell and ticket wheel; Pie display case; Security recording box (DVR); Sneeze guard and order window; Soda fountain; Walk-in cooler

**hospital** (17). *have* (3): Gurney / stretcher; Hospital vending and coffee; Medical cabinet (wall) · *partial* (4): Hospital bed (adjustable); Hospital building (small clinic); Nurse station; Reception desk and waiting chairs · *missing* (10): Ambulance bay; Crash cart; Defibrillator on the wall; Exam table and stool; Hand sanitiser dispenser; Hospital room call button; Oxygen tank on a wall; Privacy curtain on a track; Wheelchair; X-ray light box

**motel** (14). *have* (4): Motel bed; Motel bedside book; Motel curtains; Vacancy sign (tall neon) · *partial* (6): Motel TV on a dresser; Motel bathroom (tub, tiny sink); Motel desk and chair; Motel ice machine and vending alcove; Motel room door with a number; Motel room lamp and bedside phone · *missing* (4): Ice bucket and glasses; Key board and office bell; Motel pool (kidney-shaped); Motel row (rooms and numbers)

**sheriff's office** (14). *have* (4): Coffee machine and donut box; Cruiser (Deputy SUV); Sheriff's desk and chair; Wanted posters and bulletin board · *partial* (7): Cell cot and toilet; Computer terminal and printer; Dispatcher console and radio; Evidence locker room; Flag and framed photographs; Front counter and bell; Sheriff's office building · *missing* (3): Fingerprint and photo station; Holding cell (bars and bench); Key hooks and cell keys

**any** (2). *missing* (2): Pager; Road spike strip

**road** (2). *have* (1): Taxi · *missing* (1): Fire truck

### industrial only (`props/industrial.csv`)

**warehouse** (26). *have* (2): Lockers (bank); Warehouse cat · *partial* (6): Break room with vending; Fire extinguisher and sprinkler riser; Pallets (stacked); Roll-up dock doors; Warehouse building (corrugated); Warehouse office · *missing* (18): Caged tool crib; Conveyor belt; Dock bumpers and levellers; Emergency exit door and sign; Forklift charging station; High-bay light; IBC tote (liquid); Label printer; Loading dock with a truck; Mezzanine and metal stairs; Packing table and tape guns; Pallet racking (steel, 4 tiers); Safety railings and floor markings; Scissor lift; Stacked cardboard boxes; Time clock and punch cards; Warehouse fan (big, ceiling); Wire shelving units

**scrapyard** (16). *have* (1): Watchman trailer (with a light) · *partial* (4): Floodlight on a pole; Guard dog on a chain; Oil drums (rusty); Stacked wrecked cars (three high) · *missing* (11): Bathtubs, doors and junk; Car crusher / baler; Crusher and conveyor (quarry); Engine blocks and car parts; Gravel and sand heaps; Gravel quarry pit (40 m deep); Haul truck (quarry, large); Magnet crane (25 m); Scrap metal piles; Scrapyard compound (chain-link, gate); Weigh station and scale

**hangar** (15). *partial* (2): Pilot lounge (sofa, coffee); Rolling tool chest · *missing* (13): Aircraft tow bar; Airport beacon (rotating); Aviation maps and charts; Creeper (mechanic's); Engine hoist; Hangar door (bifold); Hydraulic jack and wing jack; Light helicopter; Parts bins and wall racks; Propeller stand; Single-engine airplane (original design); Small-aircraft hangar (T-hangar); Wheel chocks

**workshop** (2). *missing* (2): Blowtorch and propane; Drill press

### cabin only (`props/cabin.csv`)

**cabin** (33). *have* (6): Axe and splitting block; Bunk beds; Cabin dog (retriever); Kerosene lamp on the table; Outhouse (cabin); Wood stove with a pipe · *partial* (7): Cabin stone chimney; Enamelware pots and cups; Generator shed; Loft with a ladder; Log cabin (single room and loft); Quilt on the bunk; Woodpile under a lean-to · *missing* (20): Animal pelts on a wall; Antler chandelier; Barometer and wall thermometer; Bear-resistant food box; Bearskin rug (faux); Bird feeder on a post; Cabin porch with a swing; Cast-iron skillet on a hook; Creaky floorboards; Fishing rods and a net; Guestbook on a stand; Gun rack (empty, decor); Hand pump at the sink; Root cellar; Rope hammock on the porch; Snowshoes and skis on the wall; Solar panel and battery shed; Taxidermy fish on a plaque; Trail map on the wall; Wood-burning sauna

### leisure only (`props/leisure.csv`)

**fairground** (23). *have* (3): Carnie trailer; Fence and gate (perimeter); Hay bales as seats · *partial* (6): Funhouse mirror; Generator trucks; Livestock barn (stalls and show rings); Port-a-potties; Prize plushies (giant); Ticket office with a safe · *missing* (14): Bumper cars; Carousel; Cotton-candy and popcorn carts; Duck shoot and can-knockdown booth; Ferris wheel (25 m); Funhouse and hall of mirrors; Funnel-cake stall; Giant inflatables; Grandstand (60 x 12 m); Midway game booth (ring toss); Prize ribbons and show boards; Sound board and speakers; Spinning teacup ride; String lights across the midway

**cemetery** (16). *have* (3): Cemetery bench; Groundskeeper's shed; Shovel and wheelbarrow · *partial* (4): Grave lanterns and vigil candles; Vigil photograph on a stand; Wreaths and flowers; Yew hedge · *missing* (9): Angel statue; Bell rope; Chapel (8 x 14 m, steeple 16 m); Crosses (stone, iron, wood); Fresh grave mound with tent; Headstones (rows, 0.5 x 0.2 x 0.9 m); Mausoleum / crypt; Stone wall; Wrought-iron fence and gate

**drive-in** (13). *have* (1): Lot lighting poles · *partial* (4): Cash box and the box office safe; Concession counter and candy; Marquee sign with letters; Parked cars in fan-shaped rows · *missing* (8): Drive-in playground; Film projector; Movie screen (30 x 16 m); Popcorn machine; Projection booth (on a rise); Snack bar (12 x 8 m); Speaker post and speaker (car window); Ticket booth and gate


## Sources

All sources were read as **search-result summaries** (see [What the research says](#what-the-research-says)); `WebFetch` failed on every host in this environment, so
pages were not fetched or quoted, and no model, texture or text was taken from any of them. Packs are named only as a record that an object category
exists in the wild.

**Environment-art and level-design write-ups**

- Television props handbook split into stage props, set dressings and hand props (via a props history archive): <https://props.eric-hart.com/tag/history/page/20>
- Game Maker's Toolkit, *How Level Design Can Tell a Story* (video): <https://www.youtube.com/watch?v=RwlnCn2EB9o>
- Environmental storytelling tutorial: <https://gamedevacademy.org/environmental-storytelling-tutorial/>
- Narrative level design (tyranny of the toolbar): <https://www.wayline.io/blog/tyranny-of-toolbar-narrative-level-design>

**Free and open libraries (category trees)**

- Kenney Furniture Kit: <https://kenney.nl/assets/furniture-kit> · Survival Kit: <https://kenney.nl/assets/survival-kit> · Nature Kit: <https://kenney.nl/assets/nature-kit> and <https://opengameart.org/content/nature-kit> · Holiday Kit: <https://kenney.nl/assets/holiday-kit> · Retro Urban Kit: <https://kenney.nl/assets/retro-urban-kit> · Graveyard Kit: <https://kenney.nl/assets/graveyard-kit> · City Kit (Industrial): <https://kenney.nl/assets/city-kit-industrial> · City Kit (Commercial): <https://kenney.nl/assets/city-kit-commercial> · Mini Skate: <https://kenney.nl/assets/mini-skate> · all-assets index: <https://kenney.nl/data/itch/kga3/assets.html>
- Quaternius Ultimate Furniture Pack: <https://quaternius.com/packs/ultimatefurniture.html> · Ultimate Crops Pack: <https://quaternius.com/packs/ultimatecrops.html> · LowPoly Farm Buildings: <https://quaternius.itch.io/lowpoly-farm-buildings> · LowPoly Animated Animals: <https://quaternius.itch.io/lowpoly-animated-animals> · LowPoly House Interior Pack: <https://opengameart.org/content/lowpoly-house-interior-pack> · LowPoly Modular Sci-Fi Environments: <https://opengameart.org/content/lowpoly-modular-sci-fi-environments>
- Poly Haven models and its 15 categories: <https://polyhaven.com/models> · Containers and Storage: <https://polyhaven.com/models/containers-storage> · Electronics and Appliances: <https://polyhaven.com/models/electronics-appliances> · Decor and Art: <https://polyhaven.com/models/decor-art> · Tools and Equipment: <https://polyhaven.com/models/tools-equipment> · Leisure: <https://polyhaven.com/models/leisure> · Industrial and Infrastructure: <https://polyhaven.com/models/industrial-infrastructure> · a wall-mounted garden hose in the "shed" collection: <https://polyhaven.com/a/garden_hose_wall_mounted_01> · licence (CC0): <https://polyhaven.com/license>
- Sketchfab's 18 categories: <https://sketchfab.com/categories> and <https://help.sketchfab.com/en/articles/16152563>

**Asset-pack contents (object names and categories only)**

- Farm and barnyard: HDLM Farm Barnyard Props <https://forums.unrealengine.com/t/hdlm-studios-hdlm-farm-barnyard-props/2835776> · Synty POLYGON Farm Pack <https://syntystore.com/products/polygon-farm-pack> · Simple Farm cartoon assets <https://assetstore.unity.com/packages/3d/environments/industrial/simple-farm-cartoon-assets-47003> · ithappy farm kit <https://ithappystudios.com/environment/farm/>
- Kitchen: <https://kicodes.itch.io/low-poly-modern-kitchen-pack> · <https://assetstore.unity.com/packages/3d/props/interior/pbr-kitchen-props-megapack-188065> · Bathroom: <https://tillion.itch.io/psx-bathroom-pack> · <https://assetstore.unity.com/packages/3d/props/interior/pbr-toilet-bathroom-props-173882> · Kids' room (listings): <https://www.daz3d.com/creepy-childrens-bedroom>
- Basement and attic: <https://assetstore.unity.com/packages/3d/environments/urban/basement-85501> · <https://game-guru.com/dlc/antiques-in-the-attic-pack>
- Garage and workshop: <https://resilientlogicstudio.itch.io/garage-tools-props-pack> · <https://www.fab.com/listings/b65e8ee6-7b0d-4152-a5f4-38b4c829f0dc> · <https://www.daz3d.com/fg-garage>
- Suburb and yard: <https://assetstore.unity.com/packages/3d/environments/urban/city-suburbs-stylized-low-poly-197864> · <https://assetstore.unity.com/packages/3d/props/9t5-low-poly-tree-swings-with-physics-123584> · <https://forums.unrealengine.com/t/suburban-asset-pack-modular-residential-environments/2711371>
- Trailer park: <https://assetstore.unity.com/packages/3d/environments/pbr-trailer-park-pack-83813> · <https://elbolilloduro.itch.io/trailer-park>
- Campground: <https://paderunt.itch.io/camp-it-pack> · <https://assetstore.unity.com/packages/3d/props/exterior/camping-site-18401> · <https://assetstore.unity.com/packages/3d/environments/realistic-modern-rural-camping-site-1-asset-package-313556>
- Laboratory: <https://assetstore.unity.com/packages/3d/props/sci-fi-laboratory-props-36889> · <https://www.cgtrader.com/3d-models/science/laboratory/frozen-research-lab-modular-environment-props-pack>
- Military base: <https://assetstore.unity.com/packages/3d/props/exterior/base-camp-hdrp-207323> · <https://sofa499.itch.io/basicprops-military> · <https://assetstore.unity.com/packages/3d/environments/military-base-pack-hq-142304>
- Hospital: <https://booth.pm/en/items/9000802> · Warehouse: <https://www.cgtrader.com/3d-models/industrial/tool/industrial-warehouse-props-storage-asset-pack> · Gas station: <https://elbolilloduro.itch.io/gas-station> · Motel: <https://hpclscruffy.daz3d.com/desert-motel-room> · Diner: <https://stefan-dolidis.itch.io/diner-prop-pack> and <https://assetstore.unity.com/packages/3d/props/furniture/diner-furniture-95437>
- Forest cabin: <https://elegantcrow.itch.io/retro-log-cabin> · <https://assetstore.unity.com/packages/3d/props/interior/rustic-log-cabin-104970>
- Scrapyard: <https://ithappystudios.com/environment/junkyard/> · Fairground: <https://forums.unrealengine.com/t/3dreamax-studio-carnival-funfair-stalls-game-booths-food-carts-circus-festival-props/2741853> · Cemetery: <https://superhivemarket.com/products/cemetery> and <https://forums.unrealengine.com/t/released-forgotten-graveyards-low-poly-cemetery-mega-pack/2005285>

**Real-world inventories and equipment lists**

- Home inventory checklists: Co-operators <https://www.cooperators.ca/-/media/cooperators/assets/insurance/documents/home-inventory-checklist.pdf> · Missouri <https://insurance.mo.gov/media/21626> · Oklahoma <https://oid.ok.gov/consumers/home-inventory-checklist>
- Garage inventory (an insurer's list): <https://www.statefarm.com/content/dam/sf-library/en-us/secure/legacy/pdf/garage.pdf> · garage storage ideas: <https://www.bobvila.com/articles/garage-storage-ideas/>
- Farm machinery: <https://www.tafe.com/blog/10-must-have-implements-for-maximum-productivity/> · <https://www.mahindratractor.com/blog/top-10-tractor-Implements-for-farming>
- Hangar contents (a pilots' forum thread): <https://pilotsofamerica.com/community/threads/what-do-you-keep-in-your-hangar.71024/> · airport ground equipment: <https://visualdictionaryonline.com/transport-machinery/air-transport/airport/ground-airport-equipment_3.php>

**Stealth and interactive props in games**

- Hitman: Classic Coin <https://hitman.fandom.com/wiki/Classic_Coin> · Apple <https://hitman.fandom.com/wiki/Apple> · lures guide <https://www.speedrun.com/hitman_2/guides/q27xs>
- Thief and the throw-a-distraction trope: <https://tropedia.fandom.com/wiki/Throwing_the_Distraction> · The Blackout Club noisemaker: <https://theblackoutclub.gamepedia.com/Noisemaker> · Project Zomboid noise maker: <https://pzwiki.net/wiki/Noise_Maker>
- Alien: Isolation crafting and items: <https://www.gamerevolution.com/?p=65748> · <https://www.gamepressure.com/alien/crafting/z96a11>
- Metal Gear Solid: <https://www.gamerevolution.com/?p=30494> · <https://steamcommunity.com/app/287700/discussions/0/312265256997297221>
- Hello Neighbor item and distraction guide: <https://www.gameskinny.com/rb4cl/hello-neighbor-item-and-distraction-guide>
- Untitled Goose Game walkthrough: <https://nintendolife.com/news/2020/05/guide_untitled_goose_game_walkthrough_-_puzzle_solutions_and_to-do_list_objectives>
- Design write-ups on noise makers: <https://babel.speldesign.uu.se/?p=3843> · <https://soundingames.dei.uc.pt/index.php/Sound_Decoys>

**This repo**

`CLAUDE.md`, `art/README.md`, `docs/assets/asset-list.md`, `docs/levels/farmstead.md`, `trailer-park.md`, `campground.md`, `map-concepts.md`, `game.md`, `docs/art/*`,
`art/scripts/*`, and the issues #156, #265, #266, #267, #270, #262, #146 and #43.
