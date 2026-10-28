"""Compare a model's outline with a reference silhouette (standard library only, no Blender).

    python tools/silhouette.py GN_CatTabby_faceted_01                       # reference: out/reference/GN_CatTabby_faceted_01.png
    python tools/silhouette.py --ref out/reference/cat.png GN_CatTabby_faceted_01 GN_CatTuxedo_faceted_01
    python tools/silhouette.py --view front GN_Horse_faceted_01             # reference: out/reference/GN_Horse_faceted_01.front.png
    python tools/silhouette.py --all                                        # every out/reference/<model id>[.front].png
    python tools/silhouette.py --min-iou 0.8 ...                            # exit 1 when a model scores lower

The proportion ratios of animal_proportions.py can all pass while the animal still reads wrong (a tube on four posts, issue #125); an outline laid
over the real animal's shows that at once. The model's rest pose is read from its GLB in site/models/ (every mesh, skinned or not), projected from the
side (the model's front, +Z in a GLB, on the right of the image) or the front, and filled into a mask. The reference is any side-view PNG of the
real animal: a shape cut out on a transparent background (any colour), or a dark shape on a light, opaque one. It is scaled to the model's height (--fit length or box for the others), aligned on
the ground, flipped if it faces the other way and slid along for the best overlap.

Reference images are third-party pictures and are never committed (the blender-assets skill): keep them in out/reference/, which git ignores
(in a worktree, its own out/reference/: paths outside the checkout are refused).

Prints the overlap (intersection over union), the share of the reference the model misses and the share of the model outside it, the two aspect
ratios, and where the misses and extras are (back, middle, front by upper and lower half; those as shares of the reference's area). Writes the overlay to out/silhouette/<id>.<view>.png:
grey where both are, red where only the model is, blue where only the reference is. Without a reference it writes the model's own outline
(and fails when the reference was named with --ref). Exit codes: 0 passed, 1 an overlap under --min-iou or a named reference missing, 2 an error.
"""

import argparse
import json
import math
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

from stamp_glb import project_path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "site" / "models"
REFERENCES = ROOT / "out" / "reference"
OVERLAYS = ROOT / "out" / "silhouette"

SIDE, FRONT = "side", "front"
VIEWS = {SIDE: (2, 1), FRONT: (0, 1)}                      # (horizontal, vertical) GLB axes; the side view has the model's front on the right
COLUMNS = {SIDE: ("back", "middle", FRONT), FRONT: ("its right", "middle", "its left")}   # the model faces the viewer in the front view
FITS = ("height", "length", "box")
ROWS = 240                                                      # mask height in pixels
MAX_PIXELS = 6_000_000                                          # refuse bigger reference images (the decoder is pure Python: about 2500 x 2400)
CUT_OUT = 0.02                                                  # a PNG is a cut-out when at least this share of it is transparent
MAX_STRETCH = 8                                                 # a fitted reference is at most this many times the model's length or height

COMPONENTS = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
WIDTHS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}                       # PNG colour type: samples per pixel

BOTH, MODEL_ONLY, REFERENCE_ONLY, EMPTY = (70, 70, 70), (220, 60, 40), (40, 110, 220), (255, 255, 255)


@dataclass
class Mask:
    """A filled outline: rows from the top, each an int whose bit i is column i."""
    width: int
    rows: list

    @property
    def height(self):
        return len(self.rows)

    def area(self):
        return sum(r.bit_count() for r in self.rows)


# ---- GLB: the rest pose's triangles ----

def read_glb(path):
    raw = Path(path).read_bytes()
    if raw[:4] != b"glTF":
        raise ValueError(f"not a GLB: {path}")
    doc, binary, at = None, b"", 12
    while at < len(raw):
        length, kind = struct.unpack_from("<II", raw, at)
        data = raw[at + 8:at + 8 + length]
        if kind == 0x4E4F534A:
            doc = json.loads(data)
        elif kind == 0x004E4942:
            binary = data
        at += 8 + length
    return doc, binary


