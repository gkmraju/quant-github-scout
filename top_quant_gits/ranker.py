from __future__ import annotations

from datetime import UTC, datetime
from math import log10

from top_quant_gits.models import CategoryQuery, RepoCandidate


def score_repositories(category: CategoryQuery, repos: list[RepoCandidate]) -> list[RepoCandidate]:
    now = datetime.now(UTC)

    for repo in repos:
        haystack = " ".join(
            [
                repo.full_name.lower(),
                repo.description.lower(),
                " ".join(topic.lower() for topic in repo.topics),
            ]
        )
        matched_keywords = [word for word in category.keywords if word.lower() in haystack]
        age_days = max((now - repo.created_at).days, 0)
        idle_days = max((now - repo.pushed_at).days, 0)

        freshness = max(0.0, 35.0 - age_days * 0.35)
        traction = min(25.0, log10(repo.stars + 1) * 10.0 + log10(repo.forks + 1) * 5.0)
        activity = max(0.0, 20.0 - idle_days * 0.4)
        relevance = min(15.0, len(matched_keywords) * 2.5)
        quality = 0.0
        if repo.description and repo.description != "No description provided.":
            quality += 3.0
        if repo.license_name and repo.license_name != "NOASSERTION":
            quality += 2.0

        repo.matched_keywords = matched_keywords
        repo.score = round(freshness + traction + activity + relevance + quality, 2)

    return sorted(repos, key=lambda repo: (repo.score, repo.stars, repo.updated_at), reverse=True)
