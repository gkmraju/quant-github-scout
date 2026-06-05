from __future__ import annotations

import html
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

from top_quant_gits.models import CategoryQuery, RepoCandidate


@dataclass(slots=True)
class PublicationArtifacts:
    html_path: Path
    pdf_path: Path | None


def render_publication(
    *,
    categories: list[CategoryQuery],
    ranked_repos: dict[str, list[RepoCandidate]],
    top_n: int,
    output_base: Path,
    brand_name: str,
    signature_name: str,
    github_url: str,
) -> PublicationArtifacts:
    output_base = output_base.resolve()
    output_base.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_base.with_suffix(".html")
    pdf_path = output_base.with_suffix(".pdf")
    html_path.write_text(
        _render_html(
            categories=categories,
            ranked_repos=ranked_repos,
            top_n=top_n,
            brand_name=brand_name,
            signature_name=signature_name,
            github_url=github_url,
        ),
        encoding="utf-8",
    )
    rendered_pdf = _render_pdf(html_path, pdf_path)
    return PublicationArtifacts(
        html_path=html_path,
        pdf_path=pdf_path if rendered_pdf else None,
    )


def _render_html(
    *,
    categories: list[CategoryQuery],
    ranked_repos: dict[str, list[RepoCandidate]],
    top_n: int,
    brand_name: str,
    signature_name: str,
    github_url: str,
) -> str:
    issue_date = datetime.now(UTC).strftime("%Y-%m-%d")
    total_repos = sum(len(ranked_repos.get(category.slug, [])[:top_n]) for category in categories)
    sections = []
    for category in categories:
        repos = ranked_repos.get(category.slug, [])[:top_n]
        if not repos:
            sections.append(
                f"""
                <section class="category-block">
                  <div class="section-title">{_escape(category.title)}</div>
                  <div class="empty-card">No repositories matched this category in the selected window.</div>
                </section>
                """
            )
            continue
        cards = "\n".join(_render_repo_card(repo, rank=index) for index, repo in enumerate(repos, start=1))
        sections.append(
            f"""
            <section class="category-block">
              <div class="section-title">{_escape(category.title)}</div>
              {cards}
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{_escape(brand_name)} - {issue_date}</title>
    <style>
      @page {{
        size: A4;
        margin: 16mm 14mm 18mm 14mm;
      }}
      :root {{
        --ink: #171717;
        --muted: #5b5b5b;
        --line: #d9d0c4;
        --paper: #f6f1e8;
        --accent: #bb5a2a;
        --accent-soft: #f1d4bf;
        --card: #fffdf9;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, #f7dfc9 0%, transparent 25%),
          linear-gradient(180deg, #f8f4ed 0%, #efe4d7 100%);
        font-family: Georgia, "Times New Roman", serif;
        line-height: 1.45;
      }}
      .page {{ width: 100%; }}
      .hero {{
        border: 1px solid var(--line);
        background: linear-gradient(140deg, rgba(255,253,249,.95), rgba(246,236,223,.92));
        border-radius: 24px;
        padding: 28px 28px 24px 28px;
        margin-bottom: 18px;
      }}
      .eyebrow {{
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 11px;
        color: var(--accent);
        margin-bottom: 10px;
        font-family: Arial, sans-serif;
      }}
      h1 {{
        margin: 0 0 8px 0;
        font-size: 30px;
        line-height: 1.05;
      }}
      .subtitle {{
        color: var(--muted);
        font-size: 14px;
        margin-bottom: 14px;
      }}
      .signature {{
        color: var(--muted);
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: lowercase;
        margin-bottom: 14px;
        font-family: Arial, sans-serif;
      }}
      .hero-grid {{
        display: grid;
        grid-template-columns: 1.6fr 1fr;
        gap: 18px;
      }}
      .hero-panel {{
        border-top: 1px solid var(--line);
        padding-top: 12px;
      }}
      .hero-panel h2 {{
        margin: 0 0 8px 0;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-family: Arial, sans-serif;
      }}
      .hero-panel p, .hero-panel li {{
        font-size: 13px;
        color: var(--muted);
        margin: 0;
      }}
      .hero-panel ul {{
        padding-left: 16px;
        margin: 0;
      }}
      .section-title {{
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--accent);
        margin: 22px 0 10px 0;
        font-family: Arial, sans-serif;
      }}
      .card {{
        background: rgba(255,253,249,.95);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 10px 24px rgba(50,25,12,.05);
        break-inside: avoid;
      }}
      .rank {{
        display: inline-block;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        padding: 4px 10px;
        font-size: 11px;
        font-family: Arial, sans-serif;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: 8px;
      }}
      .card h3 {{
        margin: 0 0 8px 0;
        font-size: 22px;
        line-height: 1.18;
      }}
      .meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px 14px;
        margin-bottom: 10px;
        color: var(--muted);
        font-size: 12px;
        font-family: Arial, sans-serif;
      }}
      .lede {{
        font-size: 14px;
        margin-bottom: 10px;
      }}
      .label {{ font-weight: bold; }}
      .grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px 16px;
        margin-top: 8px;
      }}
      .mini {{
        font-size: 13px;
      }}
      .abstract {{
        margin-top: 10px;
        color: var(--muted);
        font-size: 12px;
      }}
      .links a, .footer a {{
        color: var(--accent);
        text-decoration: none;
      }}
      .topics {{
        margin-top: 10px;
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
      }}
      .tag {{
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 3px 9px;
        font-size: 11px;
        color: var(--muted);
        background: #fff;
        font-family: Arial, sans-serif;
      }}
      .footer {{
        margin-top: 20px;
        color: var(--muted);
        font-size: 12px;
        border-top: 1px solid var(--line);
        padding-top: 10px;
        font-family: Arial, sans-serif;
      }}
      .empty-card {{
        background: rgba(255,253,249,.95);
        border: 1px dashed var(--line);
        border-radius: 18px;
        padding: 18px;
        color: var(--muted);
        font-family: Arial, sans-serif;
      }}
    </style>
  </head>
  <body>
    <div class="page">
      <section class="hero">
        <div class="eyebrow">{_escape(brand_name)}</div>
        <h1>{_escape(brand_name)} Digest</h1>
        <div class="signature">by twisted_arrow</div>
        <div class="subtitle">
          {issue_date} · Latest GitHub scouts · Curated by {_escape(signature_name)}
        </div>
        <div class="hero-grid">
          <div class="hero-panel">
            <h2>Editorial Frame</h2>
            <p>
              Fresh GitHub repositories across quant, trading, crypto, backtesting,
              and Indian options, ranked for relevance, activity, and practical signal.
            </p>
          </div>
          <div class="hero-panel">
            <h2>From</h2>
            <ul>
              <li><a href="{_escape(github_url)}">{_escape(github_url)}</a></li>
              <li>Sources: GitHub Search API + Top Quant Gits ranking</li>
              <li>{total_repos} repositories in this issue</li>
            </ul>
          </div>
        </div>
      </section>

      {''.join(sections)}

      <div class="footer">
        Built with <a href="{_escape(github_url)}">{_escape(brand_name)}</a> · {_escape(signature_name)}
      </div>
    </div>
  </body>
</html>
"""


def _render_repo_card(repo: RepoCandidate, *, rank: int) -> str:
    created = repo.created_at.date().isoformat()
    updated = repo.updated_at.date().isoformat()
    language = repo.language or "Unknown"
    topics = repo.topics[:6] if repo.topics else repo.matched_keywords[:6]
    topics_html = "".join(f'<span class="tag">{_escape(tag)}</span>' for tag in topics)
    why = ", ".join(repo.matched_keywords[:4]) or "broad category relevance"
    return f"""
    <article class="card">
      <div class="rank">#{rank} · Score {repo.score:.2f}</div>
      <h3><a href="{_escape(repo.html_url)}">{_escape(repo.full_name)}</a></h3>
      <div class="meta">
        <div>{_escape(repo.category)}</div>
        <div>Created {created}</div>
        <div>Updated {updated}</div>
        <div>{_escape(language)}</div>
      </div>
      <div class="lede"><span class="label">Summary:</span> {_escape(_compact(repo.description, 260))}</div>
      <div class="mini"><span class="label">Why it stands out:</span> matched { _escape(why) }</div>
      <div class="grid">
        <div class="mini"><span class="label">Stars:</span> {repo.stars}</div>
        <div class="mini"><span class="label">Forks:</span> {repo.forks}</div>
        <div class="mini"><span class="label">License:</span> {_escape(repo.license_name or "Unknown")}</div>
        <div class="mini"><span class="label">Repo:</span> <a href="{_escape(repo.html_url)}">Open on GitHub</a></div>
      </div>
      <div class="topics">{topics_html}</div>
      <div class="abstract">{_escape(_compact(repo.description, 520))}</div>
      <div class="links mini" style="margin-top: 10px;">
        <a href="{_escape(repo.html_url)}">GitHub</a> ·
        <span>Links remain clickable in the PDF</span>
      </div>
    </article>
    """


def _render_pdf(html_path: Path, pdf_path: Path) -> bool:
    browser = _find_browser()
    if browser is None:
        return False
    html_path = html_path.resolve()
    pdf_path = pdf_path.resolve()
    file_url = f"file:///{quote(str(html_path).replace(chr(92), '/'), safe=':/')}"
    with tempfile.TemporaryDirectory(prefix="top-quant-gits-pdf-") as temp_dir:
        command = [
            browser,
            "--headless",
            "--disable-gpu",
            f"--user-data-dir={temp_dir}",
            f"--print-to-pdf={pdf_path}",
            file_url,
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    return result.returncode == 0 and pdf_path.exists()


def _find_browser() -> str | None:
    candidates = (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


def _compact(value: str, limit: int) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."
