from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


# ─── Profile Card ─────────────────────────────────────────────────────────────

GENDER_FA = {"male": "مرد 👨", "female": "زن 👩", "other": "سایر 🧑"}
LOOKING_FA = {"male": "مرد", "female": "زن", "any": "همه"}


def profile_card(user: dict, is_own: bool = False) -> str:
    gender = GENDER_FA.get(user.get("gender", ""), user.get("gender", ""))
    looking = LOOKING_FA.get(user.get("looking_for", ""), "")
    lines = [
        f"👤 *{user['name']}*  |  {user['age']} ساله",
        f"📍 {user['city']}   •   {gender}",
    ]
    if user.get("bio"):
        lines.append(f"\n💬 _{user['bio']}_")
    if is_own:
        lines.append(f"\n🔍 دنبال: {looking}  |  سن: {user['min_age']}–{user['max_age']}")
    return "\n".join(lines)


# ─── Keyboards ────────────────────────────────────────────────────────────────

def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 پروفایل من"), KeyboardButton("🔍 جستجو")],
        [KeyboardButton("💞 مچ‌های من"),  KeyboardButton("⚙️ تنظیمات")],
    ], resize_keyboard=True)


def discover_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❤️ لایک",   callback_data="like"),
        InlineKeyboardButton("👎 رد کردن", callback_data="skip"),
        InlineKeyboardButton("🚫 بلاک",   callback_data="block"),
    ]])


def profile_edit_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ ویرایش نام",    callback_data="edit_name"),
         InlineKeyboardButton("🎂 ویرایش سن",     callback_data="edit_age")],
        [InlineKeyboardButton("📍 ویرایش شهر",    callback_data="edit_city"),
         InlineKeyboardButton("💬 ویرایش بیو",    callback_data="edit_bio")],
        [InlineKeyboardButton("📸 تغییر عکس",     callback_data="edit_photo")],
        [InlineKeyboardButton("🔍 تنظیمات جستجو", callback_data="search_settings")],
    ])


def gender_keyboard(field="gender"):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("👨 مرد",    callback_data=f"{field}_male"),
        InlineKeyboardButton("👩 زن",     callback_data=f"{field}_female"),
        InlineKeyboardButton("🧑 سایر",   callback_data=f"{field}_other"),
    ]])


def looking_for_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("👨 مرد",    callback_data="look_male"),
        InlineKeyboardButton("👩 زن",     callback_data="look_female"),
        InlineKeyboardButton("👥 همه",    callback_data="look_any"),
    ]])


def match_action_keyboard(matched_user_id: int):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💬 شروع چت", url=f"tg://user?id={matched_user_id}"),
        InlineKeyboardButton("🚫 بلاک",    callback_data=f"block_match_{matched_user_id}"),
    ]])


def confirm_delete_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ بله، حذف کن", callback_data="confirm_delete"),
        InlineKeyboardButton("❌ انصراف",       callback_data="cancel_delete"),
    ]])
