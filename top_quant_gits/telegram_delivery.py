from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import httpx


class TelegramDeliveryError(RuntimeError):
    """Raised when Telegram delivery fails."""


class TelegramNotifier:
    def __init__(self, *, bot_token: str, chat_id: str, timeout: float = 30.0) -> None:
        self._chat_id = chat_id
        self._client = httpx.Client(
            base_url=f"https://api.telegram.org/bot{bot_token}",
            timeout=timeout,
        )

    def send_digest(self, digest_path: Path) -> None:
        if not digest_path.exists():
            raise TelegramDeliveryError(f"Digest file not found: {digest_path}")

        caption = f"Top Quant Gits digest for {datetime.now(UTC).date().isoformat()}"
        with digest_path.open("rb") as handle:
            response = self._client.post(
                "/sendDocument",
                data={
                    "chat_id": self._chat_id,
                    "caption": caption,
                },
                files={
                    "document": (digest_path.name, handle, "text/markdown"),
                },
            )

        if response.status_code >= 400:
            raise TelegramDeliveryError(
                "Telegram delivery failed. Check TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, and bot access."
            )
        payload = response.json()
        if not payload.get("ok"):
            raise TelegramDeliveryError(
                "Telegram delivery was rejected by the Telegram API. Verify bot access to the target chat."
            )

    def close(self) -> None:
        self._client.close()
