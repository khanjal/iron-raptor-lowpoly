"""The proportions of the four-legged animals, measured on a species dict (species.py's format) and checked against the ranges in docs/assets/briefs/animals.md.

No Blender needed: measure() reads the numbers a species is built from (body sections, head rings, leg profiles), so the unit test (tests/test_animal_proportions.py)
and audit_animals.py (which prints the result for every species it builds) use the same code. Every ratio is a share of the back height H (the top of the body
over the withers) or of the trunk length L (the body from the front of the chest to the rump), so a ratio holds at any scale.

    H        back height: the top of the highest body section
    L        trunk length: the body's y extent
    L/H      how long the animal is for its height
    width    the widest body section's full width, as a share of H            depth   the deepest section's full height, as a share of H
    elbow    the lowest point of the chest (centre z minus half height of the front sections) as a share of H: what is left for the legs
    head     the head's length (the nose to the skull ring, the one the ears sit on: sp["ear_y"]) as a share of L
    head_w   the head's full width at its widest ring from the skull forward, as a share of the head's length
    carry    the height of the top of the skull ring, as a share of H (the neck raises it above the back)
    leg_top  the full width of the front leg's top ring (the forearm with its muscle), as a share of H
    leg_low  the full width of the front leg at the ankle ring (the cannon bone and pastern: where a leg looks like a stick), as a share of H
    paw      the length of the front foot (its last ring's full depth), as a share of H
"""

# (low, high) per species key, from the brief (docs/assets/briefs/animals.md, "Proportion table"). A species with no entry is not checked.
RANGES = {
    "cat": dict(LH=(1.05, 1.65), width=(0.43, 0.66), depth=(0.46, 0.66), elbow=(0.36, 0.52), head=(0.28, 0.40), head_w=(0.64, 1.00),
                carry=(1.05, 1.35), leg_top=(0.13, 0.22), leg_low=(0.07, 0.12), paw=(0.15, 0.26)),
    "collie": dict(LH=(0.95, 1.35), width=(0.30, 0.50), depth=(0.44, 0.58), elbow=(0.44, 0.54), head=(0.31, 0.44), head_w=(0.45, 0.62),
                   carry=(1.05, 1.30), leg_top=(0.12, 0.18), leg_low=(0.07, 0.11), paw=(0.15, 0.24)),
    "husky": dict(LH=(0.95, 1.30), width=(0.32, 0.52), depth=(0.44, 0.58), elbow=(0.44, 0.54), head=(0.32, 0.42), head_w=(0.50, 0.68),
                  carry=(1.05, 1.30), leg_top=(0.12, 0.18), leg_low=(0.07, 0.11), paw=(0.15, 0.24)),
    # the farm animals (rebuilt in later PRs: audit_animals.py reports them but does not fail them yet)
    "cow": dict(LH=(1.10, 1.45), width=(0.34, 0.54), depth=(0.50, 0.66), elbow=(0.42, 0.52), head=(0.27, 0.36), head_w=(0.40, 0.55),
                carry=(0.95, 1.20), leg_top=(0.10, 0.16), leg_low=(0.05, 0.09), paw=(0.07, 0.12)),
    "horse": dict(LH=(1.00, 1.25), width=(0.26, 0.38), depth=(0.50, 0.64), elbow=(0.50, 0.60), head=(0.38, 0.50), head_w=(0.30, 0.45),
                  carry=(1.15, 1.45), leg_top=(0.07, 0.12), leg_low=(0.045, 0.07), paw=(0.05, 0.11)),
    "pig": dict(LH=(1.30, 1.70), width=(0.55, 0.78), depth=(0.60, 0.80), elbow=(0.28, 0.40), head=(0.28, 0.38), head_w=(0.55, 0.75),
                carry=(0.85, 1.05), leg_top=(0.12, 0.20), leg_low=(0.07, 0.12), paw=(0.08, 0.14)),
    "sheep": dict(LH=(1.00, 1.30), width=(0.40, 0.58), depth=(0.50, 0.68), elbow=(0.38, 0.48), head=(0.26, 0.36), head_w=(0.38, 0.55),
                  carry=(1.00, 1.25), leg_top=(0.09, 0.15), leg_low=(0.05, 0.09), paw=(0.07, 0.12)),
    "goat": dict(LH=(1.05, 1.35), width=(0.34, 0.50), depth=(0.50, 0.66), elbow=(0.44, 0.54), head=(0.26, 0.36), head_w=(0.38, 0.55),
                 carry=(1.00, 1.30), leg_top=(0.09, 0.15), leg_low=(0.05, 0.09), paw=(0.07, 0.12)),
}
# the species keys of species.SPECIES that each range row applies to
KEYS = {**{k: "cat" for k in ("cat_tabby", "cat_black", "cat_orange", "cat_tuxedo", "cat_calico", "cat_siamese", "cat_grey", "cat_kitten")}, "dog_collie": "collie", **{f"dog_collie_{c}": "collie" for c in ("brown_white", "grey_merle", "yellow", "brindle")}, "dog_husky": "husky", "cow": "cow", "horse": "horse", "pig": "pig", "sheep": "sheep", "goat": "goat"}
ENFORCED = {"cat", "collie", "husky"}          # the species already rebuilt to the brief: a miss fails the audit; the others are only reported


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
    head_len = skull[0] - nose
    foot = front["profile"][-1]
    fore = front["profile"][0]
    return dict(H=H * k, L=L * k, LH=L / H,
                width=2 * max(w for _, _, w, _ in body) / H, depth=2 * max(h for *_, h in body) / H,
                elbow=min(z - h for y, z, _, h in body if y <= mid) / H,
                head=head_len / L, head_w=2 * max(r[2] for r in head if r[0] <= skull[0]) / head_len, carry=(skull[1] + skull[3]) / H,
                leg_top=2 * fore[2] / H, leg_low=2 * front['profile'][front['joints'][1]][2] / H, paw=2 * foot[3] / H)


def check(row, sp):
    """The problems of a species against RANGES[row]: a list of strings, empty when it is within them."""
    m = measure(sp)
    return [f"{name} {m[name]:.2f} is outside {lo:.2f}-{hi:.2f}" for name, (lo, hi) in RANGES[row].items() if not lo <= m[name] <= hi]
