"""
MCP OpenHEXA Server - Main server implementation using FastMCP
"""

import base64
import io
import json
import os
import sys
import zipfile
from typing import Any

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP


# Load environment variables if available
load_dotenv()

# Import OpenHEXA SDK after loading environment variables.
try:
    from openhexa.sdk.client import openhexa
except Exception:
    openhexa = None

# Check SDK availability and required credentials.
OPENHEXA_AVAILABLE = (
    bool(openhexa)
    and bool(os.environ.get("HEXA_SERVER_URL"))
    and bool(os.environ.get("HEXA_TOKEN"))
)


# Create the MCP server
mcp = FastMCP("OpenHEXA")


@mcp.tool
def list_workspaces(page: int = 1, per_page: int = 10) -> dict:
    """
    List all available workspaces.

    Args:
        page: Page number (default: 1)
        per_page: Number of workspaces per page (default: 10)

    Returns:
        Dict containing workspaces and pagination information:
        - workspaces: List of workspace objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        workspaces_page = openhexa.workspaces(page=page, per_page=per_page)
        return {
            "workspaces": [w.model_dump() for w in workspaces_page.items],
            "total_pages": workspaces_page.total_pages,
            "current_page": page,
            "per_page": per_page,
            "count": len(workspaces_page.items),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_workspace_details(workspace_slug: str) -> dict:
    """Get details for a specific workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        workspace = openhexa.workspace(slug=workspace_slug)
        if workspace:
            return workspace.model_dump()
        else:
            return {"error": f"Workspace '{workspace_slug}' not found"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def list_datasets(page: int = 1, per_page: int = 10, workspace_slug: str | None = None) -> dict:
    """
    List datasets.

    Args:
        page: Page number (default: 1)
        per_page: Number of datasets per page (default: 10)
        workspace_slug: Optional workspace slug to scope datasets

    Returns:
        Dict containing datasets and pagination information:
        - datasets: List of dataset objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        datasets_page = openhexa.datasets(page=page, per_page=per_page)
        datasets = [d.model_dump() for d in datasets_page.items]
        if workspace_slug:
            datasets = [d for d in datasets if d.get("workspace", {}).get("slug") == workspace_slug]
        return {
            "datasets": datasets,
            "total_pages": datasets_page.total_pages,
            "current_page": page,
            "per_page": per_page,
            "count": len(datasets),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_dataset_details(dataset_id: str) -> dict:
    """Get details for a specific dataset by ID."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        dataset = openhexa.dataset(id=dataset_id)
        if dataset:
            return dataset.model_dump()
        else:
            return {"error": f"Dataset with ID '{dataset_id}' not found"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def list_pipelines(workspace_slug: str, page: int = 1, per_page: int = 10) -> dict:
    """
    List pipelines for a workspace.

    Args:
        workspace_slug: The workspace slug
        page: Page number (default: 1)
        per_page: Number of pipelines per page (default: 10)

    Returns:
        Dict containing pipelines and pagination information:
        - pipelines: List of pipeline objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        pipelines_page = openhexa.pipelines(
            workspace_slug=workspace_slug, page=page, per_page=per_page
        )
        return {
            "pipelines": [p.model_dump() for p in pipelines_page.items],
            "total_pages": pipelines_page.total_pages,
            "current_page": page,
            "per_page": per_page,
            "count": len(pipelines_page.items),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_pipeline_details(workspace_slug: str, pipeline_code: str) -> dict:
    """Get details for a specific pipeline in a workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        pipeline = openhexa.pipeline(workspace_slug=workspace_slug, pipeline_code=pipeline_code)
        if pipeline:
            return pipeline.model_dump()
        else:
            return {
                "error": f"Pipeline '{pipeline_code}' not found in workspace '{workspace_slug}'"
            }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_pipeline_runs(workspace_slug: str, pipeline_code: str) -> dict:
    """Get runs for a specific pipeline in a workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        pipeline = openhexa.pipeline(workspace_slug=workspace_slug, pipeline_code=pipeline_code)
        if pipeline:
            runs = pipeline.runs
            return {"runs": [r.model_dump() for r in runs.items], "count": len(runs.items)}
        else:
            return {
                "error": f"Pipeline '{pipeline_code}' not found in workspace '{workspace_slug}'"
            }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_pipeline_code(
    workspace_slug: str,
    pipeline_code: str,
) -> dict[str, Any]:
    """
    Get the source code of the latest version of a pipeline.

    This tool fetches the actual Python source code files from a pipeline's
    current version, including pipeline.py, requirements.txt, and any utility files.

    Args:
        workspace_slug: The workspace slug where the pipeline exists
        pipeline_code: The code identifier of the pipeline

    Returns:
        Dict containing:
        - pipeline: Basic pipeline info (id, name, code)
        - version: Version info (id, versionNumber, versionName)
        - files: List of files with their content:
            - name: Filename (e.g., "pipeline.py")
            - path: File path
            - content: The actual source code (decoded, readable)
            - language: Detected language (e.g., "python")
            - lineCount: Number of lines
        - parameters: Pipeline parameters with types and defaults
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure credentials."}

    try:
        query = """
        query getPipelineCode($workspaceSlug: String!, $code: String!) {
            pipelineByCode(workspaceSlug: $workspaceSlug, code: $code) {
                id
                name
                code
                description
                currentVersion {
                    id
                    versionNumber
                    versionName
                    description
                    createdAt
                    parameters {
                        code
                        name
                        type
                        required
                        default
                        help
                    }
                    files {
                        id
                        name
                        path
                        type
                        content
                        language
                        lineCount
                    }
                }
                workspace {
                    slug
                    name
                }
            }
        }
        """

        variables = {
            "workspaceSlug": workspace_slug,
            "code": pipeline_code,
        }

        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        pipeline = response_data.get("data", {}).get("pipelineByCode")

        if not pipeline:
            return {
                "error": f"Pipeline '{pipeline_code}' not found in workspace '{workspace_slug}'"
            }

        current_version = pipeline.get("currentVersion")
        if not current_version:
            return {
                "error": f"Pipeline '{pipeline_code}' has no versions yet",
                "pipeline": {
                    "id": pipeline.get("id"),
                    "name": pipeline.get("name"),
                    "code": pipeline.get("code"),
                },
            }

        return {
            "pipeline": {
                "id": pipeline.get("id"),
                "name": pipeline.get("name"),
                "code": pipeline.get("code"),
                "description": pipeline.get("description"),
            },
            "version": {
                "id": current_version.get("id"),
                "versionNumber": current_version.get("versionNumber"),
                "versionName": current_version.get("versionName"),
                "description": current_version.get("description"),
                "createdAt": current_version.get("createdAt"),
            },
            "files": current_version.get("files", []),
            "parameters": current_version.get("parameters", []),
            "workspace": pipeline.get("workspace"),
        }

    except Exception as e:
        return {"error": "Failed to get pipeline code: " + str(e)}


@mcp.tool
def list_workspace_members(workspace_slug: str) -> dict:
    """List members of a workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        members = openhexa.get_users(query="", workspace_slug=workspace_slug)
        return {"members": [m.model_dump() for m in members], "count": len(members)}
    except Exception as e:
        return {"error": str(e)}


def _create_pipeline_zipfile(
    code_content: str,
    requirements_txt: str | None = None,
    util_files: dict[str, str] | None = None,
) -> str:
    """
    Create a base64-encoded ZIP file containing pipeline code and optional files.

    The ZIP should have this structure:
    pipeline.zip
    ├── pipeline.py      (contains the code_content - required, main entry point)
    ├── requirements.txt (contains library dependencies - optional)
    ├── utils.py         (utility module - optional)
    ├── helpers.py       (another utility module - optional)
    └── ...              (any additional .py files)

    Args:
        code_content: Python code as string for pipeline.py (main entry point)
        requirements_txt: Optional requirements.txt content specifying library dependencies.
                         Format: one package per line, e.g., "pandas==2.0.0"
        util_files: Optional dict mapping filename to content for additional Python files.
                   Example: {"utils.py": "def helper(): ...", "config.py": "API_KEY = ..."}

    Returns:
        Base64-encoded ZIP file string
    """
    # Create in-memory ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Main pipeline file (required)
        zip_file.writestr("pipeline.py", code_content)

        # Requirements file (optional)
        if requirements_txt:
            zip_file.writestr("requirements.txt", requirements_txt)

        # Additional utility files (optional)
        if util_files:
            for filename, content in util_files.items():
                # Ensure .py extension and prevent overwriting pipeline.py
                if filename == "pipeline.py":
                    continue  # Skip, pipeline.py is already added
                zip_file.writestr(filename, content)

    # Get ZIP bytes and encode to base64
    zip_bytes = zip_buffer.getvalue()
    return base64.b64encode(zip_bytes).decode("utf-8")


@mcp.tool
def create_pipeline(
    workspace_slug: str,
    name: str,
    code_content: str,
    description: str | None = None,
    functional_type: str | None = None,
    tags: list[str] | None = None,
    requirements_txt: str | None = None,
    util_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Create a new pipeline with code in a workspace.

    Args:
        workspace_slug: The workspace slug where to create the pipeline
        name: Pipeline name (code will be auto-generated from this)
        code_content: Python code for pipeline.py (main entry point, will be packaged as ZIP)
        description: Optional pipeline description
        functional_type: Optional type: extraction, transformation, loading, or computation
        tags: Optional list of tags
        requirements_txt: Optional requirements.txt content specifying library dependencies.
                         One package per line, e.g., "pandas==2.0.0" or "requests>=2.28.0"
        util_files: Optional dict of additional Python files to include in the pipeline.
                   Keys are filenames (e.g., "utils.py"), values are file contents.
                   Example: {"utils.py": "def helper(): ...", "config.py": "API_URL = ..."}

    Returns:
        Dict containing the created pipeline details and upload status
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        # Validate inputs
        if not workspace_slug or not name or not code_content:
            return {"error": "workspace_slug, name, and code_content are required"}

        # Step 1: Create the pipeline entity
        create_query = """
            mutation createPipeline($input: CreatePipelineInput!) {
                createPipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        id
                        name
                        code
                        type
                        workspace { slug }
                    }
                }
            }
        """

        create_input = {
            "name": name,
            "workspaceSlug": workspace_slug,
        }

        if functional_type:
            create_input["functionalType"] = functional_type.lower()

        if tags:
            create_input["tags"] = tags

        create_variables = {"input": create_input}

        result = openhexa.execute(query=create_query, variables=create_variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        create_result = response_data.get("data", {}).get("createPipeline", {})

        if not create_result.get("success"):
            errors = create_result.get("errors", [])
            return {"error": f"Failed to create pipeline: {errors}"}

        pipeline = create_result.get("pipeline")
        if not pipeline:
            return {"error": "Pipeline creation succeeded but no pipeline data returned"}

        pipeline_code = pipeline["code"]

        # Step 2: Package code into ZIP (with optional requirements.txt and util files)
        try:
            zipfile_b64 = _create_pipeline_zipfile(code_content, requirements_txt, util_files)
        except Exception as e:
            return {
                "error": f"Failed to create ZIP file: {str(e)}",
                "pipeline": pipeline,
                "note": "Pipeline was created but code upload failed",
            }

        # Step 3: Upload the code
        upload_query = """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }
        """

        upload_input = {
            "workspaceSlug": workspace_slug,
            "pipelineCode": pipeline_code,
            "name": "Initial version",
            "description": description or "Created via MCP",
            "zipfile": zipfile_b64,
        }

        upload_variables = {"input": upload_input}

        upload_result = openhexa.execute(query=upload_query, variables=upload_variables)
        upload_response_data = upload_result.json()

        if "errors" in upload_response_data:
            return {
                "error": f"GraphQL error during upload: {upload_response_data['errors']}",
                "pipeline": pipeline,
                "note": "Pipeline was created but code upload failed",
            }

        upload_result_data = upload_response_data.get("data", {}).get("uploadPipeline", {})

        if not upload_result_data.get("success"):
            errors = upload_result_data.get("errors", [])
            return {
                "error": f"Failed to upload pipeline code: {errors}",
                "pipeline": pipeline,
                "note": "Pipeline was created but code upload failed",
            }

        return {
            "success": True,
            "pipeline": pipeline,
            "message": f"Pipeline '{name}' created and code uploaded successfully",
        }

    except Exception as e:
        return {"error": f"Failed to create pipeline: {str(e)}"}


@mcp.tool
def upload_pipeline_version(
    workspace_slug: str,
    pipeline_code: str,
    code_content: str,
    version_name: str | None = None,
    description: str | None = None,
    external_link: str | None = None,
    requirements_txt: str | None = None,
    util_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Upload a new version to an existing pipeline.

    This tool adds a new version to an already existing pipeline. Use create_pipeline
    to create a new pipeline first, then use this tool to update it with new versions.

    Args:
        workspace_slug: The workspace slug where the pipeline exists
        pipeline_code: The code identifier of the existing pipeline to update
        code_content: Python code for pipeline.py (main entry point, will be packaged as ZIP)
        version_name: Optional name for this version (e.g., "v2.0", "bugfix-auth")
        description: Optional description of changes in this version
        external_link: Optional URL to external documentation or repository
        requirements_txt: Optional requirements.txt content specifying library dependencies.
                         One package per line, e.g., "pandas==2.0.0" or "requests>=2.28.0"
        util_files: Optional dict of additional Python files to include in the pipeline.
                   Keys are filenames (e.g., "utils.py"), values are file contents.
                   Example: {"utils.py": "def helper(): ...", "config.py": "API_URL = ..."}

    Returns:
        Dict containing the uploaded pipeline version details
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        # Validate inputs
        if not workspace_slug or not pipeline_code or not code_content:
            return {"error": "workspace_slug, pipeline_code, and code_content are required"}

        # Package code into ZIP (with optional requirements.txt and util files)
        try:
            zipfile_b64 = _create_pipeline_zipfile(code_content, requirements_txt, util_files)
        except Exception as e:
            return {"error": f"Failed to create ZIP file: {str(e)}"}

        # Upload the new version
        upload_query = """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    details
                    pipelineVersion {
                        id
                        versionNumber
                        versionName
                        description
                        createdAt
                        pipeline {
                            id
                            name
                            code
                        }
                    }
                }
            }
        """

        upload_input = {
            "workspaceSlug": workspace_slug,
            "pipelineCode": pipeline_code,
            "zipfile": zipfile_b64,
        }

        if version_name:
            upload_input["name"] = version_name
        if description:
            upload_input["description"] = description
        if external_link:
            upload_input["externalLink"] = external_link

        upload_variables = {"input": upload_input}

        result = openhexa.execute(query=upload_query, variables=upload_variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        upload_result = response_data.get("data", {}).get("uploadPipeline", {})

        if not upload_result.get("success"):
            errors = upload_result.get("errors", [])
            details = upload_result.get("details", "")
            error_msg = f"Failed to upload pipeline version: {errors}"
            if details:
                error_msg += f" - {details}"

            # Provide helpful error messages for common errors
            if "PIPELINE_NOT_FOUND" in errors:
                error_msg += (
                    f"\nPipeline '{pipeline_code}' not found in workspace "
                    f"'{workspace_slug}'. Use create_pipeline first."
                )
            elif "PERMISSION_DENIED" in errors:
                error_msg += "\nYou don't have permission to update this pipeline."
            elif "PIPELINE_DOES_NOT_SUPPORT_PARAMETERS" in errors:
                error_msg += (
                    "\nThis pipeline has a schedule and all parameters "
                    "must be optional or have default values."
                )
            elif "DUPLICATE_PIPELINE_VERSION_NAME" in errors:
                error_msg += (
                    f"\nVersion name '{version_name}' already exists. Choose a different name."
                )

            return {"error": error_msg}

        version = upload_result.get("pipelineVersion")
        version_name_result = version.get("versionName") if version else "unknown"

        return {
            "success": True,
            "version": version,
            "message": (
                f"New version '{version_name_result}' uploaded successfully "
                f"to pipeline '{pipeline_code}'"
            ),
        }

    except Exception as e:
        return {"error": "Failed to upload pipeline version: " + str(e)}


@mcp.tool
def list_connections(workspace_slug: str) -> dict[str, Any]:
    """
    List connections in a specific workspace.

    Args:
        workspace_slug: The workspace slug

    Returns:
        Dict containing connection information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        query = """
        query WorkspaceConnections($slug: String!) {
            workspace(slug: $slug) {
                connections {
                    id
                    name
                    slug
                    description
                    type
                    createdAt
                    updatedAt
                    user {
                        id
                        displayName
                        email
                    }
                    fields {
                        code
                        value
                        secret
                    }
                }
            }
        }
        """

        variables = {"slug": workspace_slug}

        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        workspace = response_data.get("data", {}).get("workspace")
        if not workspace:
            return {"error": f"Workspace '{workspace_slug}' not found"}

        connections = workspace.get("connections", [])

        return {"connections": connections, "count": len(connections)}

    except Exception as e:
        return {"error": f"Failed to list connections: {str(e)}"}


