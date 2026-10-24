# Office equipment: first audit (paper and gaps)

Status: first pass; the faults in the table were fixed on 2026-10-24 (issue #37), see "Fixed" below. The copier, desktop printer, shredder and wastebasket (`art/scripts/office.py`) were built in Blender without exporting and looked at from four sides; sizes and positions below come from the script. Not yet looked at: the desks, cubicle kit, water cooler, filing cabinet, whiteboard, workstation and phone. US reference.

## Faults found

| Model | Fault | Cause in the script |
|---|---|---|
| GO_Printer_Desktop_01 | The output sheet is "half out": most of it is buried in the lid, and the rest sticks out past the back of the printer | A 0.21 x 0.28 m sheet is centred at y 0.1, z 0.24, tilted 12 degrees. The lid occupies z 0.22 to 0.25 and y -0.15 to 0.19, so the sheet is inside it. Its far end reaches y 0.24, about 5 cm past the back |
| GO_Printer_Desktop_01 | A dark open slit runs across the front, between the front panel and the lid | The body shell has no front face. The front panel stops at z 0.19 and the lid starts at 0.22, which leaves 3 cm open into the black inside |
| GO_Shredder_01 | An open strip across the front above the bin | The shell is open-fronted and 0.5 m high, the bin front ends at z 0.42: about 8 cm open to the inside |
| GO_Shredder_01 | No paper in or under the feed slot | The slot is only a dark patch |
| GO_Wastebasket_01 | The two crumpled paper balls sit on top of the lid, not inside the bin | The rim and a black disc close the top at z 0.30 to 0.31, the balls are at z 0.33 |
| GO_Copier_01 | Grooves 2 cm wide between the three tray fronts that read as gaps | The dividers are recessed 2 cm behind the tray fronts. Probably wanted as panel lines, but they look like open slits |
| GO_Copier_01 | The output-tray sheet is fine (sits on the tray, 0.2 x 0.28 m) | Not a fault; the check came out clean |

Common cause: `shell()` builds an open-fronted carcass and each model then covers the front with separate boxes, so every strip the boxes do not cover shows as a hole. The same helper is used by the desks, filing cabinet and cubicle pieces, which should be checked for the same thing.

## What to change

- Printer: put the sheet on the top output ramp, lying on the lid or leaving the output slot, with about a third of its length out; do not let it sink into the lid or pass the back. Close the front strip with a front rail.
- Shredder: close the strip above the bin (a front panel or a taller bin front), and show a sheet entering the feed slot.
- Wastebasket: either an open basket with the paper balls inside (hollow, per the quality bar), or balls resting on the lid.
- Copier: make the tray-front grooves shallower or fill them with a trim colour.
- Add an audit check for open faces: any `shell()` front that is not covered by drawer, door or panel boxes.

## Family members and variants to consider

Laminator, hole punch, stapler, tape dispenser, paper tray / inbox, paper ream and box, multi-function printer with a document feeder, large floor copier with finisher, label printer, fax machine, binding machine, paper cutter. Variants: colour themes (white, grey, black), paper level in trays (full, half, empty), with or without a sheet in the output.

## Fixed (2026-10-24, issue #37)

Printer: the sheet lies on the output ramp on the lid, its low end on the cover and its far end short of the back, and the front panel now reaches the lid. Shredder: the bin reaches the top plate (the Bin pivot in `art/data/interactions.json` moved from z 0.22 to 0.25) and a sheet goes into the feed slot. Wastebasket: an open dish with a rim and the paper inside it. Copier: the tray dividers are flush with the tray fronts. Built in Blender and looked at from three sides. Not done: the audit check for uncovered `shell()` fronts and the look at the other pieces (#38).
