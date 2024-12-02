import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  UpdateWorkspaceDocument,
  useUpdateWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import WorkspaceDescriptionDialog from "./UpdateDescriptionDialog";
import { faker } from "@faker-js/faker";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useUpdateWorkspaceMutation: jest.fn().mockReturnValue([]),
}));

const WORKSPACE = {
  slug: faker.string.uuid(),
  name: faker.commerce.productName(),
};

const useUpdateWorkspaceMutationMock = useUpdateWorkspaceMutation as jest.Mock;

describe("EditWorkspaceDescriptionDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useUpdateWorkspaceMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <WorkspaceDescriptionDialog
        workspace={WORKSPACE}
        open={false}
        onClose={() => {}}
      />,
    );
    const dialog = screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <WorkspaceDescriptionDialog
          workspace={WORKSPACE}
          open={true}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const dialog = screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Edit workspace description", async () => {
    const { useUpdateWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useUpdateWorkspaceMutationMock.mockImplementation(
      useUpdateWorkspaceMutation,
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: UpdateWorkspaceDocument,
          variables: {
            input: {
              slug: WORKSPACE.slug,
            },
          },
        },
        result: {
          data: {
            update: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={mocks}>
        <WorkspaceDescriptionDialog
          workspace={WORKSPACE}
          open={true}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const descriptionInput = screen.getByTestId("description");
    await user.clear(descriptionInput);

    const saveButton = screen.getByRole("button", { name: "Save" });
    await user.click(saveButton);
    await user.type(descriptionInput, "Description");
    expect(useUpdateWorkspaceMutationMock).toHaveBeenCalled();
  });
});