@mcp.tool
def list_webapps(workspace_slug: str, page: int = 1, per_page: int = 10) -> dict[str, Any]:
    """
    List webapps in a specific workspace.

    Args:
        workspace_slug: The workspace slug
        page: Page number (default: 1)
        per_page: Number of webapps per page (default: 10)

    Returns:
        Dict containing webapp information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        query = """
        query WorkspaceWebapps($slug: String!, $page: Int = 1, $perPage: Int = 10) {
            workspace(slug: $slug) {
                webapps(page: $page, perPage: $perPage) {
                    items {
                        id
                        name
                        description
                        url
                        icon
                        isFavorite
                        createdAt
                        createdBy {
                            id
                            displayName
                            email
                        }
                        permissions {
                            delete
                            update
                        }
                    }
                    pageNumber
                    totalItems
                    totalPages
                }
            }
        }
        """

        variables = {"slug": workspace_slug, "page": page, "perPage": per_page}

        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        workspace = response_data.get("data", {}).get("workspace")
        if not workspace:
            return {"error": f"Workspace '{workspace_slug}' not found"}

        webapps_data = workspace.get("webapps", {})

        return {
            "webapps": webapps_data.get("items", []),
            "total_pages": webapps_data.get("totalPages", 0),
            "total_items": webapps_data.get("totalItems", 0),
            "current_page": webapps_data.get("pageNumber", page),
        }

    except Exception as e:
        return {"error": f"Failed to list webapps: {str(e)}"}


@mcp.tool
def search_resources(
    query: str, resource_type: str | None = None, workspace_slug: str | None = None
) -> dict[str, Any]:
    """
    Search across OpenHEXA resources (workspaces, datasets, pipelines).

    Args:
        query: Search query string
        resource_type: Optional filter by resource type ('workspace', 'dataset', 'pipeline')
        workspace_slug: Optional workspace slug to limit search scope

    Returns:
        Dict containing search results
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        results = {"success": True, "query": query, "results": []}

        # Search workspaces
        if not resource_type or resource_type == "workspace":
            workspace_results = list_workspaces()
            if workspace_results.get("success"):
                for workspace in workspace_results.get("workspaces", []):
                    if (
                        query.lower() in workspace.get("name", "").lower()
                        or query.lower() in workspace.get("description", "").lower()
                    ):
                        results["results"].append({"type": "workspace", "resource": workspace})

        # Search datasets
        if not resource_type or resource_type == "dataset":
            dataset_results = list_datasets(workspace_slug=workspace_slug)
            if dataset_results.get("success"):
                for dataset in dataset_results.get("datasets", []):
                    dataset_obj = dataset.get("dataset", dataset)  # Handle nested structure
                    if (
                        query.lower() in dataset_obj.get("name", "").lower()
                        or query.lower() in dataset_obj.get("description", "").lower()
                    ):
                        results["results"].append({"type": "dataset", "resource": dataset_obj})

        # Search pipelines
        if not resource_type or resource_type == "pipeline":
            pipeline_results = list_pipelines(workspace_slug=workspace_slug)
            if pipeline_results.get("success"):
                for pipeline in pipeline_results.get("pipelines", []):
                    if (
                        query.lower() in pipeline.get("name", "").lower()
                        or query.lower() in pipeline.get("description", "").lower()
                    ):
                        results["results"].append({"type": "pipeline", "resource": pipeline})

        results["count"] = len(results["results"])
        return results

    except Exception as e:
        return {"error": f"Failed to search resources: {str(e)}"}


