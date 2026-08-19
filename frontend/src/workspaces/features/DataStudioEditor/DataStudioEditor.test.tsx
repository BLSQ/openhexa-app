import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SavedQueryVisibility } from "graphql/types";
import { ComponentProps } from "react";
import DataStudioEditor from "./DataStudioEditor";
import { downloadQueryCsv } from "./downloadQueryCsv";

// `useTranslation` is globally mocked to echo the key, so button/label
// assertions below use the raw key strings.

const mockExecute = jest.fn();
let mockQueryState: { data?: unknown; loading: boolean; error?: unknown };

jest.mock("./DataStudioEditor.generated", () => ({
  useExecuteWorkspaceSqlLazyQuery: () => [mockExecute, mockQueryState],
}));

// The schema powers CodeMirror's `sqlSchema` prop, which the CodeEditor mock
// below doesn't inspect; stubbed here purely so DataStudioEditor's own call to
// this hook (for autocomplete) doesn't need a real Apollo provider in this file.
let mockSchemaState: { data?: unknown; loading?: boolean } = { loading: false };

jest.mock("./DataStudioSchemaBrowser.generated", () => ({
  useWorkspaceDataStudioSchemaQuery: () => mockSchemaState,
}));

const mockEditDetails = jest.fn();
const mockSetVisibility = jest.fn();
const mockCommit = jest.fn();
const mockPlanSave = jest.fn();
let mockEditorState: any;

// Stand-in for `useSavedQueryEditor`'s resolved save policy. The hook decides
// what saving means (covered in its own suite); these tests only check that the
// toolbar and the ⌘S binding render/run whatever it hands them.
const savePlan = (overrides: Record<string, unknown> = {}) => ({
  variant: "create",
  save: mockPlanSave,
  blockedBy: null,
  saveAsNew: null,
  ...overrides,
});

// The save/write path (Apollo mutations + router navigation) is exercised in
// its own suite; stub it here so these tests stay focused on run/export/schema
// orchestration and need no ApolloProvider or router. `mockEditorState` is
// (re)initialised in beforeEach so a test can flip it to a saved/updatable
// query and exercise the edit-details pencil.
jest.mock("./useSavedQueryEditor", () => ({
  useSavedQueryEditor: () => mockEditorState,
}));

// The dialog owns its own mutations (covered by its suite); stub it down to the
// props this file cares about so no ApolloProvider is needed.
jest.mock("workspaces/features/SavedQueries/SaveQueryDialog", () => ({
  __esModule: true,
  default: ({ open, mode }: { open: boolean; mode: string }) => (
    <div
      data-testid="save-query-dialog"
      data-open={String(open)}
      data-mode={mode}
    />
  ),
}));

// The schema browser and results grid are covered by their own tests; stub them
// so this file exercises only the editor's orchestration logic.
jest.mock("./DataStudioSchemaBrowser", () => ({
  __esModule: true,
  default: ({ onInsert }: { onInsert: (text: string) => void }) => (
    <button onClick={() => onInsert("patients")}>insert-from-schema</button>
  ),
}));

jest.mock("./DataStudioResults", () => ({
  __esModule: true,
  default: ({
    loading,
    result,
    error,
    onRetry,
  }: {
    loading: boolean;
    result?: any;
    error?: any;
    onRetry?: () => void;
  }) => (
    <div
      data-testid="results"
      data-loading={String(loading)}
      data-success={String(Boolean(result?.success))}
      data-error={String(Boolean(error))}
    >
      {onRetry && <button onClick={onRetry}>retry-results</button>}
    </div>
  ),
}));

const mockInsertText = jest.fn();
const mockShortcuts: { current: { key: string }[] } = { current: [] };
const shortcutKeys = () => mockShortcuts.current.map((s) => s.key);
let lastCodeEditorProps: any;

