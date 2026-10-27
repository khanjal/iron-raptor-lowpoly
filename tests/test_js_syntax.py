"""The site's own JavaScript (and the thumbnail tool's) at least parses as an ES module (needs Node; skipped when it is not installed). A real browser run is a separate, heavier check."""
import shutil
import subprocess
import unittest
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
TOOLS = Path(__file__).resolve().parents[1] / "tools"


@unittest.skipUnless(shutil.which("node"), "Node is not installed")
class JsSyntax(unittest.TestCase):
    def test_modules_parse(self):
        for path in (SITE / "app.js", SITE / "viewer.js", SITE / "stress.js", TOOLS / "thumbs.js"):
            with self.subTest(path.name):
                r = subprocess.run(["node", "--input-type=module", "--check"], input=path.read_bytes(), capture_output=True)
                self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()
