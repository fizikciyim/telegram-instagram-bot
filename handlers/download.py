# handlers/download.py

from telegram import Update
from telegram.ext import ContextTypes

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("📥 Bu özellik yakında eklenecek!", show_alert=True)
