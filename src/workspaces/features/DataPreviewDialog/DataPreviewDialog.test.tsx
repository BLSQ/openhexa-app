import DataPreviewDialog from "./DataPreviewDialog";
import { render, screen } from "@testing-library/react";
import { faker } from "@faker-js/faker";
import { TestApp, waitForDialog } from "core/helpers/testutils";
import { WorkspaceDatabaseTableDataDocument } from "./DataPreviewDialog.generated";

const WORKSPACE = {
  slug: faker.commerce.productName(),
};

describe("DataPreviewDialog", () => {
  const onClose = jest.fn();

  it("is not displayed ", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <DataPreviewDialog
          workspaceSlug={WORKSPACE.slug}
          open={false}
          tableName="test"
          onClose={onClose}
        />
      </TestApp>
    );
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
  });

  it("displays table data", async () => {
    const sample = [
      {
        id: "f9d1fcfc-6846-4823-8e5a-39b96b9c0a91",
        region: "REG1",
        count: 10,
      },
      {
        id: "3f654d6f-b95a-4796-93df-1756a1065f5b",
        region: "REG2",
        count: 13,
      },
      {
        id: "701a61ae-23c9-4edd-9920-31aba81a0785",
        region: "REG3",
        count: 0,
      },
      {
        id: "3ccbf1bf-7cc0-4cb9-9d31-16b1b3afb1dc",
        region: "REG4",
        count: 34,
      },
    ];
    const graphqlMocks = [
      {
        request: {
          query: WorkspaceDatabaseTableDataDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
            tableName: "test_table",
          },
        },
        result: {
          data: {
            workspace: {
              slug: WORKSPACE.slug,
              database: {
                table: {
                  columns: [
                    {
                      name: "id",
                      type: "uuid",
                    },
                    {
                      name: "region",
                      type: "character varying",
                    },
                    {
                      name: "count",
                      type: "integer",
                    },
                  ],
                  sample,
                },
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <DataPreviewDialog
          workspaceSlug={WORKSPACE.slug}
          open={true}
          tableName="test_table"
          onClose={onClose}
        />
      </TestApp>
    );
    await waitForDialog();

    const elm = await screen.getByText("Sample data for {{name}}", {
      selector: "h3",
    });
    expect(elm).toBeInTheDocument();
    sample.forEach((s) => {
      expect(screen.queryByText(s.id)).toBeInTheDocument();
    });
  });
});
