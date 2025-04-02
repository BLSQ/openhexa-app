import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useMutation, useQuery } from "@apollo/client";
import PipelineTemplates from "./PipelineTemplates";

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

const template = (id: string) => ({
  id: id,
  name: `Template ${id}`,
  description: `Description ${id}`,
  permissions: {
    delete: true,
  },
  currentVersion: {
    id: id,
    versionNumber: id,
    createdAt: `2023-01-01T00:0${id}:00Z`,
    template: {
      sourcePipeline: {
        name: `Pipeline ${id}`,
      },
    },
  },
});
const mockPipelineTemplates = {
  pageNumber: 1,
  totalPages: 2,
  totalItems: 11,
  items: Array.from({ length: 10 }, (_, index) =>
    template((index + 1).toString()),
  ),
};

describe("PipelineTemplates", () => {
  it("renders data after loading", async () => {
    useQueryMock.mockReturnValue({
      loading: false,
      data: { pipelineTemplates: mockPipelineTemplates },
      error: null,
    });

    render(<PipelineTemplates workspace={mockWorkspace} />);

    await waitFor(() => {
      expect(screen.getByText("Template 1")).toBeInTheDocument();
      expect(screen.getByText("Description 1")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("grid-view"));

    expect(screen.getByText("Template 1")).toBeInTheDocument();
    expect(screen.getByText("v1")).toBeInTheDocument();
    expect(screen.getByText("1/1/2023, 1:01 AM")).toBeInTheDocument();
  });

  it("handles pagination", async () => {
    useQueryMock.mockReturnValue({
      loading: false,
      data: { pipelineTemplates: mockPipelineTemplates },
      error: null,
    });

    render(<PipelineTemplates workspace={mockWorkspace} />);

    const previousButton = screen.getByRole("button", { name: /Previous/i });
    const nextButton = previousButton.nextElementSibling as HTMLButtonElement;
    await waitFor(() => {
      expect(nextButton).toBeInTheDocument();
    });

    useQueryMock.mockReturnValue({
      loading: false,
      data: {
        pipelineTemplates: {
          ...mockPipelineTemplates,
          items: [template("11")],
        },
      },
      error: null,
    });

    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText("Template 11")).toBeInTheDocument();
    });
  });

  it("handles search functionality", async () => {
    useQueryMock.mockReturnValue({
      loading: false,
      data: { pipelineTemplates: mockPipelineTemplates },
      error: null,
    });

    render(<PipelineTemplates workspace={mockWorkspace} />);

    const searchInput = screen.getByRole("textbox");

    fireEvent.change(searchInput, { target: { value: "Template 1" } });

    await waitFor(() => {
      expect(useQueryMock).lastCalledWith(
        "GQL",
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

    render(<PipelineTemplates workspace={mockWorkspace} />);

    await waitFor(() => {
      expect(screen.getByText("Error loading templates")).toBeInTheDocument();
    });
  });
});
