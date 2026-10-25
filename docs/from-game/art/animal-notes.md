# Animal field notes

Look an animal up **before** modelling it: its body style, its real size, how its tail, ears, coat and mane are made, and what it does that a model must be able to show. Record it here, build the species from it (`art/scripts/species.py`, `species_wild.py`, `species_pets.py`, `biped_bird.py`), and let `art/scripts/audit_animals.py` check the size against `REFERENCE` there (the same ranges, for the mammals: the turkeys are not in it). This file is the source for those numbers; if the numbers change, change both.

Sizes are the adult's: **shoulder (back) height**, **head-and-body length** (nose to the root of the tail) and **tail length**, in metres. Sources were found by web search in October 2026 and cross-checked against several (state wildlife agencies, Animal Diversity Web, zoo pages); where they disagree the range is wide.

## How to use this (the checklist before building a new animal)

1. **Body style**: what is the shape? (barrel or lean, high at the rump or the shoulder, a shoulder hump, digitigrade or flat-footed, how long the legs are against the body, how the neck sits, how heavy the head is.)
2. **Size**: shoulder height, length, tail length, weight: put them in the table below and in `REFERENCE`. A model that is 40% too big or too long looks wrong next to a person or a cow.
3. **Appendages**: tail (bushy, bare, a fan, short, a flag; carried up or down), ears (size against the head, shape, where they sit, erect or flopped), horns or antlers (which sex, the shape and direction of the beam and tines), hooves, paws or claws, beard, wattle.
4. **Coat and marks**: colours (from the shared palette), where the markings are (mask, stripes, stockings, spots, a pale belly), mane or ruff, hair length (the model can only show it as bulk).
5. **Behaviour the model has to support**: the poses and clips it needs (sit, lie, display, hide, play dead, bolt), what it does to its tail when alarmed.
6. Build, run the audit, and look at it from the side, the front and above; compare it with a photo.

## Wildlife

