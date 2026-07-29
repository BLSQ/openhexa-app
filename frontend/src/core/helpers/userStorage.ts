// Namespace for local storage holding things a user typed but has not persisted
// server-side (editor drafts and the like). Everything under it is scoped to a
// user and wiped on logout, so a shared browser never hands one person's work to
// whoever signs in next.
const PREFIX = "user-data.";

export const userDataKey = (...parts: string[]) => PREFIX + parts.join(".");

export const clearUserData = () => {
  try {
    // Keys are collected before removing: mutating the store shifts the indices
    // that a live iteration walks.
    Object.keys(window.localStorage)
      .filter((key) => key.startsWith(PREFIX))
      .forEach((key) => window.localStorage.removeItem(key));
  } catch {
    // Storage unavailable (private browsing), so there is nothing cached to clear.
  }
};
