# Item models: fit, flicker and crude-shape audit (2026-10-27)

The room and interior props (appliances, furniture, decor, fixtures, office equipment, household tools: 195 models in `site/manifest.json`) checked for the three problems the owner reported: models too crude to recognise (the jukebox), drawers and doors with gaps, and textures that flicker. Issue #92 (crude decor and kitchenware) and #109 (models never audited) are related.

## How it was checked

- `art/scripts/audit_props.py`, extended in this branch with three tests and run over every prop it builds (299 props; 185 of the 195 item models, the other 10 below):
  - **gap**: parts the floating test counts as joined (within 1 cm) that do not touch (more than 1 mm apart). A visible sliver of background.
  - **coplanar**: faces of two parts of different colours in one plane, facing the same way and overlapping where it can be seen (not buried in a third part). These are what flicker (z-fight) in the viewer. Same-colour overlaps are not reported: they cannot be seen.
  - **reveal**: a door, drawer or lid (a moving part) with an open slot round it: sight lines 2 mm outside its edge, from the front (from above for a lid), reach more than 1 cm behind the back of the door leaf or drawer front.
- The three were checked against the thumbnails: the jukebox's glass and cyan panel flicker, the cabinet shows a dark slit between its upper and lower doors, the nightstand a gap between drawer and door.
- **Crude shapes** cannot be measured: every item thumbnail was looked at in contact sheets, with the triangle count, and judged against what makes the real object recognisable.
- **Not audited** (no recorder for them yet): the fridge's Modern, Retro and Damaged styles and the damaged wardrobe (`interactive.py` styles), and the six household tools in `tools_extra.py` / `tools_more.py` (bathroom scale, boot scraper, clothes iron, fire poker, plunger, toilet brush). The colour themes of `home_styles.py` reuse the household geometry, so a fix there reaches them.

## Summary by problem

72 of the 185 audited item models have at least one gap, flicker or slot finding.

| Problem | Models | Root causes worth fixing once |
|---|---|---|
| Drawer, door or lid with an open slot (reveal) | 13: Cabinet, Nightstand, Counter_Kitchen, Stove, FilingCabinet (GO), Fridge, Fridge_Dispenser, VendingMachine, WaterCooler, Copier, Chest, Cooler, Dumpster | `interactive.door()` / `drawer()` openings are cut wider than the leaf, or two leaves leave a slot between them |
| Gap between parts that should touch | 42 models, 65 findings | `interactive._door_handle` sits 2.5 mm off the door on all 10 models with doors (Cabinet, Counter, Fridge, Fridge_Dispenser, FuseBox, Locker, Nightstand, Stove, Wardrobe); tops 5 mm above carcasses (Nightstand, FilingCabinet); wall decals 2 mm off their sheet (KidDrawing); teddy and doll limbs 5 mm off |
| Flicker (coplanar faces) | 36 models, 42 findings | `office.shell` and the dresser/nightstand/counter dividers share the carcass side's plane; the desk edge strip shares the top's plane; picture frames' scenery shares the canvas plane |
| Too crude to recognise | about 35 (list below) | box shapes with no recognisable features |

## Too crude to recognise (judged from the thumbnails)

Grouped as they could be reworked; #92 and #89 already name some.

