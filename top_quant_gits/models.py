from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class CategoryQuery:
    slug: str
    title: str
    search_terms: list[str]
    keywords: list[str]


@dataclass
class RepoCandidate:
    category: str
    full_name: str
    html_url: str
    description: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    language: str | None
    stars: int
    forks: int
    topics: list[str] = field(default_factory=list)
    license_name: str | None = None
    is_fork: bool = False
    score: float = 0.0
    matched_keywords: list[str] = field(default_factory=list)

    @property
    def repo_name(self) -> str:
        return self.full_name.split("/")[-1]
