"""Ground and terrain materials (asset list GB-06, GD-, GI-03): tileable textures for Unity Terrain layers, decals, and road pieces.

Run in Blender:  import runpy; runpy.run_path(r"<repo>/art/scripts/ground.py", run_name="__main__")
Optional globals: GROUND_LIST (texture or piece names). Writes

  Assets/Art/Global/Ground/Tex_<Name>.png       tileable 256 x 256 ground textures (seamless, flat hard-edged patches like the models)
  Assets/Art/Global/Ground/Decal_<Name>.png     transparent decals: road lines, puddles, oil, scorch, crop circle, tyre tracks
  Assets/Art/Global/Ground/Road/<name>.fbx      road, sidewalk and curb pieces (palette-coloured geometry, no texture)
  art/data/ground_surfaces.json                 one row per texture: how large one tile should be, the footstep surface, a note

The textures use the same flat look as everything else: a periodic Voronoi (cells wrap, so the edges match) filled from 3-4 palette-like
colours, plus specks and cracks drawn in the same colour family, so they read as ground at a distance without photographic noise.
Terrain layers in Unity take Tex_*.png directly (set Tiling to the metres in the table); they are not sRGB-critical and do not need normal
maps in this style. The footstep surface names are the ones the audio list (asset-list section 4.15) should adopt: it predates the textures and lacks several of them.
"""

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import props_lib
for _m in (common, props_lib):
    importlib.reload(_m)
Prop = props_lib.Prop

SIZE = 256
OUT = common.REPO / "Assets" / "Art" / "Global" / "Ground"


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


def to_linear_free(img):
    return img


def voronoi_labels(rng, n):
    """Label every pixel with its nearest of n random points on a torus, so the result tiles."""
    pts = rng.random((n, 2))
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    xs = xs / SIZE
    ys = ys / SIZE
    best = np.full((SIZE, SIZE), 9.0)
    lab = np.zeros((SIZE, SIZE), dtype=np.int32)
    for k, (px, py) in enumerate(pts):
        dx = np.abs(xs - px); dx = np.minimum(dx, 1 - dx)
        dy = np.abs(ys - py); dy = np.minimum(dy, 1 - dy)
        d = dx * dx + dy * dy
        m = d < best
        best[m] = d[m]
        lab[m] = k
    return lab


def patches(rng, colours, n, specks=0.0, speck_colours=None, stretch=1.0):
    """Hard-edged Voronoi patches in the given colours, with optional single-pixel specks."""
    lab = voronoi_labels(rng, n)
    cols = np.array([hexrgb(c) for c in colours])
    pick = rng.integers(0, len(colours), size=n)
    img = cols[pick[lab]]
    if specks > 0:
        sc = np.array([hexrgb(c) for c in (speck_colours or colours)])
        mask = rng.random((SIZE, SIZE)) < specks
        img[mask] = sc[rng.integers(0, len(sc), size=int(mask.sum()))]
    return img


def stamp(img, x, y, colour, w=1, h=1):
    for dy in range(h):
        for dx in range(w):
            img[(y + dy) % SIZE, (x + dx) % SIZE] = colour


def cracks(img, rng, colour, count, length=60, width=1):
    c = hexrgb(colour)
    for _ in range(count):
        x, y = int(rng.integers(0, SIZE)), int(rng.integers(0, SIZE))
        ang = rng.uniform(0, 6.283)
        for _ in range(length):
            ang += rng.uniform(-0.6, 0.6)
            x += int(round(np.cos(ang) * 1.5)); y += int(round(np.sin(ang) * 1.5))
            stamp(img, x, y, c, width, width)


def rows(img, rng, light, dark, pitch=32, ridge=12):
    ys = np.arange(SIZE)
    band = ((ys % pitch) < ridge)
    img[band] = hexrgb(dark)
    img[~band] = img[~band] * 0.5 + hexrgb(light) * 0.5
    return img


