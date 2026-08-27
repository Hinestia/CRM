from django.contrib import admin

from .models import Tenant, TenantAccountAssignment


class TenantAccountAssignmentInline(admin.TabularInline):
    model = TenantAccountAssignment
    extra = 0
    fk_name = "tenant"


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email")
    search_fields = ("last_name", "first_name", "middle_name", "phone", "email", "passport_number")
    inlines = [TenantAccountAssignmentInline]


@admin.register(TenantAccountAssignment)
class TenantAccountAssignmentAdmin(admin.ModelAdmin):
    list_display = ("account", "tenant", "is_primary", "start_date", "end_date")
    list_filter = ("is_primary",)
    search_fields = ("account__number", "tenant__last_name")
