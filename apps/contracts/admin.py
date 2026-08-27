from django.contrib import admin

from .models import Contract, ContractTemplate, GeneratedContractFile


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("number", "account", "signed_date", "end_date", "is_active")
    list_filter = ("signed_date",)
    search_fields = ("number", "account__number")
    filter_horizontal = ("responsible_employees",)


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)


@admin.register(GeneratedContractFile)
class GeneratedContractFileAdmin(admin.ModelAdmin):
    list_display = ("contract", "generated_at", "generated_by")
    search_fields = ("contract__number", "contract__account__number")
