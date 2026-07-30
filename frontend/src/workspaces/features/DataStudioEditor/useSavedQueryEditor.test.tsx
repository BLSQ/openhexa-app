import { act, renderHook, waitFor } from "@testing-library/react";
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
  createdBy: null,
  permissions: { update: true, delete: true },
} as any;

const readOnlyQuery = {
  ...savedQuery,
  permissions: { update: false, delete: false },
};

const renderEditor = (
  content: string,
  initialSavedQuery: any = savedQuery,
  canCreate = true,
) =>
  renderHook(
    (props: { content: string; initialSavedQuery: any }) =>
      useSavedQueryEditor({
        workspaceSlug: "ws-1",
        content: props.content,
        initialSavedQuery: props.initialSavedQuery,
        canCreate,
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

    expect(result.current.dialog).toEqual({ mode: "create" });
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

  it("does not update a query the user cannot edit", async () => {
    const { result } = renderEditor("SELECT 2", readOnlyQuery);

    expect(result.current.canUpdate).toBe(false);
    await act(async () => {
      await result.current.save();
    });
    expect(updateMock).not.toHaveBeenCalled();
  });

  it("navigates to the new query after a create dialog save", async () => {
    const { result } = renderEditor("SELECT 42", null);

    act(() => result.current.saveAsNew());
    expect(result.current.dialog).toEqual({ mode: "create" });

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
    expect(result.current.dialog).toEqual({ mode: "edit-details" });

    act(() => result.current.onDialogSaved({ ...savedQuery, name: "Renamed" }));

    expect(result.current.savedQuery?.name).toBe("Renamed");
    expect(mockRouter.asPath).toBe("/");
  });

  it("closes the dialog", () => {
    const { result } = renderEditor("SELECT 1");
    act(() => result.current.editDetails());
    expect(result.current.dialog).not.toBeNull();
    act(() => result.current.closeDialog());
    expect(result.current.dialog).toBeNull();
  });

  // `commit` is what the ⌘S/Ctrl+S shortcut calls: it has no button state to
  // lean on, so it must resolve the right action (or no action) on its own.
  describe("commit", () => {
    beforeEach(() => {
      updateMock.mockResolvedValue({
        data: {
          updateSavedQuery: {
            success: true,
            errors: [],
            savedQuery: { ...savedQuery, content: "SELECT 2" },
          },
        },
      });
    });

    it("opens the create dialog for an unsaved query", async () => {
      const { result } = renderEditor("SELECT 42", null);

      await act(async () => result.current.commit());

      expect(result.current.dialog).toEqual({ mode: "create" });
    });

    it("does nothing for an unsaved query when the user cannot create", async () => {
      const { result } = renderEditor("SELECT 42", null, false);

      await act(async () => result.current.commit());

      expect(result.current.dialog).toBeNull();
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("updates a dirty query in place", async () => {
      const { result } = renderEditor("SELECT 2");

      await act(async () => result.current.commit());

      expect(updateMock).toHaveBeenCalledWith({
        variables: { input: { id: "q1", content: "SELECT 2" } },
      });
      expect(result.current.dialog).toBeNull();
    });

    it("does nothing when the query has no unsaved changes", async () => {
      const { result } = renderEditor("SELECT 1");

      await act(async () => result.current.commit());

      expect(updateMock).not.toHaveBeenCalled();
      expect(result.current.dialog).toBeNull();
    });

    it("does nothing when the content is blank", async () => {
      const { result } = renderEditor("   ");

      await act(async () => result.current.commit());

      expect(updateMock).not.toHaveBeenCalled();
      expect(result.current.dialog).toBeNull();
    });

    it("forks a query the user cannot update", async () => {
      const { result } = renderEditor("SELECT 2", readOnlyQuery);

      await act(async () => result.current.commit());

      expect(result.current.dialog).toEqual({ mode: "create" });
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("does nothing on a read-only query when the user cannot create either", async () => {
      const { result } = renderEditor("SELECT 2", readOnlyQuery, false);

      await act(async () => result.current.commit());

      expect(result.current.dialog).toBeNull();
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("does nothing while a dialog is already open", async () => {
      const { result } = renderEditor("SELECT 2");

      act(() => result.current.editDetails());
      await act(async () => result.current.commit());

      expect(result.current.dialog).toEqual({ mode: "edit-details" });
      expect(updateMock).not.toHaveBeenCalled();
    });
  });
});