@mcp.tool
def list_dataset_versions(dataset_id: str) -> dict[str, Any]:
    """
    List all versions of a dataset.
    Args:
        dataset_id: The ID identifier for the dataset
    Returns:
        Dict containing dataset version information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getDataset($id: ID!) {
            dataset(id: $id) {
                versions {
                    items {
                        id
                        name
                        changelog
                        createdAt
                        createdBy {
                            id
                            displayName
                            email
                        }
                    }
                }
            }
        }
        """
        result = openhexa.execute(query=query, variables={"id": dataset_id})
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        dataset = response_data.get("data", {}).get("dataset")
        if not dataset:
            return {"error": f"Dataset '{dataset_id}' not found"}
        versions = dataset.get("versions", {}).get("items", [])
        return {"versions": versions, "count": len(versions)}
    except Exception as e:
        return {"error": f"Failed to list dataset versions: {str(e)}"}


@mcp.tool
def get_dataset_version_details(version_id: str) -> dict[str, Any]:
    """
    Get detailed information about a specific dataset version.
    Args:
        version_id: The ID of the dataset version
    Returns:
        Dict containing detailed dataset version information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getDatasetVersion($id: ID!) {
            datasetVersion(id: $id) {
                id
                name
                changelog
                createdAt
                createdBy {
                    id
                    displayName
                    email
                }
                files {
                    items {
                        id
                        size
                        createdAt
                    }
                }
            }
        }
        """
        result = openhexa.execute(query=query, variables={"id": version_id})
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        version = response_data.get("data", {}).get("datasetVersion")
        if not version:
            return {"error": f"Dataset version '{version_id}' not found"}
        return {"version": version}
    except Exception as e:
        return {"error": f"Failed to get dataset version details: {str(e)}"}


