import { downloadBlob } from "core/helpers/files";
import { isNumericValue, stringifyCellValue } from "./format";

// Leading characters that spreadsheet apps interpret as the start of a formula.
// Prefixing these values with a single quote neutralises CSV injection.
// This MUST stay in lockstep with the backend guard in hexa/core/csv.py: the
// same query can be exported via this client path (small results) or the server
// path (large results), and csv.parity.test.ts asserts the two emit identical
// output.
const FORMULA_PREFIX = /^[=+\-@\t\r]/;

const escapeCsvField = (raw: unknown): string => {
  const text = stringifyCellValue(raw);
  // Numbers are safe and must stay intact (e.g. "-5" should not become "'-5").
  // NUMERIC/DECIMAL columns arrive as strings (encoded that way to preserve
  // precision), so guard by the value's textual shape, not just its JS type.
  const guarded =
    !isNumericValue(raw) && FORMULA_PREFIX.test(text) ? `'${text}` : text;
  return /[",\n\r]/.test(guarded)
    ? `"${guarded.replace(/"/g, '""')}"`
    : guarded;
};

export const buildCsv = (
  columns: string[],
  rows: Record<string, unknown>[],
): string => {
  const lines = [columns.map(escapeCsvField).join(",")];
  for (const row of rows) {
    lines.push(columns.map((column) => escapeCsvField(row[column])).join(","));
  }
  // CRLF record separator per RFC 4180, with a trailing CRLF after the last
  // record too — matching Python's csv.writer on the server so both export
  // paths produce identical bytes (see csv.parity.test.ts). Embedded newlines
  // inside quoted fields are preserved as-is by escapeCsvField.
  return lines.join("\r\n") + "\r\n";
};

// Excel decodes a UTF-8 CSV as the local ANSI codepage unless it sees a BOM,
// which mangles accented characters. Prepend one so non-ASCII data survives.
const UTF8_BOM = "\uFEFF";

export const downloadCsvBlob = (filename: string, content: string) => {
  downloadBlob(
    filename,
    new Blob([UTF8_BOM, content], { type: "text/csv;charset=utf-8;" }),
  );
};
