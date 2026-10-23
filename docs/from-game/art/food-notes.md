# Food models: notes for the quality pass (#344)

The first batch rebuilds the weakest food models in `art/scripts/food_shapes.py` (called from `contents.py`). Better-made low-poly, the shared palette, real size,
origin on the floor at the middle of the base, facing -Y. Each brief: what it is and its size, what makes it recognisable, its colours, how the game uses it.

Colours appended to the palette (indices 108-115, nothing reordered): `egg_white`, `egg_brown`, `egg_blue`, `banana_yellow`, `lettuce_heart`, `cheese_cut`, `cheese_rind`, `cheese_hole`.
The Rotten versions come from `contents.ROTTEN` (a colour remap), as before.

## Banana (`FD_Banana_01`, `FD_Banana_Rotten_01`), 232 triangles
- A ripe Cavendish, 20 cm along its curve, 3.5 cm thick, lying on its back (the bend is a smile seen from the front, so the silhouette is a crescent at 10 m).
- Five ridges (ten points round, every other one pulled in), a loft along a real arc; a green stalk with a brown cut end on the left, a small black tip on the right.
- `banana_yellow` body, `corn_green` stalk, `bark` cut, `black` tip. Rotten: brown body, olive stalk.
- Carried or on a counter; it rests on the bottom of its curve, so z = 0 is the lowest point.

## Cabbage (`FD_Cabbage_01`, `_Rotten_`), 560 triangles
- A green cabbage, 17 cm across, 14 cm tall. A pale core ellipsoid and a stem cut flat on the floor, and five leaf shells round it, each one layer outside the last (6 mm apart).
- Every leaf has a zig-zag edge at the top and bottom and a pale midrib raised a millimetre; lighter leaves inside, darker outside (`corn_leaf`, `corn_green`, `grass`, `leaf_dark` x2), the pale `siding_green` for core and ribs.
- Shells are two-sided sheets (1.5 mm thick): Unity culls back faces, and looking down between the layers would otherwise show through the head. Rotten: olive and brown.

