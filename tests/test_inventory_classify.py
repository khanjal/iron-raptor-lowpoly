"""inventory.classify splits a model's folders into (category, style, group); the style folders of Household, Decor and Interactive are a column of the parent's table."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "art" / "scripts"))
import inventory


class Classify(unittest.TestCase):
    def test_a_style_group_takes_its_style_folder_as_a_column(self):
        self.assertEqual(inventory.classify(("Global", "Household", "Retro", "x.fbx")), ("Global/Household", "Retro", ""))
        self.assertEqual(inventory.classify(("Global", "Decor", "Chair", "x.fbx")), ("Global/Decor", "base", "Chair"))

    def test_other_folders_are_a_group(self):
        self.assertEqual(inventory.classify(("Global", "Vehicles", "Sedan", "x.fbx")), ("Global/Vehicles", "", "Sedan"))

    def test_short_paths_do_not_fail(self):
        self.assertEqual(inventory.classify(("Global", "Animals", "x.fbx")), ("Global/Animals", "", ""))
        self.assertEqual(inventory.classify(("Global", "x.fbx")), ("Global", "", ""))
        self.assertEqual(inventory.classify(("x.fbx",)), ("", "", ""))


if __name__ == "__main__":
    unittest.main()
