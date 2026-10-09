def user_context(request):
    """Add common user-related data to all templates."""
    ctx = {
        'open_tickets_count': 0,
        'staff_open_tickets_count': 0,
        'user_balance': 0,
        'user_room': None,
        'user_bed': None,
        'unread_notifications': 0,
    }
    user = request.user
    if user.is_authenticated:
        ctx['open_tickets_count'] = user.tickets.filter(status__in=['open', 'in_progress']).count()
        if user.is_maintenance or user.is_manager_level:
            from tickets.models import Ticket
            ctx['staff_open_tickets_count'] = Ticket.objects.filter(
                status__in=['open', 'in_progress']).count()
        if hasattr(user, 'wallet'):
            ctx['user_balance'] = user.wallet.balance
        if hasattr(user, 'bed') and user.bed:
            ctx['user_bed'] = user.bed
            ctx['user_room'] = user.bed.room
        ctx['unread_notifications'] = user.notifications.filter(is_read=False).count()
    return ctx
