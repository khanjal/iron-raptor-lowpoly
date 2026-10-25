"""A low-poly person on the Universal Animation Library skeleton, with swappable hair, hats and accessories.

    import gp_builder
    body, rig, coll = gp_builder.build("GP_Sheriff_01", outfit=dict(shirt="tan_uniform", pants="navy"),
                                       hair="short", hat="campaign", extras=["badge"], sleeve=0.80)

Everything is lofted cross-sections like the animals; one mesh, one rig, one shared material. The look comes from
palette colours (outfit), a hair style, an optional hat and extras, so a few arguments make a new person. The base
body is the one in the asset list's GP-01..GP-03 (adult, neutral build); a child is the same person scaled (scale).

outfit keys: skin, shirt, pants, shoes, hair, eyes (palette swatch names, see common.PALETTE)
hair:    short (default), buzz, long, none
hat:     None, cap, cowboy, campaign (sheriff), fedora, hardhat
extras:  badge, tie, sunglasses, beard, vest, skirt, tail, crest (the Reptilian: a tail on the pelvis, three plates on the head)
face:    human, or an alien race's (grey, shadow, reptilian, nordic): its own head shape and a face of caps that sit on the skull (alien_parts.py)
joints:  True for the aliens: a hip block over both hip joints and a ball over each shoulder joint, so a swinging leg or arm never opens a gap
hands:   None (a box thumb) or grey | shadow | reptilian: long fingers and a thumb (alien_parts.HANDS)
         (hair, hats, a beard and sunglasses are still made for the human head: an alien with its own skull must not get them; nor does style="smooth" fit the
         alien faces, whose caps are not subdivided)
sleeve:  how far the sleeve runs along the arm in metres from the body centre: 0.36 short sleeves, 0.8 long
suit:    True makes the jacket reach the hips (the torso takes the shirt colour all the way down)
mf:      the build (issue #269, art/data/content/builds.json, art/scripts/builds.py): the mass factor, BMI / 23.5, 0.8 very slim ... 1.0 average ... 1.6 very heavy. The torso's six rings, the arms,
         legs, neck, face and feet are each scaled by their own factor for that build (a belly, thicker thighs, a thicker neck), and `girth` is not used. None (the aliens): the old
         one-factor `girth`. A child passes the build's REGION mf (builds.region_mf: its mf plus 0.30).
"""

import importlib
import math

import bmesh
import bpy
from mathutils import Vector

import alien_parts
import builds
import common
import humanoid_rig
import quadruped_rig

for _m in (common, humanoid_rig, quadruped_rig, alien_parts, builds):
    importlib.reload(_m)

DEFAULT_OUTFIT = dict(skin="skin", shirt="cloth_red", pants="denim", shoes="rubber", hair="brown_coat", eyes="black")

TORSO = [  # z, centre y, half width (x), half depth (y)
    (0.90, 0.02, 0.170, 0.115), (1.05, 0.015, 0.160, 0.106), (1.20, 0.005, 0.150, 0.104),
    (1.32, -0.005, 0.185, 0.122), (1.43, -0.005, 0.215, 0.116), (1.50, 0.00, 0.110, 0.092),
]
HEAD = [(1.60, -0.010, 0.056, 0.066), (1.65, -0.004, 0.084, 0.092), (1.71, -0.004, 0.094, 0.105),
        (1.77, -0.003, 0.092, 0.104), (1.82, 0.000, 0.072, 0.085), (1.845, 0.004, 0.040, 0.050)]
