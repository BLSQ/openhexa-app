"""Admin views for the workspace copier.

The view is wired into ``WorkspaceAdmin`` (see ``hexa/workspaces/admin.py``)
through ``get_urls()`` so it shows up under the workspace admin section. It is a
dumb wrapper: validate the form, call :func:`run_copy`, render the summary.
Restricted to superusers (source/target credentials are entered transiently and
never persisted).
"""

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse

from hexa.workspace_copier.forms import CopyTemplatesForm, CopyWorkspaceForm
from hexa.workspace_copier.progress import BufferReporter
from hexa.workspace_copier.results import format_summary, format_templates_summary
from hexa.workspace_copier.service import (
    CredentialError,
    run_copy,
    run_template_copy,
)
from hexa.workspace_copier.transport import GraphQLError


def copy_workspace_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    summary = None
    log = None
    if request.method == "POST":
        form = CopyWorkspaceForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            reporter = BufferReporter()
            try:
                result = run_copy(
                    source_url=data["source_url"],
                    source_token=data["source_token"],
                    source_slug=data["source_slug"],
                    target_url=data["target_url"],
                    target_token=data["target_token"],
                    target_organization_id=data["target_organization"],
                    target_workspace_name=data["target_workspace_name"] or None,
                    resources=set(data["resources"]),
                    reporter=reporter,
                )
                summary = format_summary(result)
                log = reporter.render()
                messages.success(request, "Workspace copy finished.")
            except CredentialError as exc:
                for err in exc.errors:
                    messages.error(request, err)
            except (GraphQLError, NotImplementedError) as exc:
                messages.error(request, f"Copy failed: {exc}")
    else:
        form = CopyWorkspaceForm()

    context = {
        **admin.site.each_context(request),
        "title": "Copy workspace",
        "form": form,
        "summary": summary,
        "log": log,
    }
    return TemplateResponse(
        request, "admin/workspace_copier/copy_workspace.html", context
    )


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
                log = reporter.render()
                messages.success(request, "Template copy finished.")
            except CredentialError as exc:
                for err in exc.errors:
                    messages.error(request, err)
            except GraphQLError as exc:
                messages.error(request, f"Copy failed: {exc}")
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
