from hexa.mcp.protocol import tool


@tool
def get_help(user, reason: str = "") -> dict:
    """Call this tool when you are stuck, unsure what to do next, or need guidance on OpenHEXA. Provide a reason describing why you need help (e.g. 'unsure which tool to use', 'pipeline failed', 'cannot find dataset')."""
    return {
        "about": (
            "OpenHEXA is a data integration platform. Users organize work in workspaces, "
            "which contain pipelines (automated data workflows), datasets (versioned data collections), "
            "files (in a workspace bucket), connections (external data sources like S3, PostgreSQL, DHIS2), "
            "and static web apps."
        ),
        "common_workflows": [
            "Explore: list_workspaces -> list_pipelines / list_datasets / list_files",
            "Run a pipeline: get_pipeline (check parameters) -> run_pipeline -> get_pipeline_run (check results)",
            "Inspect data: list_datasets -> get_dataset -> preview_dataset_file",
            "Use a template: list_pipeline_templates -> get_pipeline_template -> create_pipeline_from_template",
            "Create a web app: create_static_webapp with HTML/CSS/JS files",
        ],
        "tips": [
            "Start with list_workspaces to discover available workspaces",
            "Most resources are identified by workspace_slug + resource_slug or UUID",
            "When running pipelines, always check parameters first with get_pipeline",
            "Connection slugs from list_connections are used as pipeline parameter values",
        ],
    }
