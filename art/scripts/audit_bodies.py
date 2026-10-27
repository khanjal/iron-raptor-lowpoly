"""Audit the people and the aliens: do their parts join, do the aliens have eyes that show, and are their proportions right?

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/audit_bodies.py", run_name="__main__")
Optional globals: ONLY (a list of file stems, e.g. ["GP_Grey_01"]) and FOLDERS (default People/ and Aliens/ under Assets/Art/Global).

It imports each exported FBX (so it checks what Unity gets, not what the script meant), cuts the mesh into its pieces (connected islands: the
neck, the head, an arm...), and checks what it can. It adds the objects it imported to the Blender file and removes only those again (it never
clears the file: others work in it). The people and the humanoid aliens (GP_*) get all of it; the Insectoid and the Energy Being (GA_*: their own
skeletons or none) get the floating-piece check and the eyes.

 JOINS (no leeway beyond a few millimetres of sampling slack: a gap is a bug)
   - no floating piece. The aliens: every island's surface touches another island's (crosses it, or a vertex within 3 mm of it), or sits inside a closed one. The people: its box, grown
     by 1 cm, meets another island's box (their eye boxes still hover a few millimetres off the skin, which this does not see: issue #183).
     The Energy Being's shards and wisps orbit its core on purpose (FLOATING_ON_PURPOSE), so for it only its eyes must touch the core
   - the neck reaches into the skull and into the torso (at least 4 mm each)
   - each arm starts inside the torso, each leg inside the pelvis, each shoe overlaps the bottom of its leg and covers its back edge (no
     slit behind the ankle)

 EYES (the aliens)
   - a mirrored pair of pieces in the upper half of the head, in front, whose surface touches the head or the body they sit on, and that shows
     at least 4 mm outside it (a buried eye is invisible). It cannot tell an eye from a brow: a pair of brows would pass, so look at the head too.
     The Insectoid's pair must be lumps on its head (every side 5 cm or more); the Energy Being's sits on its core

 PROPORTIONS (ratios to the height of the figure, from the sole to the top of the skull; hats and hair do not count)
   - head height, neck length (torso top to skull bottom), neck width against the head, arm length (the arm and its hand paddle: an alien's loose fingers
     are not counted), hip height (the legs), foot length
   People must sit in HUMAN. An alien may differ a little (ALIEN_WIDEN loosens every range) and, where a design asks for more (the Grey's
   huge head), it says so in ALLOWED with the range and the reason: the report prints those as "allowed", not as a pass.

Prints one line per model, then the problems. Fix the builder (gp_builder.py, gp_cast.py), re-export, run this again.
"""

import bmesh
import bpy
import glob
import os
import sys
from pathlib import Path

from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

REPO = common.REPO
GLOBAL = common.out_dir() / "Assets" / "Art" / "Global"

# ratios to the figure's height (sole to the top of the skull); an adult. A child (GP_FarmerKid) has the CHILD overrides.
HUMAN = {
    "head": (0.115, 0.155),        # skull height: about 1/7.5 of an adult
    "neck": (0.025, 0.085),        # visible neck: torso top to skull bottom
    "neck_w": (0.38, 0.72),        # neck width against the skull's width (a heavy build's neck is 1.3x: 0.38-0.65 for the average ones)
    "arm": (0.33, 0.47),           # the arm island, shoulder to fingertip, hanging or in a T-pose
    "leg": (0.43, 0.56),           # hip height: the top of the leg
    "foot": (0.12, 0.165),         # shoe length (a foot is about 15% of the height)
}
CHILD = {"head": (0.15, 0.21), "neck": (0.02, 0.085), "foot": (0.13, 0.18)}

