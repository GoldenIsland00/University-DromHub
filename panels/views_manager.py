from decimal import Decimal
"""پنل مدیریت: آمار کلی و مدیریت کاربران با سطح دسترسی."""
from django.contrib import messages
from django.db.models import Count, Q
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.permissions import manager_required
from cafeteria.models import MealOrder
from cafeteria.views import get_current_week_start, get_today_weekday
from dormitory.models import AccessLog, Room
from tickets.models import Ticket
from wallet.models import Transaction
from .forms import SetPasswordForm, UserCreateForm, UserEditForm, WalletChargeForm


@manager_required
def dashboard(request):
    today = timezone.localdate()
    role_counts = dict(User.objects.values_list('role').annotate(n=Count('id')))
    open_statuses = ['open', 'in_progress']
    return render(request, 'panels/manager/dashboard.html', {
        'total_users': User.objects.count(),
        'role_stats': [(label, role_counts.get(value, 0), value) for value, label in User.Role.choices],
        'total_rooms': Room.objects.count(),
        'male_rooms': Room.objects.filter(building__section='male').count(),
        'female_rooms': Room.objects.filter(building__section='female').count(),
        'male_students': User.objects.filter(gender='male', role='student').count(),
        'female_students': User.objects.filter(gender='female', role='student').count(),
        'open_tickets': Ticket.objects.filter(status__in=open_statuses).count(),
        'unassigned_tickets': Ticket.objects.filter(status__in=open_statuses, assigned_to__isnull=True).count(),
        'today_orders': MealOrder.objects.filter(menu__week_start=get_current_week_start(today), menu__weekday=get_today_weekday(today)).count(),
        'today_gate': AccessLog.objects.filter(created_at__date=today).count(),
        'recent_tickets': Ticket.objects.filter(status='open').select_related('user')[:6],
    })


@manager_required
def users(request):
    qs = User.objects.all()
    role = request.GET.get('role', '')
    q = request.GET.get('q', '').strip()
    if role:
        qs = qs.filter(role=role)
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
                       | Q(student_id__icontains=q) | Q(phone__icontains=q))
    # مدیر غیرسیستم با بخش مشخص فقط دانشجویان همان بخش را می‌بیند (در نقش دانشجو)
    if not request.user.is_admin_user and request.user.gender in ('male', 'female'):
        from django.db.models import Q as _Q
        qs = qs.filter(_Q(role=User.Role.STUDENT, gender=request.user.gender) | ~_Q(role=User.Role.STUDENT))
    return render(request, 'panels/manager/users.html', {
        'users': qs, 'role': role, 'q': q, 'roles': User.Role.choices,
    })


@manager_required
def user_create(request):
    initial = {'role': request.GET.get('role')} if request.GET.get('role') else None
    if request.method == 'POST':
        form = UserCreateForm(request.POST, acting_user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('کاربر «%(u)s» با نقش «%(r)s» ساخته شد.') % {
                'u': user.display_name, 'r': user.get_role_display()})
            return redirect('panels:manager_users')
    else:
        form = UserCreateForm(acting_user=request.user, initial=initial)
    return render(request, 'panels/manager/user_form.html', {'form': form, 'creating': True})


def _can_manage(actor, target):
    """مدیریت نمی‌تواند مدیر سیستم/سوپریوزر را ویرایش کند."""
    return actor.is_admin_user or not target.is_admin_user