ARM = [  # |x|, centre y, centre z, half y, half z
    (0.17, 0.060, 1.441, 0.080, 0.082), (0.25, 0.064, 1.441, 0.070, 0.072), (0.466, 0.070, 1.441, 0.052, 0.053),
    (0.60, 0.068, 1.441, 0.048, 0.048), (0.739, 0.065, 1.441, 0.037, 0.035), (0.80, 0.064, 1.440, 0.056, 0.022),
    (0.87, 0.064, 1.440, 0.048, 0.017),
]
HAND = [  # the people's hand instead of ARM's last two rows (issue #90): knuckles, fingers and a fingertip row, 0.21 m from the wrist to the tip (a real hand is about 0.11 of the height: 0.2 m) and 0.09 m across
    (0.785, 0.066, 1.441, 0.046, 0.025), (0.86, 0.064, 1.440, 0.045, 0.021), (0.92, 0.064, 1.440, 0.038, 0.016), (0.95, 0.064, 1.440, 0.022, 0.010),
]
LEG = [  # z, centre y, half x, half y
    (0.94, 0.000, 0.095, 0.100), (0.73, 0.000, 0.086, 0.093), (0.532, 0.003, 0.068, 0.072),
    (0.32, 0.025, 0.063, 0.070), (0.12, 0.036, 0.044, 0.048), (0.08, 0.038, 0.040, 0.043),
]
SHOE = [  # y, centre z, half x, half z. A foot is about 15% of the height (0.29 m on the 1.9 m figure); the skeleton's foot bones run on to y = -0.27.
    # The heel stays at y 0.085: it must cover the bottom of the trouser leg (its back edge is at y 0.075-0.086, wider people further back)
    (0.085, 0.042, 0.046, 0.044), (0.010, 0.044, 0.054, 0.048), (-0.090, 0.039, 0.056, 0.040),
    (-0.165, 0.033, 0.048, 0.033), (-0.205, 0.026, 0.034, 0.022),
]


def _disk(bm, z, cx, cy, rx, ry, thick, n=12):
    """A flat round plate (hat brims): two rings a little apart."""
    common.loft(bm, [common.ring_z(z, cx, cy, rx, ry, n=n, p=2.0), common.ring_z(z + thick, cx, cy, rx * 0.97, ry * 0.97, n=n, p=2.0)])


STYLES = {   # faceted is the house style (the flat look of the Quaternius packs); smooth rounds it with subdivision
    "faceted": dict(sub=0, smooth=False, torso_n=8, neck_n=6, head_n=8, limb_n=6, shoe_n=6, skirt_n=8),
    "smooth": dict(sub=1, smooth=True, torso_n=10, neck_n=8, head_n=10, limb_n=8, shoe_n=8, skirt_n=12),
}

BUILDS = {  # torso ring multipliers (hips, waist, ribs, chest, shoulders, neck base) so the silhouettes differ
    "neutral": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "masculine": [0.98, 1.0, 1.04, 1.08, 1.08, 1.0],
    "feminine": [1.14, 0.92, 0.90, 0.92, 0.86, 0.95],
}


def torso_rings(girth, mult, rg=None):
    """The torso's six rings (z, centre y, half width, half depth). rg: a build's factors (builds.region) or None for the one-factor `girth`. `mult` is the sex shape (BUILDS)."""
    rings = []
    for i, ((z, cy, hw, hd), m) in enumerate(zip(TORSO, mult)):
        if rg is None:
            rings.append((z, cy, hw * girth * m, hd * girth * (0.5 + 0.5 * m)))
        else:
            rings.append((z, cy + rg["belly"][i], hw * rg["torsoWidth"][i] * m, hd * rg["torsoDepth"][i] * (0.5 + 0.5 * m)))
    return rings


def ring_at(rings, z, field):
    """The torso's ring value at height z (field 1 centre y, 2 half width, 3 half depth), between the rings (held outside them)."""
    pts = [(r[0], r[field]) for r in rings]
    if z <= pts[0][0]:
        return pts[0][1]
    for (z0, v0), (z1, v1) in zip(pts, pts[1:]):
        if z0 <= z <= z1:
            return v0 + (v1 - v0) * (z - z0) / (z1 - z0)
    return pts[-1][1]


def front_y(rings, z):
    """The y of the front of the torso at height z (the faces look towards -Y), between the rings."""
    pts = [(r[0], r[1] - r[3]) for r in rings]
    if z <= pts[0][0]:
        return pts[0][1]
    for (z0, y0), (z1, y1) in zip(pts, pts[1:]):
        if z0 <= z <= z1:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    return pts[-1][1]


