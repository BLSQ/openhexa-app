from collections.abc import Iterable
from dataclasses import dataclass, field

from graphql import DocumentNode, FieldNode, ValidationRule, validate

from config.schema import schema
from hexa.webapps.models import Webapp

Scope = Webapp.OperationScope
FieldMap = dict[str, set[str]]


def _merge(*maps: FieldMap) -> FieldMap:
    merged: FieldMap = {}
    for field_map in maps:
        for type_name, fields in field_map.items():
            merged.setdefault(type_name, set()).update(fields)
    return merged


# Building blocks shared by several scopes. Edges back up to `Workspace` (e.g.
# `Pipeline.workspace`) are deliberately absent: following them is how a web app
# would reach connections, credentials and files out of its scope.
_USER = {
    "User": {
        "id",
        "email",
        "firstName",
        "lastName",
        "displayName",
        "language",
        "avatar",
    },
    "Avatar": {"initials", "color"},
}
_BUCKET_OBJECT = {
    "BucketObject": {"key", "name", "path", "size", "updatedAt", "type"},
}
_PIPELINE_RUN = _merge(
    _BUCKET_OBJECT,
    {
        "PipelineRun": {
            "id",
            "status",
            "progress",
            "executionDate",
            "duration",
            "outputs",
            "triggerMode",
        },
        "GenericOutput": {"name", "type", "uri"},
        # Only the name: `rows` and `sample` would read the database.
        "DatabaseTable": {"name"},
    },
)
_DATASET = {
    "Dataset": {"id", "slug", "name", "description", "createdAt", "updatedAt"},
    "DatasetVersion": {"id", "name", "description", "changelog", "createdAt"},
    "DatasetVersionFile": {"id", "filename", "contentType", "size", "createdAt"},
}
_PAGE = {"items", "pageNumber", "totalPages", "totalItems"}


@dataclass(frozen=True)
class ScopeGrant:
    fields: FieldMap
    permissions: frozenset[str] = frozenset()


