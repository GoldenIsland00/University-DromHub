from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from accounts.permissions import student_required
from core.models import Notification
from .models import Bed, LeaveRequest


@student_required
def my_room_view(request):
    bed = getattr(request.user, 'bed', None)
    room = bed.room if bed else None
    roommates = []
    if room:
        roommates = Bed.objects.filter(room=room).select_related('occupant').order_by('number')
    return render(request, 'dormitory/my_room.html', {
        'room': room,
        'bed': bed,
        'roommates': roommates,
    })


@student_required
def leave_list(request):
    leaves = LeaveRequest.objects.filter(user=request.user)[:30]
    return render(request, 'dormitory/leave_list.html', {'leaves': leaves})


@student_required
def leave_create(request):
    if request.method == 'POST':
        start = request.POST.get('start_at')
        end = request.POST.get('end_at')
        reason = (request.POST.get('reason') or '').strip()
        destination = (request.POST.get('destination') or '').strip()
        if not start or not end or not reason:
            messages.error(request, _('همه فیلدهای الزامی را پر کنید.'))
        else:
            try:
                from django.utils.dateparse import parse_datetime
                from django.utils import timezone as tz
                s = parse_datetime(start)
                e = parse_datetime(end)
                if s and tz.is_naive(s):
                    s = tz.make_aware(s)
                if e and tz.is_naive(e):
                    e = tz.make_aware(e)
                if not s or not e or e <= s:
                    raise ValueError('invalid range')
                LeaveRequest.objects.create(
                    user=request.user, start_at=s, end_at=e,
                    reason=reason, destination=destination,
                )
                messages.success(request, _('درخواست مرخصی ثبت شد و در انتظار بررسی است.'))
                return redirect('dormitory:leave_list')
            except Exception:
                messages.error(request, _('تاریخ/ساعت نامعتبر است.'))
    return render(request, 'dormitory/leave_form.html')


@student_required
@require_POST
def leave_cancel(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk, user=request.user)
    if leave.status == LeaveRequest.Status.PENDING:
        leave.status = LeaveRequest.Status.CANCELLED
        leave.save(update_fields=['status'])
        messages.success(request, _('درخواست لغو شد.'))
    else:
        messages.error(request, _('فقط درخواست در انتظار قابل لغو است.'))
    return redirect('dormitory:leave_list')
