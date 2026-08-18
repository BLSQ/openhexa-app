import { gql } from "@apollo/client";
import clsx from "clsx";
import {
  ArrowDownTrayIcon,
  PencilIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";
import { PlayIcon } from "@heroicons/react/24/solid";
import CodeEditor, {
  CodeEditorHandle,
} from "core/components/CodeEditor/CodeEditor";
import useIsMac from "core/hooks/useIsMac";
import useResizablePanel from "core/hooks/useResizablePanel";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import SaveQueryDialog from "workspaces/features/SavedQueries/SaveQueryDialog";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { buildCsv, downloadCsv } from "./csv";
import DataStudioResults from "./DataStudioResults";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";
import SaveQueryButton from "./SaveQueryButton";
import { useDataStudioQuery } from "./useDataStudioQuery";
import { useSavedQueryEditor } from "./useSavedQueryEditor";

type DataStudioEditorProps = {
  workspaceSlug: string;
  savedQuery?: SavedQuery_SavedQueryFragment | null;
  canCreate?: boolean;
};

const MAX_ROWS_OPTIONS = [50, 100, 500, 1000, 10_000];

// Schema browser bounds. The floor keeps the tree usable rather than letting it
// be dragged shut; the ceiling leaves room for the editor on a laptop screen.
const SIDEBAR_DEFAULT_WIDTH = 240;
const SIDEBAR_MIN_WIDTH = 160;
const SIDEBAR_MAX_WIDTH = 640;

// Editor pane bounds. Dragging the separator sizes the editor, and the results
// panel below takes whatever is left, so the floor here is the editor's and the
// ceiling is whatever keeps the results panel from collapsing.
const EDITOR_DEFAULT_HEIGHT = 260;
const EDITOR_MIN_HEIGHT = 120;
const RESULTS_MIN_HEIGHT = 140;

const DataStudioEditor = ({
  workspaceSlug,
  savedQuery,
  canCreate = false,
}: DataStudioEditorProps) => {
  const { t } = useTranslation();
  const isMac = useIsMac();
  const [query, setQuery] = useState(savedQuery?.content ?? "");
  const [maxRows, setMaxRows] = useState(MAX_ROWS_OPTIONS[0]);
  const editorRef = useRef<CodeEditorHandle>(null);
  // Measured at drag time so the editor can never be grown past the point where
  // the results panel would collapse.
  const splitRef = useRef<HTMLDivElement>(null);

  const sidebar = useResizablePanel({
    storageKey: "datastudio.sidebarWidth",
    defaultSize: SIDEBAR_DEFAULT_WIDTH,
    min: SIDEBAR_MIN_WIDTH,
    max: SIDEBAR_MAX_WIDTH,
    axis: "x",
  });

  const editorPane = useResizablePanel({
    storageKey: "datastudio.editorHeight",
    defaultSize: EDITOR_DEFAULT_HEIGHT,
    min: EDITOR_MIN_HEIGHT,
    max: useCallback(() => {
      const available = splitRef.current?.clientHeight ?? 0;
      // Nothing to clamp against until the split has been laid out — and
      // clamping to the floor here would quietly throw away a remembered
      // height, which is what happens when the panel mounts hidden.
      if (available === 0) {
        return Number.POSITIVE_INFINITY;
      }
      return Math.max(EDITOR_MIN_HEIGHT, available - RESULTS_MIN_HEIGHT);
    }, []),
    axis: "y",
  });

  const editor = useSavedQueryEditor({
    workspaceSlug,
    content: query,
    initialSavedQuery: savedQuery,
  });

  const runShortcutLabel = isMac ? "⌘+Enter" : "Ctrl+Enter";
  // Compact form for the in-button pill: the return glyph reads cleanly next to
  // ⌘ on macOS; other platforms keep the spelled-out modifier.
  const runShortcutBadge = isMac ? "⌘↵" : "Ctrl+Enter";

  const { run, retry, result, loading, error, canExport } =
    useDataStudioQuery(workspaceSlug);

  const canRun = !loading && Boolean(query.trim());

  const runSelection = () => {
    const selected = editorRef.current?.getSelectedText() ?? "";
    run(selected.trim() || query, maxRows);
  };

  const exportCsv = () => {
    if (!result?.success) {
      return;
    }
    const csv = buildCsv(result.columns ?? [], result.rows ?? []);
    downloadCsv("query-results.csv", csv);
  };

  // Bound inside CodeMirror (see CodeEditor `shortcuts`) so the keystroke is
  // consumed and does not also insert a newline. Runs the selection when there
  // is one, otherwise the whole query. "Mod" is Cmd on macOS / Ctrl elsewhere;
  // "Ctrl" is added so Ctrl+Enter works on macOS too.
  const editorShortcuts = [
    { key: "Mod-Enter", run: runSelection },
    { key: "Ctrl-Enter", run: runSelection },
  ];

  return (
    <>
      <div className="flex h-full overflow-hidden rounded-md border bg-white shadow-xs">
        <div className="shrink-0" style={{ width: sidebar.size }}>
          <DataStudioSchemaBrowser
            workspaceSlug={workspaceSlug}
            className="h-full w-full"
            onInsert={(text) => editorRef.current?.insertText(text)}
          />
        </div>
        {/* A 1px border would be too small a target, so the handle is a 2px
            strip that carries the divider itself and widens its highlight on
            hover. `group` lets the inner line react without a second selector. */}
        <div
          {...sidebar.separatorProps}
          aria-label={t("Resize the table list")}
          title={t("Drag to resize — arrow keys also work")}
          className={clsx(
            "group relative w-[2px] shrink-0 cursor-col-resize bg-gray-200 transition-colors",
            "hover:bg-blue-400 focus-visible:bg-blue-500 focus-visible:outline-none",
            sidebar.isResizing && "bg-blue-500",
          )}
        >
          {/* Widens the grab area past the visible strip without moving the
              layout, the way an editor gutter behaves. */}
          <span className="absolute inset-y-0 -left-1 -right-1" />
        </div>
        <div className="flex min-w-0 flex-1 flex-col">
          {/* Toolbar: controls right-aligned, Run at the far right. */}
          <div className="flex h-11 shrink-0 items-center gap-2 border-b border-gray-200 px-3">
            <TableCellsIcon className="h-4 w-4 shrink-0 text-gray-400" />
            <span className="truncate text-sm font-medium text-gray-800">
              {editor.savedQuery?.name ?? t("Query")}
            </span>
            {editor.savedQuery && editor.canUpdate && (
              <button
                type="button"
                onClick={editor.editDetails}
                title={t("Edit details")}
                aria-label={t("Edit details")}
                className="inline-flex shrink-0 items-center justify-center rounded-md p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
              >
                <PencilIcon className="h-4 w-4" />
              </button>
            )}
            <div className="ml-auto flex items-center gap-2">
              <SaveQueryButton
                isSaved={Boolean(editor.savedQuery)}
                isDirty={editor.isDirty}
                hasContent={Boolean(query.trim())}
                canUpdate={editor.canUpdate}
                canCreate={canCreate}
                saving={editor.saving}
                onSave={editor.save}
                onSaveAsNew={editor.saveAsNew}
              />
              <label className="flex items-center gap-1.5 text-xs text-gray-500">
                {t("Max rows")}
                <select
                  value={maxRows}
                  onChange={(event) => setMaxRows(Number(event.target.value))}
                  className="h-8 rounded-md border border-gray-200 pr-7 pl-2 text-xs text-gray-700 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                >
                  {MAX_ROWS_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option.toLocaleString()}
                    </option>
                  ))}
                </select>
              </label>
              <button
                onClick={exportCsv}
                disabled={!canExport}
                className="inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent"
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
                {t("Export CSV")}
              </button>
              <button
                onClick={runSelection}
                disabled={!canRun}
                title={t("Run ({{shortcut}})", { shortcut: runShortcutLabel })}
                className="inline-flex h-8 min-w-[104px] items-center justify-center gap-1.5 rounded-md bg-blue-600 px-3 text-xs font-medium text-white shadow-xs transition-colors hover:bg-blue-700 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1 focus-visible:outline-none active:bg-blue-800 disabled:opacity-60 disabled:hover:bg-blue-600"
              >
                {loading ? (
                  <>
                    <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                    {t("Running…")}
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-3 w-3" />
                    {t("Run")}
                    <span
                      aria-hidden
                      className="ml-0.5 hidden rounded bg-white/20 px-1 py-0.5 text-[10px] leading-none font-medium text-white/80 sm:inline-block"
                    >
                      {runShortcutBadge}
                    </span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Editor + results split: the editor is sized, the results panel below
              takes the remaining height. */}
          <div ref={splitRef} className="flex min-h-0 flex-1 flex-col">
            <div className="shrink-0" style={{ height: editorPane.size }}>
              <CodeEditor
                ref={editorRef}
                lang="sql"
                embedded
                autoFocus
                value={query}
                onChange={setQuery}
                height="100%"
                minHeight="100%"
                placeholder={t("Write a SQL query… ({{shortcut}} to run)", {
                  shortcut: runShortcutLabel,
                })}
                shortcuts={editorShortcuts}
                className="h-full !rounded-none"
              />
            </div>
            <div
              {...editorPane.separatorProps}
              aria-label={t("Resize the results panel")}
              title={t("Drag to resize — arrow keys also work")}
              className={clsx(
                "group relative h-[2px] shrink-0 cursor-row-resize bg-gray-200 transition-colors",
                "hover:bg-blue-400 focus-visible:bg-blue-500 focus-visible:outline-none",
                editorPane.isResizing && "bg-blue-500",
              )}
            >
              <span className="absolute inset-x-0 -top-1 -bottom-1" />
            </div>
            <div className="min-h-0 flex-1">
              <DataStudioResults
                loading={loading}
                result={result}
                error={error}
                onRetry={retry}
              />
            </div>
          </div>
        </div>
      </div>
      {editor.dialog && (
        <SaveQueryDialog
          open
          mode={editor.dialog.mode}
          workspaceSlug={workspaceSlug}
          content={query}
          savedQuery={editor.savedQuery}
          onClose={editor.closeDialog}
          onSaved={editor.onDialogSaved}
        />
      )}
    </>
  );
};

DataStudioEditor.queries = {
  executeSQL: gql`
    query ExecuteWorkspaceSql(
      $workspaceSlug: String!
      $query: String!
      $maxRows: Int
    ) {
      workspace(slug: $workspaceSlug) {
        slug
        database {
          executeSQL(query: $query, maxRows: $maxRows, origin: DATA_STUDIO) {
            success
            errors
            errorMessage
            columns
            rows
            rowCount
            truncated
            durationMs
          }
        }
      }
    }
  `,
};

export default DataStudioEditor;
