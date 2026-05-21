from hexa.mcp.docs import get_index, read_doc
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
    """Call this tool when you are stuck, unsure what to do next, or need guidance on OpenHEXA.

    - Leave topic empty for an overview (orientation, common workflows, tips). Pass a reason
      describing what you are stuck on (e.g. 'unsure which tool to use', 'pipeline failed',
      'cannot find dataset').
    - Pass a topic name to fetch that doc page in full. Reason is optional here.
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


_topic_entries = get_index()
if _topic_entries:
    _lines = [
        f"    - {entry['name']} — {entry['title']}: {entry['summary']}"
        if entry.get("summary")
        else f"    - {entry['name']} — {entry['title']}"
        for entry in _topic_entries
    ]
    get_help_or_doc.__doc__ = (
        (get_help_or_doc.__doc__ or "")
        + "\n\n    Available topics:\n"
        + "\n".join(_lines)
    )
