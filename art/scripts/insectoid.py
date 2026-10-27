"""The Insectoid (GA-04): a 2.3 m mantis-like biped on digitigrade hind legs, a rig of 17 bones and Idle, Walk, Run and Carry clips.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/insectoid.py", run_name="__main__")
Exports Assets/Art/Global/Aliens/GA_Insectoid_01.fbx with the armature and the clips inside the same file (so a clip's bone paths match the
model's exactly: no remapping in Unity). It is a Generic rig, one mesh skinned rigidly (every piece follows one bone, the faceted look hides it).

The body: a thorax leaning forward, a long abdomen carried out behind at hip height as a counterweight (it sways and rises with the stride), a head
with huge eyes, mandibles and antennae, two grasping fore-arms (an upper arm and a spiked forearm) held folded, a small second pair, and hind
legs with a thigh, a shin and a long foot. It faces -Y like every model.

Bones (a name per piece, _L is +X): Root > Hips > Spine > Head, UpperArm_x > Fore_x, Arm2_x; Hips > Abdomen, Thigh_x > Shin_x > Foot_x.
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
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop

NAME = "GA_Insectoid_01"
BODY, JOINT, EYE, SPIKE = "tractor_green", "rust", "paint_yellow", "horn_cream"

HIP_Y = 0.10
# bone: (parent, head, tail); the heads are the pivots of the pieces
BONES = {"Root": (None, (0, 0, 0), (0, 0, 0.15)),
         "Hips": ("Root", (0, 0.08, 0.85), (0, 0.08, 0.98)),
         "Spine": ("Hips", (0, 0.05, 1.0), (0, -0.08, 1.5)),
         "Head": ("Spine", (0, -0.10, 1.65), (0, -0.16, 1.98)),
         "Abdomen": ("Hips", (0, 0.12, 0.96), (0, 0.85, 0.80))}
for _name, _s in (("L", 1), ("R", -1)):
    BONES.update({
        f"UpperArm_{_name}": ("Spine", (_s * 0.19, -0.08, 1.50), (_s * 0.30, -0.30, 1.36)),
        f"Fore_{_name}": (f"UpperArm_{_name}", (_s * 0.30, -0.30, 1.36), (_s * 0.27, -0.52, 1.62)),
        f"Arm2_{_name}": ("Spine", (_s * 0.15, -0.10, 1.20), (_s * 0.15, -0.38, 1.22)),
        f"Thigh_{_name}": ("Hips", (_s * 0.14, HIP_Y, 0.88), (_s * 0.23, -0.12, 0.56)),
        f"Shin_{_name}": (f"Thigh_{_name}", (_s * 0.23, -0.12, 0.56), (_s * 0.20, HIP_Y, 0.16)),
        f"Foot_{_name}": (f"Shin_{_name}", (_s * 0.20, HIP_Y, 0.16), (_s * 0.20, -0.16, 0.025)),
    })


def joint(p, centre, radius):
    """A ball over a joint's pivot, in the joint colour: the two pieces swing inside it, so no wedge opens on the outside of the bend."""
    props_lib.ball(p, JOINT, centre, radius, n=6, rings=2)


