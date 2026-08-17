from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from top_quant_gits.models import CategoryQuery
from top_quant_gits.ranker import score_repositories

from tests.helpers import candidate


class RankerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
        self.category = CategoryQuery(
            slug="quant",
            title="Quant Research",
            search_terms=["quant research"],
            keywords=["quant", "alpha", "portfolio"],
        )

    def test_scores_and_sorts_with_a_fixed_clock(self) -> None:
        stronger = candidate(
            "owner/alpha-portfolio",
            created_at=self.now - timedelta(days=2),
            pushed_at=self.now - timedelta(days=1),
            stars=100,
            forks=10,
            topics=["quant"],
        )
        weaker = candidate(
            "owner/unrelated",
            created_at=self.now - timedelta(days=80),
            pushed_at=self.now - timedelta(days=40),
            description="No description provided.",
            license_name=None,
        )

        ranked = score_repositories(self.category, [weaker, stronger], now=self.now)

        self.assertEqual([repo.full_name for repo in ranked], [stronger.full_name, weaker.full_name])
        self.assertEqual(stronger.matched_keywords, ["quant", "alpha", "portfolio"])
        self.assertGreater(stronger.score, weaker.score)

    def test_future_dates_do_not_create_bonus_points(self) -> None:
        future = candidate(
            "owner/future-quant",
            created_at=self.now + timedelta(days=3),
            pushed_at=self.now + timedelta(days=1),
        )

        [ranked] = score_repositories(self.category, [future], now=self.now)

        self.assertLessEqual(ranked.score, 100.0)

    def test_ties_favor_more_stars(self) -> None:
        popular = candidate("owner/popular", stars=10)
        quiet = candidate("owner/quiet", stars=1)

        ranked = score_repositories(self.category, [quiet, popular], now=self.now)

        self.assertEqual(ranked[0].full_name, popular.full_name)


if __name__ == "__main__":
    unittest.main()
