from django.urls import path

from . import views

app_name = "addresses"

urlpatterns = [
    path("", views.house_list, name="house_list"),
    path("new/", views.house_create, name="house_create"),
    path("streets/new/", views.street_create, name="street_create"),
    path("<int:pk>/", views.house_detail, name="house_detail"),
    path("<int:house_pk>/units/new/", views.unit_create, name="unit_create"),
    path("units/<int:pk>/edit/", views.unit_update, name="unit_update"),
]
