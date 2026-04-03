import json

from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_static_webapps(
    user, workspace_slug: str, page: int = 1, per_page: int = 10
) -> dict:
    """List static web apps in a workspace. The returned URL can be used to access each webapp in a browser."""
    return execute_graphql(
        user,
        "ListStaticWebapps",
        {"workspaceSlug": workspace_slug, "page": page, "perPage": per_page},
    )


@tool
def create_static_webapp(
    user,
    workspace_slug: str,
    name: str,
    files_json: str,
    description: str = "",
) -> dict:
    """Create a static web app in a workspace. Provide files_json as a JSON array of {path, content} objects, e.g. '[{"path": "index.html", "content": "<html>...</html>"}, {"path": "style.css", "content": "body { ... }"}]'. An index.html file is required at minimum. Returns the webapp URL to access it in a browser."""
    try:
        files = json.loads(files_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in files_json"}

    if not isinstance(files, list) or not files:
        return {
            "error": "files_json must be a non-empty JSON array of {path, content} objects"
        }

    create_input: dict = {
        "workspaceSlug": workspace_slug,
        "name": name,
        "source": {"static": files},
    }
    if description:
        create_input["description"] = description

    data = execute_graphql(
        user,
        "CreateStaticWebapp",
        {"input": create_input},
    )
    if "errors" in data:
        return data
    return data["createWebapp"]


@tool
def update_static_webapp(
    user,
    webapp_id: str,
    files_json: str = "",
    name: str = "",
    description: str = "",
) -> dict:
    """Update an existing static web app. Provide the webapp UUID (from list_static_webapps) and any fields to change. To update files, provide files_json as a JSON array of {path, content} objects — this replaces all files. Only provided non-empty fields are updated."""
    update_input: dict = {"id": webapp_id}
    if name:
        update_input["name"] = name
    if description:
        update_input["description"] = description
    if files_json:
        try:
            files = json.loads(files_json)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in files_json"}
        if not isinstance(files, list) or not files:
            return {
                "error": "files_json must be a non-empty JSON array of {path, content} objects"
            }
        update_input["files"] = files

    data = execute_graphql(
        user,
        "UpdateStaticWebapp",
        {"input": update_input},
    )
    if "errors" in data:
        return data
    return data["updateWebapp"]
