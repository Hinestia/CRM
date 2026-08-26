from django.urls import path

from . import views

app_name = "tenants"

urlpatterns = [
    path("", views.tenant_list, name="list"),
    path("new/", views.tenant_create, name="create"),
    path("<int:pk>/", views.tenant_detail, name="detail"),
    path("<int:pk>/edit/", views.tenant_update, name="update"),
    path("assign/<int:account_pk>/", views.assignment_create, name="assign"),
    path("assignment/<int:pk>/end/", views.assignment_end, name="assignment_end"),
]
