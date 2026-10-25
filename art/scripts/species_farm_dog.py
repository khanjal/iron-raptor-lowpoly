"""The farm dog (issue #275): a medium collie / shepherd cross that reads as a dog at a glance, in five coats.

    make_farm_dog("DogCollie", "black_tan")  ->  a species dict for quadruped_builder.py (see species.py for the format)
    SKINS                                    ->  the five coats: black_tan, brown_white, grey_merle, yellow, brindle

The farm's first dog looked like a sheep with a dark face (the owner's play-test): a tube of a body as deep as a barrel, the head a plain continuation of the neck,
ears flat on top of it, a stub of a tail, and a black back over a white belly. This one is built from the real animal (docs/art/animal-notes.md, "Farm dog"):

    * a **deep chest and a tucked waist** (the body is 0.27 m deep at the chest and 0.20 m at the loin, not 0.34 m the whole way), so the belly rises and the legs show
    * a **narrow wedge of a head**: a skull 12 cm wide, a stop, and a muzzle as long as the skull with a nose and a lip line, the lower jaw in a lighter colour
    * **half-folded ears** (an upright base, the tips folded forward), set on the crown at the sides of the skull
    * a **ruff** of fur round the neck, a **medium coat** (no wool: the colour only changes at the markings) and a **tail** carried low with a hook in its tip
    * a **haunch** and a **shoulder** over the top of each leg (the legs' tops are the old collie's, set lower than the new, slimmer body's sides, so a lofted blob joins each to the body)
    * **dark eyes with a highlight**, set in the front of the skull, looking forward

The legs' profiles (the knee and ankle joints and the foot) are the old collie's (the same numbers as `species_pets.make_dog` with `leg=0.22`), so the leg bones keep their lengths and
with them the gait clips' strides and the speeds in `Anims/gait-speeds.json` (regenerated: they moved by under 1%); the legs stand 1-2 cm further out and back and the body above
them is new, so the other bones' positions moved a little (the bone names and the hierarchy are the shared quadruped rig's, unchanged). Every coat is the same mesh (the same vertices, the
same bones) with the faces painted differently, so the game can swap one for another on a dog that is already in the scene (`DogSkin`).
"""

import math


def _blobs(c, blobs):
    return sum(math.exp(-((c.x - x) ** 2 + (c.y - y) ** 2 + (c.z - z) ** 2) / (2 * s * s)) for x, y, z, s in blobs)


W = "paint_white"

# The coats. Every key is a palette swatch (common.PALETTE) or None (= the coat's body colour):
#   body     the back, sides and the top of the head          under    belly and the underside of the chest      legs   the legs above the socks
#   sock     the feet                                         ruff     the collar of fur round the neck          chest  the front of the chest (a bib)
#   muzzle   the sides and top of the muzzle                  jaw      the lower jaw                             ears   the ears                   tip   the tail's tip
#   tail_under  the underside of the tail                     blaze    a stripe up the forehead and muzzle       brows  two spots over the eyes (a part of its own, None = none)
# pattern: "plain", "stripes" (brindle) or "merle" (dark blotches)
SKINS = {
    "black_tan":   dict(body="black", under="tan", legs="tan", sock="tan", ruff="black", chest="tan", muzzle="tan", jaw="tan", ears="black", tip=None, tail_under="tan",
                        blaze=None, brows="tan", pattern="plain", label="a black and tan shepherd cross"),
    "brown_white": dict(body="brown_coat", under=W, legs=W, sock=W, ruff=W, chest=W, muzzle="brown_coat", jaw=W, ears="brown_coat", tip=W, tail_under="brown_coat",
                        blaze=W, brows=None, pattern="plain", label="a brown and white collie"),
    "grey_merle":  dict(body="grey_cat", under=W, legs="grey_cat", sock=W, ruff=W, chest=W, muzzle="grey_cat", jaw=W, ears="black", tip=W, tail_under="grey_cat",
                        blaze=W, brows="tan", pattern="merle", label="a blue merle collie"),
    "yellow":      dict(body="golden", under="cream", legs="golden", sock="cream", ruff="golden", chest="cream", muzzle="golden", jaw="cream", ears="tan", tip=None,
                        tail_under="cream", blaze=None, brows=None, pattern="plain", label="a plain yellow farm dog"),
    "brindle":     dict(body="tan", under="cream", legs="tan", sock=W, ruff="tan", chest=W, muzzle="dark_brown", jaw="dark_brown", ears="dark_brown", tip=None,
                        tail_under="tan", blaze=None, brows=None, pattern="stripes", label="a brindle cattle dog"),
}
DEFAULT_SKIN = "black_tan"


