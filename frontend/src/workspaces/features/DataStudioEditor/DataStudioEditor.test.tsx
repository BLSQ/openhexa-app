import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { downloadBlob } from "core/helpers/files";
import DataStudioEditor from "./DataStudioEditor";

// `useTranslation` is globally mocked to echo the key, so button/label
// assertions below use the raw key strings.

const mockExecute = jest.fn();
let mockQueryState: { data?: unknown; loading: boolean; error?: unknown };

jest.mock("./DataStudioEditor.generated", () => ({
  useExecuteWorkspaceSqlLazyQuery: () => [mockExecute, mockQueryState],
}));

const mockEditDetails = jest.fn();
let mockEditorState: any;

// The save/write path (Apollo mutations + router navigation) is exercised in
// its own suite; stub it here so these tests stay focused on run/export/schema
// orchestration and need no ApolloProvider or router. `mockEditorState` is
// (re)initialised in beforeEach so a test can flip it to a saved/updatable
// query and exercise the edit-details pencil.
jest.mock("./useSavedQueryEditor", () => ({
  useSavedQueryEditor: () => mockEditorState,
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

// A lightweight stand-in for the CodeMirror editor: a controlled textarea whose
// imperative handle mirrors the real one (insertText + selection-aware
// getSelectedText), so selection-based behavior can be driven from tests.
jest.mock("core/components/CodeEditor/CodeEditor", () => {
  const React = require("react");
  return {
    __esModule: true,
    default: React.forwardRef(function CodeEditorMock(props: any, ref: any) {
      const innerRef = React.useRef(null);
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
      // consumes the event (preventDefault), so the keystroke's default action
      // — a newline, or the browser find bar — does not also happen.
      const onKeyDown = (event: any) => {
        const keys = (() => {
          if (event.metaKey || event.ctrlKey) {
            if (event.key === "Enter") {
              return ["Mod-Enter", "Ctrl-Enter", "Cmd-Enter"];
            }
            if (event.key === "f") {
              return ["Mod-f"];
            }
          }
          if (event.altKey && event.shiftKey && event.key === "f") {
            return ["Shift-Alt-f"];
          }
          return [];
        })();
        const shortcut = (props.shortcuts ?? []).find((s: { key: string }) =>
          keys.includes(s.key),
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

jest.mock("core/helpers/files", () => ({
  downloadBlob: jest.fn(),
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

const renderEditor = () => render(<DataStudioEditor workspaceSlug="ws-1" />);

beforeEach(() => {
  mockExecute.mockClear();
  mockInsertText.mockClear();
  (downloadBlob as jest.Mock).mockClear();
  mockEditDetails.mockClear();
  mockQueryState = { loading: false };
  mockEditorState = {
    savedQuery: null,
    isDirty: false,
    saving: false,
    canUpdate: false,
    dialog: null,
    save: jest.fn(),
    saveAsNew: jest.fn(),
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

  it("exports the current result to CSV", async () => {
    mockQueryState = successState();
    renderEditor();

    await userEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    expect(downloadBlob).toHaveBeenCalledTimes(1);
    expect(downloadBlob).toHaveBeenCalledWith(
      "query-results.csv",
      expect.any(Blob),
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

  it("opens the edit-details dialog from the pencil next to a saved query name", async () => {
    mockEditorState.savedQuery = { id: "q1", name: "Cohort query" };
    mockEditorState.canUpdate = true;
    renderEditor();

    expect(screen.getByText("Cohort query")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Edit details" }));
    expect(mockEditDetails).toHaveBeenCalledTimes(1);
  });

  it("hides the edit-details pencil when the query cannot be updated", () => {
    mockEditorState.savedQuery = { id: "q1", name: "Cohort query" };
    mockEditorState.canUpdate = false;
    renderEditor();

    expect(
      screen.queryByRole("button", { name: "Edit details" }),
    ).not.toBeInTheDocument();
  });

  it("blocks in-place Save while an existing query's content is empty", async () => {
    mockEditorState.savedQuery = { id: "q1", name: "Cohort query" };
    mockEditorState.canUpdate = true;
    mockEditorState.isDirty = true;
    renderEditor();

    // Content starts empty (wiped), so Save stays disabled even though dirty.
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();

    await userEvent.type(screen.getByTestId("editor"), "SELECT 1");
    expect(screen.getByRole("button", { name: "Save" })).toBeEnabled();
  });

  const FORMATTED = "SELECT\n  id\nFROM\n  patients";

  it("formats the whole query on click", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor");
    await userEvent.type(editor, "select id from patients");

    await userEvent.click(screen.getByRole("button", { name: "Format" }));

    expect(editor).toHaveValue(FORMATTED);
  });

  it("formats on Ctrl/Cmd+F and suppresses the browser find bar", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor");
    await userEvent.type(editor, "select id from patients");

    const notPrevented = fireEvent.keyDown(editor, { key: "f", ctrlKey: true });

    expect(editor).toHaveValue(FORMATTED);
    expect(notPrevented).toBe(false);
  });

  it("formats on Shift+Alt+F", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor");
    await userEvent.type(editor, "select id from patients");

    fireEvent.keyDown(editor, { key: "f", altKey: true, shiftKey: true });

    expect(editor).toHaveValue(FORMATTED);
  });

  it("formats only the selected statement when there is a selection", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor") as HTMLTextAreaElement;
    await userEvent.type(editor, "SELECT 1; select id from patients");
    editor.setSelectionRange(10, 33);

    await userEvent.click(screen.getByRole("button", { name: "Format" }));

    // Written back over the selection, leaving the untouched statement alone.
    expect(mockInsertText).toHaveBeenCalledWith(FORMATTED);
    expect(editor).toHaveValue("SELECT 1; select id from patients");
  });

  it("disables Format while the query is empty", async () => {
    renderEditor();
    expect(screen.getByRole("button", { name: "Format" })).toBeDisabled();

    await userEvent.type(screen.getByTestId("editor"), "select 1");
    expect(screen.getByRole("button", { name: "Format" })).toBeEnabled();
  });
});
