export function ensureArray(maybeArray: any[] | any): any[] {
  if (Array.isArray(maybeArray)) {
    return maybeArray;
  }

  return new Array(maybeArray);
}
