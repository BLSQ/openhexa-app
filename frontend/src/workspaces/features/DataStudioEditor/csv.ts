import { downloadBlob } from "core/helpers/files";
import { isNumericValue, stringifyCellValue } from "./format";

// Leading characters spreadsheet apps interpret as the start of a formula.
// Prefixing with a single quote neutralises CSV injection. This MUST stay in
// lockstep with the backend guard in hexa/core/csv.py: the same query can be
// exported via this client path (small results) or the server path (large
// results), and csv.parity.test.ts asserts the two emit byte-identical output.
const FORMULA_PREFIX = /^[=+\-@\t\r]/;

const escapeCsvField = (raw: unknown): string => {
  const text = stringifyCellValue(raw);
  // Numbers are inert in a spreadsheet and must stay intact ("-5" not "'-5").
  // NUMERIC/DECIMAL/bigint arrive as strings to preserve precision, so guard by
  // the value's textual shape, not just its JS type.
  const guarded =
    !isNumericValue(raw) && FORMULA_PREFIX.test(text) ? `'${text}` : text;
  return /[",\n\r]/.test(guarded)
    ? `"${guarded.replace(/"/g, '""')}"`
    : guarded;
};

// Every record — including the last — is terminated by CRLF, matching Python's
// csv.writer on the server so both export paths produce identical bytes.
export const buildCsv = (
  columns: string[],
  rows: Record<string, unknown>[],
): string => {
  let csv = columns.map(escapeCsvField).join(",") + "\r\n";
  for (const row of rows) {
    csv +=
      columns.map((column) => escapeCsvField(row[column])).join(",") + "\r\n";
  }
  return csv;
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
