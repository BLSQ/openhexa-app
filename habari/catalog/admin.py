from django.contrib import admin
from .models import Area, Datasource, Organization, Theme


def country_list(obj):
    return ",".join(country.alpha3 for country in obj.countries)


country_list.short_description = "Countries"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("display_name", "organization_type", country_list)


@admin.register(Datasource)
class DatasourceAdmin(admin.ModelAdmin):
    list_display = ("display_name", "datasource_type", "owner", "public", country_list)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("display_name",)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("display_name",)
