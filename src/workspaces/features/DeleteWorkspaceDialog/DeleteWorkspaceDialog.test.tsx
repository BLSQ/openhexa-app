import { faker } from "@faker-js/faker";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import router from "next/router";
import {
  DeleteWorkspaceDocument,
  useDeleteWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import DeleteWorkspaceDialog from "./DeleteWorkspaceDialog";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useDeleteWorkspaceMutation: jest.fn().mockReturnValue([]),
}));

const WORKSPACE = {
  id: faker.datatype.uuid(),
  name: faker.commerce.productName(),
};
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
        workspace={WORKSPACE}
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
          workspace={WORKSPACE}
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
              id: WORKSPACE.id,
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
          workspace={WORKSPACE}
          onClose={() => {}}
        />
      </TestApp>
    );
    expect(useDeleteWorkspaceMutationMock).toHaveBeenCalled();

    const deleteButton = screen.getByRole("button", { name: "Delete" });
    await user.click(deleteButton);
    waitFor(() => {
      expect(pushSpy).toHaveBeenCalledWith("/");
    });
  });
});
