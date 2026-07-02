import { downloadBlob } from "core/helpers/files";
import { stringifyCellValue } from "./format";

// Leading characters that spreadsheet apps interpret as the start of a formula.
// Prefixing these values with a single quote neutralises CSV injection.
const FORMULA_PREFIX = /^[=+\-@\t\r]/;

const escapeCsvField = (raw: unknown): string => {
  const text = stringifyCellValue(raw);
  // Numbers are safe and must stay intact (e.g. "-5" should not become "'-5").
  const guarded =
    typeof raw !== "number" && FORMULA_PREFIX.test(text) ? `'${text}` : text;
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
  // CRLF record separator per RFC 4180; embedded newlines inside quoted fields
  // are preserved as-is by escapeCsvField.
  return lines.join("\r\n");
};

// Excel decodes a UTF-8 CSV as the local ANSI codepage unless it sees a BOM,
// which mangles accented characters. Prepend one so non-ASCII data survives.
const UTF8_BOM = "\uFEFF";

export const downloadCsv = (filename: string, content: string) => {
  downloadBlob(
    filename,
    new Blob([UTF8_BOM, content], { type: "text/csv;charset=utf-8;" }),
  );
};
