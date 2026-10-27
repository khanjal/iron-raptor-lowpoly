"""tools/compare_builds.py: byte-identical files, files that differ only in vertex and index order, files that really differ (a position, a UV, a flipped face,
an animation key, an embedded image), a model in only one build, an unreadable file, and a missing or empty build."""

import contextlib
import io
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


def pack(code, values):
    return b"".join(struct.pack("<" + code * len(v), *v) for v in values)


def make_glb(positions, indices, name="Part", uvs=None, times=None, image=None):
    """A GLB with one mesh (float positions VEC3, optional float UVs VEC2, unsigned short indices), optionally an animation time accessor and an embedded image."""
    chunks = [("pos", pack("f", positions)), ("idx", pack("H", [(i,) for i in indices]))]
    if uvs is not None:
        chunks.append(("uv", pack("f", uvs)))
    if times is not None:
        chunks.append(("time", pack("f", [(t,) for t in times])))
    if image is not None:
        chunks.append(("img", image))
    body, views, offsets = b"", [], {}
    for key, data in chunks:
        offsets[key] = len(views)
        views.append({"buffer": 0, "byteOffset": len(body), "byteLength": len(data)})
        body += data + b"\x00" * (-len(data) % 4)
    accessors = [{"bufferView": offsets["pos"], "componentType": 5126, "count": len(positions), "type": "VEC3"},
                 {"bufferView": offsets["idx"], "componentType": 5123, "count": len(indices), "type": "SCALAR"}]
    attributes = {"POSITION": 0}
    if uvs is not None:
        attributes["TEXCOORD_0"] = len(accessors)
        accessors.append({"bufferView": offsets["uv"], "componentType": 5126, "count": len(uvs), "type": "VEC2"})
    if times is not None:
        accessors.append({"bufferView": offsets["time"], "componentType": 5126, "count": len(times), "type": "SCALAR"})
    doc = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(body)}], "bufferViews": views, "accessors": accessors,
           "meshes": [{"name": name, "primitives": [{"attributes": attributes, "indices": 1}]}]}
    js = json.dumps(doc).encode()
    js += b" " * (-len(js) % 4)
    return (b"glTF" + struct.pack("<III", 2, 12 + 8 + len(js) + 8 + len(body), len(js)) + struct.pack("<I", 0x4E4F534A) + js
            + struct.pack("<II", len(body), 0x004E4942) + body)


SQUARE = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]
UVS = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
TWO_TRIANGLES = [0, 1, 2, 0, 2, 3]


