# 💞 Match Bot تلگرام

ربات دوست‌یابی تلگرام با پایتون — مشابه Leo Match & Meet

---

## ✨ قابلیت‌ها

| قابلیت | وضعیت |
|--------|--------|
| ثبت‌نام با پروفایل کامل | ✅ |
| آپلود عکس | ✅ |
| جستجو بر اساس سن / شهر / جنسیت | ✅ |
| سیستم لایک و Match | ✅ |
| اطلاع‌رسانی Match به هر دو طرف | ✅ |
| ویرایش پروفایل | ✅ |
| بلاک کردن کاربر | ✅ |
| تنظیمات جستجو | ✅ |
| حذف اکانت | ✅ |

---

## 🚀 راه‌اندازی

### ۱. دریافت توکن ربات

به [@BotFather](https://t.me/BotFather) پیام بده و یه ربات جدید بساز:
```
/newbot
```
توکن رو کپی کن.

### ۲. نصب وابستگی‌ها

```bash
cd matchbot
python -m venv venv
source venv/bin/activate   # ویندوز: venv\Scripts\activate
pip install -r requirements.txt
```

### ۳. تنظیم .env

```bash
cp .env.example .env
# فایل .env رو باز کن و توکنت رو بذار
```

### ۴. اجرا

```bash
python main.py
```

---

## 📂 ساختار پروژه

```
matchbot/
├── main.py                  # نقطه ورود — ساخت Application و ثبت handlers
├── requirements.txt
├── .env.example
│
├── database/
│   ├── __init__.py
│   ├── db.py                # اتصال SQLite + init_db
│   └── repository.py        # همه کوئری‌های DB
│
├── handlers/
│   ├── __init__.py
│   ├── registration.py      # /start + ثبت‌نام
│   ├── profile.py           # نمایش و ویرایش پروفایل
│   ├── discovery.py         # جستجو / swipe / لایک
│   ├── matches.py           # لیست مچ‌ها
│   └── settings.py          # تنظیمات جستجو + حذف اکانت
│
└── utils/
    ├── keyboards.py         # همه keyboards و فرمت پروفایل
    └── states.py            # ثابت‌های ConversationHandler
```

---

## 🗄️ مدل داده (SQLite)

```
users    → پروفایل کاربران
likes    → لایک‌های یک‌طرفه
matches  → مچ‌های دوطرفه
blocks   → بلاک‌ها
```

---

## 🛠️ توسعه‌های پیشنهادی

- [ ] فیلتر بر اساس شهر (regex/fuzzy)
- [ ] محدودیت لایک روزانه (anti-spam)
- [ ] پنل ادمین با `/admin`
- [ ] پشتیبانی از چند عکس
- [ ] گزارش (report) کاربر
- [ ] Webhook به جای polling برای production
