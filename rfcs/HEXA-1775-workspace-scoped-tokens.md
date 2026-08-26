# RFC — Workspace-scoped access tokens (HEXA-1775)

**Status:** draft, for discussion
**Owner:** @mrivar
**Branch:** `HEXA-1775-workspace-scoped-tokens`
**Last updated:** 2026-08-21

---

## 1. TL;DR

A workspace token today authenticates **the person**, not **the workspace**. Anyone
holding a token for workspace A acts with the full authority of its owner across every
workspace, dataset and pipeline that person can reach. We want a token to grant exactly
one workspace.

The recommendation in one paragraph: enforce scoping at a **single choke point** (the
principal object created by the auth middleware), give tokens a **first-class table** so
they can be named, listed, revoked and observed, and ship the behavioural change through
a **measured deprecation** — observe first, dry-run second, opt-in third, default fourth,
cutoff last. The happy accident that makes this tractable is that every token ever issued
was already issued *for a workspace*: migration is mostly "start enforcing what the token
already says", not "make everyone re-issue".

---

## 2. Where we are today

| Fact | Where |
| --- | --- |
| A token is `WorkspaceMembership.access_token` (a UUID), signed with Django's `Signer` | `workspaces/authentication.py:68` `MembershipToken` |
| Users with *implicit* access (superusers, org admins with no membership) get an `IdentityToken` — a signed dict with `user_id`, `workspace_id`, `issued_at`, expiring after `WORKSPACE_IDENTITY_TOKEN_EXPIRE_SECONDS` | `workspaces/authentication.py:85` |
| The middleware resolves the token and sets `request.user = token.user` — **the unscoped, full-authority user** | `workspaces/middlewares.py:26-30` |
| It also sets `request.workspace`, which **nothing reads** | `grep request.workspace` → 1 hit, the assignment itself |
| It sets `request.bypass_two_factor = True` | same |
| Tokens never expire (membership flavour), have no name, no `last_used_at`, and cannot be revoked individually — the only lever is regenerating the membership's `access_token`, which invalidates every copy of it everywhere | `workspaces/models.py` |
| Tokens are minted by `generateWorkspaceToken` (UI, per workspace) and `issueWorkspaceToken`, and by the notebooks view | `schema/mutations.py:455`, `:537`, `workspaces/views.py:78` |
| There is a `FIXME` in the middleware pointing at this ticket | `workspaces/middlewares.py:10` |

### Consumers of a workspace token

1. **CLI / SDK** — `openhexa workspaces add`, `openhexa pipelines push`, pipeline runtime.
2. **Notebooks** — the Jupyter launcher mints a token per (user, workspace) session.
3. **MCP server** — talks to the GraphQL API with a workspace token.
4. **Users' own automation** — CI jobs, cron, laptops. Invisible to us today.

### Threat model, stated plainly

- A token pasted into a CI variable, a Dockerfile, a Slack thread or a notebook shared
  with a colleague currently confers **the owner's entire account**: every workspace they
  are a member of, every organisation they administer, and — if the owner is a superuser
  — the whole instance.
- `bypass_two_factor` means a token also defeats 2FA for that account.
- We cannot answer "which tokens exist, who uses them, from where, and are any of them
  reaching outside their workspace?" There is no data.
- Because tokens are indefinite and shared per-membership, the incident response for a
  leak is "rotate and break every other integration that person had".

None of this is exotic; it is the standard reason every platform moved from account
tokens to scoped tokens.

---

## 3. What "scoped" has to mean (this is the subtle part)

Naïve reading: "the token may only touch rows whose `workspace_id` equals the token's
workspace." That is **wrong** and would break real features. The correct definition:

> A scoped token may reach exactly what a member of that workspace reaches **through that
> workspace** — no more, no less.

Concretely, in-scope even though the row's `workspace_id` differs:

- **Datasets shared organisation-wide.** `DatasetQuerySet.filter_for_user` admits
  `shared_with_organization=True` datasets whose workspace is in an org the user belongs
  to (`datasets/models.py:51`). A token scoped to workspace B *must* still see a dataset
  owned by workspace A when A shared it with the org and B is in that org — the scope is
  "what B can reach", and B can reach that dataset.
- **Linked datasets.** `DatasetLink` is precisely the mechanism for cross-workspace
  reach; scoping must respect links, not undo them.
- **The organisation itself**, as the boundary those shares are evaluated against — but
  only the org the scoped workspace belongs to.
