"""The proportions of the four-legged animals, measured on a species dict (species.py's format) and checked against the ranges in docs/assets/briefs/animals.md.

No Blender needed: measure() reads the numbers a species is built from (body sections, head rings, leg profiles), so the unit test (tests/test_animal_proportions.py)
and audit_animals.py (which prints the result for every species it builds) use the same code. Every ratio is a share of the back height H (the top of the body
over the withers) or of the trunk length L (the body from the front of the chest to the rump), so a ratio holds at any scale.

    H        back height: the top of the highest body section
    L        trunk length: the body's y extent
    L/H      how long the animal is for its height
    width    the widest body section's full width, as a share of H            depth   the deepest section's full height, as a share of H
    elbow    the lowest point of the chest (centre z minus half height of the front sections) as a share of H: what is left for the legs
    head     the head's length along its slope (the nose to the skull ring, the one the ears sit on: sp["ear_y"]) as a share of L
    head_w   the head's full width at its widest ring from the skull forward, as a share of the head's length
    carry    the height of the top of the skull ring, as a share of H (the neck raises it above the back)
    leg_top  the full width of the front leg's widest ring above the elbow (the upper arm with its muscle), as a share of H
    leg_low  the full width of the front leg at the ankle ring (the cannon bone and pastern: where a leg looks like a stick), as a share of H
    paw      the length of the front foot (its last ring's full depth), as a share of H
"""

import math

# (low, high) per species key, from the brief (docs/assets/briefs/animals.md, "Proportion table"). A species with no entry is not checked.
RANGES = {
    "cat": {"LH": (1.05, 1.65), "width": (0.43, 0.66), "depth": (0.46, 0.66), "elbow": (0.36, 0.52), "head": (0.28, 0.40), "head_w": (0.64, 1.00),
                "carry": (1.05, 1.35), "leg_top": (0.13, 0.22), "leg_low": (0.07, 0.12), "paw": (0.15, 0.26)},
    "collie": {"LH": (0.95, 1.35), "width": (0.30, 0.50), "depth": (0.44, 0.58), "elbow": (0.44, 0.54), "head": (0.31, 0.44), "head_w": (0.45, 0.62),
                   "carry": (1.05, 1.30), "leg_top": (0.12, 0.18), "leg_low": (0.07, 0.11), "paw": (0.15, 0.24)},
    "husky": {"LH": (0.95, 1.30), "width": (0.32, 0.52), "depth": (0.44, 0.58), "elbow": (0.44, 0.54), "head": (0.32, 0.42), "head_w": (0.50, 0.68),
                  "carry": (1.05, 1.30), "leg_top": (0.12, 0.18), "leg_low": (0.07, 0.11), "paw": (0.15, 0.24)},
    # the other dog breeds (issue #125)
    "retriever": {"LH": (1.00, 1.35), "width": (0.34, 0.54), "depth": (0.44, 0.58), "elbow": (0.44, 0.54), "head": (0.31, 0.42), "head_w": (0.52, 0.70),
                      "carry": (1.05, 1.30), "leg_top": (0.13, 0.19), "leg_low": (0.08, 0.12), "paw": (0.16, 0.25)},
    "shepherd": {"LH": (1.05, 1.35), "width": (0.32, 0.50), "depth": (0.44, 0.58), "elbow": (0.44, 0.54), "head": (0.32, 0.44), "head_w": (0.44, 0.60),
                     "carry": (1.05, 1.35), "leg_top": (0.12, 0.18), "leg_low": (0.07, 0.11), "paw": (0.15, 0.24)},
    "beagle": {"LH": (1.00, 1.35), "width": (0.36, 0.54), "depth": (0.46, 0.60), "elbow": (0.42, 0.52), "head": (0.32, 0.44), "head_w": (0.48, 0.66),
                   "carry": (1.05, 1.35), "leg_top": (0.13, 0.19), "leg_low": (0.08, 0.12), "paw": (0.16, 0.25)},
    "bulldog": {"LH": (1.05, 1.35), "width": (0.65, 0.95), "depth": (0.55, 0.75), "elbow": (0.28, 0.42), "head": (0.22, 0.34), "head_w": (1.15, 1.60),
                    "carry": (1.00, 1.30), "leg_top": (0.20, 0.30), "leg_low": (0.13, 0.20), "paw": (0.26, 0.40)},
    "dachshund": {"LH": (1.65, 2.20), "width": (0.45, 0.70), "depth": (0.58, 0.78), "elbow": (0.25, 0.38), "head": (0.32, 0.46), "head_w": (0.38, 0.56),
                      "carry": (1.20, 1.55), "leg_top": (0.18, 0.30), "leg_low": (0.11, 0.19), "paw": (0.24, 0.38)},
    # the farm animals
    "cow": {"LH": (1.10, 1.45), "width": (0.34, 0.54), "depth": (0.50, 0.66), "elbow": (0.42, 0.52), "head": (0.27, 0.36), "head_w": (0.40, 0.55),
                "carry": (0.95, 1.20), "leg_top": (0.10, 0.16), "leg_low": (0.05, 0.09), "paw": (0.07, 0.12)},
    "horse": {"LH": (1.00, 1.25), "width": (0.26, 0.38), "depth": (0.48, 0.64), "elbow": (0.47, 0.60), "head": (0.38, 0.50), "head_w": (0.30, 0.45),
                  "carry": (1.15, 1.45), "leg_top": (0.07, 0.12), "leg_low": (0.045, 0.07), "paw": (0.05, 0.11)},
    "pig": {"LH": (1.30, 1.70), "width": (0.55, 0.78), "depth": (0.60, 0.80), "elbow": (0.28, 0.40), "head": (0.28, 0.38), "head_w": (0.55, 0.75),
                "carry": (0.85, 1.05), "leg_top": (0.12, 0.20), "leg_low": (0.07, 0.12), "paw": (0.08, 0.14)},
    "sheep": {"LH": (1.00, 1.30), "width": (0.40, 0.58), "depth": (0.50, 0.68), "elbow": (0.38, 0.48), "head": (0.26, 0.36), "head_w": (0.38, 0.55),
                  "carry": (1.00, 1.25), "leg_top": (0.09, 0.15), "leg_low": (0.05, 0.09), "paw": (0.07, 0.12)},
    "goat": {"LH": (1.05, 1.35), "width": (0.34, 0.50), "depth": (0.50, 0.66), "elbow": (0.44, 0.54), "head": (0.26, 0.36), "head_w": (0.38, 0.55),
                 "carry": (1.00, 1.30), "leg_top": (0.09, 0.15), "leg_low": (0.05, 0.09), "paw": (0.07, 0.12)},
}
# the species keys of species.SPECIES that each range row applies to
KEYS = {**dict.fromkeys(("cat_tabby", "cat_black", "cat_orange", "cat_tuxedo", "cat_calico", "cat_siamese", "cat_grey", "cat_kitten"), "cat"), "dog_collie": "collie", **{f"dog_collie_{c}": "collie" for c in ("brown_white", "grey_merle", "yellow", "brindle")}, "dog_husky": "husky", "dog_retriever": "retriever", "dog_shepherd": "shepherd", "dog_beagle": "beagle", "dog_bulldog": "bulldog",
        "dog_dachshund": "dachshund", "dog_stray": "collie", "cow": "cow", "horse": "horse", "pig": "pig", "sheep": "sheep", "goat": "goat"}
