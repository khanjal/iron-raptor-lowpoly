"""Idle, sit, walk, run and carry clips for the people, on the shared humanoid rig (humanoid_rig.py, the Universal Animation Library skeleton).

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/gp_clips.py", run_name="__main__")
Writes Assets/Art/Global/People/Anims/GP_Humanoid@Idle.fbx, @Sit.fbx, @Walk.fbx, @Run.fbx, @Carry.fbx and @CarryOne.fbx (Unity names the clips Idle, Sit, Walk, Run, Carry and
CarryOne from the @). Walk and Run are in place: the game moves the player and the Animator's Speed blends the loops. Play them with Apply Root Motion off
(ArtImportRules bakes the root's height, position and turn into the pose, so the hip bob and the few degrees of yaw stay in the animation). The clips are
Humanoid muscle clips once imported, so they play on every person and humanoid alien, not only the rig they were made on.

Each pose ends with ground(): the pelvis is moved so the lowest foot is where it is at rest, so the feet are on the floor in every frame (and the
hips are as high as the legs make them).

Why these exist: the people are exported in the rig's T-pose, and the Universal Animation Library's own clips are a separate download
that is not in the repo. A person standing in the world needs a relaxed pose, so these are a few hand-made loops of the poses
the farm needs: a standing idle (arms down, breathing, a slow weight shift) and a seated one (thighs forward, hands in the lap).

How the poses are made: the rig faces -Y, +X is its left, Z is up. A bone is turned about a world axis through its own head
(turn), parents first, and the pose is keyed on every bone each frame, so a clip is a function of the loop time.
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib
import common
import humanoid_rig
import quadruped_rig
for _m in (common, humanoid_rig, quadruped_rig):
    importlib.reload(_m)

FPS = 24
LOOP_FRAMES = 96                                   # a 4 second loop


def turn(rig, name, x=0.0, y=0.0, z=0.0, shift=(0.0, 0.0, 0.0)):
    """Turn the named bone by (x, y, z) degrees about the armature's axes, through the bone's current head; its children follow."""
    pb = rig.pose.bones[name]
    head = pb.head.copy()
    t = Matrix.Translation(head)
    r = Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ").to_matrix().to_4x4()
    m = t @ r @ t.inverted() @ pb.matrix
    m.translation += Vector(shift)
    pb.matrix = m
    bpy.context.view_layer.update()


def reset(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)                       # turn() sets the matrix, which leaves a little scale behind; without this it adds up over a loop
    bpy.context.view_layer.update()


FEET = ("foot_l", "foot_r", "ball_l", "ball_r", "ball_leaf_l", "ball_leaf_r")
REST_LOW = 0.0                                     # the lowest foot point at rest, set by make_clip


def lowest_foot(rig):
    """The lowest point of the feet (bone heads and tails) in armature space."""
    low = 1e9
    for name in FEET:
        pb = rig.pose.bones.get(name)
        if pb is not None:
            low = min(low, pb.head.z, pb.tail.z)
    return low


def ground(rig):
    """Move the pelvis (and everything on it) so the lowest foot is where it is at rest: the feet neither sink into the floor nor float."""
    turn(rig, "pelvis", shift=(0.0, 0.0, REST_LOW - lowest_foot(rig)))


def arm(rig, side, sgn, down, swing=0.0, bend=0.0, twist=0.0):
    """An arm hanging `down` degrees from the T-pose, then swung forward (negative `swing`) or back about the world X axis (two turns: the swing
    after the lowering, so it is a swing and not a twist along the arm), the elbow bent by `bend` (forward is negative), turned in by `twist`."""
    turn(rig, f"upperarm_{side}", y=sgn * down)
    turn(rig, f"upperarm_{side}", x=swing)
    turn(rig, f"lowerarm_{side}", x=bend, z=twist)
    turn(rig, f"hand_{side}", x=-6)


def standing(rig, t):
    """Relaxed standing: arms hanging with a bend at the elbow, a breath and a slow shift of weight."""
    w = 2 * math.pi * t
    breath = math.sin(2 * w)                       # two breaths per loop
    sway = math.sin(w)
    turn(rig, "pelvis", z=1.5 * sway, shift=(0.012 * sway, 0, 0))
    turn(rig, "spine_01", x=0.6 * breath, z=-0.8 * sway)
    turn(rig, "spine_02", x=0.9 * breath)
    turn(rig, "spine_03", x=1.2 * breath, z=-0.7 * sway)
    turn(rig, "Head", x=1.5 * math.sin(w - 0.8), z=3.0 * math.sin(w - 0.4))
    for side, sgn in (("l", 1), ("r", -1)):
        turn(rig, f"clavicle_{side}", y=sgn * 2.5 * breath)
        arm(rig, side, sgn, 72 + 1.5 * breath, swing=-4 + 2 * sway * sgn, bend=-14 + 2 * breath)
    ground(rig)


def seated(rig, t):
    """Sitting upright: thighs forward, shins down, hands in the lap, a breath; the hips are lowered until the feet are on the floor."""
    w = 2 * math.pi * t
    breath = math.sin(2 * w)
    sway = math.sin(w)
    turn(rig, "pelvis", z=0.8 * sway, shift=(0, 0.04, -0.4))
    for side in ("l", "r"):
        turn(rig, f"thigh_{side}", x=-86)
        turn(rig, f"calf_{side}", x=88)
        turn(rig, f"foot_{side}", x=-2)
    turn(rig, "spine_01", x=0.5 * breath)
    turn(rig, "spine_02", x=1.0 * breath)
    turn(rig, "spine_03", x=1.4 * breath, z=-0.6 * sway)
    turn(rig, "Head", x=2.0 * math.sin(w - 0.8), z=4.0 * math.sin(w - 0.4))
    for side, sgn in (("l", 1), ("r", -1)):
        turn(rig, f"clavicle_{side}", y=sgn * 2.0 * breath)
        arm(rig, side, sgn, 66, swing=-10, bend=-72 + 2 * breath, twist=-sgn * 14)   # the forearms turn in towards the lap
    ground(rig)


def carrying(rig, t):
    """Carrying something in both hands: the upper arms forward and tucked in, the forearms pointing forward so the hands meet in front of the
    chest (about 0.4 m ahead of it, 0.2 m apart), the spine leaning back a little. Played on an arms-and-spine layer over the walk, then the game
    moves the hands onto the item's grips (Animator IK), so this is the pose the hands start from and the elbows keep."""
    w = 2 * math.pi * t
    breath = math.sin(2 * w)
    turn(rig, "spine_01", x=-1.0 + 0.6 * breath)
    turn(rig, "spine_02", x=-1.5 + 0.9 * breath)
    turn(rig, "spine_03", x=-1.5 + 1.2 * breath)
    for side, sgn in (("l", 1), ("r", -1)):
        turn(rig, f"clavicle_{side}", y=sgn * 2.5 * breath)
        arm(rig, side, sgn, 62 + 1.5 * breath, swing=-40, bend=-70)
        turn(rig, f"upperarm_{side}", z=-sgn * 35)      # in towards the middle (about the vertical axis, after the swing)
    ground(rig)


