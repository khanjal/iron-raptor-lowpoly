# Asset list — every model we need

The master list of art assets for the game: first the **global** assets reused across every map
(people, aliens, animals, vehicles, tools, gear, lights, decals), then what the **Farmstead** needs on top
([`farmstead.md`](../levels/farmstead.md)). Everything is modelled in **Blender** (with the Blender MCP tool);
audio and Unity's own Terrain and particle systems are the exceptions.

This is a **plan and a tracker**, a first pass to react to. Numbers marked *proposed* are guesses until
playtesting and the Steam Deck budget (#45). Art direction is #43 (`needs-decision`), set dressing is #42, the
graybox generator is #35.

**How to read it.** IDs are stable so issues and PRs can cite them: `GP-` people, `GA-` aliens, `GN-` animals,
`GV-` vehicles, … for global items; `FM-` for Farmstead-only items. **Pri:** `P0` needed to play milestone 0.2 ·
`P1` needed for 0.3 (objectives, escalation) · `P2` set dressing and polish · `Later` another map or milestone.
A **Status** column is added when an asset is started.

## 1. Where we are

| Today | Detail |
|---|---|
| 23 MarpaStudio prefabs | `Assets/Prefabs/Farm/MarpaStudio/`: barrel, barn (closed shell), box, bucket, chicken house, fence, feed trough, gate, hay (round, square), house (closed shell), log, old shed, outhouse, rake, rocking chair, shed, shovel, silo, stool, well, wheelbarrow cart, windmill. Each exists twice (`X.prefab` and `X 1.prefab`). |
| **The pack's models are missing** | The prefabs are variants of a source whose GUID (`ac8d86af…`) is not in any `.meta` under `Assets/`, and no pack `.fbx` exists (the models under `Assets/Art/` are ours, §10). Only three materials are committed. They have no mesh to show here. |
| Graybox code | `SceneAutoSetupEditor` (Auto Setup Scene) now builds the Farmstead from `FarmsteadLayout` through `FarmsteadBuilder` and dresses it with our own models (`FarmsteadArt`); no code uses the MarpaStudio prefabs any more. A throw-away primitive farm-prefab creator (`CreateFarmPrefabs`) existed once and has been deleted. |
| Audio | CC0 clips under `Assets/Audio/` (Kenney footsteps and sci-fi sounds, a few Freesound clips): `CREDITS.md`. |
| Everything else | Our own Blender models under `Assets/Art/` (§10); nothing else yet. |

**Decision implied by "we model everything in Blender":** the MarpaStudio prefabs become placeholders and are
retired as their Blender replacements land (every one has a row below, marked *remake*). That also removes the
missing-pack and licence questions. Confirm that is wanted.

## 2. Blender pipeline

Proposed conventions, so that assets made in different sessions fit together.

| Topic | Convention |
|---|---|
| Style | Stylised low-poly, flat shading or a shared palette, big readable silhouettes (they must read in near-dark). The horror side (FBI, MIB) comes from light and sound, not extra detail. |
| Units and axes | 1 Blender unit = 1 m. Origin on the floor at the centre of the base. Export FBX with transforms applied, forward −Z, up Y, scale 1, so the model arrives in Unity upright and unscaled. |
| Naming | `Prefix_Name_NN`, for example `GP_Farmer_Body`, `FM_Barn_Wall_Door`. One Blender collection per asset. |
| Textures | One shared **palette texture** (256 or 512) for the global set and one per location, instead of a texture per prop. Few materials, GPU instancing on. |
| Colliders | Not modelled; set in Unity (boxes and capsules). Corn gets none. |
| Rigs | Four shared base rigs, each reused by many assets: **humanoid** (people and the Grey, Nordic, Shadow Entity, Mimic bodies), **quadruped** (cow, horse, sheep, pig, goat, dog, deer), **biped bird** (chicken, duck, goose, turkey, owl, crow), and per-race custom rigs for the odd aliens (Energy Being, Insectoid). One animation set per rig, retargeted. |
| LODs | Only for people, vehicles, buildings and trees (and cheap cards for corn). |
| Reproducibility | Keep the Blender Python used to build each batch in `art/scripts/`, so an asset can be regenerated and diffed. |
| Where files go | Sources: the Python in `art/scripts/` (outside `Assets/`, so Unity does not import them); no `.blend` files are in the repository. Exports: `Assets/Art/Global/…` and `Assets/Art/Farm/…`. Gameplay prefabs: `Assets/Prefabs/…`. Every file with its `.meta` (`dev/check.py`). |
| Git LFS | `.fbx`, `.png` and the audio formats (`.wav`, `.mp3`, `.ogg`) are already LFS-tracked (`.gitattributes`). **`.blend` is not**: add it before committing any, and watch the free-plan LFS budget (`CLAUDE.md`). |
| Gameplay prefab pattern | The prefab root holds the gameplay (colliders, `NetworkObject`, interactable, light, noise component); a child `Visual` holds the Blender mesh. A graybox cube and the final model are interchangeable, so the 0.2 work does not wait for art. |

### 2.1 Quality bar

Issue #344 (owner decision 2026-10-23). **Style: better-made low-poly** with the shared palette and the Blender generators; not realism. No scanned, library (Poly Haven, Sketchfab, Poly Pizza) or `generate_3d` models: wrong style for the palette, no rigs or markers, and Git LFS cost. Each new or reworked model starts from a written brief (`blender-assets` skill, "Brief before build"); the build order is blockout, secondary features, then small detail.

**Keep what already works.** A rework or a new variant never renames, replaces or drops what exists: rigs, clips, moving parts, `Light_`/`Sound_`/`Switch_` markers, `art/data/interactions.json`, ids and file names (scenes and the farm builder look models up by name; `FD_CheeseWedge_01` stays `FD_CheeseWedge_01`). The variant choice in the brief is for new models and new variants (a new id); an existing id keeps its variant unless the owner says otherwise. **Changing the animals' faceted style is out of scope** unless the owner says so.

**Triangle budget per class.** *PROPOSED* for the owner to adjust, and the only per-class table: the per-class rows of §7 are replaced by it and §7 keeps the scene total. The "repo today" column is what the repo's own README and notes state; "not stated" means nobody measured it (do not read it as an estimate). A hero piece may go over by agreement; the brief says so.

| Class | PROPOSED triangles | Repo today |
|---|---|---|
| Hand prop, tool, food | 100-400 | a few hundred |
| Furniture, appliance | 300-1,200 | not stated |
| Vehicle | 1,200-2,500 | not stated |
| Building piece (wall, door, window, roof) | 50-500; hero buildings per §7 | not stated |
| Person | 800-1,500 | faceted people about 800-900 |
| Animal | 400-1,200 (birds and small pets under 1,000) | faceted animals about 400-700 |
| Ship interior prop | 200-900; hero (console, terminal) up to 2,000 | props 190-870; terminals 1,450-1,850 |
| Ship hull and parts | 1,500-4,000 | not stated |

The `smooth` variants in `art/README.md` (animals 3,000-4,500, people 3,500-4,000) are far outside these caps. They were judged not to look right and are not exported; they stay not allowed, and a smooth variant would need the owner's yes and a budget of its own.

**Shape.**
- Bevel the hard edges of free-standing objects. No bare box where the real thing has trim, handles, feet, seams or wear. **Exempt:** kit pieces on the 3 m grid (walls, floors, the six skins), which must butt together without a groove at every seam, and the faceted animals and people (flat shaded on purpose).
- Hollow things are hollow if anyone can see inside or put something in: a fridge has a cavity, a car has a seat and a floor. Solid things stay solid: a crate, a can or a cereal box is not hollowed. An egg carton has cups and a lid; the lid is a hinged part and gets its `interactions.json` entry in the same change (the lid arrives with the food batch, not with this document).
- The silhouette reads from 10 m, and the colours are palette entries only (no new LFS-heavy textures).

**Alien tech, starships.** The look: ramps, doors, hatches and landing legs read as alien, not as a human door on a hinge: they telescope, extend, slide into the hull or open like an iris, with a lit edge marking the opening. Landing legs come out of a recess in the hull (the hull has the bay) and end in a foot pad.
- The game can pose two part kinds only: **`hinge`** and **`slide`** (vehicle wheels are a third kind, **`spin`**, which the game must turn about the axis through the pivot; the browser does) (`props_lib.part()`, `PropRuntime`, `ShipHullParts`, `ShipFlightRig`). A telescoping ramp or leg is several `slide` stages, an iris is several hinged leaves. **Do not rely on a part that scales or shrinks:** nothing in Unity poses it.
- **Existing parts stay as they are**: every hull ramp is `ShipRamp` (a `hinge`, axis x) and the legs are `ShipLeg_N` (`slide`, z), and `ShipHullParts.cs` and `docs/art/ship-varieties.md` use those names as the model's interface. Keep the names and kinds unless the owner changes them. The new look applies to new parts and to a reworked hull that keeps those names.
- A new part kind (scale/shrink, an iris pose) needs a Unity change first: #364 in the game repo.

**Vehicles.** Lights are emitters at their real positions (`emitters.py`). Each `Light_` emitter becomes a real Unity Light, so keep them few (§7: a few real-time lights): **real Lights** are the headlights (front, spot, aimed forward), the red tail and brake lights (rear) and the light bar on police and ambulance liveries. **Glow only** (an emissive palette colour on the mesh, no `Light_` marker) are the indicators at the four corners and the plate light. FBI cars are usually unmarked in the US reference: no light bar unless the brief shows one. Not one point in the middle of the roof.

**Region.** The United States is the reference: US ambulance types, police liveries, signs, appliances and packaging. Other regions are #346 (`needs-decision`); do not build them.

## 3. Animals: where they live and who they belong to

Any animal can be placed in one of three ways, and the same prefab supports all of them. The placement is data
in the level, not a different model.

| Mode | What it means | Behaviour needed |
|---|---|---|
| **Penned** | Stall, pen, sty, coop, hutch, cage, kennel or paddock behind a gate | Mostly stationary, idle loops, react to noise from behind the fence |
| **Field** | A herd or flock grazing, lying, drifting in a pasture | Group idle/graze, spook together |
| **Roaming** | Free in the yard, the street or the house | A simple wander on the NavMesh; the animal can be underfoot, which is the point |

Pets and strays add a second axis, **who it belongs to**. Same model, different behaviour component:

| Role | Meaning | Behaviour |
|---|---|---|
| **Livestock** | Belongs to the farm | Pens and fields; herd reactions |
| **Pet** | Belongs to a named human | Stays near the owner or the home: a dog follows the owner and barks, an indoor cat sits on furniture, a bird in a cage squawks |
| **Working** | Belongs to the place | Farm dog herding, barn cat hunting, K9 tracking by scent |
| **Stray** | Belongs to nobody | Scavenges, flees; can be a distraction, a nuisance, or (*proposed*) be befriended |
| **Wild** | Ambient | Flushes, bolts, calls: soft alarms and background noise |

| Animal | Penned | Field | Roaming | Reaction to aliens (a noise source or a trace) |
|---|---|---|---|---|
| Cow | Barn stalls, corral | Pasture herd | Rare | Moo, stampede if spooked |
| Horse | Stable stalls, paddock | Paddock | Rare | Whinny, rear up |
| Sheep | Pen with shelter | Flock | Yes | Bleat, the flock scatters |
| Pig | Sty with mud wallow | Pen outdoors | No | Squeal |
| Chicken | Coop and run | No | Yes, in the yard | Squawk (the classic noise trap) |
| Goat | Pen | Pasture | Yes | Bleat, climbs onto things |
| Goose / duck | Pen by the pond | Pond edge | Yes | Honk (geese are guard animals, loud) |
| Turkey | Pen | No | Yes | Gobble |
| **Dog: farm / pet** | Dog house, kennel, indoors | No | Yes, follows the owner | Smell-based detection, barks; **sniffs out Nordics and Mimics** |
| Dog: guard | Chain or fenced run | No | No | Loud bark, lunges |
| Dog: K9 | With a handler | No | Tracks | Alerts on an alien's scent; Tier 1 and up |
| Dog: stray | No | No | Yes | Scavenges, barks at what it fears |
| **Cat: house pet** | Indoors | No | Yes, indoors and the porch | Hisses, knocks things over, bolts |
| Cat: stray | No | No | Yes, alleys and bins | Yowl, bolts |
| Cat: barn / working | Haymow, stalls | No | Yes | Hiss from the dark |
| Rabbit: pet | Hutch or cage | No | Rare | Thump |
| Rabbit: wild | No | Field edge | Yes | Freeze, then bolt (a rustle) |
| Pet bird | Cage or perch | No | No | Squawk, a parrot repeating a human voice |
| Wild birds | No | No | Yes | **Flush in a flock when approached**: a soft alarm |
| Small pets (hamster, guinea pig, fish) | Cage or tank | No | No | Almost nothing; dressing |

Animals also react differently to different alien races: some set them off, some keep them calm. Concept in
[`../animal-reactions.md`](../animal-reactions.md); the art it needs is `GN-80`…`GN-84`.

Farmstead stocking (*proposed*, set by the level data): about 8 cows (4 in barn stalls, the rest in the pasture
and a corral), 2 horses, 8 sheep, 3 pigs, 10 chickens, 2 goats, 3 geese, a farm dog (working, sleeps by the
porch), the farmer's kid's pet rabbit in a hutch, a barn cat, a stray cat on the road side, a budgie in the
kitchen, and wild birds, owls and bats as ambience. This replaces the level doc's "the pasture is empty at
night"; see §9.

## 4. Global assets (reused on every map)

### 4.1 People (`GP-`)

One humanoid rig, and a modular setup: **body types × heads × hair × outfits × accessories**, so a handful of
meshes make a crowd. Each *named* character below is a combination, not a separate model; they only need new
modelling for outfit pieces.

**Base bodies and parts**

| ID | Item | Notes |
|---|---|---|
| GP-01 | Adult body, masculine | ~1.8 m, two builds (slim, heavy) |
| GP-02 | Adult body, feminine | ~1.7 m, two builds |
| GP-03 | Adult body, neutral | A third silhouette for variety and for the FBI/MIB, who should look alike |
| GP-04 | Child body | ~1.1–1.4 m, two ages |
| GP-05 | Teen body | ~1.6 m |
| GP-06 | Elder body | Stooped, slower; can be any of the above with a posture variant |
| GP-07 | Heads | 12–16 variants, plus facial-expression blend shapes (neutral, startled, scream, grin, asleep) |
| GP-08 | Hair and facial hair | ~20 pieces (short, long, bald cap, ponytail, beard, moustache, grey) |
| GP-09 | Hands, with grips | Flashlight, radio, phone, tool, tranq rifle, clipboard |
| GP-10 | Footwear | Boots, sneakers, dress shoes, slippers, barefoot |
| GP-11 | Headwear | Cap, cowboy hat, sheriff hat, hard hat, beanie, fedora, helmet, none |
| GP-12 | Eyewear | Glasses, sunglasses (the MIB's), goggles, night-vision |
| GP-13 | Badges and ID | Sheriff badge, FBI badge on a lanyard, ID card |

**Outfits** (per faction, each a few colour variants)

| ID | Faction | Outfit pieces |
|---|---|---|
| GP-20 | Rural locals | Overalls, flannel shirt, work jeans, house dress, nightgown, pyjamas, bathrobe, school clothes, cardigan |
| GP-21 | Townsfolk | T-shirt, jeans, jacket, dress, apron (diner), mechanic coverall, delivery uniform, jogging clothes, hi-vis vest |
| GP-22 | Sheriff's office | Brown/tan uniform, duty belt, jacket, rain slicker |
| GP-23 | State police | Uniform and campaign hat |
| GP-24 | FBI | Dark suit and tie, windbreaker marked FBI, tactical vest |
| GP-25 | Military | Fatigues, helmet, flak vest, officer dress, sentry gear |
| GP-26 | Scientists | Lab coat, hazmat/clean suit with visor, security guard shirt |
| GP-27 | Men in Black | Black suit, white shirt, black tie, sunglasses, identical for every MIB |

**Named cast** (combinations of the above)

| ID | Character | Where | Role | Pri |
|---|---|---|---|---|
| GP-30 | **Farmer** | Farm | Tier 0, the patrol, calls the sheriff | P0 |
| GP-31 | **Farmer's kid** | Farm | Wakes, screams (instant trace) | P0 |
| GP-32 | Farmer's spouse | Farm | Asleep upstairs (*proposed*) | P2 |
| GP-33 | Grandparent | Farm | Rocking chair, a light sleeper (*proposed*) | P2 |
| GP-34 | Farmhand | Farm | Second walking human at a bigger farm (*proposed*) | Later |
| GP-35 | **Sheriff** | Any rural map | Tier 1 | P1 |
| GP-36 | **Deputy** | Any rural map | Tier 1 | P1 |
| GP-37 | State trooper | Highway/town | Reinforcement (*proposed*) | Later |
| GP-38 | **FBI field agent**, two or three looks | Any | Tier 2, search in pairs | P1 |
| GP-39 | FBI team lead | Any | Gives orders | P1 |
| GP-40 | FBI forensic tech | Any | Collects traces, evidence flags | P1 |
| GP-41 | FBI EMF specialist | Any | Energy Being counter | P1 |
| GP-42 | FBI drone operator | Any | Tier 2 drone | P2 |
| GP-43 | **Man in Black** | Any | Tier 3, one model, never explained | Later |
| GP-44 | MIB director | Area 51 | Boss (*proposed*) | Later |
| GP-45 | Civilian: shopper / passer-by (×6 looks) | Town | Witnesses | Later |
| GP-46 | Diner cook, waitress, customer | Town | Witnesses | Later |
| GP-47 | Gas-station clerk | Town | Witness, a phone | Later |
| GP-48 | Mechanic | Town | Garage | Later |
| GP-49 | Teenagers (couple) | Town/farm | Make-out spot, comedy | Later |
| GP-50 | UFO-nut conspiracist | Any | Believed by nobody, funny (*proposed*) | Later |
| GP-51 | Drunk | Town | Comic witness | Later |
| GP-52 | Sheriff's office clerk, dispatcher | Town | Radio/phone voice | Later |
| GP-53 | Soldier, sentry | Base/Area 51 | Patrol | Later |
| GP-54 | Officer | Base/Area 51 | Command | Later |
| GP-55 | Scientist, lab tech | Research station / Area 51 | Electronics | Later |
| GP-56 | Security guard | Any | Night shift | Later |

**People animations** (one set on the humanoid rig)

Idle (standing, bored, nervous), walk, run, **crouch-walk**, sneak, sit (chair, couch, driver), **sleep** (lying),
wake up, startled, **investigate** (look around, crouch to look, point), **flashlight sweep**, shrug,
"I don't believe it", **phone call** (dial, talk, hang up), **radio call**, scream, panic run, cower, talk
(gesture loops), open/close door, climb ladder, climb stairs, carry, push, throw, work (rake, hammer, mop),
eat/drink, **lifted by Tractor Beam** (floating, flailing), **tranq hit and fall**, lie unconscious, be loaded into
a vehicle, drive (steering), shoot tranq rifle, aim net gun, handcuff, kneel to examine a trace, hold a scanner
and sweep it, hat tip. About 50 clips; many are shared with children and elders via the same rig.

### 4.2 Aliens (`GA-`)

Third-person bodies, so crewmates see each other. First-person view-models and HUDs are the race-HUD work
(#49). The humanoid rig is shared where it fits.

| ID | Race | Notes | Pri |
|---|---|---|---|
| GA-01 | **Grey** | Small body, big head and eyes, fragile and slow | P0 |
| GA-02 | **Shadow Entity** | Silhouette-heavy, light-absorbing material, no readable face | P0 |
| GA-03 | **Energy Being** | Glowing form, emissive, flickers (a custom rig, flyer) | P0 |
| GA-04 | Nordic | Tall, human-looking, odd in small ways | Later |
| GA-05 | Insectoid | Climber, many limbs; custom rig, can crawl on walls | Later |
| GA-06 | Mimic | A neutral base shape that can copy others, plus the "become object" pose | Later |
| GA-07 | Later races (Reptilian, Crawler, Synthetic Biologic, Signal Intelligence, Watcher, Phase Entity) | One body each, from `AlienSpecies` | Later |
| GA-10 | Alien animations | Idle, walk, sprint, crouch, jump, fly, ability cast per race, **being captured** (netted, tranq), downed, revived, carried, floating (beam), per-race signature move | P0 |
| GA-11 | Cosmetics (unlocks #32) | Hats, scarves, antennae; just a slot for now | Later |

### 4.3 Animals (`GN-`)

Each animal: one model, optional variants, and an animation set on a shared rig. All support the three placement
modes in §3 and a role (livestock, pet, working, stray, wild). Livestock, dogs, cats, rabbits and birds are global:
every map reuses them, so a pet dog in a town yard and the farm dog are the same model with different coats.

| ID | Animal | Variants | Animations |
|---|---|---|---|
| GN-01 | **Cow** | Holstein, brown, calf, bull | Idle, chew, graze, walk, lie down, stand up, startle, moo, stampede, **lifted** (beam pose) |
| GN-02 | Horse | Two coats, foal | Idle, graze, walk, trot, gallop, rear, whinny, lie down |
| GN-03 | Sheep | Ewe, lamb, shorn/woolly | Idle, graze, walk, run, bleat, scatter |
| GN-04 | Pig | Sow, piglet | Idle, root, walk, wallow, squeal, run |
| GN-05 | **Chicken** | Hen (two colours), rooster, chick | Peck, walk, run, flap, squawk, roost, fly up |
| GN-06 | Goat | Adult, kid | Idle, graze, walk, climb/jump, bleat |
| GN-07 | Goose | Adult | Waddle, honk, flap, chase |
| GN-08 | Duck | Drake, hen, duckling | Waddle, swim, quack |
| GN-09 | Turkey | Tom, hen | Strut, gobble |
| GN-10 | Donkey, llama | *Proposed*, for bigger farms | Idle, walk, spit |
| GN-20 | **Farm / working dog** | Border collie or heeler type (default), two coats | Sleep, wake, sniff, bark, growl, walk, run, chase, herd, wag |
| GN-21 | **Pet dogs**, each owner picks one | Retriever, beagle/hound, terrier (small, yappy), bulldog, dachshund, poodle, chihuahua (toy), mutt, husky, large shepherd mix | Same set plus sit, beg, play-bow, lie on the porch, **follow owner**, fetch |
| GN-22 | **Guard dog** | Big dog, chain or fence line | Same set, deeper bark, lunge on a chain |
| GN-23 | **K9 / police dog** | Shepherd (sheriff and FBI) | Same set plus heel, track by scent, alert (points at a hiding alien), bite-hold. Dogs see through Nordics and Mimics (`game.md`) |
| GN-24 | **Stray dog** | Scruffy mutt, skinny | Same set plus scavenge, flinch, follow a player who feeds it (*proposed*) |
| GN-25 | Puppy | Any breed, small | Tumble, yap, chew |
| GN-30 | **Cats**, a shared model with coats | Tabby, black, orange, grey, tuxedo, calico, white, Siamese; kitten | Prowl, sit, groom, sleep (curled), stretch, hiss, arch back, knock-over, jump on and off furniture, run, purr loop, meow |
| GN-31 | **House cat** | Any coat; in windows, on sofas, on a bed | Same set, indoors |
| GN-32 | **Stray cat** | Any coat, thin; alley, dumpsters, porch | Same set plus scavenge, bolt |
| GN-33 | **Barn / working cat** | Tabby, orange; haymows, stalls | Same set plus hunt mice, hiss from the dark |
| GN-34 | Cat accessories | Collar and tag, bell (a noise source), food and water bowls, litter box, scratching post, cat flap | Props |
| GN-40 | **Rabbits**: domestic | Lop, dwarf, spotted; hutch pet | Idle, hop, thump, nibble, burrow in straw |
| GN-41 | Rabbits: wild | Cottontail (fields, tree line), jackrabbit (desert) | Freeze, bolt, hop, thump |
| GN-42 | Hutch, run and bowls | Wire hutch with hay, ramp, water bottle | Props |
| GN-43 | Other small pets | Hamster, guinea pig, ferret, pet rat, turtle (cage, tank, or terrarium) | Idle loops, wheel running |
| GN-44 | Goldfish and fish tank; aquarium | Tank with light, filter hum | Swim loop (also see GN-77) |
| GN-50 | **Pet birds**, in cages or on a perch | Budgie, canary, cockatiel, parrot (loud, can repeat words), finch | Hop, preen, sing, squawk, flutter; **a parrot repeating a human voice is a Mimic-style gag** |
| GN-51 | Bird cages and stands, perches, feeders | Props | |
| GN-52 | **Songbirds**, wild | Sparrow, robin, cardinal, blue jay, wren, finch | Perch, hop, peck, sing, take off in a flock (**flushes when a player gets close: a free, soft alarm**) |
| GN-53 | Pigeons, doves | Town squares, barn rafters | Strut, coo, flock-flush |
| GN-54 | Crows, ravens, magpies | Perched on the scarecrow, fences, wires | Caw, hop, take off in a flock |
| GN-55 | Seagulls | Town, dump, lake | Scavenge, squawk, steal |
| GN-56 | Swallows | Barn eaves, nests | Flit, nest |
| GN-57 | Woodpecker | Tree line | Drum on a tree (a puzzling noise) |
| GN-58 | **Owl** | Barn owl and horned owl; perched, flying | Hoot, swivel head, glide |
| GN-59 | Hawk, eagle, vulture | Soaring overhead; vulture in the desert | Circle, dive, screech |
| GN-60 | Hummingbird, bird feeder visitors | *Proposed*, garden dressing | Hover |
| GN-70 | Bats | Flying (flock) | Flutter loop |
| GN-71 | Deer | Doe, buck, fawn | Graze, alert, bolt (tree-line cameo) |
| GN-72 | Fox, raccoon, skunk, opossum, coyote | Wild | Sneak, scavenge (knock over bins), spray (the comedy), howl |
| GN-73 | Squirrel, chipmunk | Trees, fences | Dart, chatter |
| GN-74 | Mice, rats | Barn, cellar, dumpsters | Scurry |
| GN-75 | Snakes, lizards, toads, frogs | Grass, pond, desert | Slither, hop |
| GN-76 | Insects: moths, fireflies, crickets, flies, bees, dragonflies | Mostly audio and particles; a small mesh for each | Loops |
| GN-77 | Fish | Pond, creek, lake | Swim loop |
| GN-80 | **Reaction poses** per rig (quadruped, bird, small animal) | Calm, curious, uneasy, alarmed, flee, one set per rig, readable at a distance | Lie down relaxed, nuzzle, head up, ears back, hackles, stare, back away, panic run |
| GN-81 | Animal **mood icons**, world-space | Calm, curious, uneasy, alarmed | Small icon above the head, only for animals the player is near |
| GN-82 | Animal **treats and lures** | Bone, cat-food tin, hay flake, carrot, apple, seed bag | Props, pick-up |
| GN-83 | Calm-aura VFX, per race | A soft pulse | Plays when a race is calming animals |
| GN-84 | Alarm calls per species | Audio, not Blender | Bark, meow/hiss, moo, squawk, bleat, whinny, squeal |

### 4.4 Vehicles (`GV-`)

Each has interior-visible parts only where needed (driver seat for AI), lights that really light (headlights,
brake lights, light bars), doors that open, and a "loading seat" for captured players.

| ID | Vehicle | Used for | Pri |
|---|---|---|---|
| GV-01 | **Pickup truck** (farm, 2 colours) | Cover; the alarm and horn (Possess) | P0 |
| GV-02 | Sedan, family car (2) | Civilians, town | Later |
| GV-03 | Station wagon / minivan | Civilians | Later |
| GV-04 | Delivery van, mail truck | Town | Later |
| GV-05 | Semi truck, trailer | Highway | Later |
| GV-06 | Motorcycle, ATV | Wanderers, farm | P2 |
| GV-07 | **Sheriff cruiser**, deputy variant | Tier 1; **capture vehicle** | P1 |
| GV-08 | State police cruiser | Reinforcement | Later |
| GV-09 | **FBI van** | Tier 2; capture vehicle | P1 · `GV_Police_FBI_Van_01` (#19) |
| GV-10 | **FBI SUV** | Tier 2 | P1 |
| GV-11 | FBI command trailer / RV | Tier 2 base | Later |
| GV-12 | Helicopter (FBI/military) | Searchlight | Later |
| GV-13 | **MIB black sedan** | Tier 3 | Later |
| GV-14 | Military jeep, truck, APC | Base | Later |
| GV-15 | Ambulance, fire truck | Town responses (*proposed*) | Later |
| GV-16 | Tow truck | Town | Later |
| GV-17 | **FBI drone** | Tier 2 | P2 |
| GV-18 | Hovering MIB craft, black helicopter | Area 51 | Later |
| GV-20 | Tractor | Farm and global rural | P0 |
| GV-21 | Combine harvester | Big cover, farms | P2 |
| GV-22 | Forklift, golf cart, ride-on mower | Town and base | Later |
| GV-30 | **Crashed ship** (global shell, a kit of damage per map) | Home base | P0 |
| GV-31 | Mothership, escape pod | Area 51 endgame | Later |

### 4.5 Tools, hand props and containers (`GT-`)

Most are **knockable**: a rigidbody with a noise component, so a bump makes a sound (#9). One prefab base, many meshes.

| ID | Group | Items |
|---|---|---|
| GT-01 | Garden and farm tools | Rake*, shovel*, pitchfork, hoe, spade, scythe, axe, sledgehammer, hand saw, pruning shears, wheelbarrow cart*, watering can, garden hose and reel, sprinkler (*remake of the pack's) |
| GT-02 | Workshop tools | Hammer, wrenches, screwdrivers, pliers, drill, welder and mask, vise, grinder, ladder (step, extension), toolbox, jack, tyre iron, air compressor, work lamp, extension cord reel |
| GT-03 | Containers | **Bucket***, **barrel***, **box*** and crate, crate stack, milk can, jerrycan, feed sack, tin cans, paint cans, trash can, dumpster, cardboard boxes, plastic bins, shopping cart |
| GT-04 | Rope and fixings | Rope coil, chain, hooks, tarp, cinder blocks, pallets, bricks |
| GT-05 | Wood | **Log***, firewood stack, chopping block, planks, stool* |
| GT-06 | Hay and feed | **Hay bales (round, square)***, loose hay, feed bag, grain scoop |
| GT-07 | Sports and play | Football, bat, bike, toy truck, doll, swing (kid's props) |
| GT-08 | Small litter | Bottles, cans, cups, newspapers, cigarette butts, paper plates (cheap decals/meshes) |

### 4.6 Household and furniture (`GH-`)

Reusable in every house, motel, diner, office and base.

| ID | Group | Items |
|---|---|---|
| GH-01 | Seating | Chair (kitchen, dining, office), armchair, **rocking chair***, sofa, bench, bar stool, bed stool |
| GH-02 | Tables | Dining, coffee, side, desk (wood, office, metal), workbench, counter, bar |
| GH-03 | Beds | Double, single, bunk, child's bed, cot, hospital bed, gurney |
| GH-04 | Storage | Wardrobe, dresser, nightstand, bookcase, cabinet, shelf, locker, filing cabinet, safe, chest |
| GH-05 | Kitchen | Stove, fridge, sink, dishwasher, microwave, toaster, kettle, pots, plates, mugs, cutlery, bread box |
| GH-06 | Bath | Toilet, sink, tub, shower, mirror, towel rail |
| GH-07 | Soft | Rug, curtains (open/closed), pillow, blanket, cushion |
| GH-08 | Wall and surface | Framed picture, clock, calendar, photos, mirror, shelves, bulletin board, newspaper clippings, posters |
| GH-09 | Heating and utilities | Fireplace, wood stove, boiler, water heater, fuse box, radiator, air conditioner |
| GH-10 | Office and lab | Computer desk, monitors, whiteboard, microscope, lab bench, cabinets, server rack |
| GH-11 | Food and drink | Diner counter, stools, jukebox, coffee machine, menus, cooler, vending machine |
| GH-12 | Doors and windows (kit-compatible) | See §4.12 |

### 4.7 Electronics (`GE-`): Energy Being targets

| ID | Item | Possess / Jam use |
|---|---|---|
| GE-01 | **Landline phone** (wall, desk, rotary) | Jam; wipe by possessing |
| GE-02 | Mobile phone (with a photo slot) | Wipe a photo, Jam a call |
| GE-03 | Radio, CB, police radio | Jam backup |
| GE-04 | **TV** (CRT, flat) | Possess for a distraction |
| GE-05 | Truck/car alarm and horn | Possess to pull a human away |
| GE-06 | Security camera, motion sensor | Possess or avoid |
| GE-07 | Computer, terminal | Lab and base |
| GE-08 | Light switches, breaker/fuse box, generator | Power links |
| GE-09 | Vending machine, jukebox, pager | Town |
| GE-10 | Radio tower, cell tower | Sabotage objective |
| GE-11 | Traffic light, crossing signal | Town |
| GE-12 | Drone, speaker, intercom | Escalation |

### 4.8 Gear carried by humans and aliens (`GG-`)

| ID | Item | For |
|---|---|---|
| GG-01 | **Flashlight** (farmer, deputy, FBI variants) | Beam hurts Shadow Entities |
| GG-02 | **Tranq rifle**, dart, pistol | Down a crewmate (non-lethal) |
| GG-03 | **Net gun**, net | Capture |
| GG-04 | Handcuffs, zip-tie | Capture state |
| GG-05 | **EMF meter**, scanner, thermal camera | FBI vs Energy Beings |
| GG-06 | Radio handheld, earpiece | Calling backup |
| GG-07 | Clipboard, evidence bags, **evidence flags and tent** | FBI collecting traces |
| GG-08 | Camera, binoculars, night-vision goggles | FBI/MIB |
| GG-09 | **MIB alien detector** | Tier 3 |
| GG-10 | Neuralyzer-type memory device | *Do not copy the film prop:* design an original device |
| GG-11 | Floodlight tripod (portable) | FBI Tier 2 |
| GG-12 | Alien carry items: **specimen jar, crate, containment pod, beacon**, carried item visuals | The crew |
| GG-13 | Ship tools: scanner, repair tool | Crew |

### 4.9 Lighting fixtures (`GL-`)

A light prefab is a mesh, a real light, an emissive material and the components Shadow Entities and Energy
Beings act on (Blackout target, flicker, a "lit" source for light-level sampling #7).

| ID | Fixture |
|---|---|
| GL-01 | **Yard/utility pole lamp** (tall, 14 m) |
| GL-02 | **Floodlight** (wall-mounted, 12 m) and **portable floodlight tower** |
| GL-03 | **Porch light**, wall lantern |
| GL-04 | **Bare bulb** on a cord, with a swing; workshop |
| GL-05 | **Gate lamp** and street lamp |
| GL-06 | Ceiling lights: bulb, fluorescent tube, shaded lamp, chandelier, recessed |
| GL-07 | Table and floor lamps, night light |
| GL-08 | **Window glow** (a light with a window cutout) |
| GL-09 | Lantern, kerosene lamp, candle |
| GL-10 | Neon sign, diner sign |
| GL-11 | **Flashlight beam** (cone + flicker) |
| GL-12 | Vehicle headlights, brake lights, **police light bar**, FBI strobe |
| GL-13 | Screen glow (TV, monitor) |
| GL-14 | Emergency light, runway lights, base searchlight |
| GL-15 | Campfire, bonfire barrel, fireplace glow |

### 4.10 Streets, boundaries and infrastructure (`GI-`)

| ID | Item |
|---|---|
| GI-01 | **Fences**: wood post-and-rail*, picket, wire, barbed wire, chain-link, electric wire, farm **gate*** and swing gate, cattle grid, corner and end posts |
| GI-02 | **Utility pole**, crossarm, transformer, power line and **phone line span** (a cuttable state)*: `GL_UtilityPole_01`, `GL_UtilityPoleCorner_01`, `GL_UtilityPoleTransformer_01` and `GL_ServiceEntry_01` (meter box, riser and weatherhead); the wires are generated in the editor (`FarmsteadPowerLines.cs`) |
| GI-03 | Road: asphalt, dirt road, markings (centre line, edge), shoulder, curb, speed bump |
| GI-04 | Road signs, mile marker, stop sign, cattle-crossing sign, "no trespassing", "beware of dog" |
| GI-05 | Mailbox, newspaper box, bus stop |
| GI-06 | Culvert, ditch, bridge, guard rail |
| GI-07 | Barriers: roadblock barrier, cones, sawhorses, police tape |
| GI-08 | Water: well*, pump, hydrant, water tower, trough |
| GI-09 | Garbage bins and dumpster, recycling |
| GI-10 | Benches, picnic table, playground (swing, slide) |
| GI-11 | Railroad crossing sign, tracks |
| GI-12 | Fuel pump, pay phone, ATM |
| GI-13 | Walls: stone wall, concrete barrier, base perimeter, razor wire (Area 51) |

### 4.11 Vegetation and ground (`GB-`)

| ID | Item |
|---|---|
| GB-01 | Trees: oak, pine, birch, dead tree, apple tree, willow, palm (desert), stump |
| GB-02 | Bushes, hedge, tall weeds, wildflowers, cactus (desert), tumbleweed |
| GB-03 | **Crops**: corn stalk and strip, wheat/hay, soybean, vegetable garden, pumpkins, orchard row, sunflowers |
| GB-04 | Grass tufts (short and tall, as Terrain details), moss |
| GB-05 | Rocks (boulder, pebble, flagstone), log, branch |
| GB-06 | Ground material set: short grass, long grass, dirt, packed dirt, gravel, mud, sand, tilled soil, snow, asphalt, concrete, wood, linoleum, carpet (also the **footstep surface** types) |
| GB-07 | Sky: night skybox, dusk, dawn, clouds, stars, moon |

### 4.12 Modular building kit (`GK-`), global

Sized to the metrics in `farmstead.md` (doors 1.2 × 2.2 m, ceilings 2.7 m, stairs 0.18 × 0.28 × 1.0 m, corridors at
least 1.5 m). About **40 pieces**, in re-skinnable materials: **clapboard house**, **red barn board**, **corrugated
metal**, **brick (town)**, **concrete (base/lab)**.

| Group | Pieces |
|---|---|
| Structure | Wall (solid, door gap, window gap, wide gap), corner, T-junction, half wall, foundation, floor tile, ceiling tile, loft floor, beam, roof ridge/slope/end, gable |
| Openings | Interior door, exterior door, **screen door**, double door, sliding barn door, garage door, **cellar storm doors**, loft door, window frames (single, double, sash), glass states (clean, broken) |
| Circulation | Stair run, cellar stair, **ladder**, porch steps, ramp, handrail |
| Trim | Skirting, door trim, porch rail, chimney, gutter, vent, shutter, awning |

### 4.13 Traces and decals (`GD-`)

| ID | Item |
|---|---|
| GD-01 | **Footprints**, one per race, fading |
| GD-02 | **Scorch marks**, burn, ion mark |
| GD-03 | **Crop circle**, trampled corn/grass |
| GD-04 | **Dropped objective marker** |
| GD-05 | Broken glass/bulb; the "lights killed" state |
| GD-06 | Slime/residue, per race |
| GD-07 | **Beam residue ring** (Tractor Beam) |
| GD-08 | Missing-livestock marker: **empty stall**, broken fence |
| GD-09 | **Cut phone line**, opened and damaged door states |
| GD-10 | World-space markers: **ping**, suspicion icons (`?` `!`), objective markers, a downed-player marker (mostly UI, #10) |

### 4.14 VFX (`GX-`)

Fog, ground mist, dust motes, fireflies and moths around lights, rain and puddle ripples, snow, wind in grass,
smoke (chimney, exhaust), sparks, volumetric headlight cones (cheap cone mesh), light-bar strobes, explosions
(small), footstep puffs per surface, corn rustle puffs, **ship beacon pulse**; and per race ability: **Tractor
Beam**, **Missing Time**, **Shadow Step**, **Blackout**, **Possess**, **Jam**, plus Later: Suggestion, Disguise,
Pounce, Burrow, Become Object, Lure, Copy Voice. Detail belongs to #24.

### 4.15 Audio (`GS-`)

| Group | Content |
|---|---|
| Ambience beds | Night rural, wind, rain, thunder, town hum, base hum, forest, desert |
| Wildlife and animals | Crickets, owls, frogs, distant dog, cow, horse, sheep, pig, chicken, goat, goose, rooster, bats, crows; per-animal alarm calls |
| Footsteps | Grass, gravel, packed dirt, mud, wood, concrete, linoleum, carpet, metal, corn rustle, hay |
| Doors and objects | Door (open, close, slam, creak), screen door, gate, bucket, tool clank, crate, glass, drawer, toggle |
| Vehicles | Truck, tractor, cruiser, siren, FBI van, helicopter, drone |
| Humans | Comedic barks for each faction, sheriff and FBI radio chatter, screams, snores, sighs; **voice lines are a recording job, not Blender** |
| Alien | One set per ability, ship hum, bank and launch stings |
| Music | Threat-tier stings, per-map ambient music |

## 5. Farmstead assets (`FM-`)

What the Farmstead needs *on top of* the global list. Locations are from `farmstead.md`.

### 5.1 Terrain and layout

| ID | Asset | Notes | Pri |
|---|---|---|---|
| FM-T1 | **Terrain**: 180 m play area plus ~40 m of hills and trees, ±1.5 m relief, flat pads under each building (replaces the 200 × 200 `Plane`) | Unity Terrain, painted with GB-06 layers | P0 |
| FM-T2 | ~~**Crash furrow**: scorched trench from the ship to the ship part~~ | Dropped on the Farmstead: the path made no sense; the corn grows up to the ship | n/a |
| FM-T3 | Two **tractor paths** through the cornfield | Routes | P0 |
| FM-T4 | **Driveway and county road**: gravel driveway, culvert, ditch | Where escalation arrives | P0 |
| FM-T5 | **Yard**: packed dirt with ruts and worn paths | Hub | P0 |
| FM-T6 | Pond with reeds, a dock (*proposed*); a creek | Energy Beings short out in water | P2 |
| FM-T7 | Ground clutter: puddles, hay scatter, feathers, manure patches | Dressing | P2 |

### 5.2 Buildings

| ID | Building | Notes | Pri |
|---|---|---|---|
| FM-B1 | **Farmhouse**: 2 floors and cellar, porch and steps, back door, side door (mudroom), west storm doors, chimney, gutters | From the kit; objectives 4 and 5 | P0 |
| FM-B2 | **Barn**: ten stalls, aisle, tack room, 8 m sliding doors (west, lit), rear door (east), hayloft, loft door and pulley, rafters | From the kit; objective 2 | P0 |
| FM-B3 | **Workshop**: one door, one back window, bare bulb, corrugated roof | From the kit; objective 3 | P0 |
| FM-B4 | **Silo** (*remake*) | Landmark | P0 |
| FM-B5 | **Windmill** with turning blades (*remake*) | Landmark, owl perch | P1 |
| FM-B6 | Shed, old shed (*remake*) | Cover | P1 |
| FM-B7 | **Chicken coop** with run (*remake*), nesting boxes, roosts | Noise trap | P0 |
| FM-B8 | Outhouse (*remake*) | Hiding place | P1 |
| FM-B9 | Well (*remake*) | Mud, cover | P1 |
| FM-B10 | **Dog house** | Beside the porch | P0 |
| FM-B11 | Carport / equipment lean-to | Parking | P2 |
| FM-B12 | Stable (horses), with stalls | Alternative to barn stalls | P1 |
| FM-B13 | Pig sty with mud wallow | Pen | P1 |
| FM-B14 | Sheep shelter and pen | Pen | P1 |
| FM-B15 | Goat pen and shed | Pen | P2 |
| FM-B16 | Duck/goose house and pond | Pen | P2 |
| FM-B17 | Grain bin / feed shed | Dressing | P2 |

### 5.3 Livestock structures and farm fittings

| ID | Item |
|---|---|
| FM-L1 | **Cow corral** and gates; **paddock** for horses; **sheep pasture** fence |
| FM-L2 | **Stall** (half-door, kick board, feed slot) ×10; stall gates |
| FM-L3 | **Feed troughs*** and bunks, **water troughs**, salt lick, hay rack, round-bale feeder |
| FM-L4 | Milking stand, bucket rack, feed bins |
| FM-L5 | Hay pulley and loft rope; hay hook |
| FM-L6 | Pasture gate and latch; electric fence charger (comic) |

### 5.4 Interiors (all props from the global lists plus these specifics)

| Room | Items |
|---|---|
| Kitchen | Table, four chairs, stove, fridge, sink, cabinets, wall clock, kettle, back door with screen |
| Dining | Table, sideboard, family photos |
| Mudroom | Coats and hooks, boots, **dog bed**, umbrella stand |
| Hall | Runner, coat stand, stairs, pictures |
| Living room | Sofa, armchair, rocking chair, coffee table, **TV**, **landline phone**, **desk with the photo**, bookshelf, fireplace |
| Farmer's room | Bed, wardrobe, nightstand, wall radio |
| Bathroom | Toilet, sink, tub, mirror |
| Kid's room | Bed, toys, desk, **alien drawings**, night light |
| Landing | Window onto the porch roof, rug |
| Cellar | **Fuse box**, jar shelves, boiler, tools, crates |
| Barn ground | Stalls, tack (saddle, harness), tractor, pitchforks, milk cans, lantern |
| Hayloft | Hay bales, **open drop**, loft door with pulley, ladder |
| Workshop | **Generator** (objective 3), workbench, vise, pegboard, tyres, drums, shelves, toolbox, bare bulb |
| Story details (#42) | UFO newspaper clippings, tinfoil on one window, thermos and radio, a hand-lettered sign |

### 5.5 Objectives and ship

| ID | Asset | Pri |
|---|---|---|
| FM-O1 | **Crashed ship** set up on the farm (GV-30): hull, damage, ramp, beacon; the **race-select, bank and launch terminals** | P0 |
| FM-O2 | **Ship part** (glowing, carriable) | P0 |
| FM-O3 | **Power cell** (glowing, carriable), generator slot | P1 |
| FM-O4 | **Photo** (framed) and the photo-on-phone | P1 |
| FM-O5 | **Cow** objective marker on stall 1 (GN-01) | P0 |
| FM-O6 | **Phone line pole and line** (GI-02) on the driveway side | P0 |
| FM-O7 | Carried-item visuals (in hand, hovering for Greys) | P1 |

### 5.6 Farm vegetation and landmarks

| ID | Asset |
|---|---|
| FM-V1 | **Corn stalk** and **corn strip** (4 m of ~20 stalks as crossed cards); ~5,700 m² of field, roughly 1,800 strips |
| FM-V2 | Corn **vision-blocker and rustle volumes** (invisible; #39) |
| FM-V3 | Trampled corn and broken stalks (a trace) |
| FM-V4 | **Scarecrow** in the field (landmark, a joke) |
| FM-V5 | Tree line: oak, pine, dead tree at the crash site |
| FM-V6 | Vegetable garden |
| FM-V7 | Hedge and bushes at the house |

### 5.7 Farm machinery

| ID | Asset | Pri |
|---|---|---|
| FM-M1 | **Generator** (workshop) with the power-cell slot, hum, light link | P0 |
| FM-M2 | Hay wagon / flatbed trailer | P1 |
| FM-M3 | Plough, harrow, baler | P2 |
| FM-M4 | Fuel tank and pump | P2 |
| FM-M5 | Irrigation pipe and sprinkler | P2 |
| FM-M6 | Water tank | P2 |

(The truck, tractor and combine are global: GV-01, GV-20 and GV-21.)

### 5.8 Farm lights (positions from the design)

| ID | Fixture (see §4.9) | Position / reach |
|---|---|---|
| FM-LT1 | Yard pole lamp | (0, −25), 14 m |
| FM-LT2 | Barn floodlight | above the big doors, 12 m |
| FM-LT3 | Porch light and living-room window glow | (−50, −54), 9 m |
| FM-LT4 | Workshop bare bulb | (16, −52), 6 m |
| FM-LT5 | Gate lamp | (−2, −91), 6 m |
| FM-LT6 | Moon (directional, dim, cool blue) | scene |

## 6. Counts

Rows with an ID, per section. A row often bundles several models (GT-01 alone is about 14 tools), so the number
of individual models is several times higher; the per-model tracker comes when work starts.

| Section | ID rows |
|---|---|
| People (`GP`) | 48 |
| Aliens (`GA`) | 9 |
| Animals (`GN`) | 50 |
| Vehicles (`GV`) | 23 |
| Tools and props (`GT`) | 8 |
| Household (`GH`) | 12 |
| Electronics (`GE`) | 12 |
| Gear (`GG`) | 13 |
| Lights (`GL`) | 15 |
| Streets and infrastructure (`GI`) | 13 |
| Vegetation and ground (`GB`) | 7 |
| Traces and decals (`GD`) | 10 |
| **Global total** | **220** |
| Farmstead (`FM`) | 56 |

The kit (§4.12), VFX (§4.14), audio (§4.15) and the interiors table (§5.4) are grouped lists without IDs.

## 7. Budget (proposed, to be set by #45)

The per-class triangle numbers are **replaced by §2.1** (proposed, issue #344); the table below keeps the older class list for the counts, and the scene total under it is what stays here. Where the two differ, §2.1 wins.

| Class | Triangles each | Count (rough, farm) |
|---|---|---|
| Hero buildings (house, barn, workshop) | 15–40k with the kit | 3 |
| Vehicles and machines | 3–12k | ~10 |
| People | 3–6k, LOD to 1.5k | ~10 at once |
| Animals | 0.8–6k (birds and small pets under 1k) | ~40 |
| Props and tools | 100–1,500 | ~200 |
| Corn strip | 150–400 | ~1,800 instanced |
| Trees | 500–3,000 | a few hundred instanced |

Target for the visible scene: roughly 1–2 M triangles, ≤ 100 materials, a few real-time shadowed lights. Placeholder
numbers until the Deck is measured. Shared palette textures keep the LFS footprint small.

## 8. Phasing

| Phase | Milestone | What is built | Exit |
|---|---|---|---|
| 0 | 0.2 (now) | Graybox gameplay prefabs for all P0: lights, corn volumes, a quadruped and a biped placeholder, truck, tractor, generator, ship, doors, farmer and dog capsules | Map plays; stealth can be tested |
| 1 | 0.2 | Blender style set in stone with one test of each kind (one person, one animal, one vehicle, one kit room, one prop); palette; the export pipeline | Pipeline works end to end (style answered: low-poly, §2.1) |
| 2 | 0.2 → 0.3 | Final **farmer, kid, dog, cow, chickens**, truck, tractor; kit rolled out to all three buildings; terrain; corn | No placeholder art on the critical path |
| 3 | 0.3 | Sheriff, deputy, FBI agents and vehicles; traces and decals; objective props; phone line; alien bodies | Escalation is readable |
| 4 | 0.3 → polish | Remaining livestock and pens, interiors (#42), story details, VFX, audio (#24) | Every room readable without text |
| Later | 0.4+ | Remaining races, MIB, town, base, Area 51 cast and props | |

## 9. Open questions

- **Retire the MarpaStudio placeholders** once replaced? (Recommended.)
- **Style:** ~~stay low-poly and one shared palette?~~ Answered by the owner on 2026-10-23 (#344): better-made low-poly, one shared palette (§2.1). #43 stays open for the rest of the art direction.
- **Livestock:** the level doc says the pasture is empty at night; with penned, field and roaming animals that no
  longer holds. Update `farmstead.md`? How many roaming animals before the NavMesh load and noise get annoying?
- **Pets and strays:** can a player befriend a stray (feed it to keep it quiet or pull it along)? Should a pet
  parrot repeat what it hears, including crew voice chat? Do cats and dogs get a coat-per-owner so a family's pet
  is recognisable across maps?
- **Is the objective cow fixed in barn stall 1, or any cow?** A random one would need the cow list to be data.
- **People:** one shared rig and modular bodies (recommended) vs. bespoke models per character. Do we want
  a spouse and grandparent on the farm, and how many humans can the AI and Deck afford at once?
- **Weather:** is rain in the first release, or only fog? It adds wet surfaces, puddles and VFX.
- **Tone:** the crew is non-lethal, so police carry tranq and net guns, not firearms. The farmer has no shotgun. Agreed?
- **Original designs:** the Neuralyzer-like memory device (GG-10) and the MIB look should be our own, not copies of a film's props.
- **Where do `.blend` sources live?** `art/blender/` plus `.blend` in LFS, or only the exported FBX and the Python that built it?
- **Audio and voice** are not Blender jobs: recorded, purchased or generated? Needs an owner.

## 10. Blender status (first pass, 2026-10-20)

First models exist for the rows below, built by scripts in [`art/`](../../art/README.md) in the **faceted** house style (flat,
hard-edged, no subdivision, one shared palette), exported to `Assets/Art/`. They are placeholders to react to. They import in Unity
through `Assets/Editor/ArtImportRules.cs` (one shared material, point-filtered palette, humanoid avatars for people, looping idle and walk
clips); the shared material, avatars, clips and axes were checked there. Not listed means not started.

| Group | Started |
|---|---|
| People `GP-` | Base person on the Universal Animation Library skeleton (its CC0 clips play on it); **GP-30** Farmer, **GP-31** kid, **GP-32** spouse, **GP-33** grandparent, **GP-35** Sheriff, **GP-36** Deputy, **GP-38** FBI agents (two), **GP-43** Man in Black, a worker, a waitress |
| Aliens `GA-` | **GA-01** Grey and **GA-02** Shadow Entity (humanoid rig), **GA-03** Energy Being (static, glow colour), the Nordic and the Reptilian (humanoid rig), the Insectoid (its own 17-bone rig, with Idle, Walk, Run and Carry clips) |
| Animals `GN-` | **GN-01** cow, **GN-02** horse, **GN-03** sheep, **GN-04** pig, **GN-05** chicken hen, **GN-06** goat, **GN-09** turkey tom and hen, **GN-20/21/24** eight dog breeds, **GN-30..33** eight cat coats, **GN-71** deer (doe, buck, fawn), **GN-72** raccoon, opossum, skunk and fox, and a black bear; walk and idle for every quadruped (and trot and run for the dogs), the tom turkey's Display; no other bird clips yet |
| Vehicles `GV-` | **GV-01** pickup, **GV-20** tractor, **GV-07** sheriff cruiser, **GV-30** crashed ship, and a generated family of cars (sedan, wagon, SUV, minivan, van, taxi, ambulance, tow truck, ATV, motorcycle) in civilian paint jobs plus sheriff, state police, FBI and Man in Black liveries, each New and Damaged (106 files) |
| Tools and props `GT-`, `GI-`, `GL-`, `GE-` | rake, shovel, pitchfork, bucket, barrel, crate, milk can, jerrycan, feed sack, stool, firewood stack, hay bales (square and round), wheelbarrow; fence section, gate, mailbox; bare bulb, pole lamp; landline phone |
| Modular kit `GK-` (section 4.12) | On a 3 m grid, metrics from `farmstead.md`: walls (solid, door, window, double window, wide gap, half, low), corner post and T pillar, floor tile and planks, ceiling tile, foundation block, loft floor, beam, roof slope, ridge, gable end, gutter; doors (interior, exterior, screen, double, sliding barn, garage, cellar storm, loft; hinge-pivoted leaves), windows (single, double, sash, broken), shutters, awning; stairs (run, cellar, porch), ladder, ramp, handrail; skirting, porch rail, chimney, vent, skylight, floor grate. Wall-type pieces come in six skins |
| Household `GH-` | **GH-01** seating (kitchen, dining and office chairs, armchair, rocking chair, sofa, bench, bar stool), **GH-02** tables and desks, workbench, kitchen and bar counters, **GH-03** beds (double, single, bunk, child, cot, gurney), **GH-04** storage (wardrobe, dresser, nightstand, bookcase, cabinet, locker, filing cabinet, safe, chest, wall shelf), **GH-05** kitchen (stove, fridge, sink, microwave, toaster, kettle, pot, plates, mug, bread box), **GH-06** bath (toilet, sink, tub, shower, mirror, towel rail), **GH-07** rug, curtains, pillow, blanket, cushion, **GH-09** fireplace, wood stove, boiler, water heater, fuse box, radiator, air conditioner, **GH-10** whiteboard, lab bench, server rack, microscope, **GH-11** jukebox, vending machine, coffee machine, cooler |
| Home styles (for different homes) | Every household and decor piece above also exists as **Modern** (white, grey, black, light oak, steel), **Retro** (orange, avocado, mustard, teak, chrome) and **Damaged** (grey, rusted, stained, tilted, parts missing: for the trailer park and abandoned houses), under `Household/<Theme>/` and `Decor/<Theme>/`. Bespoke shapes for the hero pieces (sofa, armchair, chairs, tables, bed, TV, lamps, fridge, stove, clock, bookcase, wardrobe, dresser, nightstand, rug), bespoke wrecks (slashed sofa, smashed CRT, rusty open fridge, overturned table, tipped bookcase, fallen lamp, torn curtains, mattress on the floor), and a boarded-up window in the kit |
| Decor and small items | table, floor, desk and ceiling lamps, chandelier, kerosene lamp, candle, neon sign (`GL-06/07/09/10`); CRT and flat TVs, retro, CB and handheld radios, mobile and rotary phones, security camera, light switch, monitor, keyboard, computer, laptop, intercom (`GE-`); frames, standing photo, clock, calendar, bulletin board, newspaper clippings, poster, kid's alien drawing, trophy, mirror (`GH-08`); houseplants, flowers; teddy, doll, toy truck, football, blocks (`GT-07`); books, newspaper, mail; umbrella stand, coat hooks, boots, doormat, bin, laundry basket, ironing board, broom, mop, fire extinguisher, first aid, toolbox, flashlight, thermos, lunchbox, suitcase, backpack, picnic basket, tinfoil window, hand-lettered sign |
| Ships and ship parts `SH-` | scout, dart, cigar ship, black triangle, escape pod, probe drone, dropship, MIB craft, mothership (`GV-31`), debris and scorched ground, the abduction UFO (`SH_AbductionUfo_01`), the ship's control panels (console, bank and launch terminals) and the alien set dressing for its inner wall (`GV_Ship*`: stasis pod, jars, couch, lockers, tool rack, sample rack, conduit, holo-map table); carriable parts: power cell (`FM-O3`), hull panel (`FM-O2`), nav crystal, engine coil, thruster nozzle, fuel canister, shield emitter, comms array, black box, warp ring segment, landing leg, console module, beacon (`GG-12`), specimen jar, containment pod; repair tool and scanner (`GG-13`), translator |
| Interactive appliances and storage | **Fridge, stove, microwave, toaster, washer, dryer, kitchen counter, bread box, wardrobe, dresser, nightstand, cabinet, locker, filing cabinet, safe, chest, suitcase, toolbox, medicine cabinet, fuse box, vending machine, cooler, dumpster, trash can, mailbox** with hinged doors, sliding drawers and lids as separate pivoted parts and `Slot_` empties for what goes inside, in Classic, Modern, Retro and Damaged (ajar); `art/data/interactions.json` lists the parts and slots |
| Food, drinks and clothes (`GH-`, `GT-`) | 68 items: produce (apple, orange, banana, carrot, corn, tomato, potato, onion, lettuce, cabbage, pumpkin, watermelon), bakery (bread, baguette, pie, cake, donut), dairy (milk bottle and carton, eggs, cheese, butter), meat and prepared (steak, drumstick, fish, sausages, hamburger, hot dog, sandwich, TV dinner, pizza box, roast turkey), drinks (soda cans in three colours, beer can and bottle, water, wine, whiskey, juice box), canned and boxed goods, pet food and bones, hay, and folded and hung clothes; every fresh food also has a **Rotten** version |
| Ground and terrain `GB-06`, `GD-` | Tileable ground textures (grass in three states, dirt, gravel, asphalt and cracked asphalt, concrete, sand, snow, carpet, cobble, linoleum...), 11 decals (road lines, crosswalk, parking lines, puddle, oil stain, scorch, leaves, crop circle, alien footprint, tyre tracks) and road, sidewalk and curb pieces; `art/data/ground_surfaces.json` has tile size and footstep sound per texture |
| Farmstead `FM-` | **FM-B1** farmhouse, **FM-B2** barn, **FM-B3** workshop (exterior shells with real openings; interiors wait for the kit), **FM-B4** silo, **FM-B5** windmill, **FM-B6** shed, **FM-B7** chicken coop, **FM-B8** outhouse, **FM-B9** well, **FM-B10** dog house, **FM-M1** generator, water trough, **FM-V4** scarecrow, **FM-V1** corn strip and stalk, **FM-V5** oak, pine and dead tree, bush, boulder, stump |

Not started: traces beyond the decals above, VFX, audio beyond the clips in `CREDITS.md`, bird
clips (the tom turkey's Display apart), the cow's beam-lift and reaction poses (`GN-80`), the remaining races, and most `GP-` and `GN-` rows.
