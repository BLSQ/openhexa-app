import { MockedProvider, MockedResponse } from "@apollo/client/testing";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";
import { WorkspaceDataStudioSchemaDocument } from "./DataStudioSchemaBrowser.generated";

// `useTranslation` is globally mocked to echo the key; placeholders/labels below
// are therefore the raw key strings (e.g. "Search…", "Insert").

type TableSpec = {
  name: string;
  columns?: { name: string; type: string }[];
};

const schemaMock = (tables: TableSpec[], totalItems = tables.length) => ({
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
            items: tables.map((table) => ({
              __typename: "DatabaseTable",
              name: table.name,
              columns: (table.columns ?? []).map((column) => ({
                __typename: "TableColumn",
                ...column,
              })),
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
    renderBrowser([schemaMock([{ name: "patients" }, { name: "visits" }])]);
    expect(await screen.findByText("patients")).toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
  });

  it("filters tables by table name", async () => {
    renderBrowser([schemaMock([{ name: "patients" }, { name: "visits" }])]);
    await screen.findByText("patients");

    await userEvent.click(screen.getByTitle("Search tables & columns"));
    await userEvent.type(
      screen.getByPlaceholderText("Search tables & columns…"),
      "visit",
    );

    expect(screen.queryByText("patients")).not.toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
  });

  it("filters tables by column name and reveals the matching column", async () => {
    renderBrowser([
      schemaMock([
        { name: "patients", columns: [{ name: "patient_id", type: "int" }] },
        { name: "visits", columns: [{ name: "visit_date", type: "date" }] },
      ]),
    ]);
    await screen.findByText("patients");

    await userEvent.click(screen.getByTitle("Search tables & columns"));
    await userEvent.type(
      screen.getByPlaceholderText("Search tables & columns…"),
      "visit_date",
    );

    expect(screen.queryByText("patients")).not.toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
    // The table only matches through its column, so it is auto-expanded.
    expect(screen.getByText("visit_date")).toBeInTheDocument();
  });

  it("shows an empty state when nothing matches the search", async () => {
    renderBrowser([schemaMock([{ name: "patients" }, { name: "visits" }])]);
    await screen.findByText("patients");

    await userEvent.click(screen.getByTitle("Search tables & columns"));
    await userEvent.type(
      screen.getByPlaceholderText("Search tables & columns…"),
      "nomatch",
    );

    expect(screen.getByText("No tables")).toBeInTheDocument();
  });

  it("collapses the search and clears the filter when closed", async () => {
    renderBrowser([schemaMock([{ name: "patients" }, { name: "visits" }])]);
    await screen.findByText("patients");

    await userEvent.click(screen.getByTitle("Search tables & columns"));
    await userEvent.type(
      screen.getByPlaceholderText("Search tables & columns…"),
      "visit",
    );
    expect(screen.queryByText("patients")).not.toBeInTheDocument();

    await userEvent.click(screen.getByTitle("Close search"));

    expect(
      screen.queryByPlaceholderText("Search tables & columns…"),
    ).not.toBeInTheDocument();
    expect(screen.getByText("patients")).toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
  });

  it("reveals columns only when a table is expanded", async () => {
    renderBrowser([
      schemaMock([
        { name: "patients", columns: [{ name: "patient_id", type: "int" }] },
      ]),
    ]);
    const patients = await screen.findByText("patients");

    expect(screen.queryByText("patient_id")).not.toBeInTheDocument();
    await userEvent.click(patients);
    expect(screen.getByText("patient_id")).toBeInTheDocument();
  });

  it("calls onInsert with the table name", async () => {
    const { onInsert } = renderBrowser([schemaMock([{ name: "patients" }])]);
    await screen.findByText("patients");

    await userEvent.click(screen.getByText("Insert"));
    expect(onInsert).toHaveBeenCalledWith("patients");
  });

  it("calls onInsert with the column name from an expanded table", async () => {
    const { onInsert } = renderBrowser([
      schemaMock([
        { name: "patients", columns: [{ name: "patient_id", type: "int" }] },
      ]),
    ]);
    const patients = await screen.findByText("patients");

    await userEvent.click(patients);
    await userEvent.click(screen.getByText("patient_id"));
    expect(onInsert).toHaveBeenCalledWith("patient_id");
  });

  it("shows the 'more tables' notice when totalItems exceeds the loaded page", async () => {
    renderBrowser([
      schemaMock([{ name: "patients" }, { name: "visits" }], 150),
    ]);
    await screen.findByText("patients");
    expect(
      screen.getByText("Showing the first {{count}} tables."),
    ).toBeInTheDocument();
  });
});
