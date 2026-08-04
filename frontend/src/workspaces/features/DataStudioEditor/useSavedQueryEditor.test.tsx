import { act, renderHook, waitFor } from "@testing-library/react";
import { SavedQueryVisibility } from "graphql/types";
import mockRouter from "next-router-mock";
import { toast } from "react-toastify";
import { useSavedQueryEditor } from "./useSavedQueryEditor";

const updateMock = jest.fn();

jest.mock("workspaces/features/SavedQueries/SavedQueries.generated", () => ({
  useCreateSavedQueryMutation: () => [jest.fn(), { loading: false }],
  useUpdateSavedQueryMutation: () => [updateMock, { loading: false }],
  useDeleteSavedQueryMutation: () => [jest.fn(), { loading: false }],
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

const savedQuery = {
  __typename: "SavedQuery",
  id: "q1",
  name: "Query One",
  description: "",
  content: "SELECT 1",
  updatedAt: "2024-01-01T00:00:00Z",
  visibility: SavedQueryVisibility.Private,
  createdBy: null,
  permissions: { update: true, delete: true, updateVisibility: true },
} as any;

const renderEditor = (content: string, initialSavedQuery: any = savedQuery) =>
  renderHook(
    (props: { content: string; initialSavedQuery: any }) =>
      useSavedQueryEditor({
        workspaceSlug: "ws-1",
        content: props.content,
        initialSavedQuery: props.initialSavedQuery,
      }),
    { initialProps: { content, initialSavedQuery } },
  );

beforeEach(() => {
  jest.clearAllMocks();
  mockRouter.setCurrentUrl("/");
});

describe("useSavedQueryEditor", () => {
  it("is clean until the content diverges from the saved baseline", () => {
    const { result, rerender } = renderEditor("SELECT 1");
    expect(result.current.isDirty).toBe(false);

    rerender({ content: "SELECT 2", initialSavedQuery: savedQuery });
    expect(result.current.isDirty).toBe(true);
  });

  it("opens the create dialog when saving a brand-new query", async () => {
    const { result } = renderEditor("SELECT 42", null);

    await act(async () => {
      await result.current.save();
    });

    expect(result.current.dialog).toEqual({ open: true, mode: "create" });
    expect(updateMock).not.toHaveBeenCalled();
  });

  it("updates the loaded query in place and clears the dirty state", async () => {
    updateMock.mockResolvedValue({
      data: {
        updateSavedQuery: {
          success: true,
          errors: [],
          savedQuery: { ...savedQuery, content: "SELECT 2" },
        },
      },
    });
    const { result } = renderEditor("SELECT 2");
    expect(result.current.isDirty).toBe(true);

    await act(async () => {
      await result.current.save();
    });

    expect(updateMock).toHaveBeenCalledWith({
      variables: { input: { id: "q1", content: "SELECT 2" } },
    });
    expect(toast.success).toHaveBeenCalledWith("Query saved");
    expect(result.current.isDirty).toBe(false);
  });

  it("shares the query without touching the unsaved content", async () => {
    updateMock.mockResolvedValue({
      data: {
        updateSavedQuery: {
          success: true,
          errors: [],
          savedQuery: {
            ...savedQuery,
            visibility: SavedQueryVisibility.Workspace,
          },
        },
      },
    });
    // Content diverges from the baseline: persisting sharing must not be mistaken
    // for saving the SQL.
    const { result } = renderEditor("SELECT 2");
    expect(result.current.isDirty).toBe(true);

    await act(async () => {
      await result.current.setVisibility(SavedQueryVisibility.Workspace);
    });

    expect(updateMock).toHaveBeenCalledWith({
      variables: {
        input: { id: "q1", visibility: SavedQueryVisibility.Workspace },
      },
    });
    expect(result.current.savedQuery?.visibility).toBe(
      SavedQueryVisibility.Workspace,
    );
    expect(toast.success).toHaveBeenCalledWith(
      "Query shared with the workspace",
    );
    expect(result.current.isDirty).toBe(true);
  });

  it("surfaces a rejected visibility change", async () => {
    updateMock.mockResolvedValue({
      data: {
        updateSavedQuery: {
          success: false,
          errors: ["PERMISSION_DENIED"],
          savedQuery: null,
        },
      },
    });
    const { result } = renderEditor("SELECT 1");

    await act(async () => {
      await result.current.setVisibility(SavedQueryVisibility.Workspace);
    });

    expect(toast.error).toHaveBeenCalledWith(
      "You are not authorized to perform this action",
    );
    expect(result.current.savedQuery?.visibility).toBe(
      SavedQueryVisibility.Private,
    );
  });

  it("does not change visibility without the permission to unshare", async () => {
    const { result } = renderEditor("SELECT 1", {
      ...savedQuery,
      permissions: { update: true, delete: true, updateVisibility: false },
    });

    expect(result.current.canUpdateVisibility).toBe(false);
    await act(async () => {
      await result.current.setVisibility(SavedQueryVisibility.Workspace);
    });
    expect(updateMock).not.toHaveBeenCalled();
  });

  it("does not update a query the user cannot edit", async () => {
    const readOnly = {
      ...savedQuery,
      permissions: { update: false, delete: false, updateVisibility: false },
    };
    const { result } = renderEditor("SELECT 2", readOnly);

    expect(result.current.canUpdate).toBe(false);
    await act(async () => {
      await result.current.save();
    });
    expect(updateMock).not.toHaveBeenCalled();
  });

  it("navigates to the new query after a create dialog save", async () => {
    const { result } = renderEditor("SELECT 42", null);

    act(() => result.current.saveAsNew());
    expect(result.current.dialog).toEqual({ open: true, mode: "create" });

    act(() => result.current.onDialogSaved({ ...savedQuery, id: "new-1" }));

    await waitFor(() =>
      expect(mockRouter.asPath).toBe(
        "/workspaces/ws-1/data-studio/queries/new-1",
      ),
    );
  });

  it("updates local metadata (no navigation) after an edit-details save", () => {
    const { result } = renderEditor("SELECT 1");

    act(() => result.current.editDetails());
    expect(result.current.dialog).toEqual({ open: true, mode: "edit-details" });

    act(() => result.current.onDialogSaved({ ...savedQuery, name: "Renamed" }));

    expect(result.current.savedQuery?.name).toBe("Renamed");
    expect(mockRouter.asPath).toBe("/");
  });

  it("starts with the dialog closed", () => {
    const { result } = renderEditor("SELECT 1");
    expect(result.current.dialog.open).toBe(false);
  });

  // The mode has to outlive the close so the title does not change while the
  // dialog fades out.
  it("closes the dialog while keeping its mode", () => {
    const { result } = renderEditor("SELECT 1");
    act(() => result.current.editDetails());
    expect(result.current.dialog.open).toBe(true);

    act(() => result.current.closeDialog());
    expect(result.current.dialog).toEqual({
      open: false,
      mode: "edit-details",
    });
  });
});
