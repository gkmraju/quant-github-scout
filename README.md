# Top Quant Gits

Top Quant Gits is a standalone Python scout that finds fresh GitHub repositories in quant, trading, crypto, backtesting, and Indian options trading niches, then publishes a ranked Markdown digest.

## What it does

- Searches GitHub for recent repositories across focused categories
- Scores repos using freshness, traction, activity, and keyword relevance
- Keeps a local history of seen repositories
- Produces a digest with the top picks per category

## Default categories

- Quant Research
- Algo Trading
- Crypto Trading
- Indian Options
- Backtesting

## Quick start

```powershell
cd D:\Python\quant-github-scout
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
top-quant-gits --days 90 --top 5
```

The generated digest is written to `output\latest_digest.md`.

To also send the digest to Telegram:

```powershell
top-quant-gits --days 90 --top 5 --send-telegram
```

## GitHub Actions

This repo includes a daily GitHub Actions workflow at `.github/workflows/daily-digest.yml`.

- Scheduled run: every day at `03:30 UTC`
- Manual run: available from the GitHub Actions tab with optional `days` and `top` inputs
- Auth: uses `GH_API_TOKEN` when provided, otherwise falls back to the repository's built-in GitHub token
- Output: commits `output/latest_digest.md` back to the repo when it changes, uploads it as a workflow artifact, prints it in the workflow summary, and sends it to Telegram when Telegram secrets are configured

If you want the schedule to align with India time, `03:30 UTC` is `09:00 IST`.

To enable Telegram delivery from GitHub Actions, add these repository secrets:

- `GH_API_TOKEN` (recommended GitHub personal access token for higher search limits)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Environment

`GITHUB_TOKEN` is optional but strongly recommended to avoid low rate limits.

```env
GITHUB_TOKEN=ghp_your_token_here
GH_API_TOKEN=ghp_your_optional_actions_token_here
TOP_QUANT_GITS_OUTPUT_DIR=output
TOP_QUANT_GITS_STATE_FILE=output/seen_repos.json
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=@your_channel_or_chat_id
```

## Example command

```powershell
top-quant-gits --days 60 --top 5 --output output\weekly_digest.md
```

To avoid repeat recommendations from previous runs:

```powershell
top-quant-gits --days 60 --top 5 --exclude-seen
```

To generate and deliver in one step:

```powershell
top-quant-gits --days 60 --top 5 --exclude-seen --send-telegram
```

## Ranking idea

This project does not use raw creation time alone. It combines:

- Freshness
- Repository traction
- Recent activity
- Relevance to the category keywords
- Basic quality signals

That keeps the digest closer to "top recent repos worth noticing" instead of "the last five repos someone created".
