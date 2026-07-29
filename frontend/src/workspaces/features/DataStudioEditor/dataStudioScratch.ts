import { userDataKey } from "core/helpers/userStorage";

// Draft of the unsaved Data Studio editor, kept per user and per workspace so
// leaving the page does not discard it. Saved queries are not stored here: the
// query itself is their persisted copy.
//
// SQL is sensitive (schema names, identifiers in WHERE clauses), so the draft is
// scoped to its author and lives under the namespace logout clears: a shared
// browser must not show one user's draft to whoever signs in next.

const KEY_PREFIX = `${userDataKey("data-studio.scratch")}.`;

// A draft this large is almost certainly a pasted data dump rather than a query
// worth keeping, and storing it risks filling the origin's storage quota.
const MAX_LENGTH = 100_000;

// A draft nobody has returned to in a month is not one they are still working on.
// Nothing else would ever remove it: an entry is only read by reopening the
// editor for that exact workspace, and renaming a workspace orphans its entry
// under a key that can never be read again at all.
const TTL_MS = 30 * 24 * 60 * 60 * 1000;

// Ceiling on how many drafts may accumulate regardless of age. localStorage is
// one budget per origin (~5MB) shared with the rest of the app, and MAX_LENGTH
// alone allows ~50 entries to exhaust it, so a user working across many
// workspaces must not be able to crowd out other features.
const MAX_ENTRIES = 20;

// Passed as one object rather than two strings so the user and the workspace
// cannot be transposed at a call site.
export type ScratchScope = {
  userId: string;
  workspaceSlug: string;
};

type StoredDraft = {
  content: string;
  updatedAt: number;
};

const storageKey = ({ userId, workspaceSlug }: ScratchScope) =>
  `${KEY_PREFIX}${userId}.${workspaceSlug}`;

// Local storage can be unavailable (private browsing) or full. Losing a draft is
// preferable to breaking the editor, so every access tolerates failure.
const tolerateFailure = (mutate: () => void) => {
  try {
    mutate();
  } catch {
    // Nothing to recover from: the draft simply is not kept.
  }
};

// Anything unreadable is reported as absent rather than repaired: malformed JSON,
// a missing timestamp, or a value left by an earlier storage format. The sweep
// then clears it out.
const parseDraft = (raw: string | null): StoredDraft | null => {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw);
    return typeof parsed?.content === "string" &&
      typeof parsed?.updatedAt === "number"
      ? parsed
      : null;
  } catch {
    return null;
  }
};

const hasExpired = (draft: StoredDraft, now: number) =>
  now - draft.updatedAt > TTL_MS;

export const readScratch = (scope: ScratchScope) => {
  try {
    const draft = parseDraft(window.localStorage.getItem(storageKey(scope)));
    // Expired entries are reported empty but left in place; sweepScratch owns
    // removal, so reading stays free of side effects.
    return draft && !hasExpired(draft, Date.now()) ? draft.content : "";
  } catch {
    return "";
  }
};

export const writeScratch = (scope: ScratchScope, content: string) =>
  tolerateFailure(() => {
    // Dropping the entry rather than skipping the write, so an outdated draft is
    // never restored in place of what the user actually has in the editor.
    if (!content || content.length > MAX_LENGTH) {
      window.localStorage.removeItem(storageKey(scope));
      return;
    }
    const draft: StoredDraft = { content, updatedAt: Date.now() };
    window.localStorage.setItem(storageKey(scope), JSON.stringify(draft));
  });

export const clearScratch = (scope: ScratchScope) =>
  tolerateFailure(() => window.localStorage.removeItem(storageKey(scope)));

// Drops what no longer earns its space: unreadable and expired entries first,
// then the oldest of whatever remains beyond MAX_ENTRIES. Deliberately spans
// every user's drafts, because the quota it protects belongs to the origin
// rather than to one account.
export const sweepScratch = () =>
  tolerateFailure(() => {
    const now = Date.now();
    const live: { key: string; updatedAt: number }[] = [];

    // Keys are collected before removing: mutating the store shifts the indices
    // that a live iteration walks.
    Object.keys(window.localStorage)
      .filter((key) => key.startsWith(KEY_PREFIX))
      .forEach((key) => {
        const draft = parseDraft(window.localStorage.getItem(key));
        if (!draft || hasExpired(draft, now)) {
          window.localStorage.removeItem(key);
          return;
        }
        live.push({ key, updatedAt: draft.updatedAt });
      });

    live
      .sort((a, b) => b.updatedAt - a.updatedAt)
      .slice(MAX_ENTRIES)
      .forEach(({ key }) => window.localStorage.removeItem(key));
  });
