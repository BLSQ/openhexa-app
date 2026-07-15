import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { toast } from "react-toastify";
import SaveQueryDialog from "./SaveQueryDialog";

const createMock = jest.fn();
const updateMock = jest.fn();

jest.mock("workspaces/features/SavedQueries/SavedQueries.generated", () => ({
  useCreateSavedQueryMutation: () => [createMock, { loading: false }],
  useUpdateSavedQueryMutation: () => [updateMock, { loading: false }],
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("core/hooks/useCacheKey", () => ({
  __esModule: true,
  default: () => jest.fn(),
}));

beforeEach(() => jest.clearAllMocks());

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

  it("edits only name/description in edit-details mode", async () => {
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
        savedQuery={{ id: "q1", name: "Old name", description: "desc" }}
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
          input: { id: "q1", name: "Renamed", description: "desc" },
        },
      }),
    );
    expect(createMock).not.toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith("Query updated");
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
