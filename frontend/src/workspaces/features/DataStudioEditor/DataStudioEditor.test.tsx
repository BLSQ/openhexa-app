import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { downloadBlob } from "core/helpers/files";
import DataStudioEditor from "./DataStudioEditor";

// `useTranslation` is globally mocked to echo the key, so button/label
// assertions below use the raw key strings.

// Headless UI's MenuButton toggles on pointer events, which jsdom does not
// implement; polyfill the minimum surface so the Run-options menu can open.
beforeAll(() => {
  (window as unknown as { PointerEvent: typeof MouseEvent }).PointerEvent =
    MouseEvent as unknown as typeof MouseEvent;
  Element.prototype.hasPointerCapture = jest.fn();
  Element.prototype.releasePointerCapture = jest.fn();
  Element.prototype.scrollIntoView = jest.fn();
});

const mockExecute = jest.fn();
let mockQueryState: { data?: unknown; loading: boolean };

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
  default: ({ loading, result }: { loading: boolean; result?: any }) => (
    <div
      data-testid="results"
      data-loading={String(loading)}
      data-success={String(Boolean(result?.success))}
    />
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
      return React.createElement("textarea", {
        ref: innerRef,
        "data-testid": "editor",
        value: props.value ?? "",
        placeholder: props.placeholder,
        onChange: (event: any) => props.onChange?.(event.target.value),
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

const renderEditor = () =>
  render(<DataStudioEditor workspaceSlug="ws-1" />);

// The chevron trigger is an aria-labelled element wrapped in the Headless UI
// menu button; click the button itself to open the menu.
const openRunMenu = async () => {
  const trigger = screen
    .getByLabelText("More run options")
    .closest("button") as HTMLButtonElement;
  await userEvent.click(trigger);
};

beforeEach(() => {
  mockExecute.mockClear();
  mockInsertText.mockClear();
  (downloadBlob as jest.Mock).mockClear();
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

  it("runs the query on Ctrl/Cmd+Enter", async () => {
    renderEditor();
    await userEvent.type(screen.getByTestId("editor"), "SELECT 1");
    fireEvent.keyDown(screen.getByTestId("editor"), {
      key: "Enter",
      ctrlKey: true,
    });

    expect(mockExecute).toHaveBeenCalledTimes(1);
  });

  it("does not run when the query is empty", async () => {
    renderEditor();
    const runButton = screen.getByRole("button", { name: "Run" });
    expect(runButton).toBeDisabled();

    await userEvent.click(runButton);
    expect(mockExecute).not.toHaveBeenCalled();
  });

  it("runs only the selected text via the Run selection menu item", async () => {
    renderEditor();
    const editor = screen.getByTestId("editor") as HTMLTextAreaElement;
    await userEvent.type(editor, "SELECT 1 SELECT 2");
    editor.setSelectionRange(9, 17);

    await openRunMenu();
    await userEvent.click(await screen.findByText("Run selection"));

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 2", maxRows: 50 },
    });
  });

  it("falls back to the full query when Run selection has no selection", async () => {
    renderEditor();
    await userEvent.type(screen.getByTestId("editor"), "SELECT 1");

    await openRunMenu();
    await userEvent.click(await screen.findByText("Run selection"));

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 1", maxRows: 50 },
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
