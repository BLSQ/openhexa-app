import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { OrderByDirection } from "graphql/types";
import DatabaseTableDataGrid from "./DatabaseTableDataGrid";
import { useDatabaseTableDataGridQuery } from "./DatabaseTableDataGrid.generated";

jest.mock("./DatabaseTableDataGrid.generated", () => ({
  ...jest.requireActual("./DatabaseTableDataGrid.generated"),
  useDatabaseTableDataGridQuery: jest.fn(),
}));

const useQueryMock = useDatabaseTableDataGridQuery as jest.Mock;

const renderGrid = (items: Record<string, unknown>[]) => {
  useQueryMock.mockReturnValue({
    data: {
      workspace: {
        slug: "ws",
        database: {
          table: {
            rows: {
              pageNumber: 1,
              hasNextPage: false,
              hasPreviousPage: false,
              items,
            },
          },
        },
      },
    },
  });

  return render(
    <TestApp>
      <DatabaseTableDataGrid
        table={{ name: "logs", columns: [{ name: "id" }, { name: "payload" }] }}
        workspace={{ slug: "ws" }}
        columns={[
          { name: "id", type: "integer" },
          { name: "payload", type: "jsonb" },
        ]}
        orderBy="id"
        direction={OrderByDirection.Desc}
        page={1}
        onChange={jest.fn()}
      />
    </TestApp>,
  );
};

describe("DatabaseTableDataGrid", () => {
  it("renders object cell values as JSON", () => {
    renderGrid([{ id: 1, payload: { qc11: true, etat_stock: "ok" } }]);

    expect(
      screen.getByText('{"qc11":true,"etat_stock":"ok"}'),
    ).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  it("renders array cell values as JSON", () => {
    renderGrid([{ id: 1, payload: ["a", "b"] }]);

    expect(screen.getByText('["a","b"]')).toBeInTheDocument();
  });

  it("keeps the default placeholder for null values", () => {
    renderGrid([{ id: 1, payload: null }]);

    expect(screen.getByText("-")).toBeInTheDocument();
  });
});
