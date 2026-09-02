---
name: pr-digest
description: Digest a pull request so a reviewer can go straight to what matters — ranked pointers into the diff, the dependency/model/migration/tooling changes, the judgment calls behind them, and a map of which files are critical. Use when asked to summarise, digest, or write a review guide for a PR.
---

# Digest a pull request

The reader is a reviewer who has not opened the PR yet. Their scarcest resource
is the first minute, so the job is to rank, not to narrate: what breaks if it is
wrong comes first, whatever the size of the change or the order files appear in
the diff.

Read the diff with `gh pr diff`, then open the surrounding files. What matters
is usually only visible against the code that was already there — a new
QuerySet, a widened model, a constraint moved between layers.

## Linking

Every `path:line` must be a link straight to that line of the diff:

    [path:line](<pr_url>/files#diff-<hash>R<line>)

`<hash>` is the SHA-256 of the file path: `printf '%s' 'backend/hexa/…/models.py' | sha256sum`.
The `printf '%s'` matters — a trailing newline changes the hash and the anchor
stops resolving. `R<line>` is the new side of the diff; use `L<line>` for a line
the PR deleted. If that command is unavailable, link to
`<repo_url>/blob/<head_sha>/<path>#L<line>` instead. Never leave a bare
`path:line` unlinked.

## Sections

Write them in this order, and drop any with nothing genuine in it.

**Start here** — up to 3 numbered pointers, each a link and one line on what to
check there. This is the section that saves the reviewer's time, so spend your
judgment on it: the riskiest line in the diff goes first. In this repo,
migrations that rewrite data or change grants, anything filtering rows per user,
permission and authentication logic, and contracts both tiers assert against
outrank everything else.

**Key changes** — one bullet each, only when the diff has them: dependency
choices, model changes, DB migrations, new tools or services.

**Decisions** — the judgment calls behind the diff. Be demanding here: this is
the section a reviewer cannot reconstruct on their own. A decision is a fork in
the road where a competent engineer could have gone the other way, so name the
road not taken and what it would have cost. "Added a field" is not a decision;
"widened the existing model instead of a separate table, so every existing row
now carries the column" is. Look for state put in a new place, a constraint
enforced in one layer rather than another, a dependency added where the repo
already had something close, a migration that backfills instead of defaulting,
an abstraction introduced before the second caller exists, error handling that
swallows rather than propagates. Say which choices look wrong and why. If the
diff genuinely made no interesting choice, write one line saying so — a padded
list is worse than an empty one.

**File map** — a table of the files that matter: file (linked), what changed,
and 🔴 critical / 🟡 worth a look / ⚪ routine. Critical means tenancy
filtering, permissions or authentication, a migration that rewrites data or
changes grants, or a cross-tier contract. Collapse the routine files into one
row, and leave generated files out — `backend/requirements.txt` (pip-compile
output), `frontend/**/*.generated.tsx` and `frontend/schema.generated.graphql`
(GraphQL codegen), lockfiles and jest snapshots are never hand-written, so a
count is all they earn.

## Rules

- Judge the choices, not the style.
- Under 400 words.
- Change no files, push nothing, and open no review — the digest is one comment.

## Running in CI

`.github/workflows/pr_digest.yml` runs this skill on every non-draft pull
request. The action owns a single sticky comment and rewrites it on each push,
so write the digest as your final message and do not post it yourself with
`gh pr comment`. The PR head is already checked out.
