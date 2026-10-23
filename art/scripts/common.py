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

import json
import os
from pathlib import Path

import bpy
import bmesh

REPO = Path(__file__).resolve().parents[2]


# ===== Where things are written =================================================================================
# Every script writes through export_fbx / export_anim_fbx / export_glb with a path such as "Assets/Art/Global/Props/GT_Bucket_01.fbx".
# That path is relative to the OUTPUT FOLDER, `out/` in this repo by default, so the scripts build standalone. To build straight into a
# Unity project (the old behaviour) set the output folder to that project's root. The settings can be given three ways, first one wins:
#     common.configure(out=..., glb=..., formats=..., only=...)    (kept in bpy.app.driver_namespace: it survives the scripts' importlib.reload)
#     the environment variables LOWPOLY_OUT, LOWPOLY_GLB, LOWPOLY_FORMATS     (set before Blender starts)
#     the defaults: out/, out/glb/, FBX only
_NS_KEYS = {"out": "lowpoly_out", "glb": "lowpoly_glb", "formats": "lowpoly_formats", "only": "lowpoly_only", "prefix": "lowpoly_prefix"}


def configure(out=None, glb=None, formats=None, only=None, prefix=None, reset=False):
    """Set the output folder (out), the folder for GLB files (glb), the formats to write ("fbx", "glb" or "fbx,glb") and, with only, a
    collection of asset names: everything else is skipped by the exporters (the scripts still build it). prefix is put in front of the name of every
    collection, object and mesh that fresh_collection, new_mesh_object and join make, so a build in a Blender file that other work shares cannot
    replace that work's collections of the same name (fresh_collection deletes the one it finds); the exported GLB nodes do not carry it.
    reset=True clears every setting first."""
    ns = bpy.app.driver_namespace
    if reset:
        for k in _NS_KEYS.values():
            ns.pop(k, None)
    for arg, val in (("out", out), ("glb", glb), ("formats", formats), ("only", only), ("prefix", prefix)):
        if val is not None:
            ns[_NS_KEYS[arg]] = val


def out_dir():
    """The output folder every relative export path is under (default out/ in the repo root)."""
    v = bpy.app.driver_namespace.get("lowpoly_out") or os.environ.get("LOWPOLY_OUT")
    return Path(v) if v else REPO / "out"


def glb_dir():
    v = bpy.app.driver_namespace.get("lowpoly_glb") or os.environ.get("LOWPOLY_GLB")
    return Path(v) if v else out_dir() / "glb"


def formats():
    v = bpy.app.driver_namespace.get("lowpoly_formats") or os.environ.get("LOWPOLY_FORMATS") or "fbx"
    return {f.strip().lower() for f in str(v).replace(";", ",").split(",") if f.strip()}


def name_prefix():
    return bpy.app.driver_namespace.get("lowpoly_prefix") or ""


def plain(name):
    """A name without the configured prefix (what the exported files and the manifest call it)."""
    p = name_prefix()
    return name[len(p):] if p and name.startswith(p) else name


def wanted(name):
    """False when configure(only=...) is set and this asset is not in it."""
    only = bpy.app.driver_namespace.get("lowpoly_only")
    return only is None or name in only


