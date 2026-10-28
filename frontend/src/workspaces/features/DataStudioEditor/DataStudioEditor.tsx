import { gql } from "@apollo/client";
import {
  ArrowDownTrayIcon,
  Bars3BottomLeftIcon,
  PencilIcon,
  SparklesIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";
import { PlayIcon } from "@heroicons/react/24/solid";
import { SQLNamespace } from "@codemirror/lang-sql";
import clsx from "clsx";
import CodeEditor, {
  CodeEditorHandle,
} from "core/components/CodeEditor/CodeEditor";
import Spinner from "core/components/Spinner";
import useIsMac from "core/hooks/useIsMac";
import ResizablePanel, {
  ResizablePanelHandle,
} from "core/components/ResizablePanel";
import useSaveShortcut from "core/hooks/useSaveShortcut";
import { useTranslation } from "next-i18next";
import {
  forwardRef,
  ReactNode,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import SaveQueryDialog from "workspaces/features/SavedQueries/SaveQueryDialog";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useWorkspaceDataStudioSchemaQuery } from "./DataStudioSchemaBrowser.generated";
import DataStudioResults from "./DataStudioResults";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";
import { formatSql } from "./formatSql";
import SaveQueryButton from "./SaveQueryButton";
import SavedQueryVisibilityButton from "./SavedQueryVisibilityButton";
import { useDataStudioQuery } from "./useDataStudioQuery";
import { useSavedQueryEditor } from "./useSavedQueryEditor";

type DataStudioEditorProps = {
  workspaceSlug: string;
  savedQuery?: SavedQuery_SavedQueryFragment | null;
  canCreate: boolean;
  // Whether the toolbar names the query and offers its details and sharing
  // controls. Off when the editor sits in a page that already shows them.
  showQueryDetails?: boolean;
  // Extra toolbar controls, placed with the editing actions.
  toolbarExtra?: ReactNode;
  // A buffer that cannot be edited or saved, e.g. an older version being browsed.
  // Running and exporting still work.
  readOnly?: boolean;
  // Drop the card chrome when the owner draws its own frame around the editor.
  flush?: boolean;
  // The in-place writes of the editor, for owners that keep their own copy.
  onSaved?: (savedQuery: SavedQuery_SavedQueryFragment) => void;
};

export type DataStudioEditorHandle = {
  // Replace the buffer, e.g. with SQL drafted by the AI assistant.
  setContent(sql: string): void;
};

const MAX_ROWS_OPTIONS = [50, 100, 500, 1000, 10_000];

// Schema browser bounds. The floor keeps the tree usable rather than letting it
// be dragged shut; the ceiling leaves room for the editor on a laptop screen.
const SIDEBAR_DEFAULT_WIDTH = 240;
const SIDEBAR_MIN_WIDTH = 160;
const SIDEBAR_MAX_WIDTH = 640;
// What the toolbar needs to lay out its controls: past this the Run button and
// the export controls would be cut off by the panel below them.
const EDITOR_MIN_WIDTH = 560;

// Results panel bounds. Dragging the separator sizes the results, the editor
// above takes whatever is left, and the reserve is what keeps the editor from
// being squeezed out.
const RESULTS_DEFAULT_HEIGHT = 300;
const RESULTS_MIN_HEIGHT = 140;
const EDITOR_MIN_HEIGHT = 120;

const DataStudioEditor = forwardRef<
  DataStudioEditorHandle,
  DataStudioEditorProps
>(
  (
    {
      workspaceSlug,
      savedQuery,
      canCreate,
      showQueryDetails = true,
      toolbarExtra,
      readOnly = false,
      flush = false,
      onSaved,
    },
    ref,
  ) => {
    const { t } = useTranslation();
    const isMac = useIsMac();
    const [query, setQuery] = useState(savedQuery?.content ?? "");
    const [maxRows, setMaxRows] = useState(MAX_ROWS_OPTIONS[0]);
    const editorRef = useRef<CodeEditorHandle>(null);
    const resultsPanelRef = useRef<ResizablePanelHandle>(null);

    const editor = useSavedQueryEditor({
      workspaceSlug,
      content: query,
      initialSavedQuery: savedQuery,
      canCreate: canCreate && !readOnly,
      onSaved,
    });

    useImperativeHandle(ref, () => ({
      setContent(sql: string) {
        setQuery(sql);
      },
    }));

    // A version persisted outside this editor (the AI assistant saving one, a
    // restored version) arrives through the `savedQuery` prop. It replaces a
    // clean buffer right away; a buffer with unsaved edits keeps them and gets
    // a banner to load the new version from, so nothing is silently overwritten.
    const [incomingVersion, setIncomingVersion] =
      useState<SavedQuery_SavedQueryFragment | null>(null);
    const adoptVersion = useCallback(
      (sq: SavedQuery_SavedQueryFragment) => {
        setQuery(sq.content);
        editor.adopt(sq);
        setIncomingVersion(null);
      },
      [editor],
    );
    useEffect(() => {
      const current = editor.savedQuery;
      if (!savedQuery || !current || savedQuery.id !== current.id) return;
      if (savedQuery.updatedAt <= current.updatedAt) return;
      if (savedQuery.content === current.content) {
        // Only the details changed: the buffer and its baseline stay as they are.
        editor.adopt(savedQuery);
        return;
      }
      if (editor.isDirty) {
        setIncomingVersion(savedQuery);
      } else {
        adoptVersion(savedQuery);
      }
    }, [savedQuery]);

    useSaveShortcut(readOnly ? () => {} : editor.commit);

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

    // Reopening the results is part of running: with the panel closed, a run
    // would otherwise leave the page looking untouched.
    const runSelection = () => {
      const selected = editorRef.current?.getSelectedText() ?? "";
      resultsPanelRef.current?.expand();
      run(selected.trim() || query, maxRows);
    };

    // Always the whole query, never the selection — unlike Run, where a bad
    // fragment fails loudly at the database, the formatter reflows fragments
    // happily ("id, name" becomes two left-aligned lines) and would splice that
    // back into the middle of a line.
    const formatQuery = () => {
      if (readOnly) return;
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
        <div
          className={clsx(
            "flex h-full overflow-hidden bg-white",
            !flush && "rounded-md border shadow-xs",
          )}
        >
          <ResizablePanel
            side="left"
            label={t("Table list")}
            defaultSize={SIDEBAR_DEFAULT_WIDTH}
            minSize={SIDEBAR_MIN_WIDTH}
            maxSize={SIDEBAR_MAX_WIDTH}
            reserve={EDITOR_MIN_WIDTH}
          >
            <DataStudioSchemaBrowser
              workspaceSlug={workspaceSlug}
              className="h-full w-full border-r border-gray-200"
              onInsert={insertIntoEditor}
            />
          </ResizablePanel>
          <div className="flex min-w-0 flex-1 flex-col">
            {/* Toolbar: controls right-aligned, Run at the far right. It wraps
                rather than clipping when the assistant dock narrows the editor. */}
            <div className="flex min-h-11 shrink-0 flex-wrap items-center gap-2 border-b border-gray-200 px-3 py-1.5">
              {showQueryDetails && (
                <>
                  <TableCellsIcon className="h-4 w-4 shrink-0 text-gray-400" />
                  <span className="truncate text-sm font-medium text-gray-800">
                    {editor.savedQuery?.name ?? t("Query")}
                  </span>
                  {editor.savedQuery && (
                    <span className="truncate text-xs text-gray-500">
                      ({editor.savedQuery.slug})
                    </span>
                  )}
                  {editor.savedQuery && editor.canUpdate && !readOnly && (
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
                </>
              )}
              <div className="ml-auto flex flex-wrap items-center justify-end gap-2">
                {!readOnly && <SaveQueryButton plan={editor.savePlan} />}
                {showQueryDetails && editor.savedQuery && !readOnly && (
                  <SavedQueryVisibilityButton
                    visibility={editor.savedQuery.visibility}
                    canUpdate={editor.canUpdateVisibility}
                    saving={editor.saving}
                    onChange={editor.setVisibility}
                  />
                )}
                <label className="flex items-center gap-1.5 whitespace-nowrap text-xs text-gray-500">
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
                {toolbarExtra}
                {!readOnly && (
                  <button
                    onClick={formatQuery}
                    disabled={!query.trim()}
                    title={t("Format ({{shortcut}})", {
                      shortcut: formatShortcutLabel,
                    })}
                    className="inline-flex h-8 items-center gap-1.5 whitespace-nowrap rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent"
                  >
                    <Bars3BottomLeftIcon className="h-4 w-4" />
                    {t("Format")}
                  </button>
                )}
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
                  className="inline-flex h-8 items-center gap-1.5 whitespace-nowrap rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent"
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
                  title={t("Run ({{shortcut}})", {
                    shortcut: runShortcutLabel,
                  })}
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

            {incomingVersion && (
              <div
                role="status"
                className="flex shrink-0 items-center gap-3 border-b border-indigo-100 bg-indigo-50 px-3 py-1.5 text-xs text-indigo-900"
              >
                <SparklesIcon className="h-4 w-4 shrink-0 text-indigo-500" />
                <span className="flex-1">
                  {t(
                    "A new version of this query was saved. Load it, or keep your unsaved edits.",
                  )}
                </span>
                <button
                  type="button"
                  onClick={() => adoptVersion(incomingVersion)}
                  className="rounded border border-indigo-300 bg-white px-2 py-0.5 font-medium text-indigo-800 hover:bg-indigo-100"
                >
                  {t("Load new version")}
                </button>
                <button
                  type="button"
                  onClick={() => setIncomingVersion(null)}
                  className="font-medium text-indigo-700 hover:text-indigo-900"
                >
                  {t("Keep my edits")}
                </button>
              </div>
            )}

            {/* Editor + results split: the results panel is sized and can be
                closed altogether, the editor takes the remaining height. */}
            <div className="flex min-h-0 flex-1 flex-col">
              <div className="min-h-0 flex-1">
                <CodeEditor
                  ref={editorRef}
                  lang="sql"
                  embedded
                  autoFocus={!readOnly}
                  editable={!readOnly}
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
              <ResizablePanel
                handleRef={resultsPanelRef}
                side="bottom"
                label={t("Results")}
                defaultSize={RESULTS_DEFAULT_HEIGHT}
                minSize={RESULTS_MIN_HEIGHT}
                reserve={EDITOR_MIN_HEIGHT}
              >
                <DataStudioResults
                  loading={loading}
                  result={result}
                  error={error}
                  onRetry={retry}
                />
              </ResizablePanel>
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
  },
);

DataStudioEditor.displayName = "DataStudioEditor";

// Assigned after `forwardRef` wraps the component: `gql` documents hang off the
// exported object so codegen keeps picking them up next to the component.
(DataStudioEditor as typeof DataStudioEditor & { queries: unknown }).queries = {
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
            pageInfo {
              hasNextPage
            }
            durationMs
          }
        }
      }
    }
  `,
};

export default DataStudioEditor;
