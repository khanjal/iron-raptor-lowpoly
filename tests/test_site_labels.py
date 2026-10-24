"""The colour picker labels every box with its part's own name, also when a model has only one part (Body, Wings, Fruit), never a generic text."""
import re
import unittest
from pathlib import Path

APP = (Path(__file__).resolve().parents[1] / "site" / "app.js").read_text(encoding="utf-8")


class PaintLabels(unittest.TestCase):
    def test_a_single_part_keeps_its_name(self):
        self.assertNotIn("Any colour", APP)
        self.assertIsNotNone(re.search(r"el\('span', \{ text: part\.part \}\)", APP), "the paint-part label should be the part's own name")


if __name__ == "__main__":
    unittest.main()
