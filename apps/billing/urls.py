from django.urls import path

from . import views

app_name = "billing"

urlpatterns = [
    path("", views.charge_list, name="charge_list"),
    path("<int:pk>/finalize/", views.charge_finalize, name="charge_finalize"),
    path("payment/<int:account_pk>/new/", views.payment_create, name="payment_create"),
]
