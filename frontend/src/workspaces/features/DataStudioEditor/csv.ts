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

// Python's csv.writer renders a row of a single empty field as `""` (to keep it
// distinct from a blank line on read-back); the server export path inherits that
// from csv.writer. Match it so single-column results stay byte-identical across
// both export paths — see the rowVectors in csv.parity.test.ts.
const joinRow = (fields: string[]): string =>
  fields.length === 1 && fields[0] === "" ? '""' : fields.join(",");

// One escaped, formula-guarded CSV record per array item (header first). The
// single source of truth for record shape, shared by buildCsv (the parity/test
// surface) and downloadCsvBlob (the streaming download) so they cannot drift.
export const buildCsvLines = (
  columns: string[],
  rows: Record<string, unknown>[],
): string[] => {
  const lines = [joinRow(columns.map(escapeCsvField))];
  for (const row of rows) {
    lines.push(joinRow(columns.map((column) => escapeCsvField(row[column]))));
  }
  return lines;
};

export const buildCsv = (
  columns: string[],
  rows: Record<string, unknown>[],
): string =>
  // CRLF record separator per RFC 4180, with a trailing CRLF after the last
  // record too — matching Python's csv.writer on the server so both export
  // paths produce identical bytes (see csv.parity.test.ts). Embedded newlines
  // inside quoted fields are preserved as-is by escapeCsvField.
  buildCsvLines(columns, rows).join("\r\n") + "\r\n";

// Excel decodes a UTF-8 CSV as the local ANSI codepage unless it sees a BOM,
// which mangles accented characters. Prepend one so non-ASCII data survives.
const UTF8_BOM = "\uFEFF";

// Download the result as a CSV without ever materialising the whole file as one
// JS string: the Blob is assembled from the per-record parts directly, so peak
// memory stays ~1× the data instead of the full string plus its Blob copy.
// Byte-for-byte identical to downloading buildCsv(columns, rows)'s output.
export const downloadCsvBlob = (
  filename: string,
  columns: string[],
  rows: Record<string, unknown>[],
) => {
  const parts: BlobPart[] = [UTF8_BOM];
  for (const line of buildCsvLines(columns, rows)) {
    parts.push(line, "\r\n");
  }
  downloadBlob(filename, new Blob(parts, { type: "text/csv;charset=utf-8;" }));
};
