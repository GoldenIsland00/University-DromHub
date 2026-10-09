from django.urls import path
from . import views_notify

app_name = 'notifications'

urlpatterns = [
    path('', views_notify.notification_list, name='list'),
    path('<int:pk>/read/', views_notify.notification_read, name='read'),
    path('read-all/', views_notify.notification_read_all, name='read_all'),
]
