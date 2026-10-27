"""The scripts that write a file at a path they are given refuse one they should not touch: stamp_glb and inventory --out stay inside the project, and the GLB rewriter Blender calls
only rewrites a .glb inside the export folder it was given."""

import io
import shutil
import struct
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "art" / "scripts"))
import inventory
import stamp_glb


def tiny_glb(name):
    body = b'{"asset":{"version":"2.0"},"nodes":[{"name":"%s"}]}' % name
    body += b" " * (-len(body) % 4)
    return b"glTF" + struct.pack("<III", 2, 20 + len(body), len(body)) + struct.pack("<I", 0x4E4F534A) + body


class PathGuards(unittest.TestCase):
    def setUp(self):
        self.outside = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.outside, True)

    def test_stamp_refuses_a_file_outside_the_project_and_leaves_it_alone(self):
        target = self.outside / "t.glb"
        target.write_bytes(b"unchanged")
        with self.assertRaises(ValueError):
            stamp_glb.stamp(target)
        self.assertEqual(target.read_bytes(), b"unchanged")

    def test_inventory_refuses_an_output_outside_the_project(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(inventory.main(["--out", str(self.outside / "inventory.md")]), 2)
        self.assertFalse((self.outside / "inventory.md").exists())

    def test_strip_prefix_only_rewrites_a_glb_inside_the_export_folder(self):
        stubs = [n for n in ("bpy", "bmesh") if n not in sys.modules]
        for n in stubs:
            sys.modules[n] = types.ModuleType(n)
        try:
            import common
            export = self.outside / "glb"
            export.mkdir()
            text = export / "notes.txt"
            text.write_bytes(b"unchanged")
            elsewhere = self.outside / "elsewhere.glb"
            elsewhere.write_bytes(b"unchanged")
            for bad in (text, elsewhere, export / ".." / "elsewhere.glb"):
                with self.assertRaises(ValueError):
                    common._strip_prefix(bad, export)
            self.assertEqual(text.read_bytes(), b"unchanged")
            self.assertEqual(elsewhere.read_bytes(), b"unchanged")
            ok = export / "ok.glb"
            ok.write_bytes(tiny_glb(b"P_Door"))
            common.plain = lambda name: name.removeprefix("P_")
            common._strip_prefix(ok, export)
            self.assertIn(b'"name":"Door"', ok.read_bytes())
        finally:
            for n in stubs:
                sys.modules.pop(n, None)
            sys.modules.pop("common", None)


if __name__ == "__main__":
    unittest.main()
