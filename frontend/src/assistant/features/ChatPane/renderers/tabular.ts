export type Row = Record<string, unknown>;

export function isPlainObject(value: unknown): value is Row {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isObjectArray(value: unknown): value is Row[] {
  return (
    Array.isArray(value) && value.length > 0 && value.every(isPlainObject)
  );
}

// Locate the tabular data inside a tool result. Tool outputs wrap their rows in
// varying envelopes — a bare array (`list_files` items), a pagination page
// (`{items: [...]}`), or single-key GraphQL nesting (`{workspace: {connections: [...]}}`,
// `{pipelines: {items: [...]}}`). We follow `items` and unambiguous single-key
// objects only, so multi-field detail objects (e.g. `get_pipeline`) are left as
// JSON rather than mistaken for a table.
export function findTabularArray(value: unknown): Row[] | null {
  if (isObjectArray(value)) return value;
  if (isPlainObject(value)) {
    if (isObjectArray(value.items)) return value.items;
    const keys = Object.keys(value);
    if (keys.length === 1) return findTabularArray(value[keys[0]]);
  }
  return null;
}

export function columnsOf(rows: Row[]): string[] {
  const seen: string[] = [];
  for (const row of rows) {
    for (const key of Object.keys(row)) {
      if (!seen.includes(key)) seen.push(key);
    }
  }
  return seen;
}

// Render a cell value compactly; nested structures collapse to a hint so the
// table stays scannable (the full value is available via the raw JSON toggle).
export function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (Array.isArray(value)) return `[${value.length}]`;
  if (typeof value === "object") return "{…}";
  return String(value);
}
