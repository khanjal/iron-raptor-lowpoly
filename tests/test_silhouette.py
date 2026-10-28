"""tools/silhouette.py: the model's outline from its GLB, PNG reading and writing, and the overlap with a reference."""
import contextlib
import io
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import silhouette  # noqa: E402

CAT = ROOT / "site" / "models" / "GN_CatTabby_faceted_01.glb"
SHAPE = """
..........
..####....
.#######..
.########.
.#..#..#..
"""


def png(width, rows, ctype, depth=8, plte=b"", trns=b""):
    """A PNG of raw sample rows (filter 0), for the reader's colour types."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    body = chunk(b"IHDR", struct.pack(">IIBBBBB", width, len(rows), depth, ctype, 0, 0, 0))
    body += chunk(b"PLTE", plte) if plte else b""
    body += chunk(b"tRNS", trns) if trns else b""
    body += chunk(b"IDAT", zlib.compress(b"".join(b"\x00" + bytes(r) for r in rows)))
    return silhouette.PNG_SIGNATURE + body + chunk(b"IEND", b"")


class Masks(unittest.TestCase):
    def test_text_round_trip_and_crop(self):
        mask = silhouette.crop(silhouette.from_text(SHAPE))
        self.assertEqual((mask.width, mask.height), (8, 4))
        self.assertEqual(silhouette.to_text(mask).splitlines()[0], ".####...")

    def test_mirror(self):
        mask = silhouette.from_text("##..\n#...")
        self.assertEqual(silhouette.to_text(silhouette.mirror(mask)), "..##\n...#")

    def test_triangle_fill(self):
        rows = [0] * 4
        silhouette.fill(rows, [(0, 0), (4, 0), (0, 4)])
        self.assertEqual(silhouette.to_text(silhouette.Mask(4, rows)), "####\n###.\n##..\n#...")

    def test_flat_sliver_still_marks_a_row(self):
        rows = [0] * 3
        silhouette.fill(rows, [(0, 1.3), (3, 1.3), (3, 1.4)])
        self.assertEqual(rows, [0, 0b111, 0])

    def test_sliver_still_marks_a_pixel(self):
        rows = [0] * 3
        silhouette.fill(rows, [(1.4, 0), (1.45, 0), (1.45, 3)])
        self.assertTrue(all(r == 0b10 for r in rows))


class Overlap(unittest.TestCase):
    def test_same_shape_scores_one(self):
        mask = silhouette.crop(silhouette.from_text(SHAPE))
        result = silhouette.compare(mask, mask)
        self.assertAlmostEqual(result.iou, 1.0)
        self.assertEqual((result.missed, result.extra), (0.0, 0.0))

    def test_reference_facing_the_other_way_is_mirrored(self):
        mask = silhouette.crop(silhouette.from_text(SHAPE))
        result = silhouette.compare(mask, silhouette.mirror(mask))
        self.assertTrue(result.flipped)
        self.assertAlmostEqual(result.iou, 1.0)

    def test_reference_at_another_scale_is_fitted(self):
        mask = silhouette.crop(silhouette.from_text(SHAPE))
        big = silhouette.resample(mask, mask.width * 3, mask.height * 3)
        self.assertAlmostEqual(silhouette.compare(mask, big).iou, 1.0)

    def test_shrinking_keeps_a_thin_line(self):
        wide = silhouette.Mask(40, [0] * 19 + [(1 << 40) - 1] + [0] * 20)     # a one-pixel line in a 40 x 40 picture
        self.assertEqual(silhouette.resample(wide, 8, 8).area(), 8)

    def test_a_long_thin_reference_is_capped(self):
        mask = silhouette.crop(silhouette.from_text(SHAPE))
        strip = silhouette.Mask(300, [(1 << 300) - 1])
        self.assertLessEqual(silhouette.fit_reference(mask, strip, "height").width, silhouette.MAX_STRETCH * mask.width)

    def test_regions_name_where_the_model_differs(self):
        ref = silhouette.from_text("######\n######")
        model = silhouette.from_text("######\n####..")       # the lower front corner is missing
        result = silhouette.compare(model, ref, fit="box")
        missed, extra = result.regions[("front", "lower")]
        self.assertAlmostEqual(missed, 2 / 12)
        self.assertEqual(extra, 0.0)
        self.assertEqual(result.regions[("back", "upper")], (0.0, 0.0))


class Png(unittest.TestCase):
    def read(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "r.png"
            path.write_bytes(data)
            return silhouette.to_text(silhouette.read_png_mask(path))

    def test_cut_out_is_its_opaque_pixels_of_any_colour(self):
        rows = [[0, 0, 0, 255, 0, 0, 0, 0, 255, 255, 255, 255], [0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255]]
        self.assertEqual(self.read(png(3, rows, 6)), "#.#\n###")             # a white horse on a transparent background still counts

    def test_opaque_picture_is_its_dark_pixels(self):
        rows = [[0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255], [0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255]]
        self.assertEqual(self.read(png(3, rows, 6)), "#..\n###")

    def test_grey_and_palette_and_bits(self):
        self.assertEqual(self.read(png(2, [[0, 255], [255, 0]], 0)), "#.\n.#")
        plte, trns = bytes((0, 0, 0, 0, 0, 0, 255, 255, 255)), bytes((255, 0))
        self.assertEqual(self.read(png(3, [[0, 1, 2]], 3, plte=plte, trns=trns)), "#.#")     # index 1 is transparent
        self.assertEqual(self.read(png(8, [[0b00001111]], 0, depth=1)), "####")

    def test_photo_with_clear_corners_is_not_a_cut_out(self):
        white, black, clear = [255, 255, 255, 255], [0, 0, 0, 255], [0, 0, 0, 0]
        rows = [white * 5 + black + white * 4 for _ in range(10)]          # a dark column on an opaque photo
        rows[0][:4] = clear                                                 # one clear corner pixel: 1 %
        self.assertEqual(self.read(png(10, rows, 6)), "\n".join(["#"] * 10))   # the dark column, not the whole picture

    def test_unknown_filter_is_an_error(self):
        with self.assertRaises(ValueError):
            silhouette.unfilter_row(7, bytes(1), bytearray(1), 1)

    def test_broken_pngs_are_errors(self):
        truncated = png(2, [[0, 0]], 0)[:-30]                                   # cut before the image data ends
        blank = png(2, [[255, 255]], 0)                                         # no silhouette in it
        with self.assertRaises(ValueError):
            self.read(truncated)
        with self.assertRaises(ValueError):
            self.read(blank)

    def test_accessor_past_the_end_is_an_error(self):
        doc = {"accessors": [{"bufferView": 0, "componentType": 5126, "type": "VEC3", "count": 1000}], "bufferViews": [{}]}
        with self.assertRaises(ValueError):
            silhouette.accessor(doc, b"\x00" * 24, 0)

    def test_write_then_read(self):
        mask = silhouette.crop(silhouette.from_text(SHAPE))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "o.png"
            silhouette.write_png(path, mask.width, silhouette.overlay(mask.rows, [0] * mask.height, mask.width))
            self.assertEqual(silhouette.to_text(silhouette.read_png_mask(path)), silhouette.to_text(mask))

    def test_filters(self):
        prev = bytearray((10, 20, 30, 40))
        self.assertEqual(silhouette.unfilter_row(1, b"\x05\x05\x05\x05", prev, 2), bytearray((5, 5, 10, 10)))
        self.assertEqual(silhouette.unfilter_row(2, b"\x01\x01\x01\x01", prev, 2), bytearray((11, 21, 31, 41)))
        self.assertEqual(silhouette.unfilter_row(3, b"\x00\x00\x00\x00", prev, 2), bytearray((5, 10, 17, 25)))
        self.assertEqual(silhouette.unfilter_row(4, b"\x00\x00\x00\x00", prev, 2), bytearray((10, 20, 30, 40)))


class Glb(unittest.TestCase):
    def test_cat_outline_is_the_cat_seen_from_the_side(self):
        tris = list(silhouette.triangles(*silhouette.read_glb(CAT)))
        ys = [p[1] for tri in tris for p in tri]
        self.assertAlmostEqual(min(ys), 0.0, delta=0.01)        # standing on the ground, not at the bind pose's origin offset
        mask, scale = silhouette.model_mask(tris)
        self.assertEqual(mask.height, silhouette.ROWS)
        self.assertGreater(mask.width / mask.height, 1.2)       # longer than tall with its tail
        head = sum(r >> (mask.width * 2 // 3) != 0 for r in mask.rows[:mask.height // 4])
        tail = sum(r & ((1 << mask.width // 6) - 1) != 0 for r in mask.rows[:mask.height // 4])
        self.assertGreater(head, 0)                             # the head is on the right (the front, +Z)
        self.assertGreater(tail, 0)                             # and the raised tail on the left
        self.assertAlmostEqual(silhouette.ROWS / scale, max(ys) - min(ys), places=3)

    def test_paths_outside_the_project_are_refused(self):
        with self.assertRaises(ValueError):
            silhouette.model_path(str(ROOT.parent / "x.glb"))


class CommandLine(unittest.TestCase):
    def run_quietly(self, argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return silhouette.main(argv)

    def test_a_named_reference_that_is_missing_fails(self):
        (ROOT / "out").mkdir(exist_ok=True)                    # git-ignored: absent on a fresh checkout
        with tempfile.TemporaryDirectory(dir=ROOT / "out") as tmp, mock.patch.object(silhouette, "OVERLAYS", Path(tmp)):
            self.assertEqual(self.run_quietly(["GN_CatTabby_faceted_01", "--ref", str(Path(tmp) / "nope.png")]), 1)

    def test_errors_exit_2(self):
        self.assertEqual(self.run_quietly(["GN_NoSuchModel_01"]), 2)
        self.assertEqual(self.run_quietly(["GN_CatTabby_faceted_01", "--ref", str(ROOT.parent / "x.png")]), 2)

    def test_all_takes_no_models(self):
        with self.assertRaises(SystemExit):
            self.run_quietly(["--all", "GN_CatTabby_faceted_01"])


if __name__ == "__main__":
    unittest.main()