class CompareFolders(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)
        self.a, self.b = self.root / "a", self.root / "b"
        for side in (self.a, self.b):
            side.mkdir()

    def put(self, side, name, data):
        (side / name).write_bytes(data)

    def compare(self):
        return compare_builds.compare_folder(self.a, self.b, "*.glb", compare_builds.same_geometry)

    def test_identical_files(self):
        glb = make_glb(SQUARE, TWO_TRIANGLES, uvs=UVS)
        self.put(self.a, "M.glb", glb)
        self.put(self.b, "M.glb", glb)
        self.assertEqual(self.compare()[compare_builds.IDENTICAL], ["M.glb"])

    def test_the_same_triangles_in_another_order_are_the_same_geometry(self):
        self.put(self.a, "M.glb", make_glb(SQUARE, TWO_TRIANGLES, uvs=UVS))
        order = [2, 0, 3, 1]                                   # vertices listed in another order, triangle corners rotated: the same two triangles
        shuffled = [SQUARE[i] for i in order]
        shuffled_uvs = [UVS[i] for i in order]
        remap = {old: new for new, old in enumerate(order)}
        indices = [remap[i] for i in (1, 2, 0, 2, 3, 0)]
        self.put(self.b, "M.glb", make_glb(shuffled, indices, uvs=shuffled_uvs))
        result = self.compare()
        self.assertEqual((result[compare_builds.IDENTICAL], result[compare_builds.SAME_GEOMETRY], result[compare_builds.DIFFERENT]), ([], ["M.glb"], []))

    def assert_different(self, glb_a, glb_b):
        self.put(self.a, "M.glb", glb_a)
        self.put(self.b, "M.glb", glb_b)
        self.assertEqual(self.compare()[compare_builds.DIFFERENT], ["M.glb"])

    def test_a_moved_vertex_is_a_difference(self):
        moved = [SQUARE[0], SQUARE[1], (1.0, 1.0, 0.001), SQUARE[3]]
        self.assert_different(make_glb(SQUARE, TWO_TRIANGLES), make_glb(moved, TWO_TRIANGLES))

    def test_a_changed_uv_is_a_difference(self):
        other = [UVS[0], UVS[1], (0.5, 1.0), UVS[3]]
        self.assert_different(make_glb(SQUARE, TWO_TRIANGLES, uvs=UVS), make_glb(SQUARE, TWO_TRIANGLES, uvs=other))

    def test_a_flipped_face_is_a_difference(self):
        self.assert_different(make_glb(SQUARE, TWO_TRIANGLES), make_glb(SQUARE, [0, 2, 1, 0, 2, 3]))

    def test_a_renamed_mesh_is_a_difference(self):
        self.assert_different(make_glb(SQUARE, TWO_TRIANGLES, name="Door"), make_glb(SQUARE, TWO_TRIANGLES, name="Lid"))

    def test_a_changed_animation_key_is_a_difference(self):
        self.assert_different(make_glb(SQUARE, TWO_TRIANGLES, times=[0.0, 1.0]), make_glb(SQUARE, TWO_TRIANGLES, times=[0.0, 1.5]))

    def test_a_changed_embedded_image_is_a_difference(self):
        self.assert_different(make_glb(SQUARE, TWO_TRIANGLES, image=b"\x89PNG-a"), make_glb(SQUARE, TWO_TRIANGLES, image=b"\x89PNG-b"))

    def test_an_unreadable_file_is_a_difference(self):
        self.assert_different(make_glb(SQUARE, TWO_TRIANGLES), make_glb(SQUARE, TWO_TRIANGLES)[:60])

    def test_a_model_in_one_build_only(self):
        self.put(self.a, "A.glb", make_glb(SQUARE, [0, 1, 2]))
        self.put(self.b, "B.glb", make_glb(SQUARE, [0, 1, 2]))
        result = self.compare()
        self.assertEqual((result[compare_builds.ONLY_FIRST], result[compare_builds.ONLY_SECOND]), (["A.glb"], ["B.glb"]))


class Main(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(dir=ROOT / ".claude"))     # inside the project: main() refuses folders outside it
        self.addCleanup(shutil.rmtree, self.root, True)
        self.a, self.b = self.root / "a", self.root / "b"
        for side in (self.a, self.b):
            (side / "site" / "models").mkdir(parents=True)
            (side / "out" / "meta").mkdir(parents=True)
            (side / "out" / "meta" / "M.json").write_text('{"triangles": 1}', encoding="utf-8")      # a build writes these beside the GLBs

    def run_main(self, first, second):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return compare_builds.main([str(first), str(second)])

    def test_success_failure_empty_and_outside(self):
        for side in (self.a, self.b):
            (side / "site" / "models" / "M.glb").write_bytes(make_glb(SQUARE, [0, 1, 2]))
        self.assertEqual(self.run_main(self.a, self.b), 0)
        (self.b / "site" / "models" / "M.glb").write_bytes(make_glb(SQUARE, [0, 1, 3]))
        self.assertEqual(self.run_main(self.a, self.b), 1)
        self.assertEqual(self.run_main(self.root / "missing1", self.root / "missing2"), 2)      # no build in either tree is not a pass
        empty_a, empty_b = self.root / "empty_a", self.root / "empty_b"
        for side in (empty_a, empty_b):
            (side / "site" / "models").mkdir(parents=True)
        self.assertEqual(self.run_main(empty_a, empty_b), 2)
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside, True)
        self.assertEqual(self.run_main(outside, outside), 2)

    def test_interactions_json_is_compared_too(self):
        for side in (self.a, self.b):
            (side / "site" / "models" / "M.glb").write_bytes(make_glb(SQUARE, [0, 1, 2]))
            (side / "art" / "data").mkdir(parents=True)
            (side / "art" / "data" / "interactions.json").write_text('{"door": {"limit": 90}}', encoding="utf-8")
        self.assertEqual(self.run_main(self.a, self.b), 0)
        (self.b / "art" / "data" / "interactions.json").write_text('{"door": {"limit": 100}}', encoding="utf-8")
        self.assertEqual(self.run_main(self.a, self.b), 1)


if __name__ == "__main__":
    unittest.main()
