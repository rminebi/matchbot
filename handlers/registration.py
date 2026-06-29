from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, CallbackQueryHandler, filters,
)
from database import upsert_user, get_user
from utils.keyboards import gender_keyboard, looking_for_keyboard, main_menu_keyboard, profile_card
from utils.states import REG_NAME, REG_AGE, REG_GENDER, REG_CITY, REG_BIO, REG_PHOTO, REG_LOOKING_FOR, REG_AGE_RANGE


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if user:
        await update.message.reply_text(
            f"👋 خوش برگشتی، *{user['name']}*!\nاز منو پایین شروع کن:",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "👋 سلام! به *Match Bot* خوش اومدی 💫\n\n"
        "بیا یه پروفایل کوتاه بسازیم.\n\n"
        "اول، *اسمت* چیه؟",
        parse_mode="Markdown",
    )
    return REG_NAME


async def reg_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 2 or len(name) > 40:
        await update.message.reply_text("⚠️ لطفاً یه اسم بین ۲ تا ۴۰ حرف وارد کن.")
        return REG_NAME
    ctx.user_data["name"] = name
    await update.message.reply_text(f"عالیه، {name}! 🎉\n\nحالا *سنت* رو بنویس (عدد):", parse_mode="Markdown")
    return REG_AGE


async def reg_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text.strip())
        assert 18 <= age <= 80
    except (ValueError, AssertionError):
        await update.message.reply_text("⚠️ سن باید بین ۱۸ تا ۸۰ باشه.")
        return REG_AGE
    ctx.user_data["age"] = age
    await update.message.reply_text("جنسیتت رو انتخاب کن:", reply_markup=gender_keyboard("gender"))
    return REG_GENDER


async def reg_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data.replace("gender_", "")
    ctx.user_data["gender"] = gender
    await query.edit_message_text("📍 *شهرت* رو بنویس:", parse_mode="Markdown")
    return REG_CITY


async def reg_city(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    if len(city) < 2:
        await update.message.reply_text("⚠️ نام شهر خیلی کوتاهه.")
        return REG_CITY
    ctx.user_data["city"] = city
    await update.message.reply_text(
        "💬 یه *بیو* کوتاه درباره خودت بنویس (یا /skip کن):",
        parse_mode="Markdown",
    )
    return REG_BIO


async def reg_bio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.startswith("/skip"):
        ctx.user_data["bio"] = ""
    else:
        bio = update.message.text.strip()[:200]
        ctx.user_data["bio"] = bio
    await update.message.reply_text("📸 عکس پروفایلت رو بفرست (یا /skip کن):")
    return REG_PHOTO


async def reg_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        ctx.user_data["photo_id"] = update.message.photo[-1].file_id
    else:
        ctx.user_data["photo_id"] = None
    await update.message.reply_text("🔍 دنبال چه کسی می‌گردی؟", reply_markup=looking_for_keyboard())
    return REG_LOOKING_FOR


async def reg_looking_for(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    looking = query.data.replace("look_", "")
    ctx.user_data["looking_for"] = looking
    await query.edit_message_text(
        "📅 بازه سنی مورد نظرت رو بنویس.\n"
        "مثال: `18-35`",
        parse_mode="Markdown",
    )
    return REG_AGE_RANGE


async def reg_age_range(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.strip().replace(" ", "").split("-")
        min_age, max_age = int(parts[0]), int(parts[1])
        assert 18 <= min_age <= max_age <= 80
    except Exception:
        await update.message.reply_text("⚠️ فرمت اشتباهه. مثال: `18-35`", parse_mode="Markdown")
        return REG_AGE_RANGE

    d = ctx.user_data
    upsert_user(
        user_id=update.effective_user.id,
        username=update.effective_user.username or "",
        name=d["name"], age=d["age"], gender=d["gender"],
        city=d["city"], bio=d.get("bio",""), photo_id=d.get("photo_id"),
        looking_for=d["looking_for"], min_age=min_age, max_age=max_age,
    )
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"✅ *پروفایلت ساخته شد!*\n\n{profile_card(user, is_own=True)}",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    ctx.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("❌ عملیات لغو شد.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


def build_registration_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REG_NAME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_AGE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_age)],
            REG_GENDER:     [CallbackQueryHandler(reg_gender, pattern="^gender_")],
            REG_CITY:       [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_city)],
            REG_BIO:        [MessageHandler(filters.TEXT | filters.COMMAND, reg_bio)],
            REG_PHOTO:      [MessageHandler(filters.PHOTO | filters.COMMAND, reg_photo)],
            REG_LOOKING_FOR:[CallbackQueryHandler(reg_looking_for, pattern="^look_")],
            REG_AGE_RANGE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_age_range)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