def make_farm_dog(name, skin=DEFAULT_SKIN, shape=None):
    """shape: optional overrides for another dog on the same builder (the husky): body, head, tail (the section lists below), front_x and hind_x (the legs' distance from the
    middle), ears ("fold": the collie's half-folded ear, "up": an upright triangle) and ruff (the collar's width factor)."""
    sk = SKINS[skin] if isinstance(skin, str) else skin
    shape = shape or {}
    # ---- the body: y runs front (negative) to back, z is the height of the section's centre, then its half width and half height (metres; shoulder height 0.53)
    body = [(-0.30, 0.375, 0.078, 0.098),       # the front of the chest
            (-0.22, 0.392, 0.112, 0.138),       # the deep chest: 0.27 m from the withers to the breastbone
            (-0.10, 0.394, 0.112, 0.138),
            (0.03, 0.404, 0.092, 0.100),        # the tucked waist: the belly rises to 0.30 m
            (0.17, 0.396, 0.097, 0.112),        # the hips
            (0.30, 0.382, 0.082, 0.100),
            (0.35, 0.372, 0.055, 0.075)]
    # ---- the head: neck, skull, stop, long muzzle; y, centre height, half width, half height
    head = [(-0.24, 0.500, 0.074, 0.105),       # the base of the neck
            (-0.31, 0.545, 0.066, 0.092),
            (-0.36, 0.580, 0.062, 0.082),       # the back of the skull
            (-0.41, 0.588, 0.063, 0.074),       # the widest: the cheeks (the head from the cheeks to the nose is 35 % of the trunk; docs/assets/briefs/animals.md)
            (-0.47, 0.572, 0.055, 0.062),       # the stop
            (-0.52, 0.552, 0.046, 0.054),       # the muzzle starts narrow
            (-0.58, 0.541, 0.042, 0.050),
            (-0.635, 0.533, 0.038, 0.045)]      # the nose
    # ---- the legs' profiles: the old collie's (make_dog leg=0.22)
    kz = (0.22 + 0.06) / 0.36
    fr = [(z * kz, dy, hx, hy) for z, dy, hx, hy in
          [(0.36, 0.00, 0.04, 0.05), (0.22, 0.00, 0.03, 0.035), (0.12, 0.00, 0.026, 0.03), (0.05, -0.004, 0.027, 0.034), (0.0, -0.024, 0.034, 0.056)]]   # a paw that is longer than it is wide
    hn = [(z * kz, dy, hx, hy) for z, dy, hx, hy in
          [(0.38, 0.00, 0.055, 0.07), (0.26, 0.03, 0.035, 0.045), (0.17, 0.06, 0.026, 0.03), (0.09, 0.03, 0.024, 0.028),
           (0.04, 0.01, 0.025, 0.03), (0.0, 0.0, 0.03, 0.045)]]
    # ---- the tail: hangs from the rump, bushy in the middle, a hook forward at the tip (height, y, radius)
    tail = [(0.395, 0.335, 0.026), (0.325, 0.415, 0.036), (0.235, 0.475, 0.042), (0.150, 0.470, 0.027)]
    body, head, tail = shape.get("body", body), shape.get("head", head), shape.get("tail", tail)
    front_leg = dict(x=shape.get("front_x", 0.068), y=-0.17, joints=(1, 3), profile=fr)
    hind_leg = dict(x=shape.get("hind_x", 0.078), y=0.22, joints=(2, 4), profile=hn)
    skull = head[3]
    ear_x = skull[2] * 0.85
    bodyz0, bodyz1 = 0.26, 0.53

    def blotches(c):
        return _blobs(c, [(0.06, -0.12, 0.42, 0.05), (-0.07, 0.0, 0.43, 0.06), (0.07, 0.10, 0.40, 0.05), (-0.06, 0.24, 0.40, 0.05),
                          (0.0, -0.02, 0.46, 0.04), (-0.04, 0.32, 0.38, 0.04), (0.08, -0.20, 0.40, 0.04)]) > 0.45

    def stripes(c):
        return math.sin((c.y * 62.0 + c.z * 40.0 + abs(c.x) * 25.0)) > 0.35

    def coat(c, n):
        if c.z < 0.075:
            return sk["sock"]
        if c.z < bodyz0 - 0.01:                                       # a leg
            return sk["legs"]
        low = c.z - (0.40 if c.y < -0.05 else 0.39)                   # how far below the centre line the face is
        if c.y < -0.16 and abs(c.x) < 0.075 and ((low < -0.04 and n.y < -0.2) or (c.y < -0.28 and n.y < -0.9)):
            return sk["chest"]                                       # the front of the chest: its underside and the breast (the body's front cap)
        if n.z < -0.45 or low < -0.085:
            return sk["under"]
        if sk["pattern"] == "stripes" and stripes(c):
            return "dark_brown"
        if sk["pattern"] == "merle" and blotches(c):
            return "black"
        return sk["body"]

    def head_coat(c, n):
        if c.y > -0.30:                                               # the neck
            return coat(c, n)
        if c.y < head[-1][0] + 0.03 and n.y < -0.4:
            return "black"                                            # the nose
        if sk["blaze"] and abs(c.x) < 0.03 and n.z > 0.7 and c.y < -0.40:
            return sk["blaze"]                                        # a blaze up the forehead and the muzzle (the two faces on the crown: the head's top vertex is on its middle line, so their centres are off it)
        if c.y < head[4][0] and (n.z < -0.30 or c.z < head[5][1] - 0.012):
            return sk["jaw"]                                          # the lower jaw: a lighter line along the underside of the muzzle
        if c.y < head[4][0] - 0.01:
            return sk["muzzle"]
        if sk["pattern"] == "merle" and blotches(c):
            return "black"
        if sk["pattern"] == "stripes" and c.y > -0.44 and stripes(c):
            return "dark_brown"
        return sk["body"]

    def tail_coat(c, n):
        if sk["tip"] and c.z < 0.21:
            return sk["tip"]
        if n.z < -0.25 or n.y < -0.4:
            return sk["tail_under"]
        if sk["pattern"] == "stripes" and stripes(c):
            return "dark_brown"
        return sk["body"]

    def extras(ctx):
        import quadruped_builder as qb
        cm = ctx.common
        ey, ez = skull[0], skull[1]

        # ears: lofted up from inside the sides of the crown, upright for most of their height and then tipped forward (a collie's half-folded ear)
        def ears(bm):
            zb = ez + skull[3] - 0.034
            for s in (-1, 1):
                if shape.get("ears") == "up":                         # an upright triangle, set close together
                    cm.loft(bm, [cm.ring_z(zb, s * ear_x * 0.80, ey + 0.012, 0.036, 0.018, n=4),
                                 cm.ring_z(zb + 0.055, s * ear_x * 0.86, ey + 0.004, 0.027, 0.013, n=4),
                                 cm.ring_z(zb + 0.115, s * ear_x * 0.92, ey - 0.004, 0.009, 0.006, n=4)])
                    continue
                cm.loft(bm, [cm.ring_z(zb, s * ear_x * 0.78, ey + 0.010, 0.028, 0.015, n=4),
                             cm.ring_z(zb + 0.062, s * ear_x * 0.88, ey + 0.006, 0.025, 0.013, n=4),
                             cm.ring_z(zb + 0.105, s * ear_x * 1.00, ey - 0.020, 0.012, 0.008, n=4)])
        ctx.make("ears", ears, lambda c, n: sk["ears"], ["Ear_L", "Ear_R"], sub=0, smooth=False)

        # a haunch over the top of each hind leg and a shoulder over each front leg: the legs' top rings are the old collie's, and the body above them is slimmer, so a blob
        # lofted from inside the body down to the leg's own top ring fills the join (skinned to the body bone and the leg's upper bone: the clips slide the upper bones along the body, and the top of the blob must stay with the body while its bottom follows the leg)
        for kind, leg_, top, wide, inset in (("hind", hind_leg, 0.385, 0.038, 0.026), ("front", front_leg, 0.375, 0.05, 0.008)):
            for s in (-1, 1):
                side = "R" if s < 0 else "L"
                ring0 = leg_["profile"][0]
                rings = [cm.ring_z(top, s * (leg_["x"] - inset), leg_["y"] - 0.005, wide, ring0[3] + 0.015, n=6),
                         cm.ring_z(ring0[0], s * leg_["x"], leg_["y"] + ring0[1], ring0[2], ring0[3], n=6)]
                blob = ctx.make(f"{'haunch' if kind == 'hind' else 'shoulder'}_{side.lower()}", lambda bm, r=rings: cm.loft(bm, r), lambda c, n: sk["body"],
                                ["Hips" if kind == "hind" else "Chest", f"{kind.capitalize()}Upper_{side}"], sub=0, smooth=False)
                # the weights by height, not by distance: the top of the blob (inside the body) is the body bone's alone and the bottom (the leg's own top ring) the leg's alone, with a
                # smooth blend between, so a clip that slides the leg's upper bone along the body (the dogs' walk, trot and run) drags the bottom of the blob and not its top
                body_bone, leg_bone = blob.vertex_groups[0].name, blob.vertex_groups[1].name
                z0 = ring0[0]
                for v in blob.data.vertices:
                    t = min(max((v.co.z - z0) / (top - z0), 0.0), 1.0)
                    t = t * t * (3.0 - 2.0 * t)
                    blob.vertex_groups[body_bone].add([v.index], t, "REPLACE")
                    blob.vertex_groups[leg_bone].add([v.index], 1.0 - t, "REPLACE")

        # the nose: a black pad at the tip
        tip = head[-1]
        ctx.make("nose", lambda bm: cm.add_box(bm, (0, tip[0] - 0.004, tip[1] + 0.004), (0.050, 0.032, 0.036), taper=0.9),
                 lambda c, n: "black", ["Head"], sub=0, smooth=False)

        # the ruff: a collar of fur round the base of the neck, a little proud of it
        rw = shape.get("ruff", 1.0)
        rings = [cm.ring_y(-0.215, 0, 0.500, 0.088 * rw, 0.118 * rw, n=8), cm.ring_y(-0.275, 0, 0.525, 0.078 * rw, 0.104 * rw, n=8), cm.ring_y(-0.335, 0, 0.560, 0.072 * rw, 0.095 * rw, n=8)]
        ctx.make("ruff", lambda bm: cm.loft(bm, rings), lambda c, n: sk["ruff"], ["Chest", "Neck1", "Neck2"], sub=0, smooth=False)

        # the eyes: dark, set into the front of the skull and looking forward, each with a small highlight
        y = head[4][0] + 0.018
        z, w, h = qb._head_at(head, y)
        r = 0.0145
        cz = z + 0.30 * h
        cx = qb._surface_x(ctx, y, cz, 0.8 * w) - 0.50 * r
        dx, dy = 0.55, 0.83                                           # the way they look: forward and a little out
        ctx.make("eyes", lambda bm: [qb._ball(bm, (s * cx, y, cz), r, n=6) for s in (-1, 1)], lambda c, n: "dark_brown", ["Head"], sub=0, smooth=False)
        ctx.make("pupils", lambda bm: [qb._ball(bm, (s * (cx + dx * 0.55 * r), y - dy * 0.55 * r, cz), 0.62 * r, n=6) for s in (-1, 1)],
                 lambda c, n: "black", ["Head"], sub=0, smooth=False)
        ctx.make("glints", lambda bm: [qb._ball(bm, (s * (cx + dx * 0.95 * r), y - dy * 0.55 * r - 0.003, cz + 0.45 * r), 0.22 * r, n=4) for s in (-1, 1)],
                 lambda c, n: W, ["Head"], sub=0, smooth=False)

        # the lip line: a thin dark line along each side of the muzzle, from the nose back to under the eye
        def lips(bm):
            n0, n1 = head[-1][0], head[5][0] + 0.03
            for yy0, yy1 in ((n0 + (n1 - n0) * i / 3, n0 + (n1 - n0) * (i + 1) / 3) for i in range(3)):
                ym = 0.5 * (yy0 + yy1)
                zz, ww, hh = qb._head_at(head, ym)
                for s in (-1, 1):
                    xs = qb._surface_x(ctx, ym, zz - 0.18 * hh, ww) - 0.002
                    cm.add_box(bm, (s * xs, ym, zz - 0.18 * hh), (0.006, abs(yy1 - yy0) + 0.003, 0.004))
        ctx.make("lips", lips, lambda c, n: "black", ["Head"], sub=0, smooth=False)

        # two small spots over the eyes (a black and tan dog's "eyebrows"). Every coat has the part, in the head's own colour when it has no spots, so that all the coats are
        # one mesh (the same vertices and bones) and the game can swap one for another
        def brows(bm):
            for s in (-1, 1):
                xs = qb._surface_x(ctx, y - 0.005, cz + 1.9 * r, w) - 0.003
                cm.add_box(bm, (s * xs, y - 0.004, cz + 1.9 * r), (0.008, 0.018, 0.012))
        ctx.make("brows", brows, lambda c, n: sk["brows"] or sk["body"], ["Head"], sub=0, smooth=False)

    return dict(
        name=name, body=body, head=head,
        front=front_leg, hind=hind_leg,
        tail=tail, ear_x=ear_x, ear_y=skull[0], ear_z=skull[1] + skull[3] * 0.72,
        coat=coat, head_coat=head_coat, tail_coat=tail_coat,
        body_n=8, head_n=8, tail_n=6, uv_jitter=True,                 # (see quadruped_builder._jitter_uvs: every coat keeps the same vertex count)
        extras=extras)


