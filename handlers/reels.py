# handlers/reels.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from igapi.private_api import private
from utils.backend_api import check_limit  # ⬅ backend'e HTTP ile soracağız
from utils.limit_message import limit_exceeded_keyboard


async def handle_reels(update, context):
    query = update.callback_query
    data = query.data
    telegram_id = query.from_user.id  # hak kontrolü için

    # data formatı → reels:{user_id}:{username}
    _, user_id, username = data.split(":")
    user_id = int(user_id)

    # -------------------------------------------------------
    # LIMIT KONTROLÜ — reels menüsünü açmak 1 hak yer
    # -------------------------------------------------------
    limit = await check_limit(telegram_id)

    if not limit.get("allowed", False):
        reason = limit.get("reason")
        if reason == "limit_reached":
            text, markup = limit_exceeded_keyboard()
            await query.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
        else:
            await query.answer("⚠ Kullanıcı bulunamadı!", show_alert=True)
        return

    # -------------------------------------------------------
    # REELSİ ÇEK
    # -------------------------------------------------------
    reels = private.user_reels(user_id)

    if not reels:
        await query.message.reply_text("📭 Reels yok.")
        return

    # İlk 10 reels’i gönder
    for reel in reels[:10]:
        url = private.reel_url(reel)
        if url:
            try:
                await query.message.reply_video(video=url)
            except Exception as e:
                print("Reel gönderilemedi:", e)

    await query.message.reply_text(
        "🎬 Reels görüntülendi.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")]
        ])
    )
