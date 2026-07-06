// Brand palette mirrored from Tailwind's default colors so non-Tailwind contexts
// (CodeMirror, canvas, chart libraries, ...) can use the exact same values as the
// utility classes used across the app (e.g. `bg-pink-500`, `text-pink-500`).
//
// Tailwind v4 no longer exports `resolveConfig`, so these values are duplicated
// here on purpose and must be kept in sync with Tailwind's palette by hand.
export const colors = {
  pink: { 300: "#f9a8d4", 500: "#ec4899", 600: "#db2777" },
  emerald: { 700: "#047857" },
  amber: { 700: "#b45309" },
  violet: { 600: "#7c3aed" },
  gray: { 300: "#d1d5db", 400: "#9ca3af", 500: "#6b7280" },
} as const;
