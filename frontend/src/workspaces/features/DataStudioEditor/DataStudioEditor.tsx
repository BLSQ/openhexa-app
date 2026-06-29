import { gql } from "@apollo/client";
import {
  ArrowDownTrayIcon,
  ChevronDownIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";
import { PlayIcon } from "@heroicons/react/24/solid";
import CodeEditor, {
  CodeEditorHandle,
} from "core/components/CodeEditor/CodeEditor";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, useEffect, useRef, useState } from "react";
import { buildCsv, downloadCsv } from "./csv";
import { useExecuteWorkspaceSqlLazyQuery } from "./DataStudioEditor.generated";
import DataStudioResults from "./DataStudioResults";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";

type DataStudioEditorProps = {
  workspaceSlug: string;
};

const MAX_ROWS_OPTIONS = [50, 100, 500, 1000, 10_000];

const DataStudioEditor = ({ workspaceSlug }: DataStudioEditorProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [maxRows, setMaxRows] = useState(MAX_ROWS_OPTIONS[0]);
  const [runMenuOpen, setRunMenuOpen] = useState(false);
  const editorRef = useRef<CodeEditorHandle>(null);
  const runMenuRef = useRef<HTMLDivElement>(null);

  const [execute, { data, loading }] = useExecuteWorkspaceSqlLazyQuery({
    fetchPolicy: "network-only",
  });

  const result = data?.workspace?.database?.executeSQL;
  const canExport = Boolean(result?.success && (result.rows?.length ?? 0) > 0);
  const canRun = !loading && Boolean(query.trim());

  useEffect(() => {
    if (!runMenuOpen) {
      return;
    }
    const onDocClick = (event: MouseEvent) => {
      if (!runMenuRef.current?.contains(event.target as Node)) {
        setRunMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [runMenuOpen]);

  const runSql = (sql: string) => {
    const trimmed = sql.trim();
    if (loading || !trimmed) {
      return;
    }
    execute({ variables: { workspaceSlug, query: trimmed, maxRows } });
  };

  const run = () => runSql(query);

  const runSelection = () => {
    const selected = editorRef.current?.getSelectedText() ?? "";
    runSql(selected.trim() || query);
  };

  const exportCsv = () => {
    if (!result?.success) {
      return;
    }
    const csv = buildCsv(result.columns ?? [], result.rows ?? []);
    downloadCsv("query-results.csv", csv);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      run();
    }
  };

  return (
    <div className="flex h-full overflow-hidden rounded-md border bg-white shadow-xs">
      <DataStudioSchemaBrowser
        workspaceSlug={workspaceSlug}
        className="w-[240px] shrink-0 border-r border-gray-200"
        onInsert={(text) => editorRef.current?.insertText(text)}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Toolbar: controls right-aligned, Run at the far right. */}
        <div className="flex h-11 shrink-0 items-center gap-2 border-b border-gray-200 px-3">
          <TableCellsIcon className="h-4 w-4 shrink-0 text-gray-400" />
          <span className="text-sm font-medium text-gray-800">{t("Query")}</span>
          <div className="ml-auto flex items-center gap-2">
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
            {/* Split Run button: main = run all, chevron = run selection. */}
            <div ref={runMenuRef} className="relative">
              <div className="inline-flex h-8 items-stretch overflow-hidden rounded-md bg-blue-600 shadow-xs">
                <button
                  onClick={run}
                  disabled={!canRun}
                  className="inline-flex items-center gap-1.5 px-3 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-60"
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
                    </>
                  )}
                </button>
                <button
                  onClick={() => setRunMenuOpen((open) => !open)}
                  disabled={loading}
                  aria-label={t("More run options")}
                  className="inline-flex w-7 items-center justify-center border-l border-white/20 text-white hover:bg-blue-700 disabled:opacity-60"
                >
                  <ChevronDownIcon className="h-3.5 w-3.5" />
                </button>
              </div>
              {runMenuOpen && !loading && (
                <div className="absolute right-0 top-9 z-20 w-52 rounded-md bg-white py-1 text-xs shadow-xl ring-1 ring-black/5">
                  <button
                    onClick={() => {
                      setRunMenuOpen(false);
                      run();
                    }}
                    disabled={!canRun}
                    className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-gray-800 hover:bg-gray-100 disabled:text-gray-300"
                  >
                    <PlayIcon className="h-3.5 w-3.5 text-blue-600" />
                    {t("Run all")}
                  </button>
                  <button
                    onClick={() => {
                      setRunMenuOpen(false);
                      runSelection();
                    }}
                    disabled={loading}
                    className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-gray-800 hover:bg-gray-100"
                  >
                    <PlayIcon className="h-3.5 w-3.5 text-gray-400" />
                    {t("Run selection")}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Editor + results split: editor on top, results fill the rest. */}
        <div className="flex min-h-0 flex-1 flex-col">
          <div
            onKeyDown={onKeyDown}
            className="h-[38%] min-h-[140px] shrink-0 border-b border-gray-200"
          >
            <CodeEditor
              ref={editorRef}
              lang="sql"
              embedded
              value={query}
              onChange={setQuery}
              height="100%"
              minHeight="100%"
              placeholder={t("Write a SQL query…")}
              className="h-full !rounded-none !border-0"
            />
          </div>
          <div className="min-h-0 flex-1">
            <DataStudioResults loading={loading} result={result} />
          </div>
        </div>
      </div>
    </div>
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
          executeSQL(query: $query, maxRows: $maxRows) {
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
