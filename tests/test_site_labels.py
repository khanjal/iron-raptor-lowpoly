"""The colour picker labels every box with its part's own name, also when a model has only one part (Body, Wings, Fruit), never a generic text."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "site" / "app.js").read_text(encoding="utf-8")


class PaintLabels(unittest.TestCase):
    def test_a_single_part_keeps_its_name(self):
        self.assertNotIn("Any colour", APP)
        self.assertIsNotNone(re.search(r"el\('span',\s*\{\s*text:\s*part\.part\s*\}\)", APP), "the paint-part label should be the part's own name")

    def test_every_single_part_model_has_a_name_to_show(self):
        doc = json.loads((ROOT / "site" / "manifest.json").read_text(encoding="utf-8"))
        for a in doc["assets"]:
            parts = a.get("paintable") or []
            if len(parts) == 1:
                self.assertTrue(parts[0]["part"].strip(), a["id"])


if __name__ == "__main__":
    unittest.main()
