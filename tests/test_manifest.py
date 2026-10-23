"""The pure parts of the manifest builder: the Blender -> glTF axis conversion of the moving parts, and the entry builder."""
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_manifest as mm  # noqa: E402


def to_gltf_vec(v):
    """Blender (x, y, z) -> glTF (x, z, -y): the mapping the GLB exporter applies (+Y up)."""
    return [v[0], v[2], -v[1]]


def rot(axis, deg, v):
    """Rotate v about a unit axis by deg degrees (right-handed, Rodrigues)."""
    a = math.radians(deg)
    k = axis
    dot = sum(k[i] * v[i] for i in range(3))
    cross = [k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0]]
    return [v[i] * math.cos(a) + cross[i] * math.sin(a) + k[i] * dot * (1 - math.cos(a)) for i in range(3)]


class AxisConversion(unittest.TestCase):
    def test_point(self):
        self.assertEqual(mm.to_gltf([1, 2, 3]), [1, 3, -2])
        self.assertEqual(mm.to_gltf([0.35, -0.37, 0.645]), [0.35, 0.645, 0.37])   # the fridge door's pivot: front (-y) becomes +z

    def test_axes_match_the_point_mapping(self):
        for name, blender in (("x", [1, 0, 0]), ("y", [0, 1, 0]), ("z", [0, 0, 1])):
            self.assertEqual(mm.AXES[name], to_gltf_vec(blender), name)

    def test_a_blender_z_hinge_is_a_gltf_y_hinge(self):
        self.assertEqual(mm.AXES["z"], [0, 1, 0])
        self.assertEqual(mm.AXES["x"], [1, 0, 0])
        self.assertEqual(mm.AXES["y"], [0, 0, -1])

    def test_rotation_about_the_converted_axis_is_the_converted_rotation(self):
        # the mapping is a proper rotation (determinant +1), so turning a point by +theta about a Blender axis and converting the result
        # equals turning the converted point by +theta about the converted axis
        for name, blender in (("x", [1, 0, 0]), ("y", [0, 1, 0]), ("z", [0, 0, 1])):
            p = [0.3, -0.5, 0.7]
            for deg in (30, -110, 100):
                a = to_gltf_vec(rot(blender, deg, p))
                b = rot(mm.AXES[name], deg, to_gltf_vec(p))
                for i in range(3):
                    self.assertAlmostEqual(a[i], b[i], places=9, msg=f"{name} {deg}")

    def test_slide_towards_the_front_is_towards_plus_z(self):
        # a drawer slides along Blender y by limit -0.38 (out of the front, -y): in glTF that is +z, and axis * limit says the same
        move = [c * -0.38 for c in mm.AXES["y"]]
        self.assertEqual(move, [0.0, 0.0, 0.38])
        self.assertEqual(to_gltf_vec([0, -0.38, 0]), [0, 0, 0.38])

    def test_convert_part(self):
        p = mm.convert_part(dict(kind="hinge", axis="z", pivot=[0.35, -0.37, 0.645], limit=100, rest=0.0))
        self.assertEqual(p, dict(kind="hinge", axis=[0, 1, 0], pivot=[0.35, 0.645, 0.37], limit=100, rest=0.0))


class Entries(unittest.TestCase):
    meta = dict(triangles=180, bbox_min=[-0.35, -0.4275, 0.0], bbox_max=[0.35, 0.35, 1.8], rigged=False, clips=[], part_nodes={"Door": [0.35, -0.37, 0.645]})
    cat = dict(name="Fridge", type="appliances/kitchen/fridge", tags=["white", "kitchen", "white"], group="fridge")
    inter = dict(parts={"Door": dict(kind="hinge", axis="z", pivot=[0.35, -0.37, 0.645], limit=100, rest=0.0)})

    def test_size_is_width_height_depth(self):
        self.assertEqual(mm.size_of(self.meta), [0.7, 1.8, 0.777])

    def test_entry(self):
        e = mm.build_entry("GI_Fridge_01", self.cat, self.meta, self.inter, {"fridge": ["GI_Fridge_01", "GI_Fridge_Retro_01"]})
        self.assertEqual(e["tags"], ["kitchen", "white"])            # sorted, no duplicates
        self.assertTrue(e["interactive"])
        self.assertEqual(e["variants"], ["GI_Fridge_Retro_01"])      # not itself
        self.assertEqual(e["glb"], "models/GI_Fridge_01.glb")
        self.assertEqual(e["thumb"], "thumbs/GI_Fridge_01.png")
        self.assertEqual(e["parts"]["Door"]["pivot"], [0.35, 0.645, 0.37])

    def test_a_part_without_a_node_is_an_error(self):
        meta = dict(self.meta, part_nodes={})
        with self.assertRaises(ValueError):
            mm.build_entry("X", self.cat, meta, self.inter, {})

    def test_a_node_without_a_part_is_an_error(self):
        with self.assertRaises(ValueError):
            mm.build_entry("X", self.cat, self.meta, None, {})

    def test_a_static_model_has_no_parts_or_variants(self):
        meta = dict(self.meta, part_nodes={})
        e = mm.build_entry("X", dict(self.cat, group=None), meta, None, {})
        self.assertFalse(e["interactive"])
        self.assertEqual((e["parts"], e["variants"]), ({}, []))

    def test_variant_groups(self):
        g = mm.variant_groups({"a": dict(group="g"), "b": dict(group="g"), "c": dict(group=None)})
        self.assertEqual(g, {"g": ["a", "b"]})


class Interactions(unittest.TestCase):
    cat = dict(name="X", type="furniture/x", tags=["x"], group=None)
    meta = dict(rigged=False, triangles=10, bbox_min=[0, 0, 0], bbox_max=[1, 1, 1], part_nodes={}, clips=[])
    lamp = dict(emitters={"Light_Bulb": dict(kind="light", position=[0, 0, 1]), "Light_Dead": dict(kind="light", working=False),
                          "Sound_Buzz": dict(kind="sound")})

    def test_a_model_with_an_entry_points_at_its_file_and_counts_working_lights(self):
        e = mm.build_entry("X", self.cat, self.meta, self.lamp, {})
        self.assertEqual((e["interactions"], e["lights"]), ("models/X.interactions.json", 1))

    def test_a_model_without_an_entry_has_neither_field(self):
        e = mm.build_entry("X", self.cat, self.meta, None, {})
        self.assertNotIn("interactions", e)
        self.assertNotIn("lights", e)

    def test_sidecars_are_written_and_stale_ones_removed(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "GONE.interactions.json").write_text("{}")
            have = mm.write_sidecars(["X", "Y"], {"X": self.lamp}, d)
            self.assertEqual(have, {"X"})
            self.assertEqual([p.name for p in d.iterdir()], ["X.interactions.json"])
            doc = json.loads((d / "X.interactions.json").read_text(encoding="utf-8"))
            self.assertEqual((doc["id"], doc["space"]), ("X", "blender"))
            self.assertIn("Light_Bulb", doc["emitters"])


class Palette(unittest.TestCase):
    def test_glow_swatches_come_from_the_palette(self):
        glow = {g["name"]: g for g in mm.glow_swatches()}
        self.assertEqual(glow["glow_cyan"]["index"], 14)
        self.assertEqual(glow["glow_cyan"]["hex"], "#6FE8E0")
        self.assertTrue(all(g["name"].startswith("glow_") for g in glow.values()))


if __name__ == "__main__":
    unittest.main()
