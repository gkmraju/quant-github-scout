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

    def send_document(self, document_path: Path, *, caption: str) -> None:
        if not document_path.exists():
            raise TelegramDeliveryError(f"Digest file not found: {document_path}")

        with document_path.open("rb") as handle:
            response = self._client.post(
                "/sendDocument",
                data={
                    "chat_id": self._chat_id,
                    "caption": caption,
                },
                files={
                    "document": (document_path.name, handle, _mime_type_for(document_path)),
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

    def send_message(self, text: str) -> None:
        response = self._client.post(
            "/sendMessage",
            data={
                "chat_id": self._chat_id,
                "text": text,
                "disable_web_page_preview": "true",
            },
        )
        if response.status_code >= 400:
            raise TelegramDeliveryError(
                "Telegram link message failed. Check TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, and bot access."
            )
        payload = response.json()
        if not payload.get("ok"):
            raise TelegramDeliveryError(
                "Telegram rejected the link message. Verify bot access to the target chat."
            )

    def close(self) -> None:
        self._client.close()


def default_digest_caption(base_caption: str) -> str:
    return f"{base_caption} · {datetime.now(UTC).date().isoformat()}"


def _mime_type_for(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "application/pdf"
    if path.suffix.lower() == ".html":
        return "text/html"
    return "text/markdown"
