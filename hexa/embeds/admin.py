from django.contrib import admin

from .models import WebPage


# Register your models here.
@admin.register(WebPage)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "workspace")
    search_fields = ("id", "title", "url")
    list_filter = ("workspace",)
