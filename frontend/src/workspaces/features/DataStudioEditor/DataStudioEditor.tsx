import { gql } from "@apollo/client";
import {
  ArrowDownTrayIcon,
  PencilIcon,
  SparklesIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";
import { PlayIcon } from "@heroicons/react/24/solid";
import CodeEditor, {
  CodeEditorHandle,
} from "core/components/CodeEditor/CodeEditor";
import Spinner from "core/components/Spinner";
import SubscriptionLimitTooltip from "core/components/SubscriptionLimitTooltip";
import useIsMac from "core/hooks/useIsMac";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import SaveQueryDialog from "workspaces/features/SavedQueries/SaveQueryDialog";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import DataStudioResults from "./DataStudioResults";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";
import GenerateSqlBar, { useGenerateSqlForm } from "./GenerateSqlBar";
import SaveQueryButton from "./SaveQueryButton";
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

  // Stable so the memoised schema browser is not re-rendered by every keystroke
  // in the editor. Goes through the imperative handle, so it needs no deps.
  const insertIntoEditor = useCallback(
    (text: string) => editorRef.current?.insertText(text),
    [],
  );

  const runShortcutLabel = isMac ? "⌘+Enter" : "Ctrl+Enter";
  // Compact form for the in-button pill: the return glyph reads cleanly next to
  // ⌘ on macOS; other platforms keep the spelled-out modifier.
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

  const canRun = !loading && Boolean(query.trim());

  const runSelection = () => {
    const selected = editorRef.current?.getSelectedText() ?? "";
    run(selected.trim() || query, maxRows);
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
        <DataStudioSchemaBrowser
          workspaceSlug={workspaceSlug}
          className="w-[240px] shrink-0 border-r border-gray-200"
          onInsert={insertIntoEditor}
        />
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

          {/* Editor + results split: editor on top, results fill the rest. */}
          <div className="flex min-h-0 flex-1 flex-col">
            <div className="h-[38%] min-h-[140px] shrink-0 border-b border-gray-200">
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
