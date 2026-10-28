"""Put reference images and renders of our model side by side, one labelled row each, as the sheet a model is judged on (asset-brief step 3,
blender-assets "Matching the references").

    python tools/compare_sheet.py --row "References" ref1.png ref2.jpg --row "Ours" out/compare/cat/*_thumb.png --out out/compare/cat_sheet.png

Each --row takes a label and then its images (files or folders; a folder gives its .png, .jpg, .jpeg and .webp files in name order). Every image
is fitted into the same square tile on white, so a reference and a render read at the same size. Keep the sheet and the references outside
the repository or in out/ (which git ignores): reference images are looked at, never committed.

Needs Pillow (pip install pillow); nothing else in the project does, so it is not in the test suite.
"""

import argparse
import sys
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def expand(paths):
    """The image files a row names: files as given, folders as their images in name order."""
    files = []
    for p in map(Path, paths):
        if p.is_dir():
            files += sorted(q for q in p.iterdir() if q.suffix.lower() in IMAGE_SUFFIXES)
        else:
            files.append(p)
    return files


def parse(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--row", nargs="+", action="append", metavar=("LABEL", "IMAGE"), required=True, help="a label and its images")
    ap.add_argument("--out", required=True, help="the sheet to write (.png)")
    ap.add_argument("--tile", type=int, default=300, help="the side of each image's tile in pixels (default 300)")
    args = ap.parse_args(argv)
    rows = []
    for row in args.row:
        if len(row) < 2:
            ap.error(f"--row {row[0]!r} has no images")
        rows.append((row[0], expand(row[1:])))
    return rows, Path(args.out), args.tile


def sheet(rows, tile):
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("arialbd.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    label_h = 36
    width = tile * max(len(files) for _, files in rows)
    out = Image.new("RGB", (width, len(rows) * (tile + label_h)), "white")
    draw = ImageDraw.Draw(out)
    for r, (label, files) in enumerate(rows):
        top = r * (tile + label_h)
        draw.text((8, top + 6), label, fill="black", font=font)
        for i, f in enumerate(files):
            im = Image.open(f).convert("RGBA")
            im.thumbnail((tile, tile))
            cell = Image.new("RGBA", (tile, tile), "white")
            cell.alpha_composite(im, ((tile - im.width) // 2, (tile - im.height) // 2))
            out.paste(cell.convert("RGB"), (i * tile, top + label_h))
    return out


def main(argv=None):
    rows, out, tile = parse(argv)
    missing = [str(f) for _, files in rows for f in files if not f.is_file()]
    if missing:
        sys.exit("compare_sheet: no such image: " + ", ".join(missing))
    try:
        image = sheet(rows, tile)
    except ImportError:
        sys.exit("compare_sheet: needs Pillow (pip install pillow)")
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(f"compare_sheet: {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
