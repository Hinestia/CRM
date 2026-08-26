from django.contrib import admin

from .models import House, Street, Unit


@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("street", "number", "building")
    list_filter = ("street",)
    search_fields = ("street__name", "number")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("house", "number", "type", "area_total", "area_living", "area_balcony")
    list_filter = ("type",)
    search_fields = ("house__street__name", "house__number", "number")
