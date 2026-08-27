from django.contrib import admin

from .models import Charge, ChargeLine, Payment


class ChargeLineInline(admin.TabularInline):
    model = ChargeLine
    extra = 0


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = (
        "account", "period", "status", "opening_balance", "accrued_total",
        "paid_total", "closing_balance",
    )
    list_filter = ("status", "period")
    search_fields = ("account__number",)
    inlines = [ChargeLineInline]
    readonly_fields = ("accrued_total", "closing_balance")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("account", "date", "amount", "reference", "charge")
    list_filter = ("date",)
    search_fields = ("account__number", "reference")