- **Pipeline templates** created in other workspaces, to the extent a member of the
  scoped workspace can already see them.

Out of scope, always:

- Other workspaces (`Workspace.objects.filter_for_user` must return exactly one row).
- Memberships, connections, pipelines, webapps, saved queries of other workspaces.
- Any account-level mutation: profile, 2FA, org membership management, creating
  workspaces, accepting invitations.
- The superuser shortcut. A superuser's token must be no wider than anyone else's.

**Design consequence:** scoping is expressed as *narrowing the principal's reach*, not as
a filter on `workspace_id` bolted onto each queryset. The WIP branch gets this right by
applying `_scoped()` **after** every branch of `filter_for_user`, including the
`self.all()` shortcuts, and by making `Organization.filter_for_user` narrow via the
relation (`workspaces__id=user.workspace_id`) so org-shared reach survives.

---

## 4. Design

### 4.1 The principal is the choke point

```
Authorization: Bearer <token>
        │
        ▼
  middleware ──► WorkspaceToken.authenticate()  ──►  token (user, workspace)
        │
        ▼
  request.user = WorkspaceTokenUser.from_token(token)   ◄── the ONE change that
        │                                                    turns scoping on
        ├──► queryset layer:  filter_for_user() narrows to user.workspace_id
        ├──► permission layer: Workspace.has_role() returns False off-scope
        └──► guard layer:     has_perm() refuses objects outside the scope
```

Three layers, deliberately redundant (defence in depth), each cheap:

| Layer | Question it answers | Mechanism |
| --- | --- | --- |
| Visibility | "what rows exist for me?" | `WorkspaceQuerySet._scoped()` applied last, cascading through every `filter_for_user` that funnels through `Workspace.objects.filter_for_user` |
| Authority | "may I act on this row?" | `Workspace.get_membership()` returns `None` off-scope, so every `has_role()`-derived permission collapses to `False` |
| Guard | "did something reach an object out of band?" | `WorkspaceTokenUser.has_perm()` refuses objects whose workspace ≠ scope |

The `has_role()` refactor already in the branch matters more than it looks: it converts
~30 hand-rolled `workspacemembership_set.filter(user=…, role__in=[…]).exists()` calls
into one method. That single method is where scoping is enforced for the whole
permission layer. Before the refactor, scoping would have needed 30 correct edits and
would have regressed the first time someone wrote the 31st check by hand.

**Design principles this leans on, named honestly:**

- **Single responsibility / DRY at the choke point.** One place decides "what can this
  principal reach". Everything else asks.
- **Open/closed.** `WorkspaceToken` is already an ABC with `MembershipToken` /
  `IdentityToken` strategies; a new scoped token format arrives as a *new subclass*, not
  as edits to `authenticate()`'s branching. (The dispatch in `authenticate()` should
  become a registry lookup rather than an `if/elif` chain — see 4.4.)
- **Liskov.** `WorkspaceTokenUser` is a `User` proxy: every call site that takes a `User`
  keeps working, it just sees less. This is what lets us turn scoping on without touching
  resolvers. It is the *decorator* pattern wearing a Django proxy model.
- **Fail closed.** `WorkspaceQuerySet.filter_for_user` raising `NotImplementedError` for
  unknown principal types (already in the branch) is the right instinct: a new principal
  class cannot silently inherit "sees everything".

### 4.2 Critique of the current WIP

Things to keep:

- `WorkspaceScopedPrincipal` as the marker, with `ServicePrincipal` inheriting from it —
  correct hierarchy: "not a person" and "confined to one workspace" were conflated, and
  the split makes `WebappUser` and a token principal express different things cleanly.
- `_scoped()` applied after the branches. Post-filtering is what makes the superuser
  shortcut safe.
- The superuser carve-out in `BaseQuerySet._filter_for_user_and_query_object`.
- The scoping test matrix (`test_visibility_scoping.py`) — an executable invariant over
  an explicit `SCOPED_MODELS` list, run twice (member and superuser holder). This is the
  single highest-value artefact on the branch.

Things to fix before merge:

1. **`WorkspaceTokenUser.workspace = None` as a class attribute** mutated per instance is
   fragile — a missed `from_token()` yields a principal whose `workspace_id` raises
   `AttributeError` on `None`. Make the scope a required constructor argument, or have
   `workspace_id` raise a domain error with a clear message.