// A lightweight stand-in for the CodeMirror editor: a controlled textarea whose
// imperative handle mirrors the real one (insertText + selection-aware
// getSelectedText), so selection-based behavior can be driven from tests.
jest.mock("core/components/CodeEditor/CodeEditor", () => {
  const React = require("react");
  return {
    __esModule: true,
    default: React.forwardRef(function CodeEditorMock(props: any, ref: any) {
      lastCodeEditorProps = props;
      const innerRef = React.useRef(null);
      mockShortcuts.current = props.shortcuts ?? [];
      React.useImperativeHandle(ref, () => ({
        insertText: mockInsertText,
        getSelectedText: () => {
          const el = innerRef.current;
          if (!el) return "";
          return el.value.slice(el.selectionStart ?? 0, el.selectionEnd ?? 0);
        },
        // The real handle writes through CodeMirror, which fires onChange; the
        // stand-in calls it directly so the controlled value stays in sync.
        replaceAll: (text: string) => props.onChange?.(text),
      }));
      // Mirror CodeMirror's keymap: a matching shortcut runs its handler and
      // consumes the event (preventDefault), so no newline is inserted. Only
      // the Enter bindings are simulated — the format shortcuts are covered
      // against the real editor in CodeEditor.test.tsx, where the binding has
      // to win against CodeMirror's own keymap to pass.
      const onKeyDown = (event: any) => {
        if (event.key !== "Enter" || !(event.metaKey || event.ctrlKey)) {
          return;
        }
        const shortcut = (props.shortcuts ?? []).find((s: { key: string }) =>
          ["Mod-Enter", "Ctrl-Enter", "Cmd-Enter"].includes(s.key),
        );
        if (shortcut) {
          event.preventDefault();
          shortcut.run();
        }
      };
      return React.createElement("textarea", {
        ref: innerRef,
        "data-testid": "editor",
        value: props.value ?? "",
        placeholder: props.placeholder,
        onChange: (event: any) => props.onChange?.(event.target.value),
        onKeyDown,
      });
    }),
  };
});

jest.mock("./downloadQueryCsv", () => ({
  downloadQueryCsv: jest.fn(),
}));

jest.mock("react-toastify", () => ({
  toast: { error: jest.fn() },
}));

// GenerateSqlBar pulls in the real Apollo `useCreateAssistantConversationMutation`
// hook, which needs an ApolloProvider this file doesn't set up. Stubbed the same way
// as DataStudioSchemaBrowser/DataStudioResults above, exposing just enough (the
// `open` prop and a call to trigger onGenerated) to test DataStudioEditor's own wiring.
jest.mock("./GenerateSqlBar", () => ({
  __esModule: true,
  default: ({
    open,
    form,
  }: {
    open: boolean;
    onClose: () => void;
    form: { handleSubmit: () => void };
  }) =>
    open ? (
      <div data-testid="generate-bar">
        <button onClick={form.handleSubmit}>trigger-generate</button>
      </div>
    ) : null,
  useGenerateSqlForm: (
    _workspaceSlug: string,
    onGenerated: (sql: string) => void,
  ) => ({
    handleSubmit: () => onGenerated("SELECT 1"),
  }),
}));

const successState = (overrides: Record<string, unknown> = {}) => ({
  loading: false,
  data: {
    workspace: {
      slug: "ws-1",
      database: {
        executeSQL: {
          success: true,
          errors: [],
          errorMessage: null,
          columns: ["id"],
          rows: [{ id: 1 }],
          rowCount: 1,
          truncated: false,
          durationMs: 3,
          ...overrides,
        },
      },
    },
  },
});

const renderEditor = (
  props: Partial<ComponentProps<typeof DataStudioEditor>> = {},
) =>
  render(
    <DataStudioEditor workspaceSlug="ws-1" canCreate={false} {...props} />,
  );

beforeEach(() => {
  mockExecute.mockClear();
  mockInsertText.mockClear();
  mockEditDetails.mockClear();
  (downloadQueryCsv as jest.Mock).mockClear();
  (downloadQueryCsv as jest.Mock).mockResolvedValue(undefined);
  mockSetVisibility.mockClear();
  mockCommit.mockClear();
  mockPlanSave.mockClear();
  mockQueryState = { loading: false };
  mockSchemaState = { loading: false };
  mockEditorState = {
    savedQuery: null,
    isDirty: false,
    saving: false,
    canUpdate: false,
    canUpdateVisibility: false,
    dialog: { open: false, mode: "create" },
    savePlan: savePlan(),
    save: jest.fn(),
    setVisibility: mockSetVisibility,
    saveAsNew: jest.fn(),
    commit: mockCommit,
    editDetails: mockEditDetails,
    closeDialog: jest.fn(),
    onDialogSaved: jest.fn(),
  };
});

