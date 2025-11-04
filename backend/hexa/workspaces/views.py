from urllib.parse import quote

from django.conf import settings
from django.core.signing import BadSignature, Signer
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.databases.api import get_db_server_credentials
from hexa.files import storage
from hexa.pipelines.models import PipelineRun
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

# ease patching


@require_POST
@csrf_exempt
def credentials(request: HttpRequest, workspace_slug: str = None) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example).

    workspace_slug is optional, if not provided, the workspace will be extracted from the request body.
    """
    workspace_slug = (
        request.POST.get("workspace", None)
        if workspace_slug is None
        else workspace_slug
    )

    if not workspace_slug:
        return JsonResponse({"error": "No workspace given"}, status=400)

    try:
        workspace = Workspace.objects.get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        return JsonResponse({}, status=404)

    pipeline_run = None  # Track if we're in a pipeline run

    if request.headers.get("Authorization"):
        auth_type, token = request.headers.get("Authorization", " ").split(" ")
        if auth_type.lower() != "bearer":
            return JsonResponse(
                {"error": "Authorization header should start with 'bearer'"}, status=401
            )
        try:
            access_token = Signer().unsign_object(token)
            # Validate that the token is valid and matches a run of the given workspace
            run = PipelineRun.objects.get(
                pipeline__workspace=workspace, access_token=access_token
            )
            pipeline_run = run  # Store for later use
            sdk_auth_token = access_token
            server_hash = str(run.id)
        except BadSignature:
            return JsonResponse({"error": "Token signature is invalid"}, status=401)
        except PipelineRun.DoesNotExist:
            return JsonResponse(
                {},
                status=404,
            )
    elif request.user.is_authenticated:
        if not request.user.has_perm("workspaces.launch_notebooks", workspace):
            return JsonResponse(
                {"error": "User does not have permission to launch notebooks"},
                status=401,
            )

        try:
            membership = WorkspaceMembership.objects.get(
                workspace=workspace, user=request.user
            )
        except WorkspaceMembership.DoesNotExist:
            assert (
                request.user.is_superuser
                or request.user.is_organization_admin_or_owner(workspace.organization)
            )
            # Auto-create membership on the fly for admins/owners/superusers
            membership = WorkspaceMembership.objects.create(
                workspace=workspace,
                user=request.user,
                role=WorkspaceMembershipRole.ADMIN,
            )
        server_hash = membership.notebooks_server_hash
        sdk_auth_token = membership.access_token
    else:
        return JsonResponse(
            {},
            status=401,
        )

    # Populate the environment variables with the connections of the workspace
    env = {
        "WORKSPACE_BUCKET_NAME": workspace.bucket_name,
    }

    # Database credentials
    db_credentials = get_db_server_credentials()

    # Build database URL with application_name for pipeline runs
    db_url = workspace.db_url
    if pipeline_run:
        # Add application_name parameter for better connection tracking
        application_name = f"{pipeline_run.pipeline.name} (run {pipeline_run.id})"
        db_url = f"{db_url}?application_name={quote(application_name)}"

    env.update(
        {
            "WORKSPACE_DATABASE_DB_NAME": workspace.db_name,
            "WORKSPACE_DATABASE_HOST": workspace.db_host,
            "WORKSPACE_DATABASE_PORT": db_credentials["port"],
            "WORKSPACE_DATABASE_USERNAME": workspace.db_name,
            "WORKSPACE_DATABASE_PASSWORD": workspace.db_password,
            "WORKSPACE_DATABASE_URL": db_url,
        }
    )

    # Bucket credentials
    env.update(
        {
            "WORKSPACE_STORAGE_ENGINE": storage.storage_type,
            **storage.get_bucket_mount_config(workspace.bucket_name),
        }
    )

    # Custom Docker image for the workspace if appropriate
    image = (
        workspace.docker_image
        if workspace.docker_image != ""
        else settings.DEFAULT_WORKSPACE_IMAGE
    )

    if sdk_auth_token is not None:
        # SDK Credentials
        env.update({"HEXA_TOKEN": Signer().sign_object(sdk_auth_token)})

    return JsonResponse(
        {"env": env, "notebooks_server_hash": server_hash, "image": image},
        status=200,
    )
