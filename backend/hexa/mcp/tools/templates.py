from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_pipeline_templates(
    user,
    search: str = "",
    page: int = 1,
    per_page: int = 15,
) -> dict:
    """List available pipeline templates. Optionally filter by search query. Templates are reusable pipeline blueprints. Workflow: list_pipeline_templates -> get_pipeline_template (to review code) -> create_pipeline_from_template (to instantiate in a workspace)."""
    variables: dict = {"page": page, "perPage": per_page}
    if search:
        variables["search"] = search
    return execute_graphql(user, "ListPipelineTemplates", variables)


@tool
def get_pipeline_template(user, template_code: str) -> dict:
    """Get full details of a pipeline template including its description, config, version history, and the current version's source code and parameters. Use the currentVersion.id as the template_version_id when calling create_pipeline_from_template."""
    data = execute_graphql(
        user,
        "GetPipelineTemplate",
        {"code": template_code},
    )
    if "errors" in data:
        return data
    template = data.get("templateByCode")
    if template is None:
        return {"error": "Template not found"}
    return template


@tool
def create_pipeline_from_template(
    user, workspace_slug: str, template_version_id: str
) -> dict:
    """Create a new pipeline in a workspace from a template version. Use get_pipeline_template first to find the template_version_id (the currentVersion.id). The new pipeline will have the template's code, parameters, and configuration pre-configured."""
    data = execute_graphql(
        user,
        "CreatePipelineFromTemplate",
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "pipelineTemplateVersionId": template_version_id,
            }
        },
    )
    if "errors" in data:
        return data
    return data["createPipelineFromTemplateVersion"]
