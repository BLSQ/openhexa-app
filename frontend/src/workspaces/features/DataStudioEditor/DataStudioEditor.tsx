import { gql } from "@apollo/client";
import clsx from "clsx";
import {
  ArrowDownTrayIcon,
  Bars3BottomLeftIcon,
  PencilIcon,
  SparklesIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";
import { PlayIcon } from "@heroicons/react/24/solid";
import { SQLNamespace } from "@codemirror/lang-sql";
import CodeEditor, {
  CodeEditorHandle,
} from "core/components/CodeEditor/CodeEditor";
import Spinner from "core/components/Spinner";
import SubscriptionLimitTooltip from "core/components/SubscriptionLimitTooltip";
import useIsMac from "core/hooks/useIsMac";
import useResizablePanel from "core/hooks/useResizablePanel";
import useSaveShortcut from "core/hooks/useSaveShortcut";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useRef, useState } from "react";
import SaveQueryDialog from "workspaces/features/SavedQueries/SaveQueryDialog";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useWorkspaceDataStudioSchemaQuery } from "./DataStudioSchemaBrowser.generated";
import DataStudioResults from "./DataStudioResults";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";
import { formatSql } from "./formatSql";
import GenerateSqlBar, { useGenerateSqlForm } from "./GenerateSqlBar";
import SaveQueryButton from "./SaveQueryButton";
import SavedQueryVisibilityButton from "./SavedQueryVisibilityButton";
import { useDataStudioQuery } from "./useDataStudioQuery";
import { useSavedQueryEditor } from "./useSavedQueryEditor";