def palette_path():
    return out_dir() / "Assets" / "Art" / "Global" / "Palette" / "GlobalPalette.png"

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
    ("egg_white",    "F2EBDD"),   # 108 eggs
    ("egg_brown",    "B97C4B"),   # 109
    ("egg_blue",     "B5D3CE"),   # 110 pale blue-green shells
    ("banana_yellow","F0CE3C"),   # 111 a ripe banana
    ("lettuce_heart","E2EDA0"),   # 112 the pale heart of a lettuce
    ("cheese_cut",   "F5D26A"),   # 113 the cut face of a cheese
    ("cheese_rind",  "C8841F"),   # 114 its rind: the curved side, top and bottom
    ("cheese_hole",  "E2A12C"),   # 115 the holes (dents) in the cut face
    ("apple_green",  "8FBF3A"),   # 116 green apples
    ("apple_yellow", "E8D25A"),   # 117 golden apples
    ("banana_green", "A3B24A"),   # 118 banana necks, green bananas
    ("lemon",        "F2DC3C"),   # 119
    ("pear_green",   "B5C24A"),   # 120
    ("grape_purple", "5A2E6B"),   # 121
    ("grape_green",  "A8C86A"),   # 122
    ("berry_red",    "C8243A"),   # 123 strawberries
    ("basket_orange","D9702A"),   # 124 basketballs, training cones
    ("tennis_yellow","C8E040"),   # 125 tennis balls
    ("leather_brown","9A5530"),   # 126 footballs, gloves
    ("wing_blue",    "4A90E2"),   # 127 butterfly wings
    ("beetle_green", "2F8F5A"),   # 128 beetle shells
    ("office_grey",  "B8BBBE"),   # 129 copiers, cubicle fabric
    ("office_dark",  "5C6066"),   # 130 cubicle trim, chair fabric
    ("laminate",     "D6C6A5"),   # 131 desk tops
    ("water_blue",   "8CC8E8"),   # 132 cooler jugs
    ("clear_glass",  "BFE0EC"),   # 133 see-through: window panes, jars, bottles, wings (the others named glass* are solid; see GLASS_PREFIXES)
    ("clear_brown",  "7A4F2A"),   # 134 see-through beer bottles
    ("clear_green",  "3E8F55"),   # 135 see-through wine bottles
    ("clear_water",  "5DAEDC"),   # 136 see-through water: the level in a cooler jug
]
GRID = 16
SWATCH_PX = 4
UNUSED = "FF00FF"
MATERIAL_NAME = "GlobalPalette"
# Transparent swatches: every swatch whose name starts with one of these prefixes is see-through (clear_*; the older glass* swatches stay solid, so the
# car windows and the like do not turn hollow). A face painted with one is put on a second material
# (GLASS_MATERIAL_NAME: the same palette texture, GLASS_ALPHA opaque, blended), so a model with a window or a bottle has two materials and a model
# without has one, as before. (Like the glow_ swatches, which the web viewer lights up: the name is the switch.)
GLASS_PREFIXES = ("clear_",)
GLASS_MATERIAL_NAME = "GlobalPaletteGlass"
GLASS_ALPHA = 0.4


def is_glass(idx):
    """True when palette swatch idx (a number) is a transparent one."""
    return idx < len(PALETTE) and PALETTE[idx][0].startswith(GLASS_PREFIXES)


def swatch_of_uv(u, v):
    """The palette swatch index a UV lands in (the inverse of set_swatch)."""
    col = min(GRID - 1, max(0, int(u * GRID)))
    row = min(GRID - 1, max(0, int((1.0 - v) * GRID)))
    return row * GRID + col


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
    """The palette as a Blender image, regenerated from PALETTE and saved to palette_path()."""
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
    path = palette_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    try:
        img.save()
    except RuntimeError:
        if not path.exists():                      # an existing file may be locked by the Unity editor while it imports it
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


def glass_material():
    """The transparent twin of palette_material(): the same texture, GLASS_ALPHA opaque, blended (glTF alphaMode BLEND on export)."""
    mat = bpy.data.materials.get(GLASS_MATERIAL_NAME)
    if mat is not None:
        return mat
    base = palette_material()
    mat = base.copy()
    mat.name = GLASS_MATERIAL_NAME
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = GLASS_ALPHA
    if hasattr(mat, "surface_render_method"):              # Blender 4.2 and later
        mat.surface_render_method = "BLENDED"
    if hasattr(mat, "blend_method"):                       # earlier ones, and what the glTF exporter still reads there
        try:
            mat.blend_method = "BLEND"
        except (TypeError, AttributeError):
            pass
    mat.use_backface_culling = True
    return mat


