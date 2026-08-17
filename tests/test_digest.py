from __future__ import annotations

import unittest
from datetime import UTC, datetime

from top_quant_gits.digest import build_markdown_digest, build_telegram_link_digest
from top_quant_gits.models import CategoryQuery

from tests.helpers import candidate


class DigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generated_at = datetime(2026, 8, 17, 6, 30, tzinfo=UTC)
        self.category = CategoryQuery("quant", "Quant Research", [], ["quant"])
        self.repo = candidate("owner/scout")
        self.repo.score = 91.25
        self.repo.matched_keywords = ["quant"]

    def test_markdown_digest_is_reproducible(self) -> None:
        digest = build_markdown_digest(
            categories=[self.category],
            ranked_repos={"quant": [self.repo]},
            top_n=1,
            generated_at=self.generated_at,
        )

        self.assertIn("_Generated on 2026-08-17 06:30 UTC_", digest)
        self.assertIn("### 1. [owner/scout](https://github.com/owner/scout)", digest)
        self.assertIn("- Score: 91.25", digest)
        self.assertTrue(digest.endswith("\n"))

    def test_markdown_digest_reports_empty_category(self) -> None:
        digest = build_markdown_digest(
            categories=[self.category],
            ranked_repos={},
            top_n=5,
            generated_at=self.generated_at,
        )

        self.assertIn("No repositories matched this category", digest)

    def test_telegram_digest_uses_direct_links_and_fixed_date(self) -> None:
        digest = build_telegram_link_digest(
            categories=[self.category],
            ranked_repos={"quant": [self.repo]},
            top_n=1,
            generated_at=self.generated_at,
        )

        self.assertIn("Date: 2026-08-17", digest)
        self.assertIn("https://github.com/owner/scout", digest)


if __name__ == "__main__":
    unittest.main()
