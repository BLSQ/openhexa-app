/**
 * A panel's layout lives in a cookie rather than in localStorage so that the
 * server sees it: `_app` hands the request's cookies to `CookiesProvider`, so a
 * panel reads its remembered size while the page is still being rendered and
 * comes back at that size in the first paint. Storage only the client can read
 * would mean painting a default first and correcting it after hydration.
 */

export type PanelLayout = { size: number; collapsed: boolean };

/** Anything larger is a corrupt cookie rather than a size someone chose. */
const MAX_SIZE = 10_000;

/**
 * The layout belongs to a place in the app, not to a name someone has to invent
 * and keep unique: two panels on one page are already told apart by the side
 * they sit on. Punctuation goes, since a cookie name cannot hold it.
 */
export const panelCookieName = (pathname: string, suffix: string) =>
  `panel_${`${pathname}_${suffix}`.replace(/[^a-zA-Z0-9-]/g, "_")}`;

/** A cookie is user input, and this one ends up as a width. */
export const sanitizePanelLayout = (
  layout: PanelLayout,
  fallbackSize: number,
): PanelLayout => {
  const size = Number(layout?.size);
  return {
    size:
      Number.isFinite(size) && size > 0 && size <= MAX_SIZE
        ? size
        : fallbackSize,
    collapsed: Boolean(layout?.collapsed),
  };
};
