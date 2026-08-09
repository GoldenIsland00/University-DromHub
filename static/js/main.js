/* =====================================================
   Dormitory Management System - Main JS
   Theme, Language, Interactions
   ===================================================== */

(function () {
  'use strict';

  // ---------- i18n Dictionary ----------
  const translations = {
    fa: {
      // Common
      'app.name': 'سامانه خوابگاه و سلف',
      'app.tagline': 'مدیریت هوشمند خوابگاه و تغذیه دانشگاه',
      'nav.home': 'خانه',
      'nav.dashboard': 'داشبورد',
      'nav.profile': 'پروفایل',
      'nav.myroom': 'اتاق من',
      'nav.tickets': 'تیکت‌ها',
      'nav.meals': 'سفارش غذا',
      'nav.wallet': 'کیف پول',
      'nav.admin': 'پنل مدیریت',
      'nav.users': 'کاربران',
      'nav.rooms': 'اتاق‌ها',
      'nav.mealsAdmin': 'منوی غذا',
      'nav.settings': 'تنظیمات',
      'nav.logout': 'خروج',
      'btn.login': 'ورود',
      'btn.register': 'ثبت‌نام',
      'btn.save': 'ذخیره',
      'btn.cancel': 'انصراف',
      'btn.submit': 'ثبت',
      'btn.create': 'ایجاد',
      'btn.reply': 'پاسخ',
      'btn.order': 'سفارش',
      'btn.back': 'بازگشت',
      'btn.theme': 'تم',
      'btn.lang': 'زبان',
      'status.open': 'باز',
      'status.inprogress': 'در حال بررسی',
      'status.resolved': 'حل شده',
      'status.closed': 'بسته',
      'gender.male': 'برادران',
      'gender.female': 'خواهران',
      'role.student': 'دانشجو',
      'role.admin': 'مدیر',
      'role.staff': 'کارمند',

      // Landing
      'landing.hero1': 'مدیریت هوشمند',
      'landing.hero2': 'خوابگاه و سلف',
      'landing.desc': 'سیستم جامع مدیریت خوابگاه (خواهران و برادران)، تیکت مشکلات اتاق، سفارش غذای هفتگی و مدیریت موجودی دانشجویان.',
      'landing.cta': 'ورود به سامانه',
      'landing.stats.students': 'دانشجو',
      'landing.stats.rooms': 'اتاق',
      'landing.stats.tickets': 'تیکت فعال',
      'landing.stats.meals': 'سفارش امروز',

      // Auth
      'auth.login.title': 'خوش آمدید',
      'auth.login.subtitle': 'وارد حساب کاربری خود شوید',
      'auth.register.title': 'ایجاد حساب',
      'auth.register.subtitle': 'ثبت‌نام در سامانه خوابگاه',
      'auth.email': 'ایمیل',
      'auth.password': 'رمز عبور',
      'auth.confirm': 'تأیید رمز عبور',
      'auth.fullname': 'نام و نام خانوادگی',
      'auth.studentId': 'شماره دانشجویی',
      'auth.gender': 'بخش خوابگاه',
      'auth.phone': 'شماره موبایل',
      'auth.forgot': 'رمز عبور را فراموش کرده‌اید؟',
      'auth.noAccount': 'حساب ندارید؟',
      'auth.hasAccount': 'قبلاً ثبت‌نام کرده‌اید؟',
      'auth.loginBtn': 'ورود',
      'auth.registerBtn': 'ثبت‌نام',

      // Dashboard
      'dash.welcome': 'سلام',
      'dash.balance': 'موجودی کیف پول',
      'dash.tickets': 'تیکت‌های باز',
      'dash.room': 'شماره اتاق',
      'dash.bed': 'شماره تخت',
      'dash.mealsToday': 'غذای امروز',
      'dash.recentTickets': 'تیکت‌های اخیر',
      'dash.roommates': 'هم‌اتاقی‌ها',
      'dash.quickActions': 'دسترسی سریع',

      // Room
      'room.title': 'اتاق من',
      'room.number': 'شماره اتاق',
      'room.floor': 'طبقه',
      'room.building': 'ساختمان',
      'room.capacity': 'ظرفیت',
      'room.bed': 'تخت',
      'room.roommate': 'هم‌اتاقی',
      'room.noRoommate': 'هم‌اتاقی ندارد',

      // Tickets
      'tickets.title': 'تیکت‌های من',
      'tickets.create': 'ثبت تیکت جدید',
      'tickets.subject': 'موضوع',
      'tickets.category': 'دسته‌بندی',
      'tickets.priority': 'اولویت',
      'tickets.desc': 'توضیحات',
      'tickets.status': 'وضعیت',
      'tickets.date': 'تاریخ',
      'tickets.cat.facility': 'تسهیلات اتاق',
      'tickets.cat.electric': 'برق و نور',
      'tickets.cat.plumbing': 'لوله‌کشی',
      'tickets.cat.cleaning': 'نظافت',
      'tickets.cat.other': 'سایر',
      'tickets.priority.low': 'کم',
      'tickets.priority.medium': 'متوسط',
      'tickets.priority.high': 'بالا',
      'tickets.priority.urgent': 'فوری',
      'tickets.empty': 'هنوز تیکتی ثبت نکرده‌اید',
      'tickets.reply': 'پاسخ مدیر',
      'tickets.yourReply': 'پاسخ شما',

      // Meals
      'meals.title': 'سفارش غذای هفتگی',
      'meals.select': 'انتخاب وعده',
      'meals.breakfast': 'صبحانه',
      'meals.lunch': 'ناهار',
      'meals.dinner': 'شام',
      'meals.price': 'قیمت',
      'meals.order': 'ثبت سفارش هفته',
      'meals.total': 'جمع کل',
      'meals.days.sat': 'شنبه',
      'meals.days.sun': 'یکشنبه',
      'meals.days.mon': 'دوشنبه',
      'meals.days.tue': 'سه‌شنبه',
      'meals.days.wed': 'چهارشنبه',
      'meals.days.thu': 'پنج‌شنبه',
      'meals.days.fri': 'جمعه',

      // Wallet
      'wallet.title': 'کیف پول',
      'wallet.balance': 'موجودی فعلی',
      'wallet.charge': 'شارژ حساب',
      'wallet.history': 'تاریخچه تراکنش‌ها',
      'wallet.amount': 'مبلغ',
      'wallet.type.charge': 'شارژ',
      'wallet.type.meal': 'خرید غذا',
      'wallet.type.refund': 'بازگشت وجه',

      // Admin
      'admin.dashboard': 'پنل مدیریت',
      'admin.totalUsers': 'کل کاربران',
      'admin.totalRooms': 'کل اتاق‌ها',
      'admin.openTickets': 'تیکت‌های باز',
      'admin.todayOrders': 'سفارش‌های امروز',
      'admin.manageTickets': 'مدیریت تیکت‌ها',
      'admin.manageUsers': 'مدیریت کاربران',
      'admin.manageRooms': 'مدیریت اتاق‌ها',
      'admin.manageMeals': 'مدیریت منوی غذا',

      // Errors
      'error.404.title': 'صفحه پیدا نشد',
      'error.404.desc': 'متأسفانه صفحه‌ای که به دنبال آن هستید وجود ندارد یا حذف شده است.',
      'error.403.title': 'دسترسی غیرمجاز',
      'error.403.desc': 'شما مجوز دسترسی به این بخش را ندارید.',
      'error.500.title': 'خطای سرور',
      'error.500.desc': 'مشکلی در سرور رخ داده است. لطفاً بعداً دوباره تلاش کنید.',
      'error.backHome': 'بازگشت به خانه',
    },
    en: {
      'app.name': 'Dorm & Cafeteria System',
      'app.tagline': 'Smart University Dormitory & Meal Management',
      'nav.home': 'Home',
      'nav.dashboard': 'Dashboard',
      'nav.profile': 'Profile',
      'nav.myroom': 'My Room',
      'nav.tickets': 'Tickets',
      'nav.meals': 'Meal Order',
      'nav.wallet': 'Wallet',
      'nav.admin': 'Admin Panel',
      'nav.users': 'Users',
      'nav.rooms': 'Rooms',
      'nav.mealsAdmin': 'Meal Menu',
      'nav.settings': 'Settings',
      'nav.logout': 'Logout',
      'btn.login': 'Login',
      'btn.register': 'Register',
      'btn.save': 'Save',
      'btn.cancel': 'Cancel',
      'btn.submit': 'Submit',
      'btn.create': 'Create',
      'btn.reply': 'Reply',
      'btn.order': 'Order',
      'btn.back': 'Back',
      'btn.theme': 'Theme',
      'btn.lang': 'Lang',
      'status.open': 'Open',
      'status.inprogress': 'In Progress',
      'status.resolved': 'Resolved',
      'status.closed': 'Closed',
      'gender.male': 'Brothers',
      'gender.female': 'Sisters',
      'role.student': 'Student',
      'role.admin': 'Admin',
      'role.staff': 'Staff',

      'landing.hero1': 'Smart Management of',
      'landing.hero2': 'Dorm & Cafeteria',
      'landing.desc': 'Complete system for dormitory management (Sisters & Brothers sections), room issue tickets, weekly meal ordering and student balance management.',
      'landing.cta': 'Enter the System',
      'landing.stats.students': 'Students',
      'landing.stats.rooms': 'Rooms',
      'landing.stats.tickets': 'Open Tickets',
      'landing.stats.meals': 'Today Orders',

      'auth.login.title': 'Welcome Back',
      'auth.login.subtitle': 'Login to your account',
      'auth.register.title': 'Create Account',
      'auth.register.subtitle': 'Register in the dormitory system',
      'auth.email': 'Email',
      'auth.password': 'Password',
      'auth.confirm': 'Confirm Password',
      'auth.fullname': 'Full Name',
      'auth.studentId': 'Student ID',
      'auth.gender': 'Dorm Section',
      'auth.phone': 'Phone Number',
      'auth.forgot': 'Forgot password?',
      'auth.noAccount': "Don't have an account?",
      'auth.hasAccount': 'Already have an account?',
      'auth.loginBtn': 'Login',
      'auth.registerBtn': 'Register',

      'dash.welcome': 'Hello',
      'dash.balance': 'Wallet Balance',
      'dash.tickets': 'Open Tickets',
      'dash.room': 'Room Number',
      'dash.bed': 'Bed Number',
      'dash.mealsToday': 'Today Meal',
      'dash.recentTickets': 'Recent Tickets',
      'dash.roommates': 'Roommates',
      'dash.quickActions': 'Quick Actions',

      'room.title': 'My Room',
      'room.number': 'Room Number',
      'room.floor': 'Floor',
      'room.building': 'Building',
      'room.capacity': 'Capacity',
      'room.bed': 'Bed',
      'room.roommate': 'Roommate',
      'room.noRoommate': 'No roommate',

      'tickets.title': 'My Tickets',
      'tickets.create': 'Create New Ticket',
      'tickets.subject': 'Subject',
      'tickets.category': 'Category',
      'tickets.priority': 'Priority',
      'tickets.desc': 'Description',
      'tickets.status': 'Status',
      'tickets.date': 'Date',
      'tickets.cat.facility': 'Room Facilities',
      'tickets.cat.electric': 'Electricity & Light',
      'tickets.cat.plumbing': 'Plumbing',
      'tickets.cat.cleaning': 'Cleaning',
      'tickets.cat.other': 'Other',
      'tickets.priority.low': 'Low',
      'tickets.priority.medium': 'Medium',
      'tickets.priority.high': 'High',
      'tickets.priority.urgent': 'Urgent',
      'tickets.empty': 'You have not created any tickets yet',
      'tickets.reply': 'Admin Reply',
      'tickets.yourReply': 'Your Reply',

      'meals.title': 'Weekly Meal Order',
      'meals.select': 'Select Meal',
      'meals.breakfast': 'Breakfast',
      'meals.lunch': 'Lunch',
      'meals.dinner': 'Dinner',
      'meals.price': 'Price',
      'meals.order': 'Submit Weekly Order',
      'meals.total': 'Total',
      'meals.days.sat': 'Sat',
      'meals.days.sun': 'Sun',
      'meals.days.mon': 'Mon',
      'meals.days.tue': 'Tue',
      'meals.days.wed': 'Wed',
      'meals.days.thu': 'Thu',
      'meals.days.fri': 'Fri',

      'wallet.title': 'Wallet',
      'wallet.balance': 'Current Balance',
      'wallet.charge': 'Charge Account',
      'wallet.history': 'Transaction History',
      'wallet.amount': 'Amount',
      'wallet.type.charge': 'Charge',
      'wallet.type.meal': 'Meal Purchase',
      'wallet.type.refund': 'Refund',

      'admin.dashboard': 'Admin Panel',
      'admin.totalUsers': 'Total Users',
      'admin.totalRooms': 'Total Rooms',
      'admin.openTickets': 'Open Tickets',
      'admin.todayOrders': 'Today Orders',
      'admin.manageTickets': 'Manage Tickets',
      'admin.manageUsers': 'Manage Users',
      'admin.manageRooms': 'Manage Rooms',
      'admin.manageMeals': 'Manage Meal Menu',

      'error.404.title': 'Page Not Found',
      'error.404.desc': 'Sorry, the page you are looking for does not exist or has been removed.',
      'error.403.title': 'Access Denied',
      'error.403.desc': 'You do not have permission to access this section.',
      'error.500.title': 'Server Error',
      'error.500.desc': 'Something went wrong on the server. Please try again later.',
      'error.backHome': 'Back to Home',
    }
  };

  // ---------- State ----------
  let currentLang = localStorage.getItem('dorm_lang') || 'fa';
  let currentTheme = localStorage.getItem('dorm_theme') || 'dark';

  // ---------- Apply Language ----------
  function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('dorm_lang', lang);
    document.documentElement.lang = lang;
    document.body.classList.toggle('rtl', lang === 'fa');

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (translations[lang] && translations[lang][key]) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = translations[lang][key];
        } else {
          el.textContent = translations[lang][key];
        }
      }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (translations[lang] && translations[lang][key]) {
        el.placeholder = translations[lang][key];
      }
    });

    // Update lang toggle button text
    const langBtn = document.getElementById('langToggle');
    if (langBtn) {
      langBtn.querySelector('span').textContent = lang === 'fa' ? 'EN' : 'FA';
    }
  }

  // ---------- Apply Theme ----------
  function applyTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('dorm_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);

    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
      const icon = themeBtn.querySelector('svg, i');
      // simple text update
      themeBtn.querySelector('span').textContent = theme === 'dark' ? '☀️' : '🌙';
    }
  }

  // ---------- Init ----------
  function init() {
    applyLanguage(currentLang);
    applyTheme(currentTheme);

    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
      });
    }

    // Lang toggle
    const langToggle = document.getElementById('langToggle');
    if (langToggle) {
      langToggle.addEventListener('click', () => {
        applyLanguage(currentLang === 'fa' ? 'en' : 'fa');
      });
    }

    // Mobile sidebar
    const menuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.querySelector('.sidebar');
    if (menuBtn && sidebar) {
      menuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
    }

    // Meal selection
    document.querySelectorAll('.meal-option').forEach(opt => {
      opt.addEventListener('click', function () {
        const parent = this.closest('.day-card');
        if (parent) {
          parent.querySelectorAll('.meal-option').forEach(o => o.classList.remove('selected'));
        }
        this.classList.toggle('selected');
      });
    });

    // Simple form validation demo
    document.querySelectorAll('form[data-validate]').forEach(form => {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        let valid = true;
        form.querySelectorAll('[required]').forEach(input => {
          if (!input.value.trim()) {
            valid = false;
            input.style.borderColor = 'var(--danger)';
          } else {
            input.style.borderColor = '';
          }
        });
        if (valid) {
          // Demo success
          const btn = form.querySelector('[type="submit"]');
          if (btn) {
            const original = btn.textContent;
            btn.textContent = currentLang === 'fa' ? '✓ ثبت شد' : '✓ Submitted';
            btn.disabled = true;
            setTimeout(() => {
              btn.textContent = original;
              btn.disabled = false;
              // In real app redirect or show success
            }, 1500);
          }
        }
      });
    });

    // Modal helpers
    window.openModal = function (id) {
      const modal = document.getElementById(id);
      if (modal) modal.classList.add('active');
    };
    window.closeModal = function (id) {
      const modal = document.getElementById(id);
      if (modal) modal.classList.remove('active');
    };

    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', function (e) {
        if (e.target === this) this.classList.remove('active');
      });
    });

    // Animate cards on load
    document.querySelectorAll('.stat-card, .card, .ticket-item, .room-card').forEach((el, i) => {
      el.style.opacity = '0';
      el.style.animation = `fadeIn 0.4s ease ${i * 0.05}s forwards`;
    });
  }

  // Run when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for external use
  window.DormApp = {
    setLang: applyLanguage,
    setTheme: applyTheme,
    t: (key) => (translations[currentLang] && translations[currentLang][key]) || key
  };
})();