# name -> (builder(rng) -> image, metres per tile, footstep surface, note)
def _grass_short(r): return patches(r, ["#5E8C4A", "#6A9A52", "#547F43", "#73A35A"], 70, 0.02, ["#8DBB6E", "#486C39"])
def _grass_long(r): return patches(r, ["#4F7A32", "#5E8C4A", "#436A2B", "#6A9A52"], 90, 0.05, ["#8DBB6E", "#2F5A22", "#C9C070"])
def _grass_dry(r): return patches(r, ["#A39A56", "#B3AA63", "#968D4C", "#C0B572"], 70, 0.03, ["#7A6F3A", "#D9CE88"])
def _dirt(r): return patches(r, ["#7A5C3E", "#6E5236", "#86664A", "#7F6040"], 80, 0.03, ["#4A3322", "#9A7A58"])
def _dirt_packed(r):
    img = patches(r, ["#8A6B4B", "#80623F", "#947554", "#86684A"], 50, 0.015, ["#6A4E33", "#A8896A"]); cracks(img, r, "#6E5236", 5, 45); return img
def _gravel(r): return patches(r, ["#8C8C86", "#7B7B76", "#9B9B95", "#6E6E6A", "#A8A8A2"], 400, 0.04, ["#55554F", "#C4C4BE"])
def _mud(r): return patches(r, ["#4F3A28", "#5A4331", "#46321F", "#634A35"], 40, 0.02, ["#8A7A66", "#33241A"])
def _sand(r): return patches(r, ["#D8C48A", "#CDB87C", "#E2D096", "#C4AE72"], 70, 0.03, ["#B49A5E", "#EFE2B0"])
def _snow(r): return patches(r, ["#F2F6F8", "#E4ECF1", "#FFFFFF", "#D6E2EA"], 60, 0.02, ["#C2D2DE", "#FFFFFF"])
def _tilled(r):
    img = patches(r, ["#5E4630", "#6A5038", "#54402B"], 60, 0.02, ["#3A2A1C", "#7E6248"]); return rows(img, r, "#6A5038", "#3F2E1F")
def _crop_green(r):
    """A green crop in rows (corn, beans): leafy plants in rows 8 per tile, bare soil between, for the far fields (FarmsteadSurroundings)."""
    img = patches(r, ["#4F7A32", "#5E8C4A", "#436A2B", "#6A9A52"], 70, 0.05, ["#2F5A22", "#8DBB6E"])
    return rows(img, r, "#5E8C4A", "#33291C", pitch=32, ridge=9)
def _crop_gold(r):
    """A ripe crop in rows (wheat, barley): gold plants in rows, soil between."""
    img = patches(r, ["#C9B35A", "#BFA84E", "#D2BC66", "#B89C46"], 70, 0.05, ["#8A7438", "#E6D58C"])
    return rows(img, r, "#C9B35A", "#3E301E", pitch=32, ridge=9)
def _asphalt(r): return patches(r, ["#3A3C40", "#34363A", "#404246", "#2E3034"], 120, 0.05, ["#5C5E62", "#232427"])
def _asphalt_cracked(r):
    img = patches(r, ["#3A3C40", "#34363A", "#404246", "#2E3034"], 120, 0.05, ["#5C5E62", "#232427"]); cracks(img, r, "#17181A", 9, 70); return img
def _concrete(r): return patches(r, ["#9A9A94", "#A2A29C", "#92928C", "#A8A8A2"], 30, 0.02, ["#7C7C76", "#BEBEB8"])
def _concrete_cracked(r):
    img = patches(r, ["#9A9A94", "#A2A29C", "#92928C", "#A8A8A2"], 30, 0.02, ["#7C7C76", "#BEBEB8"]); cracks(img, r, "#4C4C48", 7, 60); return img
