"""The release zips carry a model's interactions file next to its GLB."""
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_release_zips as mrz  # noqa: E402


class Zips(unittest.TestCase):
    def test_the_interactions_file_goes_in_with_the_glb(self):
        with tempfile.TemporaryDirectory() as d:
            paths = mrz.build(d)
            with zipfile.ZipFile(next(p for p in paths if p.name.endswith("-all.zip"))) as z:
                names = set(z.namelist())
            self.assertIn("GI_Fridge_01.glb", names)
            self.assertIn("GI_Fridge_01.interactions.json", names)
            self.assertIn("GV_Police_Sheriff_01.interactions.json", names)      # a vehicle: doors, hood, trunk and wheels
            self.assertNotIn("GS_Baseball_01.interactions.json", names)         # no entry, no file


if __name__ == "__main__":
    unittest.main()
