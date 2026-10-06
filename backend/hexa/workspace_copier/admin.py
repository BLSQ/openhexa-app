"""Admin views for the workspace copier.

The copy view is wired into ``WorkspaceAdmin`` (see ``hexa/workspaces/admin.py``)
through ``get_urls()`` so it shows up under the workspace admin section. It only
validates the form and queues a :class:`WorkspaceCopyRun`; the
``workspace_copy_worker`` executes it, and its progress is shown on the run's
admin page. Restricted to superusers. Source/target credentials are stored
encrypted on the run and erased when it ends.

The template copy view stays synchronous: it is small and remote→remote only.
"""

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html

from hexa.workspace_copier.forms import CopyTemplatesForm, CopyWorkspaceForm
from hexa.workspace_copier.models import WorkspaceCopyRun
from hexa.workspace_copier.progress import BufferReporter
from hexa.workspace_copier.queue import workspace_copy_queue
from hexa.workspace_copier.results import format_templates_summary
from hexa.workspace_copier.service import CredentialError, run_template_copy
from hexa.workspace_copier.transport import GraphQLError


def _queue_copy_run(user, data) -> WorkspaceCopyRun:
    # One transaction: the run and its job exist together or not at all, and
    # the worker is only notified on commit, once the run is readable.
    with transaction.atomic():
        run = WorkspaceCopyRun.objects.create(
            created_by=user,
            source_url=data["source_url"],
            source_token=data["source_token"] or None,
            source_slug=data["source_slug"],
            target_url=data["target_url"],
            target_token=data["target_token"] or None,
            target_organization_id=data["target_organization"],
            target_workspace_name=data["target_workspace_name"],
            target_workspace_slug=data["target_workspace_slug"],
            resources=sorted(data["resources"]),
            all_dataset_versions=data["all_dataset_versions"],
        )
        workspace_copy_queue.enqueue("run_workspace_copy", {"run_id": str(run.id)})
    return run


def copy_workspace_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        form = CopyWorkspaceForm(request.POST)
        if form.is_valid():
            run = _queue_copy_run(request.user, form.cleaned_data)
            messages.success(
                request, "Workspace copy queued. This page refreshes while it runs."
            )
            return redirect("admin:workspace_copier_workspacecopyrun_change", run.id)
    else:
        form = CopyWorkspaceForm()

    context = {
        **admin.site.each_context(request),
        "title": "Copy workspace",
        "form": form,
    }
    return TemplateResponse(
        request, "admin/workspace_copier/copy_workspace.html", context
    )


@admin.register(WorkspaceCopyRun)
class WorkspaceCopyRunAdmin(admin.ModelAdmin):
    list_display = (
        "source_slug",
        "result_workspace_slug",
        "status",
        "created_by",
        "started_at",
        "finished_at",
    )
    list_filter = ("status",)
    search_fields = ("source_slug", "result_workspace_slug", "target_workspace_slug")
    list_select_related = ("created_by",)
    # The encrypted token fields are deliberately never listed here.
    fields = (
        "status",
        "created_by",
        "source_url",
        "source_slug",
        "target_url",
        "target_organization_id",
        "target_workspace_name",
        "target_workspace_slug",
        "result_workspace_slug",
        "resources",
        "all_dataset_versions",
        "created_at",
        "started_at",
        "finished_at",
        "error",
        "logs_display",
        "summary_display",
    )
    readonly_fields = fields
    change_form_template = "admin/workspace_copier/workspacecopyrun/change_form.html"

    def get_queryset(self, request):
        # Runs are kept forever and their logs can be large; the list never
        # shows them. The run page still loads them, with one extra query.
        return super().get_queryset(request).defer("logs", "summary")

    @admin.display(description="Logs")
    def logs_display(self, obj):
        return format_html("<pre>{}</pre>", obj.logs)

    @admin.display(description="Summary")
    def summary_display(self, obj):
        return format_html("<pre>{}</pre>", obj.summary)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser and not (obj and obj.is_active)


def copy_templates_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    summary = None
    log = None
    if request.method == "POST":
        form = CopyTemplatesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            reporter = BufferReporter()
            try:
                result = run_template_copy(
                    source_url=data["source_url"],
                    source_token=data["source_token"],
                    target_url=data["target_url"],
                    target_token=data["target_token"],
                    target_organization_id=data["target_organization"],
                    reporter=reporter,
                )
                summary = format_templates_summary(result)
                messages.success(request, "Template copy finished.")
            except CredentialError as exc:
                for err in exc.errors:
                    messages.error(request, err)
            except GraphQLError as exc:
                messages.error(request, f"Copy failed: {exc}")
            finally:
                log = reporter.render()
    else:
        form = CopyTemplatesForm()

    context = {
        **admin.site.each_context(request),
        "title": "Copy pipeline templates",
        "form": form,
        "summary": summary,
        "log": log,
    }
    return TemplateResponse(
        request, "admin/workspace_copier/copy_templates.html", context
    )
