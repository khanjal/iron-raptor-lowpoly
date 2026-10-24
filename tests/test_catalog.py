"""tools/catalog.py: what the slice contains, and the rules for types and tags."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import catalog  # noqa: E402

TYPE_RE = re.compile(r"^[a-z0-9-]+(/[a-z0-9-]+){2}$")        # three levels: category / group / kind
TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def built_ids():
    ids = []
    for g in catalog.BUILD.values():
        ids += g.get("ids") or list((g.get("people") or g.get("animals")).values())
    return ids


class Catalog(unittest.TestCase):
    def test_every_built_model_is_described_and_the_other_way_round(self):
        self.assertEqual(sorted(catalog.site_id(i) for i in built_ids()), sorted(catalog.ASSETS))

    def test_browser_ids_carry_no_paint_and_old_ids_are_aliases(self):
        for old, new in catalog.SITE_IDS.items():
            self.assertNotEqual(old, new)
            self.assertNotIn(new, built_ids())           # a browser id is never also a generator's name
            self.assertEqual(catalog.ALIASES[new], old)
            self.assertIn(new, catalog.ASSETS)
            self.assertNotIn(old, catalog.ASSETS)
        self.assertEqual(len(set(catalog.SITE_IDS.values())), len(catalog.SITE_IDS))

    def test_ids_are_unique(self):
        ids = built_ids()
        self.assertEqual(len(ids), len(set(ids)))

    def test_types_are_three_level_lowercase_paths(self):
        for aid, a in catalog.ASSETS.items():
            self.assertRegex(a["type"], TYPE_RE, aid)

    def test_tags_are_lowercase_words_without_duplicates(self):
        for aid, a in catalog.ASSETS.items():
            self.assertGreaterEqual(len(a["tags"]), 3, f"{aid} needs a few tags")
            self.assertEqual(len(a["tags"]), len(set(a["tags"])), aid)
            for t in a["tags"]:
                self.assertRegex(t, TAG_RE, f"{aid}: {t}")

    def test_every_object_says_its_condition(self):
        # the browser's Condition filter only works if each model carries one (animals, people and trees are living things: no condition)
        known = {"new", "damaged", "rotten", "fresh", "weathered"}
        for aid, a in catalog.ASSETS.items():
            if a["type"].split("/")[0] in ("animals", "people", "nature"):
                continue
            self.assertTrue(known & set(a["tags"]), f"{aid} has no condition tag ({sorted(known)})")

    def test_names_are_present_and_unique_within_a_type(self):
        seen = set()
        for aid, a in catalog.ASSETS.items():
            self.assertTrue(a["name"].strip(), aid)
            key = (a["type"], a["name"])
            self.assertNotIn(key, seen, f"{aid} repeats {key}")
            seen.add(key)

    def test_variant_groups_have_more_than_one_member(self):
        groups = {}
        for aid, a in catalog.ASSETS.items():
            if a["group"]:
                groups.setdefault(a["group"], []).append(aid)
        for g, members in groups.items():
            self.assertGreater(len(members), 1, g)

    def test_ids_look_like_the_generators_names(self):
        for aid in catalog.ASSETS:
            self.assertRegex(aid, r"^[A-Z]{2}_[A-Za-z0-9_]+_0[1-9]$")


if __name__ == "__main__":
    unittest.main()
