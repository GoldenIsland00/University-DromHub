from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.wallet_view, name='wallet'),
    path('pay/<str:authority>/', views.pay_mock, name='pay_mock'),
    path('pay/<str:authority>/confirm/', views.pay_mock_confirm, name='pay_mock_confirm'),
]
