"""Shared helpers for the Blender asset scripts (run inside Blender, bpy only).

Conventions come from docs/assets/asset-list.md section 2: 1 unit = 1 m, origin on the floor at the
centre of the base, one collection per asset, one shared palette texture, FBX for Unity.

Typical use from a build script in this folder:

    import common
    common.setup_scene()
    coll = common.fresh_collection("GT_Bucket_01")
    ...build objects, link them to coll, give them common.palette_material()...
    common.export_fbx(coll, "Assets/Art/Global/Props/GT_Bucket_01.fbx")
"""

from pathlib import Path

import bpy
import bmesh

REPO = Path(__file__).resolve().parents[2]

PALETTE_PATH = REPO / "Assets" / "Art" / "Global" / "Palette" / "GlobalPalette.png"

# The global palette: a 16 x 16 grid of flat swatches (256 slots). Index = row * 16 + column, row 0 at the top.
# Append only; indices are baked into the UVs of every exported model. Unused slots are magenta so a wrong
# index is obvious. (It was 8 x 8 until household furniture needed more colours; changing the grid moves every
# swatch in the texture, so re-run build_all.py afterwards.)
PALETTE = [
    ("wood_light",   "C9A06A"),   # 0
    ("wood_dark",    "6B4A2E"),   # 1
    ("metal_galv",   "A9B4BC"),   # 2
    ("metal_dark",   "4A525A"),   # 3
    ("rust",         "9A5A3A"),   # 4
    ("barn_red",     "8E2F2A"),   # 5
    ("paint_white",  "E6E2D6"),   # 6
    ("black",        "1B1B1E"),   # 7
    ("grass",        "5E8C4A"),   # 8
    ("dirt",         "7A5C3E"),   # 9
    ("straw",        "D9B957"),   # 10
    ("skin",         "D9A98B"),   # 11
    ("denim",        "3F5F8C"),   # 12
    ("cloth_red",    "B8443B"),   # 13
    ("glow_cyan",    "6FE8E0"),   # 14
    ("rubber",       "2E2E32"),   # 15
    ("pink",         "EFB3AC"),   # 16  muzzles, udders, pigs
    ("horn_cream",   "E8DDBE"),   # 17
    ("brown_coat",   "7A4A2E"),   # 18  brown cattle, horses
    ("fur_grey",     "8C8C88"),   # 19
    ("navy",         "2B3A55"),   # 20  FBI windbreakers, deputies
    ("tan_uniform",  "B79A6A"),   # 21  sheriff's office shirts
    ("hi_vis",       "D6E04A"),   # 22
    ("skin_dark",    "8D5A3B"),   # 23
    ("skin_tan",     "C58C65"),   # 24
    ("skin_pale",    "F0C9B0"),   # 25
    ("grey_suit",    "5A5F66"),   # 26
    ("gold",         "D4AF37"),   # 27  badges
    ("flannel",      "A8453A"),   # 28  farm shirts
    ("hair_black",   "1F1A17"),   # 29
    ("hair_blond",   "C9A25A"),   # 30
    ("hair_grey",    "B9B6B0"),   # 31
    ("orange_cat",   "E08A3C"),   # 32  ginger cats
    ("cream",        "E9DCC0"),   # 33  siamese bodies, light dogs
    ("golden",       "D9A441"),   # 34  retrievers
    ("tan",          "C49A5E"),   # 35  shepherds, beagles, strays
    ("dark_brown",   "4A3322"),   # 36  dachshunds, points
    ("grey_cat",     "7C8088"),   # 37  grey cats, huskies
    ("wood_grey",    "8B8578"),   # 38  weathered boards
    ("tractor_green","3F7D3A"),   # 39
    ("truck_blue",   "2F5F8F"),   # 40
    ("glass",        "9FC8D8"),   # 41
    ("paint_yellow", "E0B83A"),   # 42
    ("alien_grey",   "A9B5A4"),   # 43  Greys
    ("shadow",       "15131A"),   # 44  Shadow Entities
    ("hay",          "D8BE6A"),   # 45
    ("concrete",     "9A9A94"),   # 46
    ("rust_dark",    "6B3A28"),   # 47
    ("corn_green",   "6E9A3E"),   # 48  corn stems
    ("corn_leaf",    "8DB752"),   # 49
    ("leaf_dark",    "4F7A32"),   # 50  oak canopies, bushes
    ("bark",         "5A4630"),   # 51
    ("pine",         "2F5A3A"),   # 52
    ("rock",         "8A8A85"),   # 53
    ("corn_cob",     "E3C255"),   # 54
    ("dead_wood",    "7A7064"),   # 55
    ("fabric_green", "5E7F5A"),   # 56  upholstery, curtains
    ("fabric_mustard","C9A43A"),  # 57
    ("fabric_brown", "7A5A44"),   # 58
    ("porcelain",    "EDEDE8"),   # 59  toilets, sinks, plates
    ("wallpaper",    "D9C9A8"),   # 60  rugs, wall panels
    ("screen",       "1E2A33"),   # 61  switched-off screens
    ("linen",        "E6DFCF"),   # 62  sheets, towels
    ("fabric_blue",  "56708F"),   # 63
    ("fabric_red",   "9A3A38"),   # 64  rugs, cushions
    ("fabric_grey",  "8A8D91"),   # 65
    ("fabric_pink",  "D9A0A8"),   # 66  a child's room
    ("brick",        "A8553F"),   # 67  chimneys, fireplaces
    ("enamel_white", "F2F2EE"),   # 68  fridges, stoves
    ("enamel_cream", "EBDDB5"),   # 69  old appliances
    ("copper",       "B06A3B"),   # 70
    ("tile_blue",    "7FB3C8"),   # 71  bathrooms
    ("tile_green",   "7FA98A"),   # 72
    ("lamp_shade",   "E8D9A0"),   # 73
    ("book_red",     "8A2E2E"),   # 74
    ("book_blue",    "2E4A7A"),   # 75
    ("book_green",   "2E6A4A"),   # 76
    ("paper",        "F0EBDD"),   # 77
    ("plant_green",  "3F7A3A"),   # 78
    ("terracotta",   "C0643A"),   # 79
    ("teddy",        "A9784A"),   # 80
    ("alien_violet", "6E4FA0"),   # 81  alien trim and crystals
    ("alien_green",  "7FD36B"),   # 82  alien fuel, specimens
    ("alien_gold",   "C9A94A"),   # 83  alien hull plating
    ("alien_dark",   "3A3F4A"),   # 84  scorched alien metal
    ("siding_yellow","E3CF8A"),   # 85  house siding
    ("siding_blue",  "8FAEC4"),   # 86
    ("siding_green", "A8BDA0"),   # 87
    ("siding_grey",  "9EA3A6"),   # 88
    ("trailer_teal", "5FA5A0"),   # 89  retro trailers
    ("roof_red",     "8A3A2E"),   # 90
    ("roof_green",   "3F5F46"),   # 91
    ("shingle",      "5B5F66"),   # 92
    ("stucco",       "D9CDB5"),   # 93
    ("log",          "7B5A3C"),   # 94
    ("crust",        "C98A4B"),   # 95  bread, pastry
    ("dough",        "E8C98A"),   # 96
    ("meat_red",     "B04848"),   # 97
    ("glass_brown",  "5A3A1E"),   # 98  beer bottles
    ("glass_green",  "2F6B3E"),   # 99  wine bottles
    ("food_orange",  "E8922A"),   # 100 oranges, carrots
    ("mould",        "6F7F4A"),   # 101 spoiled food
    ("label_red",    "C0392B"),   # 102 cans
    ("label_blue",   "2F6F9F"),   # 103
    ("label_white",  "F0EFE8"),   # 104
    ("glow_green",   "5DF28A"),   # 105 lit green: the bank terminal's screen, "ready" lamps
    ("glow_red",     "FF4B3E"),   # 106 lit red: the launch terminal's screen, "locked" lamps
    ("glow_amber",   "FFB938"),   # 107 lit amber: "working" lamps, hazard marks
]
GRID = 16
SWATCH_PX = 4
UNUSED = "FF00FF"
MATERIAL_NAME = "GlobalPalette"


