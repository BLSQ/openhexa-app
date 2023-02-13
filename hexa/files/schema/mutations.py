from ariadne import MutationType

from hexa.files.api import NotFound, delete_object
from hexa.workspaces.models import Workspace

mutations = MutationType()


@mutations.field("deleteWorkspaceObject")
def resolve_delete_workspace_object(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]
    try:
        workspace = Workspace.objects.filter_for_user(request.principal).get(
            slug=mutation_input["workspaceSlug"]
        )
        if not request.user.has_perm("files.delete_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}

        delete_object(workspace, mutation_input["objectName"])
        return {"success": True, "errors": []}
    except (NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


bindables = [
    mutations,
]
