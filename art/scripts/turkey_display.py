"""The tom turkey's display: the folded tail (the feathers lying close together behind him) rises, opens into an upright fan, quivers, and folds back down.

Run in Blender after the tom is built (gn_birds.py with SPECIES_LIST = ["turkey_tom"], which builds GN_TurkeyTom_faceted_Rig):
    import runpy; runpy.run_path(r"<repo>/art/scripts/turkey_display.py", run_name="__main__")
Creates the action "Display" (frames 1-73, 24 fps, about 3 seconds; not a loop: it starts and ends in the rest pose, the tail flat behind him) and exports
Assets/Art/Global/Animals/Anims/TurkeyTom_faceted@Display.fbx (Unity names the clip Display from the @).

Every tail feather has its own bone, a child of Tail1 (biped_bird.feather_specs): rotating Tail1 about its own X axis by +80 degrees stands the tail up (a
negative angle would push it into the ground) and rotating each feather bone about its own Z axis by -k * (open - rest) degrees (k = -5..5 across the tail, from -X, the bird's right, to +X, its left; rest 3, open 13 degrees apart) opens the feathers into the fan. A tip of the head and a quiver sell it. A script (the
behaviour, #91) plays it when the tom struts: the model's rest pose is the folded tail down.
"""

import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib
import common
import quadruped_rig
import biped_bird
importlib.reload(common)
importlib.reload(quadruped_rig)
importlib.reload(biped_bird)

RIG_NAME = globals().get("RIG_NAME", "GN_TurkeyTom_faceted_Rig")
ACTION = "Display"
FRAMES = 73
RISE, FALL = 14, 58                                   # the fan is up from frame RISE to frame FALL

rig = bpy.data.objects[RIG_NAME]
rig.hide_viewport = False
rig.hide_set(False)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="POSE")
quadruped_rig.rest_pose(rig)
quadruped_rig.fresh_action(rig, ACTION)
bpy.context.scene.render.fps = 24
bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, FRAMES


def ease(x):
    """0..1, slow at both ends."""
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


KEYED = [b.name for b in rig.pose.bones if b.name != "Root"]
for frame in range(1, FRAMES + 1):
    quadruped_rig.rest_pose(rig)
    up = ease(frame / RISE) if frame <= RISE else (1.0 if frame <= FALL else ease(1 - (frame - FALL) / (FRAMES - FALL)))
    t = (frame - RISE) / 24.0
    shake = math.sin(t * 2 * math.pi * 5.0) * 1.6 * up if RISE < frame < FALL else 0.0     # a quiver while the fan is up
    quadruped_rig.set_rot(rig, "Tail1", x=80.0 * up + shake)
    quadruped_rig.set_rot(rig, "Tail2", x=-4.0 * up)
    fan = biped_bird.TURKEY_TOM["tail_fan"]
    for spec in biped_bird.feather_specs(biped_bird.TURKEY_TOM):                          # open the feathers: each turns about its own Z axis
        quadruped_rig.set_rot(rig, spec["bone"], z=-spec["k"] * (fan["open"] - fan["rest"]) * up)
    quadruped_rig.set_rot(rig, "Neck1", x=-6.0 * up)                                       # the head tips back a little
    quadruped_rig.set_rot(rig, "Neck2", x=8.0 * up)
    for name in KEYED:
        bpy.data.objects[RIG_NAME].pose.bones[name].keyframe_insert("rotation_euler", frame=frame)
bpy.context.scene.frame_set(1)
bpy.ops.object.mode_set(mode="OBJECT")
out = common.export_anim_fbx(rig, "Assets/Art/Global/Animals/Anims/TurkeyTom_faceted@Display.fbx")
print("exported", out)
