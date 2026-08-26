from django.urls import path

from . import views

app_name = "debts"

urlpatterns = [
    path("", views.debtor_list, name="list"),
    path("accrue/", views.accrue_now, name="accrue_now"),
    path("settings/", views.penalty_settings_edit, name="settings"),
]
