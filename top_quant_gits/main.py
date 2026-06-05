from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from top_quant_gits.categories import DEFAULT_CATEGORIES
from top_quant_gits.config import load_settings
from top_quant_gits.digest import build_markdown_digest, build_telegram_link_digest
from top_quant_gits.github_client import GitHubClient, GitHubRateLimitError
from top_quant_gits.publication import render_publication
from top_quant_gits.ranker import score_repositories
from top_quant_gits.store import SeenRepoStore
from top_quant_gits.telegram_delivery import (
    TelegramDeliveryError,
    TelegramNotifier,
    default_digest_caption,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Top Quant Gits Markdown digest.")
    parser.add_argument("--days", type=int, default=90, help="Lookback window for recent repositories.")
    parser.add_argument("--top", type=int, default=5, help="Number of repositories per category.")
    parser.add_argument(
        "--per-query-limit",
        type=int,
        default=12,
        help="How many GitHub results to request for each category search term.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional explicit output Markdown file.",
    )
    parser.add_argument(
        "--exclude-seen",
        action="store_true",
        help="Skip repositories that were already saved in the local seen list.",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the generated digest to Telegram using TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.",
    )
    return parser


def main() -> None:
    load_dotenv()
    args = build_parser().parse_args()
    settings = load_settings()
    output_path = args.output or settings.output_dir / "latest_digest.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    store = SeenRepoStore(settings.state_file)
    seen_repos = store.load()
    current_run_seen = set(seen_repos)
    ranked_repos: dict[str, list] = {}

    client = GitHubClient(token=settings.github_token)
    try:
        try:
            for category in DEFAULT_CATEGORIES:
                repos = client.search_recent_repositories(
                    category,
                    lookback_days=args.days,
                    per_query_limit=args.per_query_limit,
                )
                if args.exclude_seen:
                    repos = [repo for repo in repos if repo.full_name not in seen_repos]
                ranked = score_repositories(category, repos)
                ranked_repos[category.slug] = ranked
                current_run_seen.update(repo.full_name for repo in ranked[: args.top])
        except GitHubRateLimitError as error:
            raise SystemExit(str(error)) from error
    finally:
        client.close()

    digest = build_markdown_digest(
        categories=DEFAULT_CATEGORIES,
        ranked_repos=ranked_repos,
        top_n=args.top,
    )
    output_path.write_text(digest, encoding="utf-8")
    store.save(current_run_seen)
    print(f"Wrote digest to {output_path}")

    publication = render_publication(
        categories=DEFAULT_CATEGORIES,
        ranked_repos=ranked_repos,
        top_n=args.top,
        output_base=output_path.parent / output_path.stem,
        brand_name=settings.brand_name,
        signature_name=settings.signature_name,
        github_url=settings.github_url,
    )
    print(f"Wrote HTML publication to {publication.html_path}")
    if publication.pdf_path is not None:
        print(f"Wrote PDF publication to {publication.pdf_path}")
    else:
        print("PDF publication could not be rendered because no supported browser was found.")

    if args.send_telegram:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            raise SystemExit(
                "Telegram delivery requested, but TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing."
            )
        notifier = TelegramNotifier(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
        )
        try:
            notifier.send_message(
                build_telegram_link_digest(
                    categories=DEFAULT_CATEGORIES,
                    ranked_repos=ranked_repos,
                    top_n=args.top,
                )
            )
            if publication.pdf_path is not None:
                notifier.send_document(
                    publication.pdf_path,
                    caption=default_digest_caption(settings.telegram_caption),
                )
            else:
                notifier.send_document(
                    output_path,
                    caption=default_digest_caption(settings.telegram_caption),
                )
        except TelegramDeliveryError as error:
            raise SystemExit(str(error)) from error
        finally:
            notifier.close()
        print("Sent digest to Telegram")


if __name__ == "__main__":
    main()
