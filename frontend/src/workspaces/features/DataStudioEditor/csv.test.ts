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
});
