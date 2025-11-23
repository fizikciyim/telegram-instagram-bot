# handlers/buy.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


async def handle_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data.split(":")[1]

    telegram_id = query.from_user.id 

    if choice == "1day":
        link = "https://www.shopier.com/igviewer/41409641"

        text = (
            "⭐ *1 Günlük Premium*\n\n"
            "Satın alma sayfasına gitmek için aşağıdaki bağlantıya tıklayın:\n"
            f"[→ 1 Günlük Premium Satın Al]({link})\n\n"
            "❗️❗️ *ÇOK ÖNEMLİ*\n"
            "Satın alma ekranındaki *Sipariş Notu* bölümüne *SADECE* aşağıdaki ID'yi yazın:\n\n"
            f"🆔 `{telegram_id}`\n"
            "_(ID'nin üzerine basılı tutarak kopyalayabilirsiniz.)_\n\n"
            "🛒 *Lütfen dikkat:* Ürünü sepetinize *sadece 1 adet* ekleyin. "
            "Birden fazla adet seçmek gereksiz fazla ödeme yapmanıza neden olur.\n\n"
            "🚫 *ID yazılmazsa premium üyeliğiniz otomatik olarak tanımlanmaz!*"
        )

        await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        return
    if choice == "30day":
        link = "https://www.shopier.com/igviewer/41409673"

        text = (
            "💎 *30 Günlük Premium*\n\n"
            "Satın alma sayfasına gitmek için aşağıdaki linke tıklayın:\n"
            f"[→ 30 Günlük Premium Satın Al]({link})\n\n"
            "❗️❗️ *ÇOK ÖNEMLİ*\n"
            "Satın alma ekranındaki *Sipariş Notu* bölümüne *SADECE* aşağıdaki ID'Yİ YAZIN:\n\n"
            f"🆔 `{telegram_id}`\n"
            "_(ID'nin üzerine basılı tutarak kopyalayabilirsiniz.)_\n\n"
            "🛒 *Lütfen dikkat:* Ürünü sepetinize *sadece 1 adet* ekleyin. "
            "Birden fazla adet seçmek gereksiz fazla ödeme yapmanıza neden olur.\n\n"
            "🚫 *ID'yi yazmazsanız premium üyeliğiniz otomatik olarak tanımlanmaz!*"
        )
        await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        return

    if choice == "menu":
        keyboard = [
            [InlineKeyboardButton("⭐ 1 Gün – 20 TL", callback_data="buy:1day")],
            [InlineKeyboardButton("💎 30 Gün – 120 TL", callback_data="buy:30day")],
            [InlineKeyboardButton("⬅ Geri", callback_data="back_menu")]
        ]

        await query.message.reply_text(
            "💎 *Premium Paketler*\n\nBir premium paketi seç:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return