@mcp.tool
def list_dataset_files(dataset_id: str) -> dict[str, Any]:
    """
    List all files for all versions of a dataset.
    Args:
        dataset_id: The ID identifier for the dataset
    Returns:
        Dict containing all files for all versions
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getDataset($id: ID!) {
            dataset(id: $id) {
                versions {
                    items {
                        id
                        name
                        files {
                            items {
                                id
                                size
                                createdAt
                            }
                        }
                    }
                }
            }
        }
        """
        result = openhexa.execute(query=query, variables={"id": dataset_id})
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}", "raw": response_data}
        dataset = response_data.get("data", {}).get("dataset")
        if not dataset:
            return {"error": f"Dataset '{dataset_id}' not found"}
        files = []
        for version in dataset.get("versions", {}).get("items", []):
            for file in version.get("files", {}).get("items", []):
                files.append({**file, "version_id": version["id"], "version_name": version["name"]})
        return {"files": files, "count": len(files)}
    except Exception as e:
        return {"error": f"Failed to list dataset files: {str(e)}"}


@mcp.tool
def get_dataset_file_details(file_id: str) -> dict[str, Any]:
    """
    Get details for a specific dataset file.
    Args:
        file_id: The ID of the file
    Returns:
        Dict containing file metadata
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getFile($id: ID!) {
            datasetVersionFile(id: $id) {
                id
                filename
                size
                contentType
                createdAt
                createdBy {
                    id
                    displayName
                    email
                }
                downloadUrl
                uri
            }
        }
        """
        variables = {"id": file_id}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        file = response_data.get("data", {}).get("datasetVersionFile")
        if not file:
            return {"error": f"File '{file_id}' not found"}
        return {"file": file}
    except Exception as e:
        return {"error": f"Failed to get file details: {str(e)}"}


