from django.urls import path
from . import views

app_name = 'cafeteria'

urlpatterns = [
    path('meals/', views.meal_order_view, name='meals'),
    path('meals/cancel/<int:pk>/', views.cancel_order_view, name='cancel'),
    path('receipt/<int:pk>/', views.receipt_print, name='receipt'),
]
