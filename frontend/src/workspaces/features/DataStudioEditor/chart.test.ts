import {
  chartKey,
  detectChart,
  formatNumber,
  niceTicks,
  toPoints,
} from "./chart";

describe("chartKey", () => {
  it("sorts column names alphabetically and joins them with hyphens", () => {
    expect(chartKey(["bar_quantity", "bar_label"])).toBe(
      "bar_label-bar_quantity",
    );
  });
});

describe("detectChart", () => {
  const barRows = [
    { bar_label: "Gasabo", bar_quantity: 12 },
    { bar_label: "Kicukiro", bar_quantity: 8 },
  ];

  it("resolves each of the three charts from its column names", () => {
    expect(detectChart(["bar_label", "bar_quantity"], barRows)).toBe("bar");
    expect(
      detectChart(["line_x", "line_y"], [{ line_x: "2026-01", line_y: 3 }]),
    ).toBe("line");
    expect(
      detectChart(
        ["pie_label", "pie_quantity"],
        [{ pie_label: "a", pie_quantity: 1 }],
      ),
    ).toBe("pie");
  });

  it("does not depend on the order the columns are returned in", () => {
    expect(detectChart(["bar_quantity", "bar_label"], barRows)).toBe("bar");
  });

  it("falls back to the table when an extra column is returned", () => {
    expect(
      detectChart(
        ["bar_label", "bar_quantity", "region"],
        barRows.map((row) => ({ ...row, region: "North" })),
      ),
    ).toBeNull();
  });

  it("falls back to the table when the value column is not numeric", () => {
    expect(
      detectChart(
        ["bar_label", "bar_quantity"],
        [{ bar_label: "Gasabo", bar_quantity: "many" }],
      ),
    ).toBeNull();
  });

  it("accepts numeric values Postgres serialises as strings", () => {
    expect(
      detectChart(
        ["bar_label", "bar_quantity"],
        [{ bar_label: "Gasabo", bar_quantity: "12.5" }],
      ),
    ).toBe("bar");
  });

  it("tolerates null values as long as some row has a number", () => {
    expect(
      detectChart(
        ["bar_label", "bar_quantity"],
        [
          { bar_label: "Gasabo", bar_quantity: null },
          { bar_label: "Kicukiro", bar_quantity: 8 },
        ],
      ),
    ).toBe("bar");
  });

  it("returns null for an unknown column set and for no rows", () => {
    expect(detectChart(["id", "name"], [{ id: 1, name: "a" }])).toBeNull();
    expect(detectChart(["bar_label", "bar_quantity"], [])).toBeNull();
  });
});

describe("toPoints", () => {
  const rows = [
    { bar_label: "a", bar_quantity: 3 },
    { bar_label: "b", bar_quantity: "7" },
    { bar_label: "c", bar_quantity: "n/a" },
    { bar_label: null, bar_quantity: 1 },
  ];

  it("keeps the order the query returned, drops non-numeric rows and labels blanks", () => {
    const { points } = toPoints("bar", rows, 10);
    expect(points).toEqual([
      { label: "a", value: 3 },
      { label: "b", value: 7 },
      { label: "—", value: 1 },
    ]);
  });

  it("caps the points and reports how many were left out", () => {
    const { points, hidden } = toPoints("bar", rows, 2);
    expect(points).toHaveLength(2);
    expect(hidden).toBe(1);
  });
});

describe("niceTicks", () => {
  it("produces round numbers inside the domain", () => {
    expect(niceTicks(0, 100)).toEqual([0, 20, 40, 60, 80, 100]);
    expect(niceTicks(0, 10)).toEqual([0, 2, 4, 6, 8, 10]);
  });

  it("keeps the closing tick that float drift would otherwise push out of range", () => {
    expect(niceTicks(0, 1)).toEqual([0, 0.2, 0.4, 0.6, 0.8, 1]);
  });

  it("returns a single tick for a flat domain", () => {
    expect(niceTicks(5, 5)).toEqual([5]);
  });
});

describe("formatNumber", () => {
  it("keeps integers whole and limits fraction digits", () => {
    expect(formatNumber(1234)).toBe("1,234");
    expect(formatNumber(3.14159)).toBe("3.14");
  });
});
