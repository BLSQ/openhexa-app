from django.contrib import admin

from hexa.webapps.models import Webapp


@admin.register(Webapp)
class WebappAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace")
    list_filter = ("workspace",)
    search_fields = ("id", "name")
