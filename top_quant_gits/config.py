from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    github_token: str | None
    output_dir: Path
    state_file: Path


def load_settings() -> Settings:
    output_dir = Path(os.getenv("TOP_QUANT_GITS_OUTPUT_DIR", "output"))
    state_file = Path(os.getenv("TOP_QUANT_GITS_STATE_FILE", output_dir / "seen_repos.json"))
    github_token = os.getenv("GITHUB_TOKEN") or None
    return Settings(
        github_token=github_token,
        output_dir=output_dir,
        state_file=state_file,
    )
