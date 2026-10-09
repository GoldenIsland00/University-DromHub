"""پنل تاسیسات: رسیدگی به تیکت‌های خرابی و تعمیرات."""
from django.db.models import Count, Q
from django.shortcuts import render

from accounts.permissions import role_required
from tickets.models import Ticket

maintenance_only = role_required('maintenance')


@maintenance_only
def dashboard(request):
    qs = Ticket.objects.all()
    by_status = {s: qs.filter(status=s).count() for s, _l in Ticket.Status.choices}
    by_category = (qs.exclude(status__in=['resolved', 'closed'])
                   .values('category').annotate(n=Count('id')))
    cat_labels = dict(Ticket.Category.choices)
    return render(request, 'panels/maintenance/dashboard.html', {
        'by_status': by_status,
        'urgent': qs.filter(priority='urgent').exclude(status__in=['resolved', 'closed'])
                    .select_related('user', 'room')[:8],
        'mine': qs.filter(assigned_to=request.user).exclude(status__in=['resolved', 'closed'])
                  .select_related('user', 'room')[:8],
        'by_category': [(cat_labels.get(c['category'], c['category']), c['n']) for c in by_category],
    })


@maintenance_only
def tickets(request):
    qs = Ticket.objects.select_related('user', 'room__building', 'assigned_to')
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    scope = request.GET.get('scope', '')
    if status:
        qs = qs.filter(status=status)
    else:
        qs = qs.exclude(status='closed') if scope != 'all' else qs
    if category:
        qs = qs.filter(category=category)
    if scope == 'mine':
        qs = qs.filter(assigned_to=request.user)
    elif scope == 'unassigned':
        qs = qs.filter(assigned_to__isnull=True)
    return render(request, 'panels/maintenance/tickets.html', {
        'tickets': qs, 'status': status, 'category': category, 'scope': scope,
        'statuses': Ticket.Status.choices, 'categories': Ticket.Category.choices,
    })