def build_pieces():
    """The model as a Prop: the body and one moving part per bone (a part's origin lands on its pivot)."""
    p = Prop(NAME)
    p.box(BODY, (0, 0.08, 0.85), (0.30, 0.22, 0.16))                                   # the pelvis (Hips)

    with p.part("Spine", pivot=BONES["Spine"][1]):                                      # the thorax
        thorax = [(0.80, 0.10, 0.12, 0.11), (1.00, 0.05, 0.16, 0.14), (1.25, -0.02, 0.19, 0.16), (1.50, -0.07, 0.15, 0.12), (1.66, -0.10, 0.07, 0.06)]
        p.loft_rings(BODY, [common.ring_z(z, 0, cy, rx, ry, n=6) for z, cy, rx, ry in thorax])

    with p.part("Abdomen", pivot=BONES["Abdomen"][1]):                                  # carried out behind, drooping a little, tapering to a point
        segs = [(0.12, 0.97, 0.05, 0.05), (0.20, 0.97, 0.12, 0.13), (0.42, 0.93, 0.16, 0.16), (0.62, 0.88, 0.13, 0.13), (0.78, 0.83, 0.07, 0.07), (0.88, 0.80, 0.0001, 0.0001)]
        p.loft_rings(JOINT, [common.ring_y(y, 0, z, rx, rz, n=6) for y, z, rx, rz in segs])
        for i, y in enumerate((0.30, 0.46, 0.60)):                                      # its bands
            r = 0.17 - i * 0.025
            p.cyl(BODY, (0, y, 0.93 - i * 0.04), r, 0.035, n=6, axis="y")
        joint(p, (0, 0.14, 0.95), 0.075)                           # the joint where it meets the pelvis: it sways without opening a gap

    with p.part("Head", pivot=BONES["Head"][1]):
        # a broad triangular head, wide across the eyes and narrow at the mouth, on a ball at the neck's pivot
        head = [(1.62, -0.10, 0.07, 0.06), (1.70, -0.11, 0.08, 0.07), (1.78, -0.125, 0.10, 0.09), (1.86, -0.135, 0.095, 0.085), (1.94, -0.145, 0.055, 0.05), (1.98, -0.15, 0.03, 0.03)]
        p.loft_rings(BODY, [common.ring_z(z, 0, cy, rx, ry, n=6) for z, cy, rx, ry in head])
        joint(p, (0, -0.10, 1.65), 0.075)                          # the neck's pivot: the head turns on it
        for s in (-1, 1):
            props_lib.ball(p, EYE, (s * 0.108, -0.16, 1.855), 0.072, n=8, squash=1.25, rings=4)  # a compound eye, bulging out of the side of the head
            props_lib.ball(p, "black", (s * 0.122, -0.212, 1.862), 0.028, n=6, squash=1.3, rings=3)   # its dark centre, facing forward
            props_lib.rod(p, SPIKE, (s * 0.040, -0.170, 1.715), (s * 0.075, -0.235, 1.665), 0.034)    # a mandible: out, then in to meet its twin
            props_lib.rod(p, SPIKE, (s * 0.075, -0.235, 1.665), (s * 0.022, -0.268, 1.632), 0.026)
            props_lib.rod(p, JOINT, (s * 0.040, -0.16, 1.93), (s * 0.090, -0.24, 2.17), 0.022)
            props_lib.rod(p, JOINT, (s * 0.090, -0.24, 2.17), (s * 0.170, -0.20, 2.30), 0.016)
            props_lib.rod(p, JOINT, (s * 0.170, -0.20, 2.30), (s * 0.215, -0.13, 2.345), 0.011)
        p.box(JOINT, (0, -0.170, 1.69), (0.05, 0.046, 0.03))                             # the mouth between the mandibles, its back inside the face

    for s, side in ((1, "L"), (-1, "R")):
        with p.part(f"UpperArm_{side}", pivot=BONES[f"UpperArm_{side}"][1]):
            joint(p, (s * 0.19, -0.08, 1.50), 0.058)               # the shoulder joint
            props_lib.rod(p, BODY, (s * 0.19, -0.08, 1.50), (s * 0.30, -0.30, 1.36), 0.065)
        with p.part(f"Fore_{side}", pivot=BONES[f"Fore_{side}"][1]):
            joint(p, (s * 0.30, -0.30, 1.36), 0.050)               # the elbow
            props_lib.rod(p, BODY, (s * 0.30, -0.30, 1.36), (s * 0.27, -0.52, 1.62), 0.055)
            props_lib.rod(p, SPIKE, (s * 0.27, -0.52, 1.62), (s * 0.235, -0.585, 1.715), 0.032)   # the grasping claw at its end
            for k in range(3):                                                           # a row of spikes along the forearm
                t = 0.3 + 0.25 * k
                props_lib.rod(p, SPIKE, (s * 0.30 + (s * 0.27 - s * 0.30) * t, -0.30 - 0.22 * t, 1.36 + 0.26 * t),
                              (s * 0.20, -0.33 - 0.22 * t, 1.40 + 0.26 * t), 0.015)
        with p.part(f"Arm2_{side}", pivot=BONES[f"Arm2_{side}"][1]):                      # the small second pair
            joint(p, (s * 0.15, -0.10, 1.20), 0.042)
            props_lib.rod(p, JOINT, (s * 0.15, -0.10, 1.20), (s * 0.20, -0.26, 1.08), 0.035)
            props_lib.rod(p, JOINT, (s * 0.20, -0.26, 1.08), (s * 0.15, -0.38, 1.22), 0.03)
        with p.part(f"Thigh_{side}", pivot=BONES[f"Thigh_{side}"][1]):
            joint(p, (s * 0.14, HIP_Y, 0.88), 0.068)                 # the hip: the thigh swings inside it
            props_lib.rod(p, BODY, (s * 0.14, HIP_Y, 0.88), (s * 0.23, -0.12, 0.56), 0.085)
        with p.part(f"Shin_{side}", pivot=BONES[f"Shin_{side}"][1]):
            joint(p, (s * 0.23, -0.12, 0.56), 0.058)                 # the knee
            props_lib.rod(p, BODY, (s * 0.23, -0.12, 0.56), (s * 0.20, HIP_Y, 0.16), 0.065)
        with p.part(f"Foot_{side}", pivot=BONES[f"Foot_{side}"][1]):
            joint(p, (s * 0.20, HIP_Y, 0.16), 0.046)                 # the ankle
            props_lib.rod(p, JOINT, (s * 0.20, HIP_Y, 0.16), (s * 0.20, -0.04, 0.025), 0.045)   # the foot bone runs on to y = -0.16; the pad is shorter than the bone
            p.box(JOINT, (s * 0.20, -0.06, 0.02), (0.07, 0.10, 0.04))
    return p


