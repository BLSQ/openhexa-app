import { userDataKey } from "core/helpers/userStorage";

// Draft of the unsaved Data Studio editor, kept per user and per workspace so
// leaving the page does not discard it. Saved queries are not stored here: the
// query itself is their persisted copy.
//
// SQL is sensitive (schema names, identifiers in WHERE clauses), so the draft is
// scoped to its author and lives under the namespace logout clears: a shared
// browser must not show one user's draft to whoever signs in next.

// A draft this large is almost certainly a pasted data dump rather than a query
// worth keeping, and storing it risks filling the origin's storage quota.
const MAX_LENGTH = 100_000;

// Passed as one object rather than two strings so the user and the workspace
// cannot be transposed at a call site.
export type ScratchScope = {
  userId: string;
  workspaceSlug: string;
};

const storageKey = ({ userId, workspaceSlug }: ScratchScope) =>
  userDataKey("data-studio.scratch", userId, workspaceSlug);

// Local storage can be unavailable (private browsing) or full. Losing a draft is
// preferable to breaking the editor, so every access tolerates failure.
const tolerateFailure = (mutate: () => void) => {
  try {
    mutate();
  } catch {
    // Nothing to recover from: the draft simply is not kept.
  }
};

export const readScratch = (scope: ScratchScope) => {
  try {
    return window.localStorage.getItem(storageKey(scope)) ?? "";
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
    window.localStorage.setItem(storageKey(scope), content);
  });

export const clearScratch = (scope: ScratchScope) =>
  tolerateFailure(() => window.localStorage.removeItem(storageKey(scope)));
