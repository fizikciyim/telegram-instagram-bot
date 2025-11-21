# utils/limit_message.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def limit_exceeded_keyboard():
    """Limit bittiğinde gönderilecek butonlu menü."""
    keyboard = [
        [InlineKeyboardButton("⭐ Premium 1 Gün – 20₺", callback_data="buy:1day")],
        [InlineKeyboardButton("💎 Premium 30 Gün – 150₺", callback_data="buy:30day")],
        [InlineKeyboardButton("🛒 Satın Alma Sayfası", callback_data="buy:page")],
        [InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    text = (
        "⚠ *Günlük limitiniz doldu!*\n\n"
        "Daha fazla işlem yapabilmek için premium paket satın alabilirsiniz."
    )

    return text, markup
