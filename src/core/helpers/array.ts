export function ensureArray<T>(maybeArray: T[] | T): T[] {
  if (typeof maybeArray === "undefined") {
    return [];
  } else if (maybeArray === null) {
    return [];
  } else if (Array.isArray(maybeArray)) {
    return maybeArray;
  } else {
    return [maybeArray];
  }
}
