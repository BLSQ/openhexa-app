import { act, renderHook, waitFor } from "@testing-library/react";
import { NavigationAbortedError } from "core/hooks/useNavigationWarning";
import mockRouter from "next-router-mock";
import { toast } from "react-toastify";
import { useSavedQueryEditor } from "./useSavedQueryEditor";

const updateMock = jest.fn();
// Flipped by the tests that need an in-flight save; the hook reads it as
// `saving`, which is what keeps a second ⌘S from firing a duplicate mutation.
let mockUpdating = false;

jest.mock("workspaces/features/SavedQueries/SavedQueries.generated", () => ({
  useCreateSavedQueryMutation: () => [jest.fn(), { loading: false }],
  useUpdateSavedQueryMutation: () => [updateMock, { loading: mockUpdating }],
  useDeleteSavedQueryMutation: () => [jest.fn(), { loading: false }],
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

const savedQuery = {
  __typename: "SavedQuery",
  id: "q1",
  slug: "query-one",
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
  mockUpdating = false;
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
    expect(result.current.dialog).toEqual({ open: true, mode: "create" });

    act(() =>
      result.current.onDialogSaved({
        ...savedQuery,
        id: "new-1",
        slug: "new-one",
      }),
    );

    await waitFor(() =>
      expect(mockRouter.asPath).toBe(
        "/workspaces/ws-1/data-studio/queries/new-one",
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

  describe("navigation guard", () => {
    const leave = () => mockRouter.push("/elsewhere");

    it("warns before leaving a saved query with unsaved changes", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      renderEditor("SELECT 2");

      await expect(leave()).rejects.toBeInstanceOf(NavigationAbortedError);
      expect(window.confirm).toHaveBeenCalled();
      expect(mockRouter.asPath).toBe("/");
    });

    it("does not warn when the saved query is unchanged", async () => {
      renderEditor("SELECT 1");

      await act(() => leave());

      expect(window.confirm).not.toHaveBeenCalled();
    });

    it("does not warn about an emptied buffer, which Save refuses anyway", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      renderEditor("   ");

      await act(() => leave());

      expect(window.confirm).not.toHaveBeenCalled();
      expect(mockRouter.asPath).toBe("/elsewhere");
    });

    it("does not warn about the unsaved editor", async () => {
      renderEditor("SELECT 42", null);

      await act(() => leave());

      expect(window.confirm).not.toHaveBeenCalled();
    });

    it("does not warn a viewer, who has no way to keep the changes", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      renderEditor("SELECT 2", readOnlyQuery, false);

      await act(() => leave());

      expect(window.confirm).not.toHaveBeenCalled();
      expect(mockRouter.asPath).toBe("/elsewhere");
    });

    it("warns a viewer who can still save the changes as a new query", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      renderEditor("SELECT 2", readOnlyQuery, true);

      await expect(leave()).rejects.toBeInstanceOf(NavigationAbortedError);
      expect(window.confirm).toHaveBeenCalled();
    });

    it("does not warn about the redirect that follows a save-as-new", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      const { result } = renderEditor("SELECT 2");

      act(() => result.current.saveAsNew());
      await act(async () => {
        result.current.onDialogSaved({
          ...savedQuery,
          id: "new-1",
          slug: "new-one",
        });
      });

      expect(window.confirm).not.toHaveBeenCalled();
      expect(mockRouter.asPath).toBe(
        "/workspaces/ws-1/data-studio/queries/new-one",
      );
    });
  });

  // The plan is the single source of truth the Save button renders from and the
  // ⌘S shortcut runs, so it has to name the right action and the right reason
  // for withholding it in every permission/dirtiness combination.
  describe("savePlan", () => {
    it("offers creation for an unsaved query", () => {
      const { result } = renderEditor("SELECT 42", null);

      expect(result.current.savePlan).toMatchObject({
        variant: "create",
        blockedBy: null,
        saveAsNew: null,
      });
      expect(result.current.savePlan.save).toBeInstanceOf(Function);
    });

    it("offers no save control at all when the user cannot create", () => {
      const { result } = renderEditor("SELECT 42", null, false);

      expect(result.current.savePlan).toEqual({
        variant: null,
        save: null,
        blockedBy: null,
        saveAsNew: null,
      });
    });

    it("offers an in-place update plus a fork for a dirty updatable query", () => {
      const { result } = renderEditor("SELECT 2");

      expect(result.current.savePlan.variant).toBe("update");
      expect(result.current.savePlan.blockedBy).toBeNull();
      expect(result.current.savePlan.save).toBeInstanceOf(Function);
      expect(result.current.savePlan.saveAsNew).toBeInstanceOf(Function);
    });

    it("withholds the update of a clean query, keeping the fork available", () => {
      const { result } = renderEditor("SELECT 1");

      expect(result.current.savePlan.blockedBy).toBe("clean");
      expect(result.current.savePlan.save).toBeNull();
      expect(result.current.savePlan.saveAsNew).toBeInstanceOf(Function);
    });

    it("withholds every action while the buffer is blank", () => {
      const { result } = renderEditor("   ");

      expect(result.current.savePlan.blockedBy).toBe("empty");
      expect(result.current.savePlan.save).toBeNull();
      expect(result.current.savePlan.saveAsNew).toBeNull();
    });

    it("withholds every action while a save is in flight", () => {
      mockUpdating = true;
      const { result } = renderEditor("SELECT 2");

      expect(result.current.savePlan.blockedBy).toBe("saving");
      expect(result.current.savePlan.save).toBeNull();
      expect(result.current.savePlan.saveAsNew).toBeNull();
    });

    it("drops the fork sibling when the user cannot create", () => {
      const { result } = renderEditor("SELECT 2", savedQuery, false);

      expect(result.current.savePlan.variant).toBe("update");
      expect(result.current.savePlan.save).toBeInstanceOf(Function);
      expect(result.current.savePlan.saveAsNew).toBeNull();
    });

    it("makes forking the primary action on a read-only query", () => {
      const { result } = renderEditor("SELECT 2", readOnlyQuery);

      expect(result.current.savePlan).toMatchObject({
        variant: "fork",
        blockedBy: null,
        // The fork is the primary control here, not a sibling of a Save.
        saveAsNew: null,
      });

      act(() => result.current.savePlan.save!());
      expect(result.current.dialog).toEqual({ open: true, mode: "create" });
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("offers nothing on a read-only query the user cannot fork either", () => {
      const { result } = renderEditor("SELECT 2", readOnlyQuery, false);

      expect(result.current.savePlan.variant).toBeNull();
      expect(result.current.savePlan.save).toBeNull();
    });
  });

  // `commit` is what the ⌘S/Ctrl+S shortcut calls: it runs whatever the primary
  // Save button would, and must stay silent where that button is unavailable.
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

      expect(result.current.dialog).toEqual({ open: true, mode: "create" });
    });

    it("does nothing for an unsaved query when the user cannot create", async () => {
      const { result } = renderEditor("SELECT 42", null, false);

      await act(async () => result.current.commit());

      expect(result.current.dialog.open).toBe(false);
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("updates a dirty query in place", async () => {
      const { result } = renderEditor("SELECT 2");

      await act(async () => result.current.commit());

      expect(updateMock).toHaveBeenCalledWith({
        variables: { input: { id: "q1", content: "SELECT 2" } },
      });
      expect(result.current.dialog.open).toBe(false);
    });

    it("does nothing when the query has no unsaved changes", async () => {
      const { result } = renderEditor("SELECT 1");

      await act(async () => result.current.commit());

      expect(updateMock).not.toHaveBeenCalled();
      expect(result.current.dialog.open).toBe(false);
    });

    it("does nothing when the content is blank", async () => {
      const { result } = renderEditor("   ");

      await act(async () => result.current.commit());

      expect(updateMock).not.toHaveBeenCalled();
      expect(result.current.dialog.open).toBe(false);
    });

    it("forks a query the user cannot update", async () => {
      const { result } = renderEditor("SELECT 2", readOnlyQuery);

      await act(async () => result.current.commit());

      expect(result.current.dialog).toEqual({ open: true, mode: "create" });
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("does nothing on a read-only query when the user cannot create either", async () => {
      const { result } = renderEditor("SELECT 2", readOnlyQuery, false);

      await act(async () => result.current.commit());

      expect(result.current.dialog.open).toBe(false);
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("does nothing while a dialog is already open", async () => {
      const { result } = renderEditor("SELECT 2");

      act(() => result.current.editDetails());
      await act(async () => result.current.commit());

      expect(result.current.dialog).toEqual({
        open: true,
        mode: "edit-details",
      });
      expect(updateMock).not.toHaveBeenCalled();
    });

    it("does nothing while a save is already in flight", async () => {
      mockUpdating = true;
      const { result } = renderEditor("SELECT 2");

      await act(async () => result.current.commit());

      expect(updateMock).not.toHaveBeenCalled();
    });
  });
});