HUMAN_BUILD = {   # the mass factor (the build's anchors of builds.json) -> measure -> (lowest, highest) as a ratio of the figure's height; between the anchors it is interpolated.
    # ribs_d was raised 10% for the people rebuild (issue #90: a deeper chest and back, docs/assets/briefs/people.md).
    # Written from the first pictures and measurements (the 10 adults at each anchor, all shapes and sexes together) with 7% slack each way: a deviation is a model that stopped looking like its build.
    0.8: {"hip_w": (0.152, 0.203), "waist_w": (0.125, 0.157), "ribs_w": (0.118, 0.157), "chest_w": (0.155, 0.21), "shoulder_w": (0.176, 0.254), "neckbase_w": (0.095, 0.115), "waist_d": (0.078, 0.094), "ribs_d": (0.083, 0.102), "waist_f": (0.034, 0.041), "ribs_f": (0.038, 0.046), "thigh_w": (0.075, 0.086), "upper_arm_t": (0.041, 0.047), "neck_t": (0.053, 0.061)},
    1.0: {"hip_w": (0.165, 0.221), "waist_w": (0.146, 0.182), "ribs_w": (0.134, 0.178), "chest_w": (0.169, 0.228), "shoulder_w": (0.183, 0.265), "neckbase_w": (0.104, 0.125), "waist_d": (0.095, 0.114), "ribs_d": (0.098, 0.122), "waist_f": (0.043, 0.051), "ribs_f": (0.045, 0.055), "thigh_w": (0.085, 0.098), "upper_arm_t": (0.045, 0.052), "neck_t": (0.057, 0.066)},
    1.2: {"hip_w": (0.178, 0.239), "waist_w": (0.16, 0.201), "ribs_w": (0.143, 0.19), "chest_w": (0.175, 0.237), "shoulder_w": (0.189, 0.273), "neckbase_w": (0.114, 0.138), "waist_d": (0.116, 0.139), "ribs_d": (0.118, 0.146), "waist_f": (0.058, 0.07), "ribs_f": (0.058, 0.071), "thigh_w": (0.094, 0.108), "upper_arm_t": (0.048, 0.055), "neck_t": (0.063, 0.073)},
    1.45: {"hip_w": (0.191, 0.256), "waist_w": (0.172, 0.215), "ribs_w": (0.15, 0.199), "chest_w": (0.179, 0.241), "shoulder_w": (0.192, 0.278), "neckbase_w": (0.126, 0.153), "waist_d": (0.143, 0.171), "ribs_d": (0.140, 0.173), "waist_f": (0.084, 0.1), "ribs_f": (0.078, 0.096), "thigh_w": (0.109, 0.126), "upper_arm_t": (0.053, 0.061), "neck_t": (0.07, 0.081)},
    1.6: {"hip_w": (0.198, 0.265), "waist_w": (0.181, 0.226), "ribs_w": (0.155, 0.206), "chest_w": (0.181, 0.244), "shoulder_w": (0.194, 0.281), "neckbase_w": (0.135, 0.163), "waist_d": (0.158, 0.189), "ribs_d": (0.154, 0.189), "waist_f": (0.099, 0.117), "ribs_f": (0.091, 0.11), "thigh_w": (0.114, 0.131), "upper_arm_t": (0.055, 0.063), "neck_t": (0.075, 0.086)},
}
CHILD_BUILD_SLACK = 0.08           # a child's build measures sit within the adults' ranges widened by this much each way
ARM_CLEARANCE = 0.04               # a build may push the arms this much (metres) deeper into the torso than the NEUTRAL body of the same person does (the reference, built at mf 1.0): the neutral body already has 3-6.5 cm of arm
                                   # inside the torso somewhere in the clips (the Run's bent arm sweeps across the hip and belly; the upper arm hangs against the chest), so the absolute depth means nothing, the difference does.
                                   # The heaviest builds (mf 1.6) measure 2.0-3.0 cm over their neutral body: the belly and hips are in the way of a hand that swings across them, which only a different
                                   # skeleton or clip would fix
ARM_ELBOW = 0.62                   # the forearm and hand are lower than this fraction of the figure's height, the upper arm is between this and ARM_SHOULDER (two bands, each against its own reference)
ARM_SHOULDER = 0.70                # above it is the shoulder, where the arm starts inside the torso by design
CHILDREN = {"GP_FarmerKid_01"}
ALIENS = {"GP_Grey_01", "GP_Shadow_01", "GP_Nordic_01", "GP_Reptilian_01"}
OTHER_ALIENS = {"GA_Insectoid_01", "GA_EnergyBeing_01"}      # not on the person skeleton: floating pieces and eyes only
FLOATING_ON_PURPOSE = {"GA_EnergyBeing_01": "the shards orbit the core and the wisps trail below it"}
EYE_PROUD = 0.004                  # an eye shows at least this far outside what it sits on
ALIEN_WIDEN = 0.25                 # an alien's ranges are loosened by 25% each side
ALLOWED = {                        # model -> {measure: (low, high, why)}: a design choice that is outside even the widened range.
    # Only what a model really needs: an entry that is never outside the widened range would hide a later regression.
    "GP_Grey_01": {"head": (0.2, 0.32, "the Grey's head is 2.05x: the huge-headed grey of the folklore"),
                   "neck_w": (0.22, 0.30, "a thin stalk of a neck under that head: the neck is 0.10 m across, the skull 0.43 m")},
}