| Group | Models | What is missing |
|---|---|---|
| Service and kitchen appliances | **Jukebox** (60 tris), CoffeeMachine (48), Toaster (72, #92), BreadBox (96), Cooler (108), Kettle (72), Pot (68, #92), Mug (40, #92) | jukebox: arched top, curved glass dome over the record deck, light-up pilasters, speaker grille, coin and selection panel; coffee machine: carafe, hot plate, filter head; toaster: slots, lever, dial |
| Bathroom and utilities | Tub (84), Toilet (88), Sink_Bath (56), Shower (100), Fireplace (96), WoodStove (104), AirConditioner (84), FuseBox (168, #92), Intercom (36) | tub: rolled rim, inner basin, tap and drain; toilet: seat and lid, tank lid, flush handle; shower: tray, door frame, head |
| Clutter, soft furnishings, toys | Suitcase (60, #92), Lunchbox (36), PicnicBasket (48), LaundryBasket (36), TrashCan (40), Cushion (12), Pillow (12), Blanket (24), TeddyBear (108, #92), Doll (84, #92), Backpack (48, #89), BootsPair (72, #89) | handles, lids, straps, seams, faces; the cushion and pillow are single boxes |
| Plain-box furniture and electronics | Counter_Bar (36), Bench (36), Locker (136), MedicineCabinet (120), ToyBox (80), LabBench (64), Whiteboard (84), ComputerTower (36), Radio_CB (44) | counter bar: footrest, overhang, panels; locker: vents, number plate, hinges |

## Proposed order

1. **Fit batch 1, storage and appliances** (`interactive.py`, `office.py`, `household.py`): the door handle helper, the open slots round doors and drawers, the carcass and divider flicker. About 25 models, mostly through the shared builders.
2. **Jukebox rework** (with its brief): the owner's example; also fixes its flicker.
3. **Fit batch 2, decor and fixtures**: frames, calendar, lamps, toy truck, boots, gurney, tub, sinks, boiler and water heater pipes, sofas, chairs, workbench, shelves, cubicles; the decal and limb gaps.
4. **Crude-shape reworks**, one PR per group above, each with its `asset-brief` brief.

The full findings follow (tests `reveal`, `gap`, `coplanar`; then the older `floating` and `through` for the same models). Positions are Blender coordinates in metres; the script function that made each part is in brackets.

### reveal (22 findings)

| Model | Category | Finding |
|---|---|---|
| `GI_Cabinet_01` | storage/cabinet | reveal: DoorUL: 18 of 67 sight lines just outside its edge see 35 cm into the body (an open slot round it) |
| `GI_Cabinet_01` | storage/cabinet | reveal: DoorUR: 18 of 67 sight lines just outside its edge see 35 cm into the body (an open slot round it) |
| `GI_Cabinet_01` | storage/cabinet | reveal: DoorLL: 18 of 67 sight lines just outside its edge see 35 cm into the body (an open slot round it) |
| `GI_Cabinet_01` | storage/cabinet | reveal: DoorLR: 18 of 67 sight lines just outside its edge see 35 cm into the body (an open slot round it) |
| `GI_Chest_01` | storage/chest | reveal: Lid: 4 of 10 sight lines just outside its edge see 5 cm into the body (an open slot round it) |
| `GI_Cooler_01` | service/cooler | reveal: Lid: 14 of 14 sight lines just outside its edge see 8 cm into the body (an open slot round it) |
| `GI_Counter_Kitchen_01` | kitchen/counter-kitchen | reveal: Door: 94 of 136 sight lines just outside its edge see 57 cm into the body (an open slot round it) |
| `GI_Dumpster_01` | outdoor/dumpster | reveal: LidL: 44 of 92 sight lines just outside its edge see 85 cm into the body (an open slot round it) |
| `GI_Dumpster_01` | outdoor/dumpster | reveal: LidR: 44 of 92 sight lines just outside its edge see 85 cm into the body (an open slot round it) |
| `GI_Fridge_01` | kitchen/fridge | reveal: Door: 64 of 66 sight lines just outside its edge see 3 cm into the body (an open slot round it) |
| `GI_Fridge_01` | kitchen/fridge | reveal: DoorFreezer: 32 of 34 sight lines just outside its edge see 3 cm into the body (an open slot round it) |
| `GI_Fridge_Dispenser_01` | kitchen/fridge | reveal: DoorL: 21 of 81 sight lines just outside its edge see 69 cm into the body (an open slot round it) |
| `GI_Fridge_Dispenser_01` | kitchen/fridge | reveal: DoorR: 21 of 81 sight lines just outside its edge see 69 cm into the body (an open slot round it) |
| `GI_Fridge_Dispenser_01` | kitchen/fridge | reveal: DrawerFreezer: 68 of 125 sight lines just outside its edge see 3 cm into the body (an open slot round it) |
| `GI_Nightstand_01` | storage/nightstand | reveal: Drawer1: 3 of 56 sight lines just outside its edge see 15 cm into the body (an open slot round it) |
| `GI_Nightstand_01` | storage/nightstand | reveal: Door: 18 of 64 sight lines just outside its edge see 37 cm into the body (an open slot round it) |
| `GI_Stove_01` | kitchen/stove | reveal: Door: 54 of 120 sight lines just outside its edge see 62 cm into the body (an open slot round it) |
| `GI_VendingMachine_01` | service/vending-machine | reveal: Door: 88 of 176 sight lines just outside its edge see 77 cm into the body (an open slot round it) |
| `GI_VendingMachine_01` | service/vending-machine | reveal: Flap: 40 of 62 sight lines just outside its edge see 79 cm into the body (an open slot round it) |
| `GO_Copier_01` | office/copier | reveal: Lid: 19 of 51 sight lines just outside its edge see 15 cm into the body (an open slot round it) |
| `GO_FilingCabinet_01` | office/filing-cabinet | reveal: Drawer1: 56 of 77 sight lines just outside its edge see 2 cm into the body (an open slot round it) |
| `GO_WaterCooler_01` | office/water-cooler | reveal: Door: 28 of 80 sight lines just outside its edge see 32 cm into the body (an open slot round it) |

### gap (65 findings)

| Model | Category | Finding |
|---|---|---|
| `GD_CeilingShade_01` | lighting/ceiling-shade | gap: 1 part(s) stand 10.0 mm off the rest (a visible gap): black @(0.00, 0.00, -0.20) (`ceiling_shade`) |
| `GD_Clock_Wall_Retro_01` | wall/clock | gap: 2 part(s) stand 3.0 mm off the rest (a visible gap): black @(0.00, -0.03, 0.04) (`clock_retro`) |
| `GD_ComputerTower_01` | electronics/computer-tower | gap: 1 part(s) stand 4.5 mm off the rest (a visible gap): glow_cyan @(0.06, -0.23, 0.15) (`computer_tower`) |
| `GD_DeskLamp_01` | lighting/desk-lamp | gap: 1 part(s) stand 3.2 mm off the rest (a visible gap): metal_dark @(0.00, 0.00, 0.01) (`desk_lamp`) |
| `GD_Doll_01` | toys/doll | gap: 2 part(s) stand 5.0 mm off the rest (a visible gap): skin @(0.00, 0.00, 0.27) (`doll`) |
| `GD_Keyboard_01` | electronics/keyboard | gap: 1 part(s) stand 1.2 mm off the rest (a visible gap): black @(0.00, 0.06, 0.03) (`keyboard`) |
| `GD_KidDrawing_01` | wall/kid-drawing | gap: 1 part(s) stand 2.0 mm off the rest (a visible gap): alien_grey @(0.00, -0.00, -0.05) (`kid_drawing`) |
| `GD_KidDrawing_01` | wall/kid-drawing | gap: 1 part(s) stand 2.0 mm off the rest (a visible gap): paint_yellow @(-0.10, -0.00, 0.15) (`kid_drawing`) |
| `GD_KidDrawing_02` | wall/kid-drawing | gap: 1 part(s) stand 2.0 mm off the rest (a visible gap): barn_red @(0.00, -0.00, -0.06) (`kid_drawing_02`) |
| `GD_KidDrawing_02` | wall/kid-drawing | gap: 1 part(s) stand 2.0 mm off the rest (a visible gap): wood_dark @(0.00, -0.00, 0.02) (`kid_drawing_02`) |
| `GD_KidDrawing_02` | wall/kid-drawing | gap: 1 part(s) stand 2.0 mm off the rest (a visible gap): paint_yellow @(0.09, -0.00, 0.14) (`kid_drawing_02`) |
| `GD_KidDrawing_02` | wall/kid-drawing | gap: 1 part(s) stand 2.0 mm off the rest (a visible gap): grass @(0.00, -0.00, -0.15) (`kid_drawing_02`) |
| `GD_Laptop_01` | electronics/laptop | gap: 1 part(s) stand 1.7 mm off the rest (a visible gap): screen @(0.00, 0.11, 0.13) (`laptop`) |
| `GD_MailPile_01` | paper/mail-pile | gap: 1 part(s) stand 1.0 mm off the rest (a visible gap): paint_yellow @(-0.02, -0.01, 0.02) (`mail_pile`) |
| `GD_MailPile_01` | paper/mail-pile | gap: 1 part(s) stand 1.0 mm off the rest (a visible gap): paper @(0.02, 0.00, 0.02) (`mail_pile`) |
| `GD_PhotoFrame_01` | wall/photo-frame-standing | gap: 1 part(s) stand 1.0 mm off the rest (a visible gap): skin @(-0.03, -0.01, 0.11) (`photo_frame`) |
| `GD_PicnicBasket_01` | clutter/picnic-basket | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): wood_dark @(0.00, 0.00, 0.26) (`picnic_basket`) |
| `GD_SecurityCamera_01` | electronics/security-camera | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): cloth_red @(0.03, -0.10, 0.03) (`security_camera`) |
| `GD_TV_Flat_Modern_01` | electronics/tv | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): black @(0.00, 0.10, 0.38) (`tv_modern`) |
| `GD_TeddyBear_01` | toys/teddy-bear | gap: 3 part(s) stand 5.0 mm off the rest (a visible gap): teddy @(0.00, 0.00, 0.14) (`teddy`) |
| `GD_TeddyBear_01` | toys/teddy-bear | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): teddy @(-0.11, 0.00, 0.16) (`teddy`) |
| `GD_TeddyBear_01` | toys/teddy-bear | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): teddy @(0.11, 0.00, 0.16) (`teddy`) |
| `GD_VaseFlowers_01` | plants/vase-flowers | gap: 1 part(s) stand 2.2 mm off the rest (a visible gap): plant_green @(0.00, -0.05, 0.30) (`vase_flowers`) |
| `GH_Bed_Single_01` | bedroom/bed-single | gap: 1 part(s) stand 10.0 mm off the rest (a visible gap): wood_light @(0.00, 1.04, 0.50) (`bed_single`) |
| `GH_Chair_Kitchen_01` | seating/chair-kitchen | gap: 4 part(s) stand 10.0 mm off the rest (a visible gap): wood_light @(0.00, 0.20, 0.70) (`chair_kitchen`) |
| `GH_CoffeeMachine_01` | service/coffee-machine | gap: 1 part(s) stand 10.0 mm off the rest (a visible gap): metal_dark @(0.00, 0.00, 0.40) (`coffee_machine`) |
| `GH_Mug_01` | kitchenware/mug | gap: 1 part(s) stand 2.3 mm off the rest (a visible gap): cloth_red @(0.05, 0.00, 0.06) (`mug`) |
| `GH_Shelf_Wall_05` | storage/shelf-wall | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): wood_light @(0.00, -0.06, 0.00) (`shelf_wall_05`) |
| `GH_Sofa_Damaged_01` | seating/sofa | gap: 1 part(s) stand 7.5 mm off the rest (a visible gap): rust_dark @(-0.40, -0.04, 0.56) (`sofa_damaged`) |
| `GH_WoodStove_01` | utilities/wood-stove | gap: 2 part(s) stand 1.0 mm off the rest (a visible gap): metal_dark @(0.00, -0.23, 0.45) (`wood_stove`) |
| `GI_Cabinet_01` | storage/cabinet | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/DoorLL @(-0.06, -0.23, 0.31) (`_door_handle`) |
| `GI_Cabinet_01` | storage/cabinet | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/DoorLR @(0.06, -0.23, 0.31) (`_door_handle`) |
| `GI_Counter_Kitchen_01` | kitchen/counter-kitchen | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/Door @(0.08, -0.35, 0.44) (`_door_handle`) |
| `GI_Dryer_01` | laundry/dryer | gap: 2 part(s) stand 4.0 mm off the rest (a visible gap): glass/Door @(0.00, -0.37, 0.40) (`dryer`) |
| `GI_Dryer_01` | laundry/dryer | gap: 1 part(s) stand 4.0 mm off the rest (a visible gap): paint_white/Door @(0.00, -0.35, 0.40) (`dryer`) |
| `GI_Fridge_01` | kitchen/fridge | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/Door @(-0.29, -0.41, 0.64) (`_door_handle`) |
| `GI_Fridge_01` | kitchen/fridge | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/DoorFreezer @(-0.29, -0.41, 1.50) (`_door_handle`) |
| `GI_Fridge_Dispenser_01` | kitchen/fridge | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): black/DoorL @(-0.06, -0.42, 1.25) (`_door_handle`) |
| `GI_Fridge_Dispenser_01` | kitchen/fridge | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): black/DoorR @(0.06, -0.42, 1.25) (`_door_handle`) |
| `GI_Fridge_Dispenser_01` | kitchen/fridge | gap: 1 part(s) stand 4.0 mm off the rest (a visible gap): glow_cyan/DoorR @(0.26, -0.41, 1.50) (`<lambda>`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): black @(-0.10, -0.03, 0.14) (`fuse_box`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): black @(0.10, -0.03, 0.14) (`fuse_box`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): black @(-0.10, -0.03, 0.04) (`fuse_box`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): black @(0.10, -0.03, 0.04) (`fuse_box`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): black @(-0.10, -0.03, -0.06) (`fuse_box`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): black @(0.10, -0.03, -0.06) (`fuse_box`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/Door @(0.14, -0.09, 0.00) (`_door_handle`) |
| `GI_FuseBox_01` | utilities/fuse-box | gap: 1 part(s) stand 1.0 mm off the rest (a visible gap): cloth_red/Door @(0.10, -0.07, -0.18) (`<lambda>`) |
| `GI_Locker_01` | storage/locker | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/Door @(-0.13, -0.29, 0.90) (`_door_handle`) |
| `GI_Nightstand_01` | storage/nightstand | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): wood_light @(0.00, 0.00, 0.58) (`nightstand`) |
| `GI_Nightstand_01` | storage/nightstand | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/Door @(-0.15, -0.24, 0.17) (`_door_handle`) |
| `GI_Safe_01` | storage/safe | gap: 1 part(s) stand 5.0 mm off the rest (a visible gap): metal_dark/Door @(-0.14, -0.32, 0.30) (`<lambda>`) |
| `GI_Stove_01` | kitchen/stove | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/Door @(0.00, -0.38, 0.67) (`_door_handle`) |
| `GI_Toaster_01` | kitchen/toaster | gap: 2 part(s) stand 5.8 mm off the rest (a visible gap): black/Lever @(0.15, 0.00, 0.14) (`toaster`) |
| `GI_Wardrobe_01` | storage/wardrobe | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/DoorL @(-0.06, -0.32, 0.95) (`_door_handle`) |
| `GI_Wardrobe_01` | storage/wardrobe | gap: 1 part(s) stand 2.5 mm off the rest (a visible gap): metal_galv/DoorR @(0.06, -0.32, 0.95) (`_door_handle`) |
| `GI_Washer_01` | laundry/washer | gap: 2 part(s) stand 4.0 mm off the rest (a visible gap): glass/Door @(0.00, -0.37, 0.40) (`washer`) |
| `GI_Washer_01` | laundry/washer | gap: 1 part(s) stand 4.0 mm off the rest (a visible gap): paint_white/Door @(0.00, -0.35, 0.40) (`washer`) |
| `GL_ServiceEntry_01` | utilities/service-entry | gap: 6 part(s) stand 5.0 mm off the rest (a visible gap): metal_galv @(0.00, -0.07, 0.00) (`service_entry`) |
| `GO_Copier_01` | office/copier | gap: 2 part(s) stand 1.5 mm off the rest (a visible gap): screen @(0.10, -0.32, 0.97) (`copier`) |
| `GO_Phone_01` | electronics/phone | gap: 1 part(s) stand 2.6 mm off the rest (a visible gap): office_grey @(0.00, -0.01, 0.06) (`phone`) |
| `GO_Printer_Desktop_01` | office/printer | gap: 1 part(s) stand 4.0 mm off the rest (a visible gap): paper @(0.00, 0.04, 0.28) (`printer_desktop`) |
| `GO_WaterCooler_01` | office/water-cooler | gap: 1 part(s) stand 2.0 mm off the rest (a visible gap): label_white @(0.00, 0.00, 1.30) (`water_cooler`), n=10, z0=h + 0.02,] |
| `GO_Whiteboard_Stand_01` | office/whiteboard | gap: 4 part(s) stand 7.5 mm off the rest (a visible gap): metal_dark @(-0.59, 0.04, 0.95) (`whiteboard_stand`) |
| `GO_Whiteboard_Stand_01` | office/whiteboard | gap: 4 part(s) stand 7.5 mm off the rest (a visible gap): metal_dark @(0.59, 0.04, 0.95) (`whiteboard_stand`) |