def sync_materials(objs):
    """Give each mesh the palette material, plus the glass one when a face is painted with a transparent swatch, and point every face at the
    right one (read from its UV, so it does not matter how the face was painted). Called when a model is exported; safe to call again."""
    for o in objs:
        if o.type != "MESH" or not o.data.uv_layers:
            continue
        me = o.data
        uv = me.uv_layers.active.data
        glass = [is_glass(swatch_of_uv(*uv[p.loop_start].uv)) for p in me.polygons]
        want = [palette_material()] + ([glass_material()] if any(glass) else [])
        if list(me.materials) != want:
            me.materials.clear()
            for m in want:
                me.materials.append(m)
        for p, g in zip(me.polygons, glass):
            p.material_index = 1 if g else 0


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
    name = name_prefix() + name
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
    name = name_prefix() + name
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
    name = name_prefix() + name
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
    if "fbx" not in formats():
        return None
    out = out_dir() / rel_path
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
    """Export one collection as FBX for Unity: -Z forward, Y up, scale 1. rel_path is under the output folder (out_dir()).

    Static meshes get their transforms baked in. Rigged ones keep bake_space_transform off, because baking rotates armature bones; Unity applies the axis conversion on import (check Bake Axis Conversion there).
    Socket_Front and Socket_Back empties (add_sockets) travel with the model unless sockets=False.

    Also the single place every build script calls when a model is finished, so the other formats hang off it: with "glb" in formats() a static model is also
    written as GLB (export_glb), and configure(only=...) skips the models that are not wanted. A rigged model's GLB is written by the caller, after its clips exist.
    """
    name = Path(rel_path).stem
    if not wanted(name):
        return None
    sync_materials(coll.all_objects)
    if "glb" in formats() and not rigged:
        export_glb(coll, name)
    if "fbx" not in formats():
        return None
    out = out_dir() / rel_path
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


# ===== glTF (GLB) for the web viewer ============================================================================
GLB_COPYRIGHT = "CC BY 4.0, khanjal, https://github.com/khanjal/lowpoly-assets"   # written to every GLB's asset.copyright; equals tools/stamp_glb.py COPYRIGHT (tested)
GLB_FPS = 60                                                       # the frame rate the GLB's animations are sampled at (export_glb sets the scene to it)


def stash_clip(rig_obj, action, clip_name, fps=24):
    """Park an action on the rig as an NLA track called clip_name, so export_glb writes it as an animation of that name, and clear the rig's active action.
    fps is the rate the action was keyed for (the clips differ: 24 or 60); the strip is scaled so every clip plays at its own speed in the GLB.
    Any number of clips can be stashed on one rig."""
    ad = rig_obj.animation_data_create()
    action.name = f"{rig_obj.name}:{clip_name}"                      # the clip scripts replace any action of their own name, so keep this one's out of their way
    track = ad.nla_tracks.new()
    track.name = clip_name
    strip = track.strips.new(clip_name, int(action.frame_range[0]), action)
    strip.scale = GLB_FPS / float(fps)
    ad.action = None
    return track


def clear_clips(rig_obj):
    """Remove the NLA tracks stash_clip made and the actions they used (only those: other actions in a shared file are left alone)."""
    ad = rig_obj.animation_data
    if ad is None:
        return
    used = [st.action for tr in ad.nla_tracks for st in tr.strips if st.action is not None]
    for tr in list(ad.nla_tracks):
        ad.nla_tracks.remove(tr)
    for a in used:
        if a.users == 0:
            bpy.data.actions.remove(a)


def describe(coll):
    """Facts about a built collection, in Blender's axes (x right, y back, z up, front is -y), metres: triangles, the bounding box of the meshes in their exported pose,
    the moving-part objects (child meshes of the body: their name and origin, which is the pivot) and the clips on a rig."""
    rigs = [o for o in coll.all_objects if o.type == "ARMATURE"]
    muted = []
    for r in rigs:                                                   # measure the rest pose, not whichever clip happens to be on top at this frame
        for t in (r.animation_data.nla_tracks if r.animation_data else []):
            if not t.mute:
                t.mute = True
                muted.append(t)
    bpy.context.view_layer.update()
    meshes = [o for o in coll.all_objects if o.type == "MESH"]
    import mathutils
    pts, tris = [], 0
    for o in meshes:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
        pts += [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)] if pts else [0, 0, 0]
    hi = [max(p[i] for p in pts) for i in range(3)] if pts else [0, 0, 0]
    for t in muted:
        t.mute = False
    clips = []
    for r in rigs:
        if r.animation_data:
            clips += [t.name for t in r.animation_data.nla_tracks]
    parts = {}
    for o in meshes:
        if o.parent is not None and o.parent.type == "MESH":
            parts[plain(o.name)] = [round(v, 4) for v in o.location]
    return dict(triangles=tris, bbox_min=[round(v, 4) for v in lo], bbox_max=[round(v, 4) for v in hi], rigged=bool(rigs), clips=clips, part_nodes=parts)