def _build_range(measure, mf, child=False):
    """The (lowest, highest) a build measure may have at mass factor mf: HUMAN_BUILD interpolated between the anchors (held outside them), widened for a child."""
    anchors = sorted(HUMAN_BUILD)
    if mf <= anchors[0]:
        lo, hi = HUMAN_BUILD[anchors[0]][measure]
    elif mf >= anchors[-1]:
        lo, hi = HUMAN_BUILD[anchors[-1]][measure]
    else:
        for a, b in zip(anchors, anchors[1:]):
            if a <= mf <= b:
                t = (mf - a) / (b - a)
                (l0, h0), (l1, h1) = HUMAN_BUILD[a][measure], HUMAN_BUILD[b][measure]
                lo, hi = l0 + (l1 - l0) * t, h0 + (h1 - h0) * t
                break
    if child:
        lo, hi = lo * (1 - CHILD_BUILD_SLACK), hi * (1 + CHILD_BUILD_SLACK)
    return lo, hi


def _ranges(stem):
    r = dict(HUMAN)
    if stem in CHILDREN:
        r.update(CHILD)
    if stem in ALIENS:
        r = {k: (lo * (1 - ALIEN_WIDEN), hi * (1 + ALIEN_WIDEN)) for k, (lo, hi) in r.items()}
    return r


def _islands(bm):
    seen, islands = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            x = stack.pop()
            comp.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen:
                    seen.add(y.index)
                    stack.append(y)
        islands.append(comp)
    return islands


class Piece:
    """One island: its sample points (corners and the middle of every face) and its box."""

    def __init__(self, comp, mw, names, me):
        faces = {f for v in comp for f in v.link_faces}
        self.pts = [mw @ v.co for v in comp] + [mw @ f.calc_center_median() for f in faces]
        local = {v.index: i for i, v in enumerate(comp)}
        self.vi = [v.index for v in comp]
        self._vco = [mw @ v.co for v in comp]
        self._polys = [[local[v.index] for v in f.verts] for f in faces]
        self._tree = None
        self.closed = all(len(e.link_faces) == 2 for v in comp for e in v.link_edges)    # a closed surface has an inside; a face cap does not
        xs, ys, zs = [p.x for p in self.pts], [p.y for p in self.pts], [p.z for p in self.pts]
        self.x0, self.x1, self.y0, self.y1, self.z0, self.z1 = min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)
        acc = {}
        for v in comp:
            for g in me.vertices[v.index].groups:
                acc[names[g.group]] = acc.get(names[g.group], 0.0) + g.weight
        self.group = max(acc, key=acc.get) if acc else "?"
        self.n = len(comp)

    @property
    def xr(self):
        return max(abs(self.x0), abs(self.x1))

    @property
    def tree(self):
        if self._tree is None:
            self._tree = BVHTree.FromPolygons([tuple(v) for v in self._vco], self._polys)
        return self._tree

    def inside(self, point):
        """Is the point inside this piece? Only a closed surface has an inside: the nearest face looks away from the point."""
        if not self.closed:
            return False
        hit = self.tree.find_nearest(point)
        return hit[0] is not None and (point - hit[0]).dot(hit[1]) < 0

    def near(self, other, tol):
        """Does some vertex of this piece lie within tol of the other piece's surface?"""
        for v in self._vco:
            hit = other.tree.find_nearest(v)
            if hit[0] is not None and hit[3] <= tol:
                return True
        return False

    def depth_of(self, other):
        """How far the most protruding vertex of this piece stands outside the other piece's surface (negative: all of it is inside)."""
        best = -1.0
        for v in self._vco:
            hit = other.tree.find_nearest(v)
            if hit[0] is None:
                continue
            best = max(best, -hit[3] if other.inside(v) else hit[3])
        return best


TOUCH = 0.003


def touches(a, b):
    """Do the two pieces' surfaces meet (a triangle of one crosses a triangle of the other), come within TOUCH of each other at some vertex, or does
    one sit inside the other (when that one is a closed surface)?"""
    return bool(a.tree.overlap(b.tree)) or a.near(b, TOUCH) or b.near(a, TOUCH) or b.inside(a._vco[0]) or a.inside(b._vco[0])


def _meets(a, b, slack=0.01):
    """Do the two pieces' boxes meet, each grown by slack?"""
    return (a.x0 - slack <= b.x1 and b.x0 - slack <= a.x1 and a.y0 - slack <= b.y1 and b.y0 - slack <= a.y1 and a.z0 - slack <= b.z1 and b.z0 - slack <= a.z1)


