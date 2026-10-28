# Service appliances: the jukebox (first of the group)

Status: brief for the rework of `GH_Jukebox_01` (`art/scripts/household.py`, piece `service`), the owner's example of a model that "looks nothing like" the real thing. The other service appliances judged too crude in `docs/assets/item-fit-audit.md` (coffee machine, cooler) get their own rows here when they are reworked. US reference.

## What exists

`GH_Jukebox_01`: 0.90 x 0.55 x 1.45 m, 60 triangles. A brown box with a red tapered box on top, a glass panel with a cyan panel in the same plane behind it (they flicker: `audit_props.py` coplanar finding) and a grey plate low on the front. Nothing about it says jukebox: no arched top, no lit arch, no record visible, no selector, no speaker grille. Emitters: a warm light and a looping music sound (`emitters.py`, "Jukebox"); no moving parts. **Verdict: wrong shape, needs detail; size about right.**

## The family

| Member | Real size (w x d x h) | Recognisable at 10 m | In the repo |
|---|---|---|---|
| Floor jukebox, 1940s arched top (the "bubbler" shape every drawing of a jukebox uses) | about 0.81-0.84 x 0.58-0.69 x 1.50-1.52 m (sale listings of 1946 originals and of a modern reproduction, given in inches and centimetres; they vary by a few centimetres) | round arched top; a band of coloured light following the arch and running down both sides as pilasters, with bubble tubes; a glass window in the arch showing a record and the changer; a slanted selection strip with title cards and buttons; a speaker grille in the lower front; a coin entry | `GH_Jukebox_01` (this rework) |
| Floor jukebox, 1950s "selector" type (100 to 200 selections, a glass top showing the mechanism) | about 0.88-0.91 x 0.68 x 1.37-1.49 m (listings of Seeburg models of the early 1950s) | a large glass dome or flat glass top over the record carousel, chrome grille, rows of selection cards | not in the repo |
| Wall-box selector (one per diner booth) | about 0.30 x 0.15 x 0.35 m | chrome box, page-flipping title cards, coin slot | not in the repo; would fit the diner |
| Modern CD or digital jukebox | about 0.70 x 0.40 x 1.60 m, often wall-mounted | a touch screen in a lit cabinet | not in the repo |

