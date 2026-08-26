from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("", views.service_list, name="list"),
    path("new/", views.service_create, name="create"),
    path("<int:pk>/", views.service_detail, name="detail"),
    path("<int:service_pk>/tariffs/new/", views.tariff_create, name="tariff_create"),
]