def _centre(p):
    return ((p.x0 + p.x1) / 2, (p.y0 + p.y1) / 2, (p.z0 + p.z1) / 2)


def _mirror_pairs(cands):
    """Pairs (a, b) of pieces that are each other's reflection in x = 0 (same height and depth, within 1 cm)."""
    pairs = []
    for a in cands:
        ca = _centre(a)
        if ca[0] <= 0.005:
            continue
        for b in cands:
            cb = _centre(b)
            if b is not a and abs(ca[0] + cb[0]) < 0.01 and abs(ca[1] - cb[1]) < 0.01 and abs(ca[2] - cb[2]) < 0.01:
                pairs.append((a, b))
    return pairs


def _eyes(cands, hosts, problems, what):
    """At least one mirrored pair of candidates that touches a host piece and shows EYE_PROUD outside it."""
    good = bad = 0
    for a, b in _mirror_pairs(cands):
        ok = all(any(h is not e and h is not a and h is not b and touches(e, h) and e.depth_of(h) >= EYE_PROUD for h in hosts) for e in (a, b))
        good += ok
        bad += not ok
    if not good:
        problems.append(f"no eyes: {what} has no mirrored pair that touches it and shows {EYE_PROUD * 1000:.0f} mm or more" + (f" ({bad} pairs are buried or loose)" if bad else ""))


def _levels(piece, gap=0.02):
    """The rings of a lofted piece: for each height level of its vertices (levels closer than gap are one) the x and y extents: [(z, x0, x1, y0, y1), ...] from the bottom."""
    pts = sorted(piece._vco, key=lambda v: v.z)
    groups = []
    for v in pts:
        if groups and v.z - groups[-1][-1].z <= gap:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [(sum(v.z for v in g) / len(g), min(v.x for v in g), max(v.x for v in g), min(v.y for v in g), max(v.y for v in g)) for g in groups]


def _inside_closed(tree, point):
    """Is the point inside a closed surface: an odd number of crossings of a ray along +X (the nearest face's normal is not reliable beside an edge or a cap)."""
    from mathutils import Vector
    hits, origin = 0, point.copy()
    for _ in range(40):
        hit = tree.ray_cast(origin, Vector((1.0, 0.0, 0.0)))
        if hit[0] is None:
            break
        hits += 1
        origin = hit[0] + Vector((1e-4, 0.0, 0.0))
    return hits % 2 == 1


def _arm_clearance(rig, mesh_obj, torso, arms, height):
    """How far the hanging arms stand inside the torso, below the shoulder, in the poses of the game's clips (gp_clips: the Idle, the Walk and the Run with the arms swinging): the
    biggest depth of any arm vertex lower than ARM_SHOULDER of the height. The imported rig is posed in place and put back; the posed mesh is read back by vertex index.
    Two bands: the forearm and hand (lower than ARM_ELBOW of the height) and the upper arm (ARM_ELBOW to ARM_SHOULDER). Returns (forearm depth, upper arm depth); the caller compares
    them with the neutral body's (ARM_CLEARANCE). A build that is broad where the arm hangs fails that whatever its joins say: the shared skeleton and clips cannot move the arm out of the way."""
    import gp_clips
    worst = [0.0, 0.0]
    gp_clips.reset(rig)
    gp_clips.REST_LOW = gp_clips.lowest_foot(rig)
    mw = mesh_obj.matrix_world
    try:
        for pose, t in ((gp_clips.standing, 0.0), (gp_clips.walking, 0.0), (gp_clips.walking, 0.25), (gp_clips.running, 0.25)):
            gp_clips.reset(rig)
            pose(rig, t)
            dg = bpy.context.evaluated_depsgraph_get()
            eo = mesh_obj.evaluated_get(dg)
            me = eo.to_mesh()
            tree = BVHTree.FromPolygons([mw @ me.vertices[i].co for i in torso.vi], torso._polys)
            for a in arms:
                for i in a.vi:
                    p = mw @ me.vertices[i].co
                    if p.z >= ARM_SHOULDER * height:
                        continue
                    if _inside_closed(tree, p):
                        hit = tree.find_nearest(p)
                        band = 0 if p.z < ARM_ELBOW * height else 1
                        worst[band] = max(worst[band], hit[3] if hit[0] is not None else 0.0)
            eo.to_mesh_clear()
    finally:
        gp_clips.reset(rig)
    return tuple(worst)


