import { MockedProvider } from "@apollo/client/testing";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";
import { WorkspaceDataStudioSchemaDocument } from "./DataStudioSchemaBrowser.generated";

// `useTranslation` is globally mocked to echo the key; placeholders/labels below
// are therefore the raw key strings (e.g. "Search…", "Insert").

const schemaMock = (
  items: { name: string; columns: { name: string; type: string }[] }[],
  totalItems = items.length,
) => ({
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
            items: items.map((item) => ({
              __typename: "DatabaseTable",
              name: item.name,
              columns: item.columns.map((column) => ({
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

const renderBrowser = (
  mock: ReturnType<typeof schemaMock>,
  onInsert = jest.fn(),
) => {
  render(
    <MockedProvider mocks={[mock]}>
      <DataStudioSchemaBrowser workspaceSlug="ws-1" onInsert={onInsert} />
    </MockedProvider>,
  );
  return { onInsert };
};

const tables = [
  { name: "patients", columns: [{ name: "patient_id", type: "int" }] },
  { name: "visits", columns: [{ name: "visit_date", type: "date" }] },
];

describe("DataStudioSchemaBrowser", () => {
  it("lists the tables returned by the query", async () => {
    renderBrowser(schemaMock(tables));
    expect(await screen.findByText("patients")).toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
  });

  it("filters tables by table name", async () => {
    renderBrowser(schemaMock(tables));
    await screen.findByText("patients");

    await userEvent.type(
      screen.getByPlaceholderText("Search…"),
      "visit",
    );

    expect(screen.queryByText("patients")).not.toBeInTheDocument();
    expect(screen.getByText("visits")).toBeInTheDocument();
  });

  it("filters tables by column name", async () => {
    renderBrowser(schemaMock(tables));
    await screen.findByText("patients");

    await userEvent.type(
      screen.getByPlaceholderText("Search…"),
      "patient_id",
    );

    expect(screen.getByText("patients")).toBeInTheDocument();
    expect(screen.queryByText("visits")).not.toBeInTheDocument();
  });

  it("shows an empty state when nothing matches the search", async () => {
    renderBrowser(schemaMock(tables));
    await screen.findByText("patients");

    await userEvent.type(
      screen.getByPlaceholderText("Search…"),
      "nomatch",
    );

    expect(screen.getByText("No tables")).toBeInTheDocument();
  });

  it("reveals columns when a table is expanded", async () => {
    renderBrowser(schemaMock(tables));
    const patients = await screen.findByText("patients");

    expect(screen.queryByText("patient_id")).not.toBeInTheDocument();
    await userEvent.click(patients);
    expect(screen.getByText("patient_id")).toBeInTheDocument();
  });

  it("calls onInsert with the table name", async () => {
    const { onInsert } = renderBrowser(schemaMock([tables[0]]));
    await screen.findByText("patients");

    await userEvent.click(screen.getByText("Insert"));
    expect(onInsert).toHaveBeenCalledWith("patients");
  });

  it("calls onInsert with the column name from an expanded table", async () => {
    const { onInsert } = renderBrowser(schemaMock([tables[0]]));
    const patients = await screen.findByText("patients");

    await userEvent.click(patients);
    await userEvent.click(screen.getByText("patient_id"));
    expect(onInsert).toHaveBeenCalledWith("patient_id");
  });

  it("shows the 'more tables' notice when totalItems exceeds the loaded page", async () => {
    renderBrowser(schemaMock(tables, 150));
    await screen.findByText("patients");
    expect(
      screen.getByText("Showing the first {{count}} tables."),
    ).toBeInTheDocument();
  });
});
