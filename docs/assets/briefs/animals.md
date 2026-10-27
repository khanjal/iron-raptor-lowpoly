# Brief: the animals (cat, collie, husky, cow, horse, pig, sheep, goat, hen)

Issue [#87](https://github.com/khanjal/iron-raptor-lowpoly/issues/87). Written with the `asset-brief` skill before any rebuild. United States reference (the animals of a US farm and household); style stays the faceted low-poly of `quadruped_builder.py` on the shared palette and the shared rig.

Heights and weights are rounded from the American Kennel Club breed standards (Border Collie, Siberian Husky); the cat is a typical non-pedigree house cat (the Cat Fanciers' Association does not register it, so its numbers come from veterinary anatomy references); chest, head and paw sizes of every species are estimates from veterinary anatomy and extension-service texts and photographs, not from breed standards. A range is the real spread (the table below divided by the height) with a little slack, widened where a real animal's numbers fall outside it: a model inside it reads as the animal, one outside it reads wrong whatever its colour.

## What was wrong (the thumbnails, issue #87)

| Seen | Cause in the numbers |
| --- | --- |
| head is a small wedge on a slab | the cat's head was 19 % of its trunk length (real 30-35 %) and much wider than long (1.66 times); the collie's 27 % (real 38 %) |
| no neck or shoulder | the head rings start at the back and run level with the spine; no shoulder blade or withers |
| narrow flat-sided body | the cat's 8-sided body section was a rectangle; no barrel (rib cage) and no tuck-up at the flank |
| thin legs, stub feet | straight tubes from elbow to ground, the foot a dark stub with no toes; the husky's legs were short and its chest too wide (the husky was 0.54 m tall with an elbow at 35 % of the height, real 50 %) |

## How the proportions are measured

All shares are of the back height **H** (top of the body over the withers) or the trunk length **L** (chest front to rump), so they hold at any size. `art/scripts/animal_proportions.py` measures a species dict by these definitions; `audit_animals.py` prints them and fails a species outside its range; `tests/test_animal_proportions.py` tests the table.

| Ratio | Meaning |
| --- | --- |
| `LH` | trunk length / back height |
| `width`, `depth` | widest and deepest body section, full size, / H |
| `elbow` | lowest point of the chest / H (what is left under the chest for the legs: leg length as a share of height) |
| `head` | head length along its slope (nose to the skull, where the ears sit; a horse's head is tipped 45 degrees, so its length counts, not its shadow on the floor) / L |
| `head_w` | head width at its widest (skull and cheeks) / head length |
| `carry` | top of the skull / H (the neck lifts the head above the back) |
| `leg_top`, `leg_low` | front leg width at the top ring and at the ankle / H |
| `paw` | front foot length / H |

## Per species: real measurements

| Species | Shoulder height | Trunk length (chest front to rump: point of shoulder to buttock) | Chest width / depth | Elbow height (legs) | Head length / trunk | Neck | Feet |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cat, domestic shorthair (4-5 kg) | 0.23-0.28 m | 0.30-0.38 m | 0.12-0.15 / 0.12-0.15 m | about 45 % of H | 0.09-0.11 m, 30-35 % | short; the head rides just above the back; head a round wedge, 0.07-0.08 m wide | small oval paws, 0.045-0.055 m long |
| Collie / farm dog (Border Collie; 14-25 kg) | 0.46-0.56 m | 0.52-0.62 m | 0.17-0.22 / 0.23-0.27 m | about 50 % of H | 0.19-0.23 m, 38 % | 0.15-0.2 m, raises the head 10-20 % above the withers | oval paws 0.09-0.10 m long |
| Husky (Siberian; 16-27 kg) | 0.51-0.60 m | 0.55-0.66 m | 0.19-0.24 / 0.25-0.29 m | about 50 % of H | 0.21-0.24 m, 36 % | strong, 0.15-0.2 m | large oval paws, 0.10-0.11 m |
| Golden retriever (25-34 kg) | 0.55-0.61 m | 0.60-0.70 m | 0.22-0.28 / 0.27-0.31 m | about 50 % of H | 0.22-0.25 m, 35 % | strong, medium; head carried a little above the back | round paws, 0.10-0.11 m |
| German shepherd (22-40 kg) | 0.55-0.66 m | 0.65-0.78 m (longer than tall, about 10 : 8.5) | 0.20-0.26 / 0.27-0.32 m | about 50 % of H | 0.24-0.27 m, 36 % | long, muscular, carried forward | oval paws, 0.10-0.12 m |
| Beagle (9-11 kg; the 15-inch variety) | 0.33-0.38 m | 0.40-0.48 m | 0.16-0.20 / 0.18-0.22 m | about 45 % of H | 0.17-0.20 m, 40 % | medium, clean; head carried up | round paws, 0.06-0.07 m |
| Bulldog (English; 18-23 kg) | 0.31-0.38 m | 0.40-0.50 m | 0.28-0.35 / 0.22-0.27 m | 30-40 % of H (a low, deep brisket) | 0.12-0.15 m to the skull, a muzzle of only 3-5 cm | very short and thick: the head sits on the shoulders | broad, thick paws, 0.08-0.10 m |
| Dachshund (standard; 7-15 kg) | 0.20-0.23 m | 0.38-0.46 m (about twice the height) | 0.11-0.14 / 0.13-0.16 m | about a third of H (the ground clearance) | 0.16-0.19 m, 40 % | long, carried up | large front paws for its size, 0.06-0.07 m |
| Stray (a medium mixed breed) | 0.40-0.55 m | about the collie's | as the collie | about 50 % | as the collie | as the collie | as the collie |
| Cow (Holstein) | 1.30-1.55 m | 1.5-1.8 m | 0.55-0.70 / 0.75-0.90 m | 43-50 % | 0.50-0.58 m, 30-33 % | short, level with the back | cloven hoof, 0.11-0.13 m long |
| Horse (riding, 15-15.2 hands = 1.52-1.57 m) | 1.45-1.65 m | 1.45-1.7 m | 0.40-0.58 / 0.75-0.95 m | 49-55 % | 0.60-0.70 m, 40-45 % | long, 0.7 m, head carried above the back | round hoof 0.13-0.15 m |
| Pig (domestic, market) | 0.75-1.0 m | 1.05-1.4 m | 0.50-0.65 / 0.50-0.65 m | 33 % | 0.36-0.45 m, 30-35 % | short and thick; jowl; ham at the rear | small cloven hooves |
| Sheep (adult ewe) | 0.65-0.85 m | 0.75-1.0 m | 0.30-0.40 / 0.40-0.50 m (wool adds 8 cm a side) | 40-45 % | 0.22-0.28 m, 28-33 % | short | small cloven hooves |
| Goat (dairy) | 0.70-0.90 m | 0.80-1.0 m | 0.28-0.35 / 0.40-0.50 m | 50 % | 0.22-0.28 m, 28-33 % | medium, raised | hooves, 0.07 m |
| Hen (laying hen, 2-2.5 kg) | 0.35-0.45 m high | a bird: body 0.25-0.32 m | 0.14-0.18 m wide | legs 30 % of height | head 0.06-0.08 m | upright S-neck, 0.12-0.15 m | four toes, 0.08-0.10 m span |

## The shape: what made them read wrong after #87 (issue #125)

The ratios above held, and the animals still looked like a straight tube on four posts with a horse's neck. The causes, and what the builder (`quadruped_builder.py`) and the species now do:

| Seen | Cause | Now |
| --- | --- | --- |
| the back and the belly two parallel lines | every body section a rounded box at about the same height | sections traced from the animal's side profile (top and bottom set apart: the withers high, the croup falling, the chest deep and forward of the front legs, the belly tucked up behind the ribs) |
| a box of a chest | the sections symmetric top and bottom | `body_keel` / `head_keel`: each section's lower half narrows towards the bottom (a rib cage's keel, a throat, a jaw) |
| legs stuck on under the body | each leg's first ring at the underside, straight down | the first ring inside the body at the shoulder or the hip (a profile ring may carry a fifth number, dx, to set it in), the upper arm and the thigh a little proud of the body |
| straight hind legs | the rings stacked vertically | the stifle forward of the hip and the hock behind it (the dogs' and cats' hind legs fold the other way from the old ones, so the gait solver measures each leg's folding direction on the rig) |
| a horse's neck on a dog | the neck's root on top of the back, rising steeply | the root inside the top of the chest, the neck forward and up at about 45 degrees (the horse's and the deer's still rise: theirs do) |
| a dog's face on a cat | a long sloping muzzle | a round domed skull, a steep short nose bridge, wide-based ears |

`animal_proportions.check_shape` measures these on the species numbers, and `audit_animals.py` and `tests/test_animal_proportions.py` fail an enforced species that misses them (shares of the back height H):

| Measure | Meaning | Limit |
| --- | --- | --- |
| `tuck` | how far the underline rises from the deepest point of the chest to the loin | at least 0.08 for the cats and dogs, 0.03 for the horse, cow, fox and deer, 0 for the rest |
| `front_in`, `hind_in` | how far the top of each leg is inside the body above its underside | at least 0.10 |
| `stifle` | how far the stifle (the most forward hind ring above 30 % of H) is in front of the hip | at least 0.03 |
| `hock` | how far the hock (the rearmost hind ring below 30 % of H) is behind the stifle | at least 0.06 |
| `root` | how far the top of the neck's root stands above the withers | at most 0.08 |

A straight tube on posts fails all of the first five (the test builds one from the collie). The farm animals of #87 had legs that started at the barrel's underside and a stifle that barely came forward; they got a shoulder and a thigh ring and a keel too. Triangles: dogs 1060-1164 (were about 1000-1050), cats 900 (676), farm animals 776-1040 (up by 40 each), within the budget below.

## Proportion table: the audit's ranges

These are the ranges in `animal_proportions.RANGES` (the test checks that the script and this table agree). Every four-legged animal fails the audit outside them. The horse's depth and elbow ranges start at 0.48 and 0.47: the horseman's rule is that the girth is as deep as the leg is long from the elbow, so both are about half the height (the first estimate of 0.50 and 0.55 was too high). The breeds' rows (#125) are estimates from the American Kennel Club standards' heights and photographs, like the collie's; the stray is checked against the collie's row. The hen is a biped and has its own table below.

| | LH | width | depth | elbow | head | head_w | carry | leg_top | leg_low | paw |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cat | 1.05-1.65 | 0.43-0.66 | 0.46-0.66 | 0.36-0.52 | 0.28-0.40 | 0.64-1.00 | 1.05-1.35 | 0.13-0.22 | 0.07-0.12 | 0.15-0.26 |
| collie | 0.95-1.35 | 0.30-0.50 | 0.44-0.58 | 0.44-0.54 | 0.31-0.44 | 0.45-0.62 | 1.05-1.30 | 0.12-0.18 | 0.07-0.11 | 0.15-0.24 |
| husky | 0.95-1.30 | 0.32-0.52 | 0.44-0.58 | 0.44-0.54 | 0.32-0.42 | 0.50-0.68 | 1.05-1.30 | 0.12-0.18 | 0.07-0.11 | 0.15-0.24 |
| retriever | 1.00-1.35 | 0.34-0.54 | 0.44-0.58 | 0.44-0.54 | 0.31-0.42 | 0.52-0.70 | 1.05-1.30 | 0.13-0.19 | 0.08-0.12 | 0.16-0.25 |
| shepherd | 1.05-1.35 | 0.32-0.50 | 0.44-0.58 | 0.44-0.54 | 0.32-0.44 | 0.44-0.60 | 1.05-1.35 | 0.12-0.18 | 0.07-0.11 | 0.15-0.24 |
| beagle | 1.00-1.35 | 0.36-0.54 | 0.46-0.60 | 0.42-0.52 | 0.32-0.44 | 0.48-0.66 | 1.05-1.35 | 0.13-0.19 | 0.08-0.12 | 0.16-0.25 |
| bulldog | 1.05-1.35 | 0.65-0.95 | 0.55-0.75 | 0.28-0.42 | 0.22-0.34 | 1.15-1.60 | 1.00-1.30 | 0.20-0.30 | 0.13-0.20 | 0.26-0.40 |
| dachshund | 1.65-2.20 | 0.45-0.70 | 0.58-0.78 | 0.25-0.38 | 0.32-0.46 | 0.38-0.56 | 1.20-1.55 | 0.18-0.30 | 0.11-0.19 | 0.24-0.38 |
| cow | 1.10-1.45 | 0.34-0.54 | 0.50-0.66 | 0.42-0.52 | 0.27-0.36 | 0.40-0.55 | 0.95-1.20 | 0.10-0.16 | 0.05-0.09 | 0.07-0.12 |
| horse | 1.00-1.25 | 0.26-0.38 | 0.48-0.64 | 0.47-0.60 | 0.38-0.50 | 0.30-0.45 | 1.15-1.45 | 0.07-0.12 | 0.045-0.07 | 0.05-0.11 |
| pig | 1.30-1.70 | 0.55-0.78 | 0.60-0.80 | 0.28-0.40 | 0.28-0.38 | 0.55-0.75 | 0.85-1.05 | 0.12-0.20 | 0.07-0.12 | 0.08-0.14 |
| sheep | 1.00-1.30 | 0.40-0.58 | 0.50-0.68 | 0.38-0.48 | 0.26-0.36 | 0.38-0.55 | 1.00-1.25 | 0.09-0.15 | 0.05-0.09 | 0.07-0.12 |
| goat | 1.05-1.35 | 0.34-0.50 | 0.50-0.66 | 0.44-0.54 | 0.26-0.36 | 0.38-0.55 | 1.00-1.30 | 0.09-0.15 | 0.05-0.09 | 0.07-0.12 |

### The hen's ranges (`animal_proportions.HEN`)

Measured by `measure_bird` on `biped_bird.CHICKEN_HEN`: H is the top of the head, the body is the egg-shaped trunk. A laying hen (Rhode Island Red, 2-2.5 kg) is about 0.40 m to the top of the head, her body 0.25-0.32 m from breast to tail root, 0.14-0.18 m wide, the shank (the bare leg) about 1.5-2.5 cm wide and 10 cm long with a feathered thigh above it, the toes 6-8 cm. Extension-service poultry guides and the American Poultry Association's standard give the same shape: a deep, full breast, a back that slopes up to a raised tail, and a short, thick neck that rises to a small round head.

| | LH | width | depth | legs | carry | shank | toe | tail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hen | 0.60-0.90 | 0.34-0.52 | 0.45-0.65 | 0.22-0.38 | 1.15-1.45 | 0.04-0.08 | 0.14-0.24 | 0.95-1.25 |

(LH body length / H; width, depth the body's, / H; legs the underside of the body / H; carry the top of the head / the top of the back; shank the leg's width at the ankle / H; toe the toes' length / H; tail the top of the tail / the top of the back.)

## Recognisable features (kept, faked, dropped)

- **Cat**: round head with a short muzzle, two upright triangular ears set wide (kept); eyes large and forward (kept); whisker pads (faked: a lighter muzzle); a long tail carried up with a curve (kept); the arched, tucked back and the rounded rump (kept: the body sections rise at the hips); toe splits (dropped; the paw is a flat oval).
- **Collie / farm dog**: long narrow head with a stop and a muzzle as long as the skull, half-folded ears, a ruff at the neck (the farm dog of #275, already there), a deep chest with a tucked waist, a tail with a hook (kept); feathered legs (faked with a colour).
- **Husky**: wolf-like head with a blunt, full muzzle and a pale mask, erect triangular ears set close, a thick coat that makes the body look broad and the neck full, a tail carried in a sickle curve over the back (kept); the face mask in white (kept as a coat colour); eyes ice-blue or brown (a variant, below).
- **Golden retriever** (#125): a broad skull and a strong muzzle, drop ears hanging beside the cheeks, a golden coat with lighter feathering under the tail, a straight tail carried level or low (kept); the feathering on the legs and chest (faked with the tail's underside only).
- **German shepherd** (#125): large upright ears, a long muzzle with a black mask, a tan dog with a black saddle down its back and sides, a bushy tail hanging in a sabre curve (kept); the sloping topline (dropped: the shared rig's body is level).
- **Beagle** (#125): a hound's head with long drop ears to the muzzle, a white muzzle and blaze, tan with a black saddle and white legs and belly, a tail carried up with a white tip (kept).
- **Bulldog** (#125): a huge broad head on almost no neck, a very short muzzle, small rose ears, a wide chest on short, thick, wide-set legs and narrow hips, a stub of a tail, white with fawn patches (kept); the undershot jaw and the wrinkles (dropped).
- **Dachshund** (#125): a long low body with about a third of its height under the chest, short thick legs, a long head with long ears, a tail carried in line with the back (kept); the dark chocolate coat is the palette's `dark_brown`.
- **Stray** (#125): the farm dog's build at 0.88 of its size with a medium coat, folded ears and dark patches on tan: a dog with no breed in particular.
- **Cow**: a deep barrel, a broad head carried level and tipped down with a wide muzzle, the knee halfway down the leg, a hoof (the bottom of the leg flared and dark), an udder, two horns and the Holstein patches (kept); the cloven split of the hoof (dropped).
- **Horse**: a long arched neck, a long head tipped 45 degrees, a body as deep as the legs are long, a mane and a full tail, tall ears (kept); the hoof is round and dark (kept as the dark flared foot).
- **Pig**: a long barrel as deep as it is wide, short legs, a big wedge head with jowls ending in a flat snout, floppy ears over the eyes, a curly tail (kept); the cloven hoof (dropped).
- **Sheep**: a woolly barrel wider than the legs are apart, thin dark legs, a narrow dark face with ears out to the sides, a tuft on the crown (kept); the fleece's texture (dropped).
- **Goat**: a slim straight-backed body, a narrow head with a beard and a pair of scimitar horns, ears out to the sides, a short tail up (kept); wattles and teats (dropped).
- **Hen**: an egg-shaped body, a raised tail, a comb and wattle, four toes (kept); feathers (dropped).
- **Feet** (all): a visible foot that is wider and longer than the leg above it, in the coat colour or a darker or lighter sock, never a dark stub; a hoof for the farm animals (the bottom of the leg flares into a dark foot: a separate shape would cost triangles for a detail nobody sees at 10 m).

## Variants as paints (see #48)

A variant is a recolour (the paint system, `tools/paints.py`), not a second model. Existing ids keep their coat. None of these animals has a `catalog.PAINTS` entry yet: the coats below are what to declare there once a rebuilt animal's coat colours are separate swatches (a follow-up of #48, not part of the proportions work).

| Model | Coats (paints) |
| --- | --- |
| `GN_CatTabby_faceted_01` | orange tabby (default), grey tabby, orange, black, grey (declared in `catalog.PAINTS`, issue #125). Tuxedo, calico and Siamese put their colours on other faces, so they are models of their own (variants of the tabby), as is the kitten |
| `GN_DogCollie_faceted_01` | black and tan (default), brown and white, blue merle, yellow, brindle (the farm dog's coats, already in `DOG_SKINS`) |
| `GN_DogHusky_faceted_01` | grey and white (default), black and white, red and white, all white; eyes blue or brown |

The kitten (`GN_CatKitten_faceted_01`, issue #125) is a 10-12 week kitten: 0.15 m to the back (estimated from photographs and growth charts: 0.13-0.18 m at that age), its head 1.15 times the adult's (37 % of the trunk; a kitten's head is larger for its body than a cat's, estimated 35-45 %) and its eyes about 1.44 times the adult's; it is checked against the adult cat's ranges, which it passes, but a head above 40 % of the trunk would need a kitten row of its own in `animal_proportions.RANGES`. The other dogs (retriever, shepherd, beagle, bulldog, dachshund, stray; issue #125) are models of their own, not paints: their shapes differ. They are built on the farm dog's builder by `species_farm_dog.make_breed` (the collie's sections moved and scaled, the rig scaled to the breed's height); the old `make_dog` failed nearly every ratio (a retriever 0.58 wide for its height and 0.35 to the elbow, a dachshund 2.5 times as long as tall) and was removed.

## Views to check

For every rebuilt animal, in Blender with `look` (mode `angles`) and again in the site's viewer:

1. **Side (right)**: the profile. Head carried above the back with a visible neck, a chest that hangs lower than the belly, a tucked waist, the hips rounder than the shoulders, four legs with a bend at the hock, feet longer than they are wide, a tail with a shape of its own.
2. **Front**: the body wider at the chest than the legs are apart; the head wider than the neck; two ears and two eyes visible; the legs under the shoulders, not at the sides.
3. **Top**: the body a barrel (widest at the rib cage, narrower at the waist), the head a wedge that narrows to the muzzle, the tail laid along the body.
4. **Three-quarter**, and at 10 m (the size in the game): it reads as the animal in a silhouette.

## Checklist for every animal

- [ ] `audit_animals.py` has no problem (parts, joins, spacing, size and proportions).
- [ ] The ratios in the table above.
- [ ] A neck and shoulder you can see from the side; the head is not a continuation of the spine.
- [ ] Barrel chest and tucked waist (dogs and cat); the legs are not longer than the trunk is deep.
- [ ] Feet (paws or hooves), not stubs.
- [ ] Faces -Y, origin on the floor, palette colours only, the same bone names and clips (dogs Idle / Walk / Trot / Run; the others Idle / Walk), the same ids.

## Budget and markers

The faceted animals are 500-1500 triangles (`docs/from-game/asset-list.md` class table); the rebuild may add up to about 30 % for the head, chest and paws. The husky is the exception: it moved from the simple dog builder (660 triangles) to the farm dog's builder (1048 triangles, the same as the collie), for the shoulders, haunches, ruff, lips and eye highlights that make a dog read as a dog. No hinge, slide, light or sound markers: the animals are rigged (`quadruped_rig.py`), not marked.

## Verdicts

| Model | Verdict | Reason |
| --- | --- | --- |
| Cat | rebuilt (#88) | head too small, slab body, long thin legs |
| Collie | rebuilt (#88) | head short and wide, no shoulder, stub feet |
| Retriever, shepherd, beagle, bulldog, dachshund, stray | rebuilt (#125) on the farm dog's builder | the old `make_dog` failed width, depth, elbow and head width on all six (and the length on the beagle and dachshund) |
| Husky | rebuilt (#88) | short and broad, chest hung too low (elbow at 35 % of the height, real 50 %) |
| Cow, horse, pig, sheep, goat | rebuild (done) | same causes (issue #87): bodies 8-sided slabs, thin legs with the knee too high, small wedge heads |
| Hen | rebuild (done), own check | a bird: the body is egg-shaped, the tail and wing shapes matter; it has its own table (`HEN`) |
