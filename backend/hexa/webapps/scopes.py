from collections.abc import Iterable
from dataclasses import dataclass, field

from graphql import (
    DocumentNode,
    FieldNode,
    GraphQLCompositeType,
    ValidationRule,
    validate,
)

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
_TAG = {"Tag": {"id", "name"}}
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
            "run_id",
            "code",
            "config",
            "messages",
            "logs",
            "hasErrorMessages",
            "timeout",
            "enableDebugLogs",
            "sendMailNotifications",
            "user",
            "stoppedBy",
            "pipeline",
            "datasetVersions",
        },
        "PipelineRunMessage": {"message", "priority", "timestamp"},
        "GenericOutput": {"name", "type", "uri"},
        # Table metadata only: `rows` and `sample` would read the table's content.
        "DatabaseTable": {"name", "count", "columns"},
        "TableColumn": {"name", "type"},
    },
)
_DATASET = {
    "Dataset": {
        "id",
        "slug",
        "name",
        "description",
        "createdAt",
        "updatedAt",
        "attributes",
        "targetId",
    },
    "DatasetVersion": {
        "id",
        "name",
        "description",
        "changelog",
        "createdAt",
        "attributes",
        "targetId",
    },
    "DatasetVersionFile": {
        "id",
        "filename",
        "contentType",
        "size",
        "createdAt",
        "rows",
        "columns",
        "properties",
        "attributes",
        "targetId",
    },
    "DatasetLink": {"id", "dataset", "createdAt", "isPinned"},
    "MetadataAttribute": {
        "id",
        "key",
        "label",
        "value",
        "system",
        "createdAt",
        "updatedAt",
        "createdBy",
        "updatedBy",
    },
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
            _TAG,
            {
                "Query": {"me", "workspace", "countries", "country", "boundaries"},
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
                    "permissions",
                    "tags",
                    "pipelineTags",
                    "webappsEnabled",
                },
                # Resolved through `has_perm`, so they reflect what the web app itself
                # may do, not only the viewer's role.
                "WorkspacePermissions": {
                    "update",
                    "delete",
                    "manageMembers",
                    "manageTags",
                    "createConnection",
                    "launchNotebookServer",
                    "deleteDatabaseTable",
                    "generateToken",
                    "createSavedQuery",
                    "createDataset",
                    "createObject",
                    "deleteObject",
                    "downloadObject",
                    "createPipelineTemplateVersion",
                    "createPipeline",
                },
                # Only the viewer's own membership, not its links to other objects.
                "WorkspaceMembership": {"id", "role", "createdAt", "updatedAt"},
                "Country": {"code", "alpha3", "name", "flag", "whoInfo"},
                "WHOInfo": {"region", "defaultCRS", "simplifiedExtent"},
                "WHORegion": {"code", "name"},
                "WHOBoundary": {
                    "id",
                    "name",
                    "country",
                    "administrative_level",
                    "parent",
                    "extent",
                },
                "Organization": {"id", "name", "shortName", "type", "url", "logo"},
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
            _USER,
            _TAG,
            _PIPELINE_RUN,
            {
                "Query": {
                    "pipeline",
                    "pipelines",
                    "pipelineByCode",
                    "pipelineRun",
                    "pipelineVersion",
                    # Reads a bucket file without FILES_READ, but only the file and
                    # column the pipeline's own code sets for a parameter.
                    "pipelineParameterChoices",
                },
                "PipelinesPage": _PAGE,
                "PipelineRunPage": _PAGE,
                "PipelineVersionPage": _PAGE,
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
                    "versions",
                    "scheduledPipelineVersion",
                    "config",
                    "tags",
                    "notebookPath",
                    "webhookEnabled",
                    "autoUpdateFromTemplate",
                    "hasNewTemplateVersions",
                },
                # Resolved through `has_perm`, so they tell whether the web app itself
                # (viewer's role and the web app's scopes) may act on the pipeline.
                "PipelinePermissions": {
                    "run",
                    "stopPipeline",
                    "update",
                    "delete",
                    "schedule",
                    "createVersion",
                    "createTemplateVersion",
                },
                "CreateTemplateVersionPermission": {"isAllowed", "reasons"},
                "PipelineRun": {"version"},
                "PipelineVersion": {
                    "id",
                    "versionNumber",
                    "versionName",
                    "description",
                    "createdAt",
                    "isLatestVersion",
                    "parameters",
                    "name",
                    "number",
                    "user",
                    "pipeline",
                    "timeout",
                    "config",
                    "externalLink",
                    "permissions",
                    "missingScheduleParameters",
                },
                "PipelineVersionPermissions": {"update", "delete"},
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
                    "connection",
                    "choicesFromFile",
                    "disables",
                    "disableWhen",
                },
                "PipelineParameterChoicesFromFile": {"path", "format", "column"},
                "Workspace": {"pipelineLastRunStatuses"},
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
                "Bucket": {"name", "object", "objects"},
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
                "Query": {
                    "dataset",
                    "datasets",
                    "datasetVersion",
                    "datasetLink",
                    # Shortcuts to objects the entry points above already reach.
                    "datasetLinkBySlug",
                    "datasetVersionFile",
                },
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
                    "version",
                    "latestVersion",
                    "links",
                    "sharedWithOrganization",
                    "permissions",
                },
                "DatasetVersion": {
                    "createdBy",
                    "dataset",
                    "files",
                    "fileByName",
                    "permissions",
                },
                "DatasetVersionFile": {"downloadUrl", "fileSample", "createdBy"},
                "DatasetFileSample": {"sample", "status", "statusReason"},
                "DatasetLink": {"createdBy", "permissions"},
                # Resolved through `has_perm`, like `PipelinePermissions`.
                "DatasetPermissions": {"update", "delete", "createVersion"},
                "DatasetVersionPermissions": {"update", "delete", "download"},
                "DatasetLinkPermissions": {"delete", "pin"},
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
                "CreateDatasetResult": {"success", "errors", "dataset", "link"},
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
                "pageInfo",
                "durationMs",
            },
            "QueryResultPageInfo": {
                "hasNextPage",
                "hasPreviousPage",
                "pageNumber",
                "startCursor",
                "endCursor",
                "totalItems",
                "totalPages",
            },
        },
        permissions=frozenset({"databases.run_query"}),
    ),
}


