import { buildCsv } from "./csv";

describe("buildCsv", () => {
  it("writes a header row followed by one CRLF-separated line per row", () => {
    const csv = buildCsv(
      ["id", "name"],
      [
        { id: 1, name: "Alice" },
        { id: 2, name: "Bob" },
      ],
    );
    expect(csv).toBe("id,name\r\n1,Alice\r\n2,Bob");
  });

  it("orders cells by the column list and ignores extra keys", () => {
    const csv = buildCsv(["b", "a"], [{ a: "1", b: "2", c: "3" }]);
    expect(csv).toBe("b,a\r\n2,1");
  });

  it("serialises null/undefined to empty cells and objects to JSON", () => {
    const csv = buildCsv(
      ["a", "b", "c"],
      [{ a: null, b: undefined, c: { x: 1 } }],
    );
    expect(csv).toBe('a,b,c\r\n,,"{""x"":1}"');
  });

  it("quotes and escapes values containing commas, quotes or newlines", () => {
    const csv = buildCsv(
      ["text"],
      [{ text: "a,b" }, { text: 'say "hi"' }, { text: "line1\nline2" }],
    );
    // Record separator is CRLF; the newline embedded in the data stays as-is.
    expect(csv).toBe('text\r\n"a,b"\r\n"say ""hi"""\r\n"line1\nline2"');
  });

  it("neutralises formula-injection in string cells", () => {
    const csv = buildCsv(
      ["v"],
      [{ v: "=1+1" }, { v: "+1" }, { v: "@cmd" }, { v: "-cmd" }],
    );
    expect(csv).toBe("v\r\n'=1+1\r\n'+1\r\n'@cmd\r\n'-cmd");
  });

  it("does not alter negative numbers, which are not an injection risk", () => {
    const csv = buildCsv(["n"], [{ n: -5 }]);
    expect(csv).toBe("n\r\n-5");
  });

  it("does not alter numeric strings, since NUMERIC/DECIMAL columns arrive as strings", () => {
    const csv = buildCsv(
      ["n"],
      [
        { n: "-5.5" },
        { n: "-5" },
        { n: "1e10" },
        { n: "-1.5e-3" },
        { n: "0.5" },
      ],
    );
    expect(csv).toBe("n\r\n-5.5\r\n-5\r\n1e10\r\n-1.5e-3\r\n0.5");
  });

  it("still neutralises formula-injection that merely looks numeric at the start", () => {
    const csv = buildCsv(["v"], [{ v: "-cmd" }, { v: "-1+1" }, { v: "+1" }]);
    expect(csv).toBe("v\r\n'-cmd\r\n'-1+1\r\n'+1");
  });

  // Backend NUMERIC/DECIMAL/bigint columns reach the frontend as JSON strings.
  // A pure numeric literal is inert in a spreadsheet, so it must pass through
  // untouched regardless of leading '-' (the reported bug was "-5.5" -> "'-5.5").
  describe("numeric-string preservation (regression: numbers-as-strings)", () => {
    const untouched = [
      "-5.5",
      "-5",
      "-0.001",
      "0",
      "-0",
      "0.5",
      ".5",
      "5.",
      "42",
      "1e10",
      "1E10",
      "-1.5e-3",
      "-1.5E+3",
      "123456789012345678901234567890", // beyond JS safe-int, stays a string
      "-123456789012345678901234567890.5",
    ];
    it.each(untouched)("leaves numeric literal %p intact", (value) => {
      expect(buildCsv(["n"], [{ n: value }])).toBe(`n\r\n${value}`);
    });

    it("leaves negative decimal *numbers* (JS number type) intact", () => {
      const csv = buildCsv(["n"], [{ n: -5.5 }, { n: -0.001 }, { n: -1e21 }]);
      expect(csv).toBe("n\r\n-5.5\r\n-0.001\r\n-1e+21");
    });
  });

  // Anything that is not a whole numeric literal but starts with a formula
  // trigger must still be prefixed, even when it *begins* like a number.
  describe("formula-injection guarding is preserved", () => {
    const guarded = [
      "=1+1",
      "=cmd|'/C calc'!A0",
      "+1",
      "+1+1",
      "@SUM(A1)",
      "-cmd",
      "-1+1",
      "-5.5=x",
      "-5abc",
      "-1e", // malformed exponent -> not a number
      "-", // lone dash placeholder: conservatively guarded
      "\t=danger",
      "\r=danger",
    ];
    it.each(guarded)("prefixes dangerous value %j with a single quote", (value) => {
      const csv = buildCsv(["v"], [{ v: value }]);
      const [, line] = csv.split("\r\n");
      // The cell may additionally be quoted if it contains CSV metacharacters;
      // assert only that the neutralising apostrophe is present.
      const cell = line.startsWith('"') ? line.slice(1, -1).replace(/""/g, '"') : line;
      expect(cell.startsWith("'")).toBe(true);
    });
  });

  // Plain text that happens not to be a number and does not start with a
  // formula trigger must pass through with no apostrophe added.
  describe("ordinary text is not over-guarded", () => {
    const passthrough = ["hello", "N/A", "$5", "5%", "5 apples", "1,2,3"];
    it.each(passthrough)("does not prefix %p", (value) => {
      const csv = buildCsv(["v"], [{ v: value }]);
      const [, line] = csv.split("\r\n");
      const cell = line.startsWith('"') ? line.slice(1, -1).replace(/""/g, '"') : line;
      expect(cell.startsWith("'")).toBe(false);
      expect(cell).toBe(value);
    });
  });

  describe("structural edge cases", () => {
    it("emits only a header when there are no rows", () => {
      expect(buildCsv(["a", "b"], [])).toBe("a,b");
    });

    it("emits an empty string when there are no columns and no rows", () => {
      expect(buildCsv([], [])).toBe("");
    });

    it("fills missing keys with empty cells", () => {
      expect(buildCsv(["a", "b"], [{ a: "1" }])).toBe("a,b\r\n1,");
    });

    it("guards a formula-triggering column header", () => {
      expect(buildCsv(["=danger"], [])).toBe("'=danger");
    });

    it("guards and quotes a comma-bearing value that starts like a number", () => {
      // "-5,5" (European decimal text) is not a JS-parseable numeric literal, so
      // it is both formula-guarded (leading '-') and quoted (embedded comma).
      expect(buildCsv(["n"], [{ n: "-5,5" }])).toBe('n\r\n"\'-5,5"');
    });

    it("serialises booleans without guarding", () => {
      expect(buildCsv(["b"], [{ b: true }, { b: false }])).toBe(
        "b\r\ntrue\r\nfalse",
      );
    });
  });
});