def carrying_one(rig, t):
    """Carrying something in the right hand: the right arm bent, the hand low at the hip, the left arm hanging as in the idle."""
    w = 2 * math.pi * t
    breath = math.sin(2 * w)
    sway = math.sin(w)
    turn(rig, "spine_01", x=0.6 * breath)
    turn(rig, "spine_02", x=0.9 * breath)
    turn(rig, "spine_03", x=1.2 * breath, z=3.0)           # a little weight against the load
    turn(rig, "clavicle_l", y=2.5 * breath)
    arm(rig, "l", 1, 72 + 1.5 * breath, swing=-4 + 2 * sway, bend=-14 + 2 * breath)
    turn(rig, "clavicle_r", y=-2.5 * breath)
    arm(rig, "r", -1, 70, swing=-10, bend=-75)
    ground(rig)


def gait(rig, t, A, K, arm_swing, elbow, lean, yaw):
    """A walking or running cycle (one full stride of both legs per loop): A is the thigh swing in degrees each way, K the knee bend,
    arm_swing the arm swing, elbow the elbow bend, lean the forward lean of the spine, yaw the hip twist. The hips rise and fall by
    themselves: ground() keeps the lowest foot on the floor."""
    w = 2 * math.pi * t
    turn(rig, "pelvis", z=-yaw * math.sin(w))                      # the hips turn with the leading leg ...
    turn(rig, "spine_01", x=lean * 0.4, z=yaw * 0.9 * math.sin(w))   # ... and the shoulders against it
    turn(rig, "spine_02", x=lean * 0.3, z=yaw * 0.7 * math.sin(w))
    turn(rig, "spine_03", x=lean * 0.3, z=yaw * 0.6 * math.sin(w))
    turn(rig, "Head", x=-lean * 0.8, z=-yaw * 0.5 * math.sin(w))
    for side, sgn, phase in (("l", 1, 0.0), ("r", -1, math.pi)):
        psi = w + phase
        thigh = -A * math.sin(psi)                                    # forward is negative x
        knee = K * max(0.0, math.cos(psi + 0.8)) ** 2                 # straight from heel strike to mid-stance, bending from there through the swing (a wide bend
                                                                      # lifted the foot long before the thigh was forward and the planted foot slid on the floor)
        turn(rig, f"thigh_{side}", x=thigh)
        turn(rig, f"calf_{side}", x=knee)
        turn(rig, f"foot_{side}", x=-(thigh + knee) * 0.55)
        turn(rig, f"clavicle_{side}", y=sgn * 2)
        swing = arm_swing * math.sin(psi)                             # the arm goes forward (negative x) as the OPPOSITE leg does
        arm(rig, side, sgn, 72, swing=swing, bend=elbow - abs(swing) * 0.3)
    ground(rig)


