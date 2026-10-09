from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    qs = request.user.notifications.all()[:50]
    return render(request, 'notifications/list.html', {'notifications': qs})


@login_required
@require_POST
def notification_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save(update_fields=['is_read'])
    if n.link:
        return redirect(n.link)
    return redirect('notifications:list')


@login_required
@require_POST
def notification_read_all(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:list')
