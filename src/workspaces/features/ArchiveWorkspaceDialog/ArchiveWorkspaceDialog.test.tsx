import { faker } from "@faker-js/faker";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import router from "next/router";
import {
  ArchiveWorkspaceDocument,
  useArchiveWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import ArchiveWorkspaceDialog from "./ArchiveWorkspaceDialog";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useArchiveWorkspaceMutation: jest.fn().mockReturnValue([]),
}));

const WORKSPACE = {
  id: faker.string.uuid(),
  slug: "SLUG",
  name: faker.commerce.productName(),
};
const useArchiveWorkspaceMutationMock =
  useArchiveWorkspaceMutation as jest.Mock;

describe("ArchiveWorkspaceDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useArchiveWorkspaceMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <ArchiveWorkspaceDialog
        open={false}
        workspace={WORKSPACE}
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
        <ArchiveWorkspaceDialog
          open={true}
          workspace={WORKSPACE}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Archives a workspace ", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useArchiveWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useArchiveWorkspaceMutationMock.mockImplementation(
      useArchiveWorkspaceMutation,
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: ArchiveWorkspaceDocument,
          variables: {
            input: {
              slug: WORKSPACE.slug,
            },
          },
        },
        result: {
          data: {
            archiveWorkspace: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <ArchiveWorkspaceDialog
          open={true}
          workspace={WORKSPACE}
          onClose={() => {}}
        />
      </TestApp>,
    );
    expect(useArchiveWorkspaceMutationMock).toHaveBeenCalled();

    const archiveButton = screen.getByRole("button", { name: "Archive" });
    await user.click(archiveButton);
    waitFor(() => {
      expect(pushSpy).toHaveBeenCalledWith("/");
    });
  });
});
