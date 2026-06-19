import json

from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_static_webapps(
    user, workspace_slug: str, page: int = 1, per_page: int = 10
) -> dict:
    """List static web apps in a workspace. The returned URL can be used to access each webapp in a browser. Use get_static_webapp with a webapp slug to inspect its files and configuration."""
    return execute_graphql(
        user,
        "ListStaticWebapps",
        {"workspaceSlug": workspace_slug, "page": page, "perPage": per_page},
    )


@tool
def get_static_webapp(user, workspace_slug: str, webapp_slug: str) -> dict:
    """Get full details of a static web app: metadata, allowed API operations, and the current files with their contents.

    Use the slug from list_static_webapps (not the UUID). File contents are returned with an `encoding` field — TEXT for UTF-8 strings, BASE64 for binary files. Returns the webapp's `id` which can be passed to update_static_webapp.
    """
    data = execute_graphql(
        user,
        "GetStaticWebapp",
        {"workspaceSlug": workspace_slug, "slug": webapp_slug},
    )
    if "errors" in data:
        return data
    webapp = data.get("webapp")
    if webapp is None:
        return {"error": "Webapp not found"}
    return webapp


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
    files_to_delete_json: str = "",
    name: str = "",
    description: str = "",
    allowed_operations: str = "",
) -> dict:
    """Update an existing static web app.

    Provide the webapp UUID (from list_static_webapps) and any fields to change. Only provided non-empty fields are updated. Pass name to change the human-readable name, and description to change the description.

    Files are updated incrementally — you do NOT need to resend the whole bundle. Pass files_json as a JSON array of {path, content} objects containing only the files you want to add or change (e.g. '[{"path": "app.js", "content": "..."}]'); any file you omit is left exactly as it is. Matching is by path: an existing path is overwritten, a new path is created. To remove files, pass files_to_delete_json as a JSON array of paths (e.g. '["old.js", "legacy/style.css"]'); paths that don't exist are ignored. You can combine files_json and files_to_delete_json in a single call — they are applied as one commit.

    Pass allowed_operations as a comma-separated list of API scopes the webapp's JS may call via the same-origin /graphql/ proxy — valid values: PIPELINES_READ, PIPELINES_RUN, FILES_READ, FILES_WRITE, DATASETS_READ, DATASETS_WRITE, USER_READ. Leave empty to leave the current scopes untouched, or pass "NONE" to revoke all access. For the full reference (auth model, all top-level fields per scope, sample queries and mutations), call get_help_or_doc(topic="static-webapps").
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
    if files_to_delete_json:
        try:
            files_to_delete = json.loads(files_to_delete_json)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in files_to_delete_json"}
        if not isinstance(files_to_delete, list) or not all(
            isinstance(p, str) for p in files_to_delete
        ):
            return {
                "error": "files_to_delete_json must be a JSON array of path strings"
            }
        update_input["filesToDelete"] = files_to_delete
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


@tool
def edit_static_webapp_file(
    user,
    webapp_id: str,
    path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> dict:
    """Make a precise find/replace edit to a single file in a static web app.

    Use this for small changes to an EXISTING text file — you send only the snippet that
    changes, not the whole file. The backend reads the current file, replaces old_string with
    new_string, and commits. Prefer this over update_static_webapp when changing a few lines of
    a large file.

    Provide the webapp UUID (from list_static_webapps) and the file path (e.g. "index.html").
    old_string must match the current file content exactly (including whitespace and
    indentation) and, unless replace_all is true, must appear exactly once — include enough
    surrounding context to make it unique. Set replace_all=true to replace every occurrence.

    Use update_static_webapp instead to add new files or rewrite a file wholesale. This tool
    only edits existing UTF-8 text files (not binary files such as images).
    """
    edit_input = {
        "id": webapp_id,
        "path": path,
        "oldString": old_string,
        "newString": new_string,
        "replaceAll": replace_all,
    }
    data = execute_graphql(
        user,
        "EditWebappFile",
        {"input": edit_input},
    )
    if "errors" in data:
        return data
    return data["editWebappFile"]