def _build_measures(torso, legs, arms, neck, skull, height):
    """The build's measures (issue #269), ratios to the figure's height like the proportions: the torso's width at its six rings (hips, waist, ribs, chest, shoulders, neck base: hip_w ...),
    its depth at the waist and ribs (waist_d, ribs_d), how far its front stands in front of the body's middle at the waist and ribs (waist_f, ribs_f: the belly), the thickest thigh,
    upper arm and neck. The torso's rings are found as the height levels of its vertices (a loft: six rings and nothing between), the rest from the islands' own extents."""
    m = {}
    rings = _levels(torso)
    if len(rings) >= 6:
        names = ("hip", "waist", "ribs", "chest", "shoulder", "neckbase")
        for name, (z, x0, x1, y0, y1) in zip(names, rings[:6]):
            m[name + "_w"] = (x1 - x0) / height
        m["waist_d"] = (rings[1][4] - rings[1][3]) / height
        m["ribs_d"] = (rings[2][4] - rings[2][3]) / height
        m["waist_f"] = -rings[1][3] / height               # the front of the torso (y is negative in front) at the waist, ratio to the height
        m["ribs_f"] = -rings[2][3] / height
    if legs:                                               # the thigh: the leg's width a little below the hips (the top ring is capped to the torso's side: it says nothing about the build)
        widths = []
        for l in legs:
            xs = [v.x for v in l._vco if 0.36 * height <= v.z <= 0.44 * height]
            if xs:
                widths.append(max(xs) - min(xs))
        if widths:
            m["thigh_w"] = max(widths) / height
    if arms:
        t = []
        for a in arms:                                     # the upper arm: the arm's length between a quarter and a half of the way out (the elbow's ring: its thickness is the mean of the upper arm's and the forearm's factors; the shoulder's end is inside the torso)
            xi, xo = min(abs(a.x0), abs(a.x1)), max(abs(a.x0), abs(a.x1))
            lo, hi = xi + 0.25 * (xo - xi), xi + 0.5 * (xo - xi)
            zs = [v.z for v in a._vco if lo <= abs(v.x) <= hi]
            if zs:
                t.append(max(zs) - min(zs))
        if t:
            m["upper_arm_t"] = max(t) / height
    m["neck_t"] = (neck.x1 - neck.x0) / height
    m["face_w"] = (skull.x1 - skull.x0) / height
    return m