def swatch_index(name):
    for i, (n, _) in enumerate(PALETTE):
        if n == name:
            return i
    raise KeyError(name)


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def palette_image():
    """The palette as a Blender image, regenerated from PALETTE and saved to PALETTE_PATH."""
    size = GRID * SWATCH_PX
    img = bpy.data.images.get("GlobalPalette.png")      # reused in place so existing materials keep it
    if img is None:
        img = bpy.data.images.new("GlobalPalette.png", size, size, alpha=False)
    img.colorspace_settings.name = "sRGB"
    pixels = [0.0] * (size * size * 4)
    for i in range(GRID * GRID):
        hexcol = PALETTE[i][1] if i < len(PALETTE) else UNUSED
        r, g, b = _hex_rgb(hexcol)
        col, row = i % GRID, i // GRID
        y0 = (GRID - 1 - row) * SWATCH_PX        # image rows count from the bottom
        for y in range(y0, y0 + SWATCH_PX):
            for x in range(col * SWATCH_PX, (col + 1) * SWATCH_PX):
                o = (y * size + x) * 4
                pixels[o:o + 4] = (r, g, b, 1.0)
    img.pixels.foreach_set(pixels)
    PALETTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(PALETTE_PATH)
    img.file_format = "PNG"
    try:
        img.save()
    except RuntimeError:
        if not PALETTE_PATH.exists():                      # an existing file may be locked by the Unity editor while it imports it
            raise
    return img


