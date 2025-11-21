# handlers/profile.py

from telegram import Update
from telegram.ext import ContextTypes
from logger import log
import httpx
from config import BACKEND_URL

from handlers.show_profile import show_profile


# ===========================================
# 1) Mesajdan @kullanıcı yazınca çalışan
# ===========================================
async def handle_profile_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.replace("@", "").strip()
    telegram_user = update.message.from_user

    # Kullanıcıyı veritabanına kaydet (register)
    async with httpx.AsyncClient() as client:
        await client.post(f"{BACKEND_URL}/register", json={
            "telegram_id": telegram_user.id,
            "username": telegram_user.username or ""
        })

    # Log kaydı
    async with httpx.AsyncClient() as client:
        await client.post(f"{BACKEND_URL}/log", json={
            "user_id": telegram_user.id,
            "action": "profile_search",
            "extra": username
        })

    # Son aramalar kaydı
    history = context.user_data.get("history", [])
    if username not in history:
        history.append(username)
    context.user_data["history"] = history[-5:]
    context.user_data["last_username"] = username

    # Ortak profil gösterme fonksiyonunu çağır
    return await show_profile(update.message, context, username)



# ===========================================
# 2) Callback'ten profil açılırsa
# ===========================================
async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    username = query.data.split(":")[1]

    # Son aramaya kaydet
    history = context.user_data.get("history", [])
    if username not in history:
        history.append(username)
    context.user_data["history"] = history[-5:]
    context.user_data["last_username"] = username

    log(f"PROFILE_OPEN → {query.from_user.id} @{username}")

    return await show_profile(query.message, context, username)
