from django.urls import path
from . import views

app_name = 'dormitory'

urlpatterns = [
    path('my-room/', views.my_room_view, name='my_room'),
]
