from django.contrib import admin

from .models import PersonalAccount


@admin.register(PersonalAccount)
class PersonalAccountAdmin(admin.ModelAdmin):
    list_display = (
        "number", "unit", "status", "registered_count", "current_responsible", "opened_at",
    )
    list_filter = ("status",)
    search_fields = ("number", "unit__house__street__name", "unit__number")
