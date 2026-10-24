# Ships: brief for the import from the game

Status: this is an **import**, not a new design. These ships and their interior set were designed for the game `khanjal/alien-investigation`; the generator scripts were already in this repo (`ships.py`, `ship_hulls.py`, `ship_props.py`, `terminals.py`, `ufo.py`, `vehicles.py`) but only Scout and Dart were in the asset browser. Nothing here depends on a real-world object, so there are no real sizes to check; sizes are the game's (1 unit = 1 m, front -Y, origin on the ground; the flying craft hover above their origin, as Scout and Dart do). Design notes: `docs/from-game/art/ship-varieties.md`, `terminal-notes.md`.

## Not built here
Boats (canoe, rowboat, boat on trailer, kayak): the game's catalogue lists them as `missing`; no generator exists for them. They need a real brief (canoe about 4.9 m, 0.8 m beam; 14 ft aluminium rowboat about 4.3 m; kayak 2.7-3.7 m) and are left for a later change. The alien tech parts (power cell, hull panel, engine coil...) are `ships.py` groups `parts`, `tools`, `debris` and belong to the alien-tech import.

## Added
| Group | Models | Recognisable features |
|---|---|---|
| Small craft (`ships.py`) | Cigar, Triangle, Escape pod, Probe drone, Drop ship, Agency craft, Mothership | each one silhouette: long cylinder, flat black triangle with corner lights, capsule, floating sphere, boxy lander, dark wedge, huge carrier |
| Abduction UFO (`ufo.py`) | small saucer | dark belly with emitter, pale hull, glass dome, cyan band, six belly lamps |
| Hulls | Crashed saucer (`vehicles.py`), Egg, Freighter (`ship_hulls.py`) | walkable shell, doorway, ramp part (`ShipRamp`), legs as parts on egg and freighter |
| Interior set (`ship_props.py`) | lockers, stasis pod, jars, cable run, holo table, couch, tool rack, sample rack, helm, nav screen, radar post, crates, drums, bunk, mess table | the four interior types: lab, bridge, cargo, quarters |
| Terminals (`terminals.py`) | console, bank terminal (green), launch terminal (red) | |

Colours are palette names inside the scripts. Hull themes (egg gold, freighter amber) are different models in the game, not paints, so no paint entries are added.
