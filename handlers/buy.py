# handlers/buy.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def handle_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data.split(":")[1]

    if choice == "1day":
        await query.message.reply_text(
            "⭐ *1 Günlük Premium* satın almak için:\nhttps://odeme-linki.com/1gun",
            parse_mode="Markdown"
        )
        return

    if choice == "30day":
        await query.message.reply_text(
            "💎 *30 Günlük Premium* satın almak için:\nhttps://odeme-linki.com/30gun",
            parse_mode="Markdown"
        )
        return

    if choice == "page":
        await query.message.reply_text(
            "🛒 Satın alma sayfası:\nhttps://odeme-linki.com",
            parse_mode="Markdown"
        )
        return
