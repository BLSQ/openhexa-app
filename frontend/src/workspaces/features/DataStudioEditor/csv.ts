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
  return lines.join("\n");
};

export const downloadCsv = (filename: string, content: string) => {
  downloadBlob(
    filename,
    new Blob([content], { type: "text/csv;charset=utf-8;" }),
  );
};
