import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useMutation, useQuery } from "@apollo/client";
import PipelineTemplatesTable from "./PipelineTemplateTable";

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(),
  useMutation: jest.fn(),
  gql: jest.fn(() => "GQL"),
}));

const useQueryMock = useQuery as jest.Mock;
const useMutationMock = useMutation as jest.Mock;
useMutationMock.mockReturnValue([jest.fn(), { loading: false }]);

const mockWorkspace = {
  slug: "test-workspace",
};

const mockPipelineTemplates = {
  pageNumber: 1,
  totalPages: 2,
  totalItems: 6,
  items: Array.from({ length: 6 }, (_, index) => {
    const indexAsString = (index + 1).toString();
    return {
      id: indexAsString,
      name: `Template ${indexAsString}`,
      currentVersion: {
        id: indexAsString,
        versionNumber: indexAsString,
        createdAt: `2023-01-01T00:0${indexAsString}:00Z`,
        template: {
          sourcePipeline: {
            name: `Pipeline ${indexAsString}`,
          },
        },
      },
    };
  }),
};

describe("PipelineTemplatesTable", () => {
  it("renders loading state initially", () => {
    useQueryMock.mockReturnValue({
      loading: true,
      data: null,
      error: null,
    });

    render(<PipelineTemplatesTable workspace={mockWorkspace} />);

    expect(screen.getByTestId("spinner")).toBeInTheDocument();
  });

  it("renders data after loading", async () => {
    useQueryMock.mockReturnValue({
      loading: false,
      data: { pipelineTemplates: mockPipelineTemplates },
      error: null,
    });

    render(<PipelineTemplatesTable workspace={mockWorkspace} />);

    await waitFor(() => {
      expect(screen.getByText("Template 1")).toBeInTheDocument();
      expect(screen.getByText("v1")).toBeInTheDocument();
      expect(screen.getByText("1/1/2023, 1:01 AM")).toBeInTheDocument();
    });
  });

  it("handles pagination", async () => {
    const fetchMore = jest.fn();
    useQueryMock.mockReturnValue({
      loading: false,
      data: { pipelineTemplates: mockPipelineTemplates },
      error: null,
      fetchMore,
    });

    render(<PipelineTemplatesTable workspace={mockWorkspace} />);

    const previousButton = screen.getByRole("button", { name: /Previous/i });
    const nextButton = previousButton.nextElementSibling as HTMLButtonElement;
    await waitFor(() => {
      expect(nextButton).toBeInTheDocument();
    });
    expect(fetchMore).not.toHaveBeenCalled();

    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(fetchMore).toHaveBeenCalled();
    });
  });

  it("handles search functionality", async () => {
    const fetchMore = jest.fn();
    useQueryMock.mockReturnValue({
      loading: false,
      data: { pipelineTemplates: mockPipelineTemplates },
      error: null,
      fetchMore,
    });

    render(<PipelineTemplatesTable workspace={mockWorkspace} />);

    const searchInput = screen.getByRole("textbox");

    fireEvent.change(searchInput, { target: { value: "Template 1" } });
    expect(fetchMore).not.toHaveBeenCalled();
    fireEvent.submit(searchInput);

    await waitFor(() => {
      expect(fetchMore).toHaveBeenCalledWith(
        expect.objectContaining({
          variables: expect.objectContaining({
            search: "Template 1",
          }),
        }),
      );
      expect(screen.getByText("Template 1")).toBeInTheDocument();
    });
  });

  it("displays error message on error", async () => {
    useQueryMock.mockReturnValue({
      loading: false,
      data: null,
      error: new Error("An error occurred"),
    });

    render(<PipelineTemplatesTable workspace={mockWorkspace} />);

    await waitFor(() => {
      expect(screen.getByText("Error loading templates")).toBeInTheDocument();
    });
  });
});
