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

## GitHub Actions

This repo includes a daily GitHub Actions workflow at `.github/workflows/daily-digest.yml`.

- Scheduled run: every day at `03:30 UTC`
- Manual run: available from the GitHub Actions tab with optional `days` and `top` inputs
- Auth: uses the repository's built-in `GITHUB_TOKEN`
- Output: commits `output/latest_digest.md` back to the repo when it changes, uploads it as a workflow artifact, and prints it in the workflow summary

If you want the schedule to align with India time, `03:30 UTC` is `09:00 IST`.

## Environment

`GITHUB_TOKEN` is optional but strongly recommended to avoid low rate limits.

```env
GITHUB_TOKEN=ghp_your_token_here
TOP_QUANT_GITS_OUTPUT_DIR=output
TOP_QUANT_GITS_STATE_FILE=output/seen_repos.json
```

## Example command

```powershell
top-quant-gits --days 60 --top 5 --output output\weekly_digest.md
```

To avoid repeat recommendations from previous runs:

```powershell
top-quant-gits --days 60 --top 5 --exclude-seen
```

## Ranking idea

This project does not use raw creation time alone. It combines:

- Freshness
- Repository traction
- Recent activity
- Relevance to the category keywords
- Basic quality signals

That keeps the digest closer to "top recent repos worth noticing" instead of "the last five repos someone created".
