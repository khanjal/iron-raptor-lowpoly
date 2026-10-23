"""tools/stamp_glb.py and tools/make_release_zips.py: the credit line goes into a GLB without changing anything else, and the zips hold what they should."""
import json
import re
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_site  # noqa: E402
import make_release_zips  # noqa: E402
import stamp_glb  # noqa: E402


def tiny_glb(doc, binary=b"\x01\x02\x03\x04"):
    body = json.dumps(doc).encode()
    body += b" " * (-len(body) % 4)
    return b"glTF" + struct.pack("<II", 2, 12 + 8 + len(body) + 8 + len(binary)) + struct.pack("<II", len(body), 0x4E4F534A) + body + struct.pack("<II", len(binary), 0x004E4942) + binary


class Stamp(unittest.TestCase):
    def test_adds_the_line_and_keeps_the_rest(self):
        raw = tiny_glb({"asset": {"version": "2.0"}, "nodes": [{"name": "A"}]})
        new = stamp_glb.stamp_bytes(raw)
        self.assertNotEqual(new, raw)
        path = Path(tempfile.mkdtemp()) / "t.glb"
        path.write_bytes(new)
        doc, err = check_site.read_glb(path)
        self.assertIsNone(err)
        self.assertEqual(doc["asset"], {"version": "2.0", "copyright": stamp_glb.COPYRIGHT})
        self.assertEqual(doc["nodes"], [{"name": "A"}])
        self.assertTrue(new.endswith(b"\x01\x02\x03\x04"))
        self.assertEqual(len(new) % 4, 0)

    def test_twice_changes_nothing(self):
        once = stamp_glb.stamp_bytes(tiny_glb({"asset": {"version": "2.0"}}))
        self.assertEqual(stamp_glb.stamp_bytes(once), once)

    def test_rejects_other_files(self):
        with self.assertRaises(ValueError):
            stamp_glb.stamp_bytes(b"not a glb at all, really not")

    def test_blender_export_uses_the_same_line(self):
        text = (ROOT / "art" / "scripts" / "common.py").read_text(encoding="utf-8")
        self.assertEqual(re.search(r'^GLB_COPYRIGHT = "([^"]+)"', text, re.M).group(1), stamp_glb.COPYRIGHT)


class Zips(unittest.TestCase):
    def test_all_and_per_category(self):
        out = Path(tempfile.mkdtemp())
        paths = {p.name: p for p in make_release_zips.build(out)}
        assets = json.loads((ROOT / "site" / "manifest.json").read_text(encoding="utf-8"))["assets"]
        with zipfile.ZipFile(paths["lowpoly-assets-glb-all.zip"]) as z:
            names = set(z.namelist())
        self.assertEqual({n for n in names if n.endswith(".glb")}, {a["id"] + ".glb" for a in assets})
        self.assertIn("CREDIT.txt", names)
        self.assertIn("LICENSE-MODELS", names)
        for cat in {a["type"].split("/")[0] for a in assets}:
            with zipfile.ZipFile(paths[f"lowpoly-assets-glb-{cat}.zip"]) as z:
                glbs = {n[:-4] for n in z.namelist() if n.endswith(".glb")}
            self.assertEqual(glbs, {a["id"] for a in assets if a["type"].startswith(cat + "/")})


if __name__ == "__main__":
    unittest.main()
