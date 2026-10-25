# Insects: ant and caterpillar segments

Scope: body segments of `GN_Ant_01` and `GN_Caterpillar_01` (issue: "body segments don't look right"). Other insects were checked for the same fault, see the end.

| Member | Real anatomy (reference: standard entomology texts, a worker carpenter ant is about 6 to 13 mm, a late-instar caterpillar 3 to 5 cm) | Before | Verdict |
|---|---|---|---|
| Ant | Three body parts: head, mesosoma (thorax and the first abdominal segment, carries all six legs), gaster; joined by a narrow petiole (waist node). Elbowed antennae, mandibles. | Three blobs that touched only at points, no waist, the rear leg pair sat at the very end of the mesosoma, against the gaster, no mandibles, short antennae. | Wrong shape: fixed (petiole added, mesosoma lengthened, legs on the mesosoma, mandibles, longer elbowed antennae). |
| Caterpillar | Head capsule, 3 thoracic segments with 3 pairs of true (jointed) legs, 10 abdominal segments with prolegs on abdominal segments 3 to 6 and claspers on the last; 13 body segments in all. | Seven identical beads with gaps between them, a leg stub on every segment, no true legs. | Wrong shape: fixed (11 overlapping segments: 3 thoracic with thin legs, 8 abdominal, 4 proleg pairs, a clasper pair, head capsule). The real count of 13 is cut to 11 to hold the triangle budget. |

Budget: ant 368 (a 14 mm insect with antennae, under the animal class floor on purpose), caterpillar about 800 triangles (animal class, 500 to 1,000). Moving parts: `Leg_*`, `Head`, `Seg1..` as before; the ant gains `Antenna_L` and `Antenna_R` bones.

Source: general entomology references (ant: head, mesosoma, petiole, gaster; caterpillar: head, 3 thoracic and 10 abdominal segments); no images were copied. Variants and family members: none added here (colour variants such as a red fire ant or other caterpillar colours are a later batch).

Other insects (read in the script, not rendered): ladybug, beetle, firefly, honeybee, moth, dragonfly, spider each have a body that overlaps its neighbours and legs on the thorax, so nothing else needed changing here.

## Fly clips: still bodies (issue #96)
A bee, wasp, housefly, mosquito or dragonfly beats its wings hundreds of times a second and its body does not visibly bob, so their Fly clips move only the wings (and the dragonfly's hind wings against its fore wings); the body bone does not move. A butterfly or moth flaps slowly and does rise and fall, but gently: 3 mm of a 25 mm butterfly (was 6 mm) and 2 mm for the moth (was 4 mm), pitching 3 and 2.5 degrees. The wing beat is a stylised 3 to 4 Hz (4 to 8 frames at 24 fps), not the real rate, which aliases at 60 fps; the wings blur in the viewer anyway.