def _planks(r):
    img = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    cols = ["#C9A06A", "#BF9560", "#D1AA74", "#B88C58", "#C4985F"]
    for i in range(8):
        img[i * 32:(i + 1) * 32] = hexrgb(cols[int(r.integers(0, len(cols)))])
        img[i * 32:i * 32 + 2] = hexrgb("#5A3E22")
        for _ in range(int(r.integers(1, 4))):
            x = int(r.integers(0, SIZE)); img[i * 32 + 2:(i + 1) * 32, x:x + 2] = hexrgb("#5A3E22")
    return img
def _linoleum(r):
    img = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    a, b = hexrgb("#9FA68F"), hexrgb("#E6E2D6")
    for y in range(8):
        for x in range(8):
            img[y * 32:(y + 1) * 32, x * 32:(x + 1) * 32] = a if (x + y) % 2 else b
    mask = r.random((SIZE, SIZE)) < 0.03
    img[mask] *= 0.85
    return img
def _carpet(r): return patches(r, ["#7A4A44", "#84504A", "#704440", "#8A5650"], 500, 0.15, ["#5A302C", "#9C6862"])
def _carpet_neutral(r): return patches(r, ["#E2E0DC", "#D8D6D2", "#EAE8E4", "#CFCDC9"], 500, 0.15, ["#B4B2AE", "#F2F0EC"])   # near white: a tint (a material's colour) makes it any carpet, where Carpet is already red
def _straw(r): return patches(r, ["#D9BE6A", "#CCB05C", "#E3C978", "#C0A450"], 300, 0.1, ["#8A7438", "#F0DC9A"])
def _cobble(r):
    lab = voronoi_labels(r, 90)
    cols = np.array([hexrgb(c) for c in ("#8A8A85", "#7A7A76", "#9A9A94", "#6E6E6A")])
    img = cols[r.integers(0, 4, size=90)[lab]]
    edge = np.zeros((SIZE, SIZE), dtype=bool)
    edge[:-1, :] |= lab[:-1, :] != lab[1:, :]; edge[:, :-1] |= lab[:, :-1] != lab[:, 1:]
    edge[-1, :] |= lab[-1, :] != lab[0, :]; edge[:, -1] |= lab[:, -1] != lab[:, 0]
    img[edge] = hexrgb("#3C3C38")
    return img
def _leaves(r): return patches(r, ["#7A5C2E", "#8C6A34", "#6A4E26", "#A07A3C", "#5E4A22"], 260, 0.12, ["#C0873A", "#4A3A1A"])
def _scorched(r): return patches(r, ["#2A2420", "#1E1A17", "#332B26", "#17130F"], 90, 0.06, ["#5A3E2C", "#0A0807"])
def _water(r): return patches(r, ["#3F6F95", "#47789D", "#386A8E", "#4F82A6"], 24, 0.01, ["#8FB8D4"])
def _moss(r): return patches(r, ["#4A6A3A", "#557544", "#3E5C30", "#5F7E4C"], 150, 0.05, ["#7E9E66", "#2F4624"])

