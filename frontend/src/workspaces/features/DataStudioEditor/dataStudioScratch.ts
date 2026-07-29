// Draft of the unsaved Data Studio editor, kept per workspace so leaving the
// page does not discard it. Saved queries are not stored here: the query itself
// is their persisted copy.

const KEY_PREFIX = "data-studio.scratch.";

// A draft this large is almost certainly a pasted data dump rather than a query
// worth keeping, and storing it risks filling the origin's storage quota.
const MAX_LENGTH = 100_000;

const storageKey = (workspaceSlug: string) => `${KEY_PREFIX}${workspaceSlug}`;

// Local storage can be unavailable (private browsing) or full. Losing a draft is
// preferable to breaking the editor, so every access tolerates failure.
const tolerateFailure = (mutate: () => void) => {
  try {
    mutate();
  } catch {
    // Nothing to recover from: the draft simply is not kept.
  }
};

export const readScratch = (workspaceSlug: string) => {
  try {
    return window.localStorage.getItem(storageKey(workspaceSlug)) ?? "";
  } catch {
    return "";
  }
};

export const writeScratch = (workspaceSlug: string, content: string) =>
  tolerateFailure(() => {
    // Dropping the entry rather than skipping the write, so an outdated draft is
    // never restored in place of what the user actually has in the editor.
    if (!content || content.length > MAX_LENGTH) {
      window.localStorage.removeItem(storageKey(workspaceSlug));
      return;
    }
    window.localStorage.setItem(storageKey(workspaceSlug), content);
  });

export const clearScratch = (workspaceSlug: string) =>
  tolerateFailure(() =>
    window.localStorage.removeItem(storageKey(workspaceSlug)),
  );
