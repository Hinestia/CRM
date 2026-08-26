from django.contrib import admin

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("number", "account", "signed_date", "end_date", "is_active")
    list_filter = ("signed_date",)
    search_fields = ("number", "account__number")
    filter_horizontal = ("responsible_employees",)