SURFACES = {
    "Grass_Short": (_grass_short, 4.0, "grass", "lawns, yards, pasture"),
    "Grass_Long": (_grass_long, 4.0, "grass_long", "unmown verges, the field edge; quieter to hide in than it looks"),
    "Grass_Dry": (_grass_dry, 4.0, "grass", "desert scrub, late summer"),
    "Dirt": (_dirt, 3.0, "dirt", "fields, trails"),
    "Dirt_Packed": (_dirt_packed, 3.0, "dirt", "the yard, worn paths, driveways"),
    "Gravel": (_gravel, 3.0, "gravel", "driveways, shoulders; loud underfoot"),
    "Mud": (_mud, 3.0, "mud", "the pig wallow, ruts; slows and leaves tracks"),
    "Sand": (_sand, 4.0, "sand", "desert, lakeside"),
    "Snow": (_snow, 4.0, "snow", "winter maps; leaves tracks"),
    "Tilled_Soil": (_tilled, 3.0, "dirt", "garden beds and ploughed fields"),
    "Crop_Green": (_crop_green, 6.0, "grass_long", "a green crop in rows (the far fields)"),
    "Crop_Gold": (_crop_gold, 6.0, "grass_long", "a ripe crop in rows (the far fields)"),
    "Asphalt": (_asphalt, 4.0, "asphalt", "county roads, car parks"),
    "Asphalt_Cracked": (_asphalt_cracked, 4.0, "asphalt", "old roads, the trailer park"),
    "Concrete": (_concrete, 3.0, "concrete", "slabs, sidewalks, the base"),
    "Concrete_Cracked": (_concrete_cracked, 3.0, "concrete", "old slabs, abandoned lots"),
    "Wood_Planks": (_planks, 2.0, "wood", "porches, barn floors, house floors"),
    "Linoleum": (_linoleum, 2.0, "linoleum", "kitchens, diners, clinics"),
    "Carpet": (_carpet, 2.0, "carpet", "living rooms, bedrooms; the quietest surface"),
    "Carpet_Neutral": (_carpet_neutral, 2.0, "carpet", "a carpet in any colour: tint the material (the farmhouse's rooms)"),
    "Straw": (_straw, 2.0, "hay", "barn floors, loft, pens; quiet"),
    "Cobble": (_cobble, 3.0, "stone", "town squares, old yards"),
    "Leaves": (_leaves, 3.0, "leaves", "under trees; loud, rustling"),
    "Scorched": (_scorched, 3.0, "dirt", "the crash furrow and where an alien ability burned"),
    "Water": (_water, 6.0, "water", "ponds and creeks; splashes; shorts out Energy Beings"),
    "Moss": (_moss, 3.0, "moss", "damp corners, north walls, the well"),
}


# ===== Decals: RGBA, transparent background =====================================================================
def _blank():
    return np.zeros((SIZE, SIZE, 4), dtype=np.float32)


def _fill(img, x0, y0, x1, y1, colour, a=1.0):
    c = np.append(hexrgb(colour), a)
    img[y0:y1, x0:x1] = c


def decal_center_line():
    img = _blank()
    for k in range(4):
        _fill(img, 118, k * 64 + 8, 138, k * 64 + 48, "#E0B83A")
    return img


def decal_edge_line():
    img = _blank(); _fill(img, 120, 0, 136, SIZE, "#E6E2D6"); return img


def decal_crosswalk():
    img = _blank()
    for k in range(6):
        _fill(img, 14 + k * 40, 40, 38 + k * 40, 216, "#E6E2D6")
    return img


def decal_parking():
    img = _blank()
    _fill(img, 6, 0, 16, SIZE, "#E6E2D6"); _fill(img, 240, 0, 250, SIZE, "#E6E2D6"); return img


def _disc(img, cx, cy, rx, ry, colour, a, rng=None, wobble=0.0):
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    ang = np.arctan2(ys - cy, xs - cx)
    w = 1.0 + wobble * (np.sin(ang * 3 + 1) + 0.6 * np.cos(ang * 5 + 2))
    inside = ((xs - cx) / (rx * w)) ** 2 + ((ys - cy) / (ry * w)) ** 2 < 1.0
    img[inside] = np.append(hexrgb(colour), a)


def decal_puddle():
    img = _blank(); _disc(img, 128, 128, 105, 70, "#5A7F99", 0.85, wobble=0.12); _disc(img, 100, 108, 34, 18, "#A8C4D6", 0.8, wobble=0.1); return img


def decal_oil():
    img = _blank(); _disc(img, 128, 128, 80, 60, "#17181A", 0.85, wobble=0.18); _disc(img, 150, 140, 40, 28, "#2E3034", 0.9, wobble=0.15); return img


def decal_scorch():
    img = _blank(); _disc(img, 128, 128, 120, 120, "#17130F", 0.5, wobble=0.1); _disc(img, 128, 128, 80, 80, "#0A0807", 0.8, wobble=0.15); return img


