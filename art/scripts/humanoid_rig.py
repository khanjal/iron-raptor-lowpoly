"""The shared humanoid rig: the 65-bone skeleton of Quaternius's Universal Animation Library (CC0).

The bone names, hierarchy, positions and rolls are stored in art/data/ual_skeleton.json (read once from the
library's FBX), so this rig can be rebuilt without the download. Because every bone matches the library, its
clips (idle, walk, jog, sprint, crouch, sit, drive, push, interact...) play on any mesh skinned to this rig, in
Blender or through Unity's Humanoid retargeting.

Coordinates are the armature's local space: the character faces -Y, +X is its left (_l), Z is up, feet on z = 0,
about 1.83 m tall, arms out in a T-pose. Use weights() and bind() from quadruped_rig.py to skin a mesh to it.
"""

import json

import bpy
from mathutils import Vector

import common

DATA = common.REPO / "art" / "data" / "ual_skeleton.json"


def build(rig_name, collection):
    """Create the armature object in collection from the stored skeleton; returns it."""
    spec = json.loads(DATA.read_text())["bones"]
    old = bpy.data.objects.get(rig_name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    arm = bpy.data.armatures.new(rig_name)
    obj = bpy.data.objects.new(rig_name, arm)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}
    for b in spec:                                              # parents always precede children in the file
        eb = arm.edit_bones.new(b["name"])
        eb.head, eb.tail = Vector(b["head"]), Vector(b["tail"])
        eb.roll = b["roll"]
        made[b["name"]] = eb
    for b in spec:
        if b["parent"]:
            made[b["name"]].parent = made[b["parent"]]
            made[b["name"]].use_connect = False                 # keep the stored heads exactly
    bpy.ops.object.mode_set(mode="OBJECT")
    for bone in arm.bones:
        bone.use_deform = bone.name != "root"
    arm.display_type = "OCTAHEDRAL"
    return obj
