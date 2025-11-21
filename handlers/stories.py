from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from igapi.private_api import private
from igapi.download import get_story_thumbnails, download_story
from utils.backend_api import check_limit
from utils.helpers import story_time_ago
from utils.limit_message import limit_exceeded_keyboard


async def handle_stories(update, context):
    query = update.callback_query
    data = query.data
    telegram_id = query.from_user.id


    # ---------------------------
    # Hikaye listesi (limit yer)
    # ---------------------------
    if data.startswith("stories:"):
        _, user_id, username = data.split(":")
        user_id = int(user_id)

        limit = await check_limit(telegram_id)
        if not limit["allowed"]:
            text, markup = limit_exceeded_keyboard()
            await query.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
            return

        thumbnails = get_story_thumbnails(user_id)
        if not thumbnails:
            await query.message.reply_text("📭 Hikaye yok.")
            return

        keyboard = []
        row = []

        for i, _ in enumerate(thumbnails):
            row.append(
                InlineKeyboardButton(
                    str(i+1),
                    callback_data=f"story_item:{i}:{user_id}:{username}"
                )
            )
            if len(row) == 4:
                keyboard.append(row)
                row = []

        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("📚 Tüm Hikayeler", callback_data=f"stories_all:{user_id}:{username}")])
        keyboard.append([InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")])

        await query.message.reply_text(
            "📌 *Hangi hikayeyi görmek istiyorsun?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    # ---------------------------
    # Tek hikaye (limit YEMEZ)
    # ---------------------------
    if data.startswith("story_item:"):
        _, index, user_id, username = data.split(":")
        index = int(index)
        user_id = int(user_id)

        items = private.user_stories(user_id)
        files = download_story(user_id)

        path = files[index]

        if path.endswith(".mp4"):
            await query.message.reply_video(video=open(path, "rb"))
        else:
            await query.message.reply_photo(photo=open(path, "rb"))

        info = story_time_ago(items[index])

        await query.message.reply_text(
            f"Hikaye *{info}* paylaşılmış.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")]
            ])
        )
        return


    # ---------------------------
    # Tüm hikayeler (limit yer)
    # ---------------------------
    if data.startswith("stories_all:"):
        _, user_id, username = data.split(":")
        user_id = int(user_id)

        limit = await check_limit(telegram_id)
        if not limit["allowed"]:
            text, markup = limit_exceeded_keyboard()
            await query.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
            return

        files = download_story(user_id)
        files = files[:10]

        group = []

        for path in files:
            if path.endswith(".mp4"):
                group.append(InputMediaVideo(open(path, "rb")))
            else:
                group.append(InputMediaPhoto(open(path, "rb")))

        await query.message.reply_media_group(group)

        await query.message.reply_text(
            "📚 Tüm hikayeler gönderildi.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Ana Menü", callback_data="back_menu")]])
        )
        return
