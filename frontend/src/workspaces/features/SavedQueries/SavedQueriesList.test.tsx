import { fireEvent, render, screen } from "@testing-library/react";
import mockRouter from "next-router-mock";
import SavedQueriesList from "./SavedQueriesList";

jest.mock("workspaces/features/SavedQueries/SavedQueries.generated", () => ({
  useDeleteSavedQueryMutation: () => [jest.fn()],
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
      perPage={15}
      loading={false}
      searchValue=""
      onSearchChange={props.onSearchChange ?? jest.fn()}
      onChangePage={jest.fn()}
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

  it("gates the New query button on the create permission", () => {
    const { rerender } = renderList();
    expect(
      screen.getByRole("button", { name: "New query" }),
    ).toBeInTheDocument();

    rerender(
      <SavedQueriesList
        workspace={makeWorkspace({ permissions: { createSavedQuery: false } })}
        perPage={15}
        loading={false}
        searchValue=""
        onSearchChange={jest.fn()}
        onChangePage={jest.fn()}
      />,
    );
    expect(
      screen.queryByRole("button", { name: "New query" }),
    ).not.toBeInTheDocument();
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
