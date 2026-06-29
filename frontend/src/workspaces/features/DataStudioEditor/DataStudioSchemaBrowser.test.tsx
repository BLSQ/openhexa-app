import { MockedProvider, MockedResponse } from "@apollo/client/testing";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";
import {
  WorkspaceDataStudioSchemaDocument,
  WorkspaceDataStudioTableColumnsDocument,
} from "./DataStudioSchemaBrowser.generated";

// `useTranslation` is globally mocked to echo the key; placeholders/labels below
// are therefore the raw key strings (e.g. "Search…", "Insert").

const schemaMock = (names: string[], totalItems = names.length) => ({
  request: {
    query: WorkspaceDataStudioSchemaDocument,
    variables: { workspaceSlug: "ws-1" },
  },
  result: {
    data: {
      workspace: {
        __typename: "Workspace",
        slug: "ws-1",
        database: {
          __typename: "Database",
          tables: {
            __typename: "DatabaseTablePage",
            totalItems,
            items: names.map((name) => ({
              __typename: "DatabaseTable",
              name,
            })),
          },
        },
      },
    },
  },
});

const tableColumnsMock = (
  name: string,
  columns: { name: string; type: string }[],
) => ({
  request: {
    query: WorkspaceDataStudioTableColumnsDocument,
    variables: { workspaceSlug: "ws-1", table: name },
  },
  result: {
    data: {
      workspace: {
        __typename: "Workspace",
        slug: "ws-1",
        database: {
          __typename: "Database",
          table: {
            __typename: "DatabaseTable",
            name,
            columns: columns.map((column) => ({
              __typename: "TableColumn",
              ...column,
            })),
          },
        },
      },
    },
  },
});

const renderBrowser = (mocks: MockedResponse[], onInsert = jest.fn()) => {
  render(
    <MockedProvider mocks={mocks}>
      <DataStudioSchemaBrowser workspaceSlug="ws-1" onInsert={onInsert} />
    </MockedProvider>,
  );
  return { onInsert };
};

describe("DataStudioSchemaBrowser", () => {
  it("lists the tables returned by the query", async () => {
    renderBrowser([schemaMock(["patients", "visits"])]);
    expect(await screen.findByText("patients")).toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
  });

  it("filters tables by table name", async () => {
    renderBrowser([schemaMock(["patients", "visits"])]);
    await screen.findByText("patients");

    await userEvent.type(screen.getByPlaceholderText("Search…"), "visit");

    expect(screen.queryByText("patients")).not.toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
  });

  it("shows an empty state when nothing matches the search", async () => {
    renderBrowser([schemaMock(["patients", "visits"])]);
    await screen.findByText("patients");

    await userEvent.type(screen.getByPlaceholderText("Search…"), "nomatch");

    expect(screen.getByText("No tables")).toBeInTheDocument();
  });

  it("loads and reveals columns only when a table is expanded", async () => {
    renderBrowser([
      schemaMock(["patients"]),
      tableColumnsMock("patients", [{ name: "patient_id", type: "int" }]),
    ]);
    const patients = await screen.findByText("patients");

    expect(screen.queryByText("patient_id")).not.toBeInTheDocument();
    await userEvent.click(patients);
    expect(await screen.findByText("patient_id")).toBeInTheDocument();
  });

  it("calls onInsert with the table name", async () => {
    const { onInsert } = renderBrowser([schemaMock(["patients"])]);
    await screen.findByText("patients");

    await userEvent.click(screen.getByText("Insert"));
    expect(onInsert).toHaveBeenCalledWith("patients");
  });

  it("calls onInsert with the column name from an expanded table", async () => {
    const { onInsert } = renderBrowser([
      schemaMock(["patients"]),
      tableColumnsMock("patients", [{ name: "patient_id", type: "int" }]),
    ]);
    const patients = await screen.findByText("patients");

    await userEvent.click(patients);
    await userEvent.click(await screen.findByText("patient_id"));
    expect(onInsert).toHaveBeenCalledWith("patient_id");
  });

  it("shows the 'more tables' notice when totalItems exceeds the loaded page", async () => {
    renderBrowser([schemaMock(["patients", "visits"], 150)]);
    await screen.findByText("patients");
    expect(
      screen.getByText("Showing the first {{count}} tables."),
    ).toBeInTheDocument();
  });
});
