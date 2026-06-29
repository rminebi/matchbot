import os
import logging
from dotenv import load_dotenv

from telegram.ext import (
    Application, MessageHandler, CallbackQueryHandler,
    CommandHandler, ConversationHandler, filters,
)

from database import init_db
from handlers import (
    build_registration_handler,
    show_profile, edit_callback, receive_edit,
    start_discovery, discovery_callback_handler,
    show_matches, block_match_handler,
    build_settings_handler, request_delete, confirm_delete_handler,
)
from utils.states import EDIT_FIELD

load_dotenv()
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN not set in .env")

    init_db()

    app = Application.builder().token(token).build()

    app.add_handler(build_registration_handler())

    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_callback, pattern="^edit_")],
        states={
            EDIT_FIELD: [
                MessageHandler(filters.PHOTO, receive_edit),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edit),
            ]
        },
        fallbacks=[],
    )
    app.add_handler(edit_conv)
    app.add_handler(build_settings_handler())
    app.add_handler(MessageHandler(filters.Regex("^👤 پروفایل من$"), show_profile))
    app.add_handler(MessageHandler(filters.Regex("^🔍 جستجو$"), start_discovery))
    app.add_handler(MessageHandler(filters.Regex("^💞 مچ‌های من$"), show_matches))
    app.add_handler(CommandHandler("delete", request_delete))
    app.add_handler(discovery_callback_handler())
    app.add_handler(block_match_handler())
    app.add_handler(confirm_delete_handler())

    logger.info("🚀 Bot started. Listening for updates...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()