@mcp.tool
def search_datasets(query_str: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
    """
    Search datasets by name or description.

    Args:
        query_str: Search string
        page: Page number (default: 1)
        per_page: Number of results per page (default: 20)

    Returns:
        Dict containing datasets and pagination information:
        - datasets: List of dataset objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
        - total_items: Total number of items across all pages
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query searchDatasets($query: String, $page: Int!, $perPage: Int!) {
            datasets(query: $query, page: $page, perPage: $perPage) {
                items {
                    id
                    name
                    slug
                    description
                    createdAt
                    updatedAt
                    createdBy {
                        id
                        displayName
                        email
                    }
                }
                totalItems
                totalPages
            }
        }
        """
        variables = {"query": query_str, "page": page, "perPage": per_page}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        datasets_info = response_data.get("data", {}).get("datasets", {})
        datasets = datasets_info.get("items", [])
        total_items = datasets_info.get("totalItems", 0)
        total_pages = datasets_info.get("totalPages", 0)
        return {
            "datasets": datasets,
            "count": len(datasets),
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
        }
    except Exception as e:
        return {"error": f"Failed to search datasets: {str(e)}"}


@mcp.tool
def list_datasets_by_creator(
    creator_email: str, page: int = 1, per_page: int = 20
) -> dict[str, Any]:
    """
    List datasets created by a specific user.
    Args:
        creator_email: The email of the creator
        page: Page number (default: 1)
        per_page: Number of results per page (default: 20)
    Returns:
        Dict containing datasets by creator
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query datasetsByCreator($page: Int!, $perPage: Int!) {
            datasets(page: $page, perPage: $perPage) {
                items {
                    id
                    name
                    slug
                    description
                    createdAt
                    updatedAt
                    createdBy {
                        id
                        displayName
                        email
                    }
                }
                totalItems
                totalPages
            }
        }
        """
        variables = {"page": page, "perPage": per_page}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        datasets = response_data.get("data", {}).get("datasets", {}).get("items", [])
        filtered = [d for d in datasets if d.get("createdBy", {}).get("email") == creator_email]
        return {
            "datasets": filtered,
            "count": len(filtered),
            "current_page": page,
            "per_page": per_page,
        }
    except Exception as e:
        return {"error": f"Failed to list datasets by creator: {str(e)}"}


@mcp.tool
def preview_dataset_file(file_id: str) -> dict:
    """
    Preview a dataset file by fetching a sample using the OpenHEXA GraphQL API.
    Args:
        file_id: The ID of the file to preview
    Returns:
        Dict containing the file sample, status, and any status reason
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query GetDatasetVersionFileSample($id: ID!) {
          datasetVersionFile(id: $id) {
            id
            properties
            fileSample {
              sample
              status
              statusReason
              __typename
            }
            __typename
          }
        }
        """
        variables = {"id": file_id}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}", "raw": response_data}
        file_data = response_data.get("data", {}).get("datasetVersionFile")
        if not file_data:
            return {"error": f"File '{file_id}' not found"}
        sample_info = file_data.get("fileSample")
        return {
            "file_id": file_id,
            "sample": sample_info.get("sample") if sample_info else None,
            "status": sample_info.get("status") if sample_info else None,
            "status_reason": sample_info.get("statusReason") if sample_info else None,
            "properties": file_data.get("properties"),
        }
    except Exception as e:
        return {"error": f"Failed to preview file: {str(e)}"}


