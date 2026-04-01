import json

from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_pipelines(
    user, workspace_slug: str, page: int = 1, per_page: int = 10
) -> dict:
    """List pipelines in a workspace. Returns pipeline summaries (id, code, name, description). Use get_pipeline with the pipeline code to get full details including source code and run history."""
    return execute_graphql(
        user,
        "ListPipelines",
        {"workspaceSlug": workspace_slug, "page": page, "perPage": per_page},
    )


@tool
def get_pipeline(
    user,
    workspace_slug: str,
    pipeline_code: str,
    runs_page: int = 1,
    runs_per_page: int = 5,
) -> dict:
    """Get full details of a pipeline: metadata, schedule, permissions, current version source code with all files, parameters, and recent runs. Use the returned 'id' field when calling run_pipeline or update_pipeline. Use a run 'id' from the runs list with get_pipeline_run to inspect outputs and logs."""
    data = execute_graphql(
        user,
        "GetPipeline",
        {
            "workspaceSlug": workspace_slug,
            "code": pipeline_code,
            "runsPage": runs_page,
            "runsPerPage": runs_per_page,
        },
    )
    if "errors" in data:
        return data
    pipeline = data.get("pipelineByCode")
    if pipeline is None:
        return {"error": "Pipeline not found"}
    return pipeline


@tool
def get_pipeline_run(user, run_id: str) -> dict:
    """Get detailed information about a specific pipeline run. Returns status, configuration used, messages (warnings/errors), outputs (files, database tables), and execution logs. Use this after run_pipeline to check results, or to inspect any run from get_pipeline's runs list."""
    data = execute_graphql(user, "GetPipelineRun", {"id": run_id})
    if "errors" in data:
        return data
    run = data.get("pipelineRun")
    if run is None:
        return {"error": "Pipeline run not found"}
    return run


@tool
def run_pipeline(user, pipeline_id: str, config: str = "{}") -> dict:
    """Run a pipeline. Requires the pipeline UUID (from get_pipeline's 'id' field) and a JSON config string mapping parameter codes to values. Check the pipeline's parameters with get_pipeline first to see required parameters and their types. Example config: '{"param1": "value1", "param2": 42}'. Returns the created run's ID — use get_pipeline_run to monitor progress and get results."""
    try:
        config_dict = json.loads(config)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON config string"}

    data = execute_graphql(
        user,
        "RunPipeline",
        {"input": {"id": pipeline_id, "config": config_dict}},
    )
    if "errors" in data:
        return data
    return data["runPipeline"]


@tool
def update_pipeline(
    user,
    pipeline_id: str,
    name: str = "",
    description: str = "",
    schedule: str = "",
) -> dict:
    """Update a pipeline's properties. Provide the pipeline UUID (from get_pipeline's 'id' field) and any fields to change. For schedule, use a CRON expression (minute hour day-of-month month day-of-week), e.g. '0 6 * * 1' for Mondays at 6AM, '0 */2 * * *' for every 2 hours. Pass schedule='none' to disable scheduling. Only provided non-empty fields are updated."""
    update_input = {"id": pipeline_id}
    if name:
        update_input["name"] = name
    if description:
        update_input["description"] = description
    if schedule:
        update_input["schedule"] = None if schedule == "none" else schedule

    data = execute_graphql(
        user,
        "UpdatePipeline",
        {"input": update_input},
    )
    if "errors" in data:
        return data
    return data["updatePipeline"]
