from django.urls import path

from . import views

app_name = "receipts"

urlpatterns = [
    path("", views.receipt_list, name="list"),
    path("generate-period/", views.generate_for_period, name="generate_for_period"),
    path("generate/<int:charge_pk>/", views.generate_for_charge, name="generate_for_charge"),
]
