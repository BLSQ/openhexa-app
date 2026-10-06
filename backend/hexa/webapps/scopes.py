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
# would reach connections, credentials and files its scopes don't cover.
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

# For each scope, the fields a web app may select, keyed by their parent type.
# Anything not listed is refused, so a new schema field stays out of reach of
# web apps until it is added here.
SCOPE_FIELDS: dict[str, FieldMap] = {
    Scope.USER_READ: _merge(
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
            },
            "Country": {"code", "alpha3", "name", "flag"},
            "Organization": {"id", "name", "shortName"},
        },
    ),
    Scope.PIPELINES_READ: _merge(
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
            "Pipeline": {
                "id",
                "code",
                "name",
                "description",
                "schedule",
                "type",
                "currentVersion",
            },
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
    Scope.PIPELINES_RUN: _merge(
        _PIPELINE_RUN,
        {
            "Mutation": {"runPipeline", "stopPipeline"},
            "RunPipelineResult": {"success", "errors", "run"},
            "StopPipelineResult": {"success", "errors"},
        },
    ),
    Scope.FILES_READ: _merge(
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
    Scope.FILES_WRITE: _merge(
        _BUCKET_OBJECT,
        {
            "Mutation": {
                "prepareObjectUpload",
                "createBucketFolder",
                "writeFileContent",
            },
            "PrepareObjectUploadResult": {"success", "errors", "uploadUrl", "headers"},
            "CreateBucketFolderResult": {"success", "errors", "folder"},
            "WriteFileContentResult": {"success", "errors", "filePath", "size"},
        },
    ),
    Scope.DATASETS_READ: _merge(
        _USER,
        _DATASET,
        {
            "Query": {"dataset", "datasets", "datasetVersion", "datasetLink"},
            "DatasetPage": _PAGE,
            "DatasetVersionPage": _PAGE,
            "DatasetVersionFilePage": _PAGE,
            "DatasetLinkPage": _PAGE,
            # `workspace` names the workspace a shared dataset comes from; only
            # its identity is readable through this scope.
            "Dataset": {"createdBy", "workspace", "versions", "latestVersion", "links"},
            "DatasetVersion": {"createdBy", "dataset", "files", "fileByName"},
            "DatasetVersionFile": {"downloadUrl"},
            "DatasetLink": {"id", "dataset", "workspace", "createdAt"},
            "Workspace": {"slug", "name", "datasets"},
        },
    ),
    Scope.DATASETS_WRITE: _merge(
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
    # Only the execution endpoint: `savedQuery`, `savedQueryBySlug` and
    # `Workspace.savedQueries` return the SQL body, and the point of this scope is
    # to run a vetted query without handing the web app the query itself.
    Scope.DATABASE_READ: {
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
}


@dataclass
class ScopeCheck:
    operations: set[str] = field(default_factory=set)
    """Root fields the document selects."""
    denied: set[str] = field(default_factory=set)
    """`Type.field` for every selection outside the scopes."""


class WebappScopePolicy:
    """The schema fields a web app may select, given its scopes.

    The check walks the whole document against the schema, so a field is judged
    by the type it is selected on however it is reached: nested, aliased, or
    through inline or named fragments.
    """

    def __init__(self, scopes: Iterable[str]):
        self._allowed = _merge(*(SCOPE_FIELDS[s] for s in scopes if s in SCOPE_FIELDS))

    def allows(self, type_name: str, field_name: str) -> bool:
        if field_name.startswith("__") or type_name.startswith("__"):
            return True
        return field_name in self._allowed.get(type_name, ())

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
