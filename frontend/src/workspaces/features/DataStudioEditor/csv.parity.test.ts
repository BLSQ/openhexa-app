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

const vectors: Vector[] = JSON.parse(
  readFileSync(FIXTURE_PATH, "utf-8"),
).vectors;

describe("CSV cell serialisation parity with the backend", () => {
  it.each(vectors)(
    "serialises $description identically to the server",
    ({ value, expected }) => {
      // The value sits in a two-column row (with a constant sentinel) rather
      // than alone — the realistic shape, and it sidesteps a lone-empty-field
      // quirk in Python's csv.writer. The backend asserts this same shape.
      expect(buildCsv(["a", "b"], [{ a: value, b: "x" }])).toBe(
        `a,b\r\n${expected},x\r\n`,
      );
    },
  );
});
