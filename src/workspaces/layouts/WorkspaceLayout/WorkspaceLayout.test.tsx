import WorkspaceLayout from "./WorkspaceLayout";
import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import useLocalStorage from "core/hooks/useLocalStorage";
import { SidebarMenuDocument } from "workspaces/features/SidebarMenu/SidebarMenu.generated";

jest.mock("core/hooks/useLocalStorage", () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe("WorkspaceLayout", () => {
  const workspace = {
    slug: "1",
    name: "Workspace 1",
    description: "Workspace 1 description",
    createdAt: "2021-01-01T00:00:00.000Z",
    updatedAt: "2021-01-01T00:00:00.000Z",
    workspaces: {
      totalCount: 0,
    },
    permissions: {
      manageMembers: true,
      launchNotebookServer: true,
      update: true,
    },
    countries: [],
  };
  it("renders", async () => {
    const setValueMock = jest.fn();
    (useLocalStorage as jest.Mock).mockReturnValue([null, setValueMock]);
    const { container } = render(
      <TestApp
        mocks={[
          {
            request: {
              query: SidebarMenuDocument,
              variables: {
                page: 1,
                perPage: 5,
              },
            },
            result: {
              data: {
                pendingWorkspaceInvitations: {
                  totalItems: 0,
                  items: [],
                },
                workspaces: {
                  totalItems: 0,
                  items: [],
                },
              },
            },
          },
        ]}
      >
        <WorkspaceLayout workspace={workspace}>
          <WorkspaceLayout.PageContent>Content</WorkspaceLayout.PageContent>
        </WorkspaceLayout>
      </TestApp>,
    );

    expect(screen.findByText("Content")).toBeTruthy();
    expect(setValueMock).toHaveBeenCalledWith("1");
  });
});
