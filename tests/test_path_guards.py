"""The command-line tools and scripts that take a path refuse one outside the project (or, for the GLB rewriter Blender calls, one that is not a .glb)."""

import io
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "art" / "scripts"))
import audit_layout
import glbinfo
import inventory
import stamp_glb

OUTSIDE = Path(tempfile.mkdtemp()).resolve()


def quiet(fn, *args):
    with redirect_stderr(io.StringIO()):
        return fn(*args)


class PathGuards(unittest.TestCase):
    def test_glbinfo_reads_inside_and_refuses_outside(self):
        glb = next((ROOT / "site" / "models").glob("*.glb"))
        doc, raw = glbinfo.read(glb)
        self.assertIn("asset", doc)
        outside = OUTSIDE / "x.glb"
        outside.write_bytes(raw)
        with self.assertRaises(ValueError):
            glbinfo.read(outside)

    def test_stamp_refuses_a_file_outside_the_project_and_leaves_it_alone(self):
        outside = OUTSIDE / "t.glb"
        outside.write_bytes(b"unchanged")
        with self.assertRaises(ValueError):
            stamp_glb.stamp(outside)
        self.assertEqual(outside.read_bytes(), b"unchanged")

    def test_inventory_refuses_an_output_or_dev_world_outside_the_project(self):
        self.assertEqual(quiet(inventory.main, ["--out", str(OUTSIDE / "inventory.md")]), 2)
        self.assertEqual(quiet(inventory.main, ["--out", str(ROOT / "docs" / "assets" / "inventory.md"), "--check", "--dev-world", str(OUTSIDE / "w.json")]), 2)
        self.assertFalse((OUTSIDE / "inventory.md").exists())
        with self.assertRaises(ValueError):
            inventory.load_dev_world(OUTSIDE / "w.json")

    def test_audit_layout_refuses_a_dump_outside_the_project(self):
        dump = OUTSIDE / "layout.json"
        dump.write_text("{}", encoding="utf-8")
        self.assertEqual(quiet(audit_layout.main, [str(dump)]), 2)
        self.assertEqual(audit_layout.layout_path(None), (ROOT / audit_layout.DEFAULT_JSON).resolve())

    def test_strip_prefix_only_rewrites_glb_files(self):
        stubs = [n for n in ("bpy", "bmesh") if n not in sys.modules]
        for n in stubs:
            sys.modules[n] = types.ModuleType(n)
        try:
            import common
            text = OUTSIDE / "notes.txt"
            text.write_bytes(b"unchanged")
            with self.assertRaises(ValueError):
                common._strip_prefix(text)
            self.assertEqual(text.read_bytes(), b"unchanged")
        finally:
            for n in stubs:
                sys.modules.pop(n, None)
            sys.modules.pop("common", None)


if __name__ == "__main__":
    unittest.main()
