from telegram import Update
from telegram.ext import ContextTypes

from handlers.stories import handle_stories
from handlers.posts import handle_posts
from handlers.reels import handle_reels
from handlers.highlights import handle_highlights
from handlers.profile import handle_profile
from handlers.history import handle_history
from handlers.start import send_main_menu
from handlers.buy import handle_buy
from handlers.premium_info import handle_premium_info

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # STORY
    if data.startswith("stories:") or data.startswith("story_item:") or data.startswith("stories_all:"):
        return await handle_stories(update, context)

    # POSTS
    if data.startswith("posts:") or data.startswith("post_item:") or data in [
        "posts_next", "posts_prev", "posts_back_to_list", "posts_download_batch"
    ]:
        return await handle_posts(update, context)

    # REELS
    if data.startswith("reels:"):
        return await handle_reels(update, context)

    # HIGHLIGHTS
    if (
        data.startswith("highlights:")
        or data.startswith("highlight_open:")
        or data.startswith("highlight_story:")
        or data.startswith("highlight_all:")
    ):
        return await handle_highlights(update, context)

    # HISTORY
    if data in ["history_menu", "clear_history"]:
        return await handle_history(update, context)

    if data.startswith("profile_open:"):
        return await handle_profile(update, context)

    # ANA MENÜ
    if data == "back_menu":
        username = context.user_data.get("last_username")
        return await send_main_menu(query.message, context, username)

    if data.startswith("buy:"):
        return await handle_buy(update, context)
    

    if data == "premium_open":
        query = update.callback_query
        await query.answer()
        return await handle_buy(update, context)

    # Default (tanınamayan callback)
    await query.answer("Komut tanınamadı.", show_alert=True)
