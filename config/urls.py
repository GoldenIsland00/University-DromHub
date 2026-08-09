from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from core.views import home_view, dashboard_view, admin_dashboard

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('accounts/', include('accounts.urls')),
    path('dormitory/', include('dormitory.urls')),
    path('tickets/', include('tickets.urls')),
    path('cafeteria/', include('cafeteria.urls')),
    path('wallet/', include('wallet.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