def walking(rig, t):
    gait(rig, t, A=26, K=50, arm_swing=24, elbow=-22, lean=2, yaw=4)


def running(rig, t):
    gait(rig, t, A=50, K=100, arm_swing=50, elbow=-85, lean=10, yaw=7)


CLIPS = {"Idle": (standing, 96), "Sit": (seated, 96), "Walk": (walking, 24), "Run": (running, 16),
         "Carry": (carrying, 96), "CarryOne": (carrying_one, 96)}   # the pose, and the frames in the loop


def tidy(rig):
    """Remove the rig, its data, its collection and the actions, so repeated runs do not pile up orphans (GP_Humanoid_Rig.001 ...)."""
    coll = rig.users_collection[0] if rig.users_collection else None
    data = rig.data
    bpy.data.objects.remove(rig, do_unlink=True)
    if data is not None and data.users == 0:
        bpy.data.armatures.remove(data)
    if coll is not None and coll.name == "GP_Humanoid_Clips":
        bpy.data.collections.remove(coll)
    # the loop removes from the live collection, so it iterates a copy
    for action in list(bpy.data.actions):  # NOSONAR
        bpy.data.actions.remove(action)


def make_clip(name, pose, loop_frames=LOOP_FRAMES, keep=False):
    """Build the rig, key the loop, export it. keep=True leaves the rig and the action in the file (to look at them)."""
    global REST_LOW
    coll = common.fresh_collection("GP_Humanoid_Clips")
    rig = humanoid_rig.build("GP_Humanoid_Rig", coll)
    rig.hide_viewport = False
    rig.hide_set(False)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    reset(rig)
    REST_LOW = lowest_foot(rig)
    quadruped_rig.fresh_action(rig, name)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, loop_frames + 1
    for frame in range(1, loop_frames + 2):
        reset(rig)
        pose(rig, ((frame - 1) % loop_frames) / loop_frames)
        for pb in rig.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            if pb.name == "pelvis":
                pb.keyframe_insert("location", frame=frame)
    bpy.context.scene.frame_set(1)
    bpy.ops.object.mode_set(mode="OBJECT")
    out = common.export_anim_fbx(rig, f"Assets/Art/Global/People/Anims/GP_Humanoid@{name}.fbx")
    print("exported", out)
    if keep:
        return rig
    tidy(rig)
    return None


if __name__ == "__main__":
    for clip, (fn, frames) in CLIPS.items():
        make_clip(clip, fn, frames)
    print("clips done", list(CLIPS))