def audit(path, mf=None, ref=None):
    """Import one FBX, check it, and remove what the import made (and only that: the Blender file may hold other people's work). mf: the build it was made at (for its ranges)."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    made = [o for o in bpy.data.objects if o not in before]
    try:
        return _audit_imported(Path(path).stem, made, mf, ref)
    finally:
        for o in made:
            bpy.data.objects.remove(o, do_unlink=True)


def _audit_imported(stem, made, mf=None, ref=None):
    m = next((o for o in made if o.type == "MESH"), None)
    if m is None:
        return stem, ["no mesh"], [], {}
    names = {vg.index: vg.name for vg in m.vertex_groups}
    me = m.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    mw = m.matrix_world
    pieces = [Piece(c, mw, names, me) for c in _islands(bm)]
    bm.free()

    problems, notes, measures = [], [], {}

    # --- floating pieces ---------------------------------------------------------------------------------------------------------
    if stem in FLOATING_ON_PURPOSE:
        notes.append(f"floating pieces are allowed ({FLOATING_ON_PURPOSE[stem]})")
    else:
        surface = stem in ALIENS or stem in OTHER_ALIENS      # the people's face boxes still float a few millimetres off the skin (#183): the box test for them
        for i, p in enumerate(pieces):
            if not any(_meets(p, q) and (touches(p, q) if surface else True) for j, q in enumerate(pieces) if j != i):
                problems.append(f"floating piece ({p.group}, z {p.z0:.2f}-{p.z1:.2f}, x {p.x0:+.2f}..{p.x1:+.2f}): " + ("its surface touches no other piece's" if surface else "its box meets no other piece's"))

    if stem in OTHER_ALIENS:                       # no skull, no person skeleton: the eyes are the pair of pieces high on the front that sits on the biggest piece
        top = max(p.z1 for p in pieces)
        big = max(pieces, key=lambda p: (p.x1 - p.x0) * (p.y1 - p.y0) * (p.z1 - p.z0))
        heads = [p for p in pieces if p.group == "Head"]                            # the Insectoid has a Head bone; the Energy Being has no groups at all
        least = 0.05 if heads else 0.02                                             # an eye is a lump (every side 5 cm or more on the Insectoid): not an antenna or a mandible
        cands = [p for p in (heads or pieces) if p is not big and _centre(p)[2] > 0.5 * top and _centre(p)[1] < _centre(big)[1]
                 and min(p.x1 - p.x0, p.y1 - p.y0, p.z1 - p.z0) >= least]
        _eyes(cands, pieces, problems, "head or core")
        return stem, problems, notes, {"height": top}

    # --- the skeleton of the checks: find the skull, neck, torso, arms, legs, shoes --------------------------------------------------
    skulls = sorted([p for p in pieces if p.group == "Head" and p.n > 20], key=lambda p: p.z0)
    if not skulls:
        return stem, problems + ["no skull found"], notes, measures
    skull = skulls[0]
    height = skull.z1
    necks = [p for p in pieces if p is not skull and p.z1 >= skull.z0 - 0.01 and p.z1 <= skull.z0 + 0.06 and p.z0 < skull.z0 and p.xr < skull.xr]
    # the torso: the tall piece that starts low (the arms start at the shoulders, a vest or a skirt covers part of the height). A broad torso can weigh more to a clavicle than to the spine
    torso_groups = ("spine_03", "spine_02", "spine_01", "pelvis") + (() if stem in ALIENS else ("clavicle_l", "clavicle_r"))     # (an alien's shoulder balls weigh to the clavicles: not a torso)
    torso = max((p for p in pieces if p.group in torso_groups and p.z1 > 0.4 * height and (stem in ALIENS or p.z0 < 0.55 * height)), key=lambda p: p.z1, default=None)
    arms = [p for p in pieces if p.n > 20 and p.xr - min(abs(p.x0), abs(p.x1)) > 0.25 * height * 0.6 and p.z0 > 0.4 * height]     # (a finger is a piece too: it has few vertices)
    legs = [p for p in pieces if p.z0 < 0.12 * height and 0.3 * height < p.z1 < 0.65 * height]
    shoes = [p for p in pieces if p.z1 < 0.1 * height]
    if not necks or torso is None:
        problems.append("no neck or no torso found")
        return stem, problems, notes, measures
    neck = necks[0]
    if stem in ALIENS:                             # the eyes: a mirrored pair on the front of the skull's upper half that shows outside it
        h = skull.z1 - skull.z0
        sy = _centre(skull)[1]
        cands = [p for p in pieces if p is not skull and p.group == "Head" and skull.z0 + 0.35 * h < _centre(p)[2] < skull.z0 + 0.92 * h and _centre(p)[1] < sy]
        _eyes(cands, [skull], problems, "skull")

    # --- joins -----------------------------------------------------------------------------------------------------------------------
    if neck.z1 - skull.z0 < 0.004:
        problems.append(f"the neck does not reach the skull ({neck.z1 - skull.z0:+.3f} m into it)")
    if torso.z1 - neck.z0 < 0.004:
        problems.append(f"the neck does not reach the torso ({torso.z1 - neck.z0:+.3f} m into it)")
    for a in arms:
        near = [v for v in torso.pts if abs(v.z - (a.z0 + a.z1) * 0.5) < 0.08]
        reach = max((abs(v.x) for v in near), default=0.0)
        inner = min(abs(a.x0), abs(a.x1))
        if inner > reach + 0.005:
            problems.append(f"an arm starts outside the torso (its inner end at |x| {inner:.3f}, the torso's edge at {reach:.3f})")
    for leg in legs:
        if leg.z1 < torso.z0 + 0.01:
            problems.append(f"a leg does not reach into the pelvis (its top z {leg.z1:.3f}, the pelvis's bottom {torso.z0:.3f})")
    for s in shoes:
        near = [l for l in legs if abs((l.x0 + l.x1) * 0.5 - (s.x0 + s.x1) * 0.5) < 0.1]
        if near and s.z1 < near[0].z0 - 0.002:
            problems.append(f"a shoe does not reach its leg (shoe top z {s.z1:.3f}, leg bottom {near[0].z0:.3f})")
        if near:
            back = max((p.y for p in near[0].pts if p.z < near[0].z0 + 0.03), default=None)
            if back is not None and s.y1 < back - 0.004:
                problems.append(f"the back of a leg overhangs its shoe (the leg's bottom edge at y {back:.3f}, the heel ends at {s.y1:.3f})")

    # --- proportions ---------------------------------------------------------------------------------------------------------------
    measures["head"] = (skull.z1 - skull.z0) / height
    measures["neck"] = (skull.z0 - torso.z1) / height
    measures["neck_w"] = (neck.x1 - neck.x0) / max(1e-6, skull.x1 - skull.x0)
    if arms:
        measures["arm"] = sum((a.xr - min(abs(a.x0), abs(a.x1))) for a in arms) / len(arms) / height
    if legs:
        measures["leg"] = sum(l.z1 for l in legs) / len(legs) / height
    if shoes:
        measures["foot"] = max(s.y1 - s.y0 for s in shoes)
        measures["foot"] /= height
    if stem not in ALIENS:
        measures.update(_build_measures(torso, legs, arms, neck, skull, height))
        rig = next((o for o in made if o.type == "ARMATURE"), None)
        if rig is not None and arms:
            measures["arm_in"], measures["arm_in_upper"] = _arm_clearance(rig, m, torso, arms, height)
            if ref is not None:
                if measures["arm_in"] > ref[0] + ARM_CLEARANCE:
                    problems.append(f"a swinging forearm or hand stands {measures['arm_in'] * 100:.1f} cm inside the torso in the Idle, Walk or Run pose, the neutral body's {ref[0] * 100:.1f} cm + {ARM_CLEARANCE * 100:.0f} is the limit")
                if measures["arm_in_upper"] > ref[1] + ARM_CLEARANCE:
                    problems.append(f"a hanging upper arm stands {measures['arm_in_upper'] * 100:.1f} cm inside the chest in the Idle, Walk or Run pose, the neutral body's {ref[1] * 100:.1f} cm + {ARM_CLEARANCE * 100:.0f} is the limit")
        if mf is not None:
            for k in HUMAN_BUILD[min(HUMAN_BUILD)]:
                if k in measures:
                    lo, hi = _build_range(k, mf, stem in CHILDREN)
                    if not lo <= measures[k] <= hi:
                        problems.append(f"{k} {measures[k]:.3f} is outside {lo:.3f}-{hi:.3f} for a build of {mf:.2f}")
    ranges = _ranges(stem)
    for k, v in measures.items():
        if k not in ranges:
            continue
        lo, hi = ranges[k]
        if lo <= v <= hi:
            continue
        allowed = ALLOWED.get(stem, {}).get(k)
        if allowed and allowed[0] <= v <= allowed[1]:
            notes.append(f"{k} {v:.3f} is outside {lo:.3f}-{hi:.3f} but allowed ({allowed[2]})")
        else:
            problems.append(f"{k} {v:.3f} is outside {lo:.3f}-{hi:.3f}" + (f" (allowed {allowed[0]:.2f}-{allowed[1]:.2f}: {allowed[2]})" if allowed else ""))
    measures["height"] = height
    return stem, problems, notes, measures


_REF = {}                                          # the neutral body of each cast person, audited once: key -> (forearm depth, upper arm depth) of the arm test


def _reference(key, folder):
    """The neutral body (mf 1.0) of cast person `key`: the arm test's reference. Audited once per session run (its own problems are printed and counted by the caller)."""
    if key not in _REF:
        _, problems, _, m = audit(_make_person(key, 1.0, folder), 1.0)
        _REF[key] = ((m.get("arm_in", 0.0), m.get("arm_in_upper", 0.0)), problems)
    return _REF[key]


