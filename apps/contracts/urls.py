from django.urls import path

from . import views

app_name = "contracts"

urlpatterns = [
    path("", views.contract_list, name="list"),
    path("new/", views.contract_create, name="create"),
    path("account/<int:account_pk>/new/", views.contract_create_for_account, name="create_for_account"),
    path("<int:pk>/edit/", views.contract_update, name="update"),
    path("<int:pk>/generate-pdf/", views.contract_generate_pdf, name="generate_pdf"),
]
