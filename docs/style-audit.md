# Style audit: which Modern / Retro / Damaged pieces have their own design

Written for issue #48. Source: `art/scripts/home_styles.py` and the file lists of the game repo at `89815f4` (Household, Decor and Interactive, Modern / Retro / Damaged / Classic folders).

A style is a colour theme (`THEMES`) unless the piece has an `@variant`, which is a hand-built shape. Damaged also runs `props_lib.damage()` (parts go missing, the piece sags and tilts, grime), so a Damaged piece is never only a recolour; the Damaged fridge and wardrobe in this repo differ from their base in the pose of their doors and in triangle count.

| Style | Files in the game repo | Own design (`@variant`) | Colour only (can be a theme) |
|---|---|---|---|
| Modern | 161 | 20 | 141 |
| Retro | 161 | 18 | 143 |
| Damaged | 161 | 12 + `damage()` on all | 0 (every one is its own model) |

The counts are an upper bound for the colour-only column: `python tools/paints.py A B` is the real test of a pair, and it has been run on the three style pairs that exist here (`GI_Fridge` Modern and Retro fold, Damaged does not).

## Pieces with their own design

**Modern** (20): `GD_Clock_Wall_Modern_01`, `GD_FloorLamp_Modern_01`, `GD_Radio_Modern_01`, `GD_TV_Flat_Modern_01`, `GD_TableLamp_Modern_01`, `GH_Armchair_Modern_01`, `GH_Bed_Double_Modern_01`, `GH_Bookcase_Modern_01`, `GH_Chair_Dining_Modern_01`, `GH_Chair_Kitchen_Modern_01`, `GH_Desk_Modern_01`, `GH_Dresser_Modern_01`, `GH_Fridge_Modern_01`, `GH_Nightstand_Modern_01`, `GH_Rug_Modern_01`, `GH_Sofa_Modern_01`, `GH_Stove_Modern_01`, `GH_Table_Coffee_Modern_01`, `GH_Table_Dining_Modern_01`, `GH_Wardrobe_Modern_01`

**Retro** (18): `GD_Clock_Wall_Retro_01`, `GD_FloorLamp_Retro_01`, `GD_Radio_Retro_Retro_01`, `GD_TV_CRT_Retro_01`, `GD_TableLamp_Retro_01`, `GH_Armchair_Retro_01`, `GH_Bed_Double_Retro_01`, `GH_Bookcase_Retro_01`, `GH_Chair_Kitchen_Retro_01`, `GH_Dresser_Retro_01`, `GH_Fridge_Retro_01`, `GH_Nightstand_Retro_01`, `GH_Rug_Retro_01`, `GH_Sofa_Retro_01`, `GH_Stove_Retro_01`, `GH_Table_Coffee_Retro_01`, `GH_Table_Dining_Retro_01`, `GH_Wardrobe_Retro_01`

**Damaged** (12): `GD_FloorLamp_Fallen_01`, `GD_TV_CRT_Smashed_01`, `GH_Armchair_Damaged_01`, `GH_Bed_Single_Damaged_01`, `GH_Bookcase_Tipped_01`, `GH_Chair_Kitchen_Damaged_01`, `GH_Curtains_Torn_01`, `GH_Dresser_Damaged_01`, `GH_Fridge_Damaged_01`, `GH_Sofa_Damaged_01`, `GH_Table_Dining_Overturned_01`, `GH_Wardrobe_Damaged_01`
