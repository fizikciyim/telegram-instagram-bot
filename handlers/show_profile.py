# handlers/show_profile.py

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BACKEND_URL
from igapi.private_api import private


async def show_profile(message, context, username):

    # ---- TELEGRAM ID ----
    telegram_id = context.user_data.get("telegram_id")
    if not telegram_id:
        telegram_id = message.chat_id

    # ---- BACKEND KULLANICI VERİSİ ----
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BACKEND_URL}/user/{telegram_id}")

        u = {}  # her durumda var
        if res.status_code == 200:
            u = res.json()
            daily = u.get("daily_limit", 0)
            used = u.get("used_today", 0)
            remaining = max(daily - used, 0)
        else:
            remaining = None

    # PREMIUM kontrolü
    is_premium = u.get("is_premium", 0) == 1

    # ---- INSTAGRAM PROFİL VERİSİ ----
    user = private.user_info_by_username(username)
    if not user:
        await message.reply_text("❌ Kullanıcı bulunamadı.")
        return

    full_name = user.get("full_name", "Bilinmiyor")
    follower = user.get("edge_followed_by", {}).get("count", 0)
    following = user.get("edge_follow", {}).get("count", 0)
    bio = user.get("biography", "")
    external = user.get("external_url", "")
    verified = user.get("is_verified", False)
    media_count = user.get("edge_owner_to_timeline_media", {}).get("count", 0)
    is_private = user.get("is_private", False)

    # ---- HD PROFİL FOTO ----
    pic = None
    if user.get("profile_pic_url_hd"):
        pic = user.get("profile_pic_url_hd")
    if not pic:
        versions = user.get("hd_profile_pic_versions")
        if versions:
            pic = max(versions, key=lambda x: x.get("width", 0)).get("url")
    if not pic:
        pic = user.get("hd_profile_pic_url_info", {}).get("url")
    if not pic:
        pic = user.get("profile_pic_url")

    if pic:
        try:
            await message.reply_photo(photo=pic)
        except:
            pass

    # ---- AÇIKLAMA METNİ ----
    text = (
        f"👤 *{full_name}* (@{username})\n"
        f"📸 Gönderi: {media_count}\n"
        f"👥 Takipçi: {follower}\n"
        f"🔄 Takip: {following}\n"
    )

    if bio:
        text += f"\n📝 Bio:\n{bio}\n"

    if external:
        text += f"\n🔗 Link: {external}"

    if verified:
        text += "\n✔ Doğrulanmış Hesap"

    text += "\n─────────────────────"

    # ---- PREMIUM / LİMİT GÖSTERİMİ ----
    if is_premium:
        text += "\n\n💎 *Premium Kullanıcı* — Sınırsız kullanım"
    else:
        text += f"\n\n⚡ *Kalan Günlük Hak:* {remaining}"

    # ---- ÖZEL HESAP ----
    if is_private:
        text += (
            "\n\n🔒 *Bu hesap gizlidir.*"
            "\n📌 Bu hesaba ait hiçbir içerik görüntülenemez."
            "\n\n🔍 *Başka bir kullanıcı aramak için kullanıcı adını yazabilirsiniz.*"
        )

        await message.reply_text(text, parse_mode="Markdown")
        return

    # ---- BUTONLAR ----
    user_id = user["id"]

    if is_premium:
        # ⭐ PREMIUM buton seti
        btn_story = "Hikayeler ⭐"
        btn_posts = "Gönderiler ⭐"
        btn_reels = "Reels ⭐"
        btn_highlights = "Öne Çıkanlar ⭐"
    else:
        # ⚡ NORMAL buton seti
        btn_story = "Hikayeler ⚡–1"
        btn_posts = "Gönderiler ⚡–1"
        btn_reels = "Reels ⚡–1"
        btn_highlights = "Öne Çıkanlar ⚡–1"

    keyboard = [
        [
            InlineKeyboardButton(btn_story, callback_data=f"stories:{user_id}:{username}"),
            InlineKeyboardButton(btn_posts, callback_data=f"posts:{user_id}:{username}")
        ],
        [
            InlineKeyboardButton(btn_reels, callback_data=f"reels:{user_id}:{username}"),
            InlineKeyboardButton(btn_highlights, callback_data=f"highlights:{user_id}:{username}")
        ],
        [
            InlineKeyboardButton("🔍 Son Aramalar", callback_data="history_menu"),
            InlineKeyboardButton("⚙ Ayarlar", callback_data="settings")
        ]
    ]

    await message.reply_text(
        text + "\n\nNe yapmak istersin?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
