"""Quadruped idle loop for the shared rig (quadruped_rig.py): a standing animal, breathing and fidgeting.

Run in Blender after the animal is built (gn_animals.py), with RIG_NAME and ANIM_PREFIX passed via init_globals (gn_animal_clips.py does this):
    import runpy; runpy.run_path(r"<repo>/art/scripts/quadruped_idle.py", run_name="__main__")
Creates "Quadruped_Idle" (frames 1-97, frame 97 = frame 1, 24 fps, a 4 second loop) and exports
Assets/Art/Global/Animals/Anims/<ANIM_PREFIX>@Idle.fbx (Unity names the clip "Idle" from the @).

Everything is periodic over the loop: two breaths, a slow head sway, a weight shift side to side, a chew
under the head nod, a tail swish with one flick, and one quick flick of each ear at different times.
The legs stay planted at the rest pose so the idle blends with the walk's start and end poses.
"""

import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib
import common
import quadruped_rig
importlib.reload(common)
importlib.reload(quadruped_rig)

RIG_NAME = globals().get("RIG_NAME", "GN_Cow_Rig")
ACTION = "Quadruped_Idle"
LOOP_FRAMES = 96

rig = bpy.data.objects[RIG_NAME]
rig.hide_viewport = False                       # pose mode needs a visible rig
rig.hide_set(False)
ANIM_PREFIX = globals().get("ANIM_PREFIX", "Quadruped")
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="POSE")
quadruped_rig.rest_pose(rig)
for stale in [a for a in bpy.data.actions if a.name == ACTION or a.name.startswith(ACTION + ".")]:
    bpy.data.actions.remove(stale)                              # only this clip's own action: the Blender file may be shared with other work
rig.animation_data_create()
rig.animation_data.action = bpy.data.actions.new(ACTION)
bpy.context.scene.render.fps = 24
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = LOOP_FRAMES + 1
R = lambda name, **kw: quadruped_rig.set_rot(rig, name, **kw)


def bump(t, t0, width=0.03):
    """A smooth pulse centred on t0 that wraps around the loop."""
    d = (t - t0 + 0.5) % 1.0 - 0.5
    return math.exp(-(d * d) / (2 * width * width))


KEYED = [b.name for b in rig.pose.bones if b.name != "Root"]
for frame in range(1, LOOP_FRAMES + 2):
    t = ((frame - 1) % LOOP_FRAMES) / LOOP_FRAMES
    w = 2 * math.pi * t
    breath = math.sin(2 * w)                                   # two breaths per loop
    R("Hips", y=0.8 * math.sin(w), x=0.3 * breath)
    R("Spine", x=-0.6 * breath, y=-0.5 * math.sin(w))
    R("Chest", x=1.0 * breath)
    R("Neck1", x=1.0 * math.sin(2 * w - 0.6), z=3.0 * math.sin(w))
    R("Neck2", x=1.5 * math.sin(w - 0.8), z=2.0 * math.sin(w - 0.5))
    R("Head", x=2.0 * math.sin(w - 1.2) + 1.0 * math.sin(4 * w), z=2.0 * math.sin(w - 1.0))
    flick_l = bump(t, 0.28) * math.sin(2 * math.pi * 12 * ((t - 0.28 + 0.5) % 1.0 - 0.5))
    flick_r = bump(t, 0.74) * math.sin(2 * math.pi * 12 * ((t - 0.74 + 0.5) % 1.0 - 0.5))
    R("Ear_L", z=3.0 * math.sin(w + 0.5) + 20.0 * flick_l, x=6.0 * bump(t, 0.28, 0.05))
    R("Ear_R", z=-3.0 * math.sin(w + 2.0) - 20.0 * flick_r, x=6.0 * bump(t, 0.74, 0.05))
    tail_flick = bump(t, 0.55, 0.05)
    R("Tail1", z=7.0 * math.sin(w - 0.5) + 14.0 * tail_flick, x=2.0 * math.sin(2 * w))
    R("Tail2", z=9.0 * math.sin(w - 1.2) + 16.0 * bump(t, 0.58, 0.05))
    R("Tail3", z=11.0 * math.sin(w - 1.9) + 18.0 * bump(t, 0.61, 0.05))
    bpy.context.view_layer.update()
    for name in KEYED:
        rig.pose.bones[name].keyframe_insert("rotation_euler", frame=frame)

bpy.context.scene.frame_set(1)
bpy.ops.object.mode_set(mode="OBJECT")
if globals().get("EXPORT", True):                              # EXPORT=False: build only, write nothing (gn_animal_clips.py passes it on)
    out = common.export_anim_fbx(rig, f"Assets/Art/Global/Animals/Anims/{ANIM_PREFIX}@Idle.fbx", only_active=True)
    print("exported", out)

# leave the shared file as found: the rig at rest, the clip's action not left behind for the next export
quadruped_rig.rest_pose(rig)
action = rig.animation_data.action
rig.animation_data.action = None
bpy.data.actions.remove(action)
