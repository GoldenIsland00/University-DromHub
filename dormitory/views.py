from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext as _
from .models import Room, Bed


@login_required
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
