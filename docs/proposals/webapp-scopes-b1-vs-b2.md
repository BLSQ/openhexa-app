# Web app scopes: where the allowlist lives (B1 vs B2)

Context: the web app GraphQL proxy used to check only the **names of top-level
fields** (`me`, `workspace`, `pipeline`, ...). A web app could therefore go past
its scopes by:

1. wrapping fields in an inline fragment at the root (`... on Query { ... }`),
2. naming a fragment after an allowed field (`query { ...me } fragment me on Query { ... }`),
3. following links between objects (`workspace { connections { fields { value } } }`,
   `pipeline { workspace { database { credentials } } }`).

The fix replaces that check with a **field-level allowlist**: every field in
the query is checked against the type it is selected on (`Type.field`). Anything
not listed is refused. A graphql-core validation rule walks the whole document,
so fragments, aliases and nesting are all covered by the same check.

B1 and B2 share that rule and that policy. **They differ only in where the
allowlist is written.**

## Before: only top-level names were checked

Each scope listed the root fields it allowed, and nothing else:

```python
SCOPE_FIELDS = {
    Webapp.OperationScope.USER_READ: {"me", "workspace"},
    Webapp.OperationScope.FILES_READ: {"getFileByPath", "readFileContent", "prepareObjectDownload"},
    ...
}
```

The proxy collected the names directly under `query { }` / `mutation { }`,
removed the allowed ones, and returned 403 if any were left. Otherwise it ran
the whole query. The same query as in the next section, with USER_READ +
FILES_READ:

```graphql
query {
  workspace(slug: "w") {          # "workspace" in USER_READ's list → ✅  (the only check)
    name                          # not checked
    bucket {                      # not checked (FILES_READ wasn't even needed)
      objects {                   # not checked
        items { name }            # not checked
      }
    }
    connections { name }          # not checked → returned in the response
  }
}
# → 200, with the connections included
```

The short list was misleading: it named the **entry points**, but a web app
could read **everything reachable from them**. For USER_READ:

| | Before | Now |
|---|---|---|
| Written in the code | 2 names (`me`, `workspace`) | 36 `Type.field` entries |
| Actually reachable | 74 types, 462 fields | 9 types, 36 fields |
| `Workspace` fields | All 26, including `connections`, `database`, `bucket`, `savedQueries`, `members`, `invitations` | 8: `slug`, `name`, `description`, `countries`, `organization`, `createdAt`, `updatedAt`, `createdBy` |

That's without the fragment bypasses, which opened the entire schema whatever
the scopes.

## Now: every field is checked (shared by B1 and B2)

Each field in the query is one lookup: "is `field` allowed on `Type` for this
web app's scopes?". Example with USER_READ + FILES_READ:

```graphql
query {
  workspace(slug: "w") {          # Query.workspace       → USER_READ  ✅
    name                          # Workspace.name        → USER_READ  ✅
    bucket {                      # Workspace.bucket      → FILES_READ ✅
      objects {                   # Bucket.objects        → FILES_READ ✅
        items { name }            # BucketObjectPage.items, BucketObject.name ✅
      }
    }
    connections { name }          # Workspace.connections → not listed ❌ → 403
  }
}
```

Traversal is cut at the **edges**: `Pipeline.workspace` is in no scope, so
nothing behind it can be reached from a pipeline.

```graphql
pipeline(id: "x") {     # Query.pipeline     ✅ (PIPELINES_READ)
  workspace {           # Pipeline.workspace ❌ not in any scope → stops here
    database { credentials { password } }
  }
}
```

## B1: a Python map next to the proxy (implemented)

The allowlist is one dictionary in `backend/hexa/webapps/scopes.py`, keyed by
scope, then by GraphQL type:

```python
SCOPE_FIELDS: dict[str, FieldMap] = {
    Scope.FILES_READ: _merge(
        _BUCKET_OBJECT,                          # shared building block
        {
            "Query": {"getFileByPath", "readFileContent"},
            "Mutation": {"prepareObjectDownload"},
            "Workspace": {"bucket"},             # the edge only opens with FILES_READ
            "Bucket": {"object", "objects"},
            "BucketObjectPage": {"items", "pageNumber", "hasNextPage", "hasPreviousPage"},
            "ReadFileContentResult": {"success", "errors", "content", "size"},
            "PrepareObjectDownloadResult": {"success", "errors", "downloadUrl"},
        },
    ),
    ...
}
```