@manager_required
def user_edit(request, pk):
    target = get_object_or_404(User, pk=pk)
    if not _can_manage(request.user, target):
        messages.error(request, _('اجازه ویرایش این کاربر را ندارید.'))
        return redirect('panels:manager_users')

    form = UserEditForm(instance=target, acting_user=request.user)
    pw_form = SetPasswordForm(user=target)
    charge_form = WalletChargeForm()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        if action == 'save':
            form = UserEditForm(request.POST, instance=target, acting_user=request.user)
            if form.is_valid():
                if target == request.user and not form.cleaned_data['is_active']:
                    form.add_error('is_active', _('نمی‌توانید حساب خودتان را غیرفعال کنید.'))
                elif target == request.user and form.cleaned_data['role'] != target.role:
                    form.add_error('role', _('نمی‌توانید نقش خودتان را تغییر دهید.'))
                else:
                    form.save()
                    messages.success(request, _('اطلاعات کاربر ذخیره شد.'))
                    return redirect('panels:manager_users')
        elif action == 'password':
            pw_form = SetPasswordForm(request.POST, user=target)
            if pw_form.is_valid():
                target.set_password(pw_form.cleaned_data['password1'])
                target.save(update_fields=['password'])
                messages.success(request, _('رمز عبور تغییر کرد.'))
                return redirect('panels:manager_user_edit', pk=pk)
        elif action == 'charge' and target.is_student:
            charge_form = WalletChargeForm(request.POST)
            if charge_form.is_valid():
                target.wallet.deposit(
                    charge_form.cleaned_data['amount'],
                    description=charge_form.cleaned_data['description'] or _('شارژ توسط مدیریت'),
                    performed_by=request.user,
                    transaction_type=Transaction.Type.ADJUSTMENT,
                )
                messages.success(request, _('کیف پول شارژ شد.'))
                return redirect('panels:manager_user_edit', pk=pk)

    return render(request, 'panels/manager/user_form.html', {
        'form': form, 'pw_form': pw_form, 'charge_form': charge_form,
        'target': target, 'creating': False,
    })


