# Brief: the people (civilians, law, aliens)

Issue [#90](https://github.com/khanjal/iron-raptor-lowpoly/issues/90). Written with the `asset-brief` skill before the rebuild. United States reference (the people of a US farm and town); the style stays the faceted low-poly of `gp_builder.py` (no bevels) on the shared 65-bone rig, so ids, bone names and the clips (Idle, Walk, Run, Sit) do not change.

Numbers are rounded from the US adult anthropometric surveys (CDC NHANES 2015-18 stature, ANSUR II body dimensions) and standard drawing references (the head is about 1/7.5 of an adult's height; a hand is about as long as the face; the arm hangs to mid-thigh). Women and men are given as a range. Anything finer than that (calf and wrist widths, ear size) is an estimate from those tables and photographs, not a published standard.

## What was wrong (the thumbnails, issue #90)

| Seen | Cause in the numbers |
| --- | --- |
| a stick figure from the side | the torso was 0.19-0.22 m deep (a real chest is 0.21-0.27 m, hips and seat 0.21-0.25 m) and dead straight from hip to shoulder: no seat, no chest |
| a shallow neck base | the top torso ring was 0.16 m deep (a real neck root is about 0.18 m); its 0.22 m width is kept: it is the shelf the shoulders slope down to |
| no hands | the hand was a 0.13 m paddle past the wrist (real 0.18-0.20 m, 0.08-0.09 m across) with a box for a thumb |
| thin legs | the calf was 0.116 m wide (real 0.10-0.13 m, 0.065-0.075 of the height); now 0.126 m |
| blank face | eyes and a nose box only: no brow, no ear shape, no mouth, a chin that is one ring |

## Real measurements (standing adult, rounded)

| Measure | Women | Men | In the model (1.84 m at scale 1) |
| --- | --- | --- | --- |
| Stature | 1.60-1.65 m | 1.74-1.78 m | `scale` 0.87-0.97 (1.0 is 1.84 m; the cast's taller people, 1.05, are above the survey) |
| Head height (chin to crown) | 0.21-0.22 m | 0.22-0.24 m | 1/7.5 of the height; children and aliens differ (below) |
| Head width / depth | 0.14-0.15 / 0.18-0.19 m | 0.15-0.16 / 0.19-0.20 m | width 0.60-0.85 of the head's height |
| Shoulder width, bone to bone (biacromial; with the deltoids 0.38-0.42 / 0.44-0.48 m) | 0.34-0.37 m | 0.38-0.41 m | the torso's shoulder ring, 0.205-0.265 of the height; the arms add the deltoids |
| Hip and seat depth | 0.21-0.24 m | 0.21-0.25 m | the torso's lowest ring, 0.118-0.150 of the height |
| Chest depth | 0.21-0.24 m | 0.23-0.27 m | 0.125-0.155 of the height |
| Thigh width at the top | 0.17-0.19 m | 0.17-0.20 m | 0.088-0.118 of the height |
| Calf width | 0.10-0.12 m | 0.11-0.13 m | 0.065-0.080 of the height |
| Upper arm | 0.08-0.10 m | 0.09-0.11 m | at the elbow ring, 0.045-0.068 of the height |
| Wrist width | 0.050-0.058 m | 0.055-0.065 m | 0.030-0.042 of the height (the model's wrist is a little wide: 0.074 m, the width of a wrist with the hand's thickness) |
| Hand, wrist to fingertip / across the knuckles | 0.17-0.18 / 0.07-0.08 m | 0.18-0.20 / 0.08-0.09 m | 0.095-0.125 / 0.040-0.058 of the height |
| Foot length / breadth | 0.23-0.24 / 0.09 m | 0.26-0.27 / 0.10 m | breadth 0.34-0.45 of the length (the length 0.12-0.165 of the height: `audit_bodies.py`) |
| Hip height (crotch) | about 0.45-0.47 of the height | about 0.46-0.48 | the legs' range of `audit_bodies.py` |
| Arm hanging | fingertips at mid-thigh | | arm island 0.33-0.47 of the height |

## Variants

| Variant | Differences from the adult |
| --- | --- |
| Child (6-8 years; the Farmer's kid) | 1.15-1.30 m; head 1/6.0-1/6.5 of the height (0.15-0.21: `audit_bodies.CHILD`); hands 0.13-0.15 m; round belly, thin neck |
| Elderly (the Grandparent) | 3-5 % shorter than in their prime, rounder shoulders, thinner arms (build mf 0.85); the model keeps the rig's upright pose, the shape is in the build |
| Builds | very slim to heavy: `art/data/content/builds.json` (mass factor mf) and the ranges of `audit_bodies.HUMAN_BUILD`; the people's body changes through `gp_builder`'s region factors, not through new meshes |
| Aliens | humanoid on the same rig: the Nordic and the Reptilian keep the human ranges (widened 25 %); the Grey's head (2.05x) and the Shadow Entity's long limbs are allowed deviations with a reason in `audit_bodies.ALLOWED`; aliens keep their own fingers (`alien_parts.HANDS`) |

Skin and hair are paints (palette names `skin*`, `hair*`, issue #48), never separate models. Clothing keeps its named parts (shirt, pants, shoes, hat).

## Proportion table

The ranges `art/scripts/people_proportions.py` checks on `gp_builder.py`'s tables (`tests/test_people_proportions.py` compares this table with the script).

| Measure | Low | High |
| --- | --- | --- |
| shoulder | 0.205 | 0.265 |
| chest_d | 0.125 | 0.155 |
| seat | 0.118 | 0.150 |
| thigh | 0.088 | 0.118 |
| calf | 0.065 | 0.080 |
| upper_arm | 0.045 | 0.068 |
| wrist | 0.030 | 0.042 |
| hand | 0.095 | 0.125 |
| hand_w | 0.040 | 0.058 |
| foot_w | 0.34 | 0.45 |
| head_w | 0.60 | 0.85 |

## Three-view checklist (Blender MCP `look`, before and after)

- **Side**: a chest and a seat: the torso is deeper than before (chest 0.24 m, seat 0.23 m), the back and hips bulge; the head sits over the shoulders; the hand is as long as the face is tall; the foot has a heel and a toe box.
- **Front**: shoulders wider than the hips; shoulders that slope into the neck; thighs wider than the calves, calves wider than the ankles; hands as long as the face.
- **Top**: the head is an oval deeper than it is wide; the torso an oval; arms start at the chest's side.
- Brows, ears, nose and mouth are relief, not only colour.

## Missing family members (not in this PR)

A teenager, a toddler, a woman in trousers and a heavier older man are the gaps; each is a few arguments to `gp_builder.build` once the body is right. Hair and hat shapes are untouched.