# ---- the husky: the same builder with its own numbers. A compact northern dog, 0.55 m at the shoulder: the same deep chest as the farm dog but broader (a thick coat), a head
# a little broader, with a fuller, blunter muzzle, small erect triangular ears set close, a full ruff and a brush tail curled over the back. Its coat is grey above and white below,
# with a white mask (muzzle, jaw, blaze and brows). Docs/assets/briefs/animals.md.
HUSKY_SKIN = dict(body="grey_cat", under=W, legs=W, sock=W, ruff="grey_cat", chest=W, muzzle=W, jaw=W, ears="black", tip=None, tail_under=W,
                  blaze=W, brows=W, pattern="plain", label="a grey and white husky")
HUSKY_SHAPE = dict(
    body=[(-0.30, 0.380, 0.084, 0.100), (-0.22, 0.396, 0.120, 0.140), (-0.10, 0.398, 0.120, 0.140), (0.03, 0.405, 0.100, 0.104),
          (0.17, 0.398, 0.104, 0.115), (0.28, 0.385, 0.088, 0.100), (0.32, 0.375, 0.060, 0.076)],
    head=[(-0.24, 0.500, 0.084, 0.108), (-0.31, 0.545, 0.074, 0.094), (-0.36, 0.578, 0.070, 0.082), (-0.41, 0.585, 0.071, 0.076),
          (-0.46, 0.570, 0.064, 0.066), (-0.50, 0.548, 0.054, 0.060), (-0.565, 0.538, 0.050, 0.055), (-0.625, 0.530, 0.045, 0.050)],
    tail=[(0.395, 0.310, 0.034), (0.470, 0.385, 0.050), (0.545, 0.365, 0.050), (0.580, 0.290, 0.038)],           # up and over the back
    front_x=0.076, hind_x=0.086, ears="up", ruff=1.12)


def make_husky(name="DogHusky"):
    return make_farm_dog(name, HUSKY_SKIN, HUSKY_SHAPE)