def ungrantable_fields(denied: Iterable[str]) -> set[str]:
    """The `denied` fields that no scope grants, so enabling scopes cannot fix them."""
    return {
        type_field
        for type_field in denied
        if not any(
            type_field.partition(".")[2]
            in grant.fields.get(type_field.partition(".")[0], ())
            for grant in SCOPE_GRANTS.values()
        )
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
        self._scopes = frozenset(scopes)
        grants = [SCOPE_GRANTS[s] for s in self._scopes if s in SCOPE_GRANTS]
        self._allowed = _merge(*(grant.fields for grant in grants))
        self._permissions = frozenset().union(*(grant.permissions for grant in grants))

    def allows(self, type_name: str, field_name: str) -> bool:
        if field_name.startswith("__") or type_name.startswith("__"):
            return True
        return field_name in self._allowed.get(type_name, ())

    def allows_permission(self, perm: str) -> bool:
        return perm in self._permissions

    def missing_scopes(self, denied: Iterable[str]) -> set[str]:
        """Scopes, not enabled yet, that would grant the `denied` fields.

        Shared fields such as `User.email` are granted by several scopes, so the
        scopes are picked greedily to suggest a small set rather than all of them.
        """
        coverage = {
            scope: {
                type_field
                for type_field in denied
                if type_field.partition(".")[2]
                in grant.fields.get(type_field.partition(".")[0], ())
            }
            for scope, grant in SCOPE_GRANTS.items()
            if scope not in self._scopes
        }
        uncovered = set().union(*coverage.values())
        missing = set()
        while uncovered:
            best = max(sorted(coverage), key=lambda s: len(coverage[s] & uncovered))
            missing.add(best)
            uncovered -= coverage[best]
        return missing

    def check(self, document: DocumentNode) -> ScopeCheck:
        """We use graphql-core's validator as a typed tree walker: it visits
        every field of the document (fragments, inline fragments and aliases)
        while tracking which schema type each field is selected on.
        The outcome is collected in `result` and the return value of `validate` is ignored.
        Regular schema validation still happens later, when the request is executed.
        """
        result = ScopeCheck()
        validate(schema, document, [self._rule(result)])
        return result

    def _rule(self, result: ScopeCheck) -> type[ValidationRule]:
        """`validate` instantiates rules with only a ValidationContext,
        so the policy and the result are passed through here.
        """
        policy = self

        class ScopeRule(ValidationRule):
            def enter_field(self, node: FieldNode, *_):
                policy._check_field(
                    self.context.get_parent_type(), node.name.value, result
                )

        return ScopeRule

    def _check_field(
        self, parent: GraphQLCompositeType | None, field_name: str, result: ScopeCheck
    ) -> None:
        root_types = (schema.query_type, schema.mutation_type)
        if parent in root_types and not field_name.startswith("__"):
            result.operations.add(field_name)
        # No parent type means the selection doesn't match the schema;
        # refuse it rather than let it through unchecked.
        if parent is None:
            result.denied.add(f"?.{field_name}")
        elif not self.allows(parent.name, field_name):
            result.denied.add(f"{parent.name}.{field_name}")
