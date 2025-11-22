# handlers/premium_info.py

import httpx
from datetime import datetime
from config import BACKEND_URL
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def handle_premium_info(update, context):
    # Hem /premium komutundan hem de inline butondan çalışsın diye
    if update.message:
        # /premium komutu ile gelirse
        message = update.message
        telegram_id = message.from_user.id
    else:
        # callback query ile (premium_open butonu) gelirse
        query = update.callback_query
        await query.answer()
        message = query.message
        telegram_id = query.from_user.id

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BACKEND_URL}/user/{telegram_id}")

    if res.status_code != 200:
        await message.reply_text("⚠️ Kullanıcı bilgilerine ulaşılamadı.")
        return

    data = res.json()
    is_premium = data.get("is_premium", 0) == 1
    premium_until = data.get("premium_until")

    # --- PREMIUM DEĞİLSE ---
    if not is_premium or not premium_until:
        await message.reply_text(
            "❌ *Premium üye değilsin.*\n\n"
            "Sınırsız kullanım için premium paketlerden birini seçebilirsin:",
            parse_mode="Markdown"
        )

        keyboard = [
            [InlineKeyboardButton("⭐ Premium Paketler", callback_data="buy:menu")]
        ]

        await message.reply_text(
            "💎 Premium satın almak için:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # --- PREMIUM İSE ---
    dt = datetime.fromisoformat(premium_until.replace("Z", ""))

    remaining = dt - datetime.now()
    days = remaining.days
    hours = remaining.seconds // 3600

    text = (
        "💎 *Premium Üyelik Bilgileri*\n\n"
        f"⏳ **Bitiş Tarihi:** {dt.strftime('%Y-%m-%d %H:%M')}\n"
        f"📅 **Kalan Süre:** {days} gün {hours} saat\n"
    )

    await message.reply_text(text, parse_mode="Markdown")
