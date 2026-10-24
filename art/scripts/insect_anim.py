"""Rig the insects of insects.py and give them clips (Idle, plus Fly, Walk or Hop), for the GLBs of the web viewer.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/insect_anim.py", run_name="__main__")
Optional global INSECT_LIST (names as in insects.CRITTERS). Builds each rigged model and prints its clips; the site build (tools/build_site_assets.py) calls
build_rigged() itself and writes the GLB.

The moving pieces are the ones insects.py marks with moving(): wings, legs, antennae, a grasshopper's hind legs, a caterpillar's segments. Each becomes
a bone at its pivot, all children of a Body bone (Root > Body > piece); the mesh is one object skinned rigidly (a piece follows its bone, the faceted
look hides it), like the Insectoid. The models are millimetres in size, so the rig is built in metres at that size and the shifts below are tiny.

Rotations are about the armature's axes through the bone's head (turn()), so the signs do not depend on how a bone was drawn: +Y turns a wing on
the +X side down, so a wing's lift on side s (+1 left, -1 right) is -s times its angle; +Z turns a leg on the +X side towards the back (+Y).
"""

import importlib
import math
import sys
from math import radians
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
import insects
for _m in (common, props_lib, insects):
    importlib.reload(_m)

MM = insects.MM
BONE = 0.004                                                          # every bone is 4 mm long, pointing up (its direction does not matter, its head does)


def turn(rig, name, x=0.0, y=0.0, z=0.0, shift=(0.0, 0.0, 0.0)):
    """Turn a pose bone about the armature's axes through its own head (its children follow, so call parents first), then move it by shift (metres)."""
    pb = rig.pose.bones.get(name)
    if pb is None:
        return
    t = Matrix.Translation(pb.head.copy())
    r = Euler((radians(x), radians(y), radians(z)), "XYZ").to_matrix().to_4x4()
    m = t @ r @ t.inverted() @ pb.matrix
    m.translation += Vector(shift)
    pb.matrix = m
    bpy.context.view_layer.update()


