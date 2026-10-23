# Human body builds (issue #269, slices 1 and 2)

The people of the farm are one body at different heights, widened by a single `girth` factor. A **build** gives each person a silhouette of their own: a belly, thicker thighs and a thicker neck on a heavy one, narrow hips and thin arms on a slim one. This is what slices 1 and 2 of [`docs/design/content/body-builds-and-mass.md`](../design/content/body-builds-and-mass.md) built: the **data and presets** and the **builder**. The design (the mass in kilograms, the seed picking a build per mission, `BodyMass`, pushing, noise) is in that note and is **not built yet**; what is left is at the end.

## What a build is

One number, the **mass factor** `mf` = BMI / 23.5: 0.8 very slim, 1.0 average (the neutral body, the exported ring tables as they were before `girth`), 1.2 stocky, 1.45 heavy, 1.6 very heavy. Everything else derives from it. `art/data/content/builds.json` holds it:

| Key | What |
|---|---|
| `roles` | each person's role: the model (`GP_Farmer_01`), the `gp_cast` entry, the height `scale`, the **base `mf`** the file is exported at, and `vary` (the range around it a later slice's seed may draw from; `[0, 0]` for the identical FBI agents, the MIB and the sheriff) |
| `limits`, `childLimits` | the lightest and heaviest `mf` a person may have (0.8 to 1.6; a child 0.55 to 0.95) |
| `childRegionOffset` | a child's `mf` is BMI / 23.5 too, which is lower: the builder reads the child's regions at `mf + 0.30`, so the kid's 0.70 is a neutral child |
| `regions` | what each anchor `mf` (0.8, 1.0, 1.2, 1.45, 1.6) looks like: the factors the builder multiplies its ring tables by, interpolated linearly between the anchors |
| `shapeKeys`, `derived` | the design note's `Heavy`/`Slim` shape-key deltas and the gameplay rules (radius, nudge, run scale, seat sink, creaking floor). **Data only: nothing reads them yet** |

