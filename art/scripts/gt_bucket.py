"""GT-03 Bucket (remake of the MarpaStudio bucket): galvanised pail with a wire handle.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/gt_bucket.py", run_name="__main__")
Exports Assets/Art/Global/Props/GT_Bucket_01.fbx. About 12 x 2 sides, ~200 tris.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib
import common
importlib.reload(common)

NAME = "GT_Bucket_01"
SIDES = 12
HEIGHT = 0.30
BOTTOM_R = 0.105
TOP_R = 0.140
WALL = 0.010
BASE = 0.015           # floor thickness
HANDLE_R = 0.012       # tube radius of the wire handle
HANDLE_RISE = 0.13     # how far the handle arcs above the rim

common.setup_scene()
coll = common.fresh_collection(NAME)


def body():
    """Open-topped tapered pail: a revolved profile, outer wall, rim, inner wall, floor."""
    bm = bmesh.new()
    profile = [
        (0.0, 0.0),
        (BOTTOM_R, 0.0),
        (TOP_R, HEIGHT),
        (TOP_R - WALL, HEIGHT),
        (BOTTOM_R - WALL, BASE),
        (0.0, BASE),
    ]
    verts = [bm.verts.new((r, 0.0, z)) for r, z in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=math.tau, steps=SIDES, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return common.new_mesh_object(NAME + "_Body", bm, coll, "metal_galv")


def handle():
    """Bail handle: a half-ellipse of wire hooked into the rim at +-X, 4-sided tube."""
    bm = bmesh.new()
    segs = 8
    path = []
    for i in range(segs + 1):
        a = math.pi * i / segs
        path.append(Vector((math.cos(a) * (TOP_R + 0.004), 0.0, HEIGHT - 0.01 + math.sin(a) * HANDLE_RISE)))
    rings = []
    for i, p in enumerate(path):
        tangent = (path[min(i + 1, segs)] - path[max(i - 1, 0)]).normalized()
        side = Vector((0, 1, 0))                    # the arc lies in XZ, so Y is always across it
        up = tangent.cross(side).normalized()
        ring = []
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            ring.append(bm.verts.new(p + side * (math.cos(a) * HANDLE_R) + up * (math.sin(a) * HANDLE_R)))
        rings.append(ring)
    for i in range(segs):
        for k in range(4):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return common.new_mesh_object(NAME + "_Handle", bm, coll, "metal_dark")


pail = body()
bail = handle()
bucket = common.join([pail, bail], NAME)
bucket.location = (0, 0, 0)

print(common.stats(bucket))
out = common.export_fbx(coll, "Assets/Art/Global/Props/" + NAME + ".fbx")
print("exported", out)
