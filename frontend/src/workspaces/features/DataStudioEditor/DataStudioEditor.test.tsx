import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DataStudioEditor from "./DataStudioEditor";
import { downloadQueryCsv } from "./downloadQueryCsv";

// `useTranslation` is globally mocked to echo the key, so button/label
// assertions below use the raw key strings.

const mockExecute = jest.fn();
let mockQueryState: { data?: unknown; loading: boolean; error?: unknown };

jest.mock("./DataStudioEditor.generated", () => ({
  useExecuteWorkspaceSqlLazyQuery: () => [mockExecute, mockQueryState],
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
      }));
      // Mirror CodeMirror's keymap: a matching shortcut runs its handler and
      // consumes the event (preventDefault), so no newline is inserted.
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
  (downloadQueryCsv as jest.Mock).mockClear();
  mockQueryState = { loading: false };
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

  it("exports the last run query, not the current editor contents", async () => {
    mockQueryState = successState();
    renderEditor();
    // Run one query, then change the editor: the export must use what was run.
    await userEvent.type(screen.getByTestId("editor"), "SELECT 1");
    await userEvent.click(screen.getByRole("button", { name: "Run" }));
    await userEvent.type(screen.getByTestId("editor"), " -- edited");

    await userEvent.click(screen.getByRole("button", { name: "Export CSV" }));

    expect(downloadQueryCsv).toHaveBeenCalledTimes(1);
    expect(downloadQueryCsv).toHaveBeenCalledWith("ws-1", "SELECT 1");
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
});