2. **`base.py` now imports `user_management_models` for an `isinstance` check.** The core
   layer knowing about a specific principal class is a layering inversion. Prefer asking
   the principal (`getattr(user, "workspace_id", None) is not None`, or better a
   `is_scoped` property on `UserInterface`) so `core` depends on the interface, not the
   implementation.
3. **The `authenticate()` `if/elif` on payload shape** will not survive a third token
   format. Introduce an explicit `version`/`type` discriminator on every payload plus a
   registry, and treat "unknown type" as invalid.
4. **`SCOPED_MODELS` is hand-maintained.** Add a guard test that enumerates models with a
   `filter_for_user` and fails when one is neither in `SCOPED_MODELS` nor in an explicit
   `INTENTIONALLY_UNSCOPED` list. Otherwise the matrix silently stops being a matrix.
6. **`bypass_two_factor`** should be reconsidered for scoped tokens; at minimum it must
   not let a token perform account-level mutations (2FA settings, email change).
6. **Nothing yet touches the middleware.** Wire-up is one line and should land behind the
   flag described in §5 rather than as a bare behavioural change.

### 4.3 First-class token records

`WorkspaceMembership.access_token` cannot support this change. It gives one token per
member per workspace, no name, no usage record, and revocation that breaks every copy.
Proposal — a new model (`workspaces/models.py`):

```
WorkspaceAccessToken
  id            uuid pk
  workspace     FK  → Workspace          (the scope, immutable)
  user          FK  → User               (the identity it acts as)
  name          str                      "CI — nightly refresh"
  prefix        str  indexed             first 8 chars, shown in UI, searchable in logs
  token_hash    str                      sha256; the secret is shown once, never stored
  scope_version int                      1 = legacy/unscoped, 2 = workspace-scoped
  created_at    dt
  created_by    FK  → User               (may differ from `user`? see open questions)
  expires_at    dt   null                optional, default null for now
  last_used_at  dt   null                updated at most once per N minutes
  last_used_ip  str  null
  revoked_at    dt   null
  revoked_by    FK  → User null
```

Notes:

- **Store a hash, not the token.** Today the secret is recoverable from the DB
  (`access_token` is the secret). Hashing means a DB dump is not a token dump.
- **Prefix the string** (`ohx_ws_…`) so GitHub/GitLab secret scanning can detect leaks
  and so support can identify a token from a log line without seeing the secret.
- **`scope_version` on the record**, not inferred from the payload shape, is what makes
  the rollout in §5 measurable and reversible per token.
- Keep `MembershipToken` working, unchanged, for the whole grandfather period. New model
  and old field coexist; the old field is dropped only after cutoff.
- `IdentityToken` (notebooks, implicit access) stays as-is: short-lived and already
  workspace-bound. It becomes scoped simply by producing a `WorkspaceTokenUser`.

### 4.4 Error semantics — the biggest lever on support load

When a scoped token is used out of scope, the current architecture answers with
`WORKSPACE_NOT_FOUND` / an empty list / a bare `PERMISSION_DENIED`. To a user that reads
as "the platform lost my workspace" or "my permissions were removed", and it generates a
ticket. We should return a **distinct, specific signal**:

- A GraphQL error code such as `TOKEN_SCOPE_EXCEEDED`, with the token's workspace slug in
  the message: *"This token is scoped to workspace `malaria-2026` and cannot access
  `tb-surveillance`. Create a token for that workspace in Account settings → Tokens."*
- The SDK/CLI surfaces that message verbatim and links to the doc page.
- Every such event is logged with the token prefix, so the org admin report in §5 can
  show "3 tokens hit scope errors this week".

**It must not carry `extensions.code = "UNAUTHENTICATED"`.** The CLI collapses any error
with that code into `InvalidTokenError` (`cli/api.py:213-215`), so the user would be told
their token is invalid and would regenerate it — the wrong fix, applied confidently. Any
other error is passed through as `GraphQLError(data["errors"])`, so the message text does
reach the terminal (as a raw list, until a CLI release prettifies it).

Security note: leaking "this exists but you can't have it" is acceptable here because the
token holder already knows their own workspace list; we are not disclosing anything they
could not learn with their own login. The alternative — silent emptiness — trades a small
information-disclosure gain for a large usability and support cost.

---

## 5. Migration and rollout

Design goal: **no user learns about this from a broken pipeline.** Each phase has an
entry gate, an exit gate, and a rollback.

### Phase 0 — Instrument (no behaviour change)

- Land the `WorkspaceAccessToken` table and backfill one record per existing
  `WorkspaceMembership.access_token` with `scope_version = 1`.