# =============================================================================
# Pipeline Templates Tools
# =============================================================================


@mcp.tool
def list_pipeline_templates(
    page: int = 1,
    per_page: int = 15,
    search: str | None = None,
    functional_type: str | None = None,
    is_validated: bool | None = None,
    tags: list[str] | None = None,
    order_by: str | None = None,
) -> dict[str, Any]:
    """
    List all available pipeline templates (START HERE for templates).

    Pipeline templates are reusable pipeline blueprints that can be used to create
    new pipelines. Templates are public and available across all workspaces.

    WORKFLOW:
    1. list_pipeline_templates() -> Get template list with names, descriptions, codes
    2. get_pipeline_template_by_code(code) -> Get detailed template info + version IDs
    3. get_pipeline_template_version(version_id) -> Get actual source code (files)
    4. create_pipeline_from_template(workspace, version_id) -> Create pipeline

    Returns for each template:
    - id, name, code, description, functionalType
    - currentVersion.id (use this with get_pipeline_template_version to get code)
    - tags, organization, pipelinesCount

    Args:
        page: Page number (default: 1)
        per_page: Number of templates per page (default: 15)
        search: Optional search string to filter templates by name/description
        functional_type: Optional filter by type: extraction, transformation,
                        loading, or computation
        is_validated: Optional filter for validated/official templates only
        tags: Optional list of tags to filter by
        order_by: Optional ordering: PIPELINES_COUNT_DESC, PIPELINES_COUNT_ASC,
                 NAME_DESC, NAME_ASC, CREATED_AT_DESC, CREATED_AT_ASC

    Returns:
        Dict containing templates and pagination information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure credentials."}

    try:
        query = """
        query listPipelineTemplates(
            $page: Int,
            $perPage: Int,
            $search: String,
            $functionalType: PipelineFunctionalType,
            $isValidated: Boolean,
            $tags: [String!],
            $orderBy: PipelineTemplateOrderBy
        ) {
            pipelineTemplates(
                page: $page,
                perPage: $perPage,
                search: $search,
                functionalType: $functionalType,
                isValidated: $isValidated,
                tags: $tags,
                orderBy: $orderBy
            ) {
                pageNumber
                totalPages
                totalItems
                items {
                    id
                    name
                    code
                    description
                    functionalType
                    pipelinesCount
                    validatedAt
                    updatedAt
                    tags {
                        id
                        name
                    }
                    organization {
                        id
                        name
                    }
                    currentVersion {
                        id
                        versionNumber
                        changelog
                        createdAt
                    }
                    permissions {
                        delete
                        update
                    }
                }
            }
        }
        """

        variables: dict[str, Any] = {
            "page": page,
            "perPage": per_page,
        }

        if search:
            variables["search"] = search
        if functional_type:
            variables["functionalType"] = functional_type.upper()
        if is_validated is not None:
            variables["isValidated"] = is_validated
        if tags:
            variables["tags"] = tags
        if order_by:
            variables["orderBy"] = order_by

        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        templates_data = response_data.get("data", {}).get("pipelineTemplates", {})

        return {
            "templates": templates_data.get("items", []),
            "total_pages": templates_data.get("totalPages", 0),
            "total_items": templates_data.get("totalItems", 0),
            "current_page": templates_data.get("pageNumber", page),
            "per_page": per_page,
            "count": len(templates_data.get("items", [])),
        }

    except Exception as e:
        return {"error": f"Failed to list pipeline templates: {str(e)}"}


@mcp.tool
def get_pipeline_template_by_code(template_code: str) -> dict[str, Any]:
    """
    Get detailed information about a specific pipeline template.

    Use this after list_pipeline_templates() to get more details about a template
    you're interested in. Returns version history and currentVersion.id which
    you can use with get_pipeline_template_version() to see the actual code.

    Args:
        template_code: The unique code identifier of the template (from list_pipeline_templates)

    Returns:
        Dict containing:
        - template.description, config, functionalType
        - template.currentVersion.id (use with get_pipeline_template_version for code)
        - template.versions[] (list of all versions with their IDs)
        - template.organization, workspace, tags
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure credentials."}

    try:
        query = """
        query getTemplateByCode($code: String!) {
            templateByCode(code: $code) {
                id
                name
                code
                description
                config
                functionalType
                pipelinesCount
                validatedAt
                updatedAt
                tags {
                    id
                    name
                }
                organization {
                    id
                    name
                }
                workspace {
                    slug
                    name
                }
                currentVersion {
                    id
                    versionNumber
                    changelog
                    createdAt
                    isLatestVersion
                    user {
                        id
                        displayName
                        email
                    }
                    sourcePipelineVersion {
                        id
                        versionName
                    }
                }
                versions(page: 1, perPage: 10) {
                    totalItems
                    items {
                        id
                        versionNumber
                        changelog
                        createdAt
                    }
                }
                permissions {
                    delete
                    update
                }
            }
        }
        """

        variables = {"code": template_code}

        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        template = response_data.get("data", {}).get("templateByCode")

        if not template:
            return {"error": f"Template with code '{template_code}' not found"}

        return {"template": template}

    except Exception as e:
        return {"error": f"Failed to get template: {str(e)}"}