| Animal | Shoulder height | Head and body | Tail | Body style, appendages, coat (what the model must show) |
|---|---|---|---|---|
| Raccoon | 0.23-0.30 | 0.40-0.70 | 0.20-0.40 | Stocky, rounded back arched, short legs, hind legs longer than the front; a black mask over the eyes edged white, a pointed grey face, small rounded ears, a bushy tail with **5-7 dark rings**; dexterous front paws |
| Virginia opossum | 0.15-0.25 | 0.36-0.50 | 0.25-0.38 | Low and pot-bellied, short legs; a **white pointed face** with a pink nose, big **bare black ears**, grey coat with white-tipped guard hairs; a long, **scaly, nearly bare, prehensile tail**; plays dead when frightened |
| Striped skunk | 0.14-0.24 | 0.33-0.46 | 0.18-0.38 | Stout, short-legged, wide behind, a small conical head, small ears; black with a **white blaze up the forehead and two white stripes** from the neck (a V over the shoulders) down the back (and often onto the tail); a long **bushy** tail that goes up in warning (and a stamp of the front feet before it sprays) |
| Red fox | 0.35-0.50 | 0.45-0.90 | 0.30-0.55 | Slender, long legs, a narrow muzzle, **large erect pointed ears** (backs black); orange-red coat, **black legs ("stockings")**, white chest, cheeks and belly, a very **bushy tail with a white tip** (carried low, straight out when running) |
| White-tailed deer | 0.90-1.05 (doe 0.80-1.0) | 1.30-2.00 | 0.10-0.36 | Long legs, a deep chest, a long neck, a small head, big ears; tan or red-brown (summer), a white belly, throat and chin; a brown tail that is **white underneath and held up like a flag** when alarmed; only **bucks** have antlers (a main beam sweeping forward with several unbranched tines); **fawns** are red-brown with white spots and much smaller |
| White-tailed fawn | 0.40-0.65 | 0.70-1.10 | 0.08-0.22 | Red-brown with rows of white spots (they fade after a few months), long legs for the size, a big-eyed small head, a short white-underside tail |
| American black bear | 0.75-1.05 | 1.20-2.00 | 0.08-0.14 | Heavy, **no shoulder hump** (that is the grizzly; the black bear's back is level or rises slightly toward the rump), a straight facial profile, a **pale tan muzzle**, relatively **large oval ears**, a very **short tail**, shaggy black coat, big flat feet (plantigrade) |
| Wild turkey (tom) | up to 1.0-1.2 tall | 1.0-1.25 long | 0.25-0.50 tail feathers | A bare **blue-and-red head**, a red **wattle** and a **snood** over the beak (they swell when displaying), a **beard** of coarse filaments on the breast, dark bronze-brown body; the tail is a fan of long feathers that are **folded together behind the bird** at rest and **spread into a wide, rounded fan** when displaying (the wings drop, the body puffs); long pinkish legs, spurs |
| Wild turkey (hen) | smaller | about 0.75-0.95 | shorter | Duller grey-brown, a bare grey-blue head with little or no wattle, no beard (usually), a smaller tail |

Sources: state wildlife agencies and field guides (Virginia DWR, Minnesota DNR, Missouri MDC, Tennessee TWRA, National Park Service, Pennsylvania Game Commission), the Animal Diversity Web, Dimensions.com for sizes, bearbiology.org, and the Audubon and Wikipedia pages on the wild turkey.
The turkey's folded tail was not described in the sources found: it is from general knowledge (the tail feathers lie closed in a narrow stack).

## Farm animals (sizes the existing models are checked against)

| Animal | Shoulder height | Head and body | Notes |
|---|---|---|---|
| Cow (Holstein) | 1.30-1.55 | 1.8-2.6 | The udder sits between the hind legs, joined to the belly; both sexes can have horns |
| Horse | 1.40-1.70 | 2.0-2.6 | A long neck and head, tall pointed ears, a mane down the crest and a forelock, a full tail |
| Sheep | 0.60-0.95 | 0.9-1.4 | Woolly body, dark face and legs in many breeds, a short tail |
| Pig | 0.70-1.00 | 1.2-1.8 | Barrel body, a flat snout, floppy ears, a curly tail |
| Goat | 0.65-0.95 | 0.9-1.4 | Slim, horns that sweep up and back (both sexes), a beard, a short upright tail |

## Farm dog (#275: why the first one read as a sheep, and what the new one is)

The owner's play-test: "dogs still look weird and not like a dog, but maybe more sheep-looking". Looking at the old `GN_DogCollie` beside the sheep (renders in the PR): a **tube of a body** as deep as it was wide at every section (0.34 m deep: the belly hung down to 19 cm off the ground, so the legs showed only 19 cm and looked short), a head that was the neck carrying on (no skull, no stop, no jaw), ears that were flat slabs lying on top, a four-sided stub of a tail, white eyeballs, and a **black back over a white belly** (the sheep's dark face over a pale fleece). What a dog has that a sheep does not:

