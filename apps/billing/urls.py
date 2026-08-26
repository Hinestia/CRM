from django.urls import path

from . import views

app_name = "billing"

urlpatterns = [
    path("", views.charge_list, name="charge_list"),
    path("recalculation/<int:account_pk>/new/", views.recalculation_create, name="recalculation_create"),
    path("payment/<int:account_pk>/new/", views.payment_create, name="payment_create"),
]