@manager_required
@require_POST
def user_toggle_active(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target == request.user:
        messages.error(request, _('نمی‌توانید حساب خودتان را غیرفعال کنید.'))
    elif not _can_manage(request.user, target):
        messages.error(request, _('اجازه ویرایش این کاربر را ندارید.'))
    else:
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        messages.success(request, _('وضعیت کاربر تغییر کرد.'))
    return redirect(request.POST.get('next') or 'panels:manager_users')


# ---------------------------------------------------------------------------
# وارد کردن دانشجویان از اکسل + بک‌آپ و بازگردانی
# ---------------------------------------------------------------------------
import io
import os
import shutil
import tempfile
from datetime import datetime

from django.conf import settings
from django.core.management import call_command
from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


DEFAULT_STUDENT_PASSWORD = 'student1234'

# ستون‌های مورد انتظار در فایل اکسل (به ترتیب)
EXCEL_HEADERS = [
    'username',       # نام کاربری (الزامی، یکتا)
    'first_name',     # نام
    'last_name',      # نام خانوادگی
    'student_id',     # شماره دانشجویی (الزامی، یکتا)
    'gender',         # male یا female
    'phone',          # موبایل (اختیاری)
    'email',          # ایمیل (اختیاری)
    'password',       # رمز عبور (اختیاری؛ پیش‌فرض student1234)
]


@manager_required
def students_import(request):
    """صفحه وارد کردن دانشجویان از اکسل + نمایش راهنما."""
    return render(request, 'panels/manager/students_import.html', {
        'headers': EXCEL_HEADERS,
        'default_password': DEFAULT_STUDENT_PASSWORD,
        'openpyxl_ok': OPENPYXL_AVAILABLE,
    })


@manager_required
def students_import_template(request):
    """دانلود فایل نمونه اکسل برای وارد کردن دانشجویان."""
    if not OPENPYXL_AVAILABLE:
        messages.error(request, _('کتابخانه openpyxl نصب نیست. pip install openpyxl'))
        return redirect('panels:manager_students_import')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Students'

    header_fill = PatternFill(start_color='2563EB', end_color='2563EB', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')

    for col, h in enumerate(EXCEL_HEADERS, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    # ردیف نمونه
    sample = ['ali1400', 'علی', 'محمدی', '400123456', 'male', '09121234567', 'ali@example.com', '']
    for col, val in enumerate(sample, 1):
        ws.cell(row=2, column=col, value=val)

    sample2 = ['zahra1400', 'زهرا', 'احمدی', '400654321', 'female', '09129876543', '', 'mypass123']
    for col, val in enumerate(sample2, 1):
        ws.cell(row=3, column=col, value=val)

    for col in range(1, len(EXCEL_HEADERS) + 1):
        ws.column_dimensions[chr(64 + col) if col <= 26 else 'A'].width = 16

    # برگه راهنما
    ws2 = wb.create_sheet('راهنما')
    ws2['A1'] = 'راهنمای وارد کردن دانشجویان'
    ws2['A1'].font = Font(bold=True, size=14)
    guide = [
        '',
        'ستون‌های الزامی: username, first_name, last_name, student_id, gender',
        'gender باید یکی از این دو باشد: male (برادران) یا female (خواهران)',
        'اگر password خالی باشد، رمز پیش‌فرض student1234 قرار می‌گیرد.',
        'اگر username یا student_id تکراری باشد، آن ردیف رد می‌شود.',
        'نقش همه کاربران واردشده به‌صورت خودکار student خواهد بود.',
        'کیف پول به‌صورت خودکار برای هر دانشجو ساخته می‌شود.',
    ]
    for i, line in enumerate(guide, 2):
        ws2.cell(row=i, column=1, value=line)
    ws2.column_dimensions['A'].width = 80

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = 'students_import_template.xlsx'
    response = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@manager_required
@require_http_methods(['POST'])
def students_import_upload(request):
    """پردازش فایل اکسل و ساخت دانشجویان."""
    if not OPENPYXL_AVAILABLE:
        messages.error(request, _('کتابخانه openpyxl نصب نیست.'))
        return redirect('panels:manager_students_import')

    f = request.FILES.get('excel_file')
    if not f:
        messages.error(request, _('فایلی انتخاب نشده است.'))
        return redirect('panels:manager_students_import')

    if not f.name.lower().endswith(('.xlsx', '.xlsm')):
        messages.error(request, _('فقط فایل‌های Excel با پسوند .xlsx پذیرفته می‌شوند.'))
        return redirect('panels:manager_students_import')

    try:
        wb = load_workbook(f, read_only=True, data_only=True)
        ws = wb.active
    except Exception as e:
        messages.error(request, _('خطا در خواندن فایل: %(e)s') % {'e': e})
        return redirect('panels:manager_students_import')

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        messages.error(request, _('فایل خالی است.'))
        return redirect('panels:manager_students_import')

    # نرمال‌سازی هدر
    raw_headers = [str(h).strip().lower() if h is not None else '' for h in rows[0]]
    header_map = {}
    for i, h in enumerate(raw_headers):
        if h in EXCEL_HEADERS:
            header_map[h] = i

    required = ['username', 'first_name', 'last_name', 'student_id', 'gender']
    missing = [h for h in required if h not in header_map]
    if missing:
        messages.error(request, _('ستون‌های الزامی یافت نشد: %(m)s') % {'m': ', '.join(missing)})
        return redirect('panels:manager_students_import')

    created = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(rows[1:], start=2):
        if not row or all(c is None or str(c).strip() == '' for c in row):
            continue

        def cell(key):
            idx = header_map.get(key)
            if idx is None or idx >= len(row):
                return ''
            val = row[idx]
            return str(val).strip() if val is not None else ''

        username = cell('username')
        first_name = cell('first_name')
        last_name = cell('last_name')
        student_id = cell('student_id')
        gender = cell('gender').lower()
        phone = cell('phone')
        email = cell('email')
        password = cell('password') or DEFAULT_STUDENT_PASSWORD

        if not username or not student_id:
            errors.append(_('ردیف %(r)s: نام کاربری یا شماره دانشجویی خالی است.') % {'r': row_num})
            skipped += 1
            continue

        if gender not in ('male', 'female'):
            errors.append(_('ردیف %(r)s: gender باید male یا female باشد (مقدار: %(g)s).') % {
                'r': row_num, 'g': gender or 'خالی'})
            skipped += 1
            continue

        if User.objects.filter(username=username).exists():
            errors.append(_('ردیف %(r)s: نام کاربری «%(u)s» تکراری است.') % {'r': row_num, 'u': username})
            skipped += 1
            continue

        if User.objects.filter(student_id=student_id).exists():
            errors.append(_('ردیف %(r)s: شماره دانشجویی «%(s)s» تکراری است.') % {'r': row_num, 's': student_id})
            skipped += 1
            continue

        try:
            user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                gender=gender,
                phone=phone,
                email=email,
                role=User.Role.STUDENT,
                is_active=True,
            )
            user.set_password(password)
            user.save()
            created += 1
        except Exception as e:
            errors.append(_('ردیف %(r)s: %(e)s') % {'r': row_num, 'e': e})
            skipped += 1

    if created:
        messages.success(request, _('%(n)s دانشجو با موفقیت وارد شد.') % {'n': created})
    if skipped:
        messages.warning(request, _('%(n)s ردیف رد شد.') % {'n': skipped})
    for err in errors[:15]:
        messages.error(request, err)
    if len(errors) > 15:
        messages.error(request, _('و %(n)s خطای دیگر…') % {'n': len(errors) - 15})

    return redirect('panels:manager_students_import')


@manager_required
def backup_page(request):
    """صفحه بک‌آپ و بازگردانی."""
    db_path = settings.DATABASES['default']['NAME']
    db_size = 0
    if os.path.isfile(db_path):
        db_size = os.path.getsize(db_path)
    return render(request, 'panels/manager/backup.html', {
        'db_size': db_size,
        'db_engine': settings.DATABASES['default']['ENGINE'],
        'is_sqlite': 'sqlite' in settings.DATABASES['default']['ENGINE'],
    })


@manager_required
def backup_download_db(request):
    """دانلود فایل کامل دیتابیس SQLite (بک‌آپ کامل)."""
    db_path = settings.DATABASES['default']['NAME']
    if not os.path.isfile(db_path):
        messages.error(request, _('فایل دیتابیس یافت نشد.'))
        return redirect('panels:manager_backup')

    # کپی امن برای جلوگیری از قفل شدن
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite3')
    tmp.close()
    shutil.copy2(db_path, tmp.name)

    response = FileResponse(
        open(tmp.name, 'rb'),
        as_attachment=True,
        filename=f'dormhub_backup_{ts}.sqlite3',
        content_type='application/x-sqlite3',
    )
    # فایل موقت بعد از ارسال پاک می‌شود (تقریبی)
    return response


@manager_required
def backup_download_json(request):
    """دانلود dump داده به صورت JSON (قابل حمل‌تر)."""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    buf = io.StringIO()
    call_command(
        'dumpdata',
        '--natural-foreign',
        '--natural-primary',
        '--exclude', 'contenttypes',
        '--exclude', 'auth.permission',
        '--exclude', 'sessions.session',
        '--exclude', 'admin.logentry',
        stdout=buf,
    )
    data = buf.getvalue().encode('utf-8')
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="dormhub_data_{ts}.json"'
    return response


@manager_required
@require_http_methods(['POST'])
def backup_restore(request):
    """بازگردانی از فایل بک‌آپ (sqlite3 یا json)."""
    f = request.FILES.get('backup_file')
    if not f:
        messages.error(request, _('فایلی انتخاب نشده است.'))
        return redirect('panels:manager_backup')

    name = f.name.lower()
    confirm = request.POST.get('confirm') == 'yes'
    if not confirm:
        messages.error(request, _('برای بازگردانی باید تأیید کنید که از عواقب آن آگاهید.'))
        return redirect('panels:manager_backup')

    if name.endswith(('.sqlite3', '.db', '.sqlite')):
        # بازگردانی فایل SQLite
        db_path = settings.DATABASES['default']['NAME']
        # بک‌آپ از وضعیت فعلی قبل از جایگزینی
        safety = str(db_path) + f'.pre_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        try:
            if os.path.isfile(db_path):
                shutil.copy2(db_path, safety)
            # نوشتن فایل آپلودشده
            with open(db_path, 'wb') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            messages.success(
                request,
                _('بازگردانی دیتابیس انجام شد. نسخه قبلی در %(p)s ذخیره شد. لطفاً از سیستم خارج و دوباره وارد شوید.')
                % {'p': os.path.basename(safety)},
            )
        except Exception as e:
            messages.error(request, _('خطا در بازگردانی: %(e)s') % {'e': e})
            if os.path.isfile(safety):
                shutil.copy2(safety, db_path)
        return redirect('panels:manager_backup')

    elif name.endswith('.json'):
        # loaddata از JSON
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='wb')
        try:
            for chunk in f.chunks():
                tmp.write(chunk)
            tmp.close()
            # loaddata داده‌ها را اضافه/به‌روز می‌کند؛ برای پاک‌سازی کامل نیاز به flush است
            if request.POST.get('flush') == 'yes':
                call_command('flush', interactive=False, verbosity=0)
            call_command('loaddata', tmp.name, verbosity=0)
            messages.success(request, _('داده‌ها از فایل JSON با موفقیت بارگذاری شدند.'))
        except Exception as e:
            messages.error(request, _('خطا در بارگذاری JSON: %(e)s') % {'e': e})
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
        return redirect('panels:manager_backup')

    else:
        messages.error(request, _('فرمت پشتیبانی‌نشده. فقط .sqlite3 یا .json'))
        return redirect('panels:manager_backup')


# ---------------------------------------------------------------------------
# اختصاص اتاق، گزارش‌ها، تنظیمات، مرخصی‌ها
# ---------------------------------------------------------------------------
from django.db.models import Sum
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from core.models import SystemSettings, Notification
from dormitory.models import Building, Room, Bed, LeaveRequest


def _section_filter(actor, qs, gender_field='gender'):
    """اگر مدیر سیستم نباشد و gender داشته باشد، فقط همان بخش."""
    if actor.is_admin_user:
        return qs
    if actor.gender in ('male', 'female'):
        return qs.filter(**{gender_field: actor.gender})
    return qs


@manager_required
def rooms(request):
    """لیست ساختمان‌ها و اتاق‌ها + ظرفیت."""
    section = request.GET.get('section', '')
    buildings = Building.objects.prefetch_related('rooms__beds').all()
    if section in ('male', 'female'):
        buildings = buildings.filter(section=section)
    elif not request.user.is_admin_user and request.user.gender in ('male', 'female'):
        buildings = buildings.filter(section=request.user.gender)

    rows = []
    for b in buildings:
        for room in b.rooms.all():
            beds = list(room.beds.all())
            rows.append({
                'building': b, 'room': room, 'beds': beds,
                'occupied': sum(1 for bed in beds if bed.occupant_id),
                'capacity': room.capacity,
            })
    return render(request, 'panels/manager/rooms.html', {
        'rows': rows, 'section': section,
        'buildings': Building.objects.all(),
    })


@manager_required
def room_assign(request):
    """اختصاص / تخلیه تخت."""
    from accounts.models import User as U
    if request.method == 'POST':
        action = request.POST.get('action')
        bed_id = request.POST.get('bed_id')
        bed = get_object_or_404(Bed, pk=bed_id)

        # محدودیت بخش
        if not request.user.is_admin_user and request.user.gender in ('male', 'female'):
            if bed.room.building.section != request.user.gender:
                messages.error(request, _('اجازه مدیریت این بخش را ندارید.'))
                return redirect('panels:manager_rooms')

        if action == 'release':
            if bed.occupant:
                name = bed.occupant.display_name
                Notification.notify(
                    bed.occupant, _('تخلیه تخت'),
                    _('تخت شما در اتاق %(r)s تخلیه شد.') % {'r': bed.room.number},
                    kind='info',
                )
                bed.occupant = None
                bed.save(update_fields=['occupant'])
                messages.success(request, _('تخت آزاد شد (%(n)s).') % {'n': name})
            return redirect('panels:manager_rooms')

        if action == 'assign':
            student_id = (request.POST.get('student_id') or '').strip()
            student = U.objects.filter(
                role=U.Role.STUDENT, is_active=True
            ).filter(
                models.Q(student_id=student_id) | models.Q(username=student_id)
            ).first() if student_id else None
            # fallback by pk
            if not student and request.POST.get('user_pk'):
                student = U.objects.filter(pk=request.POST.get('user_pk'), role=U.Role.STUDENT).first()

            if not student:
                messages.error(request, _('دانشجو یافت نشد.'))
                return redirect('panels:manager_rooms')

            if student.gender and student.gender != bed.room.building.section:
                messages.error(request, _('بخش خوابگاه دانشجو با ساختمان هم‌خوانی ندارد.'))
                return redirect('panels:manager_rooms')

            # آزاد کردن تخت قبلی دانشجو
            old = Bed.objects.filter(occupant=student).first()
            if old and old.pk != bed.pk:
                old.occupant = None
                old.save(update_fields=['occupant'])

            if bed.occupant and bed.occupant_id != student.pk:
                messages.error(request, _('این تخت اشغال است. ابتدا تخلیه کنید.'))
                return redirect('panels:manager_rooms')

            bed.occupant = student
            bed.save(update_fields=['occupant'])
            Notification.notify(
                student, _('اختصاص اتاق'),
                _('اتاق %(r)s — تخت %(b)s به شما اختصاص یافت.') % {
                    'r': bed.room.number, 'b': bed.number},
                kind='success', link='/dormitory/my-room/',
            )
            messages.success(request, _('دانشجو «%(n)s» به اتاق %(r)s تخت %(b)s اختصاص یافت.') % {
                'n': student.display_name, 'r': bed.room.number, 'b': bed.number})
            return redirect('panels:manager_rooms')

    # GET: فرم اختصاص برای یک تخت
    bed_id = request.GET.get('bed')
    bed = get_object_or_404(Bed.objects.select_related('room__building', 'occupant'), pk=bed_id) if bed_id else None
    unassigned = U.objects.filter(role=U.Role.STUDENT, is_active=True, bed__isnull=True)
    if bed and bed.room.building.section in ('male', 'female'):
        unassigned = unassigned.filter(gender=bed.room.building.section)
    return render(request, 'panels/manager/room_assign.html', {
        'bed': bed, 'unassigned': unassigned[:200],
    })


@manager_required
def reports(request):
    return render(request, 'panels/manager/reports.html')


def _xlsx_response(wb, filename):
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    resp = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


def _style_header(ws, headers):
    fill = PatternFill('solid', fgColor='2563EB')
    font = Font(bold=True, color='FFFFFF')
    for col, h in enumerate(headers, 1):
        cell = ws.cell(1, col, h)
        cell.fill = fill
        cell.font = font


@manager_required
def report_export(request, kind):
    """خروجی اکسل: meals / wallet / access / students / rooms"""
    today = timezone.localdate()
    wb = Workbook()
    ws = wb.active

    if kind == 'meals':
        ws.title = 'Meals'
        headers = ['کد فیش', 'دانشجو', 'شماره', 'وعده', 'روز', 'غذا', 'مبلغ', 'تحویل', 'تاریخ سفارش']
        _style_header(ws, headers)
        qs = MealOrder.objects.select_related('user', 'meal_item', 'menu').order_by('-created_at')[:5000]
        for i, o in enumerate(qs, 2):
            ws.cell(i, 1, o.receipt_code)
            ws.cell(i, 2, o.user.display_name)
            ws.cell(i, 3, o.user.student_id or '')
            ws.cell(i, 4, o.menu.get_meal_period_display())
            ws.cell(i, 5, f'{o.menu.get_weekday_display()} {o.menu.date}')
            ws.cell(i, 6, o.meal_item.name_fa)
            ws.cell(i, 7, int(o.price_at_order))
            ws.cell(i, 8, 'بله' if o.is_served else 'خیر')
            ws.cell(i, 9, o.created_at.strftime('%Y-%m-%d %H:%M'))
        return _xlsx_response(wb, f'meals_{today}.xlsx')

    if kind == 'wallet':
        ws.title = 'Wallet'
        headers = ['کاربر', 'نوع', 'مبلغ', 'توضیحات', 'موجودی بعد', 'تاریخ']
        _style_header(ws, headers)
        qs = Transaction.objects.select_related('wallet__user').order_by('-created_at')[:5000]
        for i, t in enumerate(qs, 2):
            ws.cell(i, 1, t.wallet.user.display_name)
            ws.cell(i, 2, t.get_transaction_type_display())
            ws.cell(i, 3, int(t.amount))
            ws.cell(i, 4, t.description)
            ws.cell(i, 5, int(t.balance_after) if t.balance_after is not None else '')
            ws.cell(i, 6, t.created_at.strftime('%Y-%m-%d %H:%M'))
        return _xlsx_response(wb, f'wallet_{today}.xlsx')

    if kind == 'access':
        ws.title = 'Access'
        headers = ['دانشجو', 'شماره', 'نوع', 'توضیح', 'ثبت‌کننده', 'زمان']
        _style_header(ws, headers)
        qs = AccessLog.objects.select_related('user', 'recorded_by').order_by('-created_at')[:5000]
        for i, a in enumerate(qs, 2):
            ws.cell(i, 1, a.user.display_name)
            ws.cell(i, 2, a.user.student_id or '')
            ws.cell(i, 3, a.get_direction_display())
            ws.cell(i, 4, a.note)
            ws.cell(i, 5, a.recorded_by.display_name if a.recorded_by else '')
            ws.cell(i, 6, a.created_at.strftime('%Y-%m-%d %H:%M'))
        return _xlsx_response(wb, f'access_{today}.xlsx')

    if kind == 'students':
        ws.title = 'Students'
        headers = ['نام', 'نام‌کاربری', 'شماره دانشجویی', 'بخش', 'موبایل', 'ایمیل', 'اتاق', 'تخت', 'فعال']
        _style_header(ws, headers)
        qs = User.objects.filter(role=User.Role.STUDENT).select_related('bed__room__building')
        qs = _section_filter(request.user, qs)
        for i, u in enumerate(qs, 2):
            bed = getattr(u, 'bed', None)
            ws.cell(i, 1, u.display_name)
            ws.cell(i, 2, u.username)
            ws.cell(i, 3, u.student_id or '')
            ws.cell(i, 4, u.get_gender_display() if u.gender else '')
            ws.cell(i, 5, u.phone)
            ws.cell(i, 6, u.email)
            ws.cell(i, 7, bed.room.number if bed else '')
            ws.cell(i, 8, bed.number if bed else '')
            ws.cell(i, 9, 'بله' if u.is_active else 'خیر')
        return _xlsx_response(wb, f'students_{today}.xlsx')

    if kind == 'rooms':
        ws.title = 'Rooms'
        headers = ['ساختمان', 'بخش', 'اتاق', 'طبقه', 'ظرفیت', 'اشغال', 'تخت', 'ساکن', 'شماره دانشجویی']
        _style_header(ws, headers)
        i = 2
        for bed in Bed.objects.select_related('room__building', 'occupant').order_by('room__building', 'room__number', 'number'):
            b = bed.room.building
            if not request.user.is_admin_user and request.user.gender in ('male', 'female'):
                if b.section != request.user.gender:
                    continue
            ws.cell(i, 1, b.name)
            ws.cell(i, 2, b.get_section_display())
            ws.cell(i, 3, bed.room.number)
            ws.cell(i, 4, bed.room.floor)
            ws.cell(i, 5, bed.room.capacity)
            ws.cell(i, 6, bed.room.occupied_count)
            ws.cell(i, 7, bed.number)
            ws.cell(i, 8, bed.occupant.display_name if bed.occupant else '')
            ws.cell(i, 9, bed.occupant.student_id if bed.occupant else '')
            i += 1
        return _xlsx_response(wb, f'rooms_{today}.xlsx')

    messages.error(request, _('نوع گزارش نامعتبر است.'))
    return redirect('panels:manager_reports')


@manager_required
def system_settings(request):
    cfg = SystemSettings.get()
    if request.method == 'POST':
        cfg.site_name = request.POST.get('site_name', cfg.site_name)[:120]
        try:
            cfg.order_cutoff_hour = max(0, min(23, int(request.POST.get('order_cutoff_hour', 10))))
        except ValueError:
            pass
        try:
            cfg.low_balance_threshold = Decimal(request.POST.get('low_balance_threshold') or 50000)
        except Exception:
            pass
        cfg.allow_student_charge = request.POST.get('allow_student_charge') == 'on'
        cfg.mock_payment_enabled = request.POST.get('mock_payment_enabled') == 'on'
        cfg.breakfast_enabled = request.POST.get('breakfast_enabled') == 'on'
        cfg.lunch_enabled = request.POST.get('lunch_enabled') == 'on'
        cfg.dinner_enabled = request.POST.get('dinner_enabled') == 'on'
        cfg.save()
        messages.success(request, _('تنظیمات ذخیره شد.'))
        return redirect('panels:manager_settings')
    return render(request, 'panels/manager/settings.html', {'cfg': cfg})


@manager_required
def leaves_manage(request):
    status = request.GET.get('status', 'pending')
    qs = LeaveRequest.objects.select_related('user').all()
    qs = _section_filter(request.user, qs, 'user__gender')
    if status:
        qs = qs.filter(status=status)
    return render(request, 'panels/manager/leaves.html', {
        'leaves': qs[:200], 'status': status,
    })


@manager_required
@require_POST
def leave_review(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    action = request.POST.get('action')
    note = (request.POST.get('note') or '')[:255]
    if action == 'approve':
        leave.status = LeaveRequest.Status.APPROVED
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.review_note = note
        leave.save()
        Notification.notify(
            leave.user, _('مرخصی تأیید شد'),
            note or _('درخواست مرخصی شما تأیید شد.'),
            kind='leave', link='/dormitory/leave/',
        )
        messages.success(request, _('مرخصی تأیید شد.'))
    elif action == 'reject':
        leave.status = LeaveRequest.Status.REJECTED
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.review_note = note
        leave.save()
        Notification.notify(
            leave.user, _('مرخصی رد شد'),
            note or _('درخواست مرخصی شما رد شد.'),
            kind='leave', link='/dormitory/leave/',
        )
        messages.success(request, _('مرخصی رد شد.'))
    return redirect(request.POST.get('next') or 'panels:manager_leaves')