def decal_crop_circle():
    img = _blank()
    for r, w in ((110, 10), (78, 10), (46, 10)):
        _disc(img, 128, 128, r + w, r + w, "#C9B35A", 0.9); _disc(img, 128, 128, r, r, "#C9B35A", 0.0)
        ys, xs = np.mgrid[0:SIZE, 0:SIZE]
        d = np.sqrt((xs - 128.0) ** 2 + (ys - 128.0) ** 2)
        img[(d >= r) & (d < r + w)] = np.append(hexrgb("#C9B35A"), 0.9)
        img[(d < r) & (d >= r - 1)] *= 1.0
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    img[np.sqrt((xs - 128.0) ** 2 + (ys - 128.0) ** 2) < 14] = np.append(hexrgb("#C9B35A"), 0.9)
    return img


def decal_tyre_tracks():
    img = _blank()
    for x in (84, 172):
        for y in range(0, SIZE, 6):
            _fill(img, x - 9 + (y // 6 % 2) * 2, y, x + 9 + (y // 6 % 2) * 2, y + 3, "#2E2418", 0.8)
    return img


def decal_leaves():
    img = _blank(); rng = np.random.default_rng(5)
    for _ in range(40):
        x, y = int(rng.integers(8, 248)), int(rng.integers(8, 248))
        _fill(img, x, y, x + int(rng.integers(4, 9)), y + int(rng.integers(3, 6)), ["#A07A3C", "#8C6A34", "#C0873A", "#6A4E26"][int(rng.integers(0, 4))], 0.95)
    return img


def decal_alien_footprint():
    img = _blank()
    for k, (cx, cy) in enumerate(((96, 96), (160, 96), (128, 170))):
        _disc(img, cx, cy, 22, 30, "#8FD38A", 0.7, wobble=0.1)
    _disc(img, 128, 190, 34, 22, "#8FD38A", 0.7, wobble=0.1)
    return img


DECALS = {"RoadCenterLine": decal_center_line, "RoadEdgeLine": decal_edge_line, "Crosswalk": decal_crosswalk, "ParkingLines": decal_parking,
          "Puddle": decal_puddle, "OilStain": decal_oil, "Scorch": decal_scorch, "CropCircle": decal_crop_circle, "TyreTracks": decal_tyre_tracks,
          "Leaves": decal_leaves, "AlienFootprint": decal_alien_footprint}


def save_png(img, path):
    if img.shape[2] == 3:
        img = np.concatenate([img, np.ones((SIZE, SIZE, 1), dtype=np.float32)], axis=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = path.name
    old = bpy.data.images.get(name)
    if old is not None:
        bpy.data.images.remove(old)
    im = bpy.data.images.new(name, SIZE, SIZE, alpha=True)
    im.colorspace_settings.name = "sRGB"
    flat = np.flipud(np.clip(img, 0, 1)).astype(np.float32)         # Blender images are stored bottom row first
    im.pixels.foreach_set(flat.ravel())
    im.filepath_raw = str(path)
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


# ===== Road pieces (geometry in palette colours) ================================================================
def _road_straight(name="GI_Road_Straight_01", length=8.0, width=7.0):
    p = Prop(name)
    p.box("alien_dark", (0, 0, 0.05), (width, length, 0.1))
    for k in range(2):
        p.box("paint_yellow", (0, -2.0 + k * 4.0, 0.105), (0.12, 2.0, 0.01))
    for s in (-1, 1):
        p.box("paint_white", (s * (width / 2 - 0.25), 0, 0.105), (0.1, length, 0.01))
        p.box("concrete", (s * (width / 2 + 0.6), 0, 0.075), (1.2, length, 0.15))                 # the shoulder or verge
    return p


def _road_dirt(name="GI_Road_Dirt_01", length=8.0, width=5.0):
    p = Prop(name)
    p.box("dirt", (0, 0, 0.04), (width, length, 0.08))
    for s in (-1, 1):
        p.box("rust_dark", (s * 0.8, 0, 0.085), (0.5, length, 0.01))                              # wheel ruts
        p.box("grass", (s * (width / 2 + 0.6), 0, 0.03), (1.2, length, 0.06))
    p.box("wood_grey", (0, 0, 0.083), (0.05, 0.05, 0.01))
    return p


def _road_t(name="GI_Road_Intersection_T_01", width=7.0):
    p = Prop(name)
    p.box("alien_dark", (0, 0, 0.05), (width, width, 0.1))
    p.box("alien_dark", (0, 4.5, 0.05), (width, 2.0, 0.1))
    for k in range(2):
        p.box("paint_yellow", (-2.0 - k * 1.8, 0, 0.105), (1.2, 0.12, 0.01))
    p.box("paint_white", (0, -width / 2 + 0.4, 0.105), (width - 1, 0.4, 0.01))                    # a stop line
    return p


def _road_curve(name="GI_Road_Curve_01", r=8.0, width=7.0):
    import math
    p = Prop(name)
    n = 8
    for k in range(n):
        a = math.radians((k + 0.5) * 90 / n)
        seg = math.pi / 2 * r / n
        x, y = r * math.sin(a) - r, -r * math.cos(a) + r
        p.box("alien_dark", (x, y, 0.05), (width, seg * 1.02, 0.1), rot=(0, 0, math.degrees(a) - 90))
        p.box("paint_yellow", (x, y, 0.105), (0.12, seg * 0.5, 0.01), rot=(0, 0, math.degrees(a) - 90))
    return p


def _sidewalk(name="GI_Sidewalk_01"):
    p = Prop(name)
    p.box("concrete", (0, 0, 0.08), (1.6, 4.0, 0.16))
    for k in range(3):
        p.box("fabric_grey", (0, -1.0 + k * 1.0, 0.162), (1.6, 0.03, 0.004))
    return p


def _curb(name="GI_Curb_01"):
    p = Prop(name)
    p.box("concrete", (0, 0, 0.09), (0.25, 4.0, 0.18))
    p.box("fabric_grey", (-0.13, 0, 0.09), (0.02, 4.0, 0.16))
    return p


def _driveway(name="GI_Driveway_Gravel_01"):
    p = Prop(name)
    p.box("fabric_grey", (0, 0, 0.03), (3.2, 6.0, 0.06))
    for s in (-1, 1):
        p.box("dirt", (s * 0.8, 0, 0.065), (0.5, 6.0, 0.01))
    return p


ROAD = {"road_straight": _road_straight, "road_dirt": _road_dirt, "road_t": _road_t, "road_curve": _road_curve,
        "sidewalk": _sidewalk, "curb": _curb, "driveway": _driveway}


def run():
    only = globals().get("GROUND_LIST")
    rows_out = []
    for name, (fn, tile, step, note) in SURFACES.items():
        if only and name not in only:
            continue
        rng = np.random.default_rng(sum(ord(c) * (i + 1) for i, c in enumerate(name)))
        save_png(fn(rng), OUT / f"Tex_{name}.png")
        rows_out.append(dict(name=name, file=f"Tex_{name}.png", tile_metres=tile, footstep=step, note=note))
    for name, fn in DECALS.items():
        if only and f"Decal_{name}" not in only:
            continue
        save_png(fn(), OUT / f"Decal_{name}.png")
    if not only:
        data = common.REPO / "art" / "data" / "ground_surfaces.json"
        data.parent.mkdir(parents=True, exist_ok=True)
        data.write_text(json.dumps({"size_px": SIZE, "surfaces": rows_out, "decals": [f"Decal_{n}.png" for n in DECALS]}, indent=1))
    x = 0.0
    for key, fn in ROAD.items():
        if only and key not in only:
            continue
        prop = fn()
        obj, coll = prop.finish()
        common.export_fbx(coll, f"Assets/Art/Global/Ground/Road/{prop.name}.fbx")
        obj.location = (x, 0, 0)
        x += obj.dimensions.x + 3
    print("ground done", len(rows_out), "textures,", len(DECALS), "decals,", len(ROAD), "road pieces")


if __name__ == "__main__":
    run()
