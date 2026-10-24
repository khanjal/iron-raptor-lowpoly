# Buildings and structures: brief and audit

Status: first pass. Real-world sizes are from memory of typical dimensions, not checked against a source. Built from `art/scripts/buildings.py` (ported from the game repo, which has 13 buildings in 4 Global and 9 Farm folders: Farmhouse, Barn, Workshop, Shed, Coop, Outhouse, Well, Silo, Windmill, Trailer, Garage, TownHouse, Diner; the game's sibling worktrees hold the same files).

## What the site now has (13 designs, 21 models)

| Model | Footprint x height in the GLB | Real-world check | Note |
|---|---|---|---|
| Farmhouse (+ Damaged) | 25 x 10 m | a two-storey farmhouse is 10-15 x 8-10 m: large, but the game's farmstead plan says 24 x 18 | porch, chimney, holes when damaged |
| Barn (+ Damaged) | 27 x 11 m | a small dairy or hay barn is 12-30 m long | hayloft door, big front door |
| Workshop (+ Damaged), Shed (+ Damaged) | 13 x 5 m, 4 x 3.5 m | shed 3-4 m is right | |
| Chicken coop | 2.9 x 2.1 m + run | | run fence |
| Outhouse | 2.3 x 2.95 m | about 1 x 1.2 m is real; this is a walk-in hide-out for the game | **door is a moving part (`Door`)** |
| Well, Silo, Windmill | 2 m, 5 m x 15 m, 12 m tall | a farm silo is 5-8 m across, 15-30 m tall | |
| Mobile home (+ Damaged) | 17.7 x 4 m | a single-wide is 14-24 x 3.6 m: right | on piers, hitch |
| Garage, Town house, Diner (+ Damaged) | 7 x 4 m, 11 x 6.7 m, 18.6 x 7.4 m | | |

Skins (white, brick, log, stone... 15 in `SKINS`) are not built as models: they are recolours of one design, so they are paints (`NOTES.md`, "Colour variants are paints"); the base skin is shipped and the viewer's colour picker covers the rest. Only the base skin and one Damaged skin are shipped. Damaged is `WRECK` colours plus dropped wall pieces; on small buildings (barn, shed) it is mostly the rusted palette.

## Still missing (from `docs/from-game/art/prop-catalogue.csv`, category "Buildings and structures")

None of these existed in the game's art either, so they are new work, not imports: hunting blind, deer / tree stand, beehive, trellis / arbor, cold frame and greenhouse, hitching post / bike rack, mile marker, dog chain and stake, RV pad with hookups, water spigot and sewer cap, dog waste station, metal detector arch, freight elevator, aircraft hangar, overhead gantry crane, scaffold and work platforms, church bell and rope, steeple, ceiling-hung rack, pipes and valves, pond with reeds, flagstone and gravel paths. Partial: outhouse seat and garden shed (now covered by the outhouse and shed here). The catalogue's `have` items (fireplace, towel rail, coat hooks, chopping block, firewood stack, boulder) are small furniture or nature pieces handled elsewhere.

## Known issues

- `audit.py` (floating parts, run on the imported GLBs, one per model): clean for 14 of 21. Still listed: Damaged barn, farmhouse and town house (broken window glass panes left hanging, by design of the damage pass), windmill (tail vane), trailer and Damaged trailer (hitch jack and steps). The silo's ladder floated 0.07 m off the wall; fixed.
- Fences, gates, signs and the other farm structures (mailbox, doghouse) are in `props_farm.py` / `interactive.py`, not here.
