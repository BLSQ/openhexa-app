import { act, renderHook, waitFor } from "@testing-library/react";
import mockRouter from "next-router-mock";
import { toast } from "react-toastify";
import { readScratch, writeScratch } from "./dataStudioScratch";
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

const renderEditor = (
  content: string,
  initialSavedQuery: any = savedQuery,
  canCreate = true,
) =>
  renderHook(
    (props: { content: string; initialSavedQuery: any }) =>
      useSavedQueryEditor({
        userId: "user-1",
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
    const readOnly = {
      ...savedQuery,
      permissions: { update: false, delete: false },
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

  describe("navigation guard", () => {
    const leave = () => mockRouter.push("/elsewhere");

    it("warns before leaving a saved query with unsaved changes", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      renderEditor("SELECT 2");

      await expect(leave()).rejects.toBe("Route change aborted");
      expect(window.confirm).toHaveBeenCalled();
      expect(mockRouter.asPath).toBe("/");
    });

    it("does not warn when the saved query is unchanged", async () => {
      renderEditor("SELECT 1");

      await act(() => leave());

      expect(window.confirm).not.toHaveBeenCalled();
    });

    it("does not warn about the unsaved editor", async () => {
      renderEditor("SELECT 42", null);

      await act(() => leave());

      expect(window.confirm).not.toHaveBeenCalled();
    });

    it("does not warn a viewer, who has no way to keep the changes", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      const readOnly = {
        ...savedQuery,
        permissions: { update: false, delete: false },
      };
      renderEditor("SELECT 2", readOnly, false);

      await act(() => leave());

      expect(window.confirm).not.toHaveBeenCalled();
      expect(mockRouter.asPath).toBe("/elsewhere");
    });

    it("warns a viewer who can still save the changes as a new query", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      const readOnly = {
        ...savedQuery,
        permissions: { update: false, delete: false },
      };
      renderEditor("SELECT 2", readOnly, true);

      await expect(leave()).rejects.toBe("Route change aborted");
      expect(window.confirm).toHaveBeenCalled();
    });

    it("does not warn about the redirect that follows a save-as-new", async () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      const { result } = renderEditor("SELECT 2");

      act(() => result.current.saveAsNew());
      await act(async () => {
        result.current.onDialogSaved({ ...savedQuery, id: "new-1" });
      });

      expect(window.confirm).not.toHaveBeenCalled();
      expect(mockRouter.asPath).toBe(
        "/workspaces/ws-1/data-studio/queries/new-1",
      );
    });
  });

  describe("scratch draft", () => {
    const scope = { userId: "user-1", workspaceSlug: "ws-1" };

    it("clears the draft once it becomes a saved query", async () => {
      writeScratch(scope, "SELECT 42");
      const { result } = renderEditor("SELECT 42", null);

      act(() => result.current.saveAsNew());
      await act(async () => {
        result.current.onDialogSaved({ ...savedQuery, id: "new-1" });
      });

      expect(readScratch(scope)).toBe("");
    });

    it("keeps the draft when a copy of a saved query is created", async () => {
      writeScratch(scope, "SELECT 42");
      const { result } = renderEditor("SELECT 2");

      act(() => result.current.saveAsNew());
      await act(async () => {
        result.current.onDialogSaved({ ...savedQuery, id: "new-1" });
      });

      expect(readScratch(scope)).toBe("SELECT 42");
    });
  });
});
