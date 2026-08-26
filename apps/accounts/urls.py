from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.account_list, name="list"),
    path("new/", views.account_create, name="create"),
    path("<int:pk>/", views.account_detail, name="detail"),
    path("<int:pk>/edit/", views.account_update, name="update"),
    path("<int:pk>/generate-charge/", views.account_generate_charge, name="generate_charge"),
]
