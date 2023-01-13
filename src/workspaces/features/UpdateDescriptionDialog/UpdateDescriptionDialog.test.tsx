import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  UpdateWorkspaceDocument,
  useUpdateWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import WorkspaceDescriptionDialog from "./UpdateDescriptionDialog";
import { WORKSPACES } from "workspaces/helpers/fixtures";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useUpdateWorkspaceMutation: jest.fn().mockReturnValue([]),
}));

const { id, description, name, countries, ...rest } = WORKSPACES[0];

const useUpdateWorkspaceMutationMock = useUpdateWorkspaceMutation as jest.Mock;

describe("EditWorkspaceDescriptionDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useUpdateWorkspaceMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <WorkspaceDescriptionDialog
        workspace={WORKSPACES[0]}
        open={false}
        onClose={() => {}}
      />
    );
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <WorkspaceDescriptionDialog
          workspace={WORKSPACES[0]}
          open={true}
          onClose={() => {}}
        />
      </TestApp>
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Edit workspace description", async () => {
    const { useUpdateWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useUpdateWorkspaceMutationMock.mockImplementation(
      useUpdateWorkspaceMutation
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: UpdateWorkspaceDocument,
          variables: {
            input: {
              id: WORKSPACES[0].id,
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
      <TestApp>
        <WorkspaceDescriptionDialog
          workspace={WORKSPACES[0]}
          open={true}
          onClose={() => {}}
        />
      </TestApp>
    );

    const descriptionInput = await screen.getByTestId("description");
    await user.clear(descriptionInput);

    const saveButton = screen.getByRole("button", { name: "Save" });
    expect(saveButton).toBeDisabled();
    await user.type(descriptionInput, "Description");
    expect(saveButton).not.toBeDisabled();

    await user.click(saveButton);

    expect(useUpdateWorkspaceMutationMock).toHaveBeenCalled();
  });
});
