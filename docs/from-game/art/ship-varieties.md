# Ship varieties and interior types (issue #212)

The crew's ship is no longer one model. A mission has **one variety** (the outside: a saucer, an egg, a freighter) and **one interior type** (what is on its walls: a lab,
a bridge, a cargo hold, crew quarters) that the **mission seed** picks, the same on every machine. Seed 0 is the default ship: the crashed saucer with the lab, which is what
the scene is saved with and what every batch run without `-missionSeed` gets.

| Variety | Model | Look | Interiors it offers (first = its default) |
|---|---|---|---|
| saucer | `GV_CrashedShip_01` (`vehicles.py`) | grey saucer, cyan light; fixed legs, a ramp | lab, bridge |
| egg | `GV_ShipEgg_01` (`ship_hulls.py`) | tall gold egg on four feet, violet trim, green light | quarters, lab |
| freighter | `GV_ShipFreighter_01` (`ship_hulls.py`) | a box with containers on the roof, a bridge block, three engines, hazard stripes, amber light | cargo, bridge |

| Interior type | On the walls (`ship_props.py`, `LAYOUTS`, repeated in `FarmsteadShipInterior.cs` `Plans`) |
|---|---|
| lab | stasis pods by the doorway, specimen jars (a cow, a plant, a little alien), a medical couch, lockers, tool and sample racks, cable runs, a holo-map table |
| bridge | pilots' stations (desk and chair), nav screens with a star chart, radar posts, the holo-map table |
| cargo | crates and drums on pallets, a tool rack, a cable run |
| quarters | bunks, a mess table, sleep pods, a sample rack |

## What every variety has in common (so nothing else changes)

The **walkable inside** and the **colliders** are the same for all of them: `FarmsteadBuilder.BuildLandedShip` builds the deck (0.5 m), the ring of 12 wall panels (panel 0 is
the doorway, 2.9 m wide and 2.4 m high), the ceiling (3.4 m), the ramp (2.4 m wide, 3.6 m long, from the sill at y 5.95, 0.44 m up, down to the ground) and the console once,
from `FarmsteadLayout`'s `Ship*` numbers. Each hull model is drawn over them. Every hull has the same shell inside (`ship_hulls.shell`: deck, doorway sill and jambs, wall
ring with its dark band, ceiling, two seats, the power core, a lit strip down the deck; only the colours differ), the console with the bank and launch terminals
(`terminals.py`, placed by `FarmsteadBuilder`), the safe zone, the spawn beside the ramp and the NavMesh. A new variety must keep it that way.

## The parts (for the arrival and take-off, #213)

Each hull model is **exported open**, as the ship stands once it has landed. The parts are separate objects with their origin on their pivot, listed in
`art/data/interactions.json` under the model's name (kind, axis, pivot, limit, rest):

| Part | Which | Kind | Open (the exported pose) | Closed |
|---|---|---|---|---|
| `ShipRamp` | every variety | hinge about X at the sill's outer edge, (0, -5.95, 0.44) in the model's frame | down to the ground (what the ramp collider is) | turned up 85 degrees: stands almost upright in the doorway like a drawbridge |
| `ShipLeg_1` .. `ShipLeg_4` | egg (1.2 m of travel) and freighter (1.5 m) | slide along Z | out, the pad on the ground | pulled up into the hull (egg) or against its side wall (freighter) |

The saucer has the ramp part and four **fixed** legs (the crashed ship sits on them: it settles, it does not extend legs). A variety may have no legs part.

**In Unity**: each hull carries a `ShipHullParts` (`Assets/Scripts/Props/ShipHullParts.cs`), baked by `FarmsteadShipVariants` from the JSON in Unity's axes and senses, the same
way `PropRuntime` poses a door:

```csharp
var parts = ShipVariants.Current.ActiveParts;      // the hull that is on show
parts.Pose(0f, 0f);                                // legs folded, ramp shut (flying); Pose(1, 1) is landed (the pose in the model)
parts.LegsOut = 0.6f;                              // 0 = folded in, 1 = out on the ground; HasLegs / LegCount say what there is
parts.RampOpen = 0.3f;                             // 0 = shut, 1 = down
```

Nothing is replicated by this: it only poses transforms, locally. The **ramp's collider** (a graybox block under the model) is not moved: a sequence that shuts the ramp turns
that block off, and the model's own ramp is not a collider. The model's *closed* pose is the part's `closed` value 0 and its *open* pose the `limit`, as for every prop part.

## The landing marks (no scorch)

