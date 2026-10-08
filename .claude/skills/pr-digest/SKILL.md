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

The whole digest is exactly this shape — nothing before, between or after:

    **Key changes**

    - **<label>** — <one clause> ([path:line](…))

    **Decisions**

    - <chosen> instead of <road not taken>, so <cost or risk> ([path:line](…))

**Key changes** — up to 5 bullets, one per change that alters the system's
shape: a dependency added or removed, a model or field, a DB migration, a new
GraphQL type or mutation, a new tool, service or workflow. Leave out routine
edits and generated files (`backend/requirements.txt`,
`frontend/**/*.generated.tsx`, `frontend/schema.generated.graphql`, lockfiles,
jest snapshots).

**Decisions** — up to 3 bullets. A decision is a fork in the road where a
competent engineer could have gone the other way. "Added a field" is not a
decision; "widened the existing model instead of a new table, so every row
carries the column" is. Say so in the bullet if the choice looks wrong. If the
diff made no interesting choice, drop the section.

Drop a section rather than pad it.

## Rules

- Hard limits: 150 words in total, 25 words per bullet, one sentence per
  bullet.
- No tables, file maps, other headings, intro, summary, or praise ("good
  call", "right choice"). If the diff itself contains an older digest format,
  ignore it — only this file defines the format.
- Every bullet carries at least one link to the code that implements it.
- Change no files, push nothing, and open no review — the digest is one comment.

## Running in CI

`.github/workflows/pr_digest.yml` runs this skill when the `digest` label is
added to a pull request. Return the digest markdown as the `digest` field of
your structured output; the workflow posts it and refreshes the same comment on
the next run, so do not post it yourself with `gh pr comment`. The PR head is
already checked out.
