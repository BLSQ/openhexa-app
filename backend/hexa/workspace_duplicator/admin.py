"""Admin views for the workspace duplicator.

The view is wired into ``WorkspaceAdmin`` (see ``hexa/workspaces/admin.py``)
through ``get_urls()`` so it shows up under the workspace admin section. It is a
dumb wrapper: validate the form, call :func:`run_migration`, render the summary.
Restricted to superusers (source/target credentials are entered transiently and
never persisted).
"""

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse

from hexa.workspace_duplicator import transport
from hexa.workspace_duplicator.forms import MigrateWorkspaceForm
from hexa.workspace_duplicator.results import format_summary
from hexa.workspace_duplicator.service import CredentialError, run_migration
from hexa.workspace_duplicator.transport import GraphQLError


def migrate_workspace_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    summary = None
    if request.method == "POST":
        form = MigrateWorkspaceForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transport.debug_logging(data["debug"]):
                    result = run_migration(
                        source_url=data["source_url"],
                        source_email=data["source_email"],
                        source_password=data["source_password"],
                        source_slug=data["source_slug"],
                        target_url=data["target_url"],
                        target_email=data["target_email"],
                        target_password=data["target_password"],
                        target_organization_id=data["target_organization"] or None,
                        resources=set(data["resources"]),
                    )
                summary = format_summary(result)
                messages.success(request, "Workspace duplication finished.")
            except CredentialError as exc:
                for err in exc.errors:
                    messages.error(request, err)
            except (GraphQLError, NotImplementedError) as exc:
                messages.error(request, f"Duplication failed: {exc}")
    else:
        form = MigrateWorkspaceForm()

    context = {
        **admin.site.each_context(request),
        "title": "Migrate workspace",
        "form": form,
        "summary": summary,
    }
    return TemplateResponse(
        request, "admin/workspace_duplicator/migrate_workspace.html", context
    )
