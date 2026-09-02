# git — version history on a Forgejo server

This app is the one place that talks to the git server. `GitRepoMixin` gives a model a
repository of its own (create, protect, archive) and `GitClient` / `ForgejoClient` are the
API behind it; `views` proxies git-over-HTTP for the models that expose clone and push.

Repositories are how OpenHEXA versions the things users author, one per artifact.
`webapps.GitWebapp` (a file tree) and `data_studio.SavedQuery` (a single `query.sql`) use
it today. What it buys: an append-only store no bad migration can rewrite, authorship and
commit messages for free, growth kept out of the primary database, and history inspectable
outside the app. The rest of this file is what it costs — and every cost here applies to
any model that joins.

## A commit cannot join a database transaction

There is no two-phase commit between Postgres and the git server, so a write touching both
can only choose which to trust. Both models commit to git first and write the row second,
inside `transaction.atomic()`, so a git failure aborts the change and leaves nothing
behind. Saving therefore fails while the git server is down — deliberately: the
alternative is a change kept with a hole in its history, indistinguishable afterwards from
a change nobody made.

It follows that the database must stay the source of truth for anything on a hot path. A
saved query's SQL is read to run, export and list it, so it lives in the column and git is
written through on save; only history is read back. A model reading its content from git
per request would make the git server a dependency of every page showing it.

Each model keeps the sha it last wrote (`SavedQuery.last_commit`,
`GitWebapp.published_commit`). For saved queries that is a drift detector rather than a
publishing pointer, and it doubles as the "repository exists on the server" marker — not
the same thing as having a repository *name*.

## A repository is named before it exists

Naming is free and offline; creating is an HTTP call that can fail. So they are separate
steps, and a row can carry a name for a repository that was never created — the state a
migration introducing versioning leaves existing rows in. Anything asking "does this have
history?" must test the sha, not the name.

Names derive from the primary key, not the slug, because a deleted row releases its slug:
reusing one lands on the archived repository that row left behind, which `create_repo`
reports as "already exists, reusing it" before the next commit fails on a read-only
repository.

## Commit metadata outlives the account

A commit carries its author's name and email in immutable object metadata. Deleting a user
account removes their rows but cannot rewrite the commits they made, and archiving a
repository does not either. Worth knowing wherever a deletion policy is written
(`data_studio.saved_queries_on_author_deleted`) and wherever account deletion is described
to a user: it removes what the app stores, not what git recorded.

## Nothing reaps an unarchived repository

Each model archives its repository in `delete_if_has_perm`, so history survives an
ordinary deletion. Saved queries archive on `transaction.on_commit` rather than inline,
because archiving is irreversible: inside the transaction, a commit failing afterwards
would leave a read-only repository on a query that still exists, which no later save could
recover from. The price is that archiving is best-effort — a failure is logged and leaves
the repository behind, the query being gone by then.

Three paths leak that way: that logged failure, and cascading workspace or author
deletions, which never reach `delete_if_has_perm` at all. **Nothing collects them.** The
only backstop is organization deletion, which archives every repository in the org
(`user_management.Organization._archive_git_org`). At current volumes this is accepted
rather than solved; the fix is a sweep command diffing `list_org_repositories` against live
rows, not a `post_delete` signal doing HTTP inside a cascade.
