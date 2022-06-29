from django.contrib import admin

from .models import Country, WHOBoundary


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "alpha3", "region")
    search_fields = ("name", "code", "alpha3")
    list_filter = ("region",)


@admin.register(WHOBoundary)
class WHOBoundaryAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
