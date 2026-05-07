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


def _split_scopes(value: str) -> list[str]:
    return [s.strip().upper() for s in value.split(",") if s.strip()]


@tool
def create_static_webapp(
    user,
    workspace_slug: str,
    name: str,
    files_json: str,
    description: str = "",
    allowed_operations: str = "",
) -> dict:
    """Create a static web app in a workspace.

    Provide files_json as a JSON array of {path, content} objects, e.g. '[{"path": "index.html", "content": "<html>...</html>"}, {"path": "style.css", "content": "body { ... }"}]'. An index.html file is required at minimum. Returns the webapp URL to access it in a browser.

    Private static webapps can also call OpenHEXA's GraphQL API directly from their JS via a same-origin
    proxy at POST /graphql/ (auth handled by the webapp session, no token needed). Pass
    allowed_operations as a comma-separated list of scopes to grant API access at creation time —
    valid values: PIPELINES_READ, PIPELINES_RUN, FILES_READ, FILES_WRITE, DATASETS_READ, DATASETS_WRITE,
    USER_READ. Leave empty to create with no API access (you can grant it later via
    update_static_webapp). When generating the webapp's HTML/JS, you can include
    fetch('/graphql/', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({query, variables})})
    calls. For the full reference (auth model, all top-level fields per scope, sample queries and
    mutations), call get_help_or_doc(topic="static-webapps").
    """
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
    if allowed_operations:
        create_input["allowedOperations"] = _split_scopes(allowed_operations)

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
    allowed_operations: str = "",
) -> dict:
    """Update an existing static web app.

    Provide the webapp UUID (from list_static_webapps) and any fields to change. Only provided
    non-empty fields are updated.

    Parameters
    ----------
    - files_json: JSON array of {path, content} objects to replace all files.
    - name: new human-readable name.
    - description: new description.
    - allowed_operations: comma-separated list of API scopes the webapp's JS may call via the
      same-origin /graphql/ proxy. Pass an empty string to leave the current scopes untouched, or
      "NONE" to revoke all access. Valid scopes: PIPELINES_READ, PIPELINES_RUN, FILES_READ,
      FILES_WRITE, DATASETS_READ, DATASETS_WRITE, USER_READ. Example: "PIPELINES_READ,FILES_READ".
      For what each scope grants and example queries the webapp's JS can run, call
      get_help_or_doc(topic="static-webapps").
    """
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
    if allowed_operations:
        if allowed_operations.strip().upper() == "NONE":
            update_input["allowedOperations"] = []
        else:
            update_input["allowedOperations"] = _split_scopes(allowed_operations)

    data = execute_graphql(
        user,
        "UpdateStaticWebapp",
        {"input": update_input},
    )
    if "errors" in data:
        return data
    return data["updateWebapp"]
