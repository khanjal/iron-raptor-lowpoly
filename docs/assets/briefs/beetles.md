# Beetles (ladybug, beetle, firefly): brief and audit

Written for the leg and ladybug rework. US reference. Sizes are the ranges given by field guides and encyclopedia entries for the species named
([Coccinella septempunctata](https://en.wikipedia.org/wiki/Coccinella_septempunctata), [Michigan State IPM guide](https://www.canr.msu.edu/ipm/uploads/files/Natural_Enemies_PDFs/SevenSpottedLadyBeetles.pdf),
[Photinus pyralis](https://en.wikipedia.org/wiki/Photinus_pyralis)); the sources differ by a millimetre or two, which is below what the models can show.

## What a beetle's legs do (the rule all three follow)

Three legs a side, **all from the thorax**: a pair on each of the prothorax, mesothorax and metathorax, so they come out of the *underside* in a tight group
under the front half of the body, not along the whole length. Each leg is a thigh (femur) that goes out and slightly up from the hip to the knee, and a
shin (tibia) that goes down and out to the foot; the front pair reaches forward, the hind pair back. The numbers live in `art/scripts/insect_legs.py`
(one place for the body shapes and the legs, plain Python so `tests/test_insect_legs.py` can check hips, knees and feet without Blender): each hip sits
just inside the lowest body shape over it, each knee is clear of the body, each foot stands on z = 0.

Before: the legs hung from points along the whole body (hip heights guessed, front legs under the head, hind legs under the abdomen), some hips floated
below the shell (firefly) and the ladybug's six legs spread over the wing covers.

## Members

| Model | Real size | Recognisable features | Verdict |
|---|---|---|---|
| Ladybug (seven-spot, *Coccinella septempunctata*) | 6.5 to 8 mm long, 5 to 6 mm wide | near-hemispherical red dome; black head with white face patches; black pronotum with a white patch at each front corner; seven black spots (three on each wing cover, one shared behind the pronotum); a dark seam between the covers; black underside; short legs; short clubbed antennae | **Reworked**: flat-bottomed dome instead of a full ellipsoid (it hung under the ground line), pronotum and head as in the species, six spots plus the shared scutellar one lying on the dome, seam, club antennae, legs from the thorax. The wing covers are two separate pieces and the hindwings sit folded under them: a new `Open` clip lifts the covers and unfolds the wings |
| Beetle (a green beetle, about 3 cm) | no single species; ground and leaf beetles are 1 to 3 cm | pronotum narrower than the wing covers, hard shell, chewing mouthparts, sturdy legs | Legs fixed (thorax, three a side, wider stance). Body lifted 1.5 mm so the legs have length. Id, size, colours unchanged |
| Firefly (*Photinus pyralis*) | 9 to 19 mm, most about 10 to 14 | dark soft wing covers, pale or red-pink pronotum shield, glowing tail segment | Legs fixed (hips were under the shell, now on the underside under the pronotum and wing cover base). Glow, size, colours unchanged |

Budget: insects are the smallest class; the ladybug went from 464 to 922 triangles (spots and wings are separate pieces), the beetle and firefly are unchanged.
Moving parts: Leg_L/R 0 to 2, Antenna_L/R, Elytron_L/R and WingH_L/R (ladybug only); no `hinge` / `slide`, no markers (they are bones in the rig).

## Not done

- Hindwings are a plain clear wing outline; vein detail and the folded tip are left out.
- Other ladybug species and colour forms (the convergent lady beetle with its 13 spots, the Asian lady beetle that ranges from orange to black) are variants of this script, not built.
- The firefly has no wings or elytra that open; the beetle's covers do not lift either.
