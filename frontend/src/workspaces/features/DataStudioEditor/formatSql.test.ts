import { formatSql } from "./formatSql";

describe("formatSql", () => {
  it("breaks a one-liner into indented clauses and uppercases keywords", () => {
    expect(formatSql("select id, name from patients where age > 10")).toEqual(
      [
        "SELECT",
        "  id,",
        "  name",
        "FROM",
        "  patients",
        "WHERE",
        "  age > 10",
      ].join("\n"),
    );
  });

  it("is idempotent", () => {
    const once = formatSql("select id from patients where age > 10");
    expect(formatSql(once)).toEqual(once);
  });

  it("understands PostgreSQL-only syntax", () => {
    expect(formatSql("select id::text from patients")).toContain("::text");
  });

  it("returns a half-typed query untouched rather than mangling it", () => {
    const partial = "select from where ((";
    expect(formatSql(partial)).toEqual(partial);
  });

  it("leaves an empty query empty", () => {
    expect(formatSql("")).toEqual("");
  });
});
