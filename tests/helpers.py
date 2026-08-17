from __future__ import annotations

from datetime import UTC, datetime

from top_quant_gits.models import RepoCandidate


def candidate(
    name: str,
    *,
    created_at: datetime | None = None,
    pushed_at: datetime | None = None,
    stars: int = 0,
    forks: int = 0,
    description: str = "A quantitative trading project",
    topics: list[str] | None = None,
    license_name: str | None = "MIT",
) -> RepoCandidate:
    timestamp = datetime(2026, 8, 1, tzinfo=UTC)
    return RepoCandidate(
        category="quant",
        full_name=name,
        html_url=f"https://github.com/{name}",
        description=description,
        created_at=created_at or timestamp,
        updated_at=timestamp,
        pushed_at=pushed_at or timestamp,
        language="Python",
        stars=stars,
        forks=forks,
        topics=topics or [],
        license_name=license_name,
    )
