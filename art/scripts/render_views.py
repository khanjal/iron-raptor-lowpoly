"""Render models from the standard views, to compare them with their references (tools/compare_sheet.py puts the images side by side).

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/render_views.py",
                     init_globals={"TARGETS": ["GN_CatTabby_faceted"], "OUT": r"<repo>/out/compare/cat"}, run_name="__main__")

TARGETS  object names to render (each with its children), one set of images each; a reference can be one of them (an imported model, looked at,
         never committed: see asset-brief step 3)
OUT      folder for the images (default <repo>/out/compare, which git ignores); the files are <target>_<view>[_head].png
VIEWS    names from VIEW_DIRS (default all of them)
HEAD     True frames the head end of each target (the top of its front half) instead of the whole of it
SIZE     the images' side in pixels (default 512)

Every target is drawn the same way, so the sheets compare shapes, not lighting: Workbench, flat studio light, the palette texture (a reference
without one is plain grey), from a temporary camera on the same direction and with the same lens. The scene's camera, render engine, resolution,
output path and every object's render visibility are put back afterwards.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]

# the direction from the model to the camera: "thumb" is the site's thumbnail angle (front-left, from a little above), the rest the usual checks
VIEW_DIRS = {
    "thumb": (-0.45, -1.0, 0.40),
    "front": (0.0, -1.0, 0.10),
    "side": (-1.0, 0.0, 0.05),
    "three_quarter_r": (0.60, -1.0, 0.30),
}
LENS = 85.0           # mm: a long lens, so the views are close to the flat look of a product shot
HEAD_SHARE = 0.45     # HEAD=True: the head end is the top HEAD_SHARE of the model's height, in front of its middle


def _points(obj):
    """World-space vertices of obj and its mesh children as they are drawn: the evaluated mesh, after its modifiers (a rigged model's armature
    moves its vertices away from where its own data has them, and framing those left the picture empty)."""
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in [obj] + list(obj.children_recursive):
        if o.type == "MESH":
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            pts += [ev.matrix_world @ v.co for v in me.vertices]
            ev.to_mesh_clear()
    return pts


def _frame(pts, head):
    """(centre, radius) of the points to fit in the picture: all of them, or the head end."""
    if head:
        zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
        cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
        pts = [p for p in pts if p.z > zmax - HEAD_SHARE * (zmax - zmin) and p.y < cy] or pts
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centre = (lo + hi) / 2
    return centre, max((p - centre).length for p in pts)


def _family(obj):
    return {obj.name} | {o.name for o in obj.children_recursive}


def render(targets, out, views, head, size):
    scene = bpy.context.scene
    keep = {"camera": scene.camera, "engine": scene.render.engine, "x": scene.render.resolution_x, "y": scene.render.resolution_y,
            "pct": scene.render.resolution_percentage, "path": scene.render.filepath, "film": scene.render.film_transparent}
    hidden = {o.name: o.hide_render for o in scene.objects}
    cam_data = bpy.data.cameras.new("RenderViewsCam")
    cam_data.lens = LENS
    cam = bpy.data.objects.new("RenderViewsCam", cam_data)
    scene.collection.objects.link(cam)
    written = []
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
        shading = scene.display.shading
        shading.light, shading.color_type = "STUDIO", "TEXTURE"
        scene.render.resolution_x = scene.render.resolution_y = size
        scene.render.resolution_percentage = 100
        scene.render.film_transparent = False
        scene.camera = cam
        out.mkdir(parents=True, exist_ok=True)
        half_fov = math.atan(18.0 / LENS)                            # a 36 mm sensor: half its width over the lens
        for name in targets:
            obj = bpy.data.objects[name]
            show = _family(obj)
            for o in scene.objects:
                o.hide_render = o.name not in show
            centre, radius = _frame(_points(obj), head)
            for view in views:
                d = Vector(VIEW_DIRS[view]).normalized()
                cam.location = centre + d * (radius / math.sin(half_fov) * 1.05)
                cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
                path = out / f"{name}_{view}{'_head' if head else ''}.png"
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                written.append(path)
    finally:
        for o in scene.objects:
            if o.name in hidden:
                o.hide_render = hidden[o.name]
        bpy.data.objects.remove(cam, do_unlink=True)
        bpy.data.cameras.remove(cam_data)
        scene.camera, scene.render.engine = keep["camera"], keep["engine"]
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = keep["x"], keep["y"], keep["pct"]
        scene.render.filepath, scene.render.film_transparent = keep["path"], keep["film"]
    return written


if __name__ == "__main__":
    g = globals()
    done = render(g["TARGETS"], Path(g.get("OUT") or ROOT / "out" / "compare"), g.get("VIEWS") or list(VIEW_DIRS), g.get("HEAD", False), g.get("SIZE", 512))
    print("render_views:", len(done), "images in", done[0].parent if done else "-")