**Variant chosen for the existing id**: the 1940s arched-top floor jukebox, as a generic design (not any maker's cabinet or trademark). It is the one people read as "jukebox" from across a room, it suits the diner and the retro rooms, and the current model's red dome on top was already reaching for it.

## Features: kept, faked, dropped

- **Arched top**: kept, a 16-sided half cylinder the width of the cabinet.
- **Lit arch and pilasters**: kept, a band of `glow_amber` round the arch and down both sides, 2.5 cm proud of the front; three `glow_red` bubble-tube bands on each pilaster.
- **Window with the record**: kept, a `clear_glass` window over a dark backing, with a black record and a red label behind the glass, and a chrome tone arm.
- **Selection strip**: kept, a chrome strip tilted towards the viewer with a white title-card strip and a row of black buttons.
- **Speaker grille**: kept, mustard grille cloth behind seven chrome bars.
- **Coin entry**: kept, a chrome plate with a black slot.
- Dropped: the changer mechanism in detail, the carved side panels, the real bubble tubes' liquid.

Colours (palette names): `wood_dark` cabinet and arch, `black` plinth and buttons, `glow_amber` arch light, `glow_red` bubble bands, `clear_glass` window, `metal_dark` window backing, `black` record with a `cloth_red` label, `metal_galv` chrome, `label_white` title cards, `fabric_mustard` grille cloth.

## Size, pivot, budget, markers

- Cabinet 0.84 x 0.62 x 1.50 m (w x d x h, the width at the plinth); 0.84 x 0.68 overall with the selection strip and the light band in front. Front -Y, origin on the floor at the centre of the base.
- Furniture and appliance class: 300-1,200 triangles (`docs/from-game/asset-list.md` 2.1); aim for 400-700.
- No moving parts (as now). Markers kept: the `Glow` light and the `Music` sound in `emitters.SPECS` (fractions of the bounding box, so they follow the new size).
- Condition: new only (no Damaged style is built for it).

## Parts (centre or extent, metres; y is the front face's depth, the front at y = -D/2 = -0.31)

| Part | Size or shape | Position | Attaches to |
|---|---|---|---|
| Plinth | 0.84 x 0.62 x 0.06 box, `black` | z 0 to 0.06 | the floor |
| Cabinet | 0.80 x 0.62 x 1.04 box, `wood_dark` | z 0.06 to 1.10 | stands on the plinth |
| Arch | half of a 16-sided cylinder, radius 0.40, 0.62 deep, `wood_dark` | axis along y at z 1.10; top at 1.50 | its lower half is inside the cabinet; the end caps are in the cabinet's front and back planes, same colour |
| Light arch | 10 boxes along the arc, mid radius 0.345, 0.07 wide, `glow_amber` | y -0.335 to -0.308 | sunk 2 mm into the front |
| Pilasters | 0.07 x 0.027 boxes from z 0.06 to 1.10 at x ±0.345, `glow_amber` | same depth as the light arch | meet the arch's ends at z 1.10 |
| Bubble bands | 0.066 x 0.02 boxes, three per pilaster, `glow_red` | 4 mm prouder than the pilaster | sunk into the pilaster |
| Window backing | the arch's inside (radius 0.31) down to z 0.98, `metal_dark` | y -0.316 to -0.308 | sunk into the front |
| Record and label | round discs radius 0.13 and 0.04, `black`, `cloth_red` | centre z 1.17, in front of the backing | sunk 2 mm into the backing / record |
| Tone arm | 0.016 x 0.002 rod, `metal_galv` | from a pivot at the record's upper right down onto the record | on the record's face, behind the glass |
| Window glass | same outline, radius 0.32, `clear_glass` | y -0.3325 to -0.3245 | its edge inside the light arch; the label sinks 1 mm into it |
| Selection strip | 0.60 x 0.10 x 0.05, tilted 30 degrees, `metal_galv` | centre z 0.95, in front of the window's lower edge | sunk into the front and the backing |
| Title cards, buttons | `label_white` strip and ten `black` buttons on the strip's face | on the strip | sunk 0.5 mm |
| Grille cloth | 0.60 x 0.008 x 0.52, `fabric_mustard` | z 0.18 to 0.70, y -0.316 to -0.308 | sunk into the front |
| Grille bars | seven 0.58 x 0.014 x 0.02 bars, `metal_galv` | across the cloth | sunk 2 mm into the cloth |
| Coin plate and slot | 0.08 x 0.012 x 0.12 plate, `metal_galv`; 0.006 x 0.04 slot, `black` | x 0.20, z 0.80 | on the front |

Checks: `audit_props.py` (no gap, coplanar or floating finding), thumbnail against the old one, four sides and 10 m in Blender.

# Arcade machines (new, 2026-10-27)

The owner asked for arcade machines. None exist in the repo. They sit with the jukebox in the diner, a bar, a bowling alley, a motel lobby or a teenager's basement.

## The family

| Member | Real size (w x d x h) | Recognisable at 10 m | Verdict |
|---|---|---|---|
| Upright video cabinet (1980s, one player) | about 0.61-0.64 x 0.74-0.85 x 1.47-1.76 m (maker and retailer listings of full-size and reproduction uprights; the classic full size is about 0.63 x 0.84 x 1.73 m) | tall box; the side profile (control panel sticking out at waist height, the screen leaning back above it, a lit marquee overhanging at the top); side art; a coin door low on the front | **new**, `GH_ArcadeUpright_01` |
| Cocktail table (sit-down, two players face to face) | about 0.94 x 0.53 x 0.76 m (maker listings: 37 x 21 x 30 in) | a low box with the screen facing up under a glass top, a joystick and buttons at each short end | **new**, `GH_ArcadeCocktail_01` |
| Pinball machine | about 0.74 x 1.32 x 1.93 m with the backbox (a maker's spec sheet: 29 x 52 x 76 in) | a long sloping cabinet on four legs under glass, a tall lit backbox at the far end, flipper buttons on the sides, a plunger at the front right | **new**, `GH_Pinball_01` |
| Claw crane, sit-down racer, air hockey, skee-ball | various | | not in this batch; listed for later |

All three are generic designs: no game, maker, character or logo is copied. The screens and the backglass show abstract coloured blocks.

## Features: kept, faked, dropped

- Upright: the side profile (built from three convex prisms: base, sloping screen section, marquee box), control panel tilted towards the player with a joystick and three buttons, a screen in a black bezel on the sloping face with a few lit blocks, a lit marquee, a coin door with two lit coin slots, a stripe of side art on each side.
- Cocktail table: the black box, the screen under a glass top, a control panel with a joystick and two buttons at each short end, a coin door on a long side.
- Pinball: the cabinet sloping down towards the player (6.5 degrees), four chrome legs (the front ones shorter), a coloured playfield with bumpers and flippers under glass, a backbox with a lit backglass and a speaker grille, a coin door, flipper buttons, the plunger.
- Dropped: the CRT's shape behind the bezel, the playfield's ramps (three lanes and three flat bumpers are kept), the real art.

Colours (palette names): `black` cabinets, `screen` and `glow_cyan`, `glow_red`, `glow_amber` for the screens, marquees and backglass, `cloth_red` and `label_blue` side art, controls and playfield, `metal_galv` chrome, `metal_dark` coin doors, `clear_glass` glass, `paint_white` flippers.

## Size, pivot, budget, markers

- Front -Y (the player stands at -Y; the cocktail table's players sit at its two short ends, ±X), origin on the floor at the centre of the base.
- Furniture and appliance class: 300-1,200 triangles each.
- No moving parts. Markers (`emitters.SPECS`): a cool `Screen` light and a looping `Attract` sound for each (traits power and noisy).

## Parts: upright (W 0.64; y from the front: -0.42 control panel, -0.30 base front, +0.42 back)

| Part | Size or shape | Position | Attaches to |
|---|---|---|---|
| Base | 0.64 x 0.72 x 0.86 box, `black` | y -0.30 to 0.42, z 0 to 0.86 | the floor |
| Screen section | prism, profile (y, z): (-0.30, 0.86), (0.42, 0.86), (0.42, 1.50), (-0.14, 1.50): the front leans back 14 degrees | x ±0.32 | on the base |
| Marquee box | 0.64 x 0.66 x 0.25, `black` | y -0.24 to 0.42, z 1.50 to 1.75 | on the screen section; overhangs its front by 10 cm |
| Marquee light | 0.58 x 0.012 x 0.17, `glow_amber` | on the marquee box's front | sunk 2 mm |
| Bezel, screen, pixels | parallel to the sloping face: `black` 0.56 x 0.50, `screen` 0.44 x 0.36, lit blocks | on the sloping face | each sunk into the one behind |
| Control panel | 0.64 x 0.18 x 0.05, tilted 12 degrees towards the player, `cloth_red` | front edge at y -0.42, z about 0.88, its underside on the base's front edge | sunk into the base front |
| Joystick, buttons | a `metal_galv` stick with a `black` ball; three `label_blue` buttons | on the panel's face | sunk into it |
| Coin door | 0.26 x 0.012 x 0.30, `metal_dark`; two `glow_red` slots | z 0.30 to 0.60 on the base front | sunk 2 mm |
| Side art | a 0.006 thick `label_blue` panel and a `cloth_red` stripe on each side | x ±0.322 | sunk 2 mm into the side |

The cocktail table's and the pinball's parts follow the same rules (each part sunk into what it stands on, decals 2 mm proud of their face, thin plates with their own depth) and are listed in the script's docstrings.

Checks: `audit_props.py` (no gap, coplanar or floating finding), thumbnails, four sides in Blender.
