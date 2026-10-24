# Insects, batch 1 of the wider cast (issue #80, 2026-10-24)

The list comes from the creatures of the game Grounded and Grounded 2 (see the comment on #80), as real species. Eight new insects in `art/scripts/insects.py`, rigged and keyed by `insect_anim.py` like the others (head to -Y, feet on z = 0, built in millimetres):

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

## Known limits
Plain blobs and rods (flat faceted style); the flyers' legs do not move, the walkers' legs are three simple jointed rods, the mantis's raptorial forelegs are static (the walk clip moves its two pairs of walking legs), the fly and mosquito wings are single flat ellipses and the wasp has two ellipses a side. Sizes were taken from the usual field-guide lengths, not measured on a specimen.

## Still to do from #80
Aphid, weevil, stag beetle, scarab, tick, scorpion, wolf spider, orb weaver, jumping spider, centipede, millipede, grub, snail, bumblebee, hornet, gnat; variants (black and red ants, more butterflies) as paints.
