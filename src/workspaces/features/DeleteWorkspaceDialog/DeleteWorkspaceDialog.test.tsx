import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  DeleteWorkspaceDocument,
  useDeleteWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import router from "next/router";
import DeleteWorkspaceDialog from "./DeleteWorkspaceDialog";
import { WORKSPACES } from "workspaces/helpers/fixtures";

const { id, description, name, countries, ...rest } = WORKSPACES[0];

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useDeleteWorkspaceMutation: jest.fn().mockReturnValue([]),
}));

const useDeleteWorkspaceMutationMock = useDeleteWorkspaceMutation as jest.Mock;

describe("DeleteWorkspaceDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useDeleteWorkspaceMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <DeleteWorkspaceDialog
        open={false}
        workspace={WORKSPACES[0]}
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
        <DeleteWorkspaceDialog
          open={true}
          workspace={WORKSPACES[0]}
          onClose={() => {}}
        />
      </TestApp>
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Deletes a workspace ", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useDeleteWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useDeleteWorkspaceMutationMock.mockImplementation(
      useDeleteWorkspaceMutation
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: DeleteWorkspaceDocument,
          variables: {
            input: {
              id: WORKSPACES[0].id,
            },
          },
        },
        result: {
          data: {
            deleteWorkspace: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <DeleteWorkspaceDialog
          open={true}
          workspace={WORKSPACES[0]}
          onClose={() => {}}
        />
      </TestApp>
    );
    expect(useDeleteWorkspaceMutationMock).toHaveBeenCalled();

    const deleteButton = screen.getByRole("button", { name: "Delete" });
    await user.click(deleteButton);
    waitFor(() => {
      expect(pushSpy).toHaveBeenCalledWith("/dashboard");
    });
  });
});