def build_armature(coll):
    arm = bpy.data.armatures.new(f"{NAME}_Rig")
    rig = bpy.data.objects.new(f"{NAME}_Rig", arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}
    for name, (parent, head, tail) in BONES.items():                                    # parents come first in the table
        eb = arm.edit_bones.new(name)
        eb.head, eb.tail = Vector(head), Vector(tail)
        if parent:
            eb.parent = made[parent]
            eb.use_connect = False
        made[name] = eb
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in arm.bones:
        b.use_deform = True                                                              # Root too: Unity wants one skeleton under one root
    return rig


# ----------------------------------------------------------------------------------------------------------------------
# The clips
# ----------------------------------------------------------------------------------------------------------------------

def turn(rig, name, x=0.0, y=0.0, z=0.0, shift=(0.0, 0.0, 0.0)):
    """Turn a pose bone about the armature's axes through its own head; its children follow (parents first)."""
    pb = rig.pose.bones[name]
    head = pb.head.copy()
    t = Matrix.Translation(head)
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


REST_LOW = 0.0


def lowest_foot(rig):
    low = 1e9
    for side in ("L", "R"):
        pb = rig.pose.bones[f"Foot_{side}"]
        low = min(low, pb.head.z, pb.tail.z)
    return low


def ground(rig):
    """Move Hips so the lowest foot stays where it is at rest: no sinking, no floating."""
    turn(rig, "Hips", shift=(0.0, 0.0, REST_LOW - lowest_foot(rig)))