- Record `last_used_at` / IP / user agent on every token-authenticated request.
- Add a **shadow evaluation**: on every token request, compute whether a *scoped*
  principal would have produced a different result, and log
  `{token_prefix, workspace, graphql_operation, would_deny: bool}`. Cheap version: log
  the operation name plus the workspace slugs appearing in the variables/response, and
  flag any that differ from the token's workspace.
- **Exit gate:** two weeks of data. We can then answer, per organisation: how many tokens
  are live, how many are used at all, and how many ever act outside their workspace.

This phase is non-negotiable. Every estimate of "how much will this break" is currently a
guess, and the fix is two weeks of logging.

### Phase 1 — Dry-run enforcement

- Wire the middleware to build a `WorkspaceTokenUser`, but behind a setting with three
  states: `off` / `log` / `enforce`. Default `log`.
- In `log` mode the request proceeds unscoped, and every would-be denial is recorded and
  attributed.
- **Exit gate:** the would-deny rate is understood and each remaining pattern has an
  owner: either it is legitimate (fix the scope semantics — probably org-shared datasets)
  or it is a user integration that needs migrating (contact them).

### Phase 2 — Scoped tokens available, opt-in

- Account settings → Tokens: create a **named** token for a workspace. New tokens are
  `scope_version = 2` (enforced). Existing tokens display as *Legacy — full account
  access* with a "Replace with a scoped token" action.
- CLI/SDK: a version that understands the new prefix and prints a warning when it detects
  a legacy token. Publish the minimum SDK version.
- Docs + changelog + a short migration guide with copy-paste steps.
- **Exit gate:** the create/rotate/revoke flow works, docs are live, SDK released.

### Phase 3 — Scoped by default

- `generateWorkspaceToken` mints `scope_version = 2`. Legacy tokens still work.
- In-app: a banner for users holding legacy tokens *that were used in the last 30 days*
  (do not nag people whose tokens are dormant — nag them at revocation time instead).
- Org admin view: "Tokens in this organisation" — holder, workspace, last used, scoped or
  legacy. This is what lets an admin drive their own migration instead of waiting for us.
- **Exit gate:** legacy-token usage is trending down and the remaining holders are known
  by name.

### Phase 4 — Nudge, with dates

- Email the holders of legacy tokens *in use*, with the token name, workspace, last-used
  date and the cutoff date.
- Two announced **brownouts**: on day X and day Y, legacy tokens are enforced for one
  hour. Mechanically this is nearly free: `Feature` / `FeatureFlag`
  (`user_management/models.py:840-865`) already exists, and `force_activate` is a global
  switch editable in Django admin — no deploy, no restart. Two caveats:
  `has_feature_flag` is an uncached query per call, so memoise it before putting it in the
  auth path; and a boolean cannot express `off/log/enforce`, so prefer a small model with
  a mode plus an `enforce_from`/`enforce_until` window, which also makes brownouts
  self-driving. There is no scheduler in `config/settings/base.py`, so a timed flip means
  a CronJob or a person. Brownouts convert "I ignored the email" into a survivable 60-minute incident
  instead of a surprise outage on cutoff day. (Do them outside the timezones where our
  users run nightly pipelines — check the run schedule data before picking a slot.)
- **Exit gate:** brownouts produce no unexplained failures.

### Phase 5 — Cutoff

- All tokens enforce their scope. Crucially, **legacy tokens are not rejected — they are
  scoped**: a `MembershipToken` already names its workspace, so cutoff means it starts
  behaving as a token for that workspace rather than dying. A user whose usage was
  single-workspace (expected to be the large majority) notices nothing at all.
- Only genuinely cross-workspace automation needs one token per workspace, which the CLI
  config already models per workspace.
- Provide a **per-organisation grace extension** an admin can request once, expiring on a
  hard date, so a single unlucky team cannot hold the platform.
- Afterwards: drop `WorkspaceMembership.access_token`, remove the flag, delete the
  dry-run code.

### Rollback

Every phase up to and including 5 is one setting away from `off`. That is the point of
putting enforcement in the principal rather than in the resolvers: there is exactly one
switch.

---

## 6. Product / UX view

**Who is affected, and how they find out — in order of preference:**

1. They read the changelog. (Few.)
2. They see the token list in Account settings marked "Legacy — full account access".
3. They get a banner because a token of theirs was used recently.
4. Their org admin tells them, from the org token report.
5. They get an email with the cutoff date.
6. A brownout fails a run, with an error message that names the problem and the fix.
7. Cutoff day. (Nobody should reach here.)

