# Alien control panels: design notes (issue #118)

The ship's console, the bank terminal (green), the launch terminal (red) were boxes with a screen.
This is what the replacements are and why. Source: `art/scripts/terminals.py`. Models: `Assets/Art/Global/Vehicles/GV_ShipConsole_01.fbx`,
`GV_ShipTerminalBank_01.fbx`, `GV_ShipTerminalLaunch_01.fbx`.

## References

Written from the common vocabulary of sci-fi game consoles (Mass Effect's omni-tool desks, the Alien: Isolation and Dead Space
terminals, Star Trek's LCARS panels, the old arcade cabinet), not from images pulled for this note: no reference images were fetched, so
a reviewer who wants them should add the board to this file. What those have in common, and what we took:

| Read | Why it works | What we did |
|---|---|---|
| A desk that leans towards the user | the hands go on the slope, the eyes on the screen above it | the console's front ledge leans back at 49 degrees with the buttons on it; each terminal has a 22 degree control face under a screen leaning back 12 degrees |
| A screen with a frame, not a rectangle | a curved glass reads as expensive hardware | the screens are 22 flat segments with the edges 10 cm in front of the middle (a faceted curve, no smoothing), in a dark bezel with glowing side fins |
| Buttons in groups | groups say "controls"; a uniform grid says "keyboard" | square button blocks, a row of round ones, dials with a lit tick, sliders, a segmented status bar |
| One colour owns the object | you read the object at 20 m by its colour alone | the bank is green (housing `plant_green`, glass `glow_green`), the launch terminal red (`barn_red`, `glow_red`), all share the ship's cyan for trim |
| Something that floats | a hologram says "not our technology" | stacked hexagonal rings on a lit beam (3 over the bank's intake, 2 over the launch terminal, 3 on the console) |
| Cables | they tie the machine to the floor it stands on | hoses (kinked rods with a knuckle at each bend) from the back of each terminal to the console and out of both ends of the console into the deck |

## What each one is

* **Console** (`GV_ShipConsole_01`, 3.4 x 0.9 m, 0.93 m high, about 1750 triangles). A profile lofted along X (bulging front, leaning
  ledge, flat top), five groups of controls on the ledge, a middle hologram stub between the two terminals, vent slats, access panels and a
  row of small lights on the front, glow strips down both ends, four cables into the deck. The top is flat so the two terminals stand on it.
* **Bank terminal** (`GV_ShipTerminalBank_01`, 1.3 x 1.1 m, about 1600): GREEN. A ledger on the screen (five bars, lines of text), an intake slot
  with chevrons in the control face, rings that stack above it, button group and dial.
* **Launch terminal** (`GV_ShipTerminalLaunch_01`, about 1850): RED. A warning mark on the screen and a segmented countdown, a big red button
  inside a hazard-yellow cage, a throw lever, hazard stripes along the front lip, two dials, a radar ring.

## State lamps

Each terminal has three small separate objects on the rail over its screen: `Lamp_Locked` (red), `Lamp_Ready` (green), `Lamp_Working` (amber)
(in the FBX `<model>_Lamp_Locked` and so on). `Assets/Scripts/Interactables/TerminalLamps.cs` shows the matching one, about four times a second,
from state that is already replicated. It leaves the lights alone (the glow beside a terminal counts in the stealth light level). Nothing is added to the network.

| Terminal | Locked | Ready | Working |
|---|---|---|---|
| Bank | no mission running (objective list not ready, or the mission is over) | the mission is running | an objective item is being carried (blinks) |
| Launch | `ShipBase.CanLaunch` says no (objectives missing, a crew member captured, ...) | the ship can launch | the ship has launched (blinks) |

## Budget and checks

About 1500 to 1850 triangles each (the old boxes were 12). The only floating parts are the hologram rings above the first one on the console,
and the rings are threaded on a lit beam in the middle so they are one piece; `audit.py`'s bounding-box test still lists them,
by design. Not looked at in Unity when this was written (see the pull request).

One thing to know: in the editor and in the FBX all three lamps are lit at once (the component only switches them while the game runs). The race kiosk
that stood by the old placeholder van is gone (#25): the race is chosen on the main menu and locked once the mission starts.
