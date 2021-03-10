from django.contrib import admin

from habari.catalog.models import Datasource
from habari.common.admin import country_list


@admin.register(Datasource)
class DatasourceAdmin(admin.ModelAdmin):
    list_display = ("display_name", "datasource_type", "owner", "public", country_list)
