import { render, screen } from "@testing-library/react";
import { ExecuteSqlError } from "graphql/types";
import DataStudioResults from "./DataStudioResults";

// `useTranslation` is globally mocked to echo the key, so assertions target raw
// key strings and rendered structure rather than interpolated/pluralised text.

type Result = NonNullable<
  React.ComponentProps<typeof DataStudioResults>["result"]
>;

const successResult = (overrides: Partial<Result> = {}): Result =>
  ({
    success: true,
    errors: [],
    errorMessage: null,
    columns: ["id", "name"],
    rows: [
      { id: 1, name: "Alice" },
      { id: 2, name: "Bob" },
    ],
    rowCount: 2,
    truncated: false,
    durationMs: 12,
    ...overrides,
  }) as Result;

describe("DataStudioResults", () => {
  it("shows a spinner while loading", () => {
    const { container } = render(<DataStudioResults loading={true} />);
    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows a placeholder when there is no result yet", () => {
    render(<DataStudioResults loading={false} />);
    expect(
      screen.getByText("Results will appear here after you run a query."),
    ).toBeInTheDocument();
  });

  it("renders columns and rows on success", () => {
    render(<DataStudioResults loading={false} result={successResult()} />);
    expect(screen.getByText("id")).toBeInTheDocument();
    expect(screen.getByText("name")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    // Two data rows in the body.
    expect(
      screen.getAllByRole("row").filter((r) => r.closest("tbody")),
    ).toHaveLength(2);
  });

  it("renders NULL for null cell values", () => {
    render(
      <DataStudioResults
        loading={false}
        result={successResult({
          rows: [{ id: 1, name: null }],
          rowCount: 1,
        })}
      />,
    );
    expect(screen.getByText("NULL")).toBeInTheDocument();
  });

  it("maps known error codes to their messages", () => {
    render(
      <DataStudioResults
        loading={false}
        result={successResult({
          success: false,
          errors: [ExecuteSqlError.PermissionDenied],
        })}
      />,
    );
    expect(
      screen.getByText(
        "You don't have permission to run queries on this database.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows the raw error code when it is unknown, plus the error message", () => {
    render(
      <DataStudioResults
        loading={false}
        result={successResult({
          success: false,
          errors: ["SOMETHING_ELSE" as ExecuteSqlError],
          errorMessage: "boom",
        })}
      />,
    );
    expect(screen.getByText("SOMETHING_ELSE")).toBeInTheDocument();
    expect(screen.getByText("boom")).toBeInTheDocument();
  });

  it("shows the truncation banner when the result is truncated", () => {
    render(
      <DataStudioResults
        loading={false}
        result={successResult({ truncated: true })}
      />,
    );
    expect(
      screen.getByText("Results truncated to the first {{count}} rows."),
    ).toBeInTheDocument();
  });

  it("renders EXPLAIN output through the table with a monospace, whitespace-preserving plan column", () => {
    render(
      <DataStudioResults
        loading={false}
        result={successResult({
          columns: ["QUERY PLAN"],
          rows: [
            { "QUERY PLAN": "Sort  (cost=1.00..2.00 rows=1 width=8)" },
            { "QUERY PLAN": "  Sort Key: a.n DESC" },
            {
              "QUERY PLAN": "  ->  Hash Join  (cost=0.50..1.50 rows=1 width=8)",
            },
          ],
          rowCount: 3,
        })}
      />,
    );
    // The plan reuses the results table (row-number gutter + "QUERY PLAN" header).
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByText("QUERY PLAN")).toBeInTheDocument();
    // The plan cell keeps its leading-whitespace indentation and is monospace.
    const cell = screen.getByText(/Hash Join/);
    expect(cell.tagName).toBe("TD");
    expect(cell.textContent).toBe(
      "  ->  Hash Join  (cost=0.50..1.50 rows=1 width=8)",
    );
    expect(cell).toHaveClass("whitespace-pre", "font-mono");
  });

  it("caps the displayed rows at 500 even when more are returned", () => {
    const rows = Array.from({ length: 600 }, (_, i) => ({
      id: i,
      name: `row-${i}`,
    }));
    render(
      <DataStudioResults
        loading={false}
        result={successResult({ rows, rowCount: 600 })}
      />,
    );
    const bodyRows = screen
      .getAllByRole("row")
      .filter((r) => r.closest("tbody"));
    expect(bodyRows).toHaveLength(500);
    // The "showing the first N rows" hint is rendered when rows are hidden.
    expect(
      screen.getByText(
        "Showing the first {{count}} rows — export for the full result.",
      ),
    ).toBeInTheDocument();
  });
});
