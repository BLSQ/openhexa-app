import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  DeleteWorkspaceMemberDocument,
  useDeleteWorkspaceMemberMutation,
} from "workspaces/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import router from "next/router";
import DeleteWorkspaceMemberDialog from ".";
import { v4 } from "uuid";

const MEMBER = {
  id: v4(),
  user: {
    id: v4(),
    displayName: "rooŧ@openhexa.crog",
  },
};

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useDeleteWorkspaceMemberMutation: jest.fn().mockReturnValue([]),
}));

const useDeleteWorkspaceMemberMutationMock =
  useDeleteWorkspaceMemberMutation as jest.Mock;

describe("DeleteWorkspaceMemberDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useDeleteWorkspaceMemberMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <DeleteWorkspaceMemberDialog
          open={false}
          member={MEMBER}
          onClose={() => {}}
        />
      </TestApp>,
    );
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <DeleteWorkspaceMemberDialog
          open={true}
          member={MEMBER}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const dialog = screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Deletes a workspace member ", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useDeleteWorkspaceMemberMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useDeleteWorkspaceMemberMutationMock.mockImplementation(
      useDeleteWorkspaceMemberMutation,
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: DeleteWorkspaceMemberDocument,
          variables: {
            input: {
              membershipId: MEMBER.id,
            },
          },
        },
        result: {
          data: {
            deleteWorkspaceMember: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <DeleteWorkspaceMemberDialog
          open={true}
          member={MEMBER}
          onClose={() => {}}
        />
      </TestApp>,
    );
    expect(useDeleteWorkspaceMemberMutationMock).toHaveBeenCalled();

    const deleteButton = screen.getByRole("button", { name: "Delete" });
    await user.click(deleteButton);
    waitFor(() => {
      expect(pushSpy).toHaveBeenCalledWith("/");
    });
  });
});