| Part | Border collie / shepherd cross (a medium farm dog) | The model |
|---|---|---|
| Size | 0.46-0.56 m at the withers (Kennel Club ideal 53 cm for a dog, females less), 12-25 kg; a shepherd cross up to about 0.60 | back 0.53 m, 0.95 m nose to rump, 0.30 m of tail (`REFERENCE` in `audit_animals.py`: 0.46-0.62 / 0.80-1.05 / 0.28-0.42) |
| Body | a **deep chest and a tucked waist**: the belly line rises towards the hind legs; the legs are about half the shoulder height | 0.27 m deep at the chest, 0.20 m at the loin: the belly is 25-30 cm off the ground; the body is 8-sided |
| Head | a **narrow wedge**: a flat skull, a stop, a muzzle as long as the skull that tapers to a black nose; the lower jaw and the lip line show | an 8-sided head, 0.12 m across the skull and 0.07 m at the muzzle, a black nose pad, a lip line along each side, the lower jaw in its own colour |
| Ears | medium, broad at the base, **semi-erect with the tips folded forward** (or pricked, or dropped: the Kennel Club standard allows all three) | lofted from the crown, upright for most of their height and then tipped forward |
| Neck | a **ruff** (the long coat forms a mane), not a cloud | a collar of fur 1 cm proud of the neck, in the coat's own colour or white |
| Tail | set on low, bone reaching at least the hock, **well furnished, with an upward swirl towards the end**, never carried over the back | 6-sided, bushy in the middle, hangs to the hock and hooks forward at the tip |
| Eyes | **dark**, oval, set in the front of the skull, looking ahead | dark brown with a black pupil and a white highlight |
| Coat | a dense medium-length coat (no wool), the face, ears and legs short and smooth; any colour, white never predominant: **black and tan, brown and white, blue merle, yellow, brindle** all occur on farm dogs | five coats (below): flat colours with markings, no woolly bulk |

The five coats are one model painted five ways (`art/scripts/species_farm_dog.py`, `SKINS`): black and tan (the default: tan legs, muzzle, chest and eyebrow spots), brown and white (white ruff, blaze, chest, socks and tail tip), grey merle (grey with black blotches, white ruff, chest and socks), plain yellow (golden with a cream belly and chest) and brindle (tan with dark stripes, a dark muzzle, white socks and chest). Because they have the same vertices and bones, the game swaps the mesh onto the dog that is in the scene (`DogSkin`, picked from the mission seed: `-dogSkin <id>` pins one for a test). The legs' profiles (joints and feet) are the old collie's (a haunch and a shoulder blob, skinned to the body bone and the leg's upper bone, join each leg's top ring to the slimmer body), so the leg bones keep their lengths and the clips' strides and speeds below (`gait-speeds.json`, regenerated: under 1% different) keep their meaning.

