import React from "react";
import { render, fireEvent, screen, waitFor } from "@testing-library/react";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";
import { MemoryRouterProvider } from "next-router-mock/MemoryRouterProvider";
import mockRouter from "next-router-mock";
import { TestApp } from "core/helpers/testutils";
import { mocks } from "./SpotlightSearchMock.test";

describe("SpotlightSearch", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockRouter.setCurrentUrl("/workspaces/test-workspace");
  });

  it("should type a query, filter workspaces, switch tabs, and click links", async () => {
    render(
      <MemoryRouterProvider>
        <TestApp mocks={mocks}>
          <SpotlightSearch isOpen={true} onClose={mockOnClose} />
        </TestApp>
      </MemoryRouterProvider>,
    );

    const searchInput = screen.getByTestId("search-input");
    fireEvent.change(searchInput, { target: { value: "test query" } });
    expect(searchInput).toHaveValue("test query");

    await waitFor(() => {
      expect(screen.getByText("Filter by Workspace")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Test Workspace")); // The mock data has a workspace called "Test Workspace" and expecting only one workspace in the query

    const tabs = screen.getAllByRole("tab");
    expect(tabs).toHaveLength(6);
    fireEvent.click(tabs[2]); // Switch to the tables tab
    expect(tabs[2]).toHaveAttribute("aria-selected", "true");

    await waitFor(
      () => expect(screen.getByText("Test Table")).toBeInTheDocument(),
      { timeout: 1000 }, // Account for a debounced time of 500ms in the input bar
    );
    fireEvent.keyDown(document, { key: "Enter", code: "Enter" }); // Focus and keyboard shortcuts should work
    expect(mockRouter.asPath).toBe(
      "/workspaces/test-workspace/databases/Test%20Table",
    );

    fireEvent.keyDown(document, { key: "Escape", code: "Escape" });
    expect(mockOnClose).toHaveBeenCalled();
  });
});
