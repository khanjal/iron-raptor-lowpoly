"""Audit the four-legged animals: are all their parts there, do they join, and do they sit where they should?

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/audit_animals.py", run_name="__main__")
Optional global ONLY (a list of species keys, e.g. ["horse"]).

It builds every species in species.py (no export: it audits the parts the builder made, by name, before they are joined into one mesh) and checks:

 PARTS (a missing part is a bug)
   - every animal has a body, a head, four legs, a tail, eyes (and pupils or its own), ears, and a nose or nostrils
   - the species' own parts (REQUIRED below: the horse's mane, the goat's horns and beard, the cow's udder and teats...)

 JOINS (no leeway beyond 1.5 cm)
   - every part except the body touches the rest of the animal: one of its corners is inside another part's volume or within 1.5 cm of its surface
     (an udder that hangs 9 cm under the belly fails; a horn that starts inside the skull, an ear on the crown, a leg into the body pass)

 SPACING
   - the eyes sit one on each side of the head, above its middle where they are, in front of the ears, no wider than the head there (plus 30%), and each
     shows: at least 4 mm of the eyeball is outside the head's surface (a buried eye is invisible) and no more than three quarters of its radius
     (a bulging eye looks wrong: they are set in)
   - the ears are a pair, no wider apart than 2.9 times the head where they are (a goat's flare out)

 SIZE (against the real animal: REFERENCE below, from docs/art/animal-notes.md)
   - the back height, the head-and-body length and (for the wildlife) the tail length are within the real animal's range (with a little slack): a model
     that is 40% too tall or too long looks wrong beside a person or a cow

 PROPORTIONS (docs/assets/briefs/animals.md; animal_proportions.py has the ranges)
   - the cat, collie and husky (animal_proportions.ENFORCED) fail when a ratio (trunk length to height, body width and depth, chest height, head length and
     width, head carriage, leg width, paw length) is outside the brief's range; the farm animals' misses are only printed (WARN) until each is rebuilt

Prints one line per species and the problems. Fix the species (species.py, species_pets.py, species_wild.py) or the builder (quadruped_builder.py), run again, and look at the
animal too: the audit does not see a mane that is the wrong colour or a horn that curves the wrong way.
"""

import importlib
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import quadruped_rig
import quadruped_builder
import animal_proportions
import species_farm_dog
import species_pets
import species                       # first: it imports species_wild, which imports it back
import species_wild
for _m in (common, animal_proportions, quadruped_rig, species_farm_dog, species_pets, species_wild, species, quadruped_builder):
    importlib.reload(_m)

REQUIRED = {                        # the parts a species must have besides the common ones
    "cow": ["udder", "teats", "horns"],
    "horse": ["mane"],
    "goat": ["horns", "beard"],
    "skunk": ["blaze"],
    "fox": ["ear_tips"],
    "deer_buck": ["antlers"],
}
# Real-world sizes in metres (docs/art/animal-notes.md has the sources): (shoulder height, head-and-body length, tail length); None = not checked.
# The model's back height may be up to 20% above the shoulder range (the back is higher than the shoulder), its lengths 10-15% either way.
REFERENCE = {
    "raccoon": ((0.23, 0.30), (0.40, 0.70), (0.20, 0.40)),
    "opossum": ((0.15, 0.25), (0.36, 0.50), (0.25, 0.38)),
    "skunk": ((0.14, 0.24), (0.33, 0.46), (0.18, 0.38)),
    "fox": ((0.35, 0.50), (0.45, 0.90), (0.30, 0.55)),
    "deer_doe": ((0.80, 1.00), (1.30, 2.00), (0.10, 0.36)),
    "deer_buck": ((0.90, 1.05), (1.30, 2.00), (0.10, 0.36)),
    "deer_fawn": ((0.40, 0.65), (0.70, 1.10), (0.08, 0.22)),
    "bear": ((0.75, 1.05), (1.20, 2.00), (0.08, 0.14)),
    # the cat and the husky (docs/assets/briefs/animals.md): back height, head-and-body length, tail not checked
    "cat_tabby": ((0.23, 0.30), (0.40, 0.60), None),
    "dog_husky": ((0.51, 0.62), (0.80, 1.10), None),
    "cow": ((1.30, 1.55), (1.80, 2.60), None),
    "horse": ((1.40, 1.70), (2.00, 2.60), None),
    "sheep": ((0.60, 0.95), (0.90, 1.40), None),
    "pig": ((0.70, 1.00), (1.20, 1.80), None),
    "goat": ((0.65, 0.95), (0.90, 1.40), None),
    # the farm dog and its coats (#275): a collie / shepherd cross, 0.46-0.62 m at the shoulder (docs/art/animal-notes.md, "Farm dog")
    **{k: ((0.46, 0.62), (0.80, 1.05), (0.28, 0.42)) for k in ("dog_collie", "dog_collie_brown_white", "dog_collie_grey_merle", "dog_collie_yellow", "dog_collie_brindle")},
}
COMMON = ["body", "head", "tail", "eyes", "ears", "leg_front_l", "leg_front_r", "leg_hind_l", "leg_hind_r"]
ATTACH = 0.015                      # metres


def _bvh(parts, skip):
    verts, tris = [], []
    for name, (v, t) in parts.items():
        if skip is not None and name == skip:
            continue
        base = len(verts)
        verts += v
        tris += [tuple(base + i for i in tri) for tri in t]
    return BVHTree.FromPolygons(verts, tris)


def _inside(bvh, p):
    """Odd number of surface crossings along +X."""
    hits, origin = 0, p.copy()
    for _ in range(40):
        hit = bvh.ray_cast(origin, Vector((1, 0, 0)))
        if hit[0] is None:
            break
        hits += 1
        origin = hit[0] + Vector((1e-4, 0, 0))
    return hits % 2 == 1


