def user_context(request):
    """Add common user-related data to all templates."""
    ctx = {
        'open_tickets_count': 0,
        'user_balance': 0,
        'user_room': None,
        'user_bed': None,
    }
    if request.user.is_authenticated:
        ctx['open_tickets_count'] = request.user.tickets.filter(
            status__in=['open', 'in_progress']
        ).count()
        if hasattr(request.user, 'wallet'):
            ctx['user_balance'] = request.user.wallet.balance
        if hasattr(request.user, 'bed') and request.user.bed:
            ctx['user_bed'] = request.user.bed
            ctx['user_room'] = request.user.bed.room
    return ctx
