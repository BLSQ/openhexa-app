/**
 * Returns `next` as a path on this origin, or "/" if it points anywhere else.
 *
 * Used for `?next=` query params, which are attacker-controlled: an absolute or
 * `javascript:` URL would make the redirect leave the app or run script.
 */
export function getSafeRedirectPath(next: unknown): string {
  if (typeof next !== "string") {
    return "/";
  }
  // Resolved the way the browser will navigate, so tricks like `//host`,
  // `/\host` or `/\t/host` can't leave the origin. Any origin works as the base.
  const base = "http://localhost";
  try {
    const url = new URL(next, base);
    return url.origin === base ? url.pathname + url.search + url.hash : "/";
  } catch {
    return "/";
  }
}