def palette_material():
    img = palette_image()
    mat = bpy.data.materials.get(MATERIAL_NAME)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(MATERIAL_NAME)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def set_swatch(obj, name_or_index):
    """Point every UV of obj at the centre of one palette swatch (flat colour, no unwrapping)."""
    idx = name_or_index if isinstance(name_or_index, int) else swatch_index(name_or_index)
    col, row = idx % GRID, idx // GRID
    u = (col + 0.5) / GRID
    v = 1.0 - (row + 0.5) / GRID
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    for loop in me.loops:
        uv[loop.index].uv = (u, v)


def add_box(bm, center, size, rot_deg=(0, 0, 0), taper=1.0):
    """A box in bm. taper scales the top face (z+) in x and y, for legs and horns."""
    from math import radians
    from mathutils import Euler, Matrix, Vector
    res = bmesh.ops.create_cube(bm, size=1.0)
    verts = res["verts"]
    for v in verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
        if v.co.z > 0:
            v.co.x *= taper
            v.co.y *= taper
    rot = Euler([radians(a) for a in rot_deg], "XYZ").to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(center)) @ rot, verts=verts)
    return verts


def _superellipse(n, p):
    """n unit-circle-ish points; p = 2 is an ellipse, larger is boxier."""
    from math import cos, sin, tau
    pts = []
    for i in range(n):
        a = tau * i / n
        c, s = cos(a), sin(a)
        pts.append((abs(c) ** (2 / p) * (1 if c >= 0 else -1), abs(s) ** (2 / p) * (1 if s >= 0 else -1)))
    return pts


def ring_y(y, cx, cz, hw, hh, n=10, p=2.4):
    """A ring of points in the XZ plane at height-axis y (a cross-section of something long in Y)."""
    from mathutils import Vector
    return [Vector((cx + hw * u, y, cz + hh * v)) for u, v in _superellipse(n, p)]


def ring_z(z, cx, cy, hx, hy, n=6, p=2.0):
    """A ring of points in the XY plane at height z (a cross-section of a leg, tail or horn)."""
    from mathutils import Vector
    return [Vector((cx + hx * u, cy + hy * v, z)) for u, v in _superellipse(n, p)]


def ring_x(x, cy, cz, hy, hz, n=8, p=2.0):
    """A ring of points in the YZ plane at x (a cross-section of an arm held out sideways)."""
    from mathutils import Vector
    return [Vector((x, cy + hy * u, cz + hz * v)) for u, v in _superellipse(n, p)]


