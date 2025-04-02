import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  GenerateNewDatabasePasswordDocument,
  useGenerateNewDatabasePasswordMutation,
} from "workspaces/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import GenerateWorkspaceDatabasePasswordDialog from ".";
import { faker } from "@faker-js/faker";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useGenerateNewDatabasePasswordMutation: jest.fn().mockReturnValue([]),
}));

const WORKSPACE = {
  slug: faker.string.uuid(),
};

const useGenerateDatabasePasswordMutationMock =
  useGenerateNewDatabasePasswordMutation as jest.Mock;

describe("GenerateDatabasePasswordDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useGenerateDatabasePasswordMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <GenerateWorkspaceDatabasePasswordDialog
        workspace={WORKSPACE}
        open={false}
        onClose={() => {}}
      />,
    );
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <GenerateWorkspaceDatabasePasswordDialog
          workspace={WORKSPACE}
          open={true}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Generate new database password", async () => {
    const { useGenerateNewDatabasePasswordMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useGenerateDatabasePasswordMutationMock.mockImplementation(
      useGenerateNewDatabasePasswordMutation,
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: GenerateNewDatabasePasswordDocument,
          variables: {
            input: {
              workspaceSlug: WORKSPACE.slug,
            },
          },
        },
        result: {
          data: {
            generateNewDatabasePassword: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={mocks}>
        <GenerateWorkspaceDatabasePasswordDialog
          workspace={WORKSPACE}
          open={true}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const saveButton = screen.getByRole("button", { name: "Replace password" });
    await user.click(saveButton);

    expect(useGenerateDatabasePasswordMutationMock).toHaveBeenCalled();
  });
});
