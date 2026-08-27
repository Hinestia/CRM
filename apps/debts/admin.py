from django.contrib import admin

from .models import PenaltyAccrual, PenaltySettings


@admin.register(PenaltySettings)
class PenaltySettingsAdmin(admin.ModelAdmin):
    list_display = ("name", "grace_period_days", "rate_per_day", "is_active")


@admin.register(PenaltyAccrual)
class PenaltyAccrualAdmin(admin.ModelAdmin):
    list_display = ("account", "calculation_date", "days_overdue", "debt_amount", "amount")
    list_filter = ("calculation_date",)
    search_fields = ("account__number",)
