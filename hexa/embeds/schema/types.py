from ariadne import ObjectType

from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_object

web_page_object = ObjectType("WebPage")

bindables = [web_page_object]


@workspace_object.field("homepage")
def resolve_workspace_homepage(workspace: Workspace, info, **kwargs):
    return workspace.homepage


@web_page_object.field("fullWidth")
def resolve_web_page_full_width(web_page, info, **kwargs):
    return web_page.full_width