def reset(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()


def sides(rig, prefix):
    """(bone name, +1 for the left / -1 for the right) for every bone `prefix`_L... and `prefix`_R..."""
    out = []
    for pb in rig.pose.bones:
        for tag, s in (("_L", 1), ("_R", -1)):
            if pb.name.startswith(prefix + tag):
                out.append((pb.name, s))
    return out


# ----------------------------------------------------------------------------------------------------------------------
# The poses (t runs 0..1 over the loop; w is the same as an angle)
# ----------------------------------------------------------------------------------------------------------------------

def antennae(rig, w, amp=6.0):
    for name, s in sides(rig, "Antenna"):
        turn(rig, name, x=amp * 0.6 * math.sin(3 * w + s), z=s * amp * math.sin(2 * w + 0.5 * s))


def wings(rig, prefix, angle, base=0.0):
    """Every wing bone called `prefix`_L/_R lifted by `angle` degrees (negative = down)."""
    for name, s in sides(rig, prefix):
        turn(rig, name, y=-s * (base + angle))


def idle_flyer(rig, t, rest=6.0, fan=4.0):
    """Perched: the antennae feel about, the wings fan a little."""
    w = 2 * math.pi * t
    turn(rig, "Body", x=1.2 * math.sin(w))
    antennae(rig, w)
    wings(rig, "Wing", fan * math.sin(w), base=0.0)
    wings(rig, "WingF", fan * math.sin(w))
    wings(rig, "WingH", fan * math.sin(w + 0.8))


def idle_butterfly(rig, t):
    """Wings opening and closing slowly, like a butterfly sunning itself."""
    w = 2 * math.pi * t
    turn(rig, "Body", x=1.0 * math.sin(w))
    antennae(rig, w, amp=8.0)
    wings(rig, "Wing", 28.0 * (0.5 + 0.5 * math.sin(w)) - 6.0)


def fly(rig, t, amp, base, bob, pitch, counter=False):
    """A flapping cycle per loop. The body rises on the downstroke and pitches with it; the dragonfly's hind wings beat against its fore wings."""
    w = 2 * math.pi * t
    turn(rig, "Body", x=-pitch * math.sin(w), shift=(0, 0, -bob * math.cos(w)))
    antennae(rig, w, amp=3.0)
    wings(rig, "Wing", amp * math.sin(w) + base)
    wings(rig, "WingF", amp * math.sin(w) + base)
    wings(rig, "WingH", amp * math.sin(w + (math.pi if counter else 0.0)) + base)


def idle_walker(rig, t):
    w = 2 * math.pi * t
    turn(rig, "Body", x=1.4 * math.sin(w), z=1.0 * math.sin(2 * w))
    antennae(rig, w, amp=9.0)


def walk(rig, t, swing=22.0, lift=16.0):
    """Alternating tripods (or fours, for the spider): a leg's group follows from its number and side; it sweeps back while on the ground and
    forward in the air, raised only while it swings forward."""
    w = 2 * math.pi * t
    turn(rig, "Body", z=2.0 * math.sin(w), shift=(0, 0, 0.0002 * math.sin(2 * w)))
    antennae(rig, w, amp=7.0)
    for name, s in sides(rig, "Leg"):
        i = int(name[5:])
        psi = w + math.pi * ((i + (0 if s > 0 else 1)) % 2)
        turn(rig, name, y=-s * lift * max(0.0, -math.cos(psi)), z=s * swing * math.sin(psi))


def idle_spider(rig, t):
    """Standing: the body rocks a little on its legs, the front pair feels the air."""
    w = 2 * math.pi * t
    turn(rig, "Body", x=1.5 * math.sin(w))
    for name, s in sides(rig, "Leg"):
        if name[5:] == "0":
            turn(rig, name, y=-s * (8.0 + 8.0 * math.sin(w + (0.0 if s > 0 else 1.3))), z=s * 5.0 * math.sin(2 * w))


def _caterpillar(rig, t, amp, head):
    w = 2 * math.pi * t
    for pb in list(rig.pose.bones):
        if pb.name.startswith("Seg"):
            i = int(pb.name[3:])
            turn(rig, pb.name, shift=(0, 0, amp * MM * (0.5 + 0.5 * math.sin(w - 0.9 * i))))
    turn(rig, "Head", x=head * math.sin(w - 0.9 * -1), z=head * 0.7 * math.sin(w * 2),
         shift=(0, 0, amp * MM * (0.5 + 0.5 * math.sin(w + 0.9))))


def walk_caterpillar(rig, t):
    _caterpillar(rig, t, 1.6, 6.0)


def idle_caterpillar(rig, t):
    _caterpillar(rig, t, 0.5, 4.0)


def hop(rig, t):
    """Crouch on the hind legs, kick off, arc through the air with the legs trailing, land and settle (a quarter of the loop each)."""
    w = 2 * math.pi * t
    crouch = math.sin(math.pi * min(t / 0.25, 1.0)) if t < 0.25 else 0.0
    air = math.sin(math.pi * (t - 0.25) / 0.5) if 0.25 <= t < 0.75 else 0.0
    settle = math.sin(math.pi * (t - 0.75) / 0.25) * 0.4 if t >= 0.75 else 0.0
    turn(rig, "Body", x=-8.0 * crouch + 22.0 * air - 6.0 * settle, shift=(0, 0, 0.022 * air - 0.0015 * crouch))
    antennae(rig, w, amp=6.0)
    for name, s in sides(rig, "Hind"):
        turn(rig, name, x=-28.0 * crouch + 30.0 * air + 10.0 * settle)


# motion -> clips: (name, pose, frames, fps)
MOTIONS = {
    "butterfly": (("Idle", idle_butterfly, 48, 24), ("Fly", lambda r, t: fly(r, t, 38.0, 14.0, 0.003, 5.0), 8, 24)),
    "moth": (("Idle", idle_flyer, 48, 24), ("Fly", lambda r, t: fly(r, t, 34.0, 12.0, 0.002, 4.0), 6, 24)),
    "buzz": (("Idle", idle_flyer, 48, 24), ("Fly", lambda r, t: fly(r, t, 38.0, 12.0, 0.0012, 5.0), 4, 24)),
    "dragonfly": (("Idle", idle_flyer, 48, 24), ("Fly", lambda r, t: fly(r, t, 26.0, 4.0, 0.0012, 3.0, counter=True), 6, 24)),
    "walk": (("Idle", idle_walker, 48, 24), ("Walk", walk, 24, 24)),
    "spider": (("Idle", idle_spider, 48, 24), ("Walk", lambda r, t: walk(r, t, swing=15.0, lift=14.0), 24, 24)),
    "caterpillar": (("Idle", idle_caterpillar, 48, 24), ("Walk", walk_caterpillar, 36, 24)),
    "hop": (("Idle", idle_walker, 48, 24), ("Hop", hop, 36, 24)),
}


# ----------------------------------------------------------------------------------------------------------------------
# The rig
# ----------------------------------------------------------------------------------------------------------------------

def build_armature(coll, name, body_head, bones):
    arm = bpy.data.armatures.new(name)
    rig = bpy.data.objects.new(name, arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    up = Vector((0, 0, BONE))
    root = arm.edit_bones.new("Root")
    root.head, root.tail = Vector((0, 0, 0)), up
    body = arm.edit_bones.new("Body")
    body.head, body.tail = Vector(body_head), Vector(body_head) + up
    body.parent = root
    for role, pivot in bones.items():
        eb = arm.edit_bones.new(role)
        eb.head = Vector(pivot) * MM
        eb.tail = eb.head + up
        eb.parent = body
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in arm.bones:
        b.use_deform = True
    return rig


def build_rigged(key):
    """Build insect `key` (a name in insects.CRITTERS) as one skinned mesh with its armature, in a collection of its own. Returns (mesh, rig, coll, clips),
    clips being the (name, pose, frames, fps) to key. The pieces' names are role names, so a Blender file that has others of that name is not safe
    unless common.configure(prefix=...) is set (the site build does)."""
    fn, _ = insects.CRITTERS[key]
    insects.RIGGED = True
    try:
        prop = fn()
    finally:
        insects.RIGGED = False
    obj, coll = prop.finish()
    props_lib.INTERACTIONS.pop(prop.name, None)                       # the pieces are bones, not the doors and drawers interactions.json describes
    bpy.context.view_layer.update()
    pieces = [o for o in coll.all_objects if o.type == "MESH" and o.parent is obj]
    for o in pieces:                                                   # finish() scaled only the body to metres
        for v in o.data.vertices:
            v.co *= MM
        o.location = o.location * MM
    bpy.context.view_layer.update()
    for o in pieces:
        o.data.transform(o.matrix_world)
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
    obj.parent = None
    meshes = [obj] + pieces
    for o in meshes:
        role = "Body" if o is obj else common.plain(o.name).split(".")[0]
        if o is not obj and role not in prop.bones:
            raise RuntimeError(f"{prop.name}: piece {o.name} has no bone")
        o.vertex_groups.new(name=role).add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    zs = [v.co.z for o in meshes for v in o.data.vertices]
    body_head = (0.0, 0.0, (min(zs) + max(zs)) / 2)
    mesh = common.join(meshes, prop.name)
    for role in ["Root", "Body", *prop.bones]:
        if role not in mesh.vertex_groups:
            mesh.vertex_groups.new(name=role)
    rig = build_armature(coll, f"{common.name_prefix()}{prop.name}_Rig", body_head, prop.bones)
    mesh.parent = rig
    mesh.modifiers.new("Armature", "ARMATURE").object = rig
    return mesh, rig, coll, MOTIONS[prop.motion]


def key_clip(rig, name, pose, frames, fps):
    """One looping action (frame frames+1 equals frame 1) keyed on every bone, then parked on the rig as the clip `name` (common.stash_clip)."""
    action = bpy.data.actions.new(name)
    rig.animation_data_create()
    rig.animation_data.action = action
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    for frame in range(1, frames + 2):
        reset(rig)
        pose(rig, ((frame - 1) % frames) / frames)
        for pb in rig.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            pb.keyframe_insert("location", frame=frame)
    reset(rig)
    bpy.ops.object.mode_set(mode="OBJECT")
    return common.stash_clip(rig, action, name, fps=fps)


def key_clips(rig, clips):
    for name, pose, frames, fps in clips:
        key_clip(rig, name, pose, frames, fps)


if __name__ == "__main__":
    names = globals().get("INSECT_LIST")
    x = 0.0
    for key in [k for k in insects.CRITTERS if not names or k in names]:
        mesh, rig, coll, clips = build_rigged(key)
        key_clips(rig, clips)
        rig.location.x = x
        x += 0.06
        print(key, [c[0] for c in clips])