### coplanar (42 findings)

| Model | Category | Finding |
|---|---|---|
| `GD_BootsPair_01` | clutter/boots-pair | coplanar: wood_dark @(-0.08, 0.02, 0.10) (`boots_pair`) and rubber @(-0.08, -0.03, 0.01) (`boots_pair`) share a face plane (4 face pair(s)) (and 1 more like it) |
| `GD_BootsPair_01` | clutter/boots-pair | coplanar: wood_dark @(-0.08, -0.07, 0.04) (`boots_pair`) and rubber @(-0.08, -0.03, 0.01) (`boots_pair`) share a face plane (3 face pair(s)) (and 1 more like it) |
| `GD_Calendar_01` | wall/calendar | coplanar: paper @(0.00, 0.00, 0.00) (`calendar`) and cloth_red @(0.00, -0.01, 0.17) (`calendar`) share a face plane (7 face pair(s)) |
| `GD_CeilingShade_01` | lighting/ceiling-shade | coplanar: lamp_shade @(0.00, 0.00, -0.50) (`ceiling_shade`) and glow_cyan @(0.00, 0.00, -0.56) (`ceiling_shade`) share a face plane (4 face pair(s)) |
| `GD_Chandelier_01` | lighting/chandelier | coplanar: paint_white @(0.30, 0.00, -0.55) (`chandelier`) and glow_cyan @(0.30, 0.00, -0.49) (`chandelier`) share a face plane (4 face pair(s)) (and 5 more like it) |
| `GD_Frame_Landscape_01` | wall/frame-landscape | coplanar: tile_blue @(0.00, -0.02, 0.00) (`_frame`) and grass @(0.00, -0.02, -0.10) (`frame_landscape`) share a face plane (5 face pair(s)) |
| `GD_Frame_Landscape_02` | wall/frame-landscape | coplanar: paper @(0.00, -0.02, 0.00) (`_frame`) and pine @(0.00, -0.02, -0.15) (`frame_landscape_02`) share a face plane (6 face pair(s)) |
| `GD_Frame_Landscape_02` | wall/frame-landscape | coplanar: rock @(-0.10, -0.02, -0.04) (`frame_landscape_02`) and pine @(0.00, -0.02, -0.15) (`frame_landscape_02`) share a face plane (3 face pair(s)) |
| `GD_Frame_Landscape_02` | wall/frame-landscape | coplanar: rock @(0.14, -0.02, -0.07) (`frame_landscape_02`) and pine @(0.00, -0.02, -0.15) (`frame_landscape_02`) share a face plane (2 face pair(s)) |
| `GD_Frame_Landscape_03` | wall/frame-landscape | coplanar: pink @(0.00, -0.02, 0.00) (`_frame`) and tile_blue @(0.00, -0.02, -0.10) (`frame_landscape_03`) share a face plane (5 face pair(s)) |
| `GD_Frame_Landscape_03` | wall/frame-landscape | coplanar: tile_blue @(0.00, -0.02, -0.10) (`frame_landscape_03`) and cream @(0.10, -0.02, -0.02) (`frame_landscape_03`) share a face plane (2 face pair(s)) |
| `GD_SecurityCamera_01` | electronics/security-camera | coplanar: metal_dark @(0.00, 0.00, 0.00) (`security_camera`) and fabric_grey @(0.00, -0.12, -0.02) (`security_camera`) share a face plane (2 face pair(s)) |
| `GD_TableLamp_Retro_01` | lighting/lamp | coplanar: tractor_green @(0.00, 0.00, 0.12) (`table_lamp_retro`) and rust_dark @(0.00, 0.00, 0.02) (`table_lamp_retro`) share a face plane (8 face pair(s)) |
| `GD_ToyTruck_01` | toys/toy-truck | coplanar: paint_yellow @(0.00, 0.04, 0.07) (`toy_truck`) and cloth_red @(0.00, -0.07, 0.09) (`toy_truck`) share a face plane (8 face pair(s)) |
| `GD_VaseFlowers_01` | plants/vase-flowers | coplanar: cloth_red @(0.00, 0.00, 0.41) (`vase_flowers`) and fabric_pink @(-0.04, 0.02, 0.41) (`vase_flowers`) share a face plane (4 face pair(s)) (and 1 more like it) |
| `GH_Boiler_01` | utilities/boiler | coplanar: copper @(0.15, 0.26, 1.85) (`pipe_to_wall`) and metal_galv @(0.15, 0.41, 1.85) (`pipe_to_wall`) share a face plane (8 face pair(s)) (and 1 more like it) |
| `GH_Chair_Dining_01` | seating/chair-dining | coplanar: fabric_brown @(0.00, 0.00, 0.48) (`chair_dining`) and wood_dark @(-0.19, 0.20, 0.75) (`chair_dining`) share a face plane (1 face pair(s)) (and 1 more like it) |
| `GH_Fireplace_01` | utilities/fireplace | coplanar: brick @(0.00, 0.10, 1.00) (`fireplace`) and concrete @(0.00, -0.40, 0.04) (`fireplace`) share a face plane (1 face pair(s)) |
| `GH_Gurney_01` | bedroom/gurney | coplanar: metal_dark @(-0.28, -0.80, 0.40) (`gurney`) and rubber @(-0.28, -0.80, 0.07) (`gurney`) share a face plane (11 face pair(s)) (and 3 more like it) |
| `GH_Jukebox_01` | service/jukebox | coplanar: glass @(0.00, -0.28, 0.90) (`jukebox`) and glow_cyan @(0.00, -0.28, 0.90) (`jukebox`) share a face plane (2 face pair(s)) |
| `GH_Shelf_Wall_02` | storage/shelf-wall | coplanar: wood_dark @(0.00, 0.00, 0.00) (`shelf_wall_02`) and black @(-0.40, 0.10, -0.07) (`shelf_wall_02`) share a face plane (4 face pair(s)) (and 1 more like it) |
| `GH_Sink_Kitchen_01` | kitchen/sink | coplanar: metal_galv @(-0.20, 0.00, 0.86) (`sink_kitchen`) and metal_dark @(-0.20, 0.00, 0.88) (`sink_kitchen`) share a face plane (2 face pair(s)) |
| `GH_Sofa_Modern_01` | seating/sofa | coplanar: paint_white @(-0.55, -0.05, 0.47) (`sofa_modern`) and fabric_grey @(-0.55, 0.36, 0.62) (`sofa_modern`) share a face plane (4 face pair(s)) (and 1 more like it) |
| `GH_Tub_01` | bath/tub | coplanar: porcelain @(0.00, 0.00, 0.28) (`tub`) and metal_galv @(-0.75, -0.30, 0.03) (`tub`) share a face plane (2 face pair(s)) (and 3 more like it) |
| `GH_WaterHeater_01` | utilities/water-heater | coplanar: copper @(-0.10, 0.17, 1.50) (`pipe_to_wall`) and metal_galv @(-0.10, 0.32, 1.50) (`pipe_to_wall`) share a face plane (8 face pair(s)) (and 1 more like it) |
| `GH_Workbench_01` | tables/workbench | coplanar: wood_light @(0.00, 0.00, 0.90) (`workbench`) and wood_dark @(0.00, 0.32, 1.15) (`workbench`) share a face plane (2 face pair(s)) |
| `GI_Counter_Kitchen_01` | kitchen/counter-kitchen | coplanar: wood_dark @(0.00, 0.28, 0.45) (`shell`) and wood_light @(0.00, 0.00, 0.45) (`counter_kitchen`) share a face plane (4 face pair(s)) |
| `GI_Dresser_01` | storage/dresser | coplanar: wood_light @(0.00, 0.23, 0.45) (`shell`) and wood_dark @(0.00, 0.00, 0.31) (`dresser`) share a face plane (4 face pair(s)) (and 1 more like it) |
| `GI_Dryer_01` | laundry/dryer | coplanar: metal_dark @(0.00, 0.00, 0.01) (`shell`) and enamel_cream @(0.00, -0.31, 0.09) (`dryer`) share a face plane (5 face pair(s)) |
| `GI_Nightstand_01` | storage/nightstand | coplanar: wood_dark @(0.00, 0.19, 0.29) (`shell`) and wood_light @(0.00, 0.00, 0.30) (`nightstand`) share a face plane (4 face pair(s)) |
| `GI_Toaster_01` | kitchen/toaster | coplanar: metal_galv @(0.00, 0.00, 0.09) (`toaster`) and metal_dark @(0.00, 0.00, 0.00) (`toaster`) share a face plane (2 face pair(s)) |
| `GI_Washer_01` | laundry/washer | coplanar: metal_dark @(0.00, 0.00, 0.01) (`shell`) and enamel_white @(0.00, -0.31, 0.09) (`washer`) share a face plane (5 face pair(s)) |
| `GL_ServiceEntry_01` | utilities/service-entry | coplanar: metal_galv @(0.00, -0.07, 0.00) (`service_entry`) and metal_dark @(0.00, -0.12, 0.03) (`service_entry`) share a face plane (9 face pair(s)) |
| `GO_Cubicle_Pod_01` | cubicle/pod | coplanar: office_dark @(0.20, 0.75, 0.01) (`box`) and metal_dark @(0.20, 0.69, 0.35) (`cubicle_pod`) share a face plane (4 face pair(s)) |
| `GO_Cubicle_Pod_01` | cubicle/pod | coplanar: laminate @(0.00, 0.40, 0.74) (`_worksurface`) and wood_dark @(0.00, 0.08, 0.74) (`_worksurface`) share a face plane (1 face pair(s)) (and 1 more like it) |
| `GO_Cubicle_Worksurface_01` | cubicle/worksurface | coplanar: laminate @(0.00, 0.38, 0.74) (`_worksurface`) and wood_dark @(0.00, 0.06, 0.74) (`_worksurface`) share a face plane (1 face pair(s)) (and 1 more like it) |
| `GO_Desk_Steel_01` | office/desk | coplanar: black @(0.00, 0.00, 0.73) (`_desk`) and metal_galv @(0.00, -0.37, 0.73) (`_desk`) share a face plane (2 face pair(s)) |
| `GO_Desk_Wood_01` | office/desk | coplanar: laminate @(0.00, 0.00, 0.73) (`_desk`) and wood_dark @(0.00, -0.37, 0.73) (`_desk`) share a face plane (2 face pair(s)) |
| `GO_Printer_Desktop_01` | office/printer | coplanar: black @(0.00, 0.18, 0.11) (`shell`) and office_dark @(0.00, 0.00, 0.21) (`shell`) share a face plane (2 face pair(s)) |
| `GO_Printer_Desktop_01` | office/printer | coplanar: office_grey/Tray @(0.00, -0.20, 0.04) (`drawer`) and office_dark @(0.00, -0.19, 0.14) (`printer_desktop`) share a face plane (2 face pair(s)) |
| `GO_Shredder_01` | office/shredder | coplanar: office_dark @(0.00, 0.12, 0.25) (`shell`) and black @(0.00, 0.00, 0.49) (`shell`) share a face plane (2 face pair(s)) |
| `GO_WaterCooler_01` | office/water-cooler | coplanar: office_dark @(0.00, -0.18, 0.78) (`water_cooler`) and metal_galv @(0.00, -0.22, 0.70) (`water_cooler`) share a face plane (3 face pair(s)) |

