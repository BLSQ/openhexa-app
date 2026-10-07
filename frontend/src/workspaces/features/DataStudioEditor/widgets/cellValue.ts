// A numeric literal as Postgres emits it for numeric types: optional leading
// '-', digits, optional fraction, optional exponent. No leading '+' — Postgres
// never emits "+5", so a '+'-prefixed value is genuine text, not a number.
const NUMERIC_LITERAL = /^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/;

// Whether a cell value should be treated as a number. NUMERIC/DECIMAL (and
// bigint) columns are serialised as strings to preserve precision, so a JS
// `number` check alone misses them; recognise numeric-shaped strings too.
export const isNumericValue = (value: unknown): boolean =>
  typeof value === "number" ||
  (typeof value === "string" && NUMERIC_LITERAL.test(value));

export const stringifyCellValue = (value: unknown): string => {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
};
