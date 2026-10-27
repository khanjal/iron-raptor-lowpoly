"""tools/compare_builds.py: byte-identical files, files that differ only in vertex and index order, files that really differ, and a model in only one build."""

import json
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import compare_builds


def make_glb(positions, indices, name="Part"):
    """A GLB with one mesh: float positions (VEC3) and unsigned short indices."""
    pos_bytes = b"".join(struct.pack("<3f", *p) for p in positions)
    idx_bytes = b"".join(struct.pack("<H", i) for i in indices)
    idx_bytes += b"\x00" * (-len(idx_bytes) % 4)
    body = pos_bytes + idx_bytes
    doc = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": len(body)}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(pos_bytes)}, {"buffer": 0, "byteOffset": len(pos_bytes), "byteLength": len(indices) * 2}],
        "accessors": [{"bufferView": 0, "componentType": 5126, "count": len(positions), "type": "VEC3"},
                      {"bufferView": 1, "componentType": 5123, "count": len(indices), "type": "SCALAR"}],
        "meshes": [{"name": name, "primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
    }
    js = json.dumps(doc).encode()
    js += b" " * (-len(js) % 4)
    return (b"glTF" + struct.pack("<III", 2, 12 + 8 + len(js) + 8 + len(body), len(js)) + struct.pack("<I", 0x4E4F534A) + js
            + struct.pack("<II", len(body), 0x004E4942) + body)


SQUARE = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]


class CompareBuilds(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)
        self.a, self.b = self.root / "a", self.root / "b"
        for side in (self.a, self.b):
            (side / "site" / "models").mkdir(parents=True)
            (side / "out" / "meta").mkdir(parents=True)

    def put(self, side, name, data):
        (side / "site" / "models" / name).write_bytes(data)

    def compare(self):
        return compare_builds.compare_folder(self.a / "site" / "models", self.b / "site" / "models", "*.glb", compare_builds.same_geometry)

    def test_identical_files(self):
        glb = make_glb(SQUARE, [0, 1, 2, 0, 2, 3])
        self.put(self.a, "M.glb", glb)
        self.put(self.b, "M.glb", glb)
        self.assertEqual(self.compare()["identical"], ["M.glb"])

    def test_the_same_triangles_in_another_order_are_the_same_geometry(self):
        self.put(self.a, "M.glb", make_glb(SQUARE, [0, 1, 2, 0, 2, 3]))
        # vertices listed in another order, triangles and their corners shuffled: still the same two triangles
        shuffled = [SQUARE[2], SQUARE[0], SQUARE[3], SQUARE[1]]
        self.put(self.b, "M.glb", make_glb(shuffled, [2, 0, 1, 3, 1, 0]))
        result = self.compare()
        self.assertEqual((result["identical"], result["same_geometry"], result["different"]), ([], ["M.glb"], []))

    def test_a_moved_vertex_is_a_difference(self):
        self.put(self.a, "M.glb", make_glb(SQUARE, [0, 1, 2, 0, 2, 3]))
        moved = [SQUARE[0], SQUARE[1], (1.0, 1.0, 0.001), SQUARE[3]]
        self.put(self.b, "M.glb", make_glb(moved, [0, 1, 2, 0, 2, 3]))
        self.assertEqual(self.compare()["different"], ["M.glb"])

    def test_a_renamed_mesh_is_a_difference(self):
        self.put(self.a, "M.glb", make_glb(SQUARE, [0, 1, 2, 0, 2, 3], name="Door"))
        self.put(self.b, "M.glb", make_glb(SQUARE, [0, 1, 2, 0, 2, 3], name="Lid"))
        self.assertEqual(self.compare()["different"], ["M.glb"])

    def test_a_model_in_one_build_only(self):
        self.put(self.a, "A.glb", make_glb(SQUARE, [0, 1, 2]))
        self.put(self.b, "B.glb", make_glb(SQUARE, [0, 1, 2]))
        result = self.compare()
        self.assertEqual((result["only_a"], result["only_b"]), (["A.glb"], ["B.glb"]))

    def test_main_reports_success_and_failure_and_refuses_a_folder_outside_the_project(self):
        project = ROOT / ".claude" / "worktrees" / "compare_builds_test"
        shutil.rmtree(project, ignore_errors=True)
        self.addCleanup(shutil.rmtree, project, True)
        for side in ("a", "b"):
            (project / side / "site" / "models").mkdir(parents=True)
            (project / side / "out" / "meta").mkdir(parents=True)
            (project / side / "site" / "models" / "M.glb").write_bytes(make_glb(SQUARE, [0, 1, 2]))
        self.assertEqual(compare_builds.main([str(project / "a"), str(project / "b")]), 0)
        (project / "b" / "site" / "models" / "M.glb").write_bytes(make_glb(SQUARE, [0, 1, 3]))
        self.assertEqual(compare_builds.main([str(project / "a"), str(project / "b")]), 1)
        self.assertEqual(compare_builds.main([str(self.a), str(self.b)]), 2)


if __name__ == "__main__":
    unittest.main()
