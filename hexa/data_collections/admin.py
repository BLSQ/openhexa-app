from django.contrib import admin

from hexa.data_collections.models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "created_at")
    list_filter = ("name",)
    search_fields = ("name",)
