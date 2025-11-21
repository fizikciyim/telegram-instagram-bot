# handlers/start.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from igapi.private_api import private
from logger import log
import httpx
from config import BACKEND_URL

# Ortak profil gösterici fonksiyon
from handlers.show_profile import show_profile


# =============================
# /start komutu
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # Telegram ID sakla (geri dönüşlerde lazım)
    context.user_data["telegram_id"] = user.id

    log(f"START → {user.id} (@{user.username}) botu başlattı")

    # Backend'e kullanıcı kaydı
    async with httpx.AsyncClient() as client:
        await client.post(f"{BACKEND_URL}/register", json={
            "telegram_id": user.id,
            "username": user.username or ""
        })

    text = (
    "👋 *Hoş geldin!*\n\n"
    "📱 *Instagram içerik görüntüleme botuna hoş geldin!*\n\n"
    "⚡ *Günlük 20 ücretsiz hak* ile şunları yapabilirsin:\n"
    "• *Kullanıcı profili görüntüleme* hak yemez\n"
    "🔍 Başlamak için bir *Instagram kullanıcı adı* yazman yeterli!\n\n"
)

    await update.message.reply_text(text, parse_mode="Markdown")



# =============================
# ANA MENÜ (geri dönüşlerde çağrılır)
# =============================
async def send_main_menu(message, context, username):
    return await show_profile(message, context, username)
