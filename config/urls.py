"""
URL configuration for the ЖКУ billing CRM project.

Основной рабочий интерфейс сотрудника — собственные экраны в apps/*/urls.py.
Django admin (`/admin/`) остаётся доступен как резервный доступ к редким
административным справочникам (типы улиц, настройки пени и т.п.).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from .views import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("addresses/", include("apps.addresses.urls")),
    path("tenants/", include("apps.tenants.urls")),
    path("services/", include("apps.services.urls")),
    path("contracts/", include("apps.contracts.urls")),
    path("billing/", include("apps.billing.urls")),
    path("meters/", include("apps.meters.urls")),
    path("receipts/", include("apps.receipts.urls")),
    path("debts/", include("apps.debts.urls")),
]

if settings.DEBUG:
    # В проде /media/ отдаёт nginx (см. docker/nginx.conf) — этот блок нужен
    # только для локального runserver без Docker.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
