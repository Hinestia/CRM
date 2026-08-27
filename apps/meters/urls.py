from django.urls import path

from . import views

app_name = "meters"

urlpatterns = [
    path("<int:account_pk>/new/", views.meter_create, name="meter_create"),
    path("reading/<int:meter_pk>/new/", views.reading_create, name="reading_create"),
]
