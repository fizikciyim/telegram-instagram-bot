# services/telegram_notifier.py

import httpx
from configBackend import TELEGRAM_BOT_TOKEN

async def send_premium_message(user_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": user_id,
            "text": text,
            "parse_mode": "Markdown"
        })