"""The proportions of the people (humans, and the aliens that share their body), measured on the tables gp_builder.py builds them from and checked against
docs/assets/briefs/people.md ("Proportion table").

No Blender needed: measure() reads the literal tables TORSO, HEAD, ARM, HAND, LEG and SHOE out of gp_builder.py's source, so the unit test
(tests/test_people_proportions.py) and audit_bodies.py (which prints the result before it audits the exported figures) use the same code. Every ratio is a share
of the figure's height H, the 1.84 m of the rig at scale 1 (hats and hair do not count), so it holds at any scale; a child differs through head_scale, not here.

    shoulder   the torso's widest ring, full width (bone to bone)           chest_d   the torso's deepest ring, full depth
    seat       the torso's lowest ring (the hips and buttocks), full depth
    thigh      the leg's top ring, full width                               calf      the leg's ring at the calf, full width
    upper_arm  the arm's ring at the elbow, full height (the deltoid rows are not measured)        wrist     the wrist's ring, full width
    hand       the hand's length from the wrist to the fingertip            hand_w    the hand's width at the knuckles
    foot_w     the shoe's widest ring / the shoe's length (not of H)        head_w    the skull's widest ring / its height (not of H)
"""

import ast
from pathlib import Path

HEIGHT = 1.84          # the rig's height (the skeleton's top of the head)
SOURCE = Path(__file__).resolve().parent / "gp_builder.py"

# (low, high) from the brief: the real spread (adult women to adult men, rounded) with a little slack for the faceted shapes
RANGES = {
    "shoulder": (0.205, 0.265), "chest_d": (0.125, 0.155), "seat": (0.118, 0.150), "thigh": (0.088, 0.118), "calf": (0.065, 0.080),
    "upper_arm": (0.045, 0.068), "wrist": (0.030, 0.042), "hand": (0.095, 0.125), "hand_w": (0.040, 0.058),
    "foot_w": (0.34, 0.45), "head_w": (0.60, 0.85),
}
# hand_w and wrist are measured on the width (y) of the ARM rings: the ring is flat in the hand's plane
NAMES = tuple(RANGES)


def tables():
    """The literal tables of gp_builder.py, by name."""
    wanted = {"TORSO", "HEAD", "ARM", "HAND", "LEG", "SHOE"}
    out = {}
    for node in ast.parse(SOURCE.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], "id", None) in wanted:
            out[node.targets[0].id] = ast.literal_eval(node.value)
    missing = wanted - set(out)
    if missing:
        raise ValueError(f"gp_builder.py has no literal table {sorted(missing)}")
    return out


def measure(t=None):
    """The ratios of the people's body (see the module doc) from the tables t (default: gp_builder.py's)."""
    t = t or tables()
    torso, head, arm, hand, leg, shoe = t["TORSO"], t["HEAD"], t["ARM"], t["HAND"], t["LEG"], t["SHOE"]
    wrist = arm[4]
    shoe_len = max(y for y, *_ in shoe) - min(y for y, *_ in shoe)
    head_h = head[-1][0] - head[0][0]
    return {
        "shoulder": 2 * max(r[2] for r in torso) / HEIGHT,
        "chest_d": 2 * max(r[3] for r in torso) / HEIGHT,
        "seat": 2 * torso[0][3] / HEIGHT,
        "thigh": 2 * leg[0][2] / HEIGHT,
        "calf": 2 * leg[3][2] / HEIGHT,
        "upper_arm": 2 * arm[2][4] / HEIGHT,
        "wrist": 2 * wrist[3] / HEIGHT,
        "hand": (max(r[0] for r in hand) - wrist[0]) / HEIGHT,
        "hand_w": 2 * max(r[3] for r in hand) / HEIGHT,
        "foot_w": 2 * max(r[2] for r in shoe) / shoe_len,
        "head_w": 2 * max(r[2] for r in head) / head_h,
    }


def check(m=None):
    """The problems (a list of strings) of the measures m against RANGES."""
    m = m or measure()
    return [f"{k} {m[k]:.3f} is outside {lo:.3f}-{hi:.3f}" for k, (lo, hi) in RANGES.items() if not lo <= m[k] <= hi]


if __name__ == "__main__":
    print(" ".join(f"{k} {v:.3f}" for k, v in measure().items()))
    print(check() or "ok")