The rule looks the field up by its parent type:

```python
class ScopeRule(ValidationRule):
    def enter_field(self, node: FieldNode, *_):
        parent = self.context.get_parent_type()
        if parent is None or not policy.allows(parent.name, node.name.value):
            result.denied.add(f"{parent.name if parent else '?'}.{node.name.value}")
```

Field groups used by several scopes (`_USER`, `_BUCKET_OBJECT`, `_PIPELINE_RUN`,
`_DATASET`) are written once and merged in.

## B2: directives in the schema files (alternative)

Each field declares, in the schema file of the app that owns it, which scopes
may select it:

```graphql
# hexa/webapps/graphql/schema.graphql
directive @webappScope(scopes: [WebappOperationScope!]!) on FIELD_DEFINITION

# hexa/pipelines/graphql/schema.graphql
extend type Query {
  pipeline(id: UUID!): Pipeline @webappScope(scopes: [PIPELINES_READ])
  pipelines(workspaceSlug: String, ...): PipelinesPage! @webappScope(scopes: [PIPELINES_READ])
}
extend type Mutation {
  runPipeline(input: RunPipelineInput): RunPipelineResult! @webappScope(scopes: [PIPELINES_RUN])
}
type Pipeline {
  id: UUID! @webappScope(scopes: [PIPELINES_READ, PIPELINES_RUN])
  name: String @webappScope(scopes: [PIPELINES_READ, PIPELINES_RUN])
  workspace: Workspace!          # no directive, so web apps can't follow it
  ...
}

# hexa/files/graphql/schema.graphql
extend type Workspace {
  bucket: Bucket! @webappScope(scopes: [FILES_READ])
}
```

The rule reads the directive from the field definition instead of looking it
up in a dict:

```python
def enter_field(self, node, *_):
    field_def = self.context.get_field_def()
    if not policy.allows(webapp_scopes_of(field_def)):   # reads field_def.ast_node.directives
        self.report_error(...)
```

## Comparison

| | B1: dict next to the proxy | B2: directives in the schema files |
|---|---|---|
| Size of the change | One file | About 10 `.graphql` files, roughly 100–150 annotations (the same entries as the dict, spread out) |
| Reviewing it as a security PR | Easy: the whole surface is in one place | Harder: scattered across apps |
| Drift from the schema | Possible, so it needs the schema-drift test (in place) | Not possible: the annotation is on the field |
| A new field added later | Hidden until someone edits the dict | Hidden until someone annotates it; the decision is visible in the PR that adds the field |
| Reusing groups of fields | Yes (`_USER`, `_BUCKET_OBJECT`, ...) | No: every field repeats its scope list |
| Generating docs or a reduced schema | Possible | Natural fit |
| Dependencies | The proxy knows every app's types | Each app declares its own exposure |

Both deny by default: a field nobody listed or annotated is out of reach of
web apps.

## Public web apps

Public web apps will probably want a **reduced schema** that anonymous
developers can introspect, showing only what a web app can actually call. B2
fits that better, because the schema files already carry the information
needed to build it.

The field allowlist covers only part of what public web apps need. They will
also need:

- **a principal with no user behind it**: today every resolver relies on the
  real user's membership;
- **grants per resource**: e.g. only *these* saved queries or *this* folder.
  A field allowlist can't restrict arguments;
- **abuse limits**: query depth and cost, rate limiting.

## Recommendation

**B1 now, B2 if and when public web apps need it.** The rule and the policy are
identical in both, so moving to B2 later means turning the dict into
annotations, which is a mechanical change. The schema-drift test and the
documented-example test stay valid in both options.

## Known limitation (both options)

The check looks at the parent type, not the full path. An allowed field is
therefore allowed wherever its type appears. This is why no scope grants an
edge that leads to a *different* workspace: `Pipeline.workspace`,
`Dataset.workspace` and `DatasetLink.workspace` are all refused. With
`Dataset.workspace` allowed, a shared dataset led to its source workspace, and
`Workspace.datasets` there listed every dataset linked into it (that resolver
doesn't check the user, so the same leak exists in the main API and is fixed
separately). As long as `Workspace` is only reachable through `Query.workspace`,
which the row filter limits to the web app's own workspace, path checking isn't
needed.
