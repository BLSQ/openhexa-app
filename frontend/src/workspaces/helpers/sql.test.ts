import { sanitizeSqlWhitespace } from "./sql";

const NBSP = "\u00a0";
const ZWSP = "\u200b";
const BOM = "\ufeff";

describe("sanitizeSqlWhitespace", () => {
  it.each([
    ["non-breaking space", NBSP],
    ["ideographic space", "\u3000"],
    ["thin space", "\u2009"],
    ["narrow non-breaking space", "\u202f"],
    ["line separator", "\u2028"],
    ["vertical tab", "\v"],
  ])("replaces a %s with a plain space", (_label, blank) => {
    expect(sanitizeSqlWhitespace(`SELECT${blank}1`)).toBe("SELECT 1");
  });

  it.each([
    ["zero-width space", ZWSP],
    ["byte order mark", BOM],
    ["word joiner", "\u2060"],
    ["soft hyphen", "\u00ad"],
  ])("removes a %s", (_label, invisible) => {
    expect(sanitizeSqlWhitespace(`SELECT${invisible} 1`)).toBe("SELECT 1");
  });

  it("keeps the whitespace PostgreSQL accepts", () => {
    const sql = "SELECT\t1,\r\n\f  2 FROM t";
    expect(sanitizeSqlWhitespace(sql)).toBe(sql);
  });

  it.each([
    ["string literal", `SELECT 'a${NBSP}b' AS x`],
    ["escaped quote in a literal", `SELECT 'it''s${NBSP}here' AS x`],
    ["quoted identifier", `SELECT 1 AS "col${NBSP}x"`],
    ["dollar-quoted body", `SELECT $tag$a${NBSP}b$tag$`],
    ["line comment", `-- note${NBSP}here\nSELECT 1`],
    ["block comment", `/* note${ZWSP}here */ SELECT 1`],
    ["accented identifier", "SELECT 'héllo' AS café"],
  ])("leaves a %s verbatim", (_label, sql) => {
    expect(sanitizeSqlWhitespace(sql)).toBe(sql);
  });

  it("cleans around a verbatim region", () => {
    expect(sanitizeSqlWhitespace(`SELECT${NBSP}'a${NBSP}b'${NBSP}AS x`)).toBe(
      `SELECT 'a${NBSP}b' AS x`,
    );
  });

  it("cleans up to the end of an unterminated literal", () => {
    expect(sanitizeSqlWhitespace(`SELECT${NBSP}'a${NBSP}b`)).toBe(
      `SELECT 'a${NBSP}b`,
    );
  });

  it("is idempotent", () => {
    const once = sanitizeSqlWhitespace(
      `SELECT${NBSP}'a${NBSP}b'${ZWSP} FROM t`,
    );
    expect(sanitizeSqlWhitespace(once)).toBe(once);
  });

  it("returns text without anything to clean unchanged", () => {
    const sql = "SELECT id, label FROM demo ORDER BY id";
    expect(sanitizeSqlWhitespace(sql)).toBe(sql);
    expect(sanitizeSqlWhitespace("")).toBe("");
  });
});
