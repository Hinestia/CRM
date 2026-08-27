from django.contrib import admin

from .models import Meter, MeterReading


class MeterReadingInline(admin.TabularInline):
    model = MeterReading
    extra = 0


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ("account", "service", "serial_number", "is_active", "next_verification_date")
    list_filter = ("service", "is_active")
    search_fields = ("account__number", "serial_number")
    inlines = [MeterReadingInline]


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ("meter", "period", "value", "consumption", "submitted_by")
    list_filter = ("period",)
    search_fields = ("meter__account__number", "meter__serial_number")