def audit(key):
    sp = species.SPECIES[key]
    quadruped_builder.build(sp, "faceted")
    parts = dict(quadruped_builder.LAST_PARTS)
    problems = []

    # --- parts ---------------------------------------------------------------------------------------------------------
    need = COMMON + REQUIRED.get(key, [])
    for n in need:
        if n not in parts:
            problems.append(f"missing part: {n}")
    if "nose" not in parts and "nostrils" not in parts:
        problems.append("missing part: a nose or nostrils")

    # --- joins ---------------------------------------------------------------------------------------------------------
    for name, (verts, tris) in parts.items():
        if name == "body":
            continue
        bvh = _bvh(parts, name)
        best = min(bvh.find_nearest(v)[3] for v in verts)
        if best > ATTACH and not any(_inside(bvh, v) for v in verts):
            problems.append(f"{name} floats: its nearest point is {best * 100:.1f} cm from the rest of the animal")

    # --- spacing -------------------------------------------------------------------------------------------------------
    if "head" in parts and "eyes" in parts:
        hv = parts["head"][0]
        ev = parts["eyes"][0]
        ey = sum(v.y for v in ev) / len(ev)
        ez = sum(v.z for v in ev) / len(ev)
        near = [v for v in hv if abs(v.y - ey) < 0.04]                 # the head where the eyes are
        if not (any(v.x > 0 for v in ev) and any(v.x < 0 for v in ev)):
            problems.append("the eyes are not one on each side of the head")
        elif near:
            hw = max(abs(v.x) for v in near)
            if ez < (min(v.z for v in near) + max(v.z for v in near)) / 2:
                problems.append("the eyes are below the middle of the head")
            # each eye must show: some of its eyeball outside the head's surface (a buried eye is invisible), but not hanging off it
            bvh = _bvh({"head": parts["head"]}, None)
            for sign, label in ((1, "left"), (-1, "right")):
                side = [v for v in ev if v.x * sign > 0]
                radius = (max(v.z for v in side) - min(v.z for v in side)) / 2 if side else 0.0
                out = [bvh.find_nearest(v)[3] for v in side if not _inside(bvh, v)]
                shows = max(out, default=0.0)
                if shows < 0.004:
                    problems.append(f"the {label} eye is buried: at most {shows * 1000:.1f} mm of it is outside the head")
                elif shows > 0.75 * radius:                                  # set in: no more than three quarters of the eyeball's radius out of the head
                    problems.append(f"the {label} eye bulges: {shows * 100:.1f} cm of an eyeball of radius {radius * 100:.1f} cm is outside the head")
            if max(abs(v.x) for v in ev) > hw * 1.3:
                problems.append(f"the eyes are wider apart than the head (outer edge {max(abs(v.x) for v in ev):.3f}, the head here {hw:.3f})")
        if "ears" in parts:
            ay = sum(v.y for v in parts["ears"][0]) / len(parts["ears"][0])
            if ey > ay - 0.005:
                problems.append("the eyes are not in front of the ears")
    if "head" in parts and "ears" in parts:
        av = parts["ears"][0]
        ay = sum(v.y for v in av) / len(av)
        near = [v for v in parts["head"][0] if abs(v.y - ay) < 0.05]
        hw = max(abs(v.x) for v in near) if near else max(abs(v.x) for v in parts["head"][0])
        if max(abs(v.x) for v in av) > hw * 2.9:
            problems.append("the ears are far wider apart than the head (more than 2.9 times)")
        if not (any(v.x > 0 for v in av) and any(v.x < 0 for v in av)):
            problems.append("the ears are not a pair")
    # --- size against the real animal ------------------------------------------------------------------------------------
    ref = REFERENCE.get(key)
    if ref and "body" in parts and "head" in parts:
        k = sp.get("scale", 1.0)
        body = parts["body"][0]
        height = max(v.z for v in body) * k
        length = (max(v.y for v in body) - min(v.y for v in parts["head"][0])) * k
        (h0, h1), (l0, l1), tail = ref
        if not (h0 * 0.9 <= height <= h1 * 1.2):
            problems.append(f"the back is {height:.2f} m high: a {key} stands {h0:.2f}-{h1:.2f} m at the shoulder")
        if not (l0 * 0.9 <= length <= l1 * 1.1):
            problems.append(f"the head and body are {length:.2f} m long: a {key}'s are {l0:.2f}-{l1:.2f} m")
        if tail and "tail" in parts:
            tv = parts["tail"][0]
            tl = max((a - b).length for a in tv for b in tv) * k
            if not (tail[0] * 0.85 <= tl <= tail[1] * 1.15):
                problems.append(f"the tail is {tl:.2f} m long: a {key}'s is {tail[0]:.2f}-{tail[1]:.2f} m")
    # --- proportions against the brief ---------------------------------------------------------------------------------------
    row = animal_proportions.KEYS.get(key)
    if row:
        misses = animal_proportions.check(row, sp)
        if row in animal_proportions.ENFORCED:
            problems += [f"proportions: {m}" for m in misses]
        else:
            for m in misses:
                print(f"    WARN {key}: proportions: {m}")
    return problems, parts


def main():
    only = globals().get("ONLY")
    keys = [k for k in species.SPECIES if not only or k in only]
    bad = 0
    for key in keys:
        problems, parts = audit(key)
        print(f"{key:10s} {'FAIL' if problems else 'ok  '} {len(parts)} parts: {', '.join(sorted(parts))}")
        for p in problems:
            print("    PROBLEM:", p)
        bad += bool(problems)
    print(f"audit_animals: {len(keys)} species, {bad} with problems")
    return bad


if __name__ == "__main__":
    main()
