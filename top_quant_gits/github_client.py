from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx

from top_quant_gits.models import CategoryQuery, RepoCandidate


class GitHubRateLimitError(RuntimeError):
    """Raised when the GitHub API rate limit blocks a request."""


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: float = 20.0) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "top-quant-gits",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers=headers,
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def search_recent_repositories(
        self,
        category: CategoryQuery,
        *,
        lookback_days: int,
        per_query_limit: int,
    ) -> list[RepoCandidate]:
        cutoff_date = (datetime.now(UTC) - timedelta(days=lookback_days)).date().isoformat()
        collected: dict[str, RepoCandidate] = {}

        for term in category.search_terms:
            query = (
                f"{term} archived:false is:public "
                f"created:>={cutoff_date} pushed:>={cutoff_date}"
            )
            response = self._client.get(
                "/search/repositories",
                params={
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": per_query_limit,
                },
            )
            if response.status_code == 403 and "rate limit" in response.text.lower():
                raise GitHubRateLimitError(
                    "GitHub Search API rate limit exceeded. Add GH_API_TOKEN or GITHUB_TOKEN to .env and try again."
                )
            response.raise_for_status()
            payload = response.json()

            for item in payload.get("items", []):
                repo = self._to_repo_candidate(category.slug, item)
                if repo.is_fork:
                    continue
                existing = collected.get(repo.full_name)
                if existing is None or repo.updated_at > existing.updated_at:
                    collected[repo.full_name] = repo

        return list(collected.values())

    @staticmethod
    def _to_repo_candidate(category: str, payload: dict) -> RepoCandidate:
        return RepoCandidate(
            category=category,
            full_name=payload["full_name"],
            html_url=payload["html_url"],
            description=payload.get("description") or "No description provided.",
            created_at=_parse_github_datetime(payload["created_at"]),
            updated_at=_parse_github_datetime(payload["updated_at"]),
            pushed_at=_parse_github_datetime(payload["pushed_at"]),
            language=payload.get("language"),
            stars=payload.get("stargazers_count", 0),
            forks=payload.get("forks_count", 0),
            topics=payload.get("topics", []),
            license_name=(payload.get("license") or {}).get("spdx_id"),
            is_fork=payload.get("fork", False),
        )


def _parse_github_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
