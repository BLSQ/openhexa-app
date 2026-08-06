import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { SavedQueryOrderBy } from "graphql/types";
import mockRouter from "next-router-mock";
import { useEffect, useState } from "react";
import SavedQueriesList from "./SavedQueriesList";
import { DEFAULT_SAVED_QUERY_ORDER_BY } from "./sorting";

jest.mock("workspaces/features/SavedQueries/SavedQueries.generated", () => ({
  useCreateSavedQueryMutation: () => [jest.fn(), { loading: false }],
  useUpdateSavedQueryMutation: () => [jest.fn(), { loading: false }],
  useDeleteSavedQueryMutation: () => [jest.fn(), { loading: false }],
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("core/hooks/useCacheKey", () => ({
  __esModule: true,
  default: () => jest.fn(),
}));

const item = (id: string, name: string, description: string) => ({
  __typename: "SavedQuery",
  id,
  name,
  description,
  updatedAt: "2024-01-01T00:00:00Z",
  createdBy: null,
  permissions: { update: true, delete: true },
});

const makeWorkspace = (overrides: any = {}) =>
  ({
    slug: "ws-1",
    permissions: { createSavedQuery: true },
    savedQueries: {
      totalItems: 2,
      totalPages: 1,
      pageNumber: 1,
      items: [
        item("q1", "Query One", "first"),
        item("q2", "Query Two", "second"),
      ],
    },
    ...overrides,
  }) as any;

const renderList = (props: any = {}) =>
  render(
    <SavedQueriesList
      workspace={makeWorkspace(props.workspace)}
      page={props.page ?? 1}
      perPage={15}
      orderBy={props.orderBy ?? DEFAULT_SAVED_QUERY_ORDER_BY}
      loading={false}
      searchValue=""
      onSearchChange={props.onSearchChange ?? jest.fn()}
      onChange={props.onChange ?? jest.fn()}
    />,
  );

beforeEach(() => {
  jest.clearAllMocks();
  mockRouter.setCurrentUrl("/");
});

describe("SavedQueriesList", () => {
  it("renders the saved queries", () => {
    renderList();
    expect(screen.getByText("Query One")).toBeInTheDocument();
    expect(screen.getByText("Query Two")).toBeInTheDocument();
  });

  it("shows an empty state when there are no queries", () => {
    renderList({
      workspace: {
        savedQueries: {
          totalItems: 0,
          totalPages: 0,
          pageNumber: 1,
          items: [],
        },
      },
    });
    expect(screen.getByText("No saved queries yet.")).toBeInTheDocument();
  });

  it("forwards search input changes", () => {
    const onSearchChange = jest.fn();
    renderList({ onSearchChange });
    fireEvent.change(screen.getByTestId("search-input"), {
      target: { value: "malaria" },
    });
    expect(onSearchChange).toHaveBeenCalledWith("malaria");
  });

  it("opens a query when its row is clicked", () => {
    renderList();
    fireEvent.click(screen.getByText("Query One"));
    expect(mockRouter.asPath).toBe("/workspaces/ws-1/data-studio/queries/q1");
  });
});

const PAGE_SIZE = 15;
const TOTAL = 19;
const allItems = Array.from({ length: TOTAL }, (_, i) =>
  item(`q${i + 1}`, `Query ${i + 1}`, ""),
);

// Mirrors the page's pagination wiring, including the async gap between
// requesting a page and its data arriving (Apollo + notifyOnNetworkStatusChange):
// `dataPage` catches up to `page` on a later tick. Search resets the parent to
// page 1, like the real page does.
const PaginatedHarness = () => {
  const [page, setPage] = useState(1);
  const [dataPage, setDataPage] = useState(1);

  useEffect(() => {
    if (dataPage === page) return;
    const id = setTimeout(() => setDataPage(page), 0);
    return () => clearTimeout(id);
  }, [page, dataPage]);

  const startIndex = (dataPage - 1) * PAGE_SIZE;
  const workspace = {
    slug: "ws-1",
    permissions: { createSavedQuery: true },
    savedQueries: {
      totalItems: TOTAL,
      totalPages: Math.ceil(TOTAL / PAGE_SIZE),
      pageNumber: dataPage,
      items: allItems.slice(startIndex, startIndex + PAGE_SIZE),
    },
  } as any;
  return (
    <SavedQueriesList
      workspace={workspace}
      page={page}
      perPage={PAGE_SIZE}
      orderBy={DEFAULT_SAVED_QUERY_ORDER_BY}
      loading={page !== dataPage}
      searchValue=""
      onSearchChange={() => setPage(1)}
      onChange={({ page: nextPage }) => setPage(nextPage)}
    />
  );
};

// Prev/Next disabled state reflects the grid's built-in pager (i18n is mocked to
// return keys, so the "Showing X to Y" text can't be asserted on).
const pagerButtons = () => {
  const nav = screen.getByRole("navigation", { name: "Pagination" });
  const [prev, next] = within(nav).getAllByRole("button");
  return { prev, next };
};

describe("SavedQueriesList pagination", () => {
  // Covers both directions the built-in pager can desync from server-side data:
  // forward navigation (needs `fetchData`) and an external reset to page 1 on
  // search (needs `defaultPageIndex` to feed the parent page back to the grid).
  it("keeps the built-in pager in sync with the fetched page", async () => {
    render(<PaginatedHarness />);

    expect(screen.getByText("Query 1")).toBeInTheDocument();
    expect(pagerButtons().prev).toBeDisabled();
    expect(pagerButtons().next).toBeEnabled();

    // Forward: page 2 data (items 16–19) arrives on the next tick and the pager
    // moves with it — Previous usable, Next (last page) disabled.
    fireEvent.click(pagerButtons().next);
    expect(await screen.findByText("Query 16")).toBeInTheDocument();
    expect(screen.queryByText("Query 1")).not.toBeInTheDocument();
    await waitFor(() => {
      expect(pagerButtons().prev).toBeEnabled();
      expect(pagerButtons().next).toBeDisabled();
    });

    // Reset: a search drops the parent to page 1; the pager must follow instead
    // of staying on page 2 while page-1 rows render.
    fireEvent.change(screen.getByTestId("search-input"), {
      target: { value: "malaria" },
    });
    expect(await screen.findByText("Query 1")).toBeInTheDocument();
    await waitFor(() => {
      expect(pagerButtons().prev).toBeDisabled();
      expect(pagerButtons().next).toBeEnabled();
    });
  });
});

// Not `getByRole(..., { name })`: react-table puts title="Toggle SortBy" on
// sortable headers, and testing-library's accessible-name computation lets that
// shadow the label. Match on the rendered text instead.
const header = (label: string) => {
  const match = screen
    .getAllByRole("columnheader")
    .find((cell) => cell.textContent === label);
  if (!match) {
    throw new Error(`No column header labelled "${label}"`);
  }
  return match;
};

describe("SavedQueriesList sorting", () => {
  it("marks the column the list is ordered by", () => {
    renderList({ orderBy: SavedQueryOrderBy.NameAsc });

    expect(header("Name")).toHaveAttribute("aria-sort", "ascending");
    expect(header("Last updated")).toHaveAttribute("aria-sort", "none");
    expect(header("Description")).not.toHaveAttribute("aria-sort");
  });

  it("reports the sorted column as an orderBy, toggling direction", () => {
    const onChange = jest.fn();
    const { rerender } = renderList({ onChange });

    fireEvent.click(header("Name"));
    expect(onChange).toHaveBeenLastCalledWith({
      page: 1,
      perPage: 15,
      orderBy: SavedQueryOrderBy.NameAsc,
    });

    // The parent owns orderBy, so a real toggle only happens once it feeds the
    // new value back in.
    rerender(
      <SavedQueriesList
        workspace={makeWorkspace()}
        page={1}
        perPage={15}
        orderBy={SavedQueryOrderBy.NameAsc}
        loading={false}
        searchValue=""
        onSearchChange={jest.fn()}
        onChange={onChange}
      />,
    );
    fireEvent.click(header("Name"));
    expect(onChange).toHaveBeenLastCalledWith({
      page: 1,
      perPage: 15,
      orderBy: SavedQueryOrderBy.NameDesc,
    });
  });

  it("returns to the first page when the sort changes", () => {
    const onChange = jest.fn();
    renderList({ onChange, page: 3 });

    fireEvent.click(header("Name"));
    expect(onChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 1, orderBy: SavedQueryOrderBy.NameAsc }),
    );
  });

  it("does not sort on columns with no server-side ordering", () => {
    const onChange = jest.fn();
    renderList({ onChange });

    fireEvent.click(header("Description"));
    fireEvent.click(header("Created by"));
    expect(onChange).not.toHaveBeenCalled();
  });
});
