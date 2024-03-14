from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _


class SoftDeleteFilter(SimpleListFilter):
    title = "is deleted"
    parameter_name = "is_deleted"

    def lookups(self, request, model_admin):
        return (
            ("true", _("Soft deleted")),
            ("false", _("Not Deleted")),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        value = {"true": False, "false": True}[self.value() or "false"]
        return queryset.filter(deleted_at__isnull=value)
