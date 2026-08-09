# سامانه مدیریت خوابگاه و سلف دانشگاه
# University Dormitory & Cafeteria Management System (Django)

## نصب و اجرا

```bash
# 1. ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. نصب وابستگی‌ها
pip install -r requirements.txt

# 3. مایگریشن
python manage.py migrate

# 4. داده دمو (اختیاری اما توصیه‌شده)
python manage.py seed_demo

# 5. اجرا
python manage.py runserver
```

سپس به آدرس http://127.0.0.1:8000 بروید.

### حساب‌های دمو (بعد از seed_demo)

| نقش | نام کاربری | رمز عبور |
|-----|-----------|---------|
| مدیر | admin | admin1234 |
| دانشجو (برادران) | ali | student1234 |
| دانشجو (برادران) | reza | student1234 |
| دانشجو (خواهران) | zahra | student1234 |

## ساختار اپ‌ها

- **accounts**: کاربر سفارشی، ثبت‌نام، ورود، پروفایل، نقش (دانشجو/کارمند/مدیر)، بخش خواهران/برادران
- **dormitory**: ساختمان، اتاق، تخت، اختصاص دانشجو
- **tickets**: تیکت مشکلات اتاق + پاسخ مدیر
- **cafeteria**: منوی هفتگی، آیتم غذایی، سفارش غذا + کسر از کیف پول
- **wallet**: کیف پول، تراکنش (شارژ / خرید غذا / بازگشت)

## ویژگی‌های حرفه‌ای

- مدل کاربر سفارشی (AbstractUser)
- پشتیبانی کامل i18n (فارسی / انگلیسی) + RTL
- تم دارک / لایت (Frontend)
- سیگنال ساخت خودکار کیف پول
- Context processor برای موجودی و تعداد تیکت‌های باز
- پنل ادمین Django کامل با اینلاین‌ها و اکشن‌ها
- مدیریت تیکت توسط ادمین
- سفارش غذای هفتگی با کسر موجودی
- جداسازی بخش خواهران و برادران

## نکات تولید (Production)

- SECRET_KEY را عوض کنید
- DEBUG = False
- ALLOWED_HOSTS را تنظیم کنید
- از PostgreSQL استفاده کنید
- collectstatic و سرو استاتیک با Nginx/WhiteNoise
- درگاه پرداخت واقعی برای شارژ کیف پول

