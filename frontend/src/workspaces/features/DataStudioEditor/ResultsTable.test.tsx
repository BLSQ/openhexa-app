import { render, screen } from "@testing-library/react";
import ResultsTable from "./ResultsTable";

describe("ResultsTable", () => {
  it("renders a row-number gutter, headers and cells", () => {
    render(
      <ResultsTable
        columns={["name"]}
        rows={[{ name: "Alice" }, { name: "Bob" }]}
      />,
    );
    expect(screen.getByText("name")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    // Row-number gutter is 1-based (values here are non-numeric so 1/2 are
    // unambiguously the gutter).
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("renders NULL for null cell values", () => {
    render(<ResultsTable columns={["name"]} rows={[{ name: null }]} />);
    expect(screen.getByText("NULL")).toBeInTheDocument();
  });

  it("right-aligns numeric cells with a monospace font", () => {
    render(<ResultsTable columns={["n"]} rows={[{ n: 42 }]} />);
    const cell = screen.getByText("42");
    expect(cell).toHaveClass("text-right", "font-mono");
  });

  it("appends per-column classes from columnClassName", () => {
    render(
      <ResultsTable
        columns={["QUERY PLAN"]}
        rows={[{ "QUERY PLAN": "  ->  Seq Scan" }]}
        columnClassName={{ "QUERY PLAN": "whitespace-pre font-mono" }}
      />,
    );
    const cell = screen.getByText(/Seq Scan/);
    expect(cell.textContent).toBe("  ->  Seq Scan");
    expect(cell).toHaveClass("whitespace-pre", "font-mono");
  });
});
