# handlers/start.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from logger import log
import httpx
from config import BACKEND_URL
from datetime import datetime

from handlers.show_profile import show_profile


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    context.user_data["telegram_id"] = user.id

    log(f"START → {user.id} (@{user.username}) botu başlattı")

    # Kullanıcıyı kaydet + Premium bilgisini al
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{BACKEND_URL}/register",
            json={"telegram_id": user.id, "username": user.username or ""}
        )

        res = await client.get(f"{BACKEND_URL}/user/{user.id}")

    # Premium bilgisi RAM’e kaydedilsin
    is_premium = False
    if res.status_code == 200:
        data = res.json()
        is_premium = data.get("is_premium", 0) == 1
        context.user_data["is_premium"] = is_premium

    # START MESAJI
    text = (
        "👋 *Hoş geldin!*\n\n"
        "📱 *Instagram içerik görüntüleme botuna hoş geldin!*\n\n"
        "⚡ *Günlük 20 ücretsiz hak* ile şunları yapabilirsin:\n"
        "• *Kullanıcı profili görüntüleme* hak yemez\n"
        "🔍 Başlamak için bir *Instagram kullanıcı adı* yazman yeterli!\n\n"
    )

    if is_premium:
        text += "💎 *Premium Üyelik Aktif!*\n"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Premium Bilgilerim", callback_data="premium_open")]
        ])
    else:
        text += "⭐ Daha fazla kullanım için premium olabilirsin."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ Premium Ol", callback_data="buy:menu")]
        ])

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)



async def send_main_menu(message, context, username):
    if not username:
        text = (
            "🔍 Bir Instagram profili görmek için kullanıcı adını yazman yeterli.\n"
            "Örnek: `instagram`\n\n"
            "⭐ Daha fazla kullanım için premium paketleri inceleyebilirsin."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ Premium Paketler", callback_data="buy:menu")]
        ])

        await message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return

    return await show_profile(message, context, username)
