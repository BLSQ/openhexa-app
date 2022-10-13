import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import useSearch from "catalog/hooks/useSearch";
import { SearchQueryDocument } from "catalog/hooks/useSearch.generated";
import Button from "core/components/Button";
import mockRouter from "next-router-mock";
import { useState } from "react";
import Quicksearch from "./Quicksearch";

jest.mock("catalog/hooks/useSearch", () => jest.fn(() => ({})));
jest.mock("core/hooks/useDebounce", () => jest.fn((v) => v));

const useSearchMock = useSearch as jest.Mock;

describe("Quicksearch", () => {
  const onClose = jest.fn();
  afterEach(() => {
    onClose.mockClear();
  });

  it("is not displayed by default", async () => {
    const { container } = render(<Quicksearch onClose={onClose} />);
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("is directly shown if open is true", async () => {
    const { container } = render(<Quicksearch onClose={onClose} open />);
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
  });

  it("does not fetch results if the query if empty", async () => {
    const { container } = render(<Quicksearch onClose={onClose} open />);
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(useSearchMock).toHaveBeenCalledWith({
      query: "",
      perPage: 10,
      skip: true, // Tested line
    });
  });

  it("displays the results", async () => {
    const user = await userEvent.setup({ delay: null });
    useSearchMock.mockImplementation(() => {
      return {
        results: [
          {
            rank: 1,
            object: {
              __typename: "Collection",
              id: "1",
              name: "Collection",
            },
          },
        ],
        types: [],
        loading: false,
      };
    });

    const mocks = [
      {
        request: {
          query: SearchQueryDocument,
          variables: {
            input: {
              query: "Test",
              perPage: 10,
            },
          },
        },
      },
    ];

    render(<Quicksearch onClose={onClose} open />);

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(useSearchMock).toHaveBeenCalledWith({
      query: "",
      perPage: 10,
      skip: true, // Tested line
    });
    const searchInput = screen.getByTestId("search-input");
    await user.type(searchInput, "Test");

    await screen.findByDisplayValue("Test");
    expect(useSearchMock).toHaveBeenLastCalledWith({
      query: "Test",
      skip: false,
      perPage: 10,
    });

    expect(await screen.findByTestId("results")).toBeInTheDocument();
  });

  it("removes the dialog from the dom when closed", async () => {
    function TestQuicksearch() {
      const [isOpen, setOpen] = useState(false);

      return (
        <>
          <Quicksearch onClose={() => setOpen(false)} open={isOpen} />
          <Button onClick={() => setOpen(!isOpen)} data-testid="toggle">
            Toggle
          </Button>
        </>
      );
    }
    const user = await userEvent.setup({ delay: null });

    render(<TestQuicksearch />);

    expect(await screen.queryByRole("dialog")).toBeNull();
    const btn = screen.getByTestId("toggle");

    await user.click(btn);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();

    await user.click(btn);
    expect(await screen.queryByRole("dialog")).toBeNull();
  });

  it("calls onClose when the route changes", async () => {
    mockRouter.setCurrentUrl("/");
    render(<Quicksearch onClose={onClose} open />);

    expect(onClose).not.toHaveBeenCalled();

    waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeInTheDocument();
    });

    mockRouter.setCurrentUrl("/search");

    waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
  });

  it("redirects the user to the advanced search and forward the querystring", async () => {
    mockRouter.setCurrentUrl("/");
    const user = await userEvent.setup({ delay: null });
    render(<Quicksearch onClose={onClose} open />);

    expect(screen.queryByRole("dialog")).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();

    await user.click(screen.getByText("Go to advanced search"));
    expect(onClose).toHaveBeenCalled();
  });
});
