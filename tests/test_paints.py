"""Colour variants as a palette swap: the swap works out right, a different shape is refused, and the manifest and checker accept the result."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_site  # noqa: E402
import make_manifest as mm  # noqa: E402
import paints  # noqa: E402

MODELS = ROOT / "site" / "models"


class Paints(unittest.TestCase):
    def test_palette_has_the_swatches_the_record_uses(self):
        pal = paints.palette()
        self.assertGreater(len(pal), 100)
        for base, spec in json.loads((ROOT / "art" / "data" / "paints.json").read_text()).items():
            for sw in spec["paints"].values():
                for k, v in sw.items():
                    self.assertLess(int(k), len(pal))
                    self.assertRegex(v, r"^#[0-9A-F]{6}$")

    def test_a_model_differs_from_a_wreck_by_shape_not_paint(self):
        with self.assertRaises(ValueError):
            paints.derive(MODELS / "GV_Sedan_Blue_01.glb", MODELS / "GV_Sedan_Red_Damaged_01.glb", paints.palette())

    def test_a_model_against_itself_needs_no_swap(self):
        self.assertEqual(paints.derive(MODELS / "GV_Sedan_Blue_01.glb", MODELS / "GV_Sedan_Blue_01.glb", paints.palette()), {})

    def test_manifest_lists_each_paint_once_on_the_base(self):
        doc = json.loads((ROOT / "site" / "manifest.json").read_text())
        sedan = next(a for a in doc["assets"] if a["id"] == "GV_Sedan_Blue_01")
        self.assertEqual([p["name"] for p in sedan["paints"]], ["Blue", "Red"])
        self.assertEqual(sedan["paints"][0]["swap"], {})
        self.assertFalse(any(a["id"] == "GV_Sedan_Red_01" for a in doc["assets"]))

    def test_apply_paints_drops_variant_links_to_folded_models(self):
        assets = [dict(id="A", variants=["B", "GONE"]), dict(id="B", variants=["A"])]
        mm.apply_paints(assets, {"A": dict(base="One", paints={"Two": {"3": "#112233"}})}, ["#000000"] * 5)
        self.assertEqual(assets[0]["variants"], ["B"])
        self.assertEqual([p["name"] for p in assets[0]["paints"]], ["One", "Two"])
        self.assertNotIn("paints", assets[1])

    def test_checker_rejects_bad_paints(self):
        errs = []
        check_site.check_paints(dict(paints=[dict(name="A", hex="#000000", swap={}), dict(name="A", hex="#000000", swap={"1": "#FFFFFF"})]), errs.append)
        self.assertTrue(errs)


if __name__ == "__main__":
    unittest.main()