The sheep and goat are untouched (the cats and the husky were rebuilt later, issue #87: `docs/assets/briefs/animals.md`). Beside the new dog the sheep (a wide woolly barrel with a dark wedge for a face), the goat (horns, a beard, a short upright tail) and the cats (0.25 m, a round head, a long tail, always looking ahead) are each clearly something else; the other dogs (`DogRetriever`, `DogShepherd`, `DogHusky`...) still use the old generator (`make_dog`) and are not placed on the farm.

Sources: the [Kennel Club Border Collie breed standard](https://thekennelclub.org.uk/breed-standards/pastoral/border-collie/) (height, tail, coat), the [FCI standard no. 297](https://www.fci.be/Nomenclature/Standards/297g01-en.pdf), the [UKC standard](https://www.UKCDogs.com/docs/breeds/border-collie.pdf) (ears: drop, semi-erect or prick) and [Wikipedia](https://en.wikipedia.org/wiki/Border_Collie) (weights).

## Dog gaits (what the farm dog's speeds and clips are made from)

Researched for #127 after the owner saw the collie slide across the farm at a run with the walk clip. Dogs here are the eight `GN_Dog*` species (`species_pets.py`); only the collie is placed on the farm (the farm dog, `DogAI`).

| Gait | Real dog | Footfalls | What the clip shows | The collie here |
|---|---|---|---|---|
| Walk | 0.9-2.1 m/s, 0.7-1.1 strides/s, each foot on the ground 55-75% of the stride | lateral sequence: hind left, front left, hind right, front right | each foot is down for 60% of the stride, the head and tail sway | clip 0.90 m/s (1.4 strides/s); the AI walks home at 1.0 |
| Trot | about 2-4 m/s for a dog this size (general knowledge: no source found gave dog trot numbers) | diagonal pairs together (front left with hind right), a brief moment with all four feet in the air | feet down 46%, the body bobs twice a stride, the legs fold higher | clip 2.26 m/s (2.7 strides/s); the AI trots along a trail at 3.0 (played 1.3x) |
| Gallop (run) | border collies reach about 13 m/s (30 mph) flat out, and "alternate walking, trotting and short bursts" over a working day; a farm dog chasing is about 5-8 m/s and tires | rotary gallop: hind, hind, front, front, in a circle; a gathered flight (legs under the body, back arched) and a shorter extended one (legs reaching, back hollow) | feet down 20% of the stride each; the back bends only while no foot is under load (the strongest flexion is late in the swing, just before the hind feet land) | clip 6.66 m/s (3.3 strides/s); the AI gallops at 6.5 for 8 s |

**Decisions** (set in `FarmsteadHumans.BuildDog` and `DogAI`): walk 1.0 m/s, trot (search) 3.0, gallop 6.5 with a stamina: after `runSeconds` (8 s) the dog is winded and trots until it has half a burst back, which takes `windedSeconds` (6 s; it recovers at the same rate whether it trots or stands). Since #181 the dog no longer chases: it gallops only to get away from a player who has come right at it (nearer than 2.7 m), and trots up to its 7 m stand-off. A player's sprint is 6 m/s (`PlayerController`), so a player who walks or sprints away is never caught (the dog does not follow closer than its stand-off): the point of the alert is that the dog barks and the farmer comes.

**Why the clips run slower than the real gaits** (the rig, not the dog): the legs' top bone sits at the elbow (28 cm for the collie), so swinging it alone moves a planted hoof 13 cm at most per stance: the old walk was 0.29 m/s, and the game played it at up to 2.5x to keep up, which is the skating. The dog clips therefore also slide the top of each leg along the body (the shoulder blade and the hip: 45-55% of the leg length either way) and the stride follows what the legs can plant (stride 38-50 cm), at the cadence a dog this small can turn over (a limit that scales with the square root of the leg). The speeds are the largest at which every planted hoof still moves back exactly as fast as the body moves forward: that is the foot-slide report printed by `quadruped_walk.py`.

**Foot slide per clip** (`quadruped_walk.py` prints it and `Anims/gait-speeds.json` records the speed): for the planted hooves, the greatest distance a hoof drifts from the straight line it would follow if the body moved at the clip's ground speed, and how far it is above or below the ground. The old walk (leg 28 cm, stride 13 cm) drifted 1.4 cm, 10% of its stride, 0 cm off the ground; the collie's new Walk drifts 1.6 cm (4% of a 38 cm stride), Trot 2.4 cm (6%), Run 0.8 cm (2%), all 0 cm off the ground. The other breeds are in the PR description (they range 0.2-2.8 cm).

The speeds the other breeds' clips were made for follow from their leg length by Froude's rule (speed goes with the square root of the leg): about 0.65-0.95 m/s walking, 1.4-2.4 trotting and 4.4-7.2 galloping.

Sources: the review "[Kinetic and temporospatial gait parameters in a heterogeneous group of dogs](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5015230/)" (walk speeds, stride frequency and duty factor of dogs); Biancardi and Minetti (2012), "Biomechanical determinants of transverse and rotary gallop in cursorial mammals" (rotary gallop, gathered and extended flights); "Sagittal spine movements of small therian mammals" (J. Exp. Biol. 209:3925; the back flexes late in the swing and extends after lift-off); Dogster and Hepper on the border collie's top speed (about 30 mph) and its walk-trot-burst working day. These last two are popular pages with rough figures.

## Decisions already taken from these notes

- The raccoon, opossum, skunk, fox, deer and bear are scaled down to these sizes (`scale` in `species_wild.py`); the bear has no hump.
- The tom's tail lies folded together behind him and spreads into the fan only for the Display clip.
- The dogs' Walk, Trot and Run are made for ground speeds the shoulder-slid legs can plant (see "Dog gaits"); the farm dog's AI speeds and the Animator's playback follow from them (`gn_animal_clips.py` writes `Anims/gait-speeds.json`).