def build(name, outfit=None, hair="short", hat=None, extras=(), sleeve=0.36, suit=False, scale=1.0, export=None,
          girth=1.1, head_scale=1.12, shape="neutral", style="faceted", face="human", joints=False, hands=None, mf=None):
    """Build the person, return (mesh object, rig object, collection). export: an FBX path (relative to the repo, or absolute: the audit exports to a temporary folder), or None.

    scale    whole-body size (1.0 is 1.84 m; 0.72 is a child); head_scale enlarges the head alone (children get bigger ones)
    face     human | grey (a big egg of a head, a small chin, huge slanted black eyes) | shadow (a long head, two glowing slits) | reptilian (a snout with
             teeth, a heavy brow, gold slit eyes on the sides) | nordic (a human head, glowing eyes, brows, a small nose)
    style    faceted (flat, the default) or smooth (rounded by subdivision)
    girth    widens the torso, arms and legs without changing their lengths; shape is neutral | masculine | feminine
    mf       the build instead of girth (see the module's doc): a belly, a thicker neck, thighs and arms, a fuller face"""
    st = STYLES[style]
    rg = builds.region(mf) if mf is not None else None
    if rg is not None:
        girth = 1.0                                                                  # (alien_parts and the vest still take one; the people's body no longer does)
    f_face = rg["face"] if rg else 1.0
    f_neck = rg["neck"] if rg else 1.0
    f_foot = rg["foot"] if rg else girth
    hipx = rg["hipSpread"] if rg else 1.0
    # arm rows (x, ...): the upper arm to the elbow, the forearm to the wrist, the hand unchanged; leg rows: thigh, knee, calf, ankle
    arm_tab = ARM if hands else ARM[:5] + HAND                    # an alien keeps its fingers (alien_parts) on ARM's paddle; a person gets a hand
    arm_f = [rg["upperArm"], rg["upperArm"], 0.5 * (rg["upperArm"] + rg["forearm"]), rg["forearm"], rg["forearm"]] + [1.0] * (len(arm_tab) - 5) if rg else [girth] * len(arm_tab)
    leg_f = [rg["thigh"], rg["thigh"], 0.5 * (rg["thigh"] + rg["calf"]), rg["calf"], 0.5 * (rg["calf"] + 1.0), 1.0] if rg else [girth] * len(LEG)
    t_rings = torso_rings(girth, BUILDS[shape], rg)
    if rg is not None:                                           # the top ring of each leg (z 0.94) stays within a few mm of the torso's side at that height: a thick thigh and wide hips must not leave a ledge
        hw_top = ring_at(t_rings, LEG[0][0], 2)
        leg_f[0] = min(leg_f[0], (hw_top + 0.004 - 0.089 * hipx) / LEG[0][2])
    o = dict(DEFAULT_OUTFIT)
    o.update(outfit or {})
    common.setup_scene()
    coll = common.fresh_collection(name)
    rig = humanoid_rig.build(f"{name}_Rig", coll)
    parts = []

    pivot = Vector((0, 0, 1.58))                      # where the neck meets the head
    head_rings = alien_parts.HEADS.get(face, HEAD)    # an alien race has its own skull; the Nordic keeps the human one
    if f_face != 1.0:                                 # a fuller face (a heavier build): the cheeks and the jaw grow; the first ring (where the neck enters) stays
        head_rings = [head_rings[0]] + [(z, cy, hx * f_face, hy * f_face) for z, cy, hx, hy in head_rings[1:]]
    hair_rings = [(z, cy, hx * f_face, hy * f_face) for z, cy, hx, hy in HEAD]

    def make(part, build_fn, colour, bones, sub=None, smooth=True, head=False):
        bm = bmesh.new()
        build_fn(bm)
        if head and head_scale != 1.0:
            for v in bm.verts:
                v.co = pivot + (v.co - pivot) * head_scale
        obj = common.new_mesh_object(f"{name}_{part}", bm, coll, "paint_white")
        sub = st["sub"] if sub is None else min(sub, st["sub"])
        if sub:
            common.subsurf(obj, sub)
        common.smooth(obj, smooth and st["smooth"])
        common.paint_faces(obj, colour)
        quadruped_rig.weights(obj, rig, bones)
        parts.append(obj)

    shirt_split = 0.0 if suit else 0.98
    mult = BUILDS[shape]
    make("torso", lambda bm: common.loft(bm, [common.ring_z(z, 0, cy, hw, hd, n=st["torso_n"], p=2.6) for z, cy, hw, hd in t_rings]),
         lambda c, n: o["pants"] if c.z < shirt_split else o["shirt"],
         ["pelvis", "spine_01", "spine_02", "spine_03", "clavicle_l", "clavicle_r"])
    if joints and "skirt" not in extras:                         # the hip block: the legs hinge below the narrow torso's bottom ring, so cover both joints (a skirt already does)
        make("hips", lambda bm: common.loft(bm, [common.ring_z(z, 0, cy, hx, hy, n=st["torso_n"], p=2.6) for z, cy, hx, hy in alien_parts.pelvis_rings(girth, st["torso_n"])]),
             lambda c, n: o["pants"], ["pelvis"])
    # the head is scaled about the neck's top, so its underside moves up as the head grows: the neck must still reach 1.2 cm into it (the Grey, 2.05x, had a 1 mm gap)
    neck_top = max(1.62, pivot.z + 0.02 * head_scale + 0.012)
    make("neck", lambda bm: common.loft(bm, [common.ring_z(z, 0, 0.0, r * f_neck, r * f_neck, n=st["neck_n"]) for z, r in ((1.47, 0.058), (1.55, 0.050), (neck_top, 0.052))]),
         lambda c, n: o["skin"], ["neck_01", "spine_03", "Head"])
    make("head", lambda bm: common.loft(bm, [common.ring_z(z, 0, cy, hx, hy, n=st["head_n"], p=2.4) for z, cy, hx, hy in head_rings]),
         lambda c, n: o["skin"], ["Head", "neck_01"], head=True)

    if hair != "none":
        grow = 1.03 if hair == "buzz" else 1.07
        rings = [(1.735, -0.004, 0.094 * f_face, 0.105 * f_face)] + hair_rings[3:]
        if hair == "long":
            rings = [(1.60, 0.02, 0.092 * f_face, 0.100 * f_face), (1.66, 0.012, 0.096 * f_face, 0.108 * f_face), (1.72, 0.0, 0.098 * f_face, 0.108 * f_face)] + hair_rings[3:]
        if face != "human":                                                           # (the people stay as exported until #183: this is for the Nordic)
            rings = rings[:-1] + [(rings[-1][0] + 0.008,) + rings[-1][1:]]            # the top ring a little above the skull's: the two caps would lie in one plane and flicker
        make("hair", lambda bm: common.loft(bm, [common.ring_z(z, 0, cy + (0.016 if hair == "long" else 0.004), hx * grow, hy * grow, n=st["head_n"], p=2.4)
                                                  for z, cy, hx, hy in rings]),
             lambda c, n: o["hair"], ["Head"] + (["neck_01"] if hair == "long" else []), head=True)

    if face == "human":
        f_dy = -0.105 * (f_face - 1.0)                           # a fuller face's front stands this far further forward (the head ring's half depth 0.105 at the eyes)

        def face_build(bm):
            for sx in (-1, 1):
                common.add_box(bm, (sx * 0.036 * f_face, -0.108 + f_dy, 1.708), (0.020, 0.016, 0.016))
                common.add_box(bm, (sx * 0.097 * f_face, 0.005, 1.695), (0.016, 0.032, 0.062))                           # the ears
                common.add_box(bm, (sx * 0.038 * f_face, -0.094 + f_dy, 1.733), (0.040, 0.020, 0.009), rot_deg=(0, 0, sx * 6))    # the brows (set into the brow ridge, the outer end back)
            common.add_box(bm, (0, -0.121 + f_dy, 1.680), (0.026, 0.034, 0.046))                                         # the nose
            if "beard" not in extras:
                common.add_box(bm, (0, -0.106 + f_dy, 1.640), (0.050, 0.012, 0.008))                                     # the mouth

        def face_colour(c, n):
            u = Vector((c.x / head_scale, c.y / head_scale, pivot.z + (c.z - pivot.z) / head_scale))      # (the face is painted after the head's scale: look where it was built)
            if u.y < -0.09 and u.z > 1.7225 and abs(u.x) > 0.012:
                return o["hair"]
            return o["eyes"] if (abs(c.x) < 0.06 and c.y < -0.10 and c.z > 1.695 and abs(c.x) > 0.02) else o["skin"]
        make("face", face_build, face_colour, ["Head"], sub=0, head=True)
    else:                                                        # an alien face: caps that sit on this race's skull, one part per colour
        skull = alien_parts.Skull(head_rings, n=st["head_n"])
        for part, build_fn, colour in alien_parts.face_parts(face, skull, o):
            make(f"face_{part}", build_fn, lambda c, n, colour=colour: colour, ["Head"], sub=0, head=True)

    # A narrow torso (the Grey, the Shadow Entity) ends short of where the arm starts: start the arm inside it, at the torso's shoulder edge, so
    # the arm is joined to the body and not hanging a few centimetres off it
    shoulder = t_rings[4][2] * 0.8
    if rg is not None:                                           # a build always has the root row (inside the torso's shoulder edge), so every build of a person has the same vertices: shape keys can span them
        arm_rows = [(min(shoulder, arm_tab[0][0] - 0.02),) + arm_tab[0][1:]] + arm_tab
        arm_f_rows = [arm_f[0]] + arm_f
    else:
        arm_rows = arm_tab if shoulder >= arm_tab[0][0] else [(shoulder,) + arm_tab[0][1:]] + arm_tab
        arm_f_rows = arm_f if arm_rows is arm_tab else [arm_f[0]] + arm_f

    for side, tag in ((1, "l"), (-1, "r")):
        make(f"arm_{tag}",
             lambda bm, s=side: common.loft(bm, [common.ring_x(s * x, cy, cz, hy * af, hz * af, n=st["limb_n"])
                                                  for (x, cy, cz, hy, hz), af in zip(arm_rows, arm_f_rows)]),
             lambda c, n: o["shirt"] if abs(c.x) < sleeve else o["skin"],
             [f"clavicle_{tag}", f"upperarm_{tag}", f"lowerarm_{tag}", f"hand_{tag}"])
        if joints:                                               # a ball over the shoulder's pivot: the arm swings inside it (the shirt's colour, as the sleeve is)
            make(f"shoulder_{tag}", lambda bm, s=side: alien_parts.shoulder_ball(bm, s, girth),
                 lambda c, n: o["shirt"] if 0.192 < sleeve else o["skin"], [f"clavicle_{tag}", f"upperarm_{tag}"], sub=0)
        if hands:
            spec = alien_parts.HANDS[hands]
            make(f"fingers_{tag}", lambda bm, s=side: alien_parts.fingers(bm, s, girth, spec),
                 lambda c, n: "horn_cream" if (spec.get("claws") and abs(c.x) > 0.935) else o["skin"], [f"hand_{tag}"], sub=0)
        else:
            make(f"thumb_{tag}",
                 lambda bm, s=side: common.add_box(bm, (s * 0.805, 0.030, 1.416), (0.075, 0.026, 0.026), rot_deg=(0, 0, s * 22)),
                 lambda c, n: o["skin"], [f"hand_{tag}"], sub=0)
        make(f"leg_{tag}",
             lambda bm, s=side: common.loft(bm, [common.ring_z(z, s * 0.089 * hipx, cy, hx * lf, hy * lf, n=st["limb_n"]) for (z, cy, hx, hy), lf in zip(LEG, leg_f)]),
             lambda c, n: o["pants"], ["pelvis", f"thigh_{tag}", f"calf_{tag}", f"foot_{tag}"])
        make(f"shoe_{tag}",
             lambda bm, s=side: common.loft(bm, [common.ring_y(y, s * 0.089 * hipx, cz, hx * f_foot, hz, n=st["shoe_n"], p=2.6) for y, cz, hx, hz in SHOE]),
             lambda c, n: o["shoes"], [f"calf_{tag}", f"foot_{tag}", f"ball_{tag}"])

    # --- hats: lofted crowns and flat brims, all weighted to the head ---------------------------------------
    if hat:
        def hat_build(bm):
            top = 1.80
            if hat == "cap":
                common.loft(bm, [common.ring_z(z, 0, cy, hx * f_face, hy * f_face, n=st["head_n"]) for z, cy, hx, hy in
                                 [(1.75, -0.003, 0.100, 0.112), (1.80, -0.003, 0.098, 0.110), (1.85, 0.0, 0.07, 0.085), (1.875, 0.004, 0.035, 0.045)]])
                common.add_box(bm, (0, -0.145, 1.775), (0.15, 0.10, 0.012), rot_deg=(-8, 0, 0))          # the peak
            elif hat == "cowboy":
                common.loft(bm, [common.ring_z(z, 0, cy, hx * f_face, hy * f_face, n=st["head_n"]) for z, cy, hx, hy in
                                 [(1.76, -0.003, 0.102, 0.114), (1.86, 0.0, 0.092, 0.105), (1.92, 0.0, 0.080, 0.092), (1.935, 0.0, 0.06, 0.07)]])
                _disk(bm, 1.765, 0, -0.01, 0.23, 0.22, 0.012)
            elif hat == "campaign":                                                                        # the sheriff's flat-brimmed hat
                common.loft(bm, [common.ring_z(z, 0, cy, hx * f_face, hy * f_face, n=st["head_n"]) for z, cy, hx, hy in
                                 [(1.77, -0.003, 0.100, 0.112), (1.90, 0.0, 0.082, 0.094), (1.935, 0.0, 0.07, 0.082), (1.94, 0.0, 0.05, 0.06)]])
                _disk(bm, 1.768, 0, -0.01, 0.19, 0.18, 0.010)
            elif hat == "fedora":
                common.loft(bm, [common.ring_z(z, 0, cy, hx * f_face, hy * f_face, n=st["head_n"]) for z, cy, hx, hy in
                                 [(1.77, -0.003, 0.100, 0.112), (1.87, 0.0, 0.088, 0.100), (1.91, 0.0, 0.080, 0.090), (1.915, 0.0, 0.06, 0.07)]])
                _disk(bm, 1.768, 0, -0.005, 0.16, 0.155, 0.010)
            elif hat == "hardhat":
                common.loft(bm, [common.ring_z(z, 0, cy, hx * f_face, hy * f_face, n=st["head_n"]) for z, cy, hx, hy in
                                 [(1.76, -0.003, 0.104, 0.116), (1.84, 0.0, 0.098, 0.110), (1.90, 0.0, 0.07, 0.085), (1.915, 0.004, 0.035, 0.045)]])
                _disk(bm, 1.762, 0, -0.03, 0.12, 0.15, 0.010)
        hat_colour = {"cap": o["shirt"], "cowboy": "wood_dark", "campaign": "wood_dark",
                      "fedora": "black", "hardhat": "hi_vis"}[hat]
        make("hat", hat_build, lambda c, n: hat_colour, ["Head"], sub=0, head=True)

    # --- extras ------------------------------------------------------------------------------------------------
    if "sunglasses" in extras:
        make("sunglasses", lambda bm: common.add_box(bm, (0, -0.112 + f_dy, 1.708), (0.150 * f_face, 0.014, 0.034)), lambda c, n: "black", ["Head"], sub=0, head=True)
    def front(z):                                                # the y of this build's torso front at this height (negative: forward)
        return front_y(t_rings, z)
    if "tie" in extras:
        def tie_build(bm):                                       # the blade in three pieces (z 1.20-1.42), each at the torso's front at its own height: a belly bulges most at the bottom
            for zc in (1.237, 1.310, 1.383):
                common.add_box(bm, (0, front(zc) + 0.002, zc), (0.034, 0.014, 0.0733))
            common.add_box(bm, (0, front(1.44) - 0.001, 1.44), (0.05, 0.016, 0.04))

        def collar_build(bm):                                    # the same for the shirt's front (z 1.24-1.44)
            for zc in (1.273, 1.340, 1.407):
                common.add_box(bm, (0, front(zc) + 0.002, zc), (0.10, 0.012, 0.0667))
        make("tie", tie_build, lambda c, n: "black" if suit else "cloth_red", ["spine_03", "spine_02"], sub=0)
        make("collar_shirt", collar_build, lambda c, n: "paint_white", ["spine_03", "spine_02"], sub=0)
    if "badge" in extras:
        make("badge", lambda bm: common.add_box(bm, (0.075, front(1.30) - 0.004, 1.30), (0.045, 0.012, 0.05), rot_deg=(0, 0, 0)), lambda c, n: "gold",
             ["spine_03"], sub=0)
    if "beard" in extras:
        make("beard", lambda bm: common.loft(bm, [common.ring_z(z, 0, cy, hx * f_face, hy * f_face, n=st["neck_n"]) for z, cy, hx, hy in
                                                   [(1.60, -0.045, 0.072, 0.05), (1.65, -0.062, 0.082, 0.05), (1.70, -0.060, 0.074, 0.045)]]),
             lambda c, n: o["hair"], ["Head"], sub=0, head=True)
    if "skirt" in extras:                                                                                  # a house dress or skirt
        # the skirt hangs from the waist: its top ring takes the torso's build at its own height (z 1.02, mostly the hips'), the rest the hips'
        sk_w = [ring_at(t_rings, 1.02, 2) / ring_at(TORSO, 1.02, 2)] + [t_rings[0][2] / TORSO[0][2]] * 3 if rg else [girth] * 4
        sk_d = [ring_at(t_rings, 1.02, 3) / ring_at(TORSO, 1.02, 3)] + [t_rings[0][3] / TORSO[0][3]] * 3 if rg else [girth] * 4
        sk_y = [ring_at(t_rings, 1.02, 1) - ring_at(TORSO, 1.02, 1)] + [t_rings[0][1] - TORSO[0][1]] * 3 if rg else [0.0] * 4
        make("skirt", lambda bm: common.loft(bm, [common.ring_z(z, 0, ky, hw * kw, hd * kd, n=st["skirt_n"], p=2.2)
                                                   for (z, hw, hd), kw, kd, ky in zip(((1.02, 0.17, 0.128), (0.85, 0.20, 0.150), (0.66, 0.24, 0.16), (0.55, 0.255, 0.17)), sk_w, sk_d, sk_y)]),
             lambda c, n: o["shirt"], ["pelvis", "thigh_l", "thigh_r"])
    if "tail" in extras:                                                                                   # a thick tail that tapers to the ground, on the pelvis
        make("tail", lambda bm: common.loft(bm, [common.ring_y(y, 0.0, cz, hx, hz, n=st["limb_n"], p=2.4)
                                                  for y, cz, hx, hz in ((0.06, 0.93, 0.085, 0.075), (0.28, 0.84, 0.072, 0.066), (0.52, 0.66, 0.056, 0.052),
                                                                        (0.76, 0.42, 0.038, 0.036), (0.98, 0.20, 0.022, 0.020))]),
             lambda c, n: o["skin"], ["pelvis"])
    if "crest" in extras:                                                                                  # a row of fins from the brow back over the skull, raked back, their bases in the head
        make("crest", lambda bm: [common.add_box(bm, (0, y, z), (0.012, 0.045, h), rot_deg=(-28, 0, 0), taper=0.35)
                                  for y, z, h in ((0.015, 1.833, 0.056), (0.058, 1.816, 0.062), (0.090, 1.776, 0.052))],
             lambda c, n: o["shoes"], ["Head"], sub=0, head=True)
    if "vest" in extras:                                                                                   # hi-vis over the torso
        make("vest", lambda bm: common.loft(bm, [common.ring_z(z, 0, cy, hw * 1.05, hd * 1.08, n=st["torso_n"], p=2.6)
                                                  for z, cy, hw, hd in (t_rings[1:5] if rg else TORSO[1:5])]),
             lambda c, n: "hi_vis", ["pelvis", "spine_01", "spine_02", "spine_03"])

    body = common.join(parts, name)
    body.location = (0, 0, 0)
    quadruped_rig.bind(body, rig)
    if scale != 1.0:
        rig.scale = (scale, scale, scale)
    if export:
        common.export_fbx(coll, export, rigged=True)
    return body, rig, coll
