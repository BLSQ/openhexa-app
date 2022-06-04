from django.contrib import admin

from .models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "alpha3", "region")
    search_fields = ("name", "code", "alpha3")
    list_filter = ("region",)
