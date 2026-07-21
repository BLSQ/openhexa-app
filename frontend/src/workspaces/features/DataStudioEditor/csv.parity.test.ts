import { readFileSync } from "fs";
import { resolve } from "path";
import { buildCsv } from "./csv";

// The single source of truth for the CSV-cell contract lives in the backend tree
// (so the Django test can read it inside a container that only mounts backend/).
// On the host the whole repo is present, so we read that exact same file — no
// duplication, no drift. Backend counterpart: hexa/core/tests/test_csv.py.
const FIXTURE_PATH = resolve(
  __dirname,
  "../../../../../backend/hexa/core/tests/fixtures/csv_cell_vectors.json",
);

type Vector = { description: string; value: unknown; expected: string };
type RowVector = {
  description: string;
  columns: string[];
  rows: Record<string, unknown>[];
  expected: string;
};

const contract = JSON.parse(readFileSync(FIXTURE_PATH, "utf-8"));
const vectors: Vector[] = contract.vectors;
const rowVectors: RowVector[] = contract.rowVectors;

describe("CSV cell serialisation parity with the backend", () => {
  it.each(vectors)(
    "serialises $description identically to the server",
    ({ value, expected }) => {
      // Each value sits in a two-column row (with a constant sentinel) so the
      // vector stays focused on cell content; whole-record shape is pinned by
      // the rowVectors suite below. The backend asserts this same shape.
      expect(buildCsv(["a", "b"], [{ a: value, b: "x" }])).toBe(
        `a,b\r\n${expected},x\r\n`,
      );
    },
  );
});

describe("CSV record-shape parity with the backend", () => {
  it.each(rowVectors)(
    "builds $description identically to the server",
    ({ columns, rows, expected }) => {
      expect(buildCsv(columns, rows)).toBe(expected);
    },
  );
});