def accessor(doc, binary, index):
    acc = doc["accessors"][index]
    if "sparse" in acc or "bufferView" not in acc:
        raise ValueError("sparse or compressed accessors are not read")
    view = doc["bufferViews"][acc["bufferView"]]
    item = struct.Struct("<" + COMPONENTS[acc["componentType"]] * WIDTHS[acc["type"]])
    stride = view.get("byteStride", item.size)
    base = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    end = min(len(binary), view.get("byteOffset", 0) + view.get("byteLength", len(binary)))
    if not isinstance(count, int) or count < 0 or (count and base + (count - 1) * stride + item.size > end):
        raise ValueError(f"accessor {index} runs past the end of its buffer view")
    return [item.unpack_from(binary, base + i * stride) for i in range(count)]


def matmul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def column_major(m):
    return [[m[c * 4 + r] for c in range(4)] for r in range(4)]


def local_matrix(node):
    if "matrix" in node:
        return column_major(node["matrix"])
    x, y, z, w = node.get("rotation", (0, 0, 0, 1))
    sx, sy, sz = node.get("scale", (1, 1, 1))
    tx, ty, tz = node.get("translation", (0, 0, 0))
    rot = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
           [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
           [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return [[rot[r][0] * sx, rot[r][1] * sy, rot[r][2] * sz, (tx, ty, tz)[r]] for r in range(3)] + [[0, 0, 0, 1]]


def world_matrices(doc):
    """{node index: its world matrix in the rest pose}, for the nodes of the default scene."""
    nodes = doc["nodes"]
    identity = [[float(r == c) for c in range(4)] for r in range(4)]
    stack = [(n, identity) for n in doc["scenes"][doc.get("scene", 0)]["nodes"]]
    worlds = {}
    while stack:
        index, parent = stack.pop()
        worlds[index] = matmul(parent, local_matrix(nodes[index]))
        stack.extend((child, worlds[index]) for child in nodes[index].get("children", ()))
    return worlds


def mesh_matrix(doc, binary, node, worlds, index):
    """A skinned mesh in its rest pose: every joint's world matrix times its inverse bind gives the same transform, so the first joint's is used."""
    if "skin" not in node:
        return worlds[index]
    skin = doc["skins"][node["skin"]]
    if "inverseBindMatrices" not in skin:
        return worlds[skin["joints"][0]]
    return matmul(worlds[skin["joints"][0]], column_major(accessor(doc, binary, skin["inverseBindMatrices"])[0]))


def transform(m, p):
    return tuple(m[r][0] * p[0] + m[r][1] * p[1] + m[r][2] * p[2] + m[r][3] for r in range(3))


def triangles(doc, binary):
    """Every triangle of every mesh in the scene, in world coordinates (metres, Y up, the model's front towards +Z)."""
    worlds = world_matrices(doc)
    for index in worlds:
        node = doc["nodes"][index]
        if "mesh" not in node:
            continue
        m = mesh_matrix(doc, binary, node, worlds, index)
        for prim in doc["meshes"][node["mesh"]]["primitives"]:
            if prim.get("mode", 4) != 4:
                continue
            points = [transform(m, p) for p in accessor(doc, binary, prim["attributes"]["POSITION"])]
            order = [i[0] for i in accessor(doc, binary, prim["indices"])] if "indices" in prim else range(len(points))
            corners = [points[i] for i in order]
            yield from zip(corners[0::3], corners[1::3], corners[2::3])


# ---- masks ----

def row_span(tri, y):
    """The x range a 2D triangle covers on the line at height y, or None."""
    xs = []
    for (x0, y0), (x1, y1) in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
        if min(y0, y1) <= y <= max(y0, y1) and abs(y1 - y0) > 1e-12:
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    return (min(xs), max(xs)) if xs else None


def mark(rows, j, span):
    """OR the pixels whose centres are in the x span into row j; a span narrower than a pixel marks the one it is in."""
    if span is None or not 0 <= j < len(rows):
        return
    first, last = math.ceil(span[0] - 0.5), math.floor(span[1] - 0.5)
    if first > last:
        first = last = math.floor((span[0] + span[1]) / 2)
    first = max(first, 0)
    if last >= first:
        rows[j] |= ((1 << (last - first + 1)) - 1) << first


def fill(rows, tri):
    """OR a triangle in pixel coordinates into the rows (pixel centres at +0.5); a sliver thinner than a pixel either way still marks one."""
    top, bottom = min(p[1] for p in tri), max(p[1] for p in tri)
    first, last = math.ceil(top - 0.5), math.floor(bottom - 0.5)
    if first > last:                                            # flatter than a row: its whole length on the row its middle is in
        mark(rows, math.floor((top + bottom) / 2), (min(p[0] for p in tri), max(p[0] for p in tri)))
        return
    for j in range(max(0, first), min(len(rows) - 1, last) + 1):
        mark(rows, j, row_span(tri, j + 0.5))


def model_mask(tris, view=SIDE, rows=ROWS):
    """The model's outline from the given view, `rows` pixels tall, cropped to it; also the scale (pixels per metre)."""
    h, v = VIEWS[view]
    flat = [tuple((p[h], p[v]) for p in tri) for tri in tris]
    if not flat:
        raise ValueError("the model has no triangles")
    xs = [p[0] for tri in flat for p in tri]
    ys = [p[1] for tri in flat for p in tri]
    scale = rows / max(max(ys) - min(ys), 1e-9)
    left, top = min(xs), max(ys)
    width = math.ceil((max(xs) - left) * scale) + 1
    out = [0] * rows
    for tri in flat:
        fill(out, [((x - left) * scale, (top - y) * scale) for x, y in tri])
    return crop(Mask(width, out)), scale


def crop(mask):
    used = [j for j, r in enumerate(mask.rows) if r]
    if not used:
        raise ValueError("empty outline")
    rows = mask.rows[used[0]:used[-1] + 1]
    left = min((r & -r).bit_length() - 1 for r in rows if r)
    right = max(r.bit_length() - 1 for r in rows)
    return Mask(right - left + 1, [r >> left for r in rows])


def spans(source, target):
    """For each target pixel, the source pixels it covers [first, end); at least one, so enlarging repeats pixels."""
    return [(i * source // target, max(i * source // target + 1, (i + 1) * source // target)) for i in range(target)]


def resample(mask, width, height):
    """Resize: a pixel is set when any source pixel it covers is, so shrinking a big picture keeps a thin tail or leg."""
    cols = [(first, (1 << (end - first)) - 1) for first, end in spans(mask.width, width)]
    out = []
    for first, end in spans(mask.height, height):
        src = 0
        for r in mask.rows[first:end]:
            src |= r
        out.append(sum(1 << i for i, (c, band) in enumerate(cols) if src >> c & band))
    return Mask(width, out)


def mirror(mask):
    return Mask(mask.width, [int(format(r, f"0{mask.width}b")[::-1], 2) for r in mask.rows])


def to_text(mask):
    """The mask as lines of '#' and '.', for tests and quick looks."""
    return "\n".join("".join("#" if r >> i & 1 else "." for i in range(mask.width)) for r in mask.rows)


def from_text(text):
    lines = text.strip().splitlines()
    return Mask(len(lines[0]), [sum(1 << i for i, ch in enumerate(line) if ch == "#") for line in lines])


# ---- PNG ----

def png_chunks(raw):
    if raw[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG")
    at = 8
    while at < len(raw):
        if at + 12 > len(raw) or at + 12 + struct.unpack_from(">I", raw, at)[0] > len(raw):
            raise ValueError("the PNG is truncated")
        length, kind = struct.unpack_from(">I4s", raw, at)
        yield kind, raw[at + 8:at + 8 + length]
        at += 12 + length


def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def unfilter_row(kind, row, prev, bpp):
    if kind > 4:
        raise ValueError(f"unknown PNG filter type {kind}: the file is damaged")
    out = bytearray(row)
    if kind == 2:
        return bytearray((x + p) & 255 for x, p in zip(row, prev))
    for i in range(len(out)):
        a = out[i - bpp] if i >= bpp else 0
        if kind == 1:
            out[i] = (out[i] + a) & 255
        elif kind == 3:
            out[i] = (out[i] + (a + prev[i]) // 2) & 255
        elif kind == 4:
            out[i] = (out[i] + paeth(a, prev[i], prev[i - bpp] if i >= bpp else 0)) & 255
    return out


def samples(row, depth, count):
    """The row's samples as ints (16-bit ones by their high byte)."""
    if depth == 8:
        return list(row[:count])
    if depth == 16:
        return list(row[0:count * 2:2])
    per_byte, top = 8 // depth, (1 << depth) - 1
    return [(row[i // per_byte] >> (8 - depth * (i % per_byte + 1))) & top for i in range(count)]


def pixels(values, ctype, depth, palette):
    """The row's pixels as (r, g, b, a), 0-255 (tRNS is read for palette images only)."""
    if ctype == 3:
        if max(values, default=0) >= len(palette):
            raise ValueError("a palette image with a missing or short palette")
        return [palette[i] for i in values]
    if ctype in (0, 4):
        top = (1 << min(depth, 8)) - 1
        grey = [v * 255 // top for v in values[::CHANNELS[ctype]]]
        alpha = values[1::2] if ctype == 4 else [255] * len(grey)
        return [(v, v, v, a) for v, a in zip(grey, alpha)]
    step = CHANNELS[ctype]
    alpha = values[3::4] if ctype == 6 else [255] * (len(values) // 3)
    return list(zip(values[0::step], values[1::step], values[2::step], alpha))


def bits(flags):
    return int("".join("1" if f else "0" for f in reversed(flags)) or "0", 2)


def dark(r, g, b):
    return r * 299 + g * 587 + b * 114 < 128_000


def palette_of(plte, trns):
    colours = [tuple(plte[i:i + 3]) for i in range(0, len(plte), 3)]
    return [(*c, trns[i] if i < len(trns) else 255) for i, c in enumerate(colours)]


def read_png_mask(path):
    """A PNG's silhouette as a cropped mask: its opaque pixels when some are transparent (a cut-out), else its dark ones.

    Any colour type at 8 or 16 bits (and grey or palette at 1, 2 or 4), not interlaced."""
    header, plte, trns, data = None, b"", b"", bytearray()
    for kind, chunk in png_chunks(Path(path).read_bytes()):
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"PLTE":
            plte = chunk
        elif kind == b"tRNS":
            trns = chunk
        elif kind == b"IDAT":
            data += chunk
    if header is None:
        raise ValueError(f"{path}: no PNG header")
    width, height, depth, ctype, _, _, interlace = header
    if interlace or width * height > MAX_PIXELS:
        raise ValueError(f"{path}: interlaced or too large; save it as a plain PNG under {MAX_PIXELS} pixels")
    count = width * CHANNELS[ctype]
    stride = math.ceil(count * depth / 8)
    bpp = max(1, CHANNELS[ctype] * depth // 8)
    raw = zlib.decompress(bytes(data))
    palette = palette_of(plte, trns)
    if len(raw) < height * (stride + 1):
        raise ValueError(f"{path}: image data is truncated")
    prev, opaque, shape = bytearray(stride), [], []
    for j in range(height):
        line = raw[j * (stride + 1):(j + 1) * (stride + 1)]
        prev = unfilter_row(line[0], line[1:], prev, bpp)
        row = pixels(samples(prev, depth, count), ctype, depth, palette)
        opaque.append(bits([a >= 128 for _, _, _, a in row]))
        shape.append(bits([a >= 128 and dark(r, g, b) for r, g, b, a in row]))
    clear = width * height - sum(r.bit_count() for r in opaque)
    cut_out = clear >= CUT_OUT * width * height                 # a few transparent corners do not make a photo a cut-out
    return crop(Mask(width, opaque if cut_out else shape))


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def write_png(path, width, pixels):
    """An 8-bit RGB PNG from rows of (r, g, b) tuples."""
    raw = b"".join(b"\x00" + bytes(c for px in row for c in px) for row in pixels)
    body = png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, len(pixels), 8, 2, 0, 0, 0)) + png_chunk(b"IDAT", zlib.compress(raw, 9))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(PNG_SIGNATURE + body + png_chunk(b"IEND", b""))


# ---- comparison ----

def fit_reference(model, ref, fit):
    if fit == "box":
        return resample(ref, model.width, model.height)
    if fit == "length":
        return resample(ref, model.width, min(MAX_STRETCH * model.height, max(1, round(ref.height * model.width / ref.width))))
    return resample(ref, min(MAX_STRETCH * model.width, max(1, round(ref.width * model.height / ref.height))), model.height)


def bottom_aligned(mask, height):
    return [0] * (height - mask.height) + mask.rows


def place(model, ref, offset):
    """The two masks on one canvas, bottoms on the same line, the reference `offset` pixels right of the model (left when negative)."""
    height = max(model.height, ref.height)
    m, r = bottom_aligned(model, height), bottom_aligned(ref, height)
    if offset >= 0:
        r = [x << offset for x in r]
    else:
        m = [x << -offset for x in m]
    return m, r, max(model.width + max(0, -offset), ref.width + max(0, offset))


def iou(m, r):
    union = sum((a | b).bit_count() for a, b in zip(m, r))
    return sum((a & b).bit_count() for a, b in zip(m, r)) / union if union else 0.0


def best_overlap(model, ref):
    """(iou, flipped, offset) for the reference as it is and mirrored, slid along the model by up to a quarter of the wider one."""
    centre = (model.width - ref.width) // 2
    reach = max(model.width, ref.width) // 4
    best = (-1.0, False, 0)
    for flipped, candidate in ((False, ref), (True, mirror(ref))):
        for offset in range(centre - reach, centre + reach + 1):
            m, r, _ = place(model, candidate, offset)
            score = iou(m, r)
            if score > best[0]:
                best = (score, flipped, offset)
    return best


def regions(m, r, width, view):
    """{(column, half): (missed, extra)} as shares of the reference's area: what the model leaves out and what it adds, by region."""
    total = sum(x.bit_count() for x in r) or 1
    half = len(m) // 2
    out = {}
    for c, name in enumerate(COLUMNS[view]):
        x0, x1 = width * c // 3, width * (c + 1) // 3
        band = ((1 << (x1 - x0)) - 1) << x0
        for label, lines in (("upper", range(half)), ("lower", range(half, len(m)))):
            missed = sum((r[j] & ~m[j] & band).bit_count() for j in lines)
            extra = sum((m[j] & ~r[j] & band).bit_count() for j in lines)
            out[(name, label)] = (missed / total, extra / total)
    return out


@dataclass
class Result:
    """The best fit: the overlap, the two masks on one canvas (rows from the top, `width` wide) and how they differ."""
    iou: float
    flipped: bool
    offset: int
    width: int
    model: list
    reference: list
    missed: float                                               # share of the reference the model leaves out
    extra: float                                                # share of the model outside the reference
    regions: dict


def compare(model, ref, view=SIDE, fit="height"):
    ref = fit_reference(model, ref, fit)
    if not ref.area():
        raise ValueError("the reference has no pixels left at the model's size")
    score, flipped, offset = best_overlap(model, ref)
    m, r, width = place(model, mirror(ref) if flipped else ref, offset)
    ref_area, model_area = sum(x.bit_count() for x in r), sum(x.bit_count() for x in m)
    return Result(score, flipped, offset, width, m, r,
                  sum((b & ~a).bit_count() for a, b in zip(m, r)) / ref_area,
                  sum((a & ~b).bit_count() for a, b in zip(m, r)) / model_area,
                  regions(m, r, width, view))


def overlay(m, r, width):
    colour = {(True, True): BOTH, (True, False): MODEL_ONLY, (False, True): REFERENCE_ONLY, (False, False): EMPTY}
    return [[colour[(bool(a >> i & 1), bool(b >> i & 1))] for i in range(width)] for a, b in zip(m, r)]


# ---- command line ----

def report(name, result, model, ref):
    print(f"{name}: overlap {result.iou:.2f}, reference missed {result.missed:.0%}, model outside it {result.extra:.0%}"
          f"{' (reference mirrored)' if result.flipped else ''}")
    print(f"  length/height: model {model.width / model.height:.2f}, reference {ref.width / ref.height:.2f}")
    worst = sorted(result.regions.items(), key=lambda kv: -max(kv[1]))[:3]
    print("  most different (shares of the reference's area): "
          + "; ".join(f"{c} {h}: missed {a:.0%}, extra {b:.0%}" for (c, h), (a, b) in worst))


def check_model(glb, ref_path, view, args):
    """Compare one model; True when it passes --min-iou, or when there is no reference and none was named."""
    model, _ = model_mask(triangles(*read_glb(glb)), view, args.rows)
    out = OVERLAYS / f"{glb.stem}.{view}.png"
    if not ref_path.exists():
        write_png(out, model.width, overlay(model.rows, [0] * model.height, model.width))
        print(f"{glb.stem}: no reference at {ref_path.relative_to(ROOT)}; wrote the model's outline to {out.relative_to(ROOT)}")
        return not args.ref
    ref = read_png_mask(ref_path)
    result = compare(model, ref, view, args.fit)
    write_png(out, result.width, overlay(result.model, result.reference, result.width))
    report(glb.stem, result, model, ref)
    print(f"  overlay: {out.relative_to(ROOT)}")
    return result.iou >= args.min_iou


def default_reference(model_id, view):
    return REFERENCES / (f"{model_id}.png" if view == SIDE else f"{model_id}.{view}.png")


def model_path(arg):
    path = project_path(arg) if arg.endswith(".glb") else project_path(MODELS / f"{arg}.glb")
    if not path.exists():
        raise ValueError(f"no model at {path}")
    return path


def all_jobs():
    """(glb, reference, view) for every out/reference/<model id>[.front].png whose model exists."""
    found = []
    for png in sorted(REFERENCES.glob("*.png")):
        stem, _, view = png.stem.partition(".")
        if (MODELS / f"{stem}.glb").exists() and view in ("", FRONT):
            found.append((MODELS / f"{stem}.glb", png, view or SIDE))
        else:
            print(f"skipped {png.name}: not <model id>.png or <model id>.front.png (use --ref for it)")
    if not found:
        raise ValueError(f"no <model id>.png or <model id>.front.png in {REFERENCES}")
    return found


def jobs(args):
    """(glb, reference, view) for each comparison asked for."""
    if args.all:
        return all_jobs()
    ref = project_path(args.ref) if args.ref else None
    return [(glb, ref or default_reference(glb.stem, args.view), args.view) for glb in map(model_path, args.models)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("models", nargs="*", help="model ids (site/models/<id>.glb) or GLB paths")
    parser.add_argument("--ref", help="one reference PNG for every model given")
    parser.add_argument("--view", choices=list(VIEWS), default=SIDE)
    parser.add_argument("--fit", choices=FITS, default="height", help="scale the reference to the model's height, length or both")
    parser.add_argument("--rows", type=int, default=ROWS, help="mask height in pixels")
    parser.add_argument("--min-iou", type=float, default=0.0, help="exit 1 when a model's overlap is lower")
    parser.add_argument("--all", action="store_true", help="every out/reference/<model id>[.front].png (without models, --ref or --view)")
    args = parser.parse_args(argv)
    if args.all == bool(args.models) or (args.all and (args.ref or args.view != SIDE)):
        parser.error("name models, or pass --all alone")
    try:
        failed = 0
        for glb, ref_path, view in jobs(args):              # every model, not only up to the first failure
            failed += not check_model(glb, ref_path, view, args)
    except (ValueError, OSError, KeyError, IndexError, struct.error, zlib.error) as error:
        print(f"silhouette: {error}", file=sys.stderr)
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
