/** Escapes `text` so it matches literally inside a `RegExp`. */
export function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
