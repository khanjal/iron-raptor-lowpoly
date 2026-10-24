"""Write textures/palette/GlobalPalette.png from art/scripts/common.py's PALETTE, without Blender (standard library only).

    python tools/palette_png.py           # write it
    python tools/palette_png.py --check   # exit 1 if the committed file is out of date

The same 64 x 64 image that art/scripts/common.palette_image() makes in Blender and that every GLB carries: 16 x 16 swatches of 4 x 4 pixels, index = row * 16
+ column with row 0 at the top, slots past the end of PALETTE magenta. The palette is append-only, so a copy made before a swatch was added is stale (the
game repo's copy was: the swatches added here for fruit, sports and offices were magenta in it).
"""
import re
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "textures" / "palette" / "GlobalPalette.png"
GRID, SWATCH = 16, 4


def swatches():
    text = (ROOT / "art" / "scripts" / "common.py").read_text(encoding="utf-8")
    body = text[text.index("PALETTE = ["):text.index("GRID = 16")]
    cols = [tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)) for m in re.finditer(r'\("[a-z0-9_]+",\s*"([0-9A-Fa-f]{6})"\)', body)]
    unused = re.search(r'^UNUSED\s*=\s*"([0-9A-Fa-f]{6})"', text, re.M)
    pad = tuple(int(unused.group(1)[i:i + 2], 16) for i in (0, 2, 4)) if unused else (255, 0, 255)
    return cols + [pad] * (GRID * GRID - len(cols))


def png_bytes():
    size = GRID * SWATCH
    cols = swatches()
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            row += bytes(cols[(y // SWATCH) * GRID + x // SWATCH])
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")


if __name__ == "__main__":
    data = png_bytes()
    if "--check" in sys.argv:
        sys.exit(0 if OUT.exists() and OUT.read_bytes() == data else 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)
    print("wrote", OUT.relative_to(ROOT))
