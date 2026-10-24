"""tools/check_site.py: it passes on the real site, and it fails on each kind of damage."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_site  # noqa: E402

SITE = ROOT / "site"
KEEP = ("GI_Dresser_01", "GP_Farmer_01", "GI_Fridge_01", "GI_Fridge_Damaged_01")


class RealSite(unittest.TestCase):
    def test_the_committed_site_is_consistent(self):
        self.assertEqual(check_site.check(SITE), [])

    def test_the_manifest_has_the_expected_shape(self):
        doc = json.loads((SITE / "manifest.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(doc["assets"]), 50)
        cats = {a["type"].split("/")[0] for a in doc["assets"]}
        for want in ("vehicles", "animals", "people", "furniture", "appliances", "food", "farm"):
            self.assertIn(want, cats)
        self.assertTrue(any(a["interactive"] for a in doc["assets"]))
        self.assertTrue(any(a["clips"] for a in doc["assets"]))
        self.assertTrue(any(a["variants"] for a in doc["assets"]))


class Damage(unittest.TestCase):
    """Copy a few models and the page into a temp folder, break one thing, and expect that thing to be reported."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for name in ("index.html", "app.js", "viewer.js", "style.css"):
            shutil.copy(SITE / name, self.tmp / name)
        (self.tmp / "vendor").mkdir()
        shutil.copytree(SITE / "vendor" / "three", self.tmp / "vendor" / "three")
        self.doc = json.loads((SITE / "manifest.json").read_text(encoding="utf-8"))
        use = {a["id"]: a for a in self.doc["assets"]}
        self.doc["assets"] = [use[i] for i in KEEP]
        for a in self.doc["assets"]:
            a["variants"] = [v for v in a["variants"] if v in KEEP]
            for rel in (a["glb"], a["thumb"], a.get("interactions")):
                if not rel:
                    continue
                (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(SITE / rel, self.tmp / rel)
        self.write()

    def write(self):
        (self.tmp / "manifest.json").write_text(json.dumps(self.doc), encoding="utf-8")

    def problems(self):
        self.write()
        return check_site.check(self.tmp)

    def entry(self, aid):
        return next(a for a in self.doc["assets"] if a["id"] == aid)

    def test_the_copy_is_fine(self):
        self.assertEqual(self.problems(), [])

    def test_duplicate_id(self):
        self.doc["assets"].append(dict(self.entry("GI_Dresser_01")))
        self.assertTrue(any("duplicate id" in p for p in self.problems()))

    def test_a_blended_material_must_be_the_glass_one(self):
        a = self.entry("GI_Dresser_01")
        doc, _ = check_site.read_glb(self.tmp / a["glb"])
        for name, mode, bad in (("GlobalPaletteGlass", "BLEND", False), ("GlobalPalette", "BLEND", True), ("GlobalPaletteGlass", "OPAQUE", True)):
            doc["materials"] = [dict(name=name, alphaMode=mode)]
            errs = []
            check_site.check_against_glb(a, doc, errs.append)
            self.assertEqual(any("blended" in e or "opaque" in e for e in errs), bad, (name, mode))

    def test_missing_interactions_file(self):
        (self.tmp / self.entry("GI_Fridge_01")["interactions"]).unlink()
        self.assertTrue(any("GI_Fridge_01.interactions.json does not exist" in p for p in self.problems()))

    def test_interactions_file_of_another_model(self):
        path = self.tmp / self.entry("GI_Fridge_01")["interactions"]
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["id"] = "GI_Dresser_01"
        path.write_text(json.dumps(doc), encoding="utf-8")
        self.assertTrue(any("id is 'GI_Dresser_01'" in p for p in self.problems()))

    def test_light_count_that_disagrees(self):
        self.entry("GI_Fridge_01")["lights"] = 3
        self.assertTrue(any("working lights" in p for p in self.problems()))

    def test_missing_glb(self):
        (self.tmp / self.entry("GI_Dresser_01")["glb"]).unlink()
        self.assertTrue(any("models/GI_Dresser_01.glb does not exist" in p for p in self.problems()))

    def test_missing_thumbnail(self):
        (self.tmp / self.entry("GI_Dresser_01")["thumb"]).unlink()
        self.assertTrue(any("thumbs/GI_Dresser_01.png does not exist" in p for p in self.problems()))

    def test_wrong_thumbnail_size(self):
        (self.tmp / self.entry("GI_Dresser_01")["thumb"]).write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 8 + (10).to_bytes(4, "big") * 2)
        self.assertTrue(any("256 x 256" in p for p in self.problems()))

    def test_a_part_that_is_not_a_node(self):
        self.entry("GI_Dresser_01")["parts"]["Drawer9"] = self.entry("GI_Dresser_01")["parts"]["Drawer1"]
        self.assertTrue(any("Drawer9 has no node" in p for p in self.problems()))

    def test_a_pivot_that_is_not_where_the_node_is(self):
        self.entry("GI_Fridge_01")["parts"]["Door"]["pivot"] = [0.35, 0.37, 0.645]       # the unconverted Blender order
        self.assertTrue(any("pivot" in p and "GLB node" in p for p in self.problems()))

    def test_wrong_triangle_count(self):
        self.entry("GI_Dresser_01")["triangles"] += 1
        self.assertTrue(any("triangles" in p for p in self.problems()))

    def test_clips_that_the_glb_does_not_have(self):
        self.entry("GP_Farmer_01")["clips"].append("Dance")
        self.assertTrue(any("clips" in p for p in self.problems()))

    def test_rigged_flag_must_match(self):
        self.entry("GI_Dresser_01")["rigged"] = True
        self.assertTrue(any("rigged" in p for p in self.problems()))

    def test_bad_type_and_tag(self):
        self.entry("GI_Dresser_01")["type"] = "Furniture"
        self.entry("GI_Dresser_01")["tags"].append("Not A Tag")
        p = self.problems()
        self.assertTrue(any("category path" in x for x in p))
        self.assertTrue(any("lowercase word" in x for x in p))

    def test_missing_field(self):
        del self.entry("GI_Dresser_01")["size"]
        self.assertTrue(any("missing field size" in p for p in self.problems()))

    def test_variant_that_does_not_exist_or_is_one_way(self):
        self.entry("GI_Fridge_01")["variants"] = ["GI_Nothing_01"]
        self.assertTrue(any("not in the manifest" in p for p in self.problems()))
        self.entry("GI_Fridge_01")["variants"] = ["GI_Fridge_Damaged_01"]
        self.entry("GI_Fridge_Damaged_01")["variants"] = []
        self.assertTrue(any("does not list it back" in p for p in self.problems()))

    def test_page_that_refers_to_a_missing_file(self):
        (self.tmp / "style.css").unlink()
        self.assertTrue(any("style.css" in p for p in self.problems()))

    def test_page_missing_an_element_the_script_needs(self):
        html = (self.tmp / "index.html").read_text(encoding="utf-8").replace('id="search"', 'id="searchbox"')
        (self.tmp / "index.html").write_text(html, encoding="utf-8")
        self.assertTrue(any("#search" in p for p in self.problems()))

    def test_unparsable_manifest(self):
        (self.tmp / "manifest.json").write_text("{", encoding="utf-8")
        self.assertTrue(any("manifest.json" in p for p in check_site.check(self.tmp)))


if __name__ == "__main__":
    unittest.main()