## Lettuce (`FD_Lettuce_01`, `_Rotten_`), 556 triangles
- A loose green-leaf lettuce, 17.5 cm across, 12.6 cm tall: a pale stub with three rings of cupped, ruffled leaves, five wide outer ones (flat, flaring), three middle, three upright heart leaves.
- Pale (`lettuce_heart`) at the base and heart, `corn_leaf` and `corn_green` at the edges. Leaves are two-sided sheets (2 mm thick) because you look into the cups.
- **Why it could not be seen:** the old model was one 18 cm ball in `corn_leaf` (a light green close to the farm's grass), with a second ball buried inside it (invisible), and the bottom of the ball 6.5 mm below the floor. It read as a plain green sphere and sank into the ground. I could not look at it in the world from this session.

## Corn (`FD_Corn_01`, `_Rotten_`), 408 triangles
- An ear with its husk, 21 cm tall: a stalk end, a yellow cob (a lathe, rounded tip), six husk leaves in two layers (the outer 7 mm clear of the inner) wrapped round it, wide at the base and narrowing to points that peel away so the top of the ear shows its kernels.
- **The glitch:** the old husks were three boxes through the middle of the cob (`(0.01, 0.04, 0.2)` boxes 2 cm from the axis, inside a cob 2.8 cm in radius), so every box poked through the cob and the cob through the boxes.
  The new leaves follow the cob's radius at their height plus a gap, and the layers peel by height so they never cross: `audit.py` reports no clipping.

## Eggs and carton (`FD_EggCarton_01`, `_Rotten_`), 1032 triangles (+72 for the `Lid`)
- A dozen eggs in a carton, 30.4 x 10.8 cm. A pulp tray with walls and 12 cups (cups are hollow sheets, so the eggs sit in them pointed end down), a red label band on the front, and a **hinged lid**.
- Eggs: six white, four brown, two pale blue (`egg_white`, `egg_brown`, `egg_blue`); not speckled, speckles would be tiny boxes poking through the shell.
- The `Lid` is a separate object with its origin on the hinge (back top edge, axis x), `limit` -105 degrees, **exported open** (`rest` -105) so the eggs show. It is in `art/data/interactions.json`; `PropRuntime` closes a part to 0 when it is not broken. A shut carton is `rest` 0.
- 1104 triangles with the lid is the largest food model: 12 eggs of 52 and 12 cups of 24; the eggs' pointed ends rest on the tray floor in their cups. Egg shells could drop to five sides if triangle budget matters.

## Cheese (`FD_CheeseWedge_01`, `_Rotten_`), 160 triangles
- A cheddar wedge cut from a wheel (9 cm radius, 64 degrees): the curved rind at the front (`cheese_rind`), a top sloping from 5.2 cm at the rind down to 2.2 cm at the point (`cheese_cut`), and two flat cut faces in `cheese_cut` with three square holes each (a darker `cheese_hole` floor, 9 mm deep).
- On a plate or in the fridge; the point is at the back.

## Audit of the whole Food folder (59 models, each with a `_Rotten_` twin where fresh)

From labelled contact sheets built in Blender (`contents.py` items, no export), plus the clipping check above. Verdicts: **fine**, **detail** (the shape is right, a real feature is missing),
**wrong** (does not read as the object), **fixed** (rebuilt, PR #350) or **PR #353** (rebuilt in the second PR, stacked on #350). The clipping column is the audit result.

| Folder | Model | Verdict | Why |
|---|---|---|---|
| Produce | Apple | PR #353 | was a ball with a box stem: no dimple, leaf or lobes |
| Produce | Orange | PR #353 | was a ball with a green square |
| Produce | Banana, Cabbage, Lettuce, Corn | fixed | #350 |
| Produce | Carrot | PR #353 | was a 6-sided cone with one green block |
| Produce | Tomato | PR #353 | was a squashed ball with a green square, no calyx star or lobes (clip 2 mm) |
| Produce | Potato | PR #353 | was one squashed ball |
| Produce | Onion | PR #353 | was a ball with a stick; no neck, roots or ribs |
| Produce | Pumpkin | PR #353 | was a smooth ball with a box stem: no ribs |
| Produce | Watermelon | PR #353 | wrong: a green ball ringed by six slabs sticking out |
| Bakery | BreadLoaf | PR #353 | wrong: a box with three sticks on it (clip 4 mm) |
| Bakery | Baguette | PR #353 | wrong: a 70 cm six-sided rod; no taper or scoring |
| Bakery | Pie | detail | a lattice drawn as one cross; no crimped edge, coplanar strips |
| Bakery | Cake | detail | right shape; flat tiers, no icing drips |
| Bakery | Donut | detail | a cylinder with a hole, not a ring |
| Bakery | CookieJar | detail | jar and lid read; cookies hidden behind opaque glass |
| Dairy | MilkCarton, MilkBottle | fine | gable carton and bottle read (a US gallon jug would be a variant) |
| Dairy | EggCarton, CheeseWedge | fixed | #350 |
| Dairy | Butter | detail | a box with a white top: no wrapper fold, no cut stick |
| Dairy | JuiceBox | detail | no gable top, straw is a stick |
| Drinks | SodaCan x3, BeerCan | detail | plain cylinders: no rim, taper, tab or ridges (clip 0) |
| Drinks | BeerBottle, WaterBottle, WhiskeyBottle, WineBottle | detail | silhouettes read; necks and caps crude (clip 2.6 mm) |
| Drinks | CoffeeCan | detail | no handle or lid ring |
| Canned | Can_Soup, Can_Beans | detail | as the soda cans |
| Canned | Jar_Pickles | PR #353 | wrong: reads as a pale blue column, the pickles hidden |
| Canned | Jar_Jam, PeanutButter | detail | lid and label fine; no shoulder |
| Canned | Ketchup, Mustard | detail | squeeze bottles read; the cap is a stack of cylinders (clip 5, 3.5 mm) |
| Boxed | CerealBox, PastaBox, CrackerBox | detail | boxes with a front panel; no flaps, window or text blocks |
| Boxed | FlourSack, SugarBag | PR #353 | wrong: gabled boxes, not paper sacks |
| Boxed | ChipsBag | PR #353 | wrong: a box, not a pillow bag |
| Boxed | CandyBar | detail | a flat slab: no wrapper ends (coplanar 1) |
| Prepared | Steak | detail | slab on a tray; no bone, fat, grill marks (clip 4 mm) |
| Prepared | Sausages | PR #353 | wrong: reads as a red slab (coplanar 3) |
| Prepared | Drumstick | PR #353 | wrong: a ball and a stick, reads as a lollipop |
| Prepared | TurkeyRoast | detail | right idea; the legs go 28 mm into the body (the worst clip) |
| Prepared | Fish | PR #353 | wrong: a grey slab with a flap (clip 2.5 mm) |
| Prepared | Hamburger, Sandwich, TVDinner | fine | read; Hamburger clips 7 mm (layers) |
| Prepared | HotDog | detail | bun and sausage are boxes and a cylinder |
| Prepared | PizzaBox | detail | a flat square: no lid edge, no open slice |
| Pet | DogBone | fine | reads; knobs clip 6 mm |
| Pet | CatFoodTin | detail | as the cans |
| Pet | HayFlake, SeedBag | detail | boxes with a band / a label |

**`_Rotten_` files with the wrong state** (owner note on #344): a colour swap makes no sense for `FD_CookieJar_Rotten_01`, `FD_JuiceBox_Rotten_01`, `FD_PizzaBox_Rotten_01`, `FD_TVDinner_Rotten_01`, `FD_EggCarton_Rotten_01`, `FD_MilkBottle_Rotten_01` and `FD_MilkCarton_Rotten_01`: **wrong state, needs eaten/empty instead** (a state per item is planned in a separate issue). They are not being polished; the egg carton's was rebuilt with its fresh twin in #350 only because it shares the generator. Real produce, bread, meat, fish, cheese and butter keep their `_Rotten_` versions, and a rebuilt model's rotten version follows the new shape.

**Variants worth adding** (one object, several real types): eggs (white, brown, blue exist now inside the carton; a loose single egg and a half-dozen box), bread (loaf, sliced loaf, roll, baguette), apples (red, green), potatoes (russet, red), milk (carton, plastic jug), soda (can, bottle), cheese (block, slices), bananas (green, ripe, spotted). Listed on #344; none built.

## The clipping and contact checks (`audit.py`, `AUDIT_CLIP = True`)

Parts of a model that pass through each other or share a face, and parts that touch nothing (a contact test at 2 mm, since the older floating check only compares bounding boxes within 2 cm). See the docstring of `audit.py`; it cannot see two solids that pass through each other with no corner of either inside the other. To run it over the Food folder:

```python
runpy.run_path(r"<repo>\art\scripts\contents.py", init_globals={"EXPORT": False}, run_name="__main__")      # builds them in the scene, writes nothing
runpy.run_path(r"<repo>\art\scripts\audit.py", init_globals={"AUDIT_NAMES": ("FD_",), "AUDIT_CLIP": True}, run_name="__main__")
```

Result after this batch (Food folder, 95 models, fresh and Rotten): the six models above are clean. These still report something and are **not fixed in #350** (PR #353 rebuilds `BreadLoaf`, `Fish`, `Tomato` and `Sausages`, which are clean there; the heights below are the old models') (the `Rotten` twin of each has the same defect):

| Model | Check says | Where (z from the floor, metres) |
|---|---|---|
| `FD_TurkeyRoast` | clip x3, 28 mm | a part at z 0.045-0.115 (a leg or wing) sunk into the body (0.002-0.198) |
| `FD_Hamburger` | clip x2, 7 mm | two layers at z 0.024-0.040 and 0.024-0.079 |
| `FD_DogBone` | clip x4, 6 mm | knobs at z 0.004-0.036 against the shaft (0.007-0.033) |
| `FD_Ketchup`, `FD_Mustard` | clip, 5 and 3.5 mm | a small top part (z 0.185-0.205 and 0.155-0.175) in the bottle |
| `FD_BreadLoaf` | clip, 4 mm | a strip at z 0.135-0.145 through the crust dome (0.061-0.139) |
| `FD_Steak` | clip, 4 mm | a strip at z 0.045-0.055 through the steak (0.019-0.049) |
| `FD_WhiskeyBottle`, `FD_WineBottle` | clip, 2.6 mm | the stopper (z 0.240-0.270, 0.317-0.347) in the neck |
| `FD_Fish` | clip, 2.5 mm | the tail (x 0.138-0.262, below the floor to 0.111) in the body |
| `FD_Tomato` | clip, 2 mm | the calyx (z 0.063-0.069) in the fruit |
| `FD_Pie` | coplanar x6 | two lattice strips at z 0.059-0.065 in one plane |
| `FD_Sausages` | coplanar x3 | two sausages at z 0.010-0.030 sharing a face |
| `FD_CandyBar` | coplanar x1 | the wrapper (z 0-0.020) and a part at 0.019-0.023 |

**Contact test** (`gaps()`, 2 mm): after #353 the models rebuilt in both PRs are clean. It also finds parts that touch nothing in models not rebuilt yet: `FD_CookieJar` (the four cookies hover, nearest 18 mm: they sit inside the glass), `FD_MilkCarton` (the gable top 5 mm above the body) and `FD_Jar_Jam` (the jam inside the jar, 2.8 mm from the glass). Both `_Rotten_` twins have them too. The older bounding-box floating check reports none of them.
After #353 the clipping list above no longer has `BreadLoaf`, `Fish`, `Tomato` and `Sausages` (rebuilt); `Pie`, `CandyBar`, `DogBone`, `Hamburger`, `Ketchup`, `Mustard`, `Steak`, `TurkeyRoast`, `WhiskeyBottle` and `WineBottle` remain.

The shallow ones (2 to 5 mm) are caps and stems that are set into a body on purpose and may be fine in the world; the deep and the coplanar ones are the ones to look at first.
The Clothes folder has the same check available (hangers, shoes) and is not part of this list. The check does not look inside a moving part's own object (the egg carton's lid).
