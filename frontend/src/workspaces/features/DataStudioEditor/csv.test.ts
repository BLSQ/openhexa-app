import { buildCsv } from "./csv";

describe("buildCsv", () => {
  it("writes a header row followed by one line per row", () => {
    const csv = buildCsv(
      ["id", "name"],
      [
        { id: 1, name: "Alice" },
        { id: 2, name: "Bob" },
      ],
    );
    expect(csv).toBe("id,name\n1,Alice\n2,Bob");
  });

  it("orders cells by the column list and ignores extra keys", () => {
    const csv = buildCsv(["b", "a"], [{ a: "1", b: "2", c: "3" }]);
    expect(csv).toBe("b,a\n2,1");
  });

  it("serialises null/undefined to empty cells and objects to JSON", () => {
    const csv = buildCsv(
      ["a", "b", "c"],
      [{ a: null, b: undefined, c: { x: 1 } }],
    );
    expect(csv).toBe('a,b,c\n,,"{""x"":1}"');
  });

  it("quotes and escapes values containing commas, quotes or newlines", () => {
    const csv = buildCsv(
      ["text"],
      [{ text: "a,b" }, { text: 'say "hi"' }, { text: "line1\nline2" }],
    );
    expect(csv).toBe('text\n"a,b"\n"say ""hi"""\n"line1\nline2"');
  });

  it("neutralises formula-injection in string cells", () => {
    const csv = buildCsv(
      ["v"],
      [{ v: "=1+1" }, { v: "+1" }, { v: "@cmd" }, { v: "-cmd" }],
    );
    expect(csv).toBe("v\n'=1+1\n'+1\n'@cmd\n'-cmd");
  });

  it("does not alter negative numbers, which are not an injection risk", () => {
    const csv = buildCsv(["n"], [{ n: -5 }]);
    expect(csv).toBe("n\n-5");
  });
});