A landed ship leaves **no burn**. Where it stands it leaves **dents**: a small round pressed-in pad under each foot with a ring of pushed-up earth round it (a hull with no feet that settles on its belly gets one shallow impression under it instead). The marks are built from **contact anchors** in the model, empties on the ground in its landed pose, so they follow the ship wherever it stands:

| Anchor (an empty in the FBX; also under `slots` in `art/data/interactions.json`, its footprint as `size`) | Where |
|---|---|
| `Slot_ShipFoot_1` ... `Slot_ShipFoot_n` | on the ground under the middle of each foot's pad (size = the pad's width and depth); the saucer's four fixed pads, the egg's and the freighter's four legs |
| `Slot_ShipBelly` | on the ground under the middle of a hull that rests on it (size = its diameter); none of the three varieties has one yet, `ship_hulls.belly_anchor` makes it |

The names are the model's interface (keep them). `FarmsteadShipMarks` (editor) builds a dent mesh under every hull's anchors (70 triangles each, two materials, no collider, children of the hull, so they are switched with it; `ShipFlight` keeps them hidden until the ship touches down and draws them from then on, also while the copy takes off and after it has gone: the ground keeps the dents); a sequence that places the ship elsewhere reads the anchors (`ShipHullParts.FootAnchors`, `ShipHullParts.BellyAnchor`) to place its own. The ground cannot be cut, so a dent's floor is at ground level and the 7 cm rim reads as the bowl.

## How the seed picks (`ShipVariants`, `Assets/Scripts/Props/ShipVariants.cs`)

`MissionSeed.Pick(seed, "ship-variety", 3)` picks the variety and `MissionSeed.Pick(seed, "ship-interior", n)` one of the `n` interiors that variety offers, so all combinations
occur. Every hull (a plain model: `FarmsteadArt.Place(..., interactive: false)`, so no `PropRuntime`, no network object, no prompt) and every interior group is built into the scene (named `Variant_ship-hull_<id>` and `Variant_ship-interior_<type>`, like the rooms' options), and all but the
chosen are switched off on every machine when the seed arrives (and back to the default when the mission ends). No race preference: a crew mixes races, so the pick is the seed's.

**Pin one** for a test: `-shipVariety egg -shipInterior bridge` on the command line (a build, the editor, a batch run: it wins over the seed), or in the editor Tools → Alien
Investigation → Ship (an editor preference, read when the mission's seed arrives; the saved scene keeps the default). A pinned interior that the variety does not offer is
ignored. A pin is a machine's own setting (the seed alone is the same everywhere): pin every machine of a multiplayer test the same. The tests ignore pins. The debug HUD (F1) shows `Ship: egg + bridge`.

## Checks

- `FarmsteadSelfTest` runs for **every variety and interior it offers** (6 combinations): the doorway is open and centred (rays through the hull mesh), the floor is there
  under the room, the ramp shuts and the legs fold (and come back), every piece of the interior is on the deck, under the ceiling, inside the wall ring with its back on the wall
  and clear of the doorway lane, console, seats, power core and the 2.5 m walking circle, has a collider and stays out of the NavMesh; and the seed picks every variety and
  interior, the same each time, and the default ship for seed 0.
- `ObjectiveSmokeTest` checks that the ship on show is the seed's (or the pin's) pick, with exactly one hull and one interior switched on. Run it with `-shipVariety` /
  `-shipInterior` to play the mission loop in each.
- `art/scripts/audit_props.py` audits `ship_props.py` and `ship_hulls.py` too (floating parts, rods through parts, origin and the front). A hull's skins are written straight
  into the mesh, which the audit's recorder cannot see, so floating and the origin are not checked for the two new hulls (see `HULL` in the audit).

## Adding a variety or an interior

**A variety**: a function in `ship_hulls.py` that calls `shell()`, `door_frame()`, `ramp()` and (if it has them) `leg()`, cuts the doorway out of its skin with `skin()` and
`front_faces()` (or builds a doorway tunnel through its walls: see the freighter), and goes into `HULLS`; export it (the script writes the parts into `interactions.json`); one line in
`FarmsteadShipVariants.Varieties` (id, model, the interiors it offers). The self-test then checks it with each of them. It must keep the doorway centred on the front (-Y), its
skin outside the shell (r 5.2 to 5.9), a ramp part, and the ground at z 0.

**An interior type**: its props in `ship_props.py` (a few hundred triangles each, the shared palette, `Prop`; print `Back`: how far the back is behind the origin) and a plan in
`LAYOUTS` and in `FarmsteadShipInterior.Plans`/`Models`/`Types`; the varieties list it in `FarmsteadShipVariants.Varieties`. Panel 4 is in front of the power core (shallow pieces
only) and panel 6 has the console; the self-test measures the rest.
