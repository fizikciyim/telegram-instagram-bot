from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import BOT_TOKEN
from handlers.start import start
from handlers.profile import handle_profile_text
from handlers.callback import callback
from handlers.last import last_profile
from handlers.history import history_command
from handlers.premium_info import handle_premium_info


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("last", last_profile))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_profile_text))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(CommandHandler("history", history_command))
app.add_handler(CommandHandler("premium", handle_premium_info))

print("Bot çalışıyor...")
app.run_polling()
