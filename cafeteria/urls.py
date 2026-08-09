from django.urls import path
from . import views

app_name = 'cafeteria'

urlpatterns = [
    path('meals/', views.meal_order_view, name='meals'),
]