def idle(rig, t):
    """Standing: a slow breath, the head turning, the abdomen swaying, the fore-arms and second pair twitching."""
    w = 2 * math.pi * t
    breath = math.sin(2 * w)
    turn(rig, "Hips", z=1.0 * math.sin(w))
    turn(rig, "Spine", x=1.2 * breath, z=-1.5 * math.sin(w))
    turn(rig, "Head", x=2.5 * math.sin(w - 0.9), z=7.0 * math.sin(w - 0.4) + 4.0 * math.sin(3 * w))
    turn(rig, "Abdomen", x=3.0 * math.sin(w - 0.6) + 1.0 * breath, z=6.0 * math.sin(w))
    for side, sgn in (("L", 1), ("R", -1)):
        turn(rig, f"UpperArm_{side}", x=2.0 * math.sin(w + sgn))
        turn(rig, f"Fore_{side}", x=4.0 * math.sin(2 * w + sgn) - 2.0)
        turn(rig, f"Arm2_{side}", x=6.0 * math.sin(3 * w + 2 * sgn), z=sgn * 4.0 * math.sin(w))
    ground(rig)


def carry(rig, t):
    """Carrying: the grasping fore-arms come forward and in, the spiked forearms meeting in front of the thorax like a cradle, the second pair
    held in against the chest. Played on a layer over the walk that moves only the arms and the thorax (the legs and abdomen keep walking)."""
    w = 2 * math.pi * t
    breath = math.sin(2 * w)
    turn(rig, "Spine", x=-2.0 + 1.2 * breath)
    turn(rig, "Head", x=1.0)
    for side, sgn in (("L", 1), ("R", -1)):
        turn(rig, f"UpperArm_{side}", x=CARRY_UPPER[0], z=-sgn * CARRY_UPPER[1])
        turn(rig, f"Fore_{side}", x=CARRY_FORE[0], z=-sgn * CARRY_FORE[1])
        turn(rig, f"Arm2_{side}", x=-10.0 + 3.0 * breath, z=-sgn * 25.0)
    ground(rig)


CARRY_UPPER = (-10.0, 5.0)   # degrees: about X (negative lifts it forward; the forearm rests pointing forward and up, +45 brings it level), about the vertical axis (in towards the middle)
CARRY_FORE = (45.0, 5.0)


def gait(rig, t, thigh, knee, lean, abdomen, arms, hop):
    """One stride of both legs per loop. The leg that is forward has a bent knee; the abdomen counterweights (it rises as the body leans)."""
    w = 2 * math.pi * t
    turn(rig, "Hips", z=-4.0 * math.sin(w))
    turn(rig, "Spine", x=lean, z=5.0 * math.sin(w))
    turn(rig, "Head", x=-lean * 0.7, z=-5.0 * math.sin(w))
    turn(rig, "Abdomen", x=-abdomen * (0.5 + 0.5 * math.cos(2 * w)) + 4.0, z=7.0 * math.sin(w))
    for side, sgn, phase in (("L", 1, 0.0), ("R", -1, math.pi)):
        psi = w + phase
        swing = -thigh * math.sin(psi)                                                   # forward is negative x
        bend = knee * (0.5 + 0.5 * math.cos(psi + 0.4))
        turn(rig, f"Thigh_{side}", x=swing)
        turn(rig, f"Shin_{side}", x=bend * 0.6)                                           # +x folds this leg's knee (the knee points forward, the ankle back)
        turn(rig, f"Foot_{side}", x=-(swing + bend * 0.6) * 0.7)
        turn(rig, f"UpperArm_{side}", x=-arms * math.sin(psi) * 0.4 - 6.0)                # the folded fore-arms rock a little against the legs
        turn(rig, f"Fore_{side}", x=-arms * 0.6 * math.sin(psi + 0.5))
        turn(rig, f"Arm2_{side}", x=arms * math.sin(psi + math.pi) * 0.8)
    ground(rig)


def walk(rig, t):
    gait(rig, t, thigh=30.0, knee=45.0, lean=4.0, abdomen=7.0, arms=16.0, hop=0.0)