### floating (77 findings)

| Model | Category | Finding |
|---|---|---|
| `GD_Broom_01` | clutter/broom | through: wood_light @(0.00, 0.00, 0.70) (`broom`) passes right through wood_dark @(0.00, 0.00, 0.26) (`broom`) and ends free 107.5 cm beyond it |
| `GD_DeskLamp_01` | lighting/desk-lamp | through: metal_dark @(0.00, -0.08, 0.37) (`desk_lamp`) passes right through metal_dark @(0.00, 0.02, 0.20) (`desk_lamp`) and ends free 2.8 cm beyond it |
| `GD_FloorLamp_01` | lighting/floor-lamp | floating: 1 part(s) float 15.0 cm from the rest: metal_dark @(0.00, 0.00, 0.02) (`floor_lamp`) |
| `GD_IroningBoard_01` | clutter/ironing-board | floating: 2 part(s) float 1.9 cm from the rest: metal_galv @(-0.30, -0.10, 0.42) (`ironing_board`) |
| `GD_KeroseneLamp_01` | lighting/kerosene-lamp | floating: 1 part(s) float 4.1 cm from the rest: copper @(0.00, 0.00, 0.32) (`kerosene_lamp`) |
| `GD_Monitor_01` | electronics/monitor | floating: 1 part(s) float 4.5 cm from the rest: fabric_grey @(0.00, 0.00, 0.07) (`monitor`) |
| `GD_MopBucket_01` | clutter/mop-bucket | through: wood_light @(0.05, 0.05, 0.75) (`mop_bucket`) passes right through paint_white @(0.05, 0.10, 0.38) (`mop_bucket`) and ends free 92.3 cm beyond it |
| `GD_PicnicBasket_01` | clutter/picnic-basket | floating: 1 part(s) float 5.5 cm from the rest: wood_dark @(0.00, 0.00, 0.35) (`picnic_basket`) |
| `GD_PottedPlant_01` | plants/potted-plant | floating: 2 part(s) float 4.2 cm from the rest: terracotta @(0.00, 0.00, 0.12) (`potted_plant`) |
| `GD_RotaryPhone_01` | electronics/rotary-phone | floating: 2 part(s) float 1.0 cm from the rest: black @(0.00, 0.00, 0.06) (`rotary_phone`) |
| `GD_Suitcase_01` | clutter/suitcase | floating: 1 part(s) float 1.5 cm from the rest: black @(0.00, 0.00, 0.54) (`suitcase`) |
| `GH_Armchair_Retro_01` | seating/armchair | floating: 1 part(s) float 2.0 cm from the rest: tractor_green @(-0.52, 0.34, 1.00) (`armchair_retro`) |
| `GH_Armchair_Retro_01` | seating/armchair | floating: 1 part(s) float 2.0 cm from the rest: tractor_green @(0.52, 0.34, 1.00) (`armchair_retro`) |
| `GH_Bed_Bunk_01` | bedroom/bed-bunk | floating: 1 part(s) float 1.5 cm from the rest: wood_dark @(-0.47, 0.00, 1.70) (`bed_bunk`) |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.5 cm from the rest: black @(-0.45, 0.00, 0.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.0 cm from the rest: paint_white @(-0.28, 0.00, 0.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.5 cm from the rest: fabric_grey @(-0.11, 0.00, 0.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 5.0 cm from the rest: wood_light @(0.06, 0.00, 0.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 5.0 cm from the rest: paint_white @(0.40, 0.00, 0.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.5 cm from the rest: paint_white @(-0.45, 0.00, 0.75) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.0 cm from the rest: fabric_grey @(-0.28, 0.00, 0.75) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.5 cm from the rest: wood_light @(-0.11, 0.00, 0.75) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 5.0 cm from the rest: black @(0.06, 0.00, 0.75) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 5.0 cm from the rest: fabric_grey @(0.40, 0.00, 0.75) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.5 cm from the rest: fabric_grey @(-0.45, 0.00, 1.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.0 cm from the rest: wood_light @(-0.28, 0.00, 1.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 3.5 cm from the rest: black @(-0.11, 0.00, 1.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 5.0 cm from the rest: paint_white @(0.06, 0.00, 1.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_Bookcase_Modern_01` | storage/bookcase | floating: 1 part(s) float 5.0 cm from the rest: wood_light @(0.40, 0.00, 1.25) (`bookcase_modern`), (-0.45 + k * 0.17, 0.0, 0.05 + row * 0.5 + ] |
| `GH_CoatRack_01` | storage/coat-rack | through: wood_dark @(-0.05, -0.05, 1.70) (`coat_rack`) passes right through wood_dark @(0.05, 0.05, 1.70) (`coat_rack`) and ends free 14.0 cm beyond it |
| `GH_Counter_Bar_01` | tables/counter-bar | floating: 1 part(s) float 4.0 cm from the rest: metal_galv @(0.00, -0.36, 0.20) (`counter_bar`) |
| `GH_Microscope_01` | office/microscope | floating: 1 part(s) float 3.5 cm from the rest: metal_galv @(0.00, -0.02, 0.10) (`microscope`) |
| `GH_RockingChair_01` | seating/rocking-chair | floating: 3 part(s) float 2.1 cm from the rest: wood_dark @(-0.27, 0.00, 0.04) (`rocking_chair`) |
| `GH_RockingChair_01` | seating/rocking-chair | floating: 3 part(s) float 2.1 cm from the rest: wood_dark @(0.27, 0.00, 0.04) (`rocking_chair`) |
| `GH_RockingChair_01` | seating/rocking-chair | floating: 1 part(s) float 5.7 cm from the rest: wood_light @(0.00, -0.02, 0.45) (`rocking_chair`) |
| `GH_Sofa_Damaged_01` | seating/sofa | floating: 1 part(s) float 1.9 cm from the rest: linen @(0.35, -0.50, 0.50) (`sofa_damaged`) |
| `GH_Sofa_Damaged_01` | seating/sofa | floating: 1 part(s) float 5.4 cm from the rest: linen @(0.20, -0.55, 0.42) (`sofa_damaged`) |
| `GH_Sofa_Damaged_01` | seating/sofa | through: wood_grey @(0.95, 0.10, 0.30) (`sofa_damaged`) passes right through fabric_brown @(0.00, 0.00, 0.20) (`sofa_damaged`) and ends free 13.0 cm beyond it |
| `GH_Sofa_Damaged_01` | seating/sofa | through: wood_grey @(0.95, 0.10, 0.30) (`sofa_damaged`) passes right through fabric_brown @(0.46, -0.04, 0.38) (`sofa_damaged`) and ends free 52.0 cm beyond it |
| `GH_Sofa_Retro_01` | seating/sofa | floating: 1 part(s) float 1.8 cm from the rest: rust_dark @(-0.90, -0.38, 0.14) (`sofa_retro`) |
| `GH_Sofa_Retro_01` | seating/sofa | floating: 1 part(s) float 1.8 cm from the rest: rust_dark @(-0.90, 0.38, 0.14) (`sofa_retro`) |
| `GH_Sofa_Retro_01` | seating/sofa | floating: 1 part(s) float 1.8 cm from the rest: rust_dark @(0.90, -0.38, 0.14) (`sofa_retro`) |
| `GH_Sofa_Retro_01` | seating/sofa | floating: 1 part(s) float 1.8 cm from the rest: rust_dark @(0.90, 0.38, 0.14) (`sofa_retro`) |
| `GH_Tub_01` | bath/tub | floating: 1 part(s) float 5.0 cm from the rest: metal_galv @(0.70, 0.30, 0.68) (`tub`) |
| `GI_Dryer_01` | laundry/dryer | floating: 1 part(s) float 1.0 cm from the rest: black @(0.12, -0.34, 0.82) (`dryer`) |
| `GI_Dryer_01` | laundry/dryer | floating: 1 part(s) float 1.0 cm from the rest: black @(0.22, -0.34, 0.82) (`dryer`) |
| `GI_Stove_01` | kitchen/stove | floating: 1 part(s) float 2.0 cm from the rest: metal_galv @(0.00, 0.00, 0.30) (`stove`) |
| `GI_Toaster_01` | kitchen/toaster | through: black/Lever @(0.14, 0.00, 0.14) (`toaster`) passes right through black/Lever @(0.15, 0.00, 0.14) (`toaster`) and ends free 0.9 cm beyond it (and 1 more like it) |
| `GI_TrashCan_01` | outdoor/trash-can | floating: 2 part(s) float 2.2 cm from the rest: metal_dark/Lid @(0.00, 0.00, 0.62) (`trash_can`) |
| `GI_VendingMachine_01` | service/vending-machine | floating: 1 part(s) float 2.1 cm from the rest: glow_cyan @(0.00, -0.41, 1.80) (`vending_machine`) |
| `GI_Wardrobe_01` | storage/wardrobe | floating: 1 part(s) float 1.0 cm from the rest: metal_galv @(0.00, 0.00, 1.72) (`wardrobe`) |
| `GL_UtilityPoleCorner_01` | utilities/utility-pole-corner | through: wood_grey @(0.00, 0.00, 4.00) (`utility_pole_body`) passes right through wood_dark @(0.00, 0.00, 1.00) (`utility_pole_body`) and ends free 75.0 cm beyond it |
| `GL_UtilityPoleTransformer_01` | utilities/utility-pole-transformer | through: wood_grey @(0.00, 0.00, 4.00) (`utility_pole_body`) passes right through wood_dark @(0.00, 0.00, 1.00) (`utility_pole_body`) and ends free 75.0 cm beyond it |
| `GL_UtilityPole_01` | utilities/utility-pole | through: wood_grey @(0.00, 0.00, 4.00) (`utility_pole_body`) passes right through wood_dark @(0.00, 0.00, 1.00) (`utility_pole_body`) and ends free 75.0 cm beyond it |
| `GO_Chair_Office_01` | office/chair | floating: 2 part(s) float 1.2 cm from the rest: black @(-0.27, 0.00, 0.58) (`chair_office`) |
| `GO_Chair_Office_01` | office/chair | floating: 2 part(s) float 1.2 cm from the rest: black @(0.27, 0.00, 0.58) (`chair_office`) |
| `GO_Chair_Office_01` | office/chair | through: black @(-0.09, -0.13, 0.08) (`chair_office`) passes right through black @(0.09, -0.13, 0.08) (`chair_office`) and ends free 29.6 cm beyond it (and 1 more like it) |
| `GO_Cubicle_Panel_High_01` | cubicle/panel | floating: 1 part(s) float 14.5 cm from the rest: office_dark @(-0.55, 0.00, 0.01) (`box`) |
| `GO_Cubicle_Panel_High_01` | cubicle/panel | floating: 1 part(s) float 14.5 cm from the rest: office_dark @(0.55, 0.00, 0.01) (`box`) |
| `GO_Cubicle_Panel_Low_01` | cubicle/panel | floating: 1 part(s) float 14.5 cm from the rest: office_dark @(-0.55, 0.00, 0.01) (`box`) |
| `GO_Cubicle_Panel_Low_01` | cubicle/panel | floating: 1 part(s) float 14.5 cm from the rest: office_dark @(0.55, 0.00, 0.01) (`box`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 7 part(s) float 3.5 cm from the rest: wood_dark @(0.95, 0.40, 0.34) (`cubicle_pod`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 2 part(s) float 14.5 cm from the rest: office_dark @(-1.30, 0.75, 0.01) (`box`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 2 part(s) float 1.5 cm from the rest: office_dark @(0.20, 0.75, 0.01) (`box`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 2 part(s) float 14.5 cm from the rest: office_dark @(1.30, 0.75, 0.01) (`box`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 1 part(s) float 14.5 cm from the rest: office_dark @(-0.20, 0.75, 0.01) (`box`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 1 part(s) float 14.5 cm from the rest: office_dark @(-1.50, -0.55, 0.01) (`box`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 1 part(s) float 14.5 cm from the rest: office_dark @(1.50, -0.55, 0.01) (`box`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 1 part(s) float 1.9 cm from the rest: metal_dark @(-0.80, -0.80, 0.35) (`cubicle_pod`) |
| `GO_Cubicle_Pod_01` | cubicle/pod | floating: 1 part(s) float 1.9 cm from the rest: metal_dark @(-1.45, -0.80, 0.35) (`cubicle_pod`) |
| `GO_Cubicle_Worksurface_01` | cubicle/worksurface | floating: 1 part(s) float 2.5 cm from the rest: metal_dark @(0.00, 0.67, 0.67) (`worksurface_corner`) |
| `GO_WaterCooler_01` | office/water-cooler | floating: 7 part(s) float 1.0 cm from the rest: office_dark @(0.00, -0.18, 0.78) (`water_cooler`) |
| `GO_Whiteboard_Stand_01` | office/whiteboard | through: metal_dark @(-0.59, 0.04, 0.95) (`whiteboard_stand`) passes right through metal_dark @(-0.59, 0.10, 0.05) (`whiteboard_stand`) and ends free 183.0 cm beyond it (and 3 more like it) |
| `GO_Whiteboard_Stand_01` | office/whiteboard | through: metal_dark @(-0.59, 0.10, 0.05) (`whiteboard_stand`) passes right through rubber @(-0.59, -0.04, 0.03) (`whiteboard_stand`) and ends free 13.9 cm beyond it (and 1 more like it) |
| `GO_Whiteboard_Stand_01` | office/whiteboard | through: cloth_red @(0.20, -0.01, 1.38) (`whiteboard_stand`) passes right through label_white @(0.00, 0.00, 1.40) (`whiteboard_stand`) and ends free 13.4 cm beyond it (and 1 more like it) |
| `GO_Workstation_01` | electronics/computer | floating: 4 part(s) float 21.5 cm from the rest: office_grey @(0.00, -0.20, 0.01) (`workstation`) |
| `GO_Workstation_01` | electronics/computer | floating: 1 part(s) float 27.5 cm from the rest: office_grey @(0.32, -0.20, 0.01) (`workstation`) |
