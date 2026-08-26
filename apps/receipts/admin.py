from django.contrib import admin

from .models import Receipt


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("charge", "generated_at", "generated_by", "emailed_at")
    search_fields = ("charge__account__number",)