def _make_person(key, mf, folder):
    """Build the cast person `key` at the (region) mass factor mf, export it under folder as GP_<Name>_01.fbx (the audit finds a child and the aliens by the file's name) and return the
    path. The objects the build made are removed again."""
    import gp_builder
    import gp_cast
    spec = dict(gp_cast.CAST[key])
    spec["mf"] = mf
    name = "GP_" + key.title().replace("_", "") + "_01"
    path = os.path.join(folder, name + ".fbx")
    try:
        gp_builder.build("B269_audit_" + key, export=path, **spec)
    finally:                                                    # the build's objects go even if it or the export raised
        coll = bpy.data.collections.get("B269_audit_" + key)
        if coll is not None:
            # the loop removes from the live collection, so it iterates a copy
            for o in list(coll.objects):  # NOSONAR
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(coll)
    return path


def _builds_audit(only):
    """The people at their ends: each cast person built at the lightest and the heaviest mass factor the data allows (and at every anchor of HUMAN_BUILD when EVERY_ANCHOR is set), exported to a
    temporary folder and audited like the real files (joins, proportions, the measures of their build, the arm clearance against the neutral body of the same person). The joins must hold at every
    build: a gap at the shoulder or the hip is a failure. Returns the number of models with problems."""
    import shutil
    import tempfile
    import builds
    data = builds.load()
    folder = tempfile.mkdtemp(prefix="body_builds_")
    bad = checked = 0
    try:
        for name, role in data["roles"].items():
            stem = role["model"]
            if only and stem not in only:
                continue
            key = role["cast"]
            lim = data["childLimits"] if role.get("child") else data["limits"]
            off = data["childRegionOffset"] if role.get("child") else 0.0
            already = key in _REF
            ref, ref_problems = _reference(key, os.path.join(folder, "ref"))
            if not already:
                for p in ref_problems:                              # the neutral body is a build too: its problems count (the reference of the arm test must be a sound body)
                    print(f"{stem:18s} FAIL at mf 1.00 (the reference): {p}")
                bad += bool(ref_problems)
            levels = [lim["min"] + off, lim["max"] + off]
            if globals().get("EVERY_ANCHOR"):
                levels = sorted(set(levels + list(HUMAN_BUILD)))
            for region_mf in levels:
                path = _make_person(key, region_mf, os.path.join(folder, f"mf{region_mf:.2f}"))
                _, problems, _, m = audit(path, region_mf, ref)
                checked += 1
                print(f"{stem:18s} {'FAIL' if problems else 'ok':4s} at mf {region_mf - off:.2f}: waist {m.get('waist_w', 0):.3f} x {m.get('waist_d', 0):.3f} belly {m.get('waist_f', 0):.3f} thigh {m.get('thigh_w', 0):.3f} neck {m.get('neck_t', 0):.3f} arm_in {m.get('arm_in', 0) * 100:.1f}/{m.get('arm_in_upper', 0) * 100:.1f} cm (neutral {ref[0] * 100:.1f}/{ref[1] * 100:.1f})")
                for p in problems:
                    print("    PROBLEM:", p)
                bad += bool(problems)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    print(f"audit_bodies (builds at their ends): {checked} builds, {bad} with problems")
    return bad


