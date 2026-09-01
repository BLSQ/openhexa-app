# git — version history on a Forgejo server

This app is the one place that talks to the git server. `GitRepoMixin` gives a model a
repository of its own (create, protect, archive) and `GitClient` / `ForgejoClient` are the
API behind it; `views` proxies git-over-HTTP for the models that expose clone and push.

Repositories are how OpenHEXA versions the things users author. Two models use it today —
`webapps.GitWebapp` (a file tree) and `data_studio.SavedQuery` (a single `query.sql`) — and
one repository per artifact is the pattern both follow. What that buys is an append-only
store no bad migration can rewrite, authorship and commit messages for free, growth that
stays out of the primary database, and history that is inspectable outside the app. The
rest of this file is what it costs, because both costs apply to every model that joins.

## A commit cannot join a database transaction

There is no two-phase commit between Postgres and the git server, so a write that touches
both can only choose which one to trust. Both current models commit first and write the row
second, inside `transaction.atomic()`, so a git failure aborts the whole change and leaves
nothing behind. The user-visible consequence is that saving fails while the git server is
down — deliberately, since the alternative is a change kept with a hole in its history that
nothing afterwards could tell apart from a change nobody made.

What follows from that: the database must stay the source of truth for anything on a hot
path. A saved query's SQL is read to run it, export it and list it, so it lives in the
column and git is written through on save; only history is read back from the server. A
model that read its content from git on every request would make the git server a hard
dependency of every page that shows it.

Each model keeps the sha it last wrote (`SavedQuery.last_commit`,
`GitWebapp.published_commit`) — for saved queries that is a drift detector rather than a
publishing pointer, and it doubles as the "the repository exists on the server" marker,
which is not the same thing as having a repository *name* (see below).

## A repository is named before it exists

Naming a repository is free and offline; creating it is an HTTP call that can fail. The two
are therefore separate steps, and a row can carry a name for a repository that was never
created — which is exactly the state a migration introducing versioning leaves existing
rows in. Anything asking "does this have history?" must test the sha, not the name.

Names are derived from the primary key rather than the slug, because a deleted row releases
its slug: reusing one would land on the archived repository the deleted row left behind,
which `create_repo` reports as "already exists, reusing it" before the next commit fails on
a repository that is read-only.

## Commit metadata outlives the account

A commit carries its author's name and email in immutable object metadata. Deleting a user
account removes their rows but cannot rewrite the commits they made, and archiving a
repository does not either. This is worth knowing wherever a deletion policy is written
(`data_studio.saved_queries_on_author_deleted` is one) and wherever an account deletion is
described to a user: it removes what the app stores, not what git recorded.

## Deletions that bypass the model

Each model archives its repository in its own `delete_if_has_perm`, so history survives an
ordinary deletion. Bulk paths do not go through it — a cascading workspace or author
deletion leaves an unarchived repository behind. The backstop is organization deletion,
which archives every repository in the org (`user_management.Organization._archive_git_org`).
At current volumes this is accepted rather than solved; the fix, if it ever matters, is a
sweep command, not a `post_delete` signal doing HTTP inside a cascade.
