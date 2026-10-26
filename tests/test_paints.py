"""Colour variants as a palette swap: the declared paints resolve, a different shape is refused, and the manifest and checker accept the result."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import catalog  # noqa: E402
import check_site  # noqa: E402
import make_manifest as mm  # noqa: E402
import paints  # noqa: E402

MODELS = ROOT / "site" / "models"
ENTRIES = paints.palette_entries()


class Paints(unittest.TestCase):
    def test_every_declared_paint_resolves(self):
        for base, spec in catalog.PAINTS.items():
            self.assertIn(base, catalog.ASSETS)
            parts, ps = paints.resolve(spec, ENTRIES)
            self.assertGreaterEqual(len(ps), 2, base)
            self.assertEqual(ps[0]["swap"], {})
            self.assertEqual(len({p["name"] for p in ps}), len(ps), base)

    def test_folded_models_are_not_models_any_more(self):
        for base, spec in catalog.PAINTS.items():
            for name, p in spec["presets"].items():
                if p.get("was"):
                    self.assertNotIn(p["was"], catalog.ASSETS, f"{base} {name}")
                    self.assertFalse((MODELS / f"{p['was']}.glb").exists(), p["was"])

    def test_declared_swaps_equal_what_the_glbs_say_while_they_exist(self):
        self.assertEqual(paints.check(), 0)

    def test_a_model_differs_from_a_wreck_by_shape_not_paint(self):
        with self.assertRaises(ValueError):
            paints.derive(MODELS / "GV_Sedan_01.glb", MODELS / "GV_Sedan_Damaged_01.glb", paints.palette())

    def test_unknown_swatch_part_or_colour_is_an_error(self):
        with self.assertRaises(ValueError):
            paints.resolve({"base": "A", "parts": {"Body": "no_such_swatch"}, "presets": {}}, ENTRIES)
        with self.assertRaises(ValueError):
            paints.resolve({"base": "A", "parts": {"Body": "cloth_red"}, "presets": {"B": {"set": {"Roof": "#000000"}}}}, ENTRIES)
        with self.assertRaises(ValueError):
            paints.resolve({"base": "A", "parts": {"Body": "cloth_red"}, "presets": {"B": {"set": {"Body": "purple-ish"}}}}, ENTRIES)

    def test_a_part_swatch_is_not_shared_with_another_part(self):
        for base, spec in catalog.PAINTS.items():
            sw = list(spec["parts"].values())
            self.assertEqual(len(set(sw)), len(sw), base)

    def test_themes_come_from_home_styles_and_only_name_real_swatches(self):
        th = paints.themes(ENTRIES)
        self.assertEqual(set(th), {"Modern", "Retro", "Damaged"})
        for theme, swap in th.items():
            self.assertTrue(swap, theme)
            for k, v in swap.items():
                self.assertLess(int(k), len(ENTRIES))
                self.assertRegex(v, r"^#[0-9A-F]{6}$")

    def test_a_themed_model_and_its_folded_styles(self):
        for base, styles in catalog.THEMED.items():
            self.assertIn(base, catalog.ASSETS)
            self.assertNotIn("Damaged", styles, "Damaged also drops parts and tilts: it stays a model")
            for theme, was in styles.items():
                self.assertIn(theme, paints.themes(ENTRIES))
                self.assertNotIn(was, catalog.ASSETS)
                self.assertFalse((MODELS / f"{was}.glb").exists(), was)

    def test_apply_themes_lists_the_styles_on_the_model_and_defines_them_once(self):
        from unittest import mock
        assets = [{"id": "A", "variants": ["A_Modern", "B"], "tags": ["x"]}, {"id": "B", "variants": ["A"], "tags": []}]
        doc = {}
        with mock.patch.object(catalog, "THEMED", {"A": {"Modern": "A_Modern"}}):
            mm.apply_themes(doc, assets, ENTRIES)
        self.assertEqual(set(doc["themes"]), {"Modern"})
        self.assertEqual(assets[0]["themes"], [{"name": "Modern", "was": "A_Modern"}])
        self.assertEqual(assets[0]["variants"], ["B"])
        self.assertEqual(assets[0]["tags"], ["modern", "x"])
        self.assertNotIn("themes", assets[1])

    def test_fridges_that_differ_in_design_have_their_own_builders(self):
        """The Modern and Retro fridges are different designs (French doors over a pull-out freezer; one rounded door), so they are @variant builders in
        interactive.py and not themes. The script needs Blender to run, so this reads it."""
        import ast
        tree = ast.parse((ROOT / "art" / "scripts" / "interactive.py").read_text(encoding="utf-8"))
        found = set()
        for fn in ast.walk(tree):
            if isinstance(fn, ast.FunctionDef):
                for dec in fn.decorator_list:
                    if isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "variant":
                        found.add(tuple(ast.literal_eval(x) for x in dec.args))
        self.assertLessEqual({("Fridge", "Modern"), ("Fridge", "Retro")}, found)
        self.assertNotIn("GI_Fridge_01", catalog.THEMED)

    def test_manifest_lists_the_paints_on_the_base(self):
        doc = json.loads((ROOT / "site" / "manifest.json").read_text())
        apple = next(a for a in doc["assets"] if a["id"] == "FD_Apple_01")
        self.assertEqual([p["name"] for p in apple["paints"]], ["Red", "Green", "Yellow", "Rotten"])
        self.assertEqual([p["part"] for p in apple["paintable"]], ["Skin", "Leaf"])
        self.assertIn("rotten", apple["tags"])
        self.assertFalse(any(a["id"] == "FD_Apple_Green_01" for a in doc["assets"]))

    def test_apply_paints_drops_variant_links_to_folded_models_and_adds_tags(self):
        assets = [{"id": "A", "variants": ["B", "GONE"], "tags": ["x"]}, {"id": "B", "variants": ["A"], "tags": []}]
        spec = {"base": "One", "parts": {"Body": "cloth_red"}, "presets": {"Two Tone": {"set": {"Body": "#112233"}}}}
        mm.apply_paints(assets, {"A": spec}, ENTRIES)
        self.assertEqual(assets[0]["variants"], ["B"])
        self.assertEqual([p["name"] for p in assets[0]["paints"]], ["One", "Two Tone"])
        self.assertEqual(assets[0]["tags"], ["one", "two-tone", "x"])
        self.assertNotIn("paints", assets[1])

    def test_checker_rejects_bad_paints(self):
        errs = []
        part = {"part": "Body", "swatch": 3, "hex": "#000000"}
        check_site.check_paints({"paintable": [part], "paints": [{"name": "A", "hex": "#000000", "swap": {}}, {"name": "B", "hex": "#111111", "swap": {"9": "#FFFFFF"}}]}, errs.append)
        self.assertTrue(errs)          # swatch 9 is not a paintable part
        errs.clear()
        check_site.check_paints({"paintable": [part], "paints": [{"name": "A", "hex": "#000000", "swap": {}}, {"name": "B", "hex": "#111111", "swap": {"3": "#FFFFFF"}}]}, errs.append)
        self.assertEqual(errs, [])


class AutoColours(unittest.TestCase):
    """A model with no entry in catalog.PAINTS still has colours to change: its biggest swatches, the main one first."""

    def parts(self, model):
        return paints.auto_parts(MODELS / f"{model}.glb", ENTRIES)

    def test_the_main_colour_is_the_body_not_the_trim(self):
        self.assertEqual(self.parts("GV_Taxi_Yellow_01")[0]["hex"], "#E0B83A")          # yellow, though black covers about as much
        self.assertEqual(self.parts("GN_Cow_faceted_01")[0]["hex"], "#E6E2D6")          # white: nothing coloured covers half as much
        self.assertNotEqual(self.parts("GP_Waitress_01")[0]["hex"], "#C58C65")          # her uniform, not her skin

    def test_no_glowing_or_see_through_swatch_is_offered(self):
        names = {i: n for i, (n, _) in enumerate(ENTRIES)}
        for a in json.loads((ROOT / "site" / "manifest.json").read_text())["assets"]:
            for p in a.get("paintable", []):
                self.assertFalse(names[p["swatch"]].startswith(("glow_", "clear_")), a["id"])
                self.assertLessEqual(len(a["paintable"]), paints.MAX_PARTS, a["id"])

    def test_a_model_without_presets_gets_parts_only(self):
        assets = [{"id": "GV_Taxi_Yellow_01", "variants": [], "tags": []}, {"id": "NO_SUCH_MODEL", "variants": [], "tags": []}]
        mm.apply_paints(assets, {}, ENTRIES, MODELS)
        self.assertEqual(assets[0]["paintable"][0]["part"], "Main")
        self.assertNotIn("paints", assets[0])
        self.assertNotIn("paintable", assets[1])

    def test_the_manifest_has_the_common_colours_and_most_models_are_paintable(self):
        doc = json.loads((ROOT / "site" / "manifest.json").read_text())
        self.assertEqual([c["name"] for c in doc["palette"]["common"]], [n for n, _ in paints.COMMON])
        names = {n for n, _ in paints.COMMON}
        self.assertEqual(doc["palette"]["realistic"], paints.REALISTIC)
        for cat, real in paints.REALISTIC.items():
            self.assertTrue(real and set(real) <= names, cat)
        paintable = [a for a in doc["assets"] if a.get("paintable")]
        self.assertGreaterEqual(len(paintable), len(doc["assets"]) - 3)

    def test_the_checker_accepts_parts_without_presets_and_rejects_presets_without_parts(self):
        errs = []
        check_site.check_paints({"paintable": [{"part": "Main", "swatch": 3, "hex": "#000000"}]}, errs.append)
        self.assertEqual(errs, [])
        check_site.check_paints({"paints": [{"name": "A", "hex": "#000000", "swap": {}}, {"name": "B", "hex": "#111111", "swap": {"3": "#FFFFFF"}}]}, errs.append)
        self.assertTrue(errs)


class PartNames(unittest.TestCase):
    """art/data/part_names.json names the secondary colours of a model after the area they colour (Handle, Tyres) instead of the swatch (Metal dark)."""
    NAMES = paints.part_names()

    def test_every_entry_names_a_real_model_and_real_swatches(self):
        swatches = {n for n, _ in ENTRIES}
        for aid, mapping in self.NAMES.items():
            self.assertIn(aid, catalog.ASSETS, aid)
            self.assertNotIn(aid, catalog.PAINTS, f"{aid}: its parts are named in catalog.PAINTS")
            for sw, name in mapping.items():
                if sw != "$main":                   # "$main" names the first part, the model's main colour
                    self.assertIn(sw, swatches, f"{aid}: {sw}")
                self.assertTrue(name.strip() and name != "Main", f"{aid}: {sw} -> {name!r}")
            self.assertEqual(len(set(mapping.values())), len(mapping), f"{aid}: two swatches with the same part name")

    def test_a_lone_main_part_has_a_name_of_its_own(self):
        """The models with a single colour have no secondary part to tell it apart from, so they are named after what the colour covers (Case, Fur, Skin)."""
        doc = json.loads((ROOT / "site" / "manifest.json").read_text(encoding="utf-8"))
        for a in doc["assets"]:
            if len(a.get("paintable") or []) == 1:
                self.assertNotEqual(a["paintable"][0]["part"], "Main", f"{a['id']}: add \"$main\": \"<what the colour covers>\" for it to art/data/part_names.json")

    def test_the_manifest_uses_them(self):
        doc = json.loads((ROOT / "site" / "manifest.json").read_text(encoding="utf-8"))
        parts = {a["id"]: {ENTRIES[p["swatch"]][0]: p["part"] for p in a.get("paintable", [])[1:]} for a in doc["assets"]}
        first = {a["id"]: (a.get("paintable") or [{}])[0].get("part") for a in doc["assets"]}
        counts = {a["id"]: a.get("paintable") or [] for a in doc["assets"]}
        for aid, mapping in self.NAMES.items():
            self.assertIn(aid, parts, f"{aid} is not in the manifest")
            if "$main" in mapping:
                self.assertEqual(len(counts[aid]), 1, f"{aid}: '$main' is only for models with a single part (a model with several keeps Main)")
                self.assertEqual(first[aid], mapping["$main"], f"{aid}: first part")
            for sw, name in ((k, v) for k, v in mapping.items() if k != "$main"):
                self.assertIn(sw, parts[aid], f"{aid}: {sw} is not one of the model's secondary parts, so the entry does nothing")
                self.assertEqual(parts[aid][sw], name, f"{aid}: {sw}")

    def test_part_names_do_not_repeat_within_a_model(self):
        doc = json.loads((ROOT / "site" / "manifest.json").read_text(encoding="utf-8"))
        for a in doc["assets"]:
            labels = [p["part"] for p in a.get("paintable", [])]
            self.assertEqual(len(labels), len(set(labels)), a["id"])


if __name__ == "__main__":
    unittest.main()
