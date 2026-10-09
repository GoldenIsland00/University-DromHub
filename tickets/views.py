from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from accounts.permissions import role_required, student_required
from .forms import TicketCreateForm, TicketReplyForm
from .models import Ticket, TicketReply


def is_ticket_staff(user):
    """کسانی که می‌توانند تیکت دیگران را ببینند و پاسخ دهند: تاسیسات، مدیریت، مدیر سیستم."""
    return user.is_authenticated and (user.is_maintenance or user.is_manager_level)


@student_required
def ticket_list(request):
    tickets = request.user.tickets.all()
    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@student_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            if hasattr(request.user, 'bed') and request.user.bed:
                ticket.room = request.user.bed.room
            ticket.save()
            messages.success(request, _('تیکت با موفقیت ثبت شد.'))
            return redirect('tickets:detail', pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/ticket_create.html', {'form': form})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    staff = is_ticket_staff(request.user)
    # دانشجو فقط تیکت‌های خودش؛ تاسیسات/مدیریت همه تیکت‌ها
    if not (ticket.user == request.user or staff):
        messages.error(request, _('دسترسی غیرمجاز.'))
        return redirect(request.user.panel_url_name)

    if request.method == 'POST':
        action = request.POST.get('action', 'reply')

        if action in ('status', 'assign_me', 'unassign') and staff:
            if action == 'status':
                new_status = request.POST.get('status')
                if new_status in Ticket.Status.values:
                    ticket.status = new_status
                    messages.success(request, _('وضعیت تیکت تغییر کرد.'))
            elif action == 'assign_me':
                ticket.assigned_to = request.user
                if ticket.status == Ticket.Status.OPEN:
                    ticket.status = Ticket.Status.IN_PROGRESS
                messages.success(request, _('تیکت به شما ارجاع داده شد.'))
            else:
                ticket.assigned_to = None
                messages.info(request, _('ارجاع تیکت برداشته شد.'))
            ticket.save()
            return redirect('tickets:detail', pk=ticket.pk)

        form = TicketReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ticket = ticket
            reply.user = request.user
            reply.is_staff_reply = staff
            reply.save()
            if reply.is_staff_reply and ticket.status == Ticket.Status.OPEN:
                ticket.status = Ticket.Status.IN_PROGRESS
                ticket.save(update_fields=['status'])
            messages.success(request, _('پاسخ ثبت شد.'))
            return redirect('tickets:detail', pk=ticket.pk)
    else:
        form = TicketReplyForm()

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'form': form,
        'replies': ticket.replies.select_related('user'),
        'is_staff_view': staff,
        'statuses': Ticket.Status.choices,
    })


@role_required('maintenance')
def admin_ticket_list(request):
    tickets = Ticket.objects.select_related('user', 'room', 'assigned_to').all()
    status = request.GET.get('status')
    section = request.GET.get('section')
    if status:
        tickets = tickets.filter(status=status)
    if section:
        tickets = tickets.filter(user__gender=section)
    return render(request, 'tickets/admin_ticket_list.html', {'tickets': tickets})
