from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_index, name="index"),
    path("accounts-register/", views.accounts_register_pdf, name="accounts_register"),
    path("accruals/", views.accruals_statement_pdf, name="accruals_statement"),
    path("debtors/", views.debtors_register_pdf, name="debtors_register"),
    path("reconciliation/", views.reconciliation_act_pdf, name="reconciliation_act"),
]
