from django.contrib import admin

from hexa.core.filters import SoftDeleteFilter


@admin.display
def country_list(obj):
    """List display helper for country fields"""
    country_count = len(obj.countries)
    max_count = 3
    country_list_string = ", ".join(
        country.name for country in obj.countries[:max_count]
    )
    if country_count > max_count:
        country_list_string += f" (+{country_count - max_count})"

    return country_list_string


class SoftDeletedModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        super().get_queryset(request)
        qs = self.model.deleted_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class GlobalObjectsModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        super().get_queryset(request)
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request) or []
        if not isinstance(list_filter, list):
            list_filter = list(list_filter)
        list_filter.append(SoftDeleteFilter)
        return list_filter
