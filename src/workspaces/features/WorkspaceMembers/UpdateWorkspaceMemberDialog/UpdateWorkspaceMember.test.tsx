import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  UpdateWorkspaceMemberDocument,
  useUpdateWorkspaceMemberMutation,
} from "workspaces/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import router from "next/router";
import UpdateWorkspaceMemberDialog from ".";
import { v4 } from "uuid";
import { WorkspaceMembershipRole } from "graphql/types";

const MEMBER = {
  id: v4(),
  role: WorkspaceMembershipRole.Viewer,
};

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useUpdateWorkspaceMemberMutation: jest.fn().mockReturnValue([]),
}));

const useUpdateWorkspaceMemberMutationMock =
  useUpdateWorkspaceMemberMutation as jest.Mock;

describe("UpdateWorkspaceMemberDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useUpdateWorkspaceMemberMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <UpdateWorkspaceMemberDialog
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
        <UpdateWorkspaceMemberDialog
          open={true}
          member={MEMBER}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Update a workspace member ", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useUpdateWorkspaceMemberMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useUpdateWorkspaceMemberMutationMock.mockImplementation(
      useUpdateWorkspaceMemberMutation,
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: UpdateWorkspaceMemberDocument,
          variables: {
            input: {
              membershipId: MEMBER.id,
            },
          },
        },
        result: {
          data: {
            updateWorkspaceMember: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <UpdateWorkspaceMemberDialog
          open={true}
          member={MEMBER}
          onClose={() => {}}
        />
      </TestApp>,
    );
    expect(useUpdateWorkspaceMemberMutationMock).toHaveBeenCalled();

    const updateButton = screen.getByRole("button", { name: "Save" });
    await user.click(updateButton);
  });
});
