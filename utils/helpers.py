# utils/helpers.py

from datetime import datetime
from telegram import Message

def format_date(ts):
    return datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")

def story_time_ago(item):
    ts = item.get("taken_at")
    if not ts:
        return "bilinmiyor"

    now = datetime.now()
    t = datetime.fromtimestamp(ts)
    diff = now - t
    sec = diff.total_seconds()

    if sec < 60:
        return "az önce"
    if sec < 3600:
        return f"{int(sec//60)} dakika önce"
    if sec < 86400:
        return f"{int(sec//3600)} saat önce"
    return f"{int(sec//86400)} gün önce"


async def send_photo_safely(message: Message, url: str, caption: str = None):
    try:
        await message.reply_photo(photo=url, caption=caption)
    except Exception:
        # Bazı URL'ler direkt açılmadığı için fallback
        try:
            await message.reply_photo(photo=url + "?dl=1", caption=caption)
        except Exception:
            await message.reply_text("⚠️ Fotoğraf gönderilemedi.")


async def send_video_safely(message: Message, url: str, caption: str = None):
    try:
        await message.reply_video(video=url, caption=caption)
    except Exception:
        try:
            await message.reply_video(video=url + "?dl=1", caption=caption)
        except Exception:
            await message.reply_text("⚠️ Video gönderilemedi.")
