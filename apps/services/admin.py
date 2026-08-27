from django.contrib import admin

from .models import Service, Tariff


class TariffInline(admin.TabularInline):
    model = Tariff
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "calculation_method", "unit_of_measure", "is_active")
    list_filter = ("calculation_method", "is_active")
    search_fields = ("name", "code")
    inlines = [TariffInline]


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("service", "rate", "valid_from", "valid_to", "created_by")
    list_filter = ("service",)
    autocomplete_fields = ["service"]
