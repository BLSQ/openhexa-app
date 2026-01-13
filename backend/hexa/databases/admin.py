from django.contrib import admin

from hexa.databases.models import DatasetRecipe


@admin.register(DatasetRecipe)
class DatasetRecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "is_active", "created_at", "sql_template")
    list_filter = ("workspace",)
    search_fields = ("id", "name", "workspace__name")
