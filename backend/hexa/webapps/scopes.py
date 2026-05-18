"""Mapping between webapp operation scopes, GraphQL top-level fields, and Django permissions.

This is the single source of truth used both by the GraphQL proxy (which gates
incoming requests by their top-level field names) and by `WebappUser.has_perm`
(which gates resolver-level permission checks by the scopes the webapp has been
granted). Adding a new resolver that webapps may reach means adding it here.
"""

from hexa.webapps.models import Webapp

OperationScope = Webapp.OperationScope


SCOPE_FIELDS: dict[Webapp.OperationScope, set[str]] = {
    OperationScope.PIPELINES_RUN: {"runPipeline", "stopPipeline"},
    OperationScope.PIPELINES_READ: {
        "pipeline",
        "pipelines",
        "pipelineByCode",
        "pipelineRun",
        "pipelineVersion",
    },
    OperationScope.FILES_READ: {
        "getFileByPath",
        "readFileContent",
        "prepareObjectDownload",
    },
    OperationScope.FILES_WRITE: {
        "prepareObjectUpload",
        "createBucketFolder",
        "deleteBucketObject",
        "writeFileContent",
    },
    OperationScope.DATASETS_READ: {
        "dataset",
        "datasets",
        "datasetVersion",
        "datasetLink",
    },
    OperationScope.DATASETS_WRITE: {
        "createDataset",
        "updateDataset",
        "deleteDataset",
        "createDatasetVersion",
        "updateDatasetVersion",
        "deleteDatasetVersion",
        "createDatasetVersionFile",
        "deleteDatasetLink",
    },
    OperationScope.USER_READ: {"me", "workspace"},
}


SCOPE_PERMS: dict[Webapp.OperationScope, set[str]] = {
    OperationScope.PIPELINES_RUN: {
        "pipelines.run_pipeline",
        "pipelines.stop_pipeline",
    },
    OperationScope.PIPELINES_READ: {
        "pipelines.view_pipeline_version",
    },
    OperationScope.FILES_READ: {
        "files.download_object",
    },
    OperationScope.FILES_WRITE: {
        "files.create_object",
        "files.delete_object",
    },
    OperationScope.DATASETS_READ: set(),
    OperationScope.DATASETS_WRITE: {
        "datasets.create_dataset",
        "datasets.update_dataset",
        "datasets.delete_dataset",
        "datasets.create_dataset_version",
        "datasets.update_dataset_version",
        "datasets.delete_dataset_version",
        "datasets.create_dataset_version_file",
        "datasets.create_dataset_link",
        "datasets.update_dataset_link",
        "datasets.delete_dataset_link",
    },
    OperationScope.USER_READ: set(),
}


PERM_TO_SCOPE: dict[str, Webapp.OperationScope] = {
    perm: scope for scope, perms in SCOPE_PERMS.items() for perm in perms
}


def fields_allowed_by(scopes) -> set[str]:
    """Top-level GraphQL field names allowed for the given scope set."""
    return {f for scope in scopes if scope in SCOPE_FIELDS for f in SCOPE_FIELDS[scope]}


def scope_for_perm(perm: str) -> Webapp.OperationScope | None:
    """Return the scope a Django perm belongs to, or None if unmapped.

    Unmapped perms are denied for webapp principals — adding a new perm that
    should be reachable from a webapp means registering it here first.
    """
    return PERM_TO_SCOPE.get(perm)
