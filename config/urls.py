"""
URL configuration for the ЖКУ billing CRM project.

На первом этапе интерфейсом сотрудника служит Django admin (см. DESIGN.md,
раздел "Поэтапный план") — все модели зарегистрированы в apps/*/admin.py.
Собственные экраны (списки лицевых счетов, реестр должников и т.д.)
подключаются сюда по мере разработки в apps/*/urls.py.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="admin:index", permanent=False)),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]
