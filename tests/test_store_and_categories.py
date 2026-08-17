from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from top_quant_gits.categories import DEFAULT_CATEGORIES
from top_quant_gits.store import SeenRepoStore


class SeenRepoStoreTests(unittest.TestCase):
    def test_missing_store_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = SeenRepoStore(Path(directory) / "seen.json")
            self.assertEqual(store.load(), set())

    def test_round_trip_is_deduplicated_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "seen.json"
            store = SeenRepoStore(path)

            store.save({"z/repo", "a/repo", "z/repo"})

            self.assertEqual(store.load(), {"a/repo", "z/repo"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["repos"], ["a/repo", "z/repo"])


class CategoryTests(unittest.TestCase):
    def test_default_categories_have_unique_slugs_and_search_terms(self) -> None:
        slugs = [category.slug for category in DEFAULT_CATEGORIES]

        self.assertEqual(len(slugs), len(set(slugs)))
        self.assertTrue(all(category.search_terms for category in DEFAULT_CATEGORIES))
        self.assertTrue(all(category.keywords for category in DEFAULT_CATEGORIES))


if __name__ == "__main__":
    unittest.main()
