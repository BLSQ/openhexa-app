import { buildCsv } from "./csv";

// Cell-level serialisation (nulls, numbers, formula-injection, quoting) is
// covered exhaustively — and cross-checked against the backend — in
// csv.parity.test.ts. This file covers only buildCsv's own structural shape.
describe("buildCsv", () => {
  it("writes a header then one CRLF-terminated line per row, including the last", () => {
    expect(
      buildCsv(
        ["id", "name"],
        [
          { id: 1, name: "Alice" },
          { id: 2, name: "Bob" },
        ],
      ),
    ).toBe("id,name\r\n1,Alice\r\n2,Bob\r\n");
  });

  it("orders cells by the column list and ignores extra keys", () => {
    expect(buildCsv(["b", "a"], [{ a: "1", b: "2", c: "3" }])).toBe(
      "b,a\r\n2,1\r\n",
    );
  });

  it("fills missing keys with empty cells", () => {
    expect(buildCsv(["a", "b"], [{ a: "1" }])).toBe("a,b\r\n1,\r\n");
  });

  it("emits only a terminated header when there are no rows", () => {
    expect(buildCsv(["a", "b"], [])).toBe("a,b\r\n");
  });

  it("guards a formula-triggering column header", () => {
    expect(buildCsv(["=danger"], [])).toBe("'=danger\r\n");
  });
});
