---
name: pr-digest
description: Digest a pull request in two short, linked lists — the key changes (dependencies, models, migrations, tooling) and the judgment calls behind them. Use when asked to summarise, digest, or write a review guide for a PR.
---

# Digest a pull request

The reader is a reviewer who has not opened the PR yet. Give them the shape of
the change and the choices behind it in under a minute, each pointing at the
code that implements it.

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

## Format

Two sections, in this order. Drop either when it has nothing genuine in it.

**Key changes** — one bullet per change that alters the system's shape: a
dependency added or removed, a model or field, a DB migration, a new GraphQL
type or mutation, a new tool, service or workflow. Bold label, one short
clause, and a link to where it is implemented, e.g.
`**Migration 0066** — seeds the dashboard SQL ([0066_token_scope_dashboard.py:12](…))`.
Leave out routine edits and generated files (`backend/requirements.txt`,
`frontend/**/*.generated.tsx`, `frontend/schema.generated.graphql`,
lockfiles, jest snapshots).

**Decisions** — up to 3 bullets, one sentence each, with a link to the code.
A decision is a fork in the road where a competent engineer could have gone the
other way: name the road not taken and its cost, and say if the choice looks
wrong. "Added a field" is not a decision; "widened the existing model instead
of a new table, so every row carries the column" is. If the diff made no
interesting choice, drop the section.

## Rules

- Under 150 words, no other headings. Every sentence must tell the reviewer
  something they would not get from the PR title and file list. No intro, no
  summary, no praise.
- Judge the choices, not the style.
- Change no files, push nothing, and open no review — the digest is one comment.

## Running in CI

`.github/workflows/pr_digest.yml` runs this skill on demand: when someone with
write access comments `/digest` on a pull request, or from the Actions tab.
Return the digest markdown as the `digest` field of your structured output; the
workflow posts it and refreshes the same comment on the next run, so do not
post it yourself with `gh pr comment`. The PR head is already checked out.
