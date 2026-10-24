"""The textures that are not models: the palette image is current, and every ground texture the table names is there."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import palette_png  # noqa: E402


class Textures(unittest.TestCase):
    def test_the_palette_image_is_made_from_the_palette(self):
        self.assertEqual(palette_png.OUT.read_bytes(), palette_png.png_bytes(), "run python tools/palette_png.py")

    def test_every_ground_texture_in_the_table_exists_and_is_a_png(self):
        rows = json.loads((ROOT / "art" / "data" / "ground_surfaces.json").read_text(encoding="utf-8"))["surfaces"]
        self.assertGreater(len(rows), 20)
        for r in rows:
            f = ROOT / "textures" / "ground" / r["file"]
            self.assertTrue(f.is_file(), r["file"])
            self.assertEqual(f.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", r["file"])

    def test_no_texture_is_a_git_lfs_pointer(self):
        for f in (ROOT / "textures").rglob("*.png"):
            self.assertNotIn(b"git-lfs", f.read_bytes()[:64], f.name)


if __name__ == "__main__":
    unittest.main()