**What the token UI must show** (some of this exists after HEXA-1754): name, workspace,
scoped/legacy badge, created date, **last used**, and revoke. "Last used" is what lets a
user delete tokens fearlessly, and fearless deletion is the whole security benefit.

**The one-token-per-workspace friction.** The honest cost of this change: a user
automating three workspaces now needs three tokens. Mitigations, in order: the CLI
already stores tokens per workspace; make creating a token 2 clicks from the workspace
page as well as from account settings; allow creating several tokens at once for the
workspaces you pick; and never silently invalidate — creating a new token must not kill
the old one (which today it does, and which is itself a bug worth fixing early).

**Positive framing, because there is a real user benefit.** This is not only a tax.
Scoped, named, revocable tokens with last-used dates mean: you can give a token to a
collaborator or a CI job without handing over your account; you can rotate one
integration without breaking the others; an admin can see and revoke what exists. Say
that in the changelog, not just "tokens are now restricted".

---

## 7. Risk register

| # | Risk | Likelihood | Impact | Mitigation | Detection |
| --- | --- | --- | --- | --- | --- |
| 1 | Cross-workspace automation breaks at cutoff | Medium | High | Phase 0 data identifies exactly who; direct contact; brownouts | Shadow logs; scope-error metric |
| 2 | Org-shared / linked datasets accidentally cut off by over-eager scoping | **High** (easy mistake) | High | "Reach, not rows" semantics (§3). There is a live caller: `workspace.get_dataset(…, source_workspace_slug=…)` resolves `datasetLinkBySlug` against the *source* workspace (`datasets/schema/queries.py:72-78`). The scoping fixture currently builds only a *private* link in the other workspace (`testutils.py:154`), so nothing protects this path yet — add an org-shared dataset plus its link, asserted still visible | `test_visibility_scoping.py` asserts both presence and absence |
| 3 | Notebooks break | Low | High | Notebook tokens are already per (user, workspace); assert in tests | Notebook launch smoke test |
| 4 | MCP server breaks | Medium | Medium | Audit which operations it calls; it may enumerate workspaces | Shadow logs filtered by user agent |
| 5 | Internal support/ops scripts using superuser tokens break | Medium | Medium | Superuser scoping is intentional; provide a separate, audited admin path instead of a wide token | Ask the support team in Phase 1 |
| 6 | A permission check bypasses `has_role()` and stays unscoped | Medium | High | Guard layer (`has_perm` refusal) catches it; grep for remaining `workspacemembership_set.filter` after the refactor; lint rule | Add a test that no non-test file outside the choke point queries `workspacemembership_set` with a role |
| 7 | New model added later without scoping | High over time | Medium | `SCOPED_MODELS` guard test (§4.2 item 4) | CI |
| 8 | Users hoard tokens because deletion feels risky | Medium | Low | last-used column; revoke with undo window | Token count per user |
| 9 | Rollout stalls at "legacy still in use" forever | Medium | Medium | Announced dates + brownouts + one-shot grace extension | Legacy usage dashboard |
| 10 | Scoping regresses the frontend (which authenticates by session, not token) | Low | High | Scoping keys off the *principal*, and session users are never `WorkspaceScopedPrincipal` | Existing test suite |

---

## 8. Open questions

1. ~~**Do we know the SDK/CLI's actual query set?**~~ **Answered** — checked against
   `openhexa-sdk-python` (2026-08-25). See §11 for the evidence. Summary: config is already
   one token per workspace (`cli/settings.py:82,117`), `workspaces list/activate/rm` are
   local-only, `workspaces add` validates with the singular `getWorkspace(slug)`, and
   nothing in `cli/` or `sdk/` calls `me`, the plural `workspaces`, or `organizations`.
   The blast radius is therefore small, and the cutoff story on §5 Phase 5 holds.
   Two consequences replace this question: the error code must not be `UNAUTHENTICATED`
   (§4.4), and the `get_dataset(source_workspace_slug=…)` path needs a test (§7 risk 2).
2. **Do we ship a CLI release at all?** Not needed for the token *format* — there is no
   token-format validation anywhere (`cli/api.py:193`), so `ohx_ws_…` works on every
   installed client. It buys readable scope errors (today `cli/api.py:216` prints the raw
   GraphQL errors list) and a legacy-token warning. Optional, but if we do it, it must
   land before the brownouts.

