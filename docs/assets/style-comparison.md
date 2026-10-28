# How our models compare with good low-poly work

A survey of every category in `site/manifest.json` (501 models) against published low-poly models, made on 2026-10-27 after a look at five third-party cats and dogs showed ours reading as thin and generic. It says what the good examples do, where we fall short, the weakest models, and what to change, category by category, ranked by how much each would gain. No model changes here: this is the survey, and each category's rework is its own issue and PR.

**References are described, never used.** Nothing was downloaded, traced or copied, and no third-party image or model is in the repository. The examples were looked at as gallery thumbnails on [Poly Pizza](https://poly.pizza) (searches for cat, dog, cow, deer, fox, character, car, burger, house, sofa, tree, spaceship, bee, axe, fridge, teddy, backpack and ufo), mostly the collections by Quaternius, Kenney, "Poly by Google" and a few single authors. Where this doc says "the references" it means that set. Our side is the 256 px thumbnails in `site/thumbs/`, looked at as contact sheets by category.

## What makes the references read well

The same handful of choices shows up across every category:

1. **Push the recognisable features past real size.** Heads, ears, eyes, paws, wheels, bun domes, axe heads and handles are 20-60 % bigger than real; the parts nobody looks for (necks, leg shafts, table aprons) stay real or shrink. A cat is a big round head with big ears; a burger is a dome of bun with layers spilling out.
2. **Colour in a few large blocks that follow the anatomy or construction.** A white bib, belly and socks on a cat or a deer; a black saddle on a shepherd; the cap, label and body of a bottle; the roof, walls and trim of a house. Stripes, if any, are few and broad. Shading comes from facets and light, not from many colours.
3. **A clear silhouette from three-quarter view.** Each model has one or two shapes that break its outline (a tail curl, a handle, a chimney, a spout) and they are made big enough to see at thumbnail size.
4. **Chunky ends.** Paws, hooves, hands, shoes, wheels, tool heads and furniture feet are wider than the shaft they end; a leg is never a stick of constant width.
5. **Faces that carry.** Eyes are large, set wide and often have a white or a highlight; muzzles and noses are a different colour block; on people the face has brows, a nose block and a mouth line, not just dots.
6. **Soft edges.** Boxes are bevelled or chamfered once; cushions and buns bulge; nothing reads as an untreated cube unless it is meant to.
7. **Framed tight.** The model fills 70-85 % of its tile, on a plain coloured backdrop, from about 30 degrees above and to the side.

Ours are generally correct in size and construction (the briefs and audits see to that), which is why they look plausible but plain: we stop at point 0, the real thing, and do little of 1, 2, 4 and 5.

## Before the categories: thumbnail framing (all models)

`site/viewer.js` (`_frameModel`) fits the camera to the model's bounding **sphere** (half the diagonal of its size) with 5 % margin. A cube fills the tile; anything tall, long or flat does not: a standing person is about 65 % of the tile's height and a quarter of its width, rugs, frames and flat things a sliver, and the margin around every model is wider than it needs to be. The references fill 70-85 % of the tile. (Long tools already span the tile's width; their problem is thinness, section 10.) Fit the camera to the model's **projected box** instead (its eight corners in camera space, the larger of the height and width fit, 8 % margin), keep the view direction, and regenerate the thumbnails with `tools/thumbs.html`. The same fit helps the viewer's opening view. This is the single change that improves every category's look in the browser at once, and it touches no model. Tracked in [#198](https://github.com/khanjal/iron-raptor-lowpoly/issues/198).

## Ranking

| Rank | Category | Models | Gain | Issue |
|---|---|---|---|---|
| 1 | People (and aliens) | 15 | High: every figure is thin, small-headed and faceless at thumbnail size | [#199](https://github.com/khanjal/iron-raptor-lowpoly/issues/199) |
| 2 | Animals: pets | 13 | High (in progress on `pets-stylise`) | (that branch) |
| 3 | Animals: wild and farm mammals, poultry | 16 | High: same gaps as the pets | [#200](https://github.com/khanjal/iron-raptor-lowpoly/issues/200) |
| 4 | Food: prepared food and packaged goods | 63 (17 of them produce) | High for a dozen models, low for the produce | [#201](https://github.com/khanjal/iron-raptor-lowpoly/issues/201) |
| 5 | Decor, toys, kitchenware, clutter, soft furnishings | 85 (all of `decor/*`) | High for the crude boxes | [#92](https://github.com/khanjal/iron-raptor-lowpoly/issues/92) |
| 6 | Clothing, footwear, bags | 7 (+4 elsewhere) | High, but few models | [#89](https://github.com/khanjal/iron-raptor-lowpoly/issues/89) |
| 7 | Insects and arachnids | 27 | Medium: good shapes, no faces, thin | [#202](https://github.com/khanjal/iron-raptor-lowpoly/issues/202) |
| 8 | Nature (trees and plants) | 2 (+4 plants) | Medium | [#91](https://github.com/khanjal/iron-raptor-lowpoly/issues/91) |
| 9 | Sci-fi props and ship parts | 22 | Medium: grey cylinders and boxes | [#203](https://github.com/khanjal/iron-raptor-lowpoly/issues/203) |
| 10 | Tools | 33 | Medium: thin heads and handles | [#204](https://github.com/khanjal/iron-raptor-lowpoly/issues/204) |
| 11 | Farm props and structures | 24 | Low-medium | (folded into [#92](https://github.com/khanjal/iron-raptor-lowpoly/issues/92)'s batches) |
| 12 | Appliances, fixtures, equipment | 46 | Low: right shapes, missing bevels and a few details | none (the item-fit audit covers fit) |
| 13 | Furniture | 58 | Low | none |
| 14 | Buildings | 24 | Low | none |
| 15 | Sports | 26 | Low (the glove is in #89) | none |
| 16 | Vehicles, ships and ship interiors | 40 | Low: the best-looking group | none |

Each section below follows the same order: what the references do, where we fall short, the weakest models, and the changes.

---

## 1. People (`people/*`, 15)

**References.** The stylised low-poly people (Quaternius's character sets, "Poly by Google" figures, the chibi packs) carry a head of 1/5 to 1/6 of the height, hands and shoes visibly oversized, a slightly thickened neck and limbs, and clothing in three to five colour blocks with a contrasting belt, collar, boots and hair. The hair is one chunky mass with a fringe or parting shape, not a cap. Faces have large eyes (often with whites), brows and a nose block. They stand with a little space between arms and body.

**Our gaps.** Ours are anatomically right (the brief puts the head at 1/7.5 of the height; `head_scale` is 1.12) and so read small-headed and spindly at thumbnail size. Hands and feet are within real ranges and vanish. Faces are dot eyes on skin; at 256 px most figures have no face. Hair is a thin shell. The thumbnails leave them about 65 % of the tile's height (see framing). The clothing blocks are good (the Worker's hi-vis, the Sheriff's hat) and should stay.

**Weakest.** `GP_FarmerSpouse_01` and `GP_Nordic_01` (cream on skin, no contrast at all), `GP_FbiAgent_01`, `GP_FbiAgentF_01` and `GP_Mib_01` (one dark block head to toe).

**Changes.**
- Head to about 1/6 of the height for adults: `head_scale` about 1.30. The brief's child head (1/6.0-1/6.5, `audit_bodies.CHILD`) would then be no bigger than the adult's, so the child row moves up too (about 1/5); widen the brief's head row and `people_proportions.RANGES["head_w"]` only if the head's shape changes, not its scale.
- Hands and shoes 15-25 % larger: `RANGES["hand"]` (0.095-0.125) to about 0.10-0.15, `hand_w` (0.040-0.058) to 0.045-0.07, and the shoe length in `gp_builder.SHOE`; `wrist` and `calf` up about 10 %.
- Faces: eye whites or a light eye patch with a dark pupil, brows in the hair colour, a nose block and a mouth line in a darker skin tone (all palette colours by name).
- Hair as a volume with a fringe, sideburns or a bun; give every figure a contrasting belt and shoe colour.
- Aliens: the Grey's and Shadow's deliberate deviations stay; give the Grey the large black eyes the references all lean on.

## 2. Animals: pets (`animals/pet/*`, 13), in progress

Being reworked on branch `pets-stylise` (cat_tabby first, then the other cats and the dogs); listed here so the doc covers them and the other animal work copies what lands there.

**References.** Big round heads (cats) or big blocky heads (dogs) with ears 1.5-2x real; eyes large, often with a highlight; a muzzle block in a lighter colour; coats in a few blocks (white bib, muzzle, belly and socks; a Siamese's dark mask, ears, paws and tail; a beagle's saddle); legs that thicken into paws; sitting and lying poses as well as standing.

**Our gaps.** Heads and ears are real-sized; the tabby's stripes wrap the body like a bee's; legs are sticks with no paw; faces are dot eyes; the thumbnails frame the animal small. The measures in `animal_proportions.py` leave room for a longer head but almost none for wider legs, wider heads or bigger paws (on the tabby and most dogs, head_w, leg_top and leg_low are within 0.00-0.03 of their maximum; the cat's head_w and paw have 0.04-0.05 left, and the bulldog and dachshund 0.03-0.09).

**Changes** (as the pets branch is doing): see the shared animal changes in section 3.

## 3. Animals: wild and farm mammals, poultry (`animals/wild/*`, `animals/farm/*`, 16)

**References.** The Quaternius and "Poly by Google" deer, cows, foxes, bears and farm sets: deer with a white throat, belly and tail flash, dark nose and large ears; a cow with a pink muzzle and udder, horns and big ears, patches as two or three large shapes; a fox with a white chest and cheeks, black socks and a big brush; a bear with a lighter muzzle and a heavy head. Legs taper but end in a visible hoof or paw. Necks are thick.

**Our gaps.** Some markings are already there (the horse's black socks, mane and face, the bear's tan muzzle, the goat's two-colour coat, the fox's black socks), but the deer are uniform tan with no white throat, belly or tail flash; ears are at real size and so lost; eyes are dots; legs are thin; poultry legs are pink sticks under a brick body. The turkeys read as a brown box on legs at rest: the tom's fan is folded (it fans out in its Display clip, but the thumbnail is the Idle pose) and the snood and wattle are small.

**Weakest.** `GN_TurkeyTom_faceted_01` and `GN_TurkeyHen_faceted_01`, `GN_DeerDoe_faceted_01`, `GN_DeerBuck_faceted_01` and `GN_DeerFawn_faceted_01` (uniform tan), `GN_ChickenHen_faceted_01` (stick legs).

**Changes (all four-legged animals, pets included).**
- Head, ears and eyes up: ears 1.4-1.8x real; eyes larger with a highlight or white; a muzzle block in a lighter or darker colour.
- Colour blocks from the animal's real markings, not stripes round the body: white throat, belly and tail for deer; a white chest for the fox; two or three big patches on a cow; keep the markings that are there and make them bigger.
- Legs that thicken at the end into a paw or hoof of a different colour.
- Widen `animal_proportions.RANGES` and the brief's proportion table to allow it. Measured today against each row's maximum (on the species the unit test measures: the tabby, the first collie, the doe and one of each other row, so the figures are approximate):

  | Measure | Today (cat / dogs / hoofed / wild) | Proposed maximum |
  |---|---|---|
  | `head` (head length / L) | 0.30 / 0.25-0.38 / 0.31-0.41 / 0.26-0.46: 0.04-0.10 under the max | +0.06 on every row |
  | `head_w` | 0.05 under / 0.02-0.09 under / 0.03-0.10 under / 0.07-0.15 under | +0.15 on every row (cat 1.15) |
  | `leg_top` | at the max on the cat, most dogs, horse and pig; 0.02-0.05 under elsewhere | +0.04 |
  | `leg_low` | at the max or 0.01 under on most rows; 0.02-0.04 under on the bulldog, dachshund and the wild rows | +0.03 (deer 0.085, horse 0.09) |
  | `paw` | 0.01-0.06 under | +0.05 (hooves +0.03) |

  Better than editing the real ranges: keep the brief's real numbers and add a "stylised" column (or a `STYLISED` slack per measure in `animal_proportions.py`) that the audit enforces, so the real data stays documented. Add an `ear` measure (ear length / head length) to the brief so the ears are checked too.
- Poultry: rounder body, a head and comb or snood at 1.3x, thicker shanks (the chicken's `HEN["shank"]` 0.04-0.08 to about 0.10; the turkeys have no proportion row yet, NOTES says `HEN` does not fit them, so they need one). A thumbnail or a paint that shows the tom's fan displayed would make it read as a turkey at once.

## 4. Food: prepared food and packaged goods (`food/*`, 63, of which 17 produce)

**References.** Burgers (four very similar ones on Poly Pizza) are a tall domed bun with sesame seeds, and every layer (lettuce frill, tomato, cheese with drooping corners, patty) sticks out past the bun's edge in its own colour. The food packs' previews (Kenney's food kit, Quaternius's food pack) show the same habits at small size: rounded or bevelled shapes, every item in two or three strong colours, nothing left as a plain box.

**Our gaps.** Produce is good (apple, pear, carrot, strawberry, corn, banana read at once). The prepared food is built as stacked drums and slabs: the hamburger is a cylinder with a thin green line, the donut is a tall drum with a dark hexagon on top, the hot dog bun is a box, the candy bar is a two-colour slab, the pizza box is a plain brown box, the steak and sausages sit on boards as flat shapes, the cheese wedge has no holes. Packaged goods are right in shape but every box carries the same one-rectangle label.

**Weakest.** `FD_Donut_01`, `FD_Hamburger_01`, `FD_HotDog_01`, `FD_CandyBar_01`, `FD_PizzaBox_01`, `FD_CheeseWedge_01`, `FD_Steak_01`, `FD_Sausages_01`, `FD_Watermelon_01` (no stripes), `FD_Grapes_01` (spiky diamonds instead of round grapes).

**Changes.**
- Burger: domed top bun, flat heel, layers 10-15 % wider than the bun with a frilled lettuce ring and cheese corners; seeds as a few light dots.
- Donut: a torus about 2.5:1 wide to tall, icing as a wavy cap in a second colour, sprinkles as a few dots.
- Hot dog: a split, rounded bun with the sausage's ends showing and a mustard zigzag.
- Pizza: an open box with a pizza (crust ring, sauce, cheese, a few toppings) or the pizza alone.
- Cheese wedge with a rind colour and three or four holes; steak with a fat edge and grill lines; watermelon with dark stripes; grapes as round berries on a stem.
- Packaged goods: bevel the boxes, give each a second label block and a band, and caps a rim. Generic and unbranded (see #150).
- No proportion ranges to widen: the food briefs give real sizes, and these are shape changes.

## 5. Decor, toys, kitchenware, clutter, soft furnishings (`decor/*`, 85)

Tracked in [#92](https://github.com/khanjal/iron-raptor-lowpoly/issues/92) (comment added with this survey).

**References.** The bear and panda toys found for "teddy" are a round head about a third of the height with a muzzle and round ears, and stubby limbs; the general habit of the household models is one oversized identifying detail per object (a mug's ring handle, a kettle's spout and lid knob, a pot's two handles), and soft things bulge.

**Our gaps.** Many pieces are untreated boxes: the teddy bear and the doll are stacked cubes, the toy truck is two boxes on wheels, the mug is a square drum with a slab handle, the first-aid kit, lunchbox, laundry basket and suitcase are boxes with a stripe, the cushion and pillow are trapezoid slabs, the blanket a flat board. Electronics read well; lighting and wall pieces mostly read.

**Weakest.** `GD_TeddyBear_01`, `GD_Doll_01`, `GH_Mug_01`, `GD_ToyTruck_01`, `GD_LaundryBasket_01`, `GH_Cushion_01`, `GH_Pillow_01`, `GH_Blanket_01`, `GD_Lunchbox_01`, `GD_HangingPlant_01`, `GD_PottedPlant_01`.

**Changes.** Round the soft things (cushion and pillow with bulged faces and corner points, a blanket with a fold), rebuild the bear and doll with round heads at a third of the height, and give each kitchenware piece its handle and lid. Farm props (`farm/*`: feed sack, jerrycan, toolbox, milk can are plain boxes or drums) can ride along in the same batches.

## 6. Clothing, footwear and bags (`clothing/*`, 7, plus `GD_Backpack_01`, `GD_BootsPair_01`, `GD_Suitcase_01`, `GS_BaseballGlove_01`)

Tracked in [#89](https://github.com/khanjal/iron-raptor-lowpoly/issues/89) (comment added).

**References.** Backpacks are a rounded body with a flap, a buckle strap, a front pocket and two shoulder straps; shoes have a sole in a contrasting colour, a toe cap and laces; garments on hangers hang in a soft A-shape with a collar.

**Our gaps.** The boots are four boxes, the shoes two boxes, the folded pants and towel a striped block, the scarf a flat strip, the dress a flat red panel, the backpack a box with a box on it.

**Changes.** As in #89; add from this survey: the sole in a different colour and 10 % wider than the upper, the toe rounded, and soft items bulged rather than boxed.

## 7. Insects and arachnids (`animals/insect/*`, `animals/arachnid/*`, 27)

**References.** The low-poly bees (four on Poly Pizza, from Quaternius and two single authors) are a round, plump body with two or three broad bands, big eyes and large translucent wings, framed close. Eyes are the key: every one has two large eyes, and two of them a face.

**Our gaps.** The shapes and colours are right and several read well (ladybird, butterfly, dragonfly, caterpillar). Most have no eyes or tiny ones, legs are thin sticks of constant width, and bodies are hard-edged boxes; the moth's wings are flat beige hexagons; the honeybee and wasp are small in the frame.

**Weakest.** `GN_Moth_01`, `GN_Aphid_01`, `GN_Housefly_01` (eyes too small), `GN_Weevil_01`, `GN_Scarab_01`, `GN_Wasp_01`.

**Changes.** Large eyes in a contrasting colour on every insect; legs thickened at the femur and given a foot; bees and flies rounder with bands; moth wings with a darker pattern block. The insect briefs (`docs/assets/briefs/insects*.md`, `beetles.md`) would need a stylised allowance on eye size and leg thickness.

## 8. Nature: trees and plants (`nature/*`, 2, and the four houseplants)

Tracked in [#91](https://github.com/khanjal/iron-raptor-lowpoly/issues/91) (comment added).

**References.** Low-poly broadleaf trees are three to six clumped faceted blobs in two greens (lighter on top), a trunk that forks into two or three visible branches, and a slight lean; pines are stacked cones with a darker underside. Houseplants have big individual leaves.

**Our gaps.** The oak reads (clumped canopy, lighter top); the trunk is a single stick and the canopy sits on it like a lid. The pine is a single flat silhouette. The houseplants are weak (#91).

**Changes.** Visible branches into the canopy, two or three tiers of clumps; pine tiers as separate cones with a darker under-skirt; leaves as large flat shapes on plants.

## 9. Sci-fi props and ship parts (`sci-fi/*`, 22)

**References.** The spaceships and UFOs looked at (Quaternius, "Poly by Google" and single authors) use a light hull with one or two strong accent colours (red, orange, a striped band), a dome or cockpit in a contrasting colour, and exaggerated functional shapes (big nozzles, fins). Our ship hulls already do much of this; the props and parts do not.

**Our gaps.** Nearly every part is the same grey-green with dark grey bands and a cyan glow; many are a cylinder with two rings (power cell, fuel canister, containment pod) or a plain box (console module, scanner). They read as a set but not as individual things.

**Weakest.** `SH_ConsoleModule_01`, `SH_PowerCell_01`, `SH_FuelCanister_01`, `SH_HullShard_A_01`, `SH_HullShard_B_01`, `SH_CableTangle_01`, `SH_ThrusterNozzle_01`.

**Changes.** An accent colour per family (power: yellow, fuel: orange, comms: red), a chamfer on every box, panel lines as inset faces, handles and clamps, a flared and ribbed nozzle, a glowing core visible in the power cell.

## 10. Tools (`tools/*`, 33)

**References.** Low-poly axes and hammers have a head 1.3-1.5x real and a handle thicker than real with a grip colour; the blade's edge is a lighter metal block. They are framed close and diagonal so they fill the tile.

**Our gaps.** Our tools are real-sized, so heads are small and handles are thin lines; in the 256 px tiles they are hard to tell apart (axe, sledgehammer, hoe, rake and spade are all a line with a small grey end). Some are fine (watering can, hand truck, bench vise, cordless drill).

**Weakest.** `GT_Hoe_01`, `GT_Axe_01`, `GT_Sledgehammer_01`, `GT_FirePoker_01`, `GT_Spade_01`, `GT_SnowShovel_01`, `GT_Screwdriver_01`, `GT_Sprinkler_01`, `GT_WorkLight_01`.

**Changes.** Heads 1.3x, handles 1.3-1.5x thick with a grip block; edges in a lighter metal. Framing helps less here than elsewhere: long tools already span the tile's width. The hand-tools briefs (`docs/assets/briefs/hand-tools*.md`) would need a "stylised" allowance on head size and handle diameter.

## 11. Farm props and structures (`farm/*`, 24)

**References.** None looked at specifically; the general habits above apply (soft things slump, boxes are bevelled).

**Our gaps.** Barrels, crates, firewood, fences, gate and wheelbarrow read well. The feed sack is a box, the jerrycan a red box with a cap, the toolbox a red slab, the stool's legs are thin, the generator is a black box.

**Changes.** Sack slumped and tied, jerrycan with its X-pressing and three handles, toolbox with a lid line and a handle, hay bales with rounded edges. Small enough to go into #92's batches.

## 12. Appliances, fixtures, equipment (`appliances/*`, `fixtures/*`, `equipment/*`, 46)

**References.** The low-poly fridges (Quaternius and single authors) are slightly rounded boxes with a visible door gap, a big handle, and a kick plate or feet.

**Our gaps.** Shapes and details are right (washer and dryer portholes, stove, copier, microwave); edges are sharp and handles thin. The toaster, bread box, cooler and fuse box are plain. The fit of doors and drawers is covered by the item-fit audit ([`item-fit-audit.md`](item-fit-audit.md), PR #196).

**Changes.** A chamfer on the outer edges of white goods, handles 1.5x, a kick plate; the toaster with slots, lever and rounded ends. No issue: fold into the fit batches.

## 13. Furniture (`furniture/*`, 58)

**References.** The low-poly couches have puffy, separate cushions with gaps, rounded arms and visible feet.

**Our gaps.** Bookcases, dressers, desks, office chair and beds read well. Sofas and the armchair have hard-edged cushions; wall shelves are a plank.

**Changes.** Bulge the cushions and round the arms on `GH_Sofa_Modern_01`, `GH_Sofa_Retro_01`, `GH_Armchair_Retro_01`. Low priority.

## 14. Buildings (`building/*`, 24)

**References.** The low-poly houses ("Poly by Google"'s farmhouse and house) have roof overhangs, window frames in a trim colour, a porch with posts, a chimney and siding lines.

**Our gaps.** Ours have most of these (porches, chimneys, trim on the farmhouse and town house). The shed, outhouse and workshop are plain boxes with a door; the barn has no white trim or loft door, which is the one detail that makes a barn.

**Changes.** Barn: white trim on the corners and doors, an X-brace on the doors, a hay loft door. Sheds and workshop: a window, trim and a roof overhang. Low priority.

## 15. Sports (`sports/*`, 26)

**Our gaps.** Balls read well (seams and panels are right). The golf ball and hockey puck are plain; the bat, club and hockey stick are thin lines like the tools; the baseball glove is in #89. Low priority.

## 16. Vehicles, ships and ship interiors (`vehicles/*`, 40)

**References.** The low-poly cars ("Poly by Google", J-Toastie, a few others) are a little lower and wider than real, with large wheels and simple bright paint.

**Our gaps.** Our road vehicles are the best-looking models in the set: clear cabins, glass, wheels, lights. Wheels could be 10 % bigger. The ships read well; the triangle and MIB craft are dark and lose their silhouette on the grey thumbnail background. No issue.

---

## Order of work

1. Framing ([#198](https://github.com/khanjal/iron-raptor-lowpoly/issues/198)): one site change, every thumbnail regenerated.
2. Animals: finish the pets on `pets-stylise`, then the same stylised ranges and markings on the wild and farm animals ([#200](https://github.com/khanjal/iron-raptor-lowpoly/issues/200)).
3. People ([#199](https://github.com/khanjal/iron-raptor-lowpoly/issues/199)): head, hands, shoes, faces on the shared body.
4. Food ([#201](https://github.com/khanjal/iron-raptor-lowpoly/issues/201)), then decor ([#92](https://github.com/khanjal/iron-raptor-lowpoly/issues/92)) and clothing ([#89](https://github.com/khanjal/iron-raptor-lowpoly/issues/89)).
5. Insects ([#202](https://github.com/khanjal/iron-raptor-lowpoly/issues/202)), sci-fi ([#203](https://github.com/khanjal/iron-raptor-lowpoly/issues/203)), tools ([#204](https://github.com/khanjal/iron-raptor-lowpoly/issues/204)), vegetation ([#91](https://github.com/khanjal/iron-raptor-lowpoly/issues/91)).

Each rework starts with `asset-brief` (adding the stylised allowance to the brief's ranges where it has them) and follows `blender-assets` for parts, fit and clipping; ids and file names stay as they are.
