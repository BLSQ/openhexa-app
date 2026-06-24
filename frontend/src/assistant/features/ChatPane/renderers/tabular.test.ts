import { findTabularArray } from "./tabular";

describe("findTabularArray", () => {
  it("returns a bare array of objects", () => {
    const rows = [{ a: 1 }, { a: 2 }];
    expect(findTabularArray(rows)).toBe(rows);
  });

  it("unwraps a pagination page (items)", () => {
    const items = [{ id: 1 }];
    expect(findTabularArray({ items, totalItems: 1, pageNumber: 1 })).toBe(items);
  });

  it("follows single-key GraphQL nesting", () => {
    const items = [{ code: "p1" }];
    expect(findTabularArray({ pipelines: { items, totalPages: 1 } })).toBe(items);
    const connections = [{ slug: "s3" }];
    expect(findTabularArray({ workspace: { connections } })).toBe(connections);
  });

  it("ignores multi-field detail objects so they stay JSON", () => {
    expect(
      findTabularArray({ id: "x", name: "Pipeline", versions: [{ n: 1 }] }),
    ).toBeNull();
  });

  it("returns null for empty arrays and scalars", () => {
    expect(findTabularArray([])).toBeNull();
    expect(findTabularArray("hello")).toBeNull();
    expect(findTabularArray({ items: [] })).toBeNull();
  });
});
