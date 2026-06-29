from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import get_user, update_field
from utils.keyboards import profile_card, profile_edit_keyboard, main_menu_keyboard
from utils.states import EDIT_FIELD


async def show_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("⚠️ پروفایلی پیدا نشد. /start بزن.")
        return

    caption = profile_card(user, is_own=True)
    if user.get("photo_id"):
        await update.message.reply_photo(
            photo=user["photo_id"],
            caption=caption,
            parse_mode="Markdown",
            reply_markup=profile_edit_keyboard(),
        )
    else:
        await update.message.reply_text(
            caption,
            parse_mode="Markdown",
            reply_markup=profile_edit_keyboard(),
        )


# ─── Inline edit callbacks ─────────────────────────────────────────────────

EDIT_PROMPTS = {
    "edit_name":  ("name",  "✏️ اسم جدیدت رو بنویس:"),
    "edit_age":   ("age",   "🎂 سن جدیدت رو بنویس (عدد):"),
    "edit_city":  ("city",  "📍 شهر جدیدت رو بنویس:"),
    "edit_bio":   ("bio",   "💬 بیوی جدیدت رو بنویس (حداکثر ۲۰۰ کاراکتر):"),
    "edit_photo": ("photo_id", "📸 عکس جدیدت رو بفرست:"),
}


async def edit_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data
    if key not in EDIT_PROMPTS:
        return
    field, prompt = EDIT_PROMPTS[key]
    ctx.user_data["editing_field"] = field
    await query.message.reply_text(prompt)
    return EDIT_FIELD


async def receive_edit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    field = ctx.user_data.get("editing_field")
    if not field:
        return ConversationHandler.END

    uid = update.effective_user.id

    if field == "photo_id":
        if update.message.photo:
            value = update.message.photo[-1].file_id
        else:
            await update.message.reply_text("⚠️ لطفاً یه عکس بفرست.")
            return EDIT_FIELD
    elif field == "age":
        try:
            value = int(update.message.text.strip())
            assert 18 <= value <= 80
        except Exception:
            await update.message.reply_text("⚠️ سن باید بین ۱۸ تا ۸۰ باشه.")
            return EDIT_FIELD
    elif field == "bio":
        value = update.message.text.strip()[:200]
    else:
        value = update.message.text.strip()
        if len(value) < 2:
            await update.message.reply_text("⚠️ مقدار خیلی کوتاهه.")
            return EDIT_FIELD

    update_field(uid, field, value)
    ctx.user_data.pop("editing_field", None)
    await update.message.reply_text("✅ پروفایلت آپدیت شد!", reply_markup=main_menu_keyboard())
    return ConversationHandler.END
