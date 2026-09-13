# HEXA-1793 — Template parameters for saved queries

## Context

A static web app can run a saved query today and, since part one of this ticket (#2074),
sort and page through its result with `orderBy`, `page` and the cursors. What it still
cannot do is filter: `executeSavedQuery` sends no values, so
`SELECT * FROM malaria_indicators;` always reads every district and every period.
The web app cannot work around this — the whole point of the `DATABASE_READ` scope is that
`savedQuery`/`savedQueryBySlug` are *not* allowlisted, so the app never holds the SQL and
cannot rewrite it (`backend/hexa/webapps/graphql_proxy.py:50-53`).

This part makes the stored SQL a **template** with **declared** parameters:

```sql
SELECT * FROM malaria_indicators WHERE district = ANY({{ districts }});
```

```
executeSavedQuery(input: { slug: "malaria-indicators", parameters: { districts: ["Dakar"] } })
```

Sorting and pagination stay where part one put them: the request wraps the rendered
statement, so a template never needs `ORDER BY`, `LIMIT` or `OFFSET` placeholders.

The saved query is trusted (a workspace member wrote it); the injected values are **not** —
they arrive from a web app's JavaScript. Avoiding SQL injection is the design's whole job.

Backend only. The Data Studio frontend gets its parameter form in a later ticket.

### Decisions taken

| Decision | Choice |
|---|---|
| Renderer | Slim in-house `templating.py` on Jinja2's `finalize` hook — **not** a vendored jinjasql |
| Control flow | `{% if %}`/`{% for %}` allowed (optional clauses such as `{% if districts %}`) |
| Sorting, paging | The request's `orderBy`/`page`/cursors, wrapping the rendered statement — **not** template parameters |
| Scope | `executeSavedQuery` only; `executeSQL` unchanged |
| Types | `STRING INTEGER FLOAT BOOLEAN DATE`, each optionally `multiple` |
| IN clauses | `= ANY({{ list }})` against a `multiple` parameter — **not** a jinjasql-style `inclause` filter |

`INTEGER` and `FLOAT` are split rather than folded into one `NUMBER`, mirroring how pipeline
parameters expose `int` and `float` (`backend/hexa/pipelines/graphql/schema.graphql:57`).
A single `NUMBER` would let `10.5` through to a clause that wants an integer — `period +
{{ days }}` on a date, say, where PostgreSQL rejects it ("operator does not exist: date +
numeric") — a `QUERY_ERROR` carrying a database message, where the caller deserves an
`INVALID_PARAMETERS` naming the parameter.

### Why IN clauses bind as arrays

`IN` is the one clause a scalar parameter cannot express, and it is the first thing a filtering
web app reaches for. A `multiple` parameter takes a JSON array, and the author writes:

```sql
WHERE district = ANY({{ districts }})
```

**This is not a workaround for `IN`; it is what `IN` already is.** PostgreSQL rewrites
`IN (list)` to `= ANY(array)` before planning — verified on the dev database, where both
spellings produce the identical plan node `Filter: (x = ANY ('{a,b,c}'::text[]))`, and `NOT IN`
likewise becomes `<> ALL`. psycopg2 adapts a Python list straight to a PostgreSQL array, so one
output node stays one placeholder and one bound value. `finalize` needs no special case at all,
and the count invariant below is untouched.

**Why not jinjasql's `inclause`** (`IN {{ ids | inclause }}`, which expands to `(%s, %s, %s)`):

- It binds *inside a filter*, so the filter must return placeholder text that `finalize` then
  has to recognise and not re-bind. That pass-through is exactly the `Markup` hatch this design
  removes by construction, reintroduced on day one to serve a feature `= ANY` gets for free.
- It raises `ValueError` on an empty sequence. Here that failure is unrecoverable by the caller:
  the web app never holds the SQL, so it cannot branch around a multi-select the user emptied.
  Every `IN` would need a hand-written `{% if %}` around it.
- Its syntax omits the parentheses, which reads like a mistake and means something else if you
  add them back.

**Why not a comma-separated string.** There is no escaping story: a district named
`Dakar, Rufisque` cannot be represented. The caller is JavaScript, which has arrays, and
`parameters` is already a `JSON` scalar, so a real list arrives natively. Joining and re-splitting
loses information to gain nothing.

The empty set is where the two approaches genuinely part, measured against a two-row table:

| spelling | empty list | negated, with a NULL in the list |
|---|---|---|
| expansion into `IN (...)` | syntax error | 0 rows, where 1 is correct |
| `= ANY` / `<> ALL` | 0 rows, correct | correct |

That second column is the standard SQL NULL trap, and nothing inside `finalize` can see that it
sits underneath a `NOT`. An author who writes `IN ({{ districts }})` out of habit gets a loud
`operator does not exist: text = text[]` from PostgreSQL, not a silently empty result.

**Why not vendor jinjasql.** Its `SqlExtension.filter_stream` rewrites the token stream to
append `| bind` to every output node, because jinjasql *infers* parameters from whatever the
template references. We declare them, so all of that inference is dead weight. Jinja's own
`finalize` hook already fires on exactly the output nodes and nowhere else, which gives the
same semantics in ~20 lines: `{{ min_cases }}` becomes a placeholder plus a bound value,
while `{% if min_cases > 10 %}` still sees the real integer.

More importantly, jinjasql's `bind` starts with `if isinstance(value, markupsafe.Markup):
return value`, and its environment sets `autoescape = True`. That pass-through exists to serve
`sqlsafe` — the filter we are removing. Vendoring ships the raw-injection hatch on day one,
disabled by convention (a deleted filter registration) rather than by construction, and
anything that later produces `Markup` silently regains it. Our own renderer omits the hatch
entirely.

### Designing for snippets (not built here)

Reusable SQL fragments are a stock-Jinja concern: `{% include %}` / `{% import %}` resolved by
a custom `jinja2.BaseLoader` backed by a snippet model. Two properties make that land cleanly
on this design, and both are free:

- An included template compiles in the *same* environment, so a snippet's own `{{ }}` outputs
  get bound exactly like the parent's.
- `{% include %}` output never passes through `finalize` at all — it goes straight to the
  stream. A snippet's static SQL text is therefore emitted verbatim with **no escape hatch**.

Only macro-style snippets (a fragment taking arguments) touch the binding layer, because
`{{ where_district(d) }}` *is* an output node. That is the one case that would need the
`Markup` pass-through, and it can be added deliberately, with tests naming it as the trust
boundary, if and when it is needed.

So today: build the environment through a factory that already accepts a `loader`, keep
variable discovery behind one function so it can later walk the include graph, keep the param
collector per-render rather than thread-local, and **reject `{% include %}` / `{% import %}` at
save time** so the syntax stays reserved behind a clear error.

Rejecting explicitly, rather than letting the render fail on its own: with `loader=None` Jinja
raises `TypeError("no loader for this environment specified")`, not `TemplateNotFound` — an
error that reads like a bug in OpenHEXA rather than an unsupported feature, and one that only
appears when the query is *run*. `meta.find_referenced_templates(ast)` names both constructs
at parse time, so validation catches them where the author can still see them.

---

## How it works

Rendering never puts a value into SQL text. It emits a placeholder and collects the value:

```
content:   SELECT * FROM t WHERE d = {{ d }} AND p >= {{ p }}
                                         ── templating.py, driver-neutral ──
render  →  SELECT * FROM t WHERE d = <TOKEN> AND p >= <TOKEN>   + values ['x', date]
                                         ──────── the seam ────────
escape  →  literal % doubled to %%   (only when there are values)
swap    →  SELECT * FROM t WHERE d = %s AND p >= %s      as a PreparedQuery, params attached
                                         ── databases/, psycopg2-specific ──
wrap    →  SELECT * FROM (...) AS q ORDER BY ... LIMIT %s   (only when the request sorts or pages)
execute →  cursor.execute(sql, ['x', date, 51])   ← psycopg2 binds; values are never SQL
```

**Rendering stops at the token.** `templating.py` hands back SQL that still carries its own
placeholder, and a separate function in the databases layer turns that into whatever the driver
wants. The two steps below the seam are psycopg2 facts, not SQL facts, and the file that decides
whether a value can become SQL is the one to keep free of them. See "Portability" at the end for
what this buys.

The `%`-doubling step is not optional *for psycopg2*: the moment it receives params it
`%`-formats the whole string, so an existing `WHERE name LIKE '%foo%'` would break. The token is
`__hexa_bind_<random hex>__` — word characters only, so doubling cannot touch it, and freshly
generated per render so it cannot be written literally into a template.

`to_psycopg2` goes through `PreparedQuery.from_text` on the rendered SQL, so single-statement
enforcement and `sanitize_sql` apply exactly as today, and what comes out is the same
`PreparedQuery` part one's `paginate_offset`/`paginate_cursor` wrap — their own placeholders
land after the template's, in order. One wrinkle: the token is regenerated per render, so a
cursor cannot be fingerprinted on the rendered text. `pagination.statement_text` fingerprints
the `%s` form plus the bound values instead, so the same values keep a cursor valid and other
values refuse it.

### Worked example

What a workspace member actually saves. Verified end to end against the dev database with a
prototype of this design, including the rendered SQL, the bound values and the log line.

```sql
SELECT district, period, cases
FROM malaria_indicators
WHERE district = ANY({{ districts }})
  AND period >= {{ start_date }}
```

```json
[
  { "name": "districts",  "type": "STRING", "multiple": true, "required": true },
  { "name": "start_date", "type": "DATE",   "default": "2026-01-01" }
]
```

The web app then calls, knowing only the slug and the parameter names, and sorts and pages
with the arguments part one added:

```graphql
executeSavedQuery(input: {
  slug: "malaria-by-district"
  parameters: { districts: ["Dakar", "Thiès"] }
  orderBy: [{ column: "period", direction: DESC }]
  perPage: 50
})
```

which renders to `WHERE district = ANY(%s) AND period >= %s` bound to
`[['Dakar', 'Thiès'], date(2026, 1, 1)]`, then wrapped in `SELECT * FROM (...) AS q ORDER BY
"period" DESC LIMIT %s`. `QueryLog.query` holds the stored template, and `QueryLog.parameters`
holds the bound values beside it:

```json
{"districts": ["Dakar", "Thiès"], "start_date": "2026-01-01"}
```

`start_date` was never sent, so it fell back to its default. Sending `districts: []` returns
zero rows rather than failing, and swapping `= ANY` for `<> ALL` turns the same parameter into
an exclusion list that correctly returns everything when empty.

---

## Implementation

### 1. `backend/hexa/data_studio/templating.py` (new, ~150 lines)

The whole feature's trust boundary. Exports:

- `build_environment(loader=None, finalize=None) -> SandboxedEnvironment` — the factory.
  `undefined=StrictUndefined`, `autoescape=False`, `loader` threaded through for snippets.
  **Clear `env.globals`** (`range`, `dict`, `lipsum`, `cycler`, `joiner`, `namespace`): this is
  not about bounding work — the sandbox already swaps `range` for `safe_range`, capped at
  100 000 — but about save-time validation. `meta.find_undeclared_variables` skips any name that
  is in `environment.globals`, so with globals intact `{{ range(3) }}` and `{{ lipsum() }}` are
  invisible to the undeclared-variable check. Cleared, they surface as undeclared and are
  rejected on save, which keeps "every output node comes from a declared parameter" true.
- `collect_template_variables(content) -> set[str]` — `meta.find_undeclared_variables(env.parse(content))`.
  Single function so snippets can later union in `meta.find_referenced_templates`.
- `validate_saved_query_template(content, parameters) -> list[dict]` — raises
  `InvalidTemplateError` / `InvalidParametersError`, and **returns the normalized spec** for the
  caller to store (see below). Called on save (§4).
- `render_saved_query(saved_query, values) -> RenderedQuery(sql, params, token, values)`.
  `sql` still carries `token` wherever a value belongs; converting it to a driver's placeholder
  is somebody else's job (§2). Returning the token rather than a bare `%s` is what keeps this
  module driver-neutral, and `token` is a field rather than a private detail precisely so the
  converter does not have to guess or re-derive it.
  `values` is the same set keyed by name, defaults resolved, for the audit entry.
  **Returns `saved_query.content` untouched when the query declares no parameters** — every
  query that exists today takes byte-for-byte its current path.
- `InvalidTemplateError`, `InvalidParametersError`, `TemplateRenderError`.

The binding hook:

```python
@pass_context                     # <- load-bearing, see below
def finalize(_ctx, value):
    if isinstance(value, Undefined):
        # StrictUndefined only raises when something stringifies it, and returning
        # the token means nothing ever does.
        value._fail_with_undefined_error()
    params.append(value)
    return token
```

`@pass_context` is what stops Jinja's optimiser from constant-folding output nodes at *compile*
time (`CodeGenerator._get_finalize` only precomputes a `const` for a finalize that needs no
context). Without it, placeholder order and value order drift apart. Worth a comment saying so
— it is the kind of line someone "simplifies" away.

**The `Undefined` guard is equally load-bearing, and less obvious.** Jinja passes the raw
`Undefined` object to `finalize` *before* stringifying it, so a hook that returns a token short-
circuits the only step that would have raised. Verified against jinja2 3.1.6: `{{ ''.__class__ }}`,
`{{ x.__class__ }}` and `{{ x.foo }}` all render "successfully" and append a `StrictUndefined`
to `params` — the failure then surfaces from psycopg2 as `can't adapt type 'StrictUndefined'`,
logged as `ERROR` and returned as `QUERY_ERROR`. Both `StrictUndefined` and the sandbox's own
refusals travel this way: the sandbox marks a blocked attribute access by returning an
`Undefined` whose `_fail_with_undefined_error` raises `SecurityError`, so this one line restores
both. Without it, `undefined=StrictUndefined` and `SandboxedEnvironment` are decoration.

**Render-time invariant.** After rendering, assert `sql.count(token) == len(params)` and raise
`TemplateRenderError` otherwise. Jinja has constructs that bind a value without emitting a
placeholder into the final text: `{% set s %}{{ x }}{% endset %}` collects `x`, then re-binds
the captured token *as a string* when `{{ s }}` is output (verified: two params, one placeholder).
Left unchecked that reaches psycopg2 as "not all arguments converted", and the check also
guarantees a token can never travel inside a bound value.

`params` is a per-call list closed over by `finalize`, so the environment is built per render.
Compilation of a short statement is cheap and it keeps renders trivially thread-safe.

**Error mapping on render.** Catch `jinja2.TemplateError` and re-raise as `TemplateRenderError`:
it is the common base of `UndefinedError`, `TemplateSyntaxError` and `SecurityError` (a
`TemplateRuntimeError`). Note that `SecurityError` is inherently a *render*-time verdict —
`env.parse("{{ ''.__class__ }}")` succeeds, so save-time validation cannot pre-empt it.

**Parameter spec validation** (on save): names match `^[a-zA-Z_][a-zA-Z0-9_]*$` and are unique;
`type` is one of the five; `multiple`, if given, is a boolean; `default`, if given, satisfies
its own type (a list when `multiple`);
`meta.find_referenced_templates` must yield nothing (`{% include %}`/`{% import %}` are not
supported yet — see the snippets section). Every variable `collect_template_variables` finds
must be declared — an undeclared one is an error, which is what stops a template from silently
executing a literal `{{ foo }}`. Declared-but-unused is allowed (the frontend form may want a
parameter before the SQL uses it).

**Normalization.** The validator returns the spec with every optional key filled in
(`multiple=False`, `required=False`, `default=None`, `help=""`, `type` upper-cased), and §4
stores *that*. The
GraphQL type declares `required: Boolean!` but the input leaves it optional, and the field is
resolved straight off the JSONField by the default dict resolver — so a spec stored without the
key makes every later read of that saved query fail on a null non-null field. Normalizing on the
way in is what keeps the stored document and the schema's non-null promises in agreement.

**List coercion** (`multiple`): the value must be a JSON array — a bare scalar is rejected
rather than wrapped, on the same "no guessing" grounds as the numeric strings below. Each
element is coerced by the declared `type`, so a `multiple` `INTEGER` rejects `["1"]`. Nested
arrays are rejected. **An empty array is valid** and is the case the whole design is chosen for:
it binds as an empty PostgreSQL array, which matches no rows under `= ANY` and every row under
`<> ALL`, with no syntax error either way. `required` still means "the caller must send it", so
an author who wants "unset means all districts" leaves it optional and writes
`{% if districts %}`; an empty list is falsy in Jinja, so the same guard covers both.

**Value coercion** (on execute): reject unknown names rather than ignoring them — that is how a
web app finds its typo. Missing + required + no default → error; missing + optional → default,
else `None`. `INTEGER` and `FLOAT` must both exclude `bool` explicitly (`isinstance(True, int)`
is `True` in Python); `INTEGER` also rejects every `float`, `10.0` included, since a value
written as a decimal is a caller who meant something else. `FLOAT` accepts an `int`. `DATE`
parses ISO `YYYY-MM-DD` via `date.fromisoformat`; psycopg2 adapts `date` natively. Reject
numeric strings for both numeric types — guessing is how `LIMIT "10"` bugs happen.

Add `jinja2` to `backend/requirements.in` (today it is only transitive, via `moto` and
`openhexa-sdk` — `backend/requirements.txt:282`) and re-run
`pip-compile --no-emit-index-url requirements.in`.

### 2. `backend/hexa/databases/query_text.py` — `to_psycopg2(rendered)`

The seam, and the only place in the feature that knows what a psycopg2 placeholder looks like:

```python
def to_psycopg2(rendered: RenderedQuery) -> PreparedQuery:
    prepared = PreparedQuery.from_text(rendered.sql)   # sanitize + single statement
    if not rendered.params:
        return prepared                                 # params None: raw text, never %-formatted
    convert = lambda text: text.replace("%", "%%").replace(rendered.token, "%s")
    return replace(prepared, sql=convert(prepared.sql), body=convert(prepared.body),
                   params=list(rendered.params))
```

Order matters: double first, then swap, or the `%s` we just wrote gets doubled too. The token is
word characters only, so the doubling pass cannot damage it. `body` is converted too, because
that is what the pagination wrapper embeds; `PreparedQuery._inner` already knows not to
double a statement that carries `params`.

`run_saved_query` calls this between rendering and pagination. Nothing else in the codebase
should ever write `%s` for this feature.

### 3. `backend/hexa/data_studio/models.py` — `QueryLog.parameters`

```python
parameters = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
```

The values a templated query ran with, kept **beside** the statement rather than inlined into
it. `query` holds the stored text — the template, as part one logs the stored text rather than
the pagination wrapper — and `parameters` holds the bound values. Null means the query took no
parameters, which is every query written before this ticket.

This replaces an earlier design that reproduced psycopg2's client-side interpolation
(`interpolate_for_log`, a `_quoted` helper, a latin-1 encoding fix and an `ARRAY[...]`
reconstruction). That was a reconstruction of a statement which never existed in that form,
and its fidelity claims did not survive checking: against a live connection `cursor.mogrify`
renders a list as `'{Dakar,Thiès}'`, not `ARRAY['Dakar','Thiès']`, and a backslash-bearing
string carries an `E` prefix. Storing the values is exact, needs no per-driver work, and makes
them queryable across runs.

`DjangoJSONEncoder` is required: a coerced `DATE` arrives as a `date` object, which a plain
JSONField rejects. It stores as an ISO string.

`QueryLogAdmin.search_fields` gains `parameters`, so a bound value stays findable now that it
is not part of the SQL text — Django casts a JSONField to text for `icontains`. Nothing else
reads `QueryLog`: it is not exposed in GraphQL, and `readonly_fields` is computed from
`_meta.fields`, so the column appears in the admin detail view on its own.

Migration `0011_querylog_parameters.py` — plain `AddField`, no backfill.

### 4. `backend/hexa/data_studio/models.py`

- `parameters = models.JSONField(blank=True, default=list)` on `SavedQuery`.
- Call `validate_saved_query_template(self.content, self.parameters)` from
  `create_if_has_perm` and from `update_if_has_perm`, assigning its normalized return to
  `self.parameters` — in the latter on the content and spec the edit results in, so partial
  updates validate the resulting pair, and *before* the git repository is initialised or
  committed to, so a refused edit leaves no history behind. This mirrors how
  `PipelineVersion.validate_config_types` is invoked (`backend/hexa/pipelines/models.py:223`
  and `:506`) rather than going through `save()`, which would make fixtures and data migrations
  brittle.
- **Partial-update semantics**, since `resolve_update_saved_query` forwards the whole input as
  `**kwargs`: `parameters` omitted or `null` leaves the stored spec alone (as `content` does),
  and `[]` clears it. Say it in the docstring; a client that PATCHes only `name` must not drop
  the parameters.
- `save()` is untouched: `sanitize_sql` only rewrites non-ASCII and exotic whitespace, so
  `{{ }}` / `{% %}` pass through unharmed. Add a test pinning that.
- Add `parameters` to `SavedQueryAdmin.fields` (which lists fields explicitly, so the column is
  invisible until it does). No model-level `clean()`: validation stays on the two API paths, and
  an administrator editing the JSON by hand is trusted to get it right.

Migration `0012_savedquery_parameters.py` — plain `AddField`, no backfill, after part one's
`0010_savedquery_git_versioning`. (Note the app has hit parallel-numbered migrations twice
before, hence `0004_merge_…` and `0008_merge_…`.)

### 5. `backend/hexa/data_studio/graphql/schema.graphql`

```graphql
enum SavedQueryParameterType { STRING INTEGER FLOAT BOOLEAN DATE }

type SavedQueryParameter {
  name: String!
  type: SavedQueryParameterType!
  "When true the value is a JSON array of `type`, bound as a PostgreSQL array."
  multiple: Boolean!
  required: Boolean!
  default: Generic
  help: String
}
input SavedQueryParameterInput { ... }   # same shape, multiple/required/default/help optional
```

- `SavedQuery.parameters: [SavedQueryParameter!]!`
- `parameters: [SavedQueryParameterInput!]` on `CreateSavedQueryInput` / `UpdateSavedQueryInput`
- `INVALID_TEMPLATE`, `INVALID_PARAMETERS` on `CreateSavedQueryError` / `UpdateSavedQueryError`
- `ExecuteSavedQueryInput.parameters: JSON` — a name → value map
- `extend enum ExecuteSQLError { INVALID_PARAMETERS, TEMPLATE_ERROR }`, following how
  `SAVED_QUERY_NOT_FOUND` was already added

`Generic` and `JSON` are both declared in `backend/config/graphql/schema.graphql`. Neither has a
`ScalarType` binding anywhere in `hexa/` or `config/`, so values pass through untouched in both
directions — which is what makes them usable here, and worth knowing before anyone goes looking
for the parser that coerces them (there is none; §1 does that job).

`required: Boolean!` on the type against an optional `required` on the input is deliberate, and
only safe because §4 stores the normalized spec.

### 6. Execution path

`backend/hexa/databases/utils.py` — no change: since part one `execute_database_query` takes
a `PreparedQuery` and runs `cursor.execute(prepared.sql, prepared.params)`. `params` stays
`None` (not `[]`) for a statement without values, which is what keeps psycopg2 from
`%`-formatting it.

`backend/hexa/data_studio/query_runner.py`:

- `_execute_and_log(..., parameters=None)` and `log_rejected_query(..., parameters=None)`
  store the values on the entry, so every outcome records the stored text plus the values it
  ran with. Pass the **bound** values (`RenderedQuery.values`, after defaults are filled in),
  not the caller's raw input, or a default-supplied value is invisible in the audit — except
  on a `REJECTED` entry written before binding succeeded, which keeps what the caller sent.
  On `REJECTED`, `error_message` names the offending parameter and its expected type; it must
  not echo the rejected value, which is attacker-controlled text landing in an audit field
  people read.
- `run_saved_query(request, saved_query, *, order_by, per_page, ..., parameters=None)`:
  1. `ensure_can_run_query(...)` **first**, on `saved_query.content`. Its docstring already
     invites this ("so a caller can enforce it *before* reserving anything" — the CSV export
     does the same). This keeps a caller lacking `databases.run_query` from learning anything
     about parameters, and cannot double-log: the first check raises.
  2. `render_saved_query(...)`; on `InvalidParametersError`/`TemplateRenderError`, write a
     `REJECTED` `QueryLog` via `log_rejected_query` so a bad call still leaves a trail — the
     same `except` that already handles `MultipleStatementsError` and `PaginationError`.
  3. `prepared = to_psycopg2(rendered)` — the seam, crossed exactly once.
  4. `build_page_request(prepared, ...)` and `_wrap(...)` exactly as for a plain statement;
     the cursor fingerprint comes from `pagination.statement_text(prepared)`.

`backend/hexa/data_studio/schema.py` — pass `query_input.get("parameters")` into
`run_saved_query`; map the two new exceptions onto the two new enum values with
`error_message`. `resolve_create_saved_query` / `resolve_update_saved_query` map
`InvalidTemplateError` / `InvalidParametersError` likewise.

### 7. No change: `backend/hexa/webapps/graphql_proxy.py`

`executeSavedQuery` is already the sole `DATABASE_READ` field and the proxy allowlists top-level
field *names* only — it never inspects arguments or `variables`, so `parameters` flows through
as-is. That is by design and is exactly why `ensure_can_run_query` hard-blocks web apps from
`executeSQL` at the resolver layer (`query_runner.py:62-75`). Add tests asserting both halves
still hold.

### 8. Docs (both languages — CLAUDE.md)

`docs/en/static-webapps.md` and `docs/fr/static-webapps.md`, `DATABASE_READ` section (line 978
EN / line 670 FR): updated schema block, `parameters` in the example, and a short "Query
templating" note. Three things users will hit and should read first:

- A column name can never be a bind parameter. `ORDER BY {{ sort }}` renders `ORDER BY %s`,
  which sorts by a constant and silently does nothing. Sorting and paging are the request's
  `orderBy`, `perPage`, `page` and cursors, which apply to a template like to any query, so
  `ORDER BY`, `LIMIT` and `OFFSET` stay out of the template altogether.
- `WHERE name LIKE '{{ q }}%'` is wrong — the placeholder must not sit inside a quoted literal.
  Use `LIKE {{ q }}` and put the `%` in the value.
- A web app cannot discover a query's parameters: `savedQuery`/`savedQueryBySlug` stay off the
  `DATABASE_READ` allowlist, so names and types travel out of band, the same way the slug
  already does. One sentence next to the existing "find the slug in the Data Studio" paragraph.
- Filtering on a list of values is `= ANY({{ districts }})`, and excluding one is
  `<> ALL({{ districts }})`. Say plainly that this *is* `IN`, since an author who knows SQL will
  otherwise read it as a quirk: PostgreSQL compiles the two to the same thing, and `= ANY` is
  the spelling that accepts a parameter. Note that an empty list is allowed and simply matches
  nothing, so a web app never has to special-case an emptied multi-select. `IN ({{ districts }})`
  is the mistake to name explicitly, with the error PostgreSQL returns for it.

Use the worked example above as the docs example: it exercises a list and a date default in
one query, sorted and paged by the request, which is close to what a filtered table view
actually needs. Say that a cursor is tied to the parameter values it was cut with.

`backend/hexa/data_studio/README.md` — a "Query templating" section, after "Bounding runaway
work": the trust boundary (template trusted, values not), why `sqlsafe` and the `Markup`
pass-through are deliberately absent, why `finalize` must fail on `Undefined` itself, and the
snippets seam.

---

## Tests

`backend/hexa/data_studio/tests/` — `SavedQueryTestMixin.create_saved_query` (`testutils.py`)
needs a `parameters=` passthrough.

**`test_templating.py`** (new, pure unit, no DB) is where the security case is made:

- `WHERE id = {{ id }}` → `WHERE id = %s` + `[10]`; no parameters → content returned
  byte-identical, with `params` `None`.
- Injection: `name = "1; DROP TABLE users"` reaches psycopg2 as a *value*; rendered SQL holds
  one `%s` and the string never enters the text.
- `to_psycopg2` converts `body` too (what the pagination wrapper embeds), and a rendered text
  holding two statements still raises `MultipleStatementsError`.
- `%` survival: `WHERE name LIKE '%foo%' AND id = {{ id }}` comes out of `to_psycopg2` as
  `'%%foo%%'` with a single `%s`, and psycopg2 restores `'%foo%'` when it binds.
- Placeholder ordering with a repeated parameter and with a parameter inside a `{% for %}` —
  the regression `@pass_context` exists to prevent.
- `{% if %}` receives the real typed value, not a placeholder.
- Sandbox and undefined, all of which must surface as `TemplateRenderError` **from the renderer**,
  never as a psycopg2 error later: `{{ ''.__class__ }}`, `{{ x.__class__ }}`, and `{{ x.foo }}`
  on a string `x`. Assert the exception type, and assert nothing was appended to `params` — a
  test that only checks "it failed" passes against the bug this guards.
- `{{ x | safe }}` still binds its value. The filter hands `finalize` a `Markup`, and psycopg2
  adapts that as a plain string, so it is harmless — but the whole case against vendoring
  jinjasql rests on there being no `Markup` pass-through, and that claim deserves a test.
- Count invariant: `{% set s %}{{ x }}{% endset %}{{ s }}` raises `TemplateRenderError` rather
  than reaching psycopg2 with two values for one placeholder.
- The seam: `render_saved_query` output contains the token and **no `%s`**, and `to_psycopg2` is
  what introduces one. Pin the ordering too — `LIKE '%foo%'` plus one parameter must come out as
  `'%%foo%%'` with a single `%s`, not as a doubled placeholder.
- `range` and `lipsum` are gone from globals, and `{{ range(3) }}` is therefore rejected on save
  as an undeclared variable; no `sqlsafe` filter exists.
- Coercion: `True` rejected for `INTEGER` and for `FLOAT`; `10.5` and `10.0` rejected for
  `INTEGER`; `10` accepted for `FLOAT`; `"10"` rejected for both; unknown name rejected;
  required-and-missing rejected; optional falls back to default then `None`; ISO date parsed.
- Save-time: undeclared variable rejected, duplicate names rejected, bad default rejected,
  syntax error → `InvalidTemplateError`, `{% include 'x' %}` and `{% import 'm' as m %}`
  → `InvalidTemplateError`.
- Normalization: a `{name, type}` spec comes back with `multiple`, `required`, `default` and
  `help` filled in.
- `multiple`: a list binds as one placeholder and one list value, not as expanded placeholders;
  elements are coerced by the declared type (`["1"]` rejected for `INTEGER`); a bare scalar is
  rejected; a nested array is rejected; **an empty list is accepted** and reaches psycopg2 as an
  empty list rather than raising.
- `= ANY` and `<> ALL` against a real database, empty list included, asserting the row counts —
  the empty case is the reason for the design and the one a unit test cannot express.

**`test_schema.py`** — create/update with parameters, the two new error enums, `executeSavedQuery`
with values, unknown parameter → `INVALID_PARAMETERS`, missing required → `INVALID_PARAMETERS`.
A template sorted and paged by number with a total; a cursor walk over a template, pinning that
the per-render token does not invalidate the cursor and that other values do; a `LIKE '%a%'`
beside a value surviving the pagination wrapper (no double `%`-doubling).
Plus one specifically for the Ariadne trap: **a parameter named `minDate` must survive
`convert_names_case=True`** (`backend/config/schema.py:138`). Ariadne's case conversion works
off input-object field names and should not recurse into a custom scalar, but a camelCase
parameter name silently arriving as `min_date` would fail rendering, so pin it.

**`test_schema.py`** also pins the normalized spec end to end: create with a minimal
`{name, type}` parameter, then read every field of `SavedQuery.parameters` back through
GraphQL. Without normalization that query errors on a null `required` and a null `multiple`.

**`test_models.py`** — `sanitize_sql` leaves `{{ }}`/`{% %}` intact; validation fires on both
create and partial update; an update that omits `parameters` leaves the stored spec alone and
`[]` clears it.

**`test_query_runner.py` / existing runner tests** — on `SUCCESS` and on `ERROR`,
`QueryLog.query` holds the stored text and `QueryLog.parameters` the bound values, defaults
included, with an accented value and a `€` surviving the round trip; a parameter-less run
leaves `parameters` null; a render failure writes `REJECTED` with what the caller sent; a
permission failure writes `DENIED` *before* rendering is attempted.

**`backend/hexa/webapps/tests/test_graphql_proxy.py`** — a `DATABASE_READ` webapp can pass
`parameters`; it still cannot reach `executeSQL`.

---

## Verification

```bash
docker network create openhexa            # first time only
docker compose run app test hexa.data_studio --settings=config.settings.test
docker compose run app test hexa.webapps  --settings=config.settings.test
docker compose run app makemigrations --check --dry-run
pre-commit run --all
```

Frontend schema snapshot (backend CI diffs it against `main`, see
`.github/workflows/backend-ci.yml:34`):

```bash
cd frontend && npm run codegen     # refreshes schema.generated.graphql
```

End-to-end, against a real workspace database:

1. `docker compose up`, log in as `root@openhexa.org` / `root`.
2. In Data Studio, save a query with `SELECT * FROM <table> WHERE id >= {{ min_id }}` and
   declare `min_id` as `INTEGER` (via the GraphQL playground at
   http://localhost:8000/graphql/ — the Data Studio form comes in the later ticket).
3. Run `executeSavedQuery` with `parameters: { min_id: 2 }`; vary it and confirm the rows
   move. Add `orderBy: [{ column: "id", direction: DESC }], perPage: 2`, then page on with
   `after: endCursor` and the same parameters; send other parameters with that cursor and
   confirm `INVALID_CURSOR`.
4. Send `{ min_id: "1; DROP TABLE x" }` and confirm `INVALID_PARAMETERS` — the value is
   rejected at coercion, before it ever reaches rendering. Same for `{ min_id: 2.5 }`.
5. Check the Django admin's `QueryLog` for the run: `query` reads the stored template and
   `parameters` holds `{"min_id": 2}`. Repeat with a `STRING` parameter holding an accented
   value, confirm `parameters` kept it, and search the admin changelist for that value to
   confirm `search_fields` still finds the entry.
6. Confirm an existing parameter-less saved query still runs unchanged, including one
   containing `LIKE '%…%'`.
7. Save the worked example above, then run it with two districts, with one, and with `[]`.
   Confirm the row counts move and that the empty list returns zero rows without an error.
   Check `QueryLog.parameters` holds `{"districts": ["Dakar", "Thiès"], ...}`, accents intact,
   and that `start_date` shows the default `"2026-01-01"` it was never sent.

## Portability (why the seam exists)

The likely next backend is DuckDB over tabular files rather than a workspace PostgreSQL. This
was tested against DuckDB 1.5.5, not assumed, and the split above is what the results argue for.

Ports unchanged: the whole of `templating.py`. Also, importantly, the IN-clause decision —
`= ANY(?)` and `<> ALL(?)` take a bound list in DuckDB with **identical** empty-list semantics
(no rows, then every row). A jinjasql-style `inclause` would have needed its expansion redone per
dialect, so the choice made above is the portable one. `IN (?)` fails loudly there too, and
`PreparedQuery`'s single-statement rule still earns its place: DuckDB executed `SELECT 1; SELECT 2`
and returned the second result.

Does not port, all of it below the seam:

- `%s` is a *parser error* in DuckDB, which wants `?` or `$1`. One new converter beside
  `to_psycopg2`, and nothing else moves.
- **The `%`-doubling would corrupt data.** It pre-compensates for psycopg2 formatting the string
  client-side and un-doubling as it goes; DuckDB binds inside the engine and never un-doubles, so
  a literal `'50%'` written as `'50%%'` stays `'50%%'`. Verified on both. This is the single
  strongest reason not to leave the step buried inside the renderer, where a port would carry it
  over by reflex.
The audit trail ports unchanged too, now that `QueryLog` stores the bound values rather than a
reconstruction of the interpolated statement — DuckDB offers no `mogrify` and does no
client-side interpolation, so "the statement as sent" does not exist there at all.

One thing genuinely changes the security argument, and no seam fixes it. This design rests on a
bound value being unable to change *what* a query reads, only which rows come back. That holds on
PostgreSQL, where `FROM %s` is a syntax error. It fails on DuckDB, where `read_csv_auto(?)`
accepts a bound path — a file outside the intended directory was read through a bind parameter in
testing. A query author writing `FROM read_csv_auto({{ path }})` would hand a web app arbitrary
file read. Templating cannot prevent it, since the template is trusted by construction, so a
DuckDB backend needs a path allowlist or a filesystem restriction as a separate control, decided
before the first templated file query ships.

## Out of scope, worth stating

- The Data Studio editor cannot run a templated query — `executeSQL` takes no parameters, so
  pressing Run on a template fails. Same for the CSV export, which posts raw SQL
  (`views.download_query_csv`). Both belong to the frontend ticket.
- No identifier filter, so a column or table name still cannot be parameterised; sorting is
  the request's `orderBy`, not the template's.
- Parameter declarations are not versioned: the git history of a saved query holds
  `query.sql` only, so editing the spec records nothing. Deliberate: the history exists for
  a changelog and an easy rollback of the SQL, not to execute a specific version, and
  carrying the spec alongside would add complexity for little gain. A rolled-back template
  that disagrees with the current spec is refused at save time, never run silently.
- No snippets, no `sqlsafe`, and no jinjasql-style `inclause` (see the IN-clause section).
