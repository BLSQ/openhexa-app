import { ApolloError } from "@apollo/client";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ExecuteSqlError } from "graphql/types";
import DataStudioResults from "./DataStudioResults";

// MapLibre needs a WebGL context and real layout, neither of which jsdom
// provides. Choosing the map and handing it the right features is this
// component's job; drawing it is the map's, so the map is stubbed down to what
// it was asked to render.
jest.mock("./ResultsMap", () => ({
  __esModule: true,
  default: ({ features }: { features: unknown[] }) => (
    <div data-testid="results-map">{features.length}</div>
  ),
}));

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

  const serverNetworkError = (statusCode: number) => {
    const e = new Error("Server responded with an error") as Error & {
      statusCode: number;
    };
    e.name = "ServerError";
    e.statusCode = statusCode;
    return e;
  };

  it("shows a size hint for a request-too-large (413) transport error", () => {
    render(
      <DataStudioResults
        loading={false}
        error={new ApolloError({ networkError: serverNetworkError(413) })}
      />,
    );
    expect(
      screen.getByText(
        "The query or its result is too large. Try lowering the maximum number of rows or narrowing your query.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows a connection message when the request never reached the server", () => {
    render(
      <DataStudioResults
        loading={false}
        error={new ApolloError({ networkError: new Error("Failed to fetch") })}
      />,
    );
    expect(
      screen.getByText(
        "Couldn't reach the server. Check your connection and try again.",
      ),
    ).toBeInTheDocument();
  });

  it("shows a generic message for a server-side (GraphQL) error and exposes the raw message", () => {
    render(
      <DataStudioResults
        loading={false}
        error={new ApolloError({ graphQLErrors: [{ message: "boom" } as any] })}
      />,
    );
    expect(
      screen.getByText(
        "Something went wrong while running your query. Please try again.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("boom")).toBeInTheDocument();
  });

  it("fires onRetry when the Retry button is clicked", async () => {
    const onRetry = jest.fn();
    render(
      <DataStudioResults
        loading={false}
        error={new ApolloError({ networkError: new Error("Failed to fetch") })}
        onRetry={onRetry}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("prefers the transport error over the empty placeholder", () => {
    render(
      <DataStudioResults
        loading={false}
        error={new ApolloError({ networkError: new Error("Failed to fetch") })}
      />,
    );
    expect(
      screen.queryByText("Results will appear here after you run a query."),
    ).not.toBeInTheDocument();
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

  describe("widgets", () => {
    const barResult = () =>
      successResult({
        columns: ["bar_label", "bar_quantity"],
        rows: [
          { bar_label: "Gasabo", bar_quantity: 120 },
          { bar_label: "Kicukiro", bar_quantity: 80 },
        ],
      });

    it("shows the chart first and the table on a second tab when the columns match a widget", async () => {
      render(<DataStudioResults loading={false} result={barResult()} />);

      expect(screen.getByRole("tab", { name: "Chart" })).toHaveAttribute(
        "aria-selected",
        "true",
      );
      // The chart is showing, so the table is not rendered yet.
      expect(screen.queryByRole("table")).not.toBeInTheDocument();
      expect(screen.getByText("Gasabo")).toBeInTheDocument();

      await userEvent.click(screen.getByRole("tab", { name: "Table" }));
      expect(screen.getByRole("table")).toBeInTheDocument();
      expect(screen.getByText("bar_quantity")).toBeInTheDocument();
    });

    it("renders a plain table with no tabs when the columns do not match", () => {
      render(<DataStudioResults loading={false} result={successResult()} />);
      expect(screen.getByRole("table")).toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Chart" }),
      ).not.toBeInTheDocument();
    });

    it("charts a result that returns extra columns beside the widget pair", async () => {
      render(
        <DataStudioResults
          loading={false}
          result={successResult({
            columns: ["bar_label", "bar_quantity", "region"],
            rows: [
              { bar_label: "Gasabo", bar_quantity: 120, region: "Kigali" },
            ],
            rowCount: 1,
          })}
        />,
      );
      expect(screen.getByRole("tab", { name: "Chart" })).toHaveAttribute(
        "aria-selected",
        "true",
      );

      await userEvent.click(screen.getByRole("tab", { name: "Table" }));
      expect(screen.getByText("region")).toBeInTheDocument();
    });

    it("falls back to the table when a widget column holds non-numeric values", () => {
      render(
        <DataStudioResults
          loading={false}
          result={successResult({
            columns: ["bar_label", "bar_quantity"],
            rows: [{ bar_label: "Gasabo", bar_quantity: "many" }],
            rowCount: 1,
          })}
        />,
      );
      expect(screen.getByRole("table")).toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Chart" }),
      ).not.toBeInTheDocument();
    });

    it("charts every returned row rather than the 500-row table cap", () => {
      const rows = Array.from({ length: 600 }, (_, i) => ({
        line_x: `2026-${i}`,
        line_y: i,
      }));
      render(
        <DataStudioResults
          loading={false}
          result={successResult({
            columns: ["line_x", "line_y"],
            rows,
            rowCount: 600,
          })}
        />,
      );
      // The last point's label is only reachable if all 600 rows were plotted.
      expect(screen.getByText("2026-599")).toBeInTheDocument();
      expect(
        screen.queryByText(
          "Showing the first {{count}} rows — export for the full result.",
        ),
      ).not.toBeInTheDocument();
    });

    describe("discoverability hint", () => {
      const hint = () =>
        screen.queryByRole("link", { name: "Visualize this result" });

      it("points a plain result at the widget guide", () => {
        render(<DataStudioResults loading={false} result={successResult()} />);
        expect(hint()).toHaveAttribute(
          "href",
          "https://docs.openhexa.com/sql-widgets/",
        );
      });

      it("names the columns of every widget on hover", async () => {
        render(<DataStudioResults loading={false} result={successResult()} />);

        await userEvent.hover(hint()!);

        expect(screen.getByText("bar_label, bar_quantity")).toBeInTheDocument();
        expect(screen.getByText("line_x, line_y")).toBeInTheDocument();
        expect(screen.getByText("pie_label, pie_quantity")).toBeInTheDocument();
        expect(
          screen.getByText("map_latitude, map_longitude"),
        ).toBeInTheDocument();
        expect(screen.getByText("map_geometry")).toBeInTheDocument();
      });

      it("is not offered on a result that is already charted", () => {
        render(<DataStudioResults loading={false} result={barResult()} />);
        expect(hint()).not.toBeInTheDocument();
      });

      it("is not offered on a result that is already mapped", () => {
        render(
          <DataStudioResults
            loading={false}
            result={successResult({
              columns: ["map_latitude", "map_longitude"],
              rows: [{ map_latitude: 5.34, map_longitude: -4.02 }],
              rowCount: 1,
            })}
          />,
        );
        expect(hint()).not.toBeInTheDocument();
      });

      it("is not offered on an EXPLAIN plan, which is never chartable", () => {
        render(
          <DataStudioResults
            loading={false}
            result={successResult({
              columns: ["QUERY PLAN"],
              rows: [{ "QUERY PLAN": "Seq Scan on cases" }],
              rowCount: 1,
            })}
          />,
        );
        expect(hint()).not.toBeInTheDocument();
      });
    });
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

  describe("map view", () => {
    const located = (overrides: Partial<Result> = {}) =>
      successResult({
        columns: ["name", "map_latitude", "map_longitude"],
        rows: [
          { name: "Diogo", map_latitude: 5.34, map_longitude: -4.02 },
          { name: "Boundiali", map_latitude: 9.52, map_longitude: -6.48 },
        ],
        rowCount: 2,
        ...overrides,
      });

    it("shows a located result on a map rather than as a table", async () => {
      render(<DataStudioResults loading={false} result={located()} />);

      expect(await screen.findByTestId("results-map")).toHaveTextContent("2");
      expect(screen.queryByRole("table")).not.toBeInTheDocument();
      expect(screen.getByRole("tab", { name: "Map" })).toBeInTheDocument();
    });

    it("maps only a result that opted in through the column names", () => {
      render(
        <DataStudioResults
          loading={false}
          result={successResult({
            columns: ["name", "latitude", "longitude"],
            rows: [{ name: "Diogo", latitude: 5.34, longitude: -4.02 }],
            rowCount: 1,
          })}
        />,
      );
      expect(screen.queryByRole("tab")).not.toBeInTheDocument();
    });

    it("keeps the full result reachable through the table tab", async () => {
      render(<DataStudioResults loading={false} result={located()} />);

      await userEvent.click(screen.getByRole("tab", { name: "Table" }));

      expect(screen.getByRole("table")).toBeInTheDocument();
      expect(screen.getByText("Diogo")).toBeInTheDocument();
    });

    it("offers no map for a result that has no geography", () => {
      render(<DataStudioResults loading={false} result={successResult()} />);
      expect(screen.queryByRole("tab")).not.toBeInTheDocument();
    });

    it("says how to convert a geometry column it cannot draw", async () => {
      render(
        <DataStudioResults
          loading={false}
          result={successResult({
            columns: ["map_geometry"],
            rows: [
              {
                map_geometry:
                  "0101000020E6100000B81E85EB51101040295C8FC2F5A81440",
              },
            ],
            rowCount: 1,
          })}
        />,
      );

      expect(
        await screen.findByText(/ST_AsGeoJSON\(map_geometry\)/),
      ).toBeInTheDocument();
      expect(screen.queryByTestId("results-map")).not.toBeInTheDocument();
    });

    it("never maps an EXPLAIN plan, whose single column is not a geography", () => {
      render(
        <DataStudioResults
          loading={false}
          result={successResult({
            columns: ["QUERY PLAN"],
            rows: [{ "QUERY PLAN": "Seq Scan on cases" }],
            rowCount: 1,
          })}
        />,
      );
      expect(screen.queryByRole("tab")).not.toBeInTheDocument();
    });
  });
});
