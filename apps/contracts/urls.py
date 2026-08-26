from django.urls import path

from . import views

app_name = "contracts"

urlpatterns = [
    path("", views.contract_list, name="list"),
    path("new/", views.contract_create, name="create"),
    path("<int:pk>/edit/", views.contract_update, name="update"),
]
