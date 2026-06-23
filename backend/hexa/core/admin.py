from typing import Any, Sequence

from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest

from hexa.core.filters import SoftDeleteFilter
from hexa.core.models import FailedEmail
from hexa.core.utils import resend_failed_email


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

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        for obj in queryset:
            obj.hard_delete()

    def get_list_filter(self, request: HttpRequest):
        list_filter = super().get_list_filter(request) or []
        if not isinstance(list_filter, list):
            list_filter = list(list_filter)
        list_filter.append(SoftDeleteFilter)
        return list_filter

    def get_list_display(self, request: HttpRequest) -> Sequence[str]:
        list_display = super().get_list_display(request)
        if "is_deleted" in request.GET:
            list_display = list(list_display) + ["deleted_at"]
        return list_display


@admin.action(description="Resend selected emails")
def resend_failed_emails(modeladmin, request, queryset):
    succeeded, failed = 0, 0
    for failed_email in queryset:
        try:
            resend_failed_email(failed_email)
            succeeded += 1
        except Exception as e:
            failed += 1
            modeladmin.message_user(
                request,
                f"Failed to resend '{failed_email.subject}': {e}",
                level=messages.ERROR,
            )
    if succeeded:
        modeladmin.message_user(
            request, f"Resent {succeeded} email(s).", level=messages.SUCCESS
        )


@admin.register(FailedEmail)
class FailedEmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "recipients_display", "created_at")
    list_filter = ("created_at",)
    search_fields = ("subject", "recipients", "error_message")
    readonly_fields = (
        "subject",
        "recipients",
        "text_body",
        "html_body",
        "attachments",
        "error_message",
        "created_at",
    )
    actions = [resend_failed_emails]

    @admin.display(description="Recipients")
    def recipients_display(self, obj):
        return ", ".join(obj.recipients)
