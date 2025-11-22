# handlers/highlights.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from igapi.private_api import private
from utils.backend_api import check_limit   # ❗ Artık backend'e HTTP çağrısı
from utils.helpers import story_time_ago
from utils.limit_message import limit_exceeded_keyboard
from utils.backend_api import get_user_data


async def handle_highlights(update, context):
    query = update.callback_query
    data = query.data
    telegram_id = query.from_user.id   # limit için


    # -------------------------------------------------------
    # highlights:{user_id}:{username}
    # KLASÖR LİSTESİ → 1 hak
    # -------------------------------------------------------
    # -------------------------------------------------------
# highlights:{user_id}:{username}
# KLASÖR LİSTESİ → 1 hak
# -------------------------------------------------------
    # highlights:{user_id}:{username}
    if data.startswith("highlights:"):
        _, user_id, username = data.split(":")
        user_id = int(user_id)

        context.user_data["last_username"] = username  # Kaydet

        telegram_id = query.from_user.id

        user_info = await get_user_data(telegram_id)
        is_premium = user_info.get("is_premium", 0) == 1

        # ✔ Limit kontrolü
        limit = await check_limit(telegram_id)
        if not limit.get("allowed"):
            text, markup = limit_exceeded_keyboard()
            await query.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
            return

        trays = private.user_highlights_full(user_id)
        if not trays:
            await query.message.reply_text("📭 Öne çıkan klasör yok.")
            return

        keyboard = []

        for tray in trays:
            title = tray.get("title", "İsimsiz")
            hid = tray["id"].replace(":", "-")  # callback_data için

            items = private.highlight_items(tray["id"])
            count = len(items)

            if len(title) > 20:
                title = title[:20] + "…"

            # Premium kullanıcıya özel buton
            if is_premium:
                all_text = "<-- Hepsini göster ⭐ "
            else:
                all_text = "<-- Hepsi göster ⚡–1 "

            # Klasör + Hepsi butonu yan yana
            keyboard.append([
                InlineKeyboardButton(
                    f"📁 {title} ({count})",
                    callback_data=f"highlight_open:{hid}:{user_id}"
                ),
                InlineKeyboardButton(
                    all_text,
                    callback_data=f"highlight_all:{hid}:{user_id}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")
        ])

        await query.message.reply_text(
            "📁 *Öne çıkanlar*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    # -------------------------------------------------------
    # highlight_open → klasörün içindeki hikayeler
    # ÜCRETSİZ
    # -------------------------------------------------------
    if data.startswith("highlight_open:"):
        _, hid_clean, user_id = data.split(":")
        user_id = int(user_id)
        username = context.user_data.get("last_username")

        # ⭐ PREMIUM bilgisi backend'ten çekilsin
        user_info = await get_user_data(telegram_id)
        is_premium = user_info.get("is_premium", 0) == 1

        hid = hid_clean.replace("-", ":")
        trays = private.user_highlights_full(user_id)
        tray = next((t for t in trays if t["id"] == hid), None)

        if not tray:
            await query.message.reply_text("❌ Klasör bulunamadı.")
            return

        items = private.highlight_items(hid)
        if not items:
            await query.message.reply_text("📭 Bu klasörde hikaye yok.")
            return

        keyboard = []
        row = []

        for i, _ in enumerate(items):
            row.append(
                InlineKeyboardButton(
                    str(i + 1),
                    callback_data=f"highlight_story:{hid_clean}:{i}:{user_id}"
                )
            )
            if len(row) == 5:
                keyboard.append(row)
                row = []

        if row:
            keyboard.append(row)

        
        # ⭐ PREMIUM ise farklı buton
        if is_premium:
            show_all_text = "📚 Hepsini Göster ⭐"
        else:
            show_all_text = "📚 Hepsini Göster ⚡–1"
            
        keyboard.append([
        InlineKeyboardButton(show_all_text, callback_data=f"highlight_all:{hid_clean}:{user_id}")
    ])
        keyboard.append([
            InlineKeyboardButton("⬅ Klasörler", callback_data=f"highlights:{user_id}:{context.user_data['last_username']}"),
            InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")
        ])

        await query.message.reply_text(
            f"⭐ *{tray.get('title', 'İsimsiz')}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    # -------------------------------------------------------
    # highlight_story → tek hikaye gösterimi
    # ÜCRETSİZ
    # -------------------------------------------------------
    if data.startswith("highlight_story:"):
        _, hid_clean, index, user_id = data.split(":")
        index = int(index)
        user_id = int(user_id)
        username = context.user_data.get("last_username")

        hid = hid_clean.replace("-", ":")
        items = private.highlight_items(hid)

        if index >= len(items):
            await query.message.reply_text("❌ Hikaye bulunamadı.")
            return

        item = items[index]
        media_url = private.media_url(item)

        if "video" in media_url:
            await query.message.reply_video(video=media_url)
        else:
            await query.message.reply_photo(photo=media_url)

        info = story_time_ago(item)

        await query.message.reply_text(
            f"🕓 Hikaye *{info}* paylaşılmış.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅ Bu Klasöre Dön",
                        callback_data=f"highlight_open:{hid_clean}:{user_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅ Diğer Klasörler",
                        callback_data=f"highlights:{user_id}:{username}"
                    )
                ],
                [
                    InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")
                ]
            ])
        )
        return

    if data.startswith("highlight_all:"):
        _, hid_clean, user_id = data.split(":")
        user_id = int(user_id)

        username = context.user_data.get("last_username")

        # Limit kontrolü
        limit = await check_limit(telegram_id)
        if not limit.get("allowed", False):
            text, markup = limit_exceeded_keyboard()
            await query.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
            return

        hid = hid_clean.replace("-", ":")
        items = private.highlight_items(hid)

        if not items:
            await query.message.reply_text("📭 Bu klasörde hikaye yok.")
            return

        # 10'arlı paket gönder
        batch = []
        for i, item in enumerate(items, start=1):
            media_url = private.media_url(item)

            if "video" in media_url:
                batch.append(InputMediaVideo(media_url))
            else:
                batch.append(InputMediaPhoto(media_url))

            # 10 medya olduğunda gönder
            if len(batch) == 10:
                await query.message.reply_media_group(batch)
                batch = []  # sıfırla

        # kalanlar varsa gönder
        if batch:
            await query.message.reply_media_group(batch)

        trays = private.user_highlights_full(user_id)
        tray = next((t for t in trays if t["id"] == hid), None)
        title = tray.get("title", "İsimsiz") if tray else "Bu klasör"

        await query.message.reply_text(
            f"📚 *{title}* klasörüne ait tüm öne çıkanlar gönderildi.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅ Klasörler",
                        callback_data=f"highlights:{user_id}:{username}"
                    )
                ],
                [
                    InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")
                ]
            ])
        )

        return