def _strip_prefix(path):
    """Take the build prefix off the node, mesh and material names in a GLB's JSON chunk (the binary chunk is untouched)."""
    import struct
    raw = Path(path).read_bytes()
    jlen, jtype = struct.unpack_from("<II", raw, 12)
    doc = json.loads(raw[20:20 + jlen].decode("utf-8"))
    for key in ("nodes", "meshes", "materials", "skins", "animations", "scenes"):
        for item in doc.get(key, []):
            if "name" in item:
                item["name"] = plain(item["name"])
    body = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    body += b" " * (-len(body) % 4)
    rest = raw[20 + jlen:]
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(body) + len(rest)) + struct.pack("<II", len(body), jtype) + body + rest
    Path(path).write_bytes(out)


def export_glb(coll, name, rigged=None, meta=True):
    """Export one collection as a binary glTF (GLB) for the web viewer: out_dir()/glb/<name>.glb (or glb_dir() when it was set).

    Y up (Blender's x, y, z become glTF's x, z, -y), metres. Meshes are exported with the palette material (a 64 px texture with nearest
    filtering), and a model with transparent (glass) faces also with the blended glass material. A moving part (a child mesh of the body, origin on its pivot) stays a separate node named for its role, with its origin as the node's
    origin, so the viewer can turn it. A rig is exported with the clips that stash_clip put on it, each as an animation named for its clip.
    Writes out_dir()/meta/<name>.json (meta=True) with describe(coll), for tools/make_manifest.py. Returns the path."""
    if not wanted(name):
        return None
    d = glb_dir()
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{name}.glb"
    info = describe(coll)
    rigged = info["rigged"] if rigged is None else rigged
    sync_materials(coll.all_objects)                                 # (a rigged model reaches here without export_fbx having run first)
    objs = [o for o in coll.all_objects if o.type in ("MESH", "ARMATURE")]
    top = [o for o in objs if o.parent is None]
    saved_loc = [(o, o.location.copy()) for o in top]
    saved_sel = [o for o in bpy.context.view_layer.objects if o.select_get()]
    for o in top:
        o.location = (0.0, 0.0, 0.0) if rigged else o.location        # a rig is laid out beside the others for looking at; the file wants it at the origin
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.hide_set(False)
        o.select_set(True)
    sc = bpy.context.scene
    saved_fps = sc.render.fps
    sc.render.fps, sc.render.fps_base = GLB_FPS, 1.0
    props = bpy.ops.export_scene.gltf.get_rna_type().properties
    want = dict(filepath=str(out), export_format="GLB", use_selection=True, export_apply=not rigged, export_yup=True,
                export_cameras=False, export_lights=False, export_extras=False, export_animations=bool(info["clips"]),
                export_animation_mode="NLA_TRACKS", export_force_sampling=True, export_optimize_animation_size=True,
                export_morph=False, export_skins=rigged, export_texcoords=True, export_normals=True, export_copyright=GLB_COPYRIGHT)
    try:
        bpy.ops.export_scene.gltf(**{k: v for k, v in want.items() if k in props})
    finally:
        sc.render.fps = saved_fps
        for o, loc in saved_loc:
            o.location = loc
        bpy.ops.object.select_all(action="DESELECT")
        for o in saved_sel:
            o.select_set(True)
    if name_prefix():
        _strip_prefix(out)
    if meta:
        md = out_dir() / "meta"
        md.mkdir(parents=True, exist_ok=True)
        (md / f"{name}.json").write_text(json.dumps(dict(id=name, **info), indent=1), encoding="utf-8")
    return out
