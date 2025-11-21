from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from igapi.private_api import private
from utils.backend_api import check_limit  # ⬅️ backend.services.limits yerine bunu kullan
import asyncio
from utils.helpers import format_date
from utils.limit_message import limit_exceeded_keyboard

async def handle_posts(update, context):
    query = update.callback_query
    data = query.data
    telegram_id = query.from_user.id  # limit için


    # -------------------------------------------------------
    # posts:{user_id}:{username}
    # GÖNDERİLER MENÜSÜNÜ AÇMA → 1 HAK
    # -------------------------------------------------------
    if data.startswith("posts:"):
        # ✅ Limit burada, backend üzerinden kontrol edilecek
        limit = await check_limit(telegram_id)
        if not limit.get("allowed", False):
            reason = limit.get("reason")
            if reason == "limit_reached":
                text, markup = limit_exceeded_keyboard()
                await query.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
            else:
                await query.answer("⚠ Kullanıcı bulunamadı!", show_alert=True)
            return

        _, target_id, username = data.split(":")
        target_id = int(target_id)

        await query.message.reply_text("⏳ Gönderiler yükleniyor...")

        result = private.user_posts(target_id)
        if not result:
            await query.message.reply_text("📭 Gönderi yok.")
            return

        context.user_data["posts"] = result["posts"]
        context.user_data["next_max_id"] = result["next"]
        context.user_data["post_user"] = target_id
        context.user_data["post_page"] = 0
        context.user_data["post_username"] = username

        return await send_post_page(query.message, context)



    # -------------------------------------------------------
    # posts_next / posts_prev
    # SAYFA GEZİNME → ÜCRETSİZ
    # -------------------------------------------------------
    if data == "posts_next":
        posts = context.user_data["posts"]
        next_id = context.user_data["next_max_id"]
        target_id = context.user_data["post_user"]

        if (context.user_data["post_page"] + 1) * 10 >= len(posts):
            if next_id:
                result = private.user_posts(target_id, max_id=next_id)
                if result:
                    posts.extend(result["posts"])
                    context.user_data["posts"] = posts
                    context.user_data["next_max_id"] = result["next"]

        context.user_data["post_page"] += 1
        return await send_post_page(query.message, context)


    if data == "posts_prev":
        context.user_data["post_page"] -= 1
        return await send_post_page(query.message, context)



    # -------------------------------------------------------
    # post_item:index
    # TEK GÖNDERİ GÖRME → ÜCRETSİZ
    # -------------------------------------------------------
    if data.startswith("post_item:"):
        index = int(data.split(":")[1])
        posts = context.user_data.get("posts", [])

        if index >= len(posts):
            await query.message.reply_text("Gönderi bulunamadı.")
            return

        media = posts[index]
        items = private.post_media(media)

        caption = media.get("caption", {}).get("text", "Açıklama yok.")
        like_count = media.get("like_count", 0)
        comment_count = media.get("comment_count", 0)
        ts = media.get("taken_at")
        date_text = format_date(ts) if ts else "Bilinmiyor"

        shortcode = media.get("code")
        post_url = f"https://www.instagram.com/p/{shortcode}/" if shortcode else "Link yok"

        caption_text = (
            f"🗓 *Tarih:* {date_text}\n"
            f"❤️ *Beğeni:* {like_count}\n"
            f"💬 *Yorum:* {comment_count}\n"
            f"🔗 *Instagram’da Aç:* {post_url}\n\n"
            f"📝 *Açıklama:*\n{caption}"
        )

        group = []
        for i, item in enumerate(items):
            url = item["url"]
            if item["type"] == "video":
                if i == 0:
                    group.append(InputMediaVideo(url, caption=caption_text, parse_mode="Markdown"))
                else:
                    group.append(InputMediaVideo(url))
            else:
                if i == 0:
                    group.append(InputMediaPhoto(url, caption=caption_text, parse_mode="Markdown"))
                else:
                    group.append(InputMediaPhoto(url))

        await query.message.reply_media_group(group)

        keyboard = [
            [
                InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu"),
                InlineKeyboardButton("📸 Diğer Gönderiler", callback_data="posts_back_to_list"),
            ]
        ]

        await query.message.reply_text("Ne yapmak istersin?", reply_markup=InlineKeyboardMarkup(keyboard))
        return



    # -------------------------------------------------------
    # TOPLU İNDİRME → 1 HAK
    # -------------------------------------------------------
    if data == "posts_download_batch":
        # ✅ Burada da limit kontrolü backend üzerinden
        limit = await check_limit(telegram_id)
        if not limit.get("allowed", False):
            reason = limit.get("reason")
            if reason == "limit_reached":
                text, markup = limit_exceeded_keyboard()
                await query.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
            else:
                await query.answer("⚠ Kullanıcı bulunamadı!", show_alert=True)
            return

        await query.answer()

        posts = context.user_data["posts"]
        page = context.user_data["post_page"]

        start = page * 10
        end = start + 10
        batch = posts[start:end]

        if not batch:
            await query.message.reply_text("📭 Bu sayfada indirilecek gönderi yok.")
            return

        await query.message.reply_text("⏳ Gönderiler hazırlanıyor...")

        all_media = []
        for media in batch:
            items = private.post_media(media)
            for item in items:
                url = item["url"]
                if item["type"] == "video":
                    all_media.append(InputMediaVideo(url))
                else:
                    all_media.append(InputMediaPhoto(url))

        CHUNK = 10
        total = len(all_media)

        for i in range(0, total, CHUNK):
            group = all_media[i:i+CHUNK]
            await query.message.reply_media_group(group)
            await asyncio.sleep(1)

        await query.message.reply_text(
            f"✔ Tüm içerikler gönderildi!\n\n"
            f"• İşlenen gönderi sayısı: {len(batch)}\n"
            f"• Toplam medya: {total}"
        )

        return await send_post_page(query.message, context)



async def send_post_page(message, context):
    posts = context.user_data["posts"]
    page = context.user_data["post_page"]
    next_id = context.user_data["next_max_id"]

    per = 10
    start = page * per
    end = start + per

    items = posts[start:end]
    if not items:
        return await message.reply_text("İçerik yok.")

    keyboard = []
    row = []

    for i, _ in enumerate(items, start=start):
        row.append(InlineKeyboardButton(str(i+1), callback_data=f"post_item:{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅ Önceki", callback_data="posts_prev"))
    if end < len(posts) or next_id:
        nav.append(InlineKeyboardButton("➡ Sonraki", callback_data="posts_next"))
    keyboard.append(nav)

    keyboard.append(
        [InlineKeyboardButton(f"📥 Bu Sayfadaki {len(items)} Gönderiyi İndir", callback_data="posts_download_batch")]
    )

    keyboard.append([InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")])

    await message.reply_text(
        "📸 Hangi gönderiyi görmek istiyorsun?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