3. **Should a token be able to act as *less* than its owner** (role cap, read-only)? Out
   of scope here by decision, but the token table should not make it hard later. A nullable
   `max_role` column costs nothing now.
4. **`created_by` vs `user`:** should an admin be able to mint a token for a service
   identity in their workspace (a "workspace bot") rather than for themselves? That is
   arguably the real answer for CI, and it would remove the "my token, my account" problem
   entirely. Bigger change; flag as a follow-up.
5. **Expiry defaults.** Do we want a maximum lifetime (e.g. 1 year) on `scope_version = 2`
   tokens from the start? Cheaper to introduce now than later.
6. **`bypass_two_factor`** — keep, restrict, or drop for tokens?
7. **What is the cutoff date**, and who owns the comms? Needs product sign-off before
   Phase 3, not after.
8. **Superuser tokens** — do internal tools depend on a wide token today? If yes, they
   need an alternative before Phase 5.

---

## 9. What the CLI and SDK actually do (checked 2026-08-25)

Read against `../openhexa-sdk-python`.

| Finding | Where |
| --- | --- |
| Config is already one token per workspace: `~/.openhexa.ini` `[workspaces]` maps slug → token, and `access_token` returns the *current* workspace's | `cli/settings.py:82`, `:97`, `:117` |
| `workspaces list` / `activate` / `rm` are local only — no API call | `cli/cli.py:141-160` |
| `workspaces add <slug> --token` validates via the singular `getWorkspace(slug)` — the token's own workspace | `cli/api.py:225` |
| Nothing in `cli/` or `sdk/` calls `me`, the plural `workspaces`, or `organizations` (they exist in the generated client, unused) | `graphql_client/client.py:648`, `:918` |
| Every runtime call names its workspace explicitly (`workspace(slug=self.slug)`, `pipelines(workspaceSlug=…)`, `get_connection(workspace_slug=…)`) | `sdk/workspaces/current_workspace.py:69,83,255,604` |
| User-Agent is versioned: `openhexa-cli/{version}`, `openhexa-sdk/{version}` — Phase 0 gets the client version distribution for free | `cli/api.py:194`, `graphql/base_openhexa_client.py:24` |
| No token-format validation anywhere; the token is an opaque string in a Bearer header, so `ohx_ws_…` works on every installed client | `cli/api.py:193` |
| `HEXA_TOKEN` env var overrides the config file (pipeline runtime path) | `cli/settings.py:117` |

**The one cross-workspace API:** `workspace.get_dataset(identifier, source_workspace_slug=…)`
(`sdk/workspaces/current_workspace.py:530`) — documented, and its error message tells users
to pass `source_workspace_slug` for a dataset shared from another workspace. It resolves
`datasetLinkBySlug`, whose first branch matches `dataset__workspace__slug=<source>`. Under
"reach, not rows" it keeps working; see §7 risk 2 for the missing test.

**One migration edge:** today you can store workspace A's token under slug B and it works.
Those configs break at cutoff, and they are detectable in the Phase 0 shadow log as
"token workspace ≠ requested slug".

## 10. Alternatives considered

| Option | Why not |
| --- | --- |
| **Per-request workspace header** — token stays wide, client declares intent | Client-declared scope is not a security boundary; a leaked token just omits the header |
| **JWT with claims** instead of signed opaque payloads | Real benefit (self-describing, expiring), but a bigger change and no revocation without a denylist; the signed-payload strategy already in `WorkspaceToken` is adequate, and the token table gives us revocation |
| **Capability tokens now** (read-only, pipeline-only) | Doubles the permission surface while the primary hole is still open. Ship workspace scoping, keep the extension point |
| **Enforce in each resolver** | ~200 resolvers, every one a chance to forget; unreviewable; no single rollback switch |
| **Hard cut in one release** | Fastest to a clean codebase, and the one option guaranteed to break users without warning |
| **Do nothing / document the risk** | The token is an account credential in a place users treat as a project credential. That gap does not stay theoretical |

---

## 11. What I would do next (concrete)

1. Finish the branch's enforcement wiring behind the three-state flag, default `off`.
2. Land the `WorkspaceAccessToken` table + backfill + `last_used_at` (Phase 0), since it
   blocks every measurement and every UI decision downstream.
3. Add the shadow-evaluation logging and let it run.
4. In parallel, fix the six review items in §4.2 and add the org-shared/linked dataset
   test cases — those are the ones most likely to be quietly wrong.
5. Bring the Phase 0 numbers to product, and only then pick the cutoff date.
