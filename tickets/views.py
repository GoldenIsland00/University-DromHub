from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from .models import Ticket, TicketReply
from .forms import TicketCreateForm, TicketReplyForm


def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_admin_user or user.role == 'staff' or user.is_staff)


@login_required
def ticket_list(request):
    tickets = request.user.tickets.all()
    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            if hasattr(request.user, 'bed') and request.user.bed:
                ticket.room = request.user.bed.room
            ticket.save()
            # First message as initial description is already in ticket
            messages.success(request, _('تیکت با موفقیت ثبت شد.'))
            return redirect('tickets:detail', pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/ticket_create.html', {'form': form})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    # Students can only see their own tickets; staff/admin can see all
    if not (ticket.user == request.user or is_admin_or_staff(request.user)):
        messages.error(request, _('دسترسی غیرمجاز.'))
        return redirect('tickets:list')

    if request.method == 'POST':
        form = TicketReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ticket = ticket
            reply.user = request.user
            reply.is_staff_reply = is_admin_or_staff(request.user)
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
    })


@login_required
@user_passes_test(is_admin_or_staff)
def admin_ticket_list(request):
    tickets = Ticket.objects.select_related('user', 'room').all()
    status = request.GET.get('status')
    section = request.GET.get('section')
    if status:
        tickets = tickets.filter(status=status)
    if section:
        tickets = tickets.filter(user__gender=section)
    return render(request, 'tickets/admin_ticket_list.html', {'tickets': tickets})
