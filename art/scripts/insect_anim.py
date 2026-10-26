"""Rig the insects of insects.py and give them clips (Idle, plus Fly, Walk, Hop or the ladybug's Open), for the GLBs of the web viewer.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/insect_anim.py", run_name="__main__")
Optional global INSECT_LIST (names as in insects.CRITTERS). Builds each rigged model and prints its clips; the site build (tools/build_site_assets.py) calls
build_rigged() itself and writes the GLB.

The moving pieces are the ones insects.py marks with moving(): wings, legs, antennae, the ladybug's wing covers and hindwings, a grasshopper's hind legs, a caterpillar's segments. Each becomes
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


def fold_wings(rig, prefix="Wing", back=72.0, down=14.0, spread=0.0, lift=0.0, gap=0.0):
    """Wings laid back along the body, as a fly or mosquito holds them when landed: swung back about Z, then the tail end dropped about X to follow the back.
    The two folded wings overlap over the abdomen like a landed fly's, so they never share a plane: the right one is `gap` mm above the left one. `down` is how far
    the tail end drops (follow the abdomen's slope); `spread` moves each wing outward (mm) and `lift` raises both, if one is needed."""
    for name, s in sides(rig, prefix):
        turn(rig, name, z=s * back, shift=(s * spread * MM, 0, (lift + (gap if s < 0 else 0.0)) * MM))
        turn(rig, name, x=-down)


def idle_folded(rig, t, back=72.0, down=14.0, spread=0.0, lift=0.0, gap=0.0):
    """Landed: wings folded back over the abdomen (a small shiver), the antennae feel about (a housefly has none)."""
    w = 2 * math.pi * t
    turn(rig, "Body", x=1.2 * math.sin(w))
    antennae(rig, w)
    fold_wings(rig, back=back + 2.0 * math.sin(w), down=down, spread=spread, lift=lift, gap=gap)


def hang_legs(rig, droop=126.0, trail=15.0):
    """Legs dangling in flight, nearly straight down: each thigh (Leg_) swings down about Y from the hip by `droop` degrees (the rest knee is 51 degrees up, so 126 leaves it
    75 degrees below the hip) and back about X by `trail`; the shin (Shin_) keeps its own rest direction, which is already down, and only follows the knee. The
    body is raised (a constant, not a bob) so the feet hang above the origin instead of below it."""
    bones = rig.data.bones
    legs = []
    for name, s in sides(rig, "Leg"):
        shin = "Shin" + name[3:]
        hip, knee = Vector(bones[name].head_local), Vector(bones[shin].head_local)
        rot = Matrix.Rotation(radians(trail), 3, "X") @ Matrix.Rotation(radians(s * droop), 3, "Y")
        legs.append((name, shin, s, hip, knee, rot, rot @ (knee - hip) + hip - knee))
    foot_z = min(d.z for *_, d in legs)                                  # the rest feet are at z = 0, a shin moves with its knee
    turn(rig, "Body", shift=(0, 0, -foot_z + 0.0002))
    for name, shin, s, hip, knee, rot, delta in legs:
        turn(rig, name, y=s * droop)
        turn(rig, name, x=trail)
        turn(rig, shin, shift=tuple(delta))


def fly_hanging_legs(rig, t, amp, base):
    fly(rig, t, amp, base, 0.0, 0.0)
    hang_legs(rig)


def idle_butterfly(rig, t):
    """Wings opening and closing slowly, like a butterfly sunning itself."""
    w = 2 * math.pi * t
    turn(rig, "Body", x=1.0 * math.sin(w))
    antennae(rig, w, amp=8.0)
    wings(rig, "Wing", 28.0 * (0.5 + 0.5 * math.sin(w)) - 6.0)


def fly(rig, t, amp, base, bob, pitch, counter=False):
    """A flapping cycle per loop. bob (m, half the travel) and pitch (degrees) make the body rise on the downstroke and pitch with it: only for the slow flapping butterfly and moth,
    and gently (a butterfly 25 mm tall moves 3 mm). A bee, wasp, fly, mosquito or dragonfly holds its body still and only the wings beat (bob = pitch = 0; issue #96). The dragonfly's hind wings beat against its fore wings."""
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


def open_ladybug(rig, t):
    """The wing covers (Elytron_L/R) open like a gull's wings (lifted about a lengthwise line at the suture, the rear swung a little outward) and the hindwings (WingH_L/R) unfold sideways from under them, then all fold back."""
    w = 2 * math.pi * t
    a = min(1.0, 1.5 * (0.5 - 0.5 * math.cos(w)))
    turn(rig, "Body", x=-1.5 * a)
    antennae(rig, w, amp=4.0)
    for name, s in sides(rig, "Elytron"):
        turn(rig, name, y=-s * 55.0 * a, z=-s * 14.0 * a)
    for name, s in sides(rig, "WingH"):
        turn(rig, name, y=-s * 10.0 * a, z=-s * 80.0 * a)


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
    "butterfly": (("Idle", idle_butterfly, 48, 24), ("Fly", lambda r, t: fly(r, t, 38.0, 14.0, 0.0015, 3.0), 8, 24)),
    "moth": (("Idle", idle_flyer, 48, 24), ("Fly", lambda r, t: fly(r, t, 34.0, 12.0, 0.001, 2.5), 6, 24)),
    "buzz": (("Idle", idle_flyer, 48, 24), ("Fly", lambda r, t: fly(r, t, 38.0, 12.0, 0.0, 0.0), 4, 24)),
    "fold": (("Idle", lambda r, t: idle_folded(r, t, back=86.0, down=22.0, spread=-0.48, lift=-0.15, gap=0.25), 48, 24), ("Fly", lambda r, t: fly(r, t, 38.0, 12.0, 0.0, 0.0), 4, 24)),
    "mosquito": (("Idle", lambda r, t: idle_folded(r, t, back=86.0, down=15.0, spread=-0.24, gap=0.12), 48, 24), ("Fly", lambda r, t: fly_hanging_legs(r, t, 38.0, 12.0), 4, 24)),
    "dragonfly": (("Idle", idle_flyer, 48, 24), ("Fly", lambda r, t: fly(r, t, 26.0, 4.0, 0.0, 0.0, counter=True), 6, 24)),
    "walk": (("Idle", idle_walker, 48, 24), ("Walk", walk, 24, 24)),
    "spider": (("Idle", idle_spider, 48, 24), ("Walk", lambda r, t: walk(r, t, swing=15.0, lift=14.0), 24, 24)),
    "caterpillar": (("Idle", idle_caterpillar, 48, 24), ("Walk", walk_caterpillar, 36, 24)),
    "ladybug": (("Idle", idle_walker, 48, 24), ("Walk", walk, 24, 24), ("Open", open_ladybug, 48, 24)),
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
