from __future__ import annotations

from datetime import UTC, datetime

from top_quant_gits.models import CategoryQuery, RepoCandidate


def build_markdown_digest(
    *,
    categories: list[CategoryQuery],
    ranked_repos: dict[str, list[RepoCandidate]],
    top_n: int,
) -> str:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Top Quant Gits",
        "",
        f"_Generated on {generated_at}_",
        "",
        "Recent GitHub repositories ranked by freshness, traction, activity, and category fit.",
        "",
    ]

    for category in categories:
        lines.append(f"## {category.title}")
        lines.append("")
        repos = ranked_repos.get(category.slug, [])[:top_n]
        if not repos:
            lines.append("No repositories matched this category in the selected window.")
            lines.append("")
            continue

        for index, repo in enumerate(repos, start=1):
            created = repo.created_at.date().isoformat()
            updated = repo.updated_at.date().isoformat()
            language = repo.language or "Unknown"
            keywords = ", ".join(repo.matched_keywords[:4]) or "broad relevance"
            lines.extend(
                [
                    f"### {index}. [{repo.full_name}]({repo.html_url})",
                    "",
                    repo.description.strip(),
                    "",
                    f"- Score: {repo.score}",
                    f"- Stars: {repo.stars}",
                    f"- Forks: {repo.forks}",
                    f"- Language: {language}",
                    f"- Created: {created}",
                    f"- Last updated: {updated}",
                    f"- Why it stands out: matched {keywords}",
                    "",
                ]
            )

    return "\n".join(lines).strip() + "\n"
