import React from "react";
import { render } from "@testing-library/react";
import { MemoryRouterProvider } from "next-router-mock/MemoryRouterProvider";
import mockRouter from "next-router-mock";
import { LayoutContext } from "./WorkspaceLayout";
import Sidebar from "./Sidebar";
import { Sidebar_WorkspaceFragment } from "./Sidebar.generated";
import { TestApp } from "core/helpers/testutils";

const mockWorkspace: Sidebar_WorkspaceFragment = {
  slug: "test-workspace",
  name: "Test Workspace",
  countries: [
    { __typename: "Country", flag: "🇺🇸", code: "US" },
    { __typename: "Country", flag: "🇨🇦", code: "CA" },
  ],
  permissions: {
    manageMembers: true,
    update: true,
    launchNotebookServer: true,
  },
  __typename: "Workspace",
};

describe("Sidebar", () => {
  it("should highlight the current link", () => {
    mockRouter.setCurrentUrl("/workspaces/test-workspace");
    const { getByText } = render(
      <MemoryRouterProvider>
        <TestApp>
          <LayoutContext.Provider
            value={{ isSidebarOpen: true, setSidebarOpen: jest.fn() }}
          >
            <Sidebar workspace={mockWorkspace} />
          </LayoutContext.Provider>
        </TestApp>
      </MemoryRouterProvider>,
    );

    const homeLink = getByText("Home");
    expect(homeLink).toHaveClass("text-white");
  });

  it("should highlight the pipelines link when on templates path", () => {
    mockRouter.setCurrentUrl("/workspaces/test-workspace/templates");

    const { getByText } = render(
      <MemoryRouterProvider>
        <TestApp>
          <LayoutContext.Provider
            value={{ isSidebarOpen: true, setSidebarOpen: jest.fn() }}
          >
            <Sidebar workspace={mockWorkspace} />
          </LayoutContext.Provider>
        </TestApp>
      </MemoryRouterProvider>,
    );

    const pipelinesLink = getByText("Pipelines");
    expect(pipelinesLink).toHaveClass("text-white");
  });
});
