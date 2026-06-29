from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import get_user, get_matches, block_user, remove_match
from utils.keyboards import profile_card, match_action_keyboard, main_menu_keyboard


async def show_matches(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    matches = get_matches(uid)

    if not matches:
        await update.message.reply_text(
            "💔 هنوز match ای نداری.\nبرو جستجو کن! 🔍",
            reply_markup=main_menu_keyboard(),
        )
        return

    await update.message.reply_text(f"💞 *{len(matches)} مچ* داری:", parse_mode="Markdown")

    for m in matches:
        caption = profile_card(m)
        kb = match_action_keyboard(m["user_id"])
        if m.get("photo_id"):
            await update.message.reply_photo(
                photo=m["photo_id"],
                caption=caption,
                parse_mode="Markdown",
                reply_markup=kb,
            )
        else:
            await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=kb)


async def block_match_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    target_id = int(query.data.replace("block_match_", ""))
    block_user(uid, target_id)
    remove_match(uid, target_id)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("🚫 کاربر بلاک و از لیست مچ‌ها حذف شد.")


def block_match_handler():
    return CallbackQueryHandler(block_match_callback, pattern=r"^block_match_\d+$")
