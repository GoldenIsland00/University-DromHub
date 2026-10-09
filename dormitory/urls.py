from django.urls import path
from . import views

app_name = 'dormitory'

urlpatterns = [
    path('my-room/', views.my_room_view, name='my_room'),
    path('leave/', views.leave_list, name='leave_list'),
    path('leave/new/', views.leave_create, name='leave_create'),
    path('leave/<int:pk>/cancel/', views.leave_cancel, name='leave_cancel'),
]