type DataStudioEditorProps = {
  workspaceSlug: string;
  savedQuery?: SavedQuery_SavedQueryFragment | null;
  canCreate: boolean;
  aiEnabled?: boolean;
  aiBudgetLimitReached?: boolean;
  monthlyLimitExceeded?: boolean;
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
  canCreate,
  aiEnabled = false,
  aiBudgetLimitReached = false,
  monthlyLimitExceeded = false,
}: DataStudioEditorProps) => {
  const { t } = useTranslation();
  const isMac = useIsMac();
  const [query, setQuery] = useState(savedQuery?.content ?? "");
  const [maxRows, setMaxRows] = useState(MAX_ROWS_OPTIONS[0]);
  const editorRef = useRef<CodeEditorHandle>(null);
  const [generateBarOpen, setGenerateBarOpen] = useState(false);
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

  const handleGenerated = useCallback((sql: string) => {
    setQuery(sql);
    setGenerateBarOpen(false);
  }, []);

  const generateForm = useGenerateSqlForm(workspaceSlug, handleGenerated);

  const editor = useSavedQueryEditor({
    workspaceSlug,
    content: query,
    initialSavedQuery: savedQuery,
    canCreate,
  });

  useSaveShortcut(editor.commit);

  // Stable so the memoised schema browser is not re-rendered by every keystroke
  // in the editor. Goes through the imperative handle, so it needs no deps.
  const insertIntoEditor = useCallback(
    (text: string) => editorRef.current?.insertText(text),
    [],
  );

  const runShortcutLabel = isMac ? "⌘+Enter" : "Ctrl+Enter";
  const formatShortcutLabel = isMac ? "⇧+⌥+F" : "Shift+Alt+F";
  // Compact form for the in-button pill: the modifier glyphs read cleanly on
  // macOS; other platforms keep the spelled-out modifiers.
  const runShortcutBadge = isMac ? "⌘↵" : "Ctrl+Enter";

  const {
    run,
    retry,
    downloadCsv,
    exporting,
    result,
    loading,
    error,
    canExport,
  } = useDataStudioQuery(workspaceSlug);

  // Same query DataStudioSchemaBrowser runs to populate its table tree.
  // Apollo dedupes identical in-flight queries and serves matching variables
  // from its normalized cache afterwards, so this doesn't add a network
  // request — it's how the editor gets at the schema it needs for autocomplete.
  const { data: schemaData } = useWorkspaceDataStudioSchemaQuery({
    variables: { workspaceSlug },
  });

  const sqlSchema = useMemo<SQLNamespace>(() => {
    const items = schemaData?.workspace?.database?.tables?.items ?? [];
    return Object.fromEntries(
      items.map((table) => [
        table.name,
        table.columns.map((column) => ({
          label: column.name,
          type: "property",
          detail: column.type,
        })),
      ]),
    );
  }, [schemaData]);

  const canRun = !loading && Boolean(query.trim());

  const runSelection = () => {
    const selected = editorRef.current?.getSelectedText() ?? "";
    run(selected.trim() || query, maxRows);
  };

  // Always the whole query, never the selection — unlike Run, where a bad
  // fragment fails loudly at the database, the formatter reflows fragments
  // happily ("id, name" becomes two left-aligned lines) and would splice that
  // back into the middle of a line.
  const formatQuery = () => {
    editorRef.current?.replaceAll(formatSql(query));
  };

  // Bound inside CodeMirror (see CodeEditor `shortcuts`) so the keystroke is
  // consumed and does not also insert a newline. Runs the selection when there
  // is one, otherwise the whole query. "Mod" is Cmd on macOS / Ctrl elsewhere;
  // "Ctrl" is added so Ctrl+Enter works on macOS too.
  // Formatting deliberately stays off Mod-f: that is find, both in the browser
  // and in CodeMirror, and it is used far more often than formatting.
  // "Shift-Alt-f" is the editor-conventional binding for formatting. It needs
  // both cases: CodeMirror skips its keyCode fallback for plain Alt combos on
  // macOS (Alt there types a character — ⇧⌥F is "Ï"), so it resolves the
  // keystroke to "Shift-Alt-F" on Mac and to "Shift-Alt-f" everywhere else.
  const editorShortcuts = [
    { key: "Mod-Enter", run: runSelection },
    { key: "Ctrl-Enter", run: runSelection },
    { key: "Shift-Alt-f", run: formatQuery },
    { key: "Shift-Alt-F", run: formatQuery },
  ];

  return (
    <>
      <div className="flex h-full overflow-hidden rounded-md border bg-white shadow-xs">
        <div className="shrink-0" style={{ width: sidebar.size }}>
          <DataStudioSchemaBrowser
            workspaceSlug={workspaceSlug}
            className="h-full w-full"
            onInsert={insertIntoEditor}
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
              <SaveQueryButton plan={editor.savePlan} />
              {editor.savedQuery && (
                <SavedQueryVisibilityButton
                  visibility={editor.savedQuery.visibility}
                  canUpdate={editor.canUpdateVisibility}
                  saving={editor.saving}
                  onChange={editor.setVisibility}
                />
              )}
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
              {aiEnabled && (
                <SubscriptionLimitTooltip
                  isLimitReached={aiBudgetLimitReached}
                  title={t("Monthly AI budget reached")}
                >
                  <button
                    onClick={() => setGenerateBarOpen((open) => !open)}
                    disabled={aiBudgetLimitReached}
                    aria-pressed={generateBarOpen}
                    className="inline-flex h-8 items-center gap-1.5 rounded-md bg-indigo-100 px-2.5 text-xs font-medium text-indigo-700 hover:bg-indigo-200 disabled:cursor-not-allowed disabled:bg-transparent disabled:text-gray-300"
                  >
                    <SparklesIcon className="h-4 w-4" />
                    {t("Generate")}
                  </button>
                </SubscriptionLimitTooltip>
              )}
              <button
                onClick={formatQuery}
                disabled={!query.trim()}
                title={t("Format ({{shortcut}})", {
                  shortcut: formatShortcutLabel,
                })}
                className="inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent"
              >
                <Bars3BottomLeftIcon className="h-4 w-4" />
                {t("Format")}
              </button>
              {/* The server re-run can take a while; reassure the user right
                  where they clicked. */}
              {exporting && (
                <span className="text-xs text-gray-400">
                  {t("This may take a while")}
                </span>
              )}
              <button
                onClick={downloadCsv}
                disabled={!canExport || exporting}
                className="inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent"
              >
                {exporting ? (
                  <>
                    <Spinner size="xs" />
                    {t("Exporting…")}
                  </>
                ) : (
                  <>
                    <ArrowDownTrayIcon className="h-4 w-4" />
                    {t("Export CSV")}
                  </>
                )}
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

          {aiEnabled && (
            <GenerateSqlBar
              open={generateBarOpen}
              onClose={() => setGenerateBarOpen(false)}
              form={generateForm}
              monthlyLimitExceeded={monthlyLimitExceeded}
            />
          )}

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
                sqlSchema={sqlSchema}
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
      {/* Kept mounted and toggled through `open`: Headless UI skips its enter
          transition for a dialog that mounts already open. */}
      <SaveQueryDialog
        open={editor.dialog.open}
        mode={editor.dialog.mode}
        workspaceSlug={workspaceSlug}
        content={query}
        savedQuery={editor.savedQuery}
        onClose={editor.closeDialog}
        onSaved={editor.onDialogSaved}
      />
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