def loft(bm, rings, cap=True):
    """Skin consecutive rings (equal point counts) with quads, optionally closing both ends."""
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(vr[0])
    for a, b in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if cap:
        bm.faces.new(vr[0])
        bm.faces.new(vr[-1][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def subsurf(obj, levels=1):
    """Apply a Catmull-Clark subdivision to obj (rounds a lofted part and doubles its resolution)."""
    mod = obj.modifiers.new("Subsurf", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def paint_faces(obj, fn):
    """Colour each face from the palette: fn(centre, normal) returns a swatch name or index."""
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        pick = fn(poly.center, poly.normal)
        idx = pick if isinstance(pick, int) else swatch_index(pick)
        col, row = idx % GRID, idx // GRID
        u, v = (col + 0.5) / GRID, 1.0 - (row + 0.5) / GRID
        for li in poly.loop_indices:
            uv[li].uv = (u, v)


def smooth(obj, on=True):
    for p in obj.data.polygons:
        p.use_smooth = on


def setup_scene():
    """Metric units, 1 unit = 1 m."""
    us = bpy.context.scene.unit_settings
    us.system = "METRIC"
    us.scale_length = 1.0

def fresh_collection(name):
    """An empty collection called name under the scene collection, replacing any earlier build."""
    old = bpy.data.collections.get(name)
    if old is not None:
        for o in list(old.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def new_mesh_object(name, bm, coll, swatch, flat=True):
    """Turn a bmesh into an object in coll, flat-shaded and coloured from the palette."""
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    obj.data.materials.append(palette_material())
    if flat:
        for p in me.polygons:
            p.use_smooth = False
    set_swatch(obj, swatch)
    return obj


def join(objects, name):
    """Join objects into the first one and rename it."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    old = bpy.data.meshes.get(name)
    if old is not None and old is not obj.data and old.users == 0:
        bpy.data.meshes.remove(old)                                  # an orphan of the last build: keep the new mesh's name plain
    obj.data.name = name
    return obj


def stats(obj):
    me = obj.data
    me.calc_loop_triangles()
    d = obj.dimensions
    return (f"{obj.name}: {len(me.polygons)} faces, {len(me.loop_triangles)} tris, "
            f"size {d.x:.3f} x {d.y:.3f} x {d.z:.3f} m")


def export_anim_fbx(rig_obj, rel_path, only_active=False):
    """Export just a rig and the actions in the file as an animation-only FBX (a clip library for Unity).

    Every action in the file is exported as a take named after the action, so keep bpy.data.actions to
    the clips you mean to ship. With only_active=True only the rig's current action is written, whatever else
    the (shared) Blender file holds.
    """
    out = REPO / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    rig_obj.select_set(True)
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.export_scene.fbx(
        filepath=str(out),
        use_selection=True,
        object_types={"ARMATURE"},
        axis_forward="-Z",
        axis_up="Y",
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        bake_space_transform=False,
        add_leaf_bones=False,
        use_armature_deform_only=False,
        primary_bone_axis="Y",
        secondary_bone_axis="X",
        bake_anim=True,
        bake_anim_use_all_actions=not only_active,
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        path_mode="AUTO",
    )
    return out


def add_sockets(coll):
    """Add two empties to the collection marking which way the model faces: Socket_Front on the front face and Socket_Back on the back.

    Models face -Y in Blender, which arrives as +Z (forward) in Unity, with their back at +Y. The sockets sit at the middle of those faces
    (on the floor for things that stand on it, at the middle height for wall-mounted things) with identity rotation, so in Unity a child
    called Socket_Front points the way the object looks and Socket_Back is the side to put against a wall. Returns the empties so the
    caller can delete them after exporting."""
    import mathutils
    bpy.context.view_layer.update()                                  # transforms and vertices may have changed since the last operator
    meshes = [o for o in coll.all_objects if o.type == "MESH"]
    bodies = [o for o in meshes if o.parent is None] or meshes       # doors and drawers that hang open must not move the sockets
    pts = []
    for o in bodies:
        pts += [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    if not pts:
        return []
    xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
    cx = (min(xs) + max(xs)) / 2
    z = 0.0 if -0.01 <= min(zs) < 0.05 else (min(zs) + max(zs)) / 2
    made = []
    for name, y in (("Socket_Front", min(ys)), ("Socket_Back", max(ys))):
        for stale in [o for o in bpy.data.objects if o.name == name or o.name.startswith(name + ".")]:
            bpy.data.objects.remove(stale, do_unlink=True)          # a leftover would make the new empty Socket_Front.001
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = "ARROWS"
        e.empty_display_size = 0.15
        e.location = (cx, y, z)
        coll.objects.link(e)
        made.append(e)
    return made


def export_fbx(coll, rel_path, rigged=False, sockets=True):
    """Export one collection as FBX for Unity: -Z forward, Y up, scale 1.

    Static meshes get their transforms baked in. Rigged ones keep bake_space_transform off, because baking
    rotates armature bones; Unity applies the axis conversion on import (check Bake Axis Conversion there).
    Socket_Front and Socket_Back empties (add_sockets) travel with the model unless sockets=False.
    """
    out = REPO / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    made = add_sockets(coll) if sockets else []
    bpy.ops.object.select_all(action="DESELECT")
    types = {"MESH", "ARMATURE"} if rigged else {"MESH"}
    if made:
        types = types | {"EMPTY"}
    try:
        bpy.ops.export_scene.fbx(
            filepath=str(out),
            collection=coll.name,
            object_types=types,
            use_mesh_modifiers=True,
            mesh_smooth_type="FACE",
            axis_forward="-Z",
            axis_up="Y",
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options="FBX_SCALE_ALL",
            bake_space_transform=not rigged,
            add_leaf_bones=False,
            use_armature_deform_only=False,
            primary_bone_axis="Y",
            secondary_bone_axis="X",
            bake_anim=False,
            path_mode="AUTO",
            embed_textures=False,
        )
    finally:
        for e in made:
            bpy.data.objects.remove(e, do_unlink=True)
    return out