ENFORCED = {"cat", "collie", "husky", "retriever", "shepherd", "beagle", "bulldog", "dachshund", "cow", "horse", "pig", "sheep", "goat"}          # every four-legged species is rebuilt to the brief: a miss fails the audit


def measure(sp):
    """The ratios of one species dict (see the module doc)."""
    body, head, front = sp["body"], sp["head"], sp["front"]
    k = sp.get("scale", 1.0)
    H = max(z + h for _, z, _, h in body)
    ys = [y for y, *_ in body]
    L = max(ys) - min(ys)
    mid = min(ys) + 0.5 * L
    skull = min(head, key=lambda r: abs(r[0] - sp["ear_y"]))
    nose = head[-1][0]
    head_len = math.hypot(skull[0] - nose, skull[1] - head[-1][1])      # along the head's slope (a horse's is tipped)
    foot = front["profile"][-1]
    fore = max(front["profile"][:front["joints"][0] + 1], key=lambda r: r[2])      # the widest ring above the elbow (the upper arm's muscle)
    return {"H": H * k, "L": L * k, "LH": L / H,
                "width": 2 * max(w for _, _, w, _ in body) / H, "depth": 2 * max(h for *_, h in body) / H,
                "elbow": min(z - h for y, z, _, h in body if y <= mid) / H,
                "head": head_len / L, "head_w": 2 * max(r[2] for r in head if r[0] <= skull[0]) / head_len, "carry": (skull[1] + skull[3]) / H,
                "leg_top": 2 * fore[2] / H, "leg_low": 2 * front['profile'][front['joints'][1]][2] / H, "paw": 2 * foot[3] / H}


def check(row, sp):
    """The problems of a species against RANGES[row]: a list of strings, empty when it is within them."""
    m = measure(sp)
    return [f"{name} {m[name]:.2f} is outside {lo:.2f}-{hi:.2f}" for name, (lo, hi) in RANGES[row].items() if not lo <= m[name] <= hi]


