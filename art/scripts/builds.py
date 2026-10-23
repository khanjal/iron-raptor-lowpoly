"""Body builds of the people (issue #269): the data of art/data/content/builds.json and the maths that turns a mass factor into the factors gp_builder.py multiplies its ring tables by.

    import builds
    r = builds.region(1.2)             # {"torsoWidth": [6 factors], "torsoDepth": [...], "belly": [...], "thigh": 1.10, "calf": 1.05, "upperArm": ..., ...}
    mf = builds.role_mf("Farmer")      # 1.20: the base build of the role, as gp_cast exports it
    builds.region_mf("Kid")            # 1.0: a child's mf 0.70 is a neutral child (childRegionOffset 0.30 added)

A build is one number, the mass factor mf = BMI / 23.5 (0.8 very slim ... 1.0 average ... 1.6 very heavy). `region(mf)` interpolates the anchors of the file (0.8, 1.0, 1.2, 1.45,
1.6) linearly; below the first and above the last anchor it holds the end value (the limits of the file keep a person inside). No Blender: dev/builds_check.py imports this too.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PATH = REPO / "art" / "data" / "content" / "builds.json"
SCALARS = ("thigh", "calf", "upperArm", "forearm", "neck", "face", "foot", "hipSpread")      # one factor each
RINGS = ("torsoWidth", "torsoDepth", "belly")                                                 # six factors each (hips, waist, ribs, chest, shoulders, neck base)

_cache = {}


def load(path=None):
    p = Path(path) if path else PATH
    if str(p) not in _cache:
        _cache[str(p)] = json.loads(p.read_text(encoding="utf-8"))
    return _cache[str(p)]


def _blend(rows, anchors, mf):
    """Linear interpolation of rows (one per anchor, each a number or a list of numbers) at mf; held at the ends."""
    if mf <= anchors[0]:
        return rows[0]
    if mf >= anchors[-1]:
        return rows[-1]
    for i in range(len(anchors) - 1):
        a, b = anchors[i], anchors[i + 1]
        if a <= mf <= b:
            t = (mf - a) / (b - a)
            if isinstance(rows[i], list):
                return [x + (y - x) * t for x, y in zip(rows[i], rows[i + 1])]
            return rows[i] + (rows[i + 1] - rows[i]) * t
    return rows[-1]


def region(mf, data=None):
    """The factors for a build at mass factor mf (the REGION mf: for a child already offset, see region_mf)."""
    data = data or load()
    reg = data["regions"]
    out = {k: _blend(reg[k], reg["anchors"], mf) for k in RINGS}
    out.update({k: _blend(reg[k], reg["anchors"], mf) for k in SCALARS})
    return out


def role(name, data=None):
    return (data or load())["roles"][name]


def role_mf(name, data=None):
    """The role's base mass factor."""
    return role(name, data)["mf"]


def region_mf(name, mf=None, data=None):
    """The mf the region table is read at for the role `name`: its mf (or the one given), plus childRegionOffset for a child (a child's mf is BMI / 23.5 too, which is lower: the kid's 0.70 looks like a neutral child)."""
    data = data or load()
    r = role(name, data)
    base = r["mf"] if mf is None else mf
    return base + (data["childRegionOffset"] if r.get("child") else 0.0)


def role_for_cast(cast_key, data=None):
    """The role name of a gp_cast entry, or None for the aliens."""
    for name, r in (data or load())["roles"].items():
        if r.get("cast") == cast_key:
            return name
    return None


def mass_kg(mf, scale, data=None):
    """BMI x height^2 (the data's bmiPerMassFactor and rigHeight)."""
    data = data or load()
    height = data["rigHeight"] * scale
    return data["bmiPerMassFactor"] * mf * height * height