`art/scripts/builds.py` loads it (no Blender: `region(mf)`, `role_mf`, `region_mf`, `role_for_cast`, `mass_kg`); `python dev/builds_check.py` checks it (run by `dev/check.py` as "Builds data": the shape of the file, the limits, every role's model and `gp_cast` entry exist, `mf + vary` stays inside the limits, mf 1.0 is the neutral body).

## The builder

`gp_builder.build(..., mf=...)` takes the build instead of `girth`. Each region has its own factor (`regions` in the JSON):

| Region | Factor | What it scales in `gp_builder.py` |
|---|---|---|
| hips, waist, ribs, chest, shoulders, neck base | `torsoWidth`, `torsoDepth` (six numbers each) and `belly` (a forward shift of the ring's centre, metres) | the six `TORSO` rings: half-width, half-depth, centre y. The `shape` (neutral, masculine, feminine: the sex silhouette) still multiplies on top |
| thigh, calf | `thigh`, `calf` | the `LEG` rows (thigh at the hip, calf at the ankle, the knee halfway), and `hipSpread` moves the two legs apart (the hips are wider) |
| upper arm, forearm | `upperArm`, `forearm` | the `ARM` rows (the hand is not scaled) |
| neck | `neck` | the neck's radius |
| face | `face` | the cheeks and jaw rings of the head, the hair, the hat's crown and the beard follow |
| feet | `foot` | the shoes' width |

The outfit that was placed by absolute numbers follows the torso's front (the **sex shape** still multiplies on top of a build, so a feminine person's skirt, which hangs from the build's waist and hips, is 1.14 times as wide at the hips and 0.92 at the waist as a neutral one even at mf 1.0: before, only `girth` widened it): the **tie, collar and badge** move forward by how far the build's front stands in front of the neutral one at their height (`gp_builder.front_y`), the **vest** is built from the build's rings (it was built from the neutral ones, so on the worker it was hidden inside his shirt: it shows now), and the **skirt** hangs from the build's waist and hips. Fitting the clothes properly (a shirt cut for the build, an apron, a coat) is slice 3.

`gp_cast.py` gives every person the **region `mf` of their role** (`builds.region_mf`): the farmer 1.20, the spouse 0.95, the kid 0.70 (read at 1.0), the grandparent 0.85, the sheriff 1.15, the deputy 1.05, the FBI agents 1.0 and 0.92, the MIB 1.0, the worker 1.30, the waitress 1.0. The aliens keep `girth`. Re-run `gp_cast.py` for the people to re-export.

**Topology.** Every build of a person has the same vertices (a build always has the arm's root row: before, a narrow torso added one), so the shape keys of the design's option B can span them: checked for all 11 people at 0.8, 1.0, 1.2 and 1.6.

### Shape keys: verified, not built in

The design recommends one FBX per person with `Heavy` and `Slim` shape keys (so the seed can change a build without swapping models). Verified in this slice, with a throwaway test and no code left behind: the farmer built at 1.2, 1.6 and 0.95, the two extremes added as shape keys, exported through `common.export_fbx(..., rigged=True)`, re-imported in Blender (the keys `Basis`, `Heavy` 8.4 cm at the most, `Slim` 3.6 cm), and imported by Unity 6000.4 (a throwaway copy in `Assets/`, removed again): **two blend shapes, `Heavy` and `Slim`, 65 bones, 1,652 vertices, a valid Humanoid avatar**. The default import settings keep them. **Not built into the files**: nothing uses the keys until slice 4, and a blend shape has a skinning cost on every person for no gain until then.

## The audit

`art/scripts/audit_bodies.py` (skill `body-audit`) now also checks every person's build:

* **Joins at every build.** The cast is audited as exported (each at its role's build) and **again at the lightest and heaviest build the data allows** (0.8 and 1.6; a child 0.55 and 0.95): each is built, exported to a temporary folder, imported and given every join check (neck into skull and torso, arms into the torso, legs into the pelvis, shoes over the legs, nothing floating) and the proportions. `EVERY_ANCHOR = True` adds the other anchors. A gap at the shoulder or the hip is a failure.
* **The measures of a build** (ratios of the height, like the proportions): the torso's width at its six rings, its depth and how far its front stands out at the waist and ribs (the belly), the thickest thigh, upper arm and neck. `HUMAN_BUILD` gives the range of each at each anchor `mf` (interpolated), **written from measurements of the whole cast at the five anchors** with 7% slack; a child's get 8% more. A model that stopped looking like its build fails.
* **Arm clearance.** The imported rig is posed with the game's own clips' poses (`gp_clips`: the Idle, two frames of the Walk and a frame of the Run) and the posed arm is checked against the torso: the forearm and hand (lower than 0.62 of the height) and the upper arm (0.62 to 0.70) may be at most **4 cm deeper inside the torso than the neutral body of the same person**. The reference is the neutral body because the neutral body already has 3 to 5.5 cm of arm inside the torso somewhere in the clips (the Run's bent arm sweeps across the hip and belly; the upper arm hangs against the chest): the shared skeleton and clips cannot move an arm out of a body, so the audit measures what a build makes worse. The heaviest builds (1.6) measure 2.0 to 3.0 cm over their neutral body.

The design's "keep the chest and rib half-widths near 0.19 m" is why the anchors put a heavy build's extra volume in **depth** (the belly, the seat) and in the hips and thighs, and keep the chest and shoulders almost as wide as the neutral body's (`torsoWidth` at the chest 1.04 to 1.07). It is approximate: the neutral chest is already 0.185 m and a masculine shape multiplies it by 1.08, so the heaviest masculine chest is about 0.21 m; the arm test, not that number, is the limit.

## Adding or changing a build

* A new person: a `gp_cast.CAST` entry plus a `roles` entry in `builds.json` (`python dev/builds_check.py` says what is missing).
* A different look at an anchor: edit `regions` in `builds.json`, build the cast at the five anchors and look (`audit_bodies.py` with `EVERY_ANCHOR = True`), then rewrite `HUMAN_BUILD` from the measurements.
* The skeleton and the clips are never changed to fix a mesh (the `body-audit` rule).

## Not done (the rest of the design)

Slice 3 outfits that fit each build (the clothes are still the neutral shirt and trousers, widened with the body); the mass in kilograms on each person and race (`BodyMass`, `AlienRaceDefinition.mass`), the seed picking a build per role (`MissionBuilds`, `PersonBuild`), the capsule and NavMesh radius per build and the door test, pushing, run speed, seat sink and creaking floors; the household generator; an elderly stoop (a different rest pose or clip).
