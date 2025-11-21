from telegram import Update
from telegram.ext import ContextTypes


async def last_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = context.user_data.get("last_username")

    if not last:
        await update.message.reply_text("📭 Daha önce hiç profil aramamışsın.")
        return

    # Kullanıcıya son profili göster
    await update.message.reply_text(f"🔁 Son baktığın profil: @{last}")

    # Mesaj olarak username gönder, profile_handler tekrar çalışsın
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=last
    )