def run(rig, t):
    gait(rig, t, thigh=52.0, knee=85.0, lean=14.0, abdomen=14.0, arms=34.0, hop=0.0)


CLIPS = (("Idle", idle, 96), ("Walk", walk, 24), ("Run", run, 16), ("Carry", carry, 96))


def key_clip(rig, name, pose, frames):
    """One looping action (frame frames+1 equals frame 1) keyed on every bone."""
    action = bpy.data.actions.new(name)
    rig.animation_data_create()
    rig.animation_data.action = action
    sc = bpy.context.scene
    sc.render.fps = 24
    sc.frame_start, sc.frame_end = 1, frames + 1
    for frame in range(1, frames + 2):
        reset(rig)
        pose(rig, ((frame - 1) % frames) / frames)
        for pb in rig.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            if pb.name == "Hips":
                pb.keyframe_insert("location", frame=frame)
    return action


def build_all():
    global REST_LOW
    # the loop removes from the live collection, so it iterates a copy; a second run in one session must not export the first run's clips too
    for stale in list(bpy.data.actions):  # NOSONAR
        curves = stale.fcurves if hasattr(stale, "fcurves") else [fc for layer in stale.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]   # Blender 5 keeps them in layers
        bones = {fc.data_path.split('"')[1] for fc in curves if fc.data_path.startswith("pose.bones[")}
        if bones and bones <= set(BONES):                                                # only the Insectoid's own: the Blender file may hold other models' clips
            bpy.data.actions.remove(stale)
    for name, _, _ in CLIPS:                                                             # a clip's name must come out exactly (Unity keys its settings and the Animator by it)
        if bpy.data.actions.get(name) is not None:
            raise RuntimeError(f"the Blender file has an action called {name} that is not the Insectoid's: rename or delete it first, or the clip would be exported as {name}.001")
    prop = build_pieces()
    obj, coll = prop.finish()                                                            # the pelvis, with the pieces parented to it
    rig = build_armature(coll)
    bpy.context.view_layer.update()

    # one mesh: bake each piece into world space, name its vertices' group for its bone, join
    pieces = [o for o in coll.objects if o.type == "MESH" and o.parent is obj]
    mesh_objs = [obj] + pieces
    for o in pieces:
        o.data.transform(o.matrix_world)
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
    obj.parent = None
    for o in mesh_objs:
        bone = "Hips" if o is obj else o.name
        g = o.vertex_groups.new(name=bone)
        g.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    joined = common.join(mesh_objs, NAME)
    for bone in BONES:                                                                   # a group for every bone, even one with no piece
        if bone not in joined.vertex_groups:
            joined.vertex_groups.new(name=bone)
    joined.parent = rig
    mod = joined.modifiers.new("Armature", "ARMATURE")
    mod.object = rig

    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    reset(rig)
    REST_LOW = lowest_foot(rig)
    for name, pose, frames in CLIPS:
        key_clip(rig, name, pose, frames)
    bpy.context.scene.frame_set(1)
    bpy.ops.object.mode_set(mode="OBJECT")
    return joined, rig, coll


def export(coll, rig):
    out = common.out_dir() / "Assets" / "Art" / "Global" / "Aliens" / f"{NAME}.fbx"
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.export_scene.fbx(
        filepath=str(out), collection=coll.name, object_types={"MESH", "ARMATURE"},
        use_mesh_modifiers=False, mesh_smooth_type="FACE", axis_forward="-Z", axis_up="Y", global_scale=1.0,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, add_leaf_bones=False,
        use_armature_deform_only=False, primary_bone_axis="Y", secondary_bone_axis="X",
        bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
        bake_anim_step=1.0, bake_anim_simplify_factor=0.0, path_mode="AUTO", embed_textures=False)
    return out


if __name__ == "__main__":
    mesh, rig, coll = build_all()
    print(common.stats(mesh))
    print("exported", export(coll, rig))
