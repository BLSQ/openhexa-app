from hexa.mcp.docs import available_doc_names, get_index, read_doc
from hexa.mcp.protocol import tool

_OVERVIEW = {
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
        "For deeper guidance on a topic, call this tool again with topic=<doc-name>",
    ],
}


@tool
def get_help_or_doc(user, topic: str = "", reason: str = "") -> dict:
    """Call this tool when you are stuck, unsure what to do next, or need guidance on OpenHEXA. Provide a reason describing why you need help (e.g. 'unsure which tool to use', 'pipeline failed', 'cannot find dataset').

    Leave topic empty for an overview (orientation, common workflows, tips). Pass a topic name to get guidance on a specific subject.
    """
    if topic:
        doc = read_doc(topic)
        if doc is None:
            return {
                "error": f"Unknown topic '{topic}'.",
                "available_topics": [d["name"] for d in get_index()],
            }
        return doc
    return {**_OVERVIEW, "docs": get_index()}


_topic_names = available_doc_names()
if _topic_names:
    get_help_or_doc.__doc__ = (
        (get_help_or_doc.__doc__ or "")
        + "\n\n    Available topics: "
        + ", ".join(_topic_names)
        + "."
    )