# For each scope, the fields a web app may select (keyed by their parent type)
# and the permissions it may use. Anything not listed is refused. A new schema
# field or permission stays out of reach of web apps until it is added here.
SCOPE_GRANTS: dict[str, ScopeGrant] = {
    Scope.USER_READ: ScopeGrant(
        fields=_merge(
            _USER,
            {
                "Query": {"me", "workspace"},
                "Me": {"user", "features", "permissions"},
                "FeatureFlag": {"code", "config"},
                "MePermissions": {
                    "adminPanel",
                    "createAccessmodProject",
                    "createTeam",
                    "manageAccessmodAccessRequests",
                    "superUser",
                },
                "Workspace": {
                    "slug",
                    "name",
                    "description",
                    "countries",
                    "organization",
                    "createdAt",
                    "updatedAt",
                    "createdBy",
                    "currentMembership",
                },
                # Only the viewer's own role, not the membership's other links.
                "WorkspaceMembership": {"role"},
                "Country": {"code", "alpha3", "name", "flag"},
                "Organization": {"id", "name", "shortName"},
            },
        ),
        # Read by the `me.permissions` flags; no AccessMod mutation is reachable.
        permissions=frozenset(
            {
                "connector_accessmod.create_project",
                "connector_accessmod.manage_access_requests",
            }
        ),
    ),
    Scope.PIPELINES_READ: ScopeGrant(
        fields=_merge(
            _PIPELINE_RUN,
            {
                "Query": {
                    "pipeline",
                    "pipelines",
                    "pipelineByCode",
                    "pipelineRun",
                    "pipelineVersion",
                },
                "PipelinesPage": _PAGE,
                "PipelineRunPage": _PAGE,
                "Pipeline": {
                    "id",
                    "code",
                    "name",
                    "description",
                    "schedule",
                    "type",
                    "functionalType",
                    "createdAt",
                    "updatedAt",
                    "currentVersion",
                    "runs",
                    "permissions",
                },
                # Resolved through `has_perm`, so they tell whether the web app itself
                # (viewer's role and the web app's scopes) may run or stop the pipeline.
                "PipelinePermissions": {"run", "stopPipeline"},
                "PipelineRun": {"version"},
                "PipelineVersion": {
                    "id",
                    "versionNumber",
                    "versionName",
                    "description",
                    "createdAt",
                    "isLatestVersion",
                    "parameters",
                },
                "PipelineParameter": {
                    "code",
                    "name",
                    "type",
                    "help",
                    "default",
                    "choices",
                    "multiple",
                    "required",
                    "widget",
                    "directory",
                },
            },
        ),
        permissions=frozenset({"pipelines.view_pipeline_version"}),
    ),
    Scope.PIPELINES_RUN: ScopeGrant(
        fields=_merge(
            _PIPELINE_RUN,
            {
                "Mutation": {"runPipeline", "stopPipeline"},
                "RunPipelineResult": {"success", "errors", "run"},
                "StopPipelineResult": {"success", "errors"},
            },
        ),
        permissions=frozenset({"pipelines.run_pipeline", "pipelines.stop_pipeline"}),
    ),
    Scope.FILES_READ: ScopeGrant(
        fields=_merge(
            _BUCKET_OBJECT,
            {
                "Query": {"getFileByPath", "readFileContent"},
                "Mutation": {"prepareObjectDownload"},
                "Workspace": {"bucket"},
                "Bucket": {"object", "objects"},
                "BucketObjectPage": {
                    "items",
                    "pageNumber",
                    "hasNextPage",
                    "hasPreviousPage",
                },
                "ReadFileContentResult": {"success", "errors", "content", "size"},
                "PrepareObjectDownloadResult": {"success", "errors", "downloadUrl"},
            },
        ),
        permissions=frozenset({"files.download_object"}),
    ),
    Scope.FILES_WRITE: ScopeGrant(
        fields=_merge(
            _BUCKET_OBJECT,
            {
                "Mutation": {
                    "prepareObjectUpload",
                    "createBucketFolder",
                    "writeFileContent",
                },
                "PrepareObjectUploadResult": {
                    "success",
                    "errors",
                    "uploadUrl",
                    "headers",
                },
                "CreateBucketFolderResult": {"success", "errors", "folder"},
                "WriteFileContentResult": {"success", "errors", "filePath", "size"},
            },
        ),
        permissions=frozenset({"files.create_object"}),
    ),
    Scope.DATASETS_READ: ScopeGrant(
        fields=_merge(
            _USER,
            _DATASET,
            {
                "Query": {"dataset", "datasets", "datasetVersion", "datasetLink"},
                "DatasetPage": _PAGE,
                "DatasetVersionPage": _PAGE,
                "DatasetVersionFilePage": _PAGE,
                "DatasetLinkPage": _PAGE,
                # No `Dataset.workspace` or `DatasetLink.workspace`: for a shared
                # dataset they lead to another workspace, whose `datasets` would list
                # everything linked there.
                "Dataset": {
                    "createdBy",
                    "versions",
                    "latestVersion",
                    "links",
                    "sharedWithOrganization",
                },
                "DatasetVersion": {"createdBy", "dataset", "files", "fileByName"},
                "DatasetVersionFile": {"downloadUrl"},
                "DatasetLink": {"id", "dataset", "createdAt", "isPinned"},
                # Only reachable through `Query.workspace`, i.e. with USER_READ too.
                "Workspace": {"slug", "name", "datasets"},
            },
        ),
        permissions=frozenset({"datasets.download_dataset_version"}),
    ),
    Scope.DATASETS_WRITE: ScopeGrant(
        fields=_merge(
            _DATASET,
            {
                "Mutation": {
                    "createDataset",
                    "updateDataset",
                    "createDatasetVersion",
                    "updateDatasetVersion",
                    "createDatasetVersionFile",
                },
                "CreateDatasetResult": {"success", "errors", "dataset"},
                "UpdateDatasetResult": {"success", "errors", "dataset"},
                "CreateDatasetVersionResult": {"success", "errors", "version"},
                "UpdateDatasetVersionResult": {"success", "errors", "version"},
                "CreateDatasetVersionFileResult": {
                    "success",
                    "errors",
                    "file",
                    "uploadUrl",
                },
            },
        ),
        permissions=frozenset(
            {
                "datasets.create_dataset",
                "datasets.update_dataset",
                "datasets.create_dataset_version",
                "datasets.update_dataset_version",
                "datasets.create_dataset_version_file",
            }
        ),
    ),
    # Only the execution endpoint: `savedQuery`, `savedQueryBySlug` and
    # `Workspace.savedQueries` return the SQL body, and the point of this scope is
    # to run a vetted query without handing the web app the query itself.
    Scope.DATABASE_READ: ScopeGrant(
        fields={
            "Query": {"executeSavedQuery"},
            "ExecuteSQLResult": {
                "success",
                "errors",
                "errorMessage",
                "columns",
                "rows",
                "rowCount",
                "truncated",
                "durationMs",
            },
        },
        permissions=frozenset({"databases.run_query"}),
    ),
}


@dataclass
class ScopeCheck:
    operations: set[str] = field(default_factory=set)
    """Root fields the document selects."""
    denied: set[str] = field(default_factory=set)
    """`Type.field` for every selection outside the scopes."""


class WebappScopePolicy:
    """Policy to resolve the schema fields and permissions a web app can use,
    given its scopes.

    `check` walks the whole document against the schema, so a field is judged
    by the type it is selected on, non-matter how it is reached.
    """

    def __init__(self, scopes: Iterable[str]):
        grants = [SCOPE_GRANTS[s] for s in scopes if s in SCOPE_GRANTS]
        self._allowed = _merge(*(grant.fields for grant in grants))
        self._permissions = frozenset().union(*(grant.permissions for grant in grants))

    def allows(self, type_name: str, field_name: str) -> bool:
        if field_name.startswith("__") or type_name.startswith("__"):
            return True
        return field_name in self._allowed.get(type_name, ())

    def allows_permission(self, perm: str) -> bool:
        return perm in self._permissions

    def check(self, document: DocumentNode) -> ScopeCheck:
        result = ScopeCheck()
        validate(schema, document, [self._rule(result)])
        return result

    def _rule(self, result: ScopeCheck) -> type[ValidationRule]:
        policy = self
        root_types = {schema.query_type, schema.mutation_type}

        class ScopeRule(ValidationRule):
            def enter_field(self, node: FieldNode, *_):
                parent = self.context.get_parent_type()
                field_name = node.name.value
                if parent in root_types and not field_name.startswith("__"):
                    result.operations.add(field_name)
                # No parent type means the selection doesn't match the schema;
                # refuse it rather than let it through unchecked.
                if parent is None or not policy.allows(parent.name, field_name):
                    result.denied.add(f"{parent.name if parent else '?'}.{field_name}")

        return ScopeRule