describe("DataStudioEditor", () => {
  it("runs the trimmed query with the default max rows on click", async () => {
    renderEditor();
    await userEvent.type(screen.getByTestId("editor"), "  SELECT 1  ");
    await userEvent.click(screen.getByRole("button", { name: "Run" }));

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 1", maxRows: 50 },
    });
  });

  it("passes the chosen max rows to the query", async () => {
    renderEditor();
    await userEvent.type(screen.getByTestId("editor"), "SELECT 1");
    await userEvent.selectOptions(screen.getByRole("combobox"), "1000");
    await userEvent.click(screen.getByRole("button", { name: "Run" }));

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 1", maxRows: 1000 },
    });
  });

  it("runs the full query on Ctrl/Cmd+Enter with no selection, and suppresses the newline", async () => {
    renderEditor();
    await userEvent.type(screen.getByTestId("editor"), "SELECT 1");
    // fireEvent returns false when a handler called preventDefault — i.e. the
    // keystroke was consumed and will not insert a line break.
    const notPrevented = fireEvent.keyDown(screen.getByTestId("editor"), {
      key: "Enter",
      ctrlKey: true,
    });

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 1", maxRows: 50 },
    });
    expect(notPrevented).toBe(false);
  });

  it("runs only the selected text on Ctrl/Cmd+Enter when there is a selection", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor") as HTMLTextAreaElement;
    await userEvent.type(editor, "SELECT 1 SELECT 2");
    editor.setSelectionRange(9, 17);

    fireEvent.keyDown(editor, { key: "Enter", ctrlKey: true });

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 2", maxRows: 50 },
    });
  });

  it("surfaces the run shortcut hint on the Run button (Ctrl+Enter on non-mac)", () => {
    renderEditor();
    // jsdom's userAgent is not a Mac, so the in-button pill uses the Ctrl variant.
    expect(screen.getByText("Ctrl+Enter")).toBeInTheDocument();
  });

  it("does not run when the query is empty", async () => {
    renderEditor();
    const runButton = screen.getByRole("button", { name: "Run" });
    expect(runButton).toBeDisabled();

    await userEvent.click(runButton);
    expect(mockExecute).not.toHaveBeenCalled();
  });

  it("runs only the selected text when Run is clicked with a selection", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor") as HTMLTextAreaElement;
    await userEvent.type(editor, "SELECT 1 SELECT 2");
    editor.setSelectionRange(9, 17);

    await userEvent.click(screen.getByRole("button", { name: "Run" }));

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 2", maxRows: 50 },
    });
  });

  it("shows an inline in-progress affordance while a server export runs", async () => {
    let resolveDownload!: () => void;
    (downloadQueryCsv as jest.Mock).mockReturnValue(
      new Promise<void>((res) => {
        resolveDownload = res;
      }),
    );
    mockQueryState = successState({ truncated: true });
    renderEditor();
    await userEvent.type(screen.getByTestId("editor"), "SELECT 1");
    await userEvent.click(screen.getByRole("button", { name: "Run" }));

    await userEvent.click(screen.getByRole("button", { name: "Export CSV" }));

    const exportingButton = screen.getByRole("button", { name: "Exporting…" });
    expect(exportingButton).toBeDisabled();
    expect(screen.getByText("This may take a while")).toBeInTheDocument();

    resolveDownload();
    await waitFor(() =>
      expect(
        screen.queryByText("This may take a while"),
      ).not.toBeInTheDocument(),
    );
  });

  it("disables export until there is a successful result with rows", () => {
    renderEditor();
    expect(screen.getByRole("button", { name: "Export CSV" })).toBeDisabled();
  });

  it("does not enable export for a successful result with no rows", () => {
    mockQueryState = successState({ rows: [], rowCount: 0 });
    renderEditor();
    expect(screen.getByRole("button", { name: "Export CSV" })).toBeDisabled();
  });

  it("forwards schema browser insertions to the editor", async () => {
    renderEditor();
    await userEvent.click(screen.getByText("insert-from-schema"));
    expect(mockInsertText).toHaveBeenCalledWith("patients");
  });

  it("builds a CodeMirror sqlSchema from the fetched table/column schema", () => {
    mockSchemaState = {
      loading: false,
      data: {
        workspace: {
          slug: "ws-1",
          database: {
            tables: {
              totalItems: 1,
              items: [
                {
                  name: "patients",
                  columns: [
                    { name: "id", type: "integer" },
                    { name: "name", type: "text" },
                  ],
                },
              ],
            },
          },
        },
      },
    };
    renderEditor();

    expect(lastCodeEditorProps.sqlSchema).toEqual({
      patients: [
        { label: "id", type: "property", detail: "integer" },
        { label: "name", type: "property", detail: "text" },
      ],
    });
  });

  it("forwards a transport error to the results panel", () => {
    mockQueryState = { loading: false, error: new Error("network down") };
    renderEditor();
    expect(screen.getByTestId("results")).toHaveAttribute("data-error", "true");
  });

  it("retries the exact variables that were last run", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor") as HTMLTextAreaElement;
    await userEvent.type(editor, "SELECT 1 SELECT 2");
    editor.setSelectionRange(9, 17);
    await userEvent.click(screen.getByRole("button", { name: "Run" }));
    mockExecute.mockClear();

    await userEvent.click(screen.getByText("retry-results"));

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 2", maxRows: 50 },
    });
  });

  it("does not retry before any query has been run", async () => {
    renderEditor();
    await userEvent.click(screen.getByText("retry-results"));
    expect(mockExecute).not.toHaveBeenCalled();
  });

  it("shows a running state and blocks re-runs while loading", () => {
    mockQueryState = { loading: true };
    renderEditor();

    expect(screen.getByText("Running…")).toBeInTheDocument();
    expect(screen.getByTestId("results")).toHaveAttribute(
      "data-loading",
      "true",
    );
  });

  // Headless UI skips the enter transition of a dialog that mounts already open,
  // so the dialog has to stay mounted and be driven by `open`.
  it("keeps the save dialog mounted while it is closed", () => {
    renderEditor();

    const dialog = screen.getByTestId("save-query-dialog");
    expect(dialog).toHaveAttribute("data-open", "false");
  });

  it("passes the open state and mode of the dialog through", () => {
    mockEditorState.dialog = { open: true, mode: "edit-details" };
    renderEditor();

    const dialog = screen.getByTestId("save-query-dialog");
    expect(dialog).toHaveAttribute("data-open", "true");
    expect(dialog).toHaveAttribute("data-mode", "edit-details");
  });

  it("opens the edit-details dialog from the pencil next to a saved query name", async () => {
    mockEditorState.savedQuery = {
      id: "q1",
      name: "Cohort query",
      visibility: SavedQueryVisibility.Private,
    };
    mockEditorState.canUpdate = true;
    renderEditor();

    expect(screen.getByText("Cohort query")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Edit details" }));
    expect(mockEditDetails).toHaveBeenCalledTimes(1);
  });

  it("hides the edit-details pencil when the query cannot be updated", () => {
    mockEditorState.savedQuery = {
      id: "q1",
      name: "Cohort query",
      visibility: SavedQueryVisibility.Private,
    };
    mockEditorState.canUpdate = false;
    renderEditor();

    expect(
      screen.queryByRole("button", { name: "Edit details" }),
    ).not.toBeInTheDocument();
  });

  it("shows the visibility control only once a query is saved", () => {
    renderEditor();
    expect(screen.queryByText("Private")).not.toBeInTheDocument();

    mockEditorState.savedQuery = {
      id: "q1",
      name: "Cohort query",
      visibility: SavedQueryVisibility.Private,
    };
    mockEditorState.canUpdateVisibility = true;
    renderEditor();

    expect(screen.getByRole("button", { name: /Private/ })).toBeInTheDocument();
  });

  it("disables Save when the plan withholds it, and runs it when offered", async () => {
    mockEditorState.savePlan = savePlan({ save: null, blockedBy: "empty" });
    const { unmount } = renderEditor();

    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();
    unmount();

    mockEditorState.savePlan = savePlan();
    renderEditor();

    const save = screen.getByRole("button", { name: "Save" });
    expect(save).toBeEnabled();
    await userEvent.click(save);
    expect(mockPlanSave).toHaveBeenCalledTimes(1);
  });

  it("shows no save control when the plan offers no variant", () => {
    mockEditorState.savePlan = savePlan({ variant: null, save: null });
    renderEditor();

    expect(
      screen.queryByRole("button", { name: "Save" }),
    ).not.toBeInTheDocument();
  });

  it.each([
    ["Cmd+S", { key: "s", metaKey: true }],
    ["Ctrl+S", { key: "s", ctrlKey: true }],
  ])("saves on %s and suppresses the browser save dialog", (_label, init) => {
    renderEditor();

    expect(fireEvent.keyDown(window, init)).toBe(false);
    expect(mockCommit).toHaveBeenCalledTimes(1);
  });

  it("saves once on Ctrl/Cmd+S from inside the SQL editor", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor");
    await userEvent.type(editor, "SELECT 1");

    // Only bound on the window, so a keystroke in the buffer bubbles up to a
    // single handler instead of also hitting a CodeMirror binding.
    fireEvent.keyDown(editor, { key: "s", ctrlKey: true });

    expect(mockCommit).toHaveBeenCalledTimes(1);
  });

  it("never hands Ctrl/Cmd+S back to the browser while the save dialog is open", () => {
    mockEditorState.dialog = { open: true, mode: "create" };
    renderEditor();
    expect(screen.getByTestId("save-query-dialog")).toHaveAttribute(
      "data-open",
      "true",
    );

    // The dialog has no ⌘S binding of its own, so releasing the keystroke here
    // would open the browser's "Save page as…" on top of the dialog. It stays
    // consumed; `commit` is the one that decides the dialog owns the keyboard.
    expect(fireEvent.keyDown(window, { key: "s", ctrlKey: true })).toBe(false);
  });

  it("surfaces the save shortcut in the Save tooltip (Ctrl+S on non-mac)", () => {
    renderEditor();

    // jsdom's userAgent is not a Mac, so the tooltip uses the Ctrl variant.
    expect(screen.getByRole("button", { name: "Save" })).toHaveAttribute(
      "title",
      "Save query (Ctrl+S)",
    );
  });

  it("hides the Generate button when AI is not enabled for the workspace", () => {
    renderEditor();
    expect(
      screen.queryByRole("button", { name: "Generate" }),
    ).not.toBeInTheDocument();
  });

  it("opens the generate bar from the toolbar when AI is enabled", async () => {
    renderEditor({ aiEnabled: true });
    expect(screen.queryByTestId("generate-bar")).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Generate" }));

    expect(screen.getByTestId("generate-bar")).toBeInTheDocument();
  });

  it("disables the Generate button once the AI budget is exhausted", () => {
    renderEditor({ aiEnabled: true, aiBudgetLimitReached: true });
    expect(screen.getByRole("button", { name: "Generate" })).toBeDisabled();
  });

  it("fills the editor with the generated query and closes the bar", async () => {
    renderEditor({ aiEnabled: true });
    await userEvent.click(screen.getByRole("button", { name: "Generate" }));

    await userEvent.click(screen.getByText("trigger-generate"));

    expect(screen.getByTestId("editor")).toHaveValue("SELECT 1");
    expect(screen.queryByTestId("generate-bar")).not.toBeInTheDocument();
  });

  const FORMATTED = "SELECT\n  id\nFROM\n  patients";

  it("formats the whole query on click", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor");
    await userEvent.type(editor, "select id from patients");

    await userEvent.click(screen.getByRole("button", { name: "Format" }));

    expect(editor).toHaveValue(FORMATTED);
  });

  it("formats the whole query even when part of it is selected", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor") as HTMLTextAreaElement;
    await userEvent.type(editor, "select id from patients");
    editor.setSelectionRange(7, 9);

    await userEvent.click(screen.getByRole("button", { name: "Format" }));

    // A selection must not narrow the scope: formatting a fragment produces
    // left-aligned multi-line text that would corrupt the surrounding line.
    expect(editor).toHaveValue(FORMATTED);
    expect(mockInsertText).not.toHaveBeenCalled();
  });

  it("registers the format shortcut on the editor", () => {
    renderEditor();
    // The bindings themselves are exercised against real CodeMirror in
    // CodeEditor.test.tsx; this only pins the keys this editor asks for. Both
    // cases are required — macOS resolves ⇧⌥F to the uppercase spec.
    expect(shortcutKeys()).toEqual(
      expect.arrayContaining(["Shift-Alt-f", "Shift-Alt-F"]),
    );
  });

  it("leaves Mod-f to the editor's find", () => {
    renderEditor();
    expect(shortcutKeys()).not.toContain("Mod-f");
  });

  it("disables Format while the query is empty", async () => {
    renderEditor();
    expect(screen.getByRole("button", { name: "Format" })).toBeDisabled();

    await userEvent.type(screen.getByTestId("editor"), "select 1");
    expect(screen.getByRole("button", { name: "Format" })).toBeEnabled();
  });
});
