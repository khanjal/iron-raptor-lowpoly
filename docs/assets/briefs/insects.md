# Insects: ant and caterpillar segments

Scope: body segments of `GN_Ant_01` and `GN_Caterpillar_01` (issue: "body segments don't look right"). Other insects were checked for the same fault, see the end.

| Member | Real anatomy (reference: standard entomology texts, a worker carpenter ant is about 6 to 13 mm, a late-instar caterpillar 3 to 5 cm) | Before | Verdict |
|---|---|---|---|
| Ant | Three body parts: head, mesosoma (thorax and the first abdominal segment, carries all six legs), gaster; joined by a narrow petiole (waist node). Elbowed antennae, mandibles. | Three blobs that touched only at points, no waist, the rear leg pair hung from the gaster edge, no mandibles, short antennae. | Wrong shape: fixed (petiole added, mesosoma lengthened, legs on the mesosoma, mandibles, longer elbowed antennae). |
| Caterpillar | Head capsule, 3 thoracic segments with 3 pairs of true (jointed) legs, 10 abdominal segments with prolegs on abdominal segments 3 to 6 and claspers on the last; 13 body segments in all. | Seven identical beads with gaps between them, a leg stub on every segment, no true legs. | Wrong shape: fixed (11 overlapping segments: 3 thoracic with thin legs, 8 abdominal, 4 proleg pairs, a clasper pair, head capsule). The real count of 13 is cut to 11 to hold the triangle budget. |

Budget: ant 368, caterpillar 804 triangles (animal class, 500 to 1,000). Moving parts (unchanged contract): `Leg_*`, `Antenna_*`, `Head`, `Seg1..`.

Other insects (read in the script, not rendered): ladybug, beetle, firefly, honeybee, moth, dragonfly, spider each have a body that overlaps its neighbours and legs on the thorax, so nothing else needed changing here.
