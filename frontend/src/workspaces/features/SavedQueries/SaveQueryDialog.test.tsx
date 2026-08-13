import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SavedQueryVisibility } from "graphql/types";
import { toast } from "react-toastify";
import SaveQueryDialog from "./SaveQueryDialog";

const createMock = jest.fn();
const updateMock = jest.fn();

jest.mock("workspaces/features/SavedQueries/SavedQueries.generated", () => ({
  useCreateSavedQueryMutation: () => [createMock, { loading: false }],
  useUpdateSavedQueryMutation: () => [updateMock, { loading: false }],
  useDeleteSavedQueryMutation: () => [jest.fn(), { loading: false }],
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("core/hooks/useCacheKey", () => ({
  __esModule: true,
  default: () => jest.fn(),
}));

beforeEach(() => jest.clearAllMocks());

const savedQuery = {
  id: "q1",
  name: "Old name",
  description: "desc",
  visibility: SavedQueryVisibility.Workspace,
  permissions: { update: true, delete: true, updateVisibility: true },
};

describe("SaveQueryDialog", () => {
  it("creates a query from the current editor content", async () => {
    createMock.mockResolvedValue({
      data: {
        createSavedQuery: {
          success: true,
          errors: [],
          savedQuery: { id: "new-1", name: "My query" },
        },
      },
    });
    const onSaved = jest.fn();
    const onClose = jest.fn();

    render(
      <SaveQueryDialog
        open
        mode="create"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={null}
        onClose={onClose}
        onSaved={onSaved}
      />,
    );

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "My query" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save query" }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith({
        variables: {
          input: {
            workspaceSlug: "ws-1",
            name: "My query",
            content: "SELECT 1",
            description: "",
            // A new query starts private until its author shares it.
            visibility: SavedQueryVisibility.Private,
          },
        },
      }),
    );
    expect(onSaved).toHaveBeenCalledWith({ id: "new-1", name: "My query" });
    expect(toast.success).toHaveBeenCalledWith("Query created");
    expect(onClose).toHaveBeenCalled();
  });

  it("does not create when the name is empty", () => {
    // The name input is `required`, so the browser blocks submission natively.
    render(
      <SaveQueryDialog
        open
        mode="create"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={null}
        onClose={jest.fn()}
        onSaved={jest.fn()}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Save query" }));

    expect(createMock).not.toHaveBeenCalled();
  });

  it("rejects a name longer than the max length", async () => {
    render(
      <SaveQueryDialog
        open
        mode="create"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={null}
        onClose={jest.fn()}
        onSaved={jest.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "a".repeat(256) },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save query" }));

    expect(
      await screen.findByText("Name must be at most {{max}} characters"),
    ).toBeInTheDocument();
    expect(createMock).not.toHaveBeenCalled();
  });

  it("edits name/description/visibility in edit-details mode", async () => {
    updateMock.mockResolvedValue({
      data: {
        updateSavedQuery: {
          success: true,
          errors: [],
          savedQuery: { id: "q1", name: "Renamed" },
        },
      },
    });

    render(
      <SaveQueryDialog
        open
        mode="edit-details"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={savedQuery}
        onClose={jest.fn()}
        onSaved={jest.fn()}
      />,
    );

    const nameInput = screen.getByLabelText("Name") as HTMLInputElement;
    expect(nameInput.value).toBe("Old name");
    fireEvent.change(nameInput, { target: { value: "Renamed" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() =>
      expect(updateMock).toHaveBeenCalledWith({
        variables: {
          input: {
            id: "q1",
            name: "Renamed",
            description: "desc",
            // Echoed back unchanged: the backend only gates an actual change, so
            // this must not require the author's rights.
            visibility: SavedQueryVisibility.Workspace,
          },
        },
      }),
    );
    expect(createMock).not.toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith("Query updated");
  });

  it("seeds the picker from the query being edited", () => {
    render(
      <SaveQueryDialog
        open
        mode="edit-details"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={savedQuery}
        onClose={jest.fn()}
        onSaved={jest.fn()}
      />,
    );

    expect(screen.getByRole("radio", { name: /Workspace/ })).toBeChecked();
    expect(screen.getByRole("radio", { name: /Private/ })).not.toBeChecked();
  });

  it("creates a shared query when the author picks Workspace", async () => {
    createMock.mockResolvedValue({
      data: {
        createSavedQuery: {
          success: true,
          errors: [],
          savedQuery: { id: "new-1", name: "My query" },
        },
      },
    });

    render(
      <SaveQueryDialog
        open
        mode="create"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={null}
        onClose={jest.fn()}
        onSaved={jest.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "My query" },
    });
    fireEvent.click(screen.getByRole("radio", { name: /Workspace/ }));
    fireEvent.click(screen.getByRole("button", { name: "Save query" }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith({
        variables: {
          input: expect.objectContaining({
            visibility: SavedQueryVisibility.Workspace,
          }),
        },
      }),
    );
  });

  it("locks the picker for a member who may edit but not unshare", () => {
    render(
      <SaveQueryDialog
        open
        mode="edit-details"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={{
          ...savedQuery,
          permissions: { update: true, delete: true, updateVisibility: false },
        }}
        onClose={jest.fn()}
        onSaved={jest.fn()}
      />,
    );

    expect(screen.getByRole("radio", { name: /Private/ })).toBeDisabled();
    expect(screen.getByRole("radio", { name: /Workspace/ })).toBeDisabled();
  });

  // A fork is a new query, so it must not inherit the source's sharing.
  it("forks a shared query as private", async () => {
    createMock.mockResolvedValue({
      data: {
        createSavedQuery: {
          success: true,
          errors: [],
          savedQuery: { id: "new-2", name: "Copy" },
        },
      },
    });

    render(
      <SaveQueryDialog
        open
        mode="create"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={savedQuery}
        onClose={jest.fn()}
        onSaved={jest.fn()}
      />,
    );

    expect(screen.getByRole("radio", { name: /Private/ })).toBeChecked();
    fireEvent.click(screen.getByRole("button", { name: "Save query" }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith({
        variables: {
          input: expect.objectContaining({
            visibility: SavedQueryVisibility.Private,
          }),
        },
      }),
    );
  });

  // The dialog is not remounted between opens (it stays mounted so it can
  // animate), so each open has to re-seed the form from the current props.
  it("re-seeds the form on every open", async () => {
    const props = {
      mode: "create" as const,
      workspaceSlug: "ws-1",
      content: "SELECT 1",
      savedQuery: null,
      onClose: jest.fn(),
      onSaved: jest.fn(),
    };
    const { rerender } = render(<SaveQueryDialog open {...props} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Abandoned draft" },
    });
    rerender(<SaveQueryDialog open={false} {...props} />);
    rerender(<SaveQueryDialog open {...props} />);

    await waitFor(() =>
      expect((screen.getByLabelText("Name") as HTMLInputElement).value).toBe(
        "",
      ),
    );
  });

  it("surfaces a permission error without navigating", async () => {
    createMock.mockResolvedValue({
      data: {
        createSavedQuery: {
          success: false,
          errors: ["PERMISSION_DENIED"],
          savedQuery: null,
        },
      },
    });
    const onSaved = jest.fn();

    render(
      <SaveQueryDialog
        open
        mode="create"
        workspaceSlug="ws-1"
        content="SELECT 1"
        savedQuery={null}
        onClose={jest.fn()}
        onSaved={onSaved}
      />,
    );

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "My query" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save query" }));

    expect(
      await screen.findByText("You are not authorized to perform this action"),
    ).toBeInTheDocument();
    expect(onSaved).not.toHaveBeenCalled();
  });
});