# ---- the shape (issue #125): what made the old animals read as a tube on four posts, measured on the same numbers. Shares of H:
#   tuck      how far the underline rises from the deepest point of the chest to the loin (a dog's or a cat's belly tucks up; a pig's or a sheep's does not)
#   front_in, hind_in   how far the top of each leg (its first ring) is inside the body above the body's underside there: a leg that starts at the shoulder or the hip,
#             not a post stuck on under the barrel
#   stifle    how far the stifle (the most forward ring of the hind leg between 30 % of H and the hip) is in front of the hip
#   hock      how far the hock (the rearmost ring below the stifle) is behind the stifle: together, the angle of a hind leg
#   root      how far the top of the neck's root stands above the withers (a dog's or a cat's neck leaves the chest forward; it must not rise out of the top of the back)
SHAPE_NAMES = ("tuck", "front_in", "hind_in", "stifle", "hock", "root")       # the measures; every limit is a minimum but the root's, a maximum
SHAPE_DEFAULT = dict(zip(SHAPE_NAMES, (0.0, 0.10, 0.10, 0.03, 0.06, 0.08)))
SHAPE = {**dict.fromkeys(("cat", "collie", "husky", "retriever", "shepherd", "beagle", "bulldog", "dachshund"), {**SHAPE_DEFAULT, "tuck": 0.08}),
         **dict.fromkeys(("horse", "cow", "fox", "deer"), {**SHAPE_DEFAULT, "tuck": 0.03})}


def _bottom_at(body, y):
    """The height of the body's underside at y (its sections' centre less half height, interpolated)."""
    for a, b in zip(body, body[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
            return (a[1] - a[3]) + ((b[1] - b[3]) - (a[1] - a[3])) * t
    end = body[0] if y < body[0][0] else body[-1]
    return end[1] - end[3]


def measure_shape(sp):
    """The shape measures of a species dict (see SHAPE), as shares of the back height H."""
    body, front, hind = sp["body"], sp["front"], sp["hind"]
    H = max(z + h for _, z, _, h in body)
    ys = [y for y, *_ in body]
    mid = min(ys) + 0.5 * (max(ys) - min(ys))
    chest = min(z - h for y, z, _, h in body if y <= mid)
    loin = max(z - h for y, z, _, h in body if mid < y < max(ys))
    inside = {kind: (leg["profile"][0][0] - _bottom_at(body, leg["y"] + leg["profile"][0][1])) / H for kind, leg in (("front", front), ("hind", hind))}
    p = hind["profile"]
    stifle = min((r for r in p[1:] if r[0] >= 0.30 * H), key=lambda r: r[1], default=p[0])
    hock = max((r for r in p if r[0] < stifle[0]), key=lambda r: r[1], default=p[-1])
    root = sp["head"][0]
    withers = max(z + h for y, z, _, h in body if y <= mid)
    values = ((loin - chest) / H, inside["front"], inside["hind"], (p[0][1] - stifle[1]) / H, (hock[1] - stifle[1]) / H, (root[1] + root[3] - withers) / H)
    return dict(zip(SHAPE_NAMES, values))


def check_shape(row, sp):
    """The shape problems of a species (a list of strings, empty when it passes SHAPE[row], or SHAPE_DEFAULT for a row with none of its own)."""
    lim, m = SHAPE.get(row, SHAPE_DEFAULT), measure_shape(sp)
    *minimums, root = SHAPE_NAMES
    out = [f"{name} {m[name]:.2f} is below {lim[name]:.2f}" for name in minimums if m[name] < lim[name]]
    if m[root] > lim[root]:
        out.append(f"root {m[root]:.2f} is above {lim[root]:.2f} (the neck rises out of the back)")
    return out


# ---- the hen: a biped (biped_bird.py's format: body rings (y, z, half width, half height), neck rings (z, y, rx, ry) from the shoulders to the beak, a leg, a tail) -------------
# LH body length / H, width and depth of the body / H, legs = the underside of the body / H (how much leg shows), carry = the top of the head / the back,
# shank = the width of the leg at the ankle / H, toe = the toes' length / H, tail = the top of the tail / the back
HEN = {"LH": (0.60, 0.90), "width": (0.34, 0.52), "depth": (0.45, 0.65), "legs": (0.22, 0.38), "carry": (1.15, 1.45), "shank": (0.04, 0.08), "toe": (0.14, 0.24), "tail": (0.95, 1.25)}


def measure_bird(sp):
    """The ratios of a bird species dict (see HEN), H being the top of the head."""
    body, neck, leg = sp["body"], sp["neck"], sp["leg"]
    H = max(z for z, *_ in neck)                       # the neck rings are horizontal (z, y, rx, ry): the last one is at the top of the head
    back = max(z + h for _, z, _, h in body)
    ys = [y for y, *_ in body]
    return {"H": H, "LH": (max(ys) - min(ys)) / H, "width": 2 * max(w for _, _, w, _ in body) / H, "depth": 2 * max(h for *_, h in body) / H,
                "legs": min(z - h for _, z, _, h in body) / H, "carry": H / back, "shank": 2 * leg["profile"][leg["joints"][1]][2] / H,
                "toe": leg["toe"] / H, "tail": max(z for z, _ in sp["tail"]) / back}


def check_bird(sp, ranges=HEN):
    m = measure_bird(sp)
    return [f"{name} {m[name]:.2f} is outside {lo:.2f}-{hi:.2f}" for name, (lo, hi) in ranges.items() if not lo <= m[name] <= hi]
