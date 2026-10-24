"""The category line above a model's details is a row of buttons, one per level, each jumping to that category in the grid."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "site" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "site" / "index.html").read_text(encoding="utf-8")


class Breadcrumbs(unittest.TestCase):
    def test_each_level_is_a_button_that_sets_the_category(self):
        self.assertRegex(APP, r"el\('button',\s*\{\s*class:\s*'crumb'")
        self.assertRegex(APP, r"state\.category\s*=\s*segs\.slice\(0,\s*i\s*\+\s*1\)\.join\('/'\)")

    def test_the_line_is_not_set_as_plain_text_any_more(self):
        self.assertNotRegex(APP, r"\$\('v-type'\)\.textContent")

    def test_the_container_is_a_labelled_nav(self):
        self.assertRegex(HTML, r'<nav id="v-type"[^>]*aria-label="Category"')


if __name__ == "__main__":
    unittest.main()
