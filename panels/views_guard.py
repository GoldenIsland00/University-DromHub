"""پنل گارد (حراست): ثبت ورود/خروج دانشجویان و لیست افراد بیرون از خوابگاه."""
from datetime import date

from django.contrib import messages
from django.db.models import OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.permissions import role_required
from dormitory.models import AccessLog

guard_only = role_required('guard')


def _students_for(user):
    """دانشجویان قابل مشاهده؛ اگر برای گارد بخش (برادران/خواهران) تعیین شده فقط همان بخش."""
    latest = (AccessLog.objects.filter(user=OuterRef('pk'))
              .order_by('-created_at', '-pk').values('direction')[:1])
    qs = (User.objects.filter(role=User.Role.STUDENT, is_active=True)
          .select_related('bed__room__building')
          .annotate(last_direction=Subquery(latest)))
    if user.role == User.Role.GUARD and user.gender:
        qs = qs.filter(gender=user.gender)
    return qs


def _logs_for(user):
    qs = AccessLog.objects.select_related('user', 'recorded_by')
    if user.role == User.Role.GUARD and user.gender:
        qs = qs.filter(user__gender=user.gender)
    return qs


@guard_only
def dashboard(request):
    students = _students_for(request.user)
    today = timezone.localdate()
    logs_today = _logs_for(request.user).filter(created_at__date=today)
    outside = students.filter(last_direction=AccessLog.Direction.OUT)
    return render(request, 'panels/guard/dashboard.html', {
        'total': students.count(),
        'outside_count': outside.count(),
        'in_today': logs_today.filter(direction='in').count(),
        'out_today': logs_today.filter(direction='out').count(),
        'recent': logs_today[:10],
        'outside': outside[:8],
    })


@guard_only
def gate(request):
    """جستجوی دانشجو و ثبت ورود/خروج."""
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        results = _students_for(request.user).filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(student_id__icontains=q) | Q(username__icontains=q) | Q(phone__icontains=q)
        )[:20]
    return render(request, 'panels/guard/gate.html', {'q': q, 'results': results})


@guard_only
@require_POST
def record(request):
    student = get_object_or_404(_students_for(request.user), pk=request.POST.get('user_id'))
    direction = request.POST.get('direction')
    if direction not in AccessLog.Direction.values:
        messages.error(request, _('نوع تردد نامعتبر است.'))
        return redirect('panels:guard_gate')
    AccessLog.objects.create(
        user=student, direction=direction,
        note=request.POST.get('note', '')[:255], recorded_by=request.user,
    )
    label = AccessLog.Direction(direction).label
    messages.success(request, _('%(label)s «%(name)s» ثبت شد.') % {'label': label, 'name': student.display_name})
    return redirect(request.POST.get('next') or 'panels:guard_gate')


@guard_only
def outside(request):
    return render(request, 'panels/guard/outside.html', {
        'students': _students_for(request.user).filter(last_direction=AccessLog.Direction.OUT),
    })


@guard_only
def logs(request):
    qs = _logs_for(request.user)
    try:
        day = date.fromisoformat(request.GET.get('date', ''))
    except ValueError:
        day = timezone.localdate()
    qs = qs.filter(created_at__date=day)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
                       | Q(user__student_id__icontains=q))
    return render(request, 'panels/guard/logs.html', {'logs': qs, 'day': day, 'q': q})
