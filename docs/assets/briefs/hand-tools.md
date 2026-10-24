# Hand tools: batch 1 (2026-10-24)

Source: the game's prop catalogue (`docs/from-game/art/prop-catalogue.csv`, "Hand and power tools": 64 rows, most `missing`). This batch builds ten common hand and garden tools in `art/scripts/hand_tools.py`; the rest of the category is listed under "Still to do". US reference sizes.

| Model | Real size | What it shows |
|---|---|---|
| Claw hammer (`GT_Hammer_01`) | 0.28 m handle, 16 oz head | hickory handle, rubber grip, head across it with a round face and a long claw |
| Sledgehammer (`GT_Sledgehammer_01`) | 0.9 m handle, 0.16 m head (about 8 lb) | double-faced head across the handle |
| Axe (`GT_Axe_01`) | 0.8-0.9 m felling axe, 0.1 m bit | knob, eye, poll to one side and the bit to the other, edge parallel to the handle; lies on its side |
| Hand saw (`GT_HandSaw_01`) | 20 in (0.5 m) blade | flat blade with teeth along one edge, grip with a hand hole |
| Wrench (`GT_Wrench_01`) | 10 in open-end spanner | a jaw at each end |
| Screwdriver (`GT_Screwdriver_01`) | about 0.27 m | yellow handle, shaft, flat tip |
| Pliers (`GT_Pliers_01`) | 0.2 m slip-joint, open | crossed arms, rubber grips, plain jaws, pivot |
| Hoe (`GT_Hoe_01`) | about 1.5 m | long handle, goose-neck, flat blade 0.15 m wide |
| Spade (`GT_Spade_01`) | about 1.1 m | D grip, socket, rounded blade 0.2 x 0.28 m |
| Watering can (`GT_WateringCan_01`) | 0.24 m tall, 0.2 m across, about 7 L | galvanised body, long spout with rose, arched handle |

All lie flat on the floor along X, working end at +X (the watering can stands), origin on the floor at the middle of the tool's length (the watering can: at the body's centre), 44-156 triangles each, palette colours only (no new swatches).

## Known limits
- Shapes are plain boxes and six-sided handles (flat faceted style): no curved claw, blade or tapered saw. The hoe blade lies flat; a real hoe's blade angles down from the neck. The axe's cheek does not widen to the bit.
- Handles are six-sided; no emitters, no moving parts.

## Still to do in the category
Batch 2 built the plunger, rope coil, sawhorse, paint can, pruning shears, fire poker, hose, sprinkler, cord reel and hand truck; what is left is listed in `hand-tools-2.md`.