def main():
    import builds
    only = globals().get("ONLY")
    folders = globals().get("FOLDERS") or [GLOBAL / "People", GLOBAL / "Aliens"]
    files = []
    for folder in folders:
        files += sorted(glob.glob(str(Path(folder) / "G[PA]_*_01.fbx")))
    import people_proportions
    table_bad = 0
    for p in people_proportions.check():                       # the shared body's tables against the brief (docs/assets/briefs/people.md)
        print("    PROBLEM (body tables):", p)
        table_bad += 1
    print("people_proportions: " + " ".join(f"{k} {v:.3f}" for k, v in people_proportions.measure().items()))
    data = builds.load()
    by_model = {r["model"]: (n, r) for n, r in data["roles"].items()}
    bad = checked = 0
    ref_dir = None
    _REF.clear()                                   # (the references are built once per run)
    for f in files:
        stem = Path(f).stem
        if only and stem not in only:
            continue
        mf = ref = None
        if stem in by_model:                       # a person of the cast: audited at its role's build, against the neutral body of the same person
            import shutil
            import tempfile
            role_name, role = by_model[stem]
            mf = builds.region_mf(role_name, data=data)
            ref_dir = ref_dir or tempfile.mkdtemp(prefix="body_ref_")
            already = role["cast"] in _REF
            ref, ref_problems = _reference(role["cast"], ref_dir)
            if not already:
                for p in ref_problems:
                    print(f"{stem:18s} FAIL at mf 1.00 (the neutral reference): {p}")
                bad += bool(ref_problems)
        stem, problems, notes, m = audit(f, mf, ref)
        checked += 1
        line = " ".join(f"{k} {m[k]:.3f}" for k in ("head", "neck", "neck_w", "arm", "leg", "foot") if k in m)
        if problems:
            status = "FAIL"
        elif notes:
            status = "ok (allowed deviations)"
        else:
            status = "ok"
        print(f"{stem:18s} {status:24s} H {m.get('height', 0):.2f} m | {line}")
        for p in problems:
            print("    PROBLEM:", p)
        for n in notes:
            print("    allowed:", n)
        bad += bool(problems)
    if ref_dir:
        import shutil
        shutil.rmtree(ref_dir, ignore_errors=True)
    bad += table_bad
    print(f"audit_bodies: {checked} models, {bad} with problems")
    if globals().get("BUILDS", True):
        bad += _builds_audit(only)
    return bad


if __name__ == "__main__":
    main()
