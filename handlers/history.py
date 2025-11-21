# handlers/history.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# ===========================
# /history komutu
# ===========================
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = context.user_data.get("history", [])

    if not history:
        await update.message.reply_text("📭 Hiç profil görüntülemedin.")
        return
    
    text = "🕓 *Son baktığın profiller:*\n\n"

    for i, username in enumerate(history[::-1], start=1):
        text += f"{i}️⃣ `{username}`\n"

    text += "\n🔍 Birine tıklayarak tekrar açabilirsin."

    await update.message.reply_text(text, parse_mode="Markdown")


# ===========================
# CALLBACK menüsü (history_menu / clear_history)
# ===========================
async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    history = context.user_data.get("history", [])

    # ---- temizle ----
    if data == "clear_history":
        context.user_data["history"] = []
        return await query.message.reply_text("🗑 Son aramalar temizlendi.")

    # ---- menüyü aç ----
    if data == "history_menu":
        if not history:
            return await query.message.reply_text("📭 Son arama yok.")

        keyboard = []

        for username in history[::-1]:
            keyboard.append([
                InlineKeyboardButton(
                    f"@{username}",
                    callback_data=f"profile_open:{username}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton("🗑 Temizle", callback_data="clear_history"),
            InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu"),
        ])

        return await query.message.reply_text(
            "🕓 Son baktığın profiller:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
