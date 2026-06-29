from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, CallbackQueryHandler, filters,
)
from database import get_user, update_field, delete_user
from utils.keyboards import (
    looking_for_keyboard, confirm_delete_keyboard, main_menu_keyboard,
)
from utils.states import SET_LOOKING_FOR, SET_AGE_MIN, SET_AGE_MAX


async def show_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("⚠️ ابتدا /start بزن.")
        return

    from utils.keyboards import LOOKING_FA
    text = (
        f"⚙️ *تنظیمات جستجو*\n\n"
        f"🔍 دنبال: {LOOKING_FA.get(user['looking_for'], '—')}\n"
        f"📅 بازه سنی: {user['min_age']}–{user['max_age']}\n\n"
        "برای تغییر دنبال چه کسی؟:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=looking_for_keyboard())
    return SET_LOOKING_FOR


async def set_looking_for(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    looking = query.data.replace("look_", "")
    ctx.user_data["new_looking"] = looking
    await query.edit_message_text("📅 حداقل سن مورد نظرت رو بنویس (مثال: 18):")
    return SET_AGE_MIN


async def set_age_min(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        assert 18 <= v <= 79
    except Exception:
        await update.message.reply_text("⚠️ عدد بین ۱۸ تا ۷۹ وارد کن.")
        return SET_AGE_MIN
    ctx.user_data["new_min_age"] = v
    await update.message.reply_text("📅 حداکثر سن مورد نظرت رو بنویس:")
    return SET_AGE_MAX


async def set_age_max(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        assert ctx.user_data["new_min_age"] <= v <= 80
    except Exception:
        await update.message.reply_text(f"⚠️ باید بزرگ‌تر از {ctx.user_data['new_min_age']} و حداکثر ۸۰ باشه.")
        return SET_AGE_MAX

    uid = update.effective_user.id
    update_field(uid, "looking_for", ctx.user_data["new_looking"])
    update_field(uid, "min_age",     ctx.user_data["new_min_age"])
    update_field(uid, "max_age",     v)
    ctx.user_data.clear()
    await update.message.reply_text("✅ تنظیمات ذخیره شد!", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


# ─── Account deletion ─────────────────────────────────────────────────────────

async def request_delete(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ *حذف اکانت*\n\nاین عملیات برگشت‌ناپذیره. مطمئنی؟",
        parse_mode="Markdown",
        reply_markup=confirm_delete_keyboard(),
    )


async def confirm_delete_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_delete":
        delete_user(query.from_user.id)
        await query.edit_message_text("😢 اکانتت حذف شد. هر وقت خواستی /start بزن.")
    else:
        await query.edit_message_text("❌ حذف لغو شد.")


def build_settings_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^⚙️ تنظیمات$"), show_settings)],
        states={
            SET_LOOKING_FOR: [CallbackQueryHandler(set_looking_for, pattern="^look_")],
            SET_AGE_MIN:     [MessageHandler(filters.TEXT & ~filters.COMMAND, set_age_min)],
            SET_AGE_MAX:     [MessageHandler(filters.TEXT & ~filters.COMMAND, set_age_max)],
        },
        fallbacks=[],
    )


def confirm_delete_handler():
    return CallbackQueryHandler(confirm_delete_callback, pattern="^(confirm_delete|cancel_delete)$")
