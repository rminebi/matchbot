from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import get_user, get_candidates, add_like, block_user
from utils.keyboards import profile_card, discover_keyboard, match_action_keyboard, main_menu_keyboard


async def start_discovery(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    me = get_user(uid)
    if not me:
        await update.message.reply_text("⚠️ اول /start بزن و پروفایل بساز.")
        return

    candidates = get_candidates(uid, limit=20)
    if not candidates:
        await update.message.reply_text(
            "😔 فعلاً کسی برای نمایش نیست.\nبعداً دوباره امتحان کن!",
            reply_markup=main_menu_keyboard(),
        )
        return

    ctx.user_data["queue"] = candidates
    await _show_next(update.message, ctx)


async def _show_next(message, ctx):
    queue = ctx.user_data.get("queue", [])
    if not queue:
        await message.reply_text(
            "🎉 همه رو دیدی! بعداً دوباره سر بزن.",
            reply_markup=main_menu_keyboard(),
        )
        return

    candidate = queue[0]
    ctx.user_data["current_candidate"] = candidate
    caption = profile_card(candidate)

    if candidate.get("photo_id"):
        await message.reply_photo(
            photo=candidate["photo_id"],
            caption=caption,
            parse_mode="Markdown",
            reply_markup=discover_keyboard(),
        )
    else:
        await message.reply_text(
            caption,
            parse_mode="Markdown",
            reply_markup=discover_keyboard(),
        )


async def discovery_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    uid = update.effective_user.id
    candidate = ctx.user_data.get("current_candidate")

    if not candidate:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    # Pop from queue
    queue = ctx.user_data.get("queue", [])
    if queue and queue[0]["user_id"] == candidate["user_id"]:
        queue.pop(0)
    ctx.user_data["queue"] = queue

    if action == "like":
        matched = add_like(uid, candidate["user_id"])
        if matched:
            await query.message.reply_text(
                f"🎉 *Match!* تو و *{candidate['name']}* به هم علاقه دارید!\n"
                "می‌تونید چت کنید 👇",
                parse_mode="Markdown",
                reply_markup=match_action_keyboard(candidate["user_id"]),
            )
            # Notify matched user
            try:
                me = get_user(uid)
                await ctx.bot.send_message(
                    chat_id=candidate["user_id"],
                    text=f"🎉 *Match جدید!* *{me['name']}* هم تو رو لایک کرده!\n👇 چت رو شروع کن:",
                    parse_mode="Markdown",
                    reply_markup=match_action_keyboard(uid),
                )
            except Exception:
                pass  # User may have blocked bot
        else:
            await query.answer("❤️ لایک ثبت شد!", show_alert=False)

    elif action == "block":
        block_user(uid, candidate["user_id"])
        await query.answer("🚫 بلاک شد.", show_alert=False)

    # Skip or continue
    await query.edit_message_reply_markup(reply_markup=None)
    await _show_next(query.message, ctx)


def discovery_callback_handler():
    return CallbackQueryHandler(discovery_callback, pattern="^(like|skip|block)$")