@mcp.tool
def get_pipeline_template_version(version_id: str) -> dict[str, Any]:
    """
    Get the actual source code of a pipeline template version.

    THIS IS THE TOOL TO USE TO SEE THE PIPELINE CODE.

    Use after list_pipeline_templates() or get_pipeline_template_by_code() to retrieve
    the actual Python source code files of a template.

    Args:
        version_id: The UUID of the template version (from currentVersion.id or versions[].id)

    Returns:
        Dict containing:
        - version.template (name, code, description)
        - version.sourcePipelineVersion.parameters[] (pipeline parameters with types/defaults)
        - version.sourcePipelineVersion.files[] - THE ACTUAL CODE:
            - files[].name (e.g., "pipeline.py")
            - files[].path (e.g., "pipeline.py")
            - files[].content (THE PYTHON SOURCE CODE - decoded, readable)
            - files[].language (e.g., "python")
            - files[].type ("file" or "directory")
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure credentials."}

    try:
        query = """
        query getTemplateVersion($id: UUID!) {
            pipelineTemplateVersion(id: $id) {
                id
                versionNumber
                changelog
                createdAt
                isLatestVersion
                user {
                    id
                    displayName
                    email
                }
                template {
                    id
                    name
                    code
                    description
                    functionalType
                }
                sourcePipelineVersion {
                    id
                    versionName
                    versionNumber
                    description
                    parameters {
                        code
                        name
                        type
                        required
                        default
                        help
                    }
                    files {
                        id
                        name
                        path
                        type
                        content
                        language
                        lineCount
                        autoSelect
                    }
                }
                permissions {
                    update
                    delete
                }
            }
        }
        """

        variables = {"id": version_id}

        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        version = response_data.get("data", {}).get("pipelineTemplateVersion")

        if not version:
            return {"error": f"Template version '{version_id}' not found"}

        return {"version": version}

    except Exception as e:
        return {"error": f"Failed to get template version: {str(e)}"}


@mcp.tool
def create_pipeline_from_template(
    workspace_slug: str,
    template_version_id: str,
) -> dict[str, Any]:
    """
    Create a new pipeline in your workspace from a template.

    This is the final step in the template workflow - it copies the template's
    code into a new pipeline in your workspace that you can then run or modify.

    WORKFLOW REMINDER:
    1. list_pipeline_templates() -> find template
    2. get_pipeline_template_version(currentVersion.id) -> review code
    3. create_pipeline_from_template(workspace, version_id) -> CREATE IT

    Args:
        workspace_slug: The workspace slug where to create the pipeline
        template_version_id: The UUID of the template version (from currentVersion.id)

    Returns:
        Dict containing:
        - success: True/False
        - pipeline.id, pipeline.name, pipeline.code
        - pipeline.currentVersion (the created version)
        - pipeline.sourceTemplate (reference to original template)
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure credentials."}

    try:
        mutation = """
        mutation createPipelineFromTemplate(
            $input: CreatePipelineFromTemplateVersionInput!
        ) {
            createPipelineFromTemplateVersion(input: $input) {
                success
                errors
                pipeline {
                    id
                    name
                    code
                    type
                    description
                    workspace {
                        slug
                        name
                    }
                    sourceTemplate {
                        id
                        name
                        code
                    }
                    currentVersion {
                        id
                        versionNumber
                        versionName
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "workspaceSlug": workspace_slug,
                "pipelineTemplateVersionId": template_version_id,
            }
        }

        result = openhexa.execute(query=mutation, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        create_result = response_data.get("data", {}).get("createPipelineFromTemplateVersion", {})

        if not create_result.get("success"):
            errors = create_result.get("errors", [])
            error_msg = f"Failed to create pipeline from template: {errors}"

            if "PERMISSION_DENIED" in errors:
                error_msg += "\nYou don't have permission to create pipelines."
            elif "WORKSPACE_NOT_FOUND" in errors:
                error_msg += f"\nWorkspace '{workspace_slug}' not found."
            elif "PIPELINE_TEMPLATE_VERSION_NOT_FOUND" in errors:
                error_msg += f"\nTemplate version '{template_version_id}' not found."

            return {"error": error_msg}

        pipeline = create_result.get("pipeline")

        return {
            "success": True,
            "pipeline": pipeline,
            "message": (
                f"Pipeline '{pipeline.get('name')}' created successfully "
                f"from template in workspace '{workspace_slug}'"
            ),
        }

    except Exception as e:
        return {"error": f"Failed to create pipeline from template: {str(e)}"}


# =============================================================================
# Pipeline Scheduling Tools
# =============================================================================


@mcp.tool
def schedule_pipeline(
    pipeline_id: str,
    cron_expression: str | None = None,
    enabled: bool = True,
) -> dict[str, Any]:
    """
    Schedule a pipeline to run automatically using a CRON expression.

    This tool allows you to enable, update, or disable automatic scheduling for a pipeline.
    The pipeline must be "schedulable" - meaning all required parameters must have default
    values or be configured in the pipeline's config.

    CRON FORMAT: minute hour day-of-month month day-of-week
    Examples:
    - "0 * * * *"      -> Every hour at minute 0
    - "0 0 * * *"      -> Every day at midnight
    - "0 6 * * 1"      -> Every Monday at 6:00 AM
    - "0 */4 * * *"    -> Every 4 hours
    - "30 8 * * 1-5"   -> Weekdays at 8:30 AM
    - "0 0 1 * *"      -> First day of each month at midnight

    Args:
        pipeline_id: The UUID of the pipeline to schedule
        cron_expression: CRON expression for the schedule. Set to None or empty to disable.
        enabled: If False, disables the schedule (equivalent to cron_expression=None)

    Returns:
        Dict containing:
        - success: True/False
        - pipeline: Updated pipeline with schedule info
        - message: Description of what was done
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure credentials."}

    try:
        # If disabled or no cron expression, we're disabling the schedule
        schedule_value = cron_expression if enabled and cron_expression else None

        mutation = """
        mutation updatePipelineSchedule($input: UpdatePipelineInput!) {
            updatePipeline(input: $input) {
                success
                errors
                pipeline {
                    id
                    name
                    code
                    schedule
                    currentVersion {
                        id
                        versionNumber
                        parameters {
                            code
                            name
                            type
                            required
                            default
                        }
                    }
                    workspace {
                        slug
                        name
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "id": pipeline_id,
                "schedule": schedule_value,
            }
        }

        result = openhexa.execute(query=mutation, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        update_result = response_data.get("data", {}).get("updatePipeline", {})

        if not update_result.get("success"):
            errors = update_result.get("errors", [])
            error_msg = f"Failed to update pipeline schedule: {errors}"

            if "PERMISSION_DENIED" in errors:
                error_msg += "\nYou don't have permission to schedule this pipeline."
            elif "NOT_FOUND" in errors:
                error_msg += f"\nPipeline '{pipeline_id}' not found."
            elif "MISSING_VERSION_CONFIG" in errors:
                error_msg += (
                    "\nPipeline is not schedulable. All required parameters must have "
                    "default values or be configured. Check pipeline parameters."
                )

            return {"error": error_msg}

        pipeline = update_result.get("pipeline")
        pipeline_name = pipeline.get("name", pipeline_id)

        if schedule_value:
            message = f"Pipeline '{pipeline_name}' scheduled with CRON: {schedule_value}"
        else:
            message = f"Pipeline '{pipeline_name}' schedule disabled"

        return {
            "success": True,
            "pipeline": pipeline,
            "schedule": schedule_value,
            "message": message,
        }

    except Exception as e:
        return {"error": "Failed to schedule pipeline: " + str(e)}


@mcp.tool
def get_pipeline_schedule(
    workspace_slug: str,
    pipeline_code: str,
) -> dict[str, Any]:
    """Get the current schedule configuration of a pipeline.

    Use this to check if a pipeline is scheduled and what its CRON expression is.

    Args:
        workspace_slug: The workspace slug where the pipeline exists
        pipeline_code: The code identifier of the pipeline

    Returns:
        Dict containing:
        - pipeline_id, name, code
        - schedule: Current CRON expression (null if not scheduled)
        - parameters: List of pipeline parameters (to understand scheduling requirements)
        - can_schedule: Whether user has permission to schedule
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure credentials."}

    try:
        query = """
        query getPipelineSchedule($workspaceSlug: String!, $code: String!) {
            pipelineByCode(workspaceSlug: $workspaceSlug, code: $code) {
                id
                name
                code
                schedule
                currentVersion {
                    id
                    versionNumber
                    parameters {
                        code
                        name
                        type
                        required
                        default
                        help
                    }
                }
                permissions {
                    schedule
                    update
                }
                workspace {
                    slug
                    name
                }
            }
        }
        """

        variables = {
            "workspaceSlug": workspace_slug,
            "code": pipeline_code,
        }

        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        pipeline = response_data.get("data", {}).get("pipelineByCode")

        if not pipeline:
            return {
                "error": f"Pipeline '{pipeline_code}' not found in workspace '{workspace_slug}'"
            }

        current_version = pipeline.get("currentVersion", {}) or {}
        parameters = current_version.get("parameters", [])

        # Determine if pipeline is schedulable based on parameters
        # A pipeline is schedulable if all required parameters have defaults
        is_schedulable = all(
            not param.get("required") or param.get("default") is not None for param in parameters
        )

        return {
            "pipeline_id": pipeline.get("id"),
            "name": pipeline.get("name"),
            "code": pipeline.get("code"),
            "schedule": pipeline.get("schedule"),
            "is_scheduled": pipeline.get("schedule") is not None,
            "is_schedulable": is_schedulable,
            "parameters": parameters,
            "can_schedule": pipeline.get("permissions", {}).get("schedule", False),
            "workspace": pipeline.get("workspace"),
        }

    except Exception as e:
        return {"error": "Failed to get pipeline schedule: " + str(e)}


def main():
    """Main entry point for the MCP OpenHEXA server."""
    # Check for required environment variables or configuration
    if not OPENHEXA_AVAILABLE:
        print("Warning: OpenHEXA SDK not properly initialized", file=sys.stderr)
        print("The server will start but tools will return configuration errors", file=sys.stderr)
        print(
            "Please configure your OpenHEXA credentials (HEXA_SERVER_URL, HEXA_TOKEN)",
            file=sys.stderr,
        )

    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
