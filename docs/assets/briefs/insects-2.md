# The wider cast of insects and arachnids, batches 1 and 2 (issue #80, 2026-10-24)

The list comes from the creatures of the game Grounded and Grounded 2 (see the comment on #80), as real species. Sixteen new creatures in `art/scripts/insects.py` (eight insects in batch 1, four beetle-like insects and four arachnids in batch 2), rigged and keyed by `insect_anim.py` like the others (head to -Y, feet on z = 0, built in millimetres):

| Model | Real size and anatomy | Parts and clips |
|---|---|---|
| Stink bug (`GN_StinkBug_01`) | brown marmorated stink bug, about 15 mm: shield-shaped body, broad pale-edged pronotum, small head, long antennae, six legs | Idle, Walk |
| Housefly (`GN_Housefly_01`) | about 7 mm: grey thorax and abdomen, big red compound eyes, two clear wings, bristly legs | Idle, Fly |
| Mosquito (`GN_Mosquito_01`) | about 6 mm: slim banded body, long proboscis, narrow wings, very long thin legs | Idle, Fly |
| Wasp (`GN_Wasp_01`) | about 16 mm: yellow and black banded abdomen on a thin waist, black thorax, yellow face, four clear wings | Idle, Fly |
| Cockroach (`GN_Cockroach_01`) | American cockroach, about 35 mm: flat reddish-brown oval, shield-like pronotum, very long antennae, cerci | Idle, Walk |
| Cricket (`GN_Cricket_01`) | house cricket, about 20 mm: big head, folded wings, two big jumping hind legs, very long thin antennae | Idle, Hop |
| Praying mantis (`GN_Mantis_01`) | about 60 mm: long green body, triangular head with big eyes, folded raptorial forelegs, two pairs of walking legs | Idle, Walk |
| Earwig (`GN_Earwig_01`) | about 14 mm without the pincers: slim dark brown body, reddish head and pronotum, curved pincers at the tail | Idle, Walk |

## Batch 2 (the same issue)
| Model | Real size and anatomy | Parts and clips |
|---|---|---|
| Aphid (`GN_Aphid_01`) | green aphid, about 3 mm: soft pear-shaped body, small head, long antennae, two cornicles at the tail | Idle, Walk |
| Weevil (`GN_Weevil_01`) | about 8 mm without the snout (11 mm with it): rounded dark body, a head drawn out into a long snout, elbowed antennae from its middle | Idle, Walk |
| Stag beetle (`GN_StagBeetle_01`) | male, about 40 mm with the jaws: chestnut wing covers, black pronotum and head, huge branched jaws | Idle, Walk |
| Scarab beetle (`GN_Scarab_01`) | dung beetle, about 25 mm: domed blue-black body, flat shovel head, broad legs | Idle, Walk |
| Scorpion (`GN_Scorpion_01`) | about 55 mm long with the claws: flat tan body, two big claws, eight legs, a five-segment tail curled over the back to a stinger | Idle, Walk (eight legs) |
| Wolf spider (`GN_WolfSpider_01`) | about 25 mm body: brown, a pale stripe down the back, two big front eyes, long strong legs | Idle, Walk (eight legs) |
| Orb-weaver (`GN_OrbWeaver_01`) | about 21 mm body: big round abdomen with a bright orange spot, small cephalothorax, long legs | Idle, Walk (eight legs) |
| Jumping spider (`GN_JumpingSpider_01`) | about 8 mm: stocky black cephalothorax, two huge front eyes, brown abdomen with a chevron, short legs | Idle, Walk (eight legs) |

## Known limits
Plain blobs and rods (flat faceted style); the scorpion's tail and the weevil's snout are static (only the weevil's antennae move), the arachnids' idle moves only the front pair of legs; the housefly's legs do not move (the mosquito's hang down in its Fly clip: thigh and shin are separate pieces), the walkers' legs are three simple jointed rods, the mantis's raptorial forelegs are static (the walk clip moves its two pairs of walking legs), the fly and mosquito wings are single flat ellipses and the wasp has two ellipses a side. Sizes were taken from the usual field-guide lengths, not measured on a specimen.

## Still to do from #80
Tick, centipede, millipede, grub, snail, bumblebee, hornet, gnat, black widow, tarantula; variants (black and red ants, more butterflies) as paints.